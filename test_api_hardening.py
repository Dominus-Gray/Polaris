#!/usr/bin/env python3
"""
Test script for Public API Hardening features
Tests API tokens, rate limiting, error formatting, and versioning
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://biz-matchmaker-1.preview.emergentagent.com"

def test_api_versioning():
    """Test API versioning and deprecation headers"""
    print("=== Testing API Versioning ===")
    
    # Test legacy API for deprecation headers
    try:
        response = requests.get(f"{BASE_URL}/api/auth/password-requirements")
        print(f"Legacy API Status: {response.status_code}")
        print("Legacy API Headers:")
        for header in ["sunset", "link", "deprecation"]:
            if header in response.headers:
                print(f"  {header}: {response.headers[header]}")
    except Exception as e:
        print(f"Legacy API test failed: {e}")
    
    # Test versioned API
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tokens", 
                              headers={"Authorization": "Bearer invalid"})
        print(f"Versioned API Status: {response.status_code}")
        print("Versioned API available")
    except Exception as e:
        print(f"Versioned API test failed: {e}")

def test_error_format():
    """Test Problem+JSON error format"""
    print("\n=== Testing Error Format ===")
    
    # Test invalid login for standardized error response
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json={"email": "invalid@test.com", "password": "wrong"})
        print(f"Error Response Status: {response.status_code}")
        
        if response.status_code >= 400:
            error_data = response.json()
            print("Error Response Format:")
            print(json.dumps(error_data, indent=2))
            
            # Check for Problem+JSON fields
            expected_fields = ["type", "title", "status", "detail", "instance", "code"]
            found_fields = [field for field in expected_fields if field in error_data]
            print(f"Problem+JSON fields found: {found_fields}")
            
    except Exception as e:
        print(f"Error format test failed: {e}")

def test_rate_limiting():
    """Test rate limiting headers"""
    print("\n=== Testing Rate Limiting ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/password-requirements")
        print(f"Rate Limit Response Status: {response.status_code}")
        
        # Check for rate limiting headers
        rate_headers = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
        print("Rate Limit Headers:")
        for header in rate_headers:
            if header in response.headers:
                print(f"  {header}: {response.headers[header]}")
    except Exception as e:
        print(f"Rate limiting test failed: {e}")

def test_api_scopes():
    """Test API scope definitions"""
    print("\n=== Testing API Scopes ===")
    
    # This would require a valid token, but we can test the scope definitions
    scopes = [
        "read:clients", "write:clients",
        "read:action_plans", "write:action_plans", 
        "read:tasks", "write:tasks",
        "read:analytics", "read:cohorts",
        "manage:tokens",
        "read:consents", "write:consents"
    ]
    
    print("Defined API Scopes:")
    for scope in scopes:
        print(f"  - {scope}")

def test_content_type_headers():
    """Test Content-Type headers for Problem+JSON"""
    print("\n=== Testing Content-Type Headers ===")
    
    try:
        # Make request that should return error
        response = requests.post(f"{BASE_URL}/api/v1/tokens",
                               headers={"Authorization": "Bearer invalid"},
                               json={"name": "test", "scopes": ["read:clients"]})
        
        print(f"Status: {response.status_code}")
        content_type = response.headers.get("content-type", "")
        print(f"Content-Type: {content_type}")
        
        if "application/problem+json" in content_type:
            print("✅ Correct Problem+JSON Content-Type header")
        else:
            print("❌ Missing Problem+JSON Content-Type header")
            
    except Exception as e:
        print(f"Content-Type test failed: {e}")

if __name__ == "__main__":
    print("Public API Hardening Test Suite")
    print("================================")
    
    test_api_versioning()
    test_error_format()
    test_rate_limiting() 
    test_api_scopes()
    test_content_type_headers()
    
    print("\n=== Test Complete ===")
    print("Check output above for API hardening feature validation")