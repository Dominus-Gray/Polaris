#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE QUALITY VERIFICATION
Tests ALL major functionality with correct data formats
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://agencydash.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

# Valid data formats from backend
VALID_TIMELINES = ["1-2 weeks", "2-4 weeks", "1-2 months", "2-3 months", "3+ months"]
VALID_BUDGET_RANGES = ["under-500", "500-1500", "1500-5000", "5000-15000", "over-15000"]
VALID_AREAS = ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8"]

class FinalQualityVerifier:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.start_time = time.time()
    
    def log_result(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def record_test(self, test_name, passed, details=""):
        result = {"test": test_name, "passed": passed, "details": details}
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        self.log_result(f"{status}: {test_name} - {details}")
    
    def make_request(self, method, endpoint, data=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=15)
            return response
        except Exception as e:
            self.log_result(f"Request failed: {e}", "ERROR")
            return None
    
    def test_authentication(self):
        """Test all QA user authentication"""
        self.log_result("=== 1. AUTHENTICATION & AUTHORIZATION (CRITICAL) ===")
        
        for role, creds in QA_CREDENTIALS.items():
            response = self.make_request("POST", "/auth/login", {
                "email": creds["email"],
                "password": creds["password"]
            })
            
            if response and response.status_code == 200:
                token_data = response.json()
                self.tokens[role] = token_data["access_token"]
                self.record_test(f"{role.title()} Authentication", True, 
                               f"Successfully authenticated {creds['email']}")
                
                # Test JWT token validation
                me_response = self.make_request("GET", "/auth/me", auth_token=self.tokens[role])
                if me_response and me_response.status_code == 200:
                    user_data = me_response.json()
                    if user_data.get("role") == role:
                        self.record_test(f"{role.title()} JWT Validation", True, 
                                       f"Token valid, role verified: {role}")
                    else:
                        self.record_test(f"{role.title()} JWT Validation", False, 
                                       f"Role mismatch: expected {role}, got {user_data.get('role')}")
                else:
                    self.record_test(f"{role.title()} JWT Validation", False, "Token validation failed")
            else:
                self.record_test(f"{role.title()} Authentication", False, 
                               f"Login failed: {response.status_code if response else 'No response'}")
        
        # Test Polaris error codes
        response = self.make_request("POST", "/auth/login", {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        
        if response and response.status_code == 400:
            error_data = response.json()
            if "POL-1001" in str(error_data):
                self.record_test("Polaris Error Code POL-1001", True, 
                               f"Correct error code returned")
            else:
                self.record_test("Polaris Error Code POL-1001", False, 
                               f"Expected POL-1001, got: {error_data}")
        else:
            self.record_test("Polaris Error Code POL-1001", False, 
                           f"Expected 400 error, got: {response.status_code if response else 'No response'}")
    
    def test_knowledge_base(self):
        """Test Knowledge Base system (RECENTLY ENHANCED)"""
        self.log_result("=== 2. KNOWLEDGE BASE SYSTEM (RECENTLY ENHANCED) ===")
        
        if "client" not in self.tokens:
            self.record_test("KB Testing", False, "No client token available")
            return
        
        # Test KB areas endpoint
        response = self.make_request("GET", "/knowledge-base/areas", auth_token=self.tokens["client"])
        if response and response.status_code == 200:
            areas = response.json()
            self.record_test("KB Areas Endpoint", True, f"Retrieved {len(areas)} areas")
        else:
            self.record_test("KB Areas Endpoint", False, 
                           f"Failed: {response.status_code if response else 'No response'}")
        
        # Test content access with authentication
        response = self.make_request("GET", "/knowledge-base/area1/content", 
                                   auth_token=self.tokens["client"])
        if response and response.status_code == 200:
            self.record_test("KB Content Access (Test Account)", True, 
                           "Test account has free access to KB content")
        else:
            self.record_test("KB Content Access (Test Account)", False, 
                           f"Access failed: {response.status_code if response else 'No response'}")
        
        # Test template generation for Office documents
        template_tests = [
            ("area1", "template", "Word document"),
            ("area2", "guide", "Word document"),
            ("area5", "practices", "PowerPoint document")
        ]
        
        for area_id, template_type, doc_type in template_tests:
            response = self.make_request("GET", 
                f"/knowledge-base/generate-template/{area_id}/{template_type}",
                auth_token=self.tokens["client"])
            
            if response and response.status_code == 200:
                template_data = response.json()
                filename = template_data.get("filename", "No filename")
                self.record_test(f"Template Generation {area_id}/{template_type}", True, 
                               f"{doc_type} generated: {filename}")
            else:
                self.record_test(f"Template Generation {area_id}/{template_type}", False, 
                               f"Generation failed: {response.status_code if response else 'No response'}")
    
    def test_data_standardization(self):
        """Test Data Standardization Implementation (NEW)"""
        self.log_result("=== 3. DATA STANDARDIZATION IMPLEMENTATION (NEW) ===")
        
        if "client" not in self.tokens or "provider" not in self.tokens:
            self.record_test("Data Standardization", False, "Missing required tokens")
            return
        
        # Test standardized service request
        service_request = {
            "area_id": "area5",
            "budget_range": "1500-5000",  # Valid budget range
            "timeline": "2-4 weeks",      # Valid timeline
            "description": "Testing standardized engagement request model with comprehensive validation and proper data structure compliance",
            "priority": "high"
        }
        
        response = self.make_request("POST", "/service-requests/professional-help", 
                                   service_request, auth_token=self.tokens["client"])
        
        if response and response.status_code == 200:
            request_data = response.json()
            request_id = request_data.get("request_id")
            self.record_test("Standardized Service Request", True, 
                           f"Request created with ID: {request_id}")
            
            # Test standardized provider response
            if request_id:
                provider_response = {
                    "request_id": request_id,
                    "proposed_fee": 2500.00,
                    "estimated_timeline": "2-4 weeks",  # Valid timeline
                    "proposal_note": "Comprehensive testing of standardized provider response model with detailed proposal and timeline estimation"
                }
                
                response = self.make_request("POST", "/provider/respond-to-request",
                                           provider_response, auth_token=self.tokens["provider"])
                
                if response and response.status_code == 200:
                    response_data = response.json()
                    self.record_test("Standardized Provider Response", True, 
                                   f"Response created with ID: {response_data.get('response_id')}")
                    self.service_request_id = request_id
                else:
                    self.record_test("Standardized Provider Response", False, 
                                   f"Failed: {response.status_code if response else 'No response'}")
                    if response:
                        self.log_result(f"   Error details: {response.text}")
        else:
            self.record_test("Standardized Service Request", False, 
                           f"Failed: {response.status_code if response else 'No response'}")
            if response:
                self.log_result(f"   Error details: {response.text}")
        
        # Test data validation with invalid data
        invalid_request = {
            "area_id": "invalid_area",
            "budget_range": "invalid_budget",
            "timeline": "invalid_timeline",
            "description": "Too short",  # Too short
            "priority": "invalid_priority"
        }
        
        response = self.make_request("POST", "/service-requests/professional-help",
                                   invalid_request, auth_token=self.tokens["client"])
        
        if response and response.status_code in [400, 422]:
            error_data = response.json()
            if any(code in str(error_data) for code in ["POL-3002", "POL-3001", "POL-3003"]):
                self.record_test("Data Validation Error Codes", True, 
                               f"Proper validation errors returned")
            else:
                self.record_test("Data Validation Error Codes", False, 
                               f"Expected Polaris error codes, got: {error_data}")
        else:
            self.record_test("Data Validation Error Codes", False, 
                           f"Expected validation error, got: {response.status_code if response else 'No response'}")
    
    def test_engagement_system(self):
        """Test Engagement System (CONSOLIDATED)"""
        self.log_result("=== 4. ENGAGEMENT SYSTEM (CONSOLIDATED) ===")
        
        if not hasattr(self, 'service_request_id'):
            self.record_test("Engagement System", False, "No service request available for testing")
            return
        
        # Test engagement creation
        if "client" in self.tokens:
            # Get service request to find provider response
            response = self.make_request("GET", f"/service-requests/{self.service_request_id}",
                                       auth_token=self.tokens["client"])
            
            if response and response.status_code == 200:
                request_data = response.json()
                if "provider_responses" in request_data and len(request_data["provider_responses"]) > 0:
                    provider_id = request_data["provider_responses"][0].get("provider_id")
                    
                    # Create engagement
                    engagement_data = {
                        "request_id": self.service_request_id,
                        "provider_id": provider_id
                    }
                    
                    response = self.make_request("POST", "/engagements",
                                               engagement_data, auth_token=self.tokens["client"])
                    
                    if response and response.status_code == 200:
                        engagement_result = response.json()
                        engagement_id = engagement_result.get("engagement_id")
                        self.record_test("Engagement Creation", True, 
                                       f"Engagement created: {engagement_id}")
                        
                        # Test status update
                        if engagement_id and "provider" in self.tokens:
                            status_update = {
                                "engagement_id": engagement_id,
                                "status": "in_progress",
                                "notes": "Engagement testing in progress",
                                "milestone_completion": 25.0
                            }
                            
                            response = self.make_request("PUT", f"/engagements/{engagement_id}/status",
                                                       status_update, auth_token=self.tokens["provider"])
                            
                            if response and response.status_code == 200:
                                self.record_test("Engagement Status Update", True, 
                                               "Status updated to in_progress")
                            else:
                                self.record_test("Engagement Status Update", False, 
                                               f"Status update failed: {response.status_code if response else 'No response'}")
                    else:
                        self.record_test("Engagement Creation", False, 
                                       f"Creation failed: {response.status_code if response else 'No response'}")
                else:
                    self.record_test("Engagement Creation", False, "No provider responses found")
            else:
                self.record_test("Engagement Creation", False, "Could not retrieve service request")
    
    def test_assessment_system(self):
        """Test Assessment System"""
        self.log_result("=== 5. ASSESSMENT SYSTEM ===")
        
        if "client" not in self.tokens:
            self.record_test("Assessment System", False, "No client token available")
            return
        
        # Get user info first
        response = self.make_request("GET", "/auth/me", auth_token=self.tokens["client"])
        if response and response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("id")
            
            # Test assessment progress
            response = self.make_request("GET", f"/assessment/progress/{user_id}",
                                       auth_token=self.tokens["client"])
            if response and response.status_code == 200:
                progress_data = response.json()
                self.record_test("Assessment Progress", True, 
                               f"Progress retrieved successfully")
            else:
                self.record_test("Assessment Progress", False, 
                               f"Progress retrieval failed: {response.status_code if response else 'No response'}")
            
            # Test assessment submission
            assessment_data = {
                "area_id": "area1",
                "responses": [
                    {"question_id": "q1", "answer": "yes", "evidence": "Test evidence for compliance"},
                    {"question_id": "q2", "answer": "no", "evidence": ""}
                ]
            }
            
            response = self.make_request("POST", "/assessment/submit",
                                       assessment_data, auth_token=self.tokens["client"])
            if response and response.status_code == 200:
                self.record_test("Assessment Submission", True, 
                               "Assessment submitted successfully")
            else:
                self.record_test("Assessment Submission", False, 
                               f"Submission failed: {response.status_code if response else 'No response'}")
    
    def test_performance(self):
        """Test Performance & Error Handling"""
        self.log_result("=== 6. PERFORMANCE & ERROR HANDLING ===")
        
        # Test response times
        response_times = []
        for i in range(5):
            start_time = time.time()
            response = self.make_request("GET", "/auth/me", auth_token=self.tokens.get("client", ""))
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        if avg_response_time < 2.0:
            self.record_test("Average Response Time", True, 
                           f"Average: {avg_response_time:.3f}s (< 2s requirement)")
        else:
            self.record_test("Average Response Time", False, 
                           f"Average: {avg_response_time:.3f}s (> 2s requirement)")
        
        if max_response_time < 2.0:
            self.record_test("Maximum Response Time", True, 
                           f"Maximum: {max_response_time:.3f}s (< 2s requirement)")
        else:
            self.record_test("Maximum Response Time", False, 
                           f"Maximum: {max_response_time:.3f}s (> 2s requirement)")
        
        # Test error handling
        response = self.make_request("GET", "/nonexistent-endpoint")
        if response and response.status_code == 404:
            self.record_test("404 Error Handling", True, 
                           "Proper 404 response for nonexistent endpoint")
        else:
            self.record_test("404 Error Handling", False, 
                           f"Unexpected response: {response.status_code if response else 'No response'}")
    
    def run_verification(self):
        """Run all verification tests"""
        self.log_result("🎯 STARTING FINAL COMPREHENSIVE QUALITY VERIFICATION")
        self.log_result(f"Testing against: {BASE_URL}")
        self.log_result(f"QA Credentials: {list(QA_CREDENTIALS.keys())}")
        
        try:
            self.test_authentication()
            self.test_knowledge_base()
            self.test_data_standardization()
            self.test_engagement_system()
            self.test_assessment_system()
            self.test_performance()
            
            self.generate_final_report()
            
        except Exception as e:
            self.log_result(f"Critical error during testing: {e}", "ERROR")
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        self.log_result("=" * 80)
        self.log_result("🎯 FINAL COMPREHENSIVE QUALITY VERIFICATION COMPLETE")
        self.log_result("=" * 80)
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log_result(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        self.log_result(f"TOTAL EXECUTION TIME: {total_time:.2f} seconds")
        
        # List critical failures
        critical_failures = [test for test in self.test_results if not test["passed"]]
        if critical_failures:
            self.log_result("🚨 FAILED TESTS:")
            for failure in critical_failures:
                self.log_result(f"   ❌ {failure['test']}: {failure['details']}")
        
        # Production readiness assessment
        if success_rate >= 95:
            self.log_result("✅ PRODUCTION READINESS: EXCELLENT - System ready for production")
        elif success_rate >= 90:
            self.log_result("✅ PRODUCTION READINESS: GOOD - System ready with minor issues")
        elif success_rate >= 80:
            self.log_result("⚠️ PRODUCTION READINESS: FAIR - Address issues before production")
        else:
            self.log_result("❌ PRODUCTION READINESS: POOR - Major issues need resolution")
        
        return {
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "execution_time": total_time
        }

if __name__ == "__main__":
    verifier = FinalQualityVerifier()
    verifier.run_verification()