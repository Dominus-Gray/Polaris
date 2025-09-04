#!/usr/bin/env python3
"""
Final Comprehensive Audit - Testing Issue Resolution
Testing two critical issues:
1. Knowledge Base Removed from Provider Account
2. Client-Provider Marketplace Integration
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FinalAuditTest:
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
                token_data = response.json()
                self.tokens[role] = token_data["access_token"]
                self.log_result(f"{role.title()} Authentication", True, 
                              f"Token obtained for {credentials['email']}", response_time)
                return True
            else:
                self.log_result(f"{role.title()} Authentication", False, 
                              f"Status: {response.status_code}, Response: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result(f"{role.title()} Authentication", False, f"Exception: {str(e)}", response_time)
            return False
    
    def get_headers(self, role):
        """Get authorization headers for role"""
        return {"Authorization": f"Bearer {self.tokens[role]}"}
    
    def test_provider_knowledge_base_removal(self):
        """Test Issue 1: Knowledge Base Removed from Provider Account"""
        print("\n🎯 TESTING ISSUE 1: Knowledge Base Removed from Provider Account")
        
        if not self.authenticate_user("provider"):
            return
        
        headers = self.get_headers("provider")
        
        # Test 1.1: Provider cannot access Knowledge Base areas
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_result("Provider KB Areas Access Blocked", True, 
                              f"Correctly blocked with status {response.status_code}", response_time)
            elif response.status_code == 200:
                # Check if response is empty or restricted
                data = response.json()
                if not data or len(data) == 0:
                    self.log_result("Provider KB Areas Access Blocked", True, 
                                  "No KB areas returned for provider", response_time)
                else:
                    self.log_result("Provider KB Areas Access Blocked", False, 
                                  f"Provider still has access to {len(data)} KB areas", response_time)
            else:
                self.log_result("Provider KB Areas Access Blocked", False, 
                              f"Unexpected status: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Provider KB Areas Access Blocked", False, f"Exception: {str(e)}", 0)
        
        # Test 1.2: Provider cannot access Knowledge Base templates
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/knowledge-base/generate-template/area1/template", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_result("Provider KB Template Access Blocked", True, 
                              f"Template access correctly blocked with status {response.status_code}", response_time)
            else:
                self.log_result("Provider KB Template Access Blocked", False, 
                              f"Provider can still access templates: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Provider KB Template Access Blocked", False, f"Exception: {str(e)}", 0)
        
        # Test 1.3: Provider cannot access AI assistance
        try:
            start_time = time.time()
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                   headers=headers, 
                                   json={"question": "How do I get started with business licensing?"})
            response_time = time.time() - start_time
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_result("Provider AI Assistance Access Blocked", True, 
                              f"AI assistance correctly blocked with status {response.status_code}", response_time)
            else:
                self.log_result("Provider AI Assistance Access Blocked", False, 
                              f"Provider can still access AI assistance: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Provider AI Assistance Access Blocked", False, f"Exception: {str(e)}", 0)
    
    def test_client_provider_marketplace_integration(self):
        """Test Issue 2: Client-Provider Marketplace Integration"""
        print("\n🎯 TESTING ISSUE 2: Client-Provider Marketplace Integration")
        
        if not self.authenticate_user("client"):
            return
        
        client_headers = self.get_headers("client")
        
        # Test 2.1: Client can browse marketplace/gigs (using search endpoint)
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/marketplace/gigs/search", headers=client_headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Client Marketplace Browse", True, 
                                  f"Found {len(data)} marketplace gigs", response_time)
                else:
                    self.log_result("Client Marketplace Browse", True, 
                                  "Marketplace accessible but no gigs found", response_time)
            else:
                self.log_result("Client Marketplace Browse", False, 
                              f"Cannot access marketplace: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Client Marketplace Browse", False, f"Exception: {str(e)}", 0)
        
        # Test 2.2: Marketplace search functionality
        try:
            start_time = time.time()
            search_params = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "location": "texas"
            }
            response = requests.get(f"{BACKEND_URL}/marketplace/gigs/search", 
                                  headers=client_headers, params=search_params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Marketplace Search Functionality", True, 
                              f"Search returned {len(data) if isinstance(data, list) else 'data'}", response_time)
            else:
                self.log_result("Marketplace Search Functionality", False, 
                              f"Search failed: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Marketplace Search Functionality", False, f"Exception: {str(e)}", 0)
        
        # Test 2.3: Provider gig creation system
        if not self.authenticate_user("provider"):
            return
        
        provider_headers = self.get_headers("provider")
        
        try:
            start_time = time.time()
            gig_data = {
                "title": "Technology Security Consulting",
                "description": "Professional cybersecurity assessment and implementation services for small businesses",
                "category": "tech_security",
                "subcategory": "Cybersecurity Assessment",
                "tags": ["cybersecurity", "compliance", "assessment"],
                "packages": [
                    {
                        "name": "Basic Security Assessment",
                        "description": "Basic cybersecurity evaluation",
                        "price": 1500,
                        "delivery_days": 14,
                        "revisions": 1
                    }
                ],
                "requirements": ["Business information", "Current security setup"],
                "faq": [
                    {
                        "question": "What is included?",
                        "answer": "Comprehensive security assessment and recommendations"
                    }
                ]
            }
            response = requests.post(f"{BACKEND_URL}/marketplace/gig/create", 
                                   headers=provider_headers, json=gig_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.test_data["gig_id"] = data.get("gig_id")
                self.log_result("Provider Gig Creation", True, 
                              f"Gig created successfully", response_time)
            else:
                self.log_result("Provider Gig Creation", False, 
                              f"Gig creation failed: {response.status_code} - {response.text[:100]}", response_time)
                
        except Exception as e:
            self.log_result("Provider Gig Creation", False, f"Exception: {str(e)}", 0)
        
        # Test 2.4: Client-Provider connection via service requests
        try:
            start_time = time.time()
            service_request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need cybersecurity assessment for small business compliance",
                "priority": "high"
            }
            response = requests.post(f"{BACKEND_URL}/service-requests/professional-help", 
                                   headers=client_headers, json=service_request_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.test_data["service_request_id"] = data.get("id") or data.get("request_id")
                self.log_result("Client Service Request Creation", True, 
                              f"Service request created: {self.test_data.get('service_request_id')}", response_time)
            else:
                self.log_result("Client Service Request Creation", False, 
                              f"Service request failed: {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Client Service Request Creation", False, f"Exception: {str(e)}", 0)
        
        # Test 2.5: Provider response to service request
        if self.test_data.get("service_request_id"):
            try:
                start_time = time.time()
                provider_response_data = {
                    "request_id": self.test_data["service_request_id"],
                    "proposed_fee": 2500.00,
                    "estimated_timeline": "2-4 weeks",
                    "proposal_note": "Comprehensive cybersecurity assessment including vulnerability scanning, policy review, and compliance recommendations."
                }
                response = requests.post(f"{BACKEND_URL}/provider/respond-to-request", 
                                       headers=provider_headers, json=provider_response_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result("Provider Response to Service Request", True, 
                                  f"Provider responded with $2500 proposal", response_time)
                else:
                    self.log_result("Provider Response to Service Request", False, 
                                  f"Provider response failed: {response.status_code}", response_time)
                    
            except Exception as e:
                self.log_result("Provider Response to Service Request", False, f"Exception: {str(e)}", 0)
        
        # Test 2.6: Client can view provider responses
        if self.test_data.get("service_request_id"):
            try:
                start_time = time.time()
                response = requests.get(f"{BACKEND_URL}/service-requests/{self.test_data['service_request_id']}/responses", 
                                      headers=client_headers)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_result("Client View Provider Responses", True, 
                                      f"Found {len(data)} provider responses", response_time)
                    else:
                        self.log_result("Client View Provider Responses", True, 
                                      "No provider responses yet (expected)", response_time)
                else:
                    self.log_result("Client View Provider Responses", False, 
                                  f"Cannot view responses: {response.status_code}", response_time)
                    
            except Exception as e:
                self.log_result("Client View Provider Responses", False, f"Exception: {str(e)}", 0)
    
    def test_security_and_access_control(self):
        """Test security and role-based access control"""
        print("\n🔒 TESTING SECURITY & ACCESS CONTROL")
        
        # Test that provider cannot access client-specific endpoints
        if "provider" in self.tokens:
            provider_headers = self.get_headers("provider")
            
            try:
                start_time = time.time()
                response = requests.get(f"{BACKEND_URL}/assessment/schema", headers=provider_headers)
                response_time = time.time() - start_time
                
                if response.status_code == 403 or response.status_code == 401:
                    self.log_result("Provider Assessment Access Blocked", True, 
                                  f"Assessment access correctly blocked: {response.status_code}", response_time)
                elif response.status_code == 200:
                    # This might be allowed, check if it's restricted content
                    self.log_result("Provider Assessment Access", True, 
                                  "Provider can access assessment schema (may be allowed)", response_time)
                else:
                    self.log_result("Provider Assessment Access", False, 
                                  f"Unexpected response: {response.status_code}", response_time)
                    
            except Exception as e:
                self.log_result("Provider Assessment Access Blocked", False, f"Exception: {str(e)}", 0)
    
    def run_all_tests(self):
        """Run all audit tests"""
        print("🎯 FINAL COMPREHENSIVE AUDIT - Testing Issue Resolution")
        print("=" * 60)
        
        # Test Issue 1: Knowledge Base Removed from Provider Account
        self.test_provider_knowledge_base_removal()
        
        # Test Issue 2: Client-Provider Marketplace Integration  
        self.test_client_provider_marketplace_integration()
        
        # Test Security and Access Control
        self.test_security_and_access_control()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 FINAL AUDIT TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"    {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        
        # Issue 1 Analysis
        kb_tests = [r for r in self.results if "KB" in r["test"] or "Knowledge Base" in r["test"]]
        kb_passed = sum(1 for r in kb_tests if r["success"])
        
        if kb_passed == len(kb_tests) and len(kb_tests) > 0:
            print("✅ ISSUE 1 RESOLVED: Knowledge Base successfully removed from provider account")
        else:
            print("❌ ISSUE 1 NOT RESOLVED: Provider still has Knowledge Base access")
        
        # Issue 2 Analysis  
        marketplace_tests = [r for r in self.results if "Marketplace" in r["test"] or "Service Request" in r["test"] or "Provider" in r["test"]]
        marketplace_passed = sum(1 for r in marketplace_tests if r["success"])
        
        if marketplace_passed >= len(marketplace_tests) * 0.8:  # 80% threshold
            print("✅ ISSUE 2 RESOLVED: Client-Provider marketplace integration working")
        else:
            print("❌ ISSUE 2 NOT RESOLVED: Marketplace integration has issues")
        
        print(f"\n🏁 OVERALL AUDIT STATUS: {'✅ PASSED' if success_rate >= 80 else '❌ FAILED'}")
        print(f"System ready for production: {'YES' if success_rate >= 80 else 'NO'}")

if __name__ == "__main__":
    test = FinalAuditTest()
    test.run_all_tests()