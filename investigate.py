#!/usr/bin/env python3
"""
Detailed Backend Investigation After JSX Fix
Investigating the actual response structures of failed endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

def authenticate():
    """Get auth token"""
    session = requests.Session()
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": QA_EMAIL, "password": QA_PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    return None

def investigate_endpoint(session, endpoint, description):
    """Investigate an endpoint and show its actual response"""
    print(f"\n🔍 INVESTIGATING: {description}")
    print(f"Endpoint: {endpoint}")
    print("-" * 60)
    
    try:
        response = session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A (not dict)'}")
                print("Response Sample:")
                print(json.dumps(data, indent=2, default=str)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2, default=str))
            except json.JSONDecodeError:
                print("Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}")
        else:
            print(f"Error Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")

def main():
    print("🔍 DETAILED BACKEND INVESTIGATION AFTER JSX FIX")
    print("=" * 60)
    
    # Authenticate
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Investigate failed endpoints
    investigate_endpoint(session, "/home/client", "Client Dashboard Data")
    investigate_endpoint(session, "/v2/rp/requirements/all", "V2 RP Requirements")
    investigate_endpoint(session, "/v2/rp/leads", "V2 RP Leads")
    
    # Also check some working endpoints for comparison
    investigate_endpoint(session, "/assessment/schema/tier-based", "Tier-based Assessment Schema (Working)")

if __name__ == "__main__":
    main()