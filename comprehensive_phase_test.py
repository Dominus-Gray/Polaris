#!/usr/bin/env python3
"""
Comprehensive Backend Testing - All Phases
Tests all completed phased work as requested in the review:
- Phase 1-2: Procurement opportunities, milestone engagements, core auth
- Phase 3: Advanced Knowledge Base + AI features (PRIORITY)
- Phase 4: Multi-tenant/White-label features
- Medium Phase Features: Advanced search, notifications, compliance
- Quick Wins Features: Data export, health check, bulk operations, analytics
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ComprehensivePhaseTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = {
            "phase_1_2": {"status": "PENDING", "tests": []},
            "phase_3_ai": {"status": "PENDING", "tests": []},
            "phase_4_multitenant": {"status": "PENDING", "tests": []},
            "medium_features": {"status": "PENDING", "tests": []},
            "quick_wins": {"status": "PENDING", "tests": []},
            "errors": [],
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        self.service_request_id = None
        self.engagement_id = None
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def add_test_result(self, phase: str, test_name: str, status: str, details: str = ""):
        """Add test result to tracking"""
        self.test_results[phase]["tests"].append({
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
    
    def test_phase_1_2_features(self):
        """Test Phase 1-2: Core features, procurement opportunities, milestone engagements"""
        self.log_result("\n📋 Testing Phase 1-2: Core Authentication & Procurement Features")
        
        # Test 1: User authentication system
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.add_test_result("phase_1_2", "User Authentication", "PASS", 
                                   f"User ID: {user_data.get('id', 'N/A')}")
            else:
                self.add_test_result("phase_1_2", "User Authentication", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_1_2", "User Authentication", "FAIL", str(e))
        
        # Test 2: Assessment system
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get("session_id")
                self.add_test_result("phase_1_2", "Assessment Session Creation", "PASS", 
                                   f"Session ID: {session_id}")
                
                # Test assessment response
                response = requests.post(f"{BASE_URL}/assessment/session/{session_id}/response", 
                                       json={"question_id": "q1_1", "answer": "No, I need help"}, 
                                       headers=headers)
                
                if response.status_code == 200:
                    self.add_test_result("phase_1_2", "Assessment Response", "PASS", 
                                       "Gap response recorded")
                else:
                    self.add_test_result("phase_1_2", "Assessment Response", "FAIL", 
                                       f"Status: {response.status_code}")
            else:
                self.add_test_result("phase_1_2", "Assessment Session Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_1_2", "Assessment System", "FAIL", str(e))
        
        # Test 3: Service request and provider matching
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json={
                                       "area_id": "area5",
                                       "budget_range": "$1,000-$2,500",
                                       "description": "Phase testing service request"
                                   }, headers=headers)
            
            if response.status_code == 200:
                request_data = response.json()
                self.service_request_id = request_data.get("request_id")
                self.add_test_result("phase_1_2", "Service Request Creation", "PASS", 
                                   f"Request ID: {self.service_request_id}")
                
                # Test provider response
                provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
                response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                       json={
                                           "request_id": self.service_request_id,
                                           "proposed_fee": 1500,
                                           "estimated_timeline": "2 weeks",
                                           "proposal_note": "Phase testing proposal"
                                       }, headers=provider_headers)
                
                if response.status_code == 200:
                    self.add_test_result("phase_1_2", "Provider Response", "PASS", 
                                       "Provider responded to service request")
                else:
                    self.add_test_result("phase_1_2", "Provider Response", "FAIL", 
                                       f"Status: {response.status_code}")
            else:
                self.add_test_result("phase_1_2", "Service Request Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_1_2", "Service Request System", "FAIL", str(e))
        
        # Test 4: Milestone-based engagements
        if self.service_request_id:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                response = requests.post(f"{BASE_URL}/engagements", 
                                       json={
                                           "request_id": self.service_request_id,
                                           "provider_id": self.tokens['provider'][:10]  # Mock provider ID
                                       }, headers=headers)
                
                if response.status_code == 200:
                    engagement_data = response.json()
                    self.engagement_id = engagement_data.get("engagement_id")
                    self.add_test_result("phase_1_2", "Engagement Creation", "PASS", 
                                       f"Engagement ID: {self.engagement_id}")
                else:
                    self.add_test_result("phase_1_2", "Engagement Creation", "FAIL", 
                                       f"Status: {response.status_code}")
            except Exception as e:
                self.add_test_result("phase_1_2", "Engagement Creation", "FAIL", str(e))
    
    def test_phase_3_ai_features(self):
        """Test Phase 3: Advanced Knowledge Base + AI features (PRIORITY)"""
        self.log_result("\n🤖 Testing Phase 3: Knowledge Base AI Features (PRIORITY)")
        
        # Test 1: KB Content Seeding
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.post(f"{BASE_URL}/knowledge-base/seed-content", headers=headers)
            
            if response.status_code == 200:
                self.add_test_result("phase_3_ai", "KB Content Seeding", "PASS", 
                                   "Knowledge base seeded successfully")
            else:
                self.add_test_result("phase_3_ai", "KB Content Seeding", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "KB Content Seeding", "FAIL", str(e))
        
        # Test 2: KB Articles Management
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            
            # Create article
            response = requests.post(f"{BASE_URL}/knowledge-base/articles", 
                                   json={
                                       "title": "Phase 3 Test Article",
                                       "content": "Test content for Phase 3 AI features",
                                       "area_id": "area1",
                                       "tags": ["testing", "phase3"]
                                   }, headers=headers)
            
            if response.status_code == 200:
                article_data = response.json()
                self.add_test_result("phase_3_ai", "KB Article Creation", "PASS", 
                                   f"Article ID: {article_data.get('article_id', 'N/A')}")
                
                # List articles
                response = requests.get(f"{BASE_URL}/knowledge-base/articles?area_id=area1", 
                                      headers=headers)
                
                if response.status_code == 200:
                    articles = response.json().get("articles", [])
                    self.add_test_result("phase_3_ai", "KB Article Listing", "PASS", 
                                       f"Found {len(articles)} articles")
                else:
                    self.add_test_result("phase_3_ai", "KB Article Listing", "FAIL", 
                                       f"Status: {response.status_code}")
            else:
                self.add_test_result("phase_3_ai", "KB Article Creation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "KB Articles Management", "FAIL", str(e))
        
        # Test 3: Contextual KB Cards
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/knowledge-base/contextual-cards?context=assessment&area_id=area1", 
                                  headers=headers)
            
            if response.status_code == 200:
                cards_data = response.json()
                cards = cards_data.get("cards", [])
                self.add_test_result("phase_3_ai", "Contextual KB Cards", "PASS", 
                                   f"Generated {len(cards)} contextual cards")
            else:
                self.add_test_result("phase_3_ai", "Contextual KB Cards", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "Contextual KB Cards", "FAIL", str(e))
        
        # Test 4: AI Assistance with EMERGENT_LLM_KEY
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                   json={
                                       "query": "How do I improve my cybersecurity for government contracts?",
                                       "context": "assessment",
                                       "area_id": "area5"
                                   }, headers=headers)
            
            if response.status_code == 200:
                ai_data = response.json()
                guidance = ai_data.get("guidance", "")
                self.add_test_result("phase_3_ai", "AI Assistance", "PASS", 
                                   f"Generated {len(guidance)} chars of AI guidance")
            else:
                self.add_test_result("phase_3_ai", "AI Assistance", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "AI Assistance", "FAIL", str(e))
        
        # Test 5: Next Best Actions AI
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/knowledge-base/next-best-actions", 
                                   json={
                                       "current_context": "assessment_completed",
                                       "gaps": ["area1", "area5"],
                                       "user_profile": "small_business"
                                   }, headers=headers)
            
            if response.status_code == 200:
                actions_data = response.json()
                recommendations = actions_data.get("recommendations", "")
                self.add_test_result("phase_3_ai", "Next Best Actions", "PASS", 
                                   f"Generated {len(recommendations)} chars of recommendations")
            else:
                self.add_test_result("phase_3_ai", "Next Best Actions", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "Next Best Actions", "FAIL", str(e))
        
        # Test 6: KB Analytics
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.get(f"{BASE_URL}/knowledge-base/analytics", headers=headers)
            
            if response.status_code == 200:
                analytics_data = response.json()
                self.add_test_result("phase_3_ai", "KB Analytics", "PASS", 
                                   f"Analytics data retrieved: {len(str(analytics_data))} chars")
            else:
                self.add_test_result("phase_3_ai", "KB Analytics", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "KB Analytics", "FAIL", str(e))
        
        # Test 7: AI Content Generation
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.post(f"{BASE_URL}/knowledge-base/generate-content", 
                                   json={
                                       "content_type": "checklist",
                                       "area_id": "area5",
                                       "topic": "Cybersecurity compliance for small businesses"
                                   }, headers=headers)
            
            if response.status_code == 200:
                content_data = response.json()
                generated_content = content_data.get("content", "")
                self.add_test_result("phase_3_ai", "AI Content Generation", "PASS", 
                                   f"Generated {len(generated_content)} chars of content")
            else:
                self.add_test_result("phase_3_ai", "AI Content Generation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "AI Content Generation", "FAIL", str(e))
        
        # Test 8: KB Payment Integration
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/payments/knowledge-base", 
                                   json={"access_type": "full"}, headers=headers)
            
            if response.status_code == 200:
                payment_data = response.json()
                checkout_url = payment_data.get("checkout_url", "")
                self.add_test_result("phase_3_ai", "KB Payment Integration", "PASS", 
                                   f"Stripe checkout URL generated: {bool(checkout_url)}")
            else:
                self.add_test_result("phase_3_ai", "KB Payment Integration", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_3_ai", "KB Payment Integration", "FAIL", str(e))
    
    def test_phase_4_multitenant(self):
        """Test Phase 4: Multi-tenant/White-label features"""
        self.log_result("\n🏢 Testing Phase 4: Multi-tenant/White-label Features")
        
        # Test 1: Agency Theme Configuration (POST)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
            response = requests.post(f"{BASE_URL}/agency/theme", 
                                   json={
                                       "primary_color": "#1e40af",
                                       "secondary_color": "#3b82f6",
                                       "logo_url": "https://example.com/logo.png",
                                       "brand_name": "Test Agency",
                                       "custom_css": ".header { background: #1e40af; }"
                                   }, headers=headers)
            
            if response.status_code == 200:
                self.add_test_result("phase_4_multitenant", "Agency Theme Configuration", "PASS", 
                                   "Theme configuration saved")
            else:
                self.add_test_result("phase_4_multitenant", "Agency Theme Configuration", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_4_multitenant", "Agency Theme Configuration", "FAIL", str(e))
        
        # Test 2: Agency Theme Retrieval (GET)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
            response = requests.get(f"{BASE_URL}/agency/theme", headers=headers)
            
            if response.status_code == 200:
                theme_data = response.json()
                self.add_test_result("phase_4_multitenant", "Agency Theme Retrieval", "PASS", 
                                   f"Theme data retrieved: {len(str(theme_data))} chars")
            else:
                self.add_test_result("phase_4_multitenant", "Agency Theme Retrieval", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_4_multitenant", "Agency Theme Retrieval", "FAIL", str(e))
        
        # Test 3: Certificate Generation with Branding
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/certificates/generate", 
                                   json={
                                       "assessment_id": "test_assessment_123",
                                       "include_branding": True
                                   }, headers=headers)
            
            if response.status_code == 200:
                cert_data = response.json()
                self.add_test_result("phase_4_multitenant", "Branded Certificate Generation", "PASS", 
                                   f"Certificate ID: {cert_data.get('certificate_id', 'N/A')}")
            else:
                self.add_test_result("phase_4_multitenant", "Branded Certificate Generation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_4_multitenant", "Branded Certificate Generation", "FAIL", str(e))
        
        # Test 4: OG Image Generation with Agency Branding
        try:
            headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
            response = requests.post(f"{BASE_URL}/agency/og-image", 
                                   json={
                                       "title": "Procurement Readiness Assessment",
                                       "subtitle": "Powered by Test Agency",
                                       "include_logo": True
                                   }, headers=headers)
            
            if response.status_code == 200:
                og_data = response.json()
                self.add_test_result("phase_4_multitenant", "OG Image Generation", "PASS", 
                                   f"OG Image URL: {bool(og_data.get('image_url'))}")
            else:
                self.add_test_result("phase_4_multitenant", "OG Image Generation", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_4_multitenant", "OG Image Generation", "FAIL", str(e))
        
        # Test 5: Public Theme Endpoint (White-label)
        try:
            # This should be accessible without authentication for white-label features
            response = requests.get(f"{BASE_URL}/public/theme/agency123")
            
            if response.status_code == 200:
                public_theme = response.json()
                self.add_test_result("phase_4_multitenant", "Public Theme Endpoint", "PASS", 
                                   f"Public theme data: {len(str(public_theme))} chars")
            else:
                self.add_test_result("phase_4_multitenant", "Public Theme Endpoint", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("phase_4_multitenant", "Public Theme Endpoint", "FAIL", str(e))
    
    def test_medium_phase_features(self):
        """Test Medium Phase Features: Advanced search, notifications, compliance"""
        self.log_result("\n🔍 Testing Medium Phase Features")
        
        # Test 1: Advanced Opportunity Search with Filtering
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/opportunities/search", 
                                  params={
                                      "keywords": "technology",
                                      "budget_min": 1000,
                                      "budget_max": 10000,
                                      "area_id": "area5",
                                      "location": "Texas"
                                  }, headers=headers)
            
            if response.status_code == 200:
                search_results = response.json()
                opportunities = search_results.get("opportunities", [])
                self.add_test_result("medium_features", "Advanced Opportunity Search", "PASS", 
                                   f"Found {len(opportunities)} opportunities")
            else:
                self.add_test_result("medium_features", "Advanced Opportunity Search", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("medium_features", "Advanced Opportunity Search", "FAIL", str(e))
        
        # Test 2: Notification System - Send
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.post(f"{BASE_URL}/notifications/send", 
                                   json={
                                       "recipient_id": self.tokens['client'][:10],  # Mock client ID
                                       "type": "assessment_reminder",
                                       "title": "Complete Your Assessment",
                                       "message": "Don't forget to complete your procurement readiness assessment.",
                                       "priority": "medium"
                                   }, headers=headers)
            
            if response.status_code == 200:
                notification_data = response.json()
                self.add_test_result("medium_features", "Send Notification", "PASS", 
                                   f"Notification ID: {notification_data.get('notification_id', 'N/A')}")
            else:
                self.add_test_result("medium_features", "Send Notification", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("medium_features", "Send Notification", "FAIL", str(e))
        
        # Test 3: Notification System - Get
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.get(f"{BASE_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications_data = response.json()
                notifications = notifications_data.get("notifications", [])
                self.add_test_result("medium_features", "Get Notifications", "PASS", 
                                   f"Retrieved {len(notifications)} notifications")
            else:
                self.add_test_result("medium_features", "Get Notifications", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("medium_features", "Get Notifications", "FAIL", str(e))
        
        # Test 4: Business Profile Document Verification
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/business-profile/verify-documents", 
                                   json={
                                       "document_type": "business_license",
                                       "document_url": "https://example.com/license.pdf",
                                       "verification_method": "automated"
                                   }, headers=headers)
            
            if response.status_code == 200:
                verification_data = response.json()
                self.add_test_result("medium_features", "Document Verification", "PASS", 
                                   f"Verification status: {verification_data.get('status', 'N/A')}")
            else:
                self.add_test_result("medium_features", "Document Verification", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("medium_features", "Document Verification", "FAIL", str(e))
        
        # Test 5: Compliance Monitoring System
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.get(f"{BASE_URL}/compliance/monitor", 
                                  params={"business_id": "test_business_123"}, 
                                  headers=headers)
            
            if response.status_code == 200:
                compliance_data = response.json()
                self.add_test_result("medium_features", "Compliance Monitoring", "PASS", 
                                   f"Compliance status: {compliance_data.get('overall_status', 'N/A')}")
            else:
                self.add_test_result("medium_features", "Compliance Monitoring", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("medium_features", "Compliance Monitoring", "FAIL", str(e))
    
    def test_quick_wins_features(self):
        """Test Quick Wins Features: Data export, health check, bulk operations, analytics"""
        self.log_result("\n⚡ Testing Quick Wins Features")
        
        # Test 1: Data Export (Assessment Data)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            response = requests.post(f"{BASE_URL}/data-export/assessment", 
                                   json={"format": "json", "include_evidence": True}, 
                                   headers=headers)
            
            if response.status_code == 200:
                export_data = response.json()
                self.add_test_result("quick_wins", "Assessment Data Export", "PASS", 
                                   f"Export ID: {export_data.get('export_id', 'N/A')}")
            else:
                self.add_test_result("quick_wins", "Assessment Data Export", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("quick_wins", "Assessment Data Export", "FAIL", str(e))
        
        # Test 2: System Health Check Endpoint
        try:
            response = requests.get(f"{BASE_URL}/system/health")
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                self.add_test_result("quick_wins", "System Health Check", "PASS", 
                                   f"System status: {status}")
            else:
                self.add_test_result("quick_wins", "System Health Check", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("quick_wins", "System Health Check", "FAIL", str(e))
        
        # Test 3: Bulk User Operations
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.post(f"{BASE_URL}/admin/users/bulk-action", 
                                   json={
                                       "action": "activate",
                                       "user_ids": ["test_user_1", "test_user_2"]
                                   }, headers=headers)
            
            if response.status_code == 200:
                bulk_result = response.json()
                self.add_test_result("quick_wins", "Bulk User Operations", "PASS", 
                                   f"Modified {bulk_result.get('modified_count', 0)} users")
            else:
                self.add_test_result("quick_wins", "Bulk User Operations", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("quick_wins", "Bulk User Operations", "FAIL", str(e))
        
        # Test 4: System Analytics Overview
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response = requests.get(f"{BASE_URL}/admin/system/stats", headers=headers)
            
            if response.status_code == 200:
                stats_data = response.json()
                total_users = stats_data.get("total_users", 0)
                self.add_test_result("quick_wins", "System Analytics Overview", "PASS", 
                                   f"Total users: {total_users}")
            else:
                self.add_test_result("quick_wins", "System Analytics Overview", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("quick_wins", "System Analytics Overview", "FAIL", str(e))
        
        # Test 5: Navigator Analytics (Resource Usage Tracking)
        try:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            
            # First, log some analytics
            requests.post(f"{BASE_URL}/analytics/resource-access", 
                         json={"area_id": "area1", "resource_type": "assessment"}, 
                         headers={"Authorization": f"Bearer {self.tokens['client']}"})
            
            time.sleep(1)  # Brief pause
            
            # Then retrieve analytics
            response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                  headers=headers)
            
            if response.status_code == 200:
                analytics_data = response.json()
                total_accesses = analytics_data.get("total", 0)
                self.add_test_result("quick_wins", "Navigator Analytics", "PASS", 
                                   f"Total resource accesses: {total_accesses}")
            else:
                self.add_test_result("quick_wins", "Navigator Analytics", "FAIL", 
                                   f"Status: {response.status_code}")
        except Exception as e:
            self.add_test_result("quick_wins", "Navigator Analytics", "FAIL", str(e))
    
    def run_comprehensive_test(self):
        """Execute comprehensive testing of all phases"""
        self.log_result("🚀 Starting Comprehensive Backend Testing - All Phases")
        self.log_result("=" * 80)
        
        # Login all users first
        if not self.login_all_users():
            self.log_result("❌ Failed to login users, aborting tests")
            return False
        
        # Test all phases
        self.test_phase_1_2_features()
        self.test_phase_3_ai_features()
        self.test_phase_4_multitenant()
        self.test_medium_phase_features()
        self.test_quick_wins_features()
        
        # Update phase statuses
        for phase in ["phase_1_2", "phase_3_ai", "phase_4_multitenant", "medium_features", "quick_wins"]:
            phase_tests = self.test_results[phase]["tests"]
            if phase_tests:
                passed = sum(1 for test in phase_tests if test["status"] == "PASS")
                total = len(phase_tests)
                if passed == total:
                    self.test_results[phase]["status"] = "PASS"
                elif passed > 0:
                    self.test_results[phase]["status"] = "PARTIAL"
                else:
                    self.test_results[phase]["status"] = "FAIL"
        
        return True
    
    def print_comprehensive_report(self):
        """Print detailed test report"""
        self.log_result("\n" + "=" * 80)
        self.log_result("📊 COMPREHENSIVE BACKEND TESTING REPORT")
        self.log_result("=" * 80)
        
        # Summary
        summary = self.test_results["summary"]
        success_rate = (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
        self.log_result(f"OVERALL RESULTS: {summary['passed']}/{summary['total']} tests passed ({success_rate:.1f}%)")
        
        # Phase-by-phase results
        phases = {
            "phase_1_2": "Phase 1-2: Core Features & Procurement",
            "phase_3_ai": "Phase 3: Knowledge Base AI Features (PRIORITY)",
            "phase_4_multitenant": "Phase 4: Multi-tenant/White-label",
            "medium_features": "Medium Phase: Advanced Features",
            "quick_wins": "Quick Wins: System Features"
        }
        
        for phase_key, phase_name in phases.items():
            phase_data = self.test_results[phase_key]
            status = phase_data["status"]
            tests = phase_data["tests"]
            
            if tests:
                passed = sum(1 for test in tests if test["status"] == "PASS")
                total = len(tests)
                self.log_result(f"\n{phase_name}: {status} ({passed}/{total})")
                
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
        self.log_result(f"  • Phase 3 AI features: {self.test_results['phase_3_ai']['status']}")
        self.log_result(f"  • Multi-tenant features: {self.test_results['phase_4_multitenant']['status']}")
        self.log_result(f"  • System health: {'OPERATIONAL' if success_rate > 80 else 'NEEDS ATTENTION'}")

def main():
    """Main test execution"""
    tester = ComprehensivePhaseTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_comprehensive_report()
        
        summary = tester.test_results["summary"]
        success_rate = (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
        
        if success_rate >= 80:
            print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED - SUCCESS RATE: {success_rate:.1f}%")
            sys.exit(0)
        else:
            print(f"\n⚠️ COMPREHENSIVE TESTING COMPLETED - SUCCESS RATE: {success_rate:.1f}% (NEEDS ATTENTION)")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()