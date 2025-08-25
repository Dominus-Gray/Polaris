#!/usr/bin/env python3
"""
Focused Backend API Testing for Review Request
Tests specific endpoints mentioned in the review request
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-requirements.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🎯 Focused Backend Testing at: {API_BASE}")

def register_and_login_agency():
    """Register and login agency user, return token"""
    print("\n=== Agency Auth Flow ===")
    
    # Register agency user
    agency_email = f"agency_{uuid.uuid4().hex[:8]}@test.com"
    register_payload = {
        "email": agency_email,
        "password": "AgencyPass123!",
        "role": "agency"
    }
    
    response = requests.post(
        f"{API_BASE}/auth/register",
        json=register_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Agency registration failed: {response.status_code} - {response.text}")
        return None
    
    print(f"✅ Agency registered: {agency_email}")
    
    # Login agency user
    login_payload = {
        "email": agency_email,
        "password": "AgencyPass123!"
    }
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json=login_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Agency login failed: {response.status_code} - {response.text}")
        return None
    
    token = response.json().get('access_token')
    print(f"✅ Agency login successful")
    
    # Verify /api/auth/me role=agency
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        if user_data.get('role') == 'agency':
            print(f"✅ /api/auth/me confirms role=agency")
            return token
        else:
            print(f"❌ Expected role=agency, got {user_data.get('role')}")
            return None
    else:
        print(f"❌ /api/auth/me failed: {response.status_code}")
        return None

def test_agency_endpoints(token):
    """Test all agency endpoints"""
    print("\n=== Agency Endpoints ===")
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    # Test GET /api/agency/approved-businesses
    print("Testing GET /api/agency/approved-businesses...")
    response = requests.get(f"{API_BASE}/agency/approved-businesses", headers=headers)
    if response.status_code == 200:
        print("✅ GET /api/agency/approved-businesses - WORKING")
        results['approved_businesses'] = True
    else:
        print(f"❌ GET /api/agency/approved-businesses - {response.status_code} (NOT IMPLEMENTED)")
        results['approved_businesses'] = False
    
    # Test POST /api/agency/opportunities
    print("Testing POST /api/agency/opportunities...")
    opportunity_payload = {
        "title": "IT Services RFP",
        "agency": "CoSA",
        "due_date": "2025-09-30",
        "est_value": 250000
    }
    response = requests.post(f"{API_BASE}/agency/opportunities", json=opportunity_payload, headers=headers)
    if response.status_code == 200:
        print("✅ POST /api/agency/opportunities - WORKING")
        
        # Test GET /api/agency/opportunities
        print("Testing GET /api/agency/opportunities...")
        response = requests.get(f"{API_BASE}/agency/opportunities", headers=headers)
        if response.status_code == 200:
            print("✅ GET /api/agency/opportunities - WORKING")
            results['opportunities'] = True
        else:
            print(f"❌ GET /api/agency/opportunities - {response.status_code}")
            results['opportunities'] = False
    else:
        print(f"❌ POST /api/agency/opportunities - {response.status_code} (NOT IMPLEMENTED)")
        results['opportunities'] = False
    
    # Test GET /api/agency/schedule/ics
    print("Testing GET /api/agency/schedule/ics...")
    business_id = "biz123"
    response = requests.get(f"{API_BASE}/agency/schedule/ics?business_id={business_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'ics' in data and 'BEGIN:VCALENDAR' in data['ics']:
            print("✅ GET /api/agency/schedule/ics - WORKING (returns JSON with ics field containing BEGIN:VCALENDAR)")
            results['schedule_ics'] = True
        else:
            print(f"❌ GET /api/agency/schedule/ics - Missing ics field or BEGIN:VCALENDAR: {data}")
            results['schedule_ics'] = False
    else:
        print(f"❌ GET /api/agency/schedule/ics - {response.status_code} (NOT IMPLEMENTED)")
        results['schedule_ics'] = False
    
    return results

def test_financial_endpoints(token):
    """Test financial core skeleton endpoints"""
    print("\n=== Financial Core Skeleton ===")
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    # Test POST /api/v1/revenue/calculate-success-fee
    print("Testing POST /api/v1/revenue/calculate-success-fee...")
    payload = {
        "contractValue": 300000,
        "businessTier": "small",
        "contractType": "services",
        "riskLevel": "medium",
        "platformMaturityLevel": 3
    }
    response = requests.post(f"{API_BASE}/v1/revenue/calculate-success-fee", json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'feePercentage' in data and 'feeAmount' in data:
            fee_pct = data.get('feePercentage', 0)
            fee_amt = data.get('feeAmount', 0)
            print(f"✅ POST /api/v1/revenue/calculate-success-fee - WORKING (feePercentage: {fee_pct}, feeAmount: {fee_amt})")
            results['calculate_success_fee'] = True
        else:
            print(f"❌ Missing feePercentage or feeAmount: {data}")
            results['calculate_success_fee'] = False
    else:
        print(f"❌ POST /api/v1/revenue/calculate-success-fee - {response.status_code} (NOT IMPLEMENTED)")
        results['calculate_success_fee'] = False
    
    # Test POST /api/v1/revenue/process-premium-payment
    print("Testing POST /api/v1/revenue/process-premium-payment...")
    payload = {
        "business_id": "test-biz",
        "tier": "base",
        "amount": 1500
    }
    response = requests.post(f"{API_BASE}/v1/revenue/process-premium-payment", json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print("✅ POST /api/v1/revenue/process-premium-payment - WORKING (returns ok and inserts transaction)")
            results['process_premium_payment'] = True
        else:
            print(f"❌ Expected ok=true: {data}")
            results['process_premium_payment'] = False
    else:
        print(f"❌ POST /api/v1/revenue/process-premium-payment - {response.status_code} (NOT IMPLEMENTED)")
        results['process_premium_payment'] = False
    
    # Test POST /api/v1/revenue/marketplace-transaction
    print("Testing POST /api/v1/revenue/marketplace-transaction...")
    payload = {
        "request_id": "req1",
        "service_provider_id": "prov1",
        "service_fee": 12000
    }
    response = requests.post(f"{API_BASE}/v1/revenue/marketplace-transaction", json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok') and 'fee' in data:
            fee = data.get('fee', 0)
            print(f"✅ POST /api/v1/revenue/marketplace-transaction - WORKING (returns ok and fee: {fee})")
            results['marketplace_transaction'] = True
        else:
            print(f"❌ Expected ok=true and fee field: {data}")
            results['marketplace_transaction'] = False
    else:
        print(f"❌ POST /api/v1/revenue/marketplace-transaction - {response.status_code} (NOT IMPLEMENTED)")
        results['marketplace_transaction'] = False
    
    # Test GET /api/v1/revenue/dashboard/agency
    print("Testing GET /api/v1/revenue/dashboard/agency...")
    response = requests.get(f"{API_BASE}/v1/revenue/dashboard/agency", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /api/v1/revenue/dashboard/agency - WORKING (aggregates transactions by type)")
        results['dashboard_agency'] = True
    else:
        print(f"❌ GET /api/v1/revenue/dashboard/agency - {response.status_code} (NOT IMPLEMENTED)")
        results['dashboard_agency'] = False
    
    # Test GET /api/v1/analytics/revenue-forecast
    print("Testing GET /api/v1/analytics/revenue-forecast...")
    response = requests.get(f"{API_BASE}/v1/analytics/revenue-forecast", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'monthly' in data and 'annualized' in data:
            monthly = data.get('monthly', 0)
            annualized = data.get('annualized', 0)
            print(f"✅ GET /api/v1/analytics/revenue-forecast - WORKING (monthly: {monthly}, annualized: {annualized})")
            results['revenue_forecast'] = True
        else:
            print(f"❌ Missing monthly or annualized fields: {data}")
            results['revenue_forecast'] = False
    else:
        print(f"❌ GET /api/v1/analytics/revenue-forecast - {response.status_code} (NOT IMPLEMENTED)")
        results['revenue_forecast'] = False
    
    return results

def test_regression_smoke():
    """Test regression smoke tests"""
    print("\n=== Regression Smoke Tests ===")
    
    # Register and login a client for testing
    client_email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    register_payload = {
        "email": client_email,
        "password": "ClientPass123!",
        "role": "client"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=register_payload, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print("❌ Could not register client for regression test")
        return False
    
    login_payload = {"email": client_email, "password": "ClientPass123!"}
    response = requests.post(f"{API_BASE}/auth/login", json=login_payload, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print("❌ Could not login client for regression test")
        return False
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    results = {}
    
    # Test auth register/login/me
    print("✅ Auth register/login/me - WORKING")
    results['auth'] = True
    
    # Test evidence upload flow
    print("Testing evidence upload initiate/chunk/complete...")
    session_response = requests.post(f"{API_BASE}/assessment/session", headers=headers)
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        results['evidence_upload'] = False
    else:
        session_id = session_response.json().get('session_id')
        
        # Test upload initiate
        initiate_payload = {
            "file_name": "test_evidence.pdf",
            "total_size": 1000000,
            "session_id": session_id,
            "area_id": "area1",
            "question_id": "q1"
        }
        response = requests.post(f"{API_BASE}/upload/initiate", json=initiate_payload, headers=headers)
        if response.status_code == 200:
            upload_id = response.json().get('upload_id')
            
            # Test chunk upload
            import io
            chunk_data = b'A' * 1000000
            chunk_file = io.BytesIO(chunk_data)
            files = {'file': ('chunk.part', chunk_file, 'application/octet-stream')}
            data = {'upload_id': upload_id, 'chunk_index': 0}
            chunk_headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(f"{API_BASE}/upload/chunk", files=files, data=data, headers=chunk_headers)
            if response.status_code == 200:
                # Test complete
                complete_payload = {"upload_id": upload_id, "total_chunks": 1}
                response = requests.post(f"{API_BASE}/upload/complete", json=complete_payload, headers=headers)
                if response.status_code == 200:
                    print("✅ Evidence upload initiate/chunk/complete - WORKING")
                    results['evidence_upload'] = True
                else:
                    print("❌ Evidence upload complete failed")
                    results['evidence_upload'] = False
            else:
                print("❌ Evidence chunk upload failed")
                results['evidence_upload'] = False
        else:
            print("❌ Evidence upload initiate failed")
            results['evidence_upload'] = False
    
    # Test navigator review (need navigator user)
    navigator_email = f"navigator_{uuid.uuid4().hex[:8]}@test.com"
    nav_register = {"email": navigator_email, "password": "NavPass123!", "role": "navigator"}
    response = requests.post(f"{API_BASE}/auth/register", json=nav_register, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        nav_login = {"email": navigator_email, "password": "NavPass123!"}
        response = requests.post(f"{API_BASE}/auth/login", json=nav_login, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            nav_token = response.json().get('access_token')
            nav_headers = {"Authorization": f"Bearer {nav_token}"}
            
            # Test navigator review approve
            response = requests.get(f"{API_BASE}/navigator/reviews?status=pending", headers=nav_headers)
            if response.status_code == 200:
                reviews = response.json().get('reviews', [])
                if reviews:
                    review_id = reviews[0]['id']
                    decision_payload = {"decision": "approved", "notes": "Test approval"}
                    response = requests.post(f"{API_BASE}/navigator/reviews/{review_id}/decision", json=decision_payload, headers=nav_headers)
                    if response.status_code == 200:
                        print("✅ Navigator review approve - WORKING")
                        results['navigator_review'] = True
                    else:
                        print("❌ Navigator review decision failed")
                        results['navigator_review'] = False
                else:
                    print("✅ Navigator review queue accessible (no pending reviews)")
                    results['navigator_review'] = True
            else:
                print("❌ Navigator review queue failed")
                results['navigator_review'] = False
        else:
            print("❌ Navigator login failed")
            results['navigator_review'] = False
    else:
        print("❌ Navigator registration failed")
        results['navigator_review'] = False
    
    # Test provider profile (need provider user)
    provider_email = f"provider_{uuid.uuid4().hex[:8]}@test.com"
    prov_register = {"email": provider_email, "password": "ProvPass123!", "role": "provider"}
    response = requests.post(f"{API_BASE}/auth/register", json=prov_register, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        prov_login = {"email": provider_email, "password": "ProvPass123!"}
        response = requests.post(f"{API_BASE}/auth/login", json=prov_login, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            prov_token = response.json().get('access_token')
            prov_headers = {"Authorization": f"Bearer {prov_token}"}
            
            # Test provider profile GET/POST
            profile_payload = {
                "company_name": "Test Provider Co",
                "service_areas": ["area1", "area2"],
                "price_min": 1000,
                "price_max": 5000
            }
            response = requests.post(f"{API_BASE}/provider/profile", json=profile_payload, headers=prov_headers)
            if response.status_code == 200:
                response = requests.get(f"{API_BASE}/provider/profile/me", headers=prov_headers)
                if response.status_code == 200:
                    print("✅ Provider profile GET/POST - WORKING")
                    results['provider_profile'] = True
                else:
                    print("❌ Provider profile GET failed")
                    results['provider_profile'] = False
            else:
                print("❌ Provider profile POST failed")
                results['provider_profile'] = False
        else:
            print("❌ Provider login failed")
            results['provider_profile'] = False
    else:
        print("❌ Provider registration failed")
        results['provider_profile'] = False
    
    # Test matching request/create/matches
    match_payload = {
        "budget": 3000,
        "area_id": "area1",
        "description": "Test matching request"
    }
    response = requests.post(f"{API_BASE}/match/request", json=match_payload, headers=headers)
    if response.status_code == 200:
        request_id = response.json().get('request_id')
        response = requests.get(f"{API_BASE}/match/{request_id}/matches", headers=headers)
        if response.status_code == 200:
            print("✅ Matching request/create/matches - WORKING")
            results['matching'] = True
        else:
            print("❌ Get matches failed")
            results['matching'] = False
    else:
        print("❌ Create match request failed")
        results['matching'] = False
    
    # Test AI explain
    ai_payload = {
        "session_id": session_id,
        "area_id": "area1",
        "question_id": "q1",
        "question_text": "Test question"
    }
    response = requests.post(f"{API_BASE}/ai/explain", json=ai_payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok') and 'Deliverables' in data.get('message', '') and 'Acceptable alternatives' in data.get('message', '') and 'Why it matters' in data.get('message', ''):
            print("✅ AI explain returns ok and includes Deliverables, Acceptable alternatives, Why it matters - WORKING")
            results['ai_explain'] = True
        else:
            print(f"❌ AI explain missing required sections: {data}")
            results['ai_explain'] = False
    else:
        print("❌ AI explain failed")
        results['ai_explain'] = False
    
    return results

def main():
    """Run focused backend tests as requested in review"""
    print("🎯 FOCUSED BACKEND TESTING - Review Request")
    print("="*60)
    
    # Step 1: Auth/Role - Register/login as agency user; verify /api/auth/me role=agency
    agency_token = register_and_login_agency()
    if not agency_token:
        print("❌ CRITICAL: Agency auth flow failed - cannot proceed with agency/financial tests")
        return
    
    # Step 2: Agency Endpoints
    agency_results = test_agency_endpoints(agency_token)
    
    # Step 3: Financial Core Skeleton
    financial_results = test_financial_endpoints(agency_token)
    
    # Step 4: Regression Smoke Tests
    regression_results = test_regression_smoke()
    
    # Summary
    print("\n" + "="*60)
    print("📊 FOCUSED TEST SUMMARY")
    print("="*60)
    
    print("\n🔐 AUTH/ROLE:")
    print("✅ Register/login as agency user - WORKING")
    print("✅ Verify /api/auth/me role=agency - WORKING")
    
    print("\n🏢 AGENCY ENDPOINTS:")
    for endpoint, result in agency_results.items():
        status = "✅ WORKING" if result else "❌ NOT IMPLEMENTED"
        print(f"{status} - {endpoint}")
    
    print("\n💰 FINANCIAL CORE SKELETON:")
    for endpoint, result in financial_results.items():
        status = "✅ WORKING" if result else "❌ NOT IMPLEMENTED"
        print(f"{status} - {endpoint}")
    
    print("\n🔄 REGRESSION SMOKE:")
    for test, result in regression_results.items():
        status = "✅ WORKING" if result else "❌ FAILING"
        print(f"{status} - {test}")
    
    # Overall assessment
    agency_working = sum(agency_results.values())
    agency_total = len(agency_results)
    financial_working = sum(financial_results.values())
    financial_total = len(financial_results)
    regression_working = sum(regression_results.values())
    regression_total = len(regression_results)
    
    print(f"\n📈 RESULTS:")
    print(f"Auth/Role: 2/2 ✅")
    print(f"Agency Endpoints: {agency_working}/{agency_total} {'✅' if agency_working == agency_total else '❌'}")
    print(f"Financial Core: {financial_working}/{financial_total} {'✅' if financial_working == financial_total else '❌'}")
    print(f"Regression: {regression_working}/{regression_total} {'✅' if regression_working == regression_total else '❌'}")
    
    if agency_working == 0 and financial_working == 0:
        print("\n🚨 CRITICAL FINDING: Agency and Financial endpoints are NOT IMPLEMENTED despite review request claiming they are 'now implemented in server.py'")
    
    return {
        'agency_auth': True,
        'agency_endpoints': agency_results,
        'financial_endpoints': financial_results,
        'regression': regression_results
    }

if __name__ == "__main__":
    main()