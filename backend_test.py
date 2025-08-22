#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST - Both Issues Fixed
Testing Resolution of Core Issues:
1. Knowledge Base REMOVED from Provider Account
2. Client-Provider Marketplace Integration IMPLEMENTED
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://readiness-hub-2.preview.emergentagent.com/api"

# Test Credentials
PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class FinalVerificationTester:
    def __init__(self):
        self.provider_token = None
        self.client_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_user(self, credentials, user_type):
        """Authenticate user and return token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=credentials)
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.log_test(f"{user_type} Authentication", "PASS", f"Successfully authenticated {credentials['email']}")
                return token
            else:
                self.log_test(f"{user_type} Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test(f"{user_type} Authentication", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_provider_kb_restrictions(self):
        """Test Issue 1: Knowledge Base REMOVED from Provider Account"""
        print("\n🔒 TESTING ISSUE 1: Knowledge Base REMOVED from Provider Account")
        
        if not self.provider_token:
            self.log_test("Provider KB Test Setup", "FAIL", "No provider token available")
            return
        
        headers = {"Authorization": f"Bearer {self.provider_token}"}
        
        # Test 1.1: Knowledge Base Areas Access (should be 402/403)
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB Areas Access Restriction", "PASS", f"Correctly blocked with {response.status_code}")
            else:
                self.log_test("Provider KB Areas Access Restriction", "FAIL", f"Expected 402/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Provider KB Areas Access Restriction", "FAIL", f"Exception: {str(e)}")
        
        # Test 1.2: Knowledge Base Template Download (should be 402/403)
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/generate-template/area1/template", headers=headers)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB Template Download Restriction", "PASS", f"Correctly blocked with {response.status_code}")
            else:
                self.log_test("Provider KB Template Download Restriction", "FAIL", f"Expected 402/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Provider KB Template Download Restriction", "FAIL", f"Exception: {str(e)}")
        
        # Test 1.3: Knowledge Base AI Assistance (should be 402/403)
        try:
            response = self.session.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                       headers=headers,
                                       json={"question": "How do I get started with business licensing?"})
            if response.status_code in [402, 403]:
                self.log_test("Provider KB AI Assistance Restriction", "PASS", f"Correctly blocked with {response.status_code}")
            else:
                self.log_test("Provider KB AI Assistance Restriction", "FAIL", f"Expected 402/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Provider KB AI Assistance Restriction", "FAIL", f"Exception: {str(e)}")
        
        # Test 1.4: Knowledge Base Contextual Cards (should be 402/403)
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/contextual-cards/area1", headers=headers)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB Contextual Cards Restriction", "PASS", f"Correctly blocked with {response.status_code}")
            else:
                self.log_test("Provider KB Contextual Cards Restriction", "FAIL", f"Expected 402/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Provider KB Contextual Cards Restriction", "FAIL", f"Exception: {str(e)}")
    
    def test_client_marketplace_integration(self):
        """Test Issue 2: Client-Provider Marketplace Integration IMPLEMENTED"""
        print("\n🛒 TESTING ISSUE 2: Client-Provider Marketplace Integration IMPLEMENTED")
        
        if not self.client_token:
            self.log_test("Client Marketplace Test Setup", "FAIL", "No client token available")
            return
        
        client_headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test 2.1: Client can access marketplace (my service requests)
        try:
            response = self.session.get(f"{BACKEND_URL}/service-requests/my", headers=client_headers)
            if response.status_code == 200:
                self.log_test("Client Marketplace Access", "PASS", "Client can access service requests")
            else:
                self.log_test("Client Marketplace Access", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Client Marketplace Access", "FAIL", f"Exception: {str(e)}")
        
        # Test 2.2: Client can create service request (marketplace functionality)
        try:
            service_request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with technology and security infrastructure setup for marketplace integration testing",
                "priority": "high"
            }
            response = self.session.post(f"{BACKEND_URL}/service-requests/professional-help", 
                                       headers=client_headers,
                                       json=service_request_data)
            if response.status_code == 200:
                request_data = response.json()
                request_id = request_data.get("request_id")
                self.log_test("Client Service Request Creation", "PASS", f"Created request: {request_id}")
                return request_id
            else:
                self.log_test("Client Service Request Creation", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Client Service Request Creation", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_provider_marketplace_functionality(self, request_id=None):
        """Test provider side of marketplace integration"""
        print("\n👥 TESTING PROVIDER MARKETPLACE FUNCTIONALITY")
        
        if not self.provider_token:
            self.log_test("Provider Marketplace Test Setup", "FAIL", "No provider token available")
            return
        
        provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
        
        # Test 2.3: Provider can view notifications (available endpoint)
        try:
            response = self.session.get(f"{BACKEND_URL}/provider/notifications", headers=provider_headers)
            if response.status_code == 200:
                notifications_data = response.json()
                notification_count = len(notifications_data.get("notifications", []))
                self.log_test("Provider View Notifications", "PASS", f"Found {notification_count} notifications")
            else:
                self.log_test("Provider View Notifications", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Provider View Notifications", "FAIL", f"Exception: {str(e)}")
        
        # Test 2.4: Provider can respond to service request (if we have one)
        if request_id:
            try:
                provider_response_data = {
                    "request_id": request_id,
                    "proposed_fee": 2000.00,
                    "estimated_timeline": "2-4 weeks",
                    "proposal_note": "I can help you set up a comprehensive technology and security infrastructure. My approach includes security assessment, infrastructure design, implementation, and ongoing support."
                }
                response = self.session.post(f"{BACKEND_URL}/provider/respond-to-request", 
                                           headers=provider_headers,
                                           json=provider_response_data)
                if response.status_code == 200:
                    self.log_test("Provider Service Response", "PASS", "Provider successfully responded to service request")
                else:
                    self.log_test("Provider Service Response", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("Provider Service Response", "FAIL", f"Exception: {str(e)}")
        
        # Test 2.5: Provider can view their services/engagements
        try:
            response = self.session.get(f"{BACKEND_URL}/engagements/my-services", headers=provider_headers)
            if response.status_code == 200:
                services_data = response.json()
                service_count = len(services_data.get("services", []))
                self.log_test("Provider View My Services", "PASS", f"Found {service_count} services")
            else:
                self.log_test("Provider View My Services", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Provider View My Services", "FAIL", f"Exception: {str(e)}")
    
    def test_complete_marketplace_workflow(self, request_id=None):
        """Test complete client-provider marketplace workflow"""
        print("\n🔄 TESTING COMPLETE MARKETPLACE WORKFLOW")
        
        if not request_id or not self.client_token:
            self.log_test("Complete Workflow Test Setup", "FAIL", "Missing request_id or client token")
            return
        
        client_headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test 2.6: Client can view provider responses
        try:
            response = self.session.get(f"{BACKEND_URL}/service-requests/{request_id}/responses", headers=client_headers)
            if response.status_code == 200:
                responses_data = response.json()
                response_count = len(responses_data.get("responses", []))
                self.log_test("Client View Provider Responses", "PASS", f"Found {response_count} provider responses")
                
                # If we have responses, test engagement creation
                if response_count > 0:
                    provider_response = responses_data["responses"][0]
                    provider_id = provider_response.get("provider_id")
                    
                    # Test 2.7: Client can create engagement (hire provider)
                    try:
                        engagement_data = {
                            "request_id": request_id,
                            "provider_id": provider_id
                        }
                        response = self.session.post(f"{BACKEND_URL}/engagements", 
                                                   headers=client_headers,
                                                   json=engagement_data)
                        if response.status_code == 200:
                            engagement = response.json()
                            engagement_id = engagement.get("engagement_id")
                            self.log_test("Client Create Engagement", "PASS", f"Created engagement: {engagement_id}")
                        else:
                            self.log_test("Client Create Engagement", "FAIL", f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_test("Client Create Engagement", "FAIL", f"Exception: {str(e)}")
            else:
                self.log_test("Client View Provider Responses", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Client View Provider Responses", "FAIL", f"Exception: {str(e)}")
    
    def test_client_kb_access(self):
        """Test that client still has Knowledge Base access (should work)"""
        print("\n📚 TESTING CLIENT KNOWLEDGE BASE ACCESS (Should Work)")
        
        if not self.client_token:
            self.log_test("Client KB Test Setup", "FAIL", "No client token available")
            return
        
        client_headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test: Client can access Knowledge Base areas
        try:
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas", headers=client_headers)
            if response.status_code == 200:
                areas_data = response.json()
                area_count = len(areas_data.get("areas", []))
                self.log_test("Client KB Areas Access", "PASS", f"Client can access {area_count} KB areas")
            else:
                self.log_test("Client KB Areas Access", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Client KB Areas Access", "FAIL", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("🎯 FINAL VERIFICATION TEST - Both Issues Fixed")
        print("=" * 60)
        
        # Authenticate users
        self.provider_token = self.authenticate_user(PROVIDER_CREDENTIALS, "Provider")
        self.client_token = self.authenticate_user(CLIENT_CREDENTIALS, "Client")
        
        # Test Issue 1: Knowledge Base REMOVED from Provider Account
        self.test_provider_kb_restrictions()
        
        # Test Issue 2: Client-Provider Marketplace Integration IMPLEMENTED
        request_id = self.test_client_marketplace_integration()
        self.test_provider_marketplace_functionality(request_id)
        self.test_complete_marketplace_workflow(request_id)
        
        # Verify client still has KB access (should work)
        self.test_client_kb_access()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FINAL VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 ISSUE VERIFICATION RESULTS:")
        
        # Issue 1 Analysis
        kb_restriction_tests = [t for t in self.test_results if "KB" in t["test"] and "Provider" in t["test"] and "Restriction" in t["test"]]
        kb_restrictions_passed = len([t for t in kb_restriction_tests if t["status"] == "PASS"])
        
        if kb_restrictions_passed == len(kb_restriction_tests) and len(kb_restriction_tests) > 0:
            print("✅ ISSUE 1 RESOLVED: Knowledge Base REMOVED from Provider Account")
        else:
            print("❌ ISSUE 1 NOT RESOLVED: Provider still has Knowledge Base access")
        
        # Issue 2 Analysis
        marketplace_tests = [t for t in self.test_results if any(keyword in t["test"] for keyword in ["Marketplace", "Service Request", "Provider Response", "Engagement"])]
        marketplace_passed = len([t for t in marketplace_tests if t["status"] == "PASS"])
        
        if marketplace_passed >= len(marketplace_tests) * 0.8:  # 80% success rate for marketplace
            print("✅ ISSUE 2 RESOLVED: Client-Provider Marketplace Integration IMPLEMENTED")
        else:
            print("❌ ISSUE 2 NOT RESOLVED: Marketplace integration not working properly")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   {result['details']}")

if __name__ == "__main__":
    tester = FinalVerificationTester()
    tester.run_all_tests()