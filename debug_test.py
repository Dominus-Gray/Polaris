#!/usr/bin/env python3
"""
Debug test to check actual responses from Knowledge Base endpoints for providers
"""

import requests
import json

BACKEND_URL = "https://readiness-hub-2.preview.emergentagent.com/api"

PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

def test_provider_kb_access():
    # Authenticate provider
    response = requests.post(f"{BACKEND_URL}/auth/login", json=PROVIDER_CREDENTIALS)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing Provider Knowledge Base Access")
    print("=" * 50)
    
    # Test 1: KB Areas
    print("\n1. Testing /knowledge-base/areas")
    response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Response: {response.text}")
    
    # Test 2: Template Download
    print("\n2. Testing /knowledge-base/generate-template/area1/template")
    response = requests.get(f"{BACKEND_URL}/knowledge-base/generate-template/area1/template", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        print(f"Content length: {len(data.get('content', ''))}")
    else:
        print(f"Response: {response.text}")
    
    # Test 3: AI Assistance
    print("\n3. Testing /knowledge-base/ai-assistance")
    response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                           headers=headers,
                           json={"question": "How do I get started with business licensing?"})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
    else:
        print(f"Response: {response.text}")
    
    # Test 4: Check user role
    print("\n4. Testing /auth/me to verify role")
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"User role: {data.get('role')}")
        print(f"User email: {data.get('email')}")
    else:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_provider_kb_access()