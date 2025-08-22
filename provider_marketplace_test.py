#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Test Configuration
BASE_URL = "https://readiness-hub-2.preview.emergentagent.com/api"
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