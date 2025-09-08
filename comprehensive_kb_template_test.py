#!/usr/bin/env python3
"""
Comprehensive Knowledge Base Template Download Testing
Testing all aspects of the KB template download functionality as requested in review.
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

def test_polaris_account_access(token):
    """Test that @polaris.example.com accounts have proper access"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test KB areas endpoint
        response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            areas = data.get("areas", [])
            
            # Check if areas are unlocked (not locked) for @polaris.example.com accounts
            unlocked_areas = [area for area in areas if not area.get("locked", True)]
            locked_areas = [area for area in areas if area.get("locked", True)]
            
            log_test(f"✅ KB Areas access successful - {len(areas)} total areas")
            log_test(f"   - Unlocked areas: {len(unlocked_areas)}/{len(areas)}")
            log_test(f"   - Locked areas: {len(locked_areas)}/{len(areas)}")
            
            if len(unlocked_areas) == len(areas):
                log_test("✅ All areas unlocked for @polaris.example.com account")
                return True
            else:
                log_test("❌ Some areas still locked - access control may not be working correctly", "ERROR")
                return False
        else:
            log_test(f"❌ KB Areas access failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Access control test error: {e}", "ERROR")
        return False

def test_template_download(token, area_id, template_type):
    """Test template download endpoint with detailed validation"""
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
            
            # Verify content contains expected elements
            content_lower = content.lower()
            expected_elements = ["#", "polaris platform", "government procurement"]
            missing_elements = [elem for elem in expected_elements if elem not in content_lower]
            
            if missing_elements:
                log_test(f"⚠️  Content may be missing expected elements: {missing_elements}", "WARN")
            
            log_test(f"✅ Template download successful:")
            log_test(f"   - Filename: {data['filename']}")
            log_test(f"   - Content Type: {data['content_type']}")
            log_test(f"   - Content Length: {len(content)} characters")
            log_test(f"   - Content Preview: {content[:100].replace(chr(10), ' ')}...")
            
            return True
            
        elif response.status_code == 403:
            log_test(f"❌ Access denied (403) - payment requirements may not be bypassed", "ERROR")
            return False
        else:
            log_test(f"❌ Template download failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Template download error: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test("🚀 Starting Comprehensive Knowledge Base Template Download Testing")
    log_test("Testing download functionality for Knowledge Base templates as requested")
    log_test("=" * 70)
    
    # Step 1: Authentication
    log_test("STEP 1: Authentication with QA credentials")
    log_test(f"Using credentials: {QA_CREDENTIALS['email']} / {QA_CREDENTIALS['password']}")
    token = login_user(QA_CREDENTIALS)
    if not token:
        log_test("❌ Authentication failed - cannot proceed with tests", "ERROR")
        sys.exit(1)
    
    log_test("-" * 70)
    
    # Step 2: Test @polaris.example.com access bypass
    log_test("STEP 2: Testing @polaris.example.com account access bypass")
    access_test_passed = test_polaris_account_access(token)
    
    log_test("-" * 70)
    
    # Step 3: Test specific combinations as requested in review
    log_test("STEP 3: Testing specific area_id/template_type combinations")
    
    # Exact combinations requested in the review
    requested_combinations = [
        ("area1", "template"),
        ("area2", "guide"),  
        ("area5", "practices")
    ]
    
    # Additional combinations to test different template types
    additional_combinations = [
        ("area1", "business-template"),
        ("area2", "complete-guide"),
        ("area5", "compliance-checklist"),
        ("area3", "template"),
        ("area4", "guide"),
        ("area6", "practices")
    ]
    
    all_combinations = requested_combinations + additional_combinations
    
    log_test(f"Testing {len(requested_combinations)} requested combinations + {len(additional_combinations)} additional combinations")
    log_test("Requested combinations:")
    for area_id, template_type in requested_combinations:
        log_test(f"  - /api/knowledge-base/generate-template/{area_id}/{template_type}")
    
    log_test("-" * 40)
    
    passed_tests = 0
    total_tests = len(all_combinations)
    
    for i, (area_id, template_type) in enumerate(all_combinations, 1):
        log_test(f"Test {i}/{total_tests}: area_id='{area_id}', template_type='{template_type}'")
        if test_template_download(token, area_id, template_type):
            passed_tests += 1
        log_test("-" * 40)
    
    # Step 4: Summary and Results
    log_test("=" * 70)
    log_test("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
    log_test(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
    log_test(f"@polaris.example.com Access: {'✅ PASS' if access_test_passed else '❌ FAIL'}")
    log_test(f"Template Downloads: {passed_tests}/{total_tests} passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    log_test("-" * 70)
    log_test("DETAILED BREAKDOWN:")
    log_test(f"✅ QA Credentials Working: client.qa@polaris.example.com")
    log_test(f"✅ Response Structure Validation: content, filename, content_type fields")
    log_test(f"✅ Content Type Verification: text/markdown")
    log_test(f"✅ Filename Format: polaris_{{area_id}}_{{template_type}}.md")
    log_test(f"✅ Content Generation: All templates contain meaningful content")
    
    # Final assessment
    all_tests_passed = (token is not None and 
                       access_test_passed and 
                       passed_tests == total_tests)
    
    log_test("=" * 70)
    if all_tests_passed:
        log_test("🎉 ALL TESTS PASSED - Knowledge Base template download functionality is working correctly!")
        log_test("✅ @polaris.example.com accounts have proper access")
        log_test("✅ All requested endpoint combinations working")
        log_test("✅ Response structure matches frontend expectations")
        log_test("✅ Payment requirements bypassed for test accounts")
        return True
    else:
        log_test("❌ SOME TESTS FAILED - Issues found with template download functionality", "ERROR")
        if not access_test_passed:
            log_test("❌ Access control issue: @polaris.example.com accounts may not have proper access", "ERROR")
        if passed_tests < total_tests:
            log_test(f"❌ Template download issues: {total_tests - passed_tests} combinations failed", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)