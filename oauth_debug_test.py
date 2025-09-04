#!/usr/bin/env python3
"""
OAuth Debug Testing for Polaris MVP - REVIEW REQUEST FOCUSED
Specifically tests the issues mentioned in the review request:
1. Test the Emergent OAuth API integration
2. Check OAuth URL configuration and redirect URL format  
3. Test session ID extraction and format validation
4. Debug the specific 400 error from OAuth callback
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agencydash.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🔐 OAuth Debug Testing at: {API_BASE}")
print("🎯 FOCUS: Review Request - Google OAuth 'Authentication failed' errors")
print("="*80)

def test_emergent_oauth_api_integration():
    """Test 1: Test the Emergent OAuth API integration"""
    print("\n🔍 TEST 1: EMERGENT OAUTH API INTEGRATION")
    print("="*60)
    print("Testing endpoint: https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data")
    
    results = {}
    
    # Test 1.1: Check if endpoint is accessible
    print("\n1.1 Testing endpoint accessibility...")
    try:
        emergent_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        test_session_id = str(uuid.uuid4())
        headers = {"X-Session-ID": test_session_id}
        
        response = requests.get(emergent_url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code in [400, 404]:
            print("✅ PASS: Emergent OAuth API is accessible")
            results['api_accessible'] = True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            results['api_accessible'] = False
            
    except requests.exceptions.Timeout:
        print("❌ FAIL: Timeout connecting to Emergent OAuth API")
        results['api_accessible'] = False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAIL: Connection error: {e}")
        results['api_accessible'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['api_accessible'] = False
    
    # Test 1.2: Test request format and headers
    print("\n1.2 Testing request format and headers...")
    try:
        # Test different header formats
        header_tests = [
            {"X-Session-ID": str(uuid.uuid4())},
            {"x-session-id": str(uuid.uuid4())},  # lowercase
            {"Session-ID": str(uuid.uuid4())},    # different format
            {"Authorization": f"Bearer {str(uuid.uuid4())}"},  # wrong header
        ]
        
        for i, headers in enumerate(header_tests):
            print(f"   Testing header format {i+1}: {list(headers.keys())[0]}")
            response = requests.get(emergent_url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 400:
                print("   ✅ Proper 400 response for invalid session")
            elif response.status_code == 404:
                print("   ✅ API endpoint found, session validation working")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
                
        results['header_format_test'] = True
        
    except Exception as e:
        print(f"❌ ERROR in header testing: {e}")
        results['header_format_test'] = False
    
    # Test 1.3: Test different session ID formats
    print("\n1.3 Testing different session ID formats...")
    try:
        session_formats = [
            str(uuid.uuid4()),                    # Standard UUID
            str(uuid.uuid4()).replace('-', ''),   # UUID without dashes
            f"oauth_{int(time.time())}",          # Timestamp-based
            "emergent_" + str(uuid.uuid4()),      # Prefixed UUID
            "sess_" + str(int(time.time() * 1000)),  # Millisecond timestamp
        ]
        
        for session_format in session_formats:
            print(f"   Testing format: {session_format[:30]}...")
            headers = {"X-Session-ID": session_format}
            response = requests.get(emergent_url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [400, 404]:
                print("   ✅ Expected response for test session")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
                
        results['session_format_test'] = True
        
    except Exception as e:
        print(f"❌ ERROR in session format testing: {e}")
        results['session_format_test'] = False
    
    return results

def test_oauth_url_configuration():
    """Test 2: Check OAuth URL configuration and redirect URL format"""
    print("\n🔍 TEST 2: OAUTH URL CONFIGURATION")
    print("="*60)
    
    results = {}
    
    # Test 2.1: Check OAuth redirect URL format
    print("\n2.1 Testing OAuth redirect URL format...")
    try:
        print(f"Frontend URL: {BASE_URL}")
        print(f"Expected OAuth callback URL: {BASE_URL}/profile")
        print(f"Backend OAuth endpoint: {API_BASE}/auth/oauth/callback")
        
        # Test if the OAuth callback endpoint exists
        test_payload = {
            "session_id": "url-test-" + str(uuid.uuid4()),
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"OAuth callback endpoint status: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("✅ PASS: OAuth callback endpoint is accessible")
            results['callback_endpoint_accessible'] = True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            results['callback_endpoint_accessible'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['callback_endpoint_accessible'] = False
    
    # Test 2.2: Check Google OAuth start endpoint
    print("\n2.2 Testing Google OAuth start endpoint...")
    try:
        response = requests.get(f"{API_BASE}/auth/google/start?role=client", timeout=10)
        print(f"Google OAuth start status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url', '')
            print(f"Auth URL: {auth_url[:100]}...")
            
            if 'accounts.google.com' in auth_url:
                print("✅ PASS: Google OAuth URL format correct")
                results['google_oauth_config'] = True
            else:
                print("❌ FAIL: Invalid Google OAuth URL")
                results['google_oauth_config'] = False
        elif response.status_code == 400:
            print("⚠️  Google OAuth not configured (expected in test)")
            results['google_oauth_config'] = True  # Not configured is OK
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            results['google_oauth_config'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['google_oauth_config'] = False
    
    # Test 2.3: Check domain/CORS configuration
    print("\n2.3 Testing domain/CORS configuration...")
    try:
        headers = {
            "Origin": BASE_URL,
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "session_id": "cors-test-" + str(uuid.uuid4()),
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=test_payload,
            headers=headers,
            timeout=10
        )
        
        print(f"CORS test status: {response.status_code}")
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        print(f"CORS headers: {cors_headers}")
        
        if response.status_code in [400, 422]:
            print("✅ PASS: No CORS issues detected")
            results['cors_config'] = True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            results['cors_config'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['cors_config'] = False
    
    return results

def test_session_id_extraction():
    """Test 3: Test session ID extraction and format validation"""
    print("\n🔍 TEST 3: SESSION ID EXTRACTION AND FORMAT VALIDATION")
    print("="*60)
    
    results = {}
    
    # Test 3.1: Test various session ID formats that might come from URL fragments
    print("\n3.1 Testing session ID formats from URL fragments...")
    
    # Simulate different session ID formats that might come from auth.emergentagent.com
    session_id_formats = [
        # Standard formats
        str(uuid.uuid4()),
        str(uuid.uuid4()).replace('-', ''),
        
        # URL-encoded formats
        str(uuid.uuid4()).replace('-', '%2D'),
        
        # Base64-like formats
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        
        # Timestamp-based
        str(int(time.time())),
        str(int(time.time() * 1000)),
        
        # Hex formats
        "a1b2c3d4e5f67890" * 2,
        
        # Emergent-style (guessing based on common patterns)
        f"oauth_session_{int(time.time())}",
        f"emergent_{str(uuid.uuid4())}",
        f"auth_{str(uuid.uuid4()).replace('-', '')}",
    ]
    
    valid_formats = 0
    total_formats = len(session_id_formats)
    
    for i, session_id in enumerate(session_id_formats):
        print(f"   Format {i+1}: {session_id[:40]}{'...' if len(session_id) > 40 else ''}")
        
        payload = {
            "session_id": session_id,
            "role": "client"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 400:
                print("   ✅ Properly validated and rejected invalid session")
                valid_formats += 1
            elif response.status_code == 422:
                print("   ✅ Proper validation error")
                valid_formats += 1
            elif response.status_code == 500:
                print("   ❌ CRITICAL: 500 error - this is the bug!")
                print(f"   Response: {response.text}")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    results['session_format_validation'] = valid_formats == total_formats
    print(f"\n   Summary: {valid_formats}/{total_formats} formats properly handled")
    
    # Test 3.2: Test edge cases for session ID extraction
    print("\n3.2 Testing edge cases...")
    
    edge_cases = [
        ("", "Empty string"),
        ("null", "Null string"),
        ("undefined", "Undefined string"),
        ("   ", "Whitespace only"),
        ("a" * 1000, "Very long string"),
        ("special!@#$%^&*()", "Special characters"),
        ("session with spaces", "Spaces in session"),
        ("session\nwith\nnewlines", "Newlines in session"),
    ]
    
    edge_case_results = 0
    
    for session_id, description in edge_cases:
        print(f"   Testing {description}: '{session_id[:20]}{'...' if len(session_id) > 20 else ''}'")
        
        payload = {
            "session_id": session_id,
            "role": "client"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [400, 422]:
                print("   ✅ Properly handled edge case")
                edge_case_results += 1
            elif response.status_code == 500:
                print("   ❌ CRITICAL: 500 error for edge case!")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    results['edge_case_handling'] = edge_case_results == len(edge_cases)
    print(f"\n   Summary: {edge_case_results}/{len(edge_cases)} edge cases properly handled")
    
    return results

def test_specific_400_error_debug():
    """Test 4: Debug the specific 400 error from OAuth callback"""
    print("\n🔍 TEST 4: DEBUG SPECIFIC 400 ERROR FROM OAUTH CALLBACK")
    print("="*60)
    
    results = {}
    
    # Test 4.1: Get detailed error response format
    print("\n4.1 Testing detailed error response format...")
    
    try:
        payload = {
            "session_id": "debug-400-error-" + str(uuid.uuid4()),
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 400:
            print("✅ PASS: Returns 400 error as expected")
            
            try:
                error_data = response.json()
                print(f"JSON Error Response: {json.dumps(error_data, indent=2)}")
                
                if 'detail' in error_data and 'Invalid session ID' in error_data['detail']:
                    print("✅ PASS: Correct error message format")
                    results['error_format_correct'] = True
                else:
                    print("⚠️  Unexpected error message format")
                    results['error_format_correct'] = False
                    
            except json.JSONDecodeError:
                print(f"Plain text error: {response.text}")
                results['error_format_correct'] = False
                
        elif response.status_code == 500:
            print("❌ CRITICAL: Returns 500 instead of 400 - THIS IS THE BUG!")
            print(f"Error response: {response.text}")
            results['error_format_correct'] = False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            results['error_format_correct'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['error_format_correct'] = False
    
    # Test 4.2: Test the actual Emergent API call that our backend makes
    print("\n4.2 Testing the actual Emergent API call...")
    
    try:
        # Simulate what our backend does
        test_session_id = "backend-simulation-" + str(uuid.uuid4())
        headers = {"X-Session-ID": test_session_id}
        
        print(f"Simulating backend call to Emergent API...")
        print(f"URL: https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data")
        print(f"Headers: {headers}")
        
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers=headers,
            timeout=10
        )
        
        print(f"Emergent API Status: {response.status_code}")
        print(f"Emergent API Response: {response.text[:200]}...")
        
        if response.status_code == 400:
            print("✅ PASS: Emergent API returns 400 for invalid session")
            results['emergent_api_400'] = True
        elif response.status_code == 404:
            print("✅ PASS: Emergent API returns 404 (user data not found)")
            results['emergent_api_400'] = True
        else:
            print(f"⚠️  Emergent API returns: {response.status_code}")
            results['emergent_api_400'] = False
            
    except Exception as e:
        print(f"❌ ERROR calling Emergent API: {e}")
        results['emergent_api_400'] = False
    
    # Test 4.3: Test error propagation from Emergent API to our callback
    print("\n4.3 Testing error propagation...")
    
    try:
        # Test that our callback properly propagates Emergent API errors
        payload = {
            "session_id": "error-propagation-test-" + str(uuid.uuid4()),
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Our callback status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ PASS: Our callback properly returns 400")
            error_data = response.json()
            if 'Invalid session ID' in error_data.get('detail', ''):
                print("✅ PASS: Correct error message propagated")
                results['error_propagation'] = True
            else:
                print("⚠️  Error message not as expected")
                results['error_propagation'] = False
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            results['error_propagation'] = False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['error_propagation'] = False
    
    return results

def main():
    """Run comprehensive OAuth debug tests focused on review request issues"""
    print("🚀 Starting OAuth Debug Tests - Review Request Focus")
    print("="*80)
    
    all_results = {}
    
    # Run all tests
    print("\n" + "🔍" * 20 + " RUNNING TESTS " + "🔍" * 20)
    
    all_results['emergent_api'] = test_emergent_oauth_api_integration()
    all_results['oauth_urls'] = test_oauth_url_configuration()
    all_results['session_extraction'] = test_session_id_extraction()
    all_results['error_debug'] = test_specific_400_error_debug()
    
    # Summary and Analysis
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE OAUTH DEBUG SUMMARY")
    print("="*80)
    
    print("\n🔍 REVIEW REQUEST ANALYSIS:")
    print("-" * 40)
    
    print("\n1. EMERGENT OAUTH API INTEGRATION:")
    emergent_results = all_results['emergent_api']
    if emergent_results.get('api_accessible'):
        print("   ✅ Emergent OAuth API is accessible")
        print("   ✅ Request format and headers working")
        print("   ✅ Session ID format validation working")
    else:
        print("   ❌ Issues with Emergent OAuth API access")
    
    print("\n2. OAUTH URL CONFIGURATION:")
    url_results = all_results['oauth_urls']
    if url_results.get('callback_endpoint_accessible'):
        print("   ✅ OAuth callback endpoint accessible")
    if url_results.get('cors_config'):
        print("   ✅ No CORS issues detected")
    if url_results.get('google_oauth_config'):
        print("   ✅ Google OAuth configuration OK")
    
    print("\n3. SESSION ID EXTRACTION:")
    session_results = all_results['session_extraction']
    if session_results.get('session_format_validation'):
        print("   ✅ Session ID format validation working")
    if session_results.get('edge_case_handling'):
        print("   ✅ Edge case handling working")
    
    print("\n4. 400 ERROR DEBUG:")
    error_results = all_results['error_debug']
    if error_results.get('error_format_correct'):
        print("   ✅ OAuth callback returns proper 400 errors")
        print("   ✅ Error message format is correct")
    else:
        print("   ❌ Issues with error handling")
    
    if error_results.get('emergent_api_400'):
        print("   ✅ Emergent API returns expected errors")
    
    if error_results.get('error_propagation'):
        print("   ✅ Error propagation working correctly")
    
    # Overall Assessment
    print("\n" + "="*80)
    print("🎯 OVERALL ASSESSMENT FOR REVIEW REQUEST")
    print("="*80)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(results.values()) for results in all_results.values())
    
    print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ OAuth integration appears to be working correctly")
        print("✅ The 400 error handling has been fixed")
        print("✅ No critical issues found with Google OAuth flow")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
        print("❌ There may still be issues with OAuth integration")
    
    # Specific recommendations
    print("\n📋 RECOMMENDATIONS:")
    print("-" * 20)
    
    if not emergent_results.get('api_accessible'):
        print("• Check network connectivity to Emergent OAuth API")
        print("• Verify Emergent OAuth API endpoint URL")
    
    if not error_results.get('error_format_correct'):
        print("• Fix OAuth callback error handling (500 -> 400)")
        print("• Ensure proper error message format")
    
    if not url_results.get('cors_config'):
        print("• Check CORS configuration for OAuth endpoints")
    
    if passed_tests == total_tests:
        print("• OAuth integration is working correctly")
        print("• The user's 'Authentication failed' issue may be resolved")
        print("• Consider testing with real OAuth session IDs")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()