#!/usr/bin/env python3
"""
M2 Frontend Wiring Regression Test
Testing Agent: testing
Test Date: January 2025
Test Scope: Backend quick regression check after M2 frontend wiring

Specific tests requested:
1) Create service request via POST /api/service-requests/professional-help with client.qa; 
   expect providers_notified <= 5 and request_id present
2) GET /api/service-requests/{request_id}/responses/enhanced; 
   verify structure and response_limit_reached when >=5.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://localhost:8001/api"
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class M2RegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.request_id = None
        
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
        """Authenticate with QA credentials"""
        try:
            print("🔐 AUTHENTICATING WITH CLIENT QA CREDENTIALS...")
            print(f"Email: {QA_CREDENTIALS['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                # Get user info
                me_response = self.session.get(f"{BACKEND_URL}/auth/me")
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.user_id = user_data.get("id")
                    self.log_test(
                        "Client QA Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_CREDENTIALS['email']} (Role: {user_data.get('role')})"
                    )
                    return True
                else:
                    self.log_test(
                        "Client QA Authentication - User Info", 
                        False, 
                        "Failed to get user info after login",
                        me_response.text
                    )
                    return False
            else:
                self.log_test(
                    "Client QA Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Client QA Authentication", False, f"Exception during auth: {str(e)}")
            return False

    def test_create_service_request(self):
        """Test 1: Create service request via POST /api/service-requests/professional-help"""
        try:
            print("📝 TESTING SERVICE REQUEST CREATION...")
            
            # Service request data
            request_data = {
                "area_id": "area5",  # Technology & Security Infrastructure
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "M2 regression test - Need professional help with technology infrastructure assessment and security compliance review for government contracting readiness.",
                "priority": "medium"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/service-requests/professional-help",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields are present
                required_fields = ["request_id", "providers_notified"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Service Request Creation - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Extract request_id for next test
                self.request_id = data.get("request_id")
                providers_notified = data.get("providers_notified", 0)
                
                # Verify providers_notified <= 5
                if providers_notified > 5:
                    self.log_test(
                        "Service Request Creation - Provider Notification Cap",
                        False,
                        f"Too many providers notified: {providers_notified} (expected <= 5)",
                        data
                    )
                    return False
                
                # Verify request_id is present and valid
                if not self.request_id or len(self.request_id) < 10:
                    self.log_test(
                        "Service Request Creation - Request ID",
                        False,
                        f"Invalid request_id: {self.request_id}",
                        data
                    )
                    return False
                
                self.log_test(
                    "Service Request Creation",
                    True,
                    f"Service request created successfully. Request ID: {self.request_id}, Providers notified: {providers_notified} (≤5 ✓)",
                    {
                        "request_id": self.request_id,
                        "providers_notified": providers_notified,
                        "area_id": data.get("area_id"),
                        "status": data.get("status")
                    }
                )
                return True
                
            else:
                self.log_test(
                    "Service Request Creation",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Service Request Creation",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_get_enhanced_responses(self):
        """Test 2: GET /api/service-requests/{request_id}/responses/enhanced"""
        try:
            print("📊 TESTING ENHANCED RESPONSES ENDPOINT...")
            
            if not self.request_id:
                self.log_test(
                    "Enhanced Responses - Prerequisites",
                    False,
                    "No request_id available from previous test"
                )
                return False
            
            response = self.session.get(
                f"{BACKEND_URL}/service-requests/{self.request_id}/responses/enhanced"
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["request_id", "responses", "response_limit_reached", "total_responses"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Enhanced Responses - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify request_id matches
                if data.get("request_id") != self.request_id:
                    self.log_test(
                        "Enhanced Responses - Request ID Match",
                        False,
                        f"Request ID mismatch: expected {self.request_id}, got {data.get('request_id')}",
                        data
                    )
                    return False
                
                # Verify responses is a list
                responses = data.get("responses", [])
                if not isinstance(responses, list):
                    self.log_test(
                        "Enhanced Responses - Responses Format",
                        False,
                        f"Responses must be a list, got: {type(responses)}",
                        data
                    )
                    return False
                
                # Verify response_limit_reached logic
                total_responses = data.get("total_responses", 0)
                response_limit_reached = data.get("response_limit_reached", False)
                
                # Logic: response_limit_reached should be True when total_responses >= 5
                expected_limit_reached = total_responses >= 5
                if response_limit_reached != expected_limit_reached:
                    self.log_test(
                        "Enhanced Responses - Limit Logic",
                        False,
                        f"Response limit logic incorrect: total_responses={total_responses}, response_limit_reached={response_limit_reached}, expected={expected_limit_reached}",
                        data
                    )
                    return False
                
                # Verify response structure if responses exist
                if responses:
                    first_response = responses[0]
                    expected_response_fields = ["response_id", "provider_id", "proposed_fee", "estimated_timeline", "proposal_note"]
                    missing_response_fields = [field for field in expected_response_fields if field not in first_response]
                    
                    if missing_response_fields:
                        self.log_test(
                            "Enhanced Responses - Response Item Structure",
                            False,
                            f"Missing response fields: {missing_response_fields}",
                            data
                        )
                        return False
                
                self.log_test(
                    "Enhanced Responses",
                    True,
                    f"Enhanced responses retrieved successfully. Total responses: {total_responses}, Response limit reached: {response_limit_reached}, Logic correct: ✓",
                    {
                        "request_id": data.get("request_id"),
                        "total_responses": total_responses,
                        "response_limit_reached": response_limit_reached,
                        "responses_count": len(responses),
                        "limit_logic_correct": response_limit_reached == expected_limit_reached
                    }
                )
                return True
                
            else:
                self.log_test(
                    "Enhanced Responses",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Enhanced Responses",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def run_regression_tests(self):
        """Run M2 regression tests"""
        print("🎯 M2 FRONTEND WIRING REGRESSION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_CREDENTIALS['email']}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print("=" * 60)
        print("🧪 RUNNING M2 REGRESSION TESTS")
        print("=" * 60)
        print()
        
        # Step 2: Test service request creation
        test1_success = self.test_create_service_request()
        
        # Step 3: Test enhanced responses (depends on step 2)
        test2_success = self.test_get_enhanced_responses()
        
        # Generate summary
        self.generate_summary(test1_success, test2_success)
        
        return test1_success and test2_success

    def generate_summary(self, test1_success, test2_success):
        """Generate test summary"""
        print("=" * 60)
        print("📊 M2 REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 2
        passed_tests = sum([test1_success, test2_success])
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("DETAILED TEST RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("=" * 60)
        
        if success_rate == 100:
            print("✅ M2 REGRESSION: ALL TESTS PASSED")
            print("Service request endpoints working correctly after M2 frontend wiring.")
        elif success_rate >= 50:
            print("⚠️ M2 REGRESSION: PARTIAL SUCCESS")
            print("Some issues detected that need attention.")
        else:
            print("❌ M2 REGRESSION: CRITICAL ISSUES")
            print("Major problems detected with service request endpoints.")
        
        print("=" * 60)
        
        # Evidence summary
        print("CONCISE EVIDENCE:")
        print("-" * 20)
        if self.request_id:
            print(f"✓ Service request created: {self.request_id}")
        
        for result in self.test_results:
            if result["success"] and "response_data" in result:
                data = result["response_data"]
                if "providers_notified" in data:
                    print(f"✓ Providers notified: {data['providers_notified']} (≤5)")
                if "response_limit_reached" in data:
                    print(f"✓ Response limit logic: {data['response_limit_reached']} (total: {data.get('total_responses', 0)})")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = M2RegressionTester()
    
    try:
        success = tester.run_regression_tests()
        
        if success:
            print("\n🎉 M2 REGRESSION TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n❌ M2 REGRESSION TESTS FAILED!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()