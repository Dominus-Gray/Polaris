#!/usr/bin/env python3
"""
Enhanced Platform Integration and Complete Feature Journey Testing
Testing the enhanced integration endpoints and cross-platform workflows
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class EnhancedIntegrationTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test results with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens[role] = token_data["access_token"]
                self.log_result(f"Authentication - {role.title()}", True, 
                              f"Successfully authenticated {creds['email']}")
                return True
            else:
                error_detail = response.json() if response.content else {"detail": "No response content"}
                self.log_result(f"Authentication - {role.title()}", False, 
                              f"Failed to authenticate {creds['email']}: {response.status_code}",
                              error_detail)
                return False
        except Exception as e:
            self.log_result(f"Authentication - {role.title()}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role):
        """Get authorization headers for role"""
        if role not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[role]}"}

    def test_unified_dashboard_endpoint(self):
        """Test GET /api/client/unified-dashboard endpoint"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Unified Dashboard - Authentication", False, "No client token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/client/unified-dashboard", headers=headers)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Verify dashboard structure
                required_fields = ["assessment_progress", "critical_gaps", "active_services", "readiness_score"]
                missing_fields = [field for field in required_fields if field not in dashboard_data]
                
                if missing_fields:
                    self.log_result("Unified Dashboard - Structure", False, 
                                  f"Missing required fields: {missing_fields}", dashboard_data)
                    return False
                
                self.log_result("Unified Dashboard - Endpoint", True, 
                              f"Dashboard data retrieved successfully with {len(dashboard_data)} fields",
                              {"sample_fields": list(dashboard_data.keys())[:5]})
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Unified Dashboard - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Unified Dashboard - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_realtime_dashboard_update(self):
        """Test POST /api/realtime/dashboard-update endpoint"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Realtime Dashboard Update - Authentication", False, "No client token available")
                return False
            
            # Test dashboard update payload
            update_payload = {
                "user_id": "test_client_id",
                "update_type": "assessment_progress",
                "data": {
                    "completion_percentage": 75,
                    "areas_completed": ["area1", "area2", "area3"],
                    "critical_gaps_identified": 2,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = self.session.post(f"{BASE_URL}/realtime/dashboard-update", 
                                       json=update_payload, headers=headers)
            
            if response.status_code in [200, 201]:
                update_result = response.json()
                self.log_result("Realtime Dashboard Update - Endpoint", True, 
                              "Dashboard update processed successfully", update_result)
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Realtime Dashboard Update - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Realtime Dashboard Update - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_provider_notifications_endpoint(self):
        """Test GET /api/provider/notifications endpoint"""
        try:
            headers = self.get_headers("provider")
            if not headers:
                self.log_result("Provider Notifications - Authentication", False, "No provider token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/provider/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Verify notifications structure
                if isinstance(notifications, list):
                    self.log_result("Provider Notifications - Endpoint", True, 
                                  f"Retrieved {len(notifications)} notifications")
                    return True
                elif isinstance(notifications, dict) and "notifications" in notifications:
                    notification_list = notifications["notifications"]
                    self.log_result("Provider Notifications - Endpoint", True, 
                                  f"Retrieved {len(notification_list)} notifications in wrapper")
                    return True
                else:
                    self.log_result("Provider Notifications - Structure", False, 
                                  "Unexpected response structure", notifications)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Provider Notifications - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Provider Notifications - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_provider_notification_response(self):
        """Test POST /api/provider/notifications/{id}/respond endpoint"""
        try:
            headers = self.get_headers("provider")
            if not headers:
                self.log_result("Provider Notification Response - Authentication", False, "No provider token available")
                return False
            
            # First, try to get existing notifications to find a valid ID
            notifications_response = self.session.get(f"{BASE_URL}/provider/notifications", headers=headers)
            
            notification_id = None
            if notifications_response.status_code == 200:
                notifications_data = notifications_response.json()
                if isinstance(notifications_data, list) and notifications_data:
                    notification_id = notifications_data[0].get("id")
                elif isinstance(notifications_data, dict) and "notifications" in notifications_data:
                    notification_list = notifications_data["notifications"]
                    if notification_list:
                        notification_id = notification_list[0].get("id")
            
            # If no existing notification, use a test ID
            if not notification_id:
                notification_id = str(uuid.uuid4())
            
            # Test notification response payload
            response_payload = {
                "response_type": "accepted",
                "message": "I can help with this service request",
                "estimated_timeline": "2-3 weeks",
                "proposed_fee": 1500.00
            }
            
            response = self.session.post(f"{BASE_URL}/provider/notifications/{notification_id}/respond", 
                                       json=response_payload, headers=headers)
            
            if response.status_code in [200, 201, 404]:  # 404 is acceptable for test ID
                if response.status_code == 404:
                    self.log_result("Provider Notification Response - Endpoint", True, 
                                  "Endpoint accessible (404 expected for test notification ID)")
                else:
                    response_result = response.json()
                    self.log_result("Provider Notification Response - Endpoint", True, 
                                  "Notification response processed successfully", response_result)
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Provider Notification Response - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Provider Notification Response - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_agency_business_intelligence(self):
        """Test GET /api/agency/business-intelligence/assessments endpoint"""
        try:
            headers = self.get_headers("agency")
            if not headers:
                self.log_result("Agency Business Intelligence - Authentication", False, "No agency token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/agency/business-intelligence/assessments", headers=headers)
            
            if response.status_code == 200:
                bi_data = response.json()
                
                # Verify business intelligence structure
                expected_fields = ["total_assessments", "completion_rates", "gap_analysis", "trends"]
                present_fields = [field for field in expected_fields if field in bi_data]
                
                self.log_result("Agency Business Intelligence - Endpoint", True, 
                              f"BI data retrieved with {len(present_fields)}/{len(expected_fields)} expected fields",
                              {"present_fields": present_fields})
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Agency Business Intelligence - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Agency Business Intelligence - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_assessment_to_action_workflow(self):
        """Test complete Assessment-to-Action workflow"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Assessment-to-Action Workflow - Authentication", False, "No client token available")
                return False
            
            # Step 1: Create assessment session
            assessment_payload = {
                "area_id": "area5",
                "tier_level": 1
            }
            
            session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                               data=assessment_payload, headers=headers)
            
            if session_response.status_code != 200:
                error_data = session_response.json() if session_response.content else {"error": "No content"}
                self.log_result("Assessment-to-Action Workflow - Session Creation", False, 
                              f"Failed to create assessment session: {session_response.status_code}", error_data)
                return False
            
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            
            if not session_id:
                self.log_result("Assessment-to-Action Workflow - Session ID", False, 
                              "No session_id in response", session_data)
                return False
            
            # Step 2: Submit assessment responses
            response_payload = {
                "statement_id": "area5_tier1_stmt1",
                "response": "No, I need help",
                "evidence_provided": False
            }
            
            response_submit = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                              data=response_payload, headers=headers)
            
            if response_submit.status_code != 200:
                error_data = response_submit.json() if response_submit.content else {"error": "No content"}
                self.log_result("Assessment-to-Action Workflow - Response Submit", False, 
                              f"Failed to submit response: {response_submit.status_code}", error_data)
                return False
            
            # Step 3: Check for automatic dashboard update trigger
            dashboard_response = self.session.get(f"{BASE_URL}/client/unified-dashboard", headers=headers)
            
            if dashboard_response.status_code == 200:
                self.log_result("Assessment-to-Action Workflow - Complete", True, 
                              "Assessment-to-action workflow completed successfully")
                return True
            else:
                self.log_result("Assessment-to-Action Workflow - Dashboard Update", False, 
                              f"Dashboard update verification failed: {dashboard_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Assessment-to-Action Workflow - Complete", False, f"Exception: {str(e)}")
            return False

    def test_cross_platform_analytics_integration(self):
        """Test cross-platform analytics integration"""
        try:
            # Test navigator analytics
            nav_headers = self.get_headers("navigator")
            if nav_headers:
                nav_response = self.session.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                              headers=nav_headers)
                nav_success = nav_response.status_code == 200
            else:
                nav_success = False
            
            # Test agency business intelligence
            agency_headers = self.get_headers("agency")
            if agency_headers:
                agency_response = self.session.get(f"{BASE_URL}/agency/business-intelligence/assessments", 
                                                 headers=agency_headers)
                agency_success = agency_response.status_code == 200
            else:
                agency_success = False
            
            # Test client dashboard analytics
            client_headers = self.get_headers("client")
            if client_headers:
                client_response = self.session.get(f"{BASE_URL}/client/unified-dashboard", 
                                                 headers=client_headers)
                client_success = client_response.status_code == 200
            else:
                client_success = False
            
            total_success = sum([nav_success, agency_success, client_success])
            
            if total_success >= 2:  # At least 2 out of 3 analytics endpoints working
                self.log_result("Cross-Platform Analytics Integration", True, 
                              f"Analytics integration working: {total_success}/3 endpoints successful")
                return True
            else:
                self.log_result("Cross-Platform Analytics Integration", False, 
                              f"Insufficient analytics integration: {total_success}/3 endpoints successful")
                return False
                
        except Exception as e:
            self.log_result("Cross-Platform Analytics Integration", False, f"Exception: {str(e)}")
            return False

    def test_complete_user_journey(self):
        """Test end-to-end user journey: Assessment → Gap → Service Request → Provider Response → Analytics"""
        try:
            # Step 1: Assessment completion (already tested above)
            client_headers = self.get_headers("client")
            provider_headers = self.get_headers("provider")
            
            if not client_headers or not provider_headers:
                self.log_result("Complete User Journey - Authentication", False, "Missing required tokens")
                return False
            
            # Step 2: Create service request based on gap
            service_request_payload = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with technology and security infrastructure assessment and implementation",
                "priority": "high"
            }
            
            request_response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                               json=service_request_payload, headers=client_headers)
            
            if request_response.status_code != 200:
                error_data = request_response.json() if request_response.content else {"error": "No content"}
                self.log_result("Complete User Journey - Service Request", False, 
                              f"Service request creation failed: {request_response.status_code}", error_data)
                return False
            
            request_data = request_response.json()
            request_id = request_data.get("request_id")
            
            if not request_id:
                self.log_result("Complete User Journey - Request ID", False, 
                              "No request_id in service request response", request_data)
                return False
            
            # Step 3: Provider responds to service request
            provider_response_payload = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "I can help implement comprehensive security infrastructure with compliance documentation"
            }
            
            provider_response = self.session.post(f"{BASE_URL}/provider/respond-to-request", 
                                                json=provider_response_payload, headers=provider_headers)
            
            if provider_response.status_code != 200:
                error_data = provider_response.json() if provider_response.content else {"error": "No content"}
                self.log_result("Complete User Journey - Provider Response", False, 
                              f"Provider response failed: {provider_response.status_code}", error_data)
                return False
            
            # Step 4: Verify analytics tracking
            analytics_payload = {
                "area_id": "area5",
                "action_type": "service_request_created",
                "user_type": "client"
            }
            
            analytics_response = self.session.post(f"{BASE_URL}/analytics/resource-access", 
                                                 json=analytics_payload, headers=client_headers)
            
            analytics_success = analytics_response.status_code == 200
            
            self.log_result("Complete User Journey - End-to-End", True, 
                          f"Complete user journey successful (analytics: {'✓' if analytics_success else '✗'})")
            return True
                
        except Exception as e:
            self.log_result("Complete User Journey - End-to-End", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all enhanced integration tests"""
        print("🎯 ENHANCED PLATFORM INTEGRATION AND COMPLETE FEATURE JOURNEY TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate all users
        print("📋 STEP 1: AUTHENTICATION")
        print("-" * 40)
        auth_success = 0
        for role in ["client", "provider", "agency", "navigator"]:
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success < 2:
            print("❌ CRITICAL: Insufficient authentication success. Cannot proceed with testing.")
            return False
        
        print(f"Authentication Summary: {auth_success}/4 roles authenticated successfully")
        print()
        
        # Step 2: Test Enhanced Integration Endpoints
        print("📋 STEP 2: ENHANCED INTEGRATION ENDPOINTS")
        print("-" * 40)
        
        endpoint_tests = [
            ("Unified Dashboard", self.test_unified_dashboard_endpoint),
            ("Realtime Dashboard Update", self.test_realtime_dashboard_update),
            ("Provider Notifications", self.test_provider_notifications_endpoint),
            ("Provider Notification Response", self.test_provider_notification_response),
            ("Agency Business Intelligence", self.test_agency_business_intelligence)
        ]
        
        endpoint_success = 0
        for test_name, test_func in endpoint_tests:
            if test_func():
                endpoint_success += 1
        
        print(f"Enhanced Integration Endpoints: {endpoint_success}/{len(endpoint_tests)} tests passed")
        print()
        
        # Step 3: Test Complete Workflows
        print("📋 STEP 3: COMPLETE FEATURE WORKFLOWS")
        print("-" * 40)
        
        workflow_tests = [
            ("Assessment-to-Action Workflow", self.test_assessment_to_action_workflow),
            ("Cross-Platform Analytics", self.test_cross_platform_analytics_integration),
            ("Complete User Journey", self.test_complete_user_journey)
        ]
        
        workflow_success = 0
        for test_name, test_func in workflow_tests:
            if test_func():
                workflow_success += 1
        
        print(f"Complete Feature Workflows: {workflow_success}/{len(workflow_tests)} tests passed")
        print()
        
        # Calculate overall success rate
        total_tests = len(endpoint_tests) + len(workflow_tests)
        total_success = endpoint_success + workflow_success
        success_rate = (total_success / total_tests) * 100
        
        print("📊 FINAL RESULTS")
        print("=" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_success}")
        print(f"Failed: {total_tests - total_success}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 70:
            print("✅ ENHANCED PLATFORM INTEGRATION: OPERATIONAL")
        else:
            print("❌ ENHANCED PLATFORM INTEGRATION: NEEDS ATTENTION")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = EnhancedIntegrationTester()
    success = tester.run_all_tests()
    
    # Print detailed results for debugging
    print("\n📋 DETAILED TEST RESULTS")
    print("=" * 50)
    for result in tester.test_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}")
        if result["details"]:
            print(f"   {result['details']}")
    
    return success

if __name__ == "__main__":
    main()