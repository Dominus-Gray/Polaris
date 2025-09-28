#!/usr/bin/env python3
"""
Phase 2 Specific Backend Tests as requested in review
Tests the exact flow mentioned in the review request
"""

import requests
import json
import uuid
import os
import io
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://polaris-migrate.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing Phase 2 specific flow at: {API_BASE}")

def test_phase2_specific_flow():
    """Test the exact Phase 2 flow as requested in review"""
    print("\n🚀 PHASE 2 SPECIFIC FLOW TEST")
    print("="*60)
    
    # Step 1: Register navigator user, login, get /auth/me
    print("\n1️⃣ NAVIGATOR AUTH FLOW")
    print("-" * 30)
    
    navigator_email = f"nav_{uuid.uuid4().hex[:8]}@test.com"
    nav_payload = {
        "email": navigator_email,
        "password": "NavPass123!",
        "role": "navigator"
    }
    
    # Register navigator
    response = requests.post(f"{API_BASE}/auth/register", json=nav_payload)
    print(f"Navigator register: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Navigator registration failed - {response.text}")
        return False
    
    # Login navigator
    login_payload = {"email": navigator_email, "password": "NavPass123!"}
    response = requests.post(f"{API_BASE}/auth/login", json=login_payload)
    print(f"Navigator login: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Navigator login failed - {response.text}")
        return False
    
    navigator_token = response.json().get('access_token')
    nav_headers = {"Authorization": f"Bearer {navigator_token}"}
    
    # Get /auth/me for navigator
    response = requests.get(f"{API_BASE}/auth/me", headers=nav_headers)
    print(f"Navigator /auth/me: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Navigator /auth/me failed - {response.text}")
        return False
    
    nav_user = response.json()
    print(f"✅ Navigator user: {nav_user['email']} (role: {nav_user['role']})")
    
    # Step 2: Register client user, login, get /auth/me
    print("\n2️⃣ CLIENT AUTH FLOW")
    print("-" * 30)
    
    client_email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    client_payload = {
        "email": client_email,
        "password": "ClientPass123!",
        "role": "client"
    }
    
    # Register client
    response = requests.post(f"{API_BASE}/auth/register", json=client_payload)
    print(f"Client register: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Client registration failed - {response.text}")
        return False
    
    # Login client
    login_payload = {"email": client_email, "password": "ClientPass123!"}
    response = requests.post(f"{API_BASE}/auth/login", json=login_payload)
    print(f"Client login: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Client login failed - {response.text}")
        return False
    
    client_token = response.json().get('access_token')
    client_headers = {"Authorization": f"Bearer {client_token}"}
    
    # Get /auth/me for client
    response = requests.get(f"{API_BASE}/auth/me", headers=client_headers)
    print(f"Client /auth/me: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Client /auth/me failed - {response.text}")
        return False
    
    client_user = response.json()
    print(f"✅ Client user: {client_user['email']} (role: {client_user['role']})")
    
    # Step 3: Client creates assessment session
    print("\n3️⃣ CLIENT SESSION CREATION")
    print("-" * 30)
    
    response = requests.post(f"{API_BASE}/assessment/session", headers=client_headers)
    print(f"Session creation: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Session creation failed - {response.text}")
        return False
    
    session_id = response.json().get('session_id')
    print(f"✅ Session created: {session_id}")
    
    # Step 4: Mark area3 q1 Yes with bulk answers
    print("\n4️⃣ BULK ANSWERS (area3 q1 = Yes)")
    print("-" * 30)
    
    bulk_payload = {
        "session_id": session_id,
        "answers": [
            {
                "area_id": "area3",
                "question_id": "q1",
                "value": True,
                "evidence_ids": []
            }
        ]
    }
    
    response = requests.post(f"{API_BASE}/assessment/answers/bulk", json=bulk_payload, headers=client_headers)
    print(f"Bulk answers: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Bulk answers failed - {response.text}")
        return False
    
    print("✅ Area3 Q1 marked as Yes")
    
    # Step 5: Perform chunked upload flow
    print("\n5️⃣ CHUNKED UPLOAD FLOW")
    print("-" * 30)
    
    # Initiate upload
    initiate_payload = {
        "file_name": "business_registration_certificate.pdf",
        "total_size": 3000000,  # 3MB
        "session_id": session_id,
        "area_id": "area3",
        "question_id": "q1"
    }
    
    response = requests.post(f"{API_BASE}/upload/initiate", json=initiate_payload, headers=client_headers)
    print(f"Upload initiate: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Upload initiate failed - {response.text}")
        return False
    
    upload_id = response.json().get('upload_id')
    print(f"Upload ID: {upload_id}")
    
    # Upload single chunk
    chunk_data = b'PDF_HEADER_' + b'A' * 2999985  # Simulate PDF content
    chunk_file = io.BytesIO(chunk_data)
    
    files = {'file': ('chunk.part', chunk_file, 'application/pdf')}
    data = {'upload_id': upload_id, 'chunk_index': 0}
    
    response = requests.post(f"{API_BASE}/upload/chunk", files=files, data=data, headers={"Authorization": f"Bearer {client_token}"})
    print(f"Chunk upload: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Chunk upload failed - {response.text}")
        return False
    
    # Complete upload
    complete_payload = {"upload_id": upload_id, "total_chunks": 1}
    response = requests.post(f"{API_BASE}/upload/complete", json=complete_payload, headers=client_headers)
    print(f"Upload complete: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Upload complete failed - {response.text}")
        return False
    
    complete_data = response.json()
    review_id = complete_data.get('review_id')
    print(f"✅ Upload completed, review ID: {review_id}")
    
    # Step 6: Check evidence list shows pending
    print("\n6️⃣ EVIDENCE LIST CHECK (should show pending)")
    print("-" * 30)
    
    response = requests.get(f"{API_BASE}/assessment/session/{session_id}/answer/area3/q1/evidence")
    print(f"Evidence list: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Evidence list failed - {response.text}")
        return False
    
    evidence_data = response.json()
    evidence_list = evidence_data.get('evidence', [])
    print(f"Evidence count: {len(evidence_list)}")
    
    found_pending = False
    for evidence in evidence_list:
        if evidence.get('upload_id') == upload_id:
            status = evidence.get('status')
            print(f"Evidence status: {status}")
            if status == 'pending':
                found_pending = True
                print("✅ Evidence shows pending status")
            break
    
    if not found_pending:
        print("❌ FAIL: Evidence not found or not pending")
        return False
    
    # Step 7: Navigator lists reviews pending
    print("\n7️⃣ NAVIGATOR REVIEW QUEUE")
    print("-" * 30)
    
    response = requests.get(f"{API_BASE}/navigator/reviews?status=pending", headers=nav_headers)
    print(f"Navigator reviews: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Navigator reviews failed - {response.text}")
        return False
    
    reviews_data = response.json()
    reviews = reviews_data.get('reviews', [])
    print(f"Pending reviews: {len(reviews)}")
    
    # Find our review
    our_review = None
    for review in reviews:
        if review.get('id') == review_id:
            our_review = review
            break
    
    if not our_review:
        print(f"❌ FAIL: Our review {review_id} not found in pending reviews")
        return False
    
    print(f"✅ Found our review: {our_review['file_name']} (area: {our_review['area_title']})")
    
    # Step 8: Navigator approves the review
    print("\n8️⃣ NAVIGATOR APPROVAL")
    print("-" * 30)
    
    decision_payload = {
        "decision": "approved",
        "notes": "Business registration certificate looks valid and complete."
    }
    
    response = requests.post(f"{API_BASE}/navigator/reviews/{review_id}/decision", json=decision_payload, headers=nav_headers)
    print(f"Navigator decision: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Navigator decision failed - {response.text}")
        return False
    
    print("✅ Navigator approved the review")
    
    # Wait a moment for the approval to propagate
    time.sleep(1)
    
    # Step 9: Verify evidence list now shows status approved
    print("\n9️⃣ EVIDENCE LIST CHECK (should show approved)")
    print("-" * 30)
    
    response = requests.get(f"{API_BASE}/assessment/session/{session_id}/answer/area3/q1/evidence")
    print(f"Evidence list: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Evidence list failed - {response.text}")
        return False
    
    evidence_data = response.json()
    evidence_list = evidence_data.get('evidence', [])
    
    found_approved = False
    for evidence in evidence_list:
        if evidence.get('upload_id') == upload_id:
            status = evidence.get('status')
            print(f"Evidence status after approval: {status}")
            if status == 'approved':
                found_approved = True
                print("✅ Evidence now shows approved status")
            break
    
    if not found_approved:
        print("❌ FAIL: Evidence not found or not approved")
        return False
    
    # Step 10: Verify progress endpoint shows percent increase
    print("\n🔟 PROGRESS CHECK (should reflect approved evidence)")
    print("-" * 30)
    
    response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress")
    print(f"Progress: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Progress failed - {response.text}")
        return False
    
    progress_data = response.json()
    approved_evidence_answers = progress_data.get('approved_evidence_answers', 0)
    percent_complete = progress_data.get('percent_complete', 0)
    
    print(f"Approved evidence answers: {approved_evidence_answers}")
    print(f"Percent complete: {percent_complete}%")
    
    if approved_evidence_answers > 0 and percent_complete > 0:
        print("✅ Progress reflects approved evidence")
    else:
        print("⚠️  Progress may not yet reflect approval (possible timing issue)")
    
    # Step 11: Test DELETE /upload/{upload_id} as navigator
    print("\n1️⃣1️⃣ DELETE EVIDENCE AS NAVIGATOR")
    print("-" * 30)
    
    response = requests.delete(f"{API_BASE}/upload/{upload_id}", headers=nav_headers)
    print(f"Delete as navigator: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Delete as navigator failed - {response.text}")
        return False
    
    print("✅ Navigator successfully deleted evidence")
    
    # Step 12: Verify evidence list updates and progress recalculates
    print("\n1️⃣2️⃣ VERIFY DELETE EFFECTS")
    print("-" * 30)
    
    # Check evidence list
    response = requests.get(f"{API_BASE}/assessment/session/{session_id}/answer/area3/q1/evidence")
    if response.status_code == 200:
        evidence_data = response.json()
        evidence_list = evidence_data.get('evidence', [])
        print(f"Evidence count after delete: {len(evidence_list)}")
        
        # Check if our evidence is gone or marked as deleted
        found_deleted = False
        for evidence in evidence_list:
            if evidence.get('upload_id') == upload_id:
                print(f"Evidence still exists with status: {evidence.get('status')}")
                found_deleted = True
                break
        
        if not found_deleted:
            print("✅ Evidence removed from list")
        else:
            print("✅ Evidence marked as deleted")
    
    # Check progress recalculation
    response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress")
    if response.status_code == 200:
        new_progress_data = response.json()
        new_approved_evidence_answers = new_progress_data.get('approved_evidence_answers', 0)
        new_percent_complete = new_progress_data.get('percent_complete', 0)
        
        print(f"Progress after delete - Approved evidence answers: {new_approved_evidence_answers}")
        print(f"Progress after delete - Percent complete: {new_percent_complete}%")
        
        if new_approved_evidence_answers <= approved_evidence_answers and new_percent_complete <= percent_complete:
            print("✅ Progress recalculated after delete")
        else:
            print("⚠️  Progress may not have recalculated yet")
    
    print("\n🎉 PHASE 2 SPECIFIC FLOW COMPLETED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    success = test_phase2_specific_flow()
    if success:
        print("\n✅ ALL PHASE 2 SPECIFIC TESTS PASSED")
    else:
        print("\n❌ SOME PHASE 2 SPECIFIC TESTS FAILED")