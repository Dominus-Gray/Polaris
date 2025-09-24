#!/usr/bin/env python3
"""
Focused Data Interconnectivity & Flow Verification Test Suite
Testing critical data relationships and flow across user types.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FocusedDataFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_tokens = {}
        self.user_ids = {}
        self.test_results = []
        self.generated_license_codes = []
        self.created_service_request_id = None
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

    def test_license_generation_and_tracking(self):
        """Test Scenario 1: License Generation and Agency Tracking"""
        print("🔍 Testing License Generation and Agency Tracking...")
        
        if not self.authenticate_role("agency"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['agency']}"}
            
            # Generate license codes
            license_data = {"quantity": 2, "expires_days": 60}
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
                
                # Verify agency can see their license stats
                stats_response = self.session.get(f"{BACKEND_URL}/agency/licenses/stats", headers=headers, timeout=10)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    self.log_test("Agency License Stats Visibility", True, f"Total generated: {stats.get('total_generated', 0)}, Available: {stats.get('available', 0)}")
                    
                    # Verify agency can see license list
                    list_response = self.session.get(f"{BACKEND_URL}/agency/licenses", headers=headers, timeout=10)
                    if list_response.status_code == 200:
                        licenses = list_response.json().get("licenses", [])
                        self.log_test("Agency License List Access", True, f"Agency can see {len(licenses)} licenses in their list")
                        return True
                    else:
                        self.log_test("Agency License List Access", False, f"Failed to get license list: {list_response.status_code}")
                else:
                    self.log_test("Agency License Stats Visibility", False, f"Failed to get stats: {stats_response.status_code}")
                    
                return False
            else:
                self.log_test("License Code Generation", False, f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("License Generation and Tracking", False, f"Exception: {str(e)}")
            return False

    def test_service_request_provider_flow(self):
        """Test Scenario 2: Service Request Creation and Provider Response Flow"""
        print("🔍 Testing Service Request and Provider Response Flow...")
        
        # Step 1: Client creates service request
        if not self.authenticate_role("client"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            service_request_data = {
                "area_id": "area5",
                "budget_range": "5000-15000",
                "timeline": "1-2 months",
                "description": "Need comprehensive technology infrastructure assessment for government contracting readiness including security protocols and compliance frameworks.",
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
                
                # Step 2: Provider responds to request
                if self.authenticate_role("provider"):
                    provider_headers = {"Authorization": f"Bearer {self.auth_tokens['provider']}"}
                    
                    # Provider submits response
                    provider_response_data = {
                        "request_id": self.created_service_request_id,
                        "proposed_fee": 3500.00,
                        "estimated_timeline": "8-10 weeks",
                        "proposal_note": "I specialize in technology infrastructure assessments for government contracting. I can provide comprehensive security protocol evaluation, compliance framework implementation, and detailed readiness roadmap."
                    }
                    
                    response_result = self.session.post(
                        f"{BACKEND_URL}/provider/respond-to-request",
                        json=provider_response_data,
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
                            responses_list = responses_data.get("responses", [])
                            if responses_list and len(responses_list) > 0:
                                response_details = responses_list[0]
                                self.log_test("Client Response Visibility", True, f"Client can see provider response: ${response_details.get('proposed_fee', 0)} fee, timeline: {response_details.get('estimated_timeline', 'N/A')}")
                                
                                # Step 4: Verify data integrity in response
                                if response_details.get("provider_email") and response_details.get("proposal_note"):
                                    self.log_test("Service Request Data Integrity", True, "Provider response contains complete data (email, proposal, fee)")
                                    return True
                                else:
                                    self.log_test("Service Request Data Integrity", False, "Provider response missing key data fields")
                            else:
                                self.log_test("Client Response Visibility", False, "No responses visible to client")
                        else:
                            self.log_test("Client Response Visibility", False, f"Failed to get responses: {client_responses.status_code}")
                    else:
                        self.log_test("Provider Response Submission", False, f"Response failed: {response_result.status_code} - {response_result.text}")
                else:
                    self.log_test("Provider Authentication for Service Flow", False, "Failed to authenticate provider")
                    
                return False
            else:
                self.log_test("Service Request Creation", False, f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Service Request Provider Flow", False, f"Exception: {str(e)}")
            return False

    def test_navigator_analytics_access(self):
        """Test Scenario 3: Navigator Analytics Access and Data Aggregation"""
        print("🔍 Testing Navigator Analytics Access...")
        
        if not self.authenticate_role("navigator"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['navigator']}"}
            
            # Test navigator analytics access
            analytics_response = self.session.get(
                f"{BACKEND_URL}/navigator/analytics/resources?since_days=30",
                headers=headers,
                timeout=10
            )
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                total_activity = analytics_data.get("total", 0)
                by_area = analytics_data.get("by_area", [])
                last7_trend = analytics_data.get("last7", [])
                
                self.log_test("Navigator Analytics Access", True, f"Navigator can access analytics: {total_activity} total activities across {len(by_area)} areas")
                
                # Verify data structure integrity
                if by_area and len(by_area) > 0:
                    sample_area = by_area[0]
                    if sample_area.get("area_id") and sample_area.get("area_name") and "count" in sample_area:
                        self.log_test("Analytics Data Structure", True, f"Analytics data properly structured with area details")
                        
                        # Test trend data
                        if last7_trend and len(last7_trend) > 0:
                            self.log_test("Analytics Trend Data", True, f"Trend data available for last 7 days: {len(last7_trend)} data points")
                            return True
                        else:
                            self.log_test("Analytics Trend Data", False, "No trend data available")
                    else:
                        self.log_test("Analytics Data Structure", False, "Analytics data missing required fields")
                else:
                    self.log_test("Analytics Data Structure", False, "No area-specific analytics data")
            else:
                self.log_test("Navigator Analytics Access", False, f"Failed to access analytics: {analytics_response.status_code} - {analytics_response.text}")
                
            return False
                
        except Exception as e:
            self.log_test("Navigator Analytics Access", False, f"Exception: {str(e)}")
            return False

    def test_rp_data_package_flow(self):
        """Test Scenario 4: RP Data Package Creation and Agency Visibility"""
        print("🔍 Testing RP Data Package Flow...")
        
        # Step 1: Client creates RP lead with data package
        if not self.authenticate_role("client"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            
            # Get package preview first
            preview_response = self.session.get(
                f"{BACKEND_URL}/v2/rp/package-preview?rp_type=lenders",
                headers=headers,
                timeout=10
            )
            
            if preview_response.status_code == 200:
                preview_data = preview_response.json()
                package_data = preview_data.get("package", {})
                missing_items = preview_data.get("missing", [])
                
                self.log_test("RP Package Preview", True, f"Client can preview package: {len(package_data)} data fields, {len(missing_items)} missing items")
                
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
                    
                    # Step 2: Agency views the lead
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
                                lead_status = our_lead.get("status", "unknown")
                                
                                self.log_test("Agency RP Lead Visibility", True, f"Agency can see client's RP lead (status: {lead_status})")
                                self.log_test("RP Data Package Integrity", True, f"Data package contains {len(lead_package)} fields, {len(lead_missing)} missing prerequisites")
                                
                                # Verify data flow accuracy
                                if len(lead_package) > 0 and "rp_type" in our_lead:
                                    self.log_test("RP Data Flow Accuracy", True, f"Client assessment data properly packaged for RP type: {our_lead.get('rp_type')}")
                                    return True
                                else:
                                    self.log_test("RP Data Flow Accuracy", False, "Data package incomplete or missing RP type")
                            else:
                                self.log_test("Agency RP Lead Visibility", False, "Agency cannot see client's RP lead")
                        else:
                            self.log_test("Agency RP Lead Access", False, f"Failed to get agency leads: {agency_leads_response.status_code}")
                    else:
                        self.log_test("Agency Authentication for RP Flow", False, "Failed to authenticate agency")
                else:
                    self.log_test("RP Lead Creation", False, f"Failed: {lead_response.status_code} - {lead_response.text}")
            else:
                self.log_test("RP Package Preview", False, f"Failed: {preview_response.status_code} - {preview_response.text}")
                
            return False
                
        except Exception as e:
            self.log_test("RP Data Package Flow", False, f"Exception: {str(e)}")
            return False

    def test_cross_role_access_controls(self):
        """Test Scenario 5: Cross-Role Access Controls and Data Privacy"""
        print("🔍 Testing Cross-Role Access Controls...")
        
        test_results = []
        
        # Test 1: Client trying to access agency-only endpoints
        if self.auth_tokens.get("client"):
            client_headers = {"Authorization": f"Bearer {self.auth_tokens['client']}"}
            
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
        
        # Test 2: Provider trying to access navigator analytics
        if self.auth_tokens.get("provider"):
            provider_headers = {"Authorization": f"Bearer {self.auth_tokens['provider']}"}
            
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/navigator/analytics/resources?since_days=7",
                    headers=provider_headers,
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    self.log_test("Provider Access Control - Navigator Analytics", True, "Provider properly blocked from navigator analytics")
                    test_results.append(True)
                else:
                    self.log_test("Provider Access Control - Navigator Analytics", False, f"Provider should not access navigator analytics: {response.status_code}")
                    test_results.append(False)
            except Exception as e:
                self.log_test("Provider Access Control - Navigator Analytics", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        # Test 3: Verify proper role-based data visibility
        if self.auth_tokens.get("navigator"):
            navigator_headers = {"Authorization": f"Bearer {self.auth_tokens['navigator']}"}
            
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/navigator/analytics/resources?since_days=7",
                    headers=navigator_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test("Navigator Proper Access - Analytics", True, "Navigator can properly access their analytics data")
                    test_results.append(True)
                else:
                    self.log_test("Navigator Proper Access - Analytics", False, f"Navigator should access analytics: {response.status_code}")
                    test_results.append(False)
            except Exception as e:
                self.log_test("Navigator Proper Access - Analytics", False, f"Exception: {str(e)}")
                test_results.append(False)
        
        return all(test_results)

    def run_comprehensive_test(self):
        """Run focused data interconnectivity tests"""
        print("🚀 Starting Focused Data Interconnectivity & Flow Verification Tests")
        print("=" * 80)
        
        test_scenarios = [
            ("License Generation and Agency Tracking", self.test_license_generation_and_tracking),
            ("Service Request and Provider Response Flow", self.test_service_request_provider_flow),
            ("Navigator Analytics Access", self.test_navigator_analytics_access),
            ("RP Data Package Flow", self.test_rp_data_package_flow),
            ("Cross-Role Access Controls", self.test_cross_role_access_controls)
        ]
        
        passed_tests = 0
        total_tests = len(test_scenarios)
        
        for scenario_name, test_func in test_scenarios:
            print(f"\n📋 {scenario_name}")
            print("-" * 60)
            
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {scenario_name} - PASSED")
                else:
                    print(f"❌ {scenario_name} - FAILED")
            except Exception as e:
                print(f"❌ {scenario_name} - ERROR: {str(e)}")
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} scenarios passed)")
        
        # Key findings summary
        print(f"\n🔍 KEY FINDINGS:")
        if self.generated_license_codes:
            print(f"• Generated {len(self.generated_license_codes)} license codes for testing")
        if self.created_service_request_id:
            print(f"• Created service request: {self.created_service_request_id}")
        if self.created_rp_lead_id:
            print(f"• Created RP lead: {self.created_rp_lead_id}")
        
        # Detailed results summary
        passed_count = sum(1 for result in self.test_results if result["success"])
        total_count = len(self.test_results)
        print(f"• Individual test success rate: {(passed_count/total_count)*100:.1f}% ({passed_count}/{total_count})")
        
        print(f"\n🎯 PRODUCTION READINESS: {'✅ READY' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = FocusedDataFlowTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)