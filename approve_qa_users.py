#!/usr/bin/env python3
"""
Approve existing QA Users for Testing
"""

import requests
import json

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"

def approve_qa_users():
    """Approve existing QA users"""
    session = requests.Session()
    
    print("🔧 APPROVING EXISTING QA USERS")
    print("=" * 50)
    
    # Login as navigator
    nav_login = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!"
    })
    
    if nav_login.status_code != 200:
        print(f"❌ Navigator login failed: {nav_login.status_code}")
        return
    
    nav_token = nav_login.json()["access_token"]
    nav_headers = {"Authorization": f"Bearer {nav_token}"}
    print("✅ Navigator authenticated")
    
    # Approve agency
    try:
        pending_response = session.get(f"{BACKEND_URL}/navigator/agencies/pending", headers=nav_headers)
        
        if pending_response.status_code == 200:
            pending_agencies = pending_response.json()
            print(f"📋 Found {len(pending_agencies.get('agencies', []))} pending agencies")
            
            for agency in pending_agencies.get("agencies", []):
                if agency.get("email") == "agency.qa@polaris.example.com":
                    agency_id = agency.get("id")
                    
                    approval_response = session.post(f"{BACKEND_URL}/navigator/agencies/approve", 
                                                   json={"agency_user_id": agency_id, "approval_status": "approved"},
                                                   headers=nav_headers)
                    
                    if approval_response.status_code == 200:
                        print(f"✅ Agency approved: agency.qa@polaris.example.com")
                        
                        # Now login as agency and generate license
                        agency_login = session.post(f"{BACKEND_URL}/auth/login", json={
                            "email": "agency.qa@polaris.example.com",
                            "password": "Polaris#2025!"
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
                                    
                                    # Now create client with this license
                                    client_response = session.post(f"{BACKEND_URL}/auth/register", json={
                                        "email": "client.qa@polaris.example.com",
                                        "password": "Polaris#2025!",
                                        "role": "client",
                                        "terms_accepted": True,
                                        "license_code": license_code
                                    })
                                    
                                    if client_response.status_code == 200:
                                        print(f"✅ Client created: client.qa@polaris.example.com")
                                    else:
                                        print(f"⚠️ Client creation failed: {client_response.status_code} - {client_response.text}")
                            else:
                                print(f"⚠️ License generation failed: {license_response.status_code}")
                        else:
                            print(f"⚠️ Agency login failed: {agency_login.status_code}")
                    else:
                        print(f"⚠️ Agency approval failed: {approval_response.status_code}")
                    break
        else:
            print(f"⚠️ Failed to get pending agencies: {pending_response.status_code}")
    except Exception as e:
        print(f"❌ Agency approval failed: {str(e)}")
    
    # Approve provider
    try:
        pending_response = session.get(f"{BACKEND_URL}/navigator/providers/pending", headers=nav_headers)
        
        if pending_response.status_code == 200:
            pending_providers = pending_response.json()
            print(f"📋 Found {len(pending_providers.get('providers', []))} pending providers")
            
            for provider in pending_providers.get("providers", []):
                if provider.get("email") == "provider.qa@polaris.example.com":
                    provider_id = provider.get("id")
                    
                    approval_response = session.post(f"{BACKEND_URL}/navigator/providers/approve",
                                                   json={"provider_user_id": provider_id, "approval_status": "approved"},
                                                   headers=nav_headers)
                    
                    if approval_response.status_code == 200:
                        print(f"✅ Provider approved: provider.qa@polaris.example.com")
                    else:
                        print(f"⚠️ Provider approval failed: {approval_response.status_code}")
                    break
        else:
            print(f"⚠️ Failed to get pending providers: {pending_response.status_code}")
    except Exception as e:
        print(f"❌ Provider approval failed: {str(e)}")
    
    print("\n🔍 TESTING QA USER AUTHENTICATION")
    print("=" * 50)
    
    # Test authentication for all users
    users = [
        {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!", "role": "client"},
        {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!", "role": "provider"},
        {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!", "role": "navigator"},
        {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!", "role": "agency"}
    ]
    
    for user in users:
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
    
    print("\n✅ QA USER APPROVAL COMPLETE")

if __name__ == "__main__":
    approve_qa_users()