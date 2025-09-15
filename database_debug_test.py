#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "https://production-guru.preview.emergentagent.com/api"

# Test credentials
TEST_CREDENTIALS = {
    "provider": {
        "email": "provider.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "client": {
        "email": "client.qa@polaris.example.com", 
        "password": "Polaris#2025!"
    }
}

class DatabaseDebugTester:
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
        
    def login_user(self, role, credentials):
        """Login user and return token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                return token
            else:
                return None
                
        except Exception as e:
            return None
    
    def test_knowledge_base_access_detailed(self, role, token):
        """Test knowledge base access with detailed analysis"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # First call - this might create the access record
            print(f"\n🔍 First call to /knowledge-base/access for {role}:")
            response1 = self.session.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
            
            if response1.status_code == 200:
                data1 = response1.json()
                has_all_access1 = data1.get("has_all_access", False)
                unlocked_areas1 = data1.get("unlocked_areas", [])
                
                print(f"  - First call result: has_all_access={has_all_access1}, areas={len(unlocked_areas1)}")
                
                # Second call - this should use existing record
                print(f"🔍 Second call to /knowledge-base/access for {role}:")
                response2 = self.session.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    has_all_access2 = data2.get("has_all_access", False)
                    unlocked_areas2 = data2.get("unlocked_areas", [])
                    
                    print(f"  - Second call result: has_all_access={has_all_access2}, areas={len(unlocked_areas2)}")
                    
                    # Check consistency
                    if has_all_access1 == has_all_access2:
                        self.log_result(
                            f"{role.title()} KB Access Consistency", 
                            "PASS", 
                            f"Consistent results across calls"
                        )
                    else:
                        self.log_result(
                            f"{role.title()} KB Access Consistency", 
                            "FAIL", 
                            f"Inconsistent results: {has_all_access1} vs {has_all_access2}"
                        )
                    
                    # Analyze the logic for provider
                    if role == "provider":
                        if has_all_access1:
                            self.log_result(
                                f"{role.title()} Access Logic Analysis", 
                                "FAIL", 
                                f"🚨 Provider got access - this suggests either: 1) Pre-existing DB record, 2) Logic bug, 3) Role detection issue"
                            )
                        else:
                            self.log_result(
                                f"{role.title()} Access Logic Analysis", 
                                "PASS", 
                                f"Provider correctly blocked"
                            )
                    
                    return data1
                else:
                    print(f"  - Second call failed: {response2.status_code}")
                    return data1
            else:
                print(f"  - First call failed: {response1.status_code}")
                return None
                
        except Exception as e:
            self.log_result(
                f"{role.title()} KB Access Detailed", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return None
    
    def test_role_detection_in_context(self, role, token):
        """Test role detection in the context of KB access"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get debug info
            debug_response = self.session.get(f"{BACKEND_URL}/debug/role", headers=headers)
            if debug_response.status_code != 200:
                return None
                
            debug_data = debug_response.json()
            detected_role = debug_data.get("role")
            email = debug_data.get("email")
            
            print(f"\n🔍 Role Detection Context for {role}:")
            print(f"  - Email: {email}")
            print(f"  - Detected Role: {detected_role}")
            print(f"  - Email ends with @polaris.example.com: {email.endswith('@polaris.example.com')}")
            print(f"  - Role != 'provider': {detected_role != 'provider'}")
            print(f"  - Should get access: {email.endswith('@polaris.example.com') and detected_role != 'provider'}")
            
            # Test the exact logic
            should_get_access = email.endswith("@polaris.example.com") and detected_role != "provider"
            
            if role == "provider":
                if should_get_access:
                    self.log_result(
                        f"{role.title()} Logic Evaluation", 
                        "FAIL", 
                        f"Logic says provider should get access (BUG!)"
                    )
                else:
                    self.log_result(
                        f"{role.title()} Logic Evaluation", 
                        "PASS", 
                        f"Logic correctly blocks provider"
                    )
            elif role == "client":
                if should_get_access:
                    self.log_result(
                        f"{role.title()} Logic Evaluation", 
                        "PASS", 
                        f"Logic correctly allows client"
                    )
                else:
                    self.log_result(
                        f"{role.title()} Logic Evaluation", 
                        "FAIL", 
                        f"Logic incorrectly blocks client"
                    )
            
            return debug_data
            
        except Exception as e:
            self.log_result(
                f"{role.title()} Role Context", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return None
    
    def run_database_debug_test(self):
        """Run comprehensive database debugging"""
        print("🎯 DATABASE DEBUG TEST STARTING")
        print("=" * 60)
        
        for role, credentials in TEST_CREDENTIALS.items():
            print(f"\n🔍 Testing {role.upper()} Database State:")
            print("-" * 50)
            
            # Step 1: Login
            token = self.login_user(role, credentials)
            if not token:
                print(f"❌ Failed to login as {role}")
                continue
            
            # Step 2: Test role detection in context
            self.test_role_detection_in_context(role, token)
            
            # Step 3: Test knowledge base access with detailed analysis
            self.test_knowledge_base_access_detailed(role, token)
        
        # Summary
        print(f"\n📊 DATABASE DEBUG SUMMARY:")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
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
            "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            "critical_issues": len(critical_issues),
            "results": self.results
        }

if __name__ == "__main__":
    tester = DatabaseDebugTester()
    results = tester.run_database_debug_test()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)