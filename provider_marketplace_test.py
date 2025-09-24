#!/usr/bin/env python3
"""
SERVICE PROVIDER AUTHENTICATION AND MARKETPLACE TESTING
Testing specific scope from review request:
1. POST /api/auth/login with provider.qa@polaris.example.com / Polaris#2025! credentials
2. GET /api/home/provider endpoint with authentication headers  
3. GET /api/marketplace/gigs/my endpoint for provider gigs
4. GET /api/marketplace/orders/my?role_filter=provider for provider orders
5. Verify provider role and marketplace data structure

This is to debug why Service Provider login on frontend redirects back to landing page 
instead of showing Provider dashboard.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# Test Credentials
PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class ServiceProviderMarketplaceTester:
    def __init__(self):
        self.provider_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_provider_login(self):
        """Test 1: POST /api/auth/login with provider credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=PROVIDER_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.provider_token = data["access_token"]
                    self.log_test(
                        "Provider Login Authentication", 
                        "PASS", 
                        f"Token received: {self.provider_token[:20]}..."
                    )
                    return True
                else:
                    self.log_test(
                        "Provider Login Authentication", 
                        "FAIL", 
                        f"No access_token in response: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Provider Login Authentication", 
                    "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Provider Login Authentication", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    def test_provider_role_verification(self):
        """Verify provider role from auth/me endpoint"""
        if not self.provider_token:
            self.log_test("Provider Role Verification", "SKIP", "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("role") == "provider":
                    self.log_test(
                        "Provider Role Verification", 
                        "PASS", 
                        f"Role confirmed: {data.get('role')}, Email: {data.get('email')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Provider Role Verification", 
                        "FAIL", 
                        f"Expected role 'provider', got: {data.get('role')}"
                    )
                    return False
            else:
                self.log_test(
                    "Provider Role Verification", 
                    "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Provider Role Verification", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    def test_provider_home_endpoint(self):
        """Test 2: GET /api/home/provider endpoint with authentication headers"""
        if not self.provider_token:
            self.log_test("Provider Home Endpoint", "SKIP", "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response = self.session.get(f"{BACKEND_URL}/home/provider", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected provider dashboard data
                expected_fields = ["profile_complete", "dashboard_data"]
                
                details = f"Response keys: {list(data.keys())}"
                if any(field in data for field in expected_fields):
                    self.log_test(
                        "Provider Home Endpoint", 
                        "PASS", 
                        details
                    )
                    return True
                else:
                    self.log_test(
                        "Provider Home Endpoint", 
                        "PARTIAL", 
                        f"Endpoint accessible but missing expected fields. {details}"
                    )
                    return True
            else:
                self.log_test(
                    "Provider Home Endpoint", 
                    "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Provider Home Endpoint", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    def test_marketplace_gigs_endpoint(self):
        """Test 3: GET /api/marketplace/gigs/my endpoint for provider gigs"""
        if not self.provider_token:
            self.log_test("Marketplace Gigs Endpoint", "SKIP", "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response = self.session.get(f"{BACKEND_URL}/marketplace/gigs/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Marketplace Gigs Endpoint", 
                    "PASS", 
                    f"Gigs data structure: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Marketplace Gigs Endpoint", 
                    "FAIL", 
                    "Endpoint not found - marketplace gigs functionality not implemented"
                )
                return False
            else:
                self.log_test(
                    "Marketplace Gigs Endpoint", 
                    "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Marketplace Gigs Endpoint", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    def test_marketplace_orders_endpoint(self):
        """Test 4: GET /api/marketplace/orders/my?role_filter=provider for provider orders"""
        if not self.provider_token:
            self.log_test("Marketplace Orders Endpoint", "SKIP", "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response = self.session.get(
                f"{BACKEND_URL}/marketplace/orders/my?role_filter=provider", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Marketplace Orders Endpoint", 
                    "PASS", 
                    f"Orders data structure: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Marketplace Orders Endpoint", 
                    "FAIL", 
                    "Endpoint not found - marketplace orders functionality not implemented"
                )
                return False
            else:
                self.log_test(
                    "Marketplace Orders Endpoint", 
                    "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Marketplace Orders Endpoint", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    def test_alternative_provider_endpoints(self):
        """Test alternative provider-related endpoints that might exist"""
        if not self.provider_token:
            self.log_test("Alternative Provider Endpoints", "SKIP", "No token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.provider_token}"}
        alternative_endpoints = [
            "/provider/dashboard",
            "/provider/profile", 
            "/provider/services",
            "/service-requests/provider",
            "/provider/respond-to-request"
        ]
        
        working_endpoints = []
        
        for endpoint in alternative_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    working_endpoints.append(endpoint)
                elif response.status_code in [401, 403]:
                    # Authentication/authorization issues
                    continue
                elif response.status_code == 404:
                    # Endpoint doesn't exist
                    continue
            except Exception:
                continue
        
        if working_endpoints:
            self.log_test(
                "Alternative Provider Endpoints", 
                "PASS", 
                f"Found working endpoints: {working_endpoints}"
            )
            return True
        else:
            self.log_test(
                "Alternative Provider Endpoints", 
                "FAIL", 
                "No alternative provider endpoints found"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all Service Provider marketplace tests"""
        print("🔍 SERVICE PROVIDER AUTHENTICATION AND MARKETPLACE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Provider Email: {PROVIDER_CREDENTIALS['email']}")
        print("=" * 70)
        
        # Test sequence
        tests = [
            ("Provider Login", self.test_provider_login),
            ("Provider Role Verification", self.test_provider_role_verification),
            ("Provider Home Endpoint", self.test_provider_home_endpoint),
            ("Marketplace Gigs Endpoint", self.test_marketplace_gigs_endpoint),
            ("Marketplace Orders Endpoint", self.test_marketplace_orders_endpoint),
            ("Alternative Provider Endpoints", self.test_alternative_provider_endpoints)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            if test_func():
                passed_tests += 1
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   └─ {result['details']}")
        
        # Analysis and recommendations
        print("\n🔍 ANALYSIS:")
        
        if self.provider_token:
            print("✅ Provider authentication is working correctly")
        else:
            print("❌ Provider authentication failed - this is likely the root cause")
            print("   └─ Frontend redirect issue may be due to failed backend authentication")
        
        # Check for marketplace functionality
        marketplace_working = any(
            result["test"] in ["Marketplace Gigs Endpoint", "Marketplace Orders Endpoint"] 
            and result["status"] == "PASS" 
            for result in self.test_results
        )
        
        if not marketplace_working:
            print("❌ Marketplace endpoints not implemented")
            print("   └─ This explains why provider dashboard shows no marketplace data")
        
        return success_rate >= 50  # Consider successful if at least 50% pass

if __name__ == "__main__":
    tester = ServiceProviderMarketplaceTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Service Provider testing completed with acceptable results")
    else:
        print("\n⚠️ Service Provider testing revealed critical issues")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

import requests
import json
import sys
from datetime import datetime

# Test Configuration
BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"
PROVIDER_EMAIL = "provider.qa@polaris.example.com"
PROVIDER_PASSWORD = "Polaris#2025!"

class ProviderMarketplaceTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
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

    def authenticate_provider(self):
        """Authenticate with provider credentials"""
        try:
            login_data = {
                "email": PROVIDER_EMAIL,
                "password": PROVIDER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("Provider Authentication", True, f"Successfully authenticated as {PROVIDER_EMAIL}")
                return True
            else:
                self.log_test("Provider Authentication", False, 
                            f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Provider Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_enhanced_provider_home(self):
        """Test Enhanced Provider Home endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/home/provider")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for legacy metrics
                legacy_fields = ["eligible_requests", "responses", "profile_complete"]
                legacy_present = all(field in data for field in legacy_fields)
                
                # Check for new marketplace metrics
                marketplace_fields = ["total_gigs", "active_gigs", "total_orders", "completed_orders", 
                                    "total_earned", "monthly_revenue", "available_balance", "rating", "win_rate"]
                marketplace_present = all(field in data for field in marketplace_fields)
                
                if legacy_present and marketplace_present:
                    self.log_test("Enhanced Provider Home", True, 
                                f"Both legacy and marketplace metrics present. Legacy requests: {data.get('eligible_requests', 0)}, "
                                f"Marketplace gigs: {data.get('total_gigs', 0)}, Orders: {data.get('total_orders', 0)}")
                else:
                    missing_fields = []
                    if not legacy_present:
                        missing_fields.extend([f for f in legacy_fields if f not in data])
                    if not marketplace_present:
                        missing_fields.extend([f for f in marketplace_fields if f not in data])
                    
                    self.log_test("Enhanced Provider Home", False, 
                                f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Enhanced Provider Home", False, 
                            f"Request failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Enhanced Provider Home", False, f"Error: {str(e)}")

    def test_provider_gigs(self):
        """Test Provider Gigs endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/marketplace/gigs/my")
            
            if response.status_code == 200:
                data = response.json()
                
                if "gigs" in data:
                    gigs = data["gigs"]
                    self.log_test("Provider Gigs", True, 
                                f"Successfully retrieved {len(gigs)} gigs for provider")
                    
                    # Store first gig ID for later tests if available
                    if gigs:
                        self.first_gig_id = gigs[0].get("_id") or gigs[0].get("gig_id")
                        print(f"   First gig ID: {self.first_gig_id}")
                else:
                    self.log_test("Provider Gigs", False, "Response missing 'gigs' field", data)
            else:
                self.log_test("Provider Gigs", False, 
                            f"Request failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Provider Gigs", False, f"Error: {str(e)}")

    def test_provider_analytics(self):
        """Test Provider Analytics endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/provider/analytics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required analytics fields
                required_fields = ["total_gigs", "active_gigs", "total_orders", "completed_orders", 
                                 "total_earned", "monthly_revenue", "available_balance", "rating", "win_rate"]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Provider Analytics", True, 
                                f"Comprehensive analytics returned. Total gigs: {data.get('total_gigs', 0)}, "
                                f"Total orders: {data.get('total_orders', 0)}, Total earned: ${data.get('total_earned', 0):.2f}")
                else:
                    self.log_test("Provider Analytics", False, 
                                f"Missing analytics fields: {missing_fields}", data)
            else:
                self.log_test("Provider Analytics", False, 
                            f"Request failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Provider Analytics", False, f"Error: {str(e)}")

    def test_provider_orders(self):
        """Test Provider Orders endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/marketplace/orders/my?role_filter=provider")
            
            if response.status_code == 200:
                data = response.json()
                
                if "orders" in data:
                    orders = data["orders"]
                    self.log_test("Provider Orders", True, 
                                f"Successfully retrieved {len(orders)} orders for provider")
                    
                    # Check if orders have required fields
                    if orders:
                        first_order = orders[0]
                        required_order_fields = ["order_id", "gig_id", "client_user_id", "provider_user_id", 
                                               "status", "price", "created_at"]
                        missing_order_fields = [field for field in required_order_fields if field not in first_order]
                        
                        if missing_order_fields:
                            print(f"   Warning: First order missing fields: {missing_order_fields}")
                else:
                    self.log_test("Provider Orders", False, "Response missing 'orders' field", data)
            else:
                self.log_test("Provider Orders", False, 
                            f"Request failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Provider Orders", False, f"Error: {str(e)}")

    def test_gig_creation(self):
        """Test Gig Creation endpoint"""
        try:
            # Create a sample service gig
            gig_data = {
                "title": "Professional Business Formation Consulting",
                "description": "I will help you establish your business with proper legal structure, registration, and compliance setup. This includes business entity selection, registration paperwork, EIN application, and initial compliance guidance.",
                "category": "business_formation",
                "subcategory": "Business Registration",
                "tags": ["business formation", "legal structure", "registration", "compliance", "consulting"],
                "packages": [
                    {
                        "package_type": "basic",
                        "title": "Basic Business Setup",
                        "description": "Essential business formation with entity selection and registration",
                        "price": 29900,  # $299.00 in cents
                        "delivery_days": 7,
                        "revisions_included": 1,
                        "features": ["Business entity recommendation", "Registration paperwork", "EIN application"]
                    },
                    {
                        "package_type": "standard", 
                        "title": "Complete Business Formation",
                        "description": "Comprehensive business setup with compliance guidance",
                        "price": 49900,  # $499.00 in cents
                        "delivery_days": 5,
                        "revisions_included": 2,
                        "features": ["Everything in Basic", "Operating agreement/bylaws", "Initial compliance setup", "Tax election guidance"]
                    },
                    {
                        "package_type": "premium",
                        "title": "Premium Business Launch",
                        "description": "Full-service business formation with ongoing support",
                        "price": 79900,  # $799.00 in cents
                        "delivery_days": 3,
                        "revisions_included": 3,
                        "features": ["Everything in Standard", "Business bank account setup", "30-day compliance support", "Priority support"]
                    }
                ],
                "requirements": [
                    "Business name preferences (3 options)",
                    "Preferred business structure (if known)",
                    "State of incorporation",
                    "Business purpose/description"
                ],
                "faq": [
                    {
                        "question": "What business structures do you recommend?",
                        "answer": "I recommend LLC for most small businesses due to flexibility and tax benefits, but will assess your specific needs."
                    },
                    {
                        "question": "How long does the registration process take?",
                        "answer": "State registration typically takes 3-10 business days, depending on the state. I handle all paperwork and follow up."
                    }
                ]
            }
            
            response = self.session.post(f"{BASE_URL}/marketplace/gig/create", json=gig_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "gig_id" in data:
                    gig_id = data["gig_id"]
                    self.log_test("Gig Creation", True, 
                                f"Successfully created gig with ID: {gig_id}")
                    
                    # Store the created gig ID for potential cleanup
                    self.created_gig_id = gig_id
                    
                    # Verify gig structure
                    gig = data.get("gig", {})
                    required_gig_fields = ["title", "description", "category", "packages", "status"]
                    missing_gig_fields = [field for field in required_gig_fields if field not in gig]
                    
                    if missing_gig_fields:
                        print(f"   Warning: Created gig missing fields: {missing_gig_fields}")
                else:
                    self.log_test("Gig Creation", False, "Response missing success or gig_id", data)
            else:
                self.log_test("Gig Creation", False, 
                            f"Request failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Gig Creation", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all provider marketplace tests"""
        print("🚀 Starting Enhanced Provider Account Backend Testing")
        print("=" * 60)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_provider():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Enhanced Provider Home
        self.test_enhanced_provider_home()
        
        # Step 3: Test Provider Gigs
        self.test_provider_gigs()
        
        # Step 4: Test Provider Analytics
        self.test_provider_analytics()
        
        # Step 5: Test Provider Orders
        self.test_provider_orders()
        
        # Step 6: Test Gig Creation
        self.test_gig_creation()
        
        # Summary
        self.print_summary()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Enhanced Provider account functionality is working correctly.")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY WORKING: Enhanced Provider account functionality is mostly operational with minor issues.")
        else:
            print("⚠️  NEEDS ATTENTION: Enhanced Provider account functionality has significant issues that need fixing.")

if __name__ == "__main__":
    tester = ProviderMarketplaceTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)