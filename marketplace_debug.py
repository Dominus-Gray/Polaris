#!/usr/bin/env python3
"""
Debug test to check marketplace endpoints
"""

import requests
import json

BACKEND_URL = "https://polaris-migrate.preview.emergentagent.com/api"

CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

def test_marketplace_endpoints():
    # Authenticate client
    response = requests.post(f"{BACKEND_URL}/auth/login", json=CLIENT_CREDENTIALS)
    if response.status_code != 200:
        print(f"❌ Client authentication failed: {response.status_code}")
        return
    
    client_token = response.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    
    # Authenticate provider
    response = requests.post(f"{BACKEND_URL}/auth/login", json=PROVIDER_CREDENTIALS)
    if response.status_code != 200:
        print(f"❌ Provider authentication failed: {response.status_code}")
        return
    
    provider_token = response.json()["access_token"]
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    
    print("🛒 Testing Marketplace Endpoints")
    print("=" * 50)
    
    # Test client endpoints
    print("\n📱 CLIENT ENDPOINTS:")
    
    endpoints_to_test = [
        "/service-requests",
        "/service-requests/my",
        "/engagements"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting GET {endpoint}")
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=client_headers)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text[:200]}")
    
    # Test provider endpoints
    print("\n👥 PROVIDER ENDPOINTS:")
    
    provider_endpoints = [
        "/provider/available-requests",
        "/provider/my-responses",
        "/provider/notifications"
    ]
    
    for endpoint in provider_endpoints:
        print(f"\nTesting GET {endpoint}")
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=provider_headers)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text[:200]}")

if __name__ == "__main__":
    test_marketplace_endpoints()