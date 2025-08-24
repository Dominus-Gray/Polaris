#!/usr/bin/env python3
"""
Focused Backend Testing for Matching Core and Home Dashboard Endpoints
Tests the specific endpoints mentioned in the review request
"""

import requests
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-inspector.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def register_and_login_user(role):
    """Helper function to register and login a user with specified role"""
    print(f"\n=== Registering and logging in {role} user ===")
    
    # Generate unique email
    email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    password = f"{role.title()}Pass123!"
    
    try:
        # Register
        register_payload = {
            "email": email,
            "password": password,
            "role": role
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Registration failed - {response.text}")
            return None, None
        
        print(f"✅ {role.title()} registered: {email}")
        
        # Login
        login_payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Login failed - {response.text}")
            return None, None
        
        token = response.json().get('access_token')
        print(f"✅ {role.title()} logged in successfully")
        return email, token
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def test_client_match_request(client_token):
    """Test POST /api/match/request as client"""
    print("\n=== Testing Client Match Request Creation ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "budget": 1500,
            "payment_pref": "card",
            "timeline": "2 weeks",
            "area_id": "area6",
            "description": "need marketing help"
        }
        
        response = requests.post(
            f"{API_BASE}/match/request",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id') or data.get('id')
            print(f"✅ PASS: Match request created with ID: {request_id}")
            return request_id
        elif response.status_code == 404:
            print("❌ FAIL: Match request endpoint not found (not implemented)")
            return None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_client_get_matches(client_token, request_id):
    """Test GET /api/match/{request_id}/matches as client"""
    print("\n=== Testing Client Get Matches ===")
    
    if not request_id:
        print("⚠️  SKIP: No request_id available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/match/{request_id}/matches",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"✅ PASS: Get matches returned {len(matches)} matches")
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Get matches endpoint not found (not implemented)")
            return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_provider_eligible_requests(provider_token):
    """Test GET /api/match/eligible as provider"""
    print("\n=== Testing Provider Eligible Requests ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/match/eligible",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('requests', [])
            print(f"✅ PASS: Provider eligible requests returned {len(requests_list)} requests")
            
            # Check if any requests have the 'invited' flag
            for req in requests_list:
                if 'invited' in req:
                    print(f"  Request {req.get('id', 'unknown')} - invited: {req.get('invited', False)}")
            
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Provider eligible requests endpoint not found (not implemented)")
            return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_provider_respond(provider_token, request_id):
    """Test POST /api/match/respond as provider"""
    print("\n=== Testing Provider Respond ===")
    
    if not request_id:
        print("⚠️  SKIP: No request_id available")
        return False, None
    
    try:
        headers = {
            "Authorization": f"Bearer {provider_token}"
        }
        
        # Use form-data as specified in the review request
        data = {
            'request_id': request_id,
            'proposal_note': 'I can help with your marketing needs. I have 5+ years experience in digital marketing and can deliver within your timeline.'
        }
        
        response = requests.post(
            f"{API_BASE}/match/respond",
            data=data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            response_id = response_data.get('response_id') or response_data.get('id')
            print(f"✅ PASS: Provider response submitted with ID: {response_id}")
            return True, response_id
        elif response.status_code == 404:
            print("❌ FAIL: Provider respond endpoint not found (not implemented)")
            return False, None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def test_client_get_responses(client_token, request_id):
    """Test GET /api/match/{request_id}/responses as client"""
    print("\n=== Testing Client Get Responses ===")
    
    if not request_id:
        print("⚠️  SKIP: No request_id available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/match/{request_id}/responses",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            responses = data.get('responses', [])
            print(f"✅ PASS: Get responses returned {len(responses)} responses")
            
            # Check if responses contain provider response
            for resp in responses:
                if resp.get('proposal_note'):
                    print(f"  Found response with note: {resp.get('proposal_note')[:50]}...")
            
            return True
        elif response.status_code == 404:
            print("❌ FAIL: Get responses endpoint not found (not implemented)")
            return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_home_client(client_token):
    """Test GET /api/home/client"""
    print("\n=== Testing Home Client Dashboard ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/home/client",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Client dashboard data: {json.dumps(data, indent=2)}")
            
            # Check for required fields
            required_fields = ['readiness', 'has_certificate', 'opportunities', 'profile_complete']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Client home dashboard returns all required fields")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_home_provider(provider_token):
    """Test GET /api/home/provider"""
    print("\n=== Testing Home Provider Dashboard ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/home/provider",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Provider dashboard data: {json.dumps(data, indent=2)}")
            
            # Check for required fields
            required_fields = ['eligible_requests', 'responses', 'profile_complete']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Provider home dashboard returns all required fields")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run focused tests for matching core and home dashboard endpoints"""
    print("🎯 Starting Focused Backend Tests - Matching Core & Home Dashboards")
    print(f"Base URL: {API_BASE}")
    
    results = {}
    
    # Setup users
    print("\n" + "="*60)
    print("SETUP - Creating Test Users")
    print("="*60)
    
    client_email, client_token = register_and_login_user("client")
    provider_email, provider_token = register_and_login_user("provider")
    
    if not client_token or not provider_token:
        print("❌ CRITICAL: Could not create test users. Aborting tests.")
        return False
    
    # Test Matching Core Endpoints
    print("\n" + "="*60)
    print("MATCHING CORE ENDPOINTS")
    print("="*60)
    
    # 1. Client creates match request
    request_id = test_client_match_request(client_token)
    results['client_match_request'] = request_id is not None
    
    # 2. Client gets matches for request
    results['client_get_matches'] = test_client_get_matches(client_token, request_id)
    
    # 3. Provider gets eligible requests
    results['provider_eligible_requests'] = test_provider_eligible_requests(provider_token)
    
    # 4. Provider responds to request
    provider_respond_success, response_id = test_provider_respond(provider_token, request_id)
    results['provider_respond'] = provider_respond_success
    
    # 5. Client gets responses to their request
    results['client_get_responses'] = test_client_get_responses(client_token, request_id)
    
    # Test Home Dashboard Endpoints
    print("\n" + "="*60)
    print("HOME DASHBOARD ENDPOINTS")
    print("="*60)
    
    # 6. Client home dashboard
    results['home_client'] = test_home_client(client_token)
    
    # 7. Provider home dashboard
    results['home_provider'] = test_home_provider(provider_token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 FOCUSED TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print("MATCHING CORE RESULTS:")
    matching_tests = ['client_match_request', 'client_get_matches', 'provider_eligible_requests', 'provider_respond', 'client_get_responses']
    for test_name in matching_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\nHOME DASHBOARD RESULTS:")
    dashboard_tests = ['home_client', 'home_provider']
    for test_name in dashboard_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All focused tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - endpoints may need implementation")
        return False

if __name__ == "__main__":
    main()