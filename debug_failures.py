#!/usr/bin/env python3
"""
Debug the 3 failing tests to understand the exact error messages
"""

import requests
import json

BASE_URL = "https://production-guru.preview.emergentagent.com/api"
QA_CREDENTIALS = {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}

def get_auth_token():
    response = requests.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS)
    if response.status_code == 200:
        return f"Bearer {response.json()['access_token']}"
    return None

def debug_assessment_response():
    print("=== DEBUGGING ASSESSMENT RESPONSE ===")
    token = get_auth_token()
    headers = {"Authorization": token}
    
    # Create session first
    session_response = requests.post(f"{BASE_URL}/assessment/session", headers=headers)
    if session_response.status_code == 200:
        session_id = session_response.json()["session_id"]
        print(f"Session created: {session_id}")
        
        # Try to submit response
        response_payload = {
            "question_id": "q1_1",
            "response": "no_need_help",
            "area_id": "area1"
        }
        response = requests.post(f"{BASE_URL}/assessment/session/{session_id}/response", 
                               json=response_payload, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    else:
        print(f"Session creation failed: {session_response.status_code} - {session_response.text}")

def debug_business_profile():
    print("\n=== DEBUGGING BUSINESS PROFILE ===")
    token = get_auth_token()
    headers = {"Authorization": token}
    
    profile_payload = {
        "business_name": "QA Test Business",
        "business_type": "LLC",
        "industry": "Technology",
        "location": "Minneapolis, MN",
        "employees_count": "1-10",
        "annual_revenue": "under-100k",
        "primary_service_area": "area5"
    }
    
    response = requests.post(f"{BASE_URL}/business/profile", json=profile_payload, headers=headers)
    print(f"Business profile status: {response.status_code}")
    print(f"Business profile body: {response.text}")

def debug_service_request():
    print("\n=== DEBUGGING SERVICE REQUEST ===")
    token = get_auth_token()
    headers = {"Authorization": token}
    
    service_request_payload = {
        "area_id": "area5",
        "budget_range": "$1,000-$2,500",
        "timeline": "2-4 weeks",
        "description": "Need help with cybersecurity assessment and implementation for small business",
        "maturity_statement": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                           json=service_request_payload, headers=headers)
    print(f"Service request status: {response.status_code}")
    print(f"Service request body: {response.text}")

if __name__ == "__main__":
    debug_assessment_response()
    debug_business_profile()
    debug_service_request()