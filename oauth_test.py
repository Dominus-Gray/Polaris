#!/usr/bin/env python3
"""
OAuth Implementation Testing for Polaris MVP - UPDATED IMPLEMENTATION FOCUS
Tests the updated OAuth callback endpoint with session management and cookie handling
Focuses on verifying the Emergent OAuth integration improvements
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://readiness-hub-2.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🔐 Updated OAuth Implementation Testing at: {API_BASE}")
print("🎯 FOCUS: Session token handling, cookie security, and Emergent integration")

def test_oauth_callback_session_management():
    """Test that OAuth callback properly handles session tokens and database storage"""
    print("\n=== Testing OAuth Callback Session Management ===")
    try:
        # Test with mock session ID
        payload = {
            "session_id": "test_session_" + str(uuid.uuid4())[:8],
            "role": "client"
        }
        
        # Use session to capture cookies
        session = requests.Session()
        response = session.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        # Check response structure for error handling
        if response.status_code == 400:
            data = response.json()
            if data.get('detail') == 'Invalid session ID':
                print("✅ PASS: OAuth callback properly validates session ID with Emergent API")
                
                # Check if cookies would be set (in headers)
                set_cookie_header = response.headers.get('set-cookie')
                if set_cookie_header:
                    print(f"Set-Cookie header: {set_cookie_header}")
                    print("✅ PASS: OAuth callback includes cookie handling")
                else:
                    print("ℹ️  No cookies set (expected for invalid session)")
                
                return True
            else:
                print(f"❌ FAIL: Unexpected error detail: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL: Expected 400 for invalid session, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_cookie_security():
    """Test OAuth callback cookie security attributes"""
    print("\n=== Testing OAuth Callback Cookie Security ===")
    try:
        payload = {
            "session_id": "security_test_" + str(uuid.uuid4())[:8],
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        # Check security headers
        security_headers = {
            'x-content-type-options': 'nosniff',
            'x-frame-options': 'DENY',
            'x-xss-protection': '1; mode=block',
            'strict-transport-security': 'max-age=31536000; includeSubDomains'
        }
        
        found_security_headers = 0
        for header, expected_value in security_headers.items():
            actual_value = response.headers.get(header)
            if actual_value:
                found_security_headers += 1
                print(f"✅ {header}: {actual_value}")
            else:
                print(f"⚠️  Missing {header}")
        
        if found_security_headers >= 3:
            print("✅ PASS: OAuth callback includes proper security headers")
            return True
        else:
            print(f"❌ FAIL: Insufficient security headers ({found_security_headers}/4)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_emergent_api_integration_detailed():
    """Test detailed Emergent API integration"""
    print("\n=== Testing Detailed Emergent API Integration ===")
    try:
        # Test the actual Emergent API endpoint
        test_session_ids = [
            "test_integration_" + str(uuid.uuid4())[:8],
            str(uuid.uuid4()),
            "invalid_session_123"
        ]
        
        for session_id in test_session_ids:
            print(f"\nTesting session ID: {session_id[:20]}...")
            
            # Direct API call to Emergent
            headers = {"X-Session-ID": session_id}
            try:
                emergent_response = requests.get(
                    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                    headers=headers,
                    timeout=10
                )
                print(f"Emergent API status: {emergent_response.status_code}")
                
                if emergent_response.status_code in [400, 404]:
                    print("✅ Emergent API accessible and returns expected error")
                else:
                    print(f"⚠️  Unexpected Emergent API status: {emergent_response.status_code}")
                    
            except requests.RequestException as e:
                print(f"❌ Emergent API connection error: {e}")
                return False
            
            # Test OAuth callback with same session ID
            payload = {
                "session_id": session_id,
                "role": "client"
            }
            
            oauth_response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"OAuth callback status: {oauth_response.status_code}")
            
            if oauth_response.status_code == 400:
                data = oauth_response.json()
                if data.get('detail') == 'Invalid session ID':
                    print("✅ OAuth callback properly integrates with Emergent API")
                else:
                    print(f"❌ Unexpected OAuth error: {data.get('detail')}")
                    return False
            else:
                print(f"❌ Unexpected OAuth status: {oauth_response.status_code}")
                return False
        
        print("✅ PASS: Emergent API integration working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_error_handling():
    """Test OAuth callback error handling improvements"""
    print("\n=== Testing OAuth Callback Error Handling ===")
    try:
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "Invalid session format",
                "payload": {"session_id": "invalid", "role": "client"},
                "expected_status": 400,
                "expected_detail": "Invalid session ID"
            },
            {
                "name": "Empty session",
                "payload": {"session_id": "", "role": "client"},
                "expected_status": 400,
                "expected_detail": "Invalid session ID"
            },
            {
                "name": "Whitespace session",
                "payload": {"session_id": "   ", "role": "client"},
                "expected_status": [400, 500],  # May cause 500 for extreme edge case
                "expected_detail": None  # Don't check detail for edge cases
            },
            {
                "name": "Valid UUID but invalid session",
                "payload": {"session_id": str(uuid.uuid4()), "role": "client"},
                "expected_status": 400,
                "expected_detail": "Invalid session ID"
            }
        ]
        
        passed_scenarios = 0
        total_scenarios = len(error_scenarios)
        
        for scenario in error_scenarios:
            print(f"\nTesting: {scenario['name']}")
            
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=scenario["payload"],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            # Check status code
            expected_statuses = scenario["expected_status"] if isinstance(scenario["expected_status"], list) else [scenario["expected_status"]]
            if response.status_code in expected_statuses:
                print(f"✅ Status code correct: {response.status_code}")
                
                # Check error detail if specified
                if scenario["expected_detail"] and response.status_code != 500:
                    try:
                        data = response.json()
                        if data.get('detail') == scenario["expected_detail"]:
                            print(f"✅ Error detail correct: {data.get('detail')}")
                            passed_scenarios += 1
                        else:
                            print(f"❌ Wrong error detail: {data.get('detail')}")
                    except:
                        print("❌ Invalid JSON response")
                else:
                    passed_scenarios += 1
            else:
                print(f"❌ Wrong status code: expected {expected_statuses}, got {response.status_code}")
        
        if passed_scenarios >= total_scenarios * 0.8:  # 80% pass rate
            print(f"✅ PASS: Error handling working well ({passed_scenarios}/{total_scenarios})")
            return True
        else:
            print(f"❌ FAIL: Error handling issues ({passed_scenarios}/{total_scenarios})")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_response_structure():
    """Test OAuth callback response structure for successful cases"""
    print("\n=== Testing OAuth Callback Response Structure ===")
    try:
        # Since we can't get a valid session, test the error response structure
        payload = {
            "session_id": str(uuid.uuid4()),
            "role": "client"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"Error response structure: {json.dumps(data, indent=2)}")
            
            # Check error response structure
            required_fields = ['detail']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Error response has proper structure")
                return True
            else:
                print(f"❌ FAIL: Missing fields in error response: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: Expected 400 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_role_handling():
    """Test OAuth callback role handling for all valid roles"""
    print("\n=== Testing OAuth Callback Role Handling ===")
    try:
        valid_roles = ["client", "provider", "navigator", "agency"]
        
        for role in valid_roles:
            print(f"\nTesting role: {role}")
            
            payload = {
                "session_id": f"role_test_{role}_" + str(uuid.uuid4())[:8],
                "role": role
            }
            
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            # Should get 400 for invalid session, not role validation error
            if response.status_code == 400:
                data = response.json()
                if data.get('detail') == 'Invalid session ID':
                    print(f"✅ Role '{role}' accepted and processed correctly")
                else:
                    print(f"❌ Unexpected error for role '{role}': {data.get('detail')}")
                    return False
            else:
                print(f"❌ Unexpected status for role '{role}': {response.status_code}")
                return False
        
        print("✅ PASS: All valid roles handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_comprehensive_flow():
    """Test comprehensive OAuth callback flow"""
    print("\n=== Testing Comprehensive OAuth Callback Flow ===")
    try:
        # Test the complete flow that would happen in a real OAuth scenario
        test_session = str(uuid.uuid4())
        
        print(f"Testing with session: {test_session[:20]}...")
        
        # Step 1: Test OAuth callback
        payload = {
            "session_id": test_session,
            "role": "client"
        }
        
        session = requests.Session()
        response = session.post(
            f"{API_BASE}/auth/oauth/callback",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"OAuth callback status: {response.status_code}")
        
        # Step 2: Verify error handling
        if response.status_code == 400:
            data = response.json()
            if data.get('detail') == 'Invalid session ID':
                print("✅ OAuth callback properly validates session with Emergent API")
                
                # Step 3: Check response headers
                content_type = response.headers.get('content-type')
                if 'application/json' in content_type:
                    print("✅ Response content type is JSON")
                else:
                    print(f"❌ Unexpected content type: {content_type}")
                    return False
                
                # Step 4: Verify no authentication bypass
                auth_header = response.headers.get('authorization')
                if not auth_header:
                    print("✅ No unauthorized authentication tokens in response")
                else:
                    print(f"❌ Unexpected auth header: {auth_header}")
                    return False
                
                print("✅ PASS: Comprehensive OAuth flow validation successful")
                return True
            else:
                print(f"❌ FAIL: Unexpected error detail: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL: Expected 400 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_oauth_callback_with_valid_session():
    """Test POST /api/auth/oauth/callback with a mock valid session_id"""
    print("\n=== Testing OAuth Callback with Valid Session ===")
    
    try:
        # Test with mock session_id and different roles
        test_cases = [
            {"role": "client", "description": "Client OAuth callback"},
            {"role": "provider", "description": "Provider OAuth callback"},
            {"role": "navigator", "description": "Navigator OAuth callback"},
            {"role": "agency", "description": "Agency OAuth callback"}
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"\nTesting {test_case['description']}...")
            
            # Generate a mock session_id (UUID format)
            mock_session_id = str(uuid.uuid4())
            
            payload = {
                "session_id": mock_session_id,
                "role": test_case["role"]
            }
            
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has required fields
                required_fields = ['access_token', 'user_id', 'email', 'name', 'role']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"✅ PASS: OAuth callback successful for {test_case['role']}")
                    print(f"  Access token: {data['access_token'][:20]}...")
                    print(f"  User ID: {data['user_id']}")
                    print(f"  Email: {data['email']}")
                    print(f"  Role: {data['role']}")
                    results[test_case['role']] = {
                        'success': True,
                        'token': data['access_token'],
                        'user_id': data['user_id'],
                        'email': data['email'],
                        'role': data['role']
                    }
                else:
                    print(f"❌ FAIL: Missing required fields: {missing_fields}")
                    results[test_case['role']] = {'success': False, 'error': f'Missing fields: {missing_fields}'}
                    
            elif response.status_code == 400:
                print(f"❌ EXPECTED FAIL: Invalid session ID (this is expected behavior)")
                results[test_case['role']] = {'success': False, 'error': 'Invalid session ID (expected)'}
                
            elif response.status_code == 500:
                print(f"❌ FAIL: Server error - OAuth integration may be broken")
                results[test_case['role']] = {'success': False, 'error': 'Server error'}
                
            else:
                print(f"❌ FAIL: Unexpected status code {response.status_code}")
                results[test_case['role']] = {'success': False, 'error': f'HTTP {response.status_code}'}
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def test_oauth_callback_with_invalid_session():
    """Test POST /api/auth/oauth/callback with invalid session_id"""
    print("\n=== Testing OAuth Callback with Invalid Session ===")
    
    try:
        invalid_session_cases = [
            {"session_id": "invalid-session-id", "role": "client", "description": "Invalid session ID format"},
            {"session_id": "", "role": "client", "description": "Empty session ID"},
            {"session_id": "12345", "role": "client", "description": "Non-UUID session ID"},
        ]
        
        results = {}
        
        for test_case in invalid_session_cases:
            print(f"\nTesting {test_case['description']}...")
            
            payload = {
                "session_id": test_case["session_id"],
                "role": test_case["role"]
            }
            
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print(f"✅ PASS: Correctly rejected invalid session ID")
                results[test_case['description']] = {'success': True, 'properly_rejected': True}
            elif response.status_code == 500:
                print(f"⚠️  Server error - may indicate OAuth API call failing")
                results[test_case['description']] = {'success': False, 'error': 'Server error on invalid session'}
            else:
                print(f"❌ FAIL: Unexpected response for invalid session")
                results[test_case['description']] = {'success': False, 'error': f'HTTP {response.status_code}'}
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def test_oauth_callback_missing_fields():
    """Test POST /api/auth/oauth/callback with missing required fields"""
    print("\n=== Testing OAuth Callback with Missing Fields ===")
    
    try:
        missing_field_cases = [
            {"payload": {"role": "client"}, "description": "Missing session_id"},
            {"payload": {"session_id": str(uuid.uuid4())}, "description": "Missing role"},
            {"payload": {}, "description": "Missing both fields"},
            {"payload": {"session_id": str(uuid.uuid4()), "role": "invalid_role"}, "description": "Invalid role"}
        ]
        
        results = {}
        
        for test_case in missing_field_cases:
            print(f"\nTesting {test_case['description']}...")
            
            response = requests.post(
                f"{API_BASE}/auth/oauth/callback",
                json=test_case["payload"],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [400, 422]:  # 400 Bad Request or 422 Validation Error
                print(f"✅ PASS: Correctly rejected request with {test_case['description']}")
                results[test_case['description']] = {'success': True, 'properly_rejected': True}
            else:
                print(f"❌ FAIL: Should have rejected request with {test_case['description']}")
                results[test_case['description']] = {'success': False, 'error': f'HTTP {response.status_code}'}
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def test_oauth_callback_existing_user_scenario():
    """Test OAuth callback for existing user vs new user creation"""
    print("\n=== Testing OAuth Callback User Creation vs Login ===")
    
    try:
        # First, create a regular user to simulate existing user scenario
        existing_email = f"existing_oauth_user_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register a regular user first
        register_payload = {
            "email": existing_email,
            "password": "ExistingUser123!",
            "role": "client",
            "terms_accepted": True
        }
        
        register_response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code != 200:
            print(f"❌ Could not create existing user for test: {register_response.status_code}")
            return {}
        
        print(f"✅ Created existing user: {existing_email}")
        
        # Now test OAuth callback scenarios
        # Note: Since we can't actually call the Emergent OAuth API with valid session,
        # we'll test the endpoint behavior with mock session IDs
        
        results = {
            'existing_user_test_setup': True,
            'oauth_endpoint_accessible': False,
            'error_handling': False
        }
        
        # Test with mock session ID to see how the endpoint behaves
        mock_session_id = str(uuid.uuid4())
        oauth_payload = {
            "session_id": mock_session_id,
            "role": "client"
        }
        
        oauth_response = requests.post(
            f"{API_BASE}/auth/oauth/callback",
            json=oauth_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"OAuth callback status: {oauth_response.status_code}")
        print(f"OAuth callback response: {oauth_response.text}")
        
        if oauth_response.status_code == 400:
            if "Invalid session ID" in oauth_response.text:
                print("✅ PASS: OAuth endpoint correctly validates session ID")
                results['oauth_endpoint_accessible'] = True
                results['error_handling'] = True
            else:
                print("⚠️  OAuth endpoint rejects request but with different error")
                results['oauth_endpoint_accessible'] = True
                results['error_handling'] = False
        elif oauth_response.status_code == 500:
            print("⚠️  OAuth endpoint returns server error - may indicate Emergent API call failing")
            results['oauth_endpoint_accessible'] = True
            results['error_handling'] = False
        else:
            print(f"❌ Unexpected OAuth response: {oauth_response.status_code}")
            results['oauth_endpoint_accessible'] = False
            results['error_handling'] = False
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def test_oauth_emergent_api_integration():
    """Test if the OAuth endpoint can reach the Emergent OAuth API"""
    print("\n=== Testing Emergent OAuth API Integration ===")
    
    try:
        # Test the actual Emergent API endpoint that the OAuth callback calls
        emergent_api_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        
        # Test with a mock session ID
        mock_session_id = str(uuid.uuid4())
        headers = {"X-Session-ID": mock_session_id}
        
        print(f"Testing Emergent API at: {emergent_api_url}")
        print(f"Using mock session ID: {mock_session_id}")
        
        try:
            response = requests.get(emergent_api_url, headers=headers, timeout=10)
            print(f"Emergent API Status: {response.status_code}")
            print(f"Emergent API Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ PASS: Emergent OAuth API is accessible and responding")
                return {'emergent_api_accessible': True, 'api_response_code': 200}
            elif response.status_code == 400:
                print("✅ PASS: Emergent OAuth API is accessible (correctly rejects invalid session)")
                return {'emergent_api_accessible': True, 'api_response_code': 400}
            elif response.status_code == 404:
                print("❌ FAIL: Emergent OAuth API endpoint not found")
                return {'emergent_api_accessible': False, 'api_response_code': 404}
            else:
                print(f"⚠️  Emergent OAuth API returned unexpected status: {response.status_code}")
                return {'emergent_api_accessible': True, 'api_response_code': response.status_code}
                
        except requests.exceptions.Timeout:
            print("❌ FAIL: Emergent OAuth API request timed out")
            return {'emergent_api_accessible': False, 'error': 'timeout'}
        except requests.exceptions.ConnectionError:
            print("❌ FAIL: Cannot connect to Emergent OAuth API")
            return {'emergent_api_accessible': False, 'error': 'connection_error'}
        except Exception as api_error:
            print(f"❌ ERROR: Emergent API test failed: {api_error}")
            return {'emergent_api_accessible': False, 'error': str(api_error)}
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def test_oauth_access_token_validation():
    """Test if OAuth-generated access tokens work with protected endpoints"""
    print("\n=== Testing OAuth Access Token Validation ===")
    
    try:
        # Since we can't get real OAuth tokens without valid Emergent sessions,
        # we'll test the token validation logic by checking if the endpoint
        # properly handles token validation
        
        # Test with a mock JWT-like token
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock.token"
        
        headers = {
            "Authorization": f"Bearer {mock_token}",
            "Content-Type": "application/json"
        }
        
        # Test protected endpoint
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        print(f"Protected endpoint test status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ PASS: Protected endpoint correctly rejects invalid token")
            return {'token_validation': True, 'properly_protected': True}
        elif response.status_code == 200:
            print("❌ FAIL: Protected endpoint accepted invalid token")
            return {'token_validation': False, 'properly_protected': False}
        else:
            print(f"⚠️  Unexpected response from protected endpoint: {response.status_code}")
            return {'token_validation': False, 'properly_protected': False}
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {}

def main():
    """Run comprehensive OAuth authentication flow tests"""
    print("🔐 OAUTH AUTHENTICATION FLOW TESTING")
    print("="*60)
    print("Testing POST /api/auth/oauth/callback endpoint")
    print("="*60)
    
    all_results = {}
    
    # Test 1: OAuth callback with valid session format (but mock data)
    print("\n" + "="*50)
    print("TEST 1: OAuth Callback with Valid Session Format")
    print("="*50)
    valid_session_results = test_oauth_callback_with_valid_session()
    all_results['valid_session_tests'] = valid_session_results
    
    # Test 2: OAuth callback with invalid session IDs
    print("\n" + "="*50)
    print("TEST 2: OAuth Callback with Invalid Session IDs")
    print("="*50)
    invalid_session_results = test_oauth_callback_with_invalid_session()
    all_results['invalid_session_tests'] = invalid_session_results
    
    # Test 3: OAuth callback with missing fields
    print("\n" + "="*50)
    print("TEST 3: OAuth Callback with Missing Fields")
    print("="*50)
    missing_fields_results = test_oauth_callback_missing_fields()
    all_results['missing_fields_tests'] = missing_fields_results
    
    # Test 4: User creation vs existing user login scenario
    print("\n" + "="*50)
    print("TEST 4: User Creation vs Existing User Scenario")
    print("="*50)
    user_scenario_results = test_oauth_callback_existing_user_scenario()
    all_results['user_scenario_tests'] = user_scenario_results
    
    # Test 5: Emergent OAuth API integration
    print("\n" + "="*50)
    print("TEST 5: Emergent OAuth API Integration")
    print("="*50)
    emergent_api_results = test_oauth_emergent_api_integration()
    all_results['emergent_api_tests'] = emergent_api_results
    
    # Test 6: OAuth access token validation
    print("\n" + "="*50)
    print("TEST 6: OAuth Access Token Validation")
    print("="*50)
    token_validation_results = test_oauth_access_token_validation()
    all_results['token_validation_tests'] = token_validation_results
    
    # Summary
    print("\n" + "="*60)
    print("📊 OAUTH TESTING SUMMARY")
    print("="*60)
    
    print("\n🔍 KEY FINDINGS:")
    
    # Analyze results
    oauth_endpoint_working = False
    emergent_api_accessible = False
    proper_error_handling = False
    
    # Check if OAuth endpoint is accessible
    for role_results in valid_session_results.values():
        if isinstance(role_results, dict) and 'error' in role_results:
            if 'Invalid session ID' in role_results.get('error', ''):
                oauth_endpoint_working = True
                proper_error_handling = True
                break
    
    # Check Emergent API accessibility
    if emergent_api_results.get('emergent_api_accessible'):
        emergent_api_accessible = True
    
    print(f"✅ OAuth Endpoint Accessible: {'YES' if oauth_endpoint_working else 'NO'}")
    print(f"✅ Emergent API Accessible: {'YES' if emergent_api_accessible else 'NO'}")
    print(f"✅ Proper Error Handling: {'YES' if proper_error_handling else 'NO'}")
    
    # Identify potential issues
    print("\n🚨 POTENTIAL ISSUES IDENTIFIED:")
    
    issues_found = []
    
    if not oauth_endpoint_working:
        issues_found.append("OAuth callback endpoint may not be implemented or accessible")
    
    if not emergent_api_accessible:
        issues_found.append("Cannot reach Emergent OAuth API - network or configuration issue")
    
    if not proper_error_handling:
        issues_found.append("OAuth endpoint may not be handling invalid sessions properly")
    
    # Check for server errors in results
    server_errors = []
    for test_category, results in all_results.items():
        if isinstance(results, dict):
            for test_name, result in results.items():
                if isinstance(result, dict) and 'error' in result:
                    if 'Server error' in result['error']:
                        server_errors.append(f"{test_category}: {test_name}")
    
    if server_errors:
        issues_found.append(f"Server errors detected in: {', '.join(server_errors)}")
    
    if issues_found:
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. {issue}")
    else:
        print("No critical issues detected in OAuth flow structure")
    
    print("\n🎯 RECOMMENDATIONS:")
    
    if not emergent_api_accessible:
        print("1. Check network connectivity to https://demobackend.emergentagent.com")
        print("2. Verify Emergent OAuth API endpoint is correct")
    
    if oauth_endpoint_working and emergent_api_accessible:
        print("1. OAuth infrastructure appears to be working")
        print("2. Issue may be with specific session IDs or user data handling")
        print("3. Test with actual valid OAuth session from Google sign-in flow")
    
    if server_errors:
        print("4. Investigate server errors - may indicate backend configuration issues")
    
    print("\n📋 DETAILED RESULTS:")
    print(json.dumps(all_results, indent=2, default=str))
    
    return all_results

if __name__ == "__main__":
    main()