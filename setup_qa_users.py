#!/usr/bin/env python3
"""
Setup QA Users for Testing
Creates the QA users needed for comprehensive backend testing.
"""

import requests
import json
import uuid

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"

# QA Credentials to create
QA_USERS = [
    {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client",
        "license_code": "1234567890"  # We'll need to generate this first
    },
    {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "role": "provider"
    },
    {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "navigator"
    },
    {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "agency"
    }
]

def setup_qa_users():
    """Setup QA users for testing"""
    session = requests.Session()
    
    print("🔧 SETTING UP QA USERS FOR TESTING")
    print("=" * 50)
    
    # First, let's try to create a navigator to approve agency and generate license
    navigator_created = False
    agency_token = None
    
    # Try to create navigator first
    for user in QA_USERS:
        if user["role"] == "navigator":
            try:
                response = session.post(f"{BACKEND_URL}/auth/register", json={
                    "email": user["email"],
                    "password": user["password"],
                    "role": user["role"],
                    "terms_accepted": True
                })
                
                if response.status_code == 200:
                    print(f"✅ Navigator created: {user['email']}")
                    navigator_created = True
                else:
                    print(f"⚠️ Navigator creation response: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Navigator creation failed: {str(e)}")
    
    # Try to create agency
    if navigator_created:
        for user in QA_USERS:
            if user["role"] == "agency":
                try:
                    response = session.post(f"{BACKEND_URL}/auth/register", json={
                        "email": user["email"],
                        "password": user["password"],
                        "role": user["role"],
                        "terms_accepted": True
                    })
                    
                    if response.status_code == 200:
                        print(f"✅ Agency created: {user['email']}")
                        
                        # Try to login navigator and approve agency
                        nav_login = session.post(f"{BACKEND_URL}/auth/login", json={
                            "email": "navigator.qa@polaris.example.com",
                            "password": "Polaris#2025!"
                        })
                        
                        if nav_login.status_code == 200:
                            nav_token = nav_login.json()["access_token"]
                            nav_headers = {"Authorization": f"Bearer {nav_token}"}
                            
                            # Try to approve agency - need to get agency ID from pending agencies
                            try:
                                # Get pending agencies
                                pending_response = session.get(f"{BACKEND_URL}/navigator/agencies/pending", headers=nav_headers)
                                
                                if pending_response.status_code == 200:
                                    pending_agencies = pending_response.json()
                                    
                                    # Find our agency
                                    agency_id = None
                                    for agency in pending_agencies.get("agencies", []):
                                        if agency.get("email") == user["email"]:
                                            agency_id = agency.get("id")
                                            break
                                    
                                    if agency_id:
                                        # Approve agency
                                        approval_response = session.post(f"{BACKEND_URL}/navigator/agencies/approve", 
                                                                       json={"agency_user_id": agency_id, "approval_status": "approved"},
                                                                       headers=nav_headers)
                                        
                                        if approval_response.status_code == 200:
                                            print(f"✅ Agency approved: {user['email']}")
                                            
                                            # Now login as agency to generate license
                                            agency_login = session.post(f"{BACKEND_URL}/auth/login", json={
                                                "email": user["email"],
                                                "password": user["password"]
                                            })
                                            
                                            if agency_login.status_code == 200:
                                                agency_token = agency_login.json()["access_token"]
                                                agency_headers = {"Authorization": f"Bearer {agency_token}"}
                                                
                                                # Generate license codes
                                                license_response = session.post(f"{BACKEND_URL}/agency/licenses/generate",
                                                                               json={"count": 5},
                                                                               headers=agency_headers)
                                                
                                                if license_response.status_code == 200:
                                                    licenses = license_response.json()
                                                    if licenses.get("license_codes"):
                                                        license_code = licenses["license_codes"][0]["license_code"]
                                                        print(f"✅ License generated: {license_code}")
                                                        
                                                        # Update client user with license code
                                                        for client_user in QA_USERS:
                                                            if client_user["role"] == "client":
                                                                client_user["license_code"] = license_code
                                                                break
                                                else:
                                                    print(f"⚠️ License generation failed: {license_response.status_code} - {license_response.text}")
                                            else:
                                                print(f"⚠️ Agency login after approval failed: {agency_login.status_code}")
                                        else:
                                            print(f"⚠️ Agency approval failed: {approval_response.status_code} - {approval_response.text}")
                                    else:
                                        print(f"⚠️ Agency not found in pending list")
                                else:
                                    print(f"⚠️ Failed to get pending agencies: {pending_response.status_code}")
                            except Exception as e:
                                print(f"❌ Agency approval process failed: {str(e)}")
                    else:
                        print(f"⚠️ Agency creation response: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"❌ Agency creation failed: {str(e)}")
    
    # Create remaining users
    for user in QA_USERS:
        if user["role"] in ["client", "provider"]:
            try:
                user_data = {
                    "email": user["email"],
                    "password": user["password"],
                    "role": user["role"],
                    "terms_accepted": True
                }
                
                if user["role"] == "client" and "license_code" in user:
                    user_data["license_code"] = user["license_code"]
                
                response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
                
                if response.status_code == 200:
                    print(f"✅ {user['role'].title()} created: {user['email']}")
                    
                    # If provider, try to approve it
                    if user["role"] == "provider" and navigator_created:
                        try:
                            # Login navigator
                            nav_login = session.post(f"{BACKEND_URL}/auth/login", json={
                                "email": "navigator.qa@polaris.example.com",
                                "password": "Polaris#2025!"
                            })
                            
                            if nav_login.status_code == 200:
                                nav_token = nav_login.json()["access_token"]
                                nav_headers = {"Authorization": f"Bearer {nav_token}"}
                                
                                # Get pending providers
                                pending_response = session.get(f"{BACKEND_URL}/navigator/providers/pending", headers=nav_headers)
                                
                                if pending_response.status_code == 200:
                                    pending_providers = pending_response.json()
                                    
                                    # Find our provider
                                    provider_id = None
                                    for provider in pending_providers.get("providers", []):
                                        if provider.get("email") == user["email"]:
                                            provider_id = provider.get("id")
                                            break
                                    
                                    if provider_id:
                                        # Approve provider
                                        approval_response = session.post(f"{BACKEND_URL}/navigator/providers/approve",
                                                                       json={"provider_user_id": provider_id, "approval_status": "approved"},
                                                                       headers=nav_headers)
                                        
                                        if approval_response.status_code == 200:
                                            print(f"✅ Provider approved: {user['email']}")
                                        else:
                                            print(f"⚠️ Provider approval failed: {approval_response.status_code} - {approval_response.text}")
                                    else:
                                        print(f"⚠️ Provider not found in pending list")
                                else:
                                    print(f"⚠️ Failed to get pending providers: {pending_response.status_code}")
                        except Exception as e:
                            print(f"❌ Provider approval failed: {str(e)}")
                else:
                    print(f"⚠️ {user['role'].title()} creation response: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ {user['role'].title()} creation failed: {str(e)}")
    
    print("\n🔍 TESTING QA USER AUTHENTICATION")
    print("=" * 50)
    
    # Test authentication for all users
    for user in QA_USERS:
        try:
            response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            
            if response.status_code == 200:
                print(f"✅ {user['role'].title()} login successful: {user['email']}")
            else:
                print(f"❌ {user['role'].title()} login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {user['role'].title()} login error: {str(e)}")
    
    print("\n✅ QA USER SETUP COMPLETE")

if __name__ == "__main__":
    setup_qa_users()