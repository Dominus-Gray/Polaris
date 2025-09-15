#!/usr/bin/env python3
"""
Focused Backend Smoke Retest - January 2025
Re-run focused backend smoke retest for previously failing items only
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Test Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api"

# QA Credentials
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class BackendSmokeRetest:
    def __init__(self):
        self.session = None
        self.client_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate to get client token
        try:
            login_data = {
                "email": QA_CREDENTIALS["email"],
                "password": QA_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.client_token = result.get("access_token")
                    print(f"✅ Authentication successful - Token: {self.client_token[:20]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    async def test_assessment_schema_tier_based(self):
        """Test 1: GET /api/assessment/schema/tier-based with client token"""
        print("\n🔍 Test 1: Assessment Schema Tier-Based")
        
        if not self.client_token:
            self.test_results.append({
                "test": "GET /api/assessment/schema/tier-based",
                "status": "FAIL",
                "reason": "No client token available"
            })
            return
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        try:
            async with self.session.get(f"{API_BASE}/assessment/schema/tier-based", headers=headers) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        
                        # Check for area10 presence
                        areas = data.get("areas", [])
                        area10_found = False
                        area10_details = None
                        
                        for area in areas:
                            if area.get("area_id") == "area10":
                                area10_found = True
                                area10_details = area
                                break
                        
                        # Verify each area has required keys
                        all_areas_valid = True
                        missing_keys = []
                        
                        for area in areas:
                            required_keys = ["id", "area_id", "title", "area_name"]
                            for key in required_keys:
                                if key not in area:
                                    all_areas_valid = False
                                    missing_keys.append(f"Area {area.get('area_id', 'unknown')} missing {key}")
                        
                        if area10_found and all_areas_valid:
                            self.test_results.append({
                                "test": "GET /api/assessment/schema/tier-based",
                                "status": "PASS",
                                "details": f"✅ area10 present: {area10_details.get('title', 'N/A')}, all areas have required keys"
                            })
                            print(f"✅ PASS: area10 found - {area10_details.get('title', 'N/A')}")
                        else:
                            issues = []
                            if not area10_found:
                                issues.append("area10 not found")
                            if missing_keys:
                                issues.append(f"Missing keys: {', '.join(missing_keys)}")
                            
                            self.test_results.append({
                                "test": "GET /api/assessment/schema/tier-based",
                                "status": "FAIL",
                                "reason": "; ".join(issues),
                                "body_snippet": response_text[:500]
                            })
                            print(f"❌ FAIL: {'; '.join(issues)}")
                    
                    except json.JSONDecodeError:
                        self.test_results.append({
                            "test": "GET /api/assessment/schema/tier-based",
                            "status": "FAIL",
                            "reason": "Invalid JSON response",
                            "body_snippet": response_text[:500]
                        })
                        print(f"❌ FAIL: Invalid JSON response")
                
                else:
                    self.test_results.append({
                        "test": "GET /api/assessment/schema/tier-based",
                        "status": "FAIL",
                        "reason": f"HTTP {status}",
                        "body_snippet": response_text[:500]
                    })
                    print(f"❌ FAIL: HTTP {status}")
        
        except Exception as e:
            self.test_results.append({
                "test": "GET /api/assessment/schema/tier-based",
                "status": "FAIL",
                "reason": f"Exception: {str(e)}"
            })
            print(f"❌ FAIL: Exception - {str(e)}")
    
    async def test_tier_session_creation(self):
        """Test 2: POST /api/assessment/tier-session"""
        print("\n🔍 Test 2: Tier Session Creation")
        
        if not self.client_token:
            self.test_results.append({
                "test": "POST /api/assessment/tier-session",
                "status": "FAIL",
                "reason": "No client token available"
            })
            return
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test with form data (multipart/form-data)
        form_data = aiohttp.FormData()
        form_data.add_field('area_id', 'area5')
        form_data.add_field('tier_level', '3')
        
        try:
            async with self.session.post(f"{API_BASE}/assessment/tier-session", headers=headers, data=form_data) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        
                        # Verify session returns questions array
                        if "questions" in data and isinstance(data["questions"], list):
                            self.test_results.append({
                                "test": "POST /api/assessment/tier-session",
                                "status": "PASS",
                                "details": f"✅ Session created with {len(data['questions'])} questions"
                            })
                            print(f"✅ PASS: Session created with {len(data['questions'])} questions")
                        else:
                            self.test_results.append({
                                "test": "POST /api/assessment/tier-session",
                                "status": "FAIL",
                                "reason": "No questions array in response",
                                "body_snippet": response_text[:500]
                            })
                            print(f"❌ FAIL: No questions array in response")
                    
                    except json.JSONDecodeError:
                        self.test_results.append({
                            "test": "POST /api/assessment/tier-session",
                            "status": "FAIL",
                            "reason": "Invalid JSON response",
                            "body_snippet": response_text[:500]
                        })
                        print(f"❌ FAIL: Invalid JSON response")
                
                else:
                    self.test_results.append({
                        "test": "POST /api/assessment/tier-session",
                        "status": "FAIL",
                        "reason": f"HTTP {status}",
                        "body_snippet": response_text[:500]
                    })
                    print(f"❌ FAIL: HTTP {status}")
        
        except Exception as e:
            self.test_results.append({
                "test": "POST /api/assessment/tier-session",
                "status": "FAIL",
                "reason": f"Exception: {str(e)}"
            })
            print(f"❌ FAIL: Exception - {str(e)}")
    
    async def test_ai_assistance(self):
        """Test 3: POST /api/knowledge-base/ai-assistance with client token"""
        print("\n🔍 Test 3: AI Assistance")
        
        if not self.client_token:
            self.test_results.append({
                "test": "POST /api/knowledge-base/ai-assistance",
                "status": "FAIL",
                "reason": "No client token available"
            })
            return
        
        headers = {
            "Authorization": f"Bearer {self.client_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "question": "How do I get started with business licensing?",
            "area_id": "area1"
        }
        
        try:
            async with self.session.post(f"{API_BASE}/knowledge-base/ai-assistance", headers=headers, json=payload) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        
                        # Check for text response under 200 words
                        if "response" in data or "answer" in data or "text" in data:
                            response_text_content = data.get("response") or data.get("answer") or data.get("text") or ""
                            word_count = len(response_text_content.split())
                            
                            if word_count > 0 and word_count < 200:
                                self.test_results.append({
                                    "test": "POST /api/knowledge-base/ai-assistance",
                                    "status": "PASS",
                                    "details": f"✅ AI response received ({word_count} words, under 200 limit)"
                                })
                                print(f"✅ PASS: AI response received ({word_count} words)")
                            else:
                                self.test_results.append({
                                    "test": "POST /api/knowledge-base/ai-assistance",
                                    "status": "FAIL",
                                    "reason": f"Response too long ({word_count} words) or empty",
                                    "body_snippet": response_text[:500]
                                })
                                print(f"❌ FAIL: Response too long ({word_count} words) or empty")
                        else:
                            self.test_results.append({
                                "test": "POST /api/knowledge-base/ai-assistance",
                                "status": "FAIL",
                                "reason": "No response/answer/text field in response",
                                "body_snippet": response_text[:500]
                            })
                            print(f"❌ FAIL: No response field found")
                    
                    except json.JSONDecodeError:
                        self.test_results.append({
                            "test": "POST /api/knowledge-base/ai-assistance",
                            "status": "FAIL",
                            "reason": "Invalid JSON response",
                            "body_snippet": response_text[:500]
                        })
                        print(f"❌ FAIL: Invalid JSON response")
                
                else:
                    self.test_results.append({
                        "test": "POST /api/knowledge-base/ai-assistance",
                        "status": "FAIL",
                        "reason": f"HTTP {status}",
                        "body_snippet": response_text[:500]
                    })
                    print(f"❌ FAIL: HTTP {status}")
        
        except Exception as e:
            self.test_results.append({
                "test": "POST /api/knowledge-base/ai-assistance",
                "status": "FAIL",
                "reason": f"Exception: {str(e)}"
            })
            print(f"❌ FAIL: Exception - {str(e)}")
    
    async def test_knowledge_base_content(self):
        """Test 4: GET /api/knowledge-base/{area_id}/content for area1 with client token"""
        print("\n🔍 Test 4: Knowledge Base Content")
        
        if not self.client_token:
            self.test_results.append({
                "test": "GET /api/knowledge-base/area1/content",
                "status": "FAIL",
                "reason": "No client token available"
            })
            return
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        try:
            async with self.session.get(f"{API_BASE}/knowledge-base/area1/content", headers=headers) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        
                        # Check for has_access true and content object with required arrays
                        has_access = data.get("has_access", False)
                        content = data.get("content", {})
                        
                        required_arrays = ["templates", "guides", "checklists"]
                        arrays_present = all(key in content and isinstance(content[key], list) for key in required_arrays)
                        
                        if has_access and arrays_present:
                            self.test_results.append({
                                "test": "GET /api/knowledge-base/area1/content",
                                "status": "PASS",
                                "details": f"✅ has_access=true, content has templates/guides/checklists arrays"
                            })
                            print(f"✅ PASS: has_access=true, content structure valid")
                        else:
                            issues = []
                            if not has_access:
                                issues.append("has_access is false")
                            if not arrays_present:
                                missing = [key for key in required_arrays if key not in content or not isinstance(content[key], list)]
                                issues.append(f"Missing arrays: {', '.join(missing)}")
                            
                            self.test_results.append({
                                "test": "GET /api/knowledge-base/area1/content",
                                "status": "FAIL",
                                "reason": "; ".join(issues),
                                "body_snippet": response_text[:500]
                            })
                            print(f"❌ FAIL: {'; '.join(issues)}")
                    
                    except json.JSONDecodeError:
                        self.test_results.append({
                            "test": "GET /api/knowledge-base/area1/content",
                            "status": "FAIL",
                            "reason": "Invalid JSON response",
                            "body_snippet": response_text[:500]
                        })
                        print(f"❌ FAIL: Invalid JSON response")
                
                else:
                    self.test_results.append({
                        "test": "GET /api/knowledge-base/area1/content",
                        "status": "FAIL",
                        "reason": f"HTTP {status}",
                        "body_snippet": response_text[:500]
                    })
                    print(f"❌ FAIL: HTTP {status}")
        
        except Exception as e:
            self.test_results.append({
                "test": "GET /api/knowledge-base/area1/content",
                "status": "FAIL",
                "reason": f"Exception: {str(e)}"
            })
            print(f"❌ FAIL: Exception - {str(e)}")
    
    async def test_prometheus_metrics(self):
        """Test 5: GET /api/system/prometheus-metrics"""
        print("\n🔍 Test 5: Prometheus Metrics")
        
        try:
            async with self.session.get(f"{API_BASE}/system/prometheus-metrics") as response:
                status = response.status
                response_text = await response.text()
                
                if status == 200:
                    # Check for '# HELP' text indicating Prometheus format
                    if "# HELP" in response_text:
                        self.test_results.append({
                            "test": "GET /api/system/prometheus-metrics",
                            "status": "PASS",
                            "details": f"✅ Prometheus metrics returned with '# HELP' text"
                        })
                        print(f"✅ PASS: Prometheus metrics format detected")
                    else:
                        self.test_results.append({
                            "test": "GET /api/system/prometheus-metrics",
                            "status": "FAIL",
                            "reason": "Response doesn't contain '# HELP' text",
                            "body_snippet": response_text[:500]
                        })
                        print(f"❌ FAIL: No '# HELP' text found")
                
                else:
                    self.test_results.append({
                        "test": "GET /api/system/prometheus-metrics",
                        "status": "FAIL",
                        "reason": f"HTTP {status}",
                        "body_snippet": response_text[:500]
                    })
                    print(f"❌ FAIL: HTTP {status}")
        
        except Exception as e:
            self.test_results.append({
                "test": "GET /api/system/prometheus-metrics",
                "status": "FAIL",
                "reason": f"Exception: {str(e)}"
            })
            print(f"❌ FAIL: Exception - {str(e)}")
    
    async def run_all_tests(self):
        """Run all focused smoke tests"""
        print("🎯 FOCUSED BACKEND SMOKE RETEST - PREVIOUSLY FAILING ITEMS")
        print("=" * 60)
        
        # Setup session and authenticate
        if not await self.setup_session():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run the 5 specific tests
        await self.test_assessment_schema_tier_based()
        await self.test_tier_session_creation()
        await self.test_ai_assistance()
        await self.test_knowledge_base_content()
        await self.test_prometheus_metrics()
        
        # Generate summary
        self.generate_summary()
        
        # Cleanup
        if self.session:
            await self.session.close()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED BACKEND SMOKE RETEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0.0%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{i}. {status_icon} {result['test']}: {result['status']}")
            
            if result["status"] == "PASS" and "details" in result:
                print(f"   {result['details']}")
            elif result["status"] == "FAIL":
                print(f"   Reason: {result['reason']}")
                if "body_snippet" in result and result["body_snippet"]:
                    print(f"   Body: {result['body_snippet'][:200]}...")
        
        print("\n" + "=" * 60)

async def main():
    """Main test execution"""
    tester = BackendSmokeRetest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())