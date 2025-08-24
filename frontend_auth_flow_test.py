#!/usr/bin/env python3
"""
Frontend Authentication Flow Test
Testing the exact authentication flow that the frontend uses
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://polaris-inspector.preview.emergentagent.com/api"
CLIENT_EMAIL = "client.qa@polaris.example.com"
CLIENT_PASSWORD = "Polaris#2025!"

def log_test(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_frontend_auth_flow():
    """Test the exact authentication flow that frontend uses"""
    
    log_test("🔍 TESTING FRONTEND AUTHENTICATION FLOW")
    
    # Step 1: Login (same as frontend)
    log_test("Step 1: Login with client credentials")
    
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
            log_test(f"❌ Login failed: {login_response.text}", "ERROR")
            return False
        
        login_data = login_response.json()
        access_token = login_data.get("access_token")
        
        if not access_token:
            log_test("❌ No access token in response", "ERROR")
            return False
        
        log_test("✅ Login successful, token received")
        
        # Step 2: Test /auth/me (frontend calls this to get user info)
        log_test("Step 2: Testing /auth/me endpoint")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        me_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
        
        if me_response.status_code != 200:
            log_test(f"❌ /auth/me failed: {me_response.status_code} - {me_response.text}", "ERROR")
            return False
        
        me_data = me_response.json()
        log_test(f"✅ User info: {json.dumps(me_data, indent=2)}")
        
        # Step 3: Test /home/client with same token
        log_test("Step 3: Testing /home/client with same token")
        
        home_response = requests.get(f"{BACKEND_URL}/home/client", headers=headers, timeout=10)
        
        if home_response.status_code != 200:
            log_test(f"❌ /home/client failed: {home_response.status_code} - {home_response.text}", "ERROR")
            return False
        
        home_data = home_response.json()
        log_test(f"✅ Home data: {json.dumps(home_data, indent=2)}")
        
        # Step 4: Test without Authorization header (simulate missing token)
        log_test("Step 4: Testing /home/client without Authorization header")
        
        no_auth_response = requests.get(f"{BACKEND_URL}/home/client", timeout=10)
        log_test(f"No auth response: {no_auth_response.status_code}")
        
        if no_auth_response.status_code == 401:
            log_test("✅ Proper 401 response without auth")
        else:
            log_test(f"⚠️ Unexpected response without auth: {no_auth_response.status_code}", "WARNING")
        
        # Step 5: Test with malformed token
        log_test("Step 5: Testing /home/client with malformed token")
        
        bad_headers = {
            "Authorization": "Bearer malformed_token",
            "Content-Type": "application/json"
        }
        
        bad_auth_response = requests.get(f"{BACKEND_URL}/home/client", headers=bad_headers, timeout=10)
        log_test(f"Bad auth response: {bad_auth_response.status_code}")
        
        if bad_auth_response.status_code == 401:
            log_test("✅ Proper 401 response with bad token")
        else:
            log_test(f"⚠️ Unexpected response with bad token: {bad_auth_response.status_code}", "WARNING")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Error in auth flow test: {str(e)}", "ERROR")
        return False

def test_cors_and_headers():
    """Test CORS and header issues that might affect frontend"""
    
    log_test("🔍 TESTING CORS AND HEADERS")
    
    # Test preflight request
    try:
        preflight_response = requests.options(
            f"{BACKEND_URL}/home/client",
            headers={
                "Origin": "https://polaris-inspector.preview.emergentagent.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            },
            timeout=10
        )
        
        log_test(f"CORS preflight response: {preflight_response.status_code}")
        log_test(f"CORS headers: {dict(preflight_response.headers)}")
        
        # Check for required CORS headers
        cors_headers = preflight_response.headers
        if "Access-Control-Allow-Origin" in cors_headers:
            log_test(f"✅ CORS Allow-Origin: {cors_headers['Access-Control-Allow-Origin']}")
        else:
            log_test("⚠️ Missing Access-Control-Allow-Origin header", "WARNING")
        
        if "Access-Control-Allow-Methods" in cors_headers:
            log_test(f"✅ CORS Allow-Methods: {cors_headers['Access-Control-Allow-Methods']}")
        else:
            log_test("⚠️ Missing Access-Control-Allow-Methods header", "WARNING")
        
    except Exception as e:
        log_test(f"❌ CORS test error: {str(e)}", "ERROR")

def test_network_conditions():
    """Test various network conditions that might affect frontend"""
    
    log_test("🔍 TESTING NETWORK CONDITIONS")
    
    # Test with very short timeout (simulate slow network)
    try:
        response = requests.get(f"{BACKEND_URL}/home/client", timeout=0.1)
    except requests.exceptions.Timeout:
        log_test("✅ Timeout handling works (simulated slow network)")
    except Exception as e:
        log_test(f"Network condition test: {str(e)}")

def main():
    """Main test function"""
    
    log_test("=" * 80)
    log_test("🚨 FRONTEND AUTHENTICATION FLOW DIAGNOSTIC")
    log_test("Testing exact auth flow that frontend ClientHome uses")
    log_test("=" * 80)
    
    auth_success = test_frontend_auth_flow()
    test_cors_and_headers()
    test_network_conditions()
    
    log_test("=" * 80)
    log_test("🎯 AUTHENTICATION FLOW SUMMARY")
    log_test("=" * 80)
    
    if auth_success:
        log_test("✅ Authentication flow is working correctly")
        log_test("🔍 The issue is likely one of these:")
        log_test("   1. Frontend token is not being stored properly in localStorage")
        log_test("   2. Axios default headers are not being set correctly")
        log_test("   3. There's a race condition in the useEffect")
        log_test("   4. An error in one of the subsequent API calls is causing the entire load to fail")
        log_test("   5. The 'polaris_me' localStorage item is missing or invalid")
        
        log_test("\n🔧 RECOMMENDED DEBUGGING STEPS:")
        log_test("   1. Check browser localStorage for 'polaris_token' and 'polaris_me'")
        log_test("   2. Check browser console for JavaScript errors")
        log_test("   3. Check Network tab in DevTools for failed requests")
        log_test("   4. Add console.log statements in ClientHome useEffect")
    else:
        log_test("❌ Authentication flow has issues")
        log_test("🔧 Fix authentication issues first")
    
    return auth_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)