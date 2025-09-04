#!/usr/bin/env python3
"""
Tier-Based Assessment System Backend Testing
Focus: Identify specific endpoint failures and error responses
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class TierBasedTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session_id = None
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result with detailed information"""
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
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = requests.post(f"{BACKEND_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"{role.title()} Authentication", True, 
                              f"Successfully authenticated {creds['email']}")
                return True
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result(f"{role.title()} Authentication", False, 
                              f"Status: {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result(f"{role.title()} Authentication", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role):
        """Get authorization headers for role"""
        if role not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[role]}"}

    def test_tier_based_schema(self):
        """Test GET /api/assessment/schema/tier-based"""
        try:
            headers = self.get_headers("client")
            response = requests.get(f"{BACKEND_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected structure
                if "areas" in data and isinstance(data["areas"], list):
                    area_count = len(data["areas"])
                    self.log_result("Tier-Based Schema Retrieval", True, 
                                  f"Retrieved schema with {area_count} areas")
                    return data
                else:
                    self.log_result("Tier-Based Schema Retrieval", False, 
                                  "Invalid schema structure", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier-Based Schema Retrieval", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier-Based Schema Retrieval", False, f"Exception: {str(e)}")
            return None

    def test_tier_session_creation_json(self):
        """Test POST /api/assessment/tier-session with JSON content-type"""
        try:
            headers = self.get_headers("client")
            headers["Content-Type"] = "application/json"
            
            payload = {
                "area_id": "area1",
                "tier_level": 1
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    self.session_id = data["session_id"]
                    self.log_result("Tier Session Creation (JSON)", True, 
                                  f"Created session: {self.session_id}")
                    return data
                else:
                    self.log_result("Tier Session Creation (JSON)", False, 
                                  "No session_id in response", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier Session Creation (JSON)", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier Session Creation (JSON)", False, f"Exception: {str(e)}")
            return None

    def test_tier_session_creation_form_data(self):
        """Test POST /api/assessment/tier-session with form data"""
        try:
            headers = self.get_headers("client")
            # Don't set Content-Type, let requests handle it for form data
            
            payload = {
                "area_id": "area2",
                "tier_level": "2"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   data=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    session_id = data["session_id"]
                    self.log_result("Tier Session Creation (Form Data)", True, 
                                  f"Created session: {session_id}")
                    return data
                else:
                    self.log_result("Tier Session Creation (Form Data)", False, 
                                  "No session_id in response", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier Session Creation (Form Data)", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier Session Creation (Form Data)", False, f"Exception: {str(e)}")
            return None

    def test_tier_session_response_submission(self):
        """Test POST /api/assessment/tier-session/{session_id}/response"""
        if not self.session_id:
            self.log_result("Tier Session Response Submission", False, 
                          "No session_id available from previous test")
            return None
            
        try:
            headers = self.get_headers("client")
            headers["Content-Type"] = "application/json"
            
            payload = {
                "statement_id": "area1_tier1_stmt1",
                "response": "yes",
                "evidence_provided": True,
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session/{self.session_id}/response", 
                                   json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Tier Session Response Submission", True, 
                              "Successfully submitted tier response")
                return data
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier Session Response Submission", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier Session Response Submission", False, f"Exception: {str(e)}")
            return None

    def test_client_tier_access(self):
        """Test GET /api/client/tier-access"""
        try:
            headers = self.get_headers("client")
            response = requests.get(f"{BACKEND_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "tier_access" in data or "areas" in data:
                    self.log_result("Client Tier Access", True, 
                                  "Successfully retrieved tier access information")
                    return data
                else:
                    self.log_result("Client Tier Access", False, 
                                  "Invalid tier access structure", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Client Tier Access", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Client Tier Access", False, f"Exception: {str(e)}")
            return None

    def test_agency_tier_configuration(self):
        """Test GET /api/agency/tier-configuration"""
        try:
            headers = self.get_headers("agency")
            response = requests.get(f"{BACKEND_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Agency Tier Configuration", True, 
                              "Successfully retrieved agency tier configuration")
                return data
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Agency Tier Configuration", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Agency Tier Configuration", False, f"Exception: {str(e)}")
            return None

    def test_content_type_variations(self):
        """Test different content-type scenarios"""
        print("=== CONTENT-TYPE VARIATION TESTING ===")
        
        # Test 1: JSON with explicit content-type
        try:
            headers = self.get_headers("client")
            headers["Content-Type"] = "application/json"
            
            payload = {"area_id": "area3", "tier_level": 1}
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   json=payload, headers=headers)
            
            self.log_result("Content-Type: application/json", 
                          response.status_code == 200,
                          f"Status: {response.status_code}",
                          response.json() if response.content else None)
        except Exception as e:
            self.log_result("Content-Type: application/json", False, f"Exception: {str(e)}")

        # Test 2: Form data with explicit content-type
        try:
            headers = self.get_headers("client")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            
            payload = "area_id=area4&tier_level=2"
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   data=payload, headers=headers)
            
            self.log_result("Content-Type: application/x-www-form-urlencoded", 
                          response.status_code == 200,
                          f"Status: {response.status_code}",
                          response.json() if response.content else None)
        except Exception as e:
            self.log_result("Content-Type: application/x-www-form-urlencoded", False, f"Exception: {str(e)}")

        # Test 3: Multipart form data
        try:
            headers = self.get_headers("client")
            # Don't set Content-Type for multipart, let requests handle it
            
            files = {'area_id': (None, 'area5'), 'tier_level': (None, '3')}
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   files=files, headers=headers)
            
            self.log_result("Content-Type: multipart/form-data", 
                          response.status_code == 200,
                          f"Status: {response.status_code}",
                          response.json() if response.content else None)
        except Exception as e:
            self.log_result("Content-Type: multipart/form-data", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run all tier-based assessment tests"""
        print("🎯 TIER-BASED ASSESSMENT SYSTEM TESTING")
        print("=" * 50)
        
        # Step 1: Authentication
        print("=== AUTHENTICATION ===")
        client_auth = self.authenticate_user("client")
        agency_auth = self.authenticate_user("agency")
        
        if not client_auth:
            print("❌ Cannot proceed without client authentication")
            return
            
        # Step 2: Core Tier-Based Endpoints
        print("=== CORE TIER-BASED ENDPOINTS ===")
        schema_data = self.test_tier_based_schema()
        
        # Test both JSON and form data for session creation
        json_session = self.test_tier_session_creation_json()
        form_session = self.test_tier_session_creation_form_data()
        
        # Test response submission if we have a session
        self.test_tier_session_response_submission()
        
        # Test client tier access
        tier_access = self.test_client_tier_access()
        
        # Test agency configuration (if agency auth worked)
        if agency_auth:
            self.test_agency_tier_configuration()
        
        # Step 3: Content-Type Variations
        self.test_content_type_variations()
        
        # Step 4: Summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 TIER-BASED ASSESSMENT TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
                    if "response_data" in result and result["response_data"]:
                        error_info = result["response_data"]
                        if isinstance(error_info, dict):
                            if "detail" in error_info:
                                print(f"    Error: {error_info['detail']}")
                            elif "message" in error_info:
                                print(f"    Error: {error_info['message']}")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Analyze patterns in failures
        content_type_failures = [r for r in self.test_results if not r["success"] and "Content-Type" in r["test"]]
        if content_type_failures:
            print(f"  • Content-Type Issues: {len(content_type_failures)} failures detected")
        
        auth_failures = [r for r in self.test_results if not r["success"] and "Authentication" in r["test"]]
        if auth_failures:
            print(f"  • Authentication Issues: {len(auth_failures)} failures detected")
        
        endpoint_failures = [r for r in self.test_results if not r["success"] and any(endpoint in r["test"] for endpoint in ["Schema", "Session", "Access", "Configuration"])]
        if endpoint_failures:
            print(f"  • Endpoint Issues: {len(endpoint_failures)} failures detected")
            
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = TierBasedTester()
    tester.run_comprehensive_test()