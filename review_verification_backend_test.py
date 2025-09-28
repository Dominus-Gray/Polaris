#!/usr/bin/env python3
"""
Polaris Backend API Testing - Review Request Verification
Quick verification test to ensure core API functionality is working before proceeding with frontend work.

Testing Objectives:
1. Verify backend services - Check if the API is responding properly
2. Test authentication flow - Login with QA credentials to ensure auth works  
3. Test assessment endpoints - Verify tier-based assessment system
4. Test knowledge base AI assistance - Check if AI endpoints are working
5. Test payment packages - Verify Stripe integration setup

QA Credentials:
- client.qa@polaris.example.com / Polaris#2025!
- provider.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"
TIMEOUT = 30

# QA Test Credentials as specified in the review request
QA_CREDENTIALS = {
    "client": {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client"
    },
    "provider": {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "role": "provider"
    }
}

class ReviewVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.tokens = {}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results with detailed information"""
        result = {
            "test_name": test_name,
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

    def test_backend_health_check(self):
        """Test 1: Verify backend services - Check if API is responding properly"""
        print("🔍 Testing Backend Health Check...")
        
        try:
            # Test GET /api/auth/me without authentication (should return 401)
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_test(
                    "Backend Health Check", 
                    True, 
                    f"API responding correctly with 401 status for unauthenticated request"
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check", 
                    False, 
                    f"Expected 401 status, got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Backend Health Check", 
                False, 
                f"Connection error: {str(e)}"
            )
            return False

    def test_authentication_flow(self):
        """Test 2: Test authentication flow - Login with QA credentials"""
        print("🔍 Testing Authentication Flow...")
        
        success_count = 0
        total_tests = len(QA_CREDENTIALS)
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                # Test login
                login_data = {
                    "email": creds["email"],
                    "password": creds["password"]
                }
                
                response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    if "access_token" in token_data:
                        self.tokens[role] = token_data["access_token"]
                        
                        # Test token validation with /auth/me
                        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                        me_response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
                        
                        if me_response.status_code == 200:
                            user_data = me_response.json()
                            self.log_test(
                                f"Authentication - {role.title()}", 
                                True, 
                                f"Login successful, token valid, user: {user_data.get('email', 'unknown')}"
                            )
                            success_count += 1
                        else:
                            self.log_test(
                                f"Authentication - {role.title()}", 
                                False, 
                                f"Token validation failed: {me_response.status_code}",
                                me_response.text
                            )
                    else:
                        self.log_test(
                            f"Authentication - {role.title()}", 
                            False, 
                            "No access_token in response",
                            token_data
                        )
                else:
                    self.log_test(
                        f"Authentication - {role.title()}", 
                        False, 
                        f"Login failed: {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Authentication - {role.title()}", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        return success_count == total_tests

    def test_assessment_endpoints(self):
        """Test 3: Test assessment endpoints - Verify tier-based assessment system"""
        print("🔍 Testing Assessment Endpoints...")
        
        if "client" not in self.tokens:
            self.log_test(
                "Assessment Endpoints", 
                False, 
                "No client token available for testing"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            
            # Test GET /api/assessment/schema/tier-based
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                schema_data = response.json()
                
                # Verify it contains expected structure
                if "areas" in schema_data and len(schema_data["areas"]) >= 10:
                    # Check for area10 "Competitive Advantage"
                    area10_found = False
                    for area in schema_data["areas"]:
                        if area.get("id") == "area10" and "Competitive Advantage" in area.get("name", ""):
                            area10_found = True
                            break
                    
                    if area10_found:
                        self.log_test(
                            "Assessment Schema", 
                            True, 
                            f"Tier-based schema loaded with {len(schema_data['areas'])} areas including area10 'Competitive Advantage'"
                        )
                        return True
                    else:
                        self.log_test(
                            "Assessment Schema", 
                            False, 
                            "area10 'Competitive Advantage' not found in schema"
                        )
                        return False
                else:
                    self.log_test(
                        "Assessment Schema", 
                        False, 
                        f"Invalid schema structure or insufficient areas: {len(schema_data.get('areas', []))}"
                    )
                    return False
            else:
                self.log_test(
                    "Assessment Schema", 
                    False, 
                    f"Failed to load schema: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Assessment Schema", 
                False, 
                f"Exception: {str(e)}"
            )
            return False

    def test_knowledge_base_ai_assistance(self):
        """Test 4: Test knowledge base AI assistance - Check if AI endpoints are working"""
        print("🔍 Testing Knowledge Base AI Assistance...")
        
        if "client" not in self.tokens:
            self.log_test(
                "Knowledge Base AI", 
                False, 
                "No client token available for testing"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            
            # Test POST /api/knowledge-base/ai-assistance
            ai_request = {
                "question": "How do I get started with business licensing?",
                "area_id": "area1"
            }
            
            response = self.session.post(f"{BASE_URL}/knowledge-base/ai-assistance", json=ai_request, headers=headers)
            
            if response.status_code == 200:
                ai_data = response.json()
                
                if "response" in ai_data and len(ai_data["response"]) > 50:
                    self.log_test(
                        "Knowledge Base AI Assistance", 
                        True, 
                        f"AI assistance working, response length: {len(ai_data['response'])} characters"
                    )
                    return True
                else:
                    self.log_test(
                        "Knowledge Base AI Assistance", 
                        False, 
                        "AI response too short or missing",
                        ai_data
                    )
                    return False
            else:
                self.log_test(
                    "Knowledge Base AI Assistance", 
                    False, 
                    f"AI assistance failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Knowledge Base AI Assistance", 
                False, 
                f"Exception: {str(e)}"
            )
            return False

    def test_payment_packages(self):
        """Test 5: Test payment packages - Verify Stripe integration setup"""
        print("🔍 Testing Payment Packages...")
        
        if "client" not in self.tokens:
            self.log_test(
                "Payment Packages", 
                False, 
                "No client token available for testing"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            
            # Test GET /api/payments/packages
            response = self.session.get(f"{BASE_URL}/payments/packages", headers=headers)
            
            if response.status_code == 200:
                packages_data = response.json()
                
                if isinstance(packages_data, list) and len(packages_data) > 0:
                    self.log_test(
                        "Payment Packages", 
                        True, 
                        f"Payment packages loaded: {len(packages_data)} packages available"
                    )
                    return True
                elif isinstance(packages_data, dict) and "packages" in packages_data:
                    self.log_test(
                        "Payment Packages", 
                        True, 
                        f"Payment packages loaded: {len(packages_data['packages'])} packages available"
                    )
                    return True
                else:
                    self.log_test(
                        "Payment Packages", 
                        False, 
                        "No packages found or invalid structure",
                        packages_data
                    )
                    return False
            else:
                self.log_test(
                    "Payment Packages", 
                    False, 
                    f"Failed to load packages: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Payment Packages", 
                False, 
                f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all verification tests"""
        print("🎯 POLARIS BACKEND API VERIFICATION - REVIEW REQUEST TESTING")
        print("=" * 70)
        print(f"Testing against: {BASE_URL}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        test_results = []
        
        test_results.append(self.test_backend_health_check())
        test_results.append(self.test_authentication_flow())
        test_results.append(self.test_assessment_endpoints())
        test_results.append(self.test_knowledge_base_ai_assistance())
        test_results.append(self.test_payment_packages())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 70)
        print("🎯 VERIFICATION TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("✅ VERIFICATION SUCCESSFUL - Core API functionality is working")
            print("✅ Ready to proceed with frontend work")
        else:
            print("❌ VERIFICATION FAILED - Critical issues found")
            print("❌ Backend issues must be resolved before frontend work")
        
        print()
        print("🔍 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"{i}. {status} {result['test_name']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ReviewVerificationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)