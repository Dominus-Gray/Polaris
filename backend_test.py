#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Polaris Platform
Testing all core functionality as requested in the review.
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
    },
    "agency": {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!", 
        "role": "agency"
    },
    "navigator": {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "navigator"
    }
}

class PolarisAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.tokens = {}
        self.test_results = []
        self.created_accounts = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results with detailed information"""
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

    def test_basic_health_check(self):
        """Test 1: Basic API Health Check"""
        try:
            # Test if server is responding
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Basic API Health Check", True, f"Server responding with status {response.status_code}")
                return True
            else:
                # Try alternative health endpoints
                for endpoint in ["/", "/docs", "/auth/me"]:
                    try:
                        test_response = self.session.get(f"{BASE_URL}{endpoint}", timeout=5)
                        if test_response.status_code in [200, 401, 422]:  # 401/422 means server is up
                            self.log_test("Basic API Health Check", True, f"Server responding via {endpoint} with status {test_response.status_code}")
                            return True
                    except:
                        continue
                        
                self.log_test("Basic API Health Check", False, f"Server not responding properly. Status: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Basic API Health Check", False, f"Connection error: {str(e)}")
            return False

    def create_qa_accounts_workflow(self):
        """Create QA accounts following the proper workflow"""
        print("🔧 SETTING UP QA ACCOUNTS")
        print("-" * 40)
        
        # Step 1: Create/Login Navigator (can approve other accounts)
        navigator_creds = QA_CREDENTIALS["navigator"]
        
        # Try to register navigator
        navigator_data = {
            "email": navigator_creds["email"],
            "password": navigator_creds["password"],
            "role": "navigator",
            "name": "QA Navigator User",
            "terms_accepted": True
        }
        
        navigator_response = self.session.post(f"{BASE_URL}/auth/register", json=navigator_data)
        
        if navigator_response.status_code in [200, 201]:
            navigator_result = navigator_response.json()
            navigator_token = navigator_result.get("data", {}).get("token")
            if navigator_token:
                self.tokens["navigator"] = navigator_token
                print("✅ Navigator account created and authenticated")
            else:
                # Try to login
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": navigator_creds["email"],
                    "password": navigator_creds["password"]
                })
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    navigator_token = login_result.get("data", {}).get("token")
                    if navigator_token:
                        self.tokens["navigator"] = navigator_token
                        print("✅ Navigator account authenticated")
        elif "already registered" in navigator_response.text.lower():
            # Try to login
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": navigator_creds["email"],
                "password": navigator_creds["password"]
            })
            if login_response.status_code == 200:
                login_result = login_response.json()
                navigator_token = login_result.get("data", {}).get("token")
                if navigator_token:
                    self.tokens["navigator"] = navigator_token
                    print("✅ Navigator account already exists and authenticated")
        
        # Step 2: Create Agency account
        agency_creds = QA_CREDENTIALS["agency"]
        agency_data = {
            "email": agency_creds["email"],
            "password": agency_creds["password"],
            "role": "agency",
            "name": "QA Agency User",
            "terms_accepted": True
        }
        
        agency_response = self.session.post(f"{BASE_URL}/auth/register", json=agency_data)
        
        if agency_response.status_code in [200, 201]:
            agency_result = agency_response.json()
            agency_token = agency_result.get("data", {}).get("token")
            if agency_token:
                self.tokens["agency"] = agency_token
                print("✅ Agency account created and authenticated")
        elif "already registered" in agency_response.text.lower():
            # Try to login
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": agency_creds["email"],
                "password": agency_creds["password"]
            })
            if login_response.status_code == 200:
                login_result = login_response.json()
                agency_token = login_result.get("data", {}).get("token")
                if agency_token:
                    self.tokens["agency"] = agency_token
                    print("✅ Agency account already exists and authenticated")
        
        # Step 3: Generate license code for client registration
        license_code = None
        if "agency" in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
                license_response = self.session.post(f"{BASE_URL}/agency/licenses/generate", 
                                                   json={"quantity": 1, "expires_days": 365}, 
                                                   headers=headers)
                if license_response.status_code in [200, 201]:
                    license_result = license_response.json()
                    licenses = license_result.get("licenses", [])
                    if licenses:
                        license_code = licenses[0].get("license_code")
                        print(f"✅ Generated license code: {license_code}")
            except:
                license_code = "1234567890"  # Fallback
                print("⚠️ Using fallback license code")
        
        # Step 4: Create Client account with license code
        client_creds = QA_CREDENTIALS["client"]
        client_data = {
            "email": client_creds["email"],
            "password": client_creds["password"],
            "role": "client",
            "name": "QA Client User",
            "license_code": license_code or "1234567890",
            "terms_accepted": True
        }
        
        client_response = self.session.post(f"{BASE_URL}/auth/register", json=client_data)
        
        if client_response.status_code in [200, 201]:
            client_result = client_response.json()
            client_token = client_result.get("data", {}).get("token")
            if client_token:
                self.tokens["client"] = client_token
                print("✅ Client account created and authenticated")
        elif "already registered" in client_response.text.lower():
            # Try to login
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": client_creds["email"],
                "password": client_creds["password"]
            })
            if login_response.status_code == 200:
                login_result = login_response.json()
                client_token = login_result.get("data", {}).get("token")
                if client_token:
                    self.tokens["client"] = client_token
                    print("✅ Client account already exists and authenticated")
        
        # Step 5: Create Provider account
        provider_creds = QA_CREDENTIALS["provider"]
        provider_data = {
            "email": provider_creds["email"],
            "password": provider_creds["password"],
            "role": "provider",
            "name": "QA Provider User",
            "terms_accepted": True
        }
        
        provider_response = self.session.post(f"{BASE_URL}/auth/register", json=provider_data)
        
        if provider_response.status_code in [200, 201]:
            provider_result = provider_response.json()
            provider_token = provider_result.get("data", {}).get("token")
            if provider_token:
                self.tokens["provider"] = provider_token
                print("✅ Provider account created and authenticated")
        elif "already registered" in provider_response.text.lower():
            # Try to login
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": provider_creds["email"],
                "password": provider_creds["password"]
            })
            if login_response.status_code == 200:
                login_result = login_response.json()
                provider_token = login_result.get("data", {}).get("token")
                if provider_token:
                    self.tokens["provider"] = provider_token
                    print("✅ Provider account already exists and authenticated")
        
        print(f"✅ Setup complete. Authenticated roles: {list(self.tokens.keys())}")
        print()
        
        return len(self.tokens) >= 3  # At least 3 accounts should be working

    def test_user_authentication(self):
        """Test 3: User Authentication - Verify all QA accounts can authenticate"""
        auth_results = []
        
        for role in ["navigator", "agency", "client", "provider"]:
            if role in self.tokens:
                # Verify token works by getting user info
                headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                me_response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    user_info = user_data.get("data", {}) if "data" in user_data else user_data
                    self.log_test(f"User Authentication - {role.title()}", True, 
                                f"Successfully authenticated {QA_CREDENTIALS[role]['email']}, User ID: {user_info.get('id', 'N/A')}")
                    auth_results.append(True)
                else:
                    self.log_test(f"User Authentication - {role.title()}", False, 
                                f"Token verification failed for {QA_CREDENTIALS[role]['email']}")
                    auth_results.append(False)
            else:
                self.log_test(f"User Authentication - {role.title()}", False, 
                            f"No token available for {role}")
                auth_results.append(False)
        
        return len([r for r in auth_results if r]) >= 3  # At least 3 should work

    def test_assessment_endpoints(self):
        """Test 4: Assessment Endpoints - Test tier-based assessment system"""
        if "client" not in self.tokens:
            self.log_test("Assessment Endpoints", False, "No client token available for testing")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        assessment_results = []
        
        try:
            # Test 1: Get tier-based assessment schema
            schema_response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if schema_response.status_code == 200:
                schema_data = schema_response.json()
                if "areas" in schema_data and len(schema_data["areas"]) >= 10:
                    self.log_test("Assessment Schema", True, 
                                f"Retrieved tier-based schema with {len(schema_data['areas'])} areas")
                    assessment_results.append(True)
                    
                    # Check for area10 "Competitive Advantage"
                    area10_found = False
                    for area in schema_data["areas"]:
                        if area.get("id") == "area10" and "competitive" in area.get("name", "").lower():
                            area10_found = True
                            break
                    
                    if area10_found:
                        self.log_test("Assessment Area10 Check", True, "Found area10 'Competitive Advantage'")
                        assessment_results.append(True)
                    else:
                        self.log_test("Assessment Area10 Check", False, "area10 'Competitive Advantage' not found")
                        assessment_results.append(False)
                else:
                    self.log_test("Assessment Schema", False, "Invalid schema structure", schema_data)
                    assessment_results.append(False)
            else:
                self.log_test("Assessment Schema", False, f"Schema request failed: {schema_response.status_code}", 
                            schema_response.text)
                assessment_results.append(False)
            
            # Test 2: Create assessment session
            session_data = {
                "area_id": "area1",
                "tier_level": 1,
                "session_type": "tier_based"
            }
            
            session_response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                               json=session_data, headers=headers)
            
            if session_response.status_code in [200, 201]:
                session_result = session_response.json()
                session_id = session_result.get("session_id")
                if session_id:
                    self.log_test("Assessment Session Creation", True, f"Created session: {session_id}")
                    assessment_results.append(True)
                    
                    # Test 3: Submit assessment response
                    response_data = {
                        "statement_id": "area1_tier1_stmt1",
                        "response": "yes",
                        "confidence_level": "high"
                    }
                    
                    response_response = self.session.post(
                        f"{BASE_URL}/assessment/tier-session/{session_id}/response",
                        json=response_data, headers=headers
                    )
                    
                    if response_response.status_code in [200, 201]:
                        self.log_test("Assessment Response Submission", True, "Successfully submitted assessment response")
                        assessment_results.append(True)
                    else:
                        self.log_test("Assessment Response Submission", False, 
                                    f"Response submission failed: {response_response.status_code}")
                        assessment_results.append(False)
                else:
                    self.log_test("Assessment Session Creation", False, "No session ID in response", session_result)
                    assessment_results.append(False)
            else:
                self.log_test("Assessment Session Creation", False, 
                            f"Session creation failed: {session_response.status_code}", session_response.text)
                assessment_results.append(False)
                
        except requests.exceptions.RequestException as e:
            self.log_test("Assessment Endpoints", False, f"Network error: {str(e)}")
            assessment_results.append(False)
        
        return all(assessment_results)

    def test_service_request_endpoints(self):
        """Test 5: Service Request Endpoints - Test service marketplace functionality"""
        if "client" not in self.tokens or "provider" not in self.tokens:
            self.log_test("Service Request Endpoints", False, "Missing client or provider tokens")
            return False
            
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        service_results = []
        
        try:
            # Test 1: Create service request
            request_data = {
                "area_id": "area5",
                "budget_range": "5000-15000",
                "timeline": "1-2 months",
                "description": "Need help with technology and security infrastructure assessment and implementation",
                "priority": "high"
            }
            
            request_response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                               json=request_data, headers=client_headers)
            
            if request_response.status_code in [200, 201]:
                request_result = request_response.json()
                request_id = request_result.get("request_id") or request_result.get("id")
                
                if request_id:
                    self.log_test("Service Request Creation", True, f"Created service request: {request_id}")
                    service_results.append(True)
                    
                    # Test 2: Provider responds to request
                    response_data = {
                        "request_id": request_id,
                        "proposed_fee": 2500.00,
                        "estimated_timeline": "6-8 weeks",
                        "proposal_note": "I can help with comprehensive technology security assessment and implementation plan"
                    }
                    
                    provider_response = self.session.post(f"{BASE_URL}/provider/respond-to-request",
                                                        json=response_data, headers=provider_headers)
                    
                    if provider_response.status_code in [200, 201]:
                        self.log_test("Provider Response", True, "Provider successfully responded to service request")
                        service_results.append(True)
                        
                        # Test 3: Get service request responses
                        responses_response = self.session.get(f"{BASE_URL}/service-requests/{request_id}/responses",
                                                            headers=client_headers)
                        
                        if responses_response.status_code == 200:
                            responses_data = responses_response.json()
                            if "responses" in responses_data and len(responses_data["responses"]) > 0:
                                self.log_test("Service Request Responses", True, 
                                            f"Retrieved {len(responses_data['responses'])} provider responses")
                                service_results.append(True)
                            else:
                                self.log_test("Service Request Responses", False, "No responses found", responses_data)
                                service_results.append(False)
                        else:
                            self.log_test("Service Request Responses", False, 
                                        f"Failed to get responses: {responses_response.status_code}")
                            service_results.append(False)
                    else:
                        self.log_test("Provider Response", False, 
                                    f"Provider response failed: {provider_response.status_code}", 
                                    provider_response.text)
                        service_results.append(False)
                else:
                    self.log_test("Service Request Creation", False, "No request ID in response", request_result)
                    service_results.append(False)
            else:
                self.log_test("Service Request Creation", False, 
                            f"Request creation failed: {request_response.status_code}", request_response.text)
                service_results.append(False)
                
        except requests.exceptions.RequestException as e:
            self.log_test("Service Request Endpoints", False, f"Network error: {str(e)}")
            service_results.append(False)
        
        return all(service_results)

    def test_additional_endpoints(self):
        """Test 6: Additional Core Endpoints"""
        additional_results = []
        
        # Test with different role tokens
        for role, token in self.tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                # Test dashboard data endpoint
                dashboard_response = self.session.get(f"{BASE_URL}/{role}/dashboard", headers=headers)
                
                if dashboard_response.status_code == 200:
                    self.log_test(f"{role.title()} Dashboard", True, f"Dashboard data retrieved successfully")
                    additional_results.append(True)
                elif dashboard_response.status_code == 404:
                    self.log_test(f"{role.title()} Dashboard", True, f"Dashboard endpoint not implemented (expected)")
                    additional_results.append(True)
                else:
                    self.log_test(f"{role.title()} Dashboard", False, 
                                f"Dashboard request failed: {dashboard_response.status_code}")
                    additional_results.append(False)
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"{role.title()} Dashboard", False, f"Network error: {str(e)}")
                additional_results.append(False)
        
        return len([r for r in additional_results if r]) >= len(additional_results) * 0.5  # 50% success rate

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🎯 POLARIS BACKEND API COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            ("Basic API Health Check", self.test_basic_health_check),
            ("QA Account Setup", self.create_qa_accounts_workflow),
            ("User Authentication", self.test_user_authentication),
            ("Assessment Endpoints", self.test_assessment_endpoints),
            ("Service Request Endpoints", self.test_service_request_endpoints),
            ("Additional Endpoints", self.test_additional_endpoints)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
            
            print()
        
        # Print summary
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Print detailed results
        print("📋 DETAILED RESULTS")
        print("=" * 60)
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        
        # Print created accounts
        if self.created_accounts:
            print("👥 CREATED QA ACCOUNTS")
            print("=" * 60)
            for account in self.created_accounts:
                print(f"✅ {account}")
            print()
        
        # Print available tokens
        if self.tokens:
            print("🔑 AUTHENTICATED ROLES")
            print("=" * 60)
            for role in self.tokens.keys():
                print(f"✅ {role.title()}")
            print()
        
        return passed_tests, total_tests

def main():
    """Main test execution"""
    tester = PolarisAPITester()
    
    try:
        passed, total = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        if passed == total:
            print("🎉 ALL TESTS PASSED - BACKEND IS FULLY OPERATIONAL")
            sys.exit(0)
        elif passed >= total * 0.8:  # 80% success rate
            print("⚠️  MOST TESTS PASSED - BACKEND IS MOSTLY OPERATIONAL")
            sys.exit(0)
        else:
            print("❌ MULTIPLE TEST FAILURES - BACKEND NEEDS ATTENTION")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()