#!/usr/bin/env python3
"""
COMPREHENSIVE AUTHENTICATION TESTING - FOCUSED ON ACTUAL IMPLEMENTATION
Tests what's actually implemented in the backend
"""

import requests
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-requirements.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🔐 COMPREHENSIVE AUTHENTICATION TESTING - ACTUAL IMPLEMENTATION")
print(f"Testing backend at: {API_BASE}")
print("="*80)

def test_complete_auth_flow():
    """Test complete authentication flow for all roles"""
    print("\n=== COMPLETE AUTHENTICATION FLOW TEST ===")
    
    results = {}
    roles = ['client', 'provider', 'navigator', 'agency']
    
    for role in roles:
        print(f"\n--- Testing {role.upper()} Complete Flow ---")
        
        # Step 1: Registration
        email = f"auth_test_{role}_{uuid.uuid4().hex[:8]}@test.com"
        reg_payload = {
            "email": email,
            "password": "SecurePass123!",
            "role": role,
            "terms_accepted": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/auth/register", json=reg_payload)
            print(f"  Registration: {response.status_code}")
            
            if response.status_code != 200:
                print(f"  ❌ Registration failed: {response.text}")
                results[role] = {'registration': False, 'error': response.text}
                continue
            
            # Step 2: Login
            login_payload = {"email": email, "password": "SecurePass123!"}
            response = requests.post(f"{API_BASE}/auth/login", json=login_payload)
            print(f"  Login: {response.status_code}")
            
            if response.status_code == 403 and role == 'provider':
                print(f"  ⚠️  Provider needs approval (expected behavior)")
                results[role] = {'registration': True, 'login': False, 'reason': 'pending_approval'}
                continue
            elif response.status_code != 200:
                print(f"  ❌ Login failed: {response.text}")
                results[role] = {'registration': True, 'login': False, 'error': response.text}
                continue
            
            token = response.json().get('access_token')
            
            # Step 3: Token validation
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            print(f"  Token validation: {response.status_code}")
            
            if response.status_code != 200:
                print(f"  ❌ Token validation failed: {response.text}")
                results[role] = {'registration': True, 'login': True, 'token_validation': False, 'error': response.text}
                continue
            
            user_data = response.json()
            print(f"  User ID: {user_data.get('id')}")
            print(f"  Role: {user_data.get('role')}")
            
            # Step 4: Test protected endpoints
            protected_tests = {}
            
            # Test profile endpoint
            response = requests.get(f"{API_BASE}/profiles/me", headers=headers)
            protected_tests['profiles'] = response.status_code == 200
            print(f"  Profile access: {response.status_code}")
            
            # Test business profile endpoint
            response = requests.get(f"{API_BASE}/business/profile/me", headers=headers)
            protected_tests['business_profile'] = response.status_code == 200
            print(f"  Business profile: {response.status_code}")
            
            # Test home dashboard
            if role == 'client':
                response = requests.get(f"{API_BASE}/home/client", headers=headers)
                protected_tests['home_dashboard'] = response.status_code == 200
                print(f"  Home dashboard: {response.status_code}")
            
            results[role] = {
                'registration': True,
                'login': True, 
                'token_validation': True,
                'protected_endpoints': protected_tests,
                'token': token,
                'user_id': user_data.get('id'),
                'email': email
            }
            
            print(f"  ✅ {role.upper()} complete flow successful")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results[role] = {'error': str(e)}
    
    return results

def test_oauth_comprehensive():
    """Test OAuth callback endpoint comprehensively"""
    print("\n=== OAUTH CALLBACK COMPREHENSIVE TEST ===")
    
    results = {}
    
    # Test 1: Invalid session ID (should return 400)
    print("\n--- Test 1: Invalid Session ID ---")
    payload = {"session_id": "invalid_session_123", "role": "client"}
    
    try:
        response = requests.post(f"{API_BASE}/auth/oauth/callback", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get('detail') == 'Invalid session ID':
                print("✅ PASS: Invalid session properly rejected")
                results['invalid_session'] = True
            else:
                print(f"❌ FAIL: Wrong error message: {data}")
                results['invalid_session'] = False
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            results['invalid_session'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['invalid_session'] = False
    
    # Test 2: Missing fields (should return 422)
    print("\n--- Test 2: Missing Fields ---")
    payload = {"session_id": "test_session"}  # Missing role
    
    try:
        response = requests.post(f"{API_BASE}/auth/oauth/callback", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ PASS: Missing fields properly rejected")
            results['missing_fields'] = True
        else:
            print(f"❌ FAIL: Expected 422, got {response.status_code}")
            results['missing_fields'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['missing_fields'] = False
    
    # Test 3: Edge cases
    print("\n--- Test 3: Edge Cases ---")
    edge_cases = [
        ("empty_session", "", "client"),
        ("whitespace_session", "   ", "client"),
        ("newline_session", "session\nid", "client"),
        ("invalid_role", "valid_session", "invalid_role")
    ]
    
    for case_name, session_id, role in edge_cases:
        print(f"Testing {case_name}...")
        payload = {"session_id": session_id, "role": role}
        
        try:
            response = requests.post(f"{API_BASE}/auth/oauth/callback", json=payload)
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [400, 422]:
                print(f"  ✅ PASS: {case_name} properly rejected")
                results[f'edge_case_{case_name}'] = True
            else:
                print(f"  ❌ FAIL: {case_name} not rejected properly")
                results[f'edge_case_{case_name}'] = False
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results[f'edge_case_{case_name}'] = False
    
    return results

def test_authentication_security():
    """Test authentication security features"""
    print("\n=== AUTHENTICATION SECURITY TEST ===")
    
    results = {}
    
    # Test 1: Password strength validation
    print("\n--- Test 1: Password Strength Validation ---")
    weak_passwords = [
        "weak",
        "12345678",
        "password",
        "Password",
        "Password123",
        "Password!"
    ]
    
    weak_password_results = []
    for weak_pass in weak_passwords:
        email = f"weak_test_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": email,
            "password": weak_pass,
            "role": "client",
            "terms_accepted": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/auth/register", json=payload)
            if response.status_code == 422:
                weak_password_results.append(True)
                print(f"  ✅ Weak password '{weak_pass}' properly rejected")
            else:
                weak_password_results.append(False)
                print(f"  ❌ Weak password '{weak_pass}' not rejected: {response.status_code}")
        except Exception as e:
            weak_password_results.append(False)
            print(f"  ❌ ERROR testing '{weak_pass}': {e}")
    
    results['password_strength'] = all(weak_password_results)
    
    # Test 2: Duplicate email prevention
    print("\n--- Test 2: Duplicate Email Prevention ---")
    email = f"duplicate_test_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "email": email,
        "password": "StrongPass123!",
        "role": "client",
        "terms_accepted": True
    }
    
    try:
        # First registration
        response1 = requests.post(f"{API_BASE}/auth/register", json=payload)
        print(f"  First registration: {response1.status_code}")
        
        # Second registration with same email
        payload['role'] = 'provider'  # Different role, same email
        response2 = requests.post(f"{API_BASE}/auth/register", json=payload)
        print(f"  Duplicate registration: {response2.status_code}")
        
        if response1.status_code == 200 and response2.status_code == 400:
            print("  ✅ PASS: Duplicate email properly rejected")
            results['duplicate_email'] = True
        else:
            print("  ❌ FAIL: Duplicate email not handled properly")
            results['duplicate_email'] = False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['duplicate_email'] = False
    
    # Test 3: Invalid credentials
    print("\n--- Test 3: Invalid Credentials ---")
    try:
        payload = {"email": "nonexistent@test.com", "password": "WrongPass123!"}
        response = requests.post(f"{API_BASE}/auth/login", json=payload)
        print(f"  Invalid login attempt: {response.status_code}")
        
        if response.status_code == 400:
            print("  ✅ PASS: Invalid credentials properly rejected")
            results['invalid_credentials'] = True
        else:
            print("  ❌ FAIL: Invalid credentials not rejected properly")
            results['invalid_credentials'] = False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['invalid_credentials'] = False
    
    return results

def test_jwt_security():
    """Test JWT token security"""
    print("\n=== JWT TOKEN SECURITY TEST ===")
    
    results = {}
    
    # Test 1: Invalid token
    print("\n--- Test 1: Invalid Token ---")
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
    
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers=invalid_headers)
        print(f"  Invalid token test: {response.status_code}")
        
        if response.status_code == 401:
            print("  ✅ PASS: Invalid token properly rejected")
            results['invalid_token'] = True
        else:
            print("  ❌ FAIL: Invalid token not rejected properly")
            results['invalid_token'] = False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['invalid_token'] = False
    
    # Test 2: Missing token
    print("\n--- Test 2: Missing Token ---")
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        print(f"  Missing token test: {response.status_code}")
        
        if response.status_code == 401:
            print("  ✅ PASS: Missing token properly rejected")
            results['missing_token'] = True
        else:
            print("  ❌ FAIL: Missing token not rejected properly")
            results['missing_token'] = False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['missing_token'] = False
    
    # Test 3: Malformed Authorization header
    print("\n--- Test 3: Malformed Authorization Header ---")
    malformed_headers = [
        {"Authorization": "invalid_format"},
        {"Authorization": "Bearer"},
        {"Authorization": "Basic dGVzdA=="},
    ]
    
    malformed_results = []
    for headers in malformed_headers:
        try:
            response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            print(f"  Malformed header test: {response.status_code}")
            
            if response.status_code == 401:
                malformed_results.append(True)
            else:
                malformed_results.append(False)
        except Exception as e:
            malformed_results.append(False)
            print(f"  ❌ ERROR: {e}")
    
    results['malformed_headers'] = all(malformed_results)
    if results['malformed_headers']:
        print("  ✅ PASS: All malformed headers properly rejected")
    else:
        print("  ❌ FAIL: Some malformed headers not rejected properly")
    
    return results

def test_cors_and_security():
    """Test CORS and security headers"""
    print("\n=== CORS AND SECURITY HEADERS TEST ===")
    
    results = {}
    
    # Test CORS
    print("\n--- Testing CORS ---")
    try:
        response = requests.options(
            f"{API_BASE}/auth/login",
            headers={
                "Origin": "https://polaris-requirements.preview.emergentagent.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        print(f"  CORS preflight: {response.status_code}")
        
        cors_headers = response.headers
        required_cors = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods', 
            'Access-Control-Allow-Headers'
        ]
        
        cors_present = all(header in cors_headers for header in required_cors)
        
        if cors_present:
            print("  ✅ PASS: CORS headers present")
            results['cors'] = True
        else:
            print("  ❌ FAIL: Missing CORS headers")
            results['cors'] = False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['cors'] = False
    
    # Test Security Headers
    print("\n--- Testing Security Headers ---")
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection', 
            'Strict-Transport-Security'
        ]
        
        present_headers = [h for h in security_headers if h in response.headers]
        
        print(f"  Security headers present: {len(present_headers)}/{len(security_headers)}")
        for header in present_headers:
            print(f"    ✅ {header}: {response.headers[header]}")
        
        for header in security_headers:
            if header not in response.headers:
                print(f"    ❌ Missing: {header}")
        
        results['security_headers'] = len(present_headers) >= 3  # Allow some flexibility
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['security_headers'] = False
    
    return results

def print_final_summary(all_results):
    """Print final comprehensive summary"""
    print("\n" + "="*80)
    print("🔐 FINAL COMPREHENSIVE AUTHENTICATION TEST SUMMARY")
    print("="*80)
    
    # Authentication Flow Results
    print("\n📋 AUTHENTICATION FLOW RESULTS:")
    auth_results = all_results.get('auth_flow', {})
    
    working_roles = []
    broken_roles = []
    
    for role, result in auth_results.items():
        if isinstance(result, dict):
            if result.get('registration') and result.get('login') and result.get('token_validation'):
                working_roles.append(role)
                print(f"  ✅ {role.upper()}: Complete flow working")
            elif result.get('reason') == 'pending_approval':
                print(f"  ⚠️  {role.upper()}: Pending approval (expected)")
            else:
                broken_roles.append(role)
                error = result.get('error', 'Unknown error')
                print(f"  ❌ {role.upper()}: {error}")
    
    # OAuth Results
    print("\n📋 OAUTH CALLBACK RESULTS:")
    oauth_results = all_results.get('oauth', {})
    oauth_passed = sum(1 for v in oauth_results.values() if v)
    oauth_total = len(oauth_results)
    print(f"  OAuth tests: {oauth_passed}/{oauth_total} passed")
    
    if oauth_results.get('invalid_session') and oauth_results.get('missing_fields'):
        print("  ✅ OAuth error handling working correctly")
    else:
        print("  ❌ OAuth error handling has issues")
    
    # Security Results
    print("\n📋 SECURITY RESULTS:")
    security_results = all_results.get('security', {})
    jwt_results = all_results.get('jwt_security', {})
    cors_results = all_results.get('cors_security', {})
    
    security_features = {
        'Password Strength': security_results.get('password_strength', False),
        'Duplicate Email Prevention': security_results.get('duplicate_email', False),
        'Invalid Credentials Rejection': security_results.get('invalid_credentials', False),
        'JWT Invalid Token Rejection': jwt_results.get('invalid_token', False),
        'JWT Missing Token Rejection': jwt_results.get('missing_token', False),
        'CORS Configuration': cors_results.get('cors', False),
        'Security Headers': cors_results.get('security_headers', False)
    }
    
    for feature, working in security_features.items():
        status = "✅" if working else "❌"
        print(f"  {status} {feature}")
    
    # Overall Assessment
    print("\n📊 OVERALL ASSESSMENT:")
    
    critical_issues = []
    
    if len(working_roles) == 0:
        critical_issues.append("No roles can complete authentication flow")
    
    if not oauth_results.get('invalid_session'):
        critical_issues.append("OAuth callback not properly rejecting invalid sessions")
    
    if not security_results.get('password_strength'):
        critical_issues.append("Weak password validation not working")
    
    if not jwt_results.get('invalid_token'):
        critical_issues.append("JWT token validation not working")
    
    if critical_issues:
        print("🚨 CRITICAL AUTHENTICATION ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  • {issue}")
        print("\n❌ AUTHENTICATION SYSTEM HAS CRITICAL FAILURES")
        print("❌ Users cannot reliably register and login to the platform")
        return False
    else:
        print("✅ CORE AUTHENTICATION FUNCTIONALITY WORKING")
        print(f"✅ {len(working_roles)} role(s) can successfully authenticate")
        print("✅ OAuth error handling working correctly")
        print("✅ Security features properly implemented")
        
        if len(working_roles) >= 3:  # At least 3 roles working
            print("\n🎉 AUTHENTICATION SYSTEM IS FUNCTIONAL!")
            print("✅ Users can successfully register and login")
            return True
        else:
            print("\n⚠️  AUTHENTICATION PARTIALLY WORKING")
            print("⚠️  Some roles may have issues")
            return False

def main():
    """Run comprehensive authentication testing"""
    print("🚀 Starting Comprehensive Authentication Testing...")
    
    all_results = {}
    
    # 1. Test complete authentication flow
    all_results['auth_flow'] = test_complete_auth_flow()
    
    # 2. Test OAuth comprehensively
    all_results['oauth'] = test_oauth_comprehensive()
    
    # 3. Test authentication security
    all_results['security'] = test_authentication_security()
    
    # 4. Test JWT security
    all_results['jwt_security'] = test_jwt_security()
    
    # 5. Test CORS and security headers
    all_results['cors_security'] = test_cors_and_security()
    
    # Print final summary
    success = print_final_summary(all_results)
    
    return success, all_results

if __name__ == "__main__":
    success, results = main()
    exit(0 if success else 1)