#!/usr/bin/env python3
"""
Polaris Backend Detailed Testing Suite
Focus: Comprehensive testing with detailed error analysis to achieve 95%+ success rate
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://production-guru.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class DetailedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.session_ids = {}
        self.request_ids = {}
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None, 
                   status_code: int = None, request_format: str = None):
        """Enhanced logging with request format tracking"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code,
            "request_format": request_format,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if status_code:
            print(f"   HTTP Status: {status_code}")
        if request_format:
            print(f"   Request Format: {request_format}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
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
                self.log_result(f"Authentication - {role}", False, 
                              f"Authentication failed", response.json(), response.status_code)
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role: str, content_type: str = "application/json") -> Dict[str, str]:
        """Get authorization headers for role"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}",
            "Content-Type": content_type
        }

    def test_tier_based_assessment_schema(self) -> bool:
        """Test tier-based assessment schema endpoint"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "areas" in data and len(data["areas"]) >= 10:
                    self.log_result("Tier-Based Assessment Schema", True, 
                                  f"Retrieved {len(data['areas'])} areas with tier information", 
                                  status_code=200, request_format="GET")
                    return True
                else:
                    self.log_result("Tier-Based Assessment Schema", False, 
                                  "Invalid schema structure", data, 200, "GET")
                    return False
            else:
                self.log_result("Tier-Based Assessment Schema", False, 
                              "Failed to retrieve schema", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("Tier-Based Assessment Schema", False, f"Exception: {str(e)}")
            return False

    def test_create_tier_session(self) -> bool:
        """Test tier session creation with form data"""
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            session_data = {
                "area_id": "area1",
                "tier_level": 1
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=session_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                session_id = data.get("session_id")
                if session_id:
                    self.session_ids["tier_session"] = session_id
                    self.log_result("Create Tier Session", True, 
                                  f"Session created: {session_id}", data, 
                                  response.status_code, "form-data")
                    return True
                else:
                    self.log_result("Create Tier Session", False, 
                                  "No session_id in response", data, 
                                  response.status_code, "form-data")
                    return False
            else:
                self.log_result("Create Tier Session", False, 
                              "Session creation failed", response.json(), 
                              response.status_code, "form-data")
                return False
                
        except Exception as e:
            self.log_result("Create Tier Session", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_form_data(self) -> bool:
        """Test tier response submission with form data (correct format)"""
        try:
            if "tier_session" not in self.session_ids:
                self.log_result("Tier Response (Form Data)", False, "No tier session available")
                return False
                
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            session_id = self.session_ids["tier_session"]
            
            response_data = {
                "question_id": "q1",
                "response": "yes",
                "evidence_provided": "true",
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       data=response_data, headers=headers)
            
            if response.status_code in [200, 201]:
                self.log_result("Tier Response (Form Data)", True, 
                              "Form data submission successful", response.json(), 
                              response.status_code, "form-data")
                return True
            else:
                self.log_result("Tier Response (Form Data)", False, 
                              "Form data submission failed", response.json(), 
                              response.status_code, "form-data")
                return False
                
        except Exception as e:
            self.log_result("Tier Response (Form Data)", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_json_format(self) -> bool:
        """Test tier response submission with JSON (should fail with 422)"""
        try:
            if "tier_session" not in self.session_ids:
                # Create a new session for this test
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                session_data = {"area_id": "area2", "tier_level": 1}
                session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                                   data=session_data, headers=headers)
                if session_response.status_code not in [200, 201]:
                    self.log_result("Tier Response (JSON) - Session Creation", False, 
                                  "Failed to create session for JSON test")
                    return False
                session_id = session_response.json().get("session_id")
            else:
                session_id = self.session_ids["tier_session"]
                
            headers = self.get_headers("client", "application/json")
            response_data = {
                "question_id": "q2",
                "response": "no",
                "evidence_provided": False,
                "evidence_url": None
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       json=response_data, headers=headers)
            
            if response.status_code == 422:
                # This is expected - JSON format should fail
                error_data = response.json()
                validation_errors = []
                if "detail" in error_data and isinstance(error_data["detail"], list):
                    for error in error_data["detail"]:
                        if "loc" in error and "msg" in error:
                            field = error["loc"][-1] if error["loc"] else "unknown"
                            validation_errors.append(f"{field}: {error['msg']}")
                
                self.log_result("Tier Response (JSON Format)", True, 
                              f"Expected 422 validation error: {', '.join(validation_errors)}", 
                              error_data, 422, "JSON")
                return True
            else:
                self.log_result("Tier Response (JSON Format)", False, 
                              f"Expected 422 but got {response.status_code}", response.json(), 
                              response.status_code, "JSON")
                return False
                
        except Exception as e:
            self.log_result("Tier Response (JSON Format)", False, f"Exception: {str(e)}")
            return False

    def test_ai_localized_resources(self) -> bool:
        """Test AI localized resources endpoint"""
        try:
            headers = self.get_headers("client")
            
            # Test with city and state parameters
            params = {
                "city": "San Antonio",
                "state": "Texas",
                "area_context": "Technology & Security Infrastructure"
            }
            
            response = self.session.get(f"{BASE_URL}/free-resources/localized", 
                                      params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "resources" in data and "generated_by" in data:
                    generated_by = data["generated_by"]
                    resource_count = len(data["resources"])
                    city = data.get("city", "Unknown")
                    state = data.get("state", "Unknown")
                    
                    # Check if AI generation was attempted
                    if generated_by == "ai":
                        self.log_result("AI Localized Resources", True, 
                                      f"AI-generated {resource_count} resources for {city}, {state}", 
                                      status_code=200, request_format="GET")
                        return True
                    elif generated_by == "static_enhanced":
                        # Check if static resources have location awareness
                        location_aware = any(
                            resource.get("location_specific", False) or 
                            city.lower() in str(resource).lower() or 
                            state.lower() in str(resource).lower()
                            for resource in data["resources"]
                        )
                        
                        if location_aware:
                            self.log_result("AI Localized Resources", True, 
                                          f"Location-aware static resources for {city}, {state}", 
                                          status_code=200, request_format="GET")
                            return True
                        else:
                            self.log_result("AI Localized Resources", False, 
                                          f"No location-specific content (AI unavailable, static fallback used)", 
                                          data, 200, "GET")
                            return False
                    else:
                        self.log_result("AI Localized Resources", False, 
                                      f"Unknown generation method: {generated_by}", 
                                      data, 200, "GET")
                        return False
                else:
                    self.log_result("AI Localized Resources", False, 
                                  "Invalid response structure", data, 200, "GET")
                    return False
            else:
                self.log_result("AI Localized Resources", False, 
                              "Request failed", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("AI Localized Resources", False, f"Exception: {str(e)}")
            return False

    def test_service_request_creation(self) -> bool:
        """Test service request creation"""
        try:
            headers = self.get_headers("client")
            
            request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need comprehensive technology security assessment for government contracting readiness",
                "priority": "high"
            }
            
            response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                       json=request_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                request_id = data.get("request_id") or data.get("id")
                if request_id:
                    self.request_ids["service_request"] = request_id
                    self.log_result("Service Request Creation", True, 
                                  f"Request created with ID: {request_id}", 
                                  status_code=response.status_code, request_format="JSON")
                    return True
                else:
                    self.log_result("Service Request Creation", False, 
                                  "No request ID in response", data, 
                                  response.status_code, "JSON")
                    return False
            else:
                self.log_result("Service Request Creation", False, 
                              "Request creation failed", response.json(), 
                              response.status_code, "JSON")
                return False
                
        except Exception as e:
            self.log_result("Service Request Creation", False, f"Exception: {str(e)}")
            return False

    def test_provider_response_creation(self) -> bool:
        """Test provider response to service request"""
        try:
            if "service_request" not in self.request_ids:
                self.log_result("Provider Response Creation", False, "No service request available")
                return False
                
            headers = self.get_headers("provider")
            request_id = self.request_ids["service_request"]
            
            response_data = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "I can provide comprehensive technology security assessment including vulnerability scanning, compliance review, and implementation recommendations."
            }
            
            response = self.session.post(f"{BASE_URL}/provider/respond-to-request", 
                                       json=response_data, headers=headers)
            
            if response.status_code in [200, 201]:
                self.log_result("Provider Response Creation", True, 
                              "Provider response submitted successfully", response.json(), 
                              response.status_code, "JSON")
                return True
            else:
                self.log_result("Provider Response Creation", False, 
                              "Provider response failed", response.json(), 
                              response.status_code, "JSON")
                return False
                
        except Exception as e:
            self.log_result("Provider Response Creation", False, f"Exception: {str(e)}")
            return False

    def test_client_tier_access(self) -> bool:
        """Test client tier access endpoint"""
        try:
            headers = self.get_headers("client")
            
            response = self.session.get(f"{BASE_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "areas" in data and len(data["areas"]) >= 10:
                    self.log_result("Client Tier Access", True, 
                                  f"Retrieved tier access for {len(data['areas'])} areas", 
                                  status_code=200, request_format="GET")
                    return True
                else:
                    self.log_result("Client Tier Access", False, 
                                  "Invalid tier access structure", data, 200, "GET")
                    return False
            else:
                self.log_result("Client Tier Access", False, 
                              "Failed to retrieve tier access", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("Client Tier Access", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_configuration(self) -> bool:
        """Test agency tier configuration endpoint"""
        try:
            headers = self.get_headers("agency")
            
            response = self.session.get(f"{BASE_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "tier_access_levels" in data or "areas" in data:
                    self.log_result("Agency Tier Configuration", True, 
                                  "Retrieved agency tier configuration", 
                                  status_code=200, request_format="GET")
                    return True
                else:
                    self.log_result("Agency Tier Configuration", False, 
                                  "Invalid configuration structure", data, 200, "GET")
                    return False
            else:
                self.log_result("Agency Tier Configuration", False, 
                              "Failed to retrieve configuration", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("Agency Tier Configuration", False, f"Exception: {str(e)}")
            return False

    def test_knowledge_base_areas(self) -> bool:
        """Test knowledge base areas endpoint"""
        try:
            headers = self.get_headers("client")
            
            response = self.session.get(f"{BASE_URL}/knowledge-base/areas", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "areas" in data and len(data["areas"]) >= 8:
                    self.log_result("Knowledge Base Areas", True, 
                                  f"Retrieved {len(data['areas'])} knowledge base areas", 
                                  status_code=200, request_format="GET")
                    return True
                else:
                    self.log_result("Knowledge Base Areas", False, 
                                  "Invalid areas structure", data, 200, "GET")
                    return False
            else:
                self.log_result("Knowledge Base Areas", False, 
                              "Failed to retrieve KB areas", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("Knowledge Base Areas", False, f"Exception: {str(e)}")
            return False

    def test_system_health(self) -> bool:
        """Test system health endpoint"""
        try:
            headers = self.get_headers("navigator")
            
            response = self.session.get(f"{BASE_URL}/system/health", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_result("System Health", True, 
                                  f"System status: {data['status']}", 
                                  status_code=200, request_format="GET")
                    return True
                else:
                    self.log_result("System Health", False, 
                                  "Invalid health response", data, 200, "GET")
                    return False
            else:
                self.log_result("System Health", False, 
                              "Health check failed", response.json(), 
                              response.status_code, "GET")
                return False
                
        except Exception as e:
            self.log_result("System Health", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive backend testing"""
        print("🔍 DETAILED BACKEND TESTING SUITE")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Goal: Achieve 95%+ success rate with detailed analysis")
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

        print("\n🎯 CORE FUNCTIONALITY TESTING")
        print("-" * 40)
        
        # Core functionality tests
        core_tests = [
            ("Tier-Based Assessment Schema", self.test_tier_based_assessment_schema),
            ("Create Tier Session", self.test_create_tier_session),
            ("Tier Response (Form Data)", self.test_tier_response_form_data),
            ("Tier Response (JSON Format)", self.test_tier_response_json_format),
            ("Service Request Creation", self.test_service_request_creation),
            ("Provider Response Creation", self.test_provider_response_creation),
            ("Client Tier Access", self.test_client_tier_access),
            ("Agency Tier Configuration", self.test_agency_tier_configuration),
            ("Knowledge Base Areas", self.test_knowledge_base_areas),
            ("System Health", self.test_system_health)
        ]
        
        print("\n🤖 AI & LOCALIZATION TESTING")
        print("-" * 35)
        
        # AI and localization tests
        ai_tests = [
            ("AI Localized Resources", self.test_ai_localized_resources)
        ]
        
        # Run all tests
        all_tests = core_tests + ai_tests
        passed_tests = 0
        
        for test_name, test_func in all_tests:
            if test_func():
                passed_tests += 1

        # Calculate results
        total_tests = len(all_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 60)
        print("📊 DETAILED TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"📈 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Categorize results by request format
        format_results = {}
        for result in self.test_results:
            if result.get("request_format"):
                format_type = result["request_format"]
                if format_type not in format_results:
                    format_results[format_type] = {"passed": 0, "total": 0}
                format_results[format_type]["total"] += 1
                if result["success"]:
                    format_results[format_type]["passed"] += 1
        
        print("\n📋 RESULTS BY REQUEST FORMAT:")
        print("-" * 35)
        for format_type, stats in format_results.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{format_type.upper()}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # List failed tests with details
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            print("-" * 25)
            for i, failure in enumerate(failed_tests, 1):
                print(f"{i}. {failure['test']}")
                print(f"   Status: {failure.get('status_code', 'N/A')}")
                print(f"   Format: {failure.get('request_format', 'N/A')}")
                print(f"   Details: {failure['details']}")
                print()
        
        # Success rate assessment
        if success_rate >= 95:
            print(f"🎉 SUCCESS: Achieved {success_rate:.1f}% success rate (≥95% target)")
            status = "EXCELLENT"
        elif success_rate >= 90:
            print(f"✅ GOOD: Achieved {success_rate:.1f}% success rate (close to 95% target)")
            status = "GOOD"
        elif success_rate >= 80:
            print(f"⚠️ PARTIAL: Achieved {success_rate:.1f}% success rate (below 95% target)")
            status = "NEEDS_IMPROVEMENT"
        else:
            print(f"❌ CRITICAL: Only {success_rate:.1f}% success rate (far below 95% target)")
            status = "CRITICAL"
        
        print(f"\nTest completed: {datetime.now().isoformat()}")
        print(f"Final Status: {status}")
        
        return success_rate >= 95

def main():
    """Main test execution"""
    tester = DetailedBackendTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()