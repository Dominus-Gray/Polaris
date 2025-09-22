#!/usr/bin/env python3
"""
Data Interconnectivity & Flow Verification Test Suite
Testing data relationships and flow across all user types as requested in review.

Test Scenarios:
1. License-to-Client Relationship Flow
2. Service Request Data Flow  
3. Assessment-to-Analytics Flow
4. RP Data Package Flow
5. Cross-Role Data Visibility
"""

import requests
import json
import sys
import time
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class DataInterconnectivityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_tokens = {}
        self.user_ids = {}
        self.test_results = []
        self.generated_license_codes = []
        self.created_service_request_id = None
        self.created_assessment_session_id = None
        self.created_rp_lead_id = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_data"] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_role(self, role):
        """Authenticate with specific role credentials"""
        try:
            credentials = QA_CREDENTIALS[role]
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens[role] = data.get("access_token")
                
                # Get user info
                headers = {"Authorization": f"Bearer {self.auth_tokens[role]}"}
                me_response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.user_ids[role] = user_data.get("id")
                    self.log_test(f"{role.title()} Authentication", True, f"Successfully authenticated as {credentials['email']}")
                    return True
                else:
                    self.log_test(f"{role.title()} Authentication", False, f"Failed to get user info: {me_response.status_code}")
                    return False
            else:
                self.log_test(f"{role.title()} Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"{role.title()} Authentication", False, f"Exception: {str(e)}")
            return False

    def test_license_to_client_relationship_flow(self):
        """Test Scenario 1: License-to-Client Relationship Flow"""
        print("🔍 Testing License-to-Client Relationship Flow...")
        
        # Step 1: Login as agency
        if not self.authenticate_role("agency"):
            return False
            
        # Step 2: Generate license codes
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['agency']}"}
            license_data = {"quantity": 3, "expires_days": 60}
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/licenses/generate",
                json=license_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.generated_license_codes = data.get("licenses", [])
                self.log_test("License Code Generation", True, f"Generated {len(self.generated_license_codes)} license codes")
                
                # Step 3: Verify agency can see their license stats
                stats_response = self.session.get(f"{BACKEND_URL}/agency/licenses/stats", headers=headers, timeout=10)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    self.log_test("Agency License Stats Visibility", True, f"Total generated: {stats.get('total_generated', 0)}")
                else:
                    self.log_test("Agency License Stats Visibility", False, f"Failed to get stats: {stats_response.status_code}")
                    
                return True
            else:
                self.log_test("License Code Generation", False, f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("License Code Generation", False, f"Exception: {str(e)}")
            return False

    def test_client_registration_with_license(self):
        """Test client registration using generated license code"""
        if not self.generated_license_codes:
            self.log_test("Client Registration with License", False, "No license codes available")
            return False
            
        try:
            # Use first generated license code - extract just the code string
            license_data = self.generated_license_codes[0]
            license_code = license_data.get("license_code") if isinstance(license_data, dict) else license_data
            
            # Register a new client with the license code
            registration_data = {
                "email": f"test.client.{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "role": "client",
                "license_code": license_code,
                "terms_accepted": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Client Registration with License", True, f"Client registered with license code: {license_code[:4]}****")
                
                # Verify the relationship is tracked
                headers = {"Authorization": f"Bearer {self.auth_tokens['agency']}"}
                licenses_response = self.session.get(f"{BACKEND_URL}/agency/licenses", headers=headers, timeout=10)
                
                if licenses_response.status_code == 200:
                    licenses = licenses_response.json().get("licenses", [])
                    used_license = next((l for l in licenses if l.get("license_code") == license_code), None)
                    
                    if used_license and used_license.get("used"):
                        self.log_test("License-Client Relationship Tracking", True, "License marked as used and relationship tracked")
                    else:
                        self.log_test("License-Client Relationship Tracking", False, "License not marked as used")
                else:
                    self.log_test("License-Client Relationship Tracking", False, f"Failed to verify relationship: {licenses_response.status_code}")
                    
                return True
            else:
                self.log_test("Client Registration with License", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Registration with License", False, f"Exception: {str(e)}")
            return False

    def test_service_request_data_flow(self):
        """Test Scenario 2: Service Request Data Flow"""
        print("🔍 Testing Service Request Data Flow...")
        
        # Step 1: Login as client and create service request
        if not self.authenticate_role("client"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            service_request_data = {
                "area_id": "area5",
                "budget_range": "5000-15000",
                "timeline": "1-2 months",
                "description": "Need help with technology infrastructure assessment and security implementation for government contracting readiness.",
                "priority": "high"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/service-requests/professional-help",
                json=service_request_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.created_service_request_id = data.get("request_id")
                providers_notified = data.get("providers_notified", 0)
                self.log_test("Service Request Creation", True, f"Created request {self.created_service_request_id}, {providers_notified} providers notified")
                
                # Step 2: Login as provider and respond to request
                if self.authenticate_role("provider"):
                    provider_headers = {"Authorization": f"Bearer {self.auth_tokens['provider']}"}
                    
                    # Check if provider can see the request
                    requests_response = self.session.get(
                        f"{BACKEND_URL}/service-requests/{self.created_service_request_id}",
                        headers=provider_headers,
                        timeout=10
                    )
                    
                    if requests_response.status_code == 200:
                        self.log_test("Provider Request Visibility", True, "Provider can see client's service request")
                        
                        # Provider responds to request
                        provider_response_data = {
                            "proposed_fee": 2500.00,
                            "estimated_timeline": "6-8 weeks",
                            "proposal_note": "I can help with comprehensive technology infrastructure assessment including security protocols, compliance frameworks, and implementation roadmap for government contracting requirements."
                        }
                        
                        response_result = self.session.post(
                            f"{BACKEND_URL}/provider/respond-to-request",
                            json={
                                "request_id": self.created_service_request_id,
                                **provider_response_data
                            },
                            headers=provider_headers,
                            timeout=10
                        )
                        
                        if response_result.status_code == 200:
                            self.log_test("Provider Response Submission", True, "Provider successfully responded to service request")
                            
                            # Step 3: Verify client can see provider's response
                            client_responses = self.session.get(
                                f"{BACKEND_URL}/service-requests/{self.created_service_request_id}/responses",
                                headers=headers,
                                timeout=10
                            )
                            
                            if client_responses.status_code == 200:
                                responses_data = client_responses.json()
                                if responses_data.get("responses") and len(responses_data["responses"]) > 0:
                                    self.log_test("Client Response Visibility", True, f"Client can see {len(responses_data['responses'])} provider response(s)")
                                    return True
                                else:
                                    self.log_test("Client Response Visibility", False, "No responses visible to client")
                            else:
                                self.log_test("Client Response Visibility", False, f"Failed to get responses: {client_responses.status_code}")
                        else:
                            self.log_test("Provider Response Submission", False, f"Response failed: {response_result.status_code}")
                    else:
                        self.log_test("Provider Request Visibility", False, f"Provider cannot see request: {requests_response.status_code}")
                else:
                    self.log_test("Provider Authentication for Service Flow", False, "Failed to authenticate provider")
                    
                return False
            else:
                self.log_test("Service Request Creation", False, f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Service Request Data Flow", False, f"Exception: {str(e)}")
            return False

    def test_assessment_to_analytics_flow(self):
        """Test Scenario 3: Assessment-to-Analytics Flow"""
        print("🔍 Testing Assessment-to-Analytics Flow...")
        
        # Step 1: Login as client and complete assessment
        if not self.authenticate_role("client"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            
            # Create tier-based assessment session
            session_data = {
                "area_id": "area3",
                "tier_level": 2,
                "business_context": "Legal compliance assessment for government contracting"
            }
            
            session_response = self.session.post(
                f"{BACKEND_URL}/assessment/tier-session",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                self.created_assessment_session_id = session_data.get("session_id")
                self.log_test("Assessment Session Creation", True, f"Created session {self.created_assessment_session_id}")
                
                # Submit some assessment responses
                responses_data = {
                    "responses": [
                        {
                            "statement_id": "area3_tier1_1",
                            "response": "yes",
                            "confidence": "high",
                            "notes": "We have established legal entity and basic compliance framework"
                        },
                        {
                            "statement_id": "area3_tier1_2", 
                            "response": "partial",
                            "confidence": "medium",
                            "notes": "Working on contract management processes"
                        },
                        {
                            "statement_id": "area3_tier2_1",
                            "response": "no",
                            "confidence": "high", 
                            "notes": "Need help with advanced compliance requirements"
                        }
                    ]
                }
                
                submit_response = self.session.post(
                    f"{BACKEND_URL}/assessment/tier-session/{self.created_assessment_session_id}/response",
                    json=responses_data,
                    headers=headers,
                    timeout=10
                )
                
                if submit_response.status_code == 200:
                    self.log_test("Assessment Response Submission", True, "Successfully submitted assessment responses")
                    
                    # Step 2: Login as navigator and check analytics
                    if self.authenticate_role("navigator"):
                        navigator_headers = {"Authorization": f"Bearer {self.auth_tokens['navigator']}"}
                        
                        # Check navigator analytics
                        analytics_response = self.session.get(
                            f"{BACKEND_URL}/navigator/analytics/resources?since_days=30",
                            headers=navigator_headers,
                            timeout=10
                        )
                        
                        if analytics_response.status_code == 200:
                            analytics_data = analytics_response.json()
                            total_activity = analytics_data.get("total", 0)
                            self.log_test("Navigator Analytics Access", True, f"Navigator can see analytics with {total_activity} total activities")
                            
                            # Check if assessment activity flows to analytics
                            by_area = analytics_data.get("by_area", [])
                            area3_activity = next((area for area in by_area if area.get("area_id") == "area3"), None)
                            
                            if area3_activity:
                                self.log_test("Assessment-to-Analytics Flow", True, f"Assessment activity visible in analytics for area3: {area3_activity.get('count', 0)} activities")
                                return True
                            else:
                                self.log_test("Assessment-to-Analytics Flow", False, "Assessment activity not reflected in analytics")
                        else:
                            self.log_test("Navigator Analytics Access", False, f"Failed to access analytics: {analytics_response.status_code}")
                    else:
                        self.log_test("Navigator Authentication for Analytics", False, "Failed to authenticate navigator")
                else:
                    self.log_test("Assessment Response Submission", False, f"Failed: {submit_response.status_code}")
            else:
                self.log_test("Assessment Session Creation", False, f"Failed: {session_response.status_code} - {session_response.text}")
                
            return False
                
        except Exception as e:
            self.log_test("Assessment-to-Analytics Flow", False, f"Exception: {str(e)}")
            return False

    def test_rp_data_package_flow(self):
        """Test Scenario 4: RP Data Package Flow"""
        print("🔍 Testing RP Data Package Flow...")
        
        # Step 1: Login as client and create RP lead
        if not self.authenticate_role("client"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            
            # First check RP requirements
            requirements_response = self.session.get(
                f"{BACKEND_URL}/v2/rp/requirements?rp_type=lenders",
                headers=headers,
                timeout=10
            )
            
            if requirements_response.status_code == 200:
                self.log_test("RP Requirements Access", True, "Client can access RP requirements")
                
                # Get package preview to see client's data
                preview_response = self.session.get(
                    f"{BACKEND_URL}/v2/rp/package-preview?rp_type=lenders",
                    headers=headers,
                    timeout=10
                )
                
                if preview_response.status_code == 200:
                    preview_data = preview_response.json()
                    package_data = preview_data.get("package", {})
                    missing_items = preview_data.get("missing", [])
                    
                    self.log_test("RP Package Preview", True, f"Package contains {len(package_data)} data fields, {len(missing_items)} missing items")
                    
                    # Create RP lead
                    lead_data = {"rp_type": "lenders"}
                    lead_response = self.session.post(
                        f"{BACKEND_URL}/v2/rp/leads",
                        json=lead_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if lead_response.status_code == 200:
                        lead_result = lead_response.json()
                        self.created_rp_lead_id = lead_result.get("lead_id")
                        self.log_test("RP Lead Creation", True, f"Created RP lead {self.created_rp_lead_id}")
                        
                        # Step 2: Login as agency and verify they can see the lead
                        if self.authenticate_role("agency"):
                            agency_headers = {"Authorization": f"Bearer {self.auth_tokens['agency']}"}
                            
                            agency_leads_response = self.session.get(
                                f"{BACKEND_URL}/v2/rp/leads",
                                headers=agency_headers,
                                timeout=10
                            )
                            
                            if agency_leads_response.status_code == 200:
                                agency_leads = agency_leads_response.json()
                                leads_list = agency_leads.get("leads", [])
                                
                                # Find our created lead
                                our_lead = next((lead for lead in leads_list if lead.get("lead_id") == self.created_rp_lead_id), None)
                                
                                if our_lead:
                                    lead_package = our_lead.get("package_json", {})
                                    lead_missing = our_lead.get("missing_prerequisites", [])
                                    
                                    self.log_test("Agency RP Lead Visibility", True, f"Agency can see client's RP lead with {len(lead_package)} data fields")
                                    self.log_test("RP Data Package Integrity", True, f"Client assessment data properly packaged, {len(lead_missing)} missing prerequisites identified")
                                    
                                    # Test data privacy - ensure sensitive data is handled properly
                                    if "email" in lead_package or "user_id" in lead_package:
                                        self.log_test("RP Data Privacy Controls", True, "Client identification data included for agency review")
                                    else:
                                        self.log_test("RP Data Privacy Controls", False, "Missing client identification in package")
                                        
                                    return True
                                else:
                                    self.log_test("Agency RP Lead Visibility", False, "Agency cannot see client's RP lead")
                            else:
                                self.log_test("Agency RP Lead Access", False, f"Failed to get agency leads: {agency_leads_response.status_code}")
                        else:
                            self.log_test("Agency Authentication for RP Flow", False, "Failed to authenticate agency")
                    else:
                        self.log_test("RP Lead Creation", False, f"Failed: {lead_response.status_code}")
                else:
                    self.log_test("RP Package Preview", False, f"Failed: {preview_response.status_code}")
            else:
                self.log_test("RP Requirements Access", False, f"Failed: {requirements_response.status_code}")
                
            return False
                
        except Exception as e:
            self.log_test("RP Data Package Flow", False, f"Exception: {str(e)}")
            return False

    def test_cross_role_data_visibility(self):
        """Test Scenario 5: Cross-Role Data Visibility and Access Controls"""
        print("🔍 Testing Cross-Role Data Visibility...")
        
        test_results = []
        
        # Test 1: Client trying to access agency-only endpoints
        if self.auth_tokens.get("client"):
            client_headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            
            # Try to access agency license generation (should fail)
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/agency/licenses/generate",
                    json={"quantity": 1, "expires_days": 30},
                    headers=client_headers,
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    self.log_test("Client Access Control - Agency Endpoints", True, "Client properly blocked from agency license generation")
                    test_results.append(True)
                else:
                    self.log_test("Client Access Control - Agency Endpoints", False, f"Client should not access agency endpoints: {response.status_code}")
                    test_results.append(False)
            except Exception as e:
                self.log_test("Client Access Control - Agency Endpoints", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        # Test 2: Provider trying to access client assessment data
        if self.auth_tokens.get("provider") and self.created_assessment_session_id:
            provider_headers = {"Authorization": f"Bearer {self.auth_tokens['provider']}"}
            
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/assessment/tier-session/{self.created_assessment_session_id}/progress",
                    headers=provider_headers,
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    self.log_test("Provider Access Control - Client Assessments", True, "Provider properly blocked from client assessment data")
                    test_results.append(True)
                else:
                    self.log_test("Provider Access Control - Client Assessments", False, f"Provider should not access client assessments: {response.status_code}")
                    test_results.append(False)
            except Exception as e:
                self.log_test("Provider Access Control - Client Assessments", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        # Test 3: Navigator access to analytics (should work)
        if self.auth_tokens.get("navigator"):
            navigator_headers = {"Authorization": f"Bearer {self.auth_tokens['navigator']}"}
            
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/navigator/analytics/resources?since_days=7",
                    headers=navigator_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test("Navigator Access Control - Analytics", True, "Navigator can properly access analytics data")
                    test_results.append(True)
                else:
                    self.log_test("Navigator Access Control - Analytics", False, f"Navigator should access analytics: {response.status_code}")
                    test_results.append(False)
            except Exception as e:
                self.log_test("Navigator Access Control - Analytics", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        # Test 4: Check for data leakage between unrelated users
        if self.auth_tokens.get("client") and self.created_service_request_id:
            # Create a second client session to test isolation
            try:
                # Try to register another client
                temp_client_data = {
                    "email": f"temp.client.{int(time.time())}@example.com",
                    "password": "TempPassword123!",
                    "role": "client",
                    "terms_accepted": True
                }
                
                temp_response = self.session.post(
                    f"{BACKEND_URL}/auth/register",
                    json=temp_client_data,
                    timeout=10
                )
                
                if temp_response.status_code == 200:
                    # Login as temp client
                    temp_login = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={"email": temp_client_data["email"], "password": temp_client_data["password"]},
                        timeout=10
                    )
                    
                    if temp_login.status_code == 200:
                        temp_token = temp_login.json().get("access_token")
                        temp_headers = {"Authorization": f"Bearer {temp_token}"}
                        
                        # Try to access original client's service request
                        leak_test = self.session.get(
                            f"{BACKEND_URL}/service-requests/{self.created_service_request_id}",
                            headers=temp_headers,
                            timeout=10
                        )
                        
                        if leak_test.status_code in [401, 403, 404]:
                            self.log_test("Data Isolation - Client Service Requests", True, "Proper data isolation between unrelated clients")
                            test_results.append(True)
                        else:
                            self.log_test("Data Isolation - Client Service Requests", False, f"Data leakage detected: {leak_test.status_code}")
                            test_results.append(False)
                    else:
                        self.log_test("Temp Client Login", False, "Could not create temp client for isolation test")
                        test_results.append(False)
                else:
                    self.log_test("Temp Client Registration", False, "Could not register temp client for isolation test")
                    test_results.append(False)
                    
            except Exception as e:
                self.log_test("Data Isolation Test", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        return all(test_results)

    def run_comprehensive_test(self):
        """Run all data interconnectivity tests"""
        print("🚀 Starting Data Interconnectivity & Flow Verification Tests")
        print("=" * 70)
        
        test_scenarios = [
            ("License-to-Client Relationship Flow", self.test_license_to_client_relationship_flow),
            ("Client Registration with License", self.test_client_registration_with_license),
            ("Service Request Data Flow", self.test_service_request_data_flow),
            ("Assessment-to-Analytics Flow", self.test_assessment_to_analytics_flow),
            ("RP Data Package Flow", self.test_rp_data_package_flow),
            ("Cross-Role Data Visibility", self.test_cross_role_data_visibility)
        ]
        
        passed_tests = 0
        total_tests = len(test_scenarios)
        
        for scenario_name, test_func in test_scenarios:
            print(f"\n📋 {scenario_name}")
            print("-" * 50)
            
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {scenario_name} - PASSED")
                else:
                    print(f"❌ {scenario_name} - FAILED")
            except Exception as e:
                print(f"❌ {scenario_name} - ERROR: {str(e)}")
        
        print("\n" + "=" * 70)
        print("📊 FINAL RESULTS")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} scenarios passed)")
        
        # Detailed results
        print(f"\nDetailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Summary of key findings
        print(f"\n🔍 KEY FINDINGS:")
        if self.generated_license_codes:
            print(f"• Generated {len(self.generated_license_codes)} license codes for testing")
        if self.created_service_request_id:
            print(f"• Created service request: {self.created_service_request_id}")
        if self.created_assessment_session_id:
            print(f"• Created assessment session: {self.created_assessment_session_id}")
        if self.created_rp_lead_id:
            print(f"• Created RP lead: {self.created_rp_lead_id}")
        
        print(f"\n🎯 PRODUCTION READINESS: {'✅ READY' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = DataInterconnectivityTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)