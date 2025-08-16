#!/usr/bin/env python3
"""
Regression Test for Financial Endpoints
Focuses on marketplace-transaction 5% fee verification and other financial endpoints
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bizassess-1.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def setup_auth_user(role="client"):
    """Setup authenticated user and return token"""
    print(f"\n=== Setting up {role} user ===")
    try:
        # Generate unique email
        user_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": user_email,
            "password": "TestPass123!",
            "role": role
        }
        
        # Register
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Registration failed - {response.text}")
            return None
            
        print(f"✅ User registered: {user_email}")
        
        # Login
        login_payload = {"email": user_email, "password": "TestPass123!"}
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Login failed - {response.text}")
            return None
            
        token = response.json().get('access_token')
        print(f"✅ Login successful, got token")
        return token
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_marketplace_transaction_5_percent_fee(token):
    """Test POST /api/v1/revenue/marketplace-transaction with 5% fee calculation"""
    print("\n=== Testing Marketplace Transaction 5% Fee ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test with service_fee=2000 -> expected fee=100.0 (5%)
        payload = {
            "request_id": str(uuid.uuid4()),
            "service_provider_id": str(uuid.uuid4()),
            "service_fee": 2000.0
        }
        
        response = requests.post(
            f"{API_BASE}/v1/revenue/marketplace-transaction",
            json=payload,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            expected_fee = 100.0  # 2000 * 0.05 = 100.0
            actual_fee = data.get('fee')
            
            if data.get('ok') and actual_fee == expected_fee:
                print(f"✅ PASS: Marketplace transaction returns correct 5% fee")
                print(f"  Service fee: {payload['service_fee']}")
                print(f"  Expected fee (5%): {expected_fee}")
                print(f"  Actual fee: {actual_fee}")
                return True
            else:
                print(f"❌ FAIL: Expected fee={expected_fee}, got fee={actual_fee}, ok={data.get('ok')}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_calculate_success_fee(token):
    """Test POST /api/v1/revenue/calculate-success-fee"""
    print("\n=== Testing Calculate Success Fee ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "contractValue": 300000.0,
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
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if 'feePercentage' in data and 'feeAmount' in data:
                print(f"✅ PASS: Calculate success fee working")
                print(f"  Contract value: {payload['contractValue']}")
                print(f"  Fee percentage: {data['feePercentage']}%")
                print(f"  Fee amount: ${data['feeAmount']}")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_process_premium_payment(token):
    """Test POST /api/v1/revenue/process-premium-payment"""
    print("\n=== Testing Process Premium Payment ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "business_id": str(uuid.uuid4()),
            "tier": "premium",
            "amount": 1500.0
        }
        
        response = requests.post(
            f"{API_BASE}/v1/revenue/process-premium-payment",
            json=payload,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('ok') and 'transaction_id' in data:
                print(f"✅ PASS: Process premium payment working")
                print(f"  Business ID: {payload['business_id']}")
                print(f"  Amount: ${payload['amount']}")
                print(f"  Transaction ID: {data['transaction_id']}")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_revenue_dashboard(token):
    """Test GET /api/v1/revenue/dashboard/agency"""
    print("\n=== Testing Revenue Dashboard ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/v1/revenue/dashboard/agency", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"✅ PASS: Revenue dashboard working")
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_revenue_forecast(token):
    """Test GET /api/v1/analytics/revenue-forecast"""
    print("\n=== Testing Revenue Forecast ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/v1/analytics/revenue-forecast", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if 'monthly' in data and 'annualized' in data:
                print(f"✅ PASS: Revenue forecast working")
                print(f"  Monthly: ${data['monthly']}")
                print(f"  Annualized: ${data['annualized']}")
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_basic_assessment_flow(token):
    """Test basic assessment flow to ensure it's still functional"""
    print("\n=== Testing Basic Assessment Flow ===")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test schema
        response = requests.get(f"{API_BASE}/assessment/schema", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: Schema endpoint failed - {response.status_code}")
            return False
        
        schema_data = response.json()
        areas = schema_data.get('areas', [])
        if len(areas) != 8:
            print(f"❌ FAIL: Expected 8 areas, got {len(areas)}")
            return False
        
        # Test session creation
        response = requests.post(f"{API_BASE}/assessment/session", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: Session creation failed - {response.status_code}")
            return False
            
        session_data = response.json()
        session_id = session_data.get('session_id')
        
        # Test progress
        response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress", headers=headers)
        if response.status_code != 200:
            print(f"❌ FAIL: Progress endpoint failed - {response.status_code}")
            return False
        
        progress_data = response.json()
        required_fields = ['session_id', 'total_questions', 'answered', 'approved_evidence_answers', 'percent_complete']
        missing_fields = [field for field in required_fields if field not in progress_data]
        
        if missing_fields:
            print(f"❌ FAIL: Progress missing fields: {missing_fields}")
            return False
        
        print(f"✅ PASS: Basic assessment flow working")
        print(f"  Schema: {len(areas)} areas")
        print(f"  Session: {session_id}")
        print(f"  Progress: {progress_data['total_questions']} total questions")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run regression tests focusing on financial endpoints and basic assessment flow"""
    print("🚀 Starting Regression Tests - Financial Endpoints & Basic Assessment")
    print(f"Base URL: {API_BASE}")
    
    results = {}
    
    # Setup authenticated user
    token = setup_auth_user("client")
    if not token:
        print("❌ CRITICAL: Could not setup authenticated user")
        return False
    
    # Test 1: Marketplace Transaction with 5% fee (MAIN FOCUS)
    results['marketplace_transaction_5_percent'] = test_marketplace_transaction_5_percent_fee(token)
    
    # Test 2: Other financial endpoints
    results['calculate_success_fee'] = test_calculate_success_fee(token)
    results['process_premium_payment'] = test_process_premium_payment(token)
    results['revenue_dashboard'] = test_revenue_dashboard(token)
    results['revenue_forecast'] = test_revenue_forecast(token)
    
    # Test 3: Basic assessment flow
    results['basic_assessment_flow'] = test_basic_assessment_flow(token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 REGRESSION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Special focus on marketplace transaction
    if results.get('marketplace_transaction_5_percent'):
        print("\n🎯 KEY REQUIREMENT VERIFIED:")
        print("  ✅ POST /api/v1/revenue/marketplace-transaction uses flat 5% fee")
        print("  ✅ service_fee=2000 -> fee=100.0 (confirmed)")
    else:
        print("\n❌ KEY REQUIREMENT FAILED:")
        print("  ❌ Marketplace transaction 5% fee calculation not working")
    
    if passed == total:
        print("\n🎉 All regression tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    main()