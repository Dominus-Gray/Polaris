#!/usr/bin/env python3
"""
Quick Subscription Endpoints Test
Testing the two previously failing subscription endpoints to confirm they're fixed
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "agency.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class SubscriptionEndpointsTest:
    def __init__(self):
        self.results = []
        self.token = None
        
    def log_result(self, test_name, success, details="", response_time=0):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s"
        })
        print(f"{status}: {test_name} ({response_time:.3f}s)")
        if details:
            print(f"    Details: {details}")
    
    def authenticate_agency(self):
        """Authenticate agency user and store token"""
        try:
            start_time = time.time()
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=QA_CREDENTIALS)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.log_result("Agency Authentication", True, f"Token obtained successfully", response_time)
                return True
            else:
                error_detail = response.text
                self.log_result("Agency Authentication", False, f"Status {response.status_code}: {error_detail}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Agency Authentication", False, f"Exception: {str(e)}", 0)
            return False
    
    def test_subscription_upgrade(self):
        """Test POST /api/agency/subscription/upgrade"""
        try:
            start_time = time.time()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "tier_id": "professional",
                "billing_cycle": "monthly"
            }
            
            response = requests.post(f"{BACKEND_URL}/agency/subscription/upgrade", 
                                   json=payload, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Subscription Upgrade", True, 
                              f"Upgrade successful: {json.dumps(data, indent=2)}", response_time)
                return True
            else:
                error_detail = response.text
                self.log_result("Subscription Upgrade", False, 
                              f"Status {response.status_code}: {error_detail}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Subscription Upgrade", False, f"Exception: {str(e)}", 0)
            return False
    
    def test_usage_analytics(self):
        """Test GET /api/agency/subscription/usage"""
        try:
            start_time = time.time()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(f"{BACKEND_URL}/agency/subscription/usage", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Usage Analytics", True, 
                              f"Usage data retrieved: {json.dumps(data, indent=2)}", response_time)
                return True
            else:
                error_detail = response.text
                self.log_result("Usage Analytics", False, 
                              f"Status {response.status_code}: {error_detail}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Usage Analytics", False, f"Exception: {str(e)}", 0)
            return False
    
    def run_tests(self):
        """Run all subscription endpoint tests"""
        print("🎯 SUBSCRIPTION ENDPOINTS QUICK TEST")
        print("=" * 50)
        print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"QA Credentials: {QA_CREDENTIALS['email']}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_agency():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return
        
        print()
        
        # Step 2: Test Subscription Upgrade
        print("Testing Subscription Upgrade Endpoint...")
        upgrade_success = self.test_subscription_upgrade()
        
        print()
        
        # Step 3: Test Usage Analytics
        print("Testing Usage Analytics Endpoint...")
        usage_success = self.test_usage_analytics()
        
        print()
        
        # Summary
        print("=" * 50)
        print("🎯 SUBSCRIPTION ENDPOINTS TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len([r for r in self.results if r["test"] != "Agency Authentication"])
        passed_tests = len([r for r in self.results if r["success"] and r["test"] != "Agency Authentication"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Detailed results
        for result in self.results:
            print(f"{result['status']}: {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"    {result['details']}")
        
        print()
        
        # Final assessment
        if upgrade_success and usage_success:
            print("🎉 SUCCESS: Both subscription endpoints are now working!")
        elif upgrade_success or usage_success:
            print("⚠️  PARTIAL: One endpoint working, one still failing")
        else:
            print("❌ FAILURE: Both subscription endpoints still failing")
        
        return upgrade_success and usage_success

if __name__ == "__main__":
    test = SubscriptionEndpointsTest()
    test.run_tests()