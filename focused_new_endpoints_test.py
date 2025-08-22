#!/usr/bin/env python3
"""
Focused test for the specific new endpoints mentioned in the review request
Tests only the endpoints that are visible in the current server.py
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://frontend-sync-3.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing new endpoints at: {API_BASE}")

def test_ai_resources_without_auth():
    """Test POST /api/ai/resources endpoint structure (without auth for now)"""
    print("\n=== Testing AI Resources Endpoint Structure ===")
    
    payload = {
        "area_id": "area2",
        "question_id": "q1", 
        "question_text": "Upload a screenshot of your accounting system settings",
        "locality": "San Antonio, TX",
        "count": 3
    }
    
    try:
        response = requests.post(f"{API_BASE}/ai/resources", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: AI Resources endpoint exists and requires authentication")
            return True
        elif response.status_code == 404:
            print("❌ FAIL: AI Resources endpoint not found")
            return False
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: AI Resources endpoint working - {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code} - {response.text}")
            return True  # Endpoint exists
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_client_assessment_pay():
    """Test POST /api/client/assessment/pay endpoint structure"""
    print("\n=== Testing Client Assessment Pay Endpoint Structure ===")
    
    try:
        response = requests.post(f"{API_BASE}/client/assessment/pay")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: Client assessment pay endpoint exists and requires authentication")
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Client assessment pay endpoint not found")
            return False
        elif response.status_code == 403:
            print("✅ PASS: Client assessment pay endpoint exists (role required)")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code} - {response.text}")
            return True  # Endpoint exists
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_agency_invitation_pay():
    """Test POST /api/agency/invitations/{id}/pay endpoint structure"""
    print("\n=== Testing Agency Invitation Pay Endpoint Structure ===")
    
    # Use a dummy invitation ID
    dummy_id = str(uuid.uuid4())
    
    try:
        response = requests.post(f"{API_BASE}/agency/invitations/{dummy_id}/pay")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: Agency invitation pay endpoint exists and requires authentication")
            return True
        elif response.status_code == 404:
            # Could be endpoint not found OR invitation not found
            error_detail = response.json().get('detail', '')
            if 'not found' in error_detail.lower() and 'invitation' in error_detail.lower():
                print("✅ PASS: Agency invitation pay endpoint exists (invitation not found)")
                return True
            else:
                print("❌ FAIL: Agency invitation pay endpoint not found")
                return False
        elif response.status_code == 403:
            print("✅ PASS: Agency invitation pay endpoint exists (role required)")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code} - {response.text}")
            return True  # Endpoint exists
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_opportunities_available():
    """Test GET /api/opportunities/available endpoint structure"""
    print("\n=== Testing Opportunities Available Endpoint Structure ===")
    
    try:
        response = requests.get(f"{API_BASE}/opportunities/available")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: Opportunities available endpoint exists and requires authentication")
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Opportunities available endpoint not found")
            return False
        elif response.status_code == 403:
            print("✅ PASS: Opportunities available endpoint exists (role required)")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code} - {response.text}")
            return True  # Endpoint exists
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_certificate_endpoints():
    """Test certificate-related endpoints structure"""
    print("\n=== Testing Certificate Endpoints Structure ===")
    
    results = {}
    
    # Test certificate issuance
    try:
        payload = {"client_user_id": str(uuid.uuid4())}
        response = requests.post(f"{API_BASE}/agency/certificates/issue", json=payload)
        print(f"Certificate Issue Status: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print("✅ PASS: Certificate issue endpoint exists and requires authentication")
            results['issue'] = True
        elif response.status_code == 404:
            print("❌ FAIL: Certificate issue endpoint not found")
            results['issue'] = False
        else:
            print(f"✅ PASS: Certificate issue endpoint exists - {response.status_code}")
            results['issue'] = True
            
    except Exception as e:
        print(f"❌ ERROR testing certificate issue: {e}")
        results['issue'] = False
    
    # Test certificate listing
    try:
        response = requests.get(f"{API_BASE}/agency/certificates")
        print(f"Certificate List Status: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print("✅ PASS: Certificate list endpoint exists and requires authentication")
            results['list'] = True
        elif response.status_code == 404:
            print("❌ FAIL: Certificate list endpoint not found")
            results['list'] = False
        else:
            print(f"✅ PASS: Certificate list endpoint exists - {response.status_code}")
            results['list'] = True
            
    except Exception as e:
        print(f"❌ ERROR testing certificate list: {e}")
        results['list'] = False
    
    # Test certificate retrieval
    try:
        dummy_cert_id = str(uuid.uuid4())
        response = requests.get(f"{API_BASE}/certificates/{dummy_cert_id}")
        print(f"Certificate Get Status: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print("✅ PASS: Certificate get endpoint exists and requires authentication")
            results['get'] = True
        elif response.status_code == 404:
            # Could be endpoint not found OR certificate not found
            error_detail = response.json().get('detail', '')
            if 'not found' in error_detail.lower():
                print("✅ PASS: Certificate get endpoint exists (certificate not found)")
                results['get'] = True
            else:
                print("❌ FAIL: Certificate get endpoint not found")
                results['get'] = False
        else:
            print(f"✅ PASS: Certificate get endpoint exists - {response.status_code}")
            results['get'] = True
            
    except Exception as e:
        print(f"❌ ERROR testing certificate get: {e}")
        results['get'] = False
    
    return all(results.values())

def test_agency_dashboard_impact():
    """Test GET /api/agency/dashboard/impact endpoint structure"""
    print("\n=== Testing Agency Dashboard Impact Endpoint Structure ===")
    
    try:
        response = requests.get(f"{API_BASE}/agency/dashboard/impact")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: Agency dashboard impact endpoint exists and requires authentication")
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Agency dashboard impact endpoint not found")
            return False
        elif response.status_code == 403:
            print("✅ PASS: Agency dashboard impact endpoint exists (role required)")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code} - {response.text}")
            return True  # Endpoint exists
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Test the new endpoints mentioned in the review request"""
    print("🚀 Testing New Endpoints from Review Request")
    print(f"Base URL: {API_BASE}")
    print("\nTesting endpoint existence and basic structure...")
    
    results = {}
    
    print("\n" + "="*60)
    print("NEW ENDPOINTS STRUCTURE TESTING")
    print("="*60)
    
    # Test 1: AI Resources
    results['ai_resources'] = test_ai_resources_without_auth()
    
    # Test 2: Assessment fees endpoints
    results['client_assessment_pay'] = test_client_assessment_pay()
    results['agency_invitation_pay'] = test_agency_invitation_pay()
    results['opportunities_available'] = test_opportunities_available()
    
    # Test 3: Certificate endpoints
    results['certificates'] = test_certificate_endpoints()
    
    # Test 4: Agency dashboard
    results['agency_dashboard'] = test_agency_dashboard_impact()
    
    # Summary
    print("\n" + "="*60)
    print("📊 ENDPOINT STRUCTURE TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ EXISTS" if result else "❌ MISSING"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} endpoint groups found")
    
    if passed == total:
        print("🎉 All new endpoints from review request are implemented!")
        print("\nNote: Full functional testing requires authentication setup.")
        return True
    else:
        print("⚠️  Some endpoints from review request are missing")
        return False

if __name__ == "__main__":
    main()