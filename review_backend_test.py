#!/usr/bin/env python3
"""
Review Request Backend Testing - January 2025
Tests the specific improvements and fixes mentioned in the review request:

1. Assessment Flow Testing - "No, I need help" responses and maturity statement updates
2. Knowledge Base Functionality - "View All Resources", deliverables, AI Assistant paywall
3. Business Profile Updates - simplified structure without "describe your services"
4. Service Request Flow - updated maturity statement handling
5. External Resources Integration - backend support for external resources

Using QA credentials as specified in the review request.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://biz-matchmaker-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ReviewBackendTester:
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
    
    def test_assessment_flow(self):
        """Test 1: Assessment Flow with 'No, I need help' responses"""
        print("\n=== TESTING ASSESSMENT FLOW ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test 1.1: Get assessment schema
        try:
            response = requests.get(f"{BASE_URL}/assessment/schema", headers=headers)
            if response.status_code == 200:
                schema = response.json()
                areas_count = len(schema.get("areas", []))
                self.log_result("Assessment Schema Retrieval", "PASS", f"Retrieved {areas_count} business areas")
            else:
                self.log_result("Assessment Schema Retrieval", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Assessment Schema Retrieval", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 1.2: Create assessment session
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
        
        # Test 1.3: Submit "No, I need help" response
        try:
            response_payload = {
                "question_id": "q1_1",
                "response": "no_need_help",
                "area_id": "area1"
            }
            response = requests.post(f"{BASE_URL}/assessment/session/{self.session_id}/response", json=response_payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                maturity_status = response_data.get("maturity_statement", "")
                if "pending" in maturity_status.lower():
                    self.log_result("Assessment 'No, I need help' Response", "PASS", f"Maturity statement updated to pending")
                else:
                    self.log_result("Assessment 'No, I need help' Response", "PARTIAL", f"Response recorded but maturity statement: {maturity_status}")
            else:
                self.log_result("Assessment 'No, I need help' Response", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Assessment 'No, I need help' Response", "FAIL", f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_knowledge_base_functionality(self):
        """Test 2: Knowledge Base Functionality"""
        print("\n=== TESTING KNOWLEDGE BASE FUNCTIONALITY ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test 2.1: View All Resources for each business area
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=headers)
            if response.status_code == 200:
                areas = response.json()
                areas_count = len(areas.get("areas", []))
                self.log_result("Knowledge Base Areas Retrieval", "PASS", f"Retrieved {areas_count} business areas")
                
                # Test accessing resources for area1
                if areas_count > 0:
                    area_response = requests.get(f"{BASE_URL}/knowledge-base/area1/content", headers=headers)
                    if area_response.status_code == 200:
                        resources = area_response.json()
                        deliverables_count = len(resources.get("deliverables", []))
                        self.log_result("Knowledge Base Resources Loading", "PASS", f"Loaded {deliverables_count} deliverables for area1")
                    else:
                        self.log_result("Knowledge Base Resources Loading", "FAIL", f"Status {area_response.status_code}")
            else:
                self.log_result("Knowledge Base Areas Retrieval", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Knowledge Base Areas Retrieval", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 2.2: AI Assistant paywall for non-test users
        try:
            # Test with regular user (should hit paywall)
            regular_user_creds = {"email": "regular.user@example.com", "password": "TestPass123!"}
            auth_response = requests.post(f"{BASE_URL}/auth/login", json=regular_user_creds)
            
            if auth_response.status_code == 200:
                regular_token = f"Bearer {auth_response.json()['access_token']}"
                regular_headers = {"Authorization": regular_token}
                
                ai_response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                          json={"question": "How do I get a business license?", "area_id": "area1"}, 
                                          headers=regular_headers)
                
                if ai_response.status_code == 402 or ai_response.status_code == 403:
                    self.log_result("AI Assistant Paywall", "PASS", f"Paywall correctly enforced (Status {ai_response.status_code})")
                else:
                    self.log_result("AI Assistant Paywall", "PARTIAL", f"Unexpected status {ai_response.status_code}")
            else:
                # Test with QA credentials (should work)
                ai_response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                          json={"question": "How do I get a business license?", "area_id": "area1"}, 
                                          headers=headers)
                
                if ai_response.status_code == 200:
                    ai_data = ai_response.json()
                    response_length = len(ai_data.get("response", ""))
                    self.log_result("AI Assistant for QA Users", "PASS", f"AI response generated ({response_length} chars)")
                else:
                    self.log_result("AI Assistant for QA Users", "FAIL", f"Status {ai_response.status_code}")
                    
        except Exception as e:
            self.log_result("AI Assistant Testing", "FAIL", f"Exception: {str(e)}")
        
        # Test 2.3: Knowledge Base download functionality
        try:
            download_response = requests.get(f"{BASE_URL}/knowledge-base/generate-template/area1/template", headers=headers)
            if download_response.status_code == 200:
                template_data = download_response.json()
                content_length = len(template_data.get("content", ""))
                filename = template_data.get("filename", "")
                self.log_result("Knowledge Base Download", "PASS", f"Template generated: {filename} ({content_length} chars)")
            else:
                self.log_result("Knowledge Base Download", "FAIL", f"Status {download_response.status_code}")
        except Exception as e:
            self.log_result("Knowledge Base Download", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def test_business_profile_updates(self):
        """Test 3: Business Profile Updates (simplified structure)"""
        print("\n=== TESTING BUSINESS PROFILE UPDATES ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test 3.1: Create business profile without "describe your services" field
        try:
            profile_payload = {
                "business_name": "QA Test Business",
                "business_type": "LLC",
                "industry": "Technology",
                "location": "Minneapolis, MN",
                "employees_count": "1-10",
                "annual_revenue": "under-100k",
                "primary_service_area": "area5"
            }
            # Notably missing "describe_your_services" field
            
            response = requests.post(f"{BASE_URL}/business/profile", json=profile_payload, headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result("Business Profile Creation (Simplified)", "PASS", f"Profile created without services description field")
            else:
                self.log_result("Business Profile Creation (Simplified)", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Business Profile Creation (Simplified)", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 3.2: Verify profile completion and validation
        try:
            response = requests.get(f"{BASE_URL}/business/profile/me", headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                is_complete = profile_data.get("profile_complete", False)
                self.log_result("Business Profile Validation", "PASS", f"Profile completion status: {is_complete}")
            else:
                self.log_result("Business Profile Validation", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Business Profile Validation", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def test_service_request_flow(self):
        """Test 4: Service Request Flow with updated maturity statement handling"""
        print("\n=== TESTING SERVICE REQUEST FLOW ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test 4.1: Create service request with updated maturity statement handling
        try:
            service_request_payload = {
                "area_id": "area5",
                "budget_range": "$1,000-$2,500",
                "timeline": "2-4 weeks",
                "description": "Need help with cybersecurity assessment and implementation for small business",
                "maturity_statement": "pending"  # Updated handling
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=service_request_payload, headers=headers)
            if response.status_code == 200:
                request_data = response.json()
                self.service_request_id = request_data.get("request_id")
                self.log_result("Service Request Creation", "PASS", f"Request created with ID: {self.service_request_id}")
            else:
                self.log_result("Service Request Creation", "FAIL", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Service Request Creation", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 4.2: Verify provider matching and response functionality
        if not self.authenticate_user("provider"):
            return False
        
        provider_headers = {"Authorization": self.tokens["provider"]}
        
        try:
            # Provider responds to service request
            provider_response_payload = {
                "request_id": self.service_request_id,
                "proposed_fee": 1500.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "I can help with comprehensive cybersecurity assessment including vulnerability scanning, policy development, and staff training."
            }
            
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=provider_response_payload, headers=provider_headers)
            if response.status_code == 200:
                response_data = response.json()
                self.log_result("Provider Response", "PASS", f"Provider response submitted successfully")
            else:
                self.log_result("Provider Response", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Provider Response", "FAIL", f"Exception: {str(e)}")
        
        # Test 4.3: Test engagement tracking and status updates
        try:
            # Check service request responses
            response = requests.get(f"{BASE_URL}/service-requests/{self.service_request_id}/responses", headers=headers)
            if response.status_code == 200:
                responses_data = response.json()
                responses_count = len(responses_data.get("responses", []))
                self.log_result("Engagement Tracking", "PASS", f"Retrieved {responses_count} provider responses")
            else:
                self.log_result("Engagement Tracking", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Engagement Tracking", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def test_external_resources_integration(self):
        """Test 5: External Resources Integration"""
        print("\n=== TESTING EXTERNAL RESOURCES INTEGRATION ===")
        
        if not self.authenticate_user("client"):
            return False
        
        headers = {"Authorization": self.tokens["client"]}
        
        # Test 5.1: External resources page for different business areas
        try:
            for area_id in ["area1", "area2", "area5"]:
                response = requests.get(f"{BASE_URL}/knowledge-base/{area_id}/content", headers=headers)
                if response.status_code == 200:
                    resources_data = response.json()
                    resources_count = len(resources_data.get("resources", []))
                    self.log_result(f"External Resources - {area_id}", "PASS", f"Retrieved {resources_count} external resources")
                else:
                    self.log_result(f"External Resources - {area_id}", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("External Resources Integration", "FAIL", f"Exception: {str(e)}")
        
        # Test 5.2: Navigation between assessment and external resources
        try:
            # Test the API endpoint that supports navigation from assessment to external resources
            navigation_payload = {
                "from_assessment": True,
                "area_id": "area1",
                "gap_identified": True
            }
            
            response = requests.post(f"{BASE_URL}/analytics/resource-access", json=navigation_payload, headers=headers)
            if response.status_code == 200:
                self.log_result("Assessment to External Resources Navigation", "PASS", f"Navigation tracking successful")
            else:
                self.log_result("Assessment to External Resources Navigation", "FAIL", f"Status {response.status_code}")
        except Exception as e:
            self.log_result("Assessment to External Resources Navigation", "FAIL", f"Exception: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all review request tests"""
        print("🎯 POLARIS PLATFORM REVIEW REQUEST BACKEND TESTING")
        print("=" * 60)
        print(f"Testing backend APIs for recent improvements and fixes")
        print(f"Base URL: {BASE_URL}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test suites
        test_suites = [
            ("Assessment Flow Testing", self.test_assessment_flow),
            ("Knowledge Base Functionality", self.test_knowledge_base_functionality),
            ("Business Profile Updates", self.test_business_profile_updates),
            ("Service Request Flow", self.test_service_request_flow),
            ("External Resources Integration", self.test_external_resources_integration)
        ]
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for suite_name, test_func in test_suites:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"{suite_name} - SUITE ERROR", "FAIL", f"Exception: {str(e)}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 REVIEW REQUEST BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        print()
        
        # Print detailed results
        print("DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = ReviewBackendTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Backend APIs ready for review!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests failed - Review needed")
        sys.exit(1)