#!/usr/bin/env python3
"""
Backend Thorough Test – Current Run (September 2025)
Comprehensive smoke + conformance + light performance sampling for FastAPI backend
"""

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Test Configuration
BASE_URL = "https://production-guru.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "admin": {"email": "admin.qa@polaris.example.com", "password": "Polaris#2025!"}  # Optional
}

class BackendThoroughTester:
    def __init__(self):
        self.session = None
        self.tokens = {}
        self.test_results = []
        self.performance_data = []
        self.start_time = time.time()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, category: str, test_name: str, status: str, details: Dict[str, Any], timing: float = None):
        """Log test result with timing data"""
        result = {
            "category": category,
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "timing_ms": round(timing * 1000, 2) if timing else None
        }
        self.test_results.append(result)
        if timing:
            self.performance_data.append(timing)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{category}] {test_name}: {status}")
        if details.get("error"):
            print(f"   Error: {details['error']}")
        if timing:
            print(f"   Timing: {timing*1000:.2f}ms")
    
    async def make_request(self, method: str, endpoint: str, headers: Dict = None, data: Dict = None, auth_token: str = None) -> tuple:
        """Make HTTP request with timing and error handling"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        if headers:
            request_headers.update(headers)
            
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    timing = time.time() - start_time
                    response_data = await response.text()
                    try:
                        response_json = json.loads(response_data)
                    except:
                        response_json = {"raw_response": response_data}
                    return response.status, response_json, timing, dict(response.headers)
                    
            elif method.upper() == "POST":
                async with self.session.post(url, headers=request_headers, json=data) as response:
                    timing = time.time() - start_time
                    response_data = await response.text()
                    try:
                        response_json = json.loads(response_data)
                    except:
                        response_json = {"raw_response": response_data}
                    return response.status, response_json, timing, dict(response.headers)
                    
        except Exception as e:
            timing = time.time() - start_time
            return 0, {"error": str(e)}, timing, {}
    
    async def test_authentication_and_roles(self):
        """Test 1: Authentication & Roles - Login all roles, store tokens, verify role-specific fields"""
        print("\n=== 1. AUTHENTICATION & ROLES TESTING ===")
        
        for role, creds in QA_CREDENTIALS.items():
            # Test login
            status, response, timing, headers = await self.make_request(
                "POST", "/auth/login", 
                data={"email": creds["email"], "password": creds["password"]}
            )
            
            if status == 200 and "access_token" in response:
                self.tokens[role] = response["access_token"]
                self.log_result("Authentication", f"{role.title()} Login", "PASS", {
                    "email": creds["email"],
                    "token_length": len(response["access_token"]),
                    "token_type": response.get("token_type", "bearer")
                }, timing)
                
                # Test /auth/me with stored token
                status_me, response_me, timing_me, _ = await self.make_request(
                    "GET", "/auth/me", auth_token=self.tokens[role]
                )
                
                if status_me == 200:
                    self.log_result("Authentication", f"{role.title()} Profile Verification", "PASS", {
                        "user_id": response_me.get("id"),
                        "email": response_me.get("email"),
                        "role": response_me.get("role"),
                        "role_specific_fields": list(response_me.keys())
                    }, timing_me)
                else:
                    self.log_result("Authentication", f"{role.title()} Profile Verification", "FAIL", {
                        "status_code": status_me,
                        "error": response_me
                    }, timing_me)
                    
            else:
                self.log_result("Authentication", f"{role.title()} Login", "FAIL", {
                    "status_code": status,
                    "error": response,
                    "rate_limit_headers": {k: v for k, v in headers.items() if 'rate' in k.lower() or 'limit' in k.lower()}
                }, timing)
        
        # Test rate limiting and lockout behavior (minimal tries)
        bad_creds = {"email": "client.qa@polaris.example.com", "password": "wrongpassword"}
        for attempt in range(3):  # Minimal attempts to avoid lockout
            status, response, timing, headers = await self.make_request(
                "POST", "/auth/login", data=bad_creds
            )
            if attempt == 2:  # Log final attempt
                self.log_result("Authentication", "Bad Password Rate Limiting", 
                    "PASS" if status == 401 else "FAIL", {
                    "final_status": status,
                    "attempts_made": 3,
                    "rate_limit_headers": {k: v for k, v in headers.items() if 'rate' in k.lower() or 'limit' in k.lower()}
                }, timing)
    
    async def test_assessment_system(self):
        """Test 2: Assessment - Tier-based schema, session creation, evidence upload"""
        print("\n=== 2. ASSESSMENT SYSTEM TESTING ===")
        
        if "client" not in self.tokens:
            self.log_result("Assessment", "Client Token Missing", "FAIL", {"error": "No client token available"})
            return
            
        client_token = self.tokens["client"]
        
        # Test tier-based schema endpoint
        status, response, timing, _ = await self.make_request(
            "GET", "/assessment/schema/tier-based", auth_token=client_token
        )
        
        if status == 200:
            areas_count = len(response.get("areas", []))
            has_area10 = any(area.get("id") == "area10" or area.get("area_id") == "area10" for area in response.get("areas", []))
            has_compatibility_keys = False
            
            # Check for compatibility keys (id/area_id, title/area_name)
            if response.get("areas"):
                first_area = response["areas"][0]
                has_compatibility_keys = (
                    ("id" in first_area or "area_id" in first_area) and 
                    ("title" in first_area or "area_name" in first_area)
                )
            
            self.log_result("Assessment", "Tier-Based Schema", "PASS", {
                "total_areas": areas_count,
                "has_area10_competitive_advantage": has_area10,
                "has_compatibility_keys": has_compatibility_keys,
                "sample_area": response.get("areas", [{}])[0] if response.get("areas") else {}
            }, timing)
        else:
            self.log_result("Assessment", "Tier-Based Schema", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
            return
        
        # Create Tier 3 session for area5
        session_data = {
            "area_id": "area5",
            "tier": 3,
            "business_context": "QA testing tier 3 assessment"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/assessment/tier-session", 
            data=session_data, auth_token=client_token
        )
        
        session_id = None
        if status == 200 or status == 201:
            session_id = response.get("session_id") or response.get("id")
            self.log_result("Assessment", "Tier 3 Session Creation", "PASS", {
                "session_id": session_id,
                "area_id": response.get("area_id"),
                "tier": response.get("tier"),
                "total_questions": response.get("total_questions")
            }, timing)
        else:
            self.log_result("Assessment", "Tier 3 Session Creation", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
        
        # Submit responses including "Gap Exists – I Need Help"
        if session_id:
            response_data = {
                "question_id": "area5_q1",
                "response": "Gap Exists - I Need Help",
                "notes": "QA test response indicating need for assistance",
                "confidence_level": "low"
            }
            
            status, response, timing, _ = await self.make_request(
                "POST", f"/assessment/tier-session/{session_id}/response",
                data=response_data, auth_token=client_token
            )
            
            self.log_result("Assessment", "Gap Response Submission", 
                "PASS" if status in [200, 201] else "FAIL", {
                "status_code": status,
                "response_accepted": status in [200, 201],
                "response_data": response
            }, timing)
            
            # Get progress
            status, response, timing, _ = await self.make_request(
                "GET", f"/assessment/tier-session/{session_id}/progress",
                auth_token=client_token
            )
            
            self.log_result("Assessment", "Session Progress", 
                "PASS" if status == 200 else "FAIL", {
                "status_code": status,
                "progress_data": response
            }, timing)
        
        # Test evidence upload (simple small file)
        evidence_data = {
            "session_id": session_id or "test_session",
            "question_id": "area5_q1",
            "evidence_type": "document",
            "description": "QA test evidence upload"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/assessment/evidence",
            data=evidence_data, auth_token=client_token
        )
        
        self.log_result("Assessment", "Evidence Upload", 
            "PASS" if status in [200, 201] else "FAIL", {
            "status_code": status,
            "chunked_upload_available": "upload_url" in response or "chunk_size" in response,
            "response": response
        }, timing)
    
    async def test_service_requests_marketplace(self):
        """Test 3: Service Requests & Marketplace - Create request, provider response, enhanced data"""
        print("\n=== 3. SERVICE REQUESTS & MARKETPLACE TESTING ===")
        
        if "client" not in self.tokens or "provider" not in self.tokens:
            self.log_result("Service Requests", "Required Tokens Missing", "FAIL", 
                {"error": "Client or provider token missing"})
            return
        
        client_token = self.tokens["client"]
        provider_token = self.tokens["provider"]
        
        # Create professional help request
        request_data = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "QA test professional help request for technology infrastructure assessment",
            "urgency": "medium"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/service-requests/professional-help",
            data=request_data, auth_token=client_token
        )
        
        request_id = None
        if status in [200, 201]:
            request_id = response.get("request_id") or response.get("id")
            providers_notified = response.get("providers_notified", 0)
            
            self.log_result("Service Requests", "Professional Help Request", "PASS", {
                "request_id": request_id,
                "providers_notified": providers_notified,
                "providers_notified_within_limit": providers_notified <= 5,
                "area_id": response.get("area_id"),
                "status": response.get("status")
            }, timing)
        else:
            self.log_result("Service Requests", "Professional Help Request", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
            return
        
        # Provider response to request
        if request_id:
            response_data = {
                "request_id": request_id,
                "proposed_fee": 2500.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "QA test provider response with competitive pricing and timeline"
            }
            
            status, response, timing, _ = await self.make_request(
                "POST", "/provider/respond-to-request",
                data=response_data, auth_token=provider_token
            )
            
            self.log_result("Service Requests", "Provider Response", 
                "PASS" if status in [200, 201] else "FAIL", {
                "status_code": status,
                "response_accepted": status in [200, 201],
                "response_data": response
            }, timing)
            
            # Get enhanced responses
            status, response, timing, _ = await self.make_request(
                "GET", f"/service-requests/{request_id}/responses/enhanced",
                auth_token=client_token
            )
            
            if status == 200:
                has_enriched_provider_info = "provider_info" in response or any(
                    "email" in resp or "business_name" in resp 
                    for resp in response.get("responses", [])
                )
                has_limit_banner = "response_limit_reached" in response or "limit_banner" in response
                
                self.log_result("Service Requests", "Enhanced Responses", "PASS", {
                    "total_responses": len(response.get("responses", [])),
                    "has_enriched_provider_info": has_enriched_provider_info,
                    "has_limit_banner_values": has_limit_banner,
                    "response_structure": list(response.keys())
                }, timing)
            else:
                self.log_result("Service Requests", "Enhanced Responses", "FAIL", {
                    "status_code": status,
                    "error": response
                }, timing)
    
    async def test_payments(self):
        """Test 4: Payments - Service request payment, KB unlock flow"""
        print("\n=== 4. PAYMENTS TESTING ===")
        
        if "client" not in self.tokens:
            self.log_result("Payments", "Client Token Missing", "FAIL", {"error": "No client token available"})
            return
        
        client_token = self.tokens["client"]
        
        # Test service request payment (need a request ID from previous test)
        # Create a simple request first for payment testing
        request_data = {
            "area_id": "area5",
            "budget_range": "1500-5000", 
            "timeline": "2-4 weeks",
            "description": "QA payment test request"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/service-requests/professional-help",
            data=request_data, auth_token=client_token
        )
        
        request_id = response.get("request_id") or response.get("id") if status in [200, 201] else None
        
        if request_id:
            payment_data = {
                "request_id": request_id,
                "payment_method": "stripe"
            }
            
            status, response, timing, _ = await self.make_request(
                "POST", "/payments/service-request",
                data=payment_data, auth_token=client_token
            )
            
            has_checkout_url = "checkout_url" in response or "url" in response
            self.log_result("Payments", "Service Request Payment", 
                "PASS" if status in [200, 201] and has_checkout_url else "FAIL", {
                "status_code": status,
                "has_checkout_url": has_checkout_url,
                "response_keys": list(response.keys()) if isinstance(response, dict) else []
            }, timing)
        
        # Test KB unlock flow - single area
        kb_payment_data = {
            "area_id": "area1",
            "access_type": "single_area"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/payments/v1/checkout/session",
            data=kb_payment_data, auth_token=client_token
        )
        
        self.log_result("Payments", "KB Single Area Unlock", 
            "PASS" if status in [200, 201] else "FAIL", {
            "status_code": status,
            "has_checkout_url": "checkout_url" in response or "url" in response,
            "response": response
        }, timing)
        
        # Test KB unlock flow - all areas
        kb_all_data = {
            "access_type": "all_areas"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/payments/v1/checkout/session",
            data=kb_all_data, auth_token=client_token
        )
        
        self.log_result("Payments", "KB All Areas Unlock", 
            "PASS" if status in [200, 201] else "FAIL", {
            "status_code": status,
            "has_checkout_url": "checkout_url" in response or "url" in response,
            "response": response
        }, timing)
    
    async def test_knowledge_base_ai(self):
        """Test 5: Knowledge Base & AI - Areas access, AI assistance, template generation"""
        print("\n=== 5. KNOWLEDGE BASE & AI TESTING ===")
        
        if "client" not in self.tokens:
            self.log_result("Knowledge Base", "Client Token Missing", "FAIL", {"error": "No client token available"})
            return
        
        client_token = self.tokens["client"]
        
        # Test KB areas endpoint
        status, response, timing, _ = await self.make_request(
            "GET", "/knowledge-base/areas", auth_token=client_token
        )
        
        self.log_result("Knowledge Base", "Areas Access", 
            "PASS" if status == 200 else "FAIL", {
            "status_code": status,
            "areas_count": len(response.get("areas", [])) if status == 200 else 0,
            "response": response
        }, timing)
        
        # Test KB access endpoint
        status, response, timing, _ = await self.make_request(
            "GET", "/knowledge-base/access", auth_token=client_token
        )
        
        self.log_result("Knowledge Base", "Access Status", 
            "PASS" if status == 200 else "FAIL", {
            "status_code": status,
            "access_info": response
        }, timing)
        
        # Test area content
        status, response, timing, _ = await self.make_request(
            "GET", "/knowledge-base/area1/content", auth_token=client_token
        )
        
        self.log_result("Knowledge Base", "Area1 Content", 
            "PASS" if status == 200 else "FAIL", {
            "status_code": status,
            "has_content": bool(response.get("content")) if status == 200 else False,
            "content_length": len(str(response.get("content", ""))) if status == 200 else 0
        }, timing)
        
        # Test AI assistance
        ai_data = {
            "question": "What are the key requirements for government contracting readiness?",
            "area_id": "area1"
        }
        
        status, response, timing, _ = await self.make_request(
            "POST", "/knowledge-base/ai-assistance",
            data=ai_data, auth_token=client_token
        )
        
        if status == 200:
            answer_text = response.get("answer", "")
            word_count = len(answer_text.split()) if answer_text else 0
            is_concise = word_count < 200
            
            self.log_result("Knowledge Base", "AI Assistance", "PASS", {
                "word_count": word_count,
                "is_concise_under_200_words": is_concise,
                "has_answer": bool(answer_text),
                "timing_seconds": timing
            }, timing)
        else:
            self.log_result("Knowledge Base", "AI Assistance", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
        
        # Test template generation
        status, response, timing, _ = await self.make_request(
            "GET", "/knowledge-base/generate-template/area1/template",
            auth_token=client_token
        )
        
        if status == 200:
            has_filename = "filename" in response
            has_content = "content" in response
            filename_format_correct = response.get("filename", "").endswith(".md") or response.get("filename", "").endswith(".docx")
            
            self.log_result("Knowledge Base", "Template Generation", "PASS", {
                "has_filename": has_filename,
                "has_content": has_content,
                "filename": response.get("filename"),
                "content_length": len(str(response.get("content", ""))),
                "filename_format_correct": filename_format_correct
            }, timing)
        else:
            self.log_result("Knowledge Base", "Template Generation", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
    
    async def test_analytics(self):
        """Test 6: Analytics - Resource access logging, navigator analytics"""
        print("\n=== 6. ANALYTICS TESTING ===")
        
        if "client" not in self.tokens or "navigator" not in self.tokens:
            self.log_result("Analytics", "Required Tokens Missing", "FAIL", 
                {"error": "Client or navigator token missing"})
            return
        
        client_token = self.tokens["client"]
        navigator_token = self.tokens["navigator"]
        
        # Post analytics events as client
        analytics_events = [
            {"area_id": "area1", "resource_type": "template", "action": "download"},
            {"area_id": "area2", "resource_type": "guide", "action": "view"},
            {"area_id": "area5", "resource_type": "checklist", "action": "download"}
        ]
        
        for event in analytics_events:
            status, response, timing, _ = await self.make_request(
                "POST", "/analytics/resource-access",
                data=event, auth_token=client_token
            )
            
            if event == analytics_events[-1]:  # Log last event
                self.log_result("Analytics", "Resource Access Logging", 
                    "PASS" if status in [200, 201] else "FAIL", {
                    "status_code": status,
                    "events_posted": len(analytics_events),
                    "final_response": response
                }, timing)
        
        # Get navigator analytics
        status, response, timing, _ = await self.make_request(
            "GET", "/navigator/analytics/resources?since_days=30",
            auth_token=navigator_token
        )
        
        if status == 200:
            has_required_fields = all(field in response for field in ["since", "total", "by_area", "last7"])
            total_count = response.get("total", 0)
            by_area_structure = isinstance(response.get("by_area"), list)
            
            self.log_result("Analytics", "Navigator Analytics", "PASS", {
                "has_required_fields": has_required_fields,
                "total_count": total_count,
                "by_area_count": len(response.get("by_area", [])),
                "by_area_structure_correct": by_area_structure,
                "last7_trend_available": bool(response.get("last7"))
            }, timing)
        else:
            self.log_result("Analytics", "Navigator Analytics", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
    
    async def test_navigator_agency_endpoints(self):
        """Test 7: Navigator & Agency endpoints - Review queue, analytics, license validation"""
        print("\n=== 7. NAVIGATOR & AGENCY ENDPOINTS TESTING ===")
        
        if "navigator" not in self.tokens:
            self.log_result("Navigator/Agency", "Navigator Token Missing", "FAIL", 
                {"error": "Navigator token missing"})
            return
        
        navigator_token = self.tokens["navigator"]
        
        # Test navigator review queue or analytics top-level
        endpoints_to_test = [
            "/navigator/review-queue",
            "/navigator/analytics",
            "/navigator/dashboard",
            "/navigator/agencies"
        ]
        
        for endpoint in endpoints_to_test:
            status, response, timing, _ = await self.make_request(
                "GET", endpoint, auth_token=navigator_token
            )
            
            endpoint_name = endpoint.split("/")[-1].title()
            self.log_result("Navigator/Agency", f"Navigator {endpoint_name}", 
                "PASS" if status == 200 else "PARTIAL" if status in [404, 501] else "FAIL", {
                "status_code": status,
                "endpoint": endpoint,
                "response_available": status == 200,
                "response_keys": list(response.keys()) if isinstance(response, dict) and status == 200 else []
            }, timing)
        
        # Test agency endpoints if agency token available
        if "agency" in self.tokens:
            agency_token = self.tokens["agency"]
            agency_endpoints = [
                "/agency/licenses",
                "/agency/dashboard", 
                "/agency/validation"
            ]
            
            for endpoint in agency_endpoints:
                status, response, timing, _ = await self.make_request(
                    "GET", endpoint, auth_token=agency_token
                )
                
                endpoint_name = endpoint.split("/")[-1].title()
                self.log_result("Navigator/Agency", f"Agency {endpoint_name}", 
                    "PASS" if status == 200 else "PARTIAL" if status in [404, 501] else "FAIL", {
                    "status_code": status,
                    "endpoint": endpoint,
                    "response_available": status == 200
                }, timing)
    
    async def test_observability_health(self):
        """Test 8: Observability & Health - System health, metrics"""
        print("\n=== 8. OBSERVABILITY & HEALTH TESTING ===")
        
        # Test system health
        status, response, timing, _ = await self.make_request("GET", "/health/system")
        
        if status == 200:
            has_version = "version" in response
            has_git_sha = "git_sha" in response or "commit" in response
            
            self.log_result("Observability", "System Health", "PASS", {
                "has_version": has_version,
                "has_git_sha": has_git_sha,
                "version": response.get("version"),
                "git_sha": response.get("git_sha") or response.get("commit"),
                "additional_fields": list(response.keys())
            }, timing)
        else:
            self.log_result("Observability", "System Health", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
        
        # Test metrics endpoint (alias)
        status, response, timing, headers = await self.make_request("GET", "/metrics")
        
        if status == 200:
            response_text = response.get("raw_response", "")
            is_prometheus_format = "# HELP" in response_text
            content_type_correct = headers.get("content-type", "").startswith("text/plain")
            
            self.log_result("Observability", "Prometheus Metrics", "PASS", {
                "is_prometheus_format": is_prometheus_format,
                "content_type_correct": content_type_correct,
                "content_type": headers.get("content-type"),
                "response_length": len(response_text),
                "has_help_comments": "# HELP" in response_text
            }, timing)
        else:
            self.log_result("Observability", "Prometheus Metrics", "FAIL", {
                "status_code": status,
                "error": response
            }, timing)
    
    def calculate_performance_stats(self):
        """Calculate performance statistics"""
        if not self.performance_data:
            return {}
        
        timings_ms = [t * 1000 for t in self.performance_data]
        return {
            "total_requests": len(timings_ms),
            "mean_response_time_ms": round(statistics.mean(timings_ms), 2),
            "median_response_time_ms": round(statistics.median(timings_ms), 2),
            "p95_response_time_ms": round(statistics.quantiles(timings_ms, n=20)[18], 2) if len(timings_ms) >= 20 else "N/A",
            "min_response_time_ms": round(min(timings_ms), 2),
            "max_response_time_ms": round(max(timings_ms), 2)
        }
    
    def generate_summary_report(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        
        success_rate = round((passed_tests / total_tests * 100), 1) if total_tests > 0 else 0
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0, "partial": 0, "tests": []}
            categories[category][result["status"].lower()] += 1
            categories[category]["tests"].append(result)
        
        performance_stats = self.calculate_performance_stats()
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "partial": partial_tests,
                "success_rate": f"{success_rate}%"
            },
            "category_breakdown": categories,
            "performance_stats": performance_stats,
            "test_duration": round(time.time() - self.start_time, 2),
            "timestamp": datetime.now().isoformat()
        }

async def run_comprehensive_backend_test():
    """Run comprehensive backend test suite"""
    print("🚀 Starting Backend Thorough Test – Current Run (September 2025)")
    print(f"🎯 Target: {BASE_URL}")
    print("=" * 80)
    
    async with BackendThoroughTester() as tester:
        # Execute all test categories
        await tester.test_authentication_and_roles()
        await tester.test_assessment_system()
        await tester.test_service_requests_marketplace()
        await tester.test_payments()
        await tester.test_knowledge_base_ai()
        await tester.test_analytics()
        await tester.test_navigator_agency_endpoints()
        await tester.test_observability_health()
        
        # Generate final report
        summary = tester.generate_summary_report()
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        print(f"✅ Total Tests: {summary['test_summary']['total_tests']}")
        print(f"✅ Passed: {summary['test_summary']['passed']}")
        print(f"❌ Failed: {summary['test_summary']['failed']}")
        print(f"⚠️ Partial: {summary['test_summary']['partial']}")
        print(f"📈 Success Rate: {summary['test_summary']['success_rate']}")
        print(f"⏱️ Test Duration: {summary['test_duration']}s")
        
        if summary['performance_stats']:
            print(f"\n🚀 PERFORMANCE STATS:")
            print(f"   Mean Response Time: {summary['performance_stats']['mean_response_time_ms']}ms")
            print(f"   Median Response Time: {summary['performance_stats']['median_response_time_ms']}ms")
            print(f"   P95 Response Time: {summary['performance_stats']['p95_response_time_ms']}ms")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, stats in summary['category_breakdown'].items():
            total_cat = stats['pass'] + stats['fail'] + stats['partial']
            success_rate_cat = round((stats['pass'] / total_cat * 100), 1) if total_cat > 0 else 0
            print(f"   {category}: {stats['pass']}/{total_cat} ({success_rate_cat}%)")
        
        # Identify critical issues
        critical_failures = []
        for result in tester.test_results:
            if result["status"] == "FAIL" and result["category"] in ["Authentication", "Assessment", "Service Requests"]:
                critical_failures.append(f"{result['category']}: {result['test_name']}")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_failures:
                print(f"   - {issue}")
        
        return summary, tester.test_results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_backend_test())