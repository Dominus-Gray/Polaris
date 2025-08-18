#!/usr/bin/env python3
"""
OAuth Callback Testing for Polaris MVP
Focused testing of OAuth callback endpoint and Emergent API integration
"""

import requests
import json
import uuid
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-sbap-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing OAuth callback at: {API_BASE}")

def test_emergent_oauth_api_direct():
    """Test direct calls to Emergent OAuth API"""
    print("\n=== Testing Direct Emergent OAuth API Integration ===")
    
    emergent_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
    
    # Test various session ID formats
    test_session_ids = [
        "test-session-12345",
        "invalid-session",
        "abc123def456",
        "session_with_underscores",
        "SESSION-UPPERCASE",
        "mixed-Case_Session123",
        "very-long-session-id-with-many-characters-12345678901234567890",
        "short",
        "",
        "   whitespace   ",
        "session\nwith\nnewlines",
        "session with spaces"
    ]
    
    results = []
    
    for session_id in test_session_ids:
        try:
            headers = {"X-Session-ID": session_id}
            response = requests.get(emergent_url, headers=headers, timeout=10)
            
            result = {
                "session_id": session_id,
                "status_code": response.status_code,
                "response_text": response.text[:200] if response.text else "",
                "headers": dict(response.headers)
            }
            results.append(result)
            
            print(f"Session ID: '{session_id}' -> Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Response: {response.text[:100]}")
                
        except Exception as e:
            result = {
                "session_id": session_id,
                "error": str(e),
                "status_code": "ERROR"
            }
            results.append(result)
            print(f"Session ID: '{session_id}' -> ERROR: {e}")
    
    return results

