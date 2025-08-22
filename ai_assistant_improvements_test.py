#!/usr/bin/env python3
"""
AI Assistant Improvements Testing
Testing the AI assistant concise responses, paywall protection, and access control logic
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

class AIAssistantImprovementsTest:
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
                              f"Successfully authenticated {credentials['email']}", response_time)
                return token
            else:
                self.log_result(f"Authentication - {role.title()}", False, 
                              f"Failed to authenticate: {response.status_code} - {response.text}", response_time)
                return None
                
        except Exception as e:
            self.log_result(f"Authentication - {role.title()}", False, f"Exception: {str(e)}", response_time)
            return None
    
    def create_regular_user(self):
        """Create a regular user (non-test) for paywall testing"""
        try:
            start_time = time.time()
            
            # Generate unique email for regular user
            unique_id = str(uuid.uuid4())[:8]
            regular_user_email = f"regular.user.{unique_id}@example.com"
            
            # First, we need to create a license code (as a navigator)
            navigator_token = self.authenticate_user("navigator")
            if not navigator_token:
                self.log_result("Create Regular User - License Generation", False, "Failed to authenticate navigator")
                return None
            
            # Generate license codes (need to use agency token, not navigator)
            agency_token = self.authenticate_user("agency")
            if not agency_token:
                self.log_result("Create Regular User - Agency Authentication", False, "Failed to authenticate agency")
                return None
                
            headers = {"Authorization": f"Bearer {agency_token}"}
            license_response = requests.post(f"{BACKEND_URL}/agency/licenses/generate", 
                                           json={"quantity": 1}, headers=headers)
            
            if license_response.status_code != 200:
                self.log_result("Create Regular User - License Generation", False, 
                              f"Failed to generate license: {license_response.status_code}")
                return None
            
            license_code = license_response.json()["licenses"][0]["license_code"]
            
            # Register regular user with license code
            user_data = {
                "email": regular_user_email,
                "password": "RegularUser123!",
                "role": "client",
                "terms_accepted": True,
                "license_code": license_code
            }
            
            register_response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
            response_time = time.time() - start_time
            
            if register_response.status_code == 200:
                # Login the regular user
                login_response = requests.post(f"{BACKEND_URL}/auth/login", 
                                             json={"email": regular_user_email, "password": "RegularUser123!"})
                
                if login_response.status_code == 200:
                    regular_token = login_response.json()["access_token"]
                    self.tokens["regular"] = regular_token
                    self.test_data["regular_user_email"] = regular_user_email
                    
                    self.log_result("Create Regular User", True, 
                                  f"Created and authenticated regular user: {regular_user_email}", response_time)
                    return regular_token
                else:
                    self.log_result("Create Regular User", False, 
                                  f"Failed to login regular user: {login_response.status_code}", response_time)
                    return None
            else:
                self.log_result("Create Regular User", False, 
                              f"Failed to register regular user: {register_response.status_code} - {register_response.text}", response_time)
                return None
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result("Create Regular User", False, f"Exception: {str(e)}", response_time)
            return None
    
    def test_ai_assistant_concise_responses(self):
        """Test AI Assistant Concise Responses - verify responses are under 200 words with clear structure"""
        try:
            # Test with QA client credentials
            client_token = self.tokens.get("client") or self.authenticate_user("client")
            if not client_token:
                self.log_result("AI Assistant Concise Responses", False, "Failed to authenticate client")
                return
            
            headers = {"Authorization": f"Bearer {client_token}"}
            
            # Test questions from the review request
            test_questions = [
                "How do I get started with business licensing?",
                "What documents do I need for financial compliance?"
            ]
            
            for question in test_questions:
                start_time = time.time()
                
                payload = {
                    "question": question,
                    "area_id": "area1"  # Business Formation area
                }
                
                response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                       json=payload, headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    ai_response = response.json()
                    
                    # Check if response has proper structure
                    if "response" in ai_response:
                        response_text = ai_response["response"]
                        word_count = len(response_text.split())
                        
                        # Check if response is concise (under 200 words)
                        is_concise = word_count <= 200
                        
                        # Check for clear structure (should have organized content)
                        has_structure = any(marker in response_text.lower() for marker in 
                                          ["1.", "2.", "•", "-", "first", "second", "step", "process"])
                        
                        if is_concise and has_structure:
                            self.log_result(f"AI Assistant Concise Response - '{question[:30]}...'", True, 
                                          f"Response: {word_count} words, structured format", response_time)
                        else:
                            self.log_result(f"AI Assistant Concise Response - '{question[:30]}...'", False, 
                                          f"Response: {word_count} words, structured: {has_structure}", response_time)
                    else:
                        self.log_result(f"AI Assistant Concise Response - '{question[:30]}...'", False, 
                                      f"Missing 'response' field in API response", response_time)
                else:
                    self.log_result(f"AI Assistant Concise Response - '{question[:30]}...'", False, 
                                  f"API error: {response.status_code} - {response.text}", response_time)
                    
        except Exception as e:
            self.log_result("AI Assistant Concise Responses", False, f"Exception: {str(e)}")
    
    def test_paywall_protection_regular_user(self):
        """Test Paywall Protection with regular user - should return 402 error"""
        try:
            # Create regular user if not exists
            regular_token = self.tokens.get("regular") or self.create_regular_user()
            if not regular_token:
                self.log_result("Paywall Protection - Regular User", False, "Failed to create regular user")
                return
            
            start_time = time.time()
            headers = {"Authorization": f"Bearer {regular_token}"}
            
            payload = {
                "question": "How do I get started with business licensing?",
                "area_id": "area1"
            }
            
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                   json=payload, headers=headers)
            response_time = time.time() - start_time
            
            # Should return 402 Payment Required for regular users
            if response.status_code == 402:
                response_data = response.json()
                
                # Check for proper error message structure
                has_error_code = "error_code" in response_data.get("detail", {})
                has_proper_message = "payment" in str(response_data).lower() or "unlock" in str(response_data).lower()
                
                if has_error_code or has_proper_message:
                    self.log_result("Paywall Protection - Regular User", True, 
                                  f"Correctly returned 402 with proper error message", response_time)
                else:
                    self.log_result("Paywall Protection - Regular User", False, 
                                  f"402 returned but missing proper error structure: {response_data}", response_time)
            else:
                self.log_result("Paywall Protection - Regular User", False, 
                              f"Expected 402, got {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("Paywall Protection - Regular User", False, f"Exception: {str(e)}")
    
    def test_paywall_protection_test_user(self):
        """Test Paywall Protection with test user (@polaris.example.com) - should work"""
        try:
            client_token = self.tokens.get("client") or self.authenticate_user("client")
            if not client_token:
                self.log_result("Paywall Protection - Test User", False, "Failed to authenticate test user")
                return
            
            start_time = time.time()
            headers = {"Authorization": f"Bearer {client_token}"}
            
            payload = {
                "question": "How do I get started with business licensing?",
                "area_id": "area1"
            }
            
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                   json=payload, headers=headers)
            response_time = time.time() - start_time
            
            # Should return 200 for @polaris.example.com users
            if response.status_code == 200:
                response_data = response.json()
                
                if "response" in response_data:
                    self.log_result("Paywall Protection - Test User", True, 
                                  f"Test user has access, response received", response_time)
                else:
                    self.log_result("Paywall Protection - Test User", False, 
                                  f"200 returned but missing response field", response_time)
            else:
                self.log_result("Paywall Protection - Test User", False, 
                              f"Expected 200, got {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("Paywall Protection - Test User", False, f"Exception: {str(e)}")
    
    def test_knowledge_base_access_control(self):
        """Test Knowledge Base Access Control Logic for AI assistant"""
        try:
            # Test with different user types
            test_scenarios = [
                ("client", "Should have access"),
                ("provider", "Should have access"),
                ("navigator", "Should have access"),
                ("agency", "Should have access")
            ]
            
            for role, expected_behavior in test_scenarios:
                token = self.tokens.get(role) or self.authenticate_user(role)
                if not token:
                    self.log_result(f"Access Control - {role.title()}", False, "Failed to authenticate")
                    continue
                
                start_time = time.time()
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test knowledge base areas access
                areas_response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
                response_time = time.time() - start_time
                
                if areas_response.status_code == 200:
                    areas_data = areas_response.json()
                    
                    # Check if areas are returned (should be in "areas" key)
                    areas_list = areas_data.get("areas", [])
                    if isinstance(areas_list, list) and len(areas_list) > 0:
                        # Test AI assistance access for this role
                        ai_start_time = time.time()
                        payload = {
                            "question": "What documents do I need for financial compliance?",
                            "area_id": "area2"
                        }
                        
                        ai_response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                                  json=payload, headers=headers)
                        ai_response_time = time.time() - ai_start_time
                        
                        if ai_response.status_code == 200:
                            self.log_result(f"Access Control - {role.title()}", True, 
                                          f"{expected_behavior} - AI assistance working", 
                                          response_time + ai_response_time)
                        else:
                            self.log_result(f"Access Control - {role.title()}", False, 
                                          f"KB areas accessible but AI assistance failed: {ai_response.status_code}", 
                                          response_time + ai_response_time)
                    else:
                        self.log_result(f"Access Control - {role.title()}", False, 
                                      f"No knowledge base areas returned", response_time)
                else:
                    self.log_result(f"Access Control - {role.title()}", False, 
                                  f"KB areas access failed: {areas_response.status_code}", response_time)
                    
        except Exception as e:
            self.log_result("Knowledge Base Access Control", False, f"Exception: {str(e)}")
    
    def test_error_message_validation(self):
        """Test proper error messages for various scenarios"""
        try:
            # Test with invalid token
            start_time = time.time()
            headers = {"Authorization": "Bearer invalid_token"}
            
            payload = {
                "question": "Test question",
                "area_id": "area1"
            }
            
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                   json=payload, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Error Message Validation - Invalid Token", True, 
                              f"Correctly returned 401 for invalid token", response_time)
            else:
                self.log_result("Error Message Validation - Invalid Token", False, 
                              f"Expected 401, got {response.status_code}", response_time)
            
            # Test with missing question
            if "client" in self.tokens:
                start_time = time.time()
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                
                payload = {
                    "area_id": "area1"
                    # Missing question field
                }
                
                response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                       json=payload, headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code in [400, 422]:  # Bad request or validation error
                    self.log_result("Error Message Validation - Missing Question", True, 
                                  f"Correctly returned {response.status_code} for missing question", response_time)
                else:
                    self.log_result("Error Message Validation - Missing Question", False, 
                                  f"Expected 400/422, got {response.status_code}", response_time)
                    
        except Exception as e:
            self.log_result("Error Message Validation", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all AI assistant improvement tests"""
        print("🎯 AI ASSISTANT IMPROVEMENTS TESTING STARTED")
        print("=" * 60)
        
        # Authenticate all users first
        print("\n📋 AUTHENTICATION PHASE")
        for role in ["client", "provider", "navigator", "agency"]:
            self.authenticate_user(role)
        
        print("\n🤖 AI ASSISTANT CONCISE RESPONSES TESTING")
        self.test_ai_assistant_concise_responses()
        
        print("\n💰 PAYWALL PROTECTION TESTING")
        self.test_paywall_protection_regular_user()
        self.test_paywall_protection_test_user()
        
        print("\n🔐 ACCESS CONTROL TESTING")
        self.test_knowledge_base_access_control()
        
        print("\n⚠️ ERROR MESSAGE VALIDATION")
        self.test_error_message_validation()
        
        # Generate summary
        print("\n" + "=" * 60)
        print("🎯 AI ASSISTANT IMPROVEMENTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 AI ASSISTANT IMPROVEMENTS TESTING COMPLETE")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.results
        }

if __name__ == "__main__":
    tester = AIAssistantImprovementsTest()
    results = tester.run_all_tests()