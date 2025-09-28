#!/usr/bin/env python3
"""
Simple Agency Endpoint Test - Check which endpoints are working
"""

import requests
import json

BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"
QA_AGENCY_EMAIL = "agency.qa@polaris.example.com"
QA_AGENCY_PASSWORD = "Polaris#2025!"

def get_agency_token():
    """Get agency authentication token"""
    login_data = {
        "email": QA_AGENCY_EMAIL,
        "password": QA_AGENCY_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_endpoint(endpoint, token, method='GET', data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        
        print(f"{method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Success: {type(data).__name__} with {len(data) if isinstance(data, (list, dict)) else 'data'}")
            except:
                print(f"  Success: Non-JSON response")
        elif response.status_code == 500:
            print(f"  Error: Internal Server Error")
        else:
            print(f"  Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error: {response.text[:100]}")
        
    except requests.exceptions.Timeout:
        print(f"{method} {endpoint}: TIMEOUT")
    except Exception as e:
        print(f"{method} {endpoint}: ERROR - {e}")

def main():
    print("🔍 Simple Agency Endpoint Testing")
    print("=" * 50)
    
    # Get token
    token = get_agency_token()
    if not token:
        print("❌ Failed to get agency token")
        return
    
    print("✅ Agency authentication successful")
    print()
    
    # Test endpoints
    endpoints = [
        ("/agency/license-balance", "GET"),
        ("/agency/invitations", "GET"),
        ("/agency/subscription", "GET"),
        ("/agency/branding", "GET"),
        ("/agency/contract-opportunities", "GET"),
        ("/agency/business-intelligence", "GET"),
    ]
    
    for endpoint, method in endpoints:
        test_endpoint(endpoint, token, method)
        print()

if __name__ == "__main__":
    main()