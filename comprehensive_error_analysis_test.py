#!/usr/bin/env python3
"""
Polaris Backend Comprehensive Error Analysis Test
Focus: Achieving 95%+ success rate with detailed error analysis for failing endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ComprehensiveErrorAnalysisTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.session_ids = {}
        self.request_ids = {}
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None, 
                   status_code: int = None, error_analysis: dict = None):
        """Enhanced logging with detailed error analysis"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error_analysis": error_analysis
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if status_code:
            print(f"   HTTP Status: {status_code}")
        if error_analysis:
            print(f"   Error Analysis: {error_analysis}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def authenticate_user(self, role: str) -> bool:
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"Authentication - {role}", True, 
                              f"Token obtained for {creds['email']}", status_code=200)
                return True
            else:
                error_analysis = self.analyze_error_response(response)
                self.log_result(f"Authentication - {role}", False, 
                              f"Authentication failed", response.json(), 
                              response.status_code, error_analysis)
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False

    def analyze_error_response(self, response) -> dict:
        """Analyze error response for detailed diagnostics"""
        analysis = {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", "unknown"),
            "response_size": len(response.content)
        }
        
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                json_data = response.json()
                analysis["json_structure"] = list(json_data.keys()) if isinstance(json_data, dict) else "non-dict"
                
                # Check for Pydantic validation errors
                if "detail" in json_data:
                    detail = json_data["detail"]
                    if isinstance(detail, list):
                        analysis["validation_errors"] = []
                        for error in detail:
                            if isinstance(error, dict):
                                analysis["validation_errors"].append({
                                    "field": error.get("loc", ["unknown"])[-1],
                                    "message": error.get("msg", "unknown"),
                                    "type": error.get("type", "unknown")
                                })
                    elif isinstance(detail, dict):
                        analysis["error_code"] = detail.get("error_code")
                        analysis["error_message"] = detail.get("message")
                    else:
                        analysis["error_detail"] = str(detail)
                        
        except Exception as e:
            analysis["json_parse_error"] = str(e)
            analysis["raw_content"] = response.text[:500]  # First 500 chars
            
        return analysis

    def get_headers(self, role: str, content_type: str = "application/json") -> Dict[str, str]:
        """Get authorization headers for role with specified content type"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}",
            "Content-Type": content_type
        }

    def test_tier_response_submission_json(self) -> bool:
        """Test tier response submission with JSON format (expected to fail with 422)"""
        try:
            # First create a tier session
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            session_data = {
                "area_id": "area1",
                "tier_level": 1
            }
            
            session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                               data=session_data, headers=headers)
            
            if session_response.status_code not in [200, 201]:
                self.log_result("Tier Response Submission (JSON) - Session Creation", False, 
                              "Failed to create session", session_response.json(), 
                              session_response.status_code)
                return False
            
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            
            if not session_id:
                self.log_result("Tier Response Submission (JSON) - Session ID", False, 
                              "No session_id in response", session_data)
                return False
            
            # Now test JSON submission (should fail with 422)
            headers = self.get_headers("client", "application/json")
            response_data = {
                "question_id": "q1",
                "response": "yes",
                "evidence_provided": True,
                "evidence_url": "https://example.com/evidence.pdf",
                "tier_level": 1
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       json=response_data, headers=headers)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code == 422:
                self.log_result("Tier Response Submission (JSON)", False, 
                              "Expected 422 error - JSON not accepted, form data required", 
                              response.json(), response.status_code, error_analysis)
                return True  # This is expected behavior
            elif response.status_code in [200, 201]:
                self.log_result("Tier Response Submission (JSON)", True, 
                              "Unexpectedly succeeded with JSON", response.json(), 
                              response.status_code)
                return True
            else:
                self.log_result("Tier Response Submission (JSON)", False, 
                              "Unexpected error code", response.json(), 
                              response.status_code, error_analysis)
                return False
                
        except Exception as e:
            self.log_result("Tier Response Submission (JSON)", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_submission_form_data(self) -> bool:
        """Test tier response submission with form data (should work)"""
        try:
            # First create a tier session
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            session_data = {
                "area_id": "area1",
                "tier_level": 1
            }
            
            session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                               data=session_data, headers=headers)
            
            if session_response.status_code not in [200, 201]:
                error_analysis = self.analyze_error_response(session_response)
                self.log_result("Tier Response Submission (Form) - Session Creation", False, 
                              "Failed to create session", session_response.json(), 
                              session_response.status_code, error_analysis)
                return False
            
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            
            if not session_id:
                self.log_result("Tier Response Submission (Form) - Session ID", False, 
                              "No session_id in response", session_data)
                return False
            
            # Test form data submission
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response_data = {
                "question_id": "q1",
                "response": "yes",
                "evidence_provided": "true",
                "evidence_url": "https://example.com/evidence.pdf",
                "tier_level": "1"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       data=response_data, headers=headers)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code in [200, 201]:
                self.log_result("Tier Response Submission (Form)", True, 
                              "Form data submission successful", response.json(), 
                              response.status_code)
                return True
            else:
                self.log_result("Tier Response Submission (Form)", False, 
                              "Form data submission failed", response.json(), 
                              response.status_code, error_analysis)
                return False
                
        except Exception as e:
            self.log_result("Tier Response Submission (Form)", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_submission_multipart(self) -> bool:
        """Test tier response submission with multipart form data"""
        try:
            # First create a tier session
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            session_data = {
                "area_id": "area1",
                "tier_level": 1
            }
            
            session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                               data=session_data, headers=headers)
            
            if session_response.status_code not in [200, 201]:
                error_analysis = self.analyze_error_response(session_response)
                self.log_result("Tier Response Submission (Multipart) - Session Creation", False, 
                              "Failed to create session", session_response.json(), 
                              session_response.status_code, error_analysis)
                return False
            
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            
            if not session_id:
                self.log_result("Tier Response Submission (Multipart) - Session ID", False, 
                              "No session_id in response", session_data)
                return False
            
            # Test multipart form data submission
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            # Don't set Content-Type, let requests handle it for multipart
            
            files = {
                'question_id': (None, 'q1'),
                'response': (None, 'yes'),
                'evidence_provided': (None, 'true'),
                'evidence_url': (None, 'https://example.com/evidence.pdf'),
                'tier_level': (None, '1')
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       files=files, headers=headers)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code in [200, 201]:
                self.log_result("Tier Response Submission (Multipart)", True, 
                              "Multipart form data submission successful", response.json(), 
                              response.status_code)
                return True
            else:
                self.log_result("Tier Response Submission (Multipart)", False, 
                              "Multipart form data submission failed", response.json(), 
                              response.status_code, error_analysis)
                return False
                
        except Exception as e:
            self.log_result("Tier Response Submission (Multipart)", False, f"Exception: {str(e)}")
            return False

    def test_ai_localized_resources_detailed(self) -> bool:
        """Test AI localized resources with detailed error analysis"""
        try:
            headers = self.get_headers("client")
            
            # Test with various parameter combinations
            test_cases = [
                {
                    "name": "San Antonio, Texas",
                    "params": {
                        "city": "San Antonio",
                        "state": "Texas",
                        "area_context": "Technology & Security Infrastructure"
                    }
                },
                {
                    "name": "Austin, Texas", 
                    "params": {
                        "city": "Austin",
                        "state": "Texas",
                        "area_context": "Business Formation & Registration"
                    }
                },
                {
                    "name": "No Location",
                    "params": {
                        "area_context": "Financial Operations & Management"
                    }
                }
            ]
            
            success_count = 0
            total_cases = len(test_cases)
            
            for test_case in test_cases:
                response = self.session.get(f"{BASE_URL}/free-resources/localized", 
                                          params=test_case["params"], headers=headers)
                
                error_analysis = self.analyze_error_response(response)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Analyze response for localization
                    localization_analysis = self.analyze_localization_quality(data, test_case["params"])
                    
                    if localization_analysis["is_localized"]:
                        self.log_result(f"AI Localized Resources - {test_case['name']}", True, 
                                      f"Localized content found: {localization_analysis['details']}", 
                                      status_code=200)
                        success_count += 1
                    else:
                        self.log_result(f"AI Localized Resources - {test_case['name']}", False, 
                                      f"No localized content: {localization_analysis['details']}", 
                                      data, 200, {"localization_analysis": localization_analysis})
                else:
                    self.log_result(f"AI Localized Resources - {test_case['name']}", False, 
                                  "Request failed", response.json(), 
                                  response.status_code, error_analysis)
            
            overall_success = success_count >= total_cases * 0.7  # 70% success threshold
            self.log_result("AI Localized Resources Overall", overall_success, 
                          f"Passed {success_count}/{total_cases} test cases")
            
            return overall_success
                
        except Exception as e:
            self.log_result("AI Localized Resources", False, f"Exception: {str(e)}")
            return False

    def analyze_localization_quality(self, data: dict, params: dict) -> dict:
        """Analyze the quality of localization in the response"""
        analysis = {
            "is_localized": False,
            "details": "",
            "location_mentions": 0,
            "ai_generated": False,
            "resource_count": 0
        }
        
        if "resources" not in data or not isinstance(data["resources"], list):
            analysis["details"] = "No resources array found"
            return analysis
        
        resources = data["resources"]
        analysis["resource_count"] = len(resources)
        
        city = params.get("city", "")
        state = params.get("state", "")
        
        location_mentions = 0
        ai_generated_count = 0
        
        for resource in resources:
            resource_str = json.dumps(resource).lower()
            
            # Check for location mentions
            if city and city.lower() in resource_str:
                location_mentions += 1
            if state and state.lower() in resource_str:
                location_mentions += 1
            
            # Check for AI generation markers
            if resource.get("ai_generated") or resource.get("location_specific"):
                ai_generated_count += 1
        
        analysis["location_mentions"] = location_mentions
        analysis["ai_generated"] = ai_generated_count > 0
        
        if location_mentions > 0 or ai_generated_count > 0:
            analysis["is_localized"] = True
            analysis["details"] = f"{location_mentions} location mentions, {ai_generated_count} AI-generated resources"
        else:
            analysis["details"] = "No location-specific or AI-generated content detected"
        
        return analysis

    def test_service_request_creation_formats(self) -> bool:
        """Test service request creation with different data formats"""
        try:
            headers = self.get_headers("client")
            
            # Test data
            request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need comprehensive technology security assessment for government contracting readiness",
                "priority": "high"
            }
            
            # Test JSON format
            response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                       json=request_data, headers=headers)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code in [200, 201]:
                data = response.json()
                request_id = data.get("request_id") or data.get("id")
                if request_id:
                    self.request_ids["service_request"] = request_id
                
                self.log_result("Service Request Creation (JSON)", True, 
                              f"Request created with ID: {request_id}", data, 
                              response.status_code)
                return True
            else:
                self.log_result("Service Request Creation (JSON)", False, 
                              "JSON format failed", response.json(), 
                              response.status_code, error_analysis)
                
                # Try form data format
                headers_form = {"Authorization": f"Bearer {self.tokens['client']}"}
                response_form = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                                data=request_data, headers=headers_form)
                
                error_analysis_form = self.analyze_error_response(response_form)
                
                if response_form.status_code in [200, 201]:
                    data = response_form.json()
                    request_id = data.get("request_id") or data.get("id")
                    if request_id:
                        self.request_ids["service_request"] = request_id
                    
                    self.log_result("Service Request Creation (Form)", True, 
                                  f"Form data succeeded where JSON failed. ID: {request_id}", 
                                  data, response_form.status_code)
                    return True
                else:
                    self.log_result("Service Request Creation (Form)", False, 
                                  "Both JSON and form data failed", response_form.json(), 
                                  response_form.status_code, error_analysis_form)
                    return False
                
        except Exception as e:
            self.log_result("Service Request Creation", False, f"Exception: {str(e)}")
            return False

    def test_validation_error_details(self) -> bool:
        """Test endpoints with invalid data to analyze validation error details"""
        try:
            headers = self.get_headers("client")
            
            # Test invalid tier session creation
            invalid_session_data = {
                "area_id": "invalid_area",  # Invalid area
                "tier_level": 5  # Invalid tier level
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=invalid_session_data, headers=headers)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code == 422:
                self.log_result("Validation Error Analysis - Invalid Tier Session", True, 
                              "422 validation error as expected", response.json(), 
                              response.status_code, error_analysis)
            else:
                self.log_result("Validation Error Analysis - Invalid Tier Session", False, 
                              "Expected 422 validation error", response.json(), 
                              response.status_code, error_analysis)
            
            # Test invalid service request
            invalid_request_data = {
                "area_id": "invalid_area",
                "budget_range": "invalid_budget",
                "timeline": "",  # Empty timeline
                "description": "x",  # Too short
                "priority": "invalid_priority"
            }
            
            response2 = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                        json=invalid_request_data, headers=headers)
            
            error_analysis2 = self.analyze_error_response(response2)
            
            if response2.status_code == 422:
                self.log_result("Validation Error Analysis - Invalid Service Request", True, 
                              "422 validation error as expected", response2.json(), 
                              response2.status_code, error_analysis2)
                return True
            else:
                self.log_result("Validation Error Analysis - Invalid Service Request", False, 
                              "Expected 422 validation error", response2.json(), 
                              response2.status_code, error_analysis2)
                return False
                
        except Exception as e:
            self.log_result("Validation Error Analysis", False, f"Exception: {str(e)}")
            return False

    def test_authentication_edge_cases(self) -> bool:
        """Test authentication with various edge cases"""
        try:
            # Test with invalid credentials
            invalid_creds = {"email": "invalid@example.com", "password": "wrongpassword"}
            response = self.session.post(f"{BASE_URL}/auth/login", json=invalid_creds)
            
            error_analysis = self.analyze_error_response(response)
            
            if response.status_code == 400:
                data = response.json()
                # Check for Polaris error code
                if "error" in data and "error_code" in data.get("message", {}):
                    error_code = data["message"]["error_code"]
                    if error_code == "POL-1001":
                        self.log_result("Authentication Edge Case - Invalid Credentials", True, 
                                      f"Correct Polaris error code: {error_code}", data, 
                                      response.status_code)
                        return True
                    else:
                        self.log_result("Authentication Edge Case - Invalid Credentials", False, 
                                      f"Wrong error code: {error_code}", data, 
                                      response.status_code, error_analysis)
                        return False
                else:
                    self.log_result("Authentication Edge Case - Invalid Credentials", False, 
                                  "Missing Polaris error code structure", data, 
                                  response.status_code, error_analysis)
                    return False
            else:
                self.log_result("Authentication Edge Case - Invalid Credentials", False, 
                              "Expected 400 status code", response.json(), 
                              response.status_code, error_analysis)
                return False
                
        except Exception as e:
            self.log_result("Authentication Edge Cases", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_error_analysis(self):
        """Run comprehensive error analysis testing"""
        print("🔍 COMPREHENSIVE ERROR ANALYSIS TESTING")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Goal: Achieve 95%+ success rate with detailed error analysis")
        print(f"Test started: {datetime.now().isoformat()}")
        print()

        # Authentication phase
        print("🔐 AUTHENTICATION PHASE")
        print("-" * 30)
        auth_success = True
        for role in ["client", "provider", "agency", "navigator"]:
            if not self.authenticate_user(role):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication failed for some users. Continuing with available tokens.")

        print("\n🎯 TIER RESPONSE SUBMISSION ANALYSIS")
        print("-" * 45)
        
        # Focus on tier response submission issues
        tier_tests = [
            self.test_tier_response_submission_json,
            self.test_tier_response_submission_form_data,
            self.test_tier_response_submission_multipart
        ]
        
        tier_passed = 0
        for test in tier_tests:
            if test():
                tier_passed += 1

        print("\n🤖 AI LOCALIZED RESOURCES ANALYSIS")
        print("-" * 40)
        
        # AI localization analysis
        ai_tests = [
            self.test_ai_localized_resources_detailed
        ]
        
        ai_passed = 0
        for test in ai_tests:
            if test():
                ai_passed += 1

        print("\n📝 SERVICE REQUEST FORMAT ANALYSIS")
        print("-" * 40)
        
        # Service request format analysis
        service_tests = [
            self.test_service_request_creation_formats
        ]
        
        service_passed = 0
        for test in service_tests:
            if test():
                service_passed += 1

        print("\n⚠️ VALIDATION ERROR ANALYSIS")
        print("-" * 35)
        
        # Validation error analysis
        validation_tests = [
            self.test_validation_error_details,
            self.test_authentication_edge_cases
        ]
        
        validation_passed = 0
        for test in validation_tests:
            if test():
                validation_passed += 1

        # Calculate overall results
        total_tests = len(tier_tests) + len(ai_tests) + len(service_tests) + len(validation_tests)
        total_passed = tier_passed + ai_passed + service_passed + validation_passed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE ERROR ANALYSIS RESULTS")
        print("=" * 60)
        print(f"🎯 Tier Response Submission: {tier_passed}/{len(tier_tests)} passed")
        print(f"🤖 AI Localized Resources: {ai_passed}/{len(ai_tests)} passed")
        print(f"📝 Service Request Formats: {service_passed}/{len(service_tests)} passed")
        print(f"⚠️ Validation Error Analysis: {validation_passed}/{len(validation_tests)} passed")
        print("-" * 60)
        print(f"📈 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed error summary
        print("\n🔍 DETAILED ERROR ANALYSIS SUMMARY:")
        print("-" * 40)
        
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if not failed_tests:
            print("🎉 NO FAILURES DETECTED!")
        else:
            print(f"❌ {len(failed_tests)} FAILURES DETECTED:")
            for i, failure in enumerate(failed_tests, 1):
                print(f"\n{i}. {failure['test']}")
                print(f"   Status Code: {failure.get('status_code', 'N/A')}")
                print(f"   Details: {failure['details']}")
                if failure.get('error_analysis'):
                    error_analysis = failure['error_analysis']
                    if 'validation_errors' in error_analysis:
                        print(f"   Validation Errors:")
                        for error in error_analysis['validation_errors']:
                            print(f"     - Field '{error['field']}': {error['message']} ({error['type']})")
                    if 'error_code' in error_analysis:
                        print(f"   Error Code: {error_analysis['error_code']}")
        
        # Success rate assessment
        if success_rate >= 95:
            print(f"\n🎉 SUCCESS: Achieved {success_rate:.1f}% success rate (≥95% target)")
            status = "EXCELLENT"
        elif success_rate >= 90:
            print(f"\n✅ GOOD: Achieved {success_rate:.1f}% success rate (close to 95% target)")
            status = "GOOD"
        elif success_rate >= 80:
            print(f"\n⚠️ PARTIAL: Achieved {success_rate:.1f}% success rate (below 95% target)")
            status = "NEEDS_IMPROVEMENT"
        else:
            print(f"\n❌ CRITICAL: Only {success_rate:.1f}% success rate (far below 95% target)")
            status = "CRITICAL"
        
        print(f"\nTest completed: {datetime.now().isoformat()}")
        print(f"Status: {status}")
        
        return success_rate >= 95

def main():
    """Main test execution"""
    tester = ComprehensiveErrorAnalysisTester()
    success = tester.run_comprehensive_error_analysis()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()