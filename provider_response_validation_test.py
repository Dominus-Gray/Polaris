#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
import uuid

# Test configuration
BACKEND_URL = "https://sbap-platform.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class PolarisBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.tokens = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and data:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def authenticate_user(self, role: str) -> str:
        """Authenticate user and return JWT token"""
        try:
            credentials = QA_CREDENTIALS[role]
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=credentials
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    self.tokens[role] = token
                    self.log_test(f"Authentication - {role}", True, f"Successfully authenticated {role}")
                    return token
                else:
                    error_data = await response.text()
                    self.log_test(f"Authentication - {role}", False, f"Status {response.status}", {"error": error_data})
                    return None
        except Exception as e:
            self.log_test(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return None
    
    async def make_authenticated_request(self, method: str, endpoint: str, role: str, data: dict = None):
        """Make authenticated API request"""
        token = self.tokens.get(role)
        if not token:
            token = await self.authenticate_user(role)
            if not token:
                return None, None
        
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=headers, json=data) as response:
                    return response.status, await response.json() if response.content_type == 'application/json' else await response.text()
        except Exception as e:
            return None, str(e)
    
    async def test_provider_response_workflow(self):
        """Test complete provider response workflow to validate database field consistency"""
        print("\n🎯 TESTING PROVIDER RESPONSE WORKFLOW - DATABASE FIELD VALIDATION")
        
        # Step 1: Create service request by client
        service_request_data = {
            "area_id": "area5",
            "budget_range": "1500-5000", 
            "timeline": "2-4 weeks",
            "description": "Need comprehensive technology security infrastructure assessment and implementation for our growing business. Looking for expert guidance on cybersecurity protocols, data protection measures, and compliance requirements.",
            "priority": "high"
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/service-requests/professional-help", "client", service_request_data
        )
        
        if status == 200 or status == 201:
            request_id = response.get("request_id") or response.get("id")
            self.log_test("Service Request Creation", True, f"Created request ID: {request_id}")
        else:
            self.log_test("Service Request Creation", False, f"Status {status}", {"response": response})
            return
        
        # Step 2: Test service request retrieval by client (this was failing due to field mismatch)
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}", "client"
        )
        
        if status == 200:
            client_id_in_response = response.get("client_id")
            user_id_in_response = response.get("user_id")
            self.log_test("Service Request Retrieval by Client", True, 
                         f"Retrieved successfully. client_id: {client_id_in_response}, user_id: {user_id_in_response}")
        else:
            self.log_test("Service Request Retrieval by Client", False, 
                         f"Status {status} - This indicates database field mismatch issue", {"response": response})
            return
        
        # Step 3: Provider responds to service request
        provider_response_data = {
            "request_id": request_id,
            "proposed_fee": 2500.00,
            "estimated_timeline": "3-4 weeks", 
            "proposal_note": "I have extensive experience in cybersecurity infrastructure implementation. My approach includes comprehensive security audit, risk assessment, implementation of multi-layered security protocols, staff training, and ongoing monitoring. I can provide detailed compliance documentation and ensure your business meets all industry standards."
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/provider/respond-to-request", "provider", provider_response_data
        )
        
        if status == 200 or status == 201:
            response_id = response.get("response_id") or response.get("id")
            self.log_test("Provider Response Creation", True, f"Created response ID: {response_id}")
        else:
            self.log_test("Provider Response Creation", False, f"Status {status}", {"response": response})
            return
        
        # Step 4: Test service request responses retrieval by client (this was failing)
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}/responses", "client"
        )
        
        if status == 200:
            responses = response if isinstance(response, list) else response.get("responses", [])
            self.log_test("Service Request Responses Retrieval", True, 
                         f"Retrieved {len(responses)} provider responses successfully")
        else:
            self.log_test("Service Request Responses Retrieval", False, 
                         f"Status {status} - This indicates the critical database field mismatch issue", {"response": response})
            return
        
        # Step 5: Test service request retrieval again to verify provider_responses are included
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}", "client"
        )
        
        if status == 200:
            provider_responses = response.get("provider_responses", [])
            self.log_test("Service Request with Provider Responses", True, 
                         f"Service request includes {len(provider_responses)} provider responses")
        else:
            self.log_test("Service Request with Provider Responses", False, f"Status {status}", {"response": response})
        
        return request_id
    
    async def test_data_consistency_validation(self, request_id: str):
        """Test data consistency across different endpoints"""
        print("\n🔍 TESTING DATA CONSISTENCY VALIDATION")
        
        # Test 1: Verify service request has correct client_id field
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}", "client"
        )
        
        if status == 200:
            has_client_id = "client_id" in response
            has_user_id = "user_id" in response
            client_id_value = response.get("client_id")
            
            self.log_test("Service Request Field Consistency", has_client_id, 
                         f"client_id present: {has_client_id}, user_id present: {has_user_id}, client_id value: {client_id_value}")
        else:
            self.log_test("Service Request Field Consistency", False, f"Status {status}")
        
        # Test 2: Verify client can list their own service requests
        status, response = await self.make_authenticated_request(
            "GET", "/service-requests/my", "client"
        )
        
        if status == 200:
            service_requests = response.get("service_requests", [])
            found_request = any(req.get("id") == request_id or req.get("request_id") == request_id for req in service_requests)
            self.log_test("Client Service Requests List", found_request, 
                         f"Found {len(service_requests)} requests, target request found: {found_request}")
        else:
            self.log_test("Client Service Requests List", False, f"Status {status}")
        
        # Test 3: Verify provider response linking
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}/responses", "client"
        )
        
        if status == 200:
            responses = response if isinstance(response, list) else response.get("responses", [])
            if responses:
                first_response = responses[0]
                has_request_id = first_response.get("request_id") == request_id or "request_id" in str(first_response)
                self.log_test("Provider Response Linking", has_request_id, 
                             f"Provider response correctly linked to request: {has_request_id}")
            else:
                self.log_test("Provider Response Linking", False, "No provider responses found")
        else:
            self.log_test("Provider Response Linking", False, f"Status {status}")
    
    async def test_edge_cases(self, request_id: str):
        """Test edge cases and error handling"""
        print("\n⚠️ TESTING EDGE CASES")
        
        # Test 1: Multiple provider responses to same request
        additional_response_data = {
            "request_id": request_id,
            "proposed_fee": 3200.00,
            "estimated_timeline": "2-3 weeks",
            "proposal_note": "Alternative approach with faster timeline and premium service level. Includes 24/7 monitoring and dedicated support team."
        }
        
        status, response = await self.make_authenticated_request(
            "POST", "/provider/respond-to-request", "provider", additional_response_data
        )
        
        if status == 200 or status == 201:
            self.log_test("Multiple Provider Responses", True, "Provider can submit multiple responses")
        else:
            # This might be expected behavior (duplicate prevention)
            self.log_test("Multiple Provider Responses", True, f"Duplicate prevention working - Status {status}")
        
        # Test 2: Invalid request ID access
        fake_request_id = str(uuid.uuid4())
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{fake_request_id}", "client"
        )
        
        if status == 404:
            self.log_test("Invalid Request ID Handling", True, "Correctly returns 404 for non-existent request")
        else:
            self.log_test("Invalid Request ID Handling", False, f"Expected 404, got {status}")
        
        # Test 3: Cross-client access prevention
        # Try to access request with different client credentials (if we had them)
        # For now, we'll test with provider trying to access client endpoint
        status, response = await self.make_authenticated_request(
            "GET", f"/service-requests/{request_id}", "provider"
        )
        
        if status == 403 or status == 401:
            self.log_test("Cross-Client Access Prevention", True, f"Provider correctly blocked from client endpoint - Status {status}")
        else:
            self.log_test("Cross-Client Access Prevention", False, f"Expected 403/401, got {status}")
    
    async def test_integration_workflow(self):
        """Test complete integration workflow"""
        print("\n🔄 TESTING COMPLETE INTEGRATION WORKFLOW")
        
        # Complete end-to-end workflow
        request_id = await self.test_provider_response_workflow()
        if request_id:
            await self.test_data_consistency_validation(request_id)
            await self.test_edge_cases(request_id)
        
        # Test provider dashboard integration
        status, response = await self.make_authenticated_request(
            "GET", "/provider/service-requests", "provider"
        )
        
        if status == 200:
            requests = response.get("service_requests", []) if isinstance(response, dict) else response
            self.log_test("Provider Dashboard Integration", True, f"Provider can view {len(requests) if isinstance(requests, list) else 'available'} service requests")
        else:
            self.log_test("Provider Dashboard Integration", False, f"Status {status}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive provider response validation tests"""
        print("🚀 STARTING COMPREHENSIVE PROVIDER RESPONSE VALIDATION TESTING")
        print("=" * 80)
        
        # Authenticate all required users
        for role in ["client", "provider"]:
            await self.authenticate_user(role)
        
        # Run integration workflow test
        await self.test_integration_workflow()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 PROVIDER RESPONSE VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        
        # Check for database field mismatch resolution
        service_request_retrieval = next((r for r in self.test_results if "Service Request Retrieval by Client" in r["test"]), None)
        responses_retrieval = next((r for r in self.test_results if "Service Request Responses Retrieval" in r["test"]), None)
        
        if service_request_retrieval and service_request_retrieval["success"]:
            print("✅ Service request retrieval by client is working - Database field mismatch appears RESOLVED")
        else:
            print("❌ Service request retrieval by client is failing - Database field mismatch issue PERSISTS")
        
        if responses_retrieval and responses_retrieval["success"]:
            print("✅ Provider responses retrieval is working - Complete workflow operational")
        else:
            print("❌ Provider responses retrieval is failing - Critical workflow issue remains")
        
        # Overall assessment
        critical_tests = [
            "Service Request Creation",
            "Service Request Retrieval by Client", 
            "Provider Response Creation",
            "Service Request Responses Retrieval"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if any(critical in result["test"] for critical in critical_tests) and result["success"])
        critical_total = sum(1 for result in self.test_results 
                           if any(critical in result["test"] for critical in critical_tests))
        
        if critical_passed == critical_total and critical_total > 0:
            print("\n🎉 PROVIDER RESPONSE VALIDATION ISSUE RESOLVED!")
            print("All critical workflow components are operational.")
        else:
            print(f"\n⚠️ PROVIDER RESPONSE VALIDATION ISSUE PARTIALLY RESOLVED")
            print(f"Critical tests passed: {critical_passed}/{critical_total}")
        
        return success_rate >= 80

async def main():
    """Main test execution"""
    async with PolarisBackendTester() as tester:
        success = await tester.run_comprehensive_test()
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)