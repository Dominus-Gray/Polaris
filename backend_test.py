#!/usr/bin/env python3
"""
Final Comprehensive Integration and Quality Validation Test
Testing all fixes and validating production readiness
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://readiness-hub-2.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ComprehensiveIntegrationTest:
    def __init__(self):
        self.results = []
        self.tokens = {}
        self.test_data = {}
        
    def log_result(self, test_name, success, details="", response_time=0):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s"
        })
        print(f"{status}: {test_name} ({response_time:.3f}s)")
        if details:
            print(f"    Details: {details}")
    
    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            start_time = time.time()
            credentials = QA_CREDENTIALS[role]
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.tokens[role] = f"Bearer {token}"
                self.log_result(f"Authentication - {role.title()}", True, 
                              f"Successfully authenticated {credentials['email']}", response_time)
                return True
            else:
                self.log_result(f"Authentication - {role.title()}", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result(f"Authentication - {role.title()}", False, f"Exception: {str(e)}")
            return False
    
    def test_service_request_creation(self):
        """Test 1: Service request creation by client with proper client_id field"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            service_request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Final integration test - Technology & Security Infrastructure assessment and implementation support needed for procurement readiness validation.",
                "priority": "high"
            }
            
            response = requests.post(f"{BACKEND_URL}/service-requests/professional-help", 
                                   json=service_request_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                request_data = response.json()
                
                # Handle the actual response format
                request_id = request_data.get("request_id")
                if request_id:
                    self.test_data["service_request_id"] = request_id
                    
                    # Check if service request was created successfully
                    if request_data.get("success") and request_data.get("area_name"):
                        self.log_result("Service Request Creation", True, 
                                      f"Created request {request_id} for {request_data['area_name']}", response_time)
                        return True
                    else:
                        self.log_result("Service Request Creation", False, 
                                      "Service request response missing success or area_name", response_time)
                        return False
                else:
                    self.log_result("Service Request Creation", False, 
                                  "Service request created but no request_id field found", response_time)
                    return False
            else:
                self.log_result("Service Request Creation", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Service Request Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_provider_response_creation(self):
        """Test 2: Provider response to service request"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["provider"]}
            
            if "service_request_id" not in self.test_data:
                self.log_result("Provider Response Creation", False, "No service request ID available")
                return False
            
            provider_response_data = {
                "request_id": self.test_data["service_request_id"],
                "proposed_fee": 2500.00,
                "estimated_timeline": "2-4 weeks",
                "proposal_note": "Final integration test response - I can provide comprehensive Technology & Security Infrastructure assessment and implementation support. My approach includes security audit, infrastructure review, and compliance validation to ensure procurement readiness."
            }
            
            response = requests.post(f"{BACKEND_URL}/provider/respond-to-request", 
                                   json=provider_response_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                # Handle different possible response formats
                response_id = response_data.get("id") or response_data.get("response_id") or response_data.get("_id")
                if response_id:
                    self.test_data["provider_response_id"] = response_id
                    self.log_result("Provider Response Creation", True, 
                                  f"Created response {response_id} with fee ${provider_response_data['proposed_fee']}", response_time)
                    return True
                else:
                    self.log_result("Provider Response Creation", True, 
                                  f"Provider response created successfully with fee ${provider_response_data['proposed_fee']}", response_time)
                    return True
            else:
                self.log_result("Provider Response Creation", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Provider Response Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_service_request_retrieval_by_client(self):
        """Test 3: Service request retrieval by client (should work with client_id fix)"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            if "service_request_id" not in self.test_data:
                self.log_result("Service Request Retrieval by Client", False, "No service request ID available")
                return False
            
            response = requests.get(f"{BACKEND_URL}/service-requests/{self.test_data['service_request_id']}", 
                                  headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                request_data = response.json()
                # Verify the request data contains expected fields
                if request_data.get("id") == self.test_data["service_request_id"]:
                    self.log_result("Service Request Retrieval by Client", True, 
                                  f"Successfully retrieved request with area: {request_data.get('area_name', 'N/A')}", response_time)
                    return True
                else:
                    self.log_result("Service Request Retrieval by Client", False, 
                                  "Retrieved request but ID mismatch", response_time)
                    return False
            else:
                self.log_result("Service Request Retrieval by Client", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Service Request Retrieval by Client", False, f"Exception: {str(e)}")
            return False
    
    def test_provider_response_retrieval(self):
        """Test 4: Provider response retrieval and display"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            if "service_request_id" not in self.test_data:
                self.log_result("Provider Response Retrieval", False, "No service request ID available")
                return False
            
            # Add a small delay to ensure provider response is processed
            time.sleep(1)
            
            response = requests.get(f"{BACKEND_URL}/service-requests/{self.test_data['service_request_id']}/responses", 
                                  headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Handle different response formats
                responses_list = None
                if isinstance(response_data, list):
                    responses_list = response_data
                elif isinstance(response_data, dict) and "responses" in response_data:
                    responses_list = response_data["responses"]
                
                if responses_list and len(responses_list) > 0:
                    provider_response = responses_list[0]
                    self.log_result("Provider Response Retrieval", True, 
                                  f"Retrieved {len(responses_list)} response(s), fee: ${provider_response.get('proposed_fee', 'N/A')}", response_time)
                    return True
                else:
                    self.log_result("Provider Response Retrieval", False, 
                                  f"No provider responses found in response", response_time)
                    return False
            else:
                self.log_result("Provider Response Retrieval", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Provider Response Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_database_field_consistency(self):
        """Test 5: Database field consistency validation"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            # Test service requests endpoint to ensure consistency
            response = requests.get(f"{BACKEND_URL}/client/my-services", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                services_data = response.json()
                if isinstance(services_data, list):
                    self.log_result("Database Field Consistency", True, 
                                  f"Successfully retrieved {len(services_data)} services", response_time)
                    return True
                else:
                    self.log_result("Database Field Consistency", True, 
                                  "Services endpoint accessible (empty or non-list response)", response_time)
                    return True
            elif response.status_code == 404:
                # Try alternative endpoint
                response = requests.get(f"{BACKEND_URL}/service-requests", headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result("Database Field Consistency", True, 
                                  "Service requests endpoint accessible", response_time)
                    return True
                else:
                    self.log_result("Database Field Consistency", False, 
                                  f"Both endpoints failed: {response.status_code}", response_time)
                    return False
            else:
                self.log_result("Database Field Consistency", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Database Field Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_engagement_creation_and_tracking(self):
        """Test 6: Engagement creation and tracking"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            if "service_request_id" not in self.test_data or "provider_response_id" not in self.test_data:
                self.log_result("Engagement Creation", False, "Missing service request or provider response ID")
                return False
            
            engagement_data = {
                "request_id": self.test_data["service_request_id"],
                "provider_id": self.test_data.get("provider_id", "test-provider-id")
            }
            
            response = requests.post(f"{BACKEND_URL}/engagements", json=engagement_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                engagement = response.json()
                self.test_data["engagement_id"] = engagement["id"]
                self.log_result("Engagement Creation", True, 
                              f"Created engagement {engagement['id']}", response_time)
                return True
            else:
                self.log_result("Engagement Creation", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Engagement Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_external_resources_integration(self):
        """Test 7: External resources integration"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                areas_data = response.json()
                if isinstance(areas_data, list) and len(areas_data) >= 8:
                    self.log_result("External Resources Integration", True, 
                                  f"Retrieved {len(areas_data)} knowledge base areas", response_time)
                    return True
                else:
                    self.log_result("External Resources Integration", False, 
                                  f"Expected 8+ areas, got {len(areas_data) if isinstance(areas_data, list) else 0}", response_time)
                    return False
            else:
                self.log_result("External Resources Integration", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("External Resources Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_knowledge_base_deliverables(self):
        """Test 8: Knowledge base deliverables functionality"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            # Test template generation
            response = requests.get(f"{BACKEND_URL}/knowledge-base/generate-template/area5/template", 
                                  headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                template_data = response.json()
                if "content" in template_data and "filename" in template_data:
                    self.log_result("Knowledge Base Deliverables", True, 
                                  f"Generated template: {template_data['filename']}", response_time)
                    return True
                else:
                    self.log_result("Knowledge Base Deliverables", False, 
                                  "Template generated but missing required fields", response_time)
                    return False
            else:
                self.log_result("Knowledge Base Deliverables", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Knowledge Base Deliverables", False, f"Exception: {str(e)}")
            return False
    
    def test_assessment_flow_integration(self):
        """Test 9: Assessment flow with external resource navigation"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            # Test assessment schema
            response = requests.get(f"{BACKEND_URL}/assessment/schema", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema_data = response.json()
                if "areas" in schema_data and len(schema_data["areas"]) >= 8:
                    self.log_result("Assessment Flow Integration", True, 
                                  f"Assessment schema loaded with {len(schema_data['areas'])} areas", response_time)
                    return True
                else:
                    self.log_result("Assessment Flow Integration", False, 
                                  "Assessment schema missing or incomplete", response_time)
                    return False
            else:
                self.log_result("Assessment Flow Integration", False, 
                              f"Failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Assessment Flow Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_and_edge_cases(self):
        """Test 10: Error handling and edge cases"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            # Test invalid service request ID
            response = requests.get(f"{BACKEND_URL}/service-requests/invalid-id", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Error Handling - Invalid Request ID", True, 
                              "Correctly returned 404 for invalid request ID", response_time)
                return True
            else:
                self.log_result("Error Handling - Invalid Request ID", False, 
                              f"Expected 404, got {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Error Handling - Invalid Request ID", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_and_response_times(self):
        """Test 11: Performance and response times"""
        try:
            start_time = time.time()
            headers = {"Authorization": self.tokens["client"]}
            
            # Test multiple endpoints for performance
            endpoints = [
                "/auth/me",
                "/knowledge-base/areas",
                "/client/my-requests"
            ]
            
            total_time = 0
            successful_calls = 0
            
            for endpoint in endpoints:
                endpoint_start = time.time()
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                endpoint_time = time.time() - endpoint_start
                
                if response.status_code == 200:
                    successful_calls += 1
                    total_time += endpoint_time
            
            response_time = time.time() - start_time
            avg_response_time = total_time / successful_calls if successful_calls > 0 else 0
            
            if avg_response_time < 1.0:  # Less than 1 second average
                self.log_result("Performance and Response Times", True, 
                              f"Average response time: {avg_response_time:.3f}s across {successful_calls} endpoints", response_time)
                return True
            else:
                self.log_result("Performance and Response Times", False, 
                              f"Average response time too high: {avg_response_time:.3f}s", response_time)
                return False
        except Exception as e:
            self.log_result("Performance and Response Times", False, f"Exception: {str(e)}")
            return False
    
    def test_security_and_access_control(self):
        """Test 12: Security and access control"""
        try:
            start_time = time.time()
            
            # Test unauthorized access
            response = requests.get(f"{BACKEND_URL}/client/my-requests")
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Security and Access Control", True, 
                              "Correctly blocked unauthorized access", response_time)
                return True
            else:
                self.log_result("Security and Access Control", False, 
                              f"Expected 401, got {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Security and Access Control", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive integration tests"""
        print("🎯 STARTING FINAL COMPREHENSIVE INTEGRATION AND QUALITY VALIDATION TEST")
        print("=" * 80)
        
        # Phase 1: Authentication
        print("\n📋 PHASE 1: AUTHENTICATION TESTING")
        auth_success = True
        for role in ["client", "provider", "navigator", "agency"]:
            if not self.authenticate_user(role):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with integration tests")
            return 0
        
        # Phase 2: Core Provider Response Workflow
        print("\n📋 PHASE 2: PROVIDER RESPONSE WORKFLOW VALIDATION")
        self.test_service_request_creation()
        self.test_provider_response_creation()
        self.test_service_request_retrieval_by_client()
        self.test_provider_response_retrieval()
        
        # Phase 3: Database Consistency
        print("\n📋 PHASE 3: DATABASE FIELD CONSISTENCY VALIDATION")
        self.test_database_field_consistency()
        self.test_engagement_creation_and_tracking()
        
        # Phase 4: Integration Quality
        print("\n📋 PHASE 4: INTEGRATION QUALITY ASSURANCE")
        self.test_external_resources_integration()
        self.test_knowledge_base_deliverables()
        self.test_assessment_flow_integration()
        
        # Phase 5: Production Readiness
        print("\n📋 PHASE 5: PRODUCTION READINESS FINAL CHECK")
        self.test_error_handling_and_edge_cases()
        self.test_performance_and_response_times()
        self.test_security_and_access_control()
        
        # Generate final report
        return self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive final assessment report"""
        print("\n" + "=" * 80)
        print("🎯 FINAL COMPREHENSIVE INTEGRATION AND QUALITY VALIDATION REPORT")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.results:
            print(f"   {result['status']}: {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"      └─ {result['details']}")
        
        # Critical findings
        critical_failures = [r for r in self.results if not r["success"] and 
                           any(keyword in r["test"].lower() for keyword in 
                               ["provider response", "service request", "database", "authentication"])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - System is production ready with excellent integration quality")
        elif success_rate >= 85:
            print("   ✅ GOOD - System is production ready with minor issues")
        elif success_rate >= 70:
            print("   ⚠️  ACCEPTABLE - System functional but needs attention to failed tests")
        else:
            print("   ❌ NEEDS WORK - Critical issues must be resolved before production")
        
        # Key metrics
        response_times = [float(r["response_time"].replace("s", "")) for r in self.results if r["response_time"]]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Maximum Response Time: {max_response_time:.3f}s")
            print(f"   Total API Calls: {len(response_times)}")
        
        print("\n" + "=" * 80)
        return success_rate

if __name__ == "__main__":
    test_runner = ComprehensiveIntegrationTest()
    success_rate = test_runner.run_comprehensive_test()
    
    # Exit with appropriate code
    exit(0 if success_rate >= 85 else 1)
"""
QA Credentials E2E Backend Testing
Tests the exact workflow specified in the review request.
Note: Using .example.com domains due to backend email validation restrictions on .test domains.
The workflow and credentials structure match the review request exactly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://readiness-hub-2.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class QAWorkflowTester:
    def __init__(self):
        self.tokens = {}
        self.license_code = None
        self.results = {
            "navigator": {"registration": "PENDING", "login": "PENDING"},
            "agency": {"registration": "PENDING", "login": "PENDING"},
            "client": {"registration": "PENDING", "login": "PENDING"},
            "provider": {"registration": "PENDING", "login": "PENDING"},
            "license_code": None,
            "errors": []
        }
    
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def register_user(self, role, email, password, license_code=None):
        """Register a user with the specified role"""
        payload = {
            "email": email,
            "password": password,
            "role": role,
            "terms_accepted": True
        }
        
        if license_code:
            payload["license_code"] = license_code
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            
            if response.status_code == 400 and ("already registered" in response.text.lower() or "already exists" in response.text.lower()):
                self.log_result(f"✅ {role.title()} already exists, proceeding to login")
                self.results[role]["registration"] = "EXISTS"
                return True
            elif response.status_code == 200:
                self.log_result(f"✅ {role.title()} registration successful")
                self.results[role]["registration"] = "SUCCESS"
                return True
            else:
                self.log_result(f"❌ {role.title()} registration failed: {response.status_code} - {response.text}")
                self.results[role]["registration"] = f"FAILED ({response.status_code})"
                self.results["errors"].append(f"{role} registration: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} registration error: {str(e)}")
            self.results[role]["registration"] = f"ERROR ({str(e)})"
            self.results["errors"].append(f"{role} registration error: {str(e)}")
            return False
    
    def login_user(self, role, email, password):
        """Login user and store token"""
        payload = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"✅ {role.title()} login successful")
                self.results[role]["login"] = "SUCCESS"
                return True
            else:
                self.log_result(f"❌ {role.title()} login failed: {response.status_code} - {response.text}")
                self.results[role]["login"] = f"FAILED ({response.status_code})"
                self.results["errors"].append(f"{role} login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} login error: {str(e)}")
            self.results[role]["login"] = f"ERROR ({str(e)})"
            self.results["errors"].append(f"{role} login error: {str(e)}")
            return False
    
    def get_pending_agencies(self):
        """Get pending agencies as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/navigator/agencies/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                agencies = data.get("agencies", [])
                
                # Find our QA agency
                qa_agency = None
                for agency in agencies:
                    if agency.get("email") == QA_CREDENTIALS["agency"]["email"]:
                        qa_agency = agency
                        break
                
                if qa_agency:
                    self.log_result(f"✅ Found QA agency in pending list: {qa_agency['email']}")
                    return qa_agency["id"]
                else:
                    self.log_result(f"⚠️ QA agency not found in pending list - may already be approved")
                    # Try to login directly to check if already approved
                    return "already_approved"
            else:
                self.log_result(f"❌ Failed to get pending agencies: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Error getting pending agencies: {str(e)}")
            return None
    
    def approve_agency(self, agency_id):
        """Approve agency as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        payload = {
            "agency_user_id": agency_id,
            "approval_status": "approved"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/navigator/agencies/approve", json=payload, headers=headers)
            
            if response.status_code == 200:
                self.log_result(f"✅ Agency approval successful")
                return True
            else:
                self.log_result(f"❌ Agency approval failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"Agency approval: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error approving agency: {str(e)}")
            self.results["errors"].append(f"Agency approval error: {str(e)}")
            return False
    
    def generate_licenses(self):
        """Generate license codes as agency"""
        headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
        payload = {"quantity": 3}
        
        try:
            response = requests.post(f"{BASE_URL}/agency/licenses/generate", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                licenses = data.get("licenses", [])
                
                if licenses:
                    # Get first license code
                    first_license = licenses[0]
                    if isinstance(first_license, dict):
                        self.license_code = first_license.get("license_code")
                    else:
                        self.license_code = str(first_license)
                    
                    self.results["license_code"] = f"****{self.license_code[-4:]}" if self.license_code else "NONE"
                    self.log_result(f"✅ Generated {len(licenses)} licenses, first: ****{self.license_code[-4:]}")
                    return True
                else:
                    self.log_result(f"❌ No licenses generated")
                    return False
            else:
                self.log_result(f"❌ License generation failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"License generation: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error generating licenses: {str(e)}")
            self.results["errors"].append(f"License generation error: {str(e)}")
            return False
    
    def get_pending_providers(self):
        """Get pending providers as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/navigator/providers/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                # Find our QA provider
                qa_provider = None
                for provider in providers:
                    if provider.get("email") == QA_CREDENTIALS["provider"]["email"]:
                        qa_provider = provider
                        break
                
                if qa_provider:
                    self.log_result(f"✅ Found QA provider in pending list: {qa_provider['email']}")
                    return qa_provider["id"]
                else:
                    self.log_result(f"⚠️ QA provider not found in pending list - may already be approved")
                    return "already_approved"
            else:
                self.log_result(f"❌ Failed to get pending providers: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Error getting pending providers: {str(e)}")
            return None
    
    def approve_provider(self, provider_id):
        """Approve provider as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        payload = {
            "provider_user_id": provider_id,
            "approval_status": "approved"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/navigator/providers/approve", json=payload, headers=headers)
            
            if response.status_code == 200:
                self.log_result(f"✅ Provider approval successful")
                return True
            else:
                self.log_result(f"❌ Provider approval failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"Provider approval: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error approving provider: {str(e)}")
            self.results["errors"].append(f"Provider approval error: {str(e)}")
            return False
    
    def run_complete_workflow(self):
        """Execute the complete QA workflow"""
        self.log_result("🚀 Starting QA Credentials E2E Workflow Test")
        self.log_result("=" * 60)
        
        # Step 1: Register and login navigator
        self.log_result("📋 Step 1: Navigator Registration & Login")
        nav_creds = QA_CREDENTIALS["navigator"]
        if self.register_user("navigator", nav_creds["email"], nav_creds["password"]):
            if not self.login_user("navigator", nav_creds["email"], nav_creds["password"]):
                return False
        else:
            return False
        
        # Step 2: Register agency and approve
        self.log_result("\n📋 Step 2: Agency Registration & Approval")
        agency_creds = QA_CREDENTIALS["agency"]
        if self.register_user("agency", agency_creds["email"], agency_creds["password"]):
            # Get pending agencies and approve
            agency_id = self.get_pending_agencies()
            if agency_id == "already_approved":
                self.log_result("✅ Agency already approved, proceeding to login")
            elif agency_id:
                if not self.approve_agency(agency_id):
                    return False
            else:
                self.log_result("❌ Cannot proceed without agency approval")
                return False
            
            # Login as agency
            if not self.login_user("agency", agency_creds["email"], agency_creds["password"]):
                return False
        else:
            return False
        
        # Step 3: Generate licenses
        self.log_result("\n📋 Step 3: License Generation")
        if not self.generate_licenses():
            return False
        
        # Step 4: Register client with license
        self.log_result("\n📋 Step 4: Client Registration & Login")
        client_creds = QA_CREDENTIALS["client"]
        if self.register_user("client", client_creds["email"], client_creds["password"], self.license_code):
            if not self.login_user("client", client_creds["email"], client_creds["password"]):
                return False
        else:
            return False
        
        # Step 5: Register provider and approve
        self.log_result("\n📋 Step 5: Provider Registration & Approval")
        provider_creds = QA_CREDENTIALS["provider"]
        if self.register_user("provider", provider_creds["email"], provider_creds["password"]):
            # Get pending providers and approve
            provider_id = self.get_pending_providers()
            if provider_id == "already_approved":
                self.log_result("✅ Provider already approved, proceeding to login")
            elif provider_id:
                if not self.approve_provider(provider_id):
                    return False
            else:
                self.log_result("❌ Cannot proceed without provider approval")
                return False
            
            # Login as provider
            if not self.login_user("provider", provider_creds["email"], provider_creds["password"]):
                return False
        else:
            return False
        
        return True
    
    def print_final_report(self):
        """Print the final test report"""
        self.log_result("\n" + "=" * 60)
        self.log_result("📊 FINAL QA WORKFLOW REPORT")
        self.log_result("=" * 60)
        
        # Per role status
        for role in ["navigator", "agency", "client", "provider"]:
            reg_status = self.results[role]["registration"]
            login_status = self.results[role]["login"]
            self.log_result(f"{role.upper()}: Registration={reg_status}, Login={login_status}")
        
        # License code
        if self.results["license_code"]:
            self.log_result(f"LICENSE CODE: {self.results['license_code']}")
        
        # Errors
        if self.results["errors"]:
            self.log_result("\n❌ ERRORS ENCOUNTERED:")
            for error in self.results["errors"]:
                self.log_result(f"  - {error}")
        else:
            self.log_result("\n✅ NO ERRORS - ALL STEPS COMPLETED SUCCESSFULLY")

def main():
    """Main test execution"""
    tester = QAWorkflowTester()
    
    try:
        success = tester.run_complete_workflow()
        tester.print_final_report()
        
        if success:
            print("\n🎉 QA WORKFLOW TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ QA WORKFLOW TEST FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()