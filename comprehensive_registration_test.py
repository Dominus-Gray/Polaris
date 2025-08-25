#!/usr/bin/env python3
"""
Comprehensive Role-Based Registration and Approval System Testing
Tests the complete workflow including approvals
"""

import requests
import json
import uuid
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-requirements.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Complete Role-Based Registration System at: {API_BASE}")

def test_complete_role_based_system():
    """Test the complete role-based registration and approval system"""
    print("🚀 COMPREHENSIVE ROLE-BASED REGISTRATION AND APPROVAL SYSTEM TEST")
    print("="*80)
    
    results = {}
    
    # Step 1: Create Navigator (auto-approved)
    print("\n=== STEP 1: CREATE NAVIGATOR ===")
    navigator_email = f"test_navigator_{uuid.uuid4().hex[:8]}@example.com"
    navigator_payload = {
        "email": navigator_email,
        "password": "NavigatorPass123!",
        "role": "navigator",
        "terms_accepted": True
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=navigator_payload)
    if response.status_code == 200:
        print(f"✅ Navigator registered: {navigator_email}")
        results["navigator_registration"] = True
        
        # Login as navigator
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": navigator_email,
            "password": "NavigatorPass123!"
        })
        if login_response.status_code == 200:
            navigator_token = login_response.json().get('access_token')
            print("✅ Navigator login successful")
            results["navigator_login"] = True
        else:
            print(f"❌ Navigator login failed: {login_response.text}")
            results["navigator_login"] = False
            return results
    else:
        print(f"❌ Navigator registration failed: {response.text}")
        results["navigator_registration"] = False
        return results
    
    # Step 2: Create Agency (pending approval)
    print("\n=== STEP 2: CREATE AGENCY (PENDING) ===")
    agency_email = f"test_agency_{uuid.uuid4().hex[:8]}@example.com"
    agency_payload = {
        "email": agency_email,
        "password": "AgencyPass123!",
        "role": "agency",
        "terms_accepted": True
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=agency_payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "pending":
            print(f"✅ Agency registered as pending: {agency_email}")
            results["agency_registration_pending"] = True
        else:
            print(f"❌ Agency should be pending, got: {data}")
            results["agency_registration_pending"] = False
    else:
        print(f"❌ Agency registration failed: {response.text}")
        results["agency_registration_pending"] = False
        return results
    
    # Step 3: Verify agency cannot login while pending
    print("\n=== STEP 3: VERIFY AGENCY LOGIN BLOCKED ===")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": agency_email,
        "password": "AgencyPass123!"
    })
    if login_response.status_code == 403:
        print("✅ Agency login correctly blocked while pending")
        results["agency_login_blocked"] = True
    else:
        print(f"❌ Agency should be blocked, got: {login_response.status_code}")
        results["agency_login_blocked"] = False
    
    # Step 4: Navigator approves agency
    print("\n=== STEP 4: NAVIGATOR APPROVES AGENCY ===")
    headers = {"Authorization": f"Bearer {navigator_token}"}
    
    # Get pending approvals
    pending_response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=headers)
    if pending_response.status_code == 200:
        pending_users = pending_response.json().get('pending_approvals', [])
        agency_user = next((user for user in pending_users if user.get('email') == agency_email), None)
        
        if agency_user:
            agency_user_id = agency_user.get('_id') or agency_user.get('id')
            approve_response = requests.post(
                f"{API_BASE}/admin/approve-user?user_id={agency_user_id}",
                headers=headers
            )
            if approve_response.status_code == 200:
                print("✅ Agency approved by navigator")
                results["agency_approval"] = True
            else:
                print(f"❌ Agency approval failed: {approve_response.text}")
                results["agency_approval"] = False
                return results
        else:
            print("❌ Agency not found in pending approvals")
            results["agency_approval"] = False
            return results
    else:
        print(f"❌ Could not get pending approvals: {pending_response.text}")
        results["agency_approval"] = False
        return results
    
    # Step 5: Verify agency can now login
    print("\n=== STEP 5: VERIFY AGENCY CAN NOW LOGIN ===")
    time.sleep(1)  # Brief delay for status update
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": agency_email,
        "password": "AgencyPass123!"
    })
    if login_response.status_code == 200:
        agency_token = login_response.json().get('access_token')
        print("✅ Agency can now login after approval")
        results["agency_login_after_approval"] = True
    else:
        print(f"❌ Agency still cannot login: {login_response.text}")
        results["agency_login_after_approval"] = False
        return results
    
    # Step 6: Test License Management System
    print("\n=== STEP 6: TEST LICENSE MANAGEMENT ===")
    agency_headers = {"Authorization": f"Bearer {agency_token}"}
    
    # Generate licenses
    license_response = requests.post(
        f"{API_BASE}/agency/licenses/generate",
        json={"quantity": 5},
        headers=agency_headers
    )
    if license_response.status_code == 200:
        licenses = license_response.json().get('licenses', [])
        if len(licenses) == 5:
            print(f"✅ Generated {len(licenses)} license codes")
            results["license_generation"] = True
            
            # Store first license for client registration
            test_license_code = licenses[0].get('license_code')
            print(f"Test license code: {test_license_code}")
        else:
            print(f"❌ Expected 5 licenses, got {len(licenses)}")
            results["license_generation"] = False
            return results
    else:
        print(f"❌ License generation failed: {license_response.text}")
        results["license_generation"] = False
        return results
    
    # Test license retrieval
    license_list_response = requests.get(f"{API_BASE}/agency/licenses", headers=agency_headers)
    if license_list_response.status_code == 200:
        licenses = license_list_response.json().get('licenses', [])
        print(f"✅ Retrieved {len(licenses)} licenses")
        results["license_retrieval"] = True
    else:
        print(f"❌ License retrieval failed: {license_list_response.text}")
        results["license_retrieval"] = False
    
    # Test license statistics
    stats_response = requests.get(f"{API_BASE}/agency/licenses/stats", headers=agency_headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ License stats: {stats}")
        results["license_statistics"] = True
    else:
        print(f"❌ License statistics failed: {stats_response.text}")
        results["license_statistics"] = False
    
    # Step 7: Test Client Registration with License Code
    print("\n=== STEP 7: TEST CLIENT REGISTRATION WITH LICENSE ===")
    client_email = f"test_client_{uuid.uuid4().hex[:8]}@example.com"
    client_payload = {
        "email": client_email,
        "password": "ClientPass123!",
        "role": "client",
        "terms_accepted": True,
        "license_code": test_license_code,
        "payment_info": {
            "payment_method": "credit_card",
            "billing_address": "123 Test St, San Antonio, TX 78201"
        }
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=client_payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "approved":
            print(f"✅ Client registered and auto-approved: {client_email}")
            results["client_registration_with_license"] = True
            
            # Verify client can login immediately
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": client_email,
                "password": "ClientPass123!"
            })
            if login_response.status_code == 200:
                client_token = login_response.json().get('access_token')
                print("✅ Client can login immediately after registration")
                results["client_immediate_login"] = True
            else:
                print(f"❌ Client cannot login: {login_response.text}")
                results["client_immediate_login"] = False
        else:
            print(f"❌ Client should be auto-approved, got: {data}")
            results["client_registration_with_license"] = False
    else:
        print(f"❌ Client registration failed: {response.text}")
        results["client_registration_with_license"] = False
    
    # Step 8: Verify License Usage
    print("\n=== STEP 8: VERIFY LICENSE USAGE ===")
    stats_response = requests.get(f"{API_BASE}/agency/licenses/stats", headers=agency_headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        used_count = stats.get('used', 0)
        if used_count >= 1:
            print(f"✅ License marked as used: {used_count} licenses used")
            results["license_usage_tracking"] = True
        else:
            print(f"❌ License not marked as used: {stats}")
            results["license_usage_tracking"] = False
    else:
        print(f"❌ Could not check license usage: {stats_response.text}")
        results["license_usage_tracking"] = False
    
    # Step 9: Test Provider Registration and Approval Workflow
    print("\n=== STEP 9: TEST PROVIDER APPROVAL WORKFLOW ===")
    provider_email = f"test_provider_{uuid.uuid4().hex[:8]}@example.com"
    provider_payload = {
        "email": provider_email,
        "password": "ProviderPass123!",
        "role": "provider",
        "terms_accepted": True,
        "payment_info": {
            "payment_method": "bank_transfer",
            "billing_address": "456 Provider Ave, San Antonio, TX 78202"
        }
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=provider_payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "pending":
            print(f"✅ Provider registered as pending: {provider_email}")
            results["provider_registration_pending"] = True
            
            # Verify provider cannot login
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": provider_email,
                "password": "ProviderPass123!"
            })
            if login_response.status_code == 403:
                print("✅ Provider login correctly blocked while pending")
                results["provider_login_blocked"] = True
                
                # Navigator approves provider
                pending_response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=headers)
                if pending_response.status_code == 200:
                    pending_users = pending_response.json().get('pending_approvals', [])
                    provider_user = next((user for user in pending_users if user.get('email') == provider_email), None)
                    
                    if provider_user:
                        provider_user_id = provider_user.get('_id') or provider_user.get('id')
                        approve_response = requests.post(
                            f"{API_BASE}/admin/approve-user?user_id={provider_user_id}",
                            headers=headers
                        )
                        if approve_response.status_code == 200:
                            print("✅ Provider approved by navigator")
                            results["provider_approval"] = True
                            
                            # Verify provider can now login
                            time.sleep(1)
                            login_response = requests.post(f"{API_BASE}/auth/login", json={
                                "email": provider_email,
                                "password": "ProviderPass123!"
                            })
                            if login_response.status_code == 200:
                                print("✅ Provider can now login after approval")
                                results["provider_login_after_approval"] = True
                            else:
                                print(f"❌ Provider still cannot login: {login_response.text}")
                                results["provider_login_after_approval"] = False
                        else:
                            print(f"❌ Provider approval failed: {approve_response.text}")
                            results["provider_approval"] = False
                    else:
                        print("❌ Provider not found in pending approvals")
                        results["provider_approval"] = False
                else:
                    print(f"❌ Could not get pending approvals: {pending_response.text}")
                    results["provider_approval"] = False
            else:
                print(f"❌ Provider should be blocked, got: {login_response.status_code}")
                results["provider_login_blocked"] = False
        else:
            print(f"❌ Provider should be pending, got: {data}")
            results["provider_registration_pending"] = False
    else:
        print(f"❌ Provider registration failed: {response.text}")
        results["provider_registration_pending"] = False
    
    # Step 10: Test Role-Based Access Control
    print("\n=== STEP 10: TEST ROLE-BASED ACCESS CONTROL ===")
    
    # Test that only agencies can access license endpoints
    if 'client_token' in locals():
        client_headers = {"Authorization": f"Bearer {client_token}"}
        license_access_response = requests.get(f"{API_BASE}/agency/licenses", headers=client_headers)
        if license_access_response.status_code == 403:
            print("✅ Client correctly denied access to agency license endpoint")
            results["client_denied_agency_access"] = True
        else:
            print(f"❌ Client should be denied access, got: {license_access_response.status_code}")
            results["client_denied_agency_access"] = False
    
    # Test that only navigators can access admin endpoints
    if 'client_token' in locals():
        admin_access_response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=client_headers)
        if admin_access_response.status_code == 403:
            print("✅ Client correctly denied access to admin endpoint")
            results["client_denied_admin_access"] = True
        else:
            print(f"❌ Client should be denied access, got: {admin_access_response.status_code}")
            results["client_denied_admin_access"] = False
    
    # Print Summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    categories = {
        "User Registration & Authentication": [
            "navigator_registration", "navigator_login", "agency_registration_pending", 
            "agency_login_blocked", "client_registration_with_license", "client_immediate_login",
            "provider_registration_pending", "provider_login_blocked"
        ],
        "Approval Workflow": [
            "agency_approval", "agency_login_after_approval", "provider_approval", 
            "provider_login_after_approval"
        ],
        "License Management": [
            "license_generation", "license_retrieval", "license_statistics", "license_usage_tracking"
        ],
        "Access Control": [
            "client_denied_agency_access", "client_denied_admin_access"
        ]
    }
    
    for category, tests in categories.items():
        print(f"\n{category.upper()}:")
        for test_name in tests:
            if test_name in results:
                status = "✅ PASS" if results[test_name] else "❌ FAIL"
                print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All comprehensive role-based registration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    test_complete_role_based_system()