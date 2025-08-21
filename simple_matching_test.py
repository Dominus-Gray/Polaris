#!/usr/bin/env python3
"""
Simple Backend Testing for Matching Core and Home Dashboard Endpoints
Tests the exact scenarios mentioned in the review request without complex setup
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sbap-platform.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def register_and_login_user(role):
    """Helper function to register and login a user with specified role"""
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
        return email, token
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, None

def main():
    """Test the exact scenarios from the review request"""
    print("🎯 Testing Review Request Scenarios")
    print("="*60)
    
    results = {}
    
    # Setup users
    print("Setting up test users...")
    client_email, client_token = register_and_login_user("client")
    provider_email, provider_token = register_and_login_user("provider")
    
    if not client_token or not provider_token:
        print("❌ CRITICAL: Could not create test users")
        return False
    
    print(f"✅ Client: {client_email}")
    print(f"✅ Provider: {provider_email}")
    
    # 1) As client: POST /api/match/request with exact payload from review request
    print("\n1) Client Match Request with exact payload:")
    print("   POST /api/match/request with {budget:1500, payment_pref:'card', timeline:'2 weeks', area_id:'area6', description:'need marketing help'}")
    
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
        
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            print(f"   ✅ PASS: Returns request_id: {request_id}")
            results['client_match_request'] = True
        else:
            print(f"   ❌ FAIL: {response.status_code} - {response.text}")
            results['client_match_request'] = False
            request_id = None
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['client_match_request'] = False
        request_id = None
    
    # 2) As client: GET /api/match/{request_id}/matches
    print("\n2) Client Get Matches:")
    print("   GET /api/match/{request_id}/matches -> returns matches array")
    
    if request_id:
        try:
            response = requests.get(
                f"{API_BASE}/match/{request_id}/matches",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                print(f"   ✅ PASS: Returns matches array with {len(matches)} matches")
                results['client_get_matches'] = True
            else:
                print(f"   ❌ FAIL: {response.status_code} - {response.text}")
                results['client_get_matches'] = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results['client_get_matches'] = False
    else:
        print("   ⚠️  SKIP: No request_id available")
        results['client_get_matches'] = False
    
    # 3) As provider: GET /api/match/eligible
    print("\n3) Provider Get Eligible Requests:")
    print("   GET /api/match/eligible -> returns eligible requests and flags invited if any")
    
    try:
        provider_headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/match/eligible",
            headers=provider_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('requests', [])
            print(f"   ✅ PASS: Returns eligible requests ({len(requests_list)} requests)")
            
            # Check for invited flag
            for req in requests_list:
                invited_flag = req.get('invited', False)
                print(f"     Request {req.get('id', 'unknown')}: invited={invited_flag}")
            
            results['provider_eligible'] = True
        else:
            print(f"   ❌ FAIL: {response.status_code} - {response.text}")
            results['provider_eligible'] = False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['provider_eligible'] = False
    
    # 4) As provider: POST /api/match/respond (form-data)
    print("\n4) Provider Respond:")
    print("   POST /api/match/respond (form-data: request_id, proposal_note) -> returns ok and response_id")
    
    if request_id:
        try:
            # Use form-data as specified in review request
            data = {
                'request_id': request_id,
                'proposal_note': 'I can provide excellent marketing services within your budget and timeline.'
            }
            
            response = requests.post(
                f"{API_BASE}/match/respond",
                data=data,
                headers={"Authorization": f"Bearer {provider_token}"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                response_id = response_data.get('response_id')
                ok_status = response_data.get('ok')
                print(f"   ✅ PASS: Returns ok={ok_status} and response_id={response_id}")
                results['provider_respond'] = True
            else:
                print(f"   ❌ FAIL: {response.status_code} - {response.text}")
                results['provider_respond'] = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results['provider_respond'] = False
    else:
        print("   ⚠️  SKIP: No request_id available")
        results['provider_respond'] = False
    
    # 5) As client: GET /api/match/{request_id}/responses
    print("\n5) Client Get Responses:")
    print("   GET /api/match/{request_id}/responses -> contains the provider response")
    
    if request_id:
        try:
            response = requests.get(
                f"{API_BASE}/match/{request_id}/responses",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                responses = data.get('responses', [])
                print(f"   ✅ PASS: Contains provider response ({len(responses)} responses)")
                
                # Show response details
                for resp in responses:
                    if resp.get('proposal_note'):
                        print(f"     Response: {resp.get('proposal_note')[:50]}...")
                
                results['client_get_responses'] = True
            else:
                print(f"   ❌ FAIL: {response.status_code} - {response.text}")
                results['client_get_responses'] = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results['client_get_responses'] = False
    else:
        print("   ⚠️  SKIP: No request_id available")
        results['client_get_responses'] = False
    
    # 6) As client: GET /api/home/client
    print("\n6) Client Home Dashboard:")
    print("   GET /api/home/client -> returns readiness, has_certificate, opportunities, profile_complete")
    
    try:
        response = requests.get(
            f"{API_BASE}/home/client",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['readiness', 'has_certificate', 'opportunities', 'profile_complete']
            has_all_fields = all(field in data for field in required_fields)
            
            if has_all_fields:
                print(f"   ✅ PASS: Returns all required fields")
                print(f"     readiness: {data['readiness']}")
                print(f"     has_certificate: {data['has_certificate']}")
                print(f"     opportunities: {data['opportunities']}")
                print(f"     profile_complete: {data['profile_complete']}")
                results['home_client'] = True
            else:
                missing = [f for f in required_fields if f not in data]
                print(f"   ❌ FAIL: Missing fields: {missing}")
                results['home_client'] = False
        else:
            print(f"   ❌ FAIL: {response.status_code} - {response.text}")
            results['home_client'] = False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['home_client'] = False
    
    # 7) As provider: GET /api/home/provider
    print("\n7) Provider Home Dashboard:")
    print("   GET /api/home/provider -> returns eligible_requests, responses, profile_complete")
    
    try:
        response = requests.get(
            f"{API_BASE}/home/provider",
            headers=provider_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['eligible_requests', 'responses', 'profile_complete']
            has_all_fields = all(field in data for field in required_fields)
            
            if has_all_fields:
                print(f"   ✅ PASS: Returns all required fields")
                print(f"     eligible_requests: {data['eligible_requests']}")
                print(f"     responses: {data['responses']}")
                print(f"     profile_complete: {data['profile_complete']}")
                results['home_provider'] = True
            else:
                missing = [f for f in required_fields if f not in required_fields]
                print(f"   ❌ FAIL: Missing fields: {missing}")
                results['home_provider'] = False
        else:
            print(f"   ❌ FAIL: {response.status_code} - {response.text}")
            results['home_provider'] = False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results['home_provider'] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    test_names = [
        'client_match_request',
        'client_get_matches', 
        'provider_eligible',
        'provider_respond',
        'client_get_responses',
        'home_client',
        'home_provider'
    ]
    
    for test_name in test_names:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All review request scenarios working!")
        return True
    else:
        print("⚠️  Some scenarios failed")
        return False

if __name__ == "__main__":
    main()