#!/usr/bin/env python3
"""
Focused Payment Bug Fix Testing
Re-run focused backend checks after the bugfix as per review request:
1) Login as existing client and provider created in previous test (do not re-create)
2) Create a fresh service request via POST /api/service-requests/professional-help (area5)
3) As provider respond to this new request via POST /api/provider/respond-to-request
4) As client, call POST /api/payments/service-request with the new request_id, provider_id from response, agreed_fee=1500, origin_url='https://polaris-sbap-2.preview.emergentagent.com'
5) Expect 503 Service unavailable due to Stripe, but confirm the endpoint passes validation
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing payment bugfix at: {API_BASE}")

# Working credentials from previous tests (do not re-create)
CLIENT_EMAIL = "client_5ffe6e03@cybersec.com"
CLIENT_PASSWORD = "ClientPass123!"
PROVIDER_EMAIL = "provider_f24e4887@techsolutions.com"
PROVIDER_PASSWORD = "ProviderPass123!"

def get_auth_token(email, password, role):
    """Get authentication token for user"""
    print(f"\n=== Getting {role} token ===")
    try:
        payload = {"email": email, "password": password}
        response = requests.post(f"{API_BASE}/auth/login", json=payload)
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ {role} token obtained")
            return token
        else:
            print(f"❌ {role} login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERROR getting {role} token: {e}")
        return None

def create_service_request(client_token):
    """Create a fresh service request via POST /api/service-requests/professional-help (area5)"""
    print("\n=== Creating Service Request (area5) ===")
    try:
        payload = {
            "area_id": "area5",  # Technology & Security Infrastructure
            "description": "Need cybersecurity assessment and implementation for government contracting readiness",
            "budget_range": "$1000-$2000",
            "timeline": "2-4 weeks",
            "requirements": ["Security audit", "Compliance documentation", "Staff training"]
        }
        
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{API_BASE}/service-requests/professional-help", json=payload, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            if request_id:
                print(f"✅ Service request created: {request_id}")
                return request_id
            else:
                print("❌ No request_id in response")
                return None
        else:
            print(f"❌ Service request creation failed")
            return None
    except Exception as e:
        print(f"❌ ERROR creating service request: {e}")
        return None

def provider_respond_to_request(provider_token, request_id):
    """As provider respond to the new request via POST /api/provider/respond-to-request"""
    print(f"\n=== Provider Responding to Request {request_id} ===")
    try:
        payload = {
            "request_id": request_id,
            "proposed_fee": 1500,
            "proposal_note": "Comprehensive cybersecurity assessment and implementation package including security audit, compliance documentation, and staff training for government contracting readiness.",
            "estimated_timeline": "3 weeks",
            "deliverables": ["Security assessment report", "Compliance documentation", "Staff training materials", "Implementation plan"]
        }
        
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.post(f"{API_BASE}/provider/respond-to-request", json=payload, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            provider_id = data.get('provider_id')
            if provider_id:
                print(f"✅ Provider response submitted: {provider_id}")
                return provider_id
            else:
                print("✅ Provider response submitted (no provider_id in response)")
                # Try to get provider_id from the response data
                return data.get('response_id') or 'provider_response_success'
        else:
            print(f"❌ Provider response failed")
            return None
    except Exception as e:
        print(f"❌ ERROR in provider response: {e}")
        return None

def get_provider_id_from_user(provider_token):
    """Get provider user ID from auth/me endpoint"""
    print("\n=== Getting Provider User ID ===")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            provider_id = data.get('id')
            print(f"✅ Provider ID obtained: {provider_id}")
            return provider_id
        else:
            print(f"❌ Failed to get provider ID: {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERROR getting provider ID: {e}")
        return None

def test_payment_endpoint(client_token, request_id, provider_id):
    """Test POST /api/payments/service-request - expect 503 but confirm validation passes"""
    print(f"\n=== Testing Payment Endpoint ===")
    print(f"Request ID: {request_id}")
    print(f"Provider ID: {provider_id}")
    
    try:
        payload = {
            "request_id": request_id,
            "provider_id": provider_id,
            "agreed_fee": 1500,
            "origin_url": "https://polaris-sbap-2.preview.emergentagent.com"
        }
        
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{API_BASE}/payments/service-request", json=payload, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Expected: 503 Service Unavailable due to Stripe, but validation should pass
        if response.status_code == 503:
            response_text = response.text.lower()
            if 'stripe' in response_text or 'service unavailable' in response_text:
                print("✅ PASS: Got expected 503 Service Unavailable due to Stripe")
                print("✅ PASS: Endpoint passed validation (reached Stripe check, not 404/403)")
                return True
            else:
                print(f"❌ FAIL: Got 503 but not due to Stripe: {response.text}")
                return False
        elif response.status_code == 404:
            print("❌ FAIL: Got 404 - endpoint validation failed (service request not found)")
            return False
        elif response.status_code == 403:
            print("❌ FAIL: Got 403 - endpoint validation failed (authorization issue)")
            return False
        elif response.status_code == 400:
            print(f"❌ FAIL: Got 400 - validation error: {response.text}")
            return False
        elif response.status_code == 200:
            print("✅ UNEXPECTED SUCCESS: Payment endpoint worked (Stripe might be available)")
            return True
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing payment endpoint: {e}")
        return False

def main():
    """Run the focused payment bugfix test"""
    print("=" * 60)
    print("FOCUSED PAYMENT BUGFIX TEST")
    print("=" * 60)
    
    results = []
    
    # Step 1: Login as existing client and provider
    print("\n1. Login as existing users (do not re-create)")
    client_token = get_auth_token(CLIENT_EMAIL, CLIENT_PASSWORD, "client")
    provider_token = get_auth_token(PROVIDER_EMAIL, PROVIDER_PASSWORD, "provider")
    
    if not client_token or not provider_token:
        print("❌ CRITICAL: Failed to login with existing credentials")
        return False
    
    results.append(("Login existing users", True))
    
    # Step 2: Create fresh service request (area5)
    print("\n2. Create fresh service request via POST /api/service-requests/professional-help (area5)")
    request_id = create_service_request(client_token)
    
    if not request_id:
        print("❌ CRITICAL: Failed to create service request")
        return False
    
    results.append(("Create service request (area5)", True))
    
    # Step 3: Provider respond to request
    print("\n3. Provider respond to request via POST /api/provider/respond-to-request")
    provider_response_id = provider_respond_to_request(provider_token, request_id)
    
    if not provider_response_id:
        print("❌ CRITICAL: Provider failed to respond to request")
        return False
    
    results.append(("Provider respond to request", True))
    
    # Get provider user ID for payment
    provider_id = get_provider_id_from_user(provider_token)
    if not provider_id:
        print("❌ CRITICAL: Failed to get provider ID")
        return False
    
    # Step 4: Test payment endpoint
    print("\n4. Test POST /api/payments/service-request (expect 503 but validation passes)")
    payment_test_passed = test_payment_endpoint(client_token, request_id, provider_id)
    
    results.append(("Payment endpoint validation", payment_test_passed))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Payment bugfix verification successful")
        print("✅ Service request creation works")
        print("✅ Provider response works") 
        print("✅ Payment endpoint passes validation (reaches Stripe check)")
    else:
        print("❌ SOME TESTS FAILED - Issues found in payment flow")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)