#!/usr/bin/env python3
"""
Focused Backend Testing - Existing Endpoints Only
Tests only the endpoints that actually exist in the backend implementation
Based on comprehensive review of server.py endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://agencydash.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FocusedEndpointTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = {
            "core_auth": {"status": "PENDING", "tests": []},
            "assessment_system": {"status": "PENDING", "tests": []},
            "service_requests": {"status": "PENDING", "tests": []},
            "knowledge_base": {"status": "PENDING", "tests": []},
            "analytics": {"status": "PENDING", "tests": []},
            "payment_system": {"status": "PENDING", "tests": []},
            "errors": [],
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        self.service_request_id = None
        self.session_id = None
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def add_test_result(self, category: str, test_name: str, status: str, details: str = ""):
        """Add test result to tracking"""
        self.test_results[category]["tests"].append({
            "name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        self.test_results["summary"]["total"] += 1
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
            if details:
                self.test_results["errors"].append(f"{test_name}: {details}")
    
    def login_all_users(self):
        """Login all QA users and store tokens"""
        self.log_result("🔐 Logging in all QA users...")
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": creds["email"],
                    "password": creds["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data["access_token"]
                    self.log_result(f"✅ {role.title()} login successful")
                else:
                    self.log_result(f"❌ {role.title()} login failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_result(f"❌ {role.title()} login error: {str(e)}")
                return False
        
        return True
    
    def test_core_auth_system(self):
        """Test core authentication and user management"""
        self.log_result("\n🔐 Testing Core Authentication System")
        
        # Test 1: User profile retrieval
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.add_test_result("core_auth", "User Profile Retrieval", "PASS", 
                                   f"User ID: {user_data.get('id', 'N/A')}")
            else:
                self.add_test_result("core_auth", "User Profile Retrieval", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("core_auth", "User Profile Retrieval", "FAIL", str(e))
        
        # Test 2: Navigator approval workflows
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            
            # Get pending agencies
            response = requests.get(f"{BASE_URL}/navigator/agencies/pending", headers=headers)
            if response.status_code == 200:
                agencies = response.json().get("agencies", [])
                self.add_test_result("core_auth", "Navigator Agency Management", "PASS", 
                                   f"Found {len(agencies)} pending agencies")
            else:
                self.add_test_result("core_auth", "Navigator Agency Management", "FAIL", 
                                   f"Status: {response.status_code}")
            
            # Get pending providers
            response = requests.get(f"{BASE_URL}/navigator/providers/pending", headers=headers)
            if response.status_code == 200:
                providers = response.json().get("providers", [])
                self.add_test_result("core_auth", "Navigator Provider Management", "PASS", 
                                   f"Found {len(providers)} pending providers")
            else:
                self.add_test_result("core_auth", "Navigator Provider Management", "FAIL", 
                                   f"Status: {response.status_code}")
                
        except Exception as e:
            self.add_test_result("core_auth", "Navigator Approval Workflows", "FAIL", str(e))
    
    def test_assessment_system(self):
        """Test assessment system endpoints"""
        self.log_result("\n📋 Testing Assessment System")
        
        # Test 1: Assessment schema
        try:
            response = requests.get(f"{BASE_URL}/assessment/schema")
            
            if response.status_code == 200:
                schema_data = response.json()
                areas = schema_data.get("schema", {}).get("areas", [])
                self.add_test_result("assessment_system", "Assessment Schema", "PASS", 
                                   f"Found {len(areas)} business areas")
            else:
                self.add_test_result("assessment_system", "Assessment Schema", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("assessment_system", "Assessment Schema", "FAIL", str(e))
        
        # Test 2: Assessment session creation
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
            
            if response.status_code == 200:
                session_data = response.json()
                self.session_id = session_data.get("session_id")
                self.add_test_result("assessment_system", "Session Creation", "PASS", 
                                   f"Session ID: {self.session_id}")
            else:
                self.add_test_result("assessment_system", "Session Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("assessment_system", "Session Creation", "FAIL", str(e))
        
        # Test 3: Assessment response submission
        if self.session_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                response = requests.post(f"{BASE_URL}/assessment/session/{self.session_id}/response", 
                                       json={"question_id": "q1_1", "answer": "No, I need help"}, 
                                       headers=headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    progress = response_data.get("progress_percentage", 0)
                    self.add_test_result("assessment_system", "Response Submission", "PASS", 
                                       f"Progress: {progress}%")
                else:
                    self.add_test_result("assessment_system", "Response Submission", "FAIL", 
                                       f"Status: {response.status_code}")
            except Exception as e:
                self.add_test_result("assessment_system", "Response Submission", "FAIL", str(e))
        
        # Test 4: AI explanation system
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/ai/explain", 
                                   json={"question_id": "q1_1", "context": "business_formation"}, 
                                   headers=headers)
            
            if response.status_code == 200:
                explanation_data = response.json()
                self.add_test_result("assessment_system", "AI Explanation", "PASS", 
                                   f"Explanation provided for question {explanation_data.get('question_id', 'N/A')}")
            else:
                self.add_test_result("assessment_system", "AI Explanation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("assessment_system", "AI Explanation", "FAIL", str(e))
    
    def test_service_request_system(self):
        """Test service request and provider matching system"""
        self.log_result("\n🤝 Testing Service Request System")
        
        # Test 1: Service request creation
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json={
                                       "area_id": "area5",
                                       "budget_range": "$1,000-$2,500",
                                       "description": "Testing service request system"
                                   }, headers=headers)
            
            if response.status_code == 200:
                request_data = response.json()
                self.service_request_id = request_data.get("request_id")
                self.add_test_result("service_requests", "Service Request Creation", "PASS", 
                                   f"Request ID: {self.service_request_id}")
            else:
                self.add_test_result("service_requests", "Service Request Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("service_requests", "Service Request Creation", "FAIL", str(e))
        
        # Test 2: Provider response
        if self.service_request_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                       json={
                                           "request_id": self.service_request_id,
                                           "proposed_fee": 1500,
                                           "estimated_timeline": "2 weeks",
                                           "proposal_note": "Testing provider response"
                                       }, headers=headers)
                
                if response.status_code == 200:
                    self.add_test_result("service_requests", "Provider Response", "PASS", 
                                       "Provider responded successfully")
                else:
                    self.add_test_result("service_requests", "Provider Response", "FAIL", 
                                       f"Status: {response.status_code}")
            except Exception as e:
                self.add_test_result("service_requests", "Provider Response", "FAIL", str(e))
        
        # Test 3: Client view responses
        if self.service_request_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                response = requests.get(f"{BASE_URL}/service-requests/{self.service_request_id}/responses", 
                                      headers=headers)
                
                if response.status_code == 200:
                    responses_data = response.json()
                    responses = responses_data.get("responses", [])
                    self.add_test_result("service_requests", "View Responses", "PASS", 
                                       f"Found {len(responses)} provider responses")
                else:
                    self.add_test_result("service_requests", "View Responses", "FAIL", 
                                       f"Status: {response.status_code}")
            except Exception as e:
                self.add_test_result("service_requests", "View Responses", "FAIL", str(e))
        
        # Test 4: Provider notifications
        try:
            headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
            response = requests.get(f"{BASE_URL}/provider/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications_data = response.json()
                notifications = notifications_data.get("notifications", [])
                self.add_test_result("service_requests", "Provider Notifications", "PASS", 
                                   f"Found {len(notifications)} notifications")
            else:
                self.add_test_result("service_requests", "Provider Notifications", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("service_requests", "Provider Notifications", "FAIL", str(e))
    
    def test_knowledge_base_system(self):
        """Test knowledge base and AI features"""
        self.log_result("\n📚 Testing Knowledge Base System")
        
        # Test 1: KB areas listing
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=headers)
            
            if response.status_code == 200:
                areas_data = response.json()
                areas = areas_data.get("areas", [])
                self.add_test_result("knowledge_base", "KB Areas Listing", "PASS", 
                                   f"Found {len(areas)} knowledge areas")
            else:
                self.add_test_result("knowledge_base", "KB Areas Listing", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("knowledge_base", "KB Areas Listing", "FAIL", str(e))
        
        # Test 2: KB content seeding (Navigator only)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.post(f"{BASE_URL}/knowledge-base/seed-content", headers=headers)
            
            if response.status_code == 200:
                self.add_test_result("knowledge_base", "KB Content Seeding", "PASS", 
                                   "Content seeded successfully")
            else:
                self.add_test_result("knowledge_base", "KB Content Seeding", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("knowledge_base", "KB Content Seeding", "FAIL", str(e))
        
        # Test 3: KB articles management
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            
            # Create article
            response = requests.post(f"{BASE_URL}/knowledge-base/articles", 
                                   json={
                                       "title": "Test Article",
                                       "content": "Test content for KB system",
                                       "area_id": "area1",
                                       "tags": ["testing"]
                                   }, headers=headers)
            
            if response.status_code == 200:
                article_data = response.json()
                article_id = article_data.get("article_id")
                self.add_test_result("knowledge_base", "KB Article Creation", "PASS", 
                                   f"Article ID: {article_id}")
                
                # List articles
                response = requests.get(f"{BASE_URL}/knowledge-base/articles?area_id=area1", 
                                      headers=headers)
                
                if response.status_code == 200:
                    articles_data = response.json()
                    if isinstance(articles_data, list):
                        articles = articles_data
                    else:
                        articles = articles_data.get("articles", [])
                    self.add_test_result("knowledge_base", "KB Article Listing", "PASS", 
                                       f"Found {len(articles)} articles")
                else:
                    self.add_test_result("knowledge_base", "KB Article Listing", "FAIL", 
                                       f"Status: {response.status_code}")
            else:
                self.add_test_result("knowledge_base", "KB Article Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("knowledge_base", "KB Articles Management", "FAIL", str(e))
        
        # Test 4: Contextual KB cards
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/knowledge-base/contextual-cards?context=assessment&area_id=area1", 
                                  headers=headers)
            
            if response.status_code == 200:
                cards_data = response.json()
                cards = cards_data.get("cards", [])
                self.add_test_result("knowledge_base", "Contextual KB Cards", "PASS", 
                                   f"Generated {len(cards)} contextual cards")
            else:
                self.add_test_result("knowledge_base", "Contextual KB Cards", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("knowledge_base", "Contextual KB Cards", "FAIL", str(e))
        
        # Test 5: KB analytics (Navigator only)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.get(f"{BASE_URL}/knowledge-base/analytics", headers=headers)
            
            if response.status_code == 200:
                analytics_data = response.json()
                self.add_test_result("knowledge_base", "KB Analytics", "PASS", 
                                   f"Analytics data: {len(str(analytics_data))} chars")
            else:
                self.add_test_result("knowledge_base", "KB Analytics", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("knowledge_base", "KB Analytics", "FAIL", str(e))
    
    def test_analytics_system(self):
        """Test analytics and reporting system"""
        self.log_result("\n📊 Testing Analytics System")
        
        # Test 1: Resource access logging
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/analytics/resource-access", 
                                   json={"area_id": "area1", "resource_type": "assessment"}, 
                                   headers=headers)
            
            if response.status_code == 200:
                self.add_test_result("analytics", "Resource Access Logging", "PASS", 
                                   "Analytics logged successfully")
            else:
                self.add_test_result("analytics", "Resource Access Logging", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("analytics", "Resource Access Logging", "FAIL", str(e))
        
        # Test 2: Navigator analytics
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                  headers=headers)
            
            if response.status_code == 200:
                analytics_data = response.json()
                total_accesses = analytics_data.get("total", 0)
                self.add_test_result("analytics", "Navigator Analytics", "PASS", 
                                   f"Total resource accesses: {total_accesses}")
            else:
                self.add_test_result("analytics", "Navigator Analytics", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("analytics", "Navigator Analytics", "FAIL", str(e))
        
        # Test 3: System health check
        try:
            response = requests.get(f"{BASE_URL}/system/health")
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                self.add_test_result("analytics", "System Health Check", "PASS", 
                                   f"System status: {status}")
            else:
                self.add_test_result("analytics", "System Health Check", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("analytics", "System Health Check", "FAIL", str(e))
    
    def test_payment_system(self):
        """Test payment integration system"""
        self.log_result("\n💳 Testing Payment System")
        
        # Test 1: Knowledge base payment
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/payments/knowledge-base", 
                                   json={"access_type": "full"}, headers=headers)
            
            if response.status_code == 200:
                payment_data = response.json()
                checkout_url = payment_data.get("checkout_url", "")
                self.add_test_result("payment_system", "KB Payment Integration", "PASS", 
                                   f"Stripe checkout URL generated: {bool(checkout_url)}")
            else:
                self.add_test_result("payment_system", "KB Payment Integration", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("payment_system", "KB Payment Integration", "FAIL", str(e))
        
        # Test 2: Service request payment
        if self.service_request_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                response = requests.post(f"{BASE_URL}/payments/service-request", 
                                       json={"request_id": self.service_request_id}, 
                                       headers=headers)
                
                if response.status_code == 200:
                    payment_data = response.json()
                    checkout_url = payment_data.get("checkout_url", "")
                    self.add_test_result("payment_system", "Service Request Payment", "PASS", 
                                       f"Payment session created: {bool(checkout_url)}")
                else:
                    self.add_test_result("payment_system", "Service Request Payment", "FAIL", 
                                       f"Status: {response.status_code}")
            except Exception as e:
                self.add_test_result("payment_system", "Service Request Payment", "FAIL", str(e))
    
    def run_focused_test(self):
        """Execute focused testing of existing endpoints"""
        self.log_result("🚀 Starting Focused Backend Testing - Existing Endpoints Only")
        self.log_result("=" * 80)
        
        # Login all users first
        if not self.login_all_users():
            self.log_result("❌ Failed to login users, aborting tests")
            return False
        
        # Test all categories
        self.test_core_auth_system()
        self.test_assessment_system()
        self.test_service_request_system()
        self.test_knowledge_base_system()
        self.test_analytics_system()
        self.test_payment_system()
        
        # Update category statuses
        for category in ["core_auth", "assessment_system", "service_requests", "knowledge_base", "analytics", "payment_system"]:
            category_tests = self.test_results[category]["tests"]
            if category_tests:
                passed = sum(1 for test in category_tests if test["status"] == "PASS")
                total = len(category_tests)
                if passed == total:
                    self.test_results[category]["status"] = "PASS"
                elif passed > 0:
                    self.test_results[category]["status"] = "PARTIAL"
                else:
                    self.test_results[category]["status"] = "FAIL"
        
        return True
    
    def print_focused_report(self):
        """Print detailed test report"""
        self.log_result("\n" + "=" * 80)
        self.log_result("📊 FOCUSED BACKEND TESTING REPORT - EXISTING ENDPOINTS")
        self.log_result("=" * 80)
        
        # Summary
        summary = self.test_results["summary"]
        success_rate = (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
        self.log_result(f"OVERALL RESULTS: {summary['passed']}/{summary['total']} tests passed ({success_rate:.1f}%)")
        
        # Category-by-category results
        categories = {
            "core_auth": "Core Authentication & User Management",
            "assessment_system": "Assessment System",
            "service_requests": "Service Request & Provider Matching",
            "knowledge_base": "Knowledge Base System",
            "analytics": "Analytics & Reporting",
            "payment_system": "Payment Integration"
        }
        
        for category_key, category_name in categories.items():
            category_data = self.test_results[category_key]
            status = category_data["status"]
            tests = category_data["tests"]
            
            if tests:
                passed = sum(1 for test in tests if test["status"] == "PASS")
                total = len(tests)
                self.log_result(f"\n{category_name}: {status} ({passed}/{total})")
                
                for test in tests:
                    status_icon = "✅" if test["status"] == "PASS" else "❌"
                    self.log_result(f"  {status_icon} {test['name']}: {test['details']}")
        
        # Errors
        if self.test_results["errors"]:
            self.log_result(f"\n❌ ERRORS ENCOUNTERED ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                self.log_result(f"  - {error}")
        else:
            self.log_result("\n✅ NO CRITICAL ERRORS DETECTED")
        
        # Key findings
        self.log_result(f"\n🔍 KEY FINDINGS:")
        self.log_result(f"  • All QA credentials working: {all(role in self.tokens for role in QA_CREDENTIALS.keys())}")
        self.log_result(f"  • Core authentication: {self.test_results['core_auth']['status']}")
        self.log_result(f"  • Assessment system: {self.test_results['assessment_system']['status']}")
        self.log_result(f"  • Service requests: {self.test_results['service_requests']['status']}")
        self.log_result(f"  • Knowledge base: {self.test_results['knowledge_base']['status']}")
        self.log_result(f"  • Analytics system: {self.test_results['analytics']['status']}")
        self.log_result(f"  • Payment integration: {self.test_results['payment_system']['status']}")
        self.log_result(f"  • System health: {'OPERATIONAL' if success_rate > 80 else 'NEEDS ATTENTION'}")

def main():
    """Main test execution"""
    tester = FocusedEndpointTester()
    
    try:
        success = tester.run_focused_test()
        tester.print_focused_report()
        
        summary = tester.test_results["summary"]
        success_rate = (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
        
        if success_rate >= 80:
            print(f"\n🎉 FOCUSED TESTING COMPLETED - SUCCESS RATE: {success_rate:.1f}%")
            sys.exit(0)
        else:
            print(f"\n⚠️ FOCUSED TESTING COMPLETED - SUCCESS RATE: {success_rate:.1f}% (NEEDS ATTENTION)")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()