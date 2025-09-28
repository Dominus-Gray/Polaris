#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"

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

class RoleDebugTester:
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
                self.log_result(f"{role.title()} Login", "PASS", f"Successfully logged in as {credentials['email']}")
                return token
            else:
                error_detail = response.json().get("detail", "Unknown error")
                self.log_result(f"{role.title()} Login", "FAIL", f"Login failed: {error_detail}")
                return None
                
        except Exception as e:
            self.log_result(f"{role.title()} Login", "FAIL", f"Login exception: {str(e)}")
            return None
    
    def test_debug_role_endpoint(self, role, token):
        """Test the /debug/role endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BACKEND_URL}/debug/role", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                detected_role = data.get("role")
                user_email = data.get("email")
                
                self.log_result(
                    f"{role.title()} Role Detection", 
                    "PASS", 
                    f"Role detected: '{detected_role}', Email: '{user_email}'"
                )
                
                # Check if role matches expected
                if detected_role == role:
                    self.log_result(
                        f"{role.title()} Role Validation", 
                        "PASS", 
                        f"Role correctly detected as '{detected_role}'"
                    )
                else:
                    self.log_result(
                        f"{role.title()} Role Validation", 
                        "FAIL", 
                        f"Expected '{role}' but got '{detected_role}'"
                    )
                
                return data
            else:
                self.log_result(
                    f"{role.title()} Role Detection", 
                    "FAIL", 
                    f"Debug endpoint failed: {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                f"{role.title()} Role Detection", 
                "FAIL", 
                f"Debug endpoint exception: {str(e)}"
            )
            return None
    
    def test_knowledge_base_access(self, role, token):
        """Test the /knowledge-base/access endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_all_access = data.get("has_all_access", False)
                unlocked_areas = data.get("unlocked_areas", [])
                
                self.log_result(
                    f"{role.title()} KB Access Check", 
                    "PASS", 
                    f"Has all access: {has_all_access}, Unlocked areas: {len(unlocked_areas)}"
                )
                
                # Check expected behavior based on role
                if role == "provider":
                    # Providers should NOT have automatic access
                    if has_all_access:
                        self.log_result(
                            f"{role.title()} KB Access Logic", 
                            "FAIL", 
                            f"🚨 CRITICAL: Provider has all access when they should be blocked!"
                        )
                    else:
                        self.log_result(
                            f"{role.title()} KB Access Logic", 
                            "PASS", 
                            f"Provider correctly blocked from automatic access"
                        )
                elif role == "client":
                    # Clients should have automatic access
                    if has_all_access:
                        self.log_result(
                            f"{role.title()} KB Access Logic", 
                            "PASS", 
                            f"Client correctly granted automatic access"
                        )
                    else:
                        self.log_result(
                            f"{role.title()} KB Access Logic", 
                            "FAIL", 
                            f"Client should have automatic access but doesn't"
                        )
                
                return data
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_result(
                    f"{role.title()} KB Access Check", 
                    "FAIL", 
                    f"KB access endpoint failed: {response.status_code} - {error_detail}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                f"{role.title()} KB Access Check", 
                "FAIL", 
                f"KB access exception: {str(e)}"
            )
            return None
    
    def test_role_comparison_logic(self, provider_data, client_data):
        """Test the role comparison logic specifically"""
        try:
            provider_role = provider_data.get("role") if provider_data else None
            client_role = client_data.get("role") if client_data else None
            
            # Test the exact condition from the code: current["role"] != "provider"
            if provider_role:
                provider_blocked = provider_role != "provider"
                self.log_result(
                    "Provider Role Comparison", 
                    "PASS" if not provider_blocked else "FAIL",
                    f"Provider role '{provider_role}' != 'provider' evaluates to {provider_blocked} (should be False)"
                )
            
            if client_role:
                client_allowed = client_role != "provider"
                self.log_result(
                    "Client Role Comparison", 
                    "PASS" if client_allowed else "FAIL",
                    f"Client role '{client_role}' != 'provider' evaluates to {client_allowed} (should be True)"
                )
                
        except Exception as e:
            self.log_result(
                "Role Comparison Logic", 
                "FAIL", 
                f"Role comparison exception: {str(e)}"
            )
    
    def run_comprehensive_test(self):
        """Run comprehensive role detection debugging"""
        print("🎯 ROLE DETECTION DEBUG TEST STARTING")
        print("=" * 60)
        
        # Test both roles
        role_data = {}
        
        for role, credentials in TEST_CREDENTIALS.items():
            print(f"\n🔍 Testing {role.upper()} Role Detection:")
            print("-" * 40)
            
            # Step 1: Login
            token = self.login_user(role, credentials)
            if not token:
                continue
                
            # Step 2: Test debug/role endpoint
            debug_data = self.test_debug_role_endpoint(role, token)
            role_data[role] = debug_data
            
            # Step 3: Test knowledge-base/access endpoint
            self.test_knowledge_base_access(role, token)
        
        # Step 4: Test role comparison logic
        print(f"\n🔍 Testing Role Comparison Logic:")
        print("-" * 40)
        self.test_role_comparison_logic(
            role_data.get("provider"), 
            role_data.get("client")
        )
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        critical_issues = [r for r in self.results if "CRITICAL" in r["details"]]
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"  - {issue['test']}: {issue['details']}")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        provider_role_data = role_data.get("provider")
        client_role_data = role_data.get("client")
        
        if provider_role_data and client_role_data:
            print(f"Provider JWT Role: '{provider_role_data.get('role')}'")
            print(f"Client JWT Role: '{client_role_data.get('role')}'")
            print(f"Code Logic: email.endswith('@polaris.example.com') and current['role'] != 'provider'")
            
            provider_email = provider_role_data.get("email", "")
            client_email = client_role_data.get("email", "")
            
            provider_domain_check = provider_email.endswith("@polaris.example.com")
            client_domain_check = client_email.endswith("@polaris.example.com")
            
            provider_role_check = provider_role_data.get("role") != "provider"
            client_role_check = client_role_data.get("role") != "provider"
            
            print(f"\nProvider Analysis:")
            print(f"  - Email domain check: {provider_domain_check}")
            print(f"  - Role != 'provider': {provider_role_check}")
            print(f"  - Should get access: {provider_domain_check and provider_role_check}")
            
            print(f"\nClient Analysis:")
            print(f"  - Email domain check: {client_domain_check}")
            print(f"  - Role != 'provider': {client_role_check}")
            print(f"  - Should get access: {client_domain_check and client_role_check}")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "critical_issues": len(critical_issues),
            "results": self.results
        }

if __name__ == "__main__":
    tester = RoleDebugTester()
    results = tester.run_comprehensive_test()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)