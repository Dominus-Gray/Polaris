#!/usr/bin/env python3
"""
Debug test for paywall protection
"""

import requests
import json
import uuid

BACKEND_URL = "https://quality-match-1.preview.emergentagent.com/api"

def test_paywall_debug():
    # Create a regular user
    unique_id = str(uuid.uuid4())[:8]
    regular_user_email = f"regular.user.{unique_id}@example.com"
    
    # First authenticate as agency to generate license
    agency_creds = {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
    agency_response = requests.post(f"{BACKEND_URL}/auth/login", json=agency_creds)
    
    if agency_response.status_code != 200:
        print(f"❌ Agency auth failed: {agency_response.status_code}")
        return
    
    agency_token = agency_response.json()["access_token"]
    
    # Generate license
    license_response = requests.post(f"{BACKEND_URL}/agency/licenses/generate", 
                                   json={"quantity": 1}, 
                                   headers={"Authorization": f"Bearer {agency_token}"})
    
    if license_response.status_code != 200:
        print(f"❌ License generation failed: {license_response.status_code} - {license_response.text}")
        return
    
    license_code = license_response.json()["licenses"][0]["license_code"]
    print(f"✅ Generated license: {license_code}")
    
    # Register regular user
    user_data = {
        "email": regular_user_email,
        "password": "RegularUser123!",
        "role": "client",
        "terms_accepted": True,
        "license_code": license_code
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
    
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.status_code} - {register_response.text}")
        return
    
    print(f"✅ Registered user: {regular_user_email}")
    
    # Login regular user
    login_response = requests.post(f"{BACKEND_URL}/auth/login", 
                                 json={"email": regular_user_email, "password": "RegularUser123!"})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    regular_token = login_response.json()["access_token"]
    print(f"✅ Logged in regular user")
    
    # Check knowledge base access
    access_response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", 
                                 headers={"Authorization": f"Bearer {regular_token}"})
    
    print(f"📋 KB Areas response: {access_response.status_code}")
    if access_response.status_code == 200:
        areas_data = access_response.json()
        print(f"   Areas count: {len(areas_data.get('areas', []))}")
        if areas_data.get('areas'):
            first_area = areas_data['areas'][0]
            print(f"   First area locked: {first_area.get('locked', 'unknown')}")
    
    # Check knowledge base access record in database
    print(f"\n🔍 Testing AI assistance with regular user...")
    
    payload = {
        "question": "How do I get started with business licensing?",
        "area_id": "area1"
    }
    
    ai_response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                              json=payload, 
                              headers={"Authorization": f"Bearer {regular_token}"})
    
    print(f"🤖 AI Assistance response: {ai_response.status_code}")
    print(f"   Response: {ai_response.text}")
    
    # Test with test user for comparison
    print(f"\n🔍 Testing AI assistance with test user...")
    
    test_creds = {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
    test_response = requests.post(f"{BACKEND_URL}/auth/login", json=test_creds)
    
    if test_response.status_code == 200:
        test_token = test_response.json()["access_token"]
        
        test_ai_response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", 
                                       json=payload, 
                                       headers={"Authorization": f"Bearer {test_token}"})
        
        print(f"🤖 Test user AI Assistance response: {test_ai_response.status_code}")
        if test_ai_response.status_code == 200:
            response_data = test_ai_response.json()
            print(f"   Response length: {len(response_data.get('response', ''))}")
            print(f"   Source: {response_data.get('source', 'unknown')}")

if __name__ == "__main__":
    test_paywall_debug()