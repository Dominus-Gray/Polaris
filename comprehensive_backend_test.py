#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Polaris System
Tests all endpoints and user flows as specified in the review request
"""

import requests
import json
import uuid
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://frontend-sync-3.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ComprehensiveBackendTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = {
            "authentication": {},
            "assessment_system": {},
            "service_requests": {},
            "knowledge_base": {},
            "analytics": {},
            "engagements": {},
            "payments": {},
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def log_test_result(self, test_name, success, details=""):
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            self.log_result(f"✅ {test_name}: PASS {details}")
        else:
            self.test_results["failed_tests"] += 1
            self.log_result(f"❌ {test_name}: FAIL {details}")
            self.test_results["errors"].append(f"{test_name}: {details}")
    
    def login_all_users(self):
        """Login all QA users and store tokens"""
        self.log_result("🔐 Authenticating all QA users...")
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": creds["email"],
                    "password": creds["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data["access_token"]
                    self.log_test_result(f"{role.title()} Authentication", True)
                else:
                    self.log_test_result(f"{role.title()} Authentication", False, f"Status: {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test_result(f"{role.title()} Authentication", False, str(e))
                return False
        
        return True
    
    def test_assessment_system(self):
        """Test complete assessment system flow"""
        self.log_result("\n📋 Testing Assessment System...")
        
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test 1: Get assessment schema
        try:
            response = requests.get(f"{BASE_URL}/assessment/schema", headers=headers)
            self.log_test_result("Assessment Schema Retrieval", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Assessment Schema Retrieval", False, str(e))
        
        # Test 2: Create assessment session
        try:
            response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get("session_id")
                self.log_test_result("Assessment Session Creation", True, f"Session ID: {session_id[:8]}...")
                
                # Test 3: Submit assessment response
                if session_id:
                    response = requests.post(f"{BASE_URL}/assessment/session/{session_id}/response", 
                                           json={"question_id": "q1_1", "answer": "No, I need help"}, 
                                           headers=headers)
                    self.log_test_result("Assessment Response Submission", 
                                       response.status_code == 200,
                                       f"Status: {response.status_code}")
            else:
                self.log_test_result("Assessment Session Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Assessment Session Creation", False, str(e))
    
    def test_service_request_system(self):
        """Test service request and provider matching system"""
        self.log_result("\n🔧 Testing Service Request System...")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        # Test 1: Create service request
        try:
            service_request_data = {
                "area_id": "area5",
                "budget_range": "$1,000-$2,500",
                "description": "Need cybersecurity infrastructure setup",
                "timeline": "2 weeks"
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json=service_request_data, 
                                   headers=client_headers)
            
            if response.status_code == 200:
                request_data = response.json()
                request_id = request_data.get("request_id")
                self.log_test_result("Service Request Creation", True, f"Request ID: {request_id[:8]}...")
                
                # Test 2: Provider respond to request
                if request_id:
                    provider_response = {
                        "request_id": request_id,
                        "proposed_fee": 1500,
                        "estimated_timeline": "10 business days",
                        "proposal_note": "Comprehensive cybersecurity assessment and implementation"
                    }
                    
                    response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                           json=provider_response, 
                                           headers=provider_headers)
                    self.log_test_result("Provider Response", 
                                       response.status_code == 200,
                                       f"Status: {response.status_code}")
                    
                    # Test 3: Get service request responses
                    response = requests.get(f"{BASE_URL}/service-requests/{request_id}/responses", 
                                          headers=client_headers)
                    self.log_test_result("Service Request Responses Retrieval", 
                                       response.status_code == 200,
                                       f"Status: {response.status_code}")
            else:
                self.log_test_result("Service Request Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Service Request Creation", False, str(e))
    
    def test_knowledge_base_system(self):
        """Test Phase 3 Knowledge Base AI-powered features"""
        self.log_result("\n📚 Testing Knowledge Base System...")
        
        navigator_headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test 1: Seed knowledge base content
        try:
            response = requests.post(f"{BASE_URL}/knowledge-base/seed-content", 
                                   headers=navigator_headers)
            self.log_test_result("KB Content Seeding", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Content Seeding", False, str(e))
        
        # Test 2: Get KB articles
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/articles", 
                                  headers=client_headers)
            self.log_test_result("KB Articles Retrieval", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Articles Retrieval", False, str(e))
        
        # Test 3: Get contextual cards
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/contextual-cards?context=assessment", 
                                  headers=client_headers)
            self.log_test_result("KB Contextual Cards", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Contextual Cards", False, str(e))
        
        # Test 4: AI assistance
        try:
            ai_request = {
                "question": "How do I improve my cybersecurity posture for government contracting?",
                "context": {"business_type": "small business", "focus": "procurement readiness"},
                "area_id": "area5"
            }
            response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                   json=ai_request, 
                                   headers=client_headers)
            self.log_test_result("KB AI Assistance", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB AI Assistance", False, str(e))
        
        # Test 5: Next best actions
        try:
            nba_request = {
                "user_id": "test-user-id",
                "current_gaps": ["cybersecurity", "financial_operations"],
                "completed_areas": ["business_formation"]
            }
            response = requests.post(f"{BASE_URL}/knowledge-base/next-best-actions", 
                                   json=nba_request, 
                                   headers=client_headers)
            self.log_test_result("KB Next Best Actions", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Next Best Actions", False, str(e))
    
    def test_analytics_system(self):
        """Test analytics and reporting system"""
        self.log_result("\n📊 Testing Analytics System...")
        
        navigator_headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test 1: Post analytics data
        try:
            analytics_data = {
                "area_id": "area5",
                "resource_type": "free_resource",
                "action": "accessed"
            }
            response = requests.post(f"{BASE_URL}/analytics/resource-access", 
                                   json=analytics_data, 
                                   headers=client_headers)
            self.log_test_result("Analytics Data Posting", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Analytics Data Posting", False, str(e))
        
        # Test 2: Get navigator analytics
        try:
            response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                  headers=navigator_headers)
            self.log_test_result("Navigator Analytics Retrieval", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Navigator Analytics Retrieval", False, str(e))
        
        # Test 3: KB analytics
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/analytics", 
                                  headers=navigator_headers)
            self.log_test_result("KB Analytics", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Analytics", False, str(e))
    
    def test_payment_system(self):
        """Test payment integration with Stripe"""
        self.log_result("\n💳 Testing Payment System...")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test 1: Knowledge base payment
        try:
            payment_data = {
                "package_id": "knowledge_base_all",
                "origin_url": "https://frontend-sync-3.preview.emergentagent.com"
            }
            response = requests.post(f"{BASE_URL}/payments/knowledge-base", 
                                   json=payment_data, 
                                   headers=client_headers)
            self.log_test_result("KB Payment Session Creation", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("KB Payment Session Creation", False, str(e))
    
    def test_engagements_system(self):
        """Test Phase 2 Engagements workflow"""
        self.log_result("\n🤝 Testing Engagements System...")
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        # Test 1: Get client engagements
        try:
            response = requests.get(f"{BASE_URL}/engagements/my-services", 
                                  headers=client_headers)
            self.log_test_result("Client Engagements Retrieval", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Client Engagements Retrieval", False, str(e))
        
        # Test 2: Get provider engagements
        try:
            response = requests.get(f"{BASE_URL}/engagements/my-services", 
                                  headers=provider_headers)
            self.log_test_result("Provider Engagements Retrieval", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Provider Engagements Retrieval", False, str(e))
    
    def test_agency_license_system(self):
        """Test agency license generation system"""
        self.log_result("\n🏢 Testing Agency License System...")
        
        agency_headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
        
        # Test 1: Generate licenses
        try:
            license_data = {"quantity": 2}
            response = requests.post(f"{BASE_URL}/agency/licenses/generate", 
                                   json=license_data, 
                                   headers=agency_headers)
            self.log_test_result("License Generation", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("License Generation", False, str(e))
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        self.log_result("🚀 Starting Comprehensive Backend Testing")
        self.log_result("=" * 80)
        
        # Step 1: Authentication
        if not self.login_all_users():
            self.log_result("❌ Authentication failed, aborting tests")
            return False
        
        # Step 2: Core Systems Testing
        self.test_assessment_system()
        self.test_service_request_system()
        self.test_knowledge_base_system()
        self.test_analytics_system()
        self.test_payment_system()
        self.test_engagements_system()
        self.test_agency_license_system()
        
        return True
    
    def print_final_report(self):
        """Print comprehensive test results"""
        self.log_result("\n" + "=" * 80)
        self.log_result("📊 COMPREHENSIVE BACKEND TEST REPORT")
        self.log_result("=" * 80)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.log_result(f"Total Tests: {total}")
        self.log_result(f"Passed: {passed}")
        self.log_result(f"Failed: {failed}")
        self.log_result(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            self.log_result(f"\n❌ FAILED TESTS ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                self.log_result(f"  - {error}")
        else:
            self.log_result("\n✅ ALL TESTS PASSED!")
        
        return success_rate >= 90  # Consider 90%+ success rate as overall success

def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    
    try:
        success = tester.run_comprehensive_tests()
        overall_success = tester.print_final_report()
        
        if overall_success:
            print("\n🎉 COMPREHENSIVE BACKEND TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n⚠️ COMPREHENSIVE BACKEND TESTING COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()