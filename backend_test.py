#!/usr/bin/env python3
"""
Comprehensive Polaris Platform Backend Testing
Testing all major backend endpoints and user workflows as requested in review.

QA Credentials:
- client.qa@polaris.example.com / Polaris#2025!
- provider.qa@polaris.example.com / Polaris#2025!
- agency.qa@polaris.example.com / Polaris#2025!
- navigator.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8001/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class PolarisBackendTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Polaris-Backend-Tester/1.0'
        })

    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        # Ensure response_time is a number
        if isinstance(response_time, str):
            try:
                response_time = float(response_time.replace('s', ''))
            except:
                response_time = 0
        
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
                # Handle both 'token' and 'access_token' response formats
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
            elif response.status_code == 403 and role == 'agency':
                # Handle agency pending approval case
                self.log_test(
                    f"{role.title()} Authentication",
                    False,
                    f"Agency pending approval - expected for QA setup",
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
            elif method.upper() == 'PUT':
                response = self.session.put(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=10
                )
            elif method.upper() == 'PATCH':
                response = self.session.patch(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=10
                )
            else:
                return None, f"Unsupported method: {method}"
            
            response_time = time.time() - start_time
            return response, response_time
            
        except Exception as e:
            return None, f"Request exception: {str(e)}"

    def test_health_check(self):
        """Test basic health check"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL.replace('/api', '')}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check",
                    True,
                    f"Status: {data.get('status', 'Unknown')}, Uptime: {data.get('uptime', 0):.1f}s",
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"Status {response.status_code}: {response.text}",
                    response_time
                )
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}", 0)
            return False

    def test_assessment_system(self):
        """Test tier-based assessment system"""
        print("\n🔍 Testing Assessment System...")
        
        # Test assessment schema - tier-based
        response, response_time = self.make_authenticated_request(
            'GET', '/assessment/schema/tier-based', 'client'
        )
        
        if response and response.status_code == 200:
            data = response.json()
            areas_count = len(data.get('data', {}).get('areas', []))
            has_area10 = any(area.get('area_id') == 'area10' for area in data.get('data', {}).get('areas', []))
            
            self.log_test(
                "Assessment Schema - Tier-based",
                True,
                f"Found {areas_count} areas, Area10 present: {has_area10}",
                response_time
            )
        else:
            error_msg = response.text if response else "No response"
            self.log_test(
                "Assessment Schema - Tier-based",
                False,
                f"Status {response.status_code if response else 'N/A'}: {error_msg}",
                response_time or 0
            )

        # Test tier session creation
        session_data = {
            "area_id": "area1",
            "tier_level": 1
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/assessment/tier-session', 'client', session_data
        )
        
        if response and response.status_code in [200, 201]:
            data = response.json()
            session_id = data.get('data', {}).get('session', {}).get('_id') or data.get('data', {}).get('session', {}).get('id')
            self.log_test(
                "Assessment Tier Session Creation",
                True,
                f"Session ID: {session_id}",
                response_time
            )
            
            # Test session response submission if session created
            if session_id:
                response_data = {
                    "question_id": "area1_tier1_q1",
                    "response": "compliant",
                    "evidence_provided": "false",
                    "notes": "Test response"
                }
                
                response, response_time = self.make_authenticated_request(
                    'POST', f'/assessment/tier-session/{session_id}/response', 'client', response_data
                )
                
                success = response and response.status_code in [200, 201]
                details = f"Status {response.status_code}" if response else "No response"
                self.log_test(
                    "Assessment Response Submission",
                    success,
                    details,
                    response_time or 0
                )
        else:
            error_msg = response.text if response else "No response"
            self.log_test(
                "Assessment Tier Session Creation",
                False,
                f"Status {response.status_code if response else 'N/A'}: {error_msg}",
                response_time or 0
            )

    def test_knowledge_base_system(self):
        """Test Knowledge Base system"""
        print("\n📚 Testing Knowledge Base System...")
        
        # Test knowledge base areas
        response, response_time = self.make_authenticated_request(
            'GET', '/knowledge-base/areas', 'client'
        )
        
        if response and response.status_code == 200:
            data = response.json()
            areas_count = len(data.get('areas', []))
            self.log_test(
                "Knowledge Base Areas",
                True,
                f"Found {areas_count} areas available",
                response_time
            )
        else:
            error_msg = response.text if response else "No response"
            self.log_test(
                "Knowledge Base Areas",
                False,
                f"Status {response.status_code if response else 'N/A'}: {error_msg}",
                response_time or 0
            )

        # Test template generation
        response, response_time = self.make_authenticated_request(
            'GET', '/knowledge-base/generate-template/area1/template', 'client'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            content_length = len(data.get('content', ''))
            details = f"Template generated, content length: {content_length} chars"
        else:
            details = f"Status {response.status_code if response else 'N/A'}"
            
        self.log_test(
            "Knowledge Base Template Generation",
            success,
            details,
            response_time or 0
        )

        # Test AI assistance
        ai_data = {
            "question": "How do I start my procurement readiness assessment?",
            "context": "business_licensing"
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/knowledge-base/ai-assistance', 'client', ai_data
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            response_length = len(data.get('response', ''))
            details = f"AI response generated, length: {response_length} chars"
        else:
            details = f"Status {response.status_code if response else 'N/A'}"
            
        self.log_test(
            "Knowledge Base AI Assistance",
            success,
            details,
            response_time or 0
        )

    def test_service_provider_system(self):
        """Test Service Provider system"""
        print("\n🏢 Testing Service Provider System...")
        
        # Test provider dashboard
        response, response_time = self.make_authenticated_request(
            'GET', '/provider/dashboard', 'provider'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            details = f"Dashboard data retrieved successfully"
        else:
            details = f"Status {response.status_code if response else 'N/A'}"
            
        self.log_test(
            "Provider Dashboard",
            success,
            details,
            response_time or 0
        )

        # Test service request creation (as client)
        service_request_data = {
            "area_id": "area5",
            "description": "Need help with technology infrastructure assessment",
            "budget_range": "5000-15000",
            "timeline": "1-2 months",
            "location": "New York, NY"
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/service-requests/professional-help', 'client', service_request_data
        )
        
        if response and response.status_code in [200, 201]:
            data = response.json()
            request_id = data.get('request_id') or data.get('id')
            providers_notified = data.get('providers_notified', 0)
            
            self.log_test(
                "Service Request Creation",
                True,
                f"Request ID: {request_id}, Providers notified: {providers_notified}",
                response_time
            )
            
            # Test provider response (if request created)
            if request_id:
                provider_response_data = {
                    "request_id": request_id,
                    "proposed_fee": 2500.00,
                    "estimated_timeline": "6 weeks",
                    "proposal_note": "Comprehensive technology assessment with detailed recommendations"
                }
                
                response, response_time = self.make_authenticated_request(
                    'POST', '/provider/respond-to-request', 'provider', provider_response_data
                )
                
                success = response and response.status_code in [200, 201]
                details = f"Status {response.status_code}" if response else "No response"
                self.log_test(
                    "Provider Response Submission",
                    success,
                    details,
                    response_time or 0
                )
        else:
            error_msg = response.text if response else "No response"
            self.log_test(
                "Service Request Creation",
                False,
                f"Status {response.status_code if response else 'N/A'}: {error_msg}",
                response_time or 0
            )

    def test_digital_navigator_workflow(self):
        """Test Digital Navigator workflow"""
        print("\n🧭 Testing Digital Navigator Workflow...")
        
        # Test navigator dashboard
        response, response_time = self.make_authenticated_request(
            'GET', '/navigator/dashboard', 'navigator'
        )
        
        success = response and response.status_code == 200
        details = f"Status {response.status_code}" if response else "No response"
        self.log_test(
            "Navigator Dashboard",
            success,
            details,
            response_time or 0
        )

        # Test pending evidence review
        response, response_time = self.make_authenticated_request(
            'GET', '/navigator/evidence/pending', 'navigator'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            pending_count = len(data.get('evidence', []))
            details = f"Found {pending_count} pending evidence items"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "Navigator Evidence Review",
            success,
            details,
            response_time or 0
        )

        # Test agency integration
        response, response_time = self.make_authenticated_request(
            'GET', '/agency/licenses', 'agency'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            licenses_count = len(data.get('licenses', []))
            details = f"Found {licenses_count} licenses"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "Agency License Management",
            success,
            details,
            response_time or 0
        )

    def test_comprehensive_endpoints(self):
        """Test all endpoints mentioned in review request"""
        print("\n🎯 Testing Comprehensive Endpoints from Review Request...")
        
        # Test all assessment endpoints
        endpoints_to_test = [
            # Assessment endpoints
            ('GET', '/assessment/schema/tier-based', 'client', None, 'Assessment Schema Tier-Based'),
            
            # Knowledge base endpoints  
            ('GET', '/knowledge-base/areas', 'client', None, 'Knowledge Base Areas'),
            ('POST', '/knowledge-base/ai-assistance', 'client', 
             {"question": "How do I start my procurement readiness assessment?", "context": "business_licensing"}, 
             'Knowledge Base AI Assistance'),
            ('GET', '/knowledge-base/generate-template/area1/template', 'client', None, 'Knowledge Base Template Generation'),
            
            # Service request endpoints
            ('POST', '/service-requests/professional-help', 'client',
             {"area_id": "area5", "title": "Technology Assessment", "description": "Need help with tech infrastructure", 
              "budget_range": "5000-15000", "timeline": "1-2 months", "location": "New York, NY"},
             'Service Request Creation'),
            ('GET', '/service-requests/opportunities', 'provider', None, 'Service Request Opportunities'),
            
            # Navigator endpoints
            ('GET', '/navigator/evidence/pending', 'navigator', None, 'Navigator Evidence Pending'),
            ('GET', '/navigator/analytics/resources', 'navigator', None, 'Navigator Analytics Resources'),
            
            # Agency endpoints
            ('POST', '/agency/licenses/generate', 'agency', {"quantity": 3, "expires_days": 60}, 'Agency License Generation'),
            ('GET', '/agency/licenses/stats', 'agency', None, 'Agency License Stats'),
            ('GET', '/agency/licenses', 'agency', None, 'Agency Licenses List'),
            ('POST', '/agency/tier-configuration', 'agency', 
             {"client_id": "test-client-id", "tier_levels": {"area1": 3, "area2": 2}}, 
             'Agency Tier Configuration'),
        ]
        
        for method, endpoint, role, data, test_name in endpoints_to_test:
            if role not in self.tokens:
                self.log_test(test_name, False, f"No token for role {role}", 0)
                continue
                
            response, response_time = self.make_authenticated_request(method, endpoint, role, data)
            
            if response:
                success = response.status_code in [200, 201]
                if success:
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

    def test_end_to_end_workflows(self):
        """Test end-to-end user workflows"""
        print("\n🔄 Testing End-to-End Workflows...")
        
        # Test complete client journey
        print("Testing Client Journey...")
        
        # 1. Client creates service request
        service_request_data = {
            "area_id": "area5",
            "title": "Technology Infrastructure Assessment",
            "description": "Need comprehensive technology assessment for procurement readiness",
            "budget_range": "5000-15000",
            "timeline": "1-2 months",
            "location": "New York, NY"
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/service-requests/professional-help', 'client', service_request_data
        )
        
        request_id = None
        if response and response.status_code in [200, 201]:
            data = response.json()
            request_id = data.get('data', {}).get('service_request_id')
            self.log_test(
                "Client Journey - Service Request Creation",
                True,
                f"Request ID: {request_id}",
                response_time
            )
        else:
            self.log_test(
                "Client Journey - Service Request Creation",
                False,
                f"Status {response.status_code if response else 'N/A'}",
                response_time or 0
            )
        
        # 2. Provider responds to request
        if request_id:
            provider_response_data = {
                "request_id": request_id,
                "proposed_fee": 7500.00,
                "estimated_timeline": "6 weeks",
                "proposal_note": "Comprehensive technology assessment with detailed recommendations and implementation roadmap"
            }
            
            response, response_time = self.make_authenticated_request(
                'POST', '/provider/respond-to-request', 'provider', provider_response_data
            )
            
            success = response and response.status_code in [200, 201]
            details = f"Status {response.status_code}" if response else "No response"
            self.log_test(
                "Provider Journey - Response Submission",
                success,
                details,
                response_time or 0
            )
        
        # Test navigator workflow
        print("Testing Navigator Workflow...")
        
        # Navigator reviews evidence
        response, response_time = self.make_authenticated_request(
            'GET', '/navigator/evidence/pending', 'navigator'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            pending_count = len(data.get('data', {}).get('packages', []))
            details = f"Found {pending_count} pending evidence packages"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "Navigator Journey - Evidence Review",
            success,
            details,
            response_time or 0
        )
        
        # Test agency workflow
        print("Testing Agency Workflow...")
        
        # Agency generates licenses
        license_data = {"quantity": 5, "expires_days": 60}
        response, response_time = self.make_authenticated_request(
            'POST', '/agency/licenses/generate', 'agency', license_data
        )
        
        success = response and response.status_code in [200, 201]
        if success:
            data = response.json()
            licenses_generated = len(data.get('data', {}).get('licenses', []))
            details = f"Generated {licenses_generated} license codes"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "Agency Journey - License Generation",
            success,
            details,
            response_time or 0
        )

    def test_advanced_features(self):
        """Test advanced platform features"""
        print("\n🚀 Testing Advanced Features...")
        
        # Test AI coaching
        coaching_data = {
            "message": "How do I improve my procurement readiness?",
            "session_id": str(uuid.uuid4())
        }
        
        response, response_time = self.make_authenticated_request(
            'POST', '/ai/coach/conversation', 'client', coaching_data
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            response_length = len(data.get('response', ''))
            details = f"AI coaching response: {response_length} chars"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "AI Coaching System",
            success,
            details,
            response_time or 0
        )

        # Test QuickBooks integration
        response, response_time = self.make_authenticated_request(
            'GET', '/integrations/quickbooks/auth-url', 'client'
        )
        
        success = response and response.status_code == 200
        if success:
            data = response.json()
            has_auth_url = 'auth_url' in data
            details = f"Auth URL generated: {has_auth_url}"
        else:
            details = f"Status {response.status_code}" if response else "No response"
            
        self.log_test(
            "QuickBooks Integration",
            success,
            details,
            response_time or 0
        )

    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🎯 COMPREHENSIVE POLARIS BACKEND TESTING STARTED")
        print("=" * 60)
        
        # Test basic connectivity
        print("\n🔧 Testing Basic Connectivity...")
        self.test_health_check()
        
        # Authenticate all QA users
        print("\n🔐 Authenticating QA Users...")
        auth_success = 0
        for role in QA_CREDENTIALS.keys():
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success == 0:
            print("❌ CRITICAL: No QA users could authenticate. Continuing with limited tests.")
        else:
            print(f"✅ {auth_success}/4 QA users authenticated successfully")
        
        # Run comprehensive feature tests
        self.test_assessment_system()
        self.test_knowledge_base_system()
        self.test_service_provider_system()
        self.test_digital_navigator_workflow()
        self.test_comprehensive_endpoints()
        self.test_end_to_end_workflows()
        self.test_advanced_features()
        
        # Generate summary
        self.generate_test_summary()

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Average response time
        response_times = [float(result['response_time'].replace('s', '')) for result in self.test_results if result['response_time'] != '0.000s']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Authentication status
        print(f"\n🔐 QA AUTHENTICATION STATUS:")
        for role in QA_CREDENTIALS.keys():
            status = "✅ AUTHENTICATED" if role in self.tokens else "❌ FAILED"
            print(f"   • {role.title()}: {status}")
        
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - System ready for production")
        elif success_rate >= 75:
            print("   ⚠️ GOOD - Minor issues need attention")
        elif success_rate >= 50:
            print("   ⚠️ FAIR - Several issues need fixing")
        else:
            print("   ❌ POOR - Major issues require immediate attention")
        
        print(f"\n📝 Test completed at: {datetime.now().isoformat()}")
        print("=" * 60)

if __name__ == "__main__":
    tester = PolarisBackendTester()
    tester.run_comprehensive_tests()