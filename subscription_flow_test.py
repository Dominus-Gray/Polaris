#!/usr/bin/env python3
"""
Complete Agency Subscription Flow Test
Testing the complete flow: Get current subscription -> Upgrade to professional -> Check usage analytics -> Generate license codes
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://polaris-requirements.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "agency.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class SubscriptionFlowTest:
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
                self.auth_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Agency Authentication", True, 
                             f"Successfully authenticated as {QA_CREDENTIALS['email']}")
                return True
            else:
                self.log_test("Agency Authentication", False, 
                             f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Agency Authentication", False, f"Exception: {str(e)}")
            return False

    def step1_get_current_subscription(self):
        """Step 1: Get current subscription"""
        try:
            response = self.session.get(f"{BACKEND_URL}/agency/subscription/current", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                subscription = data.get("subscription", {})
                tier_name = subscription.get("tier_name", "unknown")
                status = subscription.get("status", "unknown")
                
                self.log_test("Step 1: Get Current Subscription", True, 
                             f"Current tier: {tier_name}, Status: {status}")
                return data
            else:
                self.log_test("Step 1: Get Current Subscription", False, 
                             f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Step 1: Get Current Subscription", False, f"Exception: {str(e)}")
            return None

    def step2_upgrade_to_professional(self):
        """Step 2: Upgrade to professional tier"""
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
                    subscription = data.get("subscription", {})
                    tier_id = subscription.get("tier_id", "unknown")
                    self.log_test("Step 2: Upgrade to Professional", True, 
                                 f"Successfully upgraded to {tier_id}")
                    return data
                else:
                    self.log_test("Step 2: Upgrade to Professional", False, 
                                 "Upgrade not successful", data)
                    return None
            else:
                self.log_test("Step 2: Upgrade to Professional", False, 
                             f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Step 2: Upgrade to Professional", False, f"Exception: {str(e)}")
            return None

    def step3_check_usage_analytics(self):
        """Step 3: Check usage analytics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/agency/subscription/usage", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                usage_history = data.get("usage_history", [])
                current_limits = data.get("current_limits", {})
                current_tier = data.get("current_tier", "unknown")
                
                self.log_test("Step 3: Check Usage Analytics", True, 
                             f"Current tier: {current_tier}, History entries: {len(usage_history)}")
                return data
            else:
                self.log_test("Step 3: Check Usage Analytics", False, 
                             f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Step 3: Check Usage Analytics", False, f"Exception: {str(e)}")
            return None

    def step4_generate_license_codes(self):
        """Step 4: Generate license codes to test limits"""
        try:
            license_data = {
                "quantity": 3,  # Changed from "count" to "quantity" based on error
                "expires_in_days": 30
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/licenses/generate",
                json=license_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                license_codes = data.get("license_codes", [])
                if license_codes:
                    # Mask license codes for security
                    masked_codes = [f"****{code[-4:]}" for code in license_codes]
                    self.log_test("Step 4: Generate License Codes", True, 
                                 f"Generated {len(license_codes)} codes: {masked_codes}")
                    return data
                else:
                    self.log_test("Step 4: Generate License Codes", False, 
                                 "No license codes in response", data)
                    return None
            else:
                self.log_test("Step 4: Generate License Codes", False, 
                             f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Step 4: Generate License Codes", False, f"Exception: {str(e)}")
            return None

    def run_complete_flow(self):
        """Run the complete subscription flow"""
        print("🎯 COMPLETE AGENCY SUBSCRIPTION FLOW TEST")
        print("=" * 60)
        print("Testing the complete flow as requested in review:")
        print("1. Get current subscription")
        print("2. Upgrade to professional tier")
        print("3. Check usage analytics")
        print("4. Generate license codes to test limits")
        print()
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_CREDENTIALS['email']}")
        print("=" * 60)
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with flow test")
            return
        
        # Step 1: Get current subscription
        current_subscription = self.step1_get_current_subscription()
        
        # Step 2: Upgrade to professional (PREVIOUSLY FAILING)
        upgrade_result = self.step2_upgrade_to_professional()
        
        # Step 3: Check usage analytics (PREVIOUSLY FAILING)
        usage_analytics = self.step3_check_usage_analytics()
        
        # Step 4: Generate license codes to test limits
        license_generation = self.step4_generate_license_codes()
        
        # Print summary
        self.print_flow_summary()

    def print_flow_summary(self):
        """Print flow test summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPLETE SUBSCRIPTION FLOW TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Flow Steps Completed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Show all results
        for result in self.test_results:
            print(f"{result['test']}: {'✅ PASS' if result['success'] else '❌ FAIL'}")
            if result['details']:
                print(f"    {result['details']}")
        
        print("\n" + "=" * 60)
        print("🔍 CRITICAL FINDINGS:")
        
        # Check specific endpoints that were previously failing
        upgrade_test = next((r for r in self.test_results if "Upgrade to Professional" in r["test"]), None)
        usage_test = next((r for r in self.test_results if "Usage Analytics" in r["test"]), None)
        
        if upgrade_test:
            if upgrade_test["success"]:
                print("✅ SUBSCRIPTION UPGRADE: FIXED - Previously returned 500 error, now working")
            else:
                print("❌ SUBSCRIPTION UPGRADE: STILL FAILING - Needs immediate attention")
        
        if usage_test:
            if usage_test["success"]:
                print("✅ USAGE ANALYTICS: FIXED - Previously returned 500 error, now working")
            else:
                print("❌ USAGE ANALYTICS: STILL FAILING - Needs immediate attention")
        
        print("\n" + "=" * 60)
        print("📊 COMPLETE FLOW ASSESSMENT:")
        
        if success_rate == 100:
            print("✅ EXCELLENT - Complete subscription flow working perfectly")
        elif success_rate >= 80:
            print("✅ GOOD - Most of the flow working, minor issues need attention")
        elif success_rate >= 60:
            print("⚠️ PARTIAL - Core functionality working but significant issues remain")
        else:
            print("❌ CRITICAL - Major issues prevent complete subscription flow")
        
        print("=" * 60)

if __name__ == "__main__":
    test = SubscriptionFlowTest()
    test.run_complete_flow()