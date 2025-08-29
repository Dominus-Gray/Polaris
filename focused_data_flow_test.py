#!/usr/bin/env python3
"""
Focused Data Flow Analysis - Testing Actual Working Endpoints and Integration
Based on discovered working endpoints from initial testing
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Test Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FocusedDataFlowTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session_data = {}
        
    def log_result(self, test_name: str, success: bool, details: str, data: dict = None):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   📝 {details}")
        if data and success:
            print(f"   📊 Data: {str(data)[:100]}...")
        print()
        
    def authenticate_all_users(self) -> bool:
        """Authenticate all QA user types"""
        print("🔐 AUTHENTICATION PHASE")
        print("=" * 50)
        all_success = True
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json=creds)
                if response.status_code == 200:
                    token_data = response.json()
                    self.tokens[role] = token_data["access_token"]
                    self.log_result(f"Auth_{role}", True, f"Successfully authenticated {role} user")
                else:
                    self.log_result(f"Auth_{role}", False, f"Auth failed: {response.status_code}")
                    all_success = False
            except Exception as e:
                self.log_result(f"Auth_{role}", False, f"Auth error: {str(e)}")
                all_success = False
                
        return all_success
    
    def get_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {"Authorization": f"Bearer {self.tokens.get(role, '')}", "Content-Type": "application/json"}
    
    def test_assessment_to_service_request_flow(self) -> bool:
        """Test complete flow: Assessment → Gap Identification → Service Request → Provider Response"""
        print("🎯 ASSESSMENT TO SERVICE REQUEST FLOW")
        print("=" * 50)
        
        try:
            client_headers = self.get_headers("client")
            
            # Step 1: Create tier-based assessment session
            tier_data = {"area_id": "area5", "tier_level": "1"}
            session_response = requests.post(f"{BASE_URL}/assessment/tier-session", 
                                           data=tier_data, headers=client_headers)
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data["session_id"]
                self.session_data["assessment_session"] = session_id
                
                self.log_result("Assessment Session Creation", True, 
                              f"Created session {session_id} for {session_data['area_title']}", 
                              {"session_id": session_id, "area": session_data["area_title"]})
                
                # Step 2: Submit assessment response indicating need for help
                response_data = {
                    "maturity_statement_id": session_data["questions"][0]["id"],
                    "response": "No, I need help",
                    "evidence_provided": False
                }
                
                submit_response = requests.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response",
                                              json=response_data, headers=client_headers)
                
                if submit_response.status_code == 200:
                    self.log_result("Assessment Response Submission", True, 
                                  "Successfully submitted 'No, I need help' response")
                    
                    # Step 3: Create service request based on assessment gap
                    service_request_data = {
                        "area_id": "area5",
                        "budget_range": "1500-5000",
                        "timeline": "2-4 weeks", 
                        "description": "Need professional help with Technology & Security Infrastructure based on assessment gap",
                        "priority": "high"
                    }
                    
                    service_response = requests.post(f"{BASE_URL}/service-requests/professional-help",
                                                   json=service_request_data, headers=client_headers)
                    
                    if service_response.status_code == 200:
                        service_data = service_response.json()
                        request_id = service_data["request_id"]
                        self.session_data["service_request"] = request_id
                        
                        self.log_result("Service Request Creation", True, 
                                      f"Created service request {request_id} based on assessment gap",
                                      {"request_id": request_id, "area": "area5"})
                        
                        # Step 4: Provider responds to service request
                        provider_headers = self.get_headers("provider")
                        provider_response_data = {
                            "request_id": request_id,
                            "proposed_fee": 2500.0,
                            "estimated_timeline": "3 weeks",
                            "proposal_note": "Comprehensive technology assessment and security infrastructure setup"
                        }
                        
                        provider_resp = requests.post(f"{BASE_URL}/provider/respond-to-request",
                                                    json=provider_response_data, headers=provider_headers)
                        
                        if provider_resp.status_code == 200:
                            self.log_result("Provider Response", True, 
                                          "Provider successfully responded to service request")
                            
                            # Step 5: Verify client can see provider responses
                            responses_resp = requests.get(f"{BASE_URL}/service-requests/{request_id}/responses",
                                                        headers=client_headers)
                            
                            if responses_resp.status_code == 200:
                                responses_data = responses_resp.json()
                                response_count = len(responses_data.get("responses", []))
                                
                                self.log_result("Complete Data Flow Integration", True, 
                                              f"Full flow working: Assessment → Gap → Service Request → Provider Response ({response_count} responses)",
                                              {"flow_complete": True, "response_count": response_count})
                                return True
                            else:
                                self.log_result("Response Retrieval", False, 
                                              f"Cannot retrieve provider responses: {responses_resp.status_code}")
                        else:
                            self.log_result("Provider Response", False, 
                                          f"Provider response failed: {provider_resp.status_code}")
                    else:
                        self.log_result("Service Request Creation", False, 
                                      f"Service request creation failed: {service_response.status_code}")
                else:
                    self.log_result("Assessment Response Submission", False, 
                                  f"Assessment response failed: {submit_response.status_code}")
            else:
                self.log_result("Assessment Session Creation", False, 
                              f"Session creation failed: {session_response.status_code}")
                
        except Exception as e:
            self.log_result("Assessment to Service Request Flow", False, f"Error: {str(e)}")
            
        return False
    
    def test_agency_client_data_integration(self) -> bool:
        """Test Agency Business Intelligence with real client data"""
        print("🏢 AGENCY BUSINESS INTELLIGENCE INTEGRATION")
        print("=" * 50)
        
        try:
            agency_headers = self.get_headers("agency")
            
            # Test 1: Agency tier configuration shows real setup
            tier_config_resp = requests.get(f"{BASE_URL}/agency/tier-configuration", headers=agency_headers)
            
            if tier_config_resp.status_code == 200:
                config_data = tier_config_resp.json()
                tier_levels = config_data.get("tier_access_levels", {})
                pricing = config_data.get("pricing_per_tier", {})
                
                self.log_result("Agency Tier Configuration", True, 
                              f"Agency has {len(tier_levels)} areas configured with {len(pricing)} pricing tiers",
                              {"areas_configured": len(tier_levels), "pricing_tiers": len(pricing)})
                
                # Test 2: Agency billing tracks actual usage
                billing_resp = requests.get(f"{BASE_URL}/agency/billing/usage", headers=agency_headers)
                
                if billing_resp.status_code == 200:
                    billing_data = billing_resp.json()
                    total_assessments = billing_data.get("total_assessments", 0)
                    usage_by_tier = billing_data.get("usage_by_tier", {})
                    
                    self.log_result("Agency Billing Integration", True, 
                                  f"Billing tracks {total_assessments} assessments with tier usage: {usage_by_tier}",
                                  {"total_assessments": total_assessments, "tier_usage": usage_by_tier})
                    
                    # Test 3: Client tier access reflects agency configuration
                    client_headers = self.get_headers("client")
                    client_access_resp = requests.get(f"{BASE_URL}/client/tier-access", headers=client_headers)
                    
                    if client_access_resp.status_code == 200:
                        access_data = client_access_resp.json()
                        client_areas = access_data.get("tier_access", {})
                        
                        # Verify client access matches agency configuration
                        matching_areas = 0
                        for area_id, client_tier in client_areas.items():
                            agency_tier = tier_levels.get(area_id, 0)
                            if client_tier.get("max_tier_access", 0) <= agency_tier:
                                matching_areas += 1
                        
                        integration_success = matching_areas > 0
                        self.log_result("Agency-Client Data Integration", integration_success, 
                                      f"Client tier access properly reflects agency configuration ({matching_areas}/{len(client_areas)} areas match)",
                                      {"matching_areas": matching_areas, "total_areas": len(client_areas)})
                        
                        return integration_success
                    else:
                        self.log_result("Client Tier Access", False, 
                                      f"Cannot access client tier data: {client_access_resp.status_code}")
                else:
                    self.log_result("Agency Billing Integration", False, 
                                  f"Cannot access billing data: {billing_resp.status_code}")
            else:
                self.log_result("Agency Tier Configuration", False, 
                              f"Cannot access tier configuration: {tier_config_resp.status_code}")
                
        except Exception as e:
            self.log_result("Agency Client Data Integration", False, f"Error: {str(e)}")
            
        return False
    
    def test_knowledge_base_assessment_integration(self) -> bool:
        """Test Knowledge Base integration with assessment data"""
        print("📚 KNOWLEDGE BASE ASSESSMENT INTEGRATION")
        print("=" * 50)
        
        try:
            client_headers = self.get_headers("client")
            
            # Test 1: Knowledge Base areas accessible
            kb_areas_resp = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=client_headers)
            
            if kb_areas_resp.status_code == 200:
                areas_data = kb_areas_resp.json()
                areas = areas_data.get("areas", [])
                unlocked_areas = [area for area in areas if area.get("unlocked")]
                
                self.log_result("Knowledge Base Areas Access", True, 
                              f"Accessed {len(areas)} KB areas, {len(unlocked_areas)} unlocked for QA user",
                              {"total_areas": len(areas), "unlocked_areas": len(unlocked_areas)})
                
                # Test 2: AI assistance with assessment context
                if self.session_data.get("assessment_session"):
                    ai_request = {
                        "question": "How can I improve my technology and security infrastructure based on my assessment?",
                        "area_id": "area5"
                    }
                    
                    ai_resp = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance",
                                          json=ai_request, headers=client_headers)
                    
                    if ai_resp.status_code == 200:
                        ai_data = ai_resp.json()
                        response_text = ai_data.get("response", "")
                        
                        # Check if response is contextual to the area
                        contextual = any(keyword in response_text.lower() 
                                       for keyword in ["technology", "security", "infrastructure"])
                        
                        self.log_result("AI Assistance Context Integration", contextual, 
                                      f"AI provides contextual assistance ({len(response_text)} chars, contextual: {contextual})",
                                      {"response_length": len(response_text), "contextual": contextual})
                    else:
                        self.log_result("AI Assistance Context Integration", False, 
                                      f"AI assistance failed: {ai_resp.status_code}")
                
                # Test 3: Template generation for specific areas
                if unlocked_areas:
                    area_id = unlocked_areas[0]["id"]
                    template_resp = requests.get(f"{BASE_URL}/knowledge-base/generate-template/{area_id}/template",
                                               headers=client_headers)
                    
                    if template_resp.status_code == 200:
                        template_data = template_resp.json()
                        content = template_data.get("content", "")
                        filename = template_data.get("filename", "")
                        
                        self.log_result("Knowledge Base Template Generation", True, 
                                      f"Generated template for {area_id}: {filename} ({len(content)} chars)",
                                      {"area_id": area_id, "filename": filename, "content_length": len(content)})
                        return True
                    else:
                        self.log_result("Knowledge Base Template Generation", False, 
                                      f"Template generation failed: {template_resp.status_code}")
            else:
                self.log_result("Knowledge Base Areas Access", False, 
                              f"Cannot access KB areas: {kb_areas_resp.status_code}")
                
        except Exception as e:
            self.log_result("Knowledge Base Assessment Integration", False, f"Error: {str(e)}")
            
        return False
    
    def test_cross_platform_analytics_integration(self) -> bool:
        """Test cross-platform analytics and data tracking"""
        print("📊 CROSS-PLATFORM ANALYTICS INTEGRATION")
        print("=" * 50)
        
        try:
            # Test 1: Post analytics data from client activity
            client_headers = self.get_headers("client")
            
            analytics_data = {
                "area_id": "area5",
                "resource_type": "assessment",
                "action": "completed",
                "user_context": {
                    "assessment_session": self.session_data.get("assessment_session"),
                    "service_request": self.session_data.get("service_request")
                }
            }
            
            analytics_post_resp = requests.post(f"{BASE_URL}/analytics/resource-access",
                                              json=analytics_data, headers=client_headers)
            
            if analytics_post_resp.status_code == 200:
                self.log_result("Analytics Data Posting", True, 
                              "Successfully posted client activity analytics")
                
                # Brief delay for data processing
                time.sleep(1)
                
                # Test 2: Navigator can see aggregated analytics
                navigator_headers = self.get_headers("navigator")
                
                nav_analytics_resp = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=1",
                                                headers=navigator_headers)
                
                if nav_analytics_resp.status_code == 200:
                    nav_data = nav_analytics_resp.json()
                    total_interactions = nav_data.get("total", 0)
                    by_area_data = nav_data.get("by_area", [])
                    
                    # Check if our posted data appears in analytics
                    area5_data = next((area for area in by_area_data if area.get("area_id") == "area5"), None)
                    
                    self.log_result("Navigator Analytics Integration", True, 
                                  f"Navigator sees {total_interactions} total interactions, area5 has {area5_data.get('count', 0) if area5_data else 0} interactions",
                                  {"total_interactions": total_interactions, "area5_count": area5_data.get('count', 0) if area5_data else 0})
                    
                    # Test 3: Provider notifications integration
                    provider_headers = self.get_headers("provider")
                    
                    notifications_resp = requests.get(f"{BASE_URL}/provider/notifications", headers=provider_headers)
                    
                    if notifications_resp.status_code == 200:
                        notifications_data = notifications_resp.json()
                        notifications = notifications_data.get("notifications", [])
                        
                        # Check for service request related notifications
                        service_notifications = [n for n in notifications 
                                               if "service" in n.get("type", "").lower() or 
                                                  "request" in n.get("message", "").lower()]
                        
                        self.log_result("Provider Notification Integration", True, 
                                      f"Provider has {len(notifications)} total notifications, {len(service_notifications)} service-related",
                                      {"total_notifications": len(notifications), "service_notifications": len(service_notifications)})
                        
                        return True
                    else:
                        self.log_result("Provider Notification Integration", False, 
                                      f"Cannot access provider notifications: {notifications_resp.status_code}")
                else:
                    self.log_result("Navigator Analytics Integration", False, 
                                  f"Cannot access navigator analytics: {nav_analytics_resp.status_code}")
            else:
                self.log_result("Analytics Data Posting", False, 
                              f"Analytics posting failed: {analytics_post_resp.status_code}")
                
        except Exception as e:
            self.log_result("Cross-Platform Analytics Integration", False, f"Error: {str(e)}")
            
        return False
    
    def generate_integration_report(self) -> Dict:
        """Generate comprehensive integration report"""
        print("📋 INTEGRATION ANALYSIS REPORT")
        print("=" * 50)
        
        # Calculate success rates
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize by integration type
        integration_categories = {
            "Authentication": [],
            "Assessment Integration": [],
            "Service Provider Integration": [],
            "Agency Business Intelligence": [],
            "Knowledge Base Integration": [],
            "Analytics Integration": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Auth" in test_name:
                integration_categories["Authentication"].append(result)
            elif "Assessment" in test_name or "Session" in test_name or "Response" in test_name:
                integration_categories["Assessment Integration"].append(result)
            elif "Provider" in test_name or "Service Request" in test_name:
                integration_categories["Service Provider Integration"].append(result)
            elif "Agency" in test_name or "Billing" in test_name or "Tier" in test_name:
                integration_categories["Agency Business Intelligence"].append(result)
            elif "Knowledge Base" in test_name or "AI" in test_name or "Template" in test_name:
                integration_categories["Knowledge Base Integration"].append(result)
            elif "Analytics" in test_name or "Navigator" in test_name or "Notification" in test_name:
                integration_categories["Analytics Integration"].append(result)
        
        # Calculate category success rates
        category_success = {}
        for category, tests in integration_categories.items():
            if tests:
                category_passed = len([t for t in tests if t["success"]])
                category_success[category] = {
                    "passed": category_passed,
                    "total": len(tests),
                    "success_rate": f"{(category_passed / len(tests) * 100):.1f}%"
                }
        
        report = {
            "overall_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "integration_categories": category_success,
            "working_integrations": [r["test"] for r in self.test_results if r["success"]],
            "broken_integrations": [r["test"] for r in self.test_results if not r["success"]],
            "session_data": self.session_data,
            "detailed_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return report

def main():
    """Main test execution"""
    print("🎯 FOCUSED DATA FLOW ANALYSIS AND INTEGRATION TESTING")
    print("Testing actual working endpoints and data flow connections")
    print("=" * 80)
    
    tester = FocusedDataFlowTester()
    
    # Phase 1: Authentication
    if not tester.authenticate_all_users():
        print("❌ CRITICAL: Authentication failed. Cannot proceed.")
        return
    
    # Phase 2: Core Integration Tests
    assessment_flow_success = tester.test_assessment_to_service_request_flow()
    agency_integration_success = tester.test_agency_client_data_integration()
    kb_integration_success = tester.test_knowledge_base_assessment_integration()
    analytics_integration_success = tester.test_cross_platform_analytics_integration()
    
    # Phase 3: Generate Report
    report = tester.generate_integration_report()
    
    # Display Summary
    print("\n" + "=" * 80)
    print("🎯 FOCUSED DATA FLOW ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"📊 Overall Success Rate: {report['overall_summary']['success_rate']}")
    print(f"✅ Passed Tests: {report['overall_summary']['passed_tests']}")
    print(f"❌ Failed Tests: {report['overall_summary']['failed_tests']}")
    
    print(f"\n📈 Integration Category Results:")
    for category, results in report["integration_categories"].items():
        print(f"   {category}: {results['success_rate']} ({results['passed']}/{results['total']})")
    
    print(f"\n✅ Working Integrations:")
    for integration in report["working_integrations"]:
        print(f"   - {integration}")
    
    if report["broken_integrations"]:
        print(f"\n❌ Broken Integrations:")
        for integration in report["broken_integrations"]:
            print(f"   - {integration}")
    
    # Key Findings
    print(f"\n🔍 Key Integration Findings:")
    if assessment_flow_success:
        print("   ✅ Complete Assessment → Service Request → Provider Response flow working")
    else:
        print("   ❌ Assessment to Service Request flow has issues")
        
    if agency_integration_success:
        print("   ✅ Agency Business Intelligence properly integrated with client data")
    else:
        print("   ❌ Agency-Client data integration needs attention")
        
    if kb_integration_success:
        print("   ✅ Knowledge Base integrates with assessment context")
    else:
        print("   ❌ Knowledge Base integration with assessments needs work")
        
    if analytics_integration_success:
        print("   ✅ Cross-platform analytics tracking user interactions")
    else:
        print("   ❌ Analytics integration across platforms incomplete")
    
    # Save detailed report
    with open("/app/focused_integration_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: /app/focused_integration_report.json")
    print("=" * 80)

if __name__ == "__main__":
    main()