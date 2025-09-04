#!/usr/bin/env python3
"""
Tier-Based Assessment Workflow Verification Test
Testing the cumulative tier logic for Business Formation (area1)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://agencydash.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class TierVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result with details"""
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
    
    def authenticate(self):
        """Authenticate with QA credentials"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_result("QA Authentication", True, f"Successfully logged in as {QA_CREDENTIALS['email']}")
                return True
            else:
                self.log_result("QA Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("QA Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_tier_session_creation(self, tier_level, expected_question_count):
        """Test tier session creation and verify question count"""
        try:
            # Create tier session for area1 (Business Formation)
            form_data = {
                "area_id": "area1",
                "tier_level": str(tier_level)
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", data=form_data)
            
            if response.status_code != 200:
                self.log_result(f"Tier {tier_level} Session Creation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
            
            session_data = response.json()
            
            # Verify session structure
            required_fields = ["session_id", "area_id", "tier_level", "total_questions", "questions"]
            missing_fields = [field for field in required_fields if field not in session_data]
            
            if missing_fields:
                self.log_result(f"Tier {tier_level} Session Creation", False, 
                              f"Missing fields: {missing_fields}")
                return None
            
            # Verify area and tier level
            if session_data["area_id"] != "area1":
                self.log_result(f"Tier {tier_level} Session Creation", False, 
                              f"Wrong area_id: expected 'area1', got '{session_data['area_id']}'")
                return None
            
            if session_data["tier_level"] != tier_level:
                self.log_result(f"Tier {tier_level} Session Creation", False, 
                              f"Wrong tier_level: expected {tier_level}, got {session_data['tier_level']}")
                return None
            
            # Verify question count
            actual_count = session_data["total_questions"]
            if actual_count != expected_question_count:
                self.log_result(f"Tier {tier_level} Session Creation", False, 
                              f"Wrong question count: expected {expected_question_count}, got {actual_count}")
                return None
            
            self.log_result(f"Tier {tier_level} Session Creation", True, 
                          f"Session created with {actual_count} questions as expected")
            
            return session_data
            
        except Exception as e:
            self.log_result(f"Tier {tier_level} Session Creation", False, f"Exception: {str(e)}")
            return None
    
    def analyze_tier_questions(self, session_data, tier_level):
        """Analyze questions to verify cumulative tier logic"""
        try:
            questions = session_data.get("questions", [])
            tier_breakdown = {}
            
            # Count questions by tier level
            for question in questions:
                q_tier = question.get("tier_level", 0)
                if q_tier not in tier_breakdown:
                    tier_breakdown[q_tier] = []
                tier_breakdown[q_tier].append({
                    "id": question.get("id", "unknown"),
                    "text": question.get("text", "")[:50] + "..." if len(question.get("text", "")) > 50 else question.get("text", ""),
                    "type": question.get("type", "unknown")
                })
            
            # Verify cumulative logic
            expected_tiers = list(range(1, tier_level + 1))
            actual_tiers = sorted(tier_breakdown.keys())
            
            if actual_tiers != expected_tiers:
                self.log_result(f"Tier {tier_level} Cumulative Logic", False, 
                              f"Expected tiers {expected_tiers}, got {actual_tiers}")
                return False
            
            # Verify each tier has exactly 3 questions
            for tier in expected_tiers:
                tier_questions = tier_breakdown.get(tier, [])
                if len(tier_questions) != 3:
                    self.log_result(f"Tier {tier_level} Cumulative Logic", False, 
                                  f"Tier {tier} has {len(tier_questions)} questions, expected 3")
                    return False
            
            # Log detailed breakdown
            breakdown_details = []
            for tier in sorted(tier_breakdown.keys()):
                tier_questions = tier_breakdown[tier]
                breakdown_details.append(f"Tier {tier}: {len(tier_questions)} questions")
                for q in tier_questions:
                    breakdown_details.append(f"  - {q['id']}: {q['text']} ({q['type']})")
            
            self.log_result(f"Tier {tier_level} Cumulative Logic", True, 
                          f"Correct cumulative structure:\n" + "\n".join(breakdown_details))
            
            return True
            
        except Exception as e:
            self.log_result(f"Tier {tier_level} Cumulative Logic", False, f"Analysis error: {str(e)}")
            return False
    
    def run_comprehensive_tier_verification(self):
        """Run comprehensive tier verification tests"""
        print("🎯 TIER-BASED ASSESSMENT WORKFLOW VERIFICATION")
        print("=" * 60)
        print(f"Testing with QA credentials: {QA_CREDENTIALS['email']}")
        print(f"Target area: area1 (Business Formation & Registration)")
        print(f"Backend URL: {BASE_URL}")
        print()
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Test each tier level
        tier_tests = [
            (1, 3, "Tier 1: Should have ONLY Tier 1 questions (3 questions)"),
            (2, 6, "Tier 2: Should have Tier 1 + Tier 2 questions (6 questions)"),
            (3, 9, "Tier 3: Should have Tier 1 + Tier 2 + Tier 3 questions (9 questions)")
        ]
        
        all_passed = True
        
        for tier_level, expected_count, description in tier_tests:
            print(f"Testing {description}")
            print("-" * 50)
            
            # Create session
            session_data = self.test_tier_session_creation(tier_level, expected_count)
            if not session_data:
                all_passed = False
                continue
            
            # Analyze questions
            if not self.analyze_tier_questions(session_data, tier_level):
                all_passed = False
            
            print()
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("TIER VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        # Key findings
        print("KEY FINDINGS:")
        
        # Check if tier logic is working
        tier_creation_tests = [r for r in self.test_results if "Session Creation" in r["test"]]
        tier_logic_tests = [r for r in self.test_results if "Cumulative Logic" in r["test"]]
        
        if all(t["success"] for t in tier_creation_tests):
            print("✅ Tier session creation working for all levels")
        else:
            print("❌ Tier session creation has issues")
        
        if all(t["success"] for t in tier_logic_tests):
            print("✅ Cumulative tier logic working correctly")
        else:
            print("❌ Cumulative tier logic has issues")
        
        # Authentication check
        auth_test = next((r for r in self.test_results if "Authentication" in r["test"]), None)
        if auth_test and auth_test["success"]:
            print("✅ QA credentials authentication working")
        else:
            print("❌ QA credentials authentication failed")
        
        print()
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = TierVerificationTester()
    
    try:
        success = tester.run_comprehensive_tier_verification()
        tester.print_summary()
        
        if success:
            print("🎉 ALL TIER VERIFICATION TESTS PASSED!")
            print("The tier-based assessment system is working correctly.")
            sys.exit(0)
        else:
            print("⚠️  SOME TIER VERIFICATION TESTS FAILED!")
            print("The tier-based assessment system needs attention.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()