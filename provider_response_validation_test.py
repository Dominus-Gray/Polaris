#!/usr/bin/env python3
"""
Provider Response Validation Testing
Comprehensive testing to identify specific provider response validation issues
as requested in the review request.
"""

import requests
import json
import sys
from datetime import datetime
from decimal import Decimal

# Configuration
BASE_URL = "https://sbap-platform.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ProviderResponseValidationTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.service_request_id = None
        self.validation_issues = []
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def log_test_result(self, test_name, status, details=None):
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        self.log_result(f"{status_icon} {test_name}: {status}")
        if details:
            self.log_result(f"    Details: {details}")
    
    def login_user(self, role):
        """Login user and store token"""
        creds = QA_CREDENTIALS[role]
        payload = {
            "email": creds["email"],
            "password": creds["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"✅ {role.title()} login successful")
                return True
            else:
                self.log_result(f"❌ {role.title()} login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} login error: {str(e)}")
            return False
    
    def create_test_service_request(self):
        """Create a test service request for provider response testing"""
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        payload = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Provider response validation test - need technology security infrastructure assessment and implementation",
            "priority": "high"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.service_request_id = data.get("request_id")
                self.log_result(f"✅ Test service request created: {self.service_request_id}")
                return True
            else:
                self.log_result(f"❌ Service request creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Service request creation error: {str(e)}")
            return False
    
    def test_valid_provider_response(self):
        """Test 1: Valid provider response with all correct fields"""
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        payload = {
            "request_id": self.service_request_id,
            "proposed_fee": 2500.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "I can provide comprehensive technology security infrastructure assessment including network security audit, vulnerability testing, and implementation of security protocols. My approach includes initial assessment, security gap analysis, and phased implementation plan."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Valid Provider Response", "PASS", 
                    f"Response ID: {data.get('response_id')}, Fee: {data.get('proposed_fee')}")
                return data
            else:
                self.log_test_result("Valid Provider Response", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
                self.validation_issues.append(f"Valid response failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test_result("Valid Provider Response", "FAIL", f"Exception: {str(e)}")
            self.validation_issues.append(f"Valid response exception: {str(e)}")
            return None
    
    def test_invalid_proposed_fee_scenarios(self):
        """Test 2: Invalid proposed_fee values"""
        test_cases = [
            {"fee": -100, "description": "Negative fee"},
            {"fee": 0, "description": "Zero fee"},
            {"fee": 75000, "description": "Fee above maximum (50000)"},
            {"fee": "invalid", "description": "Non-numeric fee"},
            {"fee": None, "description": "Missing fee"}
        ]
        
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        for i, test_case in enumerate(test_cases):
            # Create new service request for each test
            if not self.create_test_service_request():
                continue
                
            payload = {
                "request_id": self.service_request_id,
                "proposed_fee": test_case["fee"],
                "estimated_timeline": "2-4 weeks",
                "proposal_note": "Test proposal note for validation testing - this is a comprehensive proposal with sufficient detail."
            }
            
            try:
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
                
                if response.status_code == 400 or response.status_code == 422:
                    self.log_test_result(f"Invalid Fee Test - {test_case['description']}", "PASS", 
                        f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test_result(f"Invalid Fee Test - {test_case['description']}", "FAIL", 
                        f"Should have been rejected but got status {response.status_code}")
                    self.validation_issues.append(f"Fee validation failed for {test_case['description']}: accepted invalid fee")
                    
            except Exception as e:
                self.log_test_result(f"Invalid Fee Test - {test_case['description']}", "FAIL", f"Exception: {str(e)}")
                self.validation_issues.append(f"Fee test exception for {test_case['description']}: {str(e)}")
    
    def test_invalid_timeline_scenarios(self):
        """Test 3: Invalid timeline formats"""
        test_cases = [
            {"timeline": "invalid timeline", "description": "Invalid timeline format"},
            {"timeline": "5-6 weeks", "description": "Timeline not in allowed ranges"},
            {"timeline": "", "description": "Empty timeline"},
            {"timeline": None, "description": "Missing timeline"}
        ]
        
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        for test_case in test_cases:
            # Create new service request for each test
            if not self.create_test_service_request():
                continue
                
            payload = {
                "request_id": self.service_request_id,
                "proposed_fee": 2000.00,
                "estimated_timeline": test_case["timeline"],
                "proposal_note": "Test proposal note for timeline validation testing - this is a comprehensive proposal with sufficient detail."
            }
            
            try:
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
                
                if response.status_code == 400 or response.status_code == 422:
                    self.log_test_result(f"Invalid Timeline Test - {test_case['description']}", "PASS", 
                        f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test_result(f"Invalid Timeline Test - {test_case['description']}", "FAIL", 
                        f"Should have been rejected but got status {response.status_code}")
                    self.validation_issues.append(f"Timeline validation failed for {test_case['description']}: accepted invalid timeline")
                    
            except Exception as e:
                self.log_test_result(f"Invalid Timeline Test - {test_case['description']}", "FAIL", f"Exception: {str(e)}")
                self.validation_issues.append(f"Timeline test exception for {test_case['description']}: {str(e)}")
    
    def test_missing_required_fields(self):
        """Test 4: Missing required fields"""
        test_cases = [
            {"missing_field": "request_id", "payload": {"proposed_fee": 2000, "estimated_timeline": "2-4 weeks", "proposal_note": "Test note"}},
            {"missing_field": "proposed_fee", "payload": {"request_id": self.service_request_id, "estimated_timeline": "2-4 weeks", "proposal_note": "Test note"}},
            {"missing_field": "estimated_timeline", "payload": {"request_id": self.service_request_id, "proposed_fee": 2000, "proposal_note": "Test note"}},
            {"missing_field": "proposal_note", "payload": {"request_id": self.service_request_id, "proposed_fee": 2000, "estimated_timeline": "2-4 weeks"}}
        ]
        
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        for test_case in test_cases:
            # Create new service request for each test (except request_id test)
            if test_case["missing_field"] != "request_id":
                if not self.create_test_service_request():
                    continue
                test_case["payload"]["request_id"] = self.service_request_id
            
            try:
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=test_case["payload"], headers=headers)
                
                if response.status_code == 400 or response.status_code == 422:
                    self.log_test_result(f"Missing Field Test - {test_case['missing_field']}", "PASS", 
                        f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test_result(f"Missing Field Test - {test_case['missing_field']}", "FAIL", 
                        f"Should have been rejected but got status {response.status_code}")
                    self.validation_issues.append(f"Missing field validation failed for {test_case['missing_field']}: accepted incomplete data")
                    
            except Exception as e:
                self.log_test_result(f"Missing Field Test - {test_case['missing_field']}", "FAIL", f"Exception: {str(e)}")
                self.validation_issues.append(f"Missing field test exception for {test_case['missing_field']}: {str(e)}")
    
    def test_proposal_note_validation(self):
        """Test 5: Proposal note validation (length and content)"""
        test_cases = [
            {"note": "Short", "description": "Too short (under 20 chars)"},
            {"note": "x" * 2000, "description": "Too long (over 1500 chars)"},
            {"note": "", "description": "Empty note"},
            {"note": None, "description": "Missing note"}
        ]
        
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        for test_case in test_cases:
            # Create new service request for each test
            if not self.create_test_service_request():
                continue
                
            payload = {
                "request_id": self.service_request_id,
                "proposed_fee": 2000.00,
                "estimated_timeline": "2-4 weeks",
                "proposal_note": test_case["note"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
                
                if response.status_code == 400 or response.status_code == 422:
                    self.log_test_result(f"Proposal Note Test - {test_case['description']}", "PASS", 
                        f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test_result(f"Proposal Note Test - {test_case['description']}", "FAIL", 
                        f"Should have been rejected but got status {response.status_code}")
                    self.validation_issues.append(f"Proposal note validation failed for {test_case['description']}: accepted invalid note")
                    
            except Exception as e:
                self.log_test_result(f"Proposal Note Test - {test_case['description']}", "FAIL", f"Exception: {str(e)}")
                self.validation_issues.append(f"Proposal note test exception for {test_case['description']}: {str(e)}")
    
    def test_duplicate_response_prevention(self):
        """Test 6: Duplicate response prevention"""
        # Create service request
        if not self.create_test_service_request():
            return
            
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        payload = {
            "request_id": self.service_request_id,
            "proposed_fee": 2000.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "First response to test duplicate prevention - comprehensive proposal with detailed approach and methodology."
        }
        
        # First response should succeed
        try:
            response1 = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
            
            if response1.status_code == 200:
                self.log_test_result("Duplicate Prevention - First Response", "PASS", "First response accepted")
                
                # Second response should be rejected
                payload["proposal_note"] = "Second response attempt - should be rejected due to duplicate prevention logic."
                response2 = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
                
                if response2.status_code == 400:
                    self.log_test_result("Duplicate Prevention - Second Response", "PASS", 
                        f"Correctly rejected duplicate with status {response2.status_code}")
                else:
                    self.log_test_result("Duplicate Prevention - Second Response", "FAIL", 
                        f"Should have rejected duplicate but got status {response2.status_code}")
                    self.validation_issues.append(f"Duplicate prevention failed: allowed second response")
            else:
                self.log_test_result("Duplicate Prevention - First Response", "FAIL", 
                    f"First response failed: {response1.status_code}")
                self.validation_issues.append(f"Duplicate test setup failed: first response rejected")
                
        except Exception as e:
            self.log_test_result("Duplicate Prevention Test", "FAIL", f"Exception: {str(e)}")
            self.validation_issues.append(f"Duplicate prevention test exception: {str(e)}")
    
    def test_non_existent_service_request(self):
        """Test 7: Response to non-existent service request"""
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        payload = {
            "request_id": "req_non-existent-request-id",
            "proposed_fee": 2000.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "Response to non-existent service request - should be rejected with appropriate error message."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
            
            if response.status_code == 404:
                self.log_test_result("Non-existent Request Test", "PASS", 
                    f"Correctly rejected with status {response.status_code}")
            else:
                self.log_test_result("Non-existent Request Test", "FAIL", 
                    f"Should have returned 404 but got status {response.status_code}")
                self.validation_issues.append(f"Non-existent request validation failed: wrong status code")
                
        except Exception as e:
            self.log_test_result("Non-existent Request Test", "FAIL", f"Exception: {str(e)}")
            self.validation_issues.append(f"Non-existent request test exception: {str(e)}")
    
    def test_data_consistency_and_retrieval(self):
        """Test 8: Data consistency between request and response"""
        # Create service request
        if not self.create_test_service_request():
            return
            
        # Create provider response
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        response_payload = {
            "request_id": self.service_request_id,
            "proposed_fee": 3500.50,
            "estimated_timeline": "1-2 months",
            "proposal_note": "Data consistency test response - comprehensive proposal with detailed methodology and implementation plan for technology security infrastructure."
        }
        
        try:
            # Submit response
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=response_payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                response_id = response_data.get("response_id")
                
                # Retrieve service request with responses
                client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                get_response = requests.get(f"{BASE_URL}/service-requests/{self.service_request_id}/responses", headers=client_headers)
                
                if get_response.status_code == 200:
                    responses_data = get_response.json()
                    responses = responses_data.get("responses", [])
                    
                    if responses:
                        provider_response = responses[0]
                        
                        # Validate data consistency
                        consistency_checks = [
                            ("proposed_fee", 3500.50, provider_response.get("proposed_fee")),
                            ("estimated_timeline", "1-2 months", provider_response.get("estimated_timeline")),
                            ("request_id", self.service_request_id, provider_response.get("request_id")),
                            ("response_id", response_id, provider_response.get("response_id"))
                        ]
                        
                        all_consistent = True
                        inconsistencies = []
                        
                        for field, expected, actual in consistency_checks:
                            if expected != actual:
                                all_consistent = False
                                inconsistencies.append(f"{field}: expected {expected}, got {actual}")
                        
                        if all_consistent:
                            self.log_test_result("Data Consistency Test", "PASS", 
                                "All fields consistent between request and response")
                        else:
                            self.log_test_result("Data Consistency Test", "FAIL", 
                                f"Inconsistencies: {', '.join(inconsistencies)}")
                            self.validation_issues.append(f"Data consistency issues: {inconsistencies}")
                    else:
                        self.log_test_result("Data Consistency Test", "FAIL", "No responses found in retrieval")
                        self.validation_issues.append("Data consistency test: response not found in retrieval")
                else:
                    self.log_test_result("Data Consistency Test", "FAIL", 
                        f"Failed to retrieve responses: {get_response.status_code}")
                    self.validation_issues.append(f"Data consistency test: retrieval failed with {get_response.status_code}")
            else:
                self.log_test_result("Data Consistency Test", "FAIL", 
                    f"Response creation failed: {response.status_code}")
                self.validation_issues.append(f"Data consistency test: response creation failed")
                
        except Exception as e:
            self.log_test_result("Data Consistency Test", "FAIL", f"Exception: {str(e)}")
            self.validation_issues.append(f"Data consistency test exception: {str(e)}")
    
    def test_database_structure_validation(self):
        """Test 9: Validate database document structure"""
        # Create service request and response
        if not self.create_test_service_request():
            return
            
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        payload = {
            "request_id": self.service_request_id,
            "proposed_fee": 2750.25,
            "estimated_timeline": "2-3 months",
            "proposal_note": "Database structure validation test - comprehensive proposal with detailed approach for technology security infrastructure implementation and ongoing support."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check required fields in response
                required_fields = ["response_id", "request_id", "proposed_fee", "estimated_timeline", "status", "created_at"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in response_data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_test_result("Database Structure Test", "PASS", 
                        "All required fields present in response")
                else:
                    self.log_test_result("Database Structure Test", "FAIL", 
                        f"Missing fields: {missing_fields}")
                    self.validation_issues.append(f"Database structure validation: missing fields {missing_fields}")
            else:
                self.log_test_result("Database Structure Test", "FAIL", 
                    f"Response creation failed: {response.status_code}")
                self.validation_issues.append(f"Database structure test: response creation failed")
                
        except Exception as e:
            self.log_test_result("Database Structure Test", "FAIL", f"Exception: {str(e)}")
            self.validation_issues.append(f"Database structure test exception: {str(e)}")
    
    def run_comprehensive_validation_tests(self):
        """Execute all provider response validation tests"""
        self.log_result("🔍 Starting Provider Response Validation Testing")
        self.log_result("=" * 70)
        
        # Setup: Login users
        if not self.login_user("client") or not self.login_user("provider"):
            self.log_result("❌ Failed to login users - cannot proceed with tests")
            return False
        
        # Run all validation tests
        test_methods = [
            self.test_valid_provider_response,
            self.test_invalid_proposed_fee_scenarios,
            self.test_invalid_timeline_scenarios,
            self.test_missing_required_fields,
            self.test_proposal_note_validation,
            self.test_duplicate_response_prevention,
            self.test_non_existent_service_request,
            self.test_data_consistency_and_retrieval,
            self.test_database_structure_validation
        ]
        
        for test_method in test_methods:
            try:
                self.log_result(f"\n🧪 Running {test_method.__name__}")
                test_method()
            except Exception as e:
                self.log_result(f"❌ Test {test_method.__name__} failed with exception: {str(e)}")
                self.validation_issues.append(f"Test {test_method.__name__} exception: {str(e)}")
        
        return True
    
    def print_final_report(self):
        """Print comprehensive test report"""
        self.log_result("\n" + "=" * 70)
        self.log_result("📊 PROVIDER RESPONSE VALIDATION TEST REPORT")
        self.log_result("=" * 70)
        
        # Test summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        self.log_result(f"Total Tests: {total_tests}")
        self.log_result(f"Passed: {passed_tests}")
        self.log_result(f"Failed: {failed_tests}")
        self.log_result(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # Failed tests details
        if failed_tests > 0:
            self.log_result(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    self.log_result(f"  - {result['test']}: {result.get('details', 'No details')}")
        
        # Validation issues summary
        if self.validation_issues:
            self.log_result(f"\n🚨 VALIDATION ISSUES IDENTIFIED ({len(self.validation_issues)}):")
            for i, issue in enumerate(self.validation_issues, 1):
                self.log_result(f"  {i}. {issue}")
        else:
            self.log_result("\n✅ NO CRITICAL VALIDATION ISSUES IDENTIFIED")
        
        # Recommendations
        self.log_result(f"\n💡 RECOMMENDATIONS:")
        if self.validation_issues:
            self.log_result("  - Review and fix the identified validation issues")
            self.log_result("  - Implement proper error handling for edge cases")
            self.log_result("  - Add comprehensive input validation")
            self.log_result("  - Ensure data consistency across database operations")
        else:
            self.log_result("  - Provider response validation appears to be working correctly")
            self.log_result("  - Continue monitoring for edge cases in production")

def main():
    """Main test execution"""
    tester = ProviderResponseValidationTester()
    
    try:
        success = tester.run_comprehensive_validation_tests()
        tester.print_final_report()
        
        if success and len(tester.validation_issues) == 0:
            print("\n🎉 PROVIDER RESPONSE VALIDATION TESTS COMPLETED - NO CRITICAL ISSUES")
            sys.exit(0)
        elif success:
            print(f"\n⚠️ PROVIDER RESPONSE VALIDATION TESTS COMPLETED - {len(tester.validation_issues)} ISSUES FOUND")
            sys.exit(1)
        else:
            print("\n❌ PROVIDER RESPONSE VALIDATION TESTS FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()