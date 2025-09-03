#!/usr/bin/env python3
"""
QA Login Verification Test
Verify QA logins for all roles against backend as requested in review.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://smartbiz-assess.preview.emergentagent.com/api"

# QA Credentials to test
QA_CREDENTIALS = [
    {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "expected_role": "client"
    },
    {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "expected_role": "provider"
    },
    {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "expected_role": "agency"
    },
    {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "expected_role": "navigator"
    }
]

class QALoginTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_login(self, email: str, password: str, expected_role: str) -> Dict[str, Any]:
        """Test login for a single QA credential"""
        result = {
            "email": email,
            "expected_role": expected_role,
            "login_success": False,
            "token_extracted": False,
            "me_endpoint_success": False,
            "role_matches": False,
            "approval_status_ok": False,
            "id_present": False,
            "email_present": False,
            "access_token": None,
            "actual_role": None,
            "approval_status": None,
            "errors": []
        }
        
        try:
            # Step 1: POST /api/auth/login
            login_payload = {
                "email": email,
                "password": password
            }
            
            print(f"Testing login for {email}...")
            login_response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_payload,
                timeout=10
            )
            
            print(f"Login response status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                result["login_success"] = True
                login_data = login_response.json()
                
                # Step 2: Extract access_token
                if "access_token" in login_data:
                    result["token_extracted"] = True
                    result["access_token"] = login_data["access_token"]
                    
                    # Step 3: GET /api/auth/me with Authorization header
                    headers = {
                        "Authorization": f"Bearer {login_data['access_token']}"
                    }
                    
                    me_response = self.session.get(
                        f"{BACKEND_URL}/auth/me",
                        headers=headers,
                        timeout=10
                    )
                    
                    print(f"Me endpoint response status: {me_response.status_code}")
                    
                    if me_response.status_code == 200:
                        result["me_endpoint_success"] = True
                        me_data = me_response.json()
                        
                        # Step 4: Verify role matches
                        actual_role = me_data.get("role")
                        result["actual_role"] = actual_role
                        if actual_role == expected_role:
                            result["role_matches"] = True
                        else:
                            result["errors"].append(f"Role mismatch: expected {expected_role}, got {actual_role}")
                        
                        # Step 5: Check approval_status is not blocking
                        approval_status = me_data.get("approval_status", "approved")
                        result["approval_status"] = approval_status
                        if approval_status in ["approved", "pending"]:
                            result["approval_status_ok"] = True
                        else:
                            result["errors"].append(f"Blocking approval status: {approval_status}")
                        
                        # Step 6: Verify id and email are present
                        if me_data.get("id"):
                            result["id_present"] = True
                        else:
                            result["errors"].append("ID field missing from /auth/me response")
                            
                        if me_data.get("email"):
                            result["email_present"] = True
                        else:
                            result["errors"].append("Email field missing from /auth/me response")
                            
                        print(f"User data: role={actual_role}, approval_status={approval_status}, id={bool(me_data.get('id'))}, email={bool(me_data.get('email'))}")
                        
                    else:
                        result["errors"].append(f"/auth/me failed with status {me_response.status_code}: {me_response.text}")
                        
                else:
                    result["errors"].append("No access_token in login response")
                    
            else:
                result["errors"].append(f"Login failed with status {login_response.status_code}: {login_response.text}")
                
        except requests.exceptions.RequestException as e:
            result["errors"].append(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON decode error: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {str(e)}")
            
        return result
    
    def run_all_tests(self):
        """Run tests for all QA credentials"""
        print("=" * 60)
        print("QA LOGIN VERIFICATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        for cred in QA_CREDENTIALS:
            result = self.test_login(
                cred["email"], 
                cred["password"], 
                cred["expected_role"]
            )
            self.results.append(result)
            print()
        
        self.print_summary()
    
    def print_summary(self):
        """Print concise summary as requested"""
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_logins = sum(1 for r in self.results if r["login_success"])
        working_tokens = sum(1 for r in self.results if r["me_endpoint_success"])
        correct_roles = sum(1 for r in self.results if r["role_matches"])
        valid_approvals = sum(1 for r in self.results if r["approval_status_ok"])
        complete_data = sum(1 for r in self.results if r["id_present"] and r["email_present"])
        
        print(f"Total QA accounts tested: {total_tests}")
        print(f"Successful logins: {successful_logins}/{total_tests}")
        print(f"Working tokens: {working_tokens}/{total_tests}")
        print(f"Correct roles: {correct_roles}/{total_tests}")
        print(f"Valid approval status: {valid_approvals}/{total_tests}")
        print(f"Complete user data: {complete_data}/{total_tests}")
        print()
        
        # Individual results
        for result in self.results:
            status = "✅ PASS" if (
                result["login_success"] and 
                result["token_extracted"] and 
                result["me_endpoint_success"] and 
                result["role_matches"] and 
                result["approval_status_ok"] and 
                result["id_present"] and 
                result["email_present"]
            ) else "❌ FAIL"
            
            print(f"{status} {result['email']} ({result['expected_role']})")
            if result["errors"]:
                for error in result["errors"]:
                    print(f"    - {error}")
        
        print()
        
        # Overall status
        all_passed = all(
            r["login_success"] and r["token_extracted"] and r["me_endpoint_success"] and 
            r["role_matches"] and r["approval_status_ok"] and r["id_present"] and r["email_present"]
            for r in self.results
        )
        
        if all_passed:
            print("🎉 ALL QA CREDENTIALS WORKING CORRECTLY")
            print("✅ All logins successful (200 status)")
            print("✅ All tokens extracted and working")
            print("✅ All roles match expected values")
            print("✅ All approval statuses are non-blocking")
            print("✅ All user data complete (id/email present)")
        else:
            print("⚠️  SOME QA CREDENTIALS HAVE ISSUES")
            print("❌ Not all tests passed - see individual results above")
        
        return all_passed

def main():
    """Main test execution"""
    tester = QALoginTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()