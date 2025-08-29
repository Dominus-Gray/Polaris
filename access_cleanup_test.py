#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "https://providermatrix.preview.emergentagent.com/api"

# Test credentials
PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class AccessCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
    def login_provider(self):
        """Login provider and return token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=PROVIDER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                self.log_result("Provider Login", "PASS", "Successfully logged in")
                return token
            else:
                self.log_result("Provider Login", "FAIL", f"Login failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Provider Login", "FAIL", f"Login exception: {str(e)}")
            return None
    
    def test_current_access_state(self, token):
        """Test current access state"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_all_access = data.get("has_all_access", False)
                unlocked_areas = data.get("unlocked_areas", [])
                
                self.log_result(
                    "Current Access State", 
                    "INFO", 
                    f"Provider has_all_access={has_all_access}, unlocked_areas={len(unlocked_areas)}"
                )
                
                return has_all_access
            else:
                self.log_result("Current Access State", "FAIL", f"Failed to get access: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Current Access State", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_fresh_provider_account(self):
        """Test with a fresh provider account to see if the logic works correctly"""
        try:
            # Create a new provider account
            fresh_email = f"fresh.provider.{datetime.now().strftime('%Y%m%d%H%M%S')}@polaris.example.com"
            fresh_password = "Polaris#2025!"
            
            # Register new provider
            register_data = {
                "email": fresh_email,
                "password": fresh_password,
                "role": "provider",
                "terms_accepted": True
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if register_response.status_code == 200:
                self.log_result("Fresh Provider Registration", "PASS", f"Created fresh provider: {fresh_email}")
                
                # Try to login (might fail if provider needs approval)
                login_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": fresh_email,
                    "password": fresh_password
                })
                
                if login_response.status_code == 200:
                    token = login_response.json().get("access_token")
                    self.log_result("Fresh Provider Login", "PASS", "Fresh provider login successful")
                    
                    # Test access
                    headers = {"Authorization": f"Bearer {token}"}
                    access_response = self.session.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
                    
                    if access_response.status_code == 200:
                        access_data = access_response.json()
                        has_all_access = access_data.get("has_all_access", False)
                        
                        if has_all_access:
                            self.log_result(
                                "Fresh Provider Access Test", 
                                "FAIL", 
                                "🚨 CRITICAL: Fresh provider also gets access - this is a logic bug!"
                            )
                        else:
                            self.log_result(
                                "Fresh Provider Access Test", 
                                "PASS", 
                                "Fresh provider correctly blocked - confirms pre-existing DB record issue"
                            )
                    else:
                        self.log_result("Fresh Provider Access Test", "FAIL", f"Access check failed: {access_response.status_code}")
                        
                else:
                    # Provider might need approval
                    error_detail = login_response.json().get("detail", {})
                    if "pending approval" in str(error_detail).lower():
                        self.log_result("Fresh Provider Login", "INFO", "Fresh provider needs approval (expected)")
                    else:
                        self.log_result("Fresh Provider Login", "FAIL", f"Fresh provider login failed: {error_detail}")
                        
            else:
                error_detail = register_response.json().get("detail", "Unknown error")
                self.log_result("Fresh Provider Registration", "FAIL", f"Registration failed: {error_detail}")
                
        except Exception as e:
            self.log_result("Fresh Provider Test", "FAIL", f"Exception: {str(e)}")
    
    def analyze_root_cause(self, current_access):
        """Analyze the root cause of the issue"""
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("=" * 50)
        
        if current_access:
            print("🚨 CONFIRMED ISSUE: Provider has access when they shouldn't")
            print("\nPOSSIBLE CAUSES:")
            print("1. 📊 PRE-EXISTING DATABASE RECORD:")
            print("   - Provider was granted access before role restrictions were implemented")
            print("   - Access record exists in user_access collection with all_areas: true")
            print("   - Logic only runs when no existing record is found")
            
            print("\n2. 🐛 LOGIC BUG:")
            print("   - Code logic has a bug despite appearing correct")
            print("   - Condition evaluation might have edge cases")
            
            print("\n3. 🔄 RACE CONDITION:")
            print("   - Multiple calls creating conflicting access records")
            
            print("\n4. 🎯 OTHER ACCESS GRANTS:")
            print("   - QA endpoint (/qa/grant/knowledge-base) was called")
            print("   - Payment system granted access")
            print("   - Manual database modification")
            
            print("\n🎯 MOST LIKELY CAUSE:")
            print("Pre-existing database record - the provider.qa@polaris.example.com account")
            print("was granted access before the role restriction logic was implemented.")
            
            print("\n💡 RECOMMENDED FIXES:")
            print("1. Clear existing access records for providers with @polaris.example.com emails")
            print("2. Add logic to revoke access for providers even if they have existing records")
            print("3. Add database migration to clean up incorrect access grants")
            
        else:
            print("✅ Provider correctly blocked - no issue found")
    
    def run_access_cleanup_test(self):
        """Run comprehensive access cleanup test"""
        print("🎯 ACCESS CLEANUP DEBUG TEST STARTING")
        print("=" * 60)
        
        # Step 1: Login existing provider
        token = self.login_provider()
        if not token:
            return {"error": "Could not login provider"}
        
        # Step 2: Test current access state
        current_access = self.test_current_access_state(token)
        
        # Step 3: Test with fresh provider account (if possible)
        print(f"\n🔍 Testing Fresh Provider Account:")
        print("-" * 40)
        self.test_fresh_provider_account()
        
        # Step 4: Root cause analysis
        self.analyze_root_cause(current_access)
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        info_tests = len([r for r in self.results if r["status"] == "INFO"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Info: {info_tests}")
        print(f"Success Rate: {(passed_tests/(total_tests-info_tests))*100:.1f}%" if (total_tests-info_tests) > 0 else "No tests to evaluate")
        
        # Critical findings
        critical_issues = [r for r in self.results if "🚨" in r["details"]]
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"  - {issue['test']}: {issue['details']}")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "info": info_tests,
            "critical_issues": len(critical_issues),
            "results": self.results
        }

if __name__ == "__main__":
    tester = AccessCleanupTester()
    results = tester.run_access_cleanup_test()
    
    # Exit with error code if critical issues found
    if results.get("critical_issues", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)