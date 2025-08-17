#!/usr/bin/env python3
"""
Payment System Integration Testing for Polaris MVP
Tests all payment-related endpoints and integration flows as specified in review request
"""

import requests
import json
import uuid
import os
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://procurement-ready.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Payment Integration at: {API_BASE}")

class PaymentIntegrationTester:
    def __init__(self):
        self.client_token = None
        self.provider_token = None
        self.agency_token = None
        self.navigator_token = None
        self.test_results = {}
        
    def create_test_user(self, role="client", email_prefix="payment_test"):
        """Create a test user and return credentials"""
        print(f"\n=== Creating {role} test user ===")
        try:
            email = f"{email_prefix}_{role}_{uuid.uuid4().hex[:8]}@example.com"
            password = f"TestPass123!{role.title()}"
            
            payload = {
                "email": email,
                "password": password,
                "role": role,
                "terms_accepted": True
            }
            
            response = requests.post(
                f"{API_BASE}/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ {role.title()} user created: {email}")
                
                # Login to get token
                login_payload = {"email": email, "password": password}
                login_response = requests.post(
                    f"{API_BASE}/auth/login",
                    json=login_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    token = login_response.json().get('access_token')
                    print(f"✅ {role.title()} login successful")
                    return email, password, token
                else:
                    print(f"❌ {role.title()} login failed: {login_response.text}")
                    return None, None, None
            else:
                print(f"❌ {role.title()} registration failed: {response.text}")
                return None, None, None
                
        except Exception as e:
            print(f"❌ Error creating {role} user: {e}")
            return None, None, None

    def test_stripe_payment_session_creation(self):
        """Test POST /api/payments/v1/checkout/session for service requests"""
        print("\n=== Testing Stripe Payment Session Creation ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            # Test service request payment with correct payload structure
            payload = {
                "package_id": "service_request_medium",  # Use valid package ID
                "origin_url": BASE_URL,  # Required field
                "metadata": {
                    "description": "Business Formation Services",
                    "service_type": "business_formation"
                }
            }
            
            response = requests.post(
                f"{API_BASE}/payments/v1/checkout/session",
                json=payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Payment session response: {json.dumps(data, indent=2)}")
                
                # Verify required fields (updated for actual API response)
                required_fields = ['session_id', 'url']  # API returns 'url' not 'checkout_url'
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ PASS: Stripe payment session created successfully")
                    print(f"Session ID: {data.get('session_id')}")
                    print(f"Checkout URL: {data.get('url')}")
                    return data.get('session_id')
                else:
                    print(f"❌ FAIL: Missing required fields: {missing_fields}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_knowledge_base_payment_session(self):
        """Test POST /api/payments/knowledge-base for knowledge base unlock"""
        print("\n=== Testing Knowledge Base Payment Session ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "package_id": "knowledge_base_all",  # Use valid package ID
                "origin_url": BASE_URL,  # Required field
                "metadata": {
                    "unlock_type": "all_areas"
                }
            }
            
            response = requests.post(
                f"{API_BASE}/payments/knowledge-base",
                json=payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Knowledge base payment response: {json.dumps(data, indent=2)}")
                
                if 'session_id' in data and 'url' in data:  # API returns 'url' not 'checkout_url'
                    print("✅ PASS: Knowledge base payment session created")
                    return data.get('session_id')
                else:
                    print(f"❌ FAIL: Missing session_id or url: {data}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_payment_status_checking(self, session_id):
        """Test GET /api/payments/v1/checkout/status/{session_id}"""
        print("\n=== Testing Payment Status Checking ===")
        try:
            if not session_id:
                print("❌ SKIP: No session ID available")
                return False
                
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{API_BASE}/payments/v1/checkout/status/{session_id}",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Payment status response: {json.dumps(data, indent=2)}")
                
                # Verify required fields
                required_fields = ['status', 'payment_status']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ PASS: Payment status retrieved successfully")
                    print(f"Status: {data.get('status')}")
                    print(f"Payment Status: {data.get('payment_status')}")
                    return True
                else:
                    print(f"❌ FAIL: Missing required fields: {missing_fields}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_stripe_webhook_processing(self):
        """Test POST /api/webhook/stripe"""
        print("\n=== Testing Stripe Webhook Processing ===")
        try:
            # Simulate a Stripe webhook payload
            webhook_payload = {
                "id": f"evt_{uuid.uuid4().hex}",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": f"cs_{uuid.uuid4().hex}",
                        "object": "checkout.session",
                        "payment_status": "paid",
                        "amount_total": 150000,  # $1500.00 in cents
                        "metadata": {
                            "user_id": str(uuid.uuid4()),
                            "package_type": "service_request"
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{API_BASE}/webhook/stripe",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Webhook response: {json.dumps(data, indent=2)}")
                
                if data.get('status') == 'processed':
                    print("✅ PASS: Stripe webhook processed successfully")
                    return True
                else:
                    print(f"❌ FAIL: Unexpected webhook response: {data}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_knowledge_base_access_control(self):
        """Test GET /api/knowledge-base/access"""
        print("\n=== Testing Knowledge Base Access Control ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{API_BASE}/knowledge-base/access",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Knowledge base access response: {json.dumps(data, indent=2)}")
                
                # Verify required fields
                required_fields = ['has_all_access', 'unlocked_areas', 'available_packages']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ PASS: Knowledge base access control working")
                    print(f"Has all access: {data.get('has_all_access')}")
                    print(f"Unlocked areas: {len(data.get('unlocked_areas', []))}")
                    print(f"Available packages: {len(data.get('available_packages', []))}")
                    return True
                else:
                    print(f"❌ FAIL: Missing required fields: {missing_fields}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_knowledge_base_content_access(self):
        """Test GET /api/knowledge-base/{area_id}/content with access control"""
        print("\n=== Testing Knowledge Base Content Access ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            # Test with a sample area ID
            area_id = "business_formation"
            response = requests.get(
                f"{API_BASE}/knowledge-base/{area_id}/content",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Knowledge base content response: {json.dumps(data, indent=2)}")
                
                # Verify access control fields
                if 'has_access' in data and 'unlock_required' in data:
                    print("✅ PASS: Knowledge base content access control working")
                    print(f"Has access: {data.get('has_access')}")
                    print(f"Unlock required: {data.get('unlock_required')}")
                    return True
                else:
                    print(f"❌ FAIL: Missing access control fields: {data}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_service_request_creation(self):
        """Test service request creation and provider matching"""
        print("\n=== Testing Service Request Creation ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "budget": 1500,
                "payment_pref": "card",
                "timeline": "2 weeks",
                "area_id": "area1",  # Business Formation
                "description": "Need help with business registration and compliance setup"
            }
            
            response = requests.post(
                f"{API_BASE}/match/request",  # Correct endpoint
                json=payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Service request response: {json.dumps(data, indent=2)}")
                
                if 'request_id' in data:
                    print("✅ PASS: Service request created successfully")
                    return data.get('request_id')
                else:
                    print(f"❌ FAIL: Missing request_id: {data}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_service_engagement_tracking(self):
        """Test GET /api/engagements/my-services"""
        print("\n=== Testing Service Engagement Tracking ===")
        try:
            if not self.client_token:
                print("❌ SKIP: No client token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.client_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{API_BASE}/engagements/my-services",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Service engagements response: {json.dumps(data, indent=2)}")
                
                if 'engagements' in data:
                    print("✅ PASS: Service engagement tracking working")
                    print(f"Number of engagements: {len(data.get('engagements', []))}")
                    return True
                else:
                    print(f"❌ FAIL: Missing engagements field: {data}")
                    return False
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_role_based_access_control(self):
        """Test role-based access control for different endpoints"""
        print("\n=== Testing Role-Based Access Control ===")
        
        test_results = {}
        
        # Test client access to client-specific endpoints
        if self.client_token:
            print("\n--- Testing Client Access ---")
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Client should access knowledge base
            response = requests.get(f"{API_BASE}/knowledge-base/access", headers=headers)
            test_results['client_knowledge_base'] = response.status_code == 200
            print(f"Client knowledge base access: {response.status_code}")
            
            # Client should access service engagements
            response = requests.get(f"{API_BASE}/engagements/my-services", headers=headers)
            test_results['client_engagements'] = response.status_code == 200
            print(f"Client engagements access: {response.status_code}")
        
        # Test provider access (if available)
        if self.provider_token:
            print("\n--- Testing Provider Access ---")
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            
            # Provider should access provider-specific endpoints
            response = requests.get(f"{API_BASE}/provider/profile/me", headers=headers)
            test_results['provider_profile'] = response.status_code in [200, 404]  # 404 OK if no profile
            print(f"Provider profile access: {response.status_code}")
        
        # Test agency access (if available)
        if self.agency_token:
            print("\n--- Testing Agency Access ---")
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            
            # Agency should access agency-specific endpoints
            response = requests.get(f"{API_BASE}/agency/opportunities", headers=headers)
            test_results['agency_opportunities'] = response.status_code == 200
            print(f"Agency opportunities access: {response.status_code}")
        
        # Test unauthorized access
        print("\n--- Testing Unauthorized Access ---")
        # No token should return 401
        response = requests.get(f"{API_BASE}/knowledge-base/access")
        test_results['unauthorized_access'] = response.status_code == 401
        print(f"Unauthorized access (should be 401): {response.status_code}")
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        if passed_tests == total_tests:
            print(f"✅ PASS: Role-based access control working ({passed_tests}/{total_tests})")
            return True
        else:
            print(f"❌ FAIL: Role-based access control issues ({passed_tests}/{total_tests})")
            return False

    def test_authentication_requirements(self):
        """Test that endpoints properly require authentication"""
        print("\n=== Testing Authentication Requirements ===")
        
        protected_endpoints = [
            ("/payments/v1/checkout/session", "POST"),
            ("/payments/knowledge-base", "POST"),
            ("/knowledge-base/access", "GET"),
            ("/engagements/my-services", "GET"),
            ("/match/request", "POST"),  # Correct endpoint
        ]
        
        passed = 0
        total = len(protected_endpoints)
        
        for endpoint, method in protected_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_BASE}{endpoint}")
                else:
                    response = requests.post(f"{API_BASE}{endpoint}", json={})
                
                if response.status_code == 401:
                    print(f"✅ {method} {endpoint}: Properly requires authentication (401)")
                    passed += 1
                else:
                    print(f"❌ {method} {endpoint}: Should require authentication, got {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {method} {endpoint}: Error testing - {e}")
        
        if passed == total:
            print(f"✅ PASS: All endpoints properly require authentication ({passed}/{total})")
            return True
        else:
            print(f"❌ FAIL: Some endpoints don't require authentication ({passed}/{total})")
            return False

    def test_error_handling_and_validation(self):
        """Test proper error responses for invalid inputs"""
        print("\n=== Testing Error Handling and Validation ===")
        
        if not self.client_token:
            print("❌ SKIP: No client token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.client_token}",
            "Content-Type": "application/json"
        }
        
        test_results = {}
        
        # Test invalid payment session creation
        print("\n--- Testing Invalid Payment Session ---")
        invalid_payload = {
            "package_type": "invalid_package",
            "amount": -100  # Invalid negative amount
        }
        
        response = requests.post(
            f"{API_BASE}/payments/v1/checkout/session",
            json=invalid_payload,
            headers=headers
        )
        
        test_results['invalid_payment'] = response.status_code in [400, 422]
        print(f"Invalid payment session (should be 400/422): {response.status_code}")
        
        # Test invalid knowledge base area
        print("\n--- Testing Invalid Knowledge Base Area ---")
        response = requests.get(
            f"{API_BASE}/knowledge-base/nonexistent_area/content",
            headers=headers
        )
        
        test_results['invalid_kb_area'] = response.status_code in [404, 400]
        print(f"Invalid KB area (should be 404/400): {response.status_code}")
        
        # Test invalid payment status check
        print("\n--- Testing Invalid Payment Status ---")
        response = requests.get(
            f"{API_BASE}/payments/v1/checkout/status/invalid_session_id",
            headers=headers
        )
        
        test_results['invalid_payment_status'] = response.status_code in [404, 400]
        print(f"Invalid payment status (should be 404/400): {response.status_code}")
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        if passed_tests == total_tests:
            print(f"✅ PASS: Error handling working properly ({passed_tests}/{total_tests})")
            return True
        else:
            print(f"❌ FAIL: Error handling issues ({passed_tests}/{total_tests})")
            return False

    def run_comprehensive_payment_tests(self):
        """Run all payment integration tests"""
        print("🚀 Starting Comprehensive Payment Integration Tests")
        print(f"Base URL: {API_BASE}")
        print("="*80)
        
        # Setup test users
        print("\n📋 SETTING UP TEST USERS")
        print("="*40)
        
        client_email, client_password, self.client_token = self.create_test_user("client", "payment_client")
        provider_email, provider_password, self.provider_token = self.create_test_user("provider", "payment_provider")
        agency_email, agency_password, self.agency_token = self.create_test_user("agency", "payment_agency")
        navigator_email, navigator_password, self.navigator_token = self.create_test_user("navigator", "payment_navigator")
        
        if not self.client_token:
            print("❌ CRITICAL: Could not create client user - aborting payment tests")
            return False
        
        # Run payment system tests
        print("\n💳 PAYMENT SYSTEM INTEGRATION TESTS")
        print("="*50)
        
        # 1. Test Stripe payment session creation
        session_id = self.test_stripe_payment_session_creation()
        self.test_results['stripe_session_creation'] = session_id is not False
        
        # 2. Test knowledge base payment session
        kb_session_id = self.test_knowledge_base_payment_session()
        self.test_results['kb_payment_session'] = kb_session_id is not False
        
        # 3. Test payment status checking
        if session_id:
            self.test_results['payment_status_check'] = self.test_payment_status_checking(session_id)
        else:
            self.test_results['payment_status_check'] = False
        
        # 4. Test Stripe webhook processing
        self.test_results['stripe_webhook'] = self.test_stripe_webhook_processing()
        
        # Run knowledge base tests
        print("\n📚 KNOWLEDGE BASE SYSTEM TESTS")
        print("="*40)
        
        # 5. Test knowledge base access control
        self.test_results['kb_access_control'] = self.test_knowledge_base_access_control()
        
        # 6. Test knowledge base content access
        self.test_results['kb_content_access'] = self.test_knowledge_base_content_access()
        
        # Run service request tests
        print("\n🔧 SERVICE REQUEST FLOW TESTS")
        print("="*35)
        
        # 7. Test service request creation
        request_id = self.test_service_request_creation()
        self.test_results['service_request_creation'] = request_id is not False
        
        # 8. Test service engagement tracking
        self.test_results['service_engagement_tracking'] = self.test_service_engagement_tracking()
        
        # Run authentication and security tests
        print("\n🔐 AUTHENTICATION & SECURITY TESTS")
        print("="*45)
        
        # 9. Test role-based access control
        self.test_results['role_based_access'] = self.test_role_based_access_control()
        
        # 10. Test authentication requirements
        self.test_results['auth_requirements'] = self.test_authentication_requirements()
        
        # 11. Test error handling and validation
        self.test_results['error_handling'] = self.test_error_handling_and_validation()
        
        # Generate summary
        self.generate_test_summary()
        
        return self.calculate_overall_success()

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE PAYMENT INTEGRATION TEST SUMMARY")
        print("="*80)
        
        # Group tests by category
        payment_tests = [
            ('stripe_session_creation', 'Stripe Payment Session Creation'),
            ('kb_payment_session', 'Knowledge Base Payment Session'),
            ('payment_status_check', 'Payment Status Checking'),
            ('stripe_webhook', 'Stripe Webhook Processing')
        ]
        
        knowledge_base_tests = [
            ('kb_access_control', 'Knowledge Base Access Control'),
            ('kb_content_access', 'Knowledge Base Content Access')
        ]
        
        service_tests = [
            ('service_request_creation', 'Service Request Creation'),
            ('service_engagement_tracking', 'Service Engagement Tracking')
        ]
        
        security_tests = [
            ('role_based_access', 'Role-Based Access Control'),
            ('auth_requirements', 'Authentication Requirements'),
            ('error_handling', 'Error Handling & Validation')
        ]
        
        def print_category_results(category_name, tests):
            print(f"\n{category_name}:")
            passed = 0
            for test_key, test_name in tests:
                if test_key in self.test_results:
                    status = "✅ PASS" if self.test_results[test_key] else "❌ FAIL"
                    print(f"  {test_name}: {status}")
                    if self.test_results[test_key]:
                        passed += 1
                else:
                    print(f"  {test_name}: ⚠️  NOT RUN")
            return passed, len(tests)
        
        # Print results by category
        total_passed = 0
        total_tests = 0
        
        payment_passed, payment_total = print_category_results("💳 PAYMENT SYSTEM INTEGRATION", payment_tests)
        kb_passed, kb_total = print_category_results("📚 KNOWLEDGE BASE SYSTEM", knowledge_base_tests)
        service_passed, service_total = print_category_results("🔧 SERVICE REQUEST FLOW", service_tests)
        security_passed, security_total = print_category_results("🔐 AUTHENTICATION & SECURITY", security_tests)
        
        total_passed = payment_passed + kb_passed + service_passed + security_passed
        total_tests = payment_total + kb_total + service_total + security_total
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"  Payment System: {payment_passed}/{payment_total} tests passed")
        print(f"  Knowledge Base: {kb_passed}/{kb_total} tests passed")
        print(f"  Service Requests: {service_passed}/{service_total} tests passed")
        print(f"  Security: {security_passed}/{security_total} tests passed")
        print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"  SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Payment integration system is working very well!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Payment integration system is mostly working with minor issues")
        elif success_rate >= 50:
            print("\n⚠️  MODERATE: Payment integration system has significant issues")
        else:
            print("\n❌ CRITICAL: Payment integration system has major problems")

    def calculate_overall_success(self):
        """Calculate overall test success"""
        if not self.test_results:
            return False
            
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        return passed >= (total * 0.75)  # 75% pass rate required

def main():
    """Main test execution"""
    tester = PaymentIntegrationTester()
    success = tester.run_comprehensive_payment_tests()
    
    if success:
        print("\n🎉 Payment integration testing completed successfully!")
        return True
    else:
        print("\n⚠️  Payment integration testing completed with issues")
        return False

if __name__ == "__main__":
    main()