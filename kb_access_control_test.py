#!/usr/bin/env python3
"""
Knowledge Base Access Control Testing
Testing that @polaris.example.com accounts have proper access and bypass payment requirements.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://polaris-inspector.preview.emergentagent.com/api"

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def login_user(credentials):
    """Login and get JWT token"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
        if response.status_code == 200:
            token = response.json()["access_token"]
            log_test(f"✅ Login successful for {credentials['email']}")
            return token
        else:
            log_test(f"❌ Login failed: {response.status_code} - {response.text}", "ERROR")
            return None
    except Exception as e:
        log_test(f"❌ Login error: {e}", "ERROR")
        return None

def test_kb_access(token, user_email):
    """Test Knowledge Base access"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test KB areas endpoint
        response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            areas = data.get("areas", [])
            log_test(f"✅ KB Areas access successful - {len(areas)} areas available")
            
            # Check if areas are unlocked for @polaris.example.com accounts
            unlocked_areas = [area for area in areas if area.get("unlocked", False)]
            log_test(f"   - Unlocked areas: {len(unlocked_areas)}/{len(areas)}")
            
            return len(unlocked_areas) > 0
        else:
            log_test(f"❌ KB Areas access failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ KB Access test error: {e}", "ERROR")
        return False

def test_template_access_without_payment(token, user_email):
    """Test that @polaris.example.com accounts can access templates without payment"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test template download for multiple areas
        test_areas = ["area1", "area2", "area5"]
        successful_downloads = 0
        
        for area_id in test_areas:
            url = f"{BACKEND_URL}/knowledge-base/generate-template/{area_id}/template"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                successful_downloads += 1
                log_test(f"✅ Template download successful for {area_id}")
            elif response.status_code == 403:
                log_test(f"❌ Access denied for {area_id} - payment may be required", "ERROR")
            else:
                log_test(f"❌ Template download failed for {area_id}: {response.status_code}", "ERROR")
        
        log_test(f"Template access summary: {successful_downloads}/{len(test_areas)} areas accessible")
        return successful_downloads == len(test_areas)
        
    except Exception as e:
        log_test(f"❌ Template access test error: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test("🚀 Starting Knowledge Base Access Control Testing")
    log_test("=" * 60)
    
    # Test with different account types
    test_accounts = [
        {
            "email": "client.qa@polaris.example.com",
            "password": "Polaris#2025!",
            "should_have_access": True,
            "description": "QA Client Account (@polaris.example.com)"
        }
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for account in test_accounts:
        log_test(f"Testing: {account['description']}")
        log_test("-" * 40)
        
        # Login
        token = login_user({"email": account["email"], "password": account["password"]})
        if not token:
            log_test(f"❌ Cannot test {account['email']} - login failed", "ERROR")
            total_tests += 2
            continue
        
        # Test KB access
        total_tests += 1
        if test_kb_access(token, account["email"]):
            passed_tests += 1
            log_test("✅ KB Access test passed")
        else:
            log_test("❌ KB Access test failed", "ERROR")
        
        # Test template access without payment
        total_tests += 1
        if test_template_access_without_payment(token, account["email"]):
            passed_tests += 1
            log_test("✅ Template access without payment test passed")
        else:
            log_test("❌ Template access without payment test failed", "ERROR")
        
        log_test("-" * 40)
    
    # Summary
    log_test("=" * 60)
    log_test("🎯 ACCESS CONTROL TEST SUMMARY")
    log_test(f"Total Tests: {total_tests}")
    log_test(f"Passed: {passed_tests}")
    log_test(f"Failed: {total_tests - passed_tests}")
    log_test(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests executed")
    
    if passed_tests == total_tests and total_tests > 0:
        log_test("✅ ALL ACCESS CONTROL TESTS PASSED")
        return True
    else:
        log_test("❌ SOME ACCESS CONTROL TESTS FAILED", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)