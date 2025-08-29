#!/usr/bin/env python3
"""
Comprehensive Backend Testing for 95%+ Success Rate Verification
Focus: AI Localized Resources, Tier-based Assessment, Overall System Reliability
After litellm dependency installation
"""

import requests
import json
import time
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"

# QA Test Credentials from review request
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.session_ids = {}
        
        print(f"🎯 Backend Testing for 95%+ Success Rate Verification")
        print(f"📍 Testing against: {BASE_URL}")
        print(f"🔑 Using QA credentials for comprehensive testing")
        print("=" * 80)
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0, response_data: dict = None):
        """Log test result with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} ({response_time:.3f}s)")
        if details:
            print(f"   📝 {details}")
        if not success and response_data:
            print(f"   🔍 Response: {str(response_data)[:200]}...")
        print()

    def authenticate_user(self, role: str) -> bool:
        """Authenticate QA user and store token"""
        try:
            start_time = time.time()
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.tokens[role] = token
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log_result(f"QA {role.title()} Authentication", True, 
                                  f"Successfully authenticated {creds['email']}", response_time)
                    return True
            
            self.log_result(f"QA {role.title()} Authentication", False, 
                          f"Failed: {response.status_code}", response_time, response.json())
            return False
            
        except Exception as e:
            self.log_result(f"QA {role.title()} Authentication", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}",
            "Content-Type": "application/json"
        }

    def test_ai_localized_resources(self) -> bool:
        """Test AI Localized Resources - should generate location-specific content"""
        try:
            print("\n🤖 Testing AI Localized Resources...")
            
            # Test 1: AI Assistance with proper context structure
            start_time = time.time()
            ai_payload = {
                "question": "What local resources are available for small business licensing in San Antonio, Texas?",
                "area_id": "area1",
                "context": {
                    "location": "San Antonio, Texas",
                    "business_area": "Business Formation & Registration"
                }
            }
            
            response = self.session.post(f"{BASE_URL}/knowledge-base/ai-assistance", json=ai_payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                
                # Check if response contains location-specific content
                location_indicators = ["san antonio", "texas", "local", "city", "state"]
                has_location_content = any(indicator in ai_response.lower() for indicator in location_indicators)
                
                if has_location_content and len(ai_response) > 100:
                    self.log_result("AI Localized Resources - Location-Specific Content", True,
                                  f"Generated {len(ai_response)} chars with location context", response_time)
                else:
                    self.log_result("AI Localized Resources - Location-Specific Content", False,
                                  f"Response lacks location specificity: {ai_response[:100]}...", response_time)
                    return False
            else:
                self.log_result("AI Localized Resources - Location-Specific Content", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 2: External Resources with Location Context
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/external-resources/area1?city=San Antonio&state=Texas")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                resources = data.get("resources", [])
                
                # Check for location-specific resources
                location_specific_count = sum(1 for r in resources if r.get("location_specific", False))
                
                if location_specific_count > 0:
                    self.log_result("AI Localized Resources - External Resources", True,
                                  f"Found {location_specific_count} location-specific resources", response_time)
                else:
                    self.log_result("AI Localized Resources - External Resources", False,
                                  f"No location-specific resources found", response_time)
                    return False
            else:
                self.log_result("AI Localized Resources - External Resources", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            return True
            
        except Exception as e:
            self.log_result("AI Localized Resources", False, f"Exception: {str(e)}")
            return False

    def test_tier_based_assessment_schema(self) -> bool:
        """Test GET /api/assessment/schema/tier-based - should return areas with tier information"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema_data = response.json()
                areas = schema_data.get("areas", [])
                if len(areas) >= 10:
                    self.log_result("Tier-Based Schema Retrieval", True,
                                  f"Retrieved schema with {len(areas)} areas", response_time)
                    return True
                else:
                    self.log_result("Tier-Based Schema Retrieval", False,
                                  f"Incomplete schema: only {len(areas)} areas", response_time)
                    return False
            else:
                self.log_result("Tier-Based Schema Retrieval", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier-Based Assessment Schema", False, f"Exception: {str(e)}")
            return False

    def test_tier_based_assessment_system(self) -> bool:
        """Test Tier-based Assessment System with form data format"""
        try:
            print("\n📊 Testing Tier-Based Assessment System...")
            
            # Test 1: Create Tier-Based Session (Form Data Format)
            start_time = time.time()
            session_data = {
                "area_id": "area1",
                "tier_level": "1",
                "client_context": "Small business seeking government contracts"
            }
            
            # Use form data format as specified in review
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", data=session_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                session_response = response.json()
                session_id = session_response.get("session_id")
                if session_id:
                    self.session_ids["tier_session"] = session_id
                    self.log_result("Tier Session Creation (Form Data)", True,
                                  f"Created session: {session_id}", response_time)
                else:
                    self.log_result("Tier Session Creation (Form Data)", False,
                                  "No session ID returned", response_time)
                    return False
            else:
                self.log_result("Tier Session Creation (Form Data)", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 2: Submit Tier Response (Form Data Format)
            start_time = time.time()
            response_data = {
                "question_id": "area1_tier1_q1",
                "response": "yes",
                "evidence_provided": "true",
                "evidence_url": "https://example.com/evidence.pdf"
            }
            
            # Use form data format for tier response submission
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       data=response_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Tier Response Submission (Form Data)", True,
                              "Successfully submitted tier response", response_time)
            else:
                self.log_result("Tier Response Submission (Form Data)", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 3: Get Session Progress
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/assessment/tier-session/{session_id}/progress")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                progress_data = response.json()
                completion_rate = progress_data.get("completion_percentage", 0)
                self.log_result("Tier Session Progress", True,
                              f"Progress: {completion_rate}% complete", response_time)
            else:
                self.log_result("Tier Session Progress", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            return True
            
        except Exception as e:
            self.log_result("Tier-Based Assessment System", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_management(self) -> bool:
        """Test Agency Tier Management endpoints"""
        try:
            print("\n🏢 Testing Agency Tier Management...")
            
            # Switch to agency credentials
            if not self.authenticate_user("agency"):
                return False
            
            # Test 1: Agency Tier Configuration
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/agency/tier-configuration")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                config_data = response.json()
                tier_levels = config_data.get("tier_access_levels", {})
                if len(tier_levels) >= 10:
                    self.log_result("Agency Tier Configuration", True,
                                  f"Retrieved config for {len(tier_levels)} areas", response_time)
                else:
                    self.log_result("Agency Tier Configuration", False,
                                  f"Incomplete config: {len(tier_levels)} areas", response_time)
                    return False
            else:
                self.log_result("Agency Tier Configuration", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 2: Agency Billing Usage
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/agency/billing/usage")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                billing_data = response.json()
                self.log_result("Agency Billing Usage", True,
                              f"Retrieved billing data", response_time)
            else:
                self.log_result("Agency Billing Usage", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            return True
            
        except Exception as e:
            self.log_result("Agency Tier Management", False, f"Exception: {str(e)}")
            return False

    def test_client_tier_access(self) -> bool:
        """Test Client Tier Access functionality"""
        try:
            print("\n👤 Testing Client Tier Access...")
            
            # Switch back to client credentials
            if not self.authenticate_user("client"):
                return False
            
            # Test Client Tier Access
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/client/tier-access")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                access_data = response.json()
                areas = access_data.get("areas", [])
                
                if len(areas) >= 10:
                    # Check that all areas have proper tier access structure
                    valid_areas = 0
                    for area_info in areas:
                        if isinstance(area_info, dict) and "max_tier_access" in area_info:
                            valid_areas += 1
                    
                    if valid_areas >= 10:
                        self.log_result("Client Tier Access", True,
                                      f"Valid tier access for {valid_areas} areas", response_time)
                        return True
                    else:
                        self.log_result("Client Tier Access", False,
                                      f"Invalid structure for some areas", response_time)
                        return False
                else:
                    self.log_result("Client Tier Access", False,
                                  f"Incomplete access data: {len(areas)} areas", response_time)
                    return False
            else:
                self.log_result("Client Tier Access", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
            
        except Exception as e:
            self.log_result("Client Tier Access", False, f"Exception: {str(e)}")
            return False

    def test_system_reliability(self) -> bool:
        """Test overall system reliability and performance"""
        try:
            print("\n⚡ Testing System Reliability...")
            
            # Test 1: System Health Check
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/system/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "")
                if status == "healthy":
                    self.log_result("System Health Check", True,
                                  f"System status: {status}", response_time)
                else:
                    self.log_result("System Health Check", False,
                                  f"System status: {status}", response_time)
                    return False
            else:
                self.log_result("System Health Check", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 2: Authentication System Reliability
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/auth/me")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get("email") == QA_CREDENTIALS["client"]["email"]:
                    self.log_result("Authentication System Reliability", True,
                                  "Auth system working correctly", response_time)
                else:
                    self.log_result("Authentication System Reliability", False,
                                  "Auth data mismatch", response_time)
                    return False
            else:
                self.log_result("Authentication System Reliability", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            # Test 3: Database Connectivity
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/assessment/schema")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema_data = response.json()
                if schema_data.get("areas"):
                    self.log_result("Database Connectivity", True,
                                  "Database queries working", response_time)
                else:
                    self.log_result("Database Connectivity", False,
                                  "Empty schema response", response_time)
                    return False
            else:
                self.log_result("Database Connectivity", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False

            return True
            
        except Exception as e:
            self.log_result("System Reliability", False, f"Exception: {str(e)}")
            return False

    def calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not self.test_results:
            return 0.0
        
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        return (successful_tests / total_tests) * 100

    def print_summary(self):
        """Print comprehensive test summary"""
        success_rate = self.calculate_success_rate()
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        print(f"🎯 TARGET: 95%+ Success Rate")
        
        if success_rate >= 95.0:
            print("✅ SUCCESS: Target 95%+ success rate ACHIEVED!")
            print("🚀 System ready for production deployment")
        else:
            print("❌ BELOW TARGET: Success rate below 95% threshold")
            print("🔧 Additional fixes needed before production")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 80)
        
        # Group results by category
        categories = {
            "Authentication": [],
            "AI Localized Resources": [],
            "Tier-Based Assessment": [],
            "Agency Management": [],
            "Client Access": [],
            "System Reliability": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif "AI Localized" in test_name:
                categories["AI Localized Resources"].append(result)
            elif "Tier" in test_name:
                categories["Tier-Based Assessment"].append(result)
            elif "Agency" in test_name:
                categories["Agency Management"].append(result)
            elif "Client" in test_name:
                categories["Client Access"].append(result)
            else:
                categories["System Reliability"].append(result)
        
        for category, results in categories.items():
            if results:
                category_success = sum(1 for r in results if r["success"])
                category_total = len(results)
                category_rate = (category_success / category_total) * 100
                
                status_icon = "✅" if category_rate >= 95 else "⚠️" if category_rate >= 80 else "❌"
                print(f"{status_icon} {category}: {category_rate:.1f}% ({category_success}/{category_total})")
                
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"    {status} {result['test']} ({result['response_time']:.3f}s)")
                    if result["details"]:
                        print(f"        📝 {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Performance metrics
        avg_response_time = sum(r["response_time"] for r in self.test_results) / len(self.test_results)
        max_response_time = max(r["response_time"] for r in self.test_results)
        
        print(f"⚡ PERFORMANCE METRICS:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Maximum Response Time: {max_response_time:.3f}s")
        
        # Production readiness assessment
        print(f"\n🏭 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 95.0:
            print("   ✅ EXCELLENT - System meets 95%+ success rate requirement")
            print("   ✅ All critical functionality operational")
            print("   ✅ AI localized resources generating dynamic content")
            print("   ✅ Tier-based assessment system fully functional")
            print("   🚀 READY FOR PRODUCTION DEPLOYMENT")
        elif success_rate >= 90.0:
            print("   ⚠️  GOOD - System approaching target with minor issues")
            print("   🔧 Minor fixes needed to reach 95% threshold")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Significant issues identified")
            print("   🚨 Major fixes required before production deployment")



    def run_comprehensive_test(self):
        """Run all tests for 95%+ success rate verification"""
        print("🚀 Starting Comprehensive Backend Testing for 95%+ Success Rate...")
        print(f"📅 Test Started: {datetime.now().isoformat()}")
        
        # Authenticate users first
        if not self.authenticate_user("client"):
            print("❌ Failed to authenticate client - aborting tests")
            return
        
        # Run all test categories
        test_categories = [
            ("AI Localized Resources", self.test_ai_localized_resources),
            ("Tier-Based Assessment System", self.test_tier_based_assessment_system),
            ("Agency Tier Management", self.test_agency_tier_management),
            ("Client Tier Access", self.test_client_tier_access),
            ("System Reliability", self.test_system_reliability)
        ]
        
        for category_name, test_function in test_categories:
            try:
                print(f"\n🔄 Running {category_name} tests...")
                test_function()
            except Exception as e:
                print(f"❌ Error in {category_name}: {str(e)}")
        
        # Print final summary
        self.print_summary()

def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()