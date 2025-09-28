#!/usr/bin/env python3
"""
Production Authentication Testing for QA Credentials
Testing against: https://polaris-migrate.preview.emergentagent.com/api

This script tests the 4 QA credentials against the production environment
to identify and resolve authentication issues.
"""

import requests
import json
import sys
from datetime import datetime

# Production URL as specified in the review request
PRODUCTION_BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"

# QA Credentials to test
QA_CREDENTIALS = [
    {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client"
    },
    {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "role": "provider"
    },
    {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "navigator"
    },
    {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "agency"
    }
]

def test_production_authentication():
    """Test authentication against production environment"""
    print("🎯 PRODUCTION AUTHENTICATION TESTING")
    print("=" * 60)
    print(f"Testing against: {PRODUCTION_BASE_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    for i, cred in enumerate(QA_CREDENTIALS, 1):
        print(f"\n{i}. Testing {cred['role'].upper()} Account: {cred['email']}")
        print("-" * 50)
        
        result = test_single_credential(cred)
        results.append(result)
        
        # Print immediate result
        if result['login_success']:
            print(f"✅ LOGIN SUCCESS: {cred['email']}")
            print(f"   Token Length: {len(result['token'])} characters")
            if result['auth_me_success']:
                print(f"✅ AUTH/ME SUCCESS: User authenticated")
                print(f"   User ID: {result['user_data'].get('id', 'N/A')}")
                print(f"   Role: {result['user_data'].get('role', 'N/A')}")
            else:
                print(f"❌ AUTH/ME FAILED: {result['auth_me_error']}")
        else:
            print(f"❌ LOGIN FAILED: {result['login_error']}")
            print(f"   Status Code: {result['login_status_code']}")
            print(f"   Error Details: {result['login_error_details']}")
    
    # Summary Report
    print("\n" + "=" * 60)
    print("🎯 PRODUCTION AUTHENTICATION TEST SUMMARY")
    print("=" * 60)
    
    successful_logins = sum(1 for r in results if r['login_success'])
    total_tests = len(results)
    
    print(f"Overall Success Rate: {successful_logins}/{total_tests} ({(successful_logins/total_tests)*100:.1f}%)")
    
    print("\n📊 DETAILED RESULTS:")
    for result in results:
        status = "✅ WORKING" if result['login_success'] else "❌ FAILED"
        print(f"  {result['email']}: {status}")
        if not result['login_success']:
            print(f"    Error: {result['login_error']}")
    
    # Production Environment Analysis
    print("\n🔍 PRODUCTION ENVIRONMENT ANALYSIS:")
    analyze_production_issues(results)
    
    # Actionable Solutions
    print("\n💡 ACTIONABLE SOLUTIONS:")
    provide_solutions(results)
    
    return results

def test_single_credential(cred):
    """Test a single set of credentials"""
    result = {
        'email': cred['email'],
        'role': cred['role'],
        'login_success': False,
        'login_error': None,
        'login_status_code': None,
        'login_error_details': None,
        'token': None,
        'auth_me_success': False,
        'auth_me_error': None,
        'user_data': None
    }
    
    try:
        # Test 1: Login attempt
        login_url = f"{PRODUCTION_BASE_URL}/auth/login"
        login_data = {
            "email": cred['email'],
            "password": cred['password']
        }
        
        print(f"   Attempting login to: {login_url}")
        
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        result['login_status_code'] = response.status_code
        
        if response.status_code == 200:
            login_response = response.json()
            result['login_success'] = True
            result['token'] = login_response.get('access_token', '')
            
            # Test 2: Verify token with /auth/me
            if result['token']:
                auth_me_result = test_auth_me(result['token'])
                result['auth_me_success'] = auth_me_result['success']
                result['auth_me_error'] = auth_me_result['error']
                result['user_data'] = auth_me_result['user_data']
            
        else:
            result['login_error'] = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                result['login_error_details'] = error_data
            except:
                result['login_error_details'] = response.text
                
    except requests.exceptions.ConnectionError as e:
        result['login_error'] = "Connection Error"
        result['login_error_details'] = str(e)
    except requests.exceptions.Timeout as e:
        result['login_error'] = "Timeout Error"
        result['login_error_details'] = str(e)
    except Exception as e:
        result['login_error'] = "Unexpected Error"
        result['login_error_details'] = str(e)
    
    return result

def test_auth_me(token):
    """Test the /auth/me endpoint with the provided token"""
    try:
        auth_me_url = f"{PRODUCTION_BASE_URL}/auth/me"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(auth_me_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                'success': True,
                'error': None,
                'user_data': user_data
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}",
                'user_data': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'user_data': None
        }

