#!/usr/bin/env python3
"""
Assessment Completion Flow Testing
Focus: Identify and fix the assessment completion error that the user is experiencing
"""

import requests
import json
import time
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://smallbiz-assist.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class AssessmentCompletionTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.session_id = None
        
        print(f"🎯 Assessment Completion Flow Testing")
        print(f"📍 Testing against: {BASE_URL}")
        print(f"🔑 Using QA credentials: {QA_CREDENTIALS['email']}")
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
            print(f"   🔍 Response: {str(response_data)[:500]}...")
        print()

    def authenticate_user(self) -> bool:
        """Authenticate QA user and store token"""
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.token = token
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log_result("QA Client Authentication", True, 
                                  f"Successfully authenticated {QA_CREDENTIALS['email']}", response_time)
                    return True
            
            self.log_result("QA Client Authentication", False, 
                          f"Failed: {response.status_code}", response_time, response.json())
            return False
            
        except Exception as e:
            self.log_result("QA Client Authentication", False, f"Exception: {str(e)}")
            return False

    def test_tier_session_creation(self) -> bool:
        """Test creating a tier session for any business area"""
        try:
            print("\n📊 Testing Tier Session Creation...")
            
            start_time = time.time()
            session_data = {
                "area_id": "area1",  # Business Formation & Registration
                "tier_level": "1",
                "client_context": "Testing assessment completion flow"
            }
            
            # Use form data format as backend expects
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", data=session_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                session_response = response.json()
                session_id = session_response.get("session_id")
                if session_id:
                    self.session_id = session_id
                    self.log_result("Tier Session Creation", True,
                                  f"Created session: {session_id}", response_time)
                    return True
                else:
                    self.log_result("Tier Session Creation", False,
                                  "No session ID returned", response_time, session_response)
                    return False
            else:
                self.log_result("Tier Session Creation", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier Session Creation", False, f"Exception: {str(e)}")
            return False

    def test_submit_all_responses(self) -> bool:
        """Submit responses to all questions in the area to complete assessment"""
        try:
            print("\n📝 Testing Assessment Response Submission...")
            
            if not self.session_id:
                self.log_result("Assessment Response Submission", False, "No session ID available")
                return False
            
            # Submit multiple responses to simulate completing the assessment
            questions = [
                {
                    "question_id": "area1_tier1_q1",
                    "response": "yes",
                    "evidence_provided": "true",
                    "evidence_url": "https://example.com/business-license.pdf"
                },
                {
                    "question_id": "area1_tier1_q2", 
                    "response": "yes",
                    "evidence_provided": "true",
                    "evidence_url": "https://example.com/registration.pdf"
                },
                {
                    "question_id": "area1_tier1_q3",
                    "response": "yes", 
                    "evidence_provided": "true",
                    "evidence_url": "https://example.com/compliance.pdf"
                }
            ]
            
            for i, question_data in enumerate(questions):
                start_time = time.time()
                response = self.session.post(
                    f"{BASE_URL}/assessment/tier-session/{self.session_id}/response", 
                    data=question_data
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"Response Submission {i+1}", True,
                                  f"Submitted response for {question_data['question_id']}", response_time)
                else:
                    self.log_result(f"Response Submission {i+1}", False,
                                  f"API Error: {response.status_code}", response_time, response.json())
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Assessment Response Submission", False, f"Exception: {str(e)}")
            return False

    def test_assessment_progress(self) -> bool:
        """Test GET /api/assessment/tier-session/{session_id}/progress"""
        try:
            print("\n📈 Testing Assessment Progress Endpoint...")
            
            if not self.session_id:
                self.log_result("Assessment Progress", False, "No session ID available")
                return False
            
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}/progress")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                progress_data = response.json()
                completion_rate = progress_data.get("completion_percentage", 0)
                status = progress_data.get("status", "unknown")
                self.log_result("Assessment Progress", True,
                              f"Progress: {completion_rate}% complete, Status: {status}", response_time)
                return True
            else:
                self.log_result("Assessment Progress", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("Assessment Progress", False, f"Exception: {str(e)}")
            return False

    def test_assessment_completion(self) -> bool:
        """Test what happens when assessment is marked as complete"""
        try:
            print("\n🏁 Testing Assessment Completion Flow...")
            
            if not self.session_id:
                self.log_result("Assessment Completion", False, "No session ID available")
                return False
            
            # Try to mark assessment as complete
            start_time = time.time()
            completion_data = {
                "status": "completed",
                "completion_notes": "All questions answered"
            }
            
            response = self.session.post(
                f"{BASE_URL}/assessment/tier-session/{self.session_id}/complete", 
                data=completion_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                completion_response = response.json()
                self.log_result("Assessment Completion", True,
                              f"Assessment marked as complete", response_time)
                return True
            elif response.status_code == 404:
                self.log_result("Assessment Completion", False,
                              "MISSING ENDPOINT: /complete endpoint not found", response_time, response.json())
                return False
            else:
                self.log_result("Assessment Completion", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("Assessment Completion", False, f"Exception: {str(e)}")
            return False

    def test_assessment_results_endpoint(self) -> bool:
        """Check if assessment results endpoint exists"""
        try:
            print("\n📊 Testing Assessment Results Endpoint...")
            
            if not self.session_id:
                self.log_result("Assessment Results Endpoint", False, "No session ID available")
                return False
            
            # Test if results endpoint exists
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/assessment/results/{self.session_id}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                results_data = response.json()
                self.log_result("Assessment Results Endpoint", True,
                              f"Results endpoint exists and working", response_time)
                return True
            elif response.status_code == 404:
                self.log_result("Assessment Results Endpoint", False,
                              "MISSING ENDPOINT: /assessment/results/{session_id} not found", response_time)
                return False
            else:
                self.log_result("Assessment Results Endpoint", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("Assessment Results Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_qa_agency_tier_access(self) -> bool:
        """Check current tier access levels for QA agency"""
        try:
            print("\n🏢 Testing QA Agency Tier Access...")
            
            # First get client tier access
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/client/tier-access")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                access_data = response.json()
                areas = access_data.get("areas", [])
                
                # Check tier 3 access
                tier3_areas = []
                for area in areas:
                    if isinstance(area, dict):
                        max_tier = area.get("max_tier_access", 1)
                        area_id = area.get("area_id", "unknown")
                        if max_tier >= 3:
                            tier3_areas.append(area_id)
                
                if tier3_areas:
                    self.log_result("QA Agency Tier Access", True,
                                  f"Tier 3 access available for {len(tier3_areas)} areas: {tier3_areas}", response_time)
                else:
                    self.log_result("QA Agency Tier Access", False,
                                  "NO TIER 3 ACCESS: QA agency needs tier 3 upgrade", response_time)
                
                return True
            else:
                self.log_result("QA Agency Tier Access", False,
                              f"API Error: {response.status_code}", response_time, response.json())
                return False
                
        except Exception as e:
            self.log_result("QA Agency Tier Access", False, f"Exception: {str(e)}")
            return False

    def test_frontend_navigation_endpoints(self) -> bool:
        """Test endpoints that frontend might be trying to access"""
        try:
            print("\n🌐 Testing Frontend Navigation Endpoints...")
            
            # Test various endpoints that might be missing
            endpoints_to_test = [
                f"/assessment/results/{self.session_id}" if self.session_id else "/assessment/results/test-session",
                "/assessment/completion",
                "/assessment/summary",
                f"/assessment/tier-session/{self.session_id}/results" if self.session_id else "/assessment/tier-session/test/results"
            ]
            
            for endpoint in endpoints_to_test:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}{endpoint}")
                response_time = time.time() - start_time
                
                endpoint_name = endpoint.split('/')[-1] or endpoint.split('/')[-2]
                
                if response.status_code == 200:
                    self.log_result(f"Frontend Endpoint: {endpoint_name}", True,
                                  f"Endpoint {endpoint} exists", response_time)
                elif response.status_code == 404:
                    self.log_result(f"Frontend Endpoint: {endpoint_name}", False,
                                  f"MISSING: {endpoint} not found", response_time)
                else:
                    self.log_result(f"Frontend Endpoint: {endpoint_name}", False,
                                  f"Error {response.status_code}: {endpoint}", response_time, response.json())
            
            return True
            
        except Exception as e:
            self.log_result("Frontend Navigation Endpoints", False, f"Exception: {str(e)}")
            return False

    def print_summary(self):
        """Print comprehensive test summary with focus on assessment completion issues"""
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 ASSESSMENT COMPLETION FLOW TESTING SUMMARY")
        print("=" * 80)
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 80)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']} ({result['response_time']:.3f}s)")
            if result["details"]:
                print(f"    📝 {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Identify critical issues
        print("🚨 CRITICAL ISSUES IDENTIFIED:")
        critical_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                if "MISSING ENDPOINT" in result["details"]:
                    critical_issues.append(f"Missing endpoint: {result['test']}")
                elif "500" in result["details"]:
                    critical_issues.append(f"Server error: {result['test']}")
                elif "NO TIER 3 ACCESS" in result["details"]:
                    critical_issues.append(f"Tier access issue: {result['test']}")
        
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        else:
            print("   ✅ No critical issues found")
        
        print("\n🔧 RECOMMENDED FIXES:")
        if any("MISSING ENDPOINT" in r["details"] for r in self.test_results if not r["success"]):
            print("   1. Implement missing assessment completion endpoints")
            print("   2. Add /assessment/results/{session_id} endpoint")
            print("   3. Add assessment completion workflow")
        
        if any("NO TIER 3 ACCESS" in r["details"] for r in self.test_results if not r["success"]):
            print("   4. Upgrade QA agency to provide tier 3 access")
        
        if any("500" in r["details"] for r in self.test_results if not r["success"]):
            print("   5. Fix server errors in assessment completion flow")

    def run_assessment_completion_test(self):
        """Run comprehensive assessment completion flow test"""
        print("🚀 Starting Assessment Completion Flow Testing...")
        print(f"📅 Test Started: {datetime.now().isoformat()}")
        
        # Authenticate first
        if not self.authenticate_user():
            print("❌ Failed to authenticate - aborting tests")
            return
        
        # Run test sequence
        test_sequence = [
            ("Create Tier Session", self.test_tier_session_creation),
            ("Submit Assessment Responses", self.test_submit_all_responses),
            ("Check Assessment Progress", self.test_assessment_progress),
            ("Test Assessment Completion", self.test_assessment_completion),
            ("Test Assessment Results Endpoint", self.test_assessment_results_endpoint),
            ("Check QA Agency Tier Access", self.test_qa_agency_tier_access),
            ("Test Frontend Navigation Endpoints", self.test_frontend_navigation_endpoints)
        ]
        
        for test_name, test_function in test_sequence:
            try:
                print(f"\n🔄 Running {test_name}...")
                test_function()
            except Exception as e:
                print(f"❌ Error in {test_name}: {str(e)}")
        
        # Print final summary
        self.print_summary()

def main():
    """Main test execution"""
    tester = AssessmentCompletionTester()
    tester.run_assessment_completion_test()

if __name__ == "__main__":
    main()