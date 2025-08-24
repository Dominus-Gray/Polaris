#!/usr/bin/env python3
"""
Comprehensive Backend Regression Testing for Polaris
Testing all major backend functionality as requested in review.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import os

# Configuration
BACKEND_URL = "https://polaris-inspector.preview.emergentagent.com/api"

# QA Credentials from test_result.md
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class PolarisBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, success, details="", endpoint=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success:
            print(f"   Endpoint: {endpoint}")
        print()

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_test(f"Authentication - {role.title()}", True, 
                            f"Successfully authenticated {creds['email']}", "/auth/login")
                return True
            else:
                self.log_test(f"Authentication - {role.title()}", False, 
                            f"Login failed: {response.status_code} - {response.text}", "/auth/login")
                return False
        except Exception as e:
            self.log_test(f"Authentication - {role.title()}", False, 
                        f"Exception: {str(e)}", "/auth/login")
            return False

    def get_headers(self, role):
        """Get authorization headers for role"""
        if role in self.tokens:
            return {"Authorization": f"Bearer {self.tokens[role]}"}
        return {}

    def test_auth_me(self, role):
        """Test /api/auth/me endpoint"""
        try:
            headers = self.get_headers(role)
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_email = QA_CREDENTIALS[role]["email"]
                if data.get("email") == expected_email and data.get("role") == role:
                    self.log_test(f"Auth Me - {role.title()}", True, 
                                f"Correct user info returned: {data['email']}", "/auth/me")
                    return True
                else:
                    self.log_test(f"Auth Me - {role.title()}", False, 
                                f"Incorrect user info: {data}", "/auth/me")
                    return False
            else:
                self.log_test(f"Auth Me - {role.title()}", False, 
                            f"Failed: {response.status_code} - {response.text}", "/auth/me")
                return False
        except Exception as e:
            self.log_test(f"Auth Me - {role.title()}", False, 
                        f"Exception: {str(e)}", "/auth/me")
            return False

    def test_assessment_schema(self):
        """Test assessment schema includes area1..area9"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BACKEND_URL}/assessment/schema", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Check for all 9 areas
                areas_found = []
                for i in range(1, 10):
                    area_key = f"area{i}"
                    if area_key in data:
                        areas_found.append(area_key)
                
                if len(areas_found) == 9:
                    self.log_test("Assessment Schema", True, 
                                f"All 9 areas found: {areas_found}", "/assessment/schema")
                    return True
                else:
                    self.log_test("Assessment Schema", False, 
                                f"Only {len(areas_found)} areas found: {areas_found}", "/assessment/schema")
                    return False
            else:
                self.log_test("Assessment Schema", False, 
                            f"Failed: {response.status_code} - {response.text}", "/assessment/schema")
                return False
        except Exception as e:
            self.log_test("Assessment Schema", False, 
                        f"Exception: {str(e)}", "/assessment/schema")
            return False

    def test_assessment_session_creation(self):
        """Test creating assessment session"""
        try:
            headers = self.get_headers("client")
            session_data = {
                "business_name": "QA Test Business",
                "industry": "Technology"
            }
            response = self.session.post(f"{BACKEND_URL}/assessment/session", 
                                       json=session_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                if session_id:
                    self.log_test("Assessment Session Creation", True, 
                                f"Session created: {session_id}", "/assessment/session")
                    return session_id
                else:
                    self.log_test("Assessment Session Creation", False, 
                                f"No session_id in response: {data}", "/assessment/session")
                    return None
            else:
                self.log_test("Assessment Session Creation", False, 
                            f"Failed: {response.status_code} - {response.text}", "/assessment/session")
                return None
        except Exception as e:
            self.log_test("Assessment Session Creation", False, 
                        f"Exception: {str(e)}", "/assessment/session")
            return None

    def test_assessment_responses(self, session_id):
        """Test submitting assessment responses including gaps"""
        try:
            headers = self.get_headers("client")
            # Submit responses with some gaps (No answers)
            responses = {
                "session_id": session_id,
                "responses": {
                    "q1_1": "Yes",
                    "q1_2": "No",  # This creates a gap
                    "q2_1": "No, I need help",  # This creates a gap
                    "q3_1": "Yes"
                }
            }
            response = self.session.post(f"{BACKEND_URL}/assessment/responses", 
                                       json=responses, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Assessment Responses", True, 
                            f"Responses submitted successfully", "/assessment/responses")
                return True
            else:
                self.log_test("Assessment Responses", False, 
                            f"Failed: {response.status_code} - {response.text}", "/assessment/responses")
                return False
        except Exception as e:
            self.log_test("Assessment Responses", False, 
                        f"Exception: {str(e)}", "/assessment/responses")
            return False

    def test_analytics_resource_access(self):
        """Test analytics resource access logging"""
        try:
            headers = self.get_headers("client")
            analytics_data = {
                "area_id": "area5",
                "resource_type": "template",
                "action": "download"
            }
            response = self.session.post(f"{BACKEND_URL}/analytics/resource-access", 
                                       json=analytics_data, headers=headers)
            
            if response.status_code == 200:
                self.log_test("Analytics Resource Access", True, 
                            f"Analytics logged successfully", "/analytics/resource-access")
                return True
            else:
                self.log_test("Analytics Resource Access", False, 
                            f"Failed: {response.status_code} - {response.text}", "/analytics/resource-access")
                return False
        except Exception as e:
            self.log_test("Analytics Resource Access", False, 
                        f"Exception: {str(e)}", "/analytics/resource-access")
            return False

    def test_knowledge_base_areas(self):
        """Test knowledge base areas endpoint"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 8:
                    self.log_test("Knowledge Base Areas", True, 
                                f"Found {len(data)} areas", "/knowledge-base/areas")
                    return True
                else:
                    self.log_test("Knowledge Base Areas", False, 
                                f"Insufficient areas: {len(data) if isinstance(data, list) else 'Not a list'}", 
                                "/knowledge-base/areas")
                    return False
            else:
                self.log_test("Knowledge Base Areas", False, 
                            f"Failed: {response.status_code} - {response.text}", "/knowledge-base/areas")
                return False
        except Exception as e:
            self.log_test("Knowledge Base Areas", False, 
                        f"Exception: {str(e)}", "/knowledge-base/areas")
            return False

    def test_contextual_cards(self):
        """Test contextual cards for area5"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/contextual-cards?area_id=area5", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Contextual Cards", True, 
                            f"Cards retrieved for area5", "/knowledge-base/contextual-cards")
                return True
            else:
                self.log_test("Contextual Cards", False, 
                            f"Failed: {response.status_code} - {response.text}", "/knowledge-base/contextual-cards")
                return False
        except Exception as e:
            self.log_test("Contextual Cards", False, 
                        f"Exception: {str(e)}", "/knowledge-base/contextual-cards")
            return False

    def test_ai_assistance(self):
        """Test AI assistance with @polaris.example.com account"""
        try:
            headers = self.get_headers("client")
            ai_request = {
                "question": "How do I improve my technology security infrastructure?",
                "area_id": "area5"
            }
            response = self.session.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                       json=ai_request, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                # Check for concise response (should be under 200 words)
                word_count = len(response_text.split())
                if word_count > 0 and word_count <= 200:
                    self.log_test("AI Assistance", True, 
                                f"Concise response received ({word_count} words)", "/knowledge-base/ai-assistance")
                    return True
                else:
                    self.log_test("AI Assistance", False, 
                                f"Response too long or empty ({word_count} words)", "/knowledge-base/ai-assistance")
                    return False
            else:
                self.log_test("AI Assistance", False, 
                            f"Failed: {response.status_code} - {response.text}", "/knowledge-base/ai-assistance")
                return False
        except Exception as e:
            self.log_test("AI Assistance", False, 
                        f"Exception: {str(e)}", "/knowledge-base/ai-assistance")
            return False

    def test_template_downloads(self):
        """Test template generation downloads"""
        templates = [
            ("area1", "template"),
            ("area2", "guide"),
            ("area5", "practices"),
            ("area9", "template")
        ]
        
        success_count = 0
        for area_id, template_type in templates:
            try:
                headers = self.get_headers("client")
                response = self.session.get(f"{BACKEND_URL}/knowledge-base/generate-template/{area_id}/{template_type}", 
                                          headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("content") and data.get("filename"):
                        self.log_test(f"Template Download - {area_id}/{template_type}", True, 
                                    f"Template generated: {data['filename']}", 
                                    f"/knowledge-base/generate-template/{area_id}/{template_type}")
                        success_count += 1
                    else:
                        self.log_test(f"Template Download - {area_id}/{template_type}", False, 
                                    f"Missing content or filename in response", 
                                    f"/knowledge-base/generate-template/{area_id}/{template_type}")
                else:
                    self.log_test(f"Template Download - {area_id}/{template_type}", False, 
                                f"Failed: {response.status_code} - {response.text}", 
                                f"/knowledge-base/generate-template/{area_id}/{template_type}")
            except Exception as e:
                self.log_test(f"Template Download - {area_id}/{template_type}", False, 
                            f"Exception: {str(e)}", 
                            f"/knowledge-base/generate-template/{area_id}/{template_type}")
        
        return success_count == len(templates)

    def test_service_request_creation(self):
        """Test creating service request for area5"""
        try:
            headers = self.get_headers("client")
            request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with technology security infrastructure assessment and implementation",
                "priority": "high"
            }
            response = self.session.post(f"{BACKEND_URL}/service-requests/professional-help", 
                                       json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                if request_id:
                    self.log_test("Service Request Creation", True, 
                                f"Request created: {request_id}", "/service-requests/professional-help")
                    return request_id
                else:
                    self.log_test("Service Request Creation", False, 
                                f"No request_id in response: {data}", "/service-requests/professional-help")
                    return None
            else:
                self.log_test("Service Request Creation", False, 
                            f"Failed: {response.status_code} - {response.text}", "/service-requests/professional-help")
                return None
        except Exception as e:
            self.log_test("Service Request Creation", False, 
                        f"Exception: {str(e)}", "/service-requests/professional-help")
            return None

    def test_provider_response(self, request_id):
        """Test provider responding to service request"""
        try:
            headers = self.get_headers("provider")
            response_data = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3-4 weeks",
                "proposal_note": "I can help you implement a comprehensive technology security infrastructure assessment including network security, data protection protocols, and compliance frameworks."
            }
            response = self.session.post(f"{BACKEND_URL}/provider/respond-to-request", 
                                       json=response_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                response_id = data.get("response_id")
                if response_id:
                    self.log_test("Provider Response", True, 
                                f"Response created: {response_id}", "/provider/respond-to-request")
                    return response_id
                else:
                    self.log_test("Provider Response", False, 
                                f"No response_id in response: {data}", "/provider/respond-to-request")
                    return None
            else:
                self.log_test("Provider Response", False, 
                            f"Failed: {response.status_code} - {response.text}", "/provider/respond-to-request")
                return None
        except Exception as e:
            self.log_test("Provider Response", False, 
                        f"Exception: {str(e)}", "/provider/respond-to-request")
            return None

    def test_client_retrieve_request(self, request_id):
        """Test client retrieving service request"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BACKEND_URL}/service-requests/{request_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("request_id") == request_id:
                    self.log_test("Client Retrieve Request", True, 
                                f"Request retrieved successfully", f"/service-requests/{request_id}")
                    return True
                else:
                    self.log_test("Client Retrieve Request", False, 
                                f"Request ID mismatch", f"/service-requests/{request_id}")
                    return False
            else:
                self.log_test("Client Retrieve Request", False, 
                            f"Failed: {response.status_code} - {response.text}", f"/service-requests/{request_id}")
                return False
        except Exception as e:
            self.log_test("Client Retrieve Request", False, 
                        f"Exception: {str(e)}", f"/service-requests/{request_id}")
            return False

    def test_client_retrieve_responses(self, request_id):
        """Test client retrieving provider responses"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BACKEND_URL}/service-requests/{request_id}/responses", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Client Retrieve Responses", True, 
                                f"Found {len(data)} responses", f"/service-requests/{request_id}/responses")
                    return True
                else:
                    self.log_test("Client Retrieve Responses", False, 
                                f"Response not a list: {type(data)}", f"/service-requests/{request_id}/responses")
                    return False
            else:
                self.log_test("Client Retrieve Responses", False, 
                            f"Failed: {response.status_code} - {response.text}", f"/service-requests/{request_id}/responses")
                return False
        except Exception as e:
            self.log_test("Client Retrieve Responses", False, 
                        f"Exception: {str(e)}", f"/service-requests/{request_id}/responses")
            return False

    def test_payment_service_request(self, request_id):
        """Test payment for service request"""
        try:
            headers = self.get_headers("client")
            # Get provider ID from responses first
            response = self.session.get(f"{BACKEND_URL}/service-requests/{request_id}/responses", headers=headers)
            if response.status_code == 200:
                responses_data = response.json()
                if isinstance(responses_data, list) and len(responses_data) > 0:
                    provider_id = responses_data[0].get("provider_id")
                    if provider_id:
                        payment_data = {
                            "request_id": request_id,
                            "provider_id": provider_id
                        }
                        payment_response = self.session.post(f"{BACKEND_URL}/payments/service-request", 
                                                   json=payment_data, headers=headers)
                        
                        if payment_response.status_code == 200:
                            data = payment_response.json()
                            if data.get("checkout_url"):
                                self.log_test("Payment Service Request", True, 
                                            f"Stripe checkout URL created", "/payments/service-request")
                                return True
                            else:
                                self.log_test("Payment Service Request", False, 
                                            f"No checkout_url in response: {data}", "/payments/service-request")
                                return False
                        else:
                            self.log_test("Payment Service Request", False, 
                                        f"Failed: {payment_response.status_code} - {payment_response.text}", "/payments/service-request")
                            return False
                    else:
                        self.log_test("Payment Service Request", False, 
                                    f"No provider_id found in responses", "/payments/service-request")
                        return False
                else:
                    self.log_test("Payment Service Request", False, 
                                f"No responses found for request", "/payments/service-request")
                    return False
            else:
                self.log_test("Payment Service Request", False, 
                            f"Failed to get responses: {response.status_code}", "/payments/service-request")
                return False
        except Exception as e:
            self.log_test("Payment Service Request", False, 
                        f"Exception: {str(e)}", "/payments/service-request")
            return False

    def test_payment_knowledge_base(self):
        """Test payment for knowledge base access"""
        try:
            headers = self.get_headers("client")
            payment_data = {
                "area_id": "area5",
                "access_type": "full"
            }
            response = self.session.post(f"{BACKEND_URL}/payments/knowledge-base", 
                                       json=payment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("checkout_url"):
                    self.log_test("Payment Knowledge Base", True, 
                                f"Stripe checkout URL created", "/payments/knowledge-base")
                    return True
                else:
                    self.log_test("Payment Knowledge Base", False, 
                                f"No checkout_url in response: {data}", "/payments/knowledge-base")
                    return False
            else:
                self.log_test("Payment Knowledge Base", False, 
                            f"Failed: {response.status_code} - {response.text}", "/payments/knowledge-base")
                return False
        except Exception as e:
            self.log_test("Payment Knowledge Base", False, 
                        f"Exception: {str(e)}", "/payments/knowledge-base")
            return False

    def test_engagement_creation(self, request_id):
        """Test creating engagement from provider response"""
        try:
            headers = self.get_headers("client")
            # Get provider ID from responses first
            response = self.session.get(f"{BACKEND_URL}/service-requests/{request_id}/responses", headers=headers)
            if response.status_code == 200:
                responses_data = response.json()
                if isinstance(responses_data, list) and len(responses_data) > 0:
                    provider_id = responses_data[0].get("provider_id")
                    if provider_id:
                        engagement_data = {
                            "request_id": request_id,
                            "provider_id": provider_id
                        }
                        engagement_response = self.session.post(f"{BACKEND_URL}/engagements", 
                                                   json=engagement_data, headers=headers)
                        
                        if engagement_response.status_code == 200:
                            data = engagement_response.json()
                            engagement_id = data.get("engagement_id")
                            if engagement_id:
                                self.log_test("Engagement Creation", True, 
                                            f"Engagement created: {engagement_id}", "/engagements")
                                return engagement_id
                            else:
                                self.log_test("Engagement Creation", False, 
                                            f"No engagement_id in response: {data}", "/engagements")
                                return None
                        else:
                            self.log_test("Engagement Creation", False, 
                                        f"Failed: {engagement_response.status_code} - {engagement_response.text}", "/engagements")
                            return None
                    else:
                        self.log_test("Engagement Creation", False, 
                                    f"No provider_id found in responses", "/engagements")
                        return None
                else:
                    self.log_test("Engagement Creation", False, 
                                f"No responses found for request", "/engagements")
                    return None
            else:
                self.log_test("Engagement Creation", False, 
                            f"Failed to get responses: {response.status_code}", "/engagements")
                return None
        except Exception as e:
            self.log_test("Engagement Creation", False, 
                        f"Exception: {str(e)}", "/engagements")
            return None

    def test_engagement_status_transitions(self, engagement_id):
        """Test engagement status transitions"""
        statuses = ["in_progress", "delivered", "approved", "released"]
        
        for status in statuses:
            try:
                headers = self.get_headers("client")
                update_data = {
                    "engagement_id": engagement_id,
                    "status": status,
                    "notes": f"Transitioning to {status} status"
                }
                response = self.session.put(f"{BACKEND_URL}/engagements/{engagement_id}/status", 
                                          json=update_data, headers=headers)
                
                if response.status_code == 200:
                    self.log_test(f"Engagement Status - {status}", True, 
                                f"Status updated to {status}", f"/engagements/{engagement_id}/status")
                else:
                    self.log_test(f"Engagement Status - {status}", False, 
                                f"Failed: {response.status_code} - {response.text}", 
                                f"/engagements/{engagement_id}/status")
                    return False
            except Exception as e:
                self.log_test(f"Engagement Status - {status}", False, 
                            f"Exception: {str(e)}", f"/engagements/{engagement_id}/status")
                return False
        
        return True

    def test_navigator_analytics(self):
        """Test navigator analytics summary"""
        try:
            headers = self.get_headers("navigator")
            response = self.session.get(f"{BACKEND_URL}/navigator/analytics/resources?since_days=30", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "total" in data and "by_area" in data:
                    self.log_test("Navigator Analytics", True, 
                                f"Analytics retrieved: {data['total']} total accesses", 
                                "/navigator/analytics/resources")
                    return True
                else:
                    self.log_test("Navigator Analytics", False, 
                                f"Missing required fields in response: {data}", 
                                "/navigator/analytics/resources")
                    return False
            else:
                self.log_test("Navigator Analytics", False, 
                            f"Failed: {response.status_code} - {response.text}", 
                            "/navigator/analytics/resources")
                return False
        except Exception as e:
            self.log_test("Navigator Analytics", False, 
                        f"Exception: {str(e)}", "/navigator/analytics/resources")
            return False

    def test_agency_theme_get(self):
        """Test GET /api/agency/theme"""
        try:
            headers = self.get_headers("agency")
            response = self.session.get(f"{BACKEND_URL}/agency/theme", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Agency Theme GET", True, 
                            f"Theme retrieved successfully", "/agency/theme")
                return True
            else:
                self.log_test("Agency Theme GET", False, 
                            f"Failed: {response.status_code} - {response.text}", "/agency/theme")
                return False
        except Exception as e:
            self.log_test("Agency Theme GET", False, 
                        f"Exception: {str(e)}", "/agency/theme")
            return False

    def test_agency_theme_post(self):
        """Test POST /api/agency/theme"""
        try:
            headers = self.get_headers("agency")
            theme_data = {
                "primary_color": "#1e40af",
                "secondary_color": "#3b82f6",
                "logo_url": "https://example.com/logo.png",
                "agency_name": "QA Test Agency"
            }
            response = self.session.post(f"{BACKEND_URL}/agency/theme", 
                                       json=theme_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Agency Theme POST", True, 
                            f"Theme updated successfully", "/agency/theme")
                return True
            else:
                self.log_test("Agency Theme POST", False, 
                            f"Failed: {response.status_code} - {response.text}", "/agency/theme")
                return False
        except Exception as e:
            self.log_test("Agency Theme POST", False, 
                        f"Exception: {str(e)}", "/agency/theme")
            return False

    def test_system_health(self):
        """Test GET /api/system/health"""
        try:
            headers = self.get_headers("navigator")  # Navigator should have access
            response = self.session.get(f"{BACKEND_URL}/system/health", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_test("System Health", True, 
                                f"Health check successful: {data['status']}", "/system/health")
                    return True
                else:
                    self.log_test("System Health", False, 
                                f"No status in response: {data}", "/system/health")
                    return False
            else:
                self.log_test("System Health", False, 
                            f"Failed: {response.status_code} - {response.text}", "/system/health")
                return False
        except Exception as e:
            self.log_test("System Health", False, 
                        f"Exception: {str(e)}", "/system/health")
            return False

    def run_comprehensive_tests(self):
        """Run all comprehensive backend regression tests"""
        print("🎯 STARTING COMPREHENSIVE BACKEND REGRESSION TESTING FOR POLARIS")
        print("=" * 80)
        print()
        
        # 1. Authentication Tests
        print("1. AUTHENTICATION TESTING")
        print("-" * 40)
        auth_success = 0
        for role in ["client", "provider", "navigator", "agency"]:
            if self.authenticate_user(role):
                auth_success += 1
                self.test_auth_me(role)
        
        # 2. Assessment System Tests
        print("2. ASSESSMENT SYSTEM TESTING")
        print("-" * 40)
        self.test_assessment_schema()
        session_id = self.test_assessment_session_creation()
        if session_id:
            self.test_assessment_responses(session_id)
        self.test_analytics_resource_access()
        
        # 3. Knowledge Base Tests
        print("3. KNOWLEDGE BASE TESTING")
        print("-" * 40)
        self.test_knowledge_base_areas()
        self.test_contextual_cards()
        self.test_ai_assistance()
        self.test_template_downloads()
        
        # 4. Service Requests & Matching Tests
        print("4. SERVICE REQUESTS & MATCHING TESTING")
        print("-" * 40)
        request_id = self.test_service_request_creation()
        if request_id:
            response_id = self.test_provider_response(request_id)
            self.test_client_retrieve_request(request_id)
            self.test_client_retrieve_responses(request_id)
        
        # 5. Payment Tests
        print("5. PAYMENT TESTING")
        print("-" * 40)
        if request_id:
            self.test_payment_service_request(request_id)
        self.test_payment_knowledge_base()
        
        # 6. Engagement Tests
        print("6. ENGAGEMENT TESTING")
        print("-" * 40)
        if request_id:
            engagement_id = self.test_engagement_creation(request_id)
            if engagement_id:
                self.test_engagement_status_transitions(engagement_id)
        
        # 7. Navigator Analytics Tests
        print("7. NAVIGATOR ANALYTICS TESTING")
        print("-" * 40)
        self.test_navigator_analytics()
        
        # 8. Multi-tenant Phase 4 Tests
        print("8. MULTI-TENANT PHASE 4 TESTING")
        print("-" * 40)
        self.test_agency_theme_get()
        self.test_agency_theme_post()
        self.test_system_health()
        
        # Generate Summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print()
        print("=" * 80)
        print("🎯 COMPREHENSIVE BACKEND REGRESSION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Test Duration: {time.time() - self.start_time:.2f} seconds")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}")
                    print(f"   Endpoint: {result['endpoint']}")
                    print(f"   Details: {result['details']}")
                    print()
        
        print("AUTHENTICATION STATUS:")
        print("-" * 40)
        for role in ["client", "provider", "navigator", "agency"]:
            status = "✅ Authenticated" if role in self.tokens else "❌ Failed"
            print(f"{role.title()}: {status}")
        
        print()
        print("TEST CATEGORIES BREAKDOWN:")
        print("-" * 40)
        categories = {
            "Authentication": [r for r in self.test_results if "Authentication" in r["test"] or "Auth Me" in r["test"]],
            "Assessment": [r for r in self.test_results if "Assessment" in r["test"] or "Analytics" in r["test"]],
            "Knowledge Base": [r for r in self.test_results if "Knowledge Base" in r["test"] or "AI Assistance" in r["test"] or "Template" in r["test"] or "Contextual" in r["test"]],
            "Service Requests": [r for r in self.test_results if "Service Request" in r["test"] or "Provider Response" in r["test"] or "Client Retrieve" in r["test"]],
            "Payments": [r for r in self.test_results if "Payment" in r["test"]],
            "Engagements": [r for r in self.test_results if "Engagement" in r["test"]],
            "Analytics": [r for r in self.test_results if "Navigator Analytics" in r["test"]],
            "Multi-tenant": [r for r in self.test_results if "Agency Theme" in r["test"] or "System Health" in r["test"]]
        }
        
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"{category}: {passed}/{total} ({rate:.1f}%)")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    tester = PolarisBackendTester()
    tester.run_comprehensive_tests()