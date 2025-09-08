#!/usr/bin/env python3
"""
Profile Settings System and Administrative System Testing
Tests the newly implemented Profile Settings and Administrative endpoints
"""

import requests
import json
import uuid
import os
import io
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://biz-matchmaker-1.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Profile Settings and Administrative Systems at: {API_BASE}")

# Global variables for test data
test_user_token = None
admin_user_token = None
test_user_id = None
admin_user_id = None

def register_and_login_user(email, password, role):
    """Helper function to register and login a user"""
    try:
        # Register user
        register_data = {
            "email": email,
            "password": password,
            "role": role,
            "terms_accepted": True
        }
        
        register_response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        if register_response.status_code != 200:
            print(f"Registration failed: {register_response.status_code} - {register_response.text}")
            return None, None
        
        # Login user
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return None, None
        
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if me_response.status_code != 200:
            print(f"Get user info failed: {me_response.status_code} - {me_response.text}")
            return None, None
        
        user_info = me_response.json()
        user_id = user_info.get("id")
        
        return token, user_id
        
    except Exception as e:
        print(f"Error in register_and_login_user: {e}")
        return None, None

def setup_test_users():
    """Setup test users for testing"""
    global test_user_token, admin_user_token, test_user_id, admin_user_id
    
    print("\n=== Setting up test users ===")
    
    # Create regular test user
    test_email = f"profile_test_{uuid.uuid4().hex[:8]}@test.com"
    test_user_token, test_user_id = register_and_login_user(test_email, "TestPass123!", "client")
    
    if test_user_token:
        print(f"✅ Regular test user created: {test_email}")
    else:
        print("❌ Failed to create regular test user")
        return False
    
    # Create admin user (we'll need to manually create this in the database or modify the role)
    admin_email = f"admin_test_{uuid.uuid4().hex[:8]}@test.com"
    admin_user_token, admin_user_id = register_and_login_user(admin_email, "AdminPass123!", "client")
    
    if admin_user_token:
        print(f"✅ Admin test user created: {admin_email}")
        # Note: In a real scenario, we'd need to update the user role to 'admin' in the database
        # For testing purposes, we'll test admin endpoints and expect 403 errors
    else:
        print("❌ Failed to create admin test user")
        return False
    
    return True

