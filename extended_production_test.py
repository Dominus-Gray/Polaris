#!/usr/bin/env python3
"""
Extended Production Functionality Testing for QA Credentials
Testing comprehensive functionality against: https://polar-docs-ai.preview.emergentagent.com/api

This script performs extended testing to verify QA accounts have proper access
to key platform features in the production environment.
"""

import requests
import json
import sys
from datetime import datetime

# Production URL as specified in the review request
PRODUCTION_BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# QA Credentials (we know these work from previous test)
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

def get_auth_token(email, password):
    """Get authentication token for a user"""
    try:
        login_url = f"{PRODUCTION_BASE_URL}/auth/login"
        login_data = {"email": email, "password": password}
        
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except:
        return None

def test_endpoint(token, endpoint, method='GET', data=None, expected_status=200):
    """Test a specific endpoint with authentication"""
    try:
        url = f"{PRODUCTION_BASE_URL}{endpoint}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            return {'success': False, 'error': f'Unsupported method: {method}'}
        
        success = response.status_code == expected_status
        
        return {
            'success': success,
            'status_code': response.status_code,
            'response_data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'error': None if success else f"Expected {expected_status}, got {response.status_code}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'status_code': None,
            'response_data': None,
            'error': str(e)
        }

def test_production_functionality():
    """Test comprehensive functionality in production environment"""
    print("🎯 EXTENDED PRODUCTION FUNCTIONALITY TESTING")
    print("=" * 70)
    print(f"Testing against: {PRODUCTION_BASE_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Get tokens for all users
    tokens = {}
    for cred in QA_CREDENTIALS:
        token = get_auth_token(cred['email'], cred['password'])
        if token:
            tokens[cred['role']] = token
            print(f"✅ Got token for {cred['role']}: {cred['email']}")
        else:
            print(f"❌ Failed to get token for {cred['role']}: {cred['email']}")
    
    if not tokens:
        print("❌ No tokens available - cannot proceed with functionality testing")
        return []
    
    print("\n" + "=" * 70)
    print("🔍 TESTING CORE PLATFORM FUNCTIONALITY")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Client Dashboard Access
    if 'client' in tokens:
        print("\n1. CLIENT DASHBOARD FUNCTIONALITY")
        print("-" * 40)
        
        client_tests = [
            ('/home/client', 'GET', None, 'Client dashboard data'),
            ('/assessment/schema', 'GET', None, 'Assessment schema access'),
            ('/knowledge-base/areas', 'GET', None, 'Knowledge base areas'),
            ('/notifications/my', 'GET', None, 'User notifications')
        ]
        
        for endpoint, method, data, description in client_tests:
            result = test_endpoint(tokens['client'], endpoint, method, data)
            test_results.append({
                'role': 'client',
                'endpoint': endpoint,
                'description': description,
                'result': result
            })
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {description}: {status}")
            if not result['success']:
                print(f"    Error: {result['error']}")
    
    # Test 2: Provider Dashboard Access
    if 'provider' in tokens:
        print("\n2. PROVIDER DASHBOARD FUNCTIONALITY")
        print("-" * 40)
        
        provider_tests = [
            ('/home/provider', 'GET', None, 'Provider dashboard data'),
            ('/service-requests/available', 'GET', None, 'Available service requests'),
            ('/provider/my-services', 'GET', None, 'Provider services'),
        ]
        
        for endpoint, method, data, description in provider_tests:
            result = test_endpoint(tokens['provider'], endpoint, method, data)
            test_results.append({
                'role': 'provider',
                'endpoint': endpoint,
                'description': description,
                'result': result
            })
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {description}: {status}")
            if not result['success']:
                print(f"    Error: {result['error']}")
    
    # Test 3: Navigator Dashboard Access
    if 'navigator' in tokens:
        print("\n3. NAVIGATOR DASHBOARD FUNCTIONALITY")
        print("-" * 40)
        
        navigator_tests = [
            ('/home/navigator', 'GET', None, 'Navigator dashboard data'),
            ('/navigator/agencies/pending', 'GET', None, 'Pending agencies'),
            ('/navigator/analytics/resources', 'GET', None, 'Resource analytics'),
        ]
        
        for endpoint, method, data, description in navigator_tests:
            result = test_endpoint(tokens['navigator'], endpoint, method, data)
            test_results.append({
                'role': 'navigator',
                'endpoint': endpoint,
                'description': description,
                'result': result
            })
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {description}: {status}")
            if not result['success']:
                print(f"    Error: {result['error']}")
    
    # Test 4: Agency Dashboard Access
    if 'agency' in tokens:
        print("\n4. AGENCY DASHBOARD FUNCTIONALITY")
        print("-" * 40)
        
        agency_tests = [
            ('/home/agency', 'GET', None, 'Agency dashboard data'),
            ('/agency/licenses/stats', 'GET', None, 'License statistics'),
            ('/agency/licenses', 'GET', None, 'Agency licenses'),
        ]
        
        for endpoint, method, data, description in agency_tests:
            result = test_endpoint(tokens['agency'], endpoint, method, data)
            test_results.append({
                'role': 'agency',
                'endpoint': endpoint,
                'description': description,
                'result': result
            })
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {description}: {status}")
            if not result['success']:
                print(f"    Error: {result['error']}")
    
    # Test 5: Cross-Role System Health
    print("\n5. SYSTEM HEALTH & CROSS-ROLE FUNCTIONALITY")
    print("-" * 40)
    
    system_tests = [
        ('/system/health', 'GET', None, 'System health check'),
        ('/assessment/schema/tier-based', 'GET', None, 'Tier-based assessment schema'),
    ]
    
    # Use client token for system tests
    test_token = tokens.get('client') or list(tokens.values())[0]
    
    for endpoint, method, data, description in system_tests:
        result = test_endpoint(test_token, endpoint, method, data)
        test_results.append({
            'role': 'system',
            'endpoint': endpoint,
            'description': description,
            'result': result
        })
        
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {description}: {status}")
        if not result['success']:
            print(f"    Error: {result['error']}")
    
    # Summary Report
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['result']['success'])
    
    print(f"Overall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Group results by role
    roles = {}
    for result in test_results:
        role = result['role']
        if role not in roles:
            roles[role] = {'passed': 0, 'total': 0, 'tests': []}
        roles[role]['total'] += 1
        if result['result']['success']:
            roles[role]['passed'] += 1
        roles[role]['tests'].append(result)
    
    print("\n📊 RESULTS BY ROLE:")
    for role, data in roles.items():
        success_rate = (data['passed'] / data['total']) * 100
        print(f"  {role.upper()}: {data['passed']}/{data['total']} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [t for t in data['tests'] if not t['result']['success']]
        if failed_tests:
            print(f"    Failed endpoints:")
            for test in failed_tests:
                print(f"      - {test['endpoint']}: {test['result']['error']}")
    
    # Production Readiness Assessment
    print("\n🏆 PRODUCTION READINESS ASSESSMENT:")
    if passed_tests == total_tests:
        print("  ✅ EXCELLENT - All QA accounts have full functionality access")
        print("  ✅ Production environment is fully operational for QA testing")
        print("  ✅ Users can successfully sign in and access all features")
    elif passed_tests >= total_tests * 0.8:
        print("  ⚠️ GOOD - Most functionality working with minor issues")
        print("  ⚠️ Some endpoints may need attention but core features operational")
    else:
        print("  ❌ NEEDS ATTENTION - Significant functionality issues detected")
        print("  ❌ Production environment requires fixes before user testing")
    
    return test_results

def main():
    """Main test execution"""
    print("🚀 Starting Extended Production Functionality Test...")
    print(f"Target URL: {PRODUCTION_BASE_URL}")
    
    try:
        results = test_production_functionality()
        
        # Exit with appropriate code
        failed_count = sum(1 for r in results if not r['result']['success'])
        total_count = len(results)
        
        if failed_count == 0:
            print("\n✅ ALL FUNCTIONALITY TESTS PASSED")
            print("✅ Production environment is ready for user sign-in testing")
            sys.exit(0)
        elif failed_count <= total_count * 0.2:  # 80% success rate
            print(f"\n⚠️ MOSTLY WORKING - {failed_count} minor issues detected")
            print("⚠️ Production environment is usable but may need minor fixes")
            sys.exit(0)
        else:
            print(f"\n❌ SIGNIFICANT ISSUES - {failed_count}/{total_count} tests failed")
            print("❌ Production environment needs attention before user testing")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()