#!/usr/bin/env python3
"""
Role-Based Registration and Approval System Testing
Tests the complete role-based registration and approval system as specified in the review request
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://providermatrix.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Role-Based Registration System at: {API_BASE}")

class TestResults:
    def __init__(self):
        self.results = {}
        self.tokens = {}
        self.users = {}
        
    def add_result(self, test_name, passed, details=""):
        self.results[test_name] = {"passed": passed, "details": details}
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
    
    def get_summary(self):
        passed = sum(1 for r in self.results.values() if r["passed"])
        total = len(self.results)
        return passed, total

def test_role_based_registration(test_results):
    """Test user registration with different roles"""
    print("\n=== 1. ROLE-BASED REGISTRATION SYSTEM ===")
    
    # Test data for different roles
    test_users = [
        {"role": "client", "email": f"client_{uuid.uuid4().hex[:8]}@example.com", "password": "ClientPass123!", "license_required": True},
        {"role": "agency", "email": f"agency_{uuid.uuid4().hex[:8]}@example.com", "password": "AgencyPass123!", "license_required": False},
        {"role": "provider", "email": f"provider_{uuid.uuid4().hex[:8]}@example.com", "password": "ProviderPass123!", "license_required": False},
        {"role": "navigator", "email": f"navigator_{uuid.uuid4().hex[:8]}@example.com", "password": "NavigatorPass123!", "license_required": False}
    ]
    
    for user_data in test_users:
        print(f"\n--- Testing {user_data['role']} registration ---")
        
        # First, generate a license code if needed for client
        license_code = None
        if user_data["license_required"]:
            # Create an agency first to generate license codes
            agency_email = f"license_agency_{uuid.uuid4().hex[:8]}@example.com"
            agency_payload = {
                "email": agency_email,
                "password": "AgencyPass123!",
                "role": "agency",
                "terms_accepted": True
            }
            
            try:
                response = requests.post(f"{API_BASE}/auth/register", json=agency_payload)
                if response.status_code == 200:
                    # Login as agency
                    login_response = requests.post(f"{API_BASE}/auth/login", json={
                        "email": agency_email,
                        "password": "AgencyPass123!"
                    })
                    if login_response.status_code == 200:
                        agency_token = login_response.json().get('access_token')
                        
                        # Generate license code
                        license_response = requests.post(
                            f"{API_BASE}/agency/licenses/generate",
                            json={"quantity": 1},  # Changed from "count" to "quantity"
                            headers={"Authorization": f"Bearer {agency_token}"}
                        )
                        if license_response.status_code == 200:
                            licenses = license_response.json().get('licenses', [])
                            if licenses:
                                license_code = licenses[0].get('license_code')
                                print(f"Generated license code: {license_code}")
            except Exception as e:
                print(f"Warning: Could not generate license code: {e}")
        
        # Prepare registration payload
        payload = {
            "email": user_data["email"],
            "password": user_data["password"],
            "role": user_data["role"],
            "terms_accepted": True
        }
        
        # Add license code for client
        if user_data["role"] == "client" and license_code:
            payload["license_code"] = license_code
        
        # Add payment info for clients and providers
        if user_data["role"] in ["client", "provider"]:
            payload["payment_info"] = {
                "payment_method": "credit_card",
                "billing_address": "123 Test St, San Antonio, TX 78201"
            }
        
        try:
            response = requests.post(f"{API_BASE}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                test_results.users[user_data["role"]] = {
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "registration_data": data
                }
                
                # Check approval status based on role
                expected_status = "approved" if user_data["role"] in ["client", "navigator"] else "pending"
                actual_status = data.get("status", "approved")
                
                if actual_status == expected_status:
                    test_results.add_result(
                        f"{user_data['role']}_registration",
                        True,
                        f"Role: {user_data['role']}, Status: {actual_status}"
                    )
                else:
                    test_results.add_result(
                        f"{user_data['role']}_registration",
                        False,
                        f"Expected status: {expected_status}, Got: {actual_status}"
                    )
            else:
                test_results.add_result(
                    f"{user_data['role']}_registration",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            test_results.add_result(
                f"{user_data['role']}_registration",
                False,
                f"Exception: {str(e)}"
            )

def test_license_management_system(test_results):
    """Test license management system endpoints"""
    print("\n=== 2. LICENSE MANAGEMENT SYSTEM ===")
    
    # First, create and login as agency to test license management
    agency_email = f"license_test_agency_{uuid.uuid4().hex[:8]}@example.com"
    agency_payload = {
        "email": agency_email,
        "password": "LicenseAgencyPass123!",
        "role": "agency",
        "terms_accepted": True
    }
    
    try:
        # Register agency
        response = requests.post(f"{API_BASE}/auth/register", json=agency_payload)
        if response.status_code != 200:
            test_results.add_result("license_agency_setup", False, f"Agency registration failed: {response.text}")
            return
        
        # Login as agency
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": agency_email,
            "password": "LicenseAgencyPass123!"
        })
        if login_response.status_code != 200:
            test_results.add_result("license_agency_setup", False, f"Agency login failed: {login_response.text}")
            return
        
        agency_token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {agency_token}"}
        
        # Test 1: POST /api/agency/licenses/generate
        print("\n--- Testing license generation ---")
        generate_payload = {"quantity": 5}  # Changed from "count" to "quantity"
        response = requests.post(f"{API_BASE}/agency/licenses/generate", json=generate_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            licenses = data.get('licenses', [])
            if len(licenses) == 5:
                # Check license format (should be 10-digit codes)
                valid_licenses = all(
                    len(license.get('license_code', '')) == 10 and license.get('license_code', '').isdigit()
                    for license in licenses
                )
                test_results.add_result(
                    "license_generation",
                    valid_licenses,
                    f"Generated {len(licenses)} licenses with valid format"
                )
            else:
                test_results.add_result("license_generation", False, f"Expected 5 licenses, got {len(licenses)}")
        else:
            test_results.add_result("license_generation", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test 2: GET /api/agency/licenses
        print("\n--- Testing license retrieval ---")
        response = requests.get(f"{API_BASE}/agency/licenses", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            licenses = data.get('licenses', [])
            test_results.add_result(
                "license_retrieval",
                len(licenses) >= 5,
                f"Retrieved {len(licenses)} licenses"
            )
        else:
            test_results.add_result("license_retrieval", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test 3: GET /api/agency/licenses/stats
        print("\n--- Testing license statistics ---")
        response = requests.get(f"{API_BASE}/agency/licenses/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ['total_generated', 'available', 'used']
            has_all_fields = all(field in data for field in required_fields)
            test_results.add_result(
                "license_statistics",
                has_all_fields,
                f"Stats: {data}" if has_all_fields else f"Missing fields in: {data}"
            )
        else:
            test_results.add_result("license_statistics", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test 4: License uniqueness verification
        print("\n--- Testing license uniqueness ---")
        response = requests.post(f"{API_BASE}/agency/licenses/generate", json={"quantity": 3}, headers=headers)  # Changed from "count" to "quantity"
        
        if response.status_code == 200:
            new_licenses = response.json().get('licenses', [])
            all_licenses_response = requests.get(f"{API_BASE}/agency/licenses", headers=headers)
            
            if all_licenses_response.status_code == 200:
                all_licenses = all_licenses_response.json().get('licenses', [])
                license_codes = [license.get('license_code') for license in all_licenses]
                unique_codes = set(license_codes)
                
                test_results.add_result(
                    "license_uniqueness",
                    len(license_codes) == len(unique_codes),
                    f"Generated {len(license_codes)} codes, {len(unique_codes)} unique"
                )
            else:
                test_results.add_result("license_uniqueness", False, "Could not retrieve all licenses for uniqueness check")
        else:
            test_results.add_result("license_uniqueness", False, f"Could not generate additional licenses: {response.text}")
            
    except Exception as e:
        test_results.add_result("license_management_system", False, f"Exception: {str(e)}")

def test_navigator_approval_system(test_results):
    """Test navigator approval system endpoints"""
    print("\n=== 3. NAVIGATOR APPROVAL SYSTEM ===")
    
    # Create and login as navigator
    navigator_email = f"approval_navigator_{uuid.uuid4().hex[:8]}@example.com"
    navigator_payload = {
        "email": navigator_email,
        "password": "NavigatorPass123!",
        "role": "navigator",
        "terms_accepted": True
    }
    
    try:
        # Register navigator
        response = requests.post(f"{API_BASE}/auth/register", json=navigator_payload)
        if response.status_code != 200:
            test_results.add_result("navigator_setup", False, f"Navigator registration failed: {response.text}")
            return
        
        # Login as navigator
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": navigator_email,
            "password": "NavigatorPass123!"
        })
        if login_response.status_code != 200:
            test_results.add_result("navigator_setup", False, f"Navigator login failed: {login_response.text}")
            return
        
        navigator_token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {navigator_token}"}
        
        # Create some pending users for approval testing
        pending_users = []
        for role in ["agency", "provider"]:
            user_email = f"pending_{role}_{uuid.uuid4().hex[:8]}@example.com"
            user_payload = {
                "email": user_email,
                "password": f"{role.title()}Pass123!",
                "role": role,
                "terms_accepted": True
            }
            
            response = requests.post(f"{API_BASE}/auth/register", json=user_payload)
            if response.status_code == 200:
                pending_users.append({"email": user_email, "role": role})
        
        # Test 1: GET /api/admin/pending-approvals
        print("\n--- Testing pending approvals retrieval ---")
        response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            pending_list = data.get('pending_approvals', [])  # Changed from 'pending_users' to 'pending_approvals'
            test_results.add_result(
                "pending_approvals_retrieval",
                len(pending_list) >= len(pending_users),
                f"Found {len(pending_list)} pending users"
            )
            
            # Store first pending user for approval/rejection tests
            if pending_list:
                test_user = pending_list[0]
                test_results.pending_user_id = test_user.get('id')
        else:
            test_results.add_result("pending_approvals_retrieval", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test 2: POST /api/admin/approve-user
        if hasattr(test_results, 'pending_user_id'):
            print("\n--- Testing user approval ---")
            response = requests.post(
                f"{API_BASE}/admin/approve-user?user_id={test_results.pending_user_id}&notes=User meets all requirements for approval",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                test_results.add_result(
                    "user_approval",
                    "message" in data,  # Check for success message instead of 'success' field
                    f"Approval response: {data}"
                )
            else:
                test_results.add_result("user_approval", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test 3: POST /api/admin/reject-user (create another pending user first)
        reject_user_email = f"reject_provider_{uuid.uuid4().hex[:8]}@example.com"
        reject_payload = {
            "email": reject_user_email,
            "password": "RejectProviderPass123!",
            "role": "provider",
            "terms_accepted": True
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=reject_payload)
        if response.status_code == 200:
            # Get the user ID for rejection
            pending_response = requests.get(f"{API_BASE}/admin/pending-approvals", headers=headers)
            if pending_response.status_code == 200:
                pending_list = pending_response.json().get('pending_approvals', [])  # Changed from 'pending_users' to 'pending_approvals'
                reject_user = next((user for user in pending_list if user.get('email') == reject_user_email), None)
                
                if reject_user:
                    print("\n--- Testing user rejection ---")
                    response = requests.post(
                        f"{API_BASE}/admin/reject-user?user_id={reject_user.get('id')}&reason=Insufficient documentation provided",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        test_results.add_result(
                            "user_rejection",
                            "message" in data,  # Check for success message instead of 'success' field
                            f"Rejection response: {data}"
                        )
                    else:
                        test_results.add_result("user_rejection", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    test_results.add_result("user_rejection", False, "Could not find user to reject")
            else:
                test_results.add_result("user_rejection", False, "Could not retrieve pending users for rejection test")
        else:
            test_results.add_result("user_rejection", False, "Could not create user for rejection test")
            
    except Exception as e:
        test_results.add_result("navigator_approval_system", False, f"Exception: {str(e)}")

def test_authentication_flow(test_results):
    """Test authentication flow with different approval statuses"""
    print("\n=== 4. AUTHENTICATION FLOW ===")
    
    # Test login with different approval statuses
    test_cases = [
        {"role": "client", "expected_login": True, "description": "approved client"},
        {"role": "navigator", "expected_login": True, "description": "approved navigator"},
        {"role": "agency", "expected_login": False, "description": "pending agency"},
        {"role": "provider", "expected_login": False, "description": "pending provider"}
    ]
    
    for case in test_cases:
        if case["role"] in test_results.users:
            user_data = test_results.users[case["role"]]
            
            print(f"\n--- Testing login for {case['description']} ---")
            login_payload = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            try:
                response = requests.post(f"{API_BASE}/auth/login", json=login_payload)
                
                if case["expected_login"]:
                    # Should be able to login
                    if response.status_code == 200:
                        token = response.json().get('access_token')
                        if token:
                            test_results.tokens[case["role"]] = token
                            test_results.add_result(
                                f"{case['role']}_login_success",
                                True,
                                f"Successfully logged in {case['description']}"
                            )
                        else:
                            test_results.add_result(
                                f"{case['role']}_login_success",
                                False,
                                "Login succeeded but no token received"
                            )
                    else:
                        test_results.add_result(
                            f"{case['role']}_login_success",
                            False,
                            f"Expected successful login, got HTTP {response.status_code}: {response.text}"
                        )
                else:
                    # Should NOT be able to login (pending approval)
                    if response.status_code in [403, 400]:
                        test_results.add_result(
                            f"{case['role']}_login_blocked",
                            True,
                            f"Correctly blocked login for {case['description']}"
                        )
                    else:
                        test_results.add_result(
                            f"{case['role']}_login_blocked",
                            False,
                            f"Expected login to be blocked, got HTTP {response.status_code}: {response.text}"
                        )
                        
            except Exception as e:
                test_results.add_result(
                    f"{case['role']}_login_test",
                    False,
                    f"Exception during login test: {str(e)}"
                )

def test_role_based_access_control(test_results):
    """Test role-based access control across endpoints"""
    print("\n=== 5. ROLE-BASED ACCESS CONTROL ===")
    
    # Test endpoints that should be role-specific
    access_tests = [
        {
            "endpoint": "/api/agency/licenses",
            "method": "GET",
            "allowed_roles": ["agency"],
            "description": "Agency license access"
        },
        {
            "endpoint": "/api/admin/pending-approvals",
            "method": "GET",
            "allowed_roles": ["navigator"],
            "description": "Navigator admin access"
        },
        {
            "endpoint": "/api/client/matched-services",
            "method": "GET",
            "allowed_roles": ["client"],
            "description": "Client services access"
        }
    ]
    
    for test_case in access_tests:
        print(f"\n--- Testing {test_case['description']} ---")
        
        for role, token in test_results.tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                if test_case["method"] == "GET":
                    response = requests.get(f"{API_BASE}{test_case['endpoint']}", headers=headers)
                else:
                    response = requests.post(f"{API_BASE}{test_case['endpoint']}", headers=headers)
                
                if role in test_case["allowed_roles"]:
                    # Should have access
                    if response.status_code in [200, 404]:  # 404 is OK if no data exists
                        test_results.add_result(
                            f"{test_case['description'].lower().replace(' ', '_')}_{role}_allowed",
                            True,
                            f"{role} correctly allowed access"
                        )
                    else:
                        test_results.add_result(
                            f"{test_case['description'].lower().replace(' ', '_')}_{role}_allowed",
                            False,
                            f"{role} denied access unexpectedly: HTTP {response.status_code}"
                        )
                else:
                    # Should be denied access
                    if response.status_code == 403:
                        test_results.add_result(
                            f"{test_case['description'].lower().replace(' ', '_')}_{role}_denied",
                            True,
                            f"{role} correctly denied access"
                        )
                    else:
                        test_results.add_result(
                            f"{test_case['description'].lower().replace(' ', '_')}_{role}_denied",
                            False,
                            f"{role} should be denied access, got HTTP {response.status_code}"
                        )
                        
            except Exception as e:
                test_results.add_result(
                    f"{test_case['description'].lower().replace(' ', '_')}_{role}_error",
                    False,
                    f"Exception testing {role} access: {str(e)}"
                )

def test_integration_flows(test_results):
    """Test end-to-end integration flows"""
    print("\n=== 6. INTEGRATION TESTING ===")
    
    # Test 1: End-to-end client registration with license code
    print("\n--- Testing end-to-end client registration flow ---")
    
    try:
        # Step 1: Create agency and generate license
        agency_email = f"integration_agency_{uuid.uuid4().hex[:8]}@example.com"
        agency_payload = {
            "email": agency_email,
            "password": "IntegrationAgency123!",
            "role": "agency",
            "terms_accepted": True
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=agency_payload)
        if response.status_code != 200:
            test_results.add_result("integration_client_flow", False, f"Agency creation failed: {response.text}")
            return
        
        # Login as agency
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": agency_email,
            "password": "IntegrationAgency123!"
        })
        if login_response.status_code != 200:
            test_results.add_result("integration_client_flow", False, f"Agency login failed: {login_response.text}")
            return
        
        agency_token = login_response.json().get('access_token')
        
        # Generate license
        license_response = requests.post(
            f"{API_BASE}/agency/licenses/generate",
            json={"quantity": 1},  # Changed from "count" to "quantity"
            headers={"Authorization": f"Bearer {agency_token}"}
        )
        if license_response.status_code != 200:
            test_results.add_result("integration_client_flow", False, f"License generation failed: {license_response.text}")
            return
        
        license_code = license_response.json().get('licenses', [{}])[0].get('license_code')
        if not license_code:
            test_results.add_result("integration_client_flow", False, "No license code generated")
            return
        
        # Step 2: Register client with license code
        client_email = f"integration_client_{uuid.uuid4().hex[:8]}@example.com"
        client_payload = {
            "email": client_email,
            "password": "IntegrationClient123!",
            "role": "client",
            "terms_accepted": True,
            "license_code": license_code,
            "payment_info": {
                "payment_method": "credit_card",
                "billing_address": "123 Integration St, San Antonio, TX 78201"
            }
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=client_payload)
        if response.status_code == 200:
            # Step 3: Verify client can login immediately (approved status)
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": client_email,
                "password": "IntegrationClient123!"
            })
            
            if login_response.status_code == 200:
                # Step 4: Verify license is marked as used
                license_stats_response = requests.get(
                    f"{API_BASE}/agency/licenses/stats",
                    headers={"Authorization": f"Bearer {agency_token}"}
                )
                
                if license_stats_response.status_code == 200:
                    stats = license_stats_response.json()
                    used_count = stats.get('used', 0)
                    
                    test_results.add_result(
                        "integration_client_flow",
                        used_count >= 1,
                        f"Complete client registration flow successful, {used_count} licenses used"
                    )
                else:
                    test_results.add_result("integration_client_flow", False, "Could not verify license usage")
            else:
                test_results.add_result("integration_client_flow", False, f"Client login failed: {login_response.text}")
        else:
            test_results.add_result("integration_client_flow", False, f"Client registration failed: {response.text}")
            
    except Exception as e:
        test_results.add_result("integration_client_flow", False, f"Exception: {str(e)}")
    
    # Test 2: Provider approval workflow
    print("\n--- Testing provider approval workflow ---")
    
    try:
        # Create navigator
        navigator_email = f"workflow_navigator_{uuid.uuid4().hex[:8]}@example.com"
        navigator_payload = {
            "email": navigator_email,
            "password": "WorkflowNavigator123!",
            "role": "navigator",
            "terms_accepted": True
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=navigator_payload)
        if response.status_code != 200:
            test_results.add_result("integration_provider_workflow", False, f"Navigator creation failed: {response.text}")
            return
        
        # Login as navigator
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": navigator_email,
            "password": "WorkflowNavigator123!"
        })
        if login_response.status_code != 200:
            test_results.add_result("integration_provider_workflow", False, f"Navigator login failed: {login_response.text}")
            return
        
        navigator_token = login_response.json().get('access_token')
        
        # Create provider (should be pending)
        provider_email = f"workflow_provider_{uuid.uuid4().hex[:8]}@example.com"
        provider_payload = {
            "email": provider_email,
            "password": "WorkflowProvider123!",
            "role": "provider",
            "terms_accepted": True,
            "payment_info": {
                "payment_method": "bank_transfer",
                "billing_address": "456 Provider Ave, San Antonio, TX 78202"
            }
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=provider_payload)
        if response.status_code != 200:
            test_results.add_result("integration_provider_workflow", False, f"Provider creation failed: {response.text}")
            return
        
        # Verify provider cannot login (pending status)
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": provider_email,
            "password": "WorkflowProvider123!"
        })
        
        if login_response.status_code in [403, 400]:
            # Get pending approvals
            pending_response = requests.get(
                f"{API_BASE}/admin/pending-approvals",
                headers={"Authorization": f"Bearer {navigator_token}"}
            )
            
            if pending_response.status_code == 200:
                pending_users = pending_response.json().get('pending_approvals', [])  # Changed from 'pending_users' to 'pending_approvals'
                provider_user = next((user for user in pending_users if user.get('email') == provider_email), None)
                
                if provider_user:
                    # Approve the provider
                    approve_response = requests.post(
                        f"{API_BASE}/admin/approve-user",
                        json={
                            "user_id": provider_user.get('id'),
                            "notes": "Provider approved for integration test"
                        },
                        headers={"Authorization": f"Bearer {navigator_token}"}
                    )
                    
                    if approve_response.status_code == 200:
                        # Now provider should be able to login
                        time.sleep(1)  # Brief delay for status update
                        final_login_response = requests.post(f"{API_BASE}/auth/login", json={
                            "email": provider_email,
                            "password": "WorkflowProvider123!"
                        })
                        
                        test_results.add_result(
                            "integration_provider_workflow",
                            final_login_response.status_code == 200,
                            f"Provider workflow complete, final login status: {final_login_response.status_code}"
                        )
                    else:
                        test_results.add_result("integration_provider_workflow", False, f"Provider approval failed: {approve_response.text}")
                else:
                    test_results.add_result("integration_provider_workflow", False, "Provider not found in pending approvals")
            else:
                test_results.add_result("integration_provider_workflow", False, f"Could not get pending approvals: {pending_response.text}")
        else:
            test_results.add_result("integration_provider_workflow", False, f"Provider should not be able to login initially, got: {login_response.status_code}")
            
    except Exception as e:
        test_results.add_result("integration_provider_workflow", False, f"Exception: {str(e)}")

def main():
    """Run all role-based registration and approval system tests"""
    print("🚀 Starting Role-Based Registration and Approval System Tests")
    print(f"Base URL: {API_BASE}")
    print("="*80)
    
    test_results = TestResults()
    
    # Run all test suites
    test_role_based_registration(test_results)
    test_license_management_system(test_results)
    test_navigator_approval_system(test_results)
    test_authentication_flow(test_results)
    test_role_based_access_control(test_results)
    test_integration_flows(test_results)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 ROLE-BASED REGISTRATION SYSTEM TEST SUMMARY")
    print("="*80)
    
    passed, total = test_results.get_summary()
    
    # Group results by category
    categories = {
        "Registration": [k for k in test_results.results.keys() if "registration" in k],
        "License Management": [k for k in test_results.results.keys() if "license" in k],
        "Navigator Approval": [k for k in test_results.results.keys() if any(x in k for x in ["approval", "pending", "reject"])],
        "Authentication": [k for k in test_results.results.keys() if "login" in k],
        "Access Control": [k for k in test_results.results.keys() if any(x in k for x in ["allowed", "denied", "access"])],
        "Integration": [k for k in test_results.results.keys() if "integration" in k]
    }
    
    for category, tests in categories.items():
        if tests:
            print(f"\n{category.upper()}:")
            for test_name in tests:
                result = test_results.results[test_name]
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {test_name.replace('_', ' ').title()}: {status}")
                if result["details"]:
                    print(f"    → {result['details']}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All role-based registration and approval system tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    main()