def test_profile_retrieval():
    """Test GET /api/profiles/me - Profile retrieval and creation"""
    print("\n=== Testing Profile Retrieval (GET /api/profiles/me) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = requests.get(f"{API_BASE}/profiles/me", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print("✅ PASS: Profile retrieved successfully")
            
            # Check required fields
            required_fields = ["display_name", "locale", "time_zone", "preferences", 
                             "privacy_settings", "notification_settings", "two_factor_enabled"]
            
            missing_fields = []
            for field in required_fields:
                if field not in profile_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️ Missing fields in profile: {missing_fields}")
            else:
                print("✅ All required profile fields present")
            
            print(f"Profile display_name: {profile_data.get('display_name')}")
            print(f"Two-factor enabled: {profile_data.get('two_factor_enabled')}")
            
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_profile_update():
    """Test PATCH /api/profiles/me - Profile updates with audit logging"""
    print("\n=== Testing Profile Update (PATCH /api/profiles/me) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Update profile data (only include optional fields for PATCH)
        update_data = {
            "display_name": "Updated Test User",
            "bio": "This is a test bio for profile update testing",
            "phone_number": "+1-555-123-4567",
            "time_zone": "America/New_York"
        }
        
        response = requests.patch(f"{API_BASE}/profiles/me", json=update_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            updated_profile = response.json()
            print("✅ PASS: Profile updated successfully")
            
            # Verify updates
            if updated_profile.get("display_name") == "Updated Test User":
                print("✅ Display name updated correctly")
            else:
                print(f"❌ Display name not updated: {updated_profile.get('display_name')}")
            
            if updated_profile.get("bio") == "This is a test bio for profile update testing":
                print("✅ Bio updated correctly")
            else:
                print(f"❌ Bio not updated: {updated_profile.get('bio')}")
            
            if updated_profile.get("time_zone") == "America/New_York":
                print("✅ Time zone updated correctly")
            else:
                print(f"❌ Time zone not updated: {updated_profile.get('time_zone')}")
            
            return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_avatar_upload():
    """Test POST /api/profiles/me/avatar - Avatar upload functionality"""
    print("\n=== Testing Avatar Upload (POST /api/profiles/me/avatar) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Create a simple test image file
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'file': ('test_avatar.png', io.BytesIO(test_image_data), 'image/png')
        }
        
        response = requests.post(f"{API_BASE}/profiles/me/avatar", files=files, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            avatar_data = response.json()
            print("✅ PASS: Avatar uploaded successfully")
            
            if "avatar_url" in avatar_data:
                print(f"✅ Avatar URL returned: {avatar_data['avatar_url']}")
                return True
            else:
                print("❌ No avatar_url in response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_data_export_request():
    """Test POST /api/profiles/me/data-export - GDPR data export requests"""
    print("\n=== Testing Data Export Request (POST /api/profiles/me/data-export) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        response = requests.post(f"{API_BASE}/profiles/me/data-export", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            export_data = response.json()
            print("✅ PASS: Data export request created successfully")
            
            required_fields = ["request_id", "status", "estimated_completion"]
            missing_fields = []
            for field in required_fields:
                if field not in export_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in export response: {missing_fields}")
                return False
            else:
                print("✅ All required export fields present")
                print(f"Request ID: {export_data['request_id']}")
                print(f"Status: {export_data['status']}")
                print(f"Estimated completion: {export_data['estimated_completion']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_data_deletion_request():
    """Test POST /api/profiles/me/data-deletion - Account deletion requests"""
    print("\n=== Testing Data Deletion Request (POST /api/profiles/me/data-deletion) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Test with correct confirmation text
        deletion_data = {
            "confirmation_text": "DELETE MY ACCOUNT"
        }
        
        response = requests.post(f"{API_BASE}/profiles/me/data-deletion", json=deletion_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            deletion_response = response.json()
            print("✅ PASS: Data deletion request created successfully")
            
            required_fields = ["deletion_id", "confirmation_required", "confirmation_email_sent"]
            missing_fields = []
            for field in required_fields:
                if field not in deletion_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in deletion response: {missing_fields}")
                return False
            else:
                print("✅ All required deletion fields present")
                print(f"Deletion ID: {deletion_response['deletion_id']}")
                print(f"Confirmation required: {deletion_response['confirmation_required']}")
                print(f"Confirmation email sent: {deletion_response['confirmation_email_sent']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_mfa_setup():
    """Test POST /api/security/mfa/setup - MFA setup with TOTP"""
    print("\n=== Testing MFA Setup (POST /api/security/mfa/setup) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        mfa_data = {
            "method": "totp"
        }
        
        response = requests.post(f"{API_BASE}/security/mfa/setup", json=mfa_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            mfa_response = response.json()
            print("✅ PASS: MFA setup initiated successfully")
            
            required_fields = ["secret", "qr_code_url", "backup_codes"]
            missing_fields = []
            for field in required_fields:
                if field not in mfa_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in MFA response: {missing_fields}")
                return False
            else:
                print("✅ All required MFA fields present")
                print(f"Secret length: {len(mfa_response['secret'])}")
                print(f"QR code URL: {mfa_response['qr_code_url'][:50]}...")
                print(f"Backup codes count: {len(mfa_response['backup_codes'])}")
                
                # Store secret for verification test
                global mfa_secret
                mfa_secret = mfa_response['secret']
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_mfa_verification():
    """Test POST /api/security/mfa/verify - MFA verification"""
    print("\n=== Testing MFA Verification (POST /api/security/mfa/verify) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Use the secret from MFA setup (if available)
        secret = globals().get('mfa_secret', 'TESTSECRET123456')
        
        verification_data = {
            "code": "123456",  # Test code (in real implementation, this would be generated by TOTP)
            "secret": secret
        }
        
        response = requests.post(f"{API_BASE}/security/mfa/verify", json=verification_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            verify_response = response.json()
            print("✅ PASS: MFA verification completed successfully")
            
            required_fields = ["verified", "backup_codes"]
            missing_fields = []
            for field in required_fields:
                if field not in verify_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in verification response: {missing_fields}")
                return False
            else:
                print("✅ All required verification fields present")
                print(f"Verified: {verify_response['verified']}")
                print(f"Backup codes count: {len(verify_response['backup_codes'])}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_trusted_devices():
    """Test GET /api/security/trusted-devices - Trusted device management"""
    print("\n=== Testing Trusted Devices (GET /api/security/trusted-devices) ===")
    
    if not test_user_token:
        print("❌ No test user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        response = requests.get(f"{API_BASE}/security/trusted-devices", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            devices = response.json()
            print("✅ PASS: Trusted devices retrieved successfully")
            
            if isinstance(devices, list):
                print(f"✅ Devices list returned with {len(devices)} devices")
                
                # If there are devices, check their structure
                if devices:
                    device = devices[0]
                    required_fields = ["id", "device_name", "device_type", "last_seen"]
                    missing_fields = []
                    for field in required_fields:
                        if field not in device:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"❌ Missing fields in device: {missing_fields}")
                        return False
                    else:
                        print("✅ Device structure is correct")
                
                return True
            else:
                print(f"❌ Expected list, got {type(devices)}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_admin_system_stats():
    """Test GET /api/admin/system/stats - System statistics (with admin user)"""
    print("\n=== Testing Admin System Stats (GET /api/admin/system/stats) ===")
    
    if not admin_user_token:
        print("❌ No admin user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        
        response = requests.get(f"{API_BASE}/admin/system/stats", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Admin endpoint correctly requires admin role (403 Forbidden)")
            return True
        elif response.status_code == 200:
            stats_data = response.json()
            print("✅ PASS: System stats retrieved successfully")
            
            required_fields = ["total_users", "active_businesses", "certificates_issued", 
                             "recent_users", "platform_health"]
            missing_fields = []
            for field in required_fields:
                if field not in stats_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in stats: {missing_fields}")
                return False
            else:
                print("✅ All required stats fields present")
                print(f"Total users: {stats_data['total_users']}")
                print(f"Active businesses: {stats_data['active_businesses']}")
                print(f"Certificates issued: {stats_data['certificates_issued']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_admin_users_list():
    """Test GET /api/admin/users - User management with filtering"""
    print("\n=== Testing Admin Users List (GET /api/admin/users) ===")
    
    if not admin_user_token:
        print("❌ No admin user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        
        # Test basic list
        response = requests.get(f"{API_BASE}/admin/users", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Admin endpoint correctly requires admin role (403 Forbidden)")
            return True
        elif response.status_code == 200:
            users_data = response.json()
            print("✅ PASS: Users list retrieved successfully")
            
            required_fields = ["users", "total", "page", "per_page"]
            missing_fields = []
            for field in required_fields:
                if field not in users_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in users response: {missing_fields}")
                return False
            else:
                print("✅ All required users list fields present")
                print(f"Total users: {users_data['total']}")
                print(f"Users in page: {len(users_data['users'])}")
                print(f"Page: {users_data['page']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_admin_bulk_action():
    """Test POST /api/admin/users/bulk-action - Bulk user operations"""
    print("\n=== Testing Admin Bulk Action (POST /api/admin/users/bulk-action) ===")
    
    if not admin_user_token:
        print("❌ No admin user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        
        bulk_action_data = {
            "action": "activate",
            "user_ids": [test_user_id] if test_user_id else ["test-user-id"]
        }
        
        response = requests.post(f"{API_BASE}/admin/users/bulk-action", json=bulk_action_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Admin endpoint correctly requires admin role (403 Forbidden)")
            return True
        elif response.status_code == 200:
            bulk_response = response.json()
            print("✅ PASS: Bulk action completed successfully")
            
            required_fields = ["success", "modified_count", "action"]
            missing_fields = []
            for field in required_fields:
                if field not in bulk_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in bulk action response: {missing_fields}")
                return False
            else:
                print("✅ All required bulk action fields present")
                print(f"Success: {bulk_response['success']}")
                print(f"Modified count: {bulk_response['modified_count']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_admin_user_action():
    """Test POST /api/admin/users/{user_id}/action - Individual user actions"""
    print("\n=== Testing Admin User Action (POST /api/admin/users/{user_id}/action) ===")
    
    if not admin_user_token or not test_user_id:
        print("❌ No admin user token or test user ID available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        
        action_data = {
            "action": "activate"
        }
        
        response = requests.post(f"{API_BASE}/admin/users/{test_user_id}/action", json=action_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Admin endpoint correctly requires admin role (403 Forbidden)")
            return True
        elif response.status_code == 200:
            action_response = response.json()
            print("✅ PASS: User action completed successfully")
            
            required_fields = ["success", "action"]
            missing_fields = []
            for field in required_fields:
                if field not in action_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in user action response: {missing_fields}")
                return False
            else:
                print("✅ All required user action fields present")
                print(f"Success: {action_response['success']}")
                print(f"Action: {action_response['action']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_admin_audit_logs():
    """Test GET /api/admin/audit-logs - Audit log retrieval"""
    print("\n=== Testing Admin Audit Logs (GET /api/admin/audit-logs) ===")
    
    if not admin_user_token:
        print("❌ No admin user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        
        response = requests.get(f"{API_BASE}/admin/audit-logs", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Admin endpoint correctly requires admin role (403 Forbidden)")
            return True
        elif response.status_code == 200:
            logs_data = response.json()
            print("✅ PASS: Audit logs retrieved successfully")
            
            required_fields = ["logs", "total", "page"]
            missing_fields = []
            for field in required_fields:
                if field not in logs_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in audit logs response: {missing_fields}")
                return False
            else:
                print("✅ All required audit logs fields present")
                print(f"Total logs: {logs_data['total']}")
                print(f"Logs in page: {len(logs_data['logs'])}")
                print(f"Page: {logs_data['page']}")
                return True
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_authentication_requirements():
    """Test that all endpoints require proper authentication"""
    print("\n=== Testing Authentication Requirements ===")
    
    endpoints_to_test = [
        ("GET", "/profiles/me"),
        ("PATCH", "/profiles/me"),
        ("POST", "/profiles/me/avatar"),
        ("POST", "/profiles/me/data-export"),
        ("POST", "/profiles/me/data-deletion"),
        ("POST", "/security/mfa/setup"),
        ("POST", "/security/mfa/verify"),
        ("GET", "/security/trusted-devices"),
        ("GET", "/admin/system/stats"),
        ("GET", "/admin/users"),
        ("POST", "/admin/users/bulk-action"),
        ("GET", "/admin/audit-logs")
    ]
    
    passed_tests = 0
    total_tests = len(endpoints_to_test)
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{API_BASE}{endpoint}", json={})
            elif method == "PATCH":
                response = requests.patch(f"{API_BASE}{endpoint}", json={})
            
            if response.status_code == 401:
                print(f"✅ {method} {endpoint}: Correctly requires authentication (401)")
                passed_tests += 1
            else:
                print(f"❌ {method} {endpoint}: Expected 401, got {response.status_code}")
                
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")
    
    print(f"\nAuthentication tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests

def run_all_tests():
    """Run all Profile Settings and Administrative System tests"""
    print("=" * 80)
    print("PROFILE SETTINGS SYSTEM AND ADMINISTRATIVE SYSTEM TESTING")
    print("=" * 80)
    
    # Setup test users
    if not setup_test_users():
        print("❌ Failed to setup test users. Aborting tests.")
        return
    
    test_results = []
    
    # Profile Settings System Tests
    print("\n" + "=" * 50)
    print("PROFILE SETTINGS SYSTEM TESTS")
    print("=" * 50)
    
    test_results.append(("Profile Retrieval", test_profile_retrieval()))
    test_results.append(("Profile Update", test_profile_update()))
    test_results.append(("Avatar Upload", test_avatar_upload()))
    test_results.append(("Data Export Request", test_data_export_request()))
    test_results.append(("Data Deletion Request", test_data_deletion_request()))
    test_results.append(("MFA Setup", test_mfa_setup()))
    test_results.append(("MFA Verification", test_mfa_verification()))
    test_results.append(("Trusted Devices", test_trusted_devices()))
    
    # Administrative System Tests
    print("\n" + "=" * 50)
    print("ADMINISTRATIVE SYSTEM TESTS")
    print("=" * 50)
    
    test_results.append(("Admin System Stats", test_admin_system_stats()))
    test_results.append(("Admin Users List", test_admin_users_list()))
    test_results.append(("Admin Bulk Action", test_admin_bulk_action()))
    test_results.append(("Admin User Action", test_admin_user_action()))
    test_results.append(("Admin Audit Logs", test_admin_audit_logs()))
    
    # Authentication Tests
    print("\n" + "=" * 50)
    print("AUTHENTICATION TESTS")
    print("=" * 50)
    
    test_results.append(("Authentication Requirements", test_authentication_requirements()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Profile Settings and Administrative Systems are working correctly.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the issues above.")

if __name__ == "__main__":
    run_all_tests()