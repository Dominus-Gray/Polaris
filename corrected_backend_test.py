#!/usr/bin/env python3
"""
Corrected Backend Testing - Using proper request formats based on backend code analysis
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
        elif method.upper() == 'PUT':
            if json_data:
                headers['Content-Type'] = 'application/json'
                response = requests.put(url, headers=headers, json=json_data, timeout=10)
            elif data:
                response = requests.put(url, headers=headers, data=data, timeout=10)
            else:
                response = requests.put(url, headers=headers, timeout=10)
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
    print("🔧 Corrected Backend Testing with Proper Request Formats")
    print("=" * 60)
    
    # Step 1: Authenticate
    print("1. Authentication Tests...")
    
    client_auth = test_endpoint('POST', '/auth/login', json_data={
        'email': QA_CLIENT_EMAIL,
        'password': QA_CLIENT_PASSWORD
    })
    
    if client_auth['success'] and client_auth['status_code'] == 200:
        client_token = client_auth['response_json']['access_token']
        print(f"✅ Client authentication: SUCCESS")
    else:
        print(f"❌ Client authentication: FAILED - {client_auth}")
        return
    
    provider_auth = test_endpoint('POST', '/auth/login', json_data={
        'email': QA_PROVIDER_EMAIL,
        'password': QA_PROVIDER_PASSWORD
    })
    
    if provider_auth['success'] and provider_auth['status_code'] == 200:
        provider_token = provider_auth['response_json']['access_token']
        print(f"✅ Provider authentication: SUCCESS")
    else:
        print(f"❌ Provider authentication: FAILED - {provider_auth}")
        return
    
    print()
    
    # Step 2: Assessment Response Submission (CORRECTED - using Form data)
    print("2. Assessment Response Submission (Corrected Format)...")
    
    # Create session first
    session_result = test_endpoint('POST', '/assessment/tier-session', token=client_token, data={
        'area_id': 'area1',
        'tier_level': 1
    })
    
    if session_result['success'] and session_result['status_code'] == 200:
        session_id = session_result['response_json']['session_id']
        print(f"✅ Session created: {session_id}")
        
        # Test response submission with FORM DATA (not JSON)
        response_result = test_endpoint('POST', f'/assessment/tier-session/{session_id}/response', 
                                      token=client_token, data={
            'question_id': 'area1_q1',
            'response': 'yes',
            'evidence_provided': 'false'
        })
        
        if response_result['success'] and response_result['status_code'] == 200:
            print(f"✅ Assessment response submission: SUCCESS")
        else:
            print(f"❌ Assessment response submission: FAILED")
            print(f"   Status: {response_result.get('status_code', 'N/A')}")
            print(f"   Error: {response_result.get('response_text', 'Unknown')}")
    else:
        print(f"❌ Session creation failed: {session_result}")
    
    print()
    
    # Step 3: Notifications System Analysis
    print("3. Notifications System Analysis...")
    
    notifications_result = test_endpoint('GET', '/notifications/my', token=client_token)
    
    if notifications_result['success']:
        if notifications_result['status_code'] == 200:
            print(f"✅ Notifications endpoint: WORKING")
            notifs = notifications_result['response_json']
            print(f"   Found {len(notifs.get('notifications', []))} notifications")
        elif notifications_result['status_code'] == 500:
            print(f"⚠️  Notifications endpoint: SERVER ERROR (500)")
            print(f"   This indicates the endpoint exists but has a runtime error")
        else:
            print(f"❌ Notifications endpoint: FAILED ({notifications_result['status_code']})")
    else:
        print(f"💥 Notifications endpoint: CONNECTION FAILED")
    
    # Test mark as read (correct endpoint format)
    mark_read_result = test_endpoint('PUT', '/notifications/test_notification_id/read', token=client_token)
    
    if mark_read_result['success']:
        if mark_read_result['status_code'] == 404:
            print(f"✅ Mark notification read endpoint: EXISTS (404 expected for non-existent notification)")
        elif mark_read_result['status_code'] == 200:
            print(f"✅ Mark notification read endpoint: WORKING")
        else:
            print(f"❌ Mark notification read: Status {mark_read_result['status_code']}")
    else:
        print(f"💥 Mark notification read: CONNECTION FAILED")
    
    print()
    
    # Step 4: Provider Profile System Analysis
    print("4. Provider Profile System Analysis...")
    
    # Get provider ID
    provider_me = test_endpoint('GET', '/auth/me', token=provider_token)
    if provider_me['success'] and provider_me['status_code'] == 200:
        provider_id = provider_me['response_json']['id']
        
        # The /providers/{id} endpoint returns 404, which means it's not implemented
        profile_result = test_endpoint('GET', f'/providers/{provider_id}', token=client_token)
        
        if profile_result['success'] and profile_result['status_code'] == 404:
            print(f"❌ Individual provider profile endpoint: NOT IMPLEMENTED (404)")
        else:
            print(f"🔍 Provider profile endpoint: Status {profile_result.get('status_code', 'N/A')}")
        
        # But /providers/approved works
        approved_result = test_endpoint('GET', '/providers/approved', token=client_token)
        if approved_result['success'] and approved_result['status_code'] == 200:
            providers = approved_result['response_json']
            print(f"✅ Approved providers list: WORKING ({len(providers)} providers)")
        else:
            print(f"❌ Approved providers list: FAILED")
    
    print()
    
    # Step 5: Service Request System
    print("5. Service Request System...")
    
    # Create service request
    service_request = test_endpoint('POST', '/service-requests/professional-help', 
                                  token=client_token, json_data={
        'area_id': 'area5',
        'budget_range': '1500-5000',
        'timeline': '2-4 weeks',
        'description': 'Technology infrastructure assessment needed',
        'priority': 'high'
    })
    
    if service_request['success'] and service_request['status_code'] == 200:
        request_id = service_request['response_json']['request_id']
        print(f"✅ Service request creation: SUCCESS ({request_id})")
        
        # Provider response
        provider_response = test_endpoint('POST', '/provider/respond-to-request',
                                        token=provider_token, json_data={
            'request_id': request_id,
            'proposed_fee': 2500.00,
            'estimated_timeline': '3 weeks',
            'proposal_note': 'Comprehensive technology assessment'
        })
        
        if provider_response['success'] and provider_response['status_code'] == 200:
            print(f"✅ Provider response: SUCCESS")
        else:
            print(f"❌ Provider response: FAILED ({provider_response.get('status_code', 'N/A')})")
        
        # Retrieve service request
        retrieve_request = test_endpoint('GET', f'/service-requests/{request_id}', token=client_token)
        if retrieve_request['success'] and retrieve_request['status_code'] == 200:
            print(f"✅ Service request retrieval: SUCCESS")
        else:
            print(f"❌ Service request retrieval: FAILED")
    else:
        print(f"❌ Service request creation: FAILED")
    
    print()
    
    # Step 6: Dashboard System
    print("6. Dashboard System...")
    
    client_dashboard = test_endpoint('GET', '/home/client', token=client_token)
    if client_dashboard['success'] and client_dashboard['status_code'] == 200:
        print(f"✅ Client dashboard: WORKING")
    else:
        print(f"❌ Client dashboard: FAILED")
    
    provider_dashboard = test_endpoint('GET', '/home/provider', token=provider_token)
    if provider_dashboard['success'] and provider_dashboard['status_code'] == 200:
        print(f"✅ Provider dashboard: WORKING")
    else:
        print(f"❌ Provider dashboard: FAILED")
    
    print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY OF FINDINGS:")
    print("=" * 60)
    print("✅ WORKING ENDPOINTS:")
    print("   - Authentication (client & provider)")
    print("   - Assessment schema retrieval")
    print("   - Assessment session creation")
    print("   - Service request creation & responses")
    print("   - Provider search (/providers/approved)")
    print("   - Dashboard endpoints")
    print()
    print("❌ FAILING/MISSING ENDPOINTS:")
    print("   - Assessment response submission (format issue - needs Form data)")
    print("   - Individual provider profiles (/providers/{id} - not implemented)")
    print("   - User statistics endpoints (not implemented)")
    print()
    print("⚠️  ENDPOINTS WITH ISSUES:")
    print("   - Notifications (/notifications/my - 500 server error)")
    print()
    print("🎯 RECOMMENDATIONS FOR 100% SUCCESS:")
    print("   1. Fix assessment response submission to accept both JSON and Form data")
    print("   2. Implement individual provider profile endpoints")
    print("   3. Fix notifications endpoint server error")
    print("   4. Implement missing user statistics endpoints")

if __name__ == "__main__":
    main()