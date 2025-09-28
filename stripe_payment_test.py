#!/usr/bin/env python3
"""
Stripe Payment Integration Testing for Polaris MVP
Tests all payment-related endpoints as specified in the review request
"""

import requests
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://nextjs-mongo-polaris.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Stripe Payment Integration at: {API_BASE}")

def create_test_user(role="client"):
    """Create a test user and return authentication token"""
    print(f"\n=== Creating Test User ({role}) ===")
    try:
        # Generate unique email
        user_email = f"stripe_test_{role}_{uuid.uuid4().hex[:8]}@example.com"
        password = "StripeTest123!"
        
        # Register user
        register_payload = {
            "email": user_email,
            "password": password,
            "role": role,
            "terms_accepted": True
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: User registration failed - {response.text}")
            return None, None
        
        # Login user
        login_payload = {
            "email": user_email,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: User login failed - {response.text}")
            return None, None
        
        token = response.json().get('access_token')
        print(f"✅ PASS: Created and authenticated {role} user")
        return token, user_email
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def test_checkout_session_creation(client_token):
    """Test POST /api/payments/v1/checkout/session"""
    print("\n=== Testing Checkout Session Creation ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "package_id": "assessment_fee",
            "origin_url": "https://nextjs-mongo-polaris.preview.emergentagent.com",
            "metadata": {}
        }
        
        response = requests.post(
            f"{API_BASE}/payments/v1/checkout/session",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Checkout session response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['session_id', 'url']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Checkout session created with all required fields")
                return data.get('session_id'), data.get('session_id')
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return None, None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def test_checkout_status(stripe_session_id, client_token):
    """Test GET /api/payments/v1/checkout/status/{session_id}"""
    print("\n=== Testing Checkout Status ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/payments/v1/checkout/status/{stripe_session_id}", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Checkout status response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['status', 'payment_status', 'amount_total']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Checkout status retrieved with all required fields")
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

def test_service_request_payment(client_token):
    """Test POST /api/payments/service-request"""
    print("\n=== Testing Service Request Payment ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        # Use a dummy provider ID for testing (the endpoint will validate it exists)
        provider_id = str(uuid.uuid4())
        print(f"Using test provider ID: {provider_id}")

        
        # First create a match request
        print("Creating match request...")
        match_payload = {
            "budget": 1500,
            "payment_pref": "card",
            "timeline": "2 weeks",
            "area_id": "area1",
            "description": "Need business formation services"
        }
        
        match_response = requests.post(
            f"{API_BASE}/match/request",
            json=match_payload,
            headers=headers
        )
        
        if match_response.status_code != 200:
            print(f"❌ FAIL: Could not create match request - {match_response.text}")
            return None, None
        
        request_id = match_response.json().get('request_id')
        print(f"Created match request: {request_id}")
        
        # Now create service payment
        payload = {
            "request_id": request_id,
            "provider_id": provider_id,
            "agreed_fee": 1500.00,
            "origin_url": "https://nextjs-mongo-polaris.preview.emergentagent.com"
        }
        
        response = requests.post(
            f"{API_BASE}/payments/service-request",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Service request payment response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['session_id', 'url']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Service request payment created with all required fields")
                return request_id, data.get('session_id')
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return None, None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def test_knowledge_base_payment(client_token):
    """Test POST /api/payments/knowledge-base"""
    print("\n=== Testing Knowledge Base Payment ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "package_id": "knowledge_base_all",
            "origin_url": "https://nextjs-mongo-polaris.preview.emergentagent.com",
            "metadata": {}
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
            
            # Check required fields
            required_fields = ['session_id', 'url']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Knowledge base payment created with all required fields")
                return data.get('session_id'), data.get('session_id')
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return None, None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def test_stripe_webhook():
    """Test POST /api/webhook/stripe"""
    print("\n=== Testing Stripe Webhook ===")
    try:
        # Simulate a Stripe webhook payload
        webhook_payload = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_id",
                    "payment_status": "paid",
                    "amount_total": 9999,
                    "currency": "usd",
                    "metadata": {
                        "engagement_id": str(uuid.uuid4()),
                        "user_id": str(uuid.uuid4())
                    }
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Stripe-Signature": "t=1234567890,v1=test_signature"  # Mock signature
        }
        
        response = requests.post(
            f"{API_BASE}/webhook/stripe",
            json=webhook_payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Webhook response: {json.dumps(data, indent=2)}")
            
            if data.get('status') == 'processed':
                print("✅ PASS: Stripe webhook processed successfully")
                return True
            else:
                print(f"❌ FAIL: Webhook not properly processed: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def create_test_engagement(client_token):
    """Create a test engagement for testing"""
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        # Create engagement via the engagements/create endpoint
        payload = {
            "service_type": "business_formation",
            "description": "Test engagement for API testing",
            "budget": 1500.00,
            "timeline": "2 weeks"
        }
        
        response = requests.post(
            f"{API_BASE}/engagements/create",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('engagement_id')
        else:
            print(f"Could not create test engagement: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating test engagement: {e}")
        return None

def test_engagement_update(client_token, engagement_id):
    """Test POST /api/engagements/{engagement_id}/update"""
    print("\n=== Testing Engagement Update ===")
    if not engagement_id:
        # Try to create a test engagement
        engagement_id = create_test_engagement(client_token)
        if not engagement_id:
            print("⚠️  SKIP: No engagement ID available and could not create one")
            return False
        
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "status": "in_progress",
            "progress_percentage": 25,
            "notes": "Initial requirements gathering completed",
            "estimated_completion": "2025-02-15"
        }
        
        response = requests.post(
            f"{API_BASE}/engagements/{engagement_id}/update",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Engagement update response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ PASS: Engagement updated successfully")
                return True
            else:
                print(f"❌ FAIL: Engagement update failed: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_engagement_tracking(client_token, engagement_id):
    """Test GET /api/engagements/{engagement_id}/tracking"""
    print("\n=== Testing Engagement Tracking ===")
    if not engagement_id:
        # Try to create a test engagement
        engagement_id = create_test_engagement(client_token)
        if not engagement_id:
            print("⚠️  SKIP: No engagement ID available and could not create one")
            return False
        
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/engagements/{engagement_id}/tracking",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Engagement tracking response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['engagement_id', 'status_history', 'current_status']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Engagement tracking retrieved with all required fields")
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

def test_engagement_rating(client_token, engagement_id):
    """Test POST /api/engagements/{engagement_id}/rating"""
    print("\n=== Testing Engagement Rating ===")
    if not engagement_id:
        # Try to create a test engagement
        engagement_id = create_test_engagement(client_token)
        if not engagement_id:
            print("⚠️  SKIP: No engagement ID available and could not create one")
            return False
        
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "rating": 5,
            "feedback": "Excellent service! Very professional and thorough.",
            "would_recommend": True,
            "service_quality": 5,
            "communication": 5,
            "timeliness": 4
        }
        
        response = requests.post(
            f"{API_BASE}/engagements/{engagement_id}/rating",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Engagement rating response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ PASS: Engagement rating submitted successfully")
                return True
            else:
                print(f"❌ FAIL: Engagement rating failed: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_my_services(client_token):
    """Test GET /api/engagements/my-services"""
    print("\n=== Testing My Services ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/engagements/my-services",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"My services response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['engagements']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: My services retrieved with all required fields")
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

def test_knowledge_base_access(client_token):
    """Test GET /api/knowledge-base/access"""
    print("\n=== Testing Knowledge Base Access ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
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
            
            # Check required fields
            required_fields = ['has_all_access', 'unlocked_areas', 'available_packages']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Knowledge base access status retrieved with all required fields")
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

def test_knowledge_base_content(client_token):
    """Test GET /api/knowledge-base/{area_id}/content"""
    print("\n=== Testing Knowledge Base Content ===")
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
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
            
            # Check required fields - content is gated, so we expect has_access and unlock_required
            required_fields = ['has_access', 'unlock_required']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Knowledge base content properly gated with access control")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return False
        elif response.status_code == 403:
            print("✅ PASS: Knowledge base content properly gated (403 Forbidden)")
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_authentication_requirements():
    """Test that payment endpoints require proper authentication"""
    print("\n=== Testing Authentication Requirements ===")
    
    endpoints_to_test = [
        ("POST", "/payments/v1/checkout/session", {"package_type": "basic", "amount": 99.99}),
        ("POST", "/payments/service-request", {"service_type": "test", "amount": 100}),
        ("POST", "/payments/knowledge-base", {"access_type": "full", "amount": 49.99}),
        ("GET", "/engagements/my-services", None),
        ("GET", "/knowledge-base/access", None),
        ("GET", "/knowledge-base/test/content", None)
    ]
    
    passed_tests = 0
    total_tests = len(endpoints_to_test)
    
    for method, endpoint, payload in endpoints_to_test:
        try:
            if method == "POST":
                response = requests.post(
                    f"{API_BASE}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
            else:
                response = requests.get(f"{API_BASE}{endpoint}")
            
            if response.status_code == 401:
                print(f"✅ PASS: {method} {endpoint} requires authentication (401)")
                passed_tests += 1
            else:
                print(f"❌ FAIL: {method} {endpoint} should require authentication, got {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR testing {method} {endpoint}: {e}")
    
    print(f"Authentication tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests

def test_error_scenarios(client_token):
    """Test error handling scenarios"""
    print("\n=== Testing Error Scenarios ===")
    
    error_tests = []
    
    # Test invalid package type
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "package_id": "invalid_package",
            "origin_url": "https://nextjs-mongo-polaris.preview.emergentagent.com",
            "metadata": {}
        }
        
        response = requests.post(
            f"{API_BASE}/payments/v1/checkout/session",
            json=payload,
            headers=headers
        )
        
        if response.status_code in [400, 422]:
            print("✅ PASS: Invalid package type properly rejected")
            error_tests.append(True)
        else:
            print(f"❌ FAIL: Invalid package type should be rejected, got {response.status_code}")
            error_tests.append(False)
            
    except Exception as e:
        print(f"❌ ERROR testing invalid package: {e}")
        error_tests.append(False)
    
    # Test invalid session ID for status check
    try:
        response = requests.get(f"{API_BASE}/payments/v1/checkout/status/invalid_session_id")
        
        if response.status_code in [404, 400]:
            print("✅ PASS: Invalid session ID properly rejected")
            error_tests.append(True)
        else:
            print(f"❌ FAIL: Invalid session ID should be rejected, got {response.status_code}")
            error_tests.append(False)
            
    except Exception as e:
        print(f"❌ ERROR testing invalid session ID: {e}")
        error_tests.append(False)
    
    # Test invalid engagement ID
    try:
        response = requests.get(
            f"{API_BASE}/engagements/invalid_engagement_id/tracking",
            headers=headers
        )
        
        if response.status_code in [404, 400]:
            print("✅ PASS: Invalid engagement ID properly rejected")
            error_tests.append(True)
        else:
            print(f"❌ FAIL: Invalid engagement ID should be rejected, got {response.status_code}")
            error_tests.append(False)
            
    except Exception as e:
        print(f"❌ ERROR testing invalid engagement ID: {e}")
        error_tests.append(False)
    
    passed_error_tests = sum(error_tests)
    total_error_tests = len(error_tests)
    print(f"Error handling tests: {passed_error_tests}/{total_error_tests} passed")
    
    return passed_error_tests == total_error_tests

def main():
    """Run comprehensive Stripe payment integration tests"""
    print("🚀 Starting Stripe Payment Integration Tests")
    print(f"Base URL: {API_BASE}")
    print("="*60)
    
    results = {}
    
    # Create test user
    client_token, client_email = create_test_user("client")
    if not client_token:
        print("❌ CRITICAL: Cannot create test user, aborting tests")
        return False
    
    results['user_creation'] = True
    
    # Test 1: Payment System Endpoints
    print("\n" + "="*60)
    print("PAYMENT SYSTEM ENDPOINTS")
    print("="*60)
    
    # Test checkout session creation
    stripe_session_id, session_id = test_checkout_session_creation(client_token)
    results['checkout_session_creation'] = stripe_session_id is not None
    
    # Test checkout status
    if stripe_session_id:
        results['checkout_status'] = test_checkout_status(stripe_session_id, client_token)
    else:
        results['checkout_status'] = False
    
    # Test service request payment
    engagement_id, payment_session_id = test_service_request_payment(client_token)
    results['service_request_payment'] = engagement_id is not None
    
    # Test knowledge base payment
    access_id, kb_payment_session_id = test_knowledge_base_payment(client_token)
    results['knowledge_base_payment'] = access_id is not None
    
    # Test Stripe webhook
    results['stripe_webhook'] = test_stripe_webhook()
    
    # Test 2: Service Management Endpoints
    print("\n" + "="*60)
    print("SERVICE MANAGEMENT ENDPOINTS")
    print("="*60)
    
    # Test engagement update
    results['engagement_update'] = test_engagement_update(client_token, engagement_id)
    
    # Test engagement tracking
    results['engagement_tracking'] = test_engagement_tracking(client_token, engagement_id)
    
    # Test engagement rating
    results['engagement_rating'] = test_engagement_rating(client_token, engagement_id)
    
    # Test my services
    results['my_services'] = test_my_services(client_token)
    
    # Test 3: Knowledge Base Unlock
    print("\n" + "="*60)
    print("KNOWLEDGE BASE UNLOCK")
    print("="*60)
    
    # Test knowledge base access
    results['knowledge_base_access'] = test_knowledge_base_access(client_token)
    
    # Test knowledge base content
    results['knowledge_base_content'] = test_knowledge_base_content(client_token)
    
    # Test 4: Authentication & Security
    print("\n" + "="*60)
    print("AUTHENTICATION & SECURITY")
    print("="*60)
    
    results['authentication_requirements'] = test_authentication_requirements()
    
    # Test 5: Error Handling
    print("\n" + "="*60)
    print("ERROR HANDLING")
    print("="*60)
    
    results['error_scenarios'] = test_error_scenarios(client_token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 STRIPE PAYMENT INTEGRATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    # Group results by category
    payment_tests = ['checkout_session_creation', 'checkout_status', 'service_request_payment', 
                    'knowledge_base_payment', 'stripe_webhook']
    service_tests = ['engagement_update', 'engagement_tracking', 'engagement_rating', 'my_services']
    knowledge_tests = ['knowledge_base_access', 'knowledge_base_content']
    security_tests = ['authentication_requirements', 'error_scenarios']
    
    print("PAYMENT SYSTEM ENDPOINTS:")
    for test_name in payment_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\nSERVICE MANAGEMENT ENDPOINTS:")
    for test_name in service_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\nKNOWLEDGE BASE UNLOCK:")
    for test_name in knowledge_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\nAUTHENTICATION & SECURITY:")
    for test_name in security_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Stripe payment integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    main()