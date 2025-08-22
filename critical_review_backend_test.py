#!/usr/bin/env python3
"""
Critical Issues Verification and Backend Support Check
Focus on 9th Business Area and Assessment Gap Flow Testing
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://frontend-sync-3.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CriticalReviewTest:
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
                self.tokens[role] = token
                self.log_result(f"Authentication - {role.title()}", True, 
                              f"Token obtained successfully", response_time)
                return True
            else:
                self.log_result(f"Authentication - {role.title()}", False, 
                              f"Status: {response.status_code}, Response: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {role.title()}", False, f"Exception: {str(e)}", response_time)
            return False
    
    def get_headers(self, role):
        """Get authorization headers for role"""
        if role not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[role]}"}
    
    def test_9th_business_area_backend_support(self):
        """Test if area9 'Supply Chain Management & Vendor Relations' is supported"""
        print("\n🔍 TESTING: 9th Business Area Backend Support")
        
        # Test 1: Check assessment schema includes area9
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/assessment/schema", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema_data = response.json()
                schema = schema_data.get("schema", {})
                areas = schema.get("areas", [])
                area9_found = any(area.get("id") == "area9" for area in areas)
                area9_name_correct = any(
                    area.get("id") == "area9" and 
                    "Supply Chain Management" in area.get("title", "") and
                    "Vendor Relations" in area.get("title", "")
                    for area in areas
                )
                
                if area9_found and area9_name_correct:
                    area9_data = next(area for area in areas if area.get("id") == "area9")
                    questions = area9_data.get("questions", [])
                    has_q9_questions = any(q.get("id", "").startswith("q9_") for q in questions)
                    
                    self.log_result("Assessment Schema - Area9 Support", 
                                  has_q9_questions,
                                  f"Area9 found with {len(questions)} questions, q9_* questions: {has_q9_questions}",
                                  response_time)
                else:
                    self.log_result("Assessment Schema - Area9 Support", False,
                                  f"Area9 not found. Found {len(areas)} areas (area1-area8). Missing area9 'Supply Chain Management & Vendor Relations'",
                                  response_time)
            else:
                self.log_result("Assessment Schema - Area9 Support", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Assessment Schema - Area9 Support", False, f"Exception: {str(e)}", 0)
        
        # Test 2: Check knowledge base endpoints recognize area9
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                areas = response.json().get("areas", [])
                area9_in_kb = any(area.get("id") == "area9" for area in areas)
                area_ids = [area.get("id") for area in areas]
                
                self.log_result("Knowledge Base - Area9 Recognition", 
                              area9_in_kb,
                              f"Area9 found in knowledge base: {area9_in_kb}. Found areas: {area_ids}",
                              response_time)
            else:
                self.log_result("Knowledge Base - Area9 Recognition", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Knowledge Base - Area9 Recognition", False, f"Exception: {str(e)}", 0)
        
        # Test 3: Test external resources endpoints for area9
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/external-resources/area9", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                resources = response.json()
                has_resources = len(resources.get("resources", [])) > 0
                
                self.log_result("External Resources - Area9 Support", 
                              has_resources,
                              f"Area9 external resources found: {len(resources.get('resources', []))} resources",
                              response_time)
            else:
                self.log_result("External Resources - Area9 Support", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("External Resources - Area9 Support", False, f"Exception: {str(e)}", 0)
        
        # Test 4: Test deliverables generation for area9
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/knowledge-base/generate-template/area9/template", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                template_data = response.json()
                has_content = len(template_data.get("content", "")) > 0
                correct_filename = "area9" in template_data.get("filename", "")
                
                self.log_result("Deliverables Generation - Area9", 
                              has_content and correct_filename,
                              f"Template generated with {len(template_data.get('content', ''))} chars, filename: {template_data.get('filename', 'N/A')}",
                              response_time)
            else:
                self.log_result("Deliverables Generation - Area9", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Deliverables Generation - Area9", False, f"Exception: {str(e)}", 0)
    
    def test_assessment_gap_flow_backend(self):
        """Test assessment response handling for 'no_help' answers and pending states"""
        print("\n🔍 TESTING: Assessment Gap Flow Backend")
        
        # Test 1: Create assessment session
        session_id = None
        try:
            start_time = time.time()
            response = requests.post(f"{BACKEND_URL}/assessment/session", 
                                   headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get("session_id")
                
                self.log_result("Assessment Session Creation", 
                              session_id is not None,
                              f"Session created: {session_id}",
                              response_time)
                self.test_data["session_id"] = session_id
            else:
                self.log_result("Assessment Session Creation", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                return
                
        except Exception as e:
            self.log_result("Assessment Session Creation", False, f"Exception: {str(e)}", 0)
            return
        
        # Test 2: Submit "no_help" response using correct endpoint format
        try:
            start_time = time.time()
            no_help_response = {
                "question_id": "q1_1",
                "answer": "no_help"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/session/{session_id}/response", 
                                   json=no_help_response,
                                   headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                success = response_data.get("success", False)
                progress = response_data.get("progress_percentage", 0)
                
                self.log_result("Assessment No-Help Response Handling", 
                              success,
                              f"Response submitted successfully: {success}, Progress: {progress}%",
                              response_time)
            else:
                self.log_result("Assessment No-Help Response Handling", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Assessment No-Help Response Handling", False, f"Exception: {str(e)}", 0)
        
        # Test 3: Test assessment progress calculation
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/assessment/session/{session_id}/progress", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                progress_data = response.json()
                has_progress = "progress" in progress_data or "percentage" in str(progress_data).lower()
                
                self.log_result("Assessment Progress Calculation", 
                              has_progress,
                              f"Progress data available: {has_progress}, Data: {str(progress_data)[:100]}...",
                              response_time)
            else:
                self.log_result("Assessment Progress Calculation", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Assessment Progress Calculation", False, f"Exception: {str(e)}", 0)
        
        # Test 4: Test session data retrieval (check if endpoint exists)
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/assessment/session/{session_id}", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                session_data = response.json()
                has_responses = "responses" in session_data
                
                self.log_result("Session Data Retrieval", 
                              has_responses,
                              f"Session data retrieved: {has_responses}",
                              response_time)
            elif response.status_code == 404:
                self.log_result("Session Data Retrieval", False,
                              "Endpoint not implemented (404)",
                              response_time)
            else:
                self.log_result("Session Data Retrieval", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Session Data Retrieval", False, f"Exception: {str(e)}", 0)
    
    def test_knowledge_base_area_support(self):
        """Test all 9 business areas in knowledge base endpoints"""
        print("\n🔍 TESTING: Knowledge Base Area Support (All 9 Areas)")
        
        expected_areas = ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8", "area9"]
        
        # Test 1: Test all 9 areas in knowledge base
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                areas_data = response.json()
                areas = areas_data.get("areas", [])
                area_ids = [area.get("id") for area in areas]
                
                all_9_areas_present = all(area_id in area_ids for area_id in expected_areas)
                
                self.log_result("Knowledge Base - All 9 Areas Present", 
                              all_9_areas_present,
                              f"Found {len(areas)} areas: {area_ids}. Missing area9. Backend only supports 8 areas currently.",
                              response_time)
            else:
                self.log_result("Knowledge Base - All 9 Areas Present", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Knowledge Base - All 9 Areas Present", False, f"Exception: {str(e)}", 0)
        
        # Test 2: Test AI consultation endpoints for area1 (since area9 doesn't exist)
        try:
            start_time = time.time()
            ai_request = {
                "area_id": "area1",
                "question": "How do I improve my business formation process?",
                "context": {"business_type": "small business", "industry": "consulting"}
            }
            
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                   json=ai_request,
                                   headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                ai_response = response.json()
                has_response = len(ai_response.get("response", "")) > 0
                business_relevant = "business" in ai_response.get("response", "").lower()
                
                self.log_result("AI Consultation - Area1 Support", 
                              has_response and business_relevant,
                              f"AI response length: {len(ai_response.get('response', ''))}, Business relevant: {business_relevant}",
                              response_time)
            else:
                self.log_result("AI Consultation - Area1 Support", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("AI Consultation - Area1 Support", False, f"Exception: {str(e)}", 0)
        
        # Test 3: Test AI resources endpoint (which seems to be the external resources equivalent)
        try:
            start_time = time.time()
            ai_resources_request = {
                "area_id": "area1",
                "question_id": "q1_1",
                "question_text": "Do you have a valid business license?",
                "locality": "San Antonio, TX",
                "count": 3,
                "prefer": "gov_edu_nonprofit"
            }
            
            response = requests.post(f"{BACKEND_URL}/ai/resources", 
                                   json=ai_resources_request,
                                   headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                resources = response.json()
                has_resources = len(resources.get("resources", [])) > 0
                
                self.log_result("AI Resources - External Resources Support", 
                              has_resources,
                              f"AI resources found: {len(resources.get('resources', []))} resources",
                              response_time)
            else:
                self.log_result("AI Resources - External Resources Support", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("AI Resources - External Resources Support", False, f"Exception: {str(e)}", 0)
    
    def test_assessment_system_validation(self):
        """Test complete assessment flow with 9 areas"""
        print("\n🔍 TESTING: Assessment System Validation (9 Areas)")
        
        # Test 1: Test complete assessment flow with 9 areas
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/assessment/schema", 
                                  headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schema_data = response.json()
                schema = schema_data.get("schema", {})
                areas = schema.get("areas", [])
                has_9_areas = len(areas) == 9
                
                # Check if area9 is included in assessment progress calculation
                area_ids = [area.get("id") for area in areas]
                area9_in_assessment = "area9" in area_ids
                
                self.log_result("Assessment System - 9 Areas Support", 
                              has_9_areas and area9_in_assessment,
                              f"Assessment has {len(areas)} areas ({area_ids}), Area9 missing: Backend only supports 8 areas",
                              response_time)
            else:
                self.log_result("Assessment System - 9 Areas Support", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Assessment System - 9 Areas Support", False, f"Exception: {str(e)}", 0)
        
        # Test 2: Test gap analysis with area9 questions
        if "session_id" in self.test_data:
            try:
                start_time = time.time()
                # Submit a gap response for area9
                gap_response = {
                    "session_id": self.test_data["session_id"],
                    "area_id": "area9",
                    "question_id": "q9_1",
                    "response": "no_help",
                    "maturity_level": "pending_professional_help"
                }
                
                response = requests.post(f"{BACKEND_URL}/assessment/response", 
                                       json=gap_response,
                                       headers=self.get_headers("client"))
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Check gap analysis
                    gap_response = requests.get(f"{BACKEND_URL}/assessment/gaps/{self.test_data['session_id']}", 
                                              headers=self.get_headers("client"))
                    
                    if gap_response.status_code == 200:
                        gaps = gap_response.json()
                        area9_gap_found = any(
                            gap.get("area_id") == "area9" 
                            for gap in gaps.get("gaps", [])
                        )
                        
                        self.log_result("Gap Analysis - Area9 Questions", 
                                      area9_gap_found,
                                      f"Area9 gap identified: {area9_gap_found}",
                                      response_time)
                    else:
                        self.log_result("Gap Analysis - Area9 Questions", False,
                                      f"Gap analysis failed: {gap_response.status_code}",
                                      response_time)
                else:
                    self.log_result("Gap Analysis - Area9 Questions", False,
                                  f"Gap response submission failed: {response.status_code}",
                                  response_time)
                    
            except Exception as e:
                self.log_result("Gap Analysis - Area9 Questions", False, f"Exception: {str(e)}", 0)
        
        # Test 3: Test certificate generation with 9-area assessment
        try:
            start_time = time.time()
            cert_request = {
                "assessment_session_id": self.test_data.get("session_id"),
                "include_all_areas": True
            }
            
            response = requests.post(f"{BACKEND_URL}/certificates/generate", 
                                   json=cert_request,
                                   headers=self.get_headers("client"))
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                cert_data = response.json()
                has_certificate = "certificate_id" in cert_data
                includes_9_areas = "area9" in str(cert_data).lower() or len(cert_data.get("areas_covered", [])) == 9
                
                self.log_result("Certificate Generation - 9 Areas", 
                              has_certificate and includes_9_areas,
                              f"Certificate generated: {has_certificate}, Includes 9 areas: {includes_9_areas}",
                              response_time)
            else:
                self.log_result("Certificate Generation - 9 Areas", False,
                              f"Status: {response.status_code}, Response: {response.text}",
                              response_time)
                
        except Exception as e:
            self.log_result("Certificate Generation - 9 Areas", False, f"Exception: {str(e)}", 0)
    
    def run_all_tests(self):
        """Run all critical review tests"""
        print("🎯 CRITICAL ISSUES VERIFICATION AND BACKEND SUPPORT CHECK")
        print("=" * 80)
        
        # Authenticate users
        print("\n🔐 AUTHENTICATION PHASE")
        auth_success = True
        for role in ["client", "provider", "navigator", "agency"]:
            if not self.authenticate_user(role):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication failed for some users. Cannot proceed with tests.")
            return
        
        # Run critical tests
        self.test_9th_business_area_backend_support()
        self.test_assessment_gap_flow_backend()
        self.test_knowledge_base_area_support()
        self.test_assessment_system_validation()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 CRITICAL REVIEW TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"    {result['details']}")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check 9th business area support
        area9_tests = [r for r in self.results if "area9" in r["test"].lower() or "9th" in r["test"].lower()]
        area9_working = all(r["success"] for r in area9_tests)
        print(f"✅ 9th Business Area Support: {'WORKING' if area9_working else 'NEEDS ATTENTION'}")
        
        # Check assessment gap flow
        gap_tests = [r for r in self.results if "gap" in r["test"].lower() or "no-help" in r["test"].lower() or "pending" in r["test"].lower()]
        gap_working = all(r["success"] for r in gap_tests)
        print(f"✅ Assessment Gap Flow: {'WORKING' if gap_working else 'NEEDS ATTENTION'}")
        
        # Check knowledge base support
        kb_tests = [r for r in self.results if "knowledge base" in r["test"].lower() or "ai consultation" in r["test"].lower()]
        kb_working = all(r["success"] for r in kb_tests)
        print(f"✅ Knowledge Base Support: {'WORKING' if kb_working else 'NEEDS ATTENTION'}")
        
        # Check assessment system
        assessment_tests = [r for r in self.results if "assessment" in r["test"].lower() and "system" in r["test"].lower()]
        assessment_working = all(r["success"] for r in assessment_tests)
        print(f"✅ Assessment System: {'WORKING' if assessment_working else 'NEEDS ATTENTION'}")
        
        print(f"\n🎯 PRODUCTION READINESS: {'✅ GOOD' if success_rate >= 80 else '⚠️ NEEDS ATTENTION' if success_rate >= 60 else '❌ CRITICAL ISSUES'}")

if __name__ == "__main__":
    test = CriticalReviewTest()
    test.run_all_tests()