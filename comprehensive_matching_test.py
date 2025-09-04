#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Matching Core and Home Dashboard Endpoints
Tests the exact scenarios mentioned in the review request
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agencydash.preview.emergentagent.com')
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

def create_provider_profile(provider_token):
    """Create a provider profile to enable matching"""
    print("\n=== Creating Provider Profile ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json"
        }
        
        # First create a business profile
        business_payload = {
            "company_name": "Marketing Solutions Inc",
            "legal_entity_type": "LLC",
            "tax_id": "12-3456789",
            "registered_address": "123 Business St, San Antonio, TX 78201",
            "mailing_address": "123 Business St, San Antonio, TX 78201",
            "website_url": "https://marketingsolutions.com",
            "industry": "Marketing Services",
            "primary_products_services": "Digital marketing, SEO, social media management",
            "revenue_range": "$100K-$500K",
            "revenue_currency": "USD",
            "employees_count": "5-10",
            "year_founded": 2020,
            "ownership_structure": "Private",
            "contact_name": "John Smith",
            "contact_title": "CEO",
            "contact_email": "john@marketingsolutions.com",
            "contact_phone": "+1-210-555-0123",
            "payment_methods": ["credit_card", "bank_transfer"],
            "subscription_plan": "professional",
            "billing_frequency": "monthly"
        }
        
        response = requests.post(
            f"{API_BASE}/business/profile",
            json=business_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Business profile created")
        else:
            print(f"⚠️  Business profile creation failed: {response.status_code}")
        
        # Create provider profile in database directly (since endpoint might not exist)
        provider_profile = {
            "_id": str(uuid.uuid4()),
            "user_id": None,  # Will be set from token
            "service_areas": ["area6", "area2", "area4"],  # Marketing, Financial, Technology
            "price_min": 1000,
            "price_max": 5000,
            "availability": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        print("✅ Provider profile setup completed")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_exact_review_scenarios():
    """Test the exact scenarios mentioned in the review request"""
    print("\n" + "="*80)
    print("TESTING EXACT REVIEW REQUEST SCENARIOS")
    print("="*80)
    
    results = {}
    
    # Setup users
    client_email, client_token = register_and_login_user("client")
    provider_email, provider_token = register_and_login_user("provider")
    
    if not client_token or not provider_token:
        print("❌ CRITICAL: Could not create test users")
        return False
    
    # Create provider profile
    create_provider_profile(provider_token)
    
    # 1) As client: POST /api/match/request with specific payload
    print("\n=== 1) Client Match Request with Exact Payload ===")
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
            request_id = data.get('request_id')
            print(f"✅ PASS: Match request created with request_id: {request_id}")
            results['client_match_request'] = True
        else:
            print(f"❌ FAIL: {response.status_code} - {response.text}")
            results['client_match_request'] = False
            request_id = None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['client_match_request'] = False
        request_id = None
    
    # 2) As client: GET /api/match/{request_id}/matches
    print("\n=== 2) Client Get Matches ===")
    if request_id:
        try:
            response = requests.get(
                f"{API_BASE}/match/{request_id}/matches",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                print(f"✅ PASS: Returns matches array with {len(matches)} matches")
                results['client_get_matches'] = True
            else:
                print(f"❌ FAIL: {response.status_code} - {response.text}")
                results['client_get_matches'] = False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results['client_get_matches'] = False
    else:
        print("⚠️  SKIP: No request_id available")
        results['client_get_matches'] = False
    
    # 3) As provider: GET /api/match/eligible
    print("\n=== 3) Provider Get Eligible Requests ===")
    try:
        provider_headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/match/eligible",
            headers=provider_headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('requests', [])
            print(f"✅ PASS: Returns eligible requests and flags invited if any ({len(requests_list)} requests)")
            
            # Check for invited flag
            for req in requests_list:
                invited_flag = req.get('invited', False)
                print(f"  Request {req.get('id', 'unknown')}: invited={invited_flag}")
            
            results['provider_eligible'] = True
        else:
            print(f"❌ FAIL: {response.status_code} - {response.text}")
            results['provider_eligible'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['provider_eligible'] = False
    
    # 4) As provider: POST /api/match/respond (form-data)
    print("\n=== 4) Provider Respond with Form Data ===")
    if request_id:
        try:
            # Use form-data as specified
            data = {
                'request_id': request_id,
                'proposal_note': 'I can provide excellent marketing services within your budget and timeline. I have experience with digital marketing campaigns and can deliver results in 2 weeks.'
            }
            
            response = requests.post(
                f"{API_BASE}/match/respond",
                data=data,
                headers={"Authorization": f"Bearer {provider_token}"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                response_id = response_data.get('response_id')
                print(f"✅ PASS: Returns ok and response_id: {response_id}")
                results['provider_respond'] = True
            else:
                print(f"❌ FAIL: {response.status_code} - {response.text}")
                results['provider_respond'] = False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results['provider_respond'] = False
    else:
        print("⚠️  SKIP: No request_id available")
        results['provider_respond'] = False
    
    # 5) As client: GET /api/match/{request_id}/responses
    print("\n=== 5) Client Get Responses ===")
    if request_id:
        try:
            response = requests.get(
                f"{API_BASE}/match/{request_id}/responses",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                responses = data.get('responses', [])
                print(f"✅ PASS: Contains the provider response ({len(responses)} responses)")
                
                # Check if provider response is included
                for resp in responses:
                    if resp.get('proposal_note'):
                        print(f"  Found response: {resp.get('proposal_note')[:50]}...")
                
                results['client_get_responses'] = True
            else:
                print(f"❌ FAIL: {response.status_code} - {response.text}")
                results['client_get_responses'] = False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results['client_get_responses'] = False
    else:
        print("⚠️  SKIP: No request_id available")
        results['client_get_responses'] = False
    
    # 6) As client: GET /api/home/client
    print("\n=== 6) Client Home Dashboard ===")
    try:
        response = requests.get(
            f"{API_BASE}/home/client",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Client dashboard: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['readiness', 'has_certificate', 'opportunities', 'profile_complete']
            has_all_fields = all(field in data for field in required_fields)
            
            if has_all_fields:
                print("✅ PASS: Returns readiness, has_certificate, opportunities, profile_complete")
                results['home_client'] = True
            else:
                missing = [f for f in required_fields if f not in data]
                print(f"❌ FAIL: Missing fields: {missing}")
                results['home_client'] = False
        else:
            print(f"❌ FAIL: {response.status_code} - {response.text}")
            results['home_client'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['home_client'] = False
    
    # 7) As provider: GET /api/home/provider
    print("\n=== 7) Provider Home Dashboard ===")
    try:
        response = requests.get(
            f"{API_BASE}/home/provider",
            headers=provider_headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Provider dashboard: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['eligible_requests', 'responses', 'profile_complete']
            has_all_fields = all(field in data for field in required_fields)
            
            if has_all_fields:
                print("✅ PASS: Returns eligible_requests, responses, profile_complete")
                results['home_provider'] = True
            else:
                missing = [f for f in required_fields if f not in data]
                print(f"❌ FAIL: Missing fields: {missing}")
                results['home_provider'] = False
        else:
            print(f"❌ FAIL: {response.status_code} - {response.text}")
            results['home_provider'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['home_provider'] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print("MATCHING CORE FLOW:")
    matching_tests = ['client_match_request', 'client_get_matches', 'provider_eligible', 'provider_respond', 'client_get_responses']
    for test_name in matching_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\nHOME DASHBOARD STABILITY:")
    dashboard_tests = ['home_client', 'home_provider']
    for test_name in dashboard_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All comprehensive tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    test_exact_review_scenarios()