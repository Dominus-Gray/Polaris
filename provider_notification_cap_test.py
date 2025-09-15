#!/usr/bin/env python3
"""
Provider Notification Cap Testing Suite
Testing the provider notification cap change as requested in review.

Test Requirements:
1) As client.qa, create a new professional help request via POST /api/service-requests/professional-help 
   (area_id=area5, budget_range="5000-15000", timeline="1-2 months", description="Test cap")
2) Capture providers_notified count; expect <= 5
3) Query GET /api/service-requests/{request_id}/responses/enhanced with client token
4) Confirm response_limit_reached reflects True when >=5 responses exist
5) If fewer available, confirm total_responses == number of provider_responses present and response_limit_reached reflects correctly
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Configuration - Using frontend .env REACT_APP_BACKEND_URL
BACKEND_URL = "http://localhost:8001/api"
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class ProviderNotificationCapTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
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

    def authenticate(self):
        """Authenticate with client QA credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                # Get user info
                me_response = self.session.get(f"{BACKEND_URL}/auth/me")
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.user_id = user_data.get("id")
                    self.log_test(
                        "Client Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_CREDENTIALS['email']}, User ID: {self.user_id}"
                    )
                    return True
                else:
                    self.log_test("Client Authentication", False, f"Failed to get user info: {me_response.status_code}")
                    return False
            else:
                self.log_test("Client Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", False, f"Authentication error: {str(e)}")
            return False

    def create_professional_help_request(self):
        """Create a new professional help request with specified parameters"""
        try:
            request_data = {
                "area_id": "area5",
                "budget_range": "5000-15000", 
                "timeline": "1-2 months",
                "description": "Test cap verification for provider notification limits"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/service-requests/professional-help",
                json=request_data,
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

    def query_enhanced_responses(self):
        """Query GET /api/service-requests/{request_id}/responses/enhanced with client token"""
        if not self.service_request_id:
            self.log_test("Query Enhanced Responses", False, "No service request ID available")
            return False
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/service-requests/{self.service_request_id}/responses/enhanced",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key fields for verification
                response_limit_reached = data.get("response_limit_reached", False)
                total_responses = data.get("total_responses", 0)
                provider_responses = data.get("responses", [])  # Changed from provider_responses to responses
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
        """Run the complete provider notification cap test suite"""
        print("🎯 PROVIDER NOTIFICATION CAP TESTING SUITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {QA_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create professional help request with cap verification
        if not self.create_professional_help_request():
            print("❌ Service request creation failed. Cannot proceed with response tests.")
            return False
        
        # Step 3: Query enhanced responses and verify logic
        if not self.query_enhanced_responses():
            print("❌ Enhanced responses query failed.")
            return False
        
        # Generate summary
        self.generate_test_summary()
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PROVIDER NOTIFICATION CAP TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = ProviderNotificationCapTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()