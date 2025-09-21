#!/usr/bin/env python3
"""
Focused Endpoint Testing - Identify specific failing endpoints with exact error messages
"""

import requests
import json
import time

BASE_URL = "https://smallbiz-assist.preview.emergentagent.com/api"
QA_CLIENT_EMAIL = "client.qa@polaris.example.com"
QA_CLIENT_PASSWORD = "Polaris#2025!"
QA_PROVIDER_EMAIL = "provider.qa@polaris.example.com"
QA_PROVIDER_PASSWORD = "Polaris#2025!"

def test_endpoint(method, endpoint, token=None, data=None, json_data=None, params=None):
    """Test a specific endpoint and return detailed results"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == 'POST':
            if json_data:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            elif data:
                response = requests.post(url, headers=headers, data=data, timeout=10)
            else:
                response = requests.post(url, headers=headers, timeout=10)
        else:
            response = requests.request(method, url, headers=headers, json=json_data, data=data, params=params, timeout=10)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response_text': response.text,
            'response_json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timeout'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Connection error'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("🔍 Focused Backend Endpoint Testing")
    print("=" * 50)
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    
    client_auth = test_endpoint('POST', '/auth/login', json_data={
        'email': QA_CLIENT_EMAIL,
        'password': QA_CLIENT_PASSWORD
    })
    
    if client_auth['success'] and client_auth['status_code'] == 200:
        client_token = client_auth['response_json']['access_token']
        print(f"✅ Client authenticated successfully")
    else:
        print(f"❌ Client authentication failed: {client_auth}")
        return
    
    provider_auth = test_endpoint('POST', '/auth/login', json_data={
        'email': QA_PROVIDER_EMAIL,
        'password': QA_PROVIDER_PASSWORD
    })
    
    if provider_auth['success'] and provider_auth['status_code'] == 200:
        provider_token = provider_auth['response_json']['access_token']
        print(f"✅ Provider authenticated successfully")
    else:
        print(f"❌ Provider authentication failed: {provider_auth}")
        return
    
    print()
    
    # Step 2: Test Assessment Response Submission
    print("2. Testing Assessment Response Submission...")
    
    # First create a session
    session_result = test_endpoint('POST', '/assessment/tier-session', token=client_token, data={
        'area_id': 'area1',
        'tier_level': 1
    })
    
    if session_result['success'] and session_result['status_code'] == 200:
        session_id = session_result['response_json']['session_id']
        print(f"✅ Session created: {session_id}")
        
        # Test response submission
        response_result = test_endpoint('POST', f'/assessment/tier-session/{session_id}/response', 
                                      token=client_token, json_data={
            'question_id': 'area1_q1',
            'response': 'yes',
            'evidence_provided': False
        })
        
        print(f"Assessment Response Submission:")
        print(f"  Status Code: {response_result.get('status_code', 'N/A')}")
        print(f"  Success: {response_result['success']}")
        if not response_result['success']:
            print(f"  Error: {response_result.get('error', 'Unknown')}")
        elif response_result['status_code'] != 200:
            print(f"  Response: {response_result.get('response_text', 'No response')}")
    else:
        print(f"❌ Session creation failed: {session_result}")
    
    print()
    
    # Step 3: Test Notifications Endpoint
    print("3. Testing Notifications Endpoint...")
    
    notifications_result = test_endpoint('GET', '/notifications/my', token=client_token)
    print(f"Notifications Endpoint:")
    print(f"  Status Code: {notifications_result.get('status_code', 'N/A')}")
    print(f"  Success: {notifications_result['success']}")
    if not notifications_result['success']:
        print(f"  Error: {notifications_result.get('error', 'Unknown')}")
    elif notifications_result['status_code'] != 200:
        print(f"  Response: {notifications_result.get('response_text', 'No response')}")
    
    print()
    
    # Step 4: Test Provider Profile Retrieval
    print("4. Testing Provider Profile Retrieval...")
    
    # Get provider ID
    provider_me = test_endpoint('GET', '/auth/me', token=provider_token)
    if provider_me['success'] and provider_me['status_code'] == 200:
        provider_id = provider_me['response_json']['id']
        print(f"✅ Provider ID: {provider_id}")
        
        # Test profile retrieval
        profile_result = test_endpoint('GET', f'/providers/{provider_id}', token=client_token)
        print(f"Provider Profile Retrieval:")
        print(f"  Status Code: {profile_result.get('status_code', 'N/A')}")
        print(f"  Success: {profile_result['success']}")
        if not profile_result['success']:
            print(f"  Error: {profile_result.get('error', 'Unknown')}")
        elif profile_result['status_code'] != 200:
            print(f"  Response: {profile_result.get('response_text', 'No response')}")
    else:
        print(f"❌ Failed to get provider ID: {provider_me}")
    
    print()
    
    # Step 5: Check which endpoints exist
    print("5. Checking Endpoint Availability...")
    
    endpoints_to_check = [
        ('GET', '/notifications/my'),
        ('GET', '/providers/approved'),
        ('POST', '/notifications/mark-read'),
        ('GET', '/user/stats'),
        ('GET', '/dashboard/stats')
    ]
    
    for method, endpoint in endpoints_to_check:
        result = test_endpoint(method, endpoint, token=client_token, json_data={} if method == 'POST' else None)
        status = result.get('status_code', 'N/A')
        success = result['success']
        
        if success:
            if status == 200:
                print(f"✅ {method} {endpoint}: Working (200)")
            elif status == 404:
                print(f"❌ {method} {endpoint}: Not Found (404)")
            elif status == 500:
                print(f"⚠️  {method} {endpoint}: Server Error (500)")
            else:
                print(f"🔍 {method} {endpoint}: Status {status}")
        else:
            print(f"💥 {method} {endpoint}: Connection Failed - {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    main()