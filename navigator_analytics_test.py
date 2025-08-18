#!/usr/bin/env python3
"""
Navigator Analytics Endpoint Testing
Tests the new Navigator analytics endpoint as per review request:
1) Login as navigator (create if needed) to get token
2) POST a few analytics/resource-access logs as a client user, then GET /api/navigator/analytics/resources?since_days=30 as navigator
3) Expect JSON with fields: since, total (>= count of posted items), by_area array with area_id/count pairs, last7 array
"""

import requests
import json
import uuid
import os
from pathlib import Path
from datetime import datetime, timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Navigator Analytics at: {API_BASE}")

def create_or_login_navigator():
    """Create navigator user if needed, then login to get token"""
    print("\n=== Step 1: Navigator Authentication ===")
    
    # Try to login first with a known navigator account
    navigator_email = "navigator_test@cybersec.com"
    navigator_password = "TestPass123!"
    
    login_data = {
        "email": navigator_email,
        "password": navigator_password
    }
    
    try:
        # Try login first
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Navigator login successful")
            return token
        elif response.status_code == 400:
            print("Navigator doesn't exist, creating new one...")
            
            # Create navigator user
            register_data = {
                "email": navigator_email,
                "password": navigator_password,
                "role": "navigator",
                "terms_accepted": True
            }
            
            reg_response = requests.post(f"{API_BASE}/auth/register", json=register_data)
            print(f"Registration status: {reg_response.status_code}")
            
            if reg_response.status_code == 200:
                # Now login
                login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    print(f"✅ Navigator created and logged in successfully")
                    return token
                else:
                    print(f"❌ Login after registration failed: {login_response.status_code}")
                    return None
            else:
                print(f"❌ Navigator registration failed: {reg_response.status_code} - {reg_response.text}")
                return None
        else:
            print(f"❌ Navigator login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Navigator auth error: {e}")
        return None

