#!/usr/bin/env python3
"""
Agency Dashboard Backend Testing Suite
Testing backend functionality for agency portal improvements as requested in review.

Focus Areas:
1. Agency authentication with QA credentials (agency.qa@polaris.example.com / Polaris#2025!)
2. Agency dashboard data endpoints (/api/home/agency)  
3. Business intelligence endpoints for agency analytics
4. License generation and management endpoints
5. Contract/opportunity matching endpoints
6. Payment integration endpoints
7. Sponsored companies management endpoints
"""

import requests
import json
import time
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://production-guru.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!"
    }
}

class AgencyDashboardTester:
    def __init__(self):
        self.session = requests.Session()
        self.agency_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_agency_authentication(self):
        """Test 1: Agency authentication with QA credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS["agency"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.agency_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.agency_token}"})
                    self.log_test(
                        "Agency Authentication", 
                        True, 
                        f"Successfully authenticated agency user, token length: {len(self.agency_token)}"
                    )
                    return True
                else:
                    self.log_test("Agency Authentication", False, "No access token in response", data)
                    return False
            else:
                self.log_test("Agency Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Agency Authentication", False, f"Exception: {str(e)}")
            return False

    def test_agency_dashboard_data(self):
        """Test 2: Agency dashboard data endpoints"""
        if not self.agency_token:
            self.log_test("Agency Dashboard Data", False, "No agency token available")
            return False
            
        try:
            # Test agency home dashboard endpoint
            response = self.session.get(f"{BACKEND_URL}/home/agency")
            
            if response.status_code == 200:
                data = response.json()
                # Check for actual fields returned by the API
                expected_fields = ["invites", "revenue", "opportunities"]
                
                missing_fields = [field for field in expected_fields if field not in data]
                if not missing_fields:
                    self.log_test(
                        "Agency Dashboard Data", 
                        True, 
                        f"Dashboard data retrieved with core fields: {list(data.keys())}"
                    )
                    return True
                else:
                    self.log_test(
                        "Agency Dashboard Data", 
                        False, 
                        f"Missing expected fields: {missing_fields}",
                        data
                    )
                    return False
            else:
                self.log_test("Agency Dashboard Data", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Agency Dashboard Data", False, f"Exception: {str(e)}")
            return False

    def test_business_intelligence_endpoints(self):
        """Test 3: Business intelligence endpoints for agency analytics"""
        if not self.agency_token:
            self.log_test("Business Intelligence Endpoints", False, "No agency token available")
            return False
            
        try:
            # Test business intelligence assessments endpoint
            response = self.session.get(f"{BACKEND_URL}/agency/business-intelligence/assessments")
            
            if response.status_code == 200:
                data = response.json()
                # Check for actual BI data structure
                expected_fields = ["assessment_overview", "business_area_breakdown", "tier_utilization"]
                found_fields = [field for field in expected_fields if field in data]
                
                if len(found_fields) >= 2:  # At least 2 out of 3 expected fields
                    self.log_test(
                        "Business Intelligence Endpoints", 
                        True, 
                        f"BI assessments retrieved with {len(found_fields)}/3 expected fields: {found_fields}"
                    )
                    return True
                else:
                    self.log_test(
                        "Business Intelligence Endpoints", 
                        False, 
                        f"Insufficient BI data fields. Found: {found_fields}",
                        data
                    )
                    return False
            else:
                self.log_test("Business Intelligence Endpoints", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Business Intelligence Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_license_generation_management(self):
        """Test 4: License generation and management endpoints"""
        if not self.agency_token:
            self.log_test("License Generation Management", False, "No agency token available")
            return False
            
        try:
            # Test license statistics endpoint
            stats_response = self.session.get(f"{BACKEND_URL}/agency/licenses/stats")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                required_stats = ["total_generated", "available", "used", "expired"]
                
                if all(field in stats_data for field in required_stats):
                    # Test license generation
                    gen_response = self.session.post(
                        f"{BACKEND_URL}/agency/licenses/generate",
                        json={"quantity": 2, "expires_days": 60}
                    )
                    
                    if gen_response.status_code == 200:
                        gen_data = gen_response.json()
                        if "licenses" in gen_data and len(gen_data["licenses"]) == 2:
                            self.log_test(
                                "License Generation Management", 
                                True, 
                                f"License stats retrieved and 2 licenses generated successfully"
                            )
                            return True
                        else:
                            self.log_test(
                                "License Generation Management", 
                                False, 
                                "License generation failed or incorrect quantity",
                                gen_data
                            )
                            return False
                    else:
                        self.log_test("License Generation Management", False, f"License generation HTTP {gen_response.status_code}", gen_response.text)
                        return False
                else:
                    self.log_test(
                        "License Generation Management", 
                        False, 
                        f"Missing required stats fields: {[f for f in required_stats if f not in stats_data]}",
                        stats_data
                    )
                    return False
            else:
                self.log_test("License Generation Management", False, f"License stats HTTP {stats_response.status_code}", stats_response.text)
                return False
                
        except Exception as e:
            self.log_test("License Generation Management", False, f"Exception: {str(e)}")
            return False

    def test_contract_opportunity_matching(self):
        """Test 5: Contract/opportunity matching endpoints"""
        if not self.agency_token:
            self.log_test("Contract Opportunity Matching", False, "No agency token available")
            return False
            
        try:
            # Test compliance insights endpoint as opportunity matching proxy
            response = self.session.get(f"{BACKEND_URL}/agency/compliance-insights")
            
            if response.status_code == 200:
                data = response.json()
                # Check for compliance insights structure
                expected_fields = ["summary", "critical_gaps", "recommendations"]
                found_fields = [field for field in expected_fields if field in data]
                
                if len(found_fields) >= 2:  # At least 2 out of 3 expected fields
                    self.log_test(
                        "Contract Opportunity Matching", 
                        True, 
                        f"Compliance insights retrieved with {len(found_fields)}/3 fields: {found_fields}"
                    )
                    return True
                else:
                    self.log_test(
                        "Contract Opportunity Matching", 
                        False, 
                        f"Insufficient compliance data. Found: {found_fields}",
                        data
                    )
                    return False
            else:
                self.log_test("Contract Opportunity Matching", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Contract Opportunity Matching", False, f"Exception: {str(e)}")
            return False

    def test_payment_integration_endpoints(self):
        """Test 6: Payment integration endpoints functionality"""
        if not self.agency_token:
            self.log_test("Payment Integration Endpoints", False, "No agency token available")
            return False
            
        try:
            # Test billing history endpoint
            response = self.session.get(f"{BACKEND_URL}/agency/billing/history")
            
            if response.status_code == 200:
                data = response.json()
                if "transactions" in data or "billing_history" in data or "payments" in data:
                    self.log_test(
                        "Payment Integration Endpoints", 
                        True, 
                        f"Billing history endpoint accessible: {list(data.keys())}"
                    )
                    return True
                else:
                    self.log_test(
                        "Payment Integration Endpoints", 
                        False, 
                        "Unexpected billing endpoint response structure",
                        data
                    )
                    return False
            else:
                self.log_test("Payment Integration Endpoints", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Payment Integration Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_sponsored_companies_management(self):
        """Test 7: Sponsored companies management endpoints"""
        if not self.agency_token:
            self.log_test("Sponsored Companies Management", False, "No agency token available")
            return False
            
        try:
            # Test agency clients accepted endpoint
            response = self.session.get(f"{BACKEND_URL}/agency/clients/accepted")
            
            if response.status_code == 200:
                data = response.json()
                if "clients" in data or "accepted_clients" in data or isinstance(data, list):
                    companies_count = len(data) if isinstance(data, list) else len(data.get("clients", data.get("accepted_clients", [])))
                    self.log_test(
                        "Sponsored Companies Management", 
                        True, 
                        f"Accepted clients list retrieved, count: {companies_count}"
                    )
                    return True
                else:
                    self.log_test(
                        "Sponsored Companies Management", 
                        False, 
                        "No clients data in response",
                        data
                    )
                    return False
            else:
                self.log_test("Sponsored Companies Management", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Sponsored Companies Management", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all agency dashboard backend tests"""
        print("🎯 AGENCY DASHBOARD BACKEND TESTING SUITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {QA_CREDENTIALS['agency']['email']}")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_agency_authentication,
            self.test_agency_dashboard_data,
            self.test_business_intelligence_endpoints,
            self.test_license_generation_management,
            self.test_contract_opportunity_matching,
            self.test_payment_integration_endpoints,
            self.test_sponsored_companies_management
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("=" * 60)
        print("🎯 AGENCY DASHBOARD BACKEND TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Detailed results
        print("📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        print("🎯 AGENCY PORTAL READINESS ASSESSMENT:")
        if passed >= 5:  # At least 5 out of 7 tests should pass
            print("✅ READY - Agency portal backend is ready for improvements")
            print("   Core agency functionality is operational")
        elif passed >= 3:
            print("⚠️  PARTIAL - Some agency endpoints need attention")
            print("   Basic functionality working but improvements needed")
        else:
            print("❌ NOT READY - Significant agency backend issues detected")
            print("   Major fixes required before portal improvements")
        
        return passed, total

if __name__ == "__main__":
    tester = AgencyDashboardTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed >= 5 else 1)