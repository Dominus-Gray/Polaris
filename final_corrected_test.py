#!/usr/bin/env python3
"""
FINAL VALIDATION - COMPREHENSIVE SYSTEM TESTING (CORRECTED)
Testing Focus: Evidence Upload Enforcement, Dashboard Data Accuracy, Agency BI, Data Standardization
QA Credentials: client.qa@polaris.example.com / Polaris#2025!, agency.qa@polaris.example.com / Polaris#2025!, navigator.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_CLIENT_EMAIL = "client.qa@polaris.example.com"
QA_CLIENT_PASSWORD = "Polaris#2025!"
QA_AGENCY_EMAIL = "agency.qa@polaris.example.com"
QA_AGENCY_PASSWORD = "Polaris#2025!"
QA_NAVIGATOR_EMAIL = "navigator.qa@polaris.example.com"
QA_NAVIGATOR_PASSWORD = "Polaris#2025!"

class FinalCorrectedTester:
    def __init__(self):
        self.client_token = None
        self.agency_token = None
        self.navigator_token = None
        self.test_results = []
        self.session = requests.Session()
        self.test_session_id = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def make_request(self, method, endpoint, token=None, **kwargs):
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def test_authentication_all_roles(self):
        """Test Authentication System - All QA credentials"""
        print("🔐 Testing Authentication System - All QA Roles...")
        
        # Test client login
        response = self.make_request('POST', '/auth/login', json={
            "email": QA_CLIENT_EMAIL,
            "password": QA_CLIENT_PASSWORD
        })
        
        if response and response.status_code == 200:
            self.client_token = response.json().get('access_token')
            self.log_test("Client QA Authentication", True, f"Successfully logged in as {QA_CLIENT_EMAIL}")
        else:
            self.log_test("Client QA Authentication", False, f"Failed to login as {QA_CLIENT_EMAIL}")

        # Test agency login
        response = self.make_request('POST', '/auth/login', json={
            "email": QA_AGENCY_EMAIL,
            "password": QA_AGENCY_PASSWORD
        })
        
        if response and response.status_code == 200:
            self.agency_token = response.json().get('access_token')
            self.log_test("Agency QA Authentication", True, f"Successfully logged in as {QA_AGENCY_EMAIL}")
        else:
            self.log_test("Agency QA Authentication", False, f"Failed to login as {QA_AGENCY_EMAIL}")

        # Test navigator login
        response = self.make_request('POST', '/auth/login', json={
            "email": QA_NAVIGATOR_EMAIL,
            "password": QA_NAVIGATOR_PASSWORD
        })
        
        if response and response.status_code == 200:
            self.navigator_token = response.json().get('access_token')
            self.log_test("Navigator QA Authentication", True, f"Successfully logged in as {QA_NAVIGATOR_EMAIL}")
        else:
            self.log_test("Navigator QA Authentication", False, f"Failed to login as {QA_NAVIGATOR_EMAIL}")

    def test_evidence_upload_enforcement(self):
        """Test Evidence Upload Enforcement (CRITICAL)"""
        print("📋 Testing Evidence Upload Enforcement (CRITICAL)...")
        
        if not self.client_token:
            self.log_test("Evidence Upload Enforcement", False, "No client token available")
            return

        # Create Tier 2 assessment session
        response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, data={
            "area_id": "area1",
            "tier_level": 2
        })
        
        if response and response.status_code == 200:
            session_id = response.json().get('session_id')
            self.test_session_id = session_id
            self.log_test("Tier 2 Assessment Session Creation", True, f"Created Tier 2 session: {session_id}")
            
            # Test: Submit Tier 2 compliant response WITHOUT evidence (should be blocked with 422)
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{session_id}/response', 
                token=self.client_token, 
                data={
                    "question_id": "q1_4_t2",  # Correct Tier 2 question ID
                    "response": "compliant",
                    "evidence_provided": "false"
                }
            )
            
            if response and response.status_code == 422:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 Blocking", 
                    True, 
                    "✅ CRITICAL: System correctly blocks Tier 2 compliant responses without evidence (HTTP 422)"
                )
            else:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 Blocking", 
                    False, 
                    f"❌ CRITICAL FAILURE: Expected 422 but got {response.status_code if response else 'No response'}"
                )
            
            # Test: Submit Tier 2 compliant response WITH evidence (should succeed)
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{session_id}/response', 
                token=self.client_token, 
                data={
                    "question_id": "q1_5_t2",  # Correct Tier 2 question ID
                    "response": "compliant",
                    "evidence_provided": "true",
                    "evidence_url": "https://example.com/evidence.pdf"
                }
            )
            
            if response and response.status_code == 200:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 With Evidence", 
                    True, 
                    "✅ System correctly accepts Tier 2 compliant responses with evidence"
                )
            else:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 With Evidence", 
                    False, 
                    f"System should accept Tier 2 responses with evidence but got {response.status_code if response else 'No response'}"
                )
        else:
            self.log_test("Tier 2 Assessment Session Creation", False, "Failed to create Tier 2 session")

    def test_dashboard_data_accuracy(self):
        """Test Dashboard Data Accuracy"""
        print("📊 Testing Dashboard Data Accuracy...")
        
        if not self.client_token:
            self.log_test("Dashboard Data Accuracy", False, "No client token available")
            return

        response = self.make_request('GET', '/home/client', token=self.client_token)
        
        if response and response.status_code == 200:
            dashboard_data = response.json()
            
            # Check for required dashboard components
            has_assessment_completion = 'completion_percentage' in dashboard_data
            has_critical_gaps = 'critical_gaps' in dashboard_data
            has_evidence_status = 'evidence_required' in dashboard_data or 'evidence_submitted' in dashboard_data
            has_tier_data = 'assessment_areas' in dashboard_data
            
            accuracy_score = sum([has_assessment_completion, has_critical_gaps, has_evidence_status, has_tier_data]) * 25
            
            self.log_test(
                "Dashboard Data Accuracy", 
                accuracy_score >= 75,
                f"Dashboard accuracy: {accuracy_score}% - Assessment: {has_assessment_completion}, Gaps: {has_critical_gaps}, Evidence: {has_evidence_status}, Tier Data: {has_tier_data}"
            )
            
            # Check for real-time data
            completion_value = dashboard_data.get('completion_percentage', 0)
            gaps_value = dashboard_data.get('critical_gaps', 0)
            is_dynamic = completion_value not in [0, 100] or gaps_value > 0
            
            self.log_test(
                "Real-time Data Calculation", 
                is_dynamic,
                f"Dashboard shows {'dynamic' if is_dynamic else 'static'} data - Completion: {completion_value}%, Gaps: {gaps_value}"
            )
        else:
            self.log_test("Dashboard Data Accuracy", False, f"Failed to retrieve dashboard data - Status: {response.status_code if response else 'No response'}")

    def test_agency_business_intelligence(self):
        """Test Agency Business Intelligence"""
        print("📈 Testing Agency Business Intelligence...")
        
        if not self.agency_token:
            self.log_test("Agency Business Intelligence", False, "No agency token available")
            return

        response = self.make_request('GET', '/agency/business-intelligence', token=self.agency_token)
        
        if response and response.status_code == 200:
            bi_data = response.json()
            
            # Check for BI components
            has_client_tracking = 'client_details' in bi_data or 'clients' in bi_data
            has_governance_alerts = 'governance_alerts' in bi_data
            has_monthly_activity = 'monthly_activity' in bi_data
            has_compliance_metrics = 'agency_overview' in bi_data
            
            bi_score = sum([has_client_tracking, has_governance_alerts, has_monthly_activity, has_compliance_metrics]) * 25
            
            self.log_test(
                "Agency Business Intelligence", 
                bi_score >= 75,
                f"Agency BI completeness: {bi_score}% - Client Tracking: {has_client_tracking}, Alerts: {has_governance_alerts}, Activity: {has_monthly_activity}, Metrics: {has_compliance_metrics}"
            )
        else:
            self.log_test("Agency Business Intelligence", False, f"Failed to access agency BI - Status: {response.status_code if response else 'No response'}")

    def test_data_standardization(self):
        """Test Data Standardization"""
        print("🔧 Testing Data Standardization...")
        
        if not self.client_token:
            self.log_test("Data Standardization", False, "No client token available")
            return

        # Test user data standardization
        response = self.make_request('GET', '/auth/me', token=self.client_token)
        
        if response and response.status_code == 200:
            user_data = response.json()
            
            user_id = user_data.get('id', '')
            is_uuid_format = len(user_id) == 36 and user_id.count('-') == 4
            
            created_at = user_data.get('created_at', '')
            is_iso_datetime = 'T' in created_at and len(created_at) >= 19
            
            self.log_test(
                "User Data Standardization", 
                is_uuid_format and is_iso_datetime,
                f"UUID format: {is_uuid_format}, ISO datetime: {is_iso_datetime}"
            )

        # Test assessment session data standardization
        if self.test_session_id:
            response = self.make_request('GET', f'/assessment/tier-session/{self.test_session_id}/progress', token=self.client_token)
            
            if response and response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('session_id', self.test_session_id)
                is_session_uuid = len(session_id) == 36 and session_id.count('-') == 4
                has_standard_fields = 'session_id' in session_data and 'area_id' in session_data
                
                self.log_test(
                    "Assessment Data Standardization", 
                    is_session_uuid and has_standard_fields,
                    f"Session UUID: {is_session_uuid}, Standard fields: {has_standard_fields}"
                )

    def test_assessment_flow(self):
        """Test Assessment Flow"""
        print("📝 Testing Assessment Flow...")
        
        if not self.client_token:
            self.log_test("Assessment Flow", False, "No client token available")
            return

        # Test assessment schema
        response = self.make_request('GET', '/assessment/schema/tier-based', token=self.client_token)
        if response and response.status_code == 200:
            schema_data = response.json()
            areas_count = len(schema_data.get('areas', []))
            self.log_test("Assessment Schema Retrieval", True, f"Retrieved schema with {areas_count} business areas")
        else:
            self.log_test("Assessment Schema Retrieval", False, "Failed to retrieve assessment schema")

        # Test tier session creation
        response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, data={
            "area_id": "area3",
            "tier_level": 1
        })
        
        if response and response.status_code == 200:
            session_id = response.json().get('session_id')
            self.log_test("Tier Session Creation", True, f"Created assessment session: {session_id}")
            
            # Test response submission for Tier 1
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{session_id}/response', 
                token=self.client_token, 
                data={
                    "question_id": "q3_1_t1",  # Correct Tier 1 question ID for area3
                    "response": "compliant",
                    "evidence_provided": "false"
                }
            )
            
            if response and response.status_code == 200:
                self.log_test("Assessment Response Submission", True, "Successfully submitted Tier 1 response")
            else:
                self.log_test("Assessment Response Submission", False, f"Failed to submit response - Status: {response.status_code if response else 'No response'}")
        else:
            self.log_test("Tier Session Creation", False, "Failed to create tier session")

    def test_navigator_review_system(self):
        """Test Navigator Review System"""
        print("👨‍💼 Testing Navigator Review System...")
        
        if not self.navigator_token:
            self.log_test("Navigator Review System", False, "No navigator token available")
            return

        # Test navigator evidence review access
        response = self.make_request('GET', '/navigator/evidence/pending', token=self.navigator_token)
        
        if response and response.status_code == 200:
            pending_evidence = response.json()
            evidence_count = len(pending_evidence) if isinstance(pending_evidence, list) else len(pending_evidence.get('evidence', []))
            self.log_test("Navigator Evidence Review Access", True, f"Navigator can access evidence queue ({evidence_count} items)")
        else:
            self.log_test("Navigator Evidence Review Access", False, f"Failed to access evidence review - Status: {response.status_code if response else 'No response'}")

        # Test navigator analytics
        response = self.make_request('GET', '/navigator/analytics/resources', token=self.navigator_token, params={"since_days": 30})
        
        if response and response.status_code == 200:
            analytics_data = response.json()
            has_analytics = 'total' in analytics_data or 'by_area' in analytics_data
            self.log_test("Navigator Analytics Access", has_analytics, f"Navigator analytics accessible: {has_analytics}")
        else:
            self.log_test("Navigator Analytics Access", False, f"Navigator analytics not accessible - Status: {response.status_code if response else 'No response'}")

    def run_final_validation(self):
        """Run final validation test"""
        print("🚀 FINAL VALIDATION - COMPREHENSIVE SYSTEM TESTING")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        self.test_authentication_all_roles()
        self.test_evidence_upload_enforcement()
        self.test_dashboard_data_accuracy()
        self.test_agency_business_intelligence()
        self.test_data_standardization()
        self.test_assessment_flow()
        self.test_navigator_review_system()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("=" * 80)
        print("🎯 FINAL VALIDATION RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        # Print detailed results
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🔍 CRITICAL VALIDATION FINDINGS:")
        print("-" * 40)
        
        # Calculate category success rates
        evidence_tests = [r for r in self.test_results if 'Evidence' in r['test']]
        evidence_rate = (sum(1 for r in evidence_tests if r['success']) / len(evidence_tests) * 100) if evidence_tests else 0
        
        dashboard_tests = [r for r in self.test_results if 'Dashboard' in r['test']]
        dashboard_rate = (sum(1 for r in dashboard_tests if r['success']) / len(dashboard_tests) * 100) if dashboard_tests else 0
        
        agency_tests = [r for r in self.test_results if 'Agency' in r['test']]
        agency_rate = (sum(1 for r in agency_tests if r['success']) / len(agency_tests) * 100) if agency_tests else 0
        
        data_tests = [r for r in self.test_results if 'Standardization' in r['test']]
        data_rate = (sum(1 for r in data_tests if r['success']) / len(data_tests) * 100) if data_tests else 0
        
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test']]
        auth_rate = (sum(1 for r in auth_tests if r['success']) / len(auth_tests) * 100) if auth_tests else 0
        
        assessment_tests = [r for r in self.test_results if 'Assessment' in r['test'] and 'Evidence' not in r['test']]
        assessment_rate = (sum(1 for r in assessment_tests if r['success']) / len(assessment_tests) * 100) if assessment_tests else 0
        
        navigator_tests = [r for r in self.test_results if 'Navigator' in r['test']]
        navigator_rate = (sum(1 for r in navigator_tests if r['success']) / len(navigator_tests) * 100) if navigator_tests else 0
        
        print(f"✅ Evidence Upload Enforcement: {evidence_rate:.0f}%")
        print(f"✅ Dashboard Data Accuracy: {dashboard_rate:.0f}%")
        print(f"✅ Agency Business Intelligence: {agency_rate:.0f}%")
        print(f"✅ Data Standardization: {data_rate:.0f}%")
        print(f"✅ Authentication System: {auth_rate:.0f}%")
        print(f"✅ Assessment Flow: {assessment_rate:.0f}%")
        print(f"✅ Navigator Review System: {navigator_rate:.0f}%")
        
        print()
        print("🎯 SUCCESS TARGETS ASSESSMENT:")
        print("-" * 40)
        
        targets_met = 0
        if evidence_rate >= 100: 
            print("✅ Evidence enforcement: 100% TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Evidence enforcement: {evidence_rate:.0f}% (Target: 100%)")
            
        if dashboard_rate >= 95:
            print("✅ Dashboard accuracy: 95%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Dashboard accuracy: {dashboard_rate:.0f}% (Target: 95%+)")
            
        if agency_rate >= 90:
            print("✅ Agency BI: 90%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Agency BI: {agency_rate:.0f}% (Target: 90%+)")
            
        if data_rate >= 100:
            print("✅ Data standardization: 100% TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Data standardization: {data_rate:.0f}% (Target: 100%)")
            
        if success_rate >= 95:
            print("✅ Overall system: 95%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Overall system: {success_rate:.1f}% (Target: 95%+)")
        
        print()
        print("🏆 PRODUCTION READINESS ASSESSMENT:")
        print("-" * 40)
        
        targets_percentage = (targets_met / 5 * 100)
        
        if targets_percentage >= 80 and success_rate >= 95:
            print("✅ EXCELLENT - System ready for production deployment")
            production_ready = True
        elif targets_percentage >= 60 and success_rate >= 85:
            print("🟡 GOOD - Minor issues identified, mostly production ready")
            production_ready = True
        elif targets_percentage >= 40 and success_rate >= 70:
            print("⚠️  MODERATE - Several issues need attention before production")
            production_ready = False
        else:
            print("🚨 CRITICAL - Major issues blocking production deployment")
            production_ready = False
        
        print(f"Targets Met: {targets_met}/5 ({targets_percentage:.0f}%)")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print()
        print("📊 QA CREDENTIALS VERIFICATION:")
        print("-" * 40)
        print(f"Client QA ({QA_CLIENT_EMAIL}): {'✅ WORKING' if self.client_token else '❌ FAILED'}")
        print(f"Agency QA ({QA_AGENCY_EMAIL}): {'✅ WORKING' if self.agency_token else '❌ FAILED'}")
        print(f"Navigator QA ({QA_NAVIGATOR_EMAIL}): {'✅ WORKING' if self.navigator_token else '❌ FAILED'}")
        
        return {
            'success_rate': success_rate,
            'production_ready': production_ready,
            'evidence_enforcement_rate': evidence_rate,
            'dashboard_accuracy_rate': dashboard_rate,
            'agency_bi_rate': agency_rate,
            'data_standardization_rate': data_rate
        }

if __name__ == "__main__":
    tester = FinalCorrectedTester()
    results = tester.run_final_validation()
    sys.exit(0 if results['production_ready'] else 1)