def test_oauth_callback_endpoint():
    """Test POST /api/auth/oauth/callback with various session IDs"""
    print("\n=== Testing OAuth Callback Endpoint ===")
    
    callback_url = f"{API_BASE}/auth/oauth/callback"
    
    # Test various session ID formats and scenarios
    test_cases = [
        {
            "name": "Valid format test session",
            "payload": {"session_id": "test-session-12345", "role": "client"}
        },
        {
            "name": "Empty session ID",
            "payload": {"session_id": "", "role": "client"}
        },
        {
            "name": "Missing session ID",
            "payload": {"role": "client"}
        },
        {
            "name": "Invalid session ID format",
            "payload": {"session_id": "invalid-session-format", "role": "client"}
        },
        {
            "name": "Long session ID",
            "payload": {"session_id": "very-long-session-id-with-many-characters-12345678901234567890", "role": "client"}
        },
        {
            "name": "Session with special characters",
            "payload": {"session_id": "session@#$%^&*()", "role": "client"}
        },
        {
            "name": "Whitespace session ID",
            "payload": {"session_id": "   whitespace   ", "role": "client"}
        },
        {
            "name": "Session with newlines",
            "payload": {"session_id": "session\nwith\nnewlines", "role": "client"}
        },
        {
            "name": "Valid role variations",
            "payload": {"session_id": "test-session-role", "role": "provider"}
        },
        {
            "name": "Invalid role",
            "payload": {"session_id": "test-session-role", "role": "invalid_role"}
        },
        {
            "name": "Missing role",
            "payload": {"session_id": "test-session-no-role"}
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"\nTesting: {test_case['name']}")
            
            response = requests.post(
                callback_url, 
                json=test_case['payload'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            result = {
                "test_name": test_case['name'],
                "payload": test_case['payload'],
                "status_code": response.status_code,
                "response_json": None,
                "response_text": response.text,
                "headers": dict(response.headers)
            }
            
            # Try to parse JSON response
            try:
                result["response_json"] = response.json()
            except:
                pass
            
            results.append(result)
            
            print(f"  Status: {response.status_code}")
            if response.status_code >= 400:
                print(f"  Error Response: {response.text[:200]}")
            elif response.status_code == 200:
                print(f"  Success Response: {response.text[:200]}")
                
        except Exception as e:
            result = {
                "test_name": test_case['name'],
                "payload": test_case['payload'],
                "error": str(e),
                "status_code": "ERROR"
            }
            results.append(result)
            print(f"  ERROR: {e}")
    
    return results

def test_oauth_error_handling():
    """Test specific error handling scenarios"""
    print("\n=== Testing OAuth Error Handling ===")
    
    callback_url = f"{API_BASE}/auth/oauth/callback"
    
    # Test malformed requests
    malformed_tests = [
        {
            "name": "Invalid JSON",
            "data": "invalid json data",
            "content_type": "application/json"
        },
        {
            "name": "Empty body",
            "data": "",
            "content_type": "application/json"
        },
        {
            "name": "Wrong content type",
            "data": json.dumps({"session_id": "test", "role": "client"}),
            "content_type": "text/plain"
        }
    ]
    
    results = []
    
    for test in malformed_tests:
        try:
            print(f"\nTesting: {test['name']}")
            
            response = requests.post(
                callback_url,
                data=test['data'],
                headers={"Content-Type": test['content_type']},
                timeout=10
            )
            
            result = {
                "test_name": test['name'],
                "status_code": response.status_code,
                "response_text": response.text,
                "expected": "Should return 422 or 400 for malformed requests"
            }
            results.append(result)
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
        except Exception as e:
            result = {
                "test_name": test['name'],
                "error": str(e),
                "status_code": "ERROR"
            }
            results.append(result)
            print(f"  ERROR: {e}")
    
    return results

def analyze_oauth_issues():
    """Analyze and summarize OAuth issues"""
    print("\n=== OAuth Issue Analysis ===")
    
    # Run all tests
    emergent_results = test_emergent_oauth_api_direct()
    callback_results = test_oauth_callback_endpoint()
    error_results = test_oauth_error_handling()
    
    print("\n=== ANALYSIS SUMMARY ===")
    
    # Analyze Emergent API responses
    print("\n1. Emergent API Analysis:")
    emergent_status_codes = {}
    for result in emergent_results:
        status = result.get('status_code', 'ERROR')
        emergent_status_codes[status] = emergent_status_codes.get(status, 0) + 1
    
    for status, count in emergent_status_codes.items():
        print(f"   Status {status}: {count} responses")
    
    # Analyze callback responses
    print("\n2. OAuth Callback Analysis:")
    callback_status_codes = {}
    for result in callback_results:
        status = result.get('status_code', 'ERROR')
        callback_status_codes[status] = callback_status_codes.get(status, 0) + 1
    
    for status, count in callback_status_codes.items():
        print(f"   Status {status}: {count} responses")
    
    # Check for specific issues
    print("\n3. Issue Detection:")
    
    # Check if 500 errors are being returned instead of 400
    server_errors = [r for r in callback_results if r.get('status_code') == 500]
    if server_errors:
        print(f"   ⚠️  Found {len(server_errors)} server errors (500) - these should likely be 400 errors")
        for error in server_errors[:3]:  # Show first 3
            print(f"      Test: {error['test_name']} -> {error.get('response_text', '')[:100]}")
    
    # Check if proper 400 errors are being returned
    bad_request_errors = [r for r in callback_results if r.get('status_code') == 400]
    if bad_request_errors:
        print(f"   ✅ Found {len(bad_request_errors)} proper 400 errors")
    
    # Check if 422 validation errors are working
    validation_errors = [r for r in callback_results if r.get('status_code') == 422]
    if validation_errors:
        print(f"   ✅ Found {len(validation_errors)} validation errors (422)")
    
    # Check for network/connectivity issues
    network_errors = [r for r in emergent_results if 'error' in r]
    if network_errors:
        print(f"   ⚠️  Found {len(network_errors)} network errors connecting to Emergent API")
    
    return {
        "emergent_results": emergent_results,
        "callback_results": callback_results,
        "error_results": error_results,
        "summary": {
            "emergent_status_codes": emergent_status_codes,
            "callback_status_codes": callback_status_codes,
            "server_errors": len(server_errors),
            "bad_request_errors": len(bad_request_errors),
            "validation_errors": len(validation_errors),
            "network_errors": len(network_errors)
        }
    }

def main():
    """Run all OAuth callback tests"""
    print("🔍 OAuth Callback Debugging Test Suite")
    print("=" * 50)
    
    try:
        analysis = analyze_oauth_issues()
        
        # Save detailed results to file
        with open('/app/oauth_test_results.json', 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"\n📊 Detailed results saved to: /app/oauth_test_results.json")
        
        # Final recommendations
        print("\n=== RECOMMENDATIONS ===")
        summary = analysis['summary']
        
        if summary['server_errors'] > 0:
            print("🔧 Fix server errors (500) - these should return proper 400/422 errors")
        
        if summary['network_errors'] > 0:
            print("🌐 Check network connectivity to Emergent OAuth API")
        
        if summary['bad_request_errors'] > 0:
            print("✅ OAuth callback is properly returning 400 errors for invalid sessions")
        
        if summary['validation_errors'] > 0:
            print("✅ OAuth callback is properly validating request format")
        
        print("\n🎯 Focus areas for debugging:")
        print("   1. Check if HTTPException(400) is being caught and converted to 500")
        print("   2. Verify Emergent API connectivity and response format")
        print("   3. Test with real Google OAuth session IDs vs test IDs")
        print("   4. Check request/response logging for actual OAuth flows")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()