#!/usr/bin/env python3
"""
Upgrade QA Agency to Tier 3 Access for All Areas
"""

import requests
import json

# Configuration
BASE_URL = "https://smartbiz-assess.preview.emergentagent.com/api"
AGENCY_CREDENTIALS = {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}

def authenticate_agency():
    """Authenticate agency and get token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=AGENCY_CREDENTIALS)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code}")
        return None

def upgrade_area_to_tier3(token, area_id):
    """Upgrade specific area to tier 3"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"area_id": area_id, "target_tier": "3"}
    
    response = requests.post(f"{BASE_URL}/agency/tier-configuration/upgrade", data=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {area_id}: Upgraded to tier {result['new_tier']} (cost: ${result['upgrade_cost']})")
        return True
    else:
        print(f"❌ {area_id}: Failed to upgrade - {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    print("🚀 Upgrading QA Agency to Tier 3 Access for All Areas...")
    
    # Authenticate
    token = authenticate_agency()
    if not token:
        print("❌ Failed to authenticate agency")
        return
    
    print("✅ Agency authenticated successfully")
    
    # Upgrade all areas to tier 3
    areas = [f"area{i}" for i in range(1, 11)]
    successful_upgrades = 0
    
    for area_id in areas:
        if upgrade_area_to_tier3(token, area_id):
            successful_upgrades += 1
    
    print(f"\n📊 Upgrade Summary: {successful_upgrades}/{len(areas)} areas upgraded to tier 3")
    
    if successful_upgrades == len(areas):
        print("🎉 All areas successfully upgraded to tier 3!")
    else:
        print("⚠️  Some areas failed to upgrade")

if __name__ == "__main__":
    main()