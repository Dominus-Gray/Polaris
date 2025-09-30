#!/usr/bin/env python3
"""
Debug specific failing endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

def authenticate_user(role):
    """Authenticate user and return token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=QA_CREDENTIALS[role],
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token') or data.get('access_token')
            print(f"✅ {role} authenticated: {len(token)} chars")
            return token
        else:
            print(f"❌ {role} auth failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ {role} auth error: {e}")
        return None

def test_endpoint(method, endpoint, token, data=None):
    """Test specific endpoint"""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=10)
        
        print(f"{method} {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.text[:200]}")
        else:
            print(f"  Success: {len(response.text)} chars")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"{method} {endpoint}: ERROR - {e}")
        return False

def main():
    print("🔍 DEBUGGING SPECIFIC FAILING ENDPOINTS")
    print("=" * 50)
    
    # Authenticate users
    client_token = authenticate_user('client')
    agency_token = authenticate_user('agency')
    
    if not client_token or not agency_token:
        print("❌ Authentication failed")
        return
    
    print("\n📊 Testing failing endpoints:")
    
    # Test 1: POST /assessment/tier-session
    print("\n1. Testing POST /assessment/tier-session")
    test_endpoint('POST', '/assessment/tier-session', client_token, {
        "area_id": "area1", 
        "tier_level": 1
    })
    
    # Test 2: GET /service-requests/my-requests  
    print("\n2. Testing GET /service-requests/my-requests")
    test_endpoint('GET', '/service-requests/my-requests', client_token)
    
    # Test 3: POST /agency/licenses/generate
    print("\n3. Testing POST /agency/licenses/generate")
    test_endpoint('POST', '/agency/licenses/generate', agency_token, {
        "quantity": 3, 
        "expires_days": 60
    })
    
    # Test 4: GET /analytics/dashboard
    print("\n4. Testing GET /analytics/dashboard")
    test_endpoint('GET', '/analytics/dashboard', client_token)
    
    # Test 5: POST /payments/checkout/session
    print("\n5. Testing POST /payments/checkout/session")
    test_endpoint('POST', '/payments/checkout/session', client_token, {
        "package_id": "knowledge_base_basic"
    })
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()