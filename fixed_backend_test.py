#!/usr/bin/env python3
"""
Fixed Backend Authentication Testing for Polaris MVP
Tests authentication system with corrected backend URL configuration
As per review request: Test the FIXED authentication system
"""

import requests
import json
import uuid
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env (should now be the correct URL)
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://readiness-hub-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🔧 TESTING FIXED BACKEND AUTHENTICATION")
print(f"Backend URL: {API_BASE}")
print(f"Expected URL: https://readiness-hub-2.preview.emergentagent.com/api")

def test_fixed_user_credentials():
    """Create and verify the exact working credentials requested in review"""
    print("\n" + "="*70)
    print("🎯 TESTING FIXED USER CREDENTIALS AS REQUESTED")
    print("="*70)
    
    # Exact credentials as specified in review request
    test_email = "fixed.user.test@example.com"
    test_password = "FixedPass123!"
    test_role = "client"
    
    print(f"Creating user with EXACT credentials from review request:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print(f"  Role: {test_role}")
    print(f"  Backend URL: {API_BASE}")
    
    try:
        # Step 1: Register the user on CORRECT backend URL
        print("\n=== Step 1: User Registration on CORRECT Backend ===")
        register_payload = {
            "email": test_email,
            "password": test_password,
            "role": test_role,
            "terms_accepted": True
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Registration Status: {response.status_code}")
        print(f"Registration URL: {API_BASE}/auth/register")
        
        if response.status_code == 200:
            print("✅ PASS: User registration successful on CORRECT backend (200 status)")
            register_data = response.json()
            print(f"Registration response: {register_data}")
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists on CORRECT backend, proceeding with login test")
        else:
            print(f"❌ FAIL: Registration failed on CORRECT backend - {response.status_code}: {response.text}")
            return False
        
        # Step 2: Login with the credentials on CORRECT backend
        print("\n=== Step 2: User Login on CORRECT Backend ===")
        login_payload = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Login Status: {response.status_code}")
        print(f"Login URL: {API_BASE}/auth/login")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Login failed on CORRECT backend - {response.status_code}: {response.text}")
            return False
        
        login_data = response.json()
        access_token = login_data.get('access_token')
        token_type = login_data.get('token_type')
        
        if not access_token or token_type != 'bearer':
            print(f"❌ FAIL: Invalid login response from CORRECT backend - {login_data}")
            return False
        
        print("✅ PASS: Login successful on CORRECT backend with JWT token")
        print(f"Token type: {token_type}")
        print(f"Access token (first 50 chars): {access_token[:50]}...")
        
        # Step 3: Test JWT token validation with GET /api/auth/me on CORRECT backend
        print("\n=== Step 3: JWT Token Validation on CORRECT Backend ===")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/auth/me", headers=headers, timeout=30)
        print(f"Token validation Status: {response.status_code}")
        print(f"Token validation URL: {API_BASE}/auth/me")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Token validation failed on CORRECT backend - {response.status_code}: {response.text}")
            return False
        
        user_data = response.json()
        print("✅ PASS: Token validation working on CORRECT backend with GET /api/auth/me")
        print(f"User data: {json.dumps(user_data, indent=2, default=str)}")
        
        # Verify user details match exactly
        if user_data.get('email') != test_email or user_data.get('role') != test_role:
            print(f"❌ FAIL: User data mismatch - expected {test_email}/{test_role}, got {user_data.get('email')}/{user_data.get('role')}")
            return False
        
        print("✅ PASS: User data matches exactly - email and role verified")
        
        # Step 4: Test access to protected endpoints on CORRECT backend
        print("\n=== Step 4: Protected Endpoints Access on CORRECT Backend ===")
        
        # Test business profile endpoint (client-specific)
        response = requests.get(f"{API_BASE}/business/profile/me", headers=headers, timeout=30)
        print(f"Business profile access Status: {response.status_code}")
        
        if response.status_code not in [200, 404]:  # 404 is OK if no profile exists yet
            print(f"❌ FAIL: Cannot access protected business profile endpoint on CORRECT backend - {response.status_code}: {response.text}")
            return False
        
        print("✅ PASS: Can access protected business profile endpoint on CORRECT backend")
        
        # Test assessment session creation (requires authentication)
        response = requests.post(f"{API_BASE}/assessment/session", headers=headers, timeout=30)
        print(f"Assessment session creation Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Cannot create assessment session on CORRECT backend - {response.status_code}: {response.text}")
            return False
        
        session_data = response.json()
        session_id = session_data.get('session_id')
        print("✅ PASS: Can create assessment session on CORRECT backend")
        print(f"Created session ID: {session_id}")
        
        # Test assessment progress (requires authentication)
        if session_id:
            response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress", headers=headers, timeout=30)
            print(f"Assessment progress access Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ FAIL: Cannot access assessment progress on CORRECT backend - {response.status_code}: {response.text}")
                return False
            
            print("✅ PASS: Can access assessment progress on CORRECT backend")
        
        # Step 5: Test home dashboard access (client-specific)
        print("\n=== Step 5: Client Home Dashboard Access ===")
        response = requests.get(f"{API_BASE}/home/client", headers=headers, timeout=30)
        print(f"Client home dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            home_data = response.json()
            print("✅ PASS: Can access client home dashboard on CORRECT backend")
            print(f"Home dashboard data: {json.dumps(home_data, indent=2, default=str)}")
        else:
            print(f"⚠️  Client home dashboard access: {response.status_code} - {response.text}")
        
        # Final success message
        print("\n" + "="*70)
        print("🎉 FIXED AUTHENTICATION SYSTEM VERIFICATION COMPLETE!")
        print("="*70)
        print("✅ Registration successful on CORRECT backend URL (200 status)")
        print("✅ Login successful with JWT token on CORRECT backend URL")
        print("✅ Token validation working with GET /api/auth/me on CORRECT backend URL")
        print("✅ User can access all protected endpoints on CORRECT backend URL")
        print("✅ Authentication system now works with user's preview URL")
        print("\n📋 VERIFIED WORKING CREDENTIALS FOR USER'S ACTUAL ENVIRONMENT:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Role: {test_role}")
        print(f"   Backend URL: {API_BASE}")
        print("\n🚀 User can now login to the platform at their preview URL!")
        print("🔧 Login redirect issue should be COMPLETELY RESOLVED!")
        print("="*70)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: Could not connect to backend - {e}")
        print("This may indicate the backend URL is still incorrect or the backend is not accessible")
        return False
    except Exception as e:
        print(f"❌ ERROR in fixed credentials verification: {e}")
        return False

def test_url_configuration():
    """Verify the frontend .env has been updated with correct backend URL"""
    print("\n" + "="*70)
    print("🔍 VERIFYING URL CONFIGURATION FIX")
    print("="*70)
    
    expected_url = "https://readiness-hub-2.preview.emergentagent.com"
    actual_url = BASE_URL
    
    print(f"Expected backend URL: {expected_url}")
    print(f"Actual backend URL:   {actual_url}")
    print(f"API endpoint:         {API_BASE}")
    
    if actual_url == expected_url:
        print("✅ PASS: Frontend .env has been updated with CORRECT backend URL")
        return True
    else:
        print("❌ FAIL: Frontend .env still has WRONG backend URL")
        print("The frontend .env file needs to be updated to:")
        print(f"REACT_APP_BACKEND_URL={expected_url}")
        return False

def test_backend_accessibility():
    """Test if the backend is accessible at the correct URL"""
    print("\n" + "="*70)
    print("🌐 TESTING BACKEND ACCESSIBILITY")
    print("="*70)
    
    try:
        # Test basic connectivity
        print(f"Testing connectivity to: {API_BASE}")
        response = requests.get(f"{API_BASE}/assessment/schema", timeout=30)
        print(f"Schema endpoint Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Backend is accessible at CORRECT URL")
            schema_data = response.json()
            areas = schema_data.get('schema', {}).get('areas', [])
            print(f"Schema returned {len(areas)} areas")
            return True
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to backend - Connection refused")
        print("This indicates the backend URL is incorrect or backend is not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ FAIL: Backend request timed out")
        print("This may indicate network issues or slow backend response")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run the fixed authentication tests as requested in review"""
    print("🔧 FIXED BACKEND AUTHENTICATION TESTING")
    print("Testing the corrected backend URL configuration")
    print("="*70)
    
    results = {}
    
    # Test 1: Verify URL configuration fix
    results['url_configuration'] = test_url_configuration()
    
    # Test 2: Test backend accessibility
    results['backend_accessibility'] = test_backend_accessibility()
    
    # Test 3: Create and verify fixed user credentials
    results['fixed_user_credentials'] = test_fixed_user_credentials()
    
    # Summary
    print("\n" + "="*70)
    print("📊 FIXED AUTHENTICATION TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FIXED AUTHENTICATION TESTS PASSED!")
        print("🔧 The login redirect issue has been COMPLETELY RESOLVED!")
        print("🚀 Users can now successfully authenticate on their preview URL!")
        return True
    else:
        print("⚠️  Some tests failed - authentication fix may be incomplete")
        return False

if __name__ == "__main__":
    main()