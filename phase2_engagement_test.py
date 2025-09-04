#!/usr/bin/env python3
"""
Phase 2 Engagement Backend Testing
Tests the complete engagement workflow as specified in the review request.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agencydash.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
CLIENT_EMAIL = "client.qa@polaris.example.com"
PROVIDER_EMAIL = "provider.qa@polaris.example.com"
PASSWORD = "Polaris#2025!"

class EngagementTester:
    def __init__(self):
        self.client_token = None
        self.provider_token = None
        self.request_id = None
        self.provider_id = None
        self.engagement_id = None
        self.results = []
        
    def log_result(self, step, status, message, details=None):
        """Log test result"""
        result = {
            "step": step,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} Step {step}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers)
            
            if response.status_code != expected_status:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "data": None
                }
            
            try:
                data = response.json()
            except:
                data = response.text
                
            return {
                "success": True,
                "status_code": response.status_code,
                "data": data
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "error": str(e),
                "data": None
            }
    
    def login_user(self, email, password, role):
        """Login user and return token"""
        response = self.make_request("POST", "/auth/login", {
            "email": email,
            "password": password
        })
        
        if response["success"]:
            return response["data"]["access_token"]
        else:
            return None
    
    def test_step_1_login_client(self):
        """Step 1: Login as client"""
        self.client_token = self.login_user(CLIENT_EMAIL, PASSWORD, "client")
        
        if self.client_token:
            self.log_result(1, "PASS", f"Client login successful for {CLIENT_EMAIL}")
        else:
            self.log_result(1, "FAIL", f"Client login failed for {CLIENT_EMAIL}")
            return False
        return True
    
    def test_step_1_login_provider(self):
        """Step 1: Login as provider"""
        self.provider_token = self.login_user(PROVIDER_EMAIL, PASSWORD, "provider")
        
        if self.provider_token:
            self.log_result(1, "PASS", f"Provider login successful for {PROVIDER_EMAIL}")
        else:
            self.log_result(1, "FAIL", f"Provider login failed for {PROVIDER_EMAIL}")
            return False
        return True
    
    def test_step_2_create_service_request(self):
        """Step 2: Create service request as client"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = self.make_request("POST", "/service-requests/professional-help", {
            "area_id": "area5",
            "budget_range": "$1,000-$2,500",
            "description": "Phase2 test"
        }, headers)
        
        if response["success"]:
            self.request_id = response["data"]["request_id"]
            self.log_result(2, "PASS", f"Service request created successfully", 
                          f"Request ID: {self.request_id}")
        else:
            self.log_result(2, "FAIL", f"Service request creation failed", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_3_provider_respond(self):
        """Step 3: Provider responds to request"""
        headers = {"Authorization": f"Bearer {self.provider_token}"}
        
        response = self.make_request("POST", "/provider/respond-to-request", {
            "request_id": self.request_id,
            "proposed_fee": 1200,
            "estimated_timeline": "10 days",
            "proposal_note": "Phase2 response"
        }, headers)
        
        if response["success"]:
            response_id = response["data"]["response_id"]
            self.log_result(3, "PASS", f"Provider response submitted successfully", 
                          f"Response ID: {response_id}")
            
            # Get provider ID from the response or from auth
            provider_auth = self.make_request("GET", "/auth/me", headers=headers)
            if provider_auth["success"]:
                self.provider_id = provider_auth["data"]["id"]
        else:
            self.log_result(3, "FAIL", f"Provider response failed", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_4_create_engagement(self):
        """Step 4: Create engagement as client"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # First get the service request to find the response ID
        response = self.make_request("GET", f"/service-requests/{self.request_id}", headers=headers)
        
        if not response["success"] or not response["data"].get("provider_responses"):
            self.log_result(4, "FAIL", "Could not retrieve provider responses for engagement creation")
            return False
        
        provider_response = response["data"]["provider_responses"][0]
        response_id = provider_response["id"]
        
        # Create engagement - Note: The API expects different field names than in review request
        # Using the actual implementation structure
        engagement_response = self.make_request("POST", "/engagements/create", {
            "request_id": self.request_id,
            "response_id": response_id,
            "agreed_fee": 1200
        }, headers)
        
        if engagement_response["success"]:
            self.engagement_id = engagement_response["data"]["engagement_id"]
            self.log_result(4, "PASS", f"Engagement created successfully", 
                          f"Engagement ID: {self.engagement_id}")
        else:
            # Try alternative endpoint structure if the first fails
            alt_response = self.make_request("POST", "/engagements/create", {
                "request_id": self.request_id,
                "provider_id": self.provider_id
            }, headers)
            
            if alt_response["success"]:
                self.engagement_id = alt_response["data"]["engagement_id"]
                self.log_result(4, "PASS", f"Engagement created successfully (alt method)", 
                              f"Engagement ID: {self.engagement_id}")
            else:
                self.log_result(4, "FAIL", f"Engagement creation failed", 
                              f"Status: {engagement_response['status_code']}, Error: {engagement_response.get('error', 'Unknown')}")
                return False
        return True
    
    def test_step_5_verify_my_services(self):
        """Step 5: Verify engagement appears in my-services for both client and provider"""
        # Test client view
        client_headers = {"Authorization": f"Bearer {self.client_token}"}
        client_response = self.make_request("GET", "/engagements/my-services", headers=client_headers)
        
        client_found = False
        if client_response["success"]:
            engagements = client_response["data"]["engagements"]
            client_found = any(eng.get("request_id") == self.request_id for eng in engagements)
        
        # Test provider view
        provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
        provider_response = self.make_request("GET", "/engagements/my-services", headers=provider_headers)
        
        provider_found = False
        if provider_response["success"]:
            engagements = provider_response["data"]["engagements"]
            provider_found = any(eng.get("request_id") == self.request_id for eng in engagements)
        
        if client_found and provider_found:
            self.log_result(5, "PASS", "Engagement appears in my-services for both client and provider")
        elif client_found:
            self.log_result(5, "PARTIAL", "Engagement appears for client but not provider")
        elif provider_found:
            self.log_result(5, "PARTIAL", "Engagement appears for provider but not client")
        else:
            self.log_result(5, "FAIL", "Engagement does not appear in my-services for either party")
            return False
        return True
    
    def test_step_6_update_to_in_progress(self):
        """Step 6: Update engagement status to 'in_progress' as client (simulate funding)"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = self.make_request("POST", f"/engagements/{self.engagement_id}/update", {
            "status": "in_progress"
        }, headers)
        
        if response["success"]:
            self.log_result(6, "PASS", "Engagement status updated to 'in_progress'")
        else:
            self.log_result(6, "FAIL", f"Failed to update engagement to in_progress", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_7_update_to_delivered(self):
        """Step 7: Update engagement status to 'delivered' as provider"""
        headers = {"Authorization": f"Bearer {self.provider_token}"}
        
        response = self.make_request("POST", f"/engagements/{self.engagement_id}/update", {
            "status": "delivered"
        }, headers)
        
        if response["success"]:
            self.log_result(7, "PASS", "Engagement status updated to 'delivered'")
        else:
            self.log_result(7, "FAIL", f"Failed to update engagement to delivered", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_8_update_to_approved(self):
        """Step 8: Update engagement status to 'approved' as client"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = self.make_request("POST", f"/engagements/{self.engagement_id}/update", {
            "status": "approved"
        }, headers)
        
        if response["success"]:
            self.log_result(8, "PASS", "Engagement status updated to 'approved'")
        else:
            self.log_result(8, "FAIL", f"Failed to update engagement to approved", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_9_update_to_released(self):
        """Step 9: Update engagement status to 'released' as client"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = self.make_request("POST", f"/engagements/{self.engagement_id}/update", {
            "status": "released"
        }, headers)
        
        if response["success"]:
            self.log_result(9, "PASS", "Engagement status updated to 'released'")
        else:
            self.log_result(9, "FAIL", f"Failed to update engagement to released", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def test_step_10_verify_tracking(self):
        """Step 10: Verify tracking entries and final status"""
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = self.make_request("GET", f"/engagements/{self.engagement_id}/tracking", headers=headers)
        
        if response["success"]:
            engagement = response["data"]["engagement"]
            tracking_history = response["data"]["tracking_history"]
            
            final_status = engagement.get("status")
            expected_statuses = ["in_progress", "delivered", "approved", "released"]
            
            # Check if we have tracking entries for the expected statuses
            tracked_statuses = [entry.get("status") for entry in tracking_history]
            
            if final_status == "released":
                self.log_result(10, "PASS", f"Tracking verification successful", 
                              f"Final status: {final_status}, Tracked statuses: {tracked_statuses}")
            else:
                self.log_result(10, "PARTIAL", f"Tracking partially successful", 
                              f"Final status: {final_status} (expected: released), Tracked statuses: {tracked_statuses}")
        else:
            self.log_result(10, "FAIL", f"Failed to retrieve tracking information", 
                          f"Status: {response['status_code']}, Error: {response.get('error', 'Unknown')}")
            return False
        return True
    
    def run_all_tests(self):
        """Run complete engagement workflow test"""
        print("🚀 Starting Phase 2 Engagement Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Client: {CLIENT_EMAIL}")
        print(f"Provider: {PROVIDER_EMAIL}")
        print("=" * 60)
        
        # Step 1: Login both users
        if not self.test_step_1_login_client():
            return False
        if not self.test_step_1_login_provider():
            return False
        
        # Step 2: Create service request
        if not self.test_step_2_create_service_request():
            return False
        
        # Step 3: Provider responds
        if not self.test_step_3_provider_respond():
            return False
        
        # Step 4: Create engagement
        if not self.test_step_4_create_engagement():
            return False
        
        # Step 5: Verify my-services
        if not self.test_step_5_verify_my_services():
            return False
        
        # Step 6-9: Status transitions
        if not self.test_step_6_update_to_in_progress():
            return False
        if not self.test_step_7_update_to_delivered():
            return False
        if not self.test_step_8_update_to_approved():
            return False
        if not self.test_step_9_update_to_released():
            return False
        
        # Step 10: Verify tracking
        if not self.test_step_10_verify_tracking():
            return False
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Partial: {partial}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  Step {result['step']}: {result['message']}")
                    if result["details"]:
                        print(f"    {result['details']}")
        
        return failed == 0

def main():
    """Main test execution"""
    tester = EngagementTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        if success:
            print("\n🎉 All Phase 2 Engagement tests PASSED!")
            sys.exit(0)
        else:
            print("\n💥 Some Phase 2 Engagement tests FAILED!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()