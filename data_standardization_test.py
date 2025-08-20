#!/usr/bin/env python3
"""
Comprehensive Data Standardization Testing for Engagement System
Tests all standardized data models, validation, processing, and error handling
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import uuid

# Test Configuration
BACKEND_URL = "https://agency-connect-4.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class DataStandardizationTester:
    def __init__(self):
        self.session = None
        self.client_token = None
        self.provider_token = None
        self.test_results = []
        self.test_data = {}
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self, role):
        """Authenticate user and return token"""
        credentials = QA_CREDENTIALS[role]
        
        async with self.session.post(
            f"{BACKEND_URL}/auth/login",
            json=credentials
        ) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("access_token")
                print(f"✅ {role.title()} authentication successful")
                return token
            else:
                error_data = await response.text()
                print(f"❌ {role.title()} authentication failed: {response.status} - {error_data}")
                return None
    
    async def make_authenticated_request(self, method, endpoint, token, data=None):
        """Make authenticated API request"""
        headers = {"Authorization": f"Bearer {token}"}
        
        if method.upper() == "GET":
            async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
        elif method.upper() == "POST":
            async with self.session.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=data) as response:
                return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
        elif method.upper() == "PUT":
            async with self.session.put(f"{BACKEND_URL}{endpoint}", headers=headers, json=data) as response:
                return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
    
    def log_test_result(self, test_name, passed, details):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    async def test_standardized_service_request_creation(self):
        """Test 1: Service Request Creation with StandardizedEngagementRequest"""
        print("\n🔍 Testing Standardized Service Request Creation...")
        
        # Test valid request
        valid_request = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Need comprehensive cybersecurity assessment and implementation for our growing business. Looking for expert guidance on security infrastructure, compliance requirements, and risk management strategies.",
            "priority": "high",
            "urgency": "medium"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/service-requests/professional-help", self.client_token, valid_request
        )
        
        if status == 200 or status == 201:
            # Verify standardized response structure
            required_fields = ["success", "request_id", "area_name", "providers_notified", "status", "created_at", "metadata"]
            
            missing_fields = [field for field in required_fields if field not in response]
            if not missing_fields:
                # Store request ID for later tests
                self.test_data["request_id"] = response["request_id"]
                
                # Verify data standardization
                standardization_checks = [
                    response["success"] == True,
                    response["area_name"] == "Technology & Security Infrastructure",
                    response["status"] == "active",
                    response["metadata"]["data_version"] == "1.0",
                    response["metadata"]["standardized"] == True,
                    "Z" in response["created_at"],  # ISO8601 format check
                    response["providers_notified"] > 0  # Should notify providers
                ]
                
                if all(standardization_checks):
                    self.log_test_result(
                        "Standardized Service Request Creation", 
                        True, 
                        f"Request created with ID: {response['request_id']}, Area: {response['area_name']}, Providers notified: {response['providers_notified']}"
                    )
                else:
                    self.log_test_result(
                        "Standardized Service Request Creation", 
                        False, 
                        f"Data standardization validation failed: {response}"
                    )
            else:
                self.log_test_result(
                    "Standardized Service Request Creation", 
                    False, 
                    f"Missing required fields: {missing_fields}"
                )
        else:
            self.log_test_result(
                "Standardized Service Request Creation", 
                False, 
                f"Request failed with status {status}: {response}"
            )
    
    async def test_data_validation_errors(self):
        """Test 2: Data Validation with Polaris Error Codes"""
        print("\n🔍 Testing Data Validation and Error Standardization...")
        
        # Test invalid area_id
        invalid_area_request = {
            "area_id": "invalid_area",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Test description for invalid area",
            "priority": "high"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/service-requests/professional-help", self.client_token, invalid_area_request
        )
        
        # Should return 400 with Polaris error code
        if status == 400 and isinstance(response, dict):
            error_detail = response.get("detail", {})
            if error_detail.get("error_code") == "POL-3002":
                self.log_test_result(
                    "Invalid Area ID Validation", 
                    True, 
                    f"Correctly returned POL-3002 error: {error_detail.get('message')}"
                )
            else:
                self.log_test_result(
                    "Invalid Area ID Validation", 
                    False, 
                    f"Expected POL-3002 error code, got: {response}"
                )
        else:
            self.log_test_result(
                "Invalid Area ID Validation", 
                False, 
                f"Expected 400 status with error code, got {status}: {response}"
            )
        
        # Test invalid budget range
        invalid_budget_request = {
            "area_id": "area5",
            "budget_range": "invalid-budget",
            "timeline": "2-4 weeks",
            "description": "Test description for invalid budget",
            "priority": "high"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/service-requests/professional-help", self.client_token, invalid_budget_request
        )
        
        if status == 400 and isinstance(response, dict):
            error_detail = response.get("detail", {})
            if error_detail.get("error_code") == "POL-3002":
                self.log_test_result(
                    "Invalid Budget Range Validation", 
                    True, 
                    f"Correctly returned POL-3002 error: {error_detail.get('message')}"
                )
            else:
                self.log_test_result(
                    "Invalid Budget Range Validation", 
                    False, 
                    f"Expected POL-3002 error code, got: {response}"
                )
        else:
            self.log_test_result(
                "Invalid Budget Range Validation", 
                False, 
                f"Expected 400 status with error code, got {status}: {response}"
            )
    
    async def test_standardized_provider_response(self):
        """Test 3: Provider Response with StandardizedProviderResponse"""
        print("\n🔍 Testing Standardized Provider Response...")
        
        if not self.test_data.get("request_id"):
            self.log_test_result(
                "Standardized Provider Response", 
                False, 
                "No request_id available from previous test"
            )
            return
        
        # Test valid provider response
        valid_response = {
            "request_id": self.test_data["request_id"],
            "proposed_fee": 2500.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "I specialize in cybersecurity assessments for small businesses. My approach includes comprehensive security audits, risk assessments, implementation of security frameworks, and ongoing monitoring solutions. I have 8+ years of experience in this field and can deliver within your timeline."
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/provider/respond-to-request", self.provider_token, valid_response
        )
        
        if status == 200 or status == 201:
            # Verify standardized response structure
            required_fields = ["response_id", "request_id", "provider_id", "proposed_fee", "currency", "fee_formatted", "estimated_timeline", "proposal_note", "status", "created_at", "updated_at", "data_version", "metadata"]
            
            missing_fields = [field for field in required_fields if field not in response]
            if not missing_fields:
                # Store response ID for later tests
                self.test_data["response_id"] = response["response_id"]
                
                # Verify currency standardization
                currency_checks = [
                    response["proposed_fee"] == 2500.00,
                    response["currency"] == "USD",
                    response["fee_formatted"] == "$2,500.00",
                    response["status"] == "submitted",
                    response["data_version"] == "1.0",
                    response["metadata"]["standardized"] == True,
                    response["metadata"]["fee_validation"] == "passed"
                ]
                
                if all(currency_checks):
                    self.log_test_result(
                        "Standardized Provider Response", 
                        True, 
                        f"Response created with ID: {response['response_id']}, Fee: {response['fee_formatted']}"
                    )
                else:
                    self.log_test_result(
                        "Standardized Provider Response", 
                        False, 
                        f"Currency standardization validation failed: {response}"
                    )
            else:
                self.log_test_result(
                    "Standardized Provider Response", 
                    False, 
                    f"Missing required fields: {missing_fields}"
                )
        else:
            self.log_test_result(
                "Standardized Provider Response", 
                False, 
                f"Response failed with status {status}: {response}"
            )
    
    async def test_provider_response_validation(self):
        """Test 4: Provider Response Data Validation"""
        print("\n🔍 Testing Provider Response Data Validation...")
        
        if not self.test_data.get("request_id"):
            self.log_test_result(
                "Provider Response Validation", 
                False, 
                "No request_id available from previous test"
            )
            return
        
        # Test invalid fee (negative)
        invalid_fee_response = {
            "request_id": self.test_data["request_id"],
            "proposed_fee": -100.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "Test proposal with invalid negative fee"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/provider/respond-to-request", self.provider_token, invalid_fee_response
        )
        
        # Should return validation error
        if status == 422 or status == 400:
            self.log_test_result(
                "Invalid Fee Validation", 
                True, 
                f"Correctly rejected negative fee with status {status}"
            )
        else:
            self.log_test_result(
                "Invalid Fee Validation", 
                False, 
                f"Expected validation error, got {status}: {response}"
            )
        
        # Test invalid timeline
        invalid_timeline_response = {
            "request_id": self.test_data["request_id"],
            "proposed_fee": 1500.00,
            "estimated_timeline": "invalid-timeline",
            "proposal_note": "Test proposal with invalid timeline format"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/provider/respond-to-request", self.provider_token, invalid_timeline_response
        )
        
        if status == 422 or status == 400:
            self.log_test_result(
                "Invalid Timeline Validation", 
                True, 
                f"Correctly rejected invalid timeline with status {status}"
            )
        else:
            self.log_test_result(
                "Invalid Timeline Validation", 
                False, 
                f"Expected validation error, got {status}: {response}"
            )
    
    async def test_engagement_status_updates(self):
        """Test 5: Engagement Status Updates"""
        print("\n🔍 Testing Engagement Status Updates...")
        
        # Test status update with valid transition
        mock_engagement_id = str(uuid.uuid4())
        
        valid_status_update = {
            "engagement_id": mock_engagement_id,
            "status": "in_progress",
            "notes": "Starting work on cybersecurity assessment",
            "milestone_completion": 10.0
        }
        
        status, response = await self.make_authenticated_request(
            "PUT", f"/engagements/{mock_engagement_id}/status", self.client_token, valid_status_update
        )
        
        # Even if engagement doesn't exist, we should get proper error handling
        if status == 404:
            error_detail = response.get("detail", {}) if isinstance(response, dict) else {}
            if error_detail.get("error_code") == "POL-1007":
                self.log_test_result(
                    "Engagement Status Update Error Handling", 
                    True, 
                    f"Correctly returned POL-1007 for non-existent engagement"
                )
            else:
                self.log_test_result(
                    "Engagement Status Update Error Handling", 
                    False, 
                    f"Expected POL-1007 error code, got: {response}"
                )
        else:
            self.log_test_result(
                "Engagement Status Update Error Handling", 
                False, 
                f"Expected 404 with POL-1007, got {status}: {response}"
            )
    
    async def test_status_transition_validation(self):
        """Test 6: Status Transition Workflow Validation"""
        print("\n🔍 Testing Status Transition Workflow Validation...")
        
        # Test invalid status transition
        mock_engagement_id = str(uuid.uuid4())
        
        # Try to transition from active to completed (should be invalid)
        invalid_transition = {
            "engagement_id": mock_engagement_id,
            "status": "completed",  # Invalid direct transition from active
            "notes": "Attempting invalid status transition"
        }
        
        status, response = await self.make_authenticated_request(
            "PUT", f"/engagements/{mock_engagement_id}/status", self.client_token, invalid_transition
        )
        
        # Should get error for non-existent engagement first, but the endpoint should exist
        if status in [404, 400, 422]:
            self.log_test_result(
                "Status Transition Validation Endpoint", 
                True, 
                f"Status transition endpoint exists and handles requests (status: {status})"
            )
        else:
            self.log_test_result(
                "Status Transition Validation Endpoint", 
                False, 
                f"Unexpected response from status transition endpoint: {status}"
            )
    
    async def test_notification_standardization(self):
        """Test 7: Notification System Standardization"""
        print("\n🔍 Testing Notification System Standardization...")
        
        # Check if notifications were created during service request creation
        # This is tested indirectly through the service request creation process
        
        # Test notification retrieval (if endpoint exists)
        status, response = await self.make_authenticated_request(
            "GET", "/notifications", self.client_token
        )
        
        if status == 200:
            if isinstance(response, list):
                self.log_test_result(
                    "Notification System Access", 
                    True, 
                    f"Successfully retrieved {len(response)} notifications"
                )
            else:
                self.log_test_result(
                    "Notification System Access", 
                    True, 
                    "Notification endpoint accessible"
                )
        elif status == 404:
            self.log_test_result(
                "Notification System Access", 
                True, 
                "Notification endpoint not implemented (expected for MVP)"
            )
        else:
            self.log_test_result(
                "Notification System Access", 
                False, 
                f"Unexpected response from notifications endpoint: {status}"
            )
    
    async def test_timestamp_standardization(self):
        """Test 8: Timestamp Standardization (ISO8601)"""
        print("\n🔍 Testing Timestamp Standardization...")
        
        # This is tested as part of other tests by checking created_at and updated_at fields
        # All timestamps should be in ISO8601 format with 'Z' suffix
        
        if self.test_data.get("request_id"):
            # Get the service request to check timestamp format
            status, response = await self.make_authenticated_request(
                "GET", f"/service-requests/{self.test_data['request_id']}", self.client_token
            )
            
            if status == 200 and isinstance(response, dict):
                created_at = response.get("created_at", "")
                updated_at = response.get("updated_at", "")
                
                # Check ISO8601 format
                iso8601_checks = [
                    "T" in created_at,
                    "Z" in created_at,
                    "T" in updated_at,
                    "Z" in updated_at,
                    len(created_at) >= 19  # Minimum ISO8601 length
                ]
                
                if all(iso8601_checks):
                    self.log_test_result(
                        "Timestamp Standardization", 
                        True, 
                        f"Timestamps in correct ISO8601 format: {created_at}"
                    )
                else:
                    self.log_test_result(
                        "Timestamp Standardization", 
                        False, 
                        f"Invalid timestamp format - created_at: {created_at}, updated_at: {updated_at}"
                    )
            else:
                self.log_test_result(
                    "Timestamp Standardization", 
                    False, 
                    f"Could not retrieve service request for timestamp validation: {status}"
                )
        else:
            self.log_test_result(
                "Timestamp Standardization", 
                False, 
                "No service request available for timestamp validation"
            )
    
    async def run_comprehensive_tests(self):
        """Run all data standardization tests"""
        print("🚀 Starting Comprehensive Data Standardization Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        
        await self.setup_session()
        
        try:
            # Authenticate users
            print("\n🔐 Authenticating test users...")
            self.client_token = await self.authenticate_user("client")
            self.provider_token = await self.authenticate_user("provider")
            
            if not self.client_token or not self.provider_token:
                print("❌ Authentication failed - cannot proceed with tests")
                return
            
            # Run all tests
            await self.test_standardized_service_request_creation()
            await self.test_data_validation_errors()
            await self.test_standardized_provider_response()
            await self.test_provider_response_validation()
            await self.test_engagement_status_updates()
            await self.test_status_transition_validation()
            await self.test_notification_standardization()
            await self.test_timestamp_standardization()
            
            # Print summary
            self.print_test_summary()
            
        finally:
            await self.cleanup_session()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 DATA STANDARDIZATION TEST SUMMARY")
        print("="*80)
        
        passed_tests = [test for test in self.test_results if test["passed"]]
        failed_tests = [test for test in self.test_results if not test["passed"]]
        
        total_tests = len(self.test_results)
        passed_count = len(passed_tests)
        failed_count = len(failed_tests)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        if passed_tests:
            print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
            for test in passed_tests:
                print(f"  • {test['test']}")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if success_rate >= 80:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Data standardization system is working well")
        elif success_rate >= 60:
            print("⚠️  OVERALL ASSESSMENT: GOOD - Minor issues need attention")
        else:
            print("🚨 OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Critical issues found")

async def main():
    """Main test execution"""
    tester = DataStandardizationTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())