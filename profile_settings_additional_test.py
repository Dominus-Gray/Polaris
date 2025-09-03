#!/usr/bin/env python3
"""
Additional Profile Settings System Tests
Tests other profile endpoints like avatar upload, MFA, data export, etc.
"""

import requests
import json
import uuid
import os
import io
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartbiz-assess.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Additional Profile Settings at: {API_BASE}")

def register_and_login_user():
    """Register a new user and get auth token"""
    print("\n=== Setting up test user ===")
    
    # Generate unique email
    test_email = f"profile_additional_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "TestPass123!"
    
    # Register user
    register_data = {
        "email": test_email,
        "password": test_password,
        "role": "client",
        "terms_accepted": True
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return None
        
        # Login to get token
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ User registered and logged in: {test_email}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR in user setup: {e}")
        return None

def test_avatar_upload(token):
    """Test POST /api/profiles/me/avatar"""
    print("\n=== Testing POST /api/profiles/me/avatar ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a fake image file
    fake_image_content = b"fake_image_data_for_testing"
    files = {
        'file': ('test_avatar.jpg', io.BytesIO(fake_image_content), 'image/jpeg')
    }
    
    try:
        response = requests.post(f"{API_BASE}/profiles/me/avatar", files=files, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            avatar_data = response.json()
            print("✅ PASS: Avatar upload successful")
            
            if 'avatar_url' in avatar_data:
                print(f"Avatar URL: {avatar_data['avatar_url']}")
                return True
            else:
                print("❌ FAIL: No avatar_url in response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_data_export_request(token):
    """Test POST /api/profiles/me/data-export"""
    print("\n=== Testing POST /api/profiles/me/data-export ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/profiles/me/data-export", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            export_data = response.json()
            print("✅ PASS: Data export request successful")
            
            required_fields = ['request_id', 'status', 'estimated_completion']
            missing_fields = []
            
            for field in required_fields:
                if field not in export_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ FAIL: Missing fields: {missing_fields}")
                return False
            else:
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

def test_data_deletion_request(token):
    """Test POST /api/profiles/me/data-deletion"""
    print("\n=== Testing POST /api/profiles/me/data-deletion ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with correct confirmation text
    deletion_data = {
        "confirmation_text": "DELETE MY ACCOUNT"
    }
    
    try:
        response = requests.post(f"{API_BASE}/profiles/me/data-deletion", json=deletion_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            deletion_response = response.json()
            print("✅ PASS: Data deletion request successful")
            
            required_fields = ['deletion_id', 'confirmation_required', 'confirmation_email_sent']
            missing_fields = []
            
            for field in required_fields:
                if field not in deletion_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ FAIL: Missing fields: {missing_fields}")
                return False
            else:
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

def test_data_deletion_wrong_confirmation(token):
    """Test POST /api/profiles/me/data-deletion with wrong confirmation"""
    print("\n=== Testing POST /api/profiles/me/data-deletion - Wrong Confirmation ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with incorrect confirmation text
    deletion_data = {
        "confirmation_text": "DELETE ACCOUNT"  # Wrong text
    }
    
    try:
        response = requests.post(f"{API_BASE}/profiles/me/data-deletion", json=deletion_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ PASS: Wrong confirmation text properly rejected")
            return True
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_mfa_setup(token):
    """Test POST /api/security/mfa/setup"""
    print("\n=== Testing POST /api/security/mfa/setup ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    mfa_data = {
        "method": "totp"
    }
    
    try:
        response = requests.post(f"{API_BASE}/security/mfa/setup", json=mfa_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            mfa_response = response.json()
            print("✅ PASS: MFA setup successful")
            
            required_fields = ['secret', 'qr_code_url', 'backup_codes']
            missing_fields = []
            
            for field in required_fields:
                if field not in mfa_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, None
            else:
                print(f"Secret length: {len(mfa_response['secret'])}")
                print(f"QR code URL: {mfa_response['qr_code_url'][:50]}...")
                print(f"Backup codes count: {len(mfa_response['backup_codes'])}")
                return True, mfa_response['secret']
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def test_mfa_verify(token, secret):
    """Test POST /api/security/mfa/verify"""
    print("\n=== Testing POST /api/security/mfa/verify ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use a 6-digit code (demo implementation accepts any 6-digit code)
    verify_data = {
        "code": "123456",
        "secret": secret
    }
    
    try:
        response = requests.post(f"{API_BASE}/security/mfa/verify", json=verify_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            verify_response = response.json()
            print("✅ PASS: MFA verification successful")
            
            if 'verified' in verify_response and 'backup_codes' in verify_response:
                print(f"Verified: {verify_response['verified']}")
                print(f"Backup codes count: {len(verify_response['backup_codes'])}")
                return True
            else:
                print("❌ FAIL: Missing fields in verification response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_trusted_devices(token):
    """Test GET /api/security/trusted-devices"""
    print("\n=== Testing GET /api/security/trusted-devices ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/security/trusted-devices", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            devices = response.json()
            print("✅ PASS: Trusted devices retrieved successfully")
            
            if isinstance(devices, list):
                print(f"Trusted devices count: {len(devices)}")
                return True
            else:
                print("❌ FAIL: Response is not a list")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_unauthenticated_access():
    """Test that profile endpoints require authentication"""
    print("\n=== Testing Unauthenticated Access ===")
    
    endpoints = [
        "/profiles/me",
        "/profiles/me/data-export",
        "/security/mfa/setup",
        "/security/trusted-devices"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            print(f"{endpoint}: Status {response.status_code}")
            
            if response.status_code == 401:
                print(f"✅ PASS: {endpoint} properly requires authentication")
            else:
                print(f"❌ FAIL: {endpoint} should return 401, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ ERROR testing {endpoint}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all additional Profile Settings System tests"""
    print("🚀 Starting Additional Profile Settings System Tests")
    print(f"Base URL: {API_BASE}")
    
    results = {}
    
    # Test unauthenticated access first
    results['unauthenticated_access'] = test_unauthenticated_access()
    
    # Setup test user
    token = register_and_login_user()
    if not token:
        print("❌ CRITICAL: Could not set up test user")
        return False
    
    # Test 1: Avatar upload
    results['avatar_upload'] = test_avatar_upload(token)
    
    # Test 2: Data export request
    results['data_export_request'] = test_data_export_request(token)
    
    # Test 3: Data deletion request (correct confirmation)
    results['data_deletion_request'] = test_data_deletion_request(token)
    
    # Test 4: Data deletion request (wrong confirmation)
    results['data_deletion_wrong_confirmation'] = test_data_deletion_wrong_confirmation(token)
    
    # Test 5: MFA setup
    mfa_success, secret = test_mfa_setup(token)
    results['mfa_setup'] = mfa_success
    
    # Test 6: MFA verify (if setup succeeded)
    if mfa_success and secret:
        results['mfa_verify'] = test_mfa_verify(token, secret)
    else:
        results['mfa_verify'] = False
    
    # Test 7: Trusted devices
    results['trusted_devices'] = test_trusted_devices(token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 ADDITIONAL PROFILE SETTINGS TESTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    main()