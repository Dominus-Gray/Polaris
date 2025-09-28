#!/usr/bin/env python3
"""
Test POL-1005 error code specifically for Knowledge Base access control
"""

import requests
import json
import uuid

BASE_URL = "https://polaris-migrate.preview.emergentagent.com/api"

def test_pol_1005():
    """Test POL-1005 error code for Knowledge Base access control"""
    
    # Create a test user that doesn't have special access
    test_email = f"test_{str(uuid.uuid4())[:8]}@example.com"
    test_password = "TestPass123!"
    
    print(f"Creating test user: {test_email}")
    
    # First, we need to get a license code from an agency
    # Let's try to login as an existing agency to get a license
    agency_creds = {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
    
    agency_login = requests.post(f"{BASE_URL}/auth/login", json=agency_creds)
    if agency_login.status_code != 200:
        print(f"Failed to login as agency: {agency_login.status_code}")
        return False
    
    agency_token = agency_login.json()["access_token"]
    agency_headers = {"Authorization": f"Bearer {agency_token}"}
    
    # Generate license codes
    license_response = requests.post(
        f"{BASE_URL}/agency/licenses/generate", 
        json={"quantity": 1},
        headers=agency_headers
    )
    
    if license_response.status_code != 200:
        print(f"Failed to generate license: {license_response.status_code}")
        return False
    
    license_code = license_response.json()["licenses"][0]["license_code"]
    print(f"Generated license code: {license_code}")
    
    # Register test user
    register_payload = {
        "email": test_email,
        "password": test_password,
        "role": "client",
        "terms_accepted": True,
        "license_code": license_code
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
    if register_response.status_code != 200:
        print(f"Failed to register test user: {register_response.status_code} - {register_response.text}")
        return False
    
    print("Test user registered successfully")
    
    # Login as test user
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    
    if login_response.status_code != 200:
        print(f"Failed to login as test user: {login_response.status_code}")
        return False
    
    test_token = login_response.json()["access_token"]
    test_headers = {"Authorization": f"Bearer {test_token}"}
    
    print("Test user logged in successfully")
    
    # Now try to access Knowledge Base download endpoint (should trigger POL-1005)
    kb_download_response = requests.get(
        f"{BASE_URL}/knowledge-base/download/default_template_area1",
        headers=test_headers
    )
    
    print(f"KB Download Response Status: {kb_download_response.status_code}")
    print(f"KB Download Response: {kb_download_response.text}")
    
    if kb_download_response.status_code == 402 or kb_download_response.status_code == 403:
        try:
            error_data = kb_download_response.json()
            message_data = error_data.get("message", {})
            
            if isinstance(message_data, dict) and message_data.get("error_code") == "POL-1005":
                print(f"✅ SUCCESS: POL-1005 error code found!")
                print(f"   Error Code: {message_data.get('error_code')}")
                print(f"   Message: {message_data.get('message')}")
                print(f"   Detail: {message_data.get('detail')}")
                return True
            else:
                print(f"❌ FAIL: Expected POL-1005 but got different error format: {error_data}")
                return False
        except:
            print(f"❌ FAIL: Could not parse error response as JSON")
            return False
    else:
        print(f"❌ FAIL: Expected 402/403 status but got {kb_download_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_pol_1005()
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")