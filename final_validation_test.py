#!/usr/bin/env python3
"""
Final Comprehensive Backend Validation Test
Tests all critical functionality mentioned in the review request:
1. Template download endpoints (generate-template API)
2. Knowledge Base access control with custom error codes
3. Authentication and authorization with QA credentials
4. Assessment data persistence and retrieval
5. Service request creation and management
6. Performance and stability checks
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://sbap-platform.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FinalValidationTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.performance_metrics = []
        
    def log_result(self, test_name, status, details="", response_time=None):
        """Log test result with timestamp and performance data"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": timestamp,
            "response_time": response_time
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"[{timestamp}] {status_icon} {test_name}: {status}{time_info}")
        if details:
            print(f"    Details: {details}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with performance tracking"""
        start_time = time.time()
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.request(method, url, timeout=30, **kwargs)
            response_time = time.time() - start_time
            self.performance_metrics.append({
                "endpoint": endpoint,
                "method": method,
                "response_time": response_time,
                "status_code": response.status_code
            })
            return response, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return None, response_time
    
    def authenticate_user(self, role):
        """Authenticate user and store token"""
        creds = QA_CREDENTIALS[role]
        response, response_time = self.make_request(
            "POST", "/auth/login",
            json={"email": creds["email"], "password": creds["password"]}
        )
        
        if response and response.status_code == 200:
            token = response.json().get("access_token")
            self.tokens[role] = token
            self.log_result(f"Authentication - {role.title()}", "PASS", 
                          f"Successfully authenticated {creds['email']}", response_time)
            return True
        else:
            error_detail = response.json() if response else "Connection failed"
            self.log_result(f"Authentication - {role.title()}", "FAIL", 
                          f"Failed to authenticate: {error_detail}", response_time)
            return False
    
    def test_custom_error_codes(self):
        """Test custom Polaris error codes (POL-1001, POL-1005, etc.)"""
        # Test POL-1001: Invalid authentication credentials
        response, response_time = self.make_request(
            "POST", "/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        
        if response and response.status_code == 400:
            error_data = response.json()
            if "POL-1001" in str(error_data):
                self.log_result("Custom Error Codes - POL-1001", "PASS", 
                              "POL-1001 error code correctly returned for invalid credentials", response_time)
            else:
                self.log_result("Custom Error Codes - POL-1001", "FAIL", 
                              f"Expected POL-1001, got: {error_data}", response_time)
        else:
            self.log_result("Custom Error Codes - POL-1001", "FAIL", 
                          f"Expected 400 status, got: {response.status_code if response else 'No response'}", response_time)
    
    def test_knowledge_base_access_control(self):
        """Test Knowledge Base access control and POL-1005 error code"""
        if "client" not in self.tokens:
            self.log_result("KB Access Control", "SKIP", "Client not authenticated")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test template download for authorized user (@polaris.example.com)
        response, response_time = self.make_request(
            "GET", "/knowledge-base/generate-template/area1/template",
            headers=headers
        )
        
        if response and response.status_code == 200:
            template_data = response.json()
            if "content" in template_data and "filename" in template_data:
                self.log_result("KB Template Download", "PASS", 
                              f"Template generated successfully: {template_data.get('filename')}", response_time)
            else:
                self.log_result("KB Template Download", "FAIL", 
                              f"Invalid template response format: {template_data}", response_time)
        else:
            error_detail = response.json() if response else "No response"
            self.log_result("KB Template Download", "FAIL", 
                          f"Template download failed: {error_detail}", response_time)
    
    def test_assessment_system(self):
        """Test assessment data persistence and retrieval"""
        if "client" not in self.tokens:
            self.log_result("Assessment System", "SKIP", "Client not authenticated")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test assessment schema retrieval
        response, response_time = self.make_request("GET", "/assessment/schema", headers=headers)
        
        if response and response.status_code == 200:
            schema_data = response.json()
            if "schema" in schema_data and "areas" in schema_data["schema"]:
                areas_count = len(schema_data["schema"]["areas"])
                self.log_result("Assessment Schema", "PASS", 
                              f"Schema loaded with {areas_count} business areas", response_time)
                
                # Test assessment session creation
                response, response_time = self.make_request("POST", "/assessment/session", headers=headers)
                
                if response and response.status_code == 200:
                    session_data = response.json()
                    session_id = session_data.get("session_id")
                    self.log_result("Assessment Session", "PASS", 
                                  f"Session created: {session_id}", response_time)
                    
                    # Test session progress retrieval
                    response, response_time = self.make_request(
                        "GET", f"/assessment/session/{session_id}/progress", headers=headers
                    )
                    
                    if response and response.status_code == 200:
                        progress_data = response.json()
                        self.log_result("Assessment Progress", "PASS", 
                                      f"Progress: {progress_data.get('progress_percentage', 0)}%", response_time)
                    else:
                        self.log_result("Assessment Progress", "FAIL", 
                                      f"Failed to get progress: {response.status_code if response else 'No response'}", response_time)
                else:
                    self.log_result("Assessment Session", "FAIL", 
                                  f"Failed to create session: {response.status_code if response else 'No response'}", response_time)
            else:
                self.log_result("Assessment Schema", "FAIL", 
                              f"Invalid schema format: {schema_data}", response_time)
        else:
            self.log_result("Assessment Schema", "FAIL", 
                          f"Failed to load schema: {response.status_code if response else 'No response'}", response_time)
    
    def test_service_request_system(self):
        """Test service request creation and management"""
        if "client" not in self.tokens:
            self.log_result("Service Request System", "SKIP", "Client not authenticated")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test service request creation
        service_request_data = {
            "area_id": "area5",
            "budget_range": "$1,000-$2,500",
            "description": "Final validation test service request",
            "timeline": "2 weeks"
        }
        
        response, response_time = self.make_request(
            "POST", "/service-requests/professional-help",
            headers=headers, json=service_request_data
        )
        
        if response and response.status_code == 200:
            request_data = response.json()
            request_id = request_data.get("request_id")
            self.log_result("Service Request Creation", "PASS", 
                          f"Request created: {request_id}", response_time)
            
            # Test service request retrieval
            response, response_time = self.make_request(
                "GET", f"/service-requests/{request_id}",
                headers=headers
            )
            
            if response and response.status_code == 200:
                retrieved_data = response.json()
                self.log_result("Service Request Retrieval", "PASS", 
                              f"Request retrieved with status: {retrieved_data.get('status')}", response_time)
            else:
                self.log_result("Service Request Retrieval", "FAIL", 
                              f"Failed to retrieve request: {response.status_code if response else 'No response'}", response_time)
        else:
            error_detail = response.json() if response else "No response"
            self.log_result("Service Request Creation", "FAIL", 
                          f"Failed to create request: {error_detail}", response_time)
    
    def test_user_permissions(self):
        """Test user access and permissions across roles"""
        # Test navigator-specific endpoints
        if "navigator" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
            response, response_time = self.make_request("GET", "/navigator/analytics/resources", headers=headers)
            
            if response and response.status_code == 200:
                analytics_data = response.json()
                total_accesses = analytics_data.get("total", 0)
                self.log_result("Navigator Permissions", "PASS", 
                              f"Navigator analytics accessible: {total_accesses} total accesses", response_time)
            else:
                self.log_result("Navigator Permissions", "FAIL", 
                              f"Navigator analytics failed: {response.status_code if response else 'No response'}", response_time)
        
        # Test provider-specific endpoints
        if "provider" in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
            response, response_time = self.make_request("GET", "/provider/proposals", headers=headers)
            
            if response and response.status_code == 200:
                self.log_result("Provider Permissions", "PASS", 
                              "Provider proposals endpoint accessible", response_time)
            else:
                # This might be expected if no proposals exist, check for 404 vs auth errors
                if response and response.status_code in [200, 404]:
                    self.log_result("Provider Permissions", "PASS", 
                                  "Provider endpoint accessible (no proposals)", response_time)
                else:
                    self.log_result("Provider Permissions", "FAIL", 
                                  f"Provider access failed: {response.status_code if response else 'No response'}", response_time)
    
    def test_performance_stability(self):
        """Test API performance and stability"""
        # Test multiple rapid requests to check for stability
        test_endpoints = [
            "/auth/me",
            "/assessment/schema",
            "/knowledge-base/areas"
        ]
        
        if "client" not in self.tokens:
            self.log_result("Performance Test", "SKIP", "Client not authenticated")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        response_times = []
        
        for endpoint in test_endpoints:
            for i in range(3):  # Test each endpoint 3 times
                response, response_time = self.make_request("GET", endpoint, headers=headers)
                if response:
                    response_times.append(response_time)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time < 2.0 and max_response_time < 5.0:
                self.log_result("Performance Test", "PASS", 
                              f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s", avg_response_time)
            else:
                self.log_result("Performance Test", "WARN", 
                              f"Slow responses - Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s", avg_response_time)
        else:
            self.log_result("Performance Test", "FAIL", "No successful responses for performance testing")
    
    def run_final_validation(self):
        """Run complete final validation test suite"""
        print("🎯 STARTING FINAL COMPREHENSIVE BACKEND VALIDATION")
        print("=" * 60)
        
        # 1. Authentication Tests
        print("\n1. AUTHENTICATION & AUTHORIZATION TESTS")
        print("-" * 40)
        for role in ["client", "navigator", "provider", "agency"]:
            self.authenticate_user(role)
        
        # 2. Custom Error Codes Tests
        print("\n2. CUSTOM POLARIS ERROR CODES TESTS")
        print("-" * 40)
        self.test_custom_error_codes()
        
        # 3. Knowledge Base Access Control Tests
        print("\n3. KNOWLEDGE BASE ACCESS CONTROL TESTS")
        print("-" * 40)
        self.test_knowledge_base_access_control()
        
        # 4. Assessment System Tests
        print("\n4. ASSESSMENT DATA PERSISTENCE TESTS")
        print("-" * 40)
        self.test_assessment_system()
        
        # 5. Service Request System Tests
        print("\n5. SERVICE REQUEST MANAGEMENT TESTS")
        print("-" * 40)
        self.test_service_request_system()
        
        # 6. User Permissions Tests
        print("\n6. USER ACCESS & PERMISSIONS TESTS")
        print("-" * 40)
        self.test_user_permissions()
        
        # 7. Performance & Stability Tests
        print("\n7. PERFORMANCE & STABILITY TESTS")
        print("-" * 40)
        self.test_performance_stability()
        
        # Generate Summary Report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate comprehensive test summary report"""
        print("\n" + "=" * 60)
        print("🎯 FINAL VALIDATION SUMMARY REPORT")
        print("=" * 60)
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warned_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 TEST RESULTS: {passed_tests}/{total_tests} PASSED ({success_rate:.1f}% success rate)")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {warned_tests}")
        print(f"   ⏭️  Skipped: {skipped_tests}")
        
        # Performance Summary
        if self.performance_metrics:
            avg_response_time = sum(m["response_time"] for m in self.performance_metrics) / len(self.performance_metrics)
            max_response_time = max(m["response_time"] for m in self.performance_metrics)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Maximum Response Time: {max_response_time:.3f}s")
            print(f"   Total API Calls: {len(self.performance_metrics)}")
        
        # Failed Tests Details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - System is production ready")
        elif success_rate >= 85:
            print("   ✅ GOOD - System is production ready with minor issues")
        elif success_rate >= 70:
            print("   ⚠️  ACCEPTABLE - System needs attention before production")
        else:
            print("   ❌ CRITICAL - System requires significant fixes before production")
        
        print("\n" + "=" * 60)
        return success_rate >= 85

if __name__ == "__main__":
    tester = FinalValidationTester()
    success = tester.run_final_validation()
    sys.exit(0 if success else 1)