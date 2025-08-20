#!/usr/bin/env python3
"""
Complete Assessment Flow Test
Tests the complete user journey through the assessment system
"""

import requests
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agency-connect-4.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"🎯 COMPLETE ASSESSMENT FLOW TEST")
print(f"Testing backend at: {API_BASE}")

def test_complete_assessment_flow():
    """Test the complete assessment flow as specified in the review request"""
    print("\n=== COMPLETE ASSESSMENT FLOW TEST ===")
    
    # Step 1: Register user
    test_email = f"flow_test_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "TestPass123!"
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "role": "client",
        "terms_accepted": True
    }
    
    print("Step 1: User Registration")
    register_response = requests.post(f"{API_BASE}/auth/register", json=register_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    print("✅ User registered successfully")
    
    # Step 2: Login user
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    print("Step 2: User Login")
    login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    print("✅ User logged in successfully")
    
    # Step 3: Get assessment schema (no auth required)
    print("Step 3: Get Assessment Schema")
    schema_response = requests.get(f"{API_BASE}/assessment/schema")
    if schema_response.status_code != 200:
        print(f"❌ Schema retrieval failed: {schema_response.text}")
        return False
    
    schema_data = schema_response.json()
    areas = schema_data["schema"]["areas"]
    print(f"✅ Assessment schema retrieved: {len(areas)} areas")
    
    # Step 4: Create assessment session
    print("Step 4: Create Assessment Session")
    session_response = requests.post(f"{API_BASE}/assessment/session", headers=headers)
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.text}")
        return False
    
    session_data = session_response.json()
    session_id = session_data.get("session_id")
    print(f"✅ Assessment session created: {session_id}")
    
    # Step 5: Get initial progress
    print("Step 5: Get Initial Progress")
    progress_response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress", headers=headers)
    if progress_response.status_code != 200:
        print(f"❌ Progress retrieval failed: {progress_response.text}")
        return False
    
    progress_data = progress_response.json()
    print(f"✅ Initial progress: {progress_data['progress_percentage']}% ({progress_data['answered_questions']}/{progress_data['total_questions']})")
    
    # Step 6: Submit responses for each area
    print("Step 6: Submit Assessment Responses")
    for i, area in enumerate(areas):
        for question in area["questions"]:
            question_id = question["id"]
            answer = "yes" if i % 2 == 0 else "no"  # Alternate answers
            
            response_data = {
                "question_id": question_id,
                "answer": answer
            }
            
            submit_response = requests.post(
                f"{API_BASE}/assessment/session/{session_id}/response",
                headers=headers,
                json=response_data
            )
            
            if submit_response.status_code != 200:
                print(f"❌ Response submission failed for {question_id}: {submit_response.text}")
                return False
            
            submit_data = submit_response.json()
            print(f"  ✅ Submitted {question_id}: {answer} (Progress: {submit_data['progress_percentage']:.1f}%)")
    
    # Step 7: Get final progress
    print("Step 7: Get Final Progress")
    final_progress_response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress", headers=headers)
    if final_progress_response.status_code != 200:
        print(f"❌ Final progress retrieval failed: {final_progress_response.text}")
        return False
    
    final_progress_data = final_progress_response.json()
    print(f"✅ Final progress: {final_progress_data['progress_percentage']}% ({final_progress_data['answered_questions']}/{final_progress_data['total_questions']})")
    
    # Step 8: Get AI explanations for questions
    print("Step 8: Get AI Explanations")
    for area in areas:
        for question in area["questions"]:
            question_id = question["id"]
            
            ai_data = {
                "question_id": question_id,
                "context": f"Need help understanding {question['text']}"
            }
            
            ai_response = requests.post(f"{API_BASE}/ai/explain", headers=headers, json=ai_data)
            if ai_response.status_code != 200:
                print(f"❌ AI explanation failed for {question_id}: {ai_response.text}")
                return False
            
            ai_explanation = ai_response.json()
            print(f"  ✅ AI explanation for {question_id}: {ai_explanation.get('area', 'Unknown area')}")
    
    print("\n🎉 COMPLETE ASSESSMENT FLOW SUCCESSFUL!")
    print(f"✅ User Journey: Register → Login → Schema → Session → Progress → Responses → AI Explanations")
    print(f"✅ Final Assessment Status: {final_progress_data['status']}")
    print(f"✅ Completion Rate: {final_progress_data['progress_percentage']}%")
    
    return True

if __name__ == "__main__":
    success = test_complete_assessment_flow()
    if success:
        print("\n✅ ALL ASSESSMENT SYSTEM REQUIREMENTS VERIFIED!")
    else:
        print("\n❌ ASSESSMENT SYSTEM FLOW FAILED!")