def create_agency_and_generate_license():
    """Create agency user and generate license codes for client registration"""
    print("\n=== Step 2A: Agency Setup for License Generation ===")
    
    agency_email = "agency_test@cybersec.com"
    agency_password = "TestPass123!"
    
    # Try to login first
    login_data = {
        "email": agency_email,
        "password": agency_password
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Agency login successful")
            return token
        elif response.status_code == 400:
            print("Agency doesn't exist, creating new one...")
            
            # Create agency user
            register_data = {
                "email": agency_email,
                "password": agency_password,
                "role": "agency",
                "terms_accepted": True
            }
            
            reg_response = requests.post(f"{API_BASE}/auth/register", json=register_data)
            print(f"Agency registration status: {reg_response.status_code}")
            
            if reg_response.status_code == 200:
                print("⚠️ Agency created but needs approval. Using navigator to approve...")
                # For testing, we'll skip the approval process and try direct license creation
                return None
            else:
                print(f"❌ Agency registration failed: {reg_response.text}")
                return None
        else:
            print(f"❌ Agency login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Agency auth error: {e}")
        return None

def create_or_login_client():
    """Create client user if needed, then login to get token"""
    print("\n=== Step 2B: Client Authentication ===")
    
    # Try to use existing client from test_result.md
    client_email = "client_5ffe6e03@cybersec.com"
    client_password = "TestPass123!"
    
    login_data = {
        "email": client_email,
        "password": client_password
    }
    
    try:
        # Try login first with existing client
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Client login successful with existing account")
            return token
        else:
            print(f"❌ Existing client login failed: {response.status_code}")
            print("⚠️ Cannot create new client without valid license codes")
            print("⚠️ Will use navigator token to directly insert analytics data for testing")
            return None
            
    except Exception as e:
        print(f"❌ Client auth error: {e}")
        return None

def post_analytics_logs(client_token, navigator_token):
    """POST several analytics/resource-access logs as client user, or use navigator if client unavailable"""
    print("\n=== Step 3: Posting Analytics Logs ===")
    
    # Use client token if available, otherwise use navigator token for testing
    if client_token:
        headers = {"Authorization": f"Bearer {client_token}"}
        print("Using client token for analytics logging")
    else:
        headers = {"Authorization": f"Bearer {navigator_token}"}
        print("⚠️ Using navigator token for analytics logging (client unavailable)")
    
    # Test data for different areas
    test_logs = [
        {"resource_id": "res_001", "gap_area": "area1"},  # Business Formation
        {"resource_id": "res_002", "gap_area": "area1"},  # Business Formation (duplicate area)
        {"resource_id": "res_003", "gap_area": "area2"},  # Financial Operations
        {"resource_id": "res_004", "gap_area": "area5"},  # Technology & Security
        {"resource_id": "res_005", "gap_area": "area5"},  # Technology & Security (duplicate area)
    ]
    
    posted_count = 0
    
    for i, log_data in enumerate(test_logs, 1):
        try:
            response = requests.post(f"{API_BASE}/analytics/resource-access", json=log_data, headers=headers)
            print(f"Log {i} - Status: {response.status_code} - Area: {log_data['gap_area']}")
            
            if response.status_code == 200:
                posted_count += 1
                print(f"  ✅ Successfully posted log {i}")
            else:
                print(f"  ❌ Failed to post log {i}: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error posting log {i}: {e}")
    
    print(f"\nPosted {posted_count}/{len(test_logs)} analytics logs successfully")
    return posted_count

def test_navigator_analytics(navigator_token, expected_minimum_count):
    """GET /api/navigator/analytics/resources as navigator and validate response"""
    print("\n=== Step 4: Testing Navigator Analytics Endpoint ===")
    
    headers = {"Authorization": f"Bearer {navigator_token}"}
    
    try:
        # Test with default 30 days
        response = requests.get(f"{API_BASE}/navigator/analytics/resources?since_days=30", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        print(f"Response received: {json.dumps(data, indent=2, default=str)}")
        
        # Validate required fields
        required_fields = ["since", "total", "by_area", "last7"]
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ FAIL: Missing required fields: {missing_fields}")
            return False
        
        print("✅ All required fields present")
        
        # Validate field types and values
        total = data.get("total", 0)
        by_area = data.get("by_area", [])
        last7 = data.get("last7", [])
        
        print(f"Total count: {total}")
        print(f"Expected minimum: {expected_minimum_count}")
        
        if total < expected_minimum_count:
            print(f"❌ FAIL: Total count {total} is less than expected minimum {expected_minimum_count}")
            return False
        
        print("✅ Total count meets minimum requirement")
        
        # Validate by_area structure
        if not isinstance(by_area, list):
            print(f"❌ FAIL: by_area should be an array, got {type(by_area)}")
            return False
        
        print(f"by_area contains {len(by_area)} entries:")
        area_total = 0
        for area in by_area:
            if not isinstance(area, dict):
                print(f"❌ FAIL: by_area entry should be object, got {type(area)}")
                return False
            
            area_id = area.get("area_id")
            count = area.get("count", 0)
            area_name = area.get("area_name", "Unknown")
            
            print(f"  - {area_id} ({area_name}): {count}")
            area_total += count
        
        if area_total != total:
            print(f"❌ FAIL: Sum of area counts ({area_total}) doesn't match total ({total})")
            return False
        
        print("✅ by_area structure and counts are valid")
        
        # Validate last7 structure
        if not isinstance(last7, list):
            print(f"❌ FAIL: last7 should be an array, got {type(last7)}")
            return False
        
        print(f"last7 contains {len(last7)} entries:")
        for entry in last7:
            if not isinstance(entry, dict):
                print(f"❌ FAIL: last7 entry should be object, got {type(entry)}")
                return False
            
            date = entry.get("date")
            count = entry.get("count", 0)
            print(f"  - {date}: {count}")
        
        print("✅ last7 structure is valid")
        
        print("\n🎉 PASS: Navigator analytics endpoint working correctly!")
        print(f"Sample output: {json.dumps(data, indent=2, default=str)}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Navigator Analytics Endpoint Test")
    print("=" * 60)
    
    # Step 1: Get navigator token
    navigator_token = create_or_login_navigator()
    if not navigator_token:
        print("❌ OVERALL FAIL: Could not authenticate navigator")
        return False
    
    # Step 2: Try to get client token (optional for this test)
    client_token = create_or_login_client()
    
    # Step 3: Post analytics logs (use client if available, navigator otherwise)
    posted_count = post_analytics_logs(client_token, navigator_token)
    if posted_count == 0:
        print("❌ OVERALL FAIL: Could not post any analytics logs")
        return False
    
    # Step 4: Test navigator analytics endpoint
    success = test_navigator_analytics(navigator_token, posted_count)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 OVERALL PASS: Navigator analytics endpoint test successful!")
    else:
        print("❌ OVERALL FAIL: Navigator analytics endpoint test failed!")
    
    return success

if __name__ == "__main__":
    main()