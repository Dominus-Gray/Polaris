#!/usr/bin/env python3
"""
Debug Client Tier Access Issue
"""

import requests
import json

# Configuration
BASE_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"
CLIENT_CREDENTIALS = {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
AGENCY_CREDENTIALS = {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}

def authenticate_user(credentials):
    """Authenticate user and get token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code}")
        return None

def debug_client_tier_access():
    """Debug why client doesn't have tier 3 access"""
    print("🔍 Debugging Client Tier Access Issue...")
    
    # Get client token
    client_token = authenticate_user(CLIENT_CREDENTIALS)
    if not client_token:
        print("❌ Failed to authenticate client")
        return
    
    # Get agency token
    agency_token = authenticate_user(AGENCY_CREDENTIALS)
    if not agency_token:
        print("❌ Failed to authenticate agency")
        return
    
    print("✅ Both users authenticated successfully")
    
    # Check client info
    print("\n📋 Client Information:")
    client_headers = {"Authorization": f"Bearer {client_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=client_headers)
    if response.status_code == 200:
        client_info = response.json()
        print(f"   Client ID: {client_info['id']}")
        print(f"   Email: {client_info['email']}")
        print(f"   Role: {client_info['role']}")
    
    # Check agency info
    print("\n🏢 Agency Information:")
    agency_headers = {"Authorization": f"Bearer {agency_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=agency_headers)
    if response.status_code == 200:
        agency_info = response.json()
        print(f"   Agency ID: {agency_info['id']}")
        print(f"   Email: {agency_info['email']}")
        print(f"   Role: {agency_info['role']}")
    
    # Check agency tier configuration
    print("\n⚙️ Agency Tier Configuration:")
    response = requests.get(f"{BASE_URL}/agency/tier-configuration", headers=agency_headers)
    if response.status_code == 200:
        config = response.json()
        print(f"   Agency ID: {config['agency_id']}")
        tier_levels = config['tier_access_levels']
        tier3_areas = [area for area, tier in tier_levels.items() if tier >= 3]
        print(f"   Tier 3 Areas: {len(tier3_areas)}/10 ({tier3_areas})")
    
    # Check client tier access
    print("\n👤 Client Tier Access:")
    response = requests.get(f"{BASE_URL}/client/tier-access", headers=client_headers)
    if response.status_code == 200:
        access = response.json()
        areas = access.get('areas', [])
        tier3_client_areas = [area['area_id'] for area in areas if area.get('max_tier_access', 1) >= 3]
        print(f"   Client Tier 3 Areas: {len(tier3_client_areas)}/10 ({tier3_client_areas})")
        
        if len(tier3_client_areas) == 0:
            print("   ❌ Client has no tier 3 access - investigating...")
            
            # Check if client has license code
            print("\n🔗 License Code Investigation:")
            print("   Need to check database directly for license code linkage")
            print("   This suggests the client may not be properly linked to the agency")
    
    print("\n💡 Potential Issues:")
    print("   1. Client may not have a license code")
    print("   2. License code may not be linked to the agency")
    print("   3. Client tier access calculation may have a bug")
    print("   4. Database query may be using wrong field names")

def main():
    debug_client_tier_access()

if __name__ == "__main__":
    main()