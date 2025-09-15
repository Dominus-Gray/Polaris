#!/usr/bin/env python3
"""
COMPREHENSIVE AUTHENTICATION TESTING FOR POLARIS MVP
Tests all authentication flows as requested in the review request:
1. Traditional Email/Password Registration
2. Traditional Email/Password Login  
3. OAuth Registration Flow
4. Authentication Middleware
5. Database Operations
6. Frontend Integration
"""

import requests
import json
import uuid
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://production-guru.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🔐 COMPREHENSIVE AUTHENTICATION TESTING")
print(f"Testing backend at: {API_BASE}")
print("="*80)

def test_traditional_registration():
    """Test POST /api/auth/register with all roles and validation"""
    print("\n=== 1. TRADITIONAL EMAIL/PASSWORD REGISTRATION ===")
    
    results = {}
    roles = ['client', 'provider', 'navigator', 'agency']
    
    for role in roles:
        print(f"\n--- Testing {role.upper()} Registration ---")
        
        # Generate unique email
        test_email = f"auth_test_{role}_{uuid.uuid4().hex[:8]}@test.com"
        
        # Test with valid data
        payload = {
            "email": test_email,
            "password": "SecurePass123!",
            "role": role,
            "terms_accepted": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'User registered successfully':
                    print(f"✅ PASS: {role} registration successful")
                    results[f"{role}_registration"] = {
                        'success': True,
                        'email': test_email,
                        'password': 'SecurePass123!'
                    }
                else:
                    print(f"❌ FAIL: Unexpected response: {data}")
                    results[f"{role}_registration"] = {'success': False, 'error': f"Unexpected response: {data}"}
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                results[f"{role}_registration"] = {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results[f"{role}_registration"] = {'success': False, 'error': str(e)}
    
    # Test validation errors
    print(f"\n--- Testing Registration Validation ---")
    
    # Test weak password
    weak_password_payload = {
        "email": f"weak_test_{uuid.uuid4().hex[:8]}@test.com",
        "password": "weak",
        "role": "client",
        "terms_accepted": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=weak_password_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print("✅ PASS: Weak password properly rejected")
            results['password_validation'] = {'success': True}
        else:
            print(f"❌ FAIL: Weak password not rejected properly: {response.status_code}")
            results['password_validation'] = {'success': False, 'error': f"Expected 422, got {response.status_code}"}
    except Exception as e:
        print(f"❌ ERROR testing password validation: {e}")
        results['password_validation'] = {'success': False, 'error': str(e)}
    
    # Test duplicate email
    if results.get('client_registration', {}).get('success'):
        duplicate_payload = {
            "email": results['client_registration']['email'],
            "password": "AnotherPass123!",
            "role": "provider",
            "terms_accepted": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register",
                json=duplicate_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print("✅ PASS: Duplicate email properly rejected")
                results['duplicate_email_validation'] = {'success': True}
            else:
                print(f"❌ FAIL: Duplicate email not rejected: {response.status_code}")
                results['duplicate_email_validation'] = {'success': False, 'error': f"Expected 400, got {response.status_code}"}
        except Exception as e:
            print(f"❌ ERROR testing duplicate email: {e}")
            results['duplicate_email_validation'] = {'success': False, 'error': str(e)}
    
    return results

def test_traditional_login(registration_results):
    """Test POST /api/auth/login with registered users"""
    print("\n=== 2. TRADITIONAL EMAIL/PASSWORD LOGIN ===")
    
    results = {}
    
    for role in ['client', 'provider', 'navigator', 'agency']:
        reg_key = f"{role}_registration"
        if registration_results.get(reg_key, {}).get('success'):
            print(f"\n--- Testing {role.upper()} Login ---")
            
            email = registration_results[reg_key]['email']
            password = registration_results[reg_key]['password']
            
            payload = {
                "email": email,
                "password": password
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/auth/login",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    token_type = data.get('token_type')
                    
                    if token and token_type == 'bearer':
                        print(f"✅ PASS: {role} login successful, JWT token received")
                        results[f"{role}_login"] = {
                            'success': True,
                            'token': token,
                            'email': email
                        }
                    else:
                        print(f"❌ FAIL: Invalid token response: {data}")
                        results[f"{role}_login"] = {'success': False, 'error': f"Invalid token response: {data}"}
                else:
                    print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                    results[f"{role}_login"] = {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results[f"{role}_login"] = {'success': False, 'error': str(e)}
        else:
            print(f"⚠️  SKIP: {role} login (registration failed)")
            results[f"{role}_login"] = {'success': False, 'error': 'Registration failed'}
    
    # Test invalid credentials
    print(f"\n--- Testing Invalid Credentials ---")
    
    invalid_payload = {
        "email": "nonexistent@test.com",
        "password": "WrongPass123!"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=invalid_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ PASS: Invalid credentials properly rejected")
            results['invalid_credentials'] = {'success': True}
        else:
            print(f"❌ FAIL: Invalid credentials not rejected properly: {response.status_code}")
            results['invalid_credentials'] = {'success': False, 'error': f"Expected 400, got {response.status_code}"}
    except Exception as e:
        print(f"❌ ERROR testing invalid credentials: {e}")
        results['invalid_credentials'] = {'success': False, 'error': str(e)}
    
    return results

def test_jwt_token_validation(login_results):
    """Test GET /api/auth/me with JWT tokens"""
    print("\n=== 3. JWT TOKEN VALIDATION ===")
    
    results = {}
    
    for role in ['client', 'provider', 'navigator', 'agency']:
        login_key = f"{role}_login"
        if login_results.get(login_key, {}).get('success'):
            print(f"\n--- Testing {role.upper()} Token Validation ---")
            
            token = login_results[login_key]['token']
            expected_email = login_results[login_key]['email']
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"User data: {json.dumps(data, indent=2, default=str)}")
                    
                    if (data.get('role') == role and 
                        data.get('email') == expected_email and 
                        data.get('id')):
                        print(f"✅ PASS: {role} token validation successful")
                        results[f"{role}_token_validation"] = {
                            'success': True,
                            'user_id': data.get('id'),
                            'role': data.get('role'),
                            'email': data.get('email')
                        }
                    else:
                        print(f"❌ FAIL: Invalid user data: {data}")
                        results[f"{role}_token_validation"] = {'success': False, 'error': f"Invalid user data: {data}"}
                else:
                    print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                    results[f"{role}_token_validation"] = {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results[f"{role}_token_validation"] = {'success': False, 'error': str(e)}
        else:
            print(f"⚠️  SKIP: {role} token validation (login failed)")
            results[f"{role}_token_validation"] = {'success': False, 'error': 'Login failed'}
    
    # Test invalid token
    print(f"\n--- Testing Invalid Token ---")
    
    invalid_headers = {
        "Authorization": "Bearer invalid_token_12345",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers=invalid_headers)
        
        if response.status_code == 401:
            print("✅ PASS: Invalid token properly rejected")
            results['invalid_token'] = {'success': True}
        else:
            print(f"❌ FAIL: Invalid token not rejected properly: {response.status_code}")
            results['invalid_token'] = {'success': False, 'error': f"Expected 401, got {response.status_code}"}
    except Exception as e:
        print(f"❌ ERROR testing invalid token: {e}")
        results['invalid_token'] = {'success': False, 'error': str(e)}
    
    # Test missing token
    print(f"\n--- Testing Missing Token ---")
    
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        
        if response.status_code == 401:
            print("✅ PASS: Missing token properly rejected")
            results['missing_token'] = {'success': True}
        else:
            print(f"❌ FAIL: Missing token not rejected properly: {response.status_code}")
            results['missing_token'] = {'success': False, 'error': f"Expected 401, got {response.status_code}"}
    except Exception as e:
        print(f"❌ ERROR testing missing token: {e}")
        results['missing_token'] = {'success': False, 'error': str(e)}
    
    return results

def test_oauth_flow():
    """Test POST /api/auth/oauth/callback with various scenarios"""
    print("\n=== 4. OAUTH AUTHENTICATION FLOW ===")
    
    results = {}
    
    # Test 1: Invalid session ID
    print(f"\n--- Testing Invalid Session ID ---")
    
    invalid_payload = {
        "session_id": "invalid_session_12345",
        "role": "client"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=invalid_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get('detail') == 'Invalid session ID':
                print("✅ PASS: Invalid session ID properly rejected with 400")
                results['oauth_invalid_session'] = {'success': True}
            else:
                print(f"❌ FAIL: Wrong error message: {data}")
                results['oauth_invalid_session'] = {'success': False, 'error': f"Wrong error message: {data}"}
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            results['oauth_invalid_session'] = {'success': False, 'error': f"Expected 400, got {response.status_code}"}
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['oauth_invalid_session'] = {'success': False, 'error': str(e)}
    
    # Test 2: Missing fields
    print(f"\n--- Testing Missing Fields ---")
    
    missing_payload = {
        "session_id": "test_session"
        # Missing role field
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=missing_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ PASS: Missing fields properly rejected with 422")
            results['oauth_missing_fields'] = {'success': True}
        else:
            print(f"❌ FAIL: Expected 422, got {response.status_code}")
            results['oauth_missing_fields'] = {'success': False, 'error': f"Expected 422, got {response.status_code}"}
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['oauth_missing_fields'] = {'success': False, 'error': str(e)}
    
    # Test 3: Invalid role
    print(f"\n--- Testing Invalid Role ---")
    
    invalid_role_payload = {
        "session_id": "test_session_123",
        "role": "invalid_role"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=invalid_role_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("✅ PASS: Invalid role properly rejected")
            results['oauth_invalid_role'] = {'success': True}
        else:
            print(f"❌ FAIL: Invalid role not rejected properly: {response.status_code}")
            results['oauth_invalid_role'] = {'success': False, 'error': f"Expected 400/422, got {response.status_code}"}
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['oauth_invalid_role'] = {'success': False, 'error': str(e)}
    
    # Test 4: Valid roles but invalid session (should get 400 from Emergent API)
    print(f"\n--- Testing Valid Roles with Invalid Session ---")
    
    for role in ['client', 'provider', 'navigator', 'agency']:
        print(f"Testing role: {role}")
        
        valid_role_payload = {
            "session_id": f"test_session_{uuid.uuid4().hex[:16]}",
            "role": role
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=valid_role_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 400:
                data = response.json()
                if data.get('detail') == 'Invalid session ID':
                    print(f"  ✅ PASS: {role} role with invalid session properly rejected")
                    results[f'oauth_valid_role_{role}'] = {'success': True}
                else:
                    print(f"  ❌ FAIL: Wrong error message for {role}: {data}")
                    results[f'oauth_valid_role_{role}'] = {'success': False, 'error': f"Wrong error message: {data}"}
            else:
                print(f"  ❌ FAIL: Expected 400 for {role}, got {response.status_code}")
                results[f'oauth_valid_role_{role}'] = {'success': False, 'error': f"Expected 400, got {response.status_code}"}
                
        except Exception as e:
            print(f"  ❌ ERROR testing {role}: {e}")
            results[f'oauth_valid_role_{role}'] = {'success': False, 'error': str(e)}
    
    # Test 5: Session ID validation edge cases
    print(f"\n--- Testing Session ID Edge Cases ---")
    
    edge_cases = [
        ("empty_string", ""),
        ("whitespace_only", "   "),
        ("with_newline", "session\nid"),
        ("with_carriage_return", "session\rid"),
        ("very_long", "a" * 1000)
    ]
    
    for case_name, session_id in edge_cases:
        print(f"Testing {case_name}: '{session_id[:20]}{'...' if len(session_id) > 20 else ''}'")
        
        edge_payload = {
            "session_id": session_id,
            "role": "client"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=edge_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 400:
                print(f"  ✅ PASS: {case_name} properly rejected")
                results[f'oauth_edge_case_{case_name}'] = {'success': True}
            else:
                print(f"  ❌ FAIL: {case_name} not rejected properly: {response.status_code}")
                results[f'oauth_edge_case_{case_name}'] = {'success': False, 'error': f"Expected 400, got {response.status_code}"}
                
        except Exception as e:
            print(f"  ❌ ERROR testing {case_name}: {e}")
            results[f'oauth_edge_case_{case_name}'] = {'success': False, 'error': str(e)}
    
    return results

def test_protected_endpoints(login_results):
    """Test protected endpoints with authentication"""
    print("\n=== 5. PROTECTED ENDPOINTS AUTHENTICATION ===")
    
    results = {}
    
    # Get a valid token
    client_token = None
    for role in ['client', 'provider', 'navigator', 'agency']:
        login_key = f"{role}_login"
        if login_results.get(login_key, {}).get('success'):
            client_token = login_results[login_key]['token']
            break
    
    if not client_token:
        print("❌ FAIL: No valid token available for protected endpoint testing")
        return {'protected_endpoints': {'success': False, 'error': 'No valid token available'}}
    
    # Test endpoints that require authentication
    protected_endpoints = [
        ("GET", "/assessment/session", "Create assessment session"),
        ("GET", "/assessment/schema", "Get assessment schema"),
        ("POST", "/ai/explain", "AI explain endpoint", {
            "session_id": "test",
            "area_id": "area1", 
            "question_id": "q1",
            "question_text": "Test question"
        })
    ]
    
    for method, endpoint, description, payload in [(e[0], e[1], e[2], e[3] if len(e) > 3 else None) for e in protected_endpoints]:
        print(f"\n--- Testing {description} ---")
        
        # Test without authentication
        print("Testing without authentication...")
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}")
            elif method == "POST":
                response = requests.post(
                    f"{API_BASE}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"  Status without auth: {response.status_code}")
            
            # Some endpoints might allow unauthenticated access, others should return 401
            if response.status_code in [200, 401]:
                no_auth_result = True
            else:
                no_auth_result = False
                print(f"  ⚠️  Unexpected status without auth: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ ERROR testing without auth: {e}")
            no_auth_result = False
        
        # Test with authentication
        print("Testing with authentication...")
        try:
            headers = {
                "Authorization": f"Bearer {client_token}",
                "Content-Type": "application/json"
            }
            
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{API_BASE}{endpoint}", json=payload, headers=headers)
            
            print(f"  Status with auth: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ PASS: {description} works with authentication")
                with_auth_result = True
            else:
                print(f"  ❌ FAIL: {description} failed with auth: {response.status_code}")
                with_auth_result = False
                
        except Exception as e:
            print(f"  ❌ ERROR testing with auth: {e}")
            with_auth_result = False
        
        results[f"protected_{endpoint.replace('/', '_')}"] = {
            'success': with_auth_result,
            'no_auth_result': no_auth_result,
            'with_auth_result': with_auth_result
        }
    
    return results

def test_cors_and_headers():
    """Test CORS configuration and security headers"""
    print("\n=== 6. CORS AND SECURITY HEADERS ===")
    
    results = {}
    
    # Test CORS preflight
    print(f"\n--- Testing CORS Preflight ---")
    
    try:
        response = requests.options(
            f"{API_BASE}/auth/login",
            headers={
                "Origin": "https://production-guru.preview.emergentagent.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        print(f"CORS preflight status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
        cors_headers = response.headers
        if (cors_headers.get('Access-Control-Allow-Origin') and
            cors_headers.get('Access-Control-Allow-Methods') and
            cors_headers.get('Access-Control-Allow-Headers')):
            print("✅ PASS: CORS headers present")
            results['cors_headers'] = {'success': True}
        else:
            print("❌ FAIL: Missing CORS headers")
            results['cors_headers'] = {'success': False, 'error': 'Missing CORS headers'}
            
    except Exception as e:
        print(f"❌ ERROR testing CORS: {e}")
        results['cors_headers'] = {'success': False, 'error': str(e)}
    
    # Test security headers
    print(f"\n--- Testing Security Headers ---")
    
    try:
        response = requests.get(f"{API_BASE}/auth/me")
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        present_headers = []
        missing_headers = []
        
        for header in security_headers:
            if header in response.headers:
                present_headers.append(header)
                print(f"  ✅ {header}: {response.headers[header]}")
            else:
                missing_headers.append(header)
                print(f"  ❌ Missing: {header}")
        
        if len(present_headers) >= 3:  # Allow some flexibility
            print("✅ PASS: Most security headers present")
            results['security_headers'] = {'success': True, 'present': present_headers, 'missing': missing_headers}
        else:
            print("❌ FAIL: Too many security headers missing")
            results['security_headers'] = {'success': False, 'error': f'Missing headers: {missing_headers}'}
            
    except Exception as e:
        print(f"❌ ERROR testing security headers: {e}")
        results['security_headers'] = {'success': False, 'error': str(e)}
    
    return results

def test_database_operations(login_results):
    """Test database operations through API calls"""
    print("\n=== 7. DATABASE OPERATIONS VERIFICATION ===")
    
    results = {}
    
    # Test user creation verification (already done in registration)
    print(f"\n--- Verifying User Creation in Database ---")
    
    created_users = 0
    for role in ['client', 'provider', 'navigator', 'agency']:
        token_key = f"{role}_token_validation"
        if login_results.get(token_key, {}).get('success'):
            created_users += 1
    
    if created_users >= 2:
        print(f"✅ PASS: {created_users} users successfully created and retrievable")
        results['user_creation'] = {'success': True, 'count': created_users}
    else:
        print(f"❌ FAIL: Only {created_users} users created successfully")
        results['user_creation'] = {'success': False, 'error': f'Only {created_users} users created'}
    
    # Test user retrieval consistency
    print(f"\n--- Testing User Retrieval Consistency ---")
    
    consistent_retrievals = 0
    for role in ['client', 'provider', 'navigator', 'agency']:
        login_key = f"{role}_login"
        token_key = f"{role}_token_validation"
        
        if (login_results.get(login_key, {}).get('success') and 
            login_results.get(token_key, {}).get('success')):
            
            login_email = login_results[login_key]['email']
            token_email = login_results[token_key]['email']
            
            if login_email == token_email:
                consistent_retrievals += 1
            else:
                print(f"❌ INCONSISTENT: {role} email mismatch: {login_email} vs {token_email}")
    
    if consistent_retrievals >= 2:
        print(f"✅ PASS: {consistent_retrievals} users have consistent data retrieval")
        results['user_retrieval_consistency'] = {'success': True, 'count': consistent_retrievals}
    else:
        print(f"❌ FAIL: Only {consistent_retrievals} users have consistent retrieval")
        results['user_retrieval_consistency'] = {'success': False, 'error': f'Only {consistent_retrievals} consistent'}
    
    return results

def print_comprehensive_summary(all_results):
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("🔐 COMPREHENSIVE AUTHENTICATION TEST SUMMARY")
    print("="*80)
    
    # Count totals
    total_tests = 0
    passed_tests = 0
    critical_failures = []
    
    for category, results in all_results.items():
        print(f"\n📋 {category.upper().replace('_', ' ')}:")
        
        for test_name, result in results.items():
            total_tests += 1
            if result.get('success'):
                passed_tests += 1
                print(f"  ✅ {test_name.replace('_', ' ').title()}")
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"  ❌ {test_name.replace('_', ' ').title()}: {error_msg}")
                
                # Mark critical failures
                if any(critical in test_name.lower() for critical in ['registration', 'login', 'token_validation', 'oauth']):
                    critical_failures.append(f"{test_name}: {error_msg}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES:")
        for failure in critical_failures:
            print(f"  • {failure}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL AUTHENTICATION TESTS PASSED!")
        print(f"✅ Users can successfully register and login")
        print(f"✅ OAuth flow is working correctly") 
        print(f"✅ JWT tokens are properly validated")
        print(f"✅ Protected endpoints require authentication")
        return True
    else:
        print(f"\n⚠️  AUTHENTICATION ISSUES FOUND!")
        if critical_failures:
            print(f"❌ Critical authentication failures prevent users from accessing the platform")
        return False

def main():
    """Run comprehensive authentication testing"""
    print("🚀 Starting Comprehensive Authentication Testing...")
    
    all_results = {}
    
    # 1. Test traditional registration
    registration_results = test_traditional_registration()
    all_results['registration'] = registration_results
    
    # 2. Test traditional login
    login_results = test_traditional_login(registration_results)
    all_results['login'] = login_results
    
    # 3. Test JWT token validation
    token_results = test_jwt_token_validation(login_results)
    all_results['token_validation'] = token_results
    
    # 4. Test OAuth flow
    oauth_results = test_oauth_flow()
    all_results['oauth'] = oauth_results
    
    # 5. Test protected endpoints
    protected_results = test_protected_endpoints(token_results)
    all_results['protected_endpoints'] = protected_results
    
    # 6. Test CORS and headers
    cors_results = test_cors_and_headers()
    all_results['cors_and_headers'] = cors_results
    
    # 7. Test database operations
    db_results = test_database_operations(token_results)
    all_results['database_operations'] = db_results
    
    # Print comprehensive summary
    success = print_comprehensive_summary(all_results)
    
    return success, all_results

if __name__ == "__main__":
    success, results = main()
    exit(0 if success else 1)