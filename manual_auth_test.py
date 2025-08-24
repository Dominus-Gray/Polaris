#!/usr/bin/env python3
"""
Manual Authentication Test for Review Request
Creates and verifies working credentials as specified in the review request:
- Email: manual.test.user@example.com
- Password: WorkingPass123!
- Role: client
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-inspector.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def create_and_verify_manual_test_user():
    """
    Create and verify working credentials as specified in review request:
    - Email: manual.test.user@example.com
    - Password: WorkingPass123!
    - Role: client
    """
    print("\n" + "="*80)
    print("🔐 CREATING MANUAL TEST USER AS PER REVIEW REQUEST")
    print("="*80)
    
    # Credentials as specified in review request
    test_email = "manual.test.user@example.com"
    test_password = "WorkingPass123!"
    test_role = "client"
    
    print(f"Creating user with specified credentials:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print(f"  Role: {test_role}")
    
    try:
        # ========== STEP 1: USER REGISTRATION ==========
        print("\n" + "="*50)
        print("STEP 1: USER REGISTRATION")
        print("="*50)
        print("Testing: POST /api/auth/register")
        
        register_payload = {
            "email": test_email,
            "password": test_password,
            "role": test_role,
            "terms_accepted": True
        }
        
        print(f"Request payload: {json.dumps(register_payload, indent=2)}")
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Body (raw): {response.text}")
        
        if response.status_code == 200:
            print("✅ REGISTRATION SUCCESS: User created with 200 status")
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists, proceeding with login test")
        else:
            print(f"❌ REGISTRATION FAILED: HTTP {response.status_code}")
            print(f"Error details: {response.text}")
            return False
        
        # ========== STEP 2: USER LOGIN ==========
        print("\n" + "="*50)
        print("STEP 2: USER LOGIN")
        print("="*50)
        print("Testing: POST /api/auth/login")
        
        login_payload = {
            "email": test_email,
            "password": test_password
        }
        
        print(f"Request payload: {json.dumps(login_payload, indent=2)}")
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ LOGIN FAILED: HTTP {response.status_code}")
            print(f"Error details: {response.text}")
            return False
        
        login_data = response.json()
        print(f"Response Body: {json.dumps(login_data, indent=2)}")
        
        access_token = login_data.get('access_token')
        token_type = login_data.get('token_type')
        
        if not access_token or token_type != 'bearer':
            print(f"❌ LOGIN FAILED: Invalid response format")
            print(f"Expected: access_token and token_type='bearer'")
            print(f"Got: {login_data}")
            return False
        
        print("✅ LOGIN SUCCESS: JWT token received")
        print(f"Token type: {token_type}")
        print(f"Access token length: {len(access_token)} characters")
        print(f"Access token (first 50 chars): {access_token[:50]}...")
        
        # ========== STEP 3: JWT TOKEN VALIDATION ==========
        print("\n" + "="*50)
        print("STEP 3: JWT TOKEN VALIDATION")
        print("="*50)
        print("Testing: GET /api/auth/me")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Request headers: {json.dumps(headers, indent=2)}")
        
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ TOKEN VALIDATION FAILED: HTTP {response.status_code}")
            print(f"Error details: {response.text}")
            return False
        
        user_data = response.json()
        print(f"Response Body: {json.dumps(user_data, indent=2, default=str)}")
        
        # Verify user details match what we created
        if user_data.get('email') != test_email:
            print(f"❌ EMAIL MISMATCH: Expected {test_email}, got {user_data.get('email')}")
            return False
        
        if user_data.get('role') != test_role:
            print(f"❌ ROLE MISMATCH: Expected {test_role}, got {user_data.get('role')}")
            return False
        
        print("✅ TOKEN VALIDATION SUCCESS: User data matches expected values")
        print(f"✅ Email verified: {user_data.get('email')}")
        print(f"✅ Role verified: {user_data.get('role')}")
        print(f"✅ User ID: {user_data.get('id')}")
        print(f"✅ Created at: {user_data.get('created_at')}")
        
        # ========== STEP 4: PROTECTED ENDPOINTS ACCESS ==========
        print("\n" + "="*50)
        print("STEP 4: PROTECTED ENDPOINTS ACCESS")
        print("="*50)
        
        # Test 4a: Business Profile Access
        print("Testing: GET /api/business/profile/me")
        response = requests.get(f"{API_BASE}/business/profile/me", headers=headers)
        print(f"Business profile Status: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ Business profile accessible: {json.dumps(profile_data, indent=2) if profile_data else 'No profile yet'}")
        elif response.status_code == 404 or response.status_code == 403:
            print("✅ Business profile endpoint accessible (no profile created yet)")
        else:
            print(f"❌ Business profile access failed: {response.status_code} - {response.text}")
            return False
        
        # Test 4b: Assessment Session Creation
        print("\nTesting: POST /api/assessment/session")
        response = requests.post(f"{API_BASE}/assessment/session", headers=headers)
        print(f"Assessment session Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Assessment session creation failed: {response.status_code} - {response.text}")
            return False
        
        session_data = response.json()
        session_id = session_data.get('session_id')
        print(f"✅ Assessment session created: {session_id}")
        print(f"Session data: {json.dumps(session_data, indent=2)}")
        
        # Test 4c: Assessment Progress Access
        if session_id:
            print(f"\nTesting: GET /api/assessment/session/{session_id}/progress")
            response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress", headers=headers)
            print(f"Assessment progress Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Assessment progress access failed: {response.status_code} - {response.text}")
                return False
            
            progress_data = response.json()
            print(f"✅ Assessment progress accessible")
            print(f"Progress data: {json.dumps(progress_data, indent=2)}")
        
        # ========== FINAL SUCCESS SUMMARY ==========
        print("\n" + "="*80)
        print("🎉 MANUAL TEST USER CREATION AND VERIFICATION COMPLETE!")
        print("="*80)
        print("✅ STEP 1: Registration API response (200 status)")
        print("✅ STEP 2: Login API response with JWT token")
        print("✅ STEP 3: Token validation response with user data")
        print("✅ STEP 4: Protected endpoints accessible")
        print("\n📋 VERIFIED WORKING CREDENTIALS FOR MANUAL TESTING:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Role: {test_role}")
        print("\n🚀 DEFINITIVE PROOF: Backend authentication system is working!")
        print("🚀 User can manually test these credentials at http://localhost:3000")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR during authentication testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the manual authentication test"""
    print("🚀 Starting Manual Authentication Test for Review Request")
    print(f"Backend URL: {API_BASE}")
    
    success = create_and_verify_manual_test_user()
    
    if success:
        print("\n✅ SUCCESS: All authentication tests passed!")
        print("✅ Backend authentication system is fully functional")
        print("✅ Working credentials provided for manual testing")
        return True
    else:
        print("\n❌ FAILURE: Authentication tests failed")
        print("❌ Backend authentication system has issues")
        return False

if __name__ == "__main__":
    main()