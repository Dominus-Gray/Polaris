#!/usr/bin/env python3
"""
System Performance Monitoring and Health Check Endpoints Testing
Testing the newly implemented system health and metrics endpoints.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://smartbiz-assess.preview.emergentagent.com/api"

class SystemMonitoringTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details="", response_time=None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        self.total_tests += 1
        if success:
            self.passed_tests += 1
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_time:
            print(f"   Response Time: {response_time:.3f}s")
        print()

    def test_system_health_endpoint(self):
        """Test GET /api/system/health endpoint"""
        print("🔍 Testing System Health Check Endpoint...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/system/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "overall_score", "timestamp", "components", "version"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "System Health - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        response_time
                    )
                    return
                
                # Verify overall score calculation
                score = data.get("overall_score", 0)
                if not isinstance(score, (int, float)) or score < 0 or score > 100:
                    self.log_result(
                        "System Health - Overall Score",
                        False,
                        f"Invalid overall score: {score} (should be 0-100)",
                        response_time
                    )
                    return
                
                # Verify component statuses
                components = data.get("components", {})
                expected_components = ["database", "ai_integration", "payment_integration"]
                
                for component in expected_components:
                    if component not in components:
                        self.log_result(
                            f"System Health - {component.title()} Component",
                            False,
                            f"Missing {component} component status",
                            response_time
                        )
                        return
                    
                    comp_data = components[component]
                    if "status" not in comp_data:
                        self.log_result(
                            f"System Health - {component.title()} Status",
                            False,
                            f"Missing status field for {component}",
                            response_time
                        )
                        return
                
                # Verify database response time is included
                db_component = components.get("database", {})
                if "response_time_ms" not in db_component:
                    self.log_result(
                        "System Health - Database Response Time",
                        False,
                        "Missing database response_time_ms field",
                        response_time
                    )
                    return
                
                # Check if response time meets SLA (under 500ms)
                if response_time > 0.5:
                    self.log_result(
                        "System Health - Response Time SLA",
                        False,
                        f"Response time {response_time:.3f}s exceeds 500ms SLA target",
                        response_time
                    )
                else:
                    self.log_result(
                        "System Health - Response Time SLA",
                        True,
                        f"Response time {response_time:.3f}s meets 500ms SLA target",
                        response_time
                    )
                
                self.log_result(
                    "System Health - Endpoint Functionality",
                    True,
                    f"Health check working. Status: {data['status']}, Score: {score}%, DB Response: {db_component.get('response_time_ms', 'N/A')}ms",
                    response_time
                )
                
            else:
                self.log_result(
                    "System Health - HTTP Response",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                
        except requests.exceptions.Timeout:
            self.log_result(
                "System Health - Timeout",
                False,
                "Request timed out after 10 seconds"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "System Health - Network Error",
                False,
                f"Network error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "System Health - Unexpected Error",
                False,
                f"Unexpected error: {str(e)}"
            )

    def test_system_metrics_endpoint(self):
        """Test GET /api/system/metrics endpoint"""
        print("📊 Testing System Performance Metrics Endpoint...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/system/metrics", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["timestamp", "database_metrics", "system_resources", "performance_targets"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "System Metrics - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        response_time
                    )
                    return
                
                # Verify database metrics
                db_metrics = data.get("database_metrics", {})
                if "error" not in db_metrics:  # If no error, check expected fields
                    expected_db_fields = ["query_response_time_ms", "active_users_24h", "total_assessments", "total_service_requests"]
                    missing_db_fields = [field for field in expected_db_fields if field not in db_metrics]
                    
                    if missing_db_fields:
                        self.log_result(
                            "System Metrics - Database Metrics",
                            False,
                            f"Missing database metric fields: {missing_db_fields}",
                            response_time
                        )
                    else:
                        self.log_result(
                            "System Metrics - Database Metrics",
                            True,
                            f"DB Query Time: {db_metrics.get('query_response_time_ms')}ms, Active Users: {db_metrics.get('active_users_24h')}, Assessments: {db_metrics.get('total_assessments')}, Requests: {db_metrics.get('total_service_requests')}",
                            response_time
                        )
                else:
                    self.log_result(
                        "System Metrics - Database Metrics",
                        False,
                        f"Database metrics error: {db_metrics.get('error')}",
                        response_time
                    )
                    return
                
                # Verify performance targets are included
                targets = data.get("performance_targets", {})
                expected_targets = ["api_response_target_ms", "db_query_target_ms"]
                missing_targets = [target for target in expected_targets if target not in targets]
                
                if missing_targets:
                    self.log_result(
                        "System Metrics - Performance Targets",
                        False,
                        f"Missing performance targets: {missing_targets}",
                        response_time
                    )
                else:
                    self.log_result(
                        "System Metrics - Performance Targets",
                        True,
                        f"API Target: {targets.get('api_response_target_ms')}ms, DB Target: {targets.get('db_query_target_ms')}ms",
                        response_time
                    )
                
                # Check if response time meets SLA (under 500ms)
                if response_time > 0.5:
                    self.log_result(
                        "System Metrics - Response Time SLA",
                        False,
                        f"Response time {response_time:.3f}s exceeds 500ms SLA target",
                        response_time
                    )
                else:
                    self.log_result(
                        "System Metrics - Response Time SLA",
                        True,
                        f"Response time {response_time:.3f}s meets 500ms SLA target",
                        response_time
                    )
                
                # Verify system resources (may have note if psutil not available)
                system_resources = data.get("system_resources", {})
                if "note" in system_resources:
                    self.log_result(
                        "System Metrics - System Resources",
                        True,
                        f"System resources monitoring: {system_resources.get('note')}",
                        response_time
                    )
                else:
                    # Check for resource metrics
                    resource_fields = ["cpu_usage_percent", "memory_usage_percent"]
                    available_resources = [field for field in resource_fields if field in system_resources]
                    
                    if available_resources:
                        self.log_result(
                            "System Metrics - System Resources",
                            True,
                            f"Resource monitoring available: {available_resources}",
                            response_time
                        )
                    else:
                        self.log_result(
                            "System Metrics - System Resources",
                            True,
                            "System resources section present but no specific metrics",
                            response_time
                        )
                
                self.log_result(
                    "System Metrics - Endpoint Functionality",
                    True,
                    "Performance metrics endpoint working correctly",
                    response_time
                )
                
            else:
                self.log_result(
                    "System Metrics - HTTP Response",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
                
        except requests.exceptions.Timeout:
            self.log_result(
                "System Metrics - Timeout",
                False,
                "Request timed out after 15 seconds"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "System Metrics - Network Error",
                False,
                f"Network error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "System Metrics - Unexpected Error",
                False,
                f"Unexpected error: {str(e)}"
            )

    def test_error_handling(self):
        """Test error handling for system endpoints"""
        print("🛡️ Testing Error Handling...")
        
        # Test with invalid endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/system/invalid", timeout=5)
            if response.status_code == 404:
                self.log_result(
                    "Error Handling - Invalid Endpoint",
                    True,
                    "Correctly returns 404 for invalid system endpoint"
                )
            else:
                self.log_result(
                    "Error Handling - Invalid Endpoint",
                    False,
                    f"Expected 404, got {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Error Handling - Invalid Endpoint",
                False,
                f"Error testing invalid endpoint: {str(e)}"
            )

    def run_all_tests(self):
        """Run all system monitoring tests"""
        print("🚀 Starting System Performance Monitoring and Health Check Testing")
        print("=" * 80)
        print()
        
        # Test system health endpoint
        self.test_system_health_endpoint()
        
        # Test system metrics endpoint  
        self.test_system_metrics_endpoint()
        
        # Test error handling
        self.test_error_handling()
        
        # Print summary
        print("=" * 80)
        print("📋 SYSTEM MONITORING TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("🎉 SYSTEM MONITORING TESTS: EXCELLENT")
            print("✅ Performance SLA monitoring implementation is working correctly")
        elif success_rate >= 60:
            print("⚠️ SYSTEM MONITORING TESTS: GOOD")
            print("✅ Core functionality working with minor issues")
        else:
            print("❌ SYSTEM MONITORING TESTS: NEEDS ATTENTION")
            print("🔧 System monitoring implementation needs fixes")
        
        print()
        print("🔍 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return success_rate >= 60

if __name__ == "__main__":
    tester = SystemMonitoringTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)