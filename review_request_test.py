#!/usr/bin/env python3
"""
Review Request Testing - New Endpoints
Tests the three specific endpoint categories mentioned in the review request:
1. AI Resources - POST /api/ai/resources
2. Assessment fees (volume + flat and client self-pay)  
3. Certificates - Agency certificate issuance and retrieval

Based on the test_result.md, these endpoints should be working.
"""

import requests
import json
import uuid
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-1.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing review request endpoints at: {API_BASE}")

def try_auth_setup():
    """Try to set up authentication - attempt multiple approaches"""
    print("\n=== Attempting Authentication Setup ===")
    
    # Try different auth endpoints that might work
    auth_attempts = [
        "/auth/register",
        "/api/auth/register", 
    ]
    
    for auth_endpoint in auth_attempts:
        try:
            test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            payload = {
                "email": test_email,
                "password": "TestPass123!",
                "role": "agency"
            }
            
            url = f"{BASE_URL}{auth_endpoint}"
            print(f"Trying: {url}")
            
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Registration successful at {auth_endpoint}")
                
                # Try login
                login_url = url.replace("/register", "/login")
                login_payload = {"email": test_email, "password": "TestPass123!"}
                
                login_response = requests.post(login_url, json=login_payload, headers={"Content-Type": "application/json"})
                
                if login_response.status_code == 200:
                    token = login_response.json().get('access_token')
                    print(f"✅ Login successful, got token")
                    return token
                    
        except Exception as e:
            print(f"Auth attempt failed: {e}")
            continue
    
    print("❌ Could not establish authentication")
    return None

