#!/usr/bin/env python3
"""
Tier-Based Assessment Results Debugging Test
Focus: Debug "Error Loading Results" issue for tier-based assessments
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://providermatrix.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class TierAssessmentResultsDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.session_id = None
        
    def authenticate(self):
        """Authenticate with QA credentials"""
        print("🔐 Authenticating with QA credentials...")
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=QA_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def create_tier_based_session(self, area_id="area1", tier_level=3):
        """Create a tier-based assessment session"""
        print(f"\n📝 Creating tier-based assessment session for {area_id} with tier {tier_level}...")
        
        # First, check tier access
        tier_access_response = self.session.get(f"{BASE_URL}/client/tier-access")
        if tier_access_response.status_code == 200:
            tier_data = tier_access_response.json()
            print(f"📊 Tier access data: {json.dumps(tier_data, indent=2)}")
        
        # Create tier-based session using form data (as backend expects)
        session_data = {
            "area_id": area_id,
            "tier_level": str(tier_level)
        }
        
        response = self.session.post(f"{BASE_URL}/assessment/tier-session", data=session_data)
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data.get("session_id")
            print(f"✅ Tier-based session created successfully")
            print(f"📋 Session ID: {self.session_id}")
            print(f"📊 Session data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Session creation failed: {response.status_code} - {response.text}")
            return False
    
    def get_session_questions(self):
        """Get questions for the tier-based session"""
        if not self.session_id:
            print("❌ No session ID available")
            return None
            
        print(f"\n📋 Getting questions for session {self.session_id}...")
        
        response = self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}/progress")
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            print(f"✅ Retrieved {len(questions)} questions from progress endpoint")
            print(f"📊 Progress data: {json.dumps(data, indent=2)}")
            
            # If no questions in progress, use the ones from session creation
            if not questions and hasattr(self, 'session_questions'):
                print(f"📋 Using questions from session creation: {len(self.session_questions)} questions")
                return self.session_questions
            
            return questions
        else:
            print(f"❌ Failed to get questions: {response.status_code} - {response.text}")
            return None
    
    def submit_all_responses(self, questions):
        """Submit responses to complete the assessment (all 9 questions for tier 3)"""
        if not questions:
            print("❌ No questions to answer")
            return False
            
        print(f"\n📝 Submitting responses for all {len(questions)} questions...")
        
        # Submit responses for all questions
        for i, question in enumerate(questions):
            question_id = question.get("id") or question.get("question_id")
            
            # Vary responses to make it realistic
            if i % 3 == 0:
                response_value = "yes"
            elif i % 3 == 1:
                response_value = "partial"
            else:
                response_value = "no"
            
            response_data = {
                "question_id": question_id,
                "response": response_value,
                "evidence_provided": "true" if response_value == "yes" else "false",
                "evidence_url": f"https://example.com/evidence_{i}.pdf" if response_value == "yes" else ""
            }
            
            print(f"📝 Submitting response {i+1}/{len(questions)}: {response_value}")
            
            response = self.session.post(
                f"{BASE_URL}/assessment/tier-session/{self.session_id}/response", 
                data=response_data
            )
            
            if response.status_code == 200:
                print(f"✅ Response {i+1} submitted successfully")
            else:
                print(f"❌ Response {i+1} failed: {response.status_code} - {response.text}")
                return False
        
        print("✅ All responses submitted successfully")
        return True
    
    def check_session_completion(self):
        """Check if session is properly completed"""
        print(f"\n🔍 Checking session completion status...")
        
        response = self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}/progress")
        
        if response.status_code == 200:
            data = response.json()
            completed = data.get("completed", False)
            completed_at = data.get("completed_at")
            responses_count = len(data.get("responses", []))
            
            print(f"📊 Session completion status:")
            print(f"   - Completed: {completed}")
            print(f"   - Completed at: {completed_at}")
            print(f"   - Responses count: {responses_count}")
            print(f"   - Full progress data: {json.dumps(data, indent=2)}")
            
            return completed
        else:
            print(f"❌ Failed to check completion: {response.status_code} - {response.text}")
            return False
    
    def test_results_endpoint(self):
        """Test the results endpoint - this is the main focus"""
        print(f"\n🎯 TESTING RESULTS ENDPOINT - Main Focus")
        print(f"📊 Testing GET /api/assessment/results/{self.session_id}")
        
        response = self.session.get(f"{BASE_URL}/assessment/results/{self.session_id}")
        
        print(f"📊 Results endpoint response:")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Results retrieved successfully")
                print(f"📊 Results structure: {json.dumps(data, indent=2)}")
                
                # Validate expected fields
                expected_fields = ["session_id", "tier_level", "responses", "tier_completion_score"]
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️ Missing expected fields: {missing_fields}")
                else:
                    print(f"✅ All expected fields present")
                
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"📄 Raw response: {response.text}")
                return False
        else:
            print(f"❌ Results endpoint failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"📊 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Raw error text: {response.text}")
            
            return False
    
    def debug_session_data(self):
        """Debug session data in database"""
        print(f"\n🔍 DEBUGGING SESSION DATA")
        
        # Check if session exists in different endpoints
        endpoints_to_check = [
            f"/assessment/tier-session/{self.session_id}/progress",
            f"/assessment/sessions/{self.session_id}",  # Alternative endpoint
        ]
        
        for endpoint in endpoints_to_check:
            print(f"\n🔍 Checking endpoint: {endpoint}")
            response = self.session.get(f"{BASE_URL}{endpoint}")
            print(f"   - Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   - Data: {json.dumps(data, indent=2)}")
                except:
                    print(f"   - Raw: {response.text}")
            else:
                print(f"   - Error: {response.text}")
    
    def run_complete_debug_test(self):
        """Run the complete debugging test"""
        print("🚀 STARTING TIER-BASED ASSESSMENT RESULTS DEBUGGING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Create tier-based session
        if not self.create_tier_based_session():
            return False
        
        # Step 3: Get questions
        questions = self.get_session_questions()
        if not questions:
            return False
        
        # Step 4: Submit all responses
        if not self.submit_all_responses(questions):
            return False
        
        # Step 5: Check completion
        if not self.check_session_completion():
            print("⚠️ Session may not be properly completed, but continuing...")
        
        # Step 6: Test results endpoint (MAIN FOCUS)
        results_success = self.test_results_endpoint()
        
        # Step 7: Debug session data
        self.debug_session_data()
        
        print("\n" + "=" * 60)
        if results_success:
            print("✅ DEBUGGING COMPLETE: Results endpoint working correctly")
        else:
            print("❌ DEBUGGING COMPLETE: Results endpoint has issues")
        
        return results_success

def main():
    """Main test execution"""
    debugger = TierAssessmentResultsDebugger()
    success = debugger.run_complete_debug_test()
    
    if success:
        print("\n🎉 All tests passed - No issues found with results endpoint")
    else:
        print("\n🚨 Issues identified with results endpoint - See details above")

if __name__ == "__main__":
    main()