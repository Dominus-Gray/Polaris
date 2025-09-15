#!/usr/bin/env python3
"""
Quick Backend Verification Test
Testing specific endpoints as requested in review:
1. GET /api/metrics - ensure HTTP 200 with '# HELP' present
2. POST /api/knowledge-base/ai-assistance - verify 200 and <200 words
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://127.0.0.1:8001"
QA_EMAIL = "client.qa@polaris.example.com"
QA_PASSWORD = "Polaris#2025!"

def authenticate_qa_user():
    """Authenticate QA user and return token"""
    print("🔐 Authenticating QA user...")
    
    login_data = {
        "email": QA_EMAIL,
        "password": QA_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Authentication successful - Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_metrics_endpoint():
    """Test GET /api/metrics endpoint"""
    print("\n📊 Testing GET /api/metrics endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/metrics", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Response Length: {len(content)} characters")
            
            # Check for '# HELP' presence
            if '# HELP' in content:
                print("✅ PASS: '# HELP' text found in metrics response")
                print(f"First 200 chars: {content[:200]}...")
                return True
            else:
                print("❌ FAIL: '# HELP' text not found in metrics response")
                print(f"Response content: {content[:500]}...")
                return False
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_ai_assistance_endpoint(token):
    """Test POST /api/knowledge-base/ai-assistance endpoint"""
    print("\n🤖 Testing POST /api/knowledge-base/ai-assistance endpoint...")
    
    if not token:
        print("❌ FAIL: No authentication token available")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "question": "List 3 steps to prepare for a government contract bid.",
        "area_id": "area3"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/knowledge-base/ai-assistance", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data.get("response", "")
            
            print(f"AI Response Length: {len(ai_response)} characters")
            
            # Count words (simple word count)
            word_count = len(ai_response.split())
            print(f"Word Count: {word_count} words")
            
            if word_count < 200:
                print("✅ PASS: AI response is under 200 words")
                print(f"AI Response: {ai_response[:300]}...")
                return True
            else:
                print("❌ FAIL: AI response exceeds 200 words")
                print(f"AI Response: {ai_response[:300]}...")
                return False
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Main test execution"""
    print("🎯 QUICK BACKEND VERIFICATION TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Test 1: Metrics endpoint
    metrics_result = test_metrics_endpoint()
    results.append(("GET /api/metrics", metrics_result))
    
    # Test 2: AI assistance endpoint (requires authentication)
    token = authenticate_qa_user()
    ai_result = test_ai_assistance_endpoint(token)
    results.append(("POST /api/knowledge-base/ai-assistance", ai_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\nSuccess Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED - Backend verification successful!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Backend needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())