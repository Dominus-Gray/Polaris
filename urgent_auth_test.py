#!/usr/bin/env python3
"""
URGENT AUTHENTICATION TESTING
Testing QA credentials against production API as requested in review
Production URL: https://polar-docs-ai.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Production API URL
BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# QA Credentials from review request
QA_CREDENTIALS = [
    {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!", "role": "client"},
    {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!", "role": "agency"},
    {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!", "role": "provider"},
    {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!", "role": "navigator"}
]

def test_authentication():
    """Test authentication for all QA credentials"""
    print("🚨 URGENT AUTHENTICATION TESTING - PRODUCTION API")
    print(f"Testing against: {BASE_URL}")
    print(f"Test time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = []
    
    for i, cred in enumerate(QA_CREDENTIALS, 1):
        print(f"\n{i}. Testing {cred['role'].upper()} Authentication")
        print(f"   Email: {cred['email']}")
        print(f"   Password: {'*' * len(cred['password'])}")
        
        # Test login endpoint
        login_result = test_login(cred['email'], cred['password'])
        
        if login_result['success']:
            # Test auth/me endpoint with token
            me_result = test_auth_me(login_result['token'])
            
            result = {
                'credential': cred,
                'login_success': True,
                'token_length': len(login_result['token']),
                'auth_me_success': me_result['success'],
                'user_data': me_result.get('user_data'),
                'issues': []
            }
            
            if not me_result['success']:
                result['issues'].append(f"Auth/me failed: {me_result.get('error')}")
                
        else:
            result = {
                'credential': cred,
                'login_success': False,
                'token_length': 0,
                'auth_me_success': False,
                'user_data': None,
                'issues': [f"Login failed: {login_result.get('error')}"]
            }
        
        results.append(result)
        
        # Print immediate result
        if result['login_success'] and result['auth_me_success']:
            print(f"   ✅ SUCCESS: Authentication working")
            if result['user_data']:
                print(f"   📋 User ID: {result['user_data'].get('id', 'N/A')}")
                print(f"   📋 Role: {result['user_data'].get('role', 'N/A')}")
        else:
            print(f"   ❌ FAILED: {', '.join(result['issues'])}")
    
    return results

def test_login(email, password):
    """Test login endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'token': data.get('access_token', ''),
                'token_type': data.get('token_type', 'bearer')
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text[:200]}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Network error: {str(e)}"
        }

def test_auth_me(token):
    """Test auth/me endpoint with token"""
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'user_data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text[:200]}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Network error: {str(e)}"
        }

def test_additional_endpoints(token):
    """Test additional endpoints that might be needed for sign-in flow"""
    endpoints_to_test = [
        "/home/client",
        "/notifications/my", 
        "/knowledge-base/areas",
        "/assessment/schema"
    ]
    
    print(f"\n🔍 Testing Additional Endpoints")
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {endpoint}: {status}")
            
        except Exception as e:
            print(f"   {endpoint}: ❌ ERROR - {str(e)[:50]}")

def generate_summary(results):
    """Generate summary and recommendations"""
    print("\n" + "=" * 80)
    print("🎯 URGENT AUTHENTICATION TEST SUMMARY")
    print("=" * 80)
    
    successful_logins = sum(1 for r in results if r['login_success'])
    successful_auth_me = sum(1 for r in results if r['auth_me_success'])
    
    print(f"📊 Results Overview:")
    print(f"   • Login Success Rate: {successful_logins}/4 ({successful_logins/4*100:.1f}%)")
    print(f"   • Auth/Me Success Rate: {successful_auth_me}/4 ({successful_auth_me/4*100:.1f}%)")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        role = result['credential']['role'].upper()
        email = result['credential']['email']
        
        if result['login_success'] and result['auth_me_success']:
            print(f"   ✅ {role} ({email}): WORKING")
        else:
            print(f"   ❌ {role} ({email}): FAILED")
            for issue in result['issues']:
                print(f"      - {issue}")
    
    # Generate recommendations
    print(f"\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
    
    if successful_logins == 4 and successful_auth_me == 4:
        print("   ✅ All QA credentials are working correctly")
        print("   ✅ Production authentication system is operational")
        print("   💡 If user still can't sign in, check:")
        print("      - Frontend integration with backend API")
        print("      - CORS configuration")
        print("      - Frontend error handling")
        print("      - Browser console for JavaScript errors")
    
    elif successful_logins == 0:
        print("   🚨 CRITICAL: No accounts can login")
        print("   💡 Possible issues:")
        print("      - Production server is down")
        print("      - Database connectivity issues")
        print("      - Authentication service failure")
        print("      - Network/DNS issues")
    
    elif successful_logins < 4:
        print("   ⚠️  Some accounts failing to login")
        print("   💡 Possible issues:")
        print("      - Specific account data corruption")
        print("      - Role-based authentication issues")
        print("      - Account lockout or suspension")
    
    elif successful_auth_me < successful_logins:
        print("   ⚠️  Login works but token validation fails")
        print("   💡 Possible issues:")
        print("      - JWT token configuration issues")
        print("      - Session management problems")
        print("      - Token expiration issues")
    
    print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
    if successful_logins == 4 and successful_auth_me == 4:
        print("   1. ✅ Backend authentication is working - focus on frontend")
        print("   2. Check frontend login form integration")
        print("   3. Verify frontend API endpoint URLs")
        print("   4. Test complete login flow in browser")
    else:
        print("   1. 🚨 Fix backend authentication issues immediately")
        print("   2. Check production server status")
        print("   3. Verify database connectivity")
        print("   4. Review authentication service logs")

def main():
    """Main test execution"""
    try:
        # Test authentication
        results = test_authentication()
        
        # Test additional endpoints with first successful token
        successful_result = next((r for r in results if r['login_success']), None)
        if successful_result:
            test_additional_endpoints(successful_result.get('token', ''))
        
        # Generate summary
        generate_summary(results)
        
        # Return appropriate exit code
        all_working = all(r['login_success'] and r['auth_me_success'] for r in results)
        sys.exit(0 if all_working else 1)
        
    except Exception as e:
        print(f"\n🚨 CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()