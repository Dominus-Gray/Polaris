#!/usr/bin/env python3
"""
Quick Backend Smoke Test After JSX Fix
Testing critical endpoints to ensure backend functionality is intact
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

class BackendSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_time=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_time:
            print(f"   Response Time: {response_time:.3f}s")
        print()

    def test_authentication(self):
        """Test 1: Authentication with QA credentials"""
        print("🔐 Testing Authentication...")
        
        try:
            start_time = datetime.now()
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": QA_EMAIL, "password": QA_PASSWORD},
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test(
                        "Authentication with QA credentials", 
                        True, 
                        f"Successfully logged in as {QA_EMAIL}",
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication with QA credentials", 
                        False, 
                        "No access_token in response",
                        response_time
                    )
            else:
                self.log_test(
                    "Authentication with QA credentials", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
        except Exception as e:
            self.log_test(
                "Authentication with QA credentials", 
                False, 
                f"Exception: {str(e)}"
            )
        
        return False

    def test_tier_schema(self):
        """Test 2: Core Assessment - GET /api/assessment/schema/tier-based"""
        print("📊 Testing Core Assessment Schema...")
        
        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{BACKEND_URL}/assessment/schema/tier-based",
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected schema structure
                if "areas" in data and isinstance(data["areas"], list):
                    area_count = len(data["areas"])
                    has_area10 = any(area.get("id") == "area10" for area in data["areas"])
                    
                    details = f"Schema loaded with {area_count} areas"
                    if has_area10:
                        details += ", area10 (Competitive Advantage) present"
                    
                    self.log_test(
                        "Tier-based assessment schema", 
                        True, 
                        details,
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Tier-based assessment schema", 
                        False, 
                        "Invalid schema structure - missing 'areas' array",
                        response_time
                    )
            else:
                self.log_test(
                    "Tier-based assessment schema", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
        except Exception as e:
            self.log_test(
                "Tier-based assessment schema", 
                False, 
                f"Exception: {str(e)}"
            )
        
        return False

    def test_client_dashboard(self):
        """Test 3: Service Requests - GET /api/home/client"""
        print("🏠 Testing Client Dashboard Data...")
        
        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{BACKEND_URL}/home/client",
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                # Check for actual dashboard structure
                expected_keys = ["readiness", "completion_percentage", "active_services", "assessment_areas"]
                has_expected_structure = all(key in data for key in expected_keys)
                
                if has_expected_structure:
                    readiness = data.get("readiness", 0)
                    completion = data.get("completion_percentage", 0)
                    active_services = data.get("active_services", 0)
                    
                    details = f"Dashboard loaded: {readiness}% readiness, {completion}% completion, {active_services} active services"
                    
                    self.log_test(
                        "Client dashboard data", 
                        True, 
                        details,
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Client dashboard data", 
                        False, 
                        f"Missing expected keys. Got: {list(data.keys())}",
                        response_time
                    )
            else:
                self.log_test(
                    "Client dashboard data", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
        except Exception as e:
            self.log_test(
                "Client dashboard data", 
                False, 
                f"Exception: {str(e)}"
            )
        
        return False

    def test_v2_rp_requirements(self):
        """Test 4a: V2 RP Requirements - GET /api/v2/rp/requirements/all"""
        print("🔧 Testing V2 RP Requirements...")
        
        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{BACKEND_URL}/v2/rp/requirements/all",
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                # Check for actual response structure with 'items' key
                if isinstance(data, dict) and "items" in data:
                    items = data["items"]
                    if isinstance(items, list):
                        rp_count = len(items)
                        rp_types = [item.get("rp_type", "unknown") for item in items[:3]]
                        
                        self.log_test(
                            "V2 RP Requirements endpoint", 
                            True, 
                            f"Retrieved {rp_count} RP requirements, types: {rp_types}",
                            response_time
                        )
                        return True
                    else:
                        self.log_test(
                            "V2 RP Requirements endpoint", 
                            False, 
                            f"'items' is not a list: {type(items)}",
                            response_time
                        )
                else:
                    self.log_test(
                        "V2 RP Requirements endpoint", 
                        False, 
                        f"Expected dict with 'items' key, got: {type(data)} with keys {list(data.keys()) if isinstance(data, dict) else 'N/A'}",
                        response_time
                    )
            else:
                self.log_test(
                    "V2 RP Requirements endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
        except Exception as e:
            self.log_test(
                "V2 RP Requirements endpoint", 
                False, 
                f"Exception: {str(e)}"
            )
        
        return False

    def test_v2_rp_leads(self):
        """Test 4b: V2 RP Leads - GET /api/v2/rp/leads"""
        print("📋 Testing V2 RP Leads...")
        
        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{BACKEND_URL}/v2/rp/leads",
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                # Check for actual response structure with 'leads' key
                if isinstance(data, dict) and "leads" in data:
                    leads = data["leads"]
                    if isinstance(leads, list):
                        leads_count = len(leads)
                        
                        details = f"Retrieved {leads_count} leads"
                        if leads_count > 0:
                            first_lead = leads[0]
                            if "lead_id" in first_lead:
                                details += f", first lead ID: {first_lead['lead_id'][:8]}..."
                        
                        self.log_test(
                            "V2 RP Leads endpoint", 
                            True, 
                            details,
                            response_time
                        )
                        return True
                    else:
                        self.log_test(
                            "V2 RP Leads endpoint", 
                            False, 
                            f"'leads' is not a list: {type(leads)}",
                            response_time
                        )
                else:
                    self.log_test(
                        "V2 RP Leads endpoint", 
                        False, 
                        f"Expected dict with 'leads' key, got: {type(data)} with keys {list(data.keys()) if isinstance(data, dict) else 'N/A'}",
                        response_time
                    )
            else:
                self.log_test(
                    "V2 RP Leads endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response_time
                )
        except Exception as e:
            self.log_test(
                "V2 RP Leads endpoint", 
                False, 
                f"Exception: {str(e)}"
            )
        
        return False

    def run_smoke_tests(self):
        """Run all smoke tests"""
        print("🚀 Starting Backend Smoke Test After JSX Fix")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_EMAIL}")
        print("=" * 60)
        print()
        
        # Test 1: Authentication (required for other tests)
        auth_success = self.test_authentication()
        
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with other tests")
            return self.generate_summary()
        
        # Test 2: Core Assessment Schema
        self.test_tier_schema()
        
        # Test 3: Client Dashboard
        self.test_client_dashboard()
        
        # Test 4a: V2 RP Requirements
        self.test_v2_rp_requirements()
        
        # Test 4b: V2 RP Leads
        self.test_v2_rp_leads()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("📊 BACKEND SMOKE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result["success"]:
                    print(f"  • {result['test']}")
            print()
        
        # Overall assessment
        if success_rate >= 80:
            print("🎉 OVERALL ASSESSMENT: BACKEND FUNCTIONALITY INTACT")
            print("✅ Core endpoints are working correctly after JSX fix")
        elif success_rate >= 60:
            print("⚠️  OVERALL ASSESSMENT: MOSTLY FUNCTIONAL WITH MINOR ISSUES")
            print("🔧 Some endpoints need attention but core functionality works")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL ISSUES DETECTED")
            print("❌ Backend functionality may be compromised")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = BackendSmokeTest()
    summary = tester.run_smoke_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["success_rate"] >= 80 else 1)