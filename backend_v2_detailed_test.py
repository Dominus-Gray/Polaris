#!/usr/bin/env python3
"""
Backend V2 Detailed Response Test
Get detailed response bodies for successful V2 endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
}

def authenticate(role):
    """Authenticate and get token"""
    try:
        creds = QA_CREDENTIALS[role]
        response = requests.post(f"{BACKEND_URL}/auth/login", json=creds, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"Bearer {data.get('access_token')}"
    except Exception as e:
        print(f"Auth error for {role}: {e}")
    return None

def make_request(method, endpoint, token=None, json_data=None, params=None):
    """Make authenticated request"""
    headers = {}
    if token:
        headers["Authorization"] = token
    
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=json_data, timeout=10)
        return response
    except Exception as e:
        print(f"Request error: {e}")
        return None

def main():
    print("🔍 Getting Detailed V2 Endpoint Responses")
    
    # Authenticate
    agency_token = authenticate("agency")
    client_token = authenticate("client")
    
    if not (agency_token and client_token):
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test each endpoint with detailed output
    tests = [
        ("POST", "/v2/matching/search-by-zip", client_token, {"zip": "78205", "radius_miles": 50}, None),
        ("POST", "/v2/rp/requirements", agency_token, {"rp_type": "bank", "required_fields": ["business_name", "tax_id", "annual_revenue", "years_in_business"]}, None),
        ("GET", "/v2/rp/requirements", client_token, None, {"rp_type": "bank"}),
        ("GET", "/v2/rp/package-preview", client_token, None, {"rp_type": "bank"}),
        ("POST", "/v2/rp/leads", client_token, {"rp_type": "bank"}, None),
        ("GET", "/v2/rp/leads", client_token, None, None),
        ("GET", "/v2/rp/leads", agency_token, None, None)
    ]
    
    for method, endpoint, token, json_data, params in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {method} {endpoint}")
        print(f"{'='*60}")
        
        response = make_request(method, endpoint, token, json_data, params)
        
        if response:
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"Response Body:")
                print(json.dumps(data, indent=2, default=str))
            except:
                print(f"Raw Response: {response.text}")
        else:
            print("❌ Request failed")

if __name__ == "__main__":
    main()