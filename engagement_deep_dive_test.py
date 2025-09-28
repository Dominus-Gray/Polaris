#!/usr/bin/env python3
"""
Deep Dive Engagement Testing - Additional endpoints and edge cases
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"

# QA Credentials
CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class EngagementDeepDive:
    def __init__(self):
        self.client_token = None
        self.provider_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_users(self):
        """Authenticate both users"""
        print("🔐 AUTHENTICATING USERS...")
        
        # Client auth
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=CLIENT_CREDENTIALS)
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication", True, "Success")
            else:
                self.log_result("Client Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False

        # Provider auth
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=PROVIDER_CREDENTIALS)
            if response.status_code == 200:
                self.provider_token = response.json()["access_token"]
                self.log_result("Provider Authentication", True, "Success")
            else:
                self.log_result("Provider Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Provider Authentication", False, f"Exception: {str(e)}")
            return False

        return True

    def test_service_request_responses(self):
        """Test getting service request responses"""
        print("📋 TESTING SERVICE REQUEST RESPONSES...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # First get client's service requests
            response = requests.get(f"{BASE_URL}/engagements/my-services", headers=headers)
            if response.status_code == 200:
                data = response.json()
                engagements = data.get("engagements", [])
                
                if engagements:
                    # Test getting responses for the first service request
                    first_request = engagements[0]
                    request_id = first_request.get("request_id")
                    
                    if request_id:
                        response = requests.get(f"{BASE_URL}/service-requests/{request_id}/responses", headers=headers)
                        if response.status_code == 200:
                            responses_data = response.json()
                            responses = responses_data.get("responses", [])
                            self.log_result("Service Request Responses", True, 
                                f"Retrieved {len(responses)} responses for request {request_id}")
                            return responses
                        else:
                            self.log_result("Service Request Responses", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    else:
                        self.log_result("Service Request Responses", False, "No request_id found")
                else:
                    self.log_result("Service Request Responses", False, "No engagements found")
            else:
                self.log_result("Service Request Responses", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Service Request Responses", False, f"Exception: {str(e)}")
        
        return []

    def test_provider_respond_to_request(self):
        """Test provider responding to service requests"""
        print("💼 TESTING PROVIDER RESPONSE WORKFLOW...")
        
        try:
            # First create a new service request as client
            headers = {"Authorization": f"Bearer {self.client_token}"}
            request_data = {
                "area_id": "area1",  # Business Formation
                "budget_range": "$500-$1,500",
                "description": "Deep dive test - Need help with business registration and licensing",
                "urgency": "low",
                "timeline": "1-2 weeks"
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                self.log_result("New Service Request Creation", True, f"Created request: {request_id}")
                
                # Now respond as provider
                provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
                response_data = {
                    "request_id": request_id,
                    "proposed_fee": 1200.00,
                    "estimated_timeline": "10 business days",
                    "proposal_note": "Comprehensive business formation package including entity registration, EIN application, business license research, and compliance checklist. Includes 2 weeks of follow-up support."
                }
                
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                       json=response_data, headers=provider_headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_id = response_data.get("response_id")
                    self.log_result("Provider Response to New Request", True, 
                        f"Created response: {response_id}")
                    return request_id, response_id
                else:
                    self.log_result("Provider Response to New Request", False, 
                        f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_result("New Service Request Creation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Provider Response Workflow", False, f"Exception: {str(e)}")
        
        return None, None

    def test_engagement_rating_system(self, engagement_id):
        """Test engagement rating system"""
        print("⭐ TESTING ENGAGEMENT RATING SYSTEM...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            rating_data = {
                "rating": 5,
                "feedback": "Excellent service! Provider was professional, timely, and delivered exactly what was promised. Would definitely work with them again.",
                "quality_score": 5,
                "communication_score": 5,
                "timeliness_score": 4
            }
            
            response = requests.post(f"{BASE_URL}/engagements/{engagement_id}/rating", 
                                   json=rating_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                rating_id = data.get("rating_id")
                self.log_result("Engagement Rating", True, f"Created rating: {rating_id}")
                return rating_id
            else:
                self.log_result("Engagement Rating", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Engagement Rating", False, f"Exception: {str(e)}")
        
        return None

    def test_engagement_edge_cases(self):
        """Test engagement system edge cases"""
        print("🔍 TESTING ENGAGEMENT EDGE CASES...")
        
        # Test accessing non-existent engagement
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            fake_engagement_id = "non-existent-engagement-id"
            
            response = requests.get(f"{BASE_URL}/engagements/{fake_engagement_id}/tracking", headers=headers)
            
            if response.status_code == 404:
                self.log_result("Non-existent Engagement Access", True, "Correctly returned 404")
            else:
                self.log_result("Non-existent Engagement Access", False, 
                    f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Non-existent Engagement Access", False, f"Exception: {str(e)}")

        # Test creating engagement with invalid data
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            invalid_data = {
                "request_id": "invalid-request-id",
                "response_id": "invalid-response-id", 
                "agreed_fee": 1000.00
            }
            
            response = requests.post(f"{BASE_URL}/engagements/create", 
                                   json=invalid_data, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Invalid Engagement Creation", True, "Correctly rejected invalid data")
            else:
                self.log_result("Invalid Engagement Creation", False, 
                    f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Invalid Engagement Creation", False, f"Exception: {str(e)}")

    def analyze_engagement_data_flow(self):
        """Analyze the complete data flow in engagement system"""
        print("📊 ANALYZING ENGAGEMENT DATA FLOW...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Get client's engagements
            response = requests.get(f"{BASE_URL}/engagements/my-services", headers=headers)
            if response.status_code == 200:
                client_data = response.json()
                client_engagements = client_data.get("engagements", [])
                
                # Get provider's engagements
                provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
                response = requests.get(f"{BASE_URL}/engagements/my-services", headers=provider_headers)
                if response.status_code == 200:
                    provider_data = response.json()
                    provider_engagements = provider_data.get("engagements", [])
                    
                    analysis = {
                        "client_view": {
                            "total_engagements": len(client_engagements),
                            "data_structure": list(client_engagements[0].keys()) if client_engagements else [],
                            "statuses": list(set(e.get("status") for e in client_engagements if e.get("status")))
                        },
                        "provider_view": {
                            "total_notifications": len(provider_engagements),
                            "data_structure": list(provider_engagements[0].keys()) if provider_engagements else [],
                            "response_status": [e.get("has_responded") for e in provider_engagements]
                        }
                    }
                    
                    self.log_result("Engagement Data Flow Analysis", True, 
                        f"Client: {analysis['client_view']['total_engagements']} engagements, Provider: {analysis['provider_view']['total_notifications']} notifications")
                    
                    return analysis
                else:
                    self.log_result("Engagement Data Flow Analysis", False, "Failed to get provider data")
            else:
                self.log_result("Engagement Data Flow Analysis", False, "Failed to get client data")
                
        except Exception as e:
            self.log_result("Engagement Data Flow Analysis", False, f"Exception: {str(e)}")
        
        return None

    def run_deep_dive_tests(self):
        """Run all deep dive tests"""
        print("🚀 STARTING ENGAGEMENT DEEP DIVE TESTS")
        print("=" * 60)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ Authentication failed")
            return
        
        # Test service request responses
        self.test_service_request_responses()
        
        # Test provider response workflow
        request_id, response_id = self.test_provider_respond_to_request()
        
        # Create engagement if we have valid request and response
        engagement_id = None
        if request_id and response_id:
            try:
                headers = {"Authorization": f"Bearer {self.client_token}"}
                engagement_data = {
                    "request_id": request_id,
                    "response_id": response_id,
                    "agreed_fee": 1200.00
                }
                
                response = requests.post(f"{BASE_URL}/engagements/create", 
                                       json=engagement_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    engagement_id = data.get("engagement_id")
                    self.log_result("Deep Dive Engagement Creation", True, 
                        f"Created engagement: {engagement_id}")
                    
                    # Test rating system (but first need to complete the engagement)
                    # Update status to completed first
                    update_data = {"status": "completed", "notes": "Deep dive test completed"}
                    provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
                    requests.post(f"{BASE_URL}/engagements/{engagement_id}/update", 
                                json=update_data, headers=provider_headers)
                    
                    # Now test rating
                    self.test_engagement_rating_system(engagement_id)
                    
            except Exception as e:
                self.log_result("Deep Dive Engagement Creation", False, f"Exception: {str(e)}")
        
        # Test edge cases
        self.test_engagement_edge_cases()
        
        # Analyze data flow
        self.analyze_engagement_data_flow()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 DEEP DIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        print("🔍 DETAILED FINDINGS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    → {result['details']}")
        
        print("\n🎉 DEEP DIVE COMPLETE!")

if __name__ == "__main__":
    deep_dive = EngagementDeepDive()
    deep_dive.run_deep_dive_tests()