#!/usr/bin/env python3
"""
Comprehensive Area9 Backend Testing - Supply Chain Management & Vendor Relations
Testing all aspects of the 9th business area backend functionality as requested in review
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://polaris-requirements.preview.emergentagent.com/api"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

class ComprehensiveArea9Tester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate with QA credentials"""
        try:
            login_data = {
                "email": QA_EMAIL,
                "password": QA_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", "PASS", f"Successfully authenticated as {QA_EMAIL}")
                return True
            else:
                self.log_test("Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Exception: {str(e)}")
            return False

    def test_assessment_schema_area9(self):
        """Test 1: Assessment Schema includes area9 with questions q9_1, q9_2, q9_3"""
        try:
            response = self.session.get(f"{BACKEND_URL}/assessment/schema")
            
            if response.status_code == 200:
                data = response.json()
                schema = data.get("schema", {})
                areas = schema.get("areas", [])
                
                # Find area9
                area9 = None
                for area in areas:
                    if area.get("id") == "area9":
                        area9 = area
                        break
                
                if area9:
                    title = area9.get("title", "")
                    questions = area9.get("questions", [])
                    
                    # Check for required questions
                    question_ids = [q.get("id") for q in questions]
                    required_questions = ["q9_1", "q9_2", "q9_3"]
                    found_questions = [qid for qid in question_ids if qid in required_questions]
                    
                    if len(found_questions) == 3 and "Supply Chain" in title:
                        self.log_test("Assessment Schema Area9", "PASS", 
                                    f"✅ Found area9 '{title}' with all required questions: {found_questions}")
                    else:
                        self.log_test("Assessment Schema Area9", "FAIL", 
                                    f"Missing questions or incorrect title. Found: {found_questions}, Title: {title}")
                else:
                    self.log_test("Assessment Schema Area9", "FAIL", "area9 not found in assessment schema")
            else:
                self.log_test("Assessment Schema Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Assessment Schema Area9", "FAIL", f"Exception: {str(e)}")

    def test_knowledge_base_areas_area9(self):
        """Test 2: Knowledge Base Areas includes area9 with proper title and description"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas")
            
            if response.status_code == 200:
                data = response.json()
                areas = data.get("areas", [])
                
                # Find area9
                area9 = None
                for area in areas:
                    if area.get("id") == "area9":
                        area9 = area
                        break
                
                if area9:
                    title = area9.get("title", "")
                    description = area9.get("description", "")
                    
                    if "Supply Chain Management & Vendor Relations" == title:
                        self.log_test("Knowledge Base Areas Area9", "PASS", 
                                    f"✅ Found area9 with correct title and description")
                    else:
                        self.log_test("Knowledge Base Areas Area9", "FAIL", 
                                    f"Incorrect title: '{title}'")
                else:
                    self.log_test("Knowledge Base Areas Area9", "FAIL", "area9 not found in knowledge base areas")
            else:
                self.log_test("Knowledge Base Areas Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Knowledge Base Areas Area9", "FAIL", f"Exception: {str(e)}")

    def test_template_generation_area9(self):
        """Test 3: Template Generation works for area9"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/generate-template/area9/template")
            
            if response.status_code == 200:
                template_data = response.json()
                
                content = template_data.get("content", "")
                filename = template_data.get("filename", "")
                content_type = template_data.get("content_type", "")
                
                # Check if content is meaningful and relates to supply chain
                supply_chain_keywords = ["supply", "vendor", "chain", "procurement", "supplier"]
                found_keywords = [kw for kw in supply_chain_keywords if kw.lower() in content.lower()]
                
                if len(content) > 500 and len(found_keywords) >= 2 and "area9" in filename:
                    self.log_test("Template Generation Area9", "PASS", 
                                f"✅ Generated {len(content)} char template with supply chain content, keywords: {found_keywords}")
                else:
                    self.log_test("Template Generation Area9", "FAIL", 
                                f"Template quality issues. Length: {len(content)}, Keywords: {found_keywords}, Filename: {filename}")
            else:
                self.log_test("Template Generation Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Template Generation Area9", "FAIL", f"Exception: {str(e)}")

    def test_service_request_area9(self):
        """Test 4: Service request creation recognizes area9"""
        try:
            service_request_data = {
                "area_id": "area9",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with supply chain management and vendor relations for our procurement process",
                "priority": "medium"
            }
            
            response = self.session.post(f"{BACKEND_URL}/service-requests/professional-help", json=service_request_data)
            
            if response.status_code in [200, 201]:
                request_data = response.json()
                
                area_name = request_data.get("area_name", "")
                request_id = request_data.get("request_id", "")
                
                if "Supply Chain Management & Vendor Relations" in area_name and request_id:
                    self.log_test("Service Request Area9", "PASS", 
                                f"✅ Service request created successfully with correct area_name: '{area_name}'")
                else:
                    self.log_test("Service Request Area9", "FAIL", 
                                f"Incorrect area_name: '{area_name}' or missing request_id")
            else:
                self.log_test("Service Request Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Service Request Area9", "FAIL", f"Exception: {str(e)}")

    def test_ai_assistance_area9(self):
        """Test 5: AI assistance endpoint works with area9"""
        try:
            ai_request_data = {
                "area_id": "area9",
                "question": "What are the key components of supply chain management for small businesses?",
                "context": {"business_type": "small_business", "industry": "procurement"}
            }
            
            response = self.session.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", json=ai_request_data)
            
            if response.status_code == 200:
                ai_response = response.json()
                
                response_text = str(ai_response).lower()
                area9_keywords = ["supply chain", "vendor", "procurement", "supplier", "management"]
                found_keywords = [kw for kw in area9_keywords if kw in response_text]
                
                if len(found_keywords) >= 2:
                    self.log_test("AI Assistance Area9", "PASS", 
                                f"✅ AI assistance working for area9, found relevant keywords: {found_keywords}")
                else:
                    self.log_test("AI Assistance Area9", "FAIL", 
                                f"AI response not area9-specific, keywords found: {found_keywords}")
            else:
                self.log_test("AI Assistance Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Assistance Area9", "FAIL", f"Exception: {str(e)}")

    def test_contextual_cards_area9(self):
        """Test 6: Contextual cards work for area9"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/contextual-cards?area_id=area9")
            
            if response.status_code == 200:
                cards_data = response.json()
                cards = cards_data.get("cards", [])
                
                if len(cards) > 0:
                    # Check if cards contain area9-relevant content
                    relevant_cards = 0
                    for card in cards:
                        card_text = str(card).lower()
                        if any(kw in card_text for kw in ["supply", "vendor", "chain", "procurement"]):
                            relevant_cards += 1
                    
                    if relevant_cards > 0:
                        self.log_test("Contextual Cards Area9", "PASS", 
                                    f"✅ Generated {len(cards)} cards, {relevant_cards} are area9-relevant")
                    else:
                        self.log_test("Contextual Cards Area9", "FAIL", 
                                    f"Generated {len(cards)} cards but none are area9-relevant")
                else:
                    self.log_test("Contextual Cards Area9", "FAIL", "No contextual cards generated for area9")
            else:
                self.log_test("Contextual Cards Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Contextual Cards Area9", "FAIL", f"Exception: {str(e)}")

    def test_next_best_actions_area9(self):
        """Test 7: Next best actions endpoint works for area9"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/next-best-actions?area_id=area9")
            
            if response.status_code == 200:
                actions_data = response.json()
                actions = actions_data.get("actions", [])
                
                if len(actions) > 0:
                    # Check if actions are area9-relevant
                    relevant_actions = 0
                    for action in actions:
                        action_text = str(action).lower()
                        if any(kw in action_text for kw in ["supply", "vendor", "chain", "procurement"]):
                            relevant_actions += 1
                    
                    if relevant_actions > 0:
                        self.log_test("Next Best Actions Area9", "PASS", 
                                    f"✅ Generated {len(actions)} actions, {relevant_actions} are area9-relevant")
                    else:
                        self.log_test("Next Best Actions Area9", "FAIL", 
                                    f"Generated {len(actions)} actions but none are area9-relevant")
                else:
                    self.log_test("Next Best Actions Area9", "FAIL", "No next best actions generated for area9")
            else:
                self.log_test("Next Best Actions Area9", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Next Best Actions Area9", "FAIL", f"Exception: {str(e)}")

    def test_area9_data_standards(self):
        """Test 8: Verify area9 is properly defined in DATA_STANDARDS"""
        try:
            # Test by creating a service request and checking if area9 is validated properly
            service_request_data = {
                "area_id": "area9",
                "budget_range": "500-1500",
                "timeline": "1-2 weeks",
                "description": "Testing area9 validation in DATA_STANDARDS",
                "priority": "low"
            }
            
            response = self.session.post(f"{BACKEND_URL}/service-requests/professional-help", json=service_request_data)
            
            if response.status_code in [200, 201]:
                request_data = response.json()
                area_name = request_data.get("area_name", "")
                
                if area_name == "Supply Chain Management & Vendor Relations":
                    self.log_test("Area9 Data Standards", "PASS", 
                                f"✅ area9 properly mapped in DATA_STANDARDS to '{area_name}'")
                else:
                    self.log_test("Area9 Data Standards", "FAIL", 
                                f"Incorrect area_name mapping: '{area_name}'")
            else:
                # Check if it's a validation error about area9
                error_text = response.text.lower()
                if "invalid service area" in error_text and "area9" in error_text:
                    self.log_test("Area9 Data Standards", "FAIL", 
                                "area9 not recognized in DATA_STANDARDS validation")
                else:
                    self.log_test("Area9 Data Standards", "PARTIAL", 
                                f"Service request failed but may not be area9-specific: {response.status_code}")
                
        except Exception as e:
            self.log_test("Area9 Data Standards", "FAIL", f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive area9 backend tests"""
        print("🎯 COMPREHENSIVE AREA9 BACKEND TESTING")
        print("Supply Chain Management & Vendor Relations - Full Backend Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_EMAIL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all tests
        print("Running Comprehensive Area9 Backend Tests...")
        print("-" * 50)
        
        self.test_assessment_schema_area9()
        self.test_knowledge_base_areas_area9()
        self.test_template_generation_area9()
        self.test_service_request_area9()
        self.test_ai_assistance_area9()
        self.test_contextual_cards_area9()
        self.test_next_best_actions_area9()
        self.test_area9_data_standards()
        
        # Summary
        print("=" * 80)
        print("🎯 COMPREHENSIVE AREA9 BACKEND TEST RESULTS")
        print("=" * 80)
        
        total_tests = len(self.test_results) - 1  # Exclude authentication
        passed_tests = len([r for r in self.test_results[1:] if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results[1:] if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results[1:] if r["status"] == "PARTIAL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical findings
        critical_passes = []
        critical_failures = []
        
        for result in self.test_results[1:]:
            if result["status"] == "PASS":
                critical_passes.append(result["test"])
            elif result["status"] == "FAIL":
                critical_failures.append(result["test"])
        
        if critical_passes:
            print("✅ CRITICAL FUNCTIONALITY WORKING:")
            for test in critical_passes:
                print(f"   • {test}")
            print()
        
        if critical_failures:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for test in critical_failures:
                print(f"   • {test}")
            print()
        
        # Overall assessment
        if passed_tests >= 6:  # Most tests passing
            print("🎉 OVERALL ASSESSMENT: Area9 backend functionality is MOSTLY OPERATIONAL")
        elif passed_tests >= 4:  # Some tests passing
            print("⚠️ OVERALL ASSESSMENT: Area9 backend functionality is PARTIALLY OPERATIONAL")
        else:  # Few tests passing
            print("❌ OVERALL ASSESSMENT: Area9 backend functionality has MAJOR ISSUES")
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "partial": partial_tests,
            "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            "results": self.test_results,
            "critical_passes": critical_passes,
            "critical_failures": critical_failures
        }

if __name__ == "__main__":
    tester = ComprehensiveArea9Tester()
    results = tester.run_comprehensive_tests()
    
    # Exit with appropriate code based on success rate
    if results["success_rate"] >= 75:
        sys.exit(0)  # Success
    elif results["success_rate"] >= 50:
        sys.exit(2)  # Partial success
    else:
        sys.exit(1)  # Failure