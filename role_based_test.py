#!/usr/bin/env python3
"""
Role-Based Registration and Approval Workflow Test
Tests the complete workflow as specified in the review request:
1. Create Digital Navigator (auto-approved)
2. Create Local Agency (pending → approve via navigator)
3. Create Service Provider (pending → approve via navigator)
4. Generate License Codes (via agency)
5. Create Small Business Client (using license code)
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://nextjs-mongo-polaris.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing role-based registration at: {API_BASE}")

class TestCredentials:
    """Store test credentials for all user types"""
    def __init__(self):
        self.navigator = None
        self.agency = None
        self.provider = None
        self.client = None
        self.license_codes = []

def test_create_navigator():
    """Create Digital Navigator (auto-approved)"""
    print("\n" + "="*60)
    print("🧭 STEP 1: CREATE DIGITAL NAVIGATOR (AUTO-APPROVED)")
    print("="*60)
    
    # Use timestamp to ensure unique email
    import time
    timestamp = int(time.time())
    
    credentials = {
        "email": f"navigator.{timestamp}@polaris.example.com",
        "password": "Navigator123!",
        "role": "navigator",
        "terms_accepted": True
    }
    
    try:
        # Register navigator
        print(f"Registering navigator with email: {credentials['email']}")
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Navigator registered successfully: {data}")
            
            # Test login immediately (should work since auto-approved)
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get('access_token')
                print(f"✅ Navigator login successful - Token obtained")
                
                # Verify token with /api/auth/me
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"✅ Navigator token verified: {user_data['email']} - Role: {user_data['role']}")
                    return {
                        "email": credentials["email"],
                        "password": credentials["password"],
                        "token": token,
                        "user_id": user_data.get('id')
                    }
                else:
                    print(f"❌ Token verification failed: {me_response.text}")
                    return None
            else:
                print(f"❌ Navigator login failed: {login_response.text}")
                return None
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️  Navigator already exists, testing login...")
            # Try login with existing user
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get('access_token')
                
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"✅ Existing navigator login successful: {user_data['email']}")
                    return {
                        "email": credentials["email"],
                        "password": credentials["password"],
                        "token": token,
                        "user_id": user_data.get('id')
                    }
            
            print(f"❌ Existing navigator login failed: {login_response.text}")
            return None
        else:
            print(f"❌ Navigator registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR creating navigator: {e}")
        return None

def test_create_agency():
    """Create Local Agency (pending → approve via navigator)"""
    print("\n" + "="*60)
    print("🏢 STEP 2: CREATE LOCAL AGENCY (PENDING STATUS)")
    print("="*60)
    
    # Use timestamp to ensure unique email
    import time
    timestamp = int(time.time())
    
    credentials = {
        "email": f"agency.{timestamp}@polaris.example.com",
        "password": "Agency123!",
        "role": "agency",
        "terms_accepted": True
    }
    
    try:
        # Register agency
        print(f"Registering agency with email: {credentials['email']}")
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agency registered successfully: {data}")
            
            # Verify agency has pending status by trying to login (should fail)
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 403:
                print(f"✅ Agency correctly blocked from login (pending approval): {login_response.text}")
                return {
                    "email": credentials["email"],
                    "password": credentials["password"],
                    "status": "pending"
                }
            else:
                print(f"⚠️  Unexpected login response: {login_response.status_code} - {login_response.text}")
                return {
                    "email": credentials["email"],
                    "password": credentials["password"],
                    "status": "unknown"
                }
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️  Agency already exists")
            return {
                "email": credentials["email"],
                "password": credentials["password"],
                "status": "existing"
            }
        else:
            print(f"❌ Agency registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR creating agency: {e}")
        return None

def test_create_provider():
    """Create Service Provider (pending → approve via navigator)"""
    print("\n" + "="*60)
    print("🔧 STEP 3: CREATE SERVICE PROVIDER (PENDING STATUS)")
    print("="*60)
    
    # Use timestamp to ensure unique email
    import time
    timestamp = int(time.time())
    
    credentials = {
        "email": f"provider.{timestamp}@polaris.example.com",
        "password": "Provider123!",
        "role": "provider",
        "terms_accepted": True
    }
    
    try:
        # Register provider
        print(f"Registering provider with email: {credentials['email']}")
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Provider registered successfully: {data}")
            
            # Verify provider has pending status by trying to login (should fail)
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 403:
                print(f"✅ Provider correctly blocked from login (pending approval): {login_response.text}")
                return {
                    "email": credentials["email"],
                    "password": credentials["password"],
                    "status": "pending"
                }
            else:
                print(f"⚠️  Unexpected login response: {login_response.status_code} - {login_response.text}")
                return {
                    "email": credentials["email"],
                    "password": credentials["password"],
                    "status": "unknown"
                }
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️  Provider already exists")
            return {
                "email": credentials["email"],
                "password": credentials["password"],
                "status": "existing"
            }
        else:
            print(f"❌ Provider registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR creating provider: {e}")
        return None

def test_navigator_approve_users(navigator_token, agency_email, provider_email):
    """Navigator approves agency and provider"""
    print("\n" + "="*60)
    print("✅ STEP 4: NAVIGATOR APPROVES AGENCY AND PROVIDER")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {navigator_token}"}
    
    try:
        # Get pending approvals
        print("Getting pending approvals...")
        response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=headers)
        print(f"Pending approvals Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pending_users = data.get('pending_approvals', [])
            print(f"Found {len(pending_users)} pending users")
            
            # Find agency and provider users
            agency_user = None
            provider_user = None
            
            for user in pending_users:
                if user.get('email') == agency_email:
                    agency_user = user
                elif user.get('email') == provider_email:
                    provider_user = user
            
            results = {}
            
            # Approve agency
            if agency_user:
                print(f"\nApproving agency user: {agency_user['email']}")
                
                approve_response = requests.post(
                    f"{API_BASE}/admin/approve-user?user_id={agency_user['_id']}",
                    headers=headers
                )
                print(f"Agency approval Status: {approve_response.status_code}")
                
                if approve_response.status_code == 200:
                    print("✅ Agency approved successfully")
                    results['agency_approved'] = True
                else:
                    print(f"❌ Agency approval failed: {approve_response.text}")
                    results['agency_approved'] = False
            else:
                print("⚠️  Agency user not found in pending list")
                results['agency_approved'] = False
            
            # Approve provider
            if provider_user:
                print(f"\nApproving provider user: {provider_user['email']}")
                
                approve_response = requests.post(
                    f"{API_BASE}/admin/approve-user?user_id={provider_user['_id']}",
                    headers=headers
                )
                print(f"Provider approval Status: {approve_response.status_code}")
                
                if approve_response.status_code == 200:
                    print("✅ Provider approved successfully")
                    results['provider_approved'] = True
                else:
                    print(f"❌ Provider approval failed: {approve_response.text}")
                    results['provider_approved'] = False
            else:
                print("⚠️  Provider user not found in pending list")
                results['provider_approved'] = False
            
            return results
            
        else:
            print(f"❌ Failed to get pending approvals: {response.text}")
            return {'agency_approved': False, 'provider_approved': False}
            
    except Exception as e:
        print(f"❌ ERROR in approval process: {e}")
        return {'agency_approved': False, 'provider_approved': False}

def test_agency_login_and_generate_licenses(agency_email, agency_password):
    """Test agency login after approval and generate license codes"""
    print("\n" + "="*60)
    print("🎫 STEP 5: AGENCY LOGIN AND LICENSE GENERATION")
    print("="*60)
    
    try:
        # Try agency login after approval
        print(f"Attempting agency login: {agency_email}")
        login_payload = {
            "email": agency_email,
            "password": agency_password
        }
        
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Agency login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Agency login failed: {login_response.text}")
            return None, []
        
        login_data = login_response.json()
        agency_token = login_data.get('access_token')
        print("✅ Agency login successful after approval")
        
        # Generate license codes
        headers = {"Authorization": f"Bearer {agency_token}"}
        license_codes = []
        
        print("\nGenerating 3 license codes...")
        for i in range(3):
            generate_response = requests.post(
                f"{API_BASE}/agency/licenses/generate",
                json={"quantity": 1, "expires_days": 30},
                headers=headers
            )
            print(f"License generation {i+1} Status: {generate_response.status_code}")
            
            if generate_response.status_code == 200:
                data = generate_response.json()
                licenses = data.get('licenses', [])
                if licenses:
                    for license_info in licenses:
                        license_codes.append(license_info['license_code'])
                    print(f"✅ Generated license code: {licenses[0]['license_code']}")
                else:
                    print(f"⚠️  No licenses in response: {data}")
            else:
                print(f"❌ License generation failed: {generate_response.text}")
        
        # Get license statistics
        stats_response = requests.get(f"{API_BASE}/agency/licenses/stats", headers=headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n📊 License Statistics: {stats}")
        
        print(f"\n✅ Generated {len(license_codes)} license codes total")
        return agency_token, license_codes
        
    except Exception as e:
        print(f"❌ ERROR in agency login/license generation: {e}")
        return None, []

def test_create_client_with_license(license_code):
    """Create Small Business Client using license code"""
    print("\n" + "="*60)
    print("👤 STEP 6: CREATE SMALL BUSINESS CLIENT WITH LICENSE CODE")
    print("="*60)
    
    # Use timestamp to ensure unique email
    import time
    timestamp = int(time.time())
    
    credentials = {
        "email": f"client.{timestamp}@polaris.example.com",
        "password": "Client123!",
        "role": "client",
        "license_code": license_code,
        "terms_accepted": True
    }
    
    try:
        # Register client with license code
        print(f"Registering client with email: {credentials['email']}")
        print(f"Using license code: {license_code}")
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Client registered successfully: {data}")
            
            # Test client login (should work immediately since auto-approved)
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get('access_token')
                print("✅ Client login successful")
                
                # Verify token
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"✅ Client token verified: {user_data['email']} - Role: {user_data['role']}")
                    return {
                        "email": credentials["email"],
                        "password": credentials["password"],
                        "token": token,
                        "user_id": user_data.get('id'),
                        "license_code": license_code
                    }
                else:
                    print(f"❌ Client token verification failed: {me_response.text}")
                    return None
            else:
                print(f"❌ Client login failed: {login_response.text}")
                return None
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️  Client already exists, testing login...")
            # Try login with existing user
            login_payload = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get('access_token')
                
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"✅ Existing client login successful: {user_data['email']}")
                    return {
                        "email": credentials["email"],
                        "password": credentials["password"],
                        "token": token,
                        "user_id": user_data.get('id'),
                        "license_code": license_code
                    }
            
            print(f"❌ Existing client login failed: {login_response.text}")
            return None
        else:
            print(f"❌ Client registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR creating client: {e}")
        return None

def test_provider_login_after_approval(provider_email, provider_password):
    """Test provider login after approval"""
    print("\n" + "="*60)
    print("🔧 STEP 7: PROVIDER LOGIN AFTER APPROVAL")
    print("="*60)
    
    try:
        # Try provider login after approval
        print(f"Attempting provider login: {provider_email}")
        login_payload = {
            "email": provider_email,
            "password": provider_password
        }
        
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Provider login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('access_token')
            print("✅ Provider login successful after approval")
            
            # Verify token
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ Provider token verified: {user_data['email']} - Role: {user_data['role']}")
                return {
                    "email": provider_email,
                    "password": provider_password,
                    "token": token,
                    "user_id": user_data.get('id')
                }
            else:
                print(f"❌ Provider token verification failed: {me_response.text}")
                return None
        else:
            print(f"❌ Provider login failed: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR in provider login: {e}")
        return None

def main():
    """Run complete role-based registration and approval workflow test"""
    print("🚀 ROLE-BASED REGISTRATION AND APPROVAL WORKFLOW TEST")
    print(f"Backend URL: {API_BASE}")
    
    credentials = TestCredentials()
    
    # Step 1: Create Navigator (auto-approved)
    navigator = test_create_navigator()
    if not navigator:
        print("❌ CRITICAL: Navigator creation failed - cannot proceed with approvals")
        return False
    
    credentials.navigator = navigator
    
    # Step 2: Create Agency (pending)
    agency = test_create_agency()
    if not agency:
        print("❌ CRITICAL: Agency creation failed")
        return False
    
    credentials.agency = agency
    
    # Step 3: Create Provider (pending)
    provider = test_create_provider()
    if not provider:
        print("❌ CRITICAL: Provider creation failed")
        return False
    
    credentials.provider = provider
    
    # Step 4: Navigator approves agency and provider
    approval_results = test_navigator_approve_users(
        navigator['token'], 
        agency['email'], 
        provider['email']
    )
    
    # Step 5: Agency login and license generation
    agency_token = None
    license_codes = []
    
    if approval_results.get('agency_approved'):
        agency_token, license_codes = test_agency_login_and_generate_licenses(
            agency['email'], 
            agency['password']
        )
    
    # Step 6: Create client with license code
    client = None
    if license_codes:
        client = test_create_client_with_license(license_codes[0])
        credentials.client = client
        credentials.license_codes = license_codes
    
    # Step 7: Provider login after approval
    provider_login = None
    if approval_results.get('provider_approved'):
        provider_login = test_provider_login_after_approval(
            provider['email'], 
            provider['password']
        )
    
    # Final Summary
    print("\n" + "="*80)
    print("🎉 COMPLETE ROLE-BASED WORKFLOW TEST RESULTS")
    print("="*80)
    
    print("\n📋 WORKING CREDENTIALS SUMMARY:")
    print("-" * 50)
    
    if navigator:
        print(f"✅ DIGITAL NAVIGATOR:")
        print(f"   Email: {navigator['email']}")
        print(f"   Password: {navigator['password']}")
        print(f"   Status: Auto-approved ✓")
        print(f"   Login: Working ✓")
    
    if agency and approval_results.get('agency_approved') and agency_token:
        print(f"\n✅ LOCAL AGENCY:")
        print(f"   Email: {agency['email']}")
        print(f"   Password: {agency['password']}")
        print(f"   Status: Approved by Navigator ✓")
        print(f"   Login: Working ✓")
        print(f"   License Generation: Working ✓")
    
    if provider and approval_results.get('provider_approved') and provider_login:
        print(f"\n✅ SERVICE PROVIDER:")
        print(f"   Email: {provider['email']}")
        print(f"   Password: {provider['password']}")
        print(f"   Status: Approved by Navigator ✓")
        print(f"   Login: Working ✓")
    
    if client and license_codes:
        print(f"\n✅ SMALL BUSINESS CLIENT:")
        print(f"   Email: {client['email']}")
        print(f"   Password: {client['password']}")
        print(f"   Status: Auto-approved ✓")
        print(f"   Login: Working ✓")
        print(f"   License Code Used: {client['license_code']}")
    
    if license_codes:
        print(f"\n🎫 GENERATED LICENSE CODES:")
        for i, code in enumerate(license_codes, 1):
            status = "USED" if i == 1 and client else "AVAILABLE"
            print(f"   {i}. {code} ({status})")
    
    print("\n" + "="*80)
    print("🔍 WORKFLOW VERIFICATION:")
    print("-" * 50)
    
    workflow_steps = [
        ("Navigator Creation", navigator is not None),
        ("Agency Registration (Pending)", agency is not None),
        ("Provider Registration (Pending)", provider is not None),
        ("Navigator Approval System", approval_results.get('agency_approved', False) and approval_results.get('provider_approved', False)),
        ("Agency Login After Approval", agency_token is not None),
        ("License Code Generation", len(license_codes) >= 3),
        ("Client Registration with License", client is not None),
        ("Provider Login After Approval", provider_login is not None)
    ]
    
    passed_steps = 0
    for step_name, passed in workflow_steps:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {step_name}: {status}")
        if passed:
            passed_steps += 1
    
    print(f"\nWorkflow Completion: {passed_steps}/{len(workflow_steps)} steps passed")
    
    if passed_steps == len(workflow_steps):
        print("\n🎉 COMPLETE SUCCESS: All role-based registration and approval workflows working!")
        print("✅ Users can now login with the provided credentials")
        print("✅ License codes are available for additional client registrations")
        return True
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed_steps}/{len(workflow_steps)} workflows completed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)