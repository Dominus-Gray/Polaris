#!/usr/bin/env python3
"""
Debug JWT token validation issue
"""

import requests
import json

BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"

# Test login and token validation
login_data = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

print("🔍 Testing login...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token_data = response.json()
    print(f"Token data: {json.dumps(token_data, indent=2)}")
    
    if "access_token" in token_data:
        token = token_data["access_token"]
        print(f"Token length: {len(token)}")
        print(f"Token preview: {token[:50]}...")
        
        # Test token validation
        headers = {"Authorization": f"Bearer {token}"}
        print("\n🔍 Testing token validation...")
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Token validation status: {me_response.status_code}")
        print(f"Response: {me_response.text}")
        
        # Test with different header format
        print("\n🔍 Testing with different header format...")
        headers2 = {"Authorization": f"bearer {token}"}
        me_response2 = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
        print(f"Token validation status (lowercase): {me_response2.status_code}")
        print(f"Response: {me_response2.text}")
else:
    print(f"Login failed: {response.text}")