def analyze_production_issues(results):
    """Analyze common production environment issues"""
    
    failed_results = [r for r in results if not r['login_success']]
    
    if not failed_results:
        print("  ✅ No authentication issues detected")
        return
    
    # Analyze error patterns
    error_patterns = {}
    for result in failed_results:
        error_key = f"{result['login_status_code']}_{result['login_error']}"
        if error_key not in error_patterns:
            error_patterns[error_key] = []
        error_patterns[error_key].append(result['email'])
    
    print("  📋 Error Pattern Analysis:")
    for error_pattern, emails in error_patterns.items():
        print(f"    {error_pattern}: {', '.join(emails)}")
    
    # Check for common issues
    connection_errors = [r for r in failed_results if 'Connection Error' in str(r['login_error'])]
    if connection_errors:
        print("  🚨 CONNECTION ISSUES DETECTED:")
        print("    - Production server may be down or unreachable")
        print("    - Network connectivity issues")
        print("    - DNS resolution problems")
    
    auth_errors = [r for r in failed_results if r['login_status_code'] in [401, 403]]
    if auth_errors:
        print("  🚨 AUTHENTICATION ISSUES DETECTED:")
        print("    - QA accounts may not exist in production database")
        print("    - Passwords may be incorrect or expired")
        print("    - Accounts may be disabled or locked")
    
    server_errors = [r for r in failed_results if r['login_status_code'] in [500, 502, 503, 504]]
    if server_errors:
        print("  🚨 SERVER ISSUES DETECTED:")
        print("    - Production backend may have internal errors")
        print("    - Database connectivity issues")
        print("    - Configuration problems")

def provide_solutions(results):
    """Provide specific actionable solutions"""
    
    failed_results = [r for r in results if not r['login_success']]
    
    if not failed_results:
        print("  ✅ All QA accounts are working correctly in production")
        print("  ✅ No action required - authentication system is operational")
        return
    
    print("  🔧 IMMEDIATE ACTIONS REQUIRED:")
    
    # Solution 1: Account Creation
    missing_accounts = [r for r in failed_results if r['login_status_code'] in [401, 404]]
    if missing_accounts:
        print("\n  1. CREATE MISSING QA ACCOUNTS IN PRODUCTION:")
        print("     Run the following commands in production environment:")
        for result in missing_accounts:
            cred = next(c for c in QA_CREDENTIALS if c['email'] == result['email'])
            print(f"     - Create {result['role']} account: {result['email']}")
            print(f"       Password: {cred['password']}")
    
    # Solution 2: Database Issues
    server_errors = [r for r in failed_results if r['login_status_code'] in [500, 502, 503]]
    if server_errors:
        print("\n  2. RESOLVE PRODUCTION SERVER ISSUES:")
        print("     - Check production backend logs for errors")
        print("     - Verify MongoDB connection in production")
        print("     - Restart production services if necessary")
        print("     - Check environment variables (MONGO_URL, JWT_SECRET_KEY)")
    
    # Solution 3: Network Issues
    connection_errors = [r for r in failed_results if 'Connection Error' in str(r['login_error'])]
    if connection_errors:
        print("\n  3. RESOLVE NETWORK CONNECTIVITY:")
        print("     - Verify production URL is accessible")
        print("     - Check DNS resolution for polar-docs-ai.preview.emergentagent.com")
        print("     - Verify SSL certificate is valid")
        print("     - Check firewall and security group settings")
    
    # Solution 4: Account Activation
    print("\n  4. ACCOUNT ACTIVATION WORKFLOW:")
    print("     If accounts exist but are inactive, run the E2E workflow:")
    print("     - Navigator approval for agency accounts")
    print("     - License generation for client registration")
    print("     - Provider approval workflow")
    
    print("\n  5. VERIFICATION STEPS:")
    print("     After implementing fixes, re-run this test to verify:")
    print("     python3 production_auth_test.py")

def main():
    """Main test execution"""
    print("🚀 Starting Production Authentication Test...")
    print(f"Target URL: {PRODUCTION_BASE_URL}")
    
    try:
        results = test_production_authentication()
        
        # Exit with appropriate code
        failed_count = sum(1 for r in results if not r['login_success'])
        if failed_count == 0:
            print("\n✅ ALL TESTS PASSED - Production authentication is working")
            sys.exit(0)
        else:
            print(f"\n❌ {failed_count} TESTS FAILED - Production authentication needs attention")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()