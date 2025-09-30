#!/usr/bin/env python3
"""
Critical Endpoints Verification Test
Final verification test to confirm 100% completion after fixing all critical endpoints.

Testing the 8 critical endpoints that were failing:
1. Assessment Tier Session Creation - POST /assessment/tier-session (was 422, should be 200)
2. Knowledge Base Areas with Area10 - GET /knowledge-base/areas (should return 10 areas including area10)
3. Provider Opportunities - GET /service-requests/opportunities (was 403, should be 200)
4. Agency License Generation - POST /agency/licenses/generate (was 403, should be 200)
5. Service Request Creation - POST /service-requests/professional-help (should still work)
6. AI Assistance - POST /knowledge-base/ai-assistance (should still work)
7. Navigator Evidence Review - GET /navigator/evidence/pending (should still work)
8. Template Generation - GET /knowledge-base/generate-template/area10/template (should still work)

QA Credentials:
- client.qa@polaris.example.com / Polaris#2025!
- provider.qa@polaris.example.com / Polaris#2025!
- agency.qa@polaris.example.com / Polaris#2025!
- navigator.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CriticalEndpointsTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Polaris-Critical-Endpoints-Tester/1.0'
        })

    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} ({response_time:.3f}s)")
        if details:
            print(f"   Details: {details}")

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            start_time = time.time()
            credentials = QA_CREDENTIALS[role]
            
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=credentials,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token') or data.get('access_token')
                if token:
                    self.tokens[role] = token
                    self.log_test(
                        f"{role.title()} Authentication",
                        True,
                        f"Token length: {len(token)} chars",
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        f"{role.title()} Authentication",
                        False,
                        f"No token in response: {data}",
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    f"{role.title()} Authentication",
                    False,
                    f"Status {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_test(
                f"{role.title()} Authentication",
                False,
                f"Exception: {str(e)}",
                0
            )
            return False

    def make_authenticated_request(self, method, endpoint, role, data=None, params=None, use_form_data=False):
        """Make authenticated request"""
        if role not in self.tokens:
            return None, f"No token for role {role}"
        
        headers = {
            'Authorization': f'Bearer {self.tokens[role]}'
        }
        
        # Don't set Content-Type for form data - let requests handle it
        if not use_form_data:
            headers['Content-Type'] = 'application/json'
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    params=params,
                    timeout=10
                )
            elif method.upper() == 'POST':
                # Debug: Print request details for assessment endpoint
                if 'assessment/tier-session' in endpoint:
                    print(f"   DEBUG: Making POST request to {BASE_URL}{endpoint}")
                    print(f"   DEBUG: Headers: {headers}")
                    print(f"   DEBUG: Data: {data}")
                    print(f"   DEBUG: Use form data: {use_form_data}")
                
                if use_form_data:
                    response = self.session.post(
                        f"{BASE_URL}{endpoint}",
                        headers=headers,
                        data=data,  # Use data instead of json for form data
                        params=params,
                        timeout=10
                    )
                else:
                    response = self.session.post(
                        f"{BASE_URL}{endpoint}",
                        headers=headers,
                        json=data,
                        params=params,
                        timeout=10
                    )
            else:
                return None, f"Unsupported method: {method}"
            
            response_time = time.time() - start_time
            return response, response_time
            
        except Exception as e:
            return None, f"Request exception: {str(e)}"

    def test_critical_endpoints(self):
        """Test the 8 critical endpoints from review request"""
        print("\n🎯 Testing 8 Critical Endpoints from Review Request...")
        
        critical_tests = [
            {
                'name': 'Assessment Tier Session Creation',
                'method': 'POST',
                'endpoint': '/assessment/tier-session',
                'role': 'client',
                'data': {'area_id': 'area1', 'tier_level': 1},
                'expected_status': [200, 201],
                'description': 'POST /assessment/tier-session (was 422, should be 200)'
            },
            {
                'name': 'Knowledge Base Areas with Area10',
                'method': 'GET',
                'endpoint': '/knowledge-base/areas',
                'role': 'client',
                'data': None,
                'expected_status': [200],
                'description': 'GET /knowledge-base/areas (should return 10 areas including area10)'
            },
            {
                'name': 'Provider Opportunities',
                'method': 'GET',
                'endpoint': '/service-requests/opportunities',
                'role': 'provider',
                'data': None,
                'expected_status': [200],
                'description': 'GET /service-requests/opportunities (was 403, should be 200)'
            },
            {
                'name': 'Agency License Generation',
                'method': 'POST',
                'endpoint': '/agency/licenses/generate',
                'role': 'agency',
                'data': {'quantity': 1, 'expires_days': 60},
                'expected_status': [200, 201],
                'description': 'POST /agency/licenses/generate (was 403, should be 200)'
            },
            {
                'name': 'Service Request Creation',
                'method': 'POST',
                'endpoint': '/service-requests/professional-help',
                'role': 'client',
                'data': {
                    'area_id': 'area5',
                    'title': 'Technology Assessment',
                    'description': 'Need help with technology infrastructure assessment',
                    'budget_range': '5000-15000',
                    'timeline': '1-2 months',
                    'location': 'New York, NY'
                },
                'expected_status': [200, 201],
                'description': 'POST /service-requests/professional-help (should still work)'
            },
            {
                'name': 'AI Assistance',
                'method': 'POST',
                'endpoint': '/knowledge-base/ai-assistance',
                'role': 'client',
                'data': {
                    'question': 'How do I start my procurement readiness assessment?',
                    'context': {'area_id': 'area1'}
                },
                'expected_status': [200],
                'description': 'POST /knowledge-base/ai-assistance (should still work)'
            },
            {
                'name': 'Navigator Evidence Review',
                'method': 'GET',
                'endpoint': '/navigator/evidence/pending',
                'role': 'navigator',
                'data': None,
                'expected_status': [200],
                'description': 'GET /navigator/evidence/pending (should still work)'
            },
            {
                'name': 'Template Generation Area10',
                'method': 'GET',
                'endpoint': '/knowledge-base/generate-template/area10/template',
                'role': 'client',
                'data': None,
                'expected_status': [200],
                'description': 'GET /knowledge-base/generate-template/area10/template (should still work)'
            }
        ]
        
        passed_tests = 0
        total_tests = len(critical_tests)
        
        for test in critical_tests:
            print(f"\n🔍 Testing: {test['description']}")
            
            # Check if we have authentication for this role
            if test['role'] not in self.tokens:
                self.log_test(
                    test['name'],
                    False,
                    f"No authentication token for role: {test['role']}",
                    0
                )
                continue
            
            # Determine if we need to use form data
            use_form_data = test['name'] == 'Assessment Tier Session Creation'
            
            # Make the request
            response, response_time = self.make_authenticated_request(
                test['method'],
                test['endpoint'],
                test['role'],
                test['data'],
                use_form_data=use_form_data
            )
            
            # Debug: Print request details for failing tests
            if test['name'] == 'Assessment Tier Session Creation':
                print(f"   DEBUG: Request data: {test['data']}")
                print(f"   DEBUG: Endpoint: {BASE_URL}{test['endpoint']}")
                if response:
                    print(f"   DEBUG: Response status: {response.status_code}")
                    print(f"   DEBUG: Response text: {response.text}")
            
            if response is None:
                self.log_test(
                    test['name'],
                    False,
                    f"No response received: {response_time}",
                    0
                )
                continue
            
            # Check if status code is expected
            success = response.status_code in test['expected_status']
            
            if success:
                passed_tests += 1
                
                # Additional validation for specific endpoints
                if test['name'] == 'Knowledge Base Areas with Area10':
                    try:
                        data = response.json()
                        areas = data.get('areas', [])
                        area_count = len(areas)
                        has_area10 = any(area.get('area_id') == 'area10' or area.get('id') == 'area10' for area in areas)
                        details = f"Status {response.status_code}, Found {area_count} areas, Area10 present: {has_area10}"
                        if not has_area10:
                            success = False
                            details += " - MISSING AREA10!"
                    except:
                        details = f"Status {response.status_code}, Could not parse response"
                elif test['name'] == 'AI Assistance':
                    try:
                        data = response.json()
                        response_text = data.get('response', '')
                        details = f"Status {response.status_code}, AI response length: {len(response_text)} chars"
                    except:
                        details = f"Status {response.status_code}, Could not parse AI response"
                elif test['name'] == 'Template Generation Area10':
                    try:
                        data = response.json()
                        content = data.get('content', '')
                        filename = data.get('filename', '')
                        details = f"Status {response.status_code}, Template content: {len(content)} chars, Filename: {filename}"
                    except:
                        details = f"Status {response.status_code}, Could not parse template response"
                else:
                    try:
                        data = response.json()
                        details = f"Status {response.status_code}, Response data: {len(str(data))} chars"
                    except:
                        details = f"Status {response.status_code}"
            else:
                # Failed test - get error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_data.get('error', str(error_data)))
                    details = f"Status {response.status_code}: {error_msg}"
                except:
                    details = f"Status {response.status_code}: {response.text[:200]}..."
            
            self.log_test(
                test['name'],
                success,
                details,
                response_time or 0
            )
        
        return passed_tests, total_tests

    def run_critical_verification(self):
        """Run critical endpoints verification"""
        print("🎯 CRITICAL ENDPOINTS VERIFICATION TEST STARTED")
        print("=" * 60)
        print("Final verification test to confirm 100% completion after fixing all critical endpoints.")
        print("=" * 60)
        
        # Authenticate all QA users
        print("\n🔐 Authenticating QA Users...")
        auth_success = 0
        for role in QA_CREDENTIALS.keys():
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success == 0:
            print("❌ CRITICAL: No QA users could authenticate. Cannot proceed with tests.")
            return
        else:
            print(f"✅ {auth_success}/4 QA users authenticated successfully")
        
        # Run critical endpoints tests
        passed_tests, total_tests = self.test_critical_endpoints()
        
        # Generate summary
        self.generate_critical_summary(passed_tests, total_tests)

    def generate_critical_summary(self, passed_tests, total_tests):
        """Generate critical endpoints test summary"""
        print("\n" + "=" * 60)
        print("🎯 CRITICAL ENDPOINTS VERIFICATION SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 CRITICAL ENDPOINTS RESULTS:")
        print(f"   Total Critical Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {total_tests - passed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Expected result assessment
        print(f"\n🎯 EXPECTED RESULT ASSESSMENT:")
        if success_rate == 100:
            print("   ✅ PERFECT - TRUE 100% COMPLETION ACHIEVED!")
            print("   All 8 critical endpoints are now operational.")
        elif success_rate >= 87.5:  # 7/8 tests
            print("   ⚠️ NEAR COMPLETION - 1 endpoint still needs attention")
        elif success_rate >= 75:    # 6/8 tests
            print("   ⚠️ GOOD PROGRESS - 2 endpoints still need fixing")
        elif success_rate >= 62.5:  # 5/8 tests (current state)
            print("   ⚠️ SAME AS BEFORE - No improvement from previous test")
        else:
            print("   ❌ REGRESSION - Performance worse than previous test")
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success'] and result['test'] != 'Client Authentication' and result['test'] != 'Provider Authentication' and result['test'] != 'Agency Authentication' and result['test'] != 'Navigator Authentication']
        if failed_tests:
            print(f"\n❌ FAILED CRITICAL ENDPOINTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['details']}")
        
        # Authentication status
        print(f"\n🔐 QA AUTHENTICATION STATUS:")
        for role in QA_CREDENTIALS.keys():
            status = "✅ AUTHENTICATED" if role in self.tokens else "❌ FAILED"
            print(f"   • {role.title()}: {status}")
        
        # Final assessment
        print(f"\n🚀 FINAL ASSESSMENT:")
        if success_rate == 100:
            print("   ✅ READY FOR 100% COMPLETION CLAIM")
            print("   All critical endpoints fixed and operational")
        else:
            print("   ❌ NOT READY FOR 100% COMPLETION CLAIM")
            print(f"   {total_tests - passed_tests} critical endpoint(s) still failing")
        
        print(f"\n📝 Test completed at: {datetime.now().isoformat()}")
        print("=" * 60)

if __name__ == "__main__":
    tester = CriticalEndpointsTester()
    tester.run_critical_verification()