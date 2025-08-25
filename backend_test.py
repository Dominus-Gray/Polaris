#!/usr/bin/env python3
"""
Backend Testing for Maturity Status Endpoints
Testing new maturity status endpoints and frontend integration contract.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://polaris-requirements.preview.emergentagent.com/api"

# Test credentials - using QA credentials from test_result.md
TEST_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class MaturityStatusTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} ({response_time:.3f}s)")
        if details:
            print(f"    Details: {details}")
    
    def authenticate_user(self, role):
        """Authenticate user and get JWT token"""
        try:
            creds = TEST_CREDENTIALS[role]
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=creds,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.tokens[role] = token
                    self.log_test(f"Authentication - {role.title()}", True, 
                                f"Token obtained successfully", response_time)
                    return True
                else:
                    self.log_test(f"Authentication - {role.title()}", False, 
                                "No access token in response", response_time)
                    return False
            else:
                self.log_test(f"Authentication - {role.title()}", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"Authentication - {role.title()}", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self, role):
        """Get authorization headers for a role"""
        token = self.tokens.get(role)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    
    def test_maturity_pending_endpoint(self, role="client"):
        """Test POST /api/assessment/maturity/pending endpoint"""
        try:
            headers = self.get_auth_headers(role)
            if not headers:
                self.log_test(f"Maturity Pending - {role.title()}", False, "No authentication token")
                return None
            
            # Test payload as specified in review request
            payload = {
                "area_id": "area5",
                "question_id": "q5_2", 
                "source": "free",
                "detail": "Selected Free Resources"
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/assessment/maturity/pending",
                json=payload,
                headers=headers,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                status_id = data.get("status_id")
                if status_id:
                    self.log_test(f"Maturity Pending - {role.title()}", True, 
                                f"Status ID: {status_id}", response_time)
                    return status_id
                else:
                    self.log_test(f"Maturity Pending - {role.title()}", False, 
                                "No status_id in response", response_time)
                    return None
            else:
                self.log_test(f"Maturity Pending - {role.title()}", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return None
                
        except Exception as e:
            self.log_test(f"Maturity Pending - {role.title()}", False, f"Exception: {str(e)}")
            return None
    
    def test_maturity_mine_endpoint(self, role="client", expected_status_id=None):
        """Test GET /api/assessment/maturity/mine endpoint"""
        try:
            headers = self.get_auth_headers(role)
            if not headers:
                self.log_test(f"Maturity Mine - {role.title()}", False, "No authentication token")
                return False
            
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/assessment/maturity/mine",
                headers=headers,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                # Check if expected status_id is in the results
                if expected_status_id:
                    found = any(item.get("id") == expected_status_id for item in items)
                    if found:
                        self.log_test(f"Maturity Mine - {role.title()}", True, 
                                    f"Found {len(items)} items, including expected status_id", response_time)
                        return True
                    else:
                        self.log_test(f"Maturity Mine - {role.title()}", False, 
                                    f"Expected status_id {expected_status_id} not found in {len(items)} items", response_time)
                        return False
                else:
                    self.log_test(f"Maturity Mine - {role.title()}", True, 
                                f"Retrieved {len(items)} maturity status items", response_time)
                    return True
            else:
                self.log_test(f"Maturity Mine - {role.title()}", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"Maturity Mine - {role.title()}", False, f"Exception: {str(e)}")
            return False
    
    def test_set_maturity_status(self, status_id, role="client", new_status="compliant"):
        """Test POST /api/assessment/maturity/{status_id}/set-status endpoint"""
        try:
            headers = self.get_auth_headers(role)
            if not headers:
                self.log_test(f"Set Maturity Status - {role.title()}", False, "No authentication token")
                return False
            
            # Use form data as specified (multipart or form)
            form_data = {"status": new_status}
            
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/assessment/maturity/{status_id}/set-status",
                data=form_data,
                headers=headers,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    self.log_test(f"Set Maturity Status - {role.title()}", True, 
                                f"Status updated to '{new_status}'", response_time)
                    return True
                else:
                    self.log_test(f"Set Maturity Status - {role.title()}", False, 
                                "Response ok=False", response_time)
                    return False
            else:
                self.log_test(f"Set Maturity Status - {role.title()}", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"Set Maturity Status - {role.title()}", False, f"Exception: {str(e)}")
            return False
    
    def test_security_cross_user_access(self, status_id, owner_role="client", other_role="provider"):
        """Test security: trying to update another user's status_id should return 404"""
        try:
            headers = self.get_auth_headers(other_role)
            if not headers:
                self.log_test(f"Security Test - Cross User Access", False, "No authentication token for other user")
                return False
            
            form_data = {"status": "compliant"}
            
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/assessment/maturity/{status_id}/set-status",
                data=form_data,
                headers=headers,
                timeout=10
            )
            response_time = time.time() - start_time
            
            # Should return 404 for unauthorized access
            if response.status_code == 404:
                self.log_test(f"Security Test - Cross User Access", True, 
                            f"Correctly returned 404 for unauthorized access", response_time)
                return True
            else:
                self.log_test(f"Security Test - Cross User Access", False, 
                            f"Expected 404, got HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"Security Test - Cross User Access", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_endpoints(self):
        """Test that existing flows are unaffected: /api/assessment/schema, /api/auth/me"""
        
        # Test assessment schema endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/assessment/schema", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                schema = data.get("schema")
                if schema and isinstance(schema, dict):
                    self.log_test("Assessment Schema Endpoint", True, 
                                f"Schema loaded with {len(schema)} areas", response_time)
                else:
                    self.log_test("Assessment Schema Endpoint", False, 
                                "Invalid schema format", response_time)
            else:
                self.log_test("Assessment Schema Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            self.log_test("Assessment Schema Endpoint", False, f"Exception: {str(e)}")
        
        # Test auth/me endpoint for each authenticated user
        for role in self.tokens.keys():
            try:
                headers = self.get_auth_headers(role)
                start_time = time.time()
                response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") and data.get("email") and data.get("role"):
                        self.log_test(f"Auth Me - {role.title()}", True, 
                                    f"User info retrieved: {data.get('role')} - {data.get('email')}", response_time)
                    else:
                        self.log_test(f"Auth Me - {role.title()}", False, 
                                    "Missing required user fields", response_time)
                else:
                    self.log_test(f"Auth Me - {role.title()}", False, 
                                f"HTTP {response.status_code}: {response.text}", response_time)
            except Exception as e:
                self.log_test(f"Auth Me - {role.title()}", False, f"Exception: {str(e)}")
    
    def verify_status_update(self, status_id, role="client", expected_status="compliant"):
        """Verify that the status was actually updated by retrieving it"""
        try:
            headers = self.get_auth_headers(role)
            if not headers:
                self.log_test(f"Verify Status Update - {role.title()}", False, "No authentication token")
                return False
            
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/assessment/maturity/mine",
                headers=headers,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                # Find the specific status_id
                target_item = None
                for item in items:
                    if item.get("id") == status_id:
                        target_item = item
                        break
                
                if target_item:
                    actual_status = target_item.get("status")
                    if actual_status == expected_status:
                        self.log_test(f"Verify Status Update - {role.title()}", True, 
                                    f"Status correctly updated to '{expected_status}'", response_time)
                        return True
                    else:
                        self.log_test(f"Verify Status Update - {role.title()}", False, 
                                    f"Expected status '{expected_status}', got '{actual_status}'", response_time)
                        return False
                else:
                    self.log_test(f"Verify Status Update - {role.title()}", False, 
                                f"Status ID {status_id} not found in results", response_time)
                    return False
            else:
                self.log_test(f"Verify Status Update - {role.title()}", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test(f"Verify Status Update - {role.title()}", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive maturity status endpoint testing"""
        print("🎯 MATURITY STATUS ENDPOINTS TESTING STARTED")
        print("=" * 60)
        
        # Step 1: Authenticate users
        print("\n📋 STEP 1: Authentication")
        auth_success = 0
        for role in ["client", "provider", "agency", "navigator"]:
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success == 0:
            print("❌ CRITICAL: No users could be authenticated. Stopping tests.")
            return
        
        # Step 2: Test existing endpoints to ensure they're unaffected
        print("\n📋 STEP 2: Verify Existing Endpoints")
        self.test_existing_endpoints()
        
        # Step 3: Test maturity pending endpoint with different roles
        print("\n📋 STEP 3: Test Maturity Pending Endpoint")
        status_ids = {}
        for role in self.tokens.keys():
            status_id = self.test_maturity_pending_endpoint(role)
            if status_id:
                status_ids[role] = status_id
        
        # Step 4: Test maturity mine endpoint
        print("\n📋 STEP 4: Test Maturity Mine Endpoint")
        for role in self.tokens.keys():
            expected_id = status_ids.get(role)
            self.test_maturity_mine_endpoint(role, expected_id)
        
        # Step 5: Test set maturity status endpoint
        print("\n📋 STEP 5: Test Set Maturity Status Endpoint")
        for role, status_id in status_ids.items():
            if self.test_set_maturity_status(status_id, role, "compliant"):
                # Verify the update worked
                self.verify_status_update(status_id, role, "compliant")
        
        # Step 6: Test security - cross-user access
        print("\n📋 STEP 6: Security Testing")
        if "client" in status_ids and "provider" in self.tokens:
            client_status_id = status_ids["client"]
            self.test_security_cross_user_access(client_status_id, "client", "provider")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 MATURITY STATUS ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Maturity status endpoints are working correctly ({success_rate:.1f}% success rate)")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Most maturity status endpoints working with minor issues ({success_rate:.1f}% success rate)")
        elif success_rate >= 50:
            print(f"\n⚠️ PARTIAL: Some maturity status endpoints working but significant issues ({success_rate:.1f}% success rate)")
        else:
            print(f"\n❌ CRITICAL: Major issues with maturity status endpoints ({success_rate:.1f}% success rate)")

def main():
    """Main test execution"""
    tester = MaturityStatusTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()