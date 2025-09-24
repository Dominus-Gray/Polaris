#!/usr/bin/env python3
"""
Create Missing QA Accounts
Attempt to create the missing QA accounts that are referenced in the review request.
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# Missing QA accounts to create
MISSING_ACCOUNTS = [
    {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client",
        "terms_accepted": True,
        "license_code": None  # Will need to get a license code for client
    },
    {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "role": "provider",
        "terms_accepted": True
    },
    {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "navigator", 
        "terms_accepted": True
    }
]

def get_agency_token():
    """Get token for agency.qa@polaris.example.com to generate license codes"""
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": "agency.qa@polaris.example.com",
                "password": "Polaris#2025!"
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            return login_response.json().get("access_token")
        else:
            print(f"Failed to login as agency: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting agency token: {e}")
        return None

def generate_license_code(agency_token):
    """Generate a license code for client registration"""
    try:
        headers = {"Authorization": f"Bearer {agency_token}"}
        response = requests.post(
            f"{BACKEND_URL}/agency/licenses/generate",
            json={"quantity": 1, "expires_days": 365},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            licenses = data.get("licenses", [])
            if licenses:
                return licenses[0].get("license_code")
        else:
            print(f"Failed to generate license: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error generating license: {e}")
        return None

def create_account(account_data):
    """Attempt to create a single QA account"""
    try:
        print(f"Creating account: {account_data['email']} ({account_data['role']})")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=account_data,
            timeout=10
        )
        
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Successfully created {account_data['email']}")
            return True
        else:
            print(f"❌ Failed to create {account_data['email']}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {account_data['email']}: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("CREATING MISSING QA ACCOUNTS")
    print("=" * 60)
    
    # First, get agency token for license generation
    print("Getting agency token for license generation...")
    agency_token = get_agency_token()
    
    if not agency_token:
        print("❌ Cannot proceed without agency token")
        return False
    
    print("✅ Agency token obtained")
    
    # Generate license code for client
    print("Generating license code for client...")
    license_code = generate_license_code(agency_token)
    
    if not license_code:
        print("❌ Cannot create client without license code")
        return False
    
    print(f"✅ License code generated: {license_code}")
    
    # Update client account data with license code
    for account in MISSING_ACCOUNTS:
        if account["role"] == "client":
            account["license_code"] = license_code
    
    # Create accounts
    success_count = 0
    for account in MISSING_ACCOUNTS:
        if create_account(account):
            success_count += 1
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Accounts created successfully: {success_count}/{len(MISSING_ACCOUNTS)}")
    
    if success_count == len(MISSING_ACCOUNTS):
        print("🎉 All missing QA accounts created successfully!")
        return True
    else:
        print("⚠️ Some accounts could not be created")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)