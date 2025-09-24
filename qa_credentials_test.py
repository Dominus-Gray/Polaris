#!/usr/bin/env python3
"""
QA Credentials E2E Test for Polaris MVP
Tests the exact workflow specified in the review request with the provided QA credentials
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polar-docs-ai.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

# QA Credentials as specified in review request (using .com instead of .test for email validation)
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.com", "password": "Polaris#2025!"}
}

def register_or_login_user(role, email, password):
    """Register user or login if already exists. Returns token and registration status."""
    print(f"\n=== Step: Register/Login {role.title()} ===")
    
    # Try to register first
    register_payload = {
        "email": email,
        "password": password,
        "role": role,
        "terms_accepted": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        registration_status = "registered"
        if response.status_code == 200:
            print(f"✅ {role.title()} registration successful")
        elif response.status_code == 400 and "already" in response.text.lower():
            print(f"⚠️  {role.title()} already exists, proceeding to login")
            registration_status = "already_exists"
        else:
            print(f"❌ {role.title()} registration failed: {response.status_code} - {response.text}")
            return None, "failed"
    except Exception as e:
        print(f"❌ {role.title()} registration error: {e}")
        return None, "error"
    
    # Now login
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
            data = response.json()
            token = data.get('access_token')
            if token:
                print(f"✅ {role.title()} login successful")
                return token, registration_status
            else:
                print(f"❌ {role.title()} login failed: No token in response")
                return None, "login_failed"
        else:
            print(f"❌ {role.title()} login failed: {response.status_code} - {response.text}")
            return None, "login_failed"
    except Exception as e:
        print(f"❌ {role.title()} login error: {e}")
        return None, "error"

def find_agency_by_email(navigator_token, agency_email):
    """Find agency in pending list by email"""
    print(f"\n=== Step: Find Agency by Email ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {navigator_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/navigator/agencies/pending", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            agencies = data.get('agencies', [])
            print(f"Found {len(agencies)} pending agencies")
            
            for agency in agencies:
                if agency.get('email') == agency_email:
                    print(f"✅ Found agency: {agency.get('id')} - {agency_email}")
                    return agency.get('id')
            
            print(f"❌ Agency {agency_email} not found in pending list")
            return None
        else:
            print(f"❌ Failed to get pending agencies: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error finding agency: {e}")
        return None

def approve_agency(navigator_token, agency_id):
    """Approve agency via POST /api/navigator/agencies/approve"""
    print(f"\n=== Step: Approve Agency ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {navigator_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "agency_user_id": agency_id,
            "approval_status": "approved",
            "notes": "QA test approval"
        }
        
        response = requests.post(
            f"{API_BASE}/navigator/agencies/approve",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Agency approved successfully")
            return True
        else:
            print(f"❌ Agency approval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error approving agency: {e}")
        return False

def generate_license_codes(agency_token, quantity=3):
    """Generate license codes as approved agency"""
    print(f"\n=== Step: Generate License Codes ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {agency_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "quantity": quantity
        }
        
        response = requests.post(
            f"{API_BASE}/agency/licenses/generate",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            licenses = data.get('licenses', [])
            if licenses:
                first_license = licenses[0].get('license_code')
                print(f"✅ Generated {len(licenses)} license codes")
                print(f"First license code: {first_license}")
                return first_license
            else:
                print(f"❌ No license codes in response: {data}")
                return None
        else:
            print(f"❌ License generation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating licenses: {e}")
        return None

def register_client_with_license(email, password, license_code):
    """Register client with license code"""
    print(f"\n=== Step: Register Client with License ===")
    
    try:
        payload = {
            "email": email,
            "password": password,
            "role": "client",
            "terms_accepted": True,
            "license_code": license_code
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Client registered with license code")
            return True
        elif response.status_code == 400 and "already" in response.text.lower():
            print(f"⚠️  Client already exists")
            return True
        else:
            print(f"❌ Client registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error registering client: {e}")
        return False

def find_provider_by_email(navigator_token, provider_email):
    """Find provider in pending list by email"""
    print(f"\n=== Step: Find Provider by Email ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {navigator_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{API_BASE}/navigator/providers/pending", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"Found {len(providers)} pending providers")
            
            for provider in providers:
                if provider.get('email') == provider_email:
                    print(f"✅ Found provider: {provider.get('id')} - {provider_email}")
                    return provider.get('id')
            
            print(f"❌ Provider {provider_email} not found in pending list")
            return None
        else:
            print(f"❌ Failed to get pending providers: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error finding provider: {e}")
        return None

def approve_provider(navigator_token, provider_id):
    """Approve provider via POST /api/navigator/providers/approve"""
    print(f"\n=== Step: Approve Provider ===")
    
    try:
        headers = {
            "Authorization": f"Bearer {navigator_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "provider_user_id": provider_id,
            "approval_status": "approved",
            "notes": "QA test approval"
        }
        
        response = requests.post(
            f"{API_BASE}/navigator/providers/approve",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Provider approved successfully")
            return True
        else:
            print(f"❌ Provider approval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error approving provider: {e}")
        return False

def mask_license_code(license_code):
    """Mask license code except last 4 digits"""
    if not license_code or len(license_code) < 4:
        return license_code
    return "*" * (len(license_code) - 4) + license_code[-4:]

def main():
    """Execute the complete E2E approval and license workflow"""
    print("🚀 Starting QA Credentials E2E Test")
    print("="*60)
    
    results = {
        "navigator": {"registration": "unknown", "login": "unknown"},
        "agency": {"registration": "unknown", "login": "unknown"},
        "client": {"registration": "unknown", "login": "unknown"},
        "provider": {"registration": "unknown", "login": "unknown"},
        "license_code": None,
        "workflow_success": False
    }
    
    try:
        # Step 1: Register navigator (role=navigator, terms_accepted=true)
        navigator_token, nav_reg_status = register_or_login_user(
            "navigator", 
            QA_CREDENTIALS["navigator"]["email"], 
            QA_CREDENTIALS["navigator"]["password"]
        )
        results["navigator"]["registration"] = nav_reg_status
        results["navigator"]["login"] = "success" if navigator_token else "failed"
        
        if not navigator_token:
            print("❌ Cannot proceed without navigator token")
            return results
        
        # Step 2: Register agency (role=agency)
        agency_token, agency_reg_status = register_or_login_user(
            "agency", 
            QA_CREDENTIALS["agency"]["email"], 
            QA_CREDENTIALS["agency"]["password"]
        )
        results["agency"]["registration"] = agency_reg_status
        
        # Find agency by email and approve
        agency_id = find_agency_by_email(navigator_token, QA_CREDENTIALS["agency"]["email"])
        if agency_id:
            approval_success = approve_agency(navigator_token, agency_id)
            if approval_success:
                # Now try to login as agency
                agency_token, _ = register_or_login_user(
                    "agency", 
                    QA_CREDENTIALS["agency"]["email"], 
                    QA_CREDENTIALS["agency"]["password"]
                )
                results["agency"]["login"] = "success" if agency_token else "failed"
            else:
                results["agency"]["login"] = "approval_failed"
        else:
            results["agency"]["login"] = "not_found_for_approval"
        
        if not agency_token:
            print("❌ Cannot proceed without agency token")
            return results
        
        # Step 3: As agency, generate license codes
        license_code = generate_license_codes(agency_token, quantity=3)
        results["license_code"] = mask_license_code(license_code) if license_code else None
        
        if not license_code:
            print("❌ Cannot proceed without license code")
            return results
        
        # Step 4: Register client with license code
        client_reg_success = register_client_with_license(
            QA_CREDENTIALS["client"]["email"],
            QA_CREDENTIALS["client"]["password"],
            license_code
        )
        results["client"]["registration"] = "success" if client_reg_success else "failed"
        
        # Login as client
        client_token, _ = register_or_login_user(
            "client", 
            QA_CREDENTIALS["client"]["email"], 
            QA_CREDENTIALS["client"]["password"]
        )
        results["client"]["login"] = "success" if client_token else "failed"
        
        # Step 5: Register provider
        provider_token, provider_reg_status = register_or_login_user(
            "provider", 
            QA_CREDENTIALS["provider"]["email"], 
            QA_CREDENTIALS["provider"]["password"]
        )
        results["provider"]["registration"] = provider_reg_status
        
        # Find provider by email and approve
        provider_id = find_provider_by_email(navigator_token, QA_CREDENTIALS["provider"]["email"])
        if provider_id:
            approval_success = approve_provider(navigator_token, provider_id)
            if approval_success:
                # Now try to login as provider
                provider_token, _ = register_or_login_user(
                    "provider", 
                    QA_CREDENTIALS["provider"]["email"], 
                    QA_CREDENTIALS["provider"]["password"]
                )
                results["provider"]["login"] = "success" if provider_token else "failed"
            else:
                results["provider"]["login"] = "approval_failed"
        else:
            results["provider"]["login"] = "not_found_for_approval"
        
        # Check if workflow was successful
        all_logins_successful = all(
            results[role]["login"] == "success" 
            for role in ["navigator", "agency", "client", "provider"]
        )
        results["workflow_success"] = all_logins_successful and license_code is not None
        
    except Exception as e:
        print(f"❌ Unexpected error in workflow: {e}")
        results["workflow_success"] = False
    
    # Generate report
    print("\n" + "="*60)
    print("📋 QA CREDENTIALS TEST REPORT")
    print("="*60)
    
    for role in ["navigator", "agency", "client", "provider"]:
        print(f"\n{role.upper()}:")
        print(f"  Email: {QA_CREDENTIALS[role]['email']}")
        print(f"  Registration Status: {results[role]['registration']}")
        print(f"  Login Status: {results[role]['login']}")
    
    print(f"\nLICENSE CODE: {results['license_code'] or 'Not generated'}")
    
    print(f"\nWORKFLOW SUCCESS: {'✅ YES' if results['workflow_success'] else '❌ NO'}")
    
    if results["workflow_success"]:
        print("\n🎉 All QA credentials are working and the complete E2E workflow passed!")
    else:
        print("\n⚠️  Some issues were found in the QA credentials workflow.")
    
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()