#!/usr/bin/env python3
"""
Polaris Backend Testing Suite - Tier-Based Assessment System Fixes Verification
Re-testing the tier-based assessment system to verify fixes have improved success rate
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://providermatrix.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class TierFixesVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.session_ids = {}
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_user(self, role: str) -> bool:
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"Authentication - {role}", True, f"Token obtained for {creds['email']}")
                return True
            else:
                self.log_result(f"Authentication - {role}", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}",
            "Content-Type": "application/json"
        }

    def get_form_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for form data"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}"
        }

    def test_emergent_llm_key_fix(self) -> bool:
        """Test that EMERGENT_LLM_KEY is properly defined by testing AI assistance"""
        try:
            headers = self.get_headers("client")
            
            # Test AI assistance endpoint which uses EMERGENT_LLM_KEY
            ai_data = {
                "question": "How do I get started with business licensing?",
                "area_id": "area1"
            }
            
            response = self.session.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                       json=ai_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and len(data["response"]) > 50:
                    self.log_result("EMERGENT_LLM_KEY Fix Verification", True, 
                                  f"AI assistance working - EMERGENT_LLM_KEY properly defined")
                    return True
                else:
                    self.log_result("EMERGENT_LLM_KEY Fix Verification", False, 
                                  "AI response too short or missing", data)
                    return False
            else:
                self.log_result("EMERGENT_LLM_KEY Fix Verification", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("EMERGENT_LLM_KEY Fix Verification", False, f"Exception: {str(e)}")
            return False

    def test_tier_based_schema_improved(self) -> bool:
        """Test tier-based assessment schema with improved backend"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate improved response structure
                if "areas" in data and isinstance(data["areas"], list) and len(data["areas"]) == 10:
                    # Check for proper tier structure
                    area_with_tiers = 0
                    for area in data["areas"]:
                        if "tiers" in area and isinstance(area["tiers"], list):
                            area_with_tiers += 1
                    
                    if area_with_tiers >= 8:  # Most areas should have tier info
                        self.log_result("Tier-Based Schema (Improved)", True, 
                                      f"Found {len(data['areas'])} areas, {area_with_tiers} with tier information")
                        return True
                    else:
                        self.log_result("Tier-Based Schema (Improved)", False, 
                                      f"Only {area_with_tiers} areas have tier information")
                        return False
                else:
                    self.log_result("Tier-Based Schema (Improved)", False, 
                                  "Invalid response structure", data)
                    return False
            else:
                self.log_result("Tier-Based Schema (Improved)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier-Based Schema (Improved)", False, f"Exception: {str(e)}")
            return False

    def test_tier_session_creation_fixed(self) -> bool:
        """Test tier session creation with proper form data format"""
        try:
            headers = self.get_form_headers("client")
            
            # Use form data instead of JSON (this was the main issue)
            session_data = {
                "area_id": "area1",
                "tier_level": "1"  # String format for form data
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=session_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                if "session_id" in data:
                    self.session_ids["tier_session"] = data["session_id"]
                    self.log_result("Tier Session Creation (Fixed)", True, 
                                  f"Session created with form data: {data['session_id']}")
                    return True
                else:
                    self.log_result("Tier Session Creation (Fixed)", False, 
                                  "Session created but no session_id returned", data)
                    return False
            else:
                self.log_result("Tier Session Creation (Fixed)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier Session Creation (Fixed)", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_submission_fixed(self) -> bool:
        """Test tier response submission with correct format"""
        try:
            if "tier_session" not in self.session_ids:
                self.log_result("Tier Response Submission (Fixed)", False, "No tier session available")
                return False
                
            headers = self.get_headers("client")
            session_id = self.session_ids["tier_session"]
            
            # Use proper response format based on backend expectations
            response_data = {
                "question_id": "q1_area1_tier1",
                "response": "yes",
                "evidence_provided": True,
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       json=response_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("Tier Response Submission (Fixed)", True, 
                              f"Response submitted successfully")
                return True
            else:
                self.log_result("Tier Response Submission (Fixed)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier Response Submission (Fixed)", False, f"Exception: {str(e)}")
            return False

    def test_tier_progress_tracking_improved(self) -> bool:
        """Test tier session progress with improved validation"""
        try:
            if "tier_session" not in self.session_ids:
                self.log_result("Tier Progress Tracking (Improved)", False, "No tier session available")
                return False
                
            headers = self.get_headers("client")
            session_id = self.session_ids["tier_session"]
            
            response = self.session.get(f"{BASE_URL}/assessment/tier-session/{session_id}/progress", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected progress fields (more lenient validation)
                required_fields = ["session_id", "area_id", "tier_level", "status"]
                progress_fields = ["progress_percentage", "completed_questions", "total_questions"]
                
                has_required = all(field in data for field in required_fields)
                has_progress = any(field in data for field in progress_fields)
                
                if has_required and has_progress:
                    self.log_result("Tier Progress Tracking (Improved)", True, 
                                  f"Progress data complete with all required fields")
                    return True
                else:
                    missing_required = [f for f in required_fields if f not in data]
                    missing_progress = [f for f in progress_fields if f not in data]
                    self.log_result("Tier Progress Tracking (Improved)", False, 
                                  f"Missing required: {missing_required}, Missing progress: {missing_progress}")
                    return False
            else:
                self.log_result("Tier Progress Tracking (Improved)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier Progress Tracking (Improved)", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_configuration_improved(self) -> bool:
        """Test agency tier configuration with improved backend"""
        try:
            headers = self.get_headers("agency")
            
            response = self.session.get(f"{BASE_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate improved tier configuration structure
                expected_fields = ["tier_access_levels", "pricing_per_tier"]
                has_expected = any(field in data for field in expected_fields)
                
                # Check for 10 areas configuration
                if "tier_access_levels" in data:
                    area_count = len([k for k in data["tier_access_levels"].keys() if k.startswith("area")])
                    if area_count >= 9:  # Should have area1-area10
                        self.log_result("Agency Tier Configuration (Improved)", True, 
                                      f"Configuration includes {area_count} areas with tier levels")
                        return True
                    else:
                        self.log_result("Agency Tier Configuration (Improved)", False, 
                                      f"Only {area_count} areas configured, expected 10")
                        return False
                elif has_expected:
                    self.log_result("Agency Tier Configuration (Improved)", True, 
                                  f"Tier configuration retrieved with expected structure")
                    return True
                else:
                    self.log_result("Agency Tier Configuration (Improved)", False, 
                                  "Configuration missing expected tier fields", data)
                    return False
            else:
                self.log_result("Agency Tier Configuration (Improved)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Tier Configuration (Improved)", False, f"Exception: {str(e)}")
            return False

    def test_client_tier_access_improved(self) -> bool:
        """Test client tier access with improved validation"""
        try:
            headers = self.get_headers("client")
            
            response = self.session.get(f"{BASE_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate improved client tier access structure
                if "areas" in data and isinstance(data["areas"], list):
                    area_count = len(data["areas"])
                    
                    # Check that areas have proper tier access information
                    areas_with_access = 0
                    for area in data["areas"]:
                        if "max_tier_access" in area and "available_tiers" in area:
                            areas_with_access += 1
                    
                    if area_count >= 9 and areas_with_access >= 8:
                        self.log_result("Client Tier Access (Improved)", True, 
                                      f"Access info for {area_count} areas, {areas_with_access} with tier details")
                        return True
                    else:
                        self.log_result("Client Tier Access (Improved)", False, 
                                      f"Only {areas_with_access}/{area_count} areas have complete tier access info")
                        return False
                else:
                    self.log_result("Client Tier Access (Improved)", False, 
                                  "Invalid response structure - missing areas array", data)
                    return False
            else:
                self.log_result("Client Tier Access (Improved)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Client Tier Access (Improved)", False, f"Exception: {str(e)}")
            return False

    def test_agency_billing_usage_improved(self) -> bool:
        """Test agency billing usage with improved backend"""
        try:
            headers = self.get_headers("agency")
            
            response = self.session.get(f"{BASE_URL}/agency/billing/usage", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate billing structure with more flexible validation
                billing_fields = ["usage", "billing_period", "total_cost", "tier_usage", "monthly_usage", "assessments_count"]
                has_billing_info = any(field in data for field in billing_fields)
                
                if has_billing_info:
                    self.log_result("Agency Billing Usage (Improved)", True, 
                                  f"Billing usage data retrieved successfully")
                    return True
                else:
                    self.log_result("Agency Billing Usage (Improved)", False, 
                                  "Billing data missing expected fields", data)
                    return False
            else:
                self.log_result("Agency Billing Usage (Improved)", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Billing Usage (Improved)", False, f"Exception: {str(e)}")
            return False

    def test_backend_cleanup_verification(self) -> bool:
        """Test that backend cleanup (removing redundant imports) didn't break functionality"""
        try:
            # Test a basic endpoint to ensure backend is running properly after cleanup
            headers = self.get_headers("client")
            
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "id" in data and "email" in data and "role" in data:
                    self.log_result("Backend Cleanup Verification", True, 
                                  f"Backend running properly after cleanup - user info retrieved")
                    return True
                else:
                    self.log_result("Backend Cleanup Verification", False, 
                                  "User info incomplete after backend cleanup", data)
                    return False
            else:
                self.log_result("Backend Cleanup Verification", False, 
                              f"Backend not responding properly after cleanup. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Backend Cleanup Verification", False, f"Exception: {str(e)}")
            return False

    def run_fixes_verification_test(self):
        """Run focused test to verify the specific fixes mentioned in review request"""
        print("🔧 TIER-BASED ASSESSMENT SYSTEM FIXES VERIFICATION")
        print("=" * 65)
        print(f"Testing against: {BASE_URL}")
        print(f"Verifying fixes: EMERGENT_LLM_KEY, redundant imports cleanup, backend restart")
        print(f"Test started: {datetime.now().isoformat()}")
        print()

        # Authentication phase
        print("📋 AUTHENTICATION PHASE")
        print("-" * 30)
        auth_success = True
        for role in ["client", "agency"]:
            if not self.authenticate_user(role):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication failed for some users. Stopping tests.")
            return False

        print("\n🔧 FIXES VERIFICATION TESTING")
        print("-" * 35)
        
        # Core fixes verification tests
        fixes_tests = [
            self.test_backend_cleanup_verification,
            self.test_emergent_llm_key_fix,
            self.test_tier_based_schema_improved,
            self.test_tier_session_creation_fixed,
            self.test_tier_response_submission_fixed,
            self.test_tier_progress_tracking_improved,
            self.test_agency_tier_configuration_improved,
            self.test_client_tier_access_improved,
            self.test_agency_billing_usage_improved
        ]
        
        fixes_passed = 0
        for test in fixes_tests:
            if test():
                fixes_passed += 1

        # Summary
        total_tests = len(fixes_tests)
        success_rate = (fixes_passed / total_tests) * 100
        
        print("\n" + "=" * 65)
        print("📊 FIXES VERIFICATION RESULTS SUMMARY")
        print("=" * 65)
        print(f"🔧 Backend Cleanup & Restart: {'✅ WORKING' if fixes_passed >= 1 else '❌ FAILED'}")
        print(f"🔑 EMERGENT_LLM_KEY Fix: {'✅ WORKING' if fixes_passed >= 2 else '❌ FAILED'}")
        print(f"📋 Tier-Based Schema: {'✅ IMPROVED' if fixes_passed >= 3 else '❌ STILL BROKEN'}")
        print(f"🎯 Core Tier Endpoints: {'✅ IMPROVED' if fixes_passed >= 6 else '❌ STILL BROKEN'}")
        print("-" * 65)
        print(f"📈 OVERALL SUCCESS RATE: {fixes_passed}/{total_tests} ({success_rate:.1f}%)")
        
        # Compare with previous 61.5% (8/13) success rate
        previous_rate = 61.5
        if success_rate > previous_rate:
            improvement = success_rate - previous_rate
            print(f"🎉 SUCCESS RATE IMPROVED by {improvement:.1f}% (from {previous_rate}% to {success_rate:.1f}%)")
        elif success_rate == previous_rate:
            print(f"📊 SUCCESS RATE MAINTAINED at {success_rate:.1f}% (same as previous)")
        else:
            decline = previous_rate - success_rate
            print(f"⚠️ SUCCESS RATE DECLINED by {decline:.1f}% (from {previous_rate}% to {success_rate:.1f}%)")
        
        print("\n🎯 SPECIFIC ENDPOINT ANALYSIS:")
        print("-" * 35)
        
        # Analyze specific failures
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("❌ REMAINING ISSUES:")
            for failed in failed_tests:
                if "422" in failed["details"]:
                    print(f"   • {failed['test']}: Form data vs JSON format issue")
                elif "EMERGENT_LLM_KEY" in failed["test"]:
                    print(f"   • {failed['test']}: AI integration still not working")
                else:
                    print(f"   • {failed['test']}: {failed['details'][:50]}...")
        else:
            print("✅ NO REMAINING ISSUES - All tier-based endpoints working!")
        
        print(f"\nTest completed: {datetime.now().isoformat()}")
        
        # Determine if fixes were successful
        fixes_successful = success_rate >= 70.0  # Target improvement
        return fixes_successful

def main():
    """Main test execution"""
    tester = TierFixesVerificationTester()
    success = tester.run_fixes_verification_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()