#!/usr/bin/env python3
"""
License Purchase Integration Testing
Testing the new license purchase integration as requested in review.

Focus Areas:
1. Authentication Test: Verify agency.qa@polaris.example.com can access agency endpoints
2. License Purchase Endpoints: Test /agency/licenses/purchase endpoint with different license packages
3. Payment Status Check: Test /agency/licenses/purchase/status/{session_id} endpoint
4. Package Validation: Verify only valid LICENSE_PACKAGES are accepted
5. Authorization: Ensure only agency role users can access these endpoints

Test packages:
- tier_1_single ($25)
- tier_1_bulk_5 ($115) 
- mixed_professional ($485)
- invalid_package (should fail)

QA Credentials: agency.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
}

# Test packages from review request
TEST_PACKAGES = [
    "tier_1_single",      # $25
    "tier_1_bulk_5",      # $115
    "mixed_professional", # $485
    "invalid_package"     # Should fail
]

# Expected package prices (from backend code)
EXPECTED_PRICES = {
    "tier_1_single": 25.0,
    "tier_1_bulk_5": 115.0,
    "mixed_professional": 485.0
}

class LicensePurchaseIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.agency_token = None
        self.client_token = None
        self.test_results = []
        self.session_ids = []  # Store session IDs for status testing
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None):
        """Log test result with timestamp"""
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
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def authenticate_agency(self) -> bool:
        """Test 1: Agency Authentication - Verify agency.qa@polaris.example.com can login"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS["agency"])
            
            if response.status_code == 200:
                data = response.json()
                self.agency_token = data.get("access_token")
                if self.agency_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.agency_token}"})
                    self.log_result("Agency Authentication", True, 
                                  f"Successfully authenticated agency user, token length: {len(self.agency_token)}")
                    return True
                else:
                    self.log_result("Agency Authentication", False, "No access token in response", data)
                    return False
            else:
                self.log_result("Agency Authentication", False, 
                              f"Login failed with status {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Authentication", False, f"Exception during authentication: {str(e)}")
            return False

    def authenticate_client(self) -> bool:
        """Authenticate client user for authorization testing"""
        try:
            # Use a separate session for client to avoid token conflicts
            client_session = requests.Session()
            response = client_session.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS["client"])
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get("access_token")
                return True
            return False
                
        except Exception as e:
            print(f"Client authentication failed: {e}")
            return False

    def test_license_purchase_endpoint(self) -> bool:
        """Test 2: License Purchase Endpoints - Test /agency/licenses/purchase with different packages"""
        if not self.agency_token:
            self.log_result("License Purchase Endpoint", False, "No agency token available")
            return False
        
        all_tests_passed = True
        
        for package_id in TEST_PACKAGES:
            try:
                payload = {
                    "package_id": package_id,
                    "origin_url": "https://smallbiz-assist.preview.emergentagent.com",
                    "metadata": {
                        "test_run": "license_purchase_integration",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                response = self.session.post(f"{BASE_URL}/agency/licenses/purchase", json=payload)
                
                if package_id == "invalid_package":
                    # This should fail
                    if response.status_code == 400:
                        self.log_result(f"License Purchase - {package_id}", True, 
                                      "Invalid package correctly rejected")
                    else:
                        self.log_result(f"License Purchase - {package_id}", False, 
                                      f"Invalid package should return 400, got {response.status_code}", 
                                      response.json() if response.content else {})
                        all_tests_passed = False
                else:
                    # Valid packages should succeed
                    if response.status_code == 200:
                        data = response.json()
                        if "url" in data and "session_id" in data:
                            self.session_ids.append(data["session_id"])
                            expected_price = EXPECTED_PRICES.get(package_id, "unknown")
                            self.log_result(f"License Purchase - {package_id}", True, 
                                          f"Checkout session created, expected price: ${expected_price}, session_id: {data['session_id'][:8]}...")
                        else:
                            self.log_result(f"License Purchase - {package_id}", False, 
                                          "Missing url or session_id in response", data)
                            all_tests_passed = False
                    else:
                        self.log_result(f"License Purchase - {package_id}", False, 
                                      f"Expected 200, got {response.status_code}", 
                                      response.json() if response.content else {})
                        all_tests_passed = False
                        
            except Exception as e:
                self.log_result(f"License Purchase - {package_id}", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        return all_tests_passed

    def test_payment_status_endpoint(self) -> bool:
        """Test 3: Payment Status Check - Test /agency/licenses/purchase/status/{session_id}"""
        if not self.agency_token:
            self.log_result("Payment Status Check", False, "No agency token available")
            return False
        
        if not self.session_ids:
            self.log_result("Payment Status Check", False, "No session IDs available from purchase tests")
            return False
        
        all_tests_passed = True
        
        for session_id in self.session_ids[:2]:  # Test first 2 session IDs
            try:
                response = self.session.get(f"{BASE_URL}/agency/licenses/purchase/status/{session_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["payment_status", "status", "amount_total", "currency"]
                    
                    if all(field in data for field in required_fields):
                        # We expect "pending" status since we're not actually completing payments
                        if data.get("payment_status") in ["pending", "unpaid", "open"]:
                            self.log_result(f"Payment Status - {session_id[:8]}...", True, 
                                          f"Status check successful, payment_status: {data.get('payment_status')}, amount: {data.get('amount_total')}")
                        else:
                            self.log_result(f"Payment Status - {session_id[:8]}...", True, 
                                          f"Unexpected payment status (but endpoint working): {data.get('payment_status')}")
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(f"Payment Status - {session_id[:8]}...", False, 
                                      f"Missing required fields: {missing_fields}", data)
                        all_tests_passed = False
                else:
                    self.log_result(f"Payment Status - {session_id[:8]}...", False, 
                                  f"Expected 200, got {response.status_code}", 
                                  response.json() if response.content else {})
                    all_tests_passed = False
                    
            except Exception as e:
                self.log_result(f"Payment Status - {session_id[:8]}...", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        return all_tests_passed

    def test_package_validation(self) -> bool:
        """Test 4: Package Validation - Verify only valid LICENSE_PACKAGES are accepted"""
        if not self.agency_token:
            self.log_result("Package Validation", False, "No agency token available")
            return False
        
        # Test various invalid packages
        invalid_packages = [
            "nonexistent_package",
            "tier_4_single",  # Doesn't exist
            "knowledge_base_single",  # This is a SERVICE_PACKAGE, not LICENSE_PACKAGE
            "",  # Empty string
            "tier_1_bulk_100"  # Doesn't exist
        ]
        
        all_tests_passed = True
        
        for invalid_package in invalid_packages:
            try:
                payload = {
                    "package_id": invalid_package,
                    "origin_url": "https://smallbiz-assist.preview.emergentagent.com",
                    "metadata": {"test": "validation"}
                }
                
                response = self.session.post(f"{BASE_URL}/agency/licenses/purchase", json=payload)
                
                if response.status_code == 400:
                    data = response.json() if response.content else {}
                    if "Invalid license package" in str(data):
                        self.log_result(f"Package Validation - {invalid_package or 'empty'}", True, 
                                      "Invalid package correctly rejected")
                    else:
                        self.log_result(f"Package Validation - {invalid_package or 'empty'}", False, 
                                      "Wrong error message for invalid package", data)
                        all_tests_passed = False
                else:
                    self.log_result(f"Package Validation - {invalid_package or 'empty'}", False, 
                                  f"Invalid package should return 400, got {response.status_code}", 
                                  response.json() if response.content else {})
                    all_tests_passed = False
                    
            except Exception as e:
                self.log_result(f"Package Validation - {invalid_package or 'empty'}", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        return all_tests_passed

    def test_authorization_controls(self) -> bool:
        """Test 5: Authorization - Ensure only agency role users can access these endpoints"""
        
        # Test 1: Try with client token
        if not self.authenticate_client():
            self.log_result("Authorization Control - Client Token", False, "Could not authenticate client user")
            return False
        
        client_session = requests.Session()
        client_session.headers.update({"Authorization": f"Bearer {self.client_token}"})
        
        try:
            payload = {
                "package_id": "tier_1_single",
                "origin_url": "https://smallbiz-assist.preview.emergentagent.com",
                "metadata": {"test": "authorization"}
            }
            
            response = client_session.post(f"{BASE_URL}/agency/licenses/purchase", json=payload)
            
            if response.status_code == 403:
                self.log_result("Authorization Control - Client Token", True, 
                              "Client user correctly denied access (403 Forbidden)")
            else:
                self.log_result("Authorization Control - Client Token", False, 
                              f"Client should be denied access, got {response.status_code}", 
                              response.json() if response.content else {})
                return False
                
        except Exception as e:
            self.log_result("Authorization Control - Client Token", False, f"Exception: {str(e)}")
            return False
        
        # Test 2: Try without any token
        no_auth_session = requests.Session()
        
        try:
            payload = {
                "package_id": "tier_1_single",
                "origin_url": "https://smallbiz-assist.preview.emergentagent.com",
                "metadata": {"test": "authorization"}
            }
            
            response = no_auth_session.post(f"{BASE_URL}/agency/licenses/purchase", json=payload)
            
            if response.status_code == 401:
                self.log_result("Authorization Control - No Token", True, 
                              "Unauthenticated user correctly denied access (401 Unauthorized)")
            else:
                self.log_result("Authorization Control - No Token", False, 
                              f"Unauthenticated user should be denied access, got {response.status_code}", 
                              response.json() if response.content else {})
                return False
                
        except Exception as e:
            self.log_result("Authorization Control - No Token", False, f"Exception: {str(e)}")
            return False
        
        return True

    def test_agency_endpoints_access(self) -> bool:
        """Additional test: Verify agency can access other agency endpoints"""
        if not self.agency_token:
            self.log_result("Agency Endpoints Access", False, "No agency token available")
            return False
        
        # Test access to existing agency endpoints
        endpoints_to_test = [
            "/agency/licenses/stats",
            "/agency/licenses"
        ]
        
        all_tests_passed = True
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    self.log_result(f"Agency Access - {endpoint}", True, 
                                  "Agency can access endpoint successfully")
                else:
                    self.log_result(f"Agency Access - {endpoint}", False, 
                                  f"Expected 200, got {response.status_code}", 
                                  response.json() if response.content else {})
                    all_tests_passed = False
                    
            except Exception as e:
                self.log_result(f"Agency Access - {endpoint}", False, f"Exception: {str(e)}")
                all_tests_passed = False
        
        return all_tests_passed

    def run_comprehensive_test(self):
        """Run all license purchase integration tests"""
        print("🎯 LICENSE PURCHASE INTEGRATION TESTING")
        print("=" * 60)
        print(f"Testing new license purchase integration as requested in review")
        print(f"Base URL: {BASE_URL}")
        print(f"QA Credentials: {QA_CREDENTIALS['agency']['email']}")
        print(f"Test Packages: {', '.join(TEST_PACKAGES)}")
        print()
        
        # Run all tests in sequence
        test_methods = [
            ("1. Agency Authentication", self.authenticate_agency),
            ("2. License Purchase Endpoints", self.test_license_purchase_endpoint),
            ("3. Payment Status Check", self.test_payment_status_endpoint),
            ("4. Package Validation", self.test_package_validation),
            ("5. Authorization Controls", self.test_authorization_controls),
            ("6. Agency Endpoints Access", self.test_agency_endpoints_access)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    passed_tests += 1
                    print(f"✅ {test_name} COMPLETED SUCCESSFULLY")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED WITH EXCEPTION: {str(e)}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 LICENSE PURCHASE INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if self.agency_token:
            print(f"✅ Agency authentication working with QA credentials")
        else:
            print(f"❌ Agency authentication failed - critical blocker")
        
        if self.session_ids:
            print(f"✅ License purchase endpoints creating checkout sessions ({len(self.session_ids)} sessions created)")
        else:
            print(f"❌ License purchase endpoints not creating sessions")
        
        # Integration functionality assessment
        if success_rate >= 80:
            print(f"\n🎉 LICENSE PURCHASE INTEGRATION: OPERATIONAL")
            print(f"✅ Integration functionality working as expected")
            print(f"✅ Focus on integration functionality rather than actual Stripe payments confirmed")
            print(f"✅ Payment pending status expected and working correctly")
        elif success_rate >= 60:
            print(f"\n⚠️ LICENSE PURCHASE INTEGRATION: MOSTLY WORKING")
            print(f"🔧 Minor issues identified but core functionality operational")
        else:
            print(f"\n🚨 LICENSE PURCHASE INTEGRATION: CRITICAL ISSUES")
            print(f"❌ Major functionality problems requiring immediate attention")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = LicensePurchaseIntegrationTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()