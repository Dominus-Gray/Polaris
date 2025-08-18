#!/usr/bin/env python3
"""
Holistic Backend Testing for Polaris System
Tests all the new enhancements as specified in the review request
"""

import requests
import json
import uuid
import os
import io
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://procurement-ready.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Polaris backend at: {API_BASE}")

# Test credentials for comprehensive testing
TEST_USER_EMAIL = "polaris.test.user@example.com"
TEST_USER_PASSWORD = "SecurePass123!"

def create_test_user():
    """Create a test user for comprehensive testing"""
    print("\n=== Creating Test User ===")
    try:
        # Try with navigator role first (doesn't require license code)
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "role": "navigator",
            "terms_accepted": True
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Test user created successfully")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  Test user already exists, proceeding with login")
            return True
        else:
            print(f"❌ Failed to create test user: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def login_test_user():
    """Login test user and return JWT token"""
    print("\n=== Logging in Test User ===")
    try:
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return None

def test_assessment_system_with_gaps(token):
    """Test Assessment System with Gap Recording"""
    print("\n" + "="*60)
    print("🔍 TESTING ASSESSMENT SYSTEM WITH GAP RECORDING")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: POST /api/assessment/answer with "yes" answer
    print("\n=== Test 1: POST /api/assessment/answer (YES answer) ===")
    try:
        payload = {
            "question_id": "q1_1",
            "answer": "yes",
            "area_id": "area1",
            "evidence_description": "Business license certificate uploaded"
        }
        
        response = requests.post(f"{API_BASE}/assessment/answer", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            results['answer_yes'] = True
            print("✅ PASS: YES answer recorded successfully")
        else:
            print(f"❌ FAIL: {response.text}")
            results['answer_yes'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['answer_yes'] = False
    
    # Test 2: POST /api/assessment/answer with "no_help" answer (should create gap)
    print("\n=== Test 2: POST /api/assessment/answer (NO_HELP answer - creates gap) ===")
    try:
        payload = {
            "question_id": "q1_2",
            "answer": "no_help",
            "area_id": "area1",
            "gap_description": "Need help with business registration process"
        }
        
        response = requests.post(f"{API_BASE}/assessment/answer", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            results['answer_no_help'] = True
            print("✅ PASS: NO_HELP answer recorded as gap successfully")
        else:
            print(f"❌ FAIL: {response.text}")
            results['answer_no_help'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['answer_no_help'] = False
    
    # Test 3: POST /api/assessment/evidence (file upload)
    print("\n=== Test 3: POST /api/assessment/evidence (file upload) ===")
    try:
        # Create a dummy file for upload
        file_content = b"PDF content for business license certificate"
        files = {
            'file': ('business_license.pdf', io.BytesIO(file_content), 'application/pdf')
        }
        data = {
            'question_id': 'q1_1',
            'area_id': 'area1',
            'description': 'Business license certificate'
        }
        
        # Remove Content-Type for multipart form data
        upload_headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE}/assessment/evidence", files=files, data=data, headers=upload_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            results['evidence_upload'] = True
            print("✅ PASS: Evidence file uploaded successfully")
        else:
            print(f"❌ FAIL: {response.text}")
            results['evidence_upload'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['evidence_upload'] = False
    
    # Test 4: GET /api/assessment/progress/{user_id} (check gaps calculation)
    print("\n=== Test 4: GET /api/assessment/progress/{user_id} (gaps calculation) ===")
    try:
        # Get current user info first
        user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            user_id = user_data.get('id')
            
            response = requests.get(f"{API_BASE}/assessment/progress/{user_id}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Progress data: {json.dumps(data, indent=2)}")
                
                # Check if gaps are properly calculated
                gaps = data.get('gaps', [])
                total_gaps = data.get('total_gaps', 0)
                
                print(f"Total gaps found: {total_gaps}")
                print(f"Gap details: {gaps}")
                
                if total_gaps > 0:
                    results['progress_gaps'] = True
                    print("✅ PASS: Gaps are properly calculated and returned")
                else:
                    results['progress_gaps'] = False
                    print("⚠️  No gaps found (may be expected if no 'no_help' answers)")
            else:
                print(f"❌ FAIL: {response.text}")
                results['progress_gaps'] = False
        else:
            print("❌ FAIL: Could not get user info")
            results['progress_gaps'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['progress_gaps'] = False
    
    return results

def test_knowledge_base_system(token):
    """Test Knowledge Base System"""
    print("\n" + "="*60)
    print("📚 TESTING KNOWLEDGE BASE SYSTEM")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: GET /api/knowledge-base/areas
    print("\n=== Test 1: GET /api/knowledge-base/areas ===")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/areas", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Knowledge base areas: {json.dumps(data, indent=2)}")
            areas = data.get('areas', [])
            if len(areas) > 0:
                results['kb_areas'] = True
                print(f"✅ PASS: Found {len(areas)} knowledge base areas")
            else:
                results['kb_areas'] = False
                print("❌ FAIL: No knowledge base areas found")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_areas'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_areas'] = False
    
    # Test 2: GET /api/knowledge-base/access
    print("\n=== Test 2: GET /api/knowledge-base/access ===")
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
    
    # Test 3: GET /api/knowledge-base/{area_id}/content
    print("\n=== Test 3: GET /api/knowledge-base/{area_id}/content ===")
    try:
        area_id = "business_formation"  # Test with a sample area ID
        response = requests.get(f"{API_BASE}/knowledge-base/{area_id}/content", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Content preview: {json.dumps(data, indent=2)[:500]}...")
            results['kb_content'] = True
            print("✅ PASS: Knowledge base content endpoint working")
        else:
            print(f"❌ FAIL: {response.text}")
            results['kb_content'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['kb_content'] = False
    
    # Test 4: POST /api/payments/knowledge-base (payment processing)
    print("\n=== Test 4: POST /api/payments/knowledge-base ===")
    try:
        payload = {
            "area_id": "business_formation",
            "payment_method": "credit_card",
            "amount": 29.99
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

def test_service_provider_matching(token):
    """Test Service Provider Matching System"""
    print("\n" + "="*60)
    print("🤝 TESTING SERVICE PROVIDER MATCHING SYSTEM")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: POST /api/service-requests/professional-help
    print("\n=== Test 1: POST /api/service-requests/professional-help ===")
    try:
        payload = {
            "service_type": "business_formation",
            "description": "Need help with business registration and licensing",
            "budget_range": "500-1500",
            "timeline": "2-4 weeks",
            "location": "San Antonio, TX"
        }
        
        response = requests.post(f"{API_BASE}/service-requests/professional-help", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Service request response: {json.dumps(data, indent=2)}")
            request_id = data.get('request_id')
            if request_id:
                results['service_request'] = True
                results['request_id'] = request_id
                print("✅ PASS: Professional help request created successfully")
            else:
                results['service_request'] = False
                print("❌ FAIL: No request_id returned")
        else:
            print(f"❌ FAIL: {response.text}")
            results['service_request'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['service_request'] = False
    
    # Create a provider user for testing notifications
    provider_token = create_provider_user()
    
    # Test 2: GET /api/provider/notifications
    print("\n=== Test 2: GET /api/provider/notifications ===")
    try:
        if provider_token:
            provider_headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
            response = requests.get(f"{API_BASE}/provider/notifications", headers=provider_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Provider notifications: {json.dumps(data, indent=2)}")
                notifications = data.get('notifications', [])
                results['provider_notifications'] = True
                print(f"✅ PASS: Found {len(notifications)} provider notifications")
            else:
                print(f"❌ FAIL: {response.text}")
                results['provider_notifications'] = False
        else:
            print("❌ FAIL: Could not create provider user")
            results['provider_notifications'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['provider_notifications'] = False
    
    # Test 3: POST /api/provider/respond-to-request
    print("\n=== Test 3: POST /api/provider/respond-to-request ===")
    try:
        if provider_token and results.get('request_id'):
            payload = {
                "request_id": results['request_id'],
                "response": "interested",
                "proposal": "I can help with business formation and licensing. 15 years experience.",
                "estimated_cost": 1200.00,
                "timeline": "3 weeks"
            }
            
            provider_headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
            response = requests.post(f"{API_BASE}/provider/respond-to-request", json=payload, headers=provider_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Provider response: {json.dumps(data, indent=2)}")
                results['provider_response'] = True
                print("✅ PASS: Provider response submitted successfully")
            else:
                print(f"❌ FAIL: {response.text}")
                results['provider_response'] = False
        else:
            print("❌ SKIP: No provider token or request_id available")
            results['provider_response'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['provider_response'] = False
    
    return results

def create_provider_user():
    """Create a provider user for testing"""
    print("\n=== Creating Provider User ===")
    try:
        provider_email = f"provider_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": provider_email,
            "password": "ProviderPass123!",
            "role": "provider",
            "terms_accepted": True
        }
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Login to get token
            login_payload = {"email": provider_email, "password": "ProviderPass123!"}
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print("✅ Provider user created and logged in")
                return token
        
        print("❌ Failed to create provider user")
        return None
    except Exception as e:
        print(f"❌ Error creating provider user: {e}")
        return None

def test_free_resources_and_analytics(token):
    """Test Free Resources and Analytics"""
    print("\n" + "="*60)
    print("📊 TESTING FREE RESOURCES AND ANALYTICS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: GET /api/free-resources/recommendations
    print("\n=== Test 1: GET /api/free-resources/recommendations ===")
    try:
        response = requests.get(f"{API_BASE}/free-resources/recommendations", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Free resources: {json.dumps(data, indent=2)}")
            resources = data.get('resources', [])
            if len(resources) > 0:
                results['free_resources'] = True
                print(f"✅ PASS: Found {len(resources)} free resources")
            else:
                results['free_resources'] = False
                print("❌ FAIL: No free resources found")
        else:
            print(f"❌ FAIL: {response.text}")
            results['free_resources'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['free_resources'] = False
    
    # Test 2: POST /api/analytics/resource-access (tracking)
    print("\n=== Test 2: POST /api/analytics/resource-access ===")
    try:
        payload = {
            "resource_id": "sba_business_guide",
            "resource_type": "guide",
            "action": "view",
            "metadata": {
                "source": "gap_recommendations",
                "area": "business_formation"
            }
        }
        
        response = requests.post(f"{API_BASE}/analytics/resource-access", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Analytics response: {json.dumps(data, indent=2)}")
            results['analytics_tracking'] = True
            print("✅ PASS: Resource access tracked successfully")
        else:
            print(f"❌ FAIL: {response.text}")
            results['analytics_tracking'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['analytics_tracking'] = False
    
    return results

def test_client_dashboard_apis(token):
    """Test Client Dashboard APIs"""
    print("\n" + "="*60)
    print("🏠 TESTING CLIENT DASHBOARD APIS")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get user ID first
    user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    user_id = None
    if user_response.status_code == 200:
        user_data = user_response.json()
        user_id = user_data.get('id')
    
    # Test 1: GET /api/assessment/progress/{user_id} (comprehensive data)
    print("\n=== Test 1: GET /api/assessment/progress/{user_id} (comprehensive) ===")
    try:
        if user_id:
            response = requests.get(f"{API_BASE}/assessment/progress/{user_id}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Comprehensive progress: {json.dumps(data, indent=2)}")
                
                # Check for comprehensive data fields
                expected_fields = ['total_questions', 'answered_questions', 'gaps', 'completion_percentage']
                has_fields = all(field in data for field in expected_fields)
                
                if has_fields:
                    results['comprehensive_progress'] = True
                    print("✅ PASS: Comprehensive progress data available")
                else:
                    results['comprehensive_progress'] = False
                    print("❌ FAIL: Missing comprehensive progress fields")
            else:
                print(f"❌ FAIL: {response.text}")
                results['comprehensive_progress'] = False
        else:
            print("❌ FAIL: Could not get user ID")
            results['comprehensive_progress'] = False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['comprehensive_progress'] = False
    
    # Test 2: GET /api/agency/info/{agency_id}
    print("\n=== Test 2: GET /api/agency/info/{agency_id} ===")
    try:
        agency_id = "sample_agency_001"  # Test with sample agency ID
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
    
    # Test 3: GET /api/engagements/my-services
    print("\n=== Test 3: GET /api/engagements/my-services ===")
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

def test_end_to_end_workflow(token):
    """Test complete end-to-end workflow"""
    print("\n" + "="*60)
    print("🔄 TESTING END-TO-END WORKFLOW")
    print("="*60)
    
    results = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("Testing complete client journey from assessment to service matching...")
    
    # Step 1: Answer assessment questions with gaps
    print("\n--- Step 1: Create gaps through assessment ---")
    gap_payload = {
        "question_id": "q2_1",
        "answer": "no_help",
        "area_id": "area2",
        "gap_description": "Need help setting up accounting system"
    }
    
    gap_response = requests.post(f"{API_BASE}/assessment/answer", json=gap_payload, headers=headers)
    gap_created = gap_response.status_code == 200
    print(f"Gap creation: {'✅ SUCCESS' if gap_created else '❌ FAILED'}")
    
    # Step 2: Get free resources for the gap
    print("\n--- Step 2: Get free resources recommendations ---")
    resources_response = requests.get(f"{API_BASE}/free-resources/recommendations", headers=headers)
    resources_available = resources_response.status_code == 200
    print(f"Free resources: {'✅ SUCCESS' if resources_available else '❌ FAILED'}")
    
    # Step 3: Request professional help
    print("\n--- Step 3: Request professional help ---")
    help_payload = {
        "service_type": "financial_operations",
        "description": "Need professional help setting up accounting system",
        "budget_range": "750-2000",
        "timeline": "2-3 weeks",
        "location": "San Antonio, TX"
    }
    
    help_response = requests.post(f"{API_BASE}/service-requests/professional-help", json=help_payload, headers=headers)
    help_requested = help_response.status_code == 200
    print(f"Professional help request: {'✅ SUCCESS' if help_requested else '❌ FAILED'}")
    
    # Step 4: Track analytics
    print("\n--- Step 4: Track resource access ---")
    analytics_payload = {
        "resource_id": "accounting_setup_guide",
        "resource_type": "guide",
        "action": "download",
        "metadata": {"source": "gap_workflow", "area": "financial_operations"}
    }
    
    analytics_response = requests.post(f"{API_BASE}/analytics/resource-access", json=analytics_payload, headers=headers)
    analytics_tracked = analytics_response.status_code == 200
    print(f"Analytics tracking: {'✅ SUCCESS' if analytics_tracked else '❌ FAILED'}")
    
    # Overall workflow success
    workflow_success = all([gap_created, resources_available, help_requested, analytics_tracked])
    results['end_to_end_workflow'] = workflow_success
    
    if workflow_success:
        print("\n🎉 END-TO-END WORKFLOW SUCCESSFUL!")
        print("✅ Gap recording working")
        print("✅ Free resources integration working")
        print("✅ Professional help matching working")
        print("✅ Analytics tracking working")
    else:
        print("\n❌ END-TO-END WORKFLOW FAILED")
        print("Some components are not working together seamlessly")
    
    return results

def main():
    """Run comprehensive holistic testing of Polaris system"""
    print("🚀 STARTING HOLISTIC POLARIS SYSTEM TESTING")
    print("="*80)
    
    # Setup test user
    if not create_test_user():
        print("❌ Failed to create test user, aborting tests")
        return False
    
    token = login_test_user()
    if not token:
        print("❌ Failed to login test user, aborting tests")
        return False
    
    all_results = {}
    
    # Test 1: Assessment System with Gap Recording
    assessment_results = test_assessment_system_with_gaps(token)
    all_results.update(assessment_results)
    
    # Test 2: Knowledge Base System
    kb_results = test_knowledge_base_system(token)
    all_results.update(kb_results)
    
    # Test 3: Service Provider Matching System
    matching_results = test_service_provider_matching(token)
    all_results.update(matching_results)
    
    # Test 4: Free Resources and Analytics
    resources_results = test_free_resources_and_analytics(token)
    all_results.update(resources_results)
    
    # Test 5: Client Dashboard APIs
    dashboard_results = test_client_dashboard_apis(token)
    all_results.update(dashboard_results)
    
    # Test 6: End-to-End Workflow
    workflow_results = test_end_to_end_workflow(token)
    all_results.update(workflow_results)
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 HOLISTIC TESTING SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    
    print("\n🔍 ASSESSMENT SYSTEM WITH GAP RECORDING:")
    assessment_tests = ['answer_yes', 'answer_no_help', 'evidence_upload', 'progress_gaps']
    for test in assessment_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n📚 KNOWLEDGE BASE SYSTEM:")
    kb_tests = ['kb_areas', 'kb_access', 'kb_content', 'kb_payment']
    for test in kb_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n🤝 SERVICE PROVIDER MATCHING SYSTEM:")
    matching_tests = ['service_request', 'provider_notifications', 'provider_response']
    for test in matching_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n📊 FREE RESOURCES AND ANALYTICS:")
    resources_tests = ['free_resources', 'analytics_tracking']
    for test in resources_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n🏠 CLIENT DASHBOARD APIS:")
    dashboard_tests = ['comprehensive_progress', 'agency_info', 'my_services']
    for test in dashboard_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print("\n🔄 END-TO-END WORKFLOW:")
    workflow_tests = ['end_to_end_workflow']
    for test in workflow_tests:
        if test in all_results:
            status = "✅ PASS" if all_results[test] else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL HOLISTIC TESTS PASSED!")
        print("The complete Polaris system with all enhancements is working seamlessly!")
        return True
    else:
        print(f"\n⚠️  {total-passed} TESTS FAILED")
        print("Some components need attention for complete system integration")
        return False

if __name__ == "__main__":
    main()