#!/usr/bin/env python3
"""
Comprehensive Client Home Data Loading Test
Testing all endpoints that ClientHome component calls to identify why data might be null
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"
CLIENT_EMAIL = "client.qa@polaris.example.com"
CLIENT_PASSWORD = "Polaris#2025!"

def log_test(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def authenticate():
    """Authenticate and return access token"""
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
            log_test(f"❌ Authentication failed: {login_response.status_code}", "ERROR")
            return None
        
        return login_response.json().get("access_token")
    except Exception as e:
        log_test(f"❌ Authentication error: {str(e)}", "ERROR")
        return None

def test_all_client_home_endpoints():
    """Test all endpoints that ClientHome component calls"""
    
    log_test("🔍 COMPREHENSIVE CLIENT HOME DATA LOADING TEST")
    log_test("Testing all endpoints that ClientHome component depends on")
    
    # Authenticate
    access_token = authenticate()
    if not access_token:
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get user info first
    me_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    user_id = None
    if me_response.status_code == 200:
        user_id = me_response.json().get("id")
        log_test(f"✅ User ID: {user_id}")
    
    # Test all endpoints in order that ClientHome calls them
    endpoints_to_test = [
        {
            "name": "Main Home Data",
            "url": f"{BACKEND_URL}/home/client",
            "critical": True,
            "description": "Primary dashboard data"
        },
        {
            "name": "Client Certificates",
            "url": f"{BACKEND_URL}/client/certificates",
            "critical": False,
            "description": "Certificate information"
        },
        {
            "name": "Matched Services",
            "url": f"{BACKEND_URL}/client/matched-services",
            "critical": False,
            "description": "Service provider matches"
        },
        {
            "name": "Knowledge Base Access",
            "url": f"{BACKEND_URL}/knowledge-base/access",
            "critical": False,
            "description": "KB unlock status"
        },
        {
            "name": "Assessment Progress",
            "url": f"{BACKEND_URL}/assessment/progress/{user_id}" if user_id else None,
            "critical": False,
            "description": "Assessment completion data"
        },
        {
            "name": "My Services/Engagements",
            "url": f"{BACKEND_URL}/engagements/my-services",
            "critical": False,
            "description": "Active service requests"
        }
    ]
    
    results = {}
    critical_failures = []
    
    for endpoint in endpoints_to_test:
        if endpoint["url"] is None:
            log_test(f"⚠️ Skipping {endpoint['name']} - no user ID", "WARNING")
            continue
            
        log_test(f"Testing: {endpoint['name']}")
        
        try:
            response = requests.get(endpoint["url"], headers=headers, timeout=10)
            
            results[endpoint["name"]] = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "data": None,
                "error": None
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint["name"]]["data"] = data
                    log_test(f"  ✅ {endpoint['name']}: SUCCESS")
                    log_test(f"     Data: {json.dumps(data, indent=6)[:200]}...")
                except json.JSONDecodeError:
                    log_test(f"  ⚠️ {endpoint['name']}: Invalid JSON response", "WARNING")
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {response.text[:100]}"
                
                results[endpoint["name"]]["error"] = error_msg
                log_test(f"  ❌ {endpoint['name']}: {error_msg}", "ERROR")
                
                if endpoint["critical"]:
                    critical_failures.append(endpoint["name"])
        
        except Exception as e:
            results[endpoint["name"]] = {
                "status_code": None,
                "success": False,
                "data": None,
                "error": str(e)
            }
            log_test(f"  ❌ {endpoint['name']}: Exception - {str(e)}", "ERROR")
            
            if endpoint["critical"]:
                critical_failures.append(endpoint["name"])
    
    # Analysis
    log_test("=" * 80)
    log_test("📊 ANALYSIS RESULTS")
    log_test("=" * 80)
    
    if critical_failures:
        log_test(f"🚨 CRITICAL FAILURES: {critical_failures}", "ERROR")
        log_test("These failures would cause the ClientHome data to be null", "ERROR")
    else:
        log_test("✅ All critical endpoints working")
    
    # Check for specific issues that could cause null data
    home_data = results.get("Main Home Data", {}).get("data")
    if home_data is None:
        log_test("🚨 FOUND THE ISSUE: /api/home/client returned null data!", "ERROR")
        log_test("This explains why ClientHome shows skeleton loader", "ERROR")
    elif not home_data:
        log_test("🚨 FOUND THE ISSUE: /api/home/client returned empty data!", "ERROR")
        log_test("This explains why ClientHome shows skeleton loader", "ERROR")
    else:
        log_test("✅ /api/home/client returned valid data")
        log_test("The issue might be in frontend error handling or async loading")
    
    # Check for common async loading issues
    log_test("🔍 Checking for potential async loading issues:")
    
    failed_endpoints = [name for name, result in results.items() if not result["success"]]
    if failed_endpoints:
        log_test(f"⚠️ Failed endpoints that might cause async errors: {failed_endpoints}", "WARNING")
        log_test("Frontend might be failing due to these errors in useEffect", "WARNING")
    
    return len(critical_failures) == 0

def test_frontend_error_scenarios():
    """Test scenarios that might cause frontend to set data to null"""
    
    log_test("🔍 Testing frontend error scenarios")
    
    # Test with invalid token
    log_test("Testing with invalid token...")
    invalid_headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/home/client", headers=invalid_headers, timeout=10)
        log_test(f"Invalid token response: {response.status_code}")
        
        if response.status_code == 401:
            log_test("✅ Proper 401 response for invalid token")
        else:
            log_test(f"⚠️ Unexpected response for invalid token: {response.status_code}", "WARNING")
    
    except Exception as e:
        log_test(f"❌ Error testing invalid token: {str(e)}", "ERROR")
    
    # Test network timeout scenario
    log_test("Testing network timeout scenario...")
    try:
        response = requests.get(f"{BACKEND_URL}/home/client", timeout=0.001)
    except requests.exceptions.Timeout:
        log_test("✅ Timeout properly handled")
    except Exception as e:
        log_test(f"Network error: {str(e)}")

def main():
    """Main test function"""
    
    log_test("=" * 80)
    log_test("🚨 COMPREHENSIVE CLIENT HOME DIAGNOSTIC")
    log_test("Investigating why ClientHome dashboard shows blank/empty content")
    log_test("=" * 80)
    
    success = test_all_client_home_endpoints()
    test_frontend_error_scenarios()
    
    log_test("=" * 80)
    log_test("🎯 DIAGNOSTIC SUMMARY")
    log_test("=" * 80)
    
    if success:
        log_test("✅ All critical backend endpoints are working")
        log_test("🔍 The issue is likely in the frontend:")
        log_test("   1. Check browser console for JavaScript errors")
        log_test("   2. Check if axios requests are failing silently")
        log_test("   3. Check if error handling in useEffect is setting data to null")
        log_test("   4. Verify that localStorage 'polaris_me' contains valid user data")
    else:
        log_test("❌ Backend endpoints have critical failures")
        log_test("🔧 Fix these backend issues to resolve the blank dashboard")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)