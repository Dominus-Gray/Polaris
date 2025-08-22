#!/usr/bin/env python3
"""
Focused Payment Integration Test - Testing Core Review Request Requirements
"""

import requests
import json
import uuid
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://frontend-sync-3.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Core Payment Integration at: {API_BASE}")

def create_test_user(role="client"):
    """Create a test user and return token"""
    try:
        email = f"focused_test_{role}_{uuid.uuid4().hex[:8]}@example.com"
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
            # Login to get token
            login_payload = {"email": email, "password": password}
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print(f"✅ Created {role} user: {email}")
                return email, token
            else:
                print(f"❌ {role.title()} login failed: {login_response.text}")
                return None, None
        else:
            print(f"❌ {role.title()} registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating {role} user: {e}")
        return None, None

def test_core_payment_integration():
    """Test the core payment integration requirements from review request"""
    print("\n" + "="*80)
    print("🎯 FOCUSED PAYMENT INTEGRATION TEST - REVIEW REQUEST REQUIREMENTS")
    print("="*80)
    
    results = {}
    
    # 1. Create test client
    print("\n📋 SETTING UP TEST CLIENT")
    client_email, client_token = create_test_user("client")
    if not client_token:
        print("❌ CRITICAL: Could not create client user")
        return False
    
    headers = {
        "Authorization": f"Bearer {client_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test Stripe Payment Session Creation for Service Requests
    print("\n💳 TESTING STRIPE PAYMENT ENDPOINTS")
    print("-" * 50)
    
    print("Testing service request payment session creation...")
    service_payload = {
        "package_id": "service_request_medium",
        "origin_url": BASE_URL,
        "metadata": {"service_type": "business_formation"}
    }
    
    response = requests.post(f"{API_BASE}/payments/v1/checkout/session", json=service_payload, headers=headers)
    service_session_success = response.status_code == 200
    results['service_payment_session'] = service_session_success
    
    if service_session_success:
        service_session_data = response.json()
        service_session_id = service_session_data.get('session_id')
        print(f"✅ Service payment session created: {service_session_id}")
    else:
        print(f"❌ Service payment session failed: {response.status_code} - {response.text}")
        service_session_id = None
    
    # 3. Test Knowledge Base Payment Session
    print("\nTesting knowledge base payment session creation...")
    kb_payload = {
        "package_id": "knowledge_base_all",
        "origin_url": BASE_URL,
        "metadata": {"unlock_type": "all_areas"}
    }
    
    response = requests.post(f"{API_BASE}/payments/knowledge-base", json=kb_payload, headers=headers)
    kb_session_success = response.status_code == 200
    results['kb_payment_session'] = kb_session_success
    
    if kb_session_success:
        kb_session_data = response.json()
        kb_session_id = kb_session_data.get('session_id')
        print(f"✅ Knowledge base payment session created: {kb_session_id}")
    else:
        print(f"❌ Knowledge base payment session failed: {response.status_code} - {response.text}")
        kb_session_id = None
    
    # 4. Test Payment Status Checking
    print("\nTesting payment status checking...")
    if service_session_id:
        response = requests.get(f"{API_BASE}/payments/v1/checkout/status/{service_session_id}", headers=headers)
        status_check_success = response.status_code == 200
        results['payment_status_check'] = status_check_success
        
        if status_check_success:
            status_data = response.json()
            print(f"✅ Payment status retrieved: {status_data.get('payment_status')}")
        else:
            print(f"❌ Payment status check failed: {response.status_code} - {response.text}")
    else:
        results['payment_status_check'] = False
        print("❌ Payment status check skipped - no session ID")
    
    # 5. Test Stripe Webhook Processing
    print("\nTesting Stripe webhook processing...")
    webhook_payload = {
        "id": f"evt_{uuid.uuid4().hex}",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_{uuid.uuid4().hex}",
                "object": "checkout.session",
                "payment_status": "paid",
                "amount_total": 150000,
                "metadata": {"user_id": str(uuid.uuid4()), "package_type": "service_request"}
            }
        }
    }
    
    response = requests.post(f"{API_BASE}/webhook/stripe", json=webhook_payload)
    webhook_success = response.status_code == 200 and response.json().get('status') == 'processed'
    results['stripe_webhook'] = webhook_success
    
    if webhook_success:
        print("✅ Stripe webhook processed successfully")
    else:
        print(f"❌ Stripe webhook failed: {response.status_code} - {response.text}")
    
    # 6. Test Knowledge Base Access Control
    print("\n📚 TESTING KNOWLEDGE BASE SYSTEM")
    print("-" * 40)
    
    print("Testing knowledge base access control...")
    response = requests.get(f"{API_BASE}/knowledge-base/access", headers=headers)
    kb_access_success = response.status_code == 200
    results['kb_access_control'] = kb_access_success
    
    if kb_access_success:
        access_data = response.json()
        print(f"✅ Knowledge base access retrieved: {access_data.get('has_all_access')}")
        print(f"   Available packages: {len(access_data.get('available_packages', {}))}")
    else:
        print(f"❌ Knowledge base access failed: {response.status_code} - {response.text}")
    
    # 7. Test Knowledge Base Content Access with Access Control
    print("\nTesting knowledge base content access control...")
    response = requests.get(f"{API_BASE}/knowledge-base/business_formation/content", headers=headers)
    kb_content_success = response.status_code == 200
    results['kb_content_access'] = kb_content_success
    
    if kb_content_success:
        content_data = response.json()
        print(f"✅ Knowledge base content access: has_access={content_data.get('has_access')}, unlock_required={content_data.get('unlock_required')}")
    else:
        print(f"❌ Knowledge base content access failed: {response.status_code} - {response.text}")
    
    # 8. Test Service Request Creation and Provider Matching
    print("\n🔧 TESTING SERVICE REQUEST FLOW")
    print("-" * 35)
    
    print("Testing service request creation...")
    service_request_payload = {
        "budget": 1500,
        "payment_pref": "card",
        "timeline": "2 weeks",
        "area_id": "area1",
        "description": "Need business formation assistance"
    }
    
    response = requests.post(f"{API_BASE}/match/request", json=service_request_payload, headers=headers)
    service_request_success = response.status_code == 200
    results['service_request_creation'] = service_request_success
    
    if service_request_success:
        request_data = response.json()
        request_id = request_data.get('request_id')
        print(f"✅ Service request created: {request_id}")
    else:
        print(f"❌ Service request creation failed: {response.status_code} - {response.text}")
    
    # 9. Test Service Engagement Tracking
    print("\nTesting service engagement tracking...")
    response = requests.get(f"{API_BASE}/engagements/my-services", headers=headers)
    engagement_tracking_success = response.status_code == 200
    results['engagement_tracking'] = engagement_tracking_success
    
    if engagement_tracking_success:
        engagement_data = response.json()
        print(f"✅ Service engagements retrieved: {len(engagement_data.get('engagements', []))} engagements")
    else:
        print(f"❌ Service engagement tracking failed: {response.status_code} - {response.text}")
    
    # 10. Test Authentication Requirements
    print("\n🔐 TESTING AUTHENTICATION & SECURITY")
    print("-" * 45)
    
    print("Testing authentication requirements...")
    auth_test_endpoints = [
        ("/payments/v1/checkout/session", "POST"),
        ("/knowledge-base/access", "GET"),
        ("/match/request", "POST")
    ]
    
    auth_passed = 0
    for endpoint, method in auth_test_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}")
            else:
                response = requests.post(f"{API_BASE}{endpoint}", json={})
            
            if response.status_code == 401:
                auth_passed += 1
                print(f"✅ {method} {endpoint}: Requires authentication (401)")
            else:
                print(f"❌ {method} {endpoint}: Should require auth, got {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")
    
    results['auth_requirements'] = auth_passed == len(auth_test_endpoints)
    
    # 11. Test Role-Based Access Control
    print("\nTesting role-based access control...")
    
    # Test client access to client endpoints
    client_endpoints_passed = 0
    client_test_endpoints = [
        ("/knowledge-base/access", "GET"),
        ("/engagements/my-services", "GET")
    ]
    
    for endpoint, method in client_test_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", json={}, headers=headers)
            
            if response.status_code == 200:
                client_endpoints_passed += 1
                print(f"✅ Client access to {endpoint}: Allowed (200)")
            else:
                print(f"❌ Client access to {endpoint}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ Client access to {endpoint}: Error - {e}")
    
    results['role_based_access'] = client_endpoints_passed == len(client_test_endpoints)
    
    # Generate Summary
    print("\n" + "="*80)
    print("📊 FOCUSED PAYMENT INTEGRATION TEST RESULTS")
    print("="*80)
    
    categories = {
        "💳 PAYMENT SYSTEM INTEGRATION": [
            ('service_payment_session', 'Service Request Payment Session'),
            ('kb_payment_session', 'Knowledge Base Payment Session'),
            ('payment_status_check', 'Payment Status Checking'),
            ('stripe_webhook', 'Stripe Webhook Processing')
        ],
        "📚 KNOWLEDGE BASE SYSTEM": [
            ('kb_access_control', 'Knowledge Base Access Control'),
            ('kb_content_access', 'Knowledge Base Content Access')
        ],
        "🔧 SERVICE REQUEST FLOW": [
            ('service_request_creation', 'Service Request Creation'),
            ('engagement_tracking', 'Service Engagement Tracking')
        ],
        "🔐 AUTHENTICATION & SECURITY": [
            ('auth_requirements', 'Authentication Requirements'),
            ('role_based_access', 'Role-Based Access Control')
        ]
    }
    
    total_passed = 0
    total_tests = 0
    
    for category_name, tests in categories.items():
        print(f"\n{category_name}:")
        category_passed = 0
        for test_key, test_name in tests:
            if test_key in results:
                status = "✅ PASS" if results[test_key] else "❌ FAIL"
                print(f"  {test_name}: {status}")
                if results[test_key]:
                    category_passed += 1
                    total_passed += 1
                total_tests += 1
            else:
                print(f"  {test_name}: ⚠️  NOT RUN")
        
        print(f"  Category Score: {category_passed}/{len(tests)}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 OVERALL RESULTS:")
    print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
    print(f"  SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT: Payment integration system is working very well!")
        return True
    elif success_rate >= 75:
        print("\n✅ GOOD: Payment integration system is mostly working with minor issues")
        return True
    elif success_rate >= 50:
        print("\n⚠️  MODERATE: Payment integration system has significant issues")
        return False
    else:
        print("\n❌ CRITICAL: Payment integration system has major problems")
        return False

if __name__ == "__main__":
    success = test_core_payment_integration()
    if success:
        print("\n🎉 Focused payment integration testing completed successfully!")
    else:
        print("\n⚠️  Focused payment integration testing completed with issues")