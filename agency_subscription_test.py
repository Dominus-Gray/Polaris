#!/usr/bin/env python3
"""
Agency Subscription System Testing
Testing the newly implemented Agency Subscription System endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://frontend-sync-3.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "agency.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class AgencySubscriptionTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
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

    def authenticate(self):
        """Authenticate with QA credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test(
                    "Agency Authentication", 
                    True, 
                    f"Successfully authenticated as {QA_CREDENTIALS['email']}"
                )
                return True
            else:
                self.log_test(
                    "Agency Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Agency Authentication", False, f"Exception: {str(e)}")
            return False

    def test_subscription_tiers(self):
        """Test GET /api/agency/subscription/tiers - verify all 4 tiers are returned"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/agency/subscription/tiers",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tiers = data.get("tiers", [])
                
                # Check if we have 4 tiers
                if len(tiers) == 4:
                    tier_ids = [tier.get("tier_id") for tier in tiers]
                    expected_tiers = ["starter", "professional", "enterprise", "enterprise_plus"]
                    
                    if all(tier_id in tier_ids for tier_id in expected_tiers):
                        # Verify pricing and features for each tier
                        pricing_correct = True
                        features_correct = True
                        
                        for tier in tiers:
                            tier_id = tier.get("tier_id")
                            
                            # Check required fields
                            required_fields = ["tier_id", "name", "monthly_price", "annual_price", 
                                             "client_limit", "license_codes_per_month", "features", "support_level"]
                            
                            if not all(field in tier for field in required_fields):
                                pricing_correct = False
                                break
                            
                            # Check specific pricing for known tiers
                            if tier_id == "starter" and tier.get("monthly_price") != 14900:
                                pricing_correct = False
                            elif tier_id == "professional" and tier.get("monthly_price") != 29900:
                                pricing_correct = False
                            elif tier_id == "enterprise" and tier.get("monthly_price") != 59900:
                                pricing_correct = False
                            elif tier_id == "enterprise_plus" and tier.get("monthly_price") != 99900:
                                pricing_correct = False
                            
                            # Check features are present
                            if not isinstance(tier.get("features"), list) or len(tier.get("features", [])) == 0:
                                features_correct = False
                        
                        if pricing_correct and features_correct:
                            self.log_test(
                                "Subscription Tiers Endpoint",
                                True,
                                f"All 4 tiers returned with correct pricing and features. Tiers: {', '.join(tier_ids)}"
                            )
                        else:
                            self.log_test(
                                "Subscription Tiers Endpoint",
                                False,
                                f"Pricing or features incorrect. Pricing OK: {pricing_correct}, Features OK: {features_correct}",
                                data
                            )
                    else:
                        self.log_test(
                            "Subscription Tiers Endpoint",
                            False,
                            f"Missing expected tiers. Found: {tier_ids}, Expected: {expected_tiers}",
                            data
                        )
                else:
                    self.log_test(
                        "Subscription Tiers Endpoint",
                        False,
                        f"Expected 4 tiers, got {len(tiers)}",
                        data
                    )
            else:
                self.log_test(
                    "Subscription Tiers Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Subscription Tiers Endpoint", False, f"Exception: {str(e)}")

    def test_current_subscription(self):
        """Test GET /api/agency/subscription/current - test with agency user"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/agency/subscription/current",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                subscription = data.get("subscription")
                tier_details = data.get("tier_details")
                
                if subscription and tier_details:
                    # Check if it's trial/default subscription
                    tier_id = subscription.get("tier_id")
                    status = subscription.get("status")
                    
                    # Should have required fields
                    required_fields = ["tier_id", "tier_name", "status"]
                    if all(field in subscription for field in required_fields):
                        
                        # Check if trial or active subscription
                        if status in ["trial", "active"]:
                            current_usage = subscription.get("current_usage", {})
                            
                            if "clients_active" in current_usage and "license_codes_used_this_month" in current_usage:
                                self.log_test(
                                    "Current Subscription Endpoint",
                                    True,
                                    f"Subscription returned: {tier_id} ({status}) with usage tracking"
                                )
                            else:
                                self.log_test(
                                    "Current Subscription Endpoint",
                                    False,
                                    "Missing usage tracking in subscription response",
                                    data
                                )
                        else:
                            self.log_test(
                                "Current Subscription Endpoint",
                                False,
                                f"Unexpected subscription status: {status}",
                                data
                            )
                    else:
                        self.log_test(
                            "Current Subscription Endpoint",
                            False,
                            "Missing required subscription fields",
                            data
                        )
                else:
                    self.log_test(
                        "Current Subscription Endpoint",
                        False,
                        "Missing subscription or tier_details in response",
                        data
                    )
            else:
                self.log_test(
                    "Current Subscription Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Current Subscription Endpoint", False, f"Exception: {str(e)}")

    def test_subscription_upgrade(self):
        """Test POST /api/agency/subscription/upgrade - test upgrading from starter to professional"""
        try:
            upgrade_data = {
                "tier_id": "professional",
                "billing_cycle": "monthly"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/subscription/upgrade",
                json=upgrade_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    subscription = data.get("subscription")
                    tier_details = data.get("tier_details")
                    
                    if subscription and tier_details:
                        # Verify upgrade was successful
                        if (subscription.get("tier_id") == "professional" and 
                            subscription.get("status") == "active" and
                            tier_details.get("name") == "Professional"):
                            
                            self.log_test(
                                "Subscription Upgrade Endpoint",
                                True,
                                f"Successfully upgraded to Professional tier. Subscription ID: {subscription.get('subscription_id')}"
                            )
                        else:
                            self.log_test(
                                "Subscription Upgrade Endpoint",
                                False,
                                "Upgrade response doesn't match expected professional tier",
                                data
                            )
                    else:
                        self.log_test(
                            "Subscription Upgrade Endpoint",
                            False,
                            "Missing subscription or tier_details in upgrade response",
                            data
                        )
                else:
                    self.log_test(
                        "Subscription Upgrade Endpoint",
                        False,
                        "Upgrade not successful according to response",
                        data
                    )
            else:
                self.log_test(
                    "Subscription Upgrade Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Subscription Upgrade Endpoint", False, f"Exception: {str(e)}")

    def test_usage_tracking(self):
        """Test POST /api/agency/subscription/usage/track - test tracking license code usage"""
        try:
            # Test tracking license code usage
            response = self.session.post(
                f"{BACKEND_URL}/agency/subscription/usage/track?usage_type=license_code",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    updated_usage = data.get("updated_usage")
                    
                    if updated_usage:
                        # Check if license codes generated was incremented
                        license_codes_generated = updated_usage.get("license_codes_generated", 0)
                        
                        if license_codes_generated > 0:
                            self.log_test(
                                "Usage Tracking Endpoint",
                                True,
                                f"Successfully tracked license code usage. Total generated: {license_codes_generated}"
                            )
                        else:
                            self.log_test(
                                "Usage Tracking Endpoint",
                                False,
                                "License codes generated count not incremented",
                                data
                            )
                    else:
                        self.log_test(
                            "Usage Tracking Endpoint",
                            False,
                            "Missing updated_usage in response",
                            data
                        )
                else:
                    self.log_test(
                        "Usage Tracking Endpoint",
                        False,
                        "Usage tracking not successful according to response",
                        data
                    )
            else:
                self.log_test(
                    "Usage Tracking Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Usage Tracking Endpoint", False, f"Exception: {str(e)}")

    def test_license_generation_limits(self):
        """Test POST /api/agency/licenses/generate - test that license generation respects subscription limits"""
        try:
            license_data = {
                "count": 3,
                "expires_in_days": 30
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/licenses/generate",
                json=license_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    license_codes = data.get("license_codes", [])
                    
                    if len(license_codes) == 3:
                        # Verify license codes format
                        valid_codes = all(
                            isinstance(code, dict) and 
                            "license_code" in code and 
                            "expires_at" in code 
                            for code in license_codes
                        )
                        
                        if valid_codes:
                            self.log_test(
                                "License Generation with Limits",
                                True,
                                f"Successfully generated {len(license_codes)} license codes within subscription limits"
                            )
                        else:
                            self.log_test(
                                "License Generation with Limits",
                                False,
                                "Generated license codes don't have proper format",
                                data
                            )
                    else:
                        self.log_test(
                            "License Generation with Limits",
                            False,
                            f"Expected 3 license codes, got {len(license_codes)}",
                            data
                        )
                else:
                    self.log_test(
                        "License Generation with Limits",
                        False,
                        "License generation not successful according to response",
                        data
                    )
            elif response.status_code == 400:
                # Check if it's a subscription limit error
                error_text = response.text
                if "limit reached" in error_text.lower() or "upgrade" in error_text.lower():
                    self.log_test(
                        "License Generation with Limits",
                        True,
                        "License generation properly respects subscription limits (limit reached)"
                    )
                else:
                    self.log_test(
                        "License Generation with Limits",
                        False,
                        f"Unexpected 400 error: {error_text}",
                        response.text
                    )
            else:
                self.log_test(
                    "License Generation with Limits",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("License Generation with Limits", False, f"Exception: {str(e)}")

    def test_usage_analytics(self):
        """Test GET /api/agency/subscription/usage - verify usage history is returned"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/agency/subscription/usage?months=6",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                usage_history = data.get("usage_history", [])
                current_limits = data.get("current_limits")
                current_tier = data.get("current_tier")
                
                if usage_history and current_limits and current_tier:
                    # Check usage history format
                    valid_history = all(
                        isinstance(entry, dict) and
                        "month" in entry and
                        "clients_active" in entry and
                        "license_codes_generated" in entry
                        for entry in usage_history
                    )
                    
                    # Check current limits format
                    valid_limits = (
                        "client_limit" in current_limits and
                        "license_codes_per_month" in current_limits
                    )
                    
                    if valid_history and valid_limits:
                        self.log_test(
                            "Usage Analytics Endpoint",
                            True,
                            f"Usage history returned for {len(usage_history)} months. Current tier: {current_tier}"
                        )
                    else:
                        self.log_test(
                            "Usage Analytics Endpoint",
                            False,
                            f"Invalid format. History valid: {valid_history}, Limits valid: {valid_limits}",
                            data
                        )
                else:
                    self.log_test(
                        "Usage Analytics Endpoint",
                        False,
                        "Missing required fields in usage analytics response",
                        data
                    )
            else:
                self.log_test(
                    "Usage Analytics Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Usage Analytics Endpoint", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all subscription system tests"""
        print("🚀 Starting Agency Subscription System Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return 0, 1
        
        # Run all tests
        self.test_subscription_tiers()
        self.test_current_subscription()
        self.test_subscription_upgrade()
        self.test_usage_tracking()
        self.test_license_generation_limits()
        self.test_usage_analytics()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = AgencySubscriptionTester()
    result = tester.run_all_tests()
    
    if result:
        passed, failed = result
        if failed == 0:
            print("\n🎉 All tests passed! Agency Subscription System is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
    else:
        print("\n❌ Testing failed to complete.")