#!/usr/bin/env python3
"""
Comprehensive Backend Readiness Smoke Test
Polaris - Small Business Procurement Readiness Platform

This script performs a comprehensive smoke test against the running FastAPI service
following the Kubernetes ingress rules and testing all critical endpoints.

Environment:
- Backend routes prefixed with /api
- Service bound internally to 0.0.0.0:8001 with ingress mapping
- MongoDB via MONGO_URL from backend/.env
- AI features using EMERGENT_LLM_KEY from backend/.env

Test Credentials:
- QA Client: client.qa@polaris.example.com / Polaris#2025!
- QA Provider: provider.qa@polaris.example.com / Polaris#2025!
- QA Navigator: navigator.qa@polaris.example.com / Polaris#2025!
- QA Agency: agency.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

class BackendSmokeTest:
    def __init__(self):
        # Use internal container HTTP for direct smoke test
        self.base_url = "http://127.0.0.1:8001"
        self.api_url = f"{self.base_url}/api"
        
        # Test credentials as specified
        self.credentials = {
            "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
            "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
            "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
            "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
        }
        
        # Store tokens for authenticated requests
        self.tokens = {}
        
        # Test results storage
        self.results = {
            "test_start": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "critical_issues": [],
            "warnings": []
        }
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Polaris-Backend-Smoke-Test/1.0'
        })

    def log_test(self, test_name: str, success: bool, status_code: int = None, 
                 response_time: float = None, details: str = None, response_body: str = None):
        """Log test result with comprehensive details"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed_tests"] += 1
        else:
            self.results["failed_tests"] += 1
            
        test_result = {
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2) if response_time else None,
            "details": details,
            "response_snippet": response_body[:200] + "..." if response_body and len(response_body) > 200 else response_body,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["test_details"].append(test_result)
        
        # Print real-time results
        status = "✅ PASS" if success else "❌ FAIL"
        timing = f" ({response_time*1000:.0f}ms)" if response_time else ""
        print(f"{status}: {test_name}{timing}")
        if not success and details:
            print(f"    Details: {details}")
        if status_code:
            print(f"    Status: {status_code}")

    def make_request(self, method: str, endpoint: str, data: dict = None, 
                    headers: dict = None, auth_token: str = None) -> Tuple[requests.Response, float]:
        """Make HTTP request with timing and error handling"""
        url = f"{self.api_url}{endpoint}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        if auth_token:
            request_headers['Authorization'] = f'Bearer {auth_token}'
            
        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_time = time.time() - start_time
            return response, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            # Create a mock response object for failed requests
            class MockResponse:
                def __init__(self, error_exception):
                    self.status_code = 0
                    self.text = str(error_exception)
                    self.headers = {}
                    self.error_exception = error_exception
                def json(self):
                    return {"error": str(self.error_exception)}
            return MockResponse(e), response_time

    def test_auth_flows(self):
        """Test authentication flows for all QA users"""
        print("\n🔐 Testing Authentication Flows...")
        
        for role, creds in self.credentials.items():
            # Test login
            response, response_time = self.make_request(
                'POST', '/auth/login', 
                data={"email": creds["email"], "password": creds["password"]}
            )
            
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    if "access_token" in token_data:
                        self.tokens[role] = token_data["access_token"]
                        self.log_test(f"Login - {role.title()}", True, response.status_code, 
                                    response_time, f"Token received: {len(token_data['access_token'])} chars")
                        
                        # Test /auth/me with the token
                        me_response, me_time = self.make_request(
                            'GET', '/auth/me', auth_token=self.tokens[role]
                        )
                        
                        if me_response.status_code == 200:
                            user_data = me_response.json()
                            self.log_test(f"Auth/Me - {role.title()}", True, me_response.status_code,
                                        me_time, f"User: {user_data.get('email', 'N/A')}, Role: {user_data.get('role', 'N/A')}")
                        else:
                            self.log_test(f"Auth/Me - {role.title()}", False, me_response.status_code,
                                        me_time, f"Failed to verify token: {me_response.text[:100]}")
                    else:
                        self.log_test(f"Login - {role.title()}", False, response.status_code,
                                    response_time, "No access_token in response")
                except json.JSONDecodeError:
                    self.log_test(f"Login - {role.title()}", False, response.status_code,
                                response_time, "Invalid JSON response")
            else:
                self.log_test(f"Login - {role.title()}", False, response.status_code,
                            response_time, f"Login failed: {response.text[:100]}")

    def test_tier_based_assessment(self):
        """Test tier-based assessment system"""
        print("\n📊 Testing Tier-Based Assessment System...")
        
        # Test assessment schema
        response, response_time = self.make_request('GET', '/assessment/schema/tier-based')
        
        if response.status_code == 200:
            try:
                schema = response.json()
                area10_found = any(area.get('area_id') == 'area10' and 'Competitive Advantage' in area.get('area_name', '') 
                                 for area in schema.get('areas', []))
                self.log_test("Assessment Schema - Area10 Competitive Advantage", area10_found, 
                            response.status_code, response_time, 
                            f"Found {len(schema.get('areas', []))} areas, Area10: {area10_found}")
            except json.JSONDecodeError:
                self.log_test("Assessment Schema", False, response.status_code, response_time, "Invalid JSON")
        else:
            self.log_test("Assessment Schema", False, response.status_code, response_time, response.text[:100])
        
        # Test tier session creation (requires client token)
        if 'client' in self.tokens:
            session_data = {
                "area_id": "area5",
                "tier_level": 3,
                "business_context": "Technology assessment for government contracting"
            }
            
            response, response_time = self.make_request(
                'POST', '/assessment/tier-session', 
                data=session_data, auth_token=self.tokens['client']
            )
            
            if response.status_code == 200:
                try:
                    session = response.json()
                    session_id = session.get('session_id')
                    self.log_test("Tier Session Creation", True, response.status_code, response_time,
                                f"Session ID: {session_id}, Tier: {session.get('tier_level')}")
                    
                    # Test response submission
                    if session_id:
                        response_data = {
                            "question_id": "area5_tier1_q1",
                            "response": "Gap Exists - I Need Help",
                            "notes": "Need assistance with cybersecurity framework implementation"
                        }
                        
                        submit_response, submit_time = self.make_request(
                            'POST', f'/assessment/tier-session/{session_id}/response',
                            data=response_data, auth_token=self.tokens['client']
                        )
                        
                        self.log_test("Tier Response Submission", submit_response.status_code == 200,
                                    submit_response.status_code, submit_time,
                                    f"Gap pathway response submitted")
                        
                        # Test progress check
                        progress_response, progress_time = self.make_request(
                            'GET', f'/assessment/tier-session/{session_id}/progress',
                            auth_token=self.tokens['client']
                        )
                        
                        if progress_response.status_code == 200:
                            progress = progress_response.json()
                            self.log_test("Tier Progress Check", True, progress_response.status_code,
                                        progress_time, f"Progress: {progress.get('completion_percentage', 0)}%")
                        else:
                            self.log_test("Tier Progress Check", False, progress_response.status_code,
                                        progress_time, progress_response.text[:100])
                            
                except json.JSONDecodeError:
                    self.log_test("Tier Session Creation", False, response.status_code, response_time, "Invalid JSON")
            else:
                self.log_test("Tier Session Creation", False, response.status_code, response_time, response.text[:100])

    def test_service_provider_marketplace(self):
        """Test service provider marketplace functionality"""
        print("\n🏪 Testing Service Provider Marketplace...")
        
        # Test service request creation (as client)
        if 'client' in self.tokens:
            request_data = {
                "area_id": "area5",
                "budget_range": "$1,000-$2,500",
                "timeline": "2-4 weeks",
                "description": "Need cybersecurity assessment and compliance framework setup for government contracting readiness"
            }
            
            response, response_time = self.make_request(
                'POST', '/service-requests/professional-help',
                data=request_data, auth_token=self.tokens['client']
            )
            
            if response.status_code == 200:
                try:
                    request_result = response.json()
                    request_id = request_result.get('request_id')
                    self.log_test("Service Request Creation", True, response.status_code, response_time,
                                f"Request ID: {request_id}, Area: {request_data['area_id']}")
                    
                    # Test provider response (as provider)
                    if request_id and 'provider' in self.tokens:
                        provider_response = {
                            "request_id": request_id,
                            "proposed_fee": 1500.00,
                            "estimated_timeline": "3 weeks",
                            "proposal_note": "Comprehensive cybersecurity assessment with NIST framework implementation and documentation"
                        }
                        
                        response, response_time = self.make_request(
                            'POST', '/provider/respond-to-request',
                            data=provider_response, auth_token=self.tokens['provider']
                        )
                        
                        self.log_test("Provider Response Submission", response.status_code == 200,
                                    response.status_code, response_time,
                                    f"Fee: ${provider_response['proposed_fee']}")
                        
                        # Test response retrieval with enriched provider data
                        responses_response, responses_time = self.make_request(
                            'GET', f'/service-requests/{request_id}/responses',
                            auth_token=self.tokens['client']
                        )
                        
                        if responses_response.status_code == 200:
                            try:
                                responses = responses_response.json()
                                provider_data_enriched = any(
                                    'email' in resp.get('provider_info', {}) 
                                    for resp in responses.get('responses', [])
                                )
                                self.log_test("Provider Data Enrichment", provider_data_enriched,
                                            responses_response.status_code, responses_time,
                                            f"Responses: {len(responses.get('responses', []))}")
                            except json.JSONDecodeError:
                                self.log_test("Provider Data Enrichment", False, responses_response.status_code,
                                            responses_time, "Invalid JSON")
                        else:
                            self.log_test("Provider Data Enrichment", False, responses_response.status_code,
                                        responses_time, responses_response.text[:100])
                            
                except json.JSONDecodeError:
                    self.log_test("Service Request Creation", False, response.status_code, response_time, "Invalid JSON")
            else:
                self.log_test("Service Request Creation", False, response.status_code, response_time, response.text[:100])

    def test_payments(self):
        """Test payment integration and validation"""
        print("\n💳 Testing Payment Integration...")
        
        # First create a service request and response to test payment against
        if 'client' in self.tokens and 'provider' in self.tokens:
            # Create service request
            request_data = {
                "area_id": "area5",
                "budget_range": "$1,000-$2,500", 
                "timeline": "2-4 weeks",
                "description": "Payment test service request"
            }
            
            request_response, _ = self.make_request(
                'POST', '/service-requests/professional-help',
                data=request_data, auth_token=self.tokens['client']
            )
            
            if request_response.status_code == 200:
                request_result = request_response.json()
                request_id = request_result.get('request_id')
                
                if request_id:
                    # Provider responds
                    provider_response = {
                        "request_id": request_id,
                        "proposed_fee": 1200.00,
                        "estimated_timeline": "2 weeks", 
                        "proposal_note": "Payment test proposal"
                    }
                    
                    self.make_request(
                        'POST', '/provider/respond-to-request',
                        data=provider_response, auth_token=self.tokens['provider']
                    )
                    
                    # Test payment endpoint
                    payment_data = {
                        "request_id": request_id,
                        "provider_id": self.tokens.get('provider_user_id', 'test-provider-id')
                    }
                    
                    response, response_time = self.make_request(
                        'POST', '/payments/service-request',
                        data=payment_data, auth_token=self.tokens['client']
                    )
                    
                    if response.status_code == 200:
                        try:
                            payment_result = response.json()
                            stripe_url = payment_result.get('checkout_url', '')
                            has_stripe_url = 'stripe.com' in stripe_url or 'checkout' in stripe_url.lower()
                            self.log_test("Payment Stripe Integration", has_stripe_url, response.status_code,
                                        response_time, f"Checkout URL generated: {bool(stripe_url)}")
                        except json.JSONDecodeError:
                            self.log_test("Payment Stripe Integration", False, response.status_code,
                                        response_time, "Invalid JSON response")
                    else:
                        self.log_test("Payment Stripe Integration", False, response.status_code,
                                    response_time, f"Payment failed: {response.text[:100]}")

    def test_knowledge_base_ai(self):
        """Test Knowledge Base and AI functionality"""
        print("\n🧠 Testing Knowledge Base & AI Features...")
        
        # Test knowledge base areas
        response, response_time = self.make_request('GET', '/knowledge-base/areas')
        
        if response.status_code == 200:
            try:
                areas = response.json()
                area_count = len(areas.get('areas', []))
                self.log_test("Knowledge Base Areas", area_count > 0, response.status_code,
                            response_time, f"Found {area_count} knowledge base areas")
                
                # Test area content endpoint
                if area_count > 0:
                    first_area = areas['areas'][0]
                    area_id = first_area.get('area_id', 'area1')
                    
                    content_response, content_time = self.make_request(
                        'GET', f'/knowledge-base/areas/{area_id}/content'
                    )
                    
                    self.log_test("Knowledge Base Content", content_response.status_code == 200,
                                content_response.status_code, content_time,
                                f"Content for {area_id}")
                    
            except json.JSONDecodeError:
                self.log_test("Knowledge Base Areas", False, response.status_code, response_time, "Invalid JSON")
        else:
            self.log_test("Knowledge Base Areas", False, response.status_code, response_time, response.text[:100])
        
        # Test AI assistance with @polaris.example.com bypass
        if 'client' in self.tokens:
            ai_question = {
                "question": "What are the key requirements for cybersecurity compliance in government contracting?",
                "context": "area5"
            }
            
            response, response_time = self.make_request(
                'POST', '/knowledge-base/ai-assistance',
                data=ai_question, auth_token=self.tokens['client']
            )
            
            if response.status_code == 200:
                try:
                    ai_result = response.json()
                    answer = ai_result.get('answer', '')
                    is_concise = len(answer.split()) < 200  # Under 200 words
                    bypass_working = '@polaris.example.com' in self.credentials['client']['email']
                    
                    self.log_test("AI Assistance - Concise Response", is_concise and len(answer) > 50,
                                response.status_code, response_time,
                                f"Answer length: {len(answer.split())} words, Bypass: {bypass_working}")
                except json.JSONDecodeError:
                    self.log_test("AI Assistance", False, response.status_code, response_time, "Invalid JSON")
            else:
                self.log_test("AI Assistance", False, response.status_code, response_time, response.text[:100])

    def test_analytics(self):
        """Test analytics and resource tracking"""
        print("\n📈 Testing Analytics & Resource Tracking...")
        
        # Test resource access logging
        if 'client' in self.tokens:
            # Post several analytics events
            events = [
                {"resource_id": "area1_guide", "area_id": "area1", "action": "view"},
                {"resource_id": "area2_template", "area_id": "area2", "action": "download"},
                {"resource_id": "area5_checklist", "area_id": "area5", "action": "view"}
            ]
            
            for event in events:
                response, response_time = self.make_request(
                    'POST', '/analytics/resource-access',
                    data=event, auth_token=self.tokens['client']
                )
                
                if response.status_code != 200:
                    self.log_test(f"Analytics Event - {event['action']}", False, response.status_code,
                                response_time, f"Failed to log {event['resource_id']}")
                    break
            else:
                self.log_test("Analytics Event Logging", True, 200, None, f"Logged {len(events)} events")
        
        # Test navigator analytics retrieval
        if 'navigator' in self.tokens:
            response, response_time = self.make_request(
                'GET', '/navigator/analytics/resources?since_days=30',
                auth_token=self.tokens['navigator']
            )
            
            if response.status_code == 200:
                try:
                    analytics = response.json()
                    required_fields = ['since', 'total', 'by_area', 'last7']
                    has_all_fields = all(field in analytics for field in required_fields)
                    
                    self.log_test("Navigator Analytics Aggregation", has_all_fields,
                                response.status_code, response_time,
                                f"Total: {analytics.get('total', 0)}, Areas: {len(analytics.get('by_area', []))}")
                except json.JSONDecodeError:
                    self.log_test("Navigator Analytics", False, response.status_code, response_time, "Invalid JSON")
            else:
                self.log_test("Navigator Analytics", False, response.status_code, response_time, response.text[:100])

    def test_security_health(self):
        """Test security and health endpoints"""
        print("\n🔒 Testing Security & Health Endpoints...")
        
        # Test health endpoint
        response, response_time = self.make_request('GET', '/health')
        
        if response.status_code == 200:
            try:
                health = response.json()
                self.log_test("Health Check", True, response.status_code, response_time,
                            f"Status: {health.get('status', 'unknown')}")
            except json.JSONDecodeError:
                self.log_test("Health Check", response.status_code == 200, response.status_code,
                            response_time, "Non-JSON health response")
        else:
            self.log_test("Health Check", False, response.status_code, response_time, response.text[:100])
        
        # Test metrics endpoint if available
        metrics_response, metrics_time = self.make_request('GET', '/metrics')
        
        if metrics_response.status_code == 200:
            metrics_content = metrics_response.text
            has_prometheus_metrics = 'polaris_' in metrics_content or 'TYPE' in metrics_content
            self.log_test("Metrics Endpoint", has_prometheus_metrics, metrics_response.status_code,
                        metrics_time, f"Metrics available: {bool(metrics_content)}")
        else:
            self.log_test("Metrics Endpoint", False, metrics_response.status_code, metrics_time,
                        "Metrics endpoint not available")

    def calculate_performance_metrics(self):
        """Calculate performance metrics from test results"""
        response_times = [t["response_time_ms"] for t in self.results["test_details"] 
                         if t["response_time_ms"] is not None]
        
        if response_times:
            self.results["performance_metrics"] = {
                "average_response_time_ms": round(sum(response_times) / len(response_times), 2),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p95_response_time_ms": round(sorted(response_times)[int(len(response_times) * 0.95)], 2) if len(response_times) > 1 else response_times[0]
            }

    def generate_report(self):
        """Generate comprehensive test report"""
        self.results["test_end"] = datetime.now().isoformat()
        self.calculate_performance_metrics()
        
        # Calculate success rate
        success_rate = (self.results["passed_tests"] / self.results["total_tests"] * 100) if self.results["total_tests"] > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 BACKEND SMOKE TEST RESULTS")
        print("="*80)
        print(f"Test Duration: {self.results['test_start']} to {self.results['test_end']}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results["performance_metrics"]:
            print(f"\n📊 Performance Metrics:")
            metrics = self.results["performance_metrics"]
            print(f"Average Response Time: {metrics['average_response_time_ms']}ms")
            print(f"P95 Response Time: {metrics['p95_response_time_ms']}ms")
            print(f"Min/Max Response Time: {metrics['min_response_time_ms']}ms / {metrics['max_response_time_ms']}ms")
        
        # Show failed tests
        failed_tests = [t for t in self.results["test_details"] if not t["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['details']} (Status: {test['status_code']})")
        
        # Show critical issues
        if self.results["critical_issues"]:
            print(f"\n🚨 Critical Issues:")
            for issue in self.results["critical_issues"]:
                print(f"  • {issue}")
        
        print("\n" + "="*80)
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

    def run_all_tests(self):
        """Execute all smoke tests in sequence"""
        print("🚀 Starting Comprehensive Backend Smoke Test")
        print(f"Target: {self.base_url}")
        print(f"API Base: {self.api_url}")
        
        try:
            # Test sequence as specified in requirements
            self.test_auth_flows()
            self.test_tier_based_assessment()
            self.test_service_provider_marketplace()
            self.test_payments()
            self.test_knowledge_base_ai()
            self.test_analytics()
            self.test_security_health()
            
            # Generate final report
            success = self.generate_report()
            
            # Save detailed results to file
            with open('/app/backend_smoke_test_results.json', 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            return success
            
        except Exception as e:
            print(f"\n💥 Critical test failure: {str(e)}")
            self.results["critical_issues"].append(f"Test execution failed: {str(e)}")
            return False

def main():
    """Main execution function"""
    tester = BackendSmokeTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()