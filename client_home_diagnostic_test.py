#!/usr/bin/env python3
"""
Critical Issue Investigation - Client Dashboard not loading
Testing /api/home/client endpoint specifically to diagnose why ClientHome component shows empty/blank content
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
CLIENT_EMAIL = "client.qa@polaris.example.com"
CLIENT_PASSWORD = "Polaris#2025!"

def log_test(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_client_home_endpoint():
    """Test the /api/home/client endpoint that's causing dashboard issues"""
    
    log_test("🔍 CRITICAL ISSUE INVESTIGATION: Client Dashboard not loading")
    log_test("Testing /api/home/client endpoint with QA credentials")
    
    # Step 1: Authenticate with client credentials
    log_test("Step 1: Authenticating with client QA credentials")
    
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": CLIENT_EMAIL,
                "password": CLIENT_PASSWORD
            },
            timeout=10
        )
        
        log_test(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            log_test(f"❌ AUTHENTICATION FAILED: {login_response.status_code}", "ERROR")
            log_test(f"Response: {login_response.text}", "ERROR")
            return False
        
        login_data = login_response.json()
        access_token = login_data.get("access_token")
        
        if not access_token:
            log_test("❌ No access token received", "ERROR")
            return False
        
        log_test("✅ Authentication successful")
        
    except Exception as e:
        log_test(f"❌ Authentication error: {str(e)}", "ERROR")
        return False
    
    # Step 2: Test /api/home/client endpoint
    log_test("Step 2: Testing /api/home/client endpoint")
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        home_response = requests.get(
            f"{BACKEND_URL}/home/client",
            headers=headers,
            timeout=10
        )
        
        log_test(f"Home endpoint response status: {home_response.status_code}")
        
        if home_response.status_code != 200:
            log_test(f"❌ HOME ENDPOINT FAILED: {home_response.status_code}", "ERROR")
            log_test(f"Response headers: {dict(home_response.headers)}", "ERROR")
            log_test(f"Response body: {home_response.text}", "ERROR")
            
            # Check if it's a 404 (endpoint doesn't exist)
            if home_response.status_code == 404:
                log_test("🚨 CRITICAL: /api/home/client endpoint does not exist!", "ERROR")
            elif home_response.status_code == 401:
                log_test("🚨 CRITICAL: Authentication failed for /api/home/client", "ERROR")
            elif home_response.status_code == 403:
                log_test("🚨 CRITICAL: Access forbidden for /api/home/client", "ERROR")
            elif home_response.status_code == 500:
                log_test("🚨 CRITICAL: Server error in /api/home/client", "ERROR")
            
            return False
        
        # Step 3: Analyze response data structure
        log_test("Step 3: Analyzing response data structure")
        
        try:
            home_data = home_response.json()
            log_test(f"✅ Response received: {json.dumps(home_data, indent=2)}")
            
            # Check if response is null or empty
            if home_data is None:
                log_test("🚨 CRITICAL: Response data is null - this explains blank dashboard!", "ERROR")
                return False
            
            if not home_data:
                log_test("🚨 CRITICAL: Response data is empty - this explains blank dashboard!", "ERROR")
                return False
            
            # Check expected fields for client dashboard
            expected_fields = ["readiness", "has_certificate", "opportunities", "profile_complete"]
            missing_fields = []
            
            for field in expected_fields:
                if field not in home_data:
                    missing_fields.append(field)
            
            if missing_fields:
                log_test(f"⚠️ Missing expected fields: {missing_fields}", "WARNING")
            
            # Analyze each field
            log_test("📊 Data Analysis:")
            log_test(f"  - Readiness Score: {home_data.get('readiness', 'MISSING')}")
            log_test(f"  - Has Certificate: {home_data.get('has_certificate', 'MISSING')}")
            log_test(f"  - Opportunities: {home_data.get('opportunities', 'MISSING')}")
            log_test(f"  - Profile Complete: {home_data.get('profile_complete', 'MISSING')}")
            
            # Check for any null values that might cause frontend issues
            null_fields = []
            for key, value in home_data.items():
                if value is None:
                    null_fields.append(key)
            
            if null_fields:
                log_test(f"⚠️ Fields with null values: {null_fields}", "WARNING")
            
            log_test("✅ /api/home/client endpoint is working and returning data")
            return True
            
        except json.JSONDecodeError as e:
            log_test(f"❌ Invalid JSON response: {str(e)}", "ERROR")
            log_test(f"Raw response: {home_response.text}", "ERROR")
            return False
        
    except Exception as e:
        log_test(f"❌ Error testing home endpoint: {str(e)}", "ERROR")
        return False

def test_related_endpoints():
    """Test related endpoints that /api/home/client depends on"""
    
    log_test("Step 4: Testing related endpoints that home/client depends on")
    
    # Authenticate first
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": CLIENT_EMAIL,
                "password": CLIENT_PASSWORD
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            log_test("❌ Cannot authenticate for related endpoint tests", "ERROR")
            return False
        
        access_token = login_response.json().get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test endpoints that home/client depends on
        related_endpoints = [
            "/assessment/sessions",  # For readiness calculation
            "/certificates",         # For certificate status
            "/opportunities",        # For opportunities count
            "/business-profiles/me"  # For profile completion
        ]
        
        for endpoint in related_endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                log_test(f"  {endpoint}: {response.status_code}")
                
                if response.status_code == 404:
                    log_test(f"    ⚠️ {endpoint} not found - may affect home/client", "WARNING")
                elif response.status_code >= 500:
                    log_test(f"    ❌ {endpoint} server error - may affect home/client", "ERROR")
                
            except Exception as e:
                log_test(f"    ❌ Error testing {endpoint}: {str(e)}", "ERROR")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Error in related endpoint tests: {str(e)}", "ERROR")
        return False

def main():
    """Main diagnostic function"""
    
    log_test("=" * 80)
    log_test("🚨 CRITICAL ISSUE INVESTIGATION")
    log_test("Problem: ClientHome dashboard showing blank/empty content")
    log_test("Suspected cause: /api/home/client endpoint not returning data")
    log_test("=" * 80)
    
    # Test the main endpoint
    success = test_client_home_endpoint()
    
    if success:
        log_test("✅ /api/home/client endpoint is working correctly")
        log_test("🔍 The issue may be in the frontend ClientHome component")
        log_test("💡 Check if frontend is correctly handling the response data")
    else:
        log_test("❌ /api/home/client endpoint has issues")
        log_test("🔧 This explains why the dashboard is blank/empty")
    
    # Test related endpoints
    test_related_endpoints()
    
    log_test("=" * 80)
    log_test("🎯 DIAGNOSTIC COMPLETE")
    log_test("=" * 80)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)