#!/usr/bin/env python3
"""
Area9 Verification Test - Quick verification of 9th business area backend implementation
Testing Supply Chain Management & Vendor Relations functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://production-guru.preview.emergentagent.com/api"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

class Area9VerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
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

    def authenticate(self):
        """Authenticate with QA credentials"""
        try:
            login_data = {
                "email": QA_EMAIL,
                "password": QA_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_result("Authentication", True, f"Successfully authenticated as {QA_EMAIL}")
                return True
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_assessment_schema_area9(self):
        """Test 1: GET /api/assessment/schema - verify area9 exists with questions q9_1, q9_2, q9_3"""
        try:
            response = self.session.get(f"{BACKEND_URL}/assessment/schema")
            
            if response.status_code == 200:
                schema_data = response.json()
                
                # Check if schema has areas
                if "schema" in schema_data and "areas" in schema_data["schema"]:
                    areas = schema_data["schema"]["areas"]
                    
                    # Find area9
                    area9_data = None
                    for area in areas:
                        if area.get("id") == "area9":
                            area9_data = area
                            break
                    
                    if area9_data:
                        # Check area9 title
                        expected_title = "Supply Chain Management & Vendor Relations"
                        actual_title = area9_data.get("title", "")
                        
                        if expected_title == actual_title:
                            # Check for required questions
                            questions = area9_data.get("questions", [])
                            required_questions = ["q9_1", "q9_2", "q9_3"]
                            found_questions = []
                            
                            for question in questions:
                                q_id = question.get("id", "")
                                if q_id in required_questions:
                                    found_questions.append(q_id)
                            
                            if len(found_questions) == 3:
                                self.log_result(
                                    "Assessment Schema Area9", 
                                    True, 
                                    f"Found area9 '{actual_title}' with all required questions: {found_questions}"
                                )
                            else:
                                self.log_result(
                                    "Assessment Schema Area9", 
                                    False, 
                                    f"Missing questions. Found: {found_questions}, Required: {required_questions}"
                                )
                        else:
                            self.log_result(
                                "Assessment Schema Area9", 
                                False, 
                                f"Area9 title mismatch. Expected: '{expected_title}', Found: '{actual_title}'"
                            )
                    else:
                        self.log_result(
                            "Assessment Schema Area9", 
                            False, 
                            "Area9 not found in assessment schema areas list"
                        )
                else:
                    self.log_result(
                        "Assessment Schema Area9", 
                        False, 
                        "Invalid schema structure - missing 'schema.areas'",
                        list(schema_data.keys())
                    )
            else:
                self.log_result(
                    "Assessment Schema Area9", 
                    False, 
                    f"API call failed with status {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Assessment Schema Area9", False, f"Error: {str(e)}")

    def test_knowledge_base_areas_area9(self):
        """Test 2: GET /api/knowledge-base/areas - verify area9 appears in the areas list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas")
            
            if response.status_code == 200:
                areas_data = response.json()
                
                # Look for area9 in the response
                area9_found = False
                area9_info = None
                
                # Check if response has 'areas' key
                if "areas" in areas_data:
                    areas_list = areas_data["areas"]
                    for area in areas_list:
                        if area.get("id") == "area9":
                            area9_found = True
                            area9_info = area
                            break
                elif isinstance(areas_data, list):
                    for area in areas_data:
                        if area.get("id") == "area9" or "area9" in str(area):
                            area9_found = True
                            area9_info = area
                            break
                elif isinstance(areas_data, dict):
                    if "area9" in areas_data:
                        area9_found = True
                        area9_info = areas_data["area9"]
                
                if area9_found:
                    title = ""
                    if isinstance(area9_info, dict):
                        title = area9_info.get("title", area9_info.get("name", ""))
                    
                    expected_title = "Supply Chain Management & Vendor Relations"
                    if title == expected_title:
                        self.log_result(
                            "Knowledge Base Areas Area9", 
                            True, 
                            f"Found area9 in knowledge base areas list. Title: '{title}'"
                        )
                    else:
                        self.log_result(
                            "Knowledge Base Areas Area9", 
                            False, 
                            f"Area9 found but title mismatch. Expected: '{expected_title}', Found: '{title}'"
                        )
                else:
                    self.log_result(
                        "Knowledge Base Areas Area9", 
                        False, 
                        "Area9 not found in knowledge base areas list",
                        areas_data
                    )
            else:
                self.log_result(
                    "Knowledge Base Areas Area9", 
                    False, 
                    f"API call failed with status {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Knowledge Base Areas Area9", False, f"Error: {str(e)}")

    def test_template_generation_area9(self):
        """Test 3: GET /api/knowledge-base/generate-template/area9/template - verify template generation works"""
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/generate-template/area9/template")
            
            if response.status_code == 200:
                template_data = response.json()
                
                # Check if template has content
                content = template_data.get("content", "")
                filename = template_data.get("filename", "")
                content_type = template_data.get("content_type", "")
                
                if content and len(content) > 100:  # Reasonable content length
                    # Check for supply chain related keywords
                    supply_chain_keywords = ["supply", "vendor", "chain", "procurement", "supplier"]
                    found_keywords = [kw for kw in supply_chain_keywords if kw.lower() in content.lower()]
                    
                    if found_keywords:
                        self.log_result(
                            "Template Generation Area9", 
                            True, 
                            f"Generated template with {len(content)} characters. Found keywords: {found_keywords}. Filename: {filename}"
                        )
                    else:
                        self.log_result(
                            "Template Generation Area9", 
                            False, 
                            f"Template generated but missing supply chain keywords. Content length: {len(content)}"
                        )
                else:
                    self.log_result(
                        "Template Generation Area9", 
                        False, 
                        f"Template content too short or empty. Length: {len(content)}",
                        template_data
                    )
            else:
                self.log_result(
                    "Template Generation Area9", 
                    False, 
                    f"API call failed with status {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Template Generation Area9", False, f"Error: {str(e)}")

    def run_verification(self):
        """Run all area9 verification tests"""
        print("🎯 AREA9 VERIFICATION TEST - Supply Chain Management & Vendor Relations")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Run the 3 verification tests
        print("Running Area9 Verification Tests...")
        print("-" * 40)
        
        self.test_assessment_schema_area9()
        self.test_knowledge_base_areas_area9()
        self.test_template_generation_area9()
        
        # Summary
        print("=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print("\nFAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['details']}")
        
        print("\nAREA9 VERIFICATION RESULT:")
        if len(passed_tests) == len(self.test_results):
            print("✅ ALL TESTS PASSED - Area9 backend is fully operational")
            return True
        else:
            print("❌ SOME TESTS FAILED - Area9 backend needs attention")
            return False

def main():
    """Main execution"""
    tester = Area9VerificationTest()
    success = tester.run_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()