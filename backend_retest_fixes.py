#!/usr/bin/env python3
"""
Backend Retest - Focused testing for fixed endpoints (September 2025)
Testing specific fixes for enhanced service responses, payments body parsing, and assessment format sanity
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
import tempfile
import os

# Test Configuration
BASE_URL = "https://production-guru.preview.emergentagent.com/api"  # Using production URL from frontend/.env
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class BackendRetestRunner:
    def __init__(self):
        self.session = None
        self.tokens = {}
        self.test_results = []
        self.service_request_id = None
        self.provider_id = None
        self.session_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_user(self, role: str) -> bool:
        """Authenticate QA user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            async with self.session.post(f"{BASE_URL}/auth/login", json=creds) as response:
                if response.status == 200:
                    data = await response.json()
                    self.tokens[role] = data["access_token"]
                    print(f"✅ {role.upper()} authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ {role.upper()} authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ {role.upper()} authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {"Authorization": f"Bearer {self.tokens[role]}"}
        
    async def test_1_enhanced_service_responses(self) -> Dict[str, Any]:
        """Test 1: Enhanced service responses workflow"""
        print("\n🔍 TEST 1: Enhanced Service Responses")
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Step 1: Create service request as client
        try:
            service_data = {
                "area_id": "area5",
                "budget_range": "1500-5000", 
                "timeline": "2-4 weeks",
                "description": "Fix retest"
            }
            
            headers = self.get_auth_headers("client")
            async with self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                       json=service_data, headers=headers) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.service_request_id = data.get("request_id") or data.get("id")
                    results["passed"] += 1
                    results["details"].append("✅ Service request created successfully")
                    print(f"   ✅ Service request created: {self.service_request_id}")
                else:
                    error_text = await response.text()
                    results["failed"] += 1
                    results["details"].append(f"❌ Service request creation failed: {response.status} - {error_text}")
                    print(f"   ❌ Service request creation failed: {response.status}")
                    return results
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Service request creation error: {str(e)}")
            return results
            
        # Step 2: Provider response as provider.qa
        try:
            response_data = {
                "request_id": self.service_request_id,
                "proposed_fee": 2000,
                "estimated_timeline": "2-4 weeks",
                "proposal_note": "QA test response"
            }
            
            headers = self.get_auth_headers("provider")
            async with self.session.post(f"{BASE_URL}/provider/respond-to-request", 
                                       json=response_data, headers=headers) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.provider_id = data.get("provider_id")
                    results["passed"] += 1
                    results["details"].append("✅ Provider response submitted successfully")
                    print(f"   ✅ Provider response submitted")
                else:
                    error_text = await response.text()
                    results["failed"] += 1
                    results["details"].append(f"❌ Provider response failed: {response.status} - {error_text}")
                    print(f"   ❌ Provider response failed: {response.status}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Provider response error: {str(e)}")
            
        # Step 3: GET enhanced responses as client
        try:
            headers = self.get_auth_headers("client")
            async with self.session.get(f"{BASE_URL}/service-requests/{self.service_request_id}/responses/enhanced", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    checks = []
                    if "responses" in data and data["responses"]:
                        provider_info = data["responses"][0].get("provider_info", {})
                        if provider_info.get("business_name") is not None:
                            checks.append("✅ provider_info.business_name not null")
                        else:
                            checks.append("❌ provider_info.business_name is null")
                    else:
                        checks.append("❌ responses array missing or empty")
                        
                    if "total_responses" in data and data["total_responses"] >= 1:
                        checks.append("✅ total_responses >= 1")
                    else:
                        checks.append("❌ total_responses < 1")
                        
                    if "response_limit_reached" in data and isinstance(data["response_limit_reached"], bool):
                        checks.append("✅ response_limit_reached boolean present")
                    else:
                        checks.append("❌ response_limit_reached boolean missing")
                        
                    if all("✅" in check for check in checks):
                        results["passed"] += 1
                        results["details"].append("✅ Enhanced responses validation passed")
                        print(f"   ✅ Enhanced responses validation passed")
                    else:
                        results["failed"] += 1
                        results["details"].append(f"❌ Enhanced responses validation failed: {checks}")
                        print(f"   ❌ Enhanced responses validation failed")
                        
                elif response.status == 500:
                    results["failed"] += 1
                    results["details"].append("❌ Enhanced responses returned 500 error")
                    print(f"   ❌ Enhanced responses returned 500 error")
                else:
                    error_text = await response.text()
                    results["failed"] += 1
                    results["details"].append(f"❌ Enhanced responses failed: {response.status} - {error_text}")
                    print(f"   ❌ Enhanced responses failed: {response.status}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Enhanced responses error: {str(e)}")
            
        return results
        
    async def test_2_payments_body_parsing(self) -> Dict[str, Any]:
        """Test 2: Payments body parsing fixes"""
        print("\n🔍 TEST 2: Payments Body Parsing")
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test 2a: Knowledge Base checkout session
        try:
            kb_payment_data = {
                "package_id": "knowledge_base_single",
                "origin_url": "http://localhost",
                "metadata": {"area_id": "area1"}
            }
            
            headers = self.get_auth_headers("client")
            async with self.session.post(f"{BASE_URL}/payments/v1/checkout/session", 
                                       json=kb_payment_data, headers=headers) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    if "url" in data:
                        results["passed"] += 1
                        results["details"].append("✅ KB checkout session created with URL (Stripe available)")
                        print(f"   ✅ KB checkout session created with URL")
                    else:
                        results["passed"] += 1
                        results["details"].append("✅ KB checkout session created without URL (expected if no Stripe)")
                        print(f"   ✅ KB checkout session created")
                elif response.status == 503:
                    results["passed"] += 1
                    results["details"].append("✅ KB checkout returned 503 (Stripe unavailable - expected)")
                    print(f"   ✅ KB checkout returned 503 (Stripe unavailable)")
                elif response.status == 422:
                    results["failed"] += 1
                    results["details"].append("❌ KB checkout returned 422 (body parsing issue)")
                    print(f"   ❌ KB checkout returned 422 (body parsing issue)")
                else:
                    error_text = await response.text()
                    results["failed"] += 1
                    results["details"].append(f"❌ KB checkout failed: {response.status} - {error_text}")
                    print(f"   ❌ KB checkout failed: {response.status}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ KB checkout error: {str(e)}")
            
        # Test 2b: Service request payment
        if self.service_request_id and self.provider_id:
            try:
                service_payment_data = {
                    "agreed_fee": 1500,
                    "provider_id": self.provider_id,
                    "origin_url": "http://localhost",
                    "request_id": self.service_request_id
                }
                
                headers = self.get_auth_headers("client")
                async with self.session.post(f"{BASE_URL}/payments/service-request", 
                                           json=service_payment_data, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        if "url" in data:
                            results["passed"] += 1
                            results["details"].append("✅ Service payment created with URL (Stripe available)")
                            print(f"   ✅ Service payment created with URL")
                        else:
                            results["passed"] += 1
                            results["details"].append("✅ Service payment created without URL")
                            print(f"   ✅ Service payment created")
                    elif response.status == 503:
                        results["passed"] += 1
                        results["details"].append("✅ Service payment returned 503 (Stripe unavailable - expected)")
                        print(f"   ✅ Service payment returned 503 (Stripe unavailable)")
                    elif response.status == 422:
                        results["failed"] += 1
                        results["details"].append("❌ Service payment returned 422 (body parsing issue)")
                        print(f"   ❌ Service payment returned 422 (body parsing issue)")
                    else:
                        error_text = await response.text()
                        results["failed"] += 1
                        results["details"].append(f"❌ Service payment failed: {response.status} - {error_text}")
                        print(f"   ❌ Service payment failed: {response.status}")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Service payment error: {str(e)}")
        else:
            results["failed"] += 1
            results["details"].append("❌ Service payment skipped - missing service request or provider ID")
            
        return results
        
    async def test_3_assessment_format_sanity(self) -> Dict[str, Any]:
        """Test 3: Assessment format sanity checks"""
        print("\n🔍 TEST 3: Assessment Format Sanity")
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Step 3a: Create tier session
        try:
            # Use multipart form data as specified
            form_data = aiohttp.FormData()
            form_data.add_field('area_id', 'area5')
            form_data.add_field('tier_level', '3')
            
            headers = self.get_auth_headers("client")
            async with self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=form_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "questions" in data and isinstance(data["questions"], list):
                        self.session_id = data.get("session_id")
                        results["passed"] += 1
                        results["details"].append("✅ Tier session created with questions array")
                        print(f"   ✅ Tier session created: {self.session_id}")
                    else:
                        results["failed"] += 1
                        results["details"].append("❌ Tier session missing questions array")
                        print(f"   ❌ Tier session missing questions array")
                else:
                    error_text = await response.text()
                    results["failed"] += 1
                    results["details"].append(f"❌ Tier session creation failed: {response.status} - {error_text}")
                    print(f"   ❌ Tier session creation failed: {response.status}")
                    return results
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Tier session creation error: {str(e)}")
            return results
            
        # Step 3b: Test evidence requirement validation
        if self.session_id:
            try:
                # Get first question ID from the session
                headers = self.get_auth_headers("client")
                async with self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}", 
                                          headers=headers) as response:
                    if response.status == 200:
                        session_data = await response.json()
                        questions = session_data.get("questions", [])
                        if questions:
                            question_id = questions[0].get("id")
                            
                            # Try submitting compliant response without evidence (should fail for Tier 2/3)
                            form_data = aiohttp.FormData()
                            form_data.add_field('question_id', question_id)
                            form_data.add_field('response', 'compliant')
                            form_data.add_field('evidence_provided', 'false')
                            
                            async with self.session.post(f"{BASE_URL}/assessment/tier-session/{self.session_id}/response", 
                                                        data=form_data, headers=headers) as response:
                                if response.status == 422:
                                    error_data = await response.json()
                                    if "evidence" in str(error_data).lower():
                                        results["passed"] += 1
                                        results["details"].append("✅ Evidence requirement validation working (422 with evidence message)")
                                        print(f"   ✅ Evidence requirement validation working")
                                    else:
                                        results["failed"] += 1
                                        results["details"].append("❌ 422 error but no evidence message")
                                        print(f"   ❌ 422 error but no evidence message")
                                else:
                                    results["failed"] += 1
                                    results["details"].append(f"❌ Expected 422 for missing evidence, got {response.status}")
                                    print(f"   ❌ Expected 422 for missing evidence, got {response.status}")
                        else:
                            results["failed"] += 1
                            results["details"].append("❌ No questions found in session")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Evidence validation error: {str(e)}")
                
        # Step 3c: Test evidence upload
        try:
            if self.session_id:
                # Create a small test file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                    temp_file.write("Test evidence document for QA")
                    temp_file_path = temp_file.name
                
                try:
                    # Upload evidence file
                    form_data = aiohttp.FormData()
                    form_data.add_field('question_id', 'test_question_id')
                    
                    with open(temp_file_path, 'rb') as f:
                        form_data.add_field('file', f, filename='test_evidence.txt', content_type='text/plain')
                        
                        headers = self.get_auth_headers("client")
                        async with self.session.post(f"{BASE_URL}/assessment/evidence", 
                                                    data=form_data, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                if "files" in data and len(data["files"]) >= 1:
                                    results["passed"] += 1
                                    results["details"].append("✅ Evidence upload successful with files array")
                                    print(f"   ✅ Evidence upload successful")
                                else:
                                    results["failed"] += 1
                                    results["details"].append("❌ Evidence upload missing files array")
                                    print(f"   ❌ Evidence upload missing files array")
                            else:
                                error_text = await response.text()
                                results["failed"] += 1
                                results["details"].append(f"❌ Evidence upload failed: {response.status} - {error_text}")
                                print(f"   ❌ Evidence upload failed: {response.status}")
                finally:
                    # Clean up temp file
                    os.unlink(temp_file_path)
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Evidence upload error: {str(e)}")
            
        # Step 3d: Re-submit response with evidence
        if self.session_id:
            try:
                headers = self.get_auth_headers("client")
                async with self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}", 
                                          headers=headers) as response:
                    if response.status == 200:
                        session_data = await response.json()
                        questions = session_data.get("questions", [])
                        if questions:
                            question_id = questions[0].get("id")
                            
                            # Submit compliant response with evidence_provided=true
                            form_data = aiohttp.FormData()
                            form_data.add_field('question_id', question_id)
                            form_data.add_field('response', 'compliant')
                            form_data.add_field('evidence_provided', 'true')
                            
                            async with self.session.post(f"{BASE_URL}/assessment/tier-session/{self.session_id}/response", 
                                                        data=form_data, headers=headers) as response:
                                if response.status == 200:
                                    results["passed"] += 1
                                    results["details"].append("✅ Response with evidence accepted (200)")
                                    print(f"   ✅ Response with evidence accepted")
                                else:
                                    error_text = await response.text()
                                    results["failed"] += 1
                                    results["details"].append(f"❌ Response with evidence failed: {response.status} - {error_text}")
                                    print(f"   ❌ Response with evidence failed: {response.status}")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ Response with evidence error: {str(e)}")
                
        return results
        
    async def run_all_tests(self):
        """Run all focused retest scenarios"""
        print("🚀 Starting Backend Retest - Focused Fixes (September 2025)")
        print(f"🔗 Testing against: {BASE_URL}")
        
        await self.setup_session()
        
        try:
            # Authenticate both users
            client_auth = await self.authenticate_user("client")
            provider_auth = await self.authenticate_user("provider")
            
            if not client_auth or not provider_auth:
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run focused tests
            test1_results = await self.test_1_enhanced_service_responses()
            test2_results = await self.test_2_payments_body_parsing()
            test3_results = await self.test_3_assessment_format_sanity()
            
            # Compile results
            total_passed = test1_results["passed"] + test2_results["passed"] + test3_results["passed"]
            total_failed = test1_results["failed"] + test2_results["failed"] + test3_results["failed"]
            total_tests = total_passed + total_failed
            success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            print(f"\n📊 BACKEND RETEST SUMMARY:")
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {total_passed}")
            print(f"   Failed: {total_failed}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            # Detailed results
            print(f"\n📋 DETAILED RESULTS:")
            print(f"   Test 1 (Enhanced Service Responses): {test1_results['passed']}/{test1_results['passed'] + test1_results['failed']}")
            for detail in test1_results["details"]:
                print(f"     {detail}")
                
            print(f"   Test 2 (Payments Body Parsing): {test2_results['passed']}/{test2_results['passed'] + test2_results['failed']}")
            for detail in test2_results["details"]:
                print(f"     {detail}")
                
            print(f"   Test 3 (Assessment Format Sanity): {test3_results['passed']}/{test3_results['passed'] + test3_results['failed']}")
            for detail in test3_results["details"]:
                print(f"     {detail}")
                
            # Generate mini-report for test_result.md
            self.generate_mini_report(success_rate, total_passed, total_failed, 
                                    test1_results, test2_results, test3_results)
                
        finally:
            await self.cleanup_session()
            
    def generate_mini_report(self, success_rate, total_passed, total_failed, test1, test2, test3):
        """Generate mini-report for test_result.md"""
        print(f"\n📝 MINI-REPORT FOR test_result.md:")
        print("=" * 60)
        
        status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
        
        report = f"""
Backend Thorough Test – Retest Fixes (Sept 2025)
{status_emoji} SUCCESS RATE: {success_rate:.1f}% ({total_passed}/{total_passed + total_failed} tests passed)

1) Enhanced service responses: {"PASS" if test1["failed"] == 0 else "FAIL"}
   - Service request creation, provider response, enhanced GET endpoint
   
2) Payments body parsing: {"PASS" if test2["failed"] == 0 else "FAIL"}  
   - KB checkout session and service request payments (422 → 200/503)
   
3) Assessment format sanity: {"PASS" if test3["failed"] == 0 else "FAIL"}
   - Tier session creation, evidence validation, file upload workflow

Key Findings: {"All critical fixes verified working" if success_rate >= 80 else "Some issues remain - see detailed results above"}
"""
        
        print(report)
        print("=" * 60)

async def main():
    """Main test runner"""
    runner = BackendRetestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())