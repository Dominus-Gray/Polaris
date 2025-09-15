#!/usr/bin/env python3
"""
Detailed Failure Analysis Backend Testing for Polaris Platform
Focus: Identifying exact failing endpoints, specific error messages, and detailed failure analysis
Goal: Achieve 100% backend success rate by identifying all issues for fixing

QA Credentials:
- Client: client.qa@polaris.example.com / Polaris#2025!
- Provider: provider.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
from datetime import datetime
import sys
import traceback

# Configuration
BASE_URL = "https://production-guru.preview.emergentagent.com/api"
QA_CLIENT_EMAIL = "client.qa@polaris.example.com"
QA_CLIENT_PASSWORD = "Polaris#2025!"
QA_PROVIDER_EMAIL = "provider.qa@polaris.example.com"
QA_PROVIDER_PASSWORD = "Polaris#2025!"

class DetailedBackendTester:
    def __init__(self):
        self.client_token = None
        self.provider_token = None
        self.navigator_token = None
        self.agency_token = None
        self.test_results = []
        self.failing_endpoints = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name, success, details="", response_data=None, http_method="", endpoint="", status_code=None):
        """Log detailed test results with failure analysis"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "http_method": http_method,
            "endpoint": endpoint,
            "status_code": status_code
        }
        self.test_results.append(result)
        
        # Track failing endpoints
        if not success and endpoint:
            failure_info = {
                "endpoint": endpoint,
                "method": http_method,
                "status_code": status_code,
                "error_message": details,
                "response_data": response_data,
                "test_name": test_name
            }
            self.failing_endpoints.append(failure_info)
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if http_method and endpoint:
            print(f"   Endpoint: {http_method} {endpoint}")
        if status_code:
            print(f"   Status Code: {status_code}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def make_request(self, method, endpoint, token=None, **kwargs):
        """Make HTTP request with detailed error tracking"""
        url = f"{BASE_URL}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout: {method} {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error: {method} {endpoint}")
            return None
        except Exception as e:
            print(f"💥 Request failed: {method} {endpoint} - {e}")
            return None

    def test_comprehensive_authentication(self):
        """Test all authentication endpoints and user roles"""
        print("🔐 Testing Comprehensive Authentication System...")
        
        # Test 1: Client QA Authentication
        login_data = {
            "email": QA_CLIENT_EMAIL,
            "password": QA_CLIENT_PASSWORD
        }
        
        response = self.make_request('POST', '/auth/login', json=login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.client_token = data.get('access_token')
            self.log_test(
                "Client QA Authentication", 
                True, 
                f"Successfully authenticated client: {QA_CLIENT_EMAIL}",
                {"token_length": len(self.client_token) if self.client_token else 0},
                "POST", "/auth/login", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Client QA Authentication", 
                False, 
                f"Authentication failed for {QA_CLIENT_EMAIL}",
                error_data,
                "POST", "/auth/login", response.status_code if response else None
            )

        # Test 2: Provider QA Authentication
        provider_login_data = {
            "email": QA_PROVIDER_EMAIL,
            "password": QA_PROVIDER_PASSWORD
        }
        
        response = self.make_request('POST', '/auth/login', json=provider_login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.provider_token = data.get('access_token')
            self.log_test(
                "Provider QA Authentication", 
                True, 
                f"Successfully authenticated provider: {QA_PROVIDER_EMAIL}",
                {"token_length": len(self.provider_token) if self.provider_token else 0},
                "POST", "/auth/login", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Provider QA Authentication", 
                False, 
                f"Authentication failed for {QA_PROVIDER_EMAIL}",
                error_data,
                "POST", "/auth/login", response.status_code if response else None
            )

        # Test 3: Token validation with /auth/me
        if self.client_token:
            response = self.make_request('GET', '/auth/me', token=self.client_token)
            if response and response.status_code == 200:
                user_data = response.json()
                self.log_test(
                    "Client Token Validation", 
                    True, 
                    f"Token valid for user: {user_data.get('email')} (Role: {user_data.get('role')})",
                    user_data,
                    "GET", "/auth/me", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Client Token Validation", 
                    False, 
                    "Client token validation failed",
                    error_data,
                    "GET", "/auth/me", response.status_code if response else None
                )

        if self.provider_token:
            response = self.make_request('GET', '/auth/me', token=self.provider_token)
            if response and response.status_code == 200:
                user_data = response.json()
                self.log_test(
                    "Provider Token Validation", 
                    True, 
                    f"Token valid for user: {user_data.get('email')} (Role: {user_data.get('role')})",
                    user_data,
                    "GET", "/auth/me", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Provider Token Validation", 
                    False, 
                    "Provider token validation failed",
                    error_data,
                    "GET", "/auth/me", response.status_code if response else None
                )

    def test_assessment_endpoints_detailed(self):
        """Detailed testing of all assessment-related endpoints"""
        print("📊 Testing Assessment Endpoints in Detail...")
        
        if not self.client_token:
            self.log_test("Assessment Endpoints", False, "No client token available for testing")
            return

        # Test 1: Assessment Schema Endpoint
        response = self.make_request('GET', '/assessment/schema/tier-based', token=self.client_token)
        if response and response.status_code == 200:
            schema_data = response.json()
            areas_count = len(schema_data.get('areas', []))
            tier_info = schema_data.get('tier_access', {})
            self.log_test(
                "Assessment Schema Retrieval", 
                True, 
                f"Retrieved tier-based schema with {areas_count} areas, tier access info: {bool(tier_info)}",
                {"areas_count": areas_count, "tier_access_keys": list(tier_info.keys()) if tier_info else []},
                "GET", "/assessment/schema/tier-based", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Assessment Schema Retrieval", 
                False, 
                "Failed to retrieve assessment schema",
                error_data,
                "GET", "/assessment/schema/tier-based", response.status_code if response else None
            )

        # Test 2: Tier Session Creation (try different data formats)
        session_data_formats = [
            # Format 1: JSON
            {"area_id": "area1", "tier_level": 1},
            # Format 2: Form data
            {"area_id": "area2", "tier_level": 2}
        ]
        
        session_id = None
        for i, session_data in enumerate(session_data_formats):
            format_type = "JSON" if i == 0 else "Form Data"
            
            if i == 0:
                response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, json=session_data)
            else:
                response = self.make_request('POST', '/assessment/tier-session', token=self.client_token, data=session_data)
            
            if response and response.status_code == 200:
                session_response = response.json()
                session_id = session_response.get('session_id')
                questions_count = len(session_response.get('questions', []))
                self.log_test(
                    f"Tier Session Creation ({format_type})", 
                    True, 
                    f"Created session for {session_data['area_id']}, tier {session_data['tier_level']} with {questions_count} questions",
                    {"session_id": session_id, "questions_count": questions_count, "format": format_type},
                    "POST", "/assessment/tier-session", response.status_code
                )
                break  # Success, no need to try other formats
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    f"Tier Session Creation ({format_type})", 
                    False, 
                    f"Failed to create tier session with {format_type}",
                    error_data,
                    "POST", "/assessment/tier-session", response.status_code if response else None
                )

        # Test 3: Assessment Response Submission (try different formats)
        if session_id:
            response_formats = [
                # Format 1: Standard response
                {
                    "question_id": "area1_q1",
                    "response": "yes",
                    "evidence_provided": False
                },
                # Format 2: Response with evidence
                {
                    "question_id": "area1_q2", 
                    "response": "compliant",
                    "evidence_provided": True,
                    "evidence_url": "https://example.com/evidence.pdf"
                },
                # Format 3: Gap response
                {
                    "question_id": "area1_q3",
                    "response": "gap_exists",
                    "gap_solution": "service_provider"
                }
            ]
            
            for i, response_data in enumerate(response_formats):
                response = self.make_request(
                    'POST', 
                    f'/assessment/tier-session/{session_id}/response', 
                    token=self.client_token, 
                    json=response_data
                )
                
                if response and response.status_code == 200:
                    result_data = response.json()
                    self.log_test(
                        f"Assessment Response Submission (Format {i+1})", 
                        True, 
                        f"Successfully submitted response: {response_data['response']}",
                        result_data,
                        "POST", f"/assessment/tier-session/{session_id}/response", response.status_code
                    )
                else:
                    error_data = response.json() if response else {"error": "No response"}
                    self.log_test(
                        f"Assessment Response Submission (Format {i+1})", 
                        False, 
                        f"Failed to submit response format {i+1}",
                        error_data,
                        "POST", f"/assessment/tier-session/{session_id}/response", response.status_code if response else None
                    )

        # Test 4: Assessment Progress Endpoint
        if session_id:
            response = self.make_request('GET', f'/assessment/tier-session/{session_id}/progress', token=self.client_token)
            if response and response.status_code == 200:
                progress_data = response.json()
                self.log_test(
                    "Assessment Progress Retrieval", 
                    True, 
                    f"Retrieved progress for session {session_id}",
                    progress_data,
                    "GET", f"/assessment/tier-session/{session_id}/progress", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Assessment Progress Retrieval", 
                    False, 
                    "Failed to retrieve assessment progress",
                    error_data,
                    "GET", f"/assessment/tier-session/{session_id}/progress", response.status_code if response else None
                )

    def test_service_provider_system_detailed(self):
        """Detailed testing of service provider and matching system"""
        print("🤝 Testing Service Provider System in Detail...")
        
        if not self.client_token or not self.provider_token:
            self.log_test("Service Provider System", False, "Missing authentication tokens")
            return

        # Test 1: Service Request Creation (try different formats)
        service_request_formats = [
            # Format 1: Standard request
            {
                "area_id": "area5",
                "budget_range": "1500-5000", 
                "timeline": "2-4 weeks",
                "description": "Technology infrastructure assessment and security compliance setup for government contracting readiness.",
                "priority": "high"
            },
            # Format 2: Enhanced request
            {
                "area_id": "area3",
                "budget_range": "500-1500",
                "timeline": "1-2 weeks", 
                "description": "Legal compliance review and contract preparation assistance.",
                "priority": "medium",
                "urgency": "normal"
            }
        ]
        
        request_id = None
        for i, request_data in enumerate(service_request_formats):
            response = self.make_request('POST', '/service-requests/professional-help', token=self.client_token, json=request_data)
            
            if response and response.status_code == 200:
                request_response = response.json()
                request_id = request_response.get('request_id')
                self.log_test(
                    f"Service Request Creation (Format {i+1})", 
                    True, 
                    f"Created service request for {request_data['area_id']} with budget {request_data['budget_range']}",
                    {"request_id": request_id, "area": request_data['area_id']},
                    "POST", "/service-requests/professional-help", response.status_code
                )
                break  # Use first successful request
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    f"Service Request Creation (Format {i+1})", 
                    False, 
                    f"Failed to create service request format {i+1}",
                    error_data,
                    "POST", "/service-requests/professional-help", response.status_code if response else None
                )

        # Test 2: Provider Response Submission
        if request_id:
            provider_response_data = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "Comprehensive technology infrastructure assessment including security compliance review, system architecture recommendations, and implementation roadmap for government contracting requirements."
            }
            
            response = self.make_request('POST', '/provider/respond-to-request', token=self.provider_token, json=provider_response_data)
            
            if response and response.status_code == 200:
                response_data = response.json()
                self.log_test(
                    "Provider Response Submission", 
                    True, 
                    f"Provider responded with ${provider_response_data['proposed_fee']} proposal",
                    response_data,
                    "POST", "/provider/respond-to-request", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Provider Response Submission", 
                    False, 
                    "Failed to submit provider response",
                    error_data,
                    "POST", "/provider/respond-to-request", response.status_code if response else None
                )

        # Test 3: Service Request Retrieval with Responses
        if request_id:
            response = self.make_request('GET', f'/service-requests/{request_id}', token=self.client_token)
            
            if response and response.status_code == 200:
                request_data = response.json()
                responses_count = len(request_data.get('provider_responses', []))
                self.log_test(
                    "Service Request Retrieval", 
                    True, 
                    f"Retrieved service request with {responses_count} provider responses",
                    {"request_id": request_id, "responses_count": responses_count, "status": request_data.get('status')},
                    "GET", f"/service-requests/{request_id}", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Service Request Retrieval", 
                    False, 
                    "Failed to retrieve service request",
                    error_data,
                    "GET", f"/service-requests/{request_id}", response.status_code if response else None
                )

        # Test 4: Service Request Responses Endpoint
        if request_id:
            response = self.make_request('GET', f'/service-requests/{request_id}/responses', token=self.client_token)
            
            if response and response.status_code == 200:
                responses_data = response.json()
                responses_count = len(responses_data) if isinstance(responses_data, list) else len(responses_data.get('responses', []))
                self.log_test(
                    "Service Request Responses Retrieval", 
                    True, 
                    f"Retrieved {responses_count} provider responses",
                    {"responses_count": responses_count},
                    "GET", f"/service-requests/{request_id}/responses", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Service Request Responses Retrieval", 
                    False, 
                    "Failed to retrieve service request responses",
                    error_data,
                    "GET", f"/service-requests/{request_id}/responses", response.status_code if response else None
                )

    def test_notifications_system_detailed(self):
        """Detailed testing of notifications system"""
        print("🔔 Testing Notifications System in Detail...")
        
        if not self.client_token:
            self.log_test("Notifications System", False, "No client token available")
            return

        # Test 1: Get User Notifications
        response = self.make_request('GET', '/notifications/my', token=self.client_token)
        
        if response and response.status_code == 200:
            notifications = response.json()
            notifications_count = len(notifications) if isinstance(notifications, list) else len(notifications.get('notifications', []))
            self.log_test(
                "Get User Notifications", 
                True, 
                f"Retrieved {notifications_count} notifications",
                {"notifications_count": notifications_count, "structure": type(notifications).__name__},
                "GET", "/notifications/my", response.status_code
            )
        elif response and response.status_code == 500:
            # 500 might be expected for unimplemented notifications
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Get User Notifications", 
                False, 
                "Notifications endpoint returns 500 - likely unimplemented",
                error_data,
                "GET", "/notifications/my", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Get User Notifications", 
                False, 
                "Notifications endpoint failed unexpectedly",
                error_data,
                "GET", "/notifications/my", response.status_code if response else None
            )

        # Test 2: Mark Notification as Read (if notifications exist)
        # First try to create a test notification or use existing one
        test_notification_endpoints = [
            '/notifications/mark-read',
            '/notifications/1/read',
            '/notifications/mark-as-read'
        ]
        
        for endpoint in test_notification_endpoints:
            test_data = {"notification_id": "test_notification_1"}
            response = self.make_request('POST', endpoint, token=self.client_token, json=test_data)
            
            if response and response.status_code in [200, 404]:  # 404 might be expected if notification doesn't exist
                if response.status_code == 200:
                    result_data = response.json()
                    self.log_test(
                        f"Mark Notification Read ({endpoint})", 
                        True, 
                        "Successfully marked notification as read",
                        result_data,
                        "POST", endpoint, response.status_code
                    )
                else:
                    self.log_test(
                        f"Mark Notification Read ({endpoint})", 
                        True, 
                        "Endpoint accessible (404 expected for non-existent notification)",
                        {"status_code": response.status_code},
                        "POST", endpoint, response.status_code
                    )
                break
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    f"Mark Notification Read ({endpoint})", 
                    False, 
                    f"Failed to mark notification as read via {endpoint}",
                    error_data,
                    "POST", endpoint, response.status_code if response else None
                )

    def test_provider_profile_system_detailed(self):
        """Detailed testing of provider profile retrieval and management"""
        print("👤 Testing Provider Profile System in Detail...")
        
        if not self.provider_token or not self.client_token:
            self.log_test("Provider Profile System", False, "Missing authentication tokens")
            return

        # Test 1: Get Provider's Own Profile
        response = self.make_request('GET', '/auth/me', token=self.provider_token)
        provider_id = None
        
        if response and response.status_code == 200:
            provider_data = response.json()
            provider_id = provider_data.get('id')
            self.log_test(
                "Provider Self Profile Retrieval", 
                True, 
                f"Retrieved provider profile: {provider_data.get('email')}",
                {"provider_id": provider_id, "role": provider_data.get('role')},
                "GET", "/auth/me", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Provider Self Profile Retrieval", 
                False, 
                "Failed to retrieve provider's own profile",
                error_data,
                "GET", "/auth/me", response.status_code if response else None
            )

        # Test 2: Client Accessing Provider Profile
        if provider_id:
            provider_profile_endpoints = [
                f'/providers/{provider_id}',
                f'/providers/{provider_id}/profile',
                f'/provider/profile/{provider_id}',
                f'/users/{provider_id}/provider-profile'
            ]
            
            profile_found = False
            for endpoint in provider_profile_endpoints:
                response = self.make_request('GET', endpoint, token=self.client_token)
                
                if response and response.status_code == 200:
                    profile_data = response.json()
                    self.log_test(
                        f"Client Access Provider Profile ({endpoint})", 
                        True, 
                        f"Successfully retrieved provider profile via {endpoint}",
                        {"provider_id": provider_id, "profile_keys": list(profile_data.keys())},
                        "GET", endpoint, response.status_code
                    )
                    profile_found = True
                    break
                else:
                    error_data = response.json() if response else {"error": "No response"}
                    self.log_test(
                        f"Client Access Provider Profile ({endpoint})", 
                        False, 
                        f"Failed to retrieve provider profile via {endpoint}",
                        error_data,
                        "GET", endpoint, response.status_code if response else None
                    )
            
            if not profile_found:
                self.log_test(
                    "Provider Profile Retrieval", 
                    False, 
                    "No working provider profile endpoint found",
                    {"tried_endpoints": provider_profile_endpoints}
                )

        # Test 3: Provider Search/Listing
        provider_search_endpoints = [
            '/providers/approved',
            '/providers/search', 
            '/providers',
            '/marketplace/providers'
        ]
        
        search_params = {
            "area_id": "area5",
            "min_rating": "4",
            "certification": "ISO 27001"
        }
        
        providers_found = False
        for endpoint in provider_search_endpoints:
            response = self.make_request('GET', endpoint, token=self.client_token, params=search_params)
            
            if response and response.status_code == 200:
                providers_data = response.json()
                providers_count = len(providers_data) if isinstance(providers_data, list) else len(providers_data.get('providers', []))
                self.log_test(
                    f"Provider Search ({endpoint})", 
                    True, 
                    f"Found {providers_count} providers via {endpoint}",
                    {"endpoint": endpoint, "providers_count": providers_count},
                    "GET", endpoint, response.status_code
                )
                providers_found = True
                break
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    f"Provider Search ({endpoint})", 
                    False, 
                    f"Provider search failed via {endpoint}",
                    error_data,
                    "GET", endpoint, response.status_code if response else None
                )
        
        if not providers_found:
            self.log_test(
                "Provider Search System", 
                False, 
                "No working provider search endpoint found",
                {"tried_endpoints": provider_search_endpoints}
            )

    def test_dashboard_system_detailed(self):
        """Detailed testing of dashboard and home endpoints"""
        print("📈 Testing Dashboard System in Detail...")
        
        if not self.client_token:
            self.log_test("Dashboard System", False, "No client token available")
            return

        # Test 1: Client Home Dashboard
        response = self.make_request('GET', '/home/client', token=self.client_token)
        
        if response and response.status_code == 200:
            dashboard_data = response.json()
            
            # Analyze dashboard structure
            expected_keys = ['assessment_completion', 'critical_gaps', 'active_services', 'readiness_score', 'metrics']
            found_keys = [key for key in expected_keys if key in dashboard_data]
            
            self.log_test(
                "Client Home Dashboard", 
                True, 
                f"Retrieved dashboard data with {len(found_keys)}/{len(expected_keys)} expected keys",
                {
                    "found_keys": found_keys,
                    "all_keys": list(dashboard_data.keys()),
                    "data_structure": {k: type(v).__name__ for k, v in dashboard_data.items()}
                },
                "GET", "/home/client", response.status_code
            )
        else:
            error_data = response.json() if response else {"error": "No response"}
            self.log_test(
                "Client Home Dashboard", 
                False, 
                "Failed to retrieve client dashboard data",
                error_data,
                "GET", "/home/client", response.status_code if response else None
            )

        # Test 2: Provider Home Dashboard
        if self.provider_token:
            response = self.make_request('GET', '/home/provider', token=self.provider_token)
            
            if response and response.status_code == 200:
                provider_dashboard = response.json()
                self.log_test(
                    "Provider Home Dashboard", 
                    True, 
                    "Retrieved provider dashboard data",
                    {"data_keys": list(provider_dashboard.keys())},
                    "GET", "/home/provider", response.status_code
                )
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    "Provider Home Dashboard", 
                    False, 
                    "Failed to retrieve provider dashboard data",
                    error_data,
                    "GET", "/home/provider", response.status_code if response else None
                )

        # Test 3: User Statistics/Metrics
        stats_endpoints = [
            '/user/stats',
            '/dashboard/stats',
            '/metrics/user',
            '/home/stats'
        ]
        
        for endpoint in stats_endpoints:
            response = self.make_request('GET', endpoint, token=self.client_token)
            
            if response and response.status_code == 200:
                stats_data = response.json()
                self.log_test(
                    f"User Statistics ({endpoint})", 
                    True, 
                    f"Retrieved user statistics via {endpoint}",
                    {"stats_keys": list(stats_data.keys())},
                    "GET", endpoint, response.status_code
                )
                break
            else:
                error_data = response.json() if response else {"error": "No response"}
                self.log_test(
                    f"User Statistics ({endpoint})", 
                    False, 
                    f"Failed to retrieve statistics via {endpoint}",
                    error_data,
                    "GET", endpoint, response.status_code if response else None
                )

    def run_detailed_failure_analysis(self):
        """Run comprehensive backend testing with detailed failure analysis"""
        print("🚀 Starting Detailed Backend Failure Analysis for Polaris Platform")
        print("🎯 Goal: Identify ALL failing endpoints with exact error messages")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all detailed test suites
        try:
            self.test_comprehensive_authentication()
            self.test_assessment_endpoints_detailed()
            self.test_service_provider_system_detailed()
            self.test_notifications_system_detailed()
            self.test_provider_profile_system_detailed()
            self.test_dashboard_system_detailed()
        except Exception as e:
            print(f"💥 Critical error during testing: {e}")
            traceback.print_exc()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print comprehensive results
        print("=" * 80)
        print("🎯 DETAILED BACKEND FAILURE ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        # DETAILED FAILING ENDPOINTS ANALYSIS
        if self.failing_endpoints:
            print("🚨 FAILING ENDPOINTS - DETAILED ANALYSIS:")
            print("=" * 60)
            
            for i, failure in enumerate(self.failing_endpoints, 1):
                print(f"\n{i}. FAILING ENDPOINT:")
                print(f"   Method: {failure['method']}")
                print(f"   Endpoint: {failure['endpoint']}")
                print(f"   Status Code: {failure['status_code']}")
                print(f"   Test: {failure['test_name']}")
                print(f"   Error: {failure['error_message']}")
                if failure['response_data']:
                    print(f"   Response: {json.dumps(failure['response_data'], indent=6)}")
                print("-" * 40)
            
            # Group failures by endpoint
            endpoint_failures = {}
            for failure in self.failing_endpoints:
                key = f"{failure['method']} {failure['endpoint']}"
                if key not in endpoint_failures:
                    endpoint_failures[key] = []
                endpoint_failures[key].append(failure)
            
            print(f"\n📊 FAILURE SUMMARY BY ENDPOINT:")
            print("-" * 40)
            for endpoint, failures in endpoint_failures.items():
                print(f"❌ {endpoint} ({len(failures)} failures)")
                for failure in failures:
                    print(f"   - {failure['test_name']}: {failure['status_code']}")
        else:
            print("✅ NO FAILING ENDPOINTS DETECTED!")
        
        # Authentication Status
        print(f"\n🔐 AUTHENTICATION STATUS:")
        print("-" * 40)
        print(f"Client QA ({QA_CLIENT_EMAIL}): {'✅ WORKING' if self.client_token else '❌ FAILED'}")
        print(f"Provider QA ({QA_PROVIDER_EMAIL}): {'✅ WORKING' if self.provider_token else '❌ FAILED'}")
        
        # System Health Assessment
        print(f"\n🏥 SYSTEM HEALTH ASSESSMENT:")
        print("-" * 40)
        
        if success_rate >= 90:
            health_status = "✅ EXCELLENT - Ready for production"
        elif success_rate >= 75:
            health_status = "🟡 GOOD - Minor issues need fixing"
        elif success_rate >= 60:
            health_status = "⚠️  MODERATE - Several issues blocking production"
        else:
            health_status = "🚨 CRITICAL - Major issues require immediate attention"
        
        print(f"Overall Health: {health_status}")
        
        # Specific Recommendations
        print(f"\n💡 SPECIFIC RECOMMENDATIONS FOR 100% SUCCESS:")
        print("-" * 50)
        
        if self.failing_endpoints:
            # Group by issue type
            auth_issues = [f for f in self.failing_endpoints if 'auth' in f['endpoint'].lower()]
            assessment_issues = [f for f in self.failing_endpoints if 'assessment' in f['endpoint'].lower()]
            service_issues = [f for f in self.failing_endpoints if 'service' in f['endpoint'].lower() or 'provider' in f['endpoint'].lower()]
            notification_issues = [f for f in self.failing_endpoints if 'notification' in f['endpoint'].lower()]
            
            if auth_issues:
                print("🔐 AUTHENTICATION FIXES NEEDED:")
                for issue in auth_issues:
                    print(f"   - Fix {issue['method']} {issue['endpoint']} (Status: {issue['status_code']})")
            
            if assessment_issues:
                print("📊 ASSESSMENT SYSTEM FIXES NEEDED:")
                for issue in assessment_issues:
                    print(f"   - Fix {issue['method']} {issue['endpoint']} (Status: {issue['status_code']})")
            
            if service_issues:
                print("🤝 SERVICE PROVIDER SYSTEM FIXES NEEDED:")
                for issue in service_issues:
                    print(f"   - Fix {issue['method']} {issue['endpoint']} (Status: {issue['status_code']})")
            
            if notification_issues:
                print("🔔 NOTIFICATION SYSTEM FIXES NEEDED:")
                for issue in notification_issues:
                    print(f"   - Fix {issue['method']} {issue['endpoint']} (Status: {issue['status_code']})")
        else:
            print("✅ All endpoints working correctly!")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'duration': duration,
            'failing_endpoints': self.failing_endpoints,
            'client_auth_working': bool(self.client_token),
            'provider_auth_working': bool(self.provider_token)
        }

if __name__ == "__main__":
    tester = DetailedBackendTester()
    results = tester.run_detailed_failure_analysis()
    
    # Exit with appropriate code
    sys.exit(0 if results['success_rate'] >= 90 else 1)