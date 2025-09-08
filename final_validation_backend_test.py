#!/usr/bin/env python3
"""
FINAL VALIDATION - COMPREHENSIVE SYSTEM TESTING
Testing Focus: Evidence Upload Enforcement, Dashboard Data Accuracy, Agency BI, Data Standardization
QA Credentials: client.qa@polaris.example.com / Polaris#2025!, agency.qa@polaris.example.com / Polaris#2025!, navigator.qa@polaris.example.com / Polaris#2025!

CRITICAL FIXES TO VERIFY:
1. Evidence Upload Enforcement (CRITICAL) - Backend endpoint `/assessment/tier-session/{session_id}/response` enhanced with validation
2. Dashboard Data Accuracy - Enhanced `/home/client` endpoint with real-time tier-based assessment data  
3. Agency Business Intelligence - New `/agency/business-intelligence` endpoint operational
4. Data Standardization - UUID-based identifiers across all user accounts
5. Authentication System - All QA credentials (client, agency, navigator)
6. Evidence Upload System - File upload, storage, enforcement validation
7. Navigator Review System - Evidence review and approval workflow

SUCCESS TARGETS:
- Evidence enforcement: 100% (proper 422 blocking)
- Dashboard accuracy: 95%+ (real-time data)
- Agency BI: 90%+ (comprehensive tracking)
- Data standardization: 100% (consistent formats)
- Overall system: 95%+ success rate
"""

import requests
import json
import time
from datetime import datetime
import sys
import os
import tempfile

# Configuration
BASE_URL = "https://biz-matchmaker-1.preview.emergentagent.com/api"
QA_CLIENT_EMAIL = "client.qa@polaris.example.com"
QA_CLIENT_PASSWORD = "Polaris#2025!"
QA_AGENCY_EMAIL = "agency.qa@polaris.example.com"
QA_AGENCY_PASSWORD = "Polaris#2025!"
QA_NAVIGATOR_EMAIL = "navigator.qa@polaris.example.com"
QA_NAVIGATOR_PASSWORD = "Polaris#2025!"

