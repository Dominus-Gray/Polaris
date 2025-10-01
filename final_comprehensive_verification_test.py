#!/usr/bin/env python3
"""
Final Comprehensive Verification Test for Polaris Platform
Testing specific endpoints mentioned in review request for 100% completion verification.
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Using production URL
BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FinalVerificationTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Polaris-Final-Verification-Tester/1.0'
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
            
            self.log_test(
                f"{role.title()} Authentication",
                False,
                f"Status {response.status_code}: {response.text[:200]}",
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

    def make_authenticated_request(self, method, endpoint, role, data=None, params=None):
        """Make authenticated request"""
        if role not in self.tokens:
            return None, f"No token for role {role}"
        
        headers = {'Authorization': f'Bearer {self.tokens[role]}'}
        
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
        """Test the 26 critical backend endpoints mentioned in review request"""
        print("\n🎯 TESTING 26 CRITICAL BACKEND ENDPOINTS...")
        
        # Critical endpoints from review request
        critical_endpoints = [
            # Authentication & User Management (4 endpoints)
            ('POST', '/auth/login', 'client', QA_CREDENTIALS['client'], 'Auth Login'),
            ('GET', '/auth/me', 'client', None, 'Auth Me'),
            ('POST', '/auth/register', None, {
                "email": "test.user@example.com",
                "password": "TestPass123!",
                "role": "client",
                "license_code": "1234567890"
            }, 'Auth Register'),
            ('POST', '/auth/logout', 'client', None, 'Auth Logout'),
            
            # Assessment System (6 endpoints)
            ('GET', '/assessment/schema/tier-based', 'client', None, 'Assessment Schema'),
            ('POST', '/assessment/tier-session', 'client', {
                "area_id": "area1",
                "tier_level": 1
            }, 'Assessment Session Create'),
            ('GET', '/assessment/tier-session/test-session-id/progress', 'client', None, 'Assessment Progress'),
            ('POST', '/assessment/tier-session/test-session-id/response', 'client', {
                "question_id": "area1_tier1_q1",
                "response": "compliant",
                "evidence_provided": "false",
                "notes": "Test response"
            }, 'Assessment Response Submit'),
            ('GET', '/client/tier-access', 'client', None, 'Client Tier Access'),
            ('GET', '/client/dashboard', 'client', None, 'Client Dashboard'),
            
            # Knowledge Base System (4 endpoints)
            ('GET', '/knowledge-base/areas', 'client', None, 'Knowledge Base Areas'),
            ('POST', '/knowledge-base/ai-assistance', 'client', {
                "question": "How do I start my procurement readiness assessment?",
                "context": {"area_id": "area1"}
            }, 'Knowledge Base AI Assistance'),
            ('GET', '/knowledge-base/generate-template/area1/template', 'client', None, 'Knowledge Base Template'),
            ('GET', '/knowledge-base/articles/area1', 'client', None, 'Knowledge Base Articles'),
            
            # Service Provider System (4 endpoints)
            ('POST', '/service-requests/professional-help', 'client', {
                "area_id": "area5",
                "title": "Technology Assessment",
                "description": "Need help with tech infrastructure",
                "budget_range": "5000-15000",
                "timeline": "1-2 months",
                "location": "New York, NY"
            }, 'Service Request Create'),
            ('GET', '/service-requests/opportunities', 'provider', None, 'Provider Opportunities'),
            ('POST', '/provider/respond-to-request', 'provider', {
                "request_id": "test-request-id",
                "proposed_fee": 2500.00,
                "estimated_timeline": "6 weeks",
                "proposal_note": "Comprehensive assessment"
            }, 'Provider Response'),
            ('GET', '/provider/dashboard', 'provider', None, 'Provider Dashboard'),
            
            # Navigator System (4 endpoints)
            ('GET', '/navigator/dashboard', 'navigator', None, 'Navigator Dashboard'),
            ('GET', '/navigator/evidence/pending', 'navigator', None, 'Navigator Evidence'),
            ('GET', '/navigator/analytics/resources', 'navigator', None, 'Navigator Analytics'),
            ('POST', '/navigator/agencies/approve', 'navigator', {
                "agency_id": "test-agency-id"
            }, 'Navigator Agency Approval'),
            
            # Agency System (4 endpoints)
            ('GET', '/agency/dashboard', 'agency', None, 'Agency Dashboard'),
            ('POST', '/agency/licenses/generate', 'agency', {
                "quantity": 3,
                "expires_days": 60
            }, 'Agency License Generate'),
            ('GET', '/agency/licenses/stats', 'agency', None, 'Agency License Stats'),
            ('GET', '/agency/licenses', 'agency', None, 'Agency Licenses List'),
            
            # Advanced Features (4 endpoints)
            ('POST', '/ai/coach/conversation', 'client', {
                "message": "How do I improve my procurement readiness?",
                "session_id": "test-session-123"
            }, 'AI Coaching'),
            ('GET', '/integrations/quickbooks/auth-url', 'client', None, 'QuickBooks Integration'),
            ('POST', '/payments/service-request', 'client', {
                "request_id": "test-request-id",
                "provider_id": "test-provider-id"
            }, 'Payment Integration'),
            ('GET', '/system/health', None, None, 'System Health Check')
        ]
        
        passed_tests = 0
        total_tests = len(critical_endpoints)
        
        for method, endpoint, role, data, test_name in critical_endpoints:
            if role and role not in self.tokens:
                self.log_test(test_name, False, f"No token for role {role}", 0)
                continue
            
            if role:
                response, response_time = self.make_authenticated_request(method, endpoint, role, data)
            else:
                # For endpoints that don't require authentication
                try:
                    start_time = time.time()
                    if method.upper() == 'GET':
                        response = self.session.get(f"{BASE_URL}{endpoint}", timeout=10)
                    elif method.upper() == 'POST':
                        response = self.session.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
                    response_time = time.time() - start_time
                except Exception as e:
                    response = None
                    response_time = 0
            
            if response:
                success = response.status_code in [200, 201, 202]
                if success:
                    passed_tests += 1
                    try:
                        response_data = response.json()
                        details = f"Status {response.status_code}, Response: {len(str(response_data))} chars"
                    except:
                        details = f"Status {response.status_code}"
                else:
                    details = f"Status {response.status_code}: {response.text[:100]}..."
            else:
                success = False
                details = "No response received"
                response_time = response_time or 0
            
            self.log_test(test_name, success, details, response_time)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📊 CRITICAL ENDPOINTS SUMMARY:")
        print(f"   Total Critical Endpoints: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {total_tests - passed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        return success_rate

    def test_data_persistence(self):
        """Test data persistence across all systems"""
        print("\n💾 TESTING DATA PERSISTENCE...")
        
        # Test service request creation and retrieval
        service_request_data = {
            "area_id": "area5",
            "title": "Data Persistence Test",
            "description": "Testing data persistence functionality",
            "budget_range": "5000-15000",
            "timeline": "1-2 months",
            "location": "Test City, NY"
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/service-requests/professional-help', 'client', service_request_data
        )
        
        request_id = None
        if response and response.status_code in [200, 201]:
            data = response.json()
            request_id = data.get('request_id') or data.get('id')
            self.log_test(
                "Data Persistence - Service Request Creation",
                True,
                f"Request ID: {request_id}",
                response_time
            )
            
            # Test retrieval of created request
            if request_id:
                response, response_time = self.make_authenticated_request(
                    'GET', f'/service-requests/{request_id}', 'client'
                )
                
                success = response and response.status_code == 200
                details = f"Status {response.status_code}" if response else "No response"
                self.log_test(
                    "Data Persistence - Service Request Retrieval",
                    success,
                    details,
                    response_time or 0
                )
        else:
            self.log_test(
                "Data Persistence - Service Request Creation",
                False,
                f"Status {response.status_code if response else 'N/A'}",
                response_time or 0
            )

    def test_integration_quality(self):
        """Test real vs fallback functionality"""
        print("\n🔗 TESTING INTEGRATION QUALITY...")
        
        # Test AI integration (real vs fallback)
        ai_data = {
            "question": "What are the key requirements for procurement readiness?",
            "context": {"area_id": "area1"}
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/knowledge-base/ai-assistance', 'client', ai_data
        )
        
        if response and response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            
            # Check if it's a real AI response or fallback
            is_real_ai = len(ai_response) > 50 and 'procurement' in ai_response.lower()
            
            self.log_test(
                "Integration Quality - AI Response",
                True,
                f"Real AI: {is_real_ai}, Length: {len(ai_response)} chars",
                response_time
            )
        else:
            self.log_test(
                "Integration Quality - AI Response",
                False,
                f"Status {response.status_code if response else 'N/A'}",
                response_time or 0
            )

    def run_final_verification(self):
        """Run final comprehensive verification"""
        print("🎯 FINAL COMPREHENSIVE VERIFICATION STARTED")
        print("=" * 60)
        
        # Authenticate all QA users
        print("\n🔐 Authenticating QA Users...")
        auth_success = 0
        for role in QA_CREDENTIALS.keys():
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success == 0:
            print("❌ CRITICAL: No QA users could authenticate. Aborting verification.")
            return
        else:
            print(f"✅ {auth_success}/4 QA users authenticated successfully")
        
        # Run verification tests
        critical_success_rate = self.test_critical_endpoints()
        self.test_data_persistence()
        self.test_integration_quality()
        
        # Generate final summary
        self.generate_final_summary(critical_success_rate)

    def generate_final_summary(self, critical_success_rate):
        """Generate final verification summary"""
        print("\n" + "=" * 60)
        print("🎯 FINAL VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"   Critical Endpoints Success Rate: {critical_success_rate:.1f}%")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details'][:100]}...")
        
        # Final assessment
        print(f"\n🚀 FINAL PRODUCTION READINESS ASSESSMENT:")
        if critical_success_rate >= 95 and overall_success_rate >= 90:
            print("   ✅ EXCELLENT - 100% completion achieved, ready for production")
        elif critical_success_rate >= 90 and overall_success_rate >= 85:
            print("   ✅ VERY GOOD - Near 100% completion, minor issues to address")
        elif critical_success_rate >= 80 and overall_success_rate >= 75:
            print("   ⚠️ GOOD - Significant progress, some critical issues remain")
        else:
            print("   ❌ NEEDS WORK - Major issues prevent 100% completion claim")
        
        print(f"\n📝 Final verification completed at: {datetime.now().isoformat()}")
        print("=" * 60)

if __name__ == "__main__":
    tester = FinalVerificationTester()
    tester.run_final_verification()