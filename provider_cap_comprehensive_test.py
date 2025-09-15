#!/usr/bin/env python3
"""
Comprehensive Provider Notification Cap Testing Suite
Testing the provider notification cap change with multiple scenarios including provider responses.
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Configuration - Using frontend .env REACT_APP_BACKEND_URL
BACKEND_URL = "http://localhost:8001/api"
QA_CREDENTIALS = {
    "client": {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "provider": {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!"
    }
}

class ComprehensiveProviderCapTester:
    def __init__(self):
        self.session = requests.Session()
        self.client_token = None
        self.provider_token = None
        self.client_id = None
        self.provider_id = None
        self.test_results = []
        self.service_request_id = None
        
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

    def authenticate_client(self):
        """Authenticate with client QA credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS["client"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get("access_token")
                
                # Get user info
                me_response = requests.get(
                    f"{BACKEND_URL}/auth/me",
                    headers={"Authorization": f"Bearer {self.client_token}"}
                )
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.client_id = user_data.get("id")
                    self.log_test(
                        "Client Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_CREDENTIALS['client']['email']}, User ID: {self.client_id}"
                    )
                    return True
                else:
                    self.log_test("Client Authentication", False, f"Failed to get client user info: {me_response.status_code}")
                    return False
            else:
                self.log_test("Client Authentication", False, f"Client login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", False, f"Client authentication error: {str(e)}")
            return False

    def authenticate_provider(self):
        """Authenticate with provider QA credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS["provider"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.provider_token = data.get("access_token")
                
                # Get user info
                me_response = requests.get(
                    f"{BACKEND_URL}/auth/me",
                    headers={"Authorization": f"Bearer {self.provider_token}"}
                )
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.provider_id = user_data.get("id")
                    self.log_test(
                        "Provider Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_CREDENTIALS['provider']['email']}, User ID: {self.provider_id}"
                    )
                    return True
                else:
                    self.log_test("Provider Authentication", False, f"Failed to get provider user info: {me_response.status_code}")
                    return False
            else:
                self.log_test("Provider Authentication", False, f"Provider login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Provider Authentication", False, f"Provider authentication error: {str(e)}")
            return False

    def create_professional_help_request(self):
        """Create a new professional help request with specified parameters"""
        try:
            request_data = {
                "area_id": "area5",
                "budget_range": "5000-15000", 
                "timeline": "1-2 months",
                "description": "Test cap verification for provider notification limits - comprehensive testing"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/service-requests/professional-help",
                json=request_data,
                headers={"Authorization": f"Bearer {self.client_token}"},
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.service_request_id = data.get("id") or data.get("request_id")
                providers_notified = data.get("providers_notified", 0)
                
                # Check if providers_notified <= 5
                cap_respected = providers_notified <= 5
                
                self.log_test(
                    "Create Professional Help Request",
                    True,
                    f"Request created successfully. Request ID: {self.service_request_id}, Providers notified: {providers_notified}, Cap respected (<=5): {cap_respected}",
                    {"request_id": self.service_request_id, "providers_notified": providers_notified, "cap_respected": cap_respected}
                )
                
                # Verify the cap constraint
                if not cap_respected:
                    self.log_test(
                        "Provider Notification Cap Verification",
                        False,
                        f"Provider notification cap violated: {providers_notified} > 5"
                    )
                else:
                    self.log_test(
                        "Provider Notification Cap Verification", 
                        True,
                        f"Provider notification cap respected: {providers_notified} <= 5"
                    )
                
                return True
            else:
                self.log_test(
                    "Create Professional Help Request", 
                    False, 
                    f"Request creation failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Create Professional Help Request", False, f"Request creation error: {str(e)}")
            return False

    def submit_provider_response(self):
        """Submit a provider response to the service request"""
        if not self.service_request_id:
            self.log_test("Submit Provider Response", False, "No service request ID available")
            return False
            
        try:
            response_data = {
                "request_id": self.service_request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "6 weeks",
                "proposal_note": "I can help with your technology and security infrastructure needs. I have extensive experience in this area and can deliver within your timeline."
            }
            
            response = requests.post(
                f"{BACKEND_URL}/provider/respond-to-request",
                json=response_data,
                headers={"Authorization": f"Bearer {self.provider_token}"},
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_test(
                    "Submit Provider Response",
                    True,
                    f"Provider response submitted successfully. Response ID: {data.get('id', 'N/A')}"
                )
                return True
            else:
                self.log_test(
                    "Submit Provider Response",
                    False,
                    f"Provider response submission failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Submit Provider Response", False, f"Provider response error: {str(e)}")
            return False

    def query_enhanced_responses(self):
        """Query GET /api/service-requests/{request_id}/responses/enhanced with client token"""
        if not self.service_request_id:
            self.log_test("Query Enhanced Responses", False, "No service request ID available")
            return False
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/service-requests/{self.service_request_id}/responses/enhanced",
                headers={"Authorization": f"Bearer {self.client_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key fields for verification
                response_limit_reached = data.get("response_limit_reached", False)
                total_responses = data.get("total_responses", 0)
                provider_responses = data.get("provider_responses", [])
                actual_response_count = len(provider_responses)
                
                self.log_test(
                    "Query Enhanced Responses",
                    True,
                    f"Enhanced responses retrieved successfully. Total responses: {total_responses}, Actual response count: {actual_response_count}, Response limit reached: {response_limit_reached}",
                    {
                        "total_responses": total_responses,
                        "actual_response_count": actual_response_count,
                        "response_limit_reached": response_limit_reached,
                        "provider_responses_sample": provider_responses[:2] if provider_responses else []
                    }
                )
                
                # Verify response_limit_reached logic
                self.verify_response_limit_logic(total_responses, actual_response_count, response_limit_reached)
                
                return True
            else:
                self.log_test(
                    "Query Enhanced Responses",
                    False,
                    f"Enhanced responses query failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Query Enhanced Responses", False, f"Enhanced responses query error: {str(e)}")
            return False

    def verify_response_limit_logic(self, total_responses, actual_response_count, response_limit_reached):
        """Verify the response limit logic is working correctly"""
        
        # Test case 1: If >= 5 responses exist, response_limit_reached should be True
        if actual_response_count >= 5:
            if response_limit_reached:
                self.log_test(
                    "Response Limit Logic - High Response Count",
                    True,
                    f"Correct: response_limit_reached=True when {actual_response_count} responses exist (>=5)"
                )
            else:
                self.log_test(
                    "Response Limit Logic - High Response Count",
                    False,
                    f"Incorrect: response_limit_reached=False when {actual_response_count} responses exist (>=5)"
                )
        
        # Test case 2: If fewer than 5 responses, verify total_responses == actual count and response_limit_reached reflects correctly
        else:
            total_matches_actual = (total_responses == actual_response_count)
            limit_logic_correct = not response_limit_reached  # Should be False when < 5 responses
            
            if total_matches_actual and limit_logic_correct:
                self.log_test(
                    "Response Limit Logic - Low Response Count",
                    True,
                    f"Correct: total_responses ({total_responses}) == actual count ({actual_response_count}) and response_limit_reached=False when <5 responses"
                )
            else:
                issues = []
                if not total_matches_actual:
                    issues.append(f"total_responses ({total_responses}) != actual count ({actual_response_count})")
                if not limit_logic_correct:
                    issues.append(f"response_limit_reached should be False when <5 responses, got {response_limit_reached}")
                
                self.log_test(
                    "Response Limit Logic - Low Response Count",
                    False,
                    f"Issues found: {'; '.join(issues)}"
                )

    def run_comprehensive_test(self):
        """Run the complete comprehensive provider notification cap test suite"""
        print("🎯 COMPREHENSIVE PROVIDER NOTIFICATION CAP TESTING SUITE")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Client User: {QA_CREDENTIALS['client']['email']}")
        print(f"Provider User: {QA_CREDENTIALS['provider']['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate both users
        if not self.authenticate_client():
            print("❌ Client authentication failed. Cannot proceed with tests.")
            return False
            
        if not self.authenticate_provider():
            print("❌ Provider authentication failed. Cannot proceed with provider response tests.")
            # Continue with client-only tests
        
        # Step 2: Create professional help request with cap verification
        if not self.create_professional_help_request():
            print("❌ Service request creation failed. Cannot proceed with response tests.")
            return False
        
        # Step 3: Submit provider response (if provider authenticated)
        if self.provider_token:
            self.submit_provider_response()
        
        # Step 4: Query enhanced responses and verify logic
        if not self.query_enhanced_responses():
            print("❌ Enhanced responses query failed.")
            return False
        
        # Generate summary
        self.generate_test_summary()
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 COMPREHENSIVE PROVIDER NOTIFICATION CAP TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Show key evidence
        print("📋 KEY EVIDENCE:")
        for result in self.test_results:
            if result["success"] and result.get("response_data"):
                if "providers_notified" in result["response_data"]:
                    print(f"   • Providers Notified: {result['response_data']['providers_notified']}")
                if "cap_respected" in result["response_data"]:
                    print(f"   • Cap Respected (<=5): {result['response_data']['cap_respected']}")
                if "total_responses" in result["response_data"]:
                    print(f"   • Total Responses: {result['response_data']['total_responses']}")
                if "response_limit_reached" in result["response_data"]:
                    print(f"   • Response Limit Reached: {result['response_data']['response_limit_reached']}")
        
        print()
        
        # Overall assessment
        if success_rate >= 100:
            print("✅ PROVIDER NOTIFICATION CAP SYSTEM: FULLY OPERATIONAL")
        elif success_rate >= 75:
            print("⚠️ PROVIDER NOTIFICATION CAP SYSTEM: MOSTLY OPERATIONAL WITH MINOR ISSUES")
        else:
            print("❌ PROVIDER NOTIFICATION CAP SYSTEM: CRITICAL ISSUES IDENTIFIED")
        
        print("=" * 70)

def main():
    """Main test execution"""
    tester = ComprehensiveProviderCapTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()