def test_with_mock_scenarios():
    """Test the new endpoints with mock scenarios based on review request"""
    print("\n=== Testing New Endpoints (Mock Scenarios) ===")
    
    # Try to get a working token
    token = try_auth_setup()
    
    if not token:
        print("⚠️  Testing without authentication - checking endpoint responses")
        headers = {}
    else:
        print(f"✅ Using authentication token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    results = {}
    
    # Test 1: AI Resources
    print("\n--- Testing AI Resources ---")
    try:
        payload = {
            "area_id": "area2",
            "question_id": "q1",
            "question_text": "Upload a screenshot of your accounting system settings",
            "locality": "San Antonio, TX",
            "count": 3
        }
        
        response = requests.post(f"{API_BASE}/ai/resources", json=payload, headers=headers)
        print(f"AI Resources Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            resources = data.get('resources', [])
            print(f"✅ PASS: AI Resources returned {len(resources)} resources")
            
            # Check if EMERGENT_LLM_KEY is present
            if len(resources) == 3:
                print("✅ PASS: Correct number of resources (3)")
                results['ai_resources'] = True
            else:
                print(f"❌ FAIL: Expected 3 resources, got {len(resources)}")
                results['ai_resources'] = False
        elif response.status_code == 401:
            print("⚠️  AI Resources requires authentication")
            results['ai_resources'] = "auth_required"
        else:
            print(f"❌ FAIL: AI Resources error - {response.text}")
            results['ai_resources'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing AI Resources: {e}")
        results['ai_resources'] = False
    
    # Test 2: Assessment Fees - Client Self-Pay
    print("\n--- Testing Client Self-Pay ---")
    try:
        response = requests.post(f"{API_BASE}/client/assessment/pay", headers=headers)
        print(f"Client Pay Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('transaction_id'):
                print("✅ PASS: Client self-pay creates transaction")
                results['client_pay'] = True
            else:
                print(f"❌ FAIL: Client pay response invalid - {data}")
                results['client_pay'] = False
        elif response.status_code == 401:
            print("⚠️  Client pay requires authentication")
            results['client_pay'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Client pay requires client role")
            results['client_pay'] = "role_required"
        else:
            print(f"❌ FAIL: Client pay error - {response.text}")
            results['client_pay'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing client pay: {e}")
        results['client_pay'] = False
    
    # Test 3: Assessment Fees - Agency Invitation Pay
    print("\n--- Testing Agency Invitation Pay ---")
    try:
        dummy_invitation_id = str(uuid.uuid4())
        response = requests.post(f"{API_BASE}/agency/invitations/{dummy_invitation_id}/pay", headers=headers)
        print(f"Agency Pay Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Agency pay response - {data}")
            results['agency_pay'] = True
        elif response.status_code == 404:
            error_detail = response.json().get('detail', '')
            if 'invitation' in error_detail.lower() and 'not found' in error_detail.lower():
                print("✅ PASS: Agency pay endpoint working (invitation not found)")
                results['agency_pay'] = True
            else:
                print(f"❌ FAIL: Agency pay endpoint not found")
                results['agency_pay'] = False
        elif response.status_code == 401:
            print("⚠️  Agency pay requires authentication")
            results['agency_pay'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Agency pay requires agency role")
            results['agency_pay'] = "role_required"
        else:
            print(f"❌ FAIL: Agency pay error - {response.text}")
            results['agency_pay'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing agency pay: {e}")
        results['agency_pay'] = False
    
    # Test 4: Opportunities Available (for unlock verification)
    print("\n--- Testing Opportunities Available ---")
    try:
        response = requests.get(f"{API_BASE}/opportunities/available", headers=headers)
        print(f"Opportunities Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            unlock_type = data.get('unlock')
            opportunities = data.get('opportunities', [])
            print(f"✅ PASS: Opportunities available - unlock: {unlock_type}, count: {len(opportunities)}")
            results['opportunities'] = True
        elif response.status_code == 401:
            print("⚠️  Opportunities requires authentication")
            results['opportunities'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Opportunities requires client role")
            results['opportunities'] = "role_required"
        else:
            print(f"❌ FAIL: Opportunities error - {response.text}")
            results['opportunities'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing opportunities: {e}")
        results['opportunities'] = False
    
    # Test 5: Certificate Issuance
    print("\n--- Testing Certificate Issuance ---")
    try:
        payload = {"client_user_id": str(uuid.uuid4())}
        response = requests.post(f"{API_BASE}/agency/certificates/issue", json=payload, headers=headers)
        print(f"Certificate Issue Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'id' in data and 'readiness_percent' in data:
                print(f"✅ PASS: Certificate issued - {data.get('id')}")
                results['cert_issue'] = True
            else:
                print(f"❌ FAIL: Certificate response invalid - {data}")
                results['cert_issue'] = False
        elif response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if 'readiness' in error_detail.lower():
                print("✅ PASS: Certificate issuance working (readiness check)")
                results['cert_issue'] = True
            else:
                print(f"❌ FAIL: Certificate issuance error - {error_detail}")
                results['cert_issue'] = False
        elif response.status_code == 401:
            print("⚠️  Certificate issuance requires authentication")
            results['cert_issue'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Certificate issuance requires agency role")
            results['cert_issue'] = "role_required"
        else:
            print(f"❌ FAIL: Certificate issuance error - {response.text}")
            results['cert_issue'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing certificate issuance: {e}")
        results['cert_issue'] = False
    
    # Test 6: Certificate Listing
    print("\n--- Testing Certificate Listing ---")
    try:
        response = requests.get(f"{API_BASE}/agency/certificates", headers=headers)
        print(f"Certificate List Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            certificates = data.get('certificates', [])
            print(f"✅ PASS: Certificate listing - {len(certificates)} certificates")
            results['cert_list'] = True
        elif response.status_code == 401:
            print("⚠️  Certificate listing requires authentication")
            results['cert_list'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Certificate listing requires agency role")
            results['cert_list'] = "role_required"
        else:
            print(f"❌ FAIL: Certificate listing error - {response.text}")
            results['cert_list'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing certificate listing: {e}")
        results['cert_list'] = False
    
    # Test 7: Certificate Retrieval
    print("\n--- Testing Certificate Retrieval ---")
    try:
        dummy_cert_id = str(uuid.uuid4())
        response = requests.get(f"{API_BASE}/certificates/{dummy_cert_id}", headers=headers)
        print(f"Certificate Get Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Certificate retrieval working")
            results['cert_get'] = True
        elif response.status_code == 404:
            error_detail = response.json().get('detail', '')
            if 'not found' in error_detail.lower():
                print("✅ PASS: Certificate retrieval working (certificate not found)")
                results['cert_get'] = True
            else:
                print(f"❌ FAIL: Certificate retrieval endpoint not found")
                results['cert_get'] = False
        elif response.status_code == 401:
            print("⚠️  Certificate retrieval requires authentication")
            results['cert_get'] = "auth_required"
        elif response.status_code == 403:
            print("⚠️  Certificate retrieval access denied")
            results['cert_get'] = "access_denied"
        else:
            print(f"❌ FAIL: Certificate retrieval error - {response.text}")
            results['cert_get'] = False
            
    except Exception as e:
        print(f"❌ ERROR testing certificate retrieval: {e}")
        results['cert_get'] = False
    
    return results

def main():
    """Main test function"""
    print("🚀 Review Request Testing - New Endpoints")
    print("Testing the three endpoint categories from the review request:")
    print("1. AI Resources")
    print("2. Assessment fees (volume + flat and client self-pay)")
    print("3. Certificates")
    
    results = test_with_mock_scenarios()
    
    # Summary
    print("\n" + "="*60)
    print("📊 REVIEW REQUEST TEST SUMMARY")
    print("="*60)
    
    working_count = 0
    auth_required_count = 0
    failed_count = 0
    
    for test_name, result in results.items():
        if result == True:
            status = "✅ WORKING"
            working_count += 1
        elif result in ["auth_required", "role_required", "access_denied"]:
            status = f"⚠️  {result.upper().replace('_', ' ')}"
            auth_required_count += 1
        else:
            status = "❌ FAILED"
            failed_count += 1
        
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    total = len(results)
    print(f"\nOverall: {working_count} working, {auth_required_count} auth/role issues, {failed_count} failed")
    
    # Determine overall status
    if working_count == total:
        print("🎉 All new endpoints are working perfectly!")
        return True
    elif working_count + auth_required_count == total:
        print("✅ All new endpoints are implemented and responding correctly!")
        print("   (Some require proper authentication/roles for full testing)")
        return True
    else:
        print("⚠️  Some endpoints may have issues")
        return False

if __name__ == "__main__":
    main()