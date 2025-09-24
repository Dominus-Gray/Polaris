#!/usr/bin/env python3
"""
Corrected Review Request Backend Testing - January 2025
Fixed the 3 failing tests based on debugging results
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CorrectedReviewTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session_id = None
        self.service_request_id = None
        
    def log_result(self, test_name, status, details=""):
        """Log test result with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": timestamp
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"[{timestamp}] {status_icon} {test_name}: {status}")
        if details:
            print(f"    Details: {details}")
    
    def authenticate_user(self, role):
        """Authenticate user and get JWT token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = requests.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.tokens[role] = f"Bearer {token}"
                self.log_result(f"{role.title()} Authentication", "PASS", f"Token obtained")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error")
                self.log_result(f"{role.title()} Authentication", "FAIL", f"Status {response.status_code}: {error_detail}")
                return False
                
        except Exception as e:
            self.log_result(f"{role.title()} Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_corrected_assessment_flow(self):
        """Test 1: Corrected Assessment Flow"""
        print("\n=== TESTING CORRECTED ASSESSMENT FLOW ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Create assessment session
        try:
            response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
            if response.status_code == 200:
                session_data = response.json()
                self.session_id = session_data.get("session_id")
                self.log_result("Assessment Session Creation", "PASS", f"Session ID: {self.session_id}")
            else:
                self.log_result("Assessment Session Creation", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Assessment Session Creation", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Submit corrected "No, I need help" response (using "answer" instead of "response")
        try:
            response_payload = {
                "question_id": "q1_1",
                "answer": "no_need_help"  # Fixed: using "answer" instead of "response"
            }
            response = requests.post(f"{BASE_URL}/assessment/session/{self.session_id}/response", 
                                   json=response_payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                self.log_result("Assessment 'No, I need help' Response (Corrected)", "PASS", f"Response submitted successfully")
            else:
                self.log_result("Assessment 'No, I need help' Response (Corrected)", "FAIL", f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Assessment 'No, I need help' Response (Corrected)", "FAIL", f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_corrected_business_profile(self):
        """Test 2: Corrected Business Profile with all required fields"""
        print("\n=== TESTING CORRECTED BUSINESS PROFILE ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Create business profile with all required fields (but notably without "describe_your_services")
        try:
            profile_payload = {
                "company_name": "QA Test Business",  # Fixed: using correct field name
                "legal_entity_type": "LLC",  # Fixed: using correct field name
                "tax_id": "12-3456789",  # Added required field
                "registered_address": "123 Main St, Minneapolis, MN 55401",  # Added required field
                "mailing_address": "123 Main St, Minneapolis, MN 55401",  # Added required field
                "industry": "Technology",
                "primary_products_services": "Cybersecurity consulting and software development",  # Added required field
                "revenue_range": "under-500",  # Fixed: using correct format from DATA_STANDARDS
                "employees_count": "1-10",
                "ownership_structure": "Single Member LLC",  # Added required field
                "contact_name": "John Doe",  # Added required field
                "contact_title": "CEO",  # Added required field
                "contact_email": "john.doe@qatest.com",  # Added required field
                "contact_phone": "+1-555-123-4567"  # Added required field
                # Notably missing "describe_your_services" field as per review request
            }
            
            response = requests.post(f"{BASE_URL}/business/profile", json=profile_payload, headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result("Business Profile Creation (Corrected - No Services Description)", "PASS", f"Profile created successfully without services description field")
            else:
                self.log_result("Business Profile Creation (Corrected - No Services Description)", "FAIL", f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Business Profile Creation (Corrected - No Services Description)", "FAIL", f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_corrected_service_request_flow(self):
        """Test 3: Corrected Service Request Flow"""
        print("\n=== TESTING CORRECTED SERVICE REQUEST FLOW ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Create service request with corrected budget range format
        try:
            service_request_payload = {
                "area_id": "area5",
                "budget_range": "1500-5000",  # Fixed: using correct format from DATA_STANDARDS
                "timeline": "2-4 weeks",
                "description": "Need help with cybersecurity assessment and implementation for small business"
                # Removed "maturity_statement" as it's not part of StandardizedEngagementRequest
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json=service_request_payload, headers=headers)
            if response.status_code == 200:
                request_data = response.json()
                self.service_request_id = request_data.get("request_id")
                self.log_result("Service Request Creation (Corrected)", "PASS", f"Request created with ID: {self.service_request_id}")
            else:
                self.log_result("Service Request Creation (Corrected)", "FAIL", f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Service Request Creation (Corrected)", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test provider response
        if not self.authenticate_user("provider"):
            return False
        
        provider_headers = {"Authorization": self.tokens["provider"]}
        
        try:
            provider_response_payload = {
                "request_id": self.service_request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "2-4 weeks",  # Fixed: using correct format from DATA_STANDARDS
                "proposal_note": "I can help with comprehensive cybersecurity assessment including vulnerability scanning, policy development, and staff training."
            }
            
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                   json=provider_response_payload, headers=provider_headers)
            if response.status_code == 200:
                self.log_result("Provider Response (Corrected)", "PASS", f"Provider response submitted successfully")
            else:
                self.log_result("Provider Response (Corrected)", "FAIL", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Provider Response (Corrected)", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def test_knowledge_base_functionality(self):
        """Test 4: Knowledge Base Functionality (already working)"""
        print("\n=== TESTING KNOWLEDGE BASE FUNCTIONALITY ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test Knowledge Base areas
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=headers)
            if response.status_code == 200:
                areas = response.json()
                areas_count = len(areas.get("areas", []))
                self.log_result("Knowledge Base Areas", "PASS", f"Retrieved {areas_count} business areas")
            else:
                self.log_result("Knowledge Base Areas", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Knowledge Base Areas", "FAIL", f"Exception: {str(e)}")
        
        # Test AI Assistant
        try:
            ai_response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                      json={"question": "How do I get a business license?", "area_id": "area1"}, 
                                      headers=headers)
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                response_length = len(ai_data.get("response", ""))
                self.log_result("AI Assistant", "PASS", f"AI response generated ({response_length} chars)")
            else:
                self.log_result("AI Assistant", "FAIL", f"Status {ai_response.status_code}")
        except Exception as e:
            self.log_result("AI Assistant", "FAIL", f"Exception: {str(e)}")
        
        # Test template download
        try:
            download_response = requests.get(f"{BASE_URL}/knowledge-base/generate-template/area1/template", headers=headers)
            if download_response.status_code == 200:
                template_data = download_response.json()
                content_length = len(template_data.get("content", ""))
                filename = template_data.get("filename", "")
                self.log_result("Template Download", "PASS", f"Template generated: {filename} ({content_length} chars)")
            else:
                self.log_result("Template Download", "FAIL", f"Status {download_response.status_code}")
        except Exception as e:
            self.log_result("Template Download", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def run_corrected_tests(self):
        """Run all corrected tests"""
        print("🎯 CORRECTED POLARIS PLATFORM REVIEW REQUEST BACKEND TESTING")
        print("=" * 70)
        print(f"Testing corrected backend APIs for recent improvements and fixes")
        print(f"Base URL: {BASE_URL}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run corrected test suites
        test_suites = [
            ("Corrected Assessment Flow", self.test_corrected_assessment_flow),
            ("Corrected Business Profile", self.test_corrected_business_profile),
            ("Corrected Service Request Flow", self.test_corrected_service_request_flow),
            ("Knowledge Base Functionality", self.test_knowledge_base_functionality)
        ]
        
        for suite_name, test_func in test_suites:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"{suite_name} - SUITE ERROR", "FAIL", f"Exception: {str(e)}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 CORRECTED REVIEW REQUEST BACKEND TESTING SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        print()
        
        # Print detailed results
        print("DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = CorrectedReviewTester()
    passed, total = tester.run_corrected_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 ALL CORRECTED TESTS PASSED - Backend APIs ready for review!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests still failing - Further investigation needed")
        sys.exit(1)