#!/usr/bin/env python3
"""
Area9 Backend Testing - Supply Chain Management & Vendor Relations
Testing the newly implemented 9th business area backend functionality
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

class Area9BackendTester:
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
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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
                schema = response.json()
                
                # Check if area9 exists in schema
                if "area9" in schema:
                    area9_data = schema["area9"]
                    
                    # Check for required questions
                    required_questions = ["q9_1", "q9_2", "q9_3"]
                    found_questions = []
                    
                    if "questions" in area9_data:
                        for question_id in area9_data["questions"]:
                            if question_id in required_questions:
                                found_questions.append(question_id)
                    
                    if len(found_questions) == 3:
                        self.log_test("Assessment Schema Area9", "PASS", 
                                    f"Found area9 with all required questions: {found_questions}",
                                    {"area9_title": area9_data.get("title", ""), "questions_count": len(area9_data.get("questions", []))})
                    else:
                        self.log_test("Assessment Schema Area9", "FAIL", 
                                    f"Missing questions. Found: {found_questions}, Required: {required_questions}",
                                    area9_data)
                else:
                    self.log_test("Assessment Schema Area9", "FAIL", 
                                "area9 not found in assessment schema",
                                {"available_areas": list(schema.keys())})
            else:
                self.log_test("Assessment Schema Area9", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Assessment Schema Area9", "FAIL", f"Exception: {str(e)}")

    def test_knowledge_base_areas_area9(self):
        """Test 2: Knowledge Base Areas includes area9 with proper title and description"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas")
            
            if response.status_code == 200:
                areas = response.json()
                
                # Look for area9 in the areas list
                area9_found = False
                area9_data = None
                
                if isinstance(areas, list):
                    for area in areas:
                        if area.get("id") == "area9" or area.get("area_id") == "area9":
                            area9_found = True
                            area9_data = area
                            break
                elif isinstance(areas, dict) and "area9" in areas:
                    area9_found = True
                    area9_data = areas["area9"]
                
                if area9_found:
                    title = area9_data.get("title", "") or area9_data.get("name", "")
                    description = area9_data.get("description", "")
                    
                    # Check if title contains "Supply Chain" keywords
                    if "supply chain" in title.lower() or "vendor" in title.lower():
                        self.log_test("Knowledge Base Areas Area9", "PASS", 
                                    f"Found area9: '{title}'",
                                    {"title": title, "description": description[:100] + "..." if len(description) > 100 else description})
                    else:
                        self.log_test("Knowledge Base Areas Area9", "PARTIAL", 
                                    f"Found area9 but title may be incorrect: '{title}'",
                                    area9_data)
                else:
                    self.log_test("Knowledge Base Areas Area9", "FAIL", 
                                "area9 not found in knowledge base areas",
                                {"total_areas": len(areas) if isinstance(areas, list) else len(areas.keys()) if isinstance(areas, dict) else 0})
            else:
                self.log_test("Knowledge Base Areas Area9", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Knowledge Base Areas Area9", "FAIL", f"Exception: {str(e)}")

    def test_template_generation_area9(self):
        """Test 3: Template Generation works for area9"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/generate-template/area9/template")
            
            if response.status_code == 200:
                template_data = response.json()
                
                # Check if response has required fields
                required_fields = ["content", "filename", "content_type"]
                missing_fields = [field for field in required_fields if field not in template_data]
                
                if not missing_fields:
                    content = template_data.get("content", "")
                    filename = template_data.get("filename", "")
                    
                    # Check if content is meaningful and relates to supply chain
                    if len(content) > 100 and ("supply" in content.lower() or "vendor" in content.lower() or "chain" in content.lower()):
                        self.log_test("Template Generation Area9", "PASS", 
                                    f"Generated template with {len(content)} characters, filename: {filename}",
                                    {"content_preview": content[:200] + "...", "filename": filename})
                    else:
                        self.log_test("Template Generation Area9", "PARTIAL", 
                                    f"Template generated but content may not be area9-specific. Length: {len(content)}",
                                    {"content_preview": content[:200] + "...", "filename": filename})
                else:
                    self.log_test("Template Generation Area9", "FAIL", 
                                f"Missing required fields: {missing_fields}",
                                template_data)
            else:
                self.log_test("Template Generation Area9", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Template Generation Area9", "FAIL", f"Exception: {str(e)}")

    def test_service_areas_area9(self):
        """Test 4: Service Areas recognizes area9 in service request creation"""
        try:
            # Test creating a service request with area9
            service_request_data = {
                "area_id": "area9",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with supply chain management and vendor relations for our procurement process",
                "priority": "medium"
            }
            
            response = self.session.post(f"{BACKEND_URL}/service-requests/professional-help", json=service_request_data)
            
            if response.status_code == 200 or response.status_code == 201:
                request_data = response.json()
                
                # Check if area9 is properly recognized
                if request_data.get("area_id") == "area9":
                    area_name = request_data.get("area_name", "")
                    if "supply chain" in area_name.lower() or "vendor" in area_name.lower():
                        self.log_test("Service Areas Area9", "PASS", 
                                    f"Service request created with area9, area_name: '{area_name}'",
                                    {"request_id": request_data.get("id", ""), "area_name": area_name})
                    else:
                        self.log_test("Service Areas Area9", "PARTIAL", 
                                    f"Service request created but area_name may be incorrect: '{area_name}'",
                                    request_data)
                else:
                    self.log_test("Service Areas Area9", "FAIL", 
                                f"Service request created but area_id is {request_data.get('area_id')} instead of area9",
                                request_data)
            else:
                # Check if it's a validation error specifically about area9
                error_text = response.text.lower()
                if "area9" in error_text or "invalid service area" in error_text:
                    self.log_test("Service Areas Area9", "FAIL", 
                                f"area9 not recognized as valid service area. HTTP {response.status_code}: {response.text}")
                else:
                    self.log_test("Service Areas Area9", "PARTIAL", 
                                f"Service request failed but may not be area9-specific issue. HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Service Areas Area9", "FAIL", f"Exception: {str(e)}")

    def test_ai_content_area9(self):
        """Test 5: AI-powered endpoints reference area9 with proper area name resolution"""
        try:
            # Test AI assistance endpoint with area9
            ai_request_data = {
                "area_id": "area9",
                "question": "What are the key components of supply chain management for small businesses?",
                "context": "procurement readiness"
            }
            
            response = self.session.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", json=ai_request_data)
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Check if response contains area9-related content
                response_text = str(ai_response).lower()
                area9_keywords = ["supply chain", "vendor", "procurement", "supplier"]
                
                found_keywords = [keyword for keyword in area9_keywords if keyword in response_text]
                
                if found_keywords:
                    self.log_test("AI Content Area9", "PASS", 
                                f"AI assistance working for area9, found keywords: {found_keywords}",
                                {"response_length": len(str(ai_response)), "keywords_found": found_keywords})
                else:
                    self.log_test("AI Content Area9", "PARTIAL", 
                                "AI assistance responded but content may not be area9-specific",
                                {"response_preview": str(ai_response)[:200] + "..."})
            else:
                # Check if it's specifically an area9 recognition issue
                error_text = response.text.lower()
                if "area9" in error_text or "invalid area" in error_text:
                    self.log_test("AI Content Area9", "FAIL", 
                                f"AI endpoint doesn't recognize area9. HTTP {response.status_code}: {response.text}")
                else:
                    self.log_test("AI Content Area9", "PARTIAL", 
                                f"AI endpoint failed but may not be area9-specific. HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Content Area9", "FAIL", f"Exception: {str(e)}")

    def test_contextual_cards_area9(self):
        """Test 6: Contextual cards endpoint works for area9"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/contextual-cards?area_id=area9")
            
            if response.status_code == 200:
                cards_data = response.json()
                
                if isinstance(cards_data, list) and len(cards_data) > 0:
                    # Check if cards contain area9-relevant content
                    area9_relevant = False
                    for card in cards_data:
                        card_text = str(card).lower()
                        if any(keyword in card_text for keyword in ["supply", "vendor", "chain", "procurement"]):
                            area9_relevant = True
                            break
                    
                    if area9_relevant:
                        self.log_test("Contextual Cards Area9", "PASS", 
                                    f"Generated {len(cards_data)} contextual cards for area9",
                                    {"cards_count": len(cards_data), "first_card": cards_data[0] if cards_data else None})
                    else:
                        self.log_test("Contextual Cards Area9", "PARTIAL", 
                                    f"Generated cards but content may not be area9-specific",
                                    {"cards_count": len(cards_data)})
                else:
                    self.log_test("Contextual Cards Area9", "FAIL", 
                                "No contextual cards generated for area9",
                                cards_data)
            else:
                self.log_test("Contextual Cards Area9", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Contextual Cards Area9", "FAIL", f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all area9 backend tests"""
        print("🎯 AREA9 BACKEND TESTING - Supply Chain Management & Vendor Relations")
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
        print("Running Area9 Backend Tests...")
        print("-" * 40)
        
        self.test_assessment_schema_area9()
        self.test_knowledge_base_areas_area9()
        self.test_template_generation_area9()
        self.test_service_areas_area9()
        self.test_ai_content_area9()
        self.test_contextual_cards_area9()
        
        # Summary
        print("=" * 80)
        print("🎯 AREA9 BACKEND TEST SUMMARY")
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
        
        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 40)
        for result in self.test_results[1:]:  # Skip authentication
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "partial": partial_tests,
            "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = Area9BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    elif results["partial"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)