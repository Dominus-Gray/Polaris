#!/usr/bin/env python3
"""
User Journey Testing for Polaris System
Tests complete end-to-end user journeys as specified in the review request
"""

import requests
import json
import uuid
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://agency-connect-4.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class UserJourneyTester:
    def __init__(self):
        self.tokens = {}
        self.test_data = {}
        self.results = {
            "journeys": {},
            "total_steps": 0,
            "passed_steps": 0,
            "failed_steps": 0,
            "errors": []
        }
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def log_step_result(self, journey, step_name, success, details=""):
        self.results["total_steps"] += 1
        if journey not in self.results["journeys"]:
            self.results["journeys"][journey] = {"steps": [], "success": True}
            
        if success:
            self.results["passed_steps"] += 1
            self.log_result(f"✅ {journey} - {step_name}: PASS {details}")
            self.results["journeys"][journey]["steps"].append(f"✅ {step_name}")
        else:
            self.results["failed_steps"] += 1
            self.log_result(f"❌ {journey} - {step_name}: FAIL {details}")
            self.results["journeys"][journey]["steps"].append(f"❌ {step_name}")
            self.results["journeys"][journey]["success"] = False
            self.results["errors"].append(f"{journey} - {step_name}: {details}")
    
    def login_user(self, role):
        """Login user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": creds["email"],
                "password": creds["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                return True
            else:
                return False
        except Exception:
            return False
    
    def test_client_assessment_journey(self):
        """Test complete client assessment journey"""
        journey = "Client Assessment Journey"
        self.log_result(f"\n🎯 Testing {journey}")
        
        if not self.login_user("client"):
            self.log_step_result(journey, "Client Login", False, "Authentication failed")
            return
        
        self.log_step_result(journey, "Client Login", True)
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Step 1: Create assessment session
        try:
            response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get("session_id")
                self.test_data["assessment_session_id"] = session_id
                self.log_step_result(journey, "Assessment Session Creation", True, f"Session: {session_id[:8]}...")
            else:
                self.log_step_result(journey, "Assessment Session Creation", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_step_result(journey, "Assessment Session Creation", False, str(e))
            return
        
        # Step 2: Submit "No, I need help" response
        try:
            response = requests.post(f"{BASE_URL}/assessment/session/{session_id}/response", 
                                   json={"question_id": "q5_1", "answer": "No, I need help"}, 
                                   headers=headers)
            self.log_step_result(journey, "Gap Response Submission", 
                               response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Gap Response Submission", False, str(e))
        
        # Step 3: Get free resources
        try:
            response = requests.get(f"{BASE_URL}/free-resources?area_id=area5", headers=headers)
            self.log_step_result(journey, "Free Resources Retrieval", 
                               response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Free Resources Retrieval", False, str(e))
        
        # Step 4: Log analytics for resource access
        try:
            analytics_data = {
                "area_id": "area5",
                "resource_type": "free_resource",
                "action": "accessed"
            }
            response = requests.post(f"{BASE_URL}/analytics/resource-access", 
                                   json=analytics_data, headers=headers)
            self.log_step_result(journey, "Analytics Logging", 
                               response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Analytics Logging", False, str(e))
    
    def test_service_request_journey(self):
        """Test complete service request and provider matching journey"""
        journey = "Service Request Journey"
        self.log_result(f"\n🔧 Testing {journey}")
        
        # Login both client and provider
        if not (self.login_user("client") and self.login_user("provider")):
            self.log_step_result(journey, "User Authentication", False, "Login failed")
            return
        
        self.log_step_result(journey, "User Authentication", True)
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        # Step 1: Create service request
        try:
            service_request_data = {
                "area_id": "area5",
                "budget_range": "$2,500-$5,000",
                "description": "Need comprehensive cybersecurity assessment and implementation for government contracting readiness",
                "timeline": "3 weeks"
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json=service_request_data, headers=client_headers)
            
            if response.status_code == 200:
                request_data = response.json()
                request_id = request_data.get("request_id")
                self.test_data["service_request_id"] = request_id
                self.log_step_result(journey, "Service Request Creation", True, f"Request: {request_id[:8]}...")
            else:
                self.log_step_result(journey, "Service Request Creation", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_step_result(journey, "Service Request Creation", False, str(e))
            return
        
        # Step 2: Provider responds to request
        try:
            provider_response = {
                "request_id": request_id,
                "proposed_fee": 2800,
                "estimated_timeline": "15 business days",
                "proposal_note": "Comprehensive cybersecurity assessment including NIST framework implementation, security policy development, and staff training for government contracting compliance."
            }
            
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                   json=provider_response, headers=provider_headers)
            
            if response.status_code == 200:
                response_data = response.json()
                response_id = response_data.get("response_id")
                self.test_data["provider_response_id"] = response_id
                self.log_step_result(journey, "Provider Response", True, f"Response: {response_id[:8]}...")
            else:
                self.log_step_result(journey, "Provider Response", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_step_result(journey, "Provider Response", False, str(e))
            return
        
        # Step 3: Client views responses
        try:
            response = requests.get(f"{BASE_URL}/service-requests/{request_id}/responses", 
                                  headers=client_headers)
            if response.status_code == 200:
                responses_data = response.json()
                responses = responses_data.get("responses", [])
                self.log_step_result(journey, "Response Viewing", True, f"Found {len(responses)} responses")
            else:
                self.log_step_result(journey, "Response Viewing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Response Viewing", False, str(e))
        
        # Step 4: Payment validation
        try:
            payment_data = {
                "request_id": request_id,
                "provider_id": self.test_data.get("provider_response_id", "test-provider-id")
            }
            response = requests.post(f"{BASE_URL}/payments/service-request", 
                                   json=payment_data, headers=client_headers)
            self.log_step_result(journey, "Payment Validation", 
                               response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Payment Validation", False, str(e))
    
    def test_knowledge_base_journey(self):
        """Test knowledge base access and AI assistance journey"""
        journey = "Knowledge Base Journey"
        self.log_result(f"\n📚 Testing {journey}")
        
        if not self.login_user("client"):
            self.log_step_result(journey, "Client Login", False, "Authentication failed")
            return
        
        self.log_step_result(journey, "Client Login", True)
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Step 1: Get contextual KB cards
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/contextual-cards?context=assessment", 
                                  headers=headers)
            if response.status_code == 200:
                cards_data = response.json()
                cards = cards_data.get("cards", [])
                self.log_step_result(journey, "Contextual Cards", True, f"Found {len(cards)} cards")
            else:
                self.log_step_result(journey, "Contextual Cards", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Contextual Cards", False, str(e))
        
        # Step 2: AI assistance request
        try:
            ai_request = {
                "question": "What are the key cybersecurity requirements for government contracting?",
                "context": {"business_area": "cybersecurity", "goal": "government_contracting"},
                "area_id": "area5"
            }
            response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                   json=ai_request, headers=headers)
            if response.status_code == 200:
                ai_data = response.json()
                response_text = ai_data.get("response", "")
                self.log_step_result(journey, "AI Assistance", True, f"Response length: {len(response_text)} chars")
            else:
                self.log_step_result(journey, "AI Assistance", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "AI Assistance", False, str(e))
        
        # Step 3: Next best actions
        try:
            nba_request = {
                "user_id": "test-client-id",
                "current_gaps": ["cybersecurity", "quality_management"],
                "completed_areas": ["business_formation"]
            }
            response = requests.post(f"{BASE_URL}/knowledge-base/next-best-actions", 
                                   json=nba_request, headers=headers)
            if response.status_code == 200:
                nba_data = response.json()
                actions = nba_data.get("actions", [])
                self.log_step_result(journey, "Next Best Actions", True, f"Found {len(actions)} actions")
            else:
                self.log_step_result(journey, "Next Best Actions", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Next Best Actions", False, str(e))
        
        # Step 4: KB payment flow
        try:
            payment_data = {
                "package_id": "knowledge_base_all",
                "origin_url": "https://agency-connect-4.preview.emergentagent.com"
            }
            response = requests.post(f"{BASE_URL}/payments/knowledge-base", 
                                   json=payment_data, headers=headers)
            if response.status_code == 200:
                payment_data = response.json()
                session_url = payment_data.get("checkout_url", "")
                self.log_step_result(journey, "KB Payment Flow", True, "Stripe session created")
            else:
                self.log_step_result(journey, "KB Payment Flow", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "KB Payment Flow", False, str(e))
    
    def test_navigator_analytics_journey(self):
        """Test navigator analytics and reporting journey"""
        journey = "Navigator Analytics Journey"
        self.log_result(f"\n📊 Testing {journey}")
        
        if not self.login_user("navigator"):
            self.log_step_result(journey, "Navigator Login", False, "Authentication failed")
            return
        
        self.log_step_result(journey, "Navigator Login", True)
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        
        # Step 1: Get resource analytics
        try:
            response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                  headers=headers)
            if response.status_code == 200:
                analytics_data = response.json()
                total = analytics_data.get("total", 0)
                by_area = analytics_data.get("by_area", [])
                self.log_step_result(journey, "Resource Analytics", True, f"Total: {total}, Areas: {len(by_area)}")
            else:
                self.log_step_result(journey, "Resource Analytics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "Resource Analytics", False, str(e))
        
        # Step 2: Get KB analytics
        try:
            response = requests.get(f"{BASE_URL}/knowledge-base/analytics", headers=headers)
            if response.status_code == 200:
                kb_analytics = response.json()
                self.log_step_result(journey, "KB Analytics", True, "Analytics retrieved")
            else:
                self.log_step_result(journey, "KB Analytics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "KB Analytics", False, str(e))
    
    def test_agency_workflow_journey(self):
        """Test agency license generation workflow"""
        journey = "Agency Workflow Journey"
        self.log_result(f"\n🏢 Testing {journey}")
        
        if not self.login_user("agency"):
            self.log_step_result(journey, "Agency Login", False, "Authentication failed")
            return
        
        self.log_step_result(journey, "Agency Login", True)
        headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
        
        # Step 1: Generate license codes
        try:
            license_data = {"quantity": 5}
            response = requests.post(f"{BASE_URL}/agency/licenses/generate", 
                                   json=license_data, headers=headers)
            if response.status_code == 200:
                license_response = response.json()
                licenses = license_response.get("licenses", [])
                self.log_step_result(journey, "License Generation", True, f"Generated {len(licenses)} licenses")
            else:
                self.log_step_result(journey, "License Generation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_step_result(journey, "License Generation", False, str(e))
    
    def run_all_journeys(self):
        """Run all user journey tests"""
        self.log_result("🚀 Starting Complete User Journey Testing")
        self.log_result("=" * 80)
        
        self.test_client_assessment_journey()
        self.test_service_request_journey()
        self.test_knowledge_base_journey()
        self.test_navigator_analytics_journey()
        self.test_agency_workflow_journey()
        
        return True
    
    def print_final_report(self):
        """Print comprehensive journey test results"""
        self.log_result("\n" + "=" * 80)
        self.log_result("📊 USER JOURNEY TEST REPORT")
        self.log_result("=" * 80)
        
        total = self.results["total_steps"]
        passed = self.results["passed_steps"]
        failed = self.results["failed_steps"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.log_result(f"Total Steps: {total}")
        self.log_result(f"Passed: {passed}")
        self.log_result(f"Failed: {failed}")
        self.log_result(f"Success Rate: {success_rate:.1f}%")
        
        # Journey-by-journey breakdown
        self.log_result("\n📋 JOURNEY BREAKDOWN:")
        for journey, data in self.results["journeys"].items():
            status = "✅ PASS" if data["success"] else "❌ FAIL"
            self.log_result(f"{status} {journey}")
            for step in data["steps"]:
                self.log_result(f"    {step}")
        
        if self.results["errors"]:
            self.log_result(f"\n❌ FAILED STEPS ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                self.log_result(f"  - {error}")
        else:
            self.log_result("\n✅ ALL JOURNEYS COMPLETED SUCCESSFULLY!")
        
        return success_rate >= 90

def main():
    """Main test execution"""
    tester = UserJourneyTester()
    
    try:
        success = tester.run_all_journeys()
        overall_success = tester.print_final_report()
        
        if overall_success:
            print("\n🎉 USER JOURNEY TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n⚠️ USER JOURNEY TESTING COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()