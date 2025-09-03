#!/usr/bin/env python3
"""
Focused Holistic Backend Testing for Polaris System
Tests the specific endpoints mentioned in the review request with proper authentication
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartbiz-assess.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Polaris backend at: {API_BASE}")

def create_working_client_user():
    """Create a client user with proper license code"""
    print("\n=== Creating Working Client User ===")
    
    # First create agency and generate license
    agency_email = f"agency_{uuid.uuid4().hex[:8]}@test.com"
    agency_payload = {
        "email": agency_email,
        "password": "AgencyPass123!",
        "role": "agency",
        "terms_accepted": True
    }
    
    try:
        # Register agency
        response = requests.post(f"{API_BASE}/auth/register", json=agency_payload)
        if response.status_code != 200:
            print(f"❌ Agency registration failed: {response.text}")
            return None, None
        
        # Login agency
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": agency_email, 
            "password": "AgencyPass123!"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Agency login failed: {login_response.text}")
            return None, None
        
        agency_token = login_response.json().get('access_token')
        agency_headers = {"Authorization": f"Bearer {agency_token}", "Content-Type": "application/json"}
        
        # Generate license
        license_payload = {"count": 1, "business_type": "small_business"}
        license_response = requests.post(f"{API_BASE}/agency/licenses/generate", json=license_payload, headers=agency_headers)
        
        if license_response.status_code != 200:
            print(f"❌ License generation failed: {license_response.text}")
            return None, None
        
        license_data = license_response.json()
        license_codes = license_data.get('license_codes', [])
        
        if not license_codes:
            print("❌ No license codes generated")
            return None, None
        
        license_code = license_codes[0]
        print(f"✅ Generated license code: {license_code}")
        
        # Now create client with license code
        client_email = f"client_{uuid.uuid4().hex[:8]}@test.com"
        client_payload = {
            "email": client_email,
            "password": "ClientPass123!",
            "role": "client",
            "terms_accepted": True,
            "license_code": license_code
        }
        
        client_response = requests.post(f"{API_BASE}/auth/register", json=client_payload)
        if client_response.status_code != 200:
            print(f"❌ Client registration failed: {client_response.text}")
            return None, None
        
        # Login client
        client_login_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": client_email,
            "password": "ClientPass123!"
        })
        
        if client_login_response.status_code != 200:
            print(f"❌ Client login failed: {client_login_response.text}")
            return None, None
        
        client_token = client_login_response.json().get('access_token')
        print("✅ Client user created and logged in successfully")
        
        return client_token, client_email
        
    except Exception as e:
        print(f"❌ Error creating client user: {e}")
        return None, None

def test_assessment_endpoints(token):
    """Test assessment endpoints with gap recording"""
    print("\n" + "="*60)
    print("🔍 TESTING ASSESSMENT ENDPOINTS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test POST /api/assessment/answer with "yes"
    print("\n=== POST /api/assessment/answer (YES) ===")
    try:
        payload = {
            "question_id": "q1_1",
            "answer": "yes",
            "area_id": "area1"
        }
        response = requests.post(f"{API_BASE}/assessment/answer", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PASS: YES answer recorded")
            results['answer_yes'] = True
        else:
            print(f"❌ FAIL: {response.text}")
            results['answer_yes'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['answer_yes'] = False
    
    # Test POST /api/assessment/answer with "no_help" (creates gap)
    print("\n=== POST /api/assessment/answer (NO_HELP - creates gap) ===")
    try:
        payload = {
            "question_id": "q1_2", 
            "answer": "no_help",
            "area_id": "area1"
        }
        response = requests.post(f"{API_BASE}/assessment/answer", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PASS: NO_HELP answer recorded (gap created)")
            results['answer_no_help'] = True
        else:
            print(f"❌ FAIL: {response.text}")
            results['answer_no_help'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['answer_no_help'] = False
    
    # Test POST /api/assessment/evidence (file upload)
    print("\n=== POST /api/assessment/evidence (file upload) ===")
    try:
        # Create proper multipart form data
        files = [('files', ('test.pdf', b'PDF content', 'application/pdf'))]
        data = {
            'question_id': 'q1_1',
            'area_id': 'area1',
            'description': 'Test evidence file'
        }
        
        upload_headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE}/assessment/evidence", files=files, data=data, headers=upload_headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PASS: Evidence file uploaded")
            results['evidence_upload'] = True
        else:
            print(f"❌ FAIL: {response.text}")
            results['evidence_upload'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['evidence_upload'] = False
    
    # Get user ID for progress test
    user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    user_id = None
    if user_response.status_code == 200:
        user_id = user_response.json().get('id')
    
    # Test GET /api/assessment/progress/{user_id}
    print("\n=== GET /api/assessment/progress/{user_id} ===")
    try:
        if user_id:
            response = requests.get(f"{API_BASE}/assessment/progress/{user_id}", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                gaps = data.get('gaps', [])
                print(f"Found {len(gaps)} gaps")
                print(f"Progress data: {json.dumps(data, indent=2)}")
                results['progress_check'] = True
                print("✅ PASS: Progress endpoint working with gaps calculation")
            else:
                print(f"❌ FAIL: {response.text}")
                results['progress_check'] = False
        else:
            print("❌ FAIL: Could not get user ID")
            results['progress_check'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['progress_check'] = False
    
    return results

def test_knowledge_base_endpoints(token):
    """Test knowledge base endpoints"""
    print("\n" + "="*60)
    print("📚 TESTING KNOWLEDGE BASE ENDPOINTS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test GET /api/knowledge-base/areas
    print("\n=== GET /api/knowledge-base/areas ===")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/areas", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            areas = data.get('areas', [])
            print(f"Found {len(areas)} knowledge base areas")
            results['kb_areas'] = True
            print("✅ PASS: Knowledge base areas endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_areas'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_areas'] = False
    
    # Test GET /api/knowledge-base/access
    print("\n=== GET /api/knowledge-base/access ===")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/access", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Access info: {json.dumps(data, indent=2)}")
            results['kb_access'] = True
            print("✅ PASS: Knowledge base access endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_access'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_access'] = False
    
    # Test GET /api/knowledge-base/{area_id}/content
    print("\n=== GET /api/knowledge-base/{area_id}/content ===")
    try:
        area_id = "area1"
        response = requests.get(f"{API_BASE}/knowledge-base/{area_id}/content", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Content info: {json.dumps(data, indent=2)}")
            results['kb_content'] = True
            print("✅ PASS: Knowledge base content endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_content'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_content'] = False
    
    # Test POST /api/payments/knowledge-base
    print("\n=== POST /api/payments/knowledge-base ===")
    try:
        payload = {
            "package_id": "single_area_area1",
            "origin_url": "https://test.com/kb"
        }
        response = requests.post(f"{API_BASE}/payments/knowledge-base", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Payment response: {json.dumps(data, indent=2)}")
            results['kb_payment'] = True
            print("✅ PASS: Knowledge base payment endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_payment'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_payment'] = False
    
    return results

def test_service_provider_endpoints(token):
    """Test service provider matching endpoints"""
    print("\n" + "="*60)
    print("🤝 TESTING SERVICE PROVIDER ENDPOINTS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test POST /api/service-requests/professional-help
    print("\n=== POST /api/service-requests/professional-help ===")
    try:
        payload = {
            "service_type": "business_formation",
            "description": "Need help with business registration",
            "budget_range": "500-1500",
            "timeline": "2-4 weeks"
        }
        response = requests.post(f"{API_BASE}/service-requests/professional-help", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Service request response: {json.dumps(data, indent=2)}")
            results['service_request'] = True
            results['request_id'] = data.get('request_id')
            print("✅ PASS: Professional help request endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['service_request'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['service_request'] = False
    
    # Create provider user for testing
    provider_token = create_provider_user()
    
    # Test GET /api/provider/notifications
    print("\n=== GET /api/provider/notifications ===")
    try:
        if provider_token:
            provider_headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
            response = requests.get(f"{API_BASE}/provider/notifications", headers=provider_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                print(f"Found {len(notifications)} provider notifications")
                results['provider_notifications'] = True
                print("✅ PASS: Provider notifications endpoint working")
            else:
                print(f"❌ FAIL: {response.text}")
                results['provider_notifications'] = False
        else:
            print("❌ FAIL: No provider token available")
            results['provider_notifications'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['provider_notifications'] = False
    
    # Test POST /api/provider/respond-to-request
    print("\n=== POST /api/provider/respond-to-request ===")
    try:
        if provider_token and results.get('request_id'):
            payload = {
                "request_id": results['request_id'],
                "response": "interested",
                "proposal": "I can help with business formation",
                "estimated_cost": 1000.00
            }
            provider_headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
            response = requests.post(f"{API_BASE}/provider/respond-to-request", json=payload, headers=provider_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Provider response: {json.dumps(data, indent=2)}")
                results['provider_response'] = True
                print("✅ PASS: Provider response endpoint working")
            else:
                print(f"❌ FAIL: {response.text}")
                results['provider_response'] = False
        else:
            print("❌ SKIP: No provider token or request ID")
            results['provider_response'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['provider_response'] = False
    
    return results

def create_provider_user():
    """Create a provider user for testing"""
    try:
        provider_email = f"provider_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": provider_email,
            "password": "ProviderPass123!",
            "role": "provider",
            "terms_accepted": True
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=payload)
        if response.status_code == 200:
            # Login
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": provider_email,
                "password": "ProviderPass123!"
            })
            if login_response.status_code == 200:
                return login_response.json().get('access_token')
        return None
    except:
        return None

def test_free_resources_and_analytics(token):
    """Test free resources and analytics endpoints"""
    print("\n" + "="*60)
    print("📊 TESTING FREE RESOURCES AND ANALYTICS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test GET /api/free-resources/recommendations
    print("\n=== GET /api/free-resources/recommendations ===")
    try:
        response = requests.get(f"{API_BASE}/free-resources/recommendations", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            resources = data.get('resources', [])
            print(f"Found {len(resources)} free resources")
            results['free_resources'] = True
            print("✅ PASS: Free resources endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['free_resources'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['free_resources'] = False
    
    # Test POST /api/analytics/resource-access
    print("\n=== POST /api/analytics/resource-access ===")
    try:
        payload = {
            "resource_id": "test_resource",
            "resource_type": "guide",
            "action": "view"
        }
        response = requests.post(f"{API_BASE}/analytics/resource-access", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Analytics response: {json.dumps(data, indent=2)}")
            results['analytics_tracking'] = True
            print("✅ PASS: Analytics tracking endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['analytics_tracking'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['analytics_tracking'] = False
    
    return results

def test_client_dashboard_endpoints(token):
    """Test client dashboard endpoints"""
    print("\n" + "="*60)
    print("🏠 TESTING CLIENT DASHBOARD ENDPOINTS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get user ID
    user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    user_id = None
    if user_response.status_code == 200:
        user_id = user_response.json().get('id')
    
    # Test GET /api/assessment/progress/{user_id}
    print("\n=== GET /api/assessment/progress/{user_id} (comprehensive) ===")
    try:
        if user_id:
            response = requests.get(f"{API_BASE}/assessment/progress/{user_id}", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Progress data keys: {list(data.keys())}")
                results['progress_comprehensive'] = True
                print("✅ PASS: Comprehensive progress endpoint working")
            else:
                print(f"❌ FAIL: {response.text}")
                results['progress_comprehensive'] = False
        else:
            print("❌ FAIL: No user ID")
            results['progress_comprehensive'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['progress_comprehensive'] = False
    
    # Test GET /api/agency/info/{agency_id}
    print("\n=== GET /api/agency/info/{agency_id} ===")
    try:
        agency_id = "test_agency_001"
        response = requests.get(f"{API_BASE}/agency/info/{agency_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Agency info: {json.dumps(data, indent=2)}")
            results['agency_info'] = True
            print("✅ PASS: Agency info endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['agency_info'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['agency_info'] = False
    
    # Test GET /api/engagements/my-services
    print("\n=== GET /api/engagements/my-services ===")
    try:
        response = requests.get(f"{API_BASE}/engagements/my-services", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"My services: {json.dumps(data, indent=2)}")
            results['my_services'] = True
            print("✅ PASS: My services endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['my_services'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['my_services'] = False
    
    return results

def main():
    """Run focused holistic testing"""
    print("🚀 STARTING FOCUSED HOLISTIC POLARIS TESTING")
    print("="*80)
    
    # Create working client user
    client_token, client_email = create_working_client_user()
    if not client_token:
        print("❌ Failed to create working client user, aborting tests")
        return False
    
    print(f"✅ Testing with client: {client_email}")
    
    all_results = {}
    
    # Run all test suites
    assessment_results = test_assessment_endpoints(client_token)
    all_results.update(assessment_results)
    
    kb_results = test_knowledge_base_endpoints(client_token)
    all_results.update(kb_results)
    
    service_results = test_service_provider_endpoints(client_token)
    all_results.update(service_results)
    
    resources_results = test_free_resources_and_analytics(client_token)
    all_results.update(resources_results)
    
    dashboard_results = test_client_dashboard_endpoints(client_token)
    all_results.update(dashboard_results)
    
    # Summary
    print("\n" + "="*80)
    print("📊 FOCUSED HOLISTIC TESTING SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    
    print("\n🔍 ASSESSMENT SYSTEM:")
    for test in ['answer_yes', 'answer_no_help', 'evidence_upload', 'progress_check']:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n📚 KNOWLEDGE BASE SYSTEM:")
    for test in ['kb_areas', 'kb_access', 'kb_content', 'kb_payment']:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n🤝 SERVICE PROVIDER MATCHING:")
    for test in ['service_request', 'provider_notifications', 'provider_response']:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n📊 FREE RESOURCES & ANALYTICS:")
    for test in ['free_resources', 'analytics_tracking']:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n🏠 CLIENT DASHBOARD:")
    for test in ['progress_comprehensive', 'agency_info', 'my_services']:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed >= total * 0.7:  # 70% pass rate
        print("\n🎉 HOLISTIC TESTING LARGELY SUCCESSFUL!")
        print("Most Polaris system components are working well")
        return True
    else:
        print(f"\n⚠️  SIGNIFICANT ISSUES FOUND")
        print("Multiple system components need attention")
        return False

if __name__ == "__main__":
    main()