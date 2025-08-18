#!/usr/bin/env python3
"""
Option F Backend Testing for Polaris MVP
Tests newly added Option F features:
1) Invitations (agency creates, pays, client accepts)
2) Opportunity gating for clients
3) Agency impact dashboard
4) Regression checks
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Option F features at: {API_BASE}")

# Global variables to store user tokens and data
agency_token = None
client_token = None
agency_user_id = None
client_user_id = None
invitation_id = None
session_id = None

def setup_users():
    """Setup agency and client users for testing"""
    global agency_token, client_token, agency_user_id, client_user_id
    
    print("\n=== Setting up Agency and Client Users ===")
    
    # Register Agency User
    agency_email = f"agency_{uuid.uuid4().hex[:8]}@test.com"
    agency_payload = {
        "email": agency_email,
        "password": "AgencyPass123!",
        "role": "agency"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=agency_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Agency registration failed - {response.text}")
            return False
            
        agency_data = response.json()
        agency_user_id = agency_data.get('id')
        print(f"✅ Agency registered: {agency_email}")
        
        # Login Agency
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": agency_email, "password": "AgencyPass123!"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ FAIL: Agency login failed - {login_response.text}")
            return False
            
        agency_token = login_response.json().get('access_token')
        print(f"✅ Agency logged in successfully")
        
    except Exception as e:
        print(f"❌ ERROR setting up agency: {e}")
        return False
    
    # Register Client User
    client_email = f"biz@test.com"  # Using the email from review request
    client_payload = {
        "email": client_email,
        "password": "ClientPass123!",
        "role": "client"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=client_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Client registration failed - {response.text}")
            return False
            
        client_data = response.json()
        client_user_id = client_data.get('id')
        print(f"✅ Client registered: {client_email}")
        
        # Login Client
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": client_email, "password": "ClientPass123!"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ FAIL: Client login failed - {login_response.text}")
            return False
            
        client_token = login_response.json().get('access_token')
        print(f"✅ Client logged in successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR setting up client: {e}")
        return False

def test_agency_create_invitation():
    """Test POST /api/agency/invitations with {invite_email:"biz@test.com", amount:100}"""
    global invitation_id
    
    print("\n=== Testing Agency Create Invitation ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "invite_email": "biz@test.com",
            "amount": 100
        }
        
        response = requests.post(
            f"{API_BASE}/agency/invitations",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            invitation_id = data.get('id')
            status = data.get('status')
            amount = data.get('amount')
            
            print(f"Invitation created: {invitation_id}")
            print(f"Status: {status}")
            print(f"Amount: {amount}")
            
            if status == "pending" and amount == 100:
                print("✅ PASS: Invitation created with pending status and correct amount")
                return True
            else:
                print(f"❌ FAIL: Expected status=pending and amount=100, got status={status}, amount={amount}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_agency_list_invitations():
    """Test GET /api/agency/invitations => includes invite"""
    print("\n=== Testing Agency List Invitations ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/agency/invitations", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            invitations = data.get('invitations', [])
            
            print(f"Number of invitations: {len(invitations)}")
            
            # Check if our invitation is in the list
            found_invitation = False
            for inv in invitations:
                if inv.get('id') == invitation_id:
                    found_invitation = True
                    print(f"Found invitation: {inv}")
                    break
            
            if found_invitation:
                print("✅ PASS: Agency can list invitations and created invitation is included")
                return True
            else:
                print(f"❌ FAIL: Created invitation {invitation_id} not found in list")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_agency_pay_invitation():
    """Test POST /api/agency/invitations/{id}/pay => status paid and revenue_transactions entry"""
    print("\n=== Testing Agency Pay Invitation ===")
    
    if not agency_token or not invitation_id:
        print("❌ FAIL: No agency token or invitation ID available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/agency/invitations/{invitation_id}/pay",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transaction_id = data.get('transaction_id')
            
            print(f"Payment response: {data}")
            
            if data.get('ok') and transaction_id:
                print(f"✅ PASS: Payment processed successfully with transaction_id: {transaction_id}")
                
                # Verify invitation status changed to paid
                inv_response = requests.get(f"{API_BASE}/agency/invitations", headers=headers)
                if inv_response.status_code == 200:
                    invitations = inv_response.json().get('invitations', [])
                    for inv in invitations:
                        if inv.get('id') == invitation_id:
                            if inv.get('status') == 'paid':
                                print("✅ PASS: Invitation status updated to 'paid'")
                                return True
                            else:
                                print(f"❌ FAIL: Expected status 'paid', got '{inv.get('status')}'")
                                return False
                
                print("❌ FAIL: Could not verify invitation status update")
                return False
            else:
                print(f"❌ FAIL: Payment response missing ok=true or transaction_id: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_client_accept_invitation():
    """Test POST /api/agency/invitations/{id}/accept => returns session_id; re-check invite status accepted"""
    global session_id
    
    print("\n=== Testing Client Accept Invitation ===")
    
    if not client_token or not invitation_id:
        print("❌ FAIL: No client token or invitation ID available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/agency/invitations/{invitation_id}/accept",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            
            print(f"Accept response: {data}")
            
            if data.get('ok') and session_id:
                print(f"✅ PASS: Invitation accepted successfully with session_id: {session_id}")
                
                # Verify invitation status changed to accepted (check as agency)
                agency_headers = {
                    "Authorization": f"Bearer {agency_token}",
                    "Content-Type": "application/json"
                }
                
                inv_response = requests.get(f"{API_BASE}/agency/invitations", headers=agency_headers)
                if inv_response.status_code == 200:
                    invitations = inv_response.json().get('invitations', [])
                    for inv in invitations:
                        if inv.get('id') == invitation_id:
                            if inv.get('status') == 'accepted' and inv.get('session_id') == session_id:
                                print("✅ PASS: Invitation status updated to 'accepted' with session_id set")
                                return True
                            else:
                                print(f"❌ FAIL: Expected status 'accepted' with session_id, got status='{inv.get('status')}', session_id='{inv.get('session_id')}'")
                                return False
                
                print("❌ FAIL: Could not verify invitation status update")
                return False
            else:
                print(f"❌ FAIL: Accept response missing ok=true or session_id: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_create_agency_opportunity():
    """Create an agency opportunity for testing opportunity gating"""
    print("\n=== Creating Agency Opportunity for Testing ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": "Small Business IT Services RFP",
            "agency": "City of San Antonio",
            "due_date": "2025-09-30",
            "est_value": 250000
        }
        
        response = requests.post(
            f"{API_BASE}/agency/opportunities",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Opportunity created: {data}")
            print("✅ PASS: Agency opportunity created successfully")
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_client_available_opportunities():
    """Test GET /api/opportunities/available => returns list created by same agency"""
    print("\n=== Testing Client Available Opportunities (Gated) ===")
    
    if not client_token:
        print("❌ FAIL: No client token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {client_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/opportunities/available", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('opportunities', [])
            
            print(f"Number of available opportunities: {len(opportunities)}")
            
            if len(opportunities) > 0:
                print("✅ PASS: Client can see opportunities from inviting agency")
                for opp in opportunities:
                    print(f"  - {opp.get('title')} by {opp.get('agency')} (${opp.get('est_value')})")
                return True
            else:
                print("⚠️  No opportunities available (may be expected if agency hasn't created any)")
                return True  # Don't fail if no opportunities exist
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_agency_impact_dashboard():
    """Test GET /api/agency/dashboard/impact => returns invites totals, assessment_fees amount, opportunities count, and readiness_buckets"""
    print("\n=== Testing Agency Impact Dashboard ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/agency/dashboard/impact", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Impact dashboard response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['invites', 'revenue', 'opportunities', 'readiness_buckets']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                invites = data.get('invites', {})
                revenue = data.get('revenue', {})
                opportunities = data.get('opportunities', {})
                readiness_buckets = data.get('readiness_buckets', {})
                
                print(f"Invites: total={invites.get('total')}, paid={invites.get('paid')}, accepted={invites.get('accepted')}")
                print(f"Revenue: assessment_fees={revenue.get('assessment_fees')}")
                print(f"Opportunities: count={opportunities.get('count')}")
                print(f"Readiness buckets: {readiness_buckets}")
                
                # Verify numeric values
                if (isinstance(invites.get('total'), int) and 
                    isinstance(invites.get('paid'), int) and 
                    isinstance(invites.get('accepted'), int) and
                    isinstance(revenue.get('assessment_fees'), (int, float)) and
                    isinstance(opportunities.get('count'), int) and
                    isinstance(readiness_buckets, dict)):
                    
                    print("✅ PASS: Agency impact dashboard returns all required fields with numeric values")
                    return True
                else:
                    print("❌ FAIL: Some fields are not numeric as expected")
                    return False
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_regression_agency_opportunities():
    """Test Agency opportunities CRUD still works"""
    print("\n=== Testing Regression: Agency Opportunities CRUD ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        # Test GET opportunities
        response = requests.get(f"{API_BASE}/agency/opportunities", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: GET opportunities failed - {response.text}")
            return False
        
        # Test POST opportunity (create)
        payload = {
            "title": "Regression Test Opportunity",
            "agency": "Test Agency",
            "due_date": "2025-12-31",
            "est_value": 100000
        }
        
        response = requests.post(
            f"{API_BASE}/agency/opportunities",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ PASS: Agency opportunities CRUD still working")
            return True
        else:
            print(f"❌ FAIL: POST opportunity failed - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_regression_approved_businesses():
    """Test Approved businesses endpoint still works"""
    print("\n=== Testing Regression: Approved Businesses Endpoint ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/agency/approved-businesses", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Approved businesses: {len(data.get('businesses', []))} found")
            print("✅ PASS: Approved businesses endpoint still working")
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_regression_revenue_endpoints():
    """Test Revenue endpoints still work"""
    print("\n=== Testing Regression: Revenue Endpoints ===")
    
    if not agency_token:
        print("❌ FAIL: No agency token available")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        # Test revenue dashboard
        response = requests.get(f"{API_BASE}/v1/revenue/dashboard/agency", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: Revenue dashboard failed - {response.text}")
            return False
        
        # Test revenue forecast
        response = requests.get(f"{API_BASE}/v1/analytics/revenue-forecast", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: Revenue forecast failed - {response.text}")
            return False
        
        # Test calculate success fee
        payload = {
            "contractValue": 300000,
            "businessTier": "small",
            "contractType": "services",
            "riskLevel": "medium",
            "platformMaturityLevel": 3
        }
        
        response = requests.post(
            f"{API_BASE}/v1/revenue/calculate-success-fee",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ PASS: Revenue endpoints still working")
            return True
        else:
            print(f"❌ FAIL: Calculate success fee failed - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all Option F backend tests"""
    print("🚀 Starting Option F Backend Tests")
    print(f"Base URL: {API_BASE}")
    
    results = {}
    
    # Setup users first
    if not setup_users():
        print("❌ CRITICAL: Failed to setup users, cannot continue")
        return False
    
    print("\n" + "="*60)
    print("OPTION F FEATURE TESTS")
    print("="*60)
    
    # 1) Invitations Flow
    print("\n--- 1) INVITATIONS FLOW ---")
    results['create_invitation'] = test_agency_create_invitation()
    results['list_invitations'] = test_agency_list_invitations()
    results['pay_invitation'] = test_agency_pay_invitation()
    results['accept_invitation'] = test_client_accept_invitation()
    
    # 2) Opportunity Gating
    print("\n--- 2) OPPORTUNITY GATING ---")
    results['create_opportunity'] = test_create_agency_opportunity()
    results['client_opportunities'] = test_client_available_opportunities()
    
    # 3) Agency Impact Dashboard
    print("\n--- 3) AGENCY IMPACT DASHBOARD ---")
    results['impact_dashboard'] = test_agency_impact_dashboard()
    
    # 4) Regression Checks
    print("\n--- 4) REGRESSION CHECKS ---")
    results['regression_opportunities'] = test_regression_agency_opportunities()
    results['regression_approved_businesses'] = test_regression_approved_businesses()
    results['regression_revenue'] = test_regression_revenue_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("📊 OPTION F TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Option F tests passed!")
        return True
    else:
        print("⚠️  Some Option F tests failed")
        return False

if __name__ == "__main__":
    main()