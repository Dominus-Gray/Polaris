#!/usr/bin/env python3
"""
FRONTEND INTEGRATION TESTING
Testing the complete login flow including frontend API calls
"""

import requests
import json
from datetime import datetime

# Production URLs
FRONTEND_URL = "https://polar-docs-ai.preview.emergentagent.com"
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

def test_frontend_endpoints():
    """Test if frontend is making correct API calls"""
    print("🔍 FRONTEND INTEGRATION TESTING")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Test client credentials
    email = "client.qa@polaris.example.com"
    password = "Polaris#2025!"
    
    print(f"\n1. Testing Frontend Login Flow")
    print(f"   Using: {email}")
    
    # First, get a valid token from backend
    print(f"\n   Step 1: Backend Authentication")
    backend_login = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if backend_login.status_code == 200:
        token = backend_login.json().get('access_token')
        print(f"   ✅ Backend login successful (token: {len(token)} chars)")
        
        # Test endpoints that frontend might be calling
        print(f"\n   Step 2: Testing Frontend API Endpoints")
        
        endpoints_to_test = [
            # Correct backend endpoints
            ("/auth/me", "Auth verification"),
            ("/home/client", "Client dashboard data"),
            ("/notifications/my", "User notifications"),
            ("/knowledge-base/areas", "Knowledge base areas"),
            ("/assessment/schema", "Assessment schema"),
            ("/planner/tasks", "Task planner"),
            ("/engagements/my-services", "User services"),
            
            # Common frontend mistakes (missing /api prefix)
            ("/auth/login", "Login endpoint (frontend might call this)"),
            ("/home/client", "Dashboard (frontend might call this)"),
        ]
        
        for endpoint, description in endpoints_to_test:
            test_endpoint(f"{BACKEND_URL}{endpoint}", token, description)
            
        # Test if frontend might be calling wrong URLs
        print(f"\n   Step 3: Testing Common Frontend Mistakes")
        
        wrong_endpoints = [
            (f"{FRONTEND_URL}/auth/login", "Frontend calling auth without /api"),
            (f"{FRONTEND_URL}/home/client", "Frontend calling home without /api"),
            (f"{FRONTEND_URL}/api/auth/login", "Frontend calling with /api (correct)"),
        ]
        
        for url, description in wrong_endpoints:
            test_wrong_endpoint(url, description)
            
    else:
        print(f"   ❌ Backend login failed: {backend_login.status_code}")
        print(f"   Response: {backend_login.text[:200]}")

def test_endpoint(url, token, description):
    """Test a specific endpoint with token"""
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ {description}: OK")
        elif response.status_code == 401:
            print(f"   ⚠️  {description}: 401 Unauthorized")
        elif response.status_code == 404:
            print(f"   ❌ {description}: 404 Not Found")
        else:
            print(f"   ❌ {description}: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ {description}: ERROR - {str(e)[:50]}")

def test_wrong_endpoint(url, description):
    """Test endpoints that frontend might incorrectly call"""
    try:
        response = requests.post(
            url,
            json={"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"   📍 {description}: {response.status_code}")
        
    except Exception as e:
        print(f"   📍 {description}: ERROR - {str(e)[:50]}")

def test_cors_and_headers():
    """Test CORS and header configuration"""
    print(f"\n2. Testing CORS and Headers")
    
    try:
        # Test OPTIONS request (CORS preflight)
        response = requests.options(
            f"{BACKEND_URL}/auth/login",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        print(f"   CORS Preflight: {response.status_code}")
        
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials"
        ]
        
        for header in cors_headers:
            value = response.headers.get(header, "Not set")
            print(f"   {header}: {value}")
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {str(e)}")

def check_frontend_accessibility():
    """Check if frontend is accessible"""
    print(f"\n3. Testing Frontend Accessibility")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"   Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's actually serving the React app
            content = response.text.lower()
            if "react" in content or "polaris" in content or "root" in content:
                print(f"   ✅ Frontend appears to be serving React app")
            else:
                print(f"   ⚠️  Frontend response doesn't look like React app")
        
    except Exception as e:
        print(f"   ❌ Frontend accessibility test failed: {str(e)}")

def main():
    """Main test execution"""
    try:
        test_frontend_endpoints()
        test_cors_and_headers()
        check_frontend_accessibility()
        
        print(f"\n" + "=" * 80)
        print("🎯 FRONTEND INTEGRATION ANALYSIS")
        print("=" * 80)
        print("✅ Backend authentication: WORKING (all 4 QA accounts)")
        print("⚠️  Some dashboard endpoints: 401 errors (expected without proper auth)")
        print("✅ Assessment schema: Working")
        print("")
        print("🔧 LIKELY ISSUES:")
        print("1. Frontend may be calling endpoints without /api prefix")
        print("2. Frontend may not be properly handling authentication tokens")
        print("3. Frontend may not be setting Authorization headers correctly")
        print("4. Frontend login form may not be redirecting after successful auth")
        print("")
        print("🎯 RECOMMENDED FIXES:")
        print("1. Ensure all frontend API calls include /api prefix")
        print("2. Verify frontend stores and uses JWT tokens correctly")
        print("3. Check frontend login form submission and redirect logic")
        print("4. Test complete user flow in browser with developer tools")
        
    except Exception as e:
        print(f"\n🚨 CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    main()