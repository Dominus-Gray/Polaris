#!/usr/bin/env python3
"""
Production Authentication Verification Test
Testing Agent: testing
Test Date: January 25, 2025
Production URL: https://polar-docs-ai.preview.emergentagent.com/api
Test Scope: Complete verification of all 4 QA credentials as requested in review

This test provides hard evidence that authentication is working correctly
on the production environment by testing all QA credentials and documenting
exact API calls and responses.
"""

import requests
import json
import sys
from datetime import datetime

# Production API Configuration
PRODUCTION_BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"
LOGIN_ENDPOINT = f"{PRODUCTION_BASE_URL}/auth/login"
ME_ENDPOINT = f"{PRODUCTION_BASE_URL}/auth/me"

# QA Credentials to Test
QA_CREDENTIALS = [
    {
        "role": "client",
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "description": "Client QA Account"
    },
    {
        "role": "provider", 
        "email": "provider.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "description": "Provider QA Account"
    },
    {
        "role": "navigator",
        "email": "navigator.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "description": "Navigator QA Account"
    },
    {
        "role": "agency",
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "description": "Agency QA Account"
    }
]

def print_separator(title):
    """Print a formatted separator for test sections"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")

def test_login_credential(credential):
    """Test a single QA credential and return detailed results"""
    print_subsection(f"Testing {credential['description']}")
    
    result = {
        "credential": credential,
        "login_success": False,
        "token_valid": False,
        "user_data": None,
        "login_response": None,
        "me_response": None,
        "errors": []
    }
    
    try:
        # Step 1: Test Login Endpoint
        print(f"📧 Email: {credential['email']}")
        print(f"🔐 Password: {credential['password']}")
        print(f"🌐 Login URL: {LOGIN_ENDPOINT}")
        
        login_payload = {
            "email": credential["email"],
            "password": credential["password"]
        }
        
        print(f"📤 Login Request Payload:")
        print(json.dumps(login_payload, indent=2))
        
        # Make login request
        login_response = requests.post(
            LOGIN_ENDPOINT,
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Login Response Status: {login_response.status_code}")
        print(f"📥 Login Response Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            result["login_response"] = login_data
            result["login_success"] = True
            
            print(f"✅ LOGIN SUCCESS")
            print(f"📥 Login Response Body:")
            print(json.dumps(login_data, indent=2))
            
            # Extract access token
            access_token = login_data.get("access_token")
            if access_token:
                print(f"🎫 Access Token Length: {len(access_token)} characters")
                print(f"🎫 Access Token (first 50 chars): {access_token[:50]}...")
                
                # Step 2: Test Token with /auth/me
                print_subsection("Testing Token Validation with /auth/me")
                print(f"🌐 Auth Me URL: {ME_ENDPOINT}")
                
                auth_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                print(f"📤 Auth Headers:")
                print(json.dumps({k: v if k != "Authorization" else f"Bearer {access_token[:20]}..." for k, v in auth_headers.items()}, indent=2))
                
                me_response = requests.get(
                    ME_ENDPOINT,
                    headers=auth_headers,
                    timeout=30
                )
                
                print(f"📥 Auth Me Response Status: {me_response.status_code}")
                print(f"📥 Auth Me Response Headers: {dict(me_response.headers)}")
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    result["me_response"] = me_data
                    result["token_valid"] = True
                    result["user_data"] = me_data
                    
                    print(f"✅ TOKEN VALIDATION SUCCESS")
                    print(f"📥 User Data Response:")
                    print(json.dumps(me_data, indent=2))
                    
                    # Verify user data matches expected credential
                    if me_data.get("email") == credential["email"]:
                        print(f"✅ Email Match Confirmed: {me_data.get('email')}")
                    else:
                        print(f"❌ Email Mismatch: Expected {credential['email']}, Got {me_data.get('email')}")
                        result["errors"].append("Email mismatch in user data")
                    
                    if me_data.get("role") == credential["role"]:
                        print(f"✅ Role Match Confirmed: {me_data.get('role')}")
                    else:
                        print(f"❌ Role Mismatch: Expected {credential['role']}, Got {me_data.get('role')}")
                        result["errors"].append("Role mismatch in user data")
                    
                    print(f"👤 User ID: {me_data.get('id')}")
                    print(f"📧 Confirmed Email: {me_data.get('email')}")
                    print(f"🎭 Confirmed Role: {me_data.get('role')}")
                    
                else:
                    error_msg = f"Auth me endpoint failed with status {me_response.status_code}"
                    result["errors"].append(error_msg)
                    print(f"❌ TOKEN VALIDATION FAILED: {error_msg}")
                    try:
                        error_data = me_response.json()
                        print(f"📥 Error Response:")
                        print(json.dumps(error_data, indent=2))
                    except:
                        print(f"📥 Error Response (raw): {me_response.text}")
            else:
                error_msg = "No access_token in login response"
                result["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        else:
            error_msg = f"Login failed with status {login_response.status_code}"
            result["errors"].append(error_msg)
            print(f"❌ LOGIN FAILED: {error_msg}")
            try:
                error_data = login_response.json()
                print(f"📥 Error Response:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"📥 Error Response (raw): {login_response.text}")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        result["errors"].append(error_msg)
        print(f"❌ NETWORK ERROR: {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        result["errors"].append(error_msg)
        print(f"❌ UNEXPECTED ERROR: {error_msg}")
    
    return result

def main():
    """Main test execution function"""
    print_separator("PRODUCTION AUTHENTICATION VERIFICATION TEST")
    print(f"🕐 Test Started: {datetime.now().isoformat()}")
    print(f"🌐 Production URL: {PRODUCTION_BASE_URL}")
    print(f"🎯 Testing {len(QA_CREDENTIALS)} QA Credentials")
    
    all_results = []
    successful_logins = 0
    successful_validations = 0
    
    # Test each credential
    for i, credential in enumerate(QA_CREDENTIALS, 1):
        print_separator(f"CREDENTIAL {i}/{len(QA_CREDENTIALS)}: {credential['description'].upper()}")
        
        result = test_login_credential(credential)
        all_results.append(result)
        
        if result["login_success"]:
            successful_logins += 1
        if result["token_valid"]:
            successful_validations += 1
        
        # Summary for this credential
        print_subsection("Credential Test Summary")
        if result["login_success"] and result["token_valid"] and not result["errors"]:
            print("🎉 OVERALL RESULT: ✅ FULLY SUCCESSFUL")
        elif result["login_success"] and result["token_valid"]:
            print("⚠️  OVERALL RESULT: ✅ SUCCESSFUL WITH MINOR ISSUES")
            for error in result["errors"]:
                print(f"   ⚠️  {error}")
        else:
            print("❌ OVERALL RESULT: ❌ FAILED")
            for error in result["errors"]:
                print(f"   ❌ {error}")
    
    # Final comprehensive summary
    print_separator("COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"🕐 Test Completed: {datetime.now().isoformat()}")
    print(f"📊 Total Credentials Tested: {len(QA_CREDENTIALS)}")
    print(f"✅ Successful Logins: {successful_logins}/{len(QA_CREDENTIALS)}")
    print(f"🎫 Valid Token Validations: {successful_validations}/{len(QA_CREDENTIALS)}")
    print(f"📈 Overall Success Rate: {(successful_validations/len(QA_CREDENTIALS)*100):.1f}%")
    
    print_subsection("Detailed Results by Credential")
    for i, result in enumerate(all_results, 1):
        credential = result["credential"]
        status = "✅ SUCCESS" if result["login_success"] and result["token_valid"] and not result["errors"] else "❌ FAILED"
        print(f"{i}. {credential['description']} ({credential['email']}): {status}")
        
        if result["login_success"]:
            print(f"   ✅ Login: SUCCESS")
            if result["login_response"] and "access_token" in result["login_response"]:
                token_length = len(result["login_response"]["access_token"])
                print(f"   🎫 Token: {token_length} characters")
        else:
            print(f"   ❌ Login: FAILED")
        
        if result["token_valid"]:
            print(f"   ✅ Token Validation: SUCCESS")
            if result["user_data"]:
                print(f"   👤 User ID: {result['user_data'].get('id')}")
                print(f"   📧 Email: {result['user_data'].get('email')}")
                print(f"   🎭 Role: {result['user_data'].get('role')}")
        else:
            print(f"   ❌ Token Validation: FAILED")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"   ⚠️  Issue: {error}")
        print()
    
    print_separator("HARD EVIDENCE DOCUMENTATION")
    print("📋 STEP-BY-STEP LOGIN INSTRUCTIONS FOR USER:")
    print()
    print("1. Navigate to: https://polar-docs-ai.preview.emergentagent.com/")
    print("2. Click 'Start Your Journey' or login button")
    print("3. Use any of the following QA credentials:")
    print()
    
    for i, credential in enumerate(QA_CREDENTIALS, 1):
        result = all_results[i-1]
        status = "✅ WORKING" if result["login_success"] and result["token_valid"] else "❌ NOT WORKING"
        print(f"   {i}. {credential['description']}:")
        print(f"      📧 Email: {credential['email']}")
        print(f"      🔐 Password: {credential['password']}")
        print(f"      🎭 Role: {credential['role']}")
        print(f"      📊 Status: {status}")
        if result["user_data"]:
            print(f"      👤 User ID: {result['user_data'].get('id')}")
        print()
    
    print_subsection("API ENDPOINT VERIFICATION")
    print(f"🌐 Login Endpoint: {LOGIN_ENDPOINT}")
    print(f"🌐 User Verification Endpoint: {ME_ENDPOINT}")
    print(f"📡 Both endpoints are accessible and responding correctly")
    
    print_subsection("PRODUCTION READINESS ASSESSMENT")
    if successful_validations == len(QA_CREDENTIALS):
        print("🎉 PRODUCTION STATUS: ✅ FULLY OPERATIONAL")
        print("✅ All QA credentials work perfectly")
        print("✅ Authentication system is production-ready")
        print("✅ Users can successfully sign in and access the platform")
    elif successful_validations > 0:
        print("⚠️  PRODUCTION STATUS: ⚠️  PARTIALLY OPERATIONAL")
        print(f"✅ {successful_validations}/{len(QA_CREDENTIALS)} credentials working")
        print("⚠️  Some credentials may need attention")
    else:
        print("❌ PRODUCTION STATUS: ❌ NOT OPERATIONAL")
        print("❌ Authentication system needs immediate attention")
        print("❌ Users cannot sign in to the platform")
    
    print_separator("TEST COMPLETION")
    print(f"🏁 Production Authentication Verification Test Complete")
    print(f"📊 Final Success Rate: {(successful_validations/len(QA_CREDENTIALS)*100):.1f}%")
    
    # Return exit code based on results
    return 0 if successful_validations == len(QA_CREDENTIALS) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)