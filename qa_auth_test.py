#!/usr/bin/env python3
"""
QA Authentication Test
Testing Agent: testing
Test Date: January 2025
Test Scope: Quick authentication test for QA user accounts as requested in review

Testing the following QA credentials:
1. client.qa@polaris.example.com / Polaris#2025!
2. provider.qa@polaris.example.com / Polaris#2025!  
3. navigator.qa@polaris.example.com / Polaris#2025!
4. agency.qa@polaris.example.com / Polaris#2025!

For each account:
- Test POST /api/auth/login with the credentials
- Verify the response includes a valid token
- Test GET /api/auth/me with the token to confirm authentication works
- Check if any accounts need to be created or have authentication issues
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"

# QA Test Credentials from review request
QA_CREDENTIALS = {
    "client": {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "provider": {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!"
    },
    "navigator": {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "agency": {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!"
    }
}

class QAAuthTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.tokens = {}
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "QA-Auth-Tester/1.0"
            }
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str, data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if data and isinstance(data, dict):
            if "token" in str(data):
                # Mask token for security
                masked_data = {k: v if k != "access_token" else f"{v[:10]}..." if v else None for k, v in data.items()}
                print(f"   Data: {json.dumps(masked_data, indent=2)}")
            else:
                print(f"   Data: {json.dumps(data, indent=2)}")
        print()
        
    async def test_login(self, role: str, credentials: Dict[str, str]) -> bool:
        """Test login for a specific role"""
        try:
            login_url = f"{BACKEND_URL}/auth/login"
            
            async with self.session.post(login_url, json=credentials) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if "access_token" in data and data["access_token"]:
                            # Store token for further testing
                            self.tokens[role] = data["access_token"]
                            self.log_result(
                                f"{role.title()} Login",
                                True,
                                f"Successfully logged in as {credentials['email']}. Token received ({len(data['access_token'])} chars)",
                                {"token_type": data.get("token_type", "bearer"), "token_length": len(data["access_token"])}
                            )
                            return True
                        else:
                            self.log_result(
                                f"{role.title()} Login",
                                False,
                                f"Login response missing access_token field",
                                data
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_result(
                            f"{role.title()} Login",
                            False,
                            f"Invalid JSON response: {response_text[:200]}",
                            {"status": response.status}
                        )
                        return False
                else:
                    try:
                        error_data = json.loads(response_text)
                        self.log_result(
                            f"{role.title()} Login",
                            False,
                            f"Login failed with status {response.status}: {error_data.get('detail', response_text[:200])}",
                            {"status": response.status, "error": error_data}
                        )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"{role.title()} Login",
                            False,
                            f"Login failed with status {response.status}: {response_text[:200]}",
                            {"status": response.status}
                        )
                    return False
                    
        except Exception as e:
            self.log_result(
                f"{role.title()} Login",
                False,
                f"Exception during login: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def test_auth_me(self, role: str) -> bool:
        """Test /api/auth/me endpoint with stored token"""
        if role not in self.tokens:
            self.log_result(
                f"{role.title()} Auth Me",
                False,
                f"No token available for {role} - login must have failed",
                None
            )
            return False
            
        try:
            auth_me_url = f"{BACKEND_URL}/auth/me"
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            
            async with self.session.get(auth_me_url, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        expected_email = QA_CREDENTIALS[role]["email"]
                        
                        if data.get("email") == expected_email and data.get("role") == role:
                            self.log_result(
                                f"{role.title()} Auth Me",
                                True,
                                f"Successfully authenticated as {expected_email} with role {role}",
                                {"email": data.get("email"), "role": data.get("role"), "id": data.get("id", "N/A")}
                            )
                            return True
                        else:
                            self.log_result(
                                f"{role.title()} Auth Me",
                                False,
                                f"User data mismatch - expected {expected_email}/{role}, got {data.get('email')}/{data.get('role')}",
                                data
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_result(
                            f"{role.title()} Auth Me",
                            False,
                            f"Invalid JSON response: {response_text[:200]}",
                            {"status": response.status}
                        )
                        return False
                else:
                    try:
                        error_data = json.loads(response_text)
                        self.log_result(
                            f"{role.title()} Auth Me",
                            False,
                            f"Auth me failed with status {response.status}: {error_data.get('detail', response_text[:200])}",
                            {"status": response.status, "error": error_data}
                        )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"{role.title()} Auth Me",
                            False,
                            f"Auth me failed with status {response.status}: {response_text[:200]}",
                            {"status": response.status}
                        )
                    return False
                    
        except Exception as e:
            self.log_result(
                f"{role.title()} Auth Me",
                False,
                f"Exception during auth me: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def run_comprehensive_auth_test(self):
        """Run comprehensive authentication test for all QA credentials"""
        print("🎯 QA AUTHENTICATION COMPREHENSIVE TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        await self.setup_session()
        
        try:
            total_tests = 0
            passed_tests = 0
            
            # Test each role
            for role, credentials in QA_CREDENTIALS.items():
                print(f"🔐 Testing {role.upper()} Authentication")
                print("-" * 40)
                
                # Test login
                login_success = await self.test_login(role, credentials)
                total_tests += 1
                if login_success:
                    passed_tests += 1
                
                # Test auth/me if login succeeded
                if login_success:
                    auth_me_success = await self.test_auth_me(role)
                    total_tests += 1
                    if auth_me_success:
                        passed_tests += 1
                else:
                    # Still count auth/me as a test, but it will fail
                    await self.test_auth_me(role)
                    total_tests += 1
                
                print()
            
            # Summary
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            print("📊 QA AUTHENTICATION TEST SUMMARY")
            print("=" * 60)
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {success_rate:.1f}%")
            print()
            
            # Detailed results
            print("📋 DETAILED RESULTS:")
            print("-" * 30)
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}: {result['details']}")
            
            print()
            
            # Identify issues
            failed_tests = [r for r in self.test_results if not r["success"]]
            if failed_tests:
                print("🚨 ISSUES IDENTIFIED:")
                print("-" * 30)
                for failed in failed_tests:
                    print(f"❌ {failed['test']}: {failed['details']}")
                print()
                
                # Provide specific solutions
                print("💡 SPECIFIC SOLUTIONS:")
                print("-" * 30)
                
                login_failures = [f for f in failed_tests if "Login" in f["test"]]
                auth_failures = [f for f in failed_tests if "Auth Me" in f["test"]]
                
                if login_failures:
                    print("🔑 LOGIN ISSUES:")
                    for failure in login_failures:
                        role = failure["test"].split()[0].lower()
                        if "not found" in failure["details"].lower() or "user not found" in failure["details"].lower():
                            print(f"   - {role.title()} account needs to be created")
                        elif "invalid" in failure["details"].lower() or "credentials" in failure["details"].lower():
                            print(f"   - {role.title()} password may need to be reset")
                        elif "status 500" in failure["details"]:
                            print(f"   - {role.title()} login has server error - check backend logs")
                        else:
                            print(f"   - {role.title()} has authentication issue: {failure['details']}")
                
                if auth_failures:
                    print("🔐 TOKEN VALIDATION ISSUES:")
                    for failure in auth_failures:
                        role = failure["test"].split()[0].lower()
                        if "no token" in failure["details"].lower():
                            print(f"   - {role.title()} login failed, so no token to test")
                        elif "401" in failure["details"]:
                            print(f"   - {role.title()} token is invalid or expired")
                        else:
                            print(f"   - {role.title()} has token validation issue: {failure['details']}")
            else:
                print("✅ ALL QA CREDENTIALS WORKING CORRECTLY")
                print("   - All 4 roles can successfully authenticate")
                print("   - All tokens are valid and working")
                print("   - Authentication system is fully operational")
            
            return success_rate >= 100.0
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = QAAuthTester()
    
    try:
        success = await tester.run_comprehensive_auth_test()
        
        if success:
            print("\n🎉 QA AUTHENTICATION TEST: COMPLETE SUCCESS")
            sys.exit(0)
        else:
            print("\n⚠️  QA AUTHENTICATION TEST: ISSUES FOUND")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 QA AUTHENTICATION TEST: CRITICAL ERROR")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())