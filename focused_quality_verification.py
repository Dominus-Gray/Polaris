#!/usr/bin/env python3
"""
FOCUSED QUALITY VERIFICATION - Critical Issues Testing
Focuses on the specific issues mentioned in the review request
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://readiness-hub-2.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

def log_result(message, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {level}: {message}")

def make_request(method, endpoint, data=None, auth_token=None):
    """Make HTTP request with proper error handling"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            response = requests.request(method, url, json=data, headers=headers, timeout=10)
        
        return response
    except Exception as e:
        log_result(f"Request failed: {e}", "ERROR")
        return None

def test_authentication():
    """Test all QA user authentication"""
    log_result("=== TESTING AUTHENTICATION & AUTHORIZATION ===")
    tokens = {}
    
    for role, creds in QA_CREDENTIALS.items():
        response = make_request("POST", "/auth/login", {
            "email": creds["email"],
            "password": creds["password"]
        })
        
        if response and response.status_code == 200:
            token_data = response.json()
            tokens[role] = token_data["access_token"]
            log_result(f"✅ {role.title()} login successful")
        else:
            log_result(f"❌ {role.title()} login failed: {response.status_code if response else 'No response'}")
    
    return tokens

def test_knowledge_base(tokens):
    """Test Knowledge Base system"""
    log_result("=== TESTING KNOWLEDGE BASE SYSTEM ===")
    
    if "client" not in tokens:
        log_result("❌ No client token available for KB testing")
        return
    
    # Test KB areas with authentication
    response = make_request("GET", "/knowledge-base/areas", auth_token=tokens["client"])
    if response and response.status_code == 200:
        areas = response.json()
        log_result(f"✅ KB Areas retrieved: {len(areas)} areas")
    else:
        log_result(f"❌ KB Areas failed: {response.status_code if response else 'No response'}")
    
    # Test template generation (the failing feature from test_result.md)
    response = make_request("GET", "/knowledge-base/generate-template/area1/template", 
                          auth_token=tokens["client"])
    if response and response.status_code == 200:
        template_data = response.json()
        log_result(f"✅ Template generation working: {template_data.get('filename', 'No filename')}")
    else:
        log_result(f"❌ Template generation failed: {response.status_code if response else 'No response'}")
    
    # Test content access
    response = make_request("GET", "/knowledge-base/area1/content", auth_token=tokens["client"])
    if response and response.status_code == 200:
        log_result("✅ KB content access working for test accounts")
    else:
        log_result(f"❌ KB content access failed: {response.status_code if response else 'No response'}")

def test_data_standardization(tokens):
    """Test new standardized models"""
    log_result("=== TESTING DATA STANDARDIZATION ===")
    
    if "client" not in tokens or "provider" not in tokens:
        log_result("❌ Missing tokens for data standardization testing")
        return
    
    # Test standardized service request
    service_request = {
        "area_id": "area5",
        "budget_range": "1500-5000",
        "timeline": "2-4 weeks",
        "description": "Testing standardized engagement request model with comprehensive validation",
        "priority": "high"
    }
    
    response = make_request("POST", "/service-requests/professional-help", 
                          service_request, auth_token=tokens["client"])
    
    if response and response.status_code == 200:
        request_data = response.json()
        request_id = request_data.get("request_id")
        log_result(f"✅ Standardized service request created: {request_id}")
        
        # Test standardized provider response
        if request_id:
            provider_response = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3-4 weeks",
                "proposal_note": "Comprehensive testing of standardized provider response model"
            }
            
            response = make_request("POST", "/provider/respond-to-request",
                                  provider_response, auth_token=tokens["provider"])
            
            if response and response.status_code == 200:
                log_result("✅ Standardized provider response working")
            else:
                log_result(f"❌ Provider response failed: {response.status_code if response else 'No response'}")
                if response:
                    log_result(f"   Error details: {response.text}")
    else:
        log_result(f"❌ Service request creation failed: {response.status_code if response else 'No response'}")
        if response:
            log_result(f"   Error details: {response.text}")

def test_polaris_error_codes():
    """Test Polaris error codes"""
    log_result("=== TESTING POLARIS ERROR CODES ===")
    
    # Test invalid login for POL-1001
    response = make_request("POST", "/auth/login", {
        "email": "invalid@test.com",
        "password": "wrongpassword"
    })
    
    if response and response.status_code == 400:
        error_data = response.json()
        if "POL-1001" in str(error_data):
            log_result("✅ POL-1001 error code working correctly")
        else:
            log_result(f"❌ Expected POL-1001, got: {error_data}")
    else:
        log_result(f"❌ Invalid login test failed: {response.status_code if response else 'No response'}")

def test_assessment_system(tokens):
    """Test assessment system"""
    log_result("=== TESTING ASSESSMENT SYSTEM ===")
    
    if "client" not in tokens:
        log_result("❌ No client token for assessment testing")
        return
    
    # Get user info first
    response = make_request("GET", "/auth/me", auth_token=tokens["client"])
    if response and response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get("id")
        
        # Test assessment progress
        response = make_request("GET", f"/assessment/progress/{user_id}", 
                              auth_token=tokens["client"])
        if response and response.status_code == 200:
            log_result("✅ Assessment progress endpoint working")
        else:
            log_result(f"❌ Assessment progress failed: {response.status_code if response else 'No response'}")
        
        # Test assessment submission
        assessment_data = {
            "area_id": "area1",
            "responses": [
                {"question_id": "q1", "answer": "yes", "evidence": "Test evidence"},
                {"question_id": "q2", "answer": "no", "evidence": ""}
            ]
        }
        
        response = make_request("POST", "/assessment/submit", 
                              assessment_data, auth_token=tokens["client"])
        if response and response.status_code == 200:
            log_result("✅ Assessment submission working")
        else:
            log_result(f"❌ Assessment submission failed: {response.status_code if response else 'No response'}")

def test_performance():
    """Test performance requirements"""
    log_result("=== TESTING PERFORMANCE ===")
    
    # Test response times
    start_time = time.time()
    response = make_request("GET", "/auth/me")  # This will return 401 but still test response time
    response_time = time.time() - start_time
    
    if response_time < 2.0:
        log_result(f"✅ Response time good: {response_time:.3f}s (< 2s requirement)")
    else:
        log_result(f"❌ Response time too slow: {response_time:.3f}s (> 2s requirement)")

def main():
    log_result("🎯 STARTING FOCUSED QUALITY VERIFICATION")
    log_result(f"Testing against: {BASE_URL}")
    
    # Run focused tests
    tokens = test_authentication()
    test_polaris_error_codes()
    test_knowledge_base(tokens)
    test_data_standardization(tokens)
    test_assessment_system(tokens)
    test_performance()
    
    log_result("🎯 FOCUSED QUALITY VERIFICATION COMPLETE")

if __name__ == "__main__":
    main()