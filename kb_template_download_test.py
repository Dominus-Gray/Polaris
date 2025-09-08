#!/usr/bin/env python3
"""
Knowledge Base Template Download Testing
Testing the download functionality for Knowledge Base templates as requested in review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://biz-matchmaker-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

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

def test_template_download(token, area_id, template_type):
    """Test template download endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BACKEND_URL}/knowledge-base/generate-template/{area_id}/{template_type}"
        
        log_test(f"Testing: GET {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["content", "filename", "content_type"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test(f"❌ Missing fields in response: {missing_fields}", "ERROR")
                return False
            
            # Verify content type
            if data["content_type"] != "text/markdown":
                log_test(f"❌ Wrong content type: {data['content_type']} (expected: text/markdown)", "ERROR")
                return False
            
            # Verify filename format
            expected_filename = f"polaris_{area_id}_{template_type}.md"
            if data["filename"] != expected_filename:
                log_test(f"❌ Wrong filename: {data['filename']} (expected: {expected_filename})", "ERROR")
                return False
            
            # Verify content exists and is reasonable length
            content = data["content"]
            if not content or len(content) < 100:
                log_test(f"❌ Content too short or empty: {len(content)} chars", "ERROR")
                return False
            
            log_test(f"✅ Template download successful:")
            log_test(f"   - Filename: {data['filename']}")
            log_test(f"   - Content Type: {data['content_type']}")
            log_test(f"   - Content Length: {len(content)} characters")
            log_test(f"   - Content Preview: {content[:100]}...")
            
            return True
            
        else:
            log_test(f"❌ Template download failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Template download error: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test("🚀 Starting Knowledge Base Template Download Testing")
    log_test("=" * 60)
    
    # Login with QA credentials
    log_test("Step 1: Authenticating with QA credentials")
    token = login_user(QA_CREDENTIALS)
    if not token:
        log_test("❌ Authentication failed - cannot proceed with tests", "ERROR")
        sys.exit(1)
    
    # Test combinations as requested
    test_combinations = [
        ("area1", "template"),
        ("area1", "business-template"),  # Also test the actual endpoint name
        ("area2", "guide"),
        ("area2", "complete-guide"),  # Also test the actual endpoint name
        ("area5", "practices"),
        ("area5", "compliance-checklist"),  # Also test the actual endpoint name
        ("area3", "template"),
        ("area4", "guide"),
        ("area6", "practices")
    ]
    
    log_test(f"Step 2: Testing {len(test_combinations)} template download combinations")
    log_test("-" * 40)
    
    passed_tests = 0
    total_tests = len(test_combinations)
    
    for area_id, template_type in test_combinations:
        log_test(f"Testing area_id='{area_id}', template_type='{template_type}'")
        if test_template_download(token, area_id, template_type):
            passed_tests += 1
        log_test("-" * 40)
    
    # Summary
    log_test("=" * 60)
    log_test("🎯 KNOWLEDGE BASE TEMPLATE DOWNLOAD TEST SUMMARY")
    log_test(f"Total Tests: {total_tests}")
    log_test(f"Passed: {passed_tests}")
    log_test(f"Failed: {total_tests - passed_tests}")
    log_test(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        log_test("✅ ALL TESTS PASSED - Knowledge Base template download functionality working correctly")
        return True
    else:
        log_test("❌ SOME TESTS FAILED - Issues found with template download functionality", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)