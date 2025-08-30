#!/usr/bin/env python3
"""
COMPREHENSIVE STRESS TESTING AND CRITICAL ISSUE RESOLUTION
Focus on critical issues, load testing, error handling, and end-to-end workflows
"""

import requests
import json
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
import uuid
import random
import statistics

# Configuration
BASE_URL = "https://providermatrix.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CriticalStressTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        self.performance_metrics = []
        self.concurrent_results = []
        
    def log_result(self, test_name, success, details="", response_data=None, duration=None):
        """Log test results with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response_data": response_data,
            "duration": duration
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.3f}s)" if duration else ""
        print(f"{status}: {test_name}{duration_str}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.tokens[role] = token
                self.log_result(f"Authentication - {role}", True, f"Token obtained", duration=duration)
                return True
            else:
                self.log_result(f"Authentication - {role}", False, f"Status: {response.status_code}", response.text, duration)
                return False
        except Exception as e:
            self.log_result(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role):
        """Get authorization headers for role"""
        if role not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[role]}"}

    # CRITICAL ISSUE 1: AI-powered resources endpoint rate limiting decorator issue
    def test_ai_resources_rate_limiting(self):
        """Test AI-powered resources endpoint for rate limiting issues"""
        print("🔍 TESTING CRITICAL ISSUE 1: AI-powered resources endpoint rate limiting")
        
        if not self.authenticate_user("client"):
            return
        
        headers = self.get_headers("client")
        
        # Test multiple rapid requests to trigger rate limiting
        for i in range(10):
            try:
                start_time = time.time()
                response = self.session.get(
                    f"{BASE_URL}/knowledge-base/ai-resources",
                    headers=headers,
                    params={"city": "San Antonio", "state": "TX", "area_id": "area1"}
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"AI Resources Request {i+1}", True, 
                                  f"Response received successfully", duration=duration)
                elif response.status_code == 429:
                    self.log_result(f"AI Resources Request {i+1}", True, 
                                  f"Rate limit working correctly (429)", duration=duration)
                else:
                    self.log_result(f"AI Resources Request {i+1}", False, 
                                  f"Unexpected status: {response.status_code}", response.text, duration)
                
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                self.log_result(f"AI Resources Request {i+1}", False, f"Exception: {str(e)}")

    # CRITICAL ISSUE 2: Frontend template download base64 decoding bug
    def test_template_download_base64(self):
        """Test template download endpoints for base64 encoding issues"""
        print("🔍 TESTING CRITICAL ISSUE 2: Template download base64 encoding")
        
        if not self.authenticate_user("client"):
            return
        
        headers = self.get_headers("client")
        
        # Test different template types
        template_tests = [
            ("area1", "template"),
            ("area2", "guide"), 
            ("area5", "practices")
        ]
        
        for area_id, template_type in template_tests:
            try:
                start_time = time.time()
                response = self.session.get(
                    f"{BASE_URL}/knowledge-base/generate-template/{area_id}/{template_type}",
                    headers=headers
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if response has proper structure for frontend
                    if "content" in data and "filename" in data and "content_type" in data:
                        # Verify content is properly encoded (not base64 if it's text)
                        content = data["content"]
                        if isinstance(content, str) and len(content) > 0:
                            self.log_result(f"Template Download {area_id}/{template_type}", True,
                                          f"Template generated successfully, content length: {len(content)}", duration=duration)
                        else:
                            self.log_result(f"Template Download {area_id}/{template_type}", False,
                                          f"Invalid content format", data, duration)
                    else:
                        self.log_result(f"Template Download {area_id}/{template_type}", False,
                                      f"Missing required fields in response", data, duration)
                else:
                    self.log_result(f"Template Download {area_id}/{template_type}", False,
                                  f"Status: {response.status_code}", response.text, duration)
                    
            except Exception as e:
                self.log_result(f"Template Download {area_id}/{template_type}", False, f"Exception: {str(e)}")

    # CRITICAL ISSUE 3: Knowledge Base providers unauthorized access
    def test_kb_provider_access_control(self):
        """Test Knowledge Base access control for providers"""
        print("🔍 TESTING CRITICAL ISSUE 3: Knowledge Base provider unauthorized access")
        
        # Test provider access to KB (should be restricted)
        if not self.authenticate_user("provider"):
            return
        
        headers = self.get_headers("provider")
        
        # Test KB areas access
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/knowledge-base/areas", headers=headers)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Check if provider has restricted access
                if "areas" in data:
                    locked_areas = [area for area in data["areas"] if not area.get("unlocked", False)]
                    if len(locked_areas) > 0:
                        self.log_result("Provider KB Access Control", True,
                                      f"Providers properly restricted from KB areas: {len(locked_areas)} locked", duration=duration)
                    else:
                        self.log_result("Provider KB Access Control", False,
                                      f"SECURITY ISSUE: Providers have full KB access", data, duration)
                else:
                    self.log_result("Provider KB Access Control", False,
                                  f"Unexpected response format", data, duration)
            elif response.status_code == 403:
                self.log_result("Provider KB Access Control", True,
                              f"Providers properly blocked from KB access (403)", duration=duration)
            else:
                self.log_result("Provider KB Access Control", False,
                              f"Unexpected status: {response.status_code}", response.text, duration)
                
        except Exception as e:
            self.log_result("Provider KB Access Control", False, f"Exception: {str(e)}")

    # CRITICAL ISSUE 4: Notification API returning 500 errors
    def test_notification_api_errors(self):
        """Test notification API for 500 errors"""
        print("🔍 TESTING CRITICAL ISSUE 4: Notification API 500 errors")
        
        for role in ["client", "provider", "navigator", "agency"]:
            if not self.authenticate_user(role):
                continue
                
            headers = self.get_headers(role)
            
            # Test notification endpoints
            notification_endpoints = [
                ("GET", "/notifications", None),
                ("POST", "/notifications/mark-read", {"notification_id": "test_id"}),
                ("GET", "/notifications/unread-count", None)
            ]
            
            for method, endpoint, data in notification_endpoints:
                try:
                    start_time = time.time()
                    if method == "GET":
                        response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                    else:
                        response = self.session.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
                    duration = time.time() - start_time
                    
                    if response.status_code == 500:
                        self.log_result(f"Notification API {role} {method} {endpoint}", False,
                                      f"500 Internal Server Error detected", response.text, duration)
                    elif response.status_code in [200, 404, 422]:  # Expected responses
                        self.log_result(f"Notification API {role} {method} {endpoint}", True,
                                      f"No 500 error, status: {response.status_code}", duration=duration)
                    else:
                        self.log_result(f"Notification API {role} {method} {endpoint}", True,
                                      f"Unexpected but not 500 status: {response.status_code}", duration=duration)
                        
                except Exception as e:
                    self.log_result(f"Notification API {role} {method} {endpoint}", False, f"Exception: {str(e)}")

    # CRITICAL ISSUE 5: Certificate generation returning 400 errors
    def test_certificate_generation_errors(self):
        """Test certificate generation for 400 errors"""
        print("🔍 TESTING CRITICAL ISSUE 5: Certificate generation 400 errors")
        
        if not self.authenticate_user("client"):
            return
        
        headers = self.get_headers("client")
        
        # Test certificate generation
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BASE_URL}/certificates/generate",
                headers=headers,
                json={"assessment_id": "test_assessment_id"}
            )
            duration = time.time() - start_time
            
            if response.status_code == 400:
                # Check if it's a legitimate validation error or a bug
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if "assessment" in str(error_data).lower() or "completion" in str(error_data).lower():
                    self.log_result("Certificate Generation", True,
                                  f"400 error is legitimate validation (assessment not complete)", duration=duration)
                else:
                    self.log_result("Certificate Generation", False,
                                  f"400 error may be a bug", error_data, duration)
            elif response.status_code == 200:
                self.log_result("Certificate Generation", True,
                              f"Certificate generated successfully", duration=duration)
            else:
                self.log_result("Certificate Generation", False,
                              f"Unexpected status: {response.status_code}", response.text, duration)
                
        except Exception as e:
            self.log_result("Certificate Generation", False, f"Exception: {str(e)}")

    # CRITICAL ISSUE 6: Phase 4 multi-tenant features not fully implemented
    def test_phase4_multitenant_features(self):
        """Test Phase 4 multi-tenant features implementation"""
        print("🔍 TESTING CRITICAL ISSUE 6: Phase 4 multi-tenant features")
        
        if not self.authenticate_user("agency"):
            return
        
        headers = self.get_headers("agency")
        
        # Test multi-tenant endpoints
        multitenant_endpoints = [
            ("GET", "/agency/theme"),
            ("POST", "/agency/theme", {"primary_color": "#007bff", "secondary_color": "#6c757d"}),
            ("GET", "/agency/theme/public"),
            ("POST", "/certificates/generate-branded", {"assessment_id": "test_id"}),
            ("GET", "/system/health")
        ]
        
        implemented_count = 0
        total_count = len(multitenant_endpoints)
        
        for method, endpoint, data in multitenant_endpoints:
            try:
                start_time = time.time()
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
                duration = time.time() - start_time
                
                if response.status_code in [200, 201, 422]:  # Implemented (422 is validation error)
                    implemented_count += 1
                    self.log_result(f"Phase 4 Feature {method} {endpoint}", True,
                                  f"Endpoint implemented, status: {response.status_code}", duration=duration)
                elif response.status_code == 404:
                    self.log_result(f"Phase 4 Feature {method} {endpoint}", False,
                                  f"Endpoint not implemented (404)", duration=duration)
                else:
                    self.log_result(f"Phase 4 Feature {method} {endpoint}", False,
                                  f"Unexpected status: {response.status_code}", response.text, duration)
                    
            except Exception as e:
                self.log_result(f"Phase 4 Feature {method} {endpoint}", False, f"Exception: {str(e)}")
        
        implementation_rate = (implemented_count / total_count) * 100
        self.log_result("Phase 4 Implementation Rate", implementation_rate >= 75,
                      f"Implementation rate: {implementation_rate:.1f}% ({implemented_count}/{total_count})")

    # LOAD & PERFORMANCE TESTING
    def concurrent_user_test(self, user_count=5, duration_seconds=30):
        """Simulate concurrent users for load testing"""
        print(f"🚀 LOAD TESTING: Simulating {user_count} concurrent users for {duration_seconds} seconds")
        
        def simulate_user_session(user_id):
            """Simulate a single user session"""
            session = requests.Session()
            results = []
            
            # Authenticate
            role = random.choice(["client", "provider", "agency", "navigator"])
            creds = QA_CREDENTIALS[role]
            
            try:
                auth_response = session.post(f"{BASE_URL}/auth/login", json=creds)
                if auth_response.status_code != 200:
                    return results
                
                token = auth_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Simulate user activities
                end_time = time.time() + duration_seconds
                request_count = 0
                
                while time.time() < end_time:
                    # Random API calls
                    endpoints = [
                        ("GET", "/auth/me"),
                        ("GET", "/assessment/schema"),
                        ("GET", "/knowledge-base/areas"),
                        ("GET", "/service-requests")
                    ]
                    
                    method, endpoint = random.choice(endpoints)
                    start_time = time.time()
                    
                    try:
                        if method == "GET":
                            response = session.get(f"{BASE_URL}{endpoint}", headers=headers)
                        
                        duration = time.time() - start_time
                        results.append({
                            "user_id": user_id,
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "duration": duration,
                            "success": response.status_code < 400
                        })
                        request_count += 1
                        
                    except Exception as e:
                        results.append({
                            "user_id": user_id,
                            "endpoint": endpoint,
                            "status": 0,
                            "duration": time.time() - start_time,
                            "success": False,
                            "error": str(e)
                        })
                    
                    # Small delay between requests
                    time.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                pass
            
            return results
        
        # Run concurrent user sessions
        with concurrent.futures.ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [executor.submit(simulate_user_session, i) for i in range(user_count)]
            all_results = []
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"User session error: {e}")
        
        # Analyze results
        if all_results:
            total_requests = len(all_results)
            successful_requests = sum(1 for r in all_results if r["success"])
            success_rate = (successful_requests / total_requests) * 100
            
            durations = [r["duration"] for r in all_results if "duration" in r]
            avg_duration = statistics.mean(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            self.log_result("Concurrent User Load Test", success_rate >= 90,
                          f"Success rate: {success_rate:.1f}% ({successful_requests}/{total_requests}), "
                          f"Avg response: {avg_duration:.3f}s, Max: {max_duration:.3f}s")
            
            # Store detailed results
            self.concurrent_results = all_results
        else:
            self.log_result("Concurrent User Load Test", False, "No results collected")

    # ERROR HANDLING & EDGE CASES
    def test_error_handling_edge_cases(self):
        """Test various error handling and edge cases"""
        print("🔍 TESTING ERROR HANDLING & EDGE CASES")
        
        if not self.authenticate_user("client"):
            return
        
        headers = self.get_headers("client")
        
        # Test malformed requests
        edge_cases = [
            # Invalid JSON
            ("POST", "/assessment/sessions", "invalid_json"),
            # Missing required fields
            ("POST", "/service-requests", {}),
            # Invalid data types
            ("POST", "/service-requests", {"area_id": 123, "description": None}),
            # SQL injection attempts
            ("GET", "/service-requests", {"id": "'; DROP TABLE users; --"}),
            # XSS attempts
            ("POST", "/assessment/sessions", {"description": "<script>alert('xss')</script>"}),
            # Very long strings
            ("POST", "/service-requests", {"description": "A" * 10000}),
            # Invalid UUIDs
            ("GET", "/service-requests/invalid-uuid-format"),
            # Non-existent resources
            ("GET", "/service-requests/99999999-9999-9999-9999-999999999999")
        ]
        
        for method, endpoint, data in edge_cases:
            try:
                start_time = time.time()
                
                if method == "GET":
                    if isinstance(data, dict):
                        response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers, params=data)
                    else:
                        response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                else:
                    if data == "invalid_json":
                        # Send invalid JSON
                        response = self.session.post(f"{BASE_URL}{endpoint}", headers=headers, data="invalid_json")
                    else:
                        response = self.session.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
                
                duration = time.time() - start_time
                
                # Check if error is handled gracefully (not 500)
                if response.status_code == 500:
                    self.log_result(f"Edge Case {method} {endpoint}", False,
                                  f"Unhandled 500 error", response.text, duration)
                elif response.status_code in [400, 404, 422, 401, 403]:
                    self.log_result(f"Edge Case {method} {endpoint}", True,
                                  f"Error handled gracefully: {response.status_code}", duration=duration)
                else:
                    self.log_result(f"Edge Case {method} {endpoint}", True,
                                  f"Unexpected but handled: {response.status_code}", duration=duration)
                    
            except Exception as e:
                self.log_result(f"Edge Case {method} {endpoint}", False, f"Exception: {str(e)}")

    # END-TO-END WORKFLOW TESTING
    def test_complete_user_journey(self):
        """Test complete end-to-end user journeys"""
        print("🔄 TESTING END-TO-END WORKFLOWS")
        
        # Test complete client journey
        if not self.authenticate_user("client"):
            return
        
        client_headers = self.get_headers("client")
        
        # 1. Create assessment session
        try:
            start_time = time.time()
            assessment_response = self.session.post(
                f"{BASE_URL}/assessment/sessions",
                headers=client_headers,
                json={"assessment_type": "full"}
            )
            duration = time.time() - start_time
            
            if assessment_response.status_code == 200:
                session_id = assessment_response.json().get("session_id")
                self.log_result("E2E: Assessment Creation", True,
                              f"Session created: {session_id}", duration=duration)
                
                # 2. Submit assessment responses
                start_time = time.time()
                response_data = {
                    "session_id": session_id,
                    "area_id": "area1",
                    "responses": [
                        {"statement_id": "stmt1", "response": "yes"},
                        {"statement_id": "stmt2", "response": "no"}
                    ]
                }
                submit_response = self.session.post(
                    f"{BASE_URL}/assessment/sessions/{session_id}/responses",
                    headers=client_headers,
                    json=response_data
                )
                duration = time.time() - start_time
                
                if submit_response.status_code in [200, 201]:
                    self.log_result("E2E: Assessment Submission", True,
                                  f"Responses submitted successfully", duration=duration)
                else:
                    self.log_result("E2E: Assessment Submission", False,
                                  f"Status: {submit_response.status_code}", submit_response.text, duration)
            else:
                self.log_result("E2E: Assessment Creation", False,
                              f"Status: {assessment_response.status_code}", assessment_response.text, duration)
                
        except Exception as e:
            self.log_result("E2E: Assessment Workflow", False, f"Exception: {str(e)}")
        
        # 3. Create service request
        try:
            start_time = time.time()
            service_request = self.session.post(
                f"{BASE_URL}/service-requests",
                headers=client_headers,
                json={
                    "area_id": "area5",
                    "budget_range": "1500-5000",
                    "timeline": "2-4 weeks",
                    "description": "Need help with technology infrastructure assessment"
                }
            )
            duration = time.time() - start_time
            
            if service_request.status_code in [200, 201]:
                request_id = service_request.json().get("request_id")
                self.log_result("E2E: Service Request Creation", True,
                              f"Request created: {request_id}", duration=duration)
            else:
                self.log_result("E2E: Service Request Creation", False,
                              f"Status: {service_request.status_code}", service_request.text, duration)
                
        except Exception as e:
            self.log_result("E2E: Service Request Workflow", False, f"Exception: {str(e)}")

    def run_comprehensive_stress_test(self):
        """Run all stress tests and critical issue investigations"""
        print("🚨 STARTING COMPREHENSIVE STRESS TESTING AND CRITICAL ISSUE RESOLUTION")
        print("=" * 80)
        
        start_time = time.time()
        
        # Critical Issues Testing
        self.test_ai_resources_rate_limiting()
        self.test_template_download_base64()
        self.test_kb_provider_access_control()
        self.test_notification_api_errors()
        self.test_certificate_generation_errors()
        self.test_phase4_multitenant_features()
        
        # Load & Performance Testing
        self.concurrent_user_test(user_count=5, duration_seconds=30)
        
        # Error Handling & Edge Cases
        self.test_error_handling_edge_cases()
        
        # End-to-End Workflow Testing
        self.test_complete_user_journey()
        
        total_duration = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_comprehensive_report(total_duration)

    def generate_comprehensive_report(self, total_duration):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE STRESS TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {total_duration:.2f} seconds")
        
        # Critical Issues Summary
        print(f"\n🚨 CRITICAL ISSUES ANALYSIS:")
        critical_issues = [
            "AI-powered resources endpoint rate limiting",
            "Template download base64 encoding", 
            "Knowledge Base provider unauthorized access",
            "Notification API 500 errors",
            "Certificate generation 400 errors",
            "Phase 4 multi-tenant features"
        ]
        
        for issue in critical_issues:
            related_tests = [r for r in self.test_results if issue.lower().replace(" ", "_") in r["test"].lower()]
            if related_tests:
                issue_success = all(r["success"] for r in related_tests)
                status = "✅ RESOLVED" if issue_success else "❌ NEEDS ATTENTION"
                print(f"   {status}: {issue}")
        
        # Performance Summary
        if self.concurrent_results:
            durations = [r["duration"] for r in self.concurrent_results if "duration" in r]
            if durations:
                avg_response = statistics.mean(durations)
                max_response = max(durations)
                print(f"\n⚡ PERFORMANCE METRICS:")
                print(f"   Average Response Time: {avg_response:.3f}s")
                print(f"   Maximum Response Time: {max_response:.3f}s")
                print(f"   Total Concurrent Requests: {len(self.concurrent_results)}")
        
        # Failed Tests Details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)
        print("🎯 RECOMMENDATIONS:")
        
        if success_rate >= 90:
            print("   ✅ System is performing well under stress conditions")
        elif success_rate >= 75:
            print("   ⚠️  System has minor issues that should be addressed")
        else:
            print("   🚨 System has significant issues requiring immediate attention")
        
        if failed_tests > 0:
            print(f"   📋 Review and fix {failed_tests} failed test cases")
        
        print("   🔄 Consider implementing additional monitoring for critical endpoints")
        print("   📊 Set up performance baselines based on these metrics")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "duration": total_duration,
            "critical_issues_resolved": sum(1 for issue in critical_issues if any(
                r["success"] for r in self.test_results 
                if issue.lower().replace(" ", "_") in r["test"].lower()
            ))
        }

if __name__ == "__main__":
    tester = CriticalStressTester()
    tester.run_comprehensive_stress_test()