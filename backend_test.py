#!/usr/bin/env python3
"""
Backend API Testing for Polaris MVP
Tests all backend endpoints as specified in test_result.md
"""

import requests
import json
import uuid
import os
import io
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "frontend" / ".env")

# Get base URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://small-biz-assess.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def test_assessment_schema():
    """Test GET /api/assessment/schema should return 8 areas"""
    print("\n=== Testing Assessment Schema ===")
    try:
        response = requests.get(f"{API_BASE}/assessment/schema")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            areas = data.get('areas', [])
            print(f"Number of areas returned: {len(areas)}")
            
            if len(areas) == 8:
                print("✅ PASS: Schema returns exactly 8 areas")
                # Print area titles for verification
                for i, area in enumerate(areas, 1):
                    print(f"  Area {i}: {area.get('title', 'No title')}")
                return True
            else:
                print(f"❌ FAIL: Expected 8 areas, got {len(areas)}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_create_session():
    """Test POST /api/assessment/session returns session_id UUID"""
    print("\n=== Testing Create Session ===")
    try:
        response = requests.post(f"{API_BASE}/assessment/session")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            
            # Validate UUID format
            try:
                uuid.UUID(session_id)
                print("✅ PASS: Session created with valid UUID")
                return session_id
            except ValueError:
                print(f"❌ FAIL: Invalid UUID format: {session_id}")
                return None
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_bulk_answers(session_id):
    """Test POST /api/assessment/answers/bulk"""
    print("\n=== Testing Bulk Answers ===")
    try:
        payload = {
            "session_id": session_id,
            "answers": [
                {
                    "area_id": "area1",
                    "question_id": "q1",
                    "value": True,
                    "evidence_ids": ["dummy"]
                }
            ]
        }
        
        response = requests.post(
            f"{API_BASE}/assessment/answers/bulk",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ PASS: Bulk answers saved successfully")
                return True
            else:
                print(f"❌ FAIL: Response not ok: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_progress(session_id):
    """Test GET /api/assessment/session/{session}/progress"""
    print("\n=== Testing Progress Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Progress data: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['session_id', 'total_questions', 'answered', 'answered_with_required_evidence', 'percent_complete']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ PASS: Progress endpoint returns all required fields")
                print(f"  Total questions: {data['total_questions']}")
                print(f"  Answered: {data['answered']}")
                print(f"  Answered with evidence: {data['answered_with_required_evidence']}")
                print(f"  Percent complete: {data['percent_complete']}%")
                return True
            else:
                print(f"❌ FAIL: Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_chunked_upload_flow(session_id):
    """Test complete chunked upload flow"""
    print("\n=== Testing Chunked Upload Flow ===")
    
    # Step 1: Initiate upload
    print("Step 1: Initiating upload...")
    try:
        initiate_payload = {
            "file_name": "test.pdf",
            "total_size": 11000000,
            "session_id": session_id,
            "area_id": "area1",
            "question_id": "q1"
        }
        
        response = requests.post(
            f"{API_BASE}/upload/initiate",
            json=initiate_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Initiate status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAIL: Initiate failed - {response.text}")
            return False
            
        initiate_data = response.json()
        upload_id = initiate_data.get('upload_id')
        chunk_size = initiate_data.get('chunk_size', 5000000)
        print(f"Upload ID: {upload_id}")
        print(f"Chunk size: {chunk_size}")
        
    except Exception as e:
        print(f"❌ ERROR in initiate: {e}")
        return False
    
    # Step 2: Upload chunks
    print("Step 2: Uploading chunks...")
    try:
        total_size = 11000000
        chunk_size = min(chunk_size, 4000000)  # Use smaller chunks for testing
        total_chunks = (total_size + chunk_size - 1) // chunk_size  # Ceiling division
        
        for chunk_index in range(total_chunks):
            # Create dummy chunk data
            start_byte = chunk_index * chunk_size
            end_byte = min(start_byte + chunk_size, total_size)
            chunk_data = b'A' * (end_byte - start_byte)  # Dummy PDF-like data
            
            # Create file-like object
            chunk_file = io.BytesIO(chunk_data)
            
            files = {
                'file': ('chunk.part', chunk_file, 'application/octet-stream')
            }
            data = {
                'upload_id': upload_id,
                'chunk_index': chunk_index
            }
            
            response = requests.post(f"{API_BASE}/upload/chunk", files=files, data=data)
            print(f"Chunk {chunk_index} status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ FAIL: Chunk {chunk_index} upload failed - {response.text}")
                return False
                
        print(f"✅ All {total_chunks} chunks uploaded successfully")
        
    except Exception as e:
        print(f"❌ ERROR in chunk upload: {e}")
        return False
    
    # Step 3: Complete upload
    print("Step 3: Completing upload...")
    try:
        complete_payload = {
            "upload_id": upload_id,
            "total_chunks": total_chunks
        }
        
        response = requests.post(
            f"{API_BASE}/upload/complete",
            json=complete_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Complete status: {response.status_code}")
        
        if response.status_code == 200:
            complete_data = response.json()
            print(f"Complete response: {json.dumps(complete_data, indent=2)}")
            print("✅ PASS: Upload completed successfully")
            
            # Step 4: Verify evidence_ids updated
            print("Step 4: Verifying evidence_ids updated...")
            progress_response = requests.get(f"{API_BASE}/assessment/session/{session_id}/progress")
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                print(f"Updated progress: answered_with_required_evidence = {progress_data.get('answered_with_required_evidence', 0)}")
                
                # Also check the session data to see if evidence_ids were updated
                session_response = requests.get(f"{API_BASE}/assessment/session/{session_id}")
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    answers = session_data.get('answers', [])
                    area1_q1_answer = next((a for a in answers if a['area_id'] == 'area1' and a['question_id'] == 'q1'), None)
                    if area1_q1_answer and upload_id in area1_q1_answer.get('evidence_ids', []):
                        print("✅ PASS: Upload ID found in evidence_ids")
                        return True
                    else:
                        print(f"❌ FAIL: Upload ID not found in evidence_ids. Answer: {area1_q1_answer}")
                        return False
            
            return True
        else:
            print(f"❌ FAIL: Complete failed - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in complete: {e}")
        return False

def test_ai_explain():
    """Test POST /api/ai/explain - should return ok=true with AI response now that EMERGENT_LLM_KEY is set"""
    print("\n=== Testing AI Explain ===")
    try:
        payload = {
            "session_id": "test-ui",
            "area_id": "area1",
            "question_id": "q1",
            "question_text": "Is your business legally registered in Texas and San Antonio?"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/explain",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"AI response: {json.dumps(data, indent=2)}")
            
            if data.get('ok') == True and data.get('message') and len(data.get('message', '').strip()) > 0:
                print("✅ PASS: AI endpoint returns ok=true with non-empty message using openai/gpt-4o-mini")
                print(f"AI Message: {data.get('message')}")
                return True
            elif data.get('ok') == False:
                print(f"❌ FAIL: AI endpoint returned ok=false: {data.get('message', 'No message')}")
                return False
            else:
                print(f"❌ FAIL: Expected ok=true with non-empty message, got: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests")
    print(f"Base URL: {API_BASE}")
    
    results = {}
    
    # Test 1: Assessment Schema
    results['schema'] = test_assessment_schema()
    
    # Test 2: Create Session
    session_id = test_create_session()
    results['session'] = session_id is not None
    
    if session_id:
        # Test 3: Bulk Answers
        results['bulk_answers'] = test_bulk_answers(session_id)
        
        # Test 4: Progress
        results['progress'] = test_progress(session_id)
        
        # Test 5: Chunked Upload Flow
        results['chunked_upload'] = test_chunked_upload_flow(session_id)
    else:
        results['bulk_answers'] = False
        results['progress'] = False
        results['chunked_upload'] = False
    
    # Test 6: AI Explain
    results['ai_explain'] = test_ai_explain()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    main()