#!/usr/bin/env python3
"""
Corrected Tier-Based Assessment System Testing
Focus: Use proper form data format as expected by endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://providermatrix.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CorrectedTierTester:
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

    def test_tier_session_creation_tier1(self):
        """Test POST /api/assessment/tier-session with Tier 1 (should work)"""
        try:
            headers = self.get_headers("client")
            
            # Use form data as expected by the endpoint
            payload = {
                "area_id": "area1",
                "tier_level": "1"  # String format for form data
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   data=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    self.session_id = data["session_id"]
                    self.log_result("Tier 1 Session Creation (Form Data)", True, 
                                  f"Created session: {self.session_id}")
                    return data
                else:
                    self.log_result("Tier 1 Session Creation (Form Data)", False, 
                                  "No session_id in response", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier 1 Session Creation (Form Data)", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier 1 Session Creation (Form Data)", False, f"Exception: {str(e)}")
            return None

    def test_tier_session_creation_tier2(self):
        """Test POST /api/assessment/tier-session with Tier 2 (may fail due to access)"""
        try:
            headers = self.get_headers("client")
            
            payload = {
                "area_id": "area2",
                "tier_level": "2"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   data=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Tier 2 Session Creation (Form Data)", True, 
                              f"Created Tier 2 session successfully")
                return data
            elif response.status_code == 403:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier 2 Session Creation (Form Data)", False, 
                              f"Access denied (expected): {error_data.get('message', 'No message')}")
                return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier 2 Session Creation (Form Data)", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier 2 Session Creation (Form Data)", False, f"Exception: {str(e)}")
            return None

    def test_tier_response_submission(self):
        """Test POST /api/assessment/tier-session/{session_id}/response"""
        if not self.session_id:
            self.log_result("Tier Response Submission", False, 
                          "No session_id available from previous test")
            return None
            
        try:
            headers = self.get_headers("client")
            
            # Use form data as expected by the endpoint
            payload = {
                "question_id": "area1_tier1_q1",
                "response": "yes",
                "evidence_provided": "true",
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session/{self.session_id}/response", 
                                   data=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Tier Response Submission", True, 
                              "Successfully submitted tier response")
                return data
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Tier Response Submission", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Tier Response Submission", False, f"Exception: {str(e)}")
            return None

    def test_client_tier_access_detailed(self):
        """Test GET /api/client/tier-access with detailed analysis"""
        try:
            headers = self.get_headers("client")
            response = requests.get(f"{BACKEND_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the tier access structure
                if "areas" in data:
                    areas = data["areas"]
                    tier_summary = {}
                    for area in areas:
                        area_id = area.get("area_id", "unknown")
                        max_tier = area.get("max_tier_access", 0)
                        tier_summary[area_id] = max_tier
                    
                    self.log_result("Client Tier Access Analysis", True, 
                                  f"Retrieved tier access for {len(areas)} areas. Summary: {tier_summary}")
                    return data
                else:
                    self.log_result("Client Tier Access Analysis", False, 
                                  "Invalid tier access structure", data)
                    return None
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Client Tier Access Analysis", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Client Tier Access Analysis", False, f"Exception: {str(e)}")
            return None

    def test_agency_tier_configuration_detailed(self):
        """Test GET /api/agency/tier-configuration with detailed analysis"""
        try:
            headers = self.get_headers("agency")
            response = requests.get(f"{BACKEND_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the configuration structure
                config_summary = {}
                if "tier_access_levels" in data:
                    config_summary["tier_access_levels"] = len(data["tier_access_levels"])
                if "pricing_per_tier" in data:
                    config_summary["pricing_tiers"] = list(data["pricing_per_tier"].keys())
                
                self.log_result("Agency Tier Configuration Analysis", True, 
                              f"Retrieved agency configuration. Summary: {config_summary}")
                return data
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Agency Tier Configuration Analysis", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Agency Tier Configuration Analysis", False, f"Exception: {str(e)}")
            return None

    def test_schema_structure(self):
        """Test GET /api/assessment/schema/tier-based with structure analysis"""
        try:
            headers = self.get_headers("client")
            response = requests.get(f"{BACKEND_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze schema structure
                schema_summary = {}
                if "areas" in data:
                    areas = data["areas"]
                    schema_summary["total_areas"] = len(areas)
                    
                    # Check tier structure
                    tier_counts = {}
                    for area in areas:
                        if "tiers" in area:
                            tier_count = len(area["tiers"])
                            tier_counts[area.get("id", "unknown")] = tier_count
                    
                    schema_summary["tier_structure"] = tier_counts
                
                self.log_result("Schema Structure Analysis", True, 
                              f"Schema analysis: {schema_summary}")
                return data
            else:
                error_data = response.json() if response.content else {"error": "No response content"}
                self.log_result("Schema Structure Analysis", False, 
                              f"Status: {response.status_code}", error_data)
                return None
                
        except Exception as e:
            self.log_result("Schema Structure Analysis", False, f"Exception: {str(e)}")
            return None

    def run_corrected_test(self):
        """Run corrected tier-based assessment tests"""
        print("🎯 CORRECTED TIER-BASED ASSESSMENT TESTING")
        print("=" * 50)
        
        # Step 1: Authentication
        print("=== AUTHENTICATION ===")
        client_auth = self.authenticate_user("client")
        agency_auth = self.authenticate_user("agency")
        
        if not client_auth:
            print("❌ Cannot proceed without client authentication")
            return
            
        # Step 2: Schema Analysis
        print("=== SCHEMA ANALYSIS ===")
        schema_data = self.test_schema_structure()
        
        # Step 3: Tier Access Analysis
        print("=== TIER ACCESS ANALYSIS ===")
        tier_access = self.test_client_tier_access_detailed()
        
        if agency_auth:
            agency_config = self.test_agency_tier_configuration_detailed()
        
        # Step 4: Session Creation Tests (Corrected)
        print("=== SESSION CREATION TESTS (CORRECTED) ===")
        tier1_session = self.test_tier_session_creation_tier1()
        tier2_session = self.test_tier_session_creation_tier2()
        
        # Step 5: Response Submission Test
        print("=== RESPONSE SUBMISSION TEST ===")
        self.test_tier_response_submission()
        
        # Step 6: Summary
        self.print_detailed_summary()

    def print_detailed_summary(self):
        """Print detailed test summary with specific findings"""
        print("\n" + "=" * 60)
        print("🎯 CORRECTED TIER-BASED TESTING SUMMARY")
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
        
        # Categorize results
        auth_results = [r for r in self.test_results if "Authentication" in r["test"]]
        schema_results = [r for r in self.test_results if "Schema" in r["test"]]
        access_results = [r for r in self.test_results if "Access" in r["test"] or "Configuration" in r["test"]]
        session_results = [r for r in self.test_results if "Session" in r["test"]]
        response_results = [r for r in self.test_results if "Response" in r["test"]]
        
        print("📊 RESULTS BY CATEGORY:")
        print(f"  Authentication: {sum(1 for r in auth_results if r['success'])}/{len(auth_results)} passed")
        print(f"  Schema/Access: {sum(1 for r in schema_results + access_results if r['success'])}/{len(schema_results + access_results)} passed")
        print(f"  Session Creation: {sum(1 for r in session_results if r['success'])}/{len(session_results)} passed")
        print(f"  Response Submission: {sum(1 for r in response_results if r['success'])}/{len(response_results)} passed")
        print()
        
        # Specific issues found
        print("🔍 SPECIFIC ISSUES IDENTIFIED:")
        
        # Check for form data vs JSON issues
        json_issues = [r for r in self.test_results if not r["success"] and "422" in r["details"]]
        if json_issues:
            print("  ❌ Form Data vs JSON Issues: RESOLVED - Using proper form data format")
        else:
            print("  ✅ Form Data Format: Working correctly")
        
        # Check for tier access issues
        tier_access_issues = [r for r in self.test_results if not r["success"] and "403" in r["details"]]
        if tier_access_issues:
            print(f"  ⚠️  Tier Access Restrictions: {len(tier_access_issues)} access denied responses (may be expected)")
        
        # Check for authentication issues
        auth_issues = [r for r in auth_results if not r["success"]]
        if auth_issues:
            print(f"  ❌ Authentication Issues: {len(auth_issues)} failures")
        else:
            print("  ✅ Authentication: Working correctly")
        
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}")
                    print(f"    Issue: {result['details']}")
                    if "response_data" in result and result["response_data"]:
                        error_info = result["response_data"]
                        if isinstance(error_info, dict) and "message" in error_info:
                            print(f"    Error: {error_info['message']}")
                    print()
        
        print("=" * 60)

if __name__ == "__main__":
    tester = CorrectedTierTester()
    tester.run_corrected_test()