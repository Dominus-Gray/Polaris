#!/usr/bin/env python3
"""
Approve Provider QA Account
Use navigator credentials to approve the provider.qa@polaris.example.com account.
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://biz-matchmaker-1.preview.emergentagent.com/api"

def get_navigator_token():
    """Get token for navigator.qa@polaris.example.com"""
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": "navigator.qa@polaris.example.com",
                "password": "Polaris#2025!"
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            return login_response.json().get("access_token")
        else:
            print(f"Failed to login as navigator: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting navigator token: {e}")
        return None

def get_provider_user_id():
    """Get the user ID for provider.qa@polaris.example.com"""
    try:
        # Try to login to get the user ID from the error message or find another way
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": "provider.qa@polaris.example.com",
                "password": "Polaris#2025!"
            },
            timeout=10
        )
        
        # Even though login fails, we might be able to find the user ID
        # Let's try a different approach - search for pending providers
        return None
    except Exception as e:
        print(f"Error getting provider user ID: {e}")
        return None

def find_pending_providers(navigator_token):
    """Find pending providers that need approval"""
    try:
        headers = {"Authorization": f"Bearer {navigator_token}"}
        
        # Try different endpoints to find pending providers
        endpoints_to_try = [
            "/navigator/providers/pending",
            "/navigator/approvals/pending", 
            "/navigator/providers",
            "/admin/users?role=provider&status=pending"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                
                print(f"Trying {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    # Look for provider.qa@polaris.example.com in the response
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("email") == "provider.qa@polaris.example.com":
                                return item.get("id") or item.get("_id") or item.get("user_id")
                    elif isinstance(data, dict):
                        if "providers" in data:
                            for provider in data["providers"]:
                                if provider.get("email") == "provider.qa@polaris.example.com":
                                    return provider.get("id") or provider.get("_id") or provider.get("user_id")
                        elif "users" in data:
                            for user in data["users"]:
                                if user.get("email") == "provider.qa@polaris.example.com":
                                    return user.get("id") or user.get("_id") or user.get("user_id")
                
            except Exception as e:
                print(f"Error trying {endpoint}: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"Error finding pending providers: {e}")
        return None

def approve_provider(navigator_token, provider_user_id):
    """Approve the provider account"""
    try:
        headers = {"Authorization": f"Bearer {navigator_token}"}
        
        # Try different approval endpoints
        approval_endpoints = [
            "/navigator/providers/approve",
            "/navigator/approvals/approve",
            "/admin/users/approve"
        ]
        
        approval_data = {
            "provider_user_id": provider_user_id,
            "approval_status": "approved",
            "notes": "QA account approval for testing"
        }
        
        for endpoint in approval_endpoints:
            try:
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=approval_data,
                    headers=headers,
                    timeout=10
                )
                
                print(f"Trying approval at {endpoint}: {response.status_code}")
                if response.status_code in [200, 201]:
                    print(f"✅ Provider approved successfully via {endpoint}")
                    return True
                else:
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"Error trying {endpoint}: {e}")
                continue
        
        return False
    except Exception as e:
        print(f"Error approving provider: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("APPROVING PROVIDER QA ACCOUNT")
    print("=" * 60)
    
    # Get navigator token
    print("Getting navigator token...")
    navigator_token = get_navigator_token()
    
    if not navigator_token:
        print("❌ Cannot proceed without navigator token")
        return False
    
    print("✅ Navigator token obtained")
    
    # Find pending providers
    print("Finding pending providers...")
    provider_user_id = find_pending_providers(navigator_token)
    
    if not provider_user_id:
        print("❌ Could not find provider.qa@polaris.example.com user ID")
        return False
    
    print(f"✅ Found provider user ID: {provider_user_id}")
    
    # Approve provider
    print("Approving provider...")
    if approve_provider(navigator_token, provider_user_id):
        print("✅ Provider approved successfully!")
        return True
    else:
        print("❌ Failed to approve provider")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)