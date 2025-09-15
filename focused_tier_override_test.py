#!/usr/bin/env python3
"""
Focused Backend Test - QA Tier Override Validation
Testing the two previously failing tests after QA tier override change
"""

import requests
import json
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "http://127.0.0.1:8001"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

class TierOverrideTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.results = []
        
    def log_result(self, test_name, success, details, response_snippet=None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "status": "PASS" if success else "FAIL", 
            "details": details,
            "response_snippet": response_snippet,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
        print(f"   Details: {details}")
        if response_snippet:
            print(f"   Response: {response_snippet}")
        print()
        
    def authenticate(self):
        """Authenticate with QA credentials"""
        try:
            login_data = {
                "email": QA_EMAIL,
                "password": QA_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_result(
                        "QA Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_EMAIL}",
                        f"Token length: {len(self.token)} chars"
                    )
                    return True
                else:
                    self.log_result("QA Authentication", False, "No access token in response", str(data))
                    return False
            else:
                self.log_result(
                    "QA Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result("QA Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_tier_session_creation(self):
        """Test 1: POST /api/assessment/tier-session with area_id=area5, tier_level=3"""
        try:
            # Using form data as specified in the request
            form_data = {
                "area_id": "area5",
                "tier_level": "3"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/assessment/tier-session",
                data=form_data,  # Using form data instead of JSON
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if questions are returned
                questions = data.get("questions", [])
                session_id = data.get("session_id")
                
                if questions and session_id:
                    self.log_result(
                        "Tier Session Creation (area5, tier3)",
                        True,
                        f"Session created successfully with {len(questions)} questions",
                        f"Session ID: {session_id}, Questions: {len(questions)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Tier Session Creation (area5, tier3)",
                        False,
                        "Response missing questions or session_id",
                        str(data)[:300]
                    )
                    return False
            else:
                self.log_result(
                    "Tier Session Creation (area5, tier3)",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text[:300]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Tier Session Creation (area5, tier3)",
                False,
                f"Request error: {str(e)}"
            )
            return False
    
    def test_ai_assistance(self):
        """Test 2: POST /api/knowledge-base/ai-assistance with business licensing question"""
        try:
            request_data = {
                "question": "How do I get started with business licensing?",
                "area_id": "area1"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/knowledge-base/ai-assistance",
                json=request_data,
                timeout=30  # AI requests may take longer
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is returned and under 200 words
                ai_response = data.get("response", "")
                
                if ai_response:
                    word_count = len(ai_response.split())
                    
                    if word_count < 200:
                        self.log_result(
                            "AI Assistance (business licensing)",
                            True,
                            f"AI response received with {word_count} words (under 200 limit)",
                            f"Response preview: {ai_response[:150]}..."
                        )
                        return True
                    else:
                        self.log_result(
                            "AI Assistance (business licensing)",
                            False,
                            f"AI response too long: {word_count} words (over 200 limit)",
                            f"Response preview: {ai_response[:150]}..."
                        )
                        return False
                else:
                    self.log_result(
                        "AI Assistance (business licensing)",
                        False,
                        "No AI response in API response",
                        str(data)[:300]
                    )
                    return False
            else:
                self.log_result(
                    "AI Assistance (business licensing)",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text[:300]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "AI Assistance (business licensing)",
                False,
                f"Request error: {str(e)}"
            )
            return False
    
    def run_tests(self):
        """Run all focused tests"""
        print("🎯 FOCUSED TIER OVERRIDE TESTING - QA VALIDATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Run the two specific tests
        test1_success = self.test_tier_session_creation()
        test2_success = self.test_ai_assistance()
        
        # Generate mini report
        self.generate_mini_report(test1_success, test2_success)
        
        return test1_success and test2_success
    
    def generate_mini_report(self, test1_success, test2_success):
        """Generate mini report as requested"""
        print("📋 MINI REPORT - QA TIER OVERRIDE VALIDATION")
        print("=" * 60)
        
        total_tests = 2
        passed_tests = sum([test1_success, test2_success])
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        print("TEST RESULTS:")
        for result in self.results[1:]:  # Skip authentication result
            status_icon = "✅ PASS" if result["status"] == "PASS" else "❌ FAIL"
            print(f"{status_icon}: {result['test']}")
            print(f"   Details: {result['details']}")
            if result.get('response_snippet'):
                print(f"   Snippet: {result['response_snippet']}")
            print()
        
        print("SUMMARY:")
        if test1_success and test2_success:
            print("✅ Both previously failing tests are now PASSING")
            print("✅ QA tier override changes are working correctly")
        elif test1_success or test2_success:
            print("⚠️  One test passing, one test failing - partial success")
            print("⚠️  QA tier override changes need additional review")
        else:
            print("❌ Both tests still failing")
            print("❌ QA tier override changes not effective")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")

def main():
    """Main test execution"""
    tester = TierOverrideTest()
    success = tester.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()