#!/usr/bin/env python3
"""
E2E Backend Testing for Polaris Approval and License Flow
Tests the complete approval and license workflow as specified in review request
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing E2E Approval and License Flow at: {API_BASE}")

class TestCredentials:
    """Store test credentials for reuse"""
    def __init__(self):
        # Generate unique emails for this test run
        unique_id = uuid.uuid4().hex[:8]
        self.navigator_email = f"navigator_qa_{unique_id}@example.com"
        self.navigator_password = "NavigatorPass123!"
        self.navigator_token = None
        
        self.agency_email = f"agency_qa_{unique_id}@example.com"
        self.agency_password = "AgencyPass123!"
        self.agency_token = None
        
        self.client_email = None
        self.client_password = "ClientPass123!"
        self.client_token = None
        self.client_license_code = None
        
        self.provider_email = None
        self.provider_password = "ProviderPass123!"
        self.provider_token = None

def create_or_login_user(email, password, role, terms_accepted=True, license_code=None):
    """Create user if not exists, then login and return token"""
    print(f"\n=== Creating/Login User: {email} ({role}) ===")
    
    # Try to register first
    register_payload = {
        "email": email,
        "password": password,
        "role": role,
        "terms_accepted": terms_accepted
    }
    
    if license_code:
        register_payload["license_code"] = license_code
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ User {email} registered successfully")
            register_data = response.json()
            print(f"Registration response: {register_data}")
        elif response.status_code == 400 and ("already registered" in response.text or "already exists" in response.text):
            print(f"⚠️  User {email} already exists, proceeding with login")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None
    
    # Now try to login
    login_payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            login_data = response.json()
            token = login_data.get('access_token')
            print(f"✅ Login successful for {email}")
            return token
        elif response.status_code == 403:
            print(f"❌ Login failed - Account pending approval: {response.text}")
            return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def step1_create_users(creds):
    """Step 1: Create agency and navigator users if not exists"""
    print("\n" + "="*60)
    print("STEP 1: CREATE AGENCY AND NAVIGATOR USERS")
    print("="*60)
    
    # Create navigator
    creds.navigator_token = create_or_login_user(
        creds.navigator_email, 
        creds.navigator_password, 
        "navigator"
    )
    
    if not creds.navigator_token:
        print("❌ FAIL: Could not create/login navigator")
        return False
    
    # Create agency (will be pending approval)
    creds.agency_token = create_or_login_user(
        creds.agency_email, 
        creds.agency_password, 
        "agency"
    )
    
    if not creds.agency_token:
        print("❌ FAIL: Could not create/login agency")
        return False
    
    print("✅ PASS: Step 1 completed - Navigator and Agency users created/verified")
    return True

def step2_navigator_search_agency(creds):
    """Step 2: Login as navigator and search for agency user ID via GET /api/navigator/agencies/pending"""
    print("\n" + "="*60)
    print("STEP 2: NAVIGATOR SEARCH FOR PENDING AGENCIES")
    print("="*60)
    
    try:
        headers = {
            "Authorization": f"Bearer {creds.navigator_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/navigator/agencies/pending", headers=headers)
        print(f"GET /api/navigator/agencies/pending Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            agencies = data.get('agencies', [])
            print(f"Found {len(agencies)} pending agencies")
            
            # Look for our test agency
            target_agency = None
            for agency in agencies:
                if agency.get('email') == creds.agency_email:
                    target_agency = agency
                    break
            
            if target_agency:
                agency_user_id = target_agency.get('id')
                print(f"✅ PASS: Found target agency with ID: {agency_user_id}")
                print(f"Agency details: {json.dumps(target_agency, indent=2, default=str)}")
                return agency_user_id
            else:
                print(f"❌ FAIL: Could not find agency with email {creds.agency_email}")
                print(f"Available agencies: {[a.get('email') for a in agencies]}")
                return None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def step3_approve_agency(creds, agency_user_id):
    """Step 3: POST /api/navigator/agencies/approve with approval_status=approved"""
    print("\n" + "="*60)
    print("STEP 3: APPROVE AGENCY")
    print("="*60)
    
    try:
        headers = {
            "Authorization": f"Bearer {creds.navigator_token}",
            "Content-Type": "application/json"
        }
        
        approval_payload = {
            "agency_user_id": agency_user_id,
            "approval_status": "approved",
            "notes": "Agency approved for E2E testing"
        }
        
        response = requests.post(
            f"{API_BASE}/navigator/agencies/approve",
            json=approval_payload,
            headers=headers
        )
        
        print(f"POST /api/navigator/agencies/approve Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Agency approved successfully")
            print(f"Approval response: {json.dumps(data, indent=2, default=str)}")
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def step4_generate_licenses(creds):
    """Step 4: Login as agency and POST /api/agency/licenses/generate with quantity=5"""
    print("\n" + "="*60)
    print("STEP 4: GENERATE LICENSE CODES")
    print("="*60)
    
    try:
        headers = {
            "Authorization": f"Bearer {creds.agency_token}",
            "Content-Type": "application/json"
        }
        
        license_payload = {
            "quantity": 5
        }
        
        response = requests.post(
            f"{API_BASE}/agency/licenses/generate",
            json=license_payload,
            headers=headers
        )
        
        print(f"POST /api/agency/licenses/generate Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            license_codes = data.get('license_codes', [])
            print(f"✅ PASS: Generated {len(license_codes)} license codes")
            print(f"License codes: {license_codes}")
            
            if license_codes:
                # Store first license code for client registration
                creds.client_license_code = license_codes[0]
                return license_codes
            else:
                print("❌ FAIL: No license codes returned")
                return None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def step5_register_client_and_provider(creds):
    """Step 5: Register client with license and register provider"""
    print("\n" + "="*60)
    print("STEP 5: REGISTER CLIENT AND PROVIDER")
    print("="*60)
    
    # Generate unique emails
    creds.client_email = f"client_{uuid.uuid4().hex[:8]}@example.com"
    creds.provider_email = f"provider_{uuid.uuid4().hex[:8]}@example.com"
    
    # Register client with license code
    print("Registering client with license code...")
    creds.client_token = create_or_login_user(
        creds.client_email,
        creds.client_password,
        "client",
        license_code=creds.client_license_code
    )
    
    if not creds.client_token:
        print("❌ FAIL: Could not register client with license")
        return False
    
    # Register provider
    print("Registering provider...")
    creds.provider_token = create_or_login_user(
        creds.provider_email,
        creds.provider_password,
        "provider"
    )
    
    if not creds.provider_token:
        print("❌ FAIL: Could not register provider")
        return False
    
    print("✅ PASS: Client and provider registered successfully")
    return True

def step5b_approve_provider(creds):
    """Step 5b: Approve provider via /api/navigator/providers/approve"""
    print("\n" + "="*60)
    print("STEP 5B: APPROVE PROVIDER")
    print("="*60)
    
    try:
        # First get pending providers
        headers = {
            "Authorization": f"Bearer {creds.navigator_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/navigator/providers/pending", headers=headers)
        print(f"GET /api/navigator/providers/pending Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"Found {len(providers)} pending providers")
            
            # Look for our test provider
            target_provider = None
            for provider in providers:
                if provider.get('email') == creds.provider_email:
                    target_provider = provider
                    break
            
            if not target_provider:
                print(f"❌ FAIL: Could not find provider with email {creds.provider_email}")
                return False
            
            provider_user_id = target_provider.get('id')
            print(f"Found provider with ID: {provider_user_id}")
            
            # Now approve the provider
            approval_payload = {
                "provider_user_id": provider_user_id,
                "approval_status": "approved",
                "notes": "Provider approved for E2E testing"
            }
            
            response = requests.post(
                f"{API_BASE}/navigator/providers/approve",
                json=approval_payload,
                headers=headers
            )
            
            print(f"POST /api/navigator/providers/approve Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASS: Provider approved successfully")
                print(f"Approval response: {json.dumps(data, indent=2, default=str)}")
                return True
            else:
                print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
                return False
        else:
            print(f"❌ FAIL: Could not get pending providers: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def step6_service_request_flow(creds):
    """Step 6: Create service request, provider response, client fetch, attempt payment"""
    print("\n" + "="*60)
    print("STEP 6: SERVICE REQUEST AND PAYMENT FLOW")
    print("="*60)
    
    try:
        # Step 6a: Create service request as client
        print("6a: Creating service request as client...")
        client_headers = {
            "Authorization": f"Bearer {creds.client_token}",
            "Content-Type": "application/json"
        }
        
        service_request_payload = {
            "area_id": "area5",  # Technology & Security Infrastructure
            "description": "Need cybersecurity assessment and implementation",
            "budget_range": "$1000-$3000"
        }
        
        response = requests.post(
            f"{API_BASE}/service-requests/professional-help",
            json=service_request_payload,
            headers=client_headers
        )
        
        print(f"POST /api/service-requests/professional-help Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Could not create service request: {response.text}")
            return False
        
        service_request_data = response.json()
        service_request_id = service_request_data.get('request_id')
        print(f"✅ Service request created with ID: {service_request_id}")
        
        # Step 6b: Provider responds to service request
        print("6b: Provider responding to service request...")
        provider_headers = {
            "Authorization": f"Bearer {creds.provider_token}",
            "Content-Type": "application/json"
        }
        
        provider_response_payload = {
            "proposed_fee": 1500,
            "proposal_note": "Comprehensive cybersecurity assessment and implementation plan"
        }
        
        response = requests.post(
            f"{API_BASE}/provider/respond-to-request",
            json=provider_response_payload,
            headers=provider_headers
        )
        
        print(f"POST /api/provider/respond-to-request Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Provider could not respond: {response.text}")
            return False
        
        print("✅ Provider response submitted")
        
        # Step 6c: Client fetches responses
        print("6c: Client fetching service request responses...")
        response = requests.get(
            f"{API_BASE}/service-requests/{service_request_id}/responses",
            headers=client_headers
        )
        
        print(f"GET /api/service-requests/{service_request_id}/responses Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Could not fetch responses: {response.text}")
            return False
        
        responses_data = response.json()
        print(f"✅ Fetched responses: {json.dumps(responses_data, indent=2, default=str)}")
        
        # Step 6d: Attempt payment (expect 503 or success)
        print("6d: Attempting payment...")
        payment_payload = {
            "service_request_id": service_request_id,
            "provider_id": creds.provider_email,  # Using email as identifier
            "amount": 1500
        }
        
        response = requests.post(
            f"{API_BASE}/payments/service-request",
            json=payment_payload,
            headers=client_headers
        )
        
        print(f"POST /api/payments/service-request Status: {response.status_code}")
        
        if response.status_code == 503:
            print("✅ PASS: Payment returned 503 as expected (service unavailable)")
            return True
        elif response.status_code == 200:
            payment_data = response.json()
            print(f"✅ PASS: Payment successful: {json.dumps(payment_data, indent=2, default=str)}")
            return True
        else:
            print(f"❌ FAIL: Unexpected payment response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def step7_analytics_flow(creds):
    """Step 7: Post analytics and fetch navigator analytics totals"""
    print("\n" + "="*60)
    print("STEP 7: ANALYTICS FLOW")
    print("="*60)
    
    try:
        # Step 7a: Post analytics data
        print("7a: Posting analytics data...")
        client_headers = {
            "Authorization": f"Bearer {creds.client_token}",
            "Content-Type": "application/json"
        }
        
        # Post multiple analytics entries
        analytics_entries = [
            {"area_id": "area1", "resource_type": "free_resource"},
            {"area_id": "area2", "resource_type": "free_resource"},
            {"area_id": "area5", "resource_type": "professional_help"},
            {"area_id": "area3", "resource_type": "free_resource"},
            {"area_id": "area5", "resource_type": "free_resource"}
        ]
        
        for entry in analytics_entries:
            response = requests.post(
                f"{API_BASE}/analytics/resource-access",
                json=entry,
                headers=client_headers
            )
            print(f"Analytics POST Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"⚠️  Analytics post failed: {response.text}")
        
        print("✅ Analytics data posted")
        
        # Step 7b: Fetch navigator analytics totals
        print("7b: Fetching navigator analytics totals...")
        navigator_headers = {
            "Authorization": f"Bearer {creds.navigator_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/navigator/analytics/resources?since_days=30",
            headers=navigator_headers
        )
        
        print(f"GET /api/navigator/analytics/resources Status: {response.status_code}")
        
        if response.status_code == 200:
            analytics_data = response.json()
            print(f"✅ PASS: Navigator analytics retrieved successfully")
            print(f"Analytics totals: {json.dumps(analytics_data, indent=2, default=str)}")
            
            # Validate required fields
            required_fields = ['since', 'total', 'by_area', 'last7']
            missing_fields = [field for field in required_fields if field not in analytics_data]
            
            if not missing_fields:
                print("✅ All required analytics fields present")
                return True
            else:
                print(f"❌ FAIL: Missing analytics fields: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: Could not fetch analytics: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run the complete E2E approval and license flow test"""
    print("🚀 Starting E2E Approval and License Flow Test")
    print(f"Base URL: {API_BASE}")
    
    creds = TestCredentials()
    results = {}
    
    # Step 1: Create agency and navigator users
    results['step1_create_users'] = step1_create_users(creds)
    if not results['step1_create_users']:
        print("❌ CRITICAL FAIL: Cannot proceed without users")
        return False
    
    # Step 2: Navigator search for agency
    agency_user_id = step2_navigator_search_agency(creds)
    results['step2_search_agency'] = agency_user_id is not None
    if not agency_user_id:
        print("❌ CRITICAL FAIL: Cannot proceed without agency ID")
        return False
    
    # Step 3: Approve agency
    results['step3_approve_agency'] = step3_approve_agency(creds, agency_user_id)
    if not results['step3_approve_agency']:
        print("❌ CRITICAL FAIL: Cannot proceed without agency approval")
        return False
    
    # Step 4: Generate license codes
    license_codes = step4_generate_licenses(creds)
    results['step4_generate_licenses'] = license_codes is not None
    if not license_codes:
        print("❌ CRITICAL FAIL: Cannot proceed without license codes")
        return False
    
    # Step 5: Register client and provider
    results['step5_register_users'] = step5_register_client_and_provider(creds)
    if not results['step5_register_users']:
        print("❌ CRITICAL FAIL: Cannot proceed without client/provider")
        return False
    
    # Step 5b: Approve provider
    results['step5b_approve_provider'] = step5b_approve_provider(creds)
    if not results['step5b_approve_provider']:
        print("⚠️  Provider approval failed, but continuing...")
    
    # Step 6: Service request and payment flow
    results['step6_service_payment'] = step6_service_request_flow(creds)
    
    # Step 7: Analytics flow
    results['step7_analytics'] = step7_analytics_flow(creds)
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 E2E TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for step, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {step.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} steps passed")
    
    # Print credentials for user
    print("\n" + "="*60)
    print("🔐 TEST CREDENTIALS CREATED/USED")
    print("="*60)
    print(f"Navigator: {creds.navigator_email} / {creds.navigator_password}")
    print(f"Agency: {creds.agency_email} / {creds.agency_password}")
    if creds.client_email:
        print(f"Client: {creds.client_email} / {creds.client_password}")
    if creds.provider_email:
        print(f"Provider: {creds.provider_email} / {creds.provider_password}")
    if creds.client_license_code:
        print(f"License Code Used: {creds.client_license_code}")
    
    # Pass/Fail per step as requested
    print("\n" + "="*60)
    print("📋 PASS/FAIL PER STEP")
    print("="*60)
    step_descriptions = {
        'step1_create_users': 'Create agency and navigator users',
        'step2_search_agency': 'Navigator search for agency user ID',
        'step3_approve_agency': 'Approve agency via navigator',
        'step4_generate_licenses': 'Generate license codes as agency',
        'step5_register_users': 'Register client with license and provider',
        'step5b_approve_provider': 'Approve provider via navigator',
        'step6_service_payment': 'Service request and payment flow',
        'step7_analytics': 'Analytics posting and retrieval'
    }
    
    for step, result in results.items():
        description = step_descriptions.get(step, step)
        status = "PASS" if result else "FAIL"
        print(f"{status}: {description}")
    
    if passed == total:
        print("\n🎉 All E2E tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return False

if __name__ == "__main__":
    main()