class FinalValidationTester:
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
        if not success and response_data:
            print(f"   Response: {response_data}")
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

    def test_authentication_system_all_roles(self):
        """Test 1: Authentication System - All QA credentials (client, agency, navigator)"""
        print("🔐 Testing Authentication System - All QA Roles...")
        
        # Test client login
        login_data = {
            "email": QA_CLIENT_EMAIL,
            "password": QA_CLIENT_PASSWORD
        }
        
        response = self.make_request('POST', '/auth/login', json=login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.client_token = data.get('access_token')
            self.log_test(
                "Client QA Authentication", 
                True, 
                f"Successfully logged in as {QA_CLIENT_EMAIL}",
                {"token_length": len(self.client_token) if self.client_token else 0}
            )
        else:
            self.log_test(
                "Client QA Authentication", 
                False, 
                f"Failed to login as {QA_CLIENT_EMAIL}",
                response.json() if response else "No response"
            )

        # Test agency login
        agency_login_data = {
            "email": QA_AGENCY_EMAIL,
            "password": QA_AGENCY_PASSWORD
        }
        
        response = self.make_request('POST', '/auth/login', json=agency_login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.agency_token = data.get('access_token')
            self.log_test(
                "Agency QA Authentication", 
                True, 
                f"Successfully logged in as {QA_AGENCY_EMAIL}",
                {"token_length": len(self.agency_token) if self.agency_token else 0}
            )
        else:
            self.log_test(
                "Agency QA Authentication", 
                False, 
                f"Failed to login as {QA_AGENCY_EMAIL}",
                response.json() if response else "No response"
            )

        # Test navigator login
        navigator_login_data = {
            "email": QA_NAVIGATOR_EMAIL,
            "password": QA_NAVIGATOR_PASSWORD
        }
        
        response = self.make_request('POST', '/auth/login', json=navigator_login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.navigator_token = data.get('access_token')
            self.log_test(
                "Navigator QA Authentication", 
                True, 
                f"Successfully logged in as {QA_NAVIGATOR_EMAIL}",
                {"token_length": len(self.navigator_token) if self.navigator_token else 0}
            )
        else:
            self.log_test(
                "Navigator QA Authentication", 
                False, 
                f"Failed to login as {QA_NAVIGATOR_EMAIL}",
                response.json() if response else "No response"
            )

        return True

    def test_evidence_upload_enforcement(self):
        """Test 2: Evidence Upload Enforcement (CRITICAL) - HTTP 422 blocking for Tier 2/3 without evidence"""
        print("📋 Testing Evidence Upload Enforcement (CRITICAL)...")
        
        if not self.client_token:
            self.log_test("Evidence Upload Enforcement", False, "No client token available")
            return False

        # Create a Tier 2 assessment session first
        session_data = {
            "area_id": "area1",
            "tier_level": 2  # Tier 2 requires evidence
        }
        
        response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, data=session_data)
        
        if response and response.status_code == 200:
            session_response = response.json()
            session_id = session_response.get('session_id')
            self.test_session_id = session_id
            
            self.log_test(
                "Tier 2 Assessment Session Creation", 
                True, 
                f"Created Tier 2 assessment session for area1",
                {"session_id": session_id, "tier_level": 2}
            )
            
            # Test 1: Submit Tier 2 compliant response WITHOUT evidence (should be blocked with 422)
            response_data_no_evidence = {
                "question_id": "area1_q4",  # Tier 2 question
                "response": "compliant",
                "evidence_provided": False
            }
            
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{session_id}/response', 
                token=self.client_token, 
                json=response_data_no_evidence
            )
            
            if response and response.status_code == 422:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 Blocking", 
                    True, 
                    "✅ CRITICAL: System correctly blocks Tier 2 compliant responses without evidence (HTTP 422)",
                    {"status_code": response.status_code, "response": response.json()}
                )
            else:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 Blocking", 
                    False, 
                    f"❌ CRITICAL FAILURE: System should block Tier 2 responses without evidence but returned {response.status_code if response else 'No response'}",
                    response.json() if response else "No response"
                )
            
            # Test 2: Submit Tier 2 compliant response WITH evidence (should succeed)
            response_data_with_evidence = {
                "question_id": "area1_q4",
                "response": "compliant", 
                "evidence_provided": True,
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{session_id}/response', 
                token=self.client_token, 
                json=response_data_with_evidence
            )
            
            if response and response.status_code == 200:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 With Evidence", 
                    True, 
                    "✅ System correctly accepts Tier 2 compliant responses with evidence",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 2 With Evidence", 
                    False, 
                    f"System should accept Tier 2 responses with evidence but returned {response.status_code if response else 'No response'}",
                    response.json() if response else "No response"
                )
                
        else:
            self.log_test(
                "Tier 2 Assessment Session Creation", 
                False, 
                "Failed to create Tier 2 assessment session",
                response.json() if response else "No response"
            )

        # Test 3: Create Tier 3 session and test evidence enforcement
        tier3_session_data = {
            "area_id": "area2", 
            "tier_level": 3  # Tier 3 requires evidence
        }
        
        response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, data=tier3_session_data)
        
        if response and response.status_code == 200:
            session_response = response.json()
            tier3_session_id = session_response.get('session_id')
            
            # Test Tier 3 compliant response WITHOUT evidence (should be blocked with 422)
            tier3_response_data = {
                "question_id": "area2_q7",  # Tier 3 question
                "response": "compliant",
                "evidence_provided": False
            }
            
            response = self.make_request(
                'POST', 
                f'/assessment/tier-session/{tier3_session_id}/response', 
                token=self.client_token, 
                json=tier3_response_data
            )
            
            if response and response.status_code == 422:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 3 Blocking", 
                    True, 
                    "✅ CRITICAL: System correctly blocks Tier 3 compliant responses without evidence (HTTP 422)",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Evidence Upload Enforcement - Tier 3 Blocking", 
                    False, 
                    f"❌ CRITICAL FAILURE: System should block Tier 3 responses without evidence but returned {response.status_code if response else 'No response'}",
                    response.json() if response else "No response"
                )

        return True

    def test_evidence_upload_system(self):
        """Test 3: Evidence Upload System - File upload, storage, multi-file support"""
        print("📁 Testing Evidence Upload System...")
        
        if not self.client_token or not self.test_session_id:
            self.log_test("Evidence Upload System", False, "Missing client token or test session")
            return False

        # Test evidence file upload endpoint
        # Create a temporary test file
        test_file_content = b"This is a test evidence document for Polaris assessment validation."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(test_file_content)
            temp_file_path = temp_file.name

        try:
            # Test single file upload
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_evidence.pdf', f, 'application/pdf')}
                data = {
                    'session_id': self.test_session_id,
                    'question_id': 'area1_q4'
                }
                
                response = self.make_request(
                    'POST', 
                    '/assessment/evidence/upload', 
                    token=self.client_token, 
                    files=files,
                    data=data
                )
                
                if response and response.status_code == 200:
                    upload_response = response.json()
                    self.log_test(
                        "Evidence File Upload", 
                        True, 
                        f"Successfully uploaded evidence file",
                        {
                            "status_code": response.status_code,
                            "file_id": upload_response.get('file_id'),
                            "storage_path": upload_response.get('storage_path')
                        }
                    )
                else:
                    self.log_test(
                        "Evidence File Upload", 
                        False, 
                        f"Failed to upload evidence file - Status: {response.status_code if response else 'No response'}",
                        response.json() if response else "No response"
                    )

            # Test multi-file upload support
            with open(temp_file_path, 'rb') as f1:
                # Create second test file
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file2:
                    temp_file2.write(b"Second test document for multi-file upload validation.")
                    temp_file2_path = temp_file2.name

                try:
                    with open(temp_file2_path, 'rb') as f2:
                        files = [
                            ('files', ('evidence1.pdf', f1, 'application/pdf')),
                            ('files', ('evidence2.docx', f2, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
                        ]
                        data = {
                            'session_id': self.test_session_id,
                            'question_id': 'area1_q5'
                        }
                        
                        response = self.make_request(
                            'POST', 
                            '/assessment/evidence/upload-multiple', 
                            token=self.client_token, 
                            files=files,
                            data=data
                        )
                        
                        if response and response.status_code == 200:
                            self.log_test(
                                "Multi-File Evidence Upload", 
                                True, 
                                "Successfully uploaded multiple evidence files",
                                {"status_code": response.status_code, "files_count": 2}
                            )
                        else:
                            # Multi-file might not be implemented, try alternative
                            self.log_test(
                                "Multi-File Evidence Upload", 
                                False, 
                                f"Multi-file upload not available - Status: {response.status_code if response else 'No response'}",
                                response.json() if response else "No response"
                            )
                finally:
                    os.unlink(temp_file2_path)

        finally:
            os.unlink(temp_file_path)

        return True

    def test_dashboard_data_accuracy(self):
        """Test 4: Dashboard Data Accuracy - Real-time tier-based assessment data"""
        print("📊 Testing Dashboard Data Accuracy...")
        
        if not self.client_token:
            self.log_test("Dashboard Data Accuracy", False, "No client token available")
            return False

        # Test enhanced /home/client endpoint
        response = self.make_request('GET', '/home/client', token=self.client_token)
        
        if response and response.status_code == 200:
            dashboard_data = response.json()
            
            # Check for real-time data indicators
            has_assessment_completion = 'assessment_completion' in dashboard_data or 'assessment_complete' in dashboard_data
            has_critical_gaps = 'critical_gaps' in dashboard_data
            has_evidence_status = 'evidence_status' in dashboard_data or 'evidence' in dashboard_data
            has_tier_data = any('tier' in str(key).lower() for key in dashboard_data.keys())
            
            # Check for dynamic vs static data
            completion_value = dashboard_data.get('assessment_completion', dashboard_data.get('assessment_complete', 0))
            gaps_value = dashboard_data.get('critical_gaps', 0)
            
            # Real-time data should not be exactly 0% or 100% for test accounts
            is_dynamic_data = completion_value not in [0, 100] or gaps_value > 0
            
            accuracy_score = 0
            if has_assessment_completion: accuracy_score += 25
            if has_critical_gaps: accuracy_score += 25  
            if has_evidence_status: accuracy_score += 25
            if has_tier_data: accuracy_score += 25
            
            self.log_test(
                "Dashboard Data Accuracy", 
                accuracy_score >= 75,  # 75% = 3/4 required fields
                f"Dashboard accuracy: {accuracy_score}% - Assessment: {has_assessment_completion}, Gaps: {has_critical_gaps}, Evidence: {has_evidence_status}, Tier Data: {has_tier_data}",
                {
                    "accuracy_score": accuracy_score,
                    "completion_value": completion_value,
                    "gaps_value": gaps_value,
                    "is_dynamic": is_dynamic_data,
                    "data_keys": list(dashboard_data.keys())
                }
            )
            
            # Test real-time calculation
            if is_dynamic_data:
                self.log_test(
                    "Real-time Data Calculation", 
                    True, 
                    f"Dashboard shows dynamic data - Completion: {completion_value}%, Gaps: {gaps_value}",
                    {"completion": completion_value, "gaps": gaps_value}
                )
            else:
                self.log_test(
                    "Real-time Data Calculation", 
                    False, 
                    f"Dashboard appears to show static data - Completion: {completion_value}%, Gaps: {gaps_value}",
                    {"completion": completion_value, "gaps": gaps_value}
                )
                
        else:
            self.log_test(
                "Dashboard Data Accuracy", 
                False, 
                f"Failed to retrieve dashboard data - Status: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

        return True

    def test_agency_business_intelligence(self):
        """Test 5: Agency Business Intelligence - New /agency/business-intelligence endpoint"""
        print("📈 Testing Agency Business Intelligence...")
        
        if not self.agency_token:
            self.log_test("Agency Business Intelligence", False, "No agency token available")
            return False

        # Test agency business intelligence endpoint
        response = self.make_request('GET', '/agency/business-intelligence', token=self.agency_token)
        
        if response and response.status_code == 200:
            bi_data = response.json()
            
            # Check for comprehensive client compliance tracking
            has_client_tracking = 'client_compliance' in bi_data or 'clients' in bi_data
            has_governance_alerts = 'governance_alerts' in bi_data or 'alerts' in bi_data
            has_monthly_activity = 'monthly_activity' in bi_data or 'activity' in bi_data
            has_compliance_metrics = 'compliance_metrics' in bi_data or 'metrics' in bi_data
            
            bi_score = 0
            if has_client_tracking: bi_score += 25
            if has_governance_alerts: bi_score += 25
            if has_monthly_activity: bi_score += 25
            if has_compliance_metrics: bi_score += 25
            
            self.log_test(
                "Agency Business Intelligence", 
                bi_score >= 75,  # 75% = 3/4 required features
                f"Agency BI completeness: {bi_score}% - Client Tracking: {has_client_tracking}, Alerts: {has_governance_alerts}, Activity: {has_monthly_activity}, Metrics: {has_compliance_metrics}",
                {
                    "bi_score": bi_score,
                    "data_keys": list(bi_data.keys()),
                    "client_count": len(bi_data.get('clients', [])) if isinstance(bi_data.get('clients'), list) else 0
                }
            )
            
        else:
            self.log_test(
                "Agency Business Intelligence", 
                False, 
                f"Failed to access agency BI endpoint - Status: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

        return True

    def test_data_standardization(self):
        """Test 6: Data Standardization - UUID-based identifiers, consistent datetime formatting"""
        print("🔧 Testing Data Standardization...")
        
        if not self.client_token:
            self.log_test("Data Standardization", False, "No client token available")
            return False

        # Test user account data standardization
        response = self.make_request('GET', '/auth/me', token=self.client_token)
        
        if response and response.status_code == 200:
            user_data = response.json()
            
            # Check UUID format for user ID
            user_id = user_data.get('id', '')
            is_uuid_format = len(user_id) == 36 and user_id.count('-') == 4
            
            # Check datetime format
            created_at = user_data.get('created_at', '')
            is_iso_datetime = 'T' in created_at and ('Z' in created_at or '+' in created_at)
            
            self.log_test(
                "User Data Standardization", 
                is_uuid_format and is_iso_datetime,
                f"UUID format: {is_uuid_format} ({user_id}), ISO datetime: {is_iso_datetime} ({created_at})",
                {"user_id": user_id, "created_at": created_at, "uuid_valid": is_uuid_format, "datetime_valid": is_iso_datetime}
            )

        # Test assessment session data standardization
        if self.test_session_id:
            response = self.make_request('GET', f'/assessment/tier-session/{self.test_session_id}/progress', token=self.client_token)
            
            if response and response.status_code == 200:
                session_data = response.json()
                
                # Check session ID format
                session_id = session_data.get('session_id', self.test_session_id)
                is_session_uuid = len(session_id) == 36 and session_id.count('-') == 4
                
                # Check for consistent data structures
                has_standard_fields = all(field in session_data for field in ['session_id', 'area_id'])
                
                self.log_test(
                    "Assessment Data Standardization", 
                    is_session_uuid and has_standard_fields,
                    f"Session UUID: {is_session_uuid}, Standard fields: {has_standard_fields}",
                    {"session_id": session_id, "uuid_valid": is_session_uuid, "fields_valid": has_standard_fields}
                )

        # Test service request data standardization (if available)
        service_request_data = {
            "area_id": "area1",
            "budget_range": "1500-5000", 
            "timeline": "2-4 weeks",
            "description": "Test service request for data standardization validation",
            "priority": "medium"
        }
        
        response = self.make_request('POST', '/service-requests/professional-help', token=self.client_token, json=service_request_data)
        
        if response and response.status_code == 200:
            request_response = response.json()
            request_id = request_response.get('request_id', '')
            
            # Check request ID format
            is_request_uuid = len(request_id) == 36 and request_id.count('-') == 4
            
            self.log_test(
                "Service Request Data Standardization", 
                is_request_uuid,
                f"Request UUID format: {is_request_uuid} ({request_id})",
                {"request_id": request_id, "uuid_valid": is_request_uuid}
            )

        return True

    def test_navigator_review_system(self):
        """Test 7: Navigator Review System - Evidence review and approval workflow"""
        print("👨‍💼 Testing Navigator Review System...")
        
        if not self.navigator_token:
            self.log_test("Navigator Review System", False, "No navigator token available")
            return False

        # Test navigator evidence review endpoints
        response = self.make_request('GET', '/navigator/evidence/pending', token=self.navigator_token)
        
        if response and response.status_code == 200:
            pending_evidence = response.json()
            
            evidence_count = len(pending_evidence) if isinstance(pending_evidence, list) else len(pending_evidence.get('evidence', []))
            
            self.log_test(
                "Navigator Evidence Review Access", 
                True,
                f"Navigator can access pending evidence review queue ({evidence_count} items)",
                {"evidence_count": evidence_count, "status_code": response.status_code}
            )
            
            # Test evidence approval workflow if evidence exists
            if evidence_count > 0:
                evidence_item = pending_evidence[0] if isinstance(pending_evidence, list) else pending_evidence.get('evidence', [{}])[0]
                evidence_id = evidence_item.get('id') or evidence_item.get('evidence_id')
                
                if evidence_id:
                    # Test evidence approval
                    approval_data = {
                        "evidence_id": evidence_id,
                        "status": "approved",
                        "notes": "Evidence meets compliance requirements"
                    }
                    
                    response = self.make_request('POST', '/navigator/evidence/review', token=self.navigator_token, json=approval_data)
                    
                    if response and response.status_code == 200:
                        self.log_test(
                            "Navigator Evidence Approval", 
                            True,
                            f"Successfully approved evidence item {evidence_id}",
                            {"evidence_id": evidence_id, "status": "approved"}
                        )
                    else:
                        self.log_test(
                            "Navigator Evidence Approval", 
                            False,
                            f"Failed to approve evidence - Status: {response.status_code if response else 'No response'}",
                            response.json() if response else "No response"
                        )
                        
        else:
            self.log_test(
                "Navigator Evidence Review Access", 
                False,
                f"Failed to access navigator evidence review - Status: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

        # Test navigator dashboard/overview
        response = self.make_request('GET', '/navigator/dashboard', token=self.navigator_token)
        
        if response and response.status_code == 200:
            navigator_dashboard = response.json()
            
            has_review_queue = 'pending_reviews' in navigator_dashboard or 'evidence_queue' in navigator_dashboard
            has_approval_stats = 'approval_stats' in navigator_dashboard or 'stats' in navigator_dashboard
            
            self.log_test(
                "Navigator Dashboard Access", 
                has_review_queue or has_approval_stats,
                f"Navigator dashboard accessible - Review queue: {has_review_queue}, Stats: {has_approval_stats}",
                {"has_queue": has_review_queue, "has_stats": has_approval_stats}
            )
        else:
            self.log_test(
                "Navigator Dashboard Access", 
                False,
                f"Navigator dashboard not accessible - Status: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

        return True

    def run_final_validation(self):
        """Run comprehensive final validation test"""
        print("🚀 FINAL VALIDATION - COMPREHENSIVE SYSTEM TESTING")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all validation tests
        self.test_authentication_system_all_roles()
        self.test_evidence_upload_enforcement()
        self.test_evidence_upload_system()
        self.test_dashboard_data_accuracy()
        self.test_agency_business_intelligence()
        self.test_data_standardization()
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
        
        # Evidence enforcement findings (CRITICAL)
        evidence_tests = [r for r in self.test_results if 'Evidence' in r['test']]
        evidence_success = all(r['success'] for r in evidence_tests)
        evidence_rate = (sum(1 for r in evidence_tests if r['success']) / len(evidence_tests) * 100) if evidence_tests else 0
        print(f"✅ Evidence Upload Enforcement: {evidence_rate:.0f}% ({'OPERATIONAL' if evidence_success else 'ISSUES DETECTED'})")
        
        # Dashboard accuracy findings
        dashboard_tests = [r for r in self.test_results if 'Dashboard' in r['test']]
        dashboard_success = all(r['success'] for r in dashboard_tests)
        dashboard_rate = (sum(1 for r in dashboard_tests if r['success']) / len(dashboard_tests) * 100) if dashboard_tests else 0
        print(f"✅ Dashboard Data Accuracy: {dashboard_rate:.0f}% ({'OPERATIONAL' if dashboard_success else 'ISSUES DETECTED'})")
        
        # Agency BI findings
        agency_tests = [r for r in self.test_results if 'Agency' in r['test']]
        agency_success = all(r['success'] for r in agency_tests)
        agency_rate = (sum(1 for r in agency_tests if r['success']) / len(agency_tests) * 100) if agency_tests else 0
        print(f"✅ Agency Business Intelligence: {agency_rate:.0f}% ({'OPERATIONAL' if agency_success else 'ISSUES DETECTED'})")
        
        # Data standardization findings
        data_tests = [r for r in self.test_results if 'Standardization' in r['test']]
        data_success = all(r['success'] for r in data_tests)
        data_rate = (sum(1 for r in data_tests if r['success']) / len(data_tests) * 100) if data_tests else 0
        print(f"✅ Data Standardization: {data_rate:.0f}% ({'OPERATIONAL' if data_success else 'ISSUES DETECTED'})")
        
        # Authentication findings
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test']]
        auth_success = all(r['success'] for r in auth_tests)
        auth_rate = (sum(1 for r in auth_tests if r['success']) / len(auth_tests) * 100) if auth_tests else 0
        print(f"✅ Authentication System: {auth_rate:.0f}% ({'OPERATIONAL' if auth_success else 'ISSUES DETECTED'})")
        
        # Navigator system findings
        navigator_tests = [r for r in self.test_results if 'Navigator' in r['test']]
        navigator_success = all(r['success'] for r in navigator_tests)
        navigator_rate = (sum(1 for r in navigator_tests if r['success']) / len(navigator_tests) * 100) if navigator_tests else 0
        print(f"✅ Navigator Review System: {navigator_rate:.0f}% ({'OPERATIONAL' if navigator_success else 'ISSUES DETECTED'})")
        
        print()
        print("🎯 SUCCESS TARGETS ASSESSMENT:")
        print("-" * 40)
        
        # Check against success targets
        targets_met = 0
        total_targets = 5
        
        if evidence_rate >= 100:  # Evidence enforcement: 100%
            print("✅ Evidence enforcement: 100% TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Evidence enforcement: {evidence_rate:.0f}% (Target: 100%)")
            
        if dashboard_rate >= 95:  # Dashboard accuracy: 95%+
            print("✅ Dashboard accuracy: 95%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Dashboard accuracy: {dashboard_rate:.0f}% (Target: 95%+)")
            
        if agency_rate >= 90:  # Agency BI: 90%+
            print("✅ Agency BI: 90%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Agency BI: {agency_rate:.0f}% (Target: 90%+)")
            
        if data_rate >= 100:  # Data standardization: 100%
            print("✅ Data standardization: 100% TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Data standardization: {data_rate:.0f}% (Target: 100%)")
            
        if success_rate >= 95:  # Overall system: 95%+
            print("✅ Overall system: 95%+ TARGET MET")
            targets_met += 1
        else:
            print(f"❌ Overall system: {success_rate:.1f}% (Target: 95%+)")
        
        print()
        print("🏆 PRODUCTION READINESS ASSESSMENT:")
        print("-" * 40)
        
        targets_percentage = (targets_met / total_targets * 100)
        
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
        
        print(f"Targets Met: {targets_met}/{total_targets} ({targets_percentage:.0f}%)")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print()
        print("📊 QA CREDENTIALS VERIFICATION:")
        print("-" * 40)
        print(f"Client QA ({QA_CLIENT_EMAIL}): {'✅ WORKING' if self.client_token else '❌ FAILED'}")
        print(f"Agency QA ({QA_AGENCY_EMAIL}): {'✅ WORKING' if self.agency_token else '❌ FAILED'}")
        print(f"Navigator QA ({QA_NAVIGATOR_EMAIL}): {'✅ WORKING' if self.navigator_token else '❌ FAILED'}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'duration': duration,
            'targets_met': targets_met,
            'targets_percentage': targets_percentage,
            'production_ready': production_ready,
            'evidence_enforcement_rate': evidence_rate,
            'dashboard_accuracy_rate': dashboard_rate,
            'agency_bi_rate': agency_rate,
            'data_standardization_rate': data_rate,
            'auth_rate': auth_rate,
            'navigator_rate': navigator_rate
        }

if __name__ == "__main__":
    tester = FinalValidationTester()
    results = tester.run_final_validation()
    
    # Exit with appropriate code
    sys.exit(0 if results['production_ready'] else 1)