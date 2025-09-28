#!/usr/bin/env python3
"""
OAuth Callback Fix Test
Test the specific issue with whitespace/newline session IDs causing 500 errors
"""

import requests
import json
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://nextjs-mongo-polaris.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

def test_problematic_session_ids():
    """Test the specific session IDs that cause 500 errors"""
    print("=== Testing Problematic Session IDs ===")
    
    callback_url = f"{API_BASE}/auth/oauth/callback"
    
    # These are the session IDs that cause 500 errors
    problematic_cases = [
        {
            "name": "Whitespace session ID",
            "session_id": "   whitespace   ",
            "expected": "Should return 400, not 500"
        },
        {
            "name": "Session with newlines",
            "session_id": "session\nwith\nnewlines",
            "expected": "Should return 400, not 500"
        },
        {
            "name": "Session with tabs",
            "session_id": "session\twith\ttabs",
            "expected": "Should return 400, not 500"
        },
        {
            "name": "Session with carriage return",
            "session_id": "session\rwith\rcarriage",
            "expected": "Should return 400, not 500"
        }
    ]
    
    results = []
    
    for case in problematic_cases:
        try:
            print(f"\nTesting: {case['name']}")
            print(f"Session ID repr: {repr(case['session_id'])}")
            
            payload = {
                "session_id": case['session_id'],
                "role": "client"
            }
            
            response = requests.post(
                callback_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            result = {
                "test_name": case['name'],
                "session_id": case['session_id'],
                "status_code": response.status_code,
                "response_text": response.text,
                "expected": case['expected'],
                "is_500_error": response.status_code == 500
            }
            results.append(result)
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
            if response.status_code == 500:
                print(f"  ❌ ISSUE: Returning 500 instead of 400")
            elif response.status_code == 400:
                print(f"  ✅ GOOD: Properly returning 400")
            else:
                print(f"  ⚠️  UNEXPECTED: Status {response.status_code}")
                
        except Exception as e:
            result = {
                "test_name": case['name'],
                "session_id": case['session_id'],
                "error": str(e),
                "status_code": "ERROR",
                "expected": case['expected'],
                "is_500_error": False
            }
            results.append(result)
            print(f"  ERROR: {e}")
    
    return results

def test_direct_requests_library():
    """Test what happens when we call requests directly with problematic headers"""
    print("\n=== Testing Direct Requests Library Behavior ===")
    
    emergent_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
    
    problematic_headers = [
        "   whitespace   ",
        "session\nwith\nnewlines",
        "session\twith\ttabs",
        "session\rwith\rcarriage"
    ]
    
    for header_value in problematic_headers:
        try:
            print(f"\nTesting header value: {repr(header_value)}")
            headers = {"X-Session-ID": header_value}
            response = requests.get(emergent_url, headers=headers, timeout=5)
            print(f"  Unexpected success: {response.status_code}")
        except requests.exceptions.InvalidHeader as e:
            print(f"  ✅ Expected InvalidHeader: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")

def main():
    """Run the OAuth fix test"""
    print("🔧 OAuth Callback Fix Test")
    print("=" * 40)
    
    # Test the problematic session IDs
    results = test_problematic_session_ids()
    
    # Test direct requests behavior
    test_direct_requests_library()
    
    # Summary
    print("\n=== SUMMARY ===")
    server_errors = [r for r in results if r.get('is_500_error')]
    
    if server_errors:
        print(f"❌ Found {len(server_errors)} cases returning 500 errors:")
        for error in server_errors:
            print(f"   - {error['test_name']}")
        
        print("\n🔧 RECOMMENDED FIX:")
        print("   Add session ID validation before making the requests.get() call")
        print("   Check for whitespace, newlines, tabs, and other invalid characters")
        print("   Return HTTPException(400, 'Invalid session ID') for invalid formats")
    else:
        print("✅ All tests returning proper 400 errors")
    
    return results

if __name__ == "__main__":
    main()