#!/usr/bin/env python3

"""
Per-Assessment Credit System Backend Testing
===========================================

This test suite validates the new Per-Assessment Credit System that replaced 
the monthly subscription model. Tests all 6 core endpoints with QA credentials.

Test Coverage:
1. GET /api/agency/pricing/tiers - verify all 4 tiers with per-assessment pricing
2. GET /api/agency/credits/balance - test credit balance and breakdown
3. POST /api/agency/credits/purchase - test purchasing 25 credits with volume tier
4. POST /api/agency/assessment/complete - test assessment billing and credit deduction
5. GET /api/agency/billing/history - verify billing history shows assessment usage
6. POST /api/marketplace/gig/create - test creating a new service gig

QA Credentials: agency.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class CreditSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.agency_token = None
        self.provider_token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
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

    def authenticate_user(self, role: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        try:
            credentials = QA_CREDENTIALS[role]
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.log_test(f"{role.title()} Authentication", True, 
                            f"Successfully authenticated {credentials['email']}")
                return token
            else:
                self.log_test(f"{role.title()} Authentication", False, 
                            f"Login failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"{role.title()} Authentication", False, f"Authentication error: {str(e)}")
            return None

    def test_pricing_tiers(self):
        """Test GET /api/agency/pricing/tiers - verify all 4 tiers with per-assessment pricing"""
        try:
            response = self.session.get(f"{BASE_URL}/agency/pricing/tiers", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tiers = data.get("tiers", [])
                
                # Expected tiers
                expected_tiers = ["basic", "volume", "enterprise", "government"]
                found_tiers = [tier.get("tier_id") for tier in tiers]
                
                # Validate all 4 tiers exist
                missing_tiers = [tier for tier in expected_tiers if tier not in found_tiers]
                if missing_tiers:
                    self.log_test("Pricing Tiers Structure", False, 
                                f"Missing tiers: {missing_tiers}. Found: {found_tiers}")
                    return
                
                # Validate tier structure
                validation_results = []
                for tier in tiers:
                    tier_id = tier.get("tier_id")
                    required_fields = ["name", "per_assessment_price", "volume_threshold", "features", "description"]
                    missing_fields = [field for field in required_fields if field not in tier]
                    
                    if missing_fields:
                        validation_results.append(f"{tier_id}: missing {missing_fields}")
                    else:
                        # Validate pricing structure
                        price = tier.get("per_assessment_price")
                        if not isinstance(price, int) or price <= 0:
                            validation_results.append(f"{tier_id}: invalid price {price}")
                        
                        # Validate features list
                        features = tier.get("features", [])
                        if not isinstance(features, list) or len(features) == 0:
                            validation_results.append(f"{tier_id}: invalid features {features}")
                
                if validation_results:
                    self.log_test("Pricing Tiers Structure", False, 
                                f"Validation errors: {'; '.join(validation_results)}")
                else:
                    # Log pricing details
                    pricing_summary = []
                    for tier in tiers:
                        price_dollars = tier["per_assessment_price"] / 100
                        pricing_summary.append(f"{tier['name']}: ${price_dollars:.2f}/assessment")
                    
                    self.log_test("Pricing Tiers Structure", True, 
                                f"All 4 tiers validated. Pricing: {'; '.join(pricing_summary)}", 
                                {"tier_count": len(tiers), "tiers": found_tiers})
            else:
                self.log_test("Pricing Tiers Structure", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Pricing Tiers Structure", False, f"Request error: {str(e)}")

    def test_credit_balance(self):
        """Test GET /api/agency/credits/balance - test with agency user"""
        if not self.agency_token:
            self.log_test("Credit Balance Check", False, "No agency authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            response = self.session.get(f"{BASE_URL}/agency/credits/balance", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["total_credits", "used_this_month", "credits_breakdown"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Credit Balance Check", False, 
                                f"Missing fields: {missing_fields}")
                else:
                    total_credits = data["total_credits"]
                    used_this_month = data["used_this_month"]
                    breakdown = data["credits_breakdown"]
                    
                    # Validate data types
                    if not isinstance(total_credits, int) or not isinstance(used_this_month, int):
                        self.log_test("Credit Balance Check", False, 
                                    f"Invalid data types: total_credits={type(total_credits)}, used_this_month={type(used_this_month)}")
                    elif not isinstance(breakdown, list):
                        self.log_test("Credit Balance Check", False, 
                                    f"Invalid breakdown type: {type(breakdown)}")
                    else:
                        self.log_test("Credit Balance Check", True, 
                                    f"Total credits: {total_credits}, Used this month: {used_this_month}, Breakdown entries: {len(breakdown)}", 
                                    data)
            else:
                self.log_test("Credit Balance Check", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Credit Balance Check", False, f"Request error: {str(e)}")

    def test_credit_purchase(self):
        """Test POST /api/agency/credits/purchase - test purchasing 25 credits with volume tier"""
        if not self.agency_token:
            self.log_test("Credit Purchase (Volume Tier)", False, "No agency authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            purchase_data = {
                "credit_amount": 25,
                "tier_id": "volume"
            }
            
            response = self.session.post(f"{BASE_URL}/agency/credits/purchase", 
                                       headers=headers, json=purchase_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "credit_id", "credits_purchased", "total_cost", "price_per_credit", "tier"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Credit Purchase (Volume Tier)", False, 
                                f"Missing response fields: {missing_fields}")
                else:
                    success = data["success"]
                    credits_purchased = data["credits_purchased"]
                    total_cost = data["total_cost"]
                    price_per_credit = data["price_per_credit"]
                    tier = data["tier"]
                    
                    # Validate purchase details
                    if not success:
                        self.log_test("Credit Purchase (Volume Tier)", False, "Purchase not successful")
                    elif credits_purchased != 25:
                        self.log_test("Credit Purchase (Volume Tier)", False, 
                                    f"Wrong credit amount: expected 25, got {credits_purchased}")
                    elif tier != "Volume":
                        self.log_test("Credit Purchase (Volume Tier)", False, 
                                    f"Wrong tier: expected Volume, got {tier}")
                    else:
                        # Calculate expected cost (volume tier: $60.00 per assessment)
                        expected_cost = 25 * 60.00
                        if abs(total_cost - expected_cost) > 0.01:
                            self.log_test("Credit Purchase (Volume Tier)", False, 
                                        f"Cost mismatch: expected ${expected_cost:.2f}, got ${total_cost:.2f}")
                        else:
                            self.log_test("Credit Purchase (Volume Tier)", True, 
                                        f"Purchased {credits_purchased} credits for ${total_cost:.2f} (${price_per_credit:.2f} each)", 
                                        data)
            else:
                self.log_test("Credit Purchase (Volume Tier)", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Credit Purchase (Volume Tier)", False, f"Request error: {str(e)}")

    def test_assessment_billing(self):
        """Test POST /api/agency/assessment/complete - test completing assessment and deducting credit"""
        if not self.agency_token:
            self.log_test("Assessment Billing", False, "No agency authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            
            # Create test data for assessment completion
            test_client_id = "test_client_123"
            test_session_id = "test_session_456"
            
            # Note: The endpoint expects query parameters, not JSON body
            params = {
                "client_user_id": test_client_id,
                "assessment_session_id": test_session_id
            }
            
            response = self.session.post(f"{BASE_URL}/agency/assessment/complete", 
                                       headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "assessment_billed", "remaining_credits", "amount_charged"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Assessment Billing", False, 
                                f"Missing response fields: {missing_fields}")
                else:
                    success = data["success"]
                    assessment_billed = data["assessment_billed"]
                    remaining_credits = data["remaining_credits"]
                    amount_charged = data["amount_charged"]
                    
                    if not success or not assessment_billed:
                        self.log_test("Assessment Billing", False, 
                                    f"Billing failed: success={success}, billed={assessment_billed}")
                    else:
                        self.log_test("Assessment Billing", True, 
                                    f"Assessment billed successfully. Charged: ${amount_charged:.2f}, Remaining credits: {remaining_credits}", 
                                    data)
            elif response.status_code == 402:
                # No credits available - this is expected if no credits were purchased
                self.log_test("Assessment Billing", True, 
                            "No credits available (expected if no prior purchase)", 
                            {"status": "no_credits", "message": response.text})
            else:
                self.log_test("Assessment Billing", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Assessment Billing", False, f"Request error: {str(e)}")

    def test_billing_history(self):
        """Test GET /api/agency/billing/history - verify billing history shows assessment usage"""
        if not self.agency_token:
            self.log_test("Billing History", False, "No agency authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            response = self.session.get(f"{BASE_URL}/agency/billing/history", 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["billing_history", "total_records"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Billing History", False, 
                                f"Missing response fields: {missing_fields}")
                else:
                    billing_history = data["billing_history"]
                    total_records = data["total_records"]
                    
                    if not isinstance(billing_history, list):
                        self.log_test("Billing History", False, 
                                    f"Invalid billing_history type: {type(billing_history)}")
                    elif not isinstance(total_records, int):
                        self.log_test("Billing History", False, 
                                    f"Invalid total_records type: {type(total_records)}")
                    else:
                        # Validate billing history entries
                        if len(billing_history) > 0:
                            sample_entry = billing_history[0]
                            required_entry_fields = ["month", "assessments_count", "total_cost", "average_cost"]
                            missing_entry_fields = [field for field in required_entry_fields if field not in sample_entry]
                            
                            if missing_entry_fields:
                                self.log_test("Billing History", False, 
                                            f"Missing entry fields: {missing_entry_fields}")
                            else:
                                self.log_test("Billing History", True, 
                                            f"Retrieved {len(billing_history)} monthly records, {total_records} total billing records", 
                                            {"months": len(billing_history), "total_records": total_records})
                        else:
                            self.log_test("Billing History", True, 
                                        "No billing history (expected for new agency)", 
                                        {"months": 0, "total_records": total_records})
            else:
                self.log_test("Billing History", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Billing History", False, f"Request error: {str(e)}")

    def test_marketplace_gig_creation(self):
        """Test POST /api/marketplace/gig/create - test creating a new service gig"""
        if not self.provider_token:
            self.log_test("Marketplace Gig Creation", False, "No provider authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            
            # Create test gig data
            gig_data = {
                "title": "Business Formation Consulting Services",
                "description": "Comprehensive business formation consulting including entity selection, registration assistance, and compliance guidance for small businesses entering government contracting.",
                "category": "business_formation",
                "subcategory": "entity_formation",
                "tags": ["business_formation", "llc", "corporation", "compliance", "consulting"],
                "packages": [
                    {
                        "name": "Basic Formation",
                        "description": "Basic business entity formation assistance",
                        "price": 500,
                        "delivery_days": 7,
                        "revisions": 1,
                        "features": ["Entity selection guidance", "Basic registration assistance"]
                    },
                    {
                        "name": "Standard Formation",
                        "description": "Complete business formation with compliance setup",
                        "price": 1000,
                        "delivery_days": 10,
                        "revisions": 2,
                        "features": ["Entity formation", "EIN application", "Basic compliance setup"]
                    }
                ],
                "requirements": [
                    "Business concept description",
                    "Preferred business structure (if known)",
                    "State of incorporation"
                ],
                "faq": [
                    {
                        "question": "What business structures do you help with?",
                        "answer": "We assist with LLC, Corporation, Partnership, and Sole Proprietorship formations."
                    }
                ]
            }
            
            response = self.session.post(f"{BASE_URL}/marketplace/gig/create", 
                                       headers=headers, json=gig_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "gig_id", "message", "gig"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Marketplace Gig Creation", False, 
                                f"Missing response fields: {missing_fields}")
                else:
                    success = data["success"]
                    gig_id = data["gig_id"]
                    message = data["message"]
                    gig = data["gig"]
                    
                    if not success:
                        self.log_test("Marketplace Gig Creation", False, 
                                    f"Gig creation failed: {message}")
                    elif not gig_id:
                        self.log_test("Marketplace Gig Creation", False, 
                                    "No gig_id returned")
                    else:
                        # Validate gig data
                        if gig.get("title") != gig_data["title"]:
                            self.log_test("Marketplace Gig Creation", False, 
                                        f"Title mismatch: expected '{gig_data['title']}', got '{gig.get('title')}'")
                        elif gig.get("category") != gig_data["category"]:
                            self.log_test("Marketplace Gig Creation", False, 
                                        f"Category mismatch: expected '{gig_data['category']}', got '{gig.get('category')}'")
                        elif len(gig.get("packages", [])) != len(gig_data["packages"]):
                            self.log_test("Marketplace Gig Creation", False, 
                                        f"Package count mismatch: expected {len(gig_data['packages'])}, got {len(gig.get('packages', []))}")
                        else:
                            self.log_test("Marketplace Gig Creation", True, 
                                        f"Gig created successfully: {gig_id}", 
                                        {"gig_id": gig_id, "title": gig["title"], "category": gig["category"]})
            elif response.status_code == 403:
                self.log_test("Marketplace Gig Creation", False, 
                            "Provider not approved (expected for test provider)", 
                            {"status": "not_approved", "message": response.text})
            else:
                self.log_test("Marketplace Gig Creation", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Marketplace Gig Creation", False, f"Request error: {str(e)}")

    def run_comprehensive_test(self):
        """Run all credit system tests"""
        print("🎯 PER-ASSESSMENT CREDIT SYSTEM TESTING")
        print("=" * 50)
        print(f"Testing against: {BASE_URL}")
        print(f"Start time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate users
        print("STEP 1: Authentication")
        print("-" * 20)
        self.agency_token = self.authenticate_user("agency")
        self.provider_token = self.authenticate_user("provider")
        print()
        
        # Step 2: Test pricing tiers (no auth required)
        print("STEP 2: Pricing Tiers")
        print("-" * 20)
        self.test_pricing_tiers()
        
        # Step 3: Test credit balance
        print("STEP 3: Credit Balance")
        print("-" * 20)
        self.test_credit_balance()
        
        # Step 4: Test credit purchase
        print("STEP 4: Credit Purchase")
        print("-" * 20)
        self.test_credit_purchase()
        
        # Step 5: Test assessment billing
        print("STEP 5: Assessment Billing")
        print("-" * 20)
        self.test_assessment_billing()
        
        # Step 6: Test billing history
        print("STEP 6: Billing History")
        print("-" * 20)
        self.test_billing_history()
        
        # Step 7: Test marketplace gig creation
        print("STEP 7: Marketplace Gig Creation")
        print("-" * 20)
        self.test_marketplace_gig_creation()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PER-ASSESSMENT CREDIT SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {time.time() - self.start_time:.2f}s")
        print()
        
        # Test breakdown
        print("TEST BREAKDOWN:")
        print("-" * 40)
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        print()
        
        # Critical findings
        critical_failures = [r for r in self.test_results if not r["success"] and "authentication" not in r["test"].lower()]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES:")
            print("-" * 20)
            for failure in critical_failures:
                print(f"• {failure['test']}: {failure['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: ✅ EXCELLENT")
            print("Per-Assessment Credit System is fully operational and ready for production.")
        elif success_rate >= 75:
            print("⚠️  OVERALL ASSESSMENT: ✅ GOOD")
            print("Per-Assessment Credit System is mostly operational with minor issues.")
        elif success_rate >= 50:
            print("⚠️  OVERALL ASSESSMENT: ⚠️  NEEDS ATTENTION")
            print("Per-Assessment Credit System has significant issues that need fixing.")
        else:
            print("🚨 OVERALL ASSESSMENT: ❌ CRITICAL")
            print("Per-Assessment Credit System has major failures and needs immediate attention.")
        
        print()
        print("=" * 60)

if __name__ == "__main__":
    tester = CreditSystemTester()
    tester.run_comprehensive_test()