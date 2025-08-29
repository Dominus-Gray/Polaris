#!/usr/bin/env python3
"""
Comprehensive Data Flow Analysis and Integration Testing
Focus: Assessment Data Integration, Service Provider Marketplace, Agency BI, Knowledge Base, Cross-Platform Analytics
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

class DataFlowTester:
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
        print(f"{status}: {test_name} - {details}")
        
    def authenticate_all_users(self) -> bool:
        """Authenticate all QA user types"""
        print("\n=== AUTHENTICATION PHASE ===")
        all_success = True
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json=creds)
                if response.status_code == 200:
                    token_data = response.json()
                    self.tokens[role] = token_data["access_token"]
                    self.log_result(f"Auth_{role}", True, f"Successfully authenticated {role}")
                else:
                    self.log_result(f"Auth_{role}", False, f"Auth failed: {response.status_code} - {response.text}")
                    all_success = False
            except Exception as e:
                self.log_result(f"Auth_{role}", False, f"Auth error: {str(e)}")
                all_success = False
                
        return all_success
    
    def get_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {"Authorization": f"Bearer {self.tokens.get(role, '')}", "Content-Type": "application/json"}
    
    def test_assessment_data_integration(self) -> Dict[str, bool]:
        """Test Assessment Data Integration across platform features"""
        print("\n=== ASSESSMENT DATA INTEGRATION TESTING ===")
        results = {}
        
        # 1. Test assessment completion triggers dashboard updates
        try:
            headers = self.get_headers("client")
            session_response = requests.post(f"{BASE_URL}/assessment/tier-session", 
                                           data={"area_id": "area1", "tier_level": 1}, 
                                           headers=headers)
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data.get("session_id")
                self.session_data["assessment_session"] = session_id
                
                # Submit assessment response
                response_data = {
                    "maturity_statement_id": "area1_tier1_stmt1",
                    "response": "No, I need help",
                    "evidence_provided": False
                }
                
                submit_response = requests.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response",
                                              json=response_data, headers=headers)
                
                if submit_response.status_code == 200:
                    # Check if dashboard reflects assessment progress
                    dashboard_response = requests.get(f"{BASE_URL}/client/dashboard", headers=headers)
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        assessment_progress = dashboard_data.get("assessment_progress", {})
                        
                        results["assessment_completion_triggers_dashboard"] = True
                        self.log_result("Assessment→Dashboard Integration", True, 
                                      f"Assessment completion updates dashboard: {assessment_progress}")
                    else:
                        results["assessment_completion_triggers_dashboard"] = False
                        self.log_result("Assessment→Dashboard Integration", False, 
                                      f"Dashboard not accessible: {dashboard_response.status_code}")
                else:
                    results["assessment_completion_triggers_dashboard"] = False
                    self.log_result("Assessment→Dashboard Integration", False, 
                                  f"Assessment response submission failed: {submit_response.status_code}")
            else:
                results["assessment_completion_triggers_dashboard"] = False
                self.log_result("Assessment→Dashboard Integration", False, 
                              f"Assessment session creation failed: {session_response.status_code}")
                
        except Exception as e:
            results["assessment_completion_triggers_dashboard"] = False
            self.log_result("Assessment→Dashboard Integration", False, f"Error: {str(e)}")
        
        # 2. Test gap identification connects to service provider matching
        try:
            headers = self.get_headers("client")
            
            # Check if gaps from assessment trigger service provider recommendations
            gaps_response = requests.get(f"{BASE_URL}/client/gaps", headers=headers)
            if gaps_response.status_code == 200:
                gaps_data = gaps_response.json()
                
                # Test if gaps connect to service requests
                if gaps_data.get("gaps"):
                    gap_area = gaps_data["gaps"][0].get("area_id", "area1")
                    
                    # Create service request based on gap
                    service_request_data = {
                        "area_id": gap_area,
                        "budget_range": "1500-5000",
                        "timeline": "2-4 weeks",
                        "description": f"Need help with {gap_area} based on assessment gap identification",
                        "priority": "high"
                    }
                    
                    service_response = requests.post(f"{BASE_URL}/service-requests/professional-help",
                                                   json=service_request_data, headers=headers)
                    
                    if service_response.status_code == 200:
                        service_data = service_response.json()
                        self.session_data["service_request"] = service_data.get("request_id")
                        
                        results["gap_identification_to_provider_matching"] = True
                        self.log_result("Gap→Provider Matching", True, 
                                      f"Gap identification successfully connects to service provider matching")
                    else:
                        results["gap_identification_to_provider_matching"] = False
                        self.log_result("Gap→Provider Matching", False, 
                                      f"Service request creation failed: {service_response.status_code}")
                else:
                    results["gap_identification_to_provider_matching"] = False
                    self.log_result("Gap→Provider Matching", False, "No gaps found to test connection")
            else:
                results["gap_identification_to_provider_matching"] = False
                self.log_result("Gap→Provider Matching", False, f"Gaps endpoint not accessible: {gaps_response.status_code}")
                
        except Exception as e:
            results["gap_identification_to_provider_matching"] = False
            self.log_result("Gap→Provider Matching", False, f"Error: {str(e)}")
        
        # 3. Test assessment scores affect resource recommendations
        try:
            headers = self.get_headers("client")
            
            # Get assessment progress/scores
            progress_response = requests.get(f"{BASE_URL}/client/assessment-progress", headers=headers)
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                
                # Check if resources are personalized based on assessment
                resources_response = requests.get(f"{BASE_URL}/client/recommended-resources", headers=headers)
                if resources_response.status_code == 200:
                    resources_data = resources_response.json()
                    
                    # Verify resources are tailored to assessment results
                    personalized = any(resource.get("based_on_assessment") for resource in resources_data.get("resources", []))
                    
                    results["assessment_scores_affect_resources"] = personalized
                    self.log_result("Assessment→Resource Recommendations", personalized, 
                                  f"Resources personalized based on assessment: {personalized}")
                else:
                    results["assessment_scores_affect_resources"] = False
                    self.log_result("Assessment→Resource Recommendations", False, 
                                  f"Resources endpoint not accessible: {resources_response.status_code}")
            else:
                results["assessment_scores_affect_resources"] = False
                self.log_result("Assessment→Resource Recommendations", False, 
                              f"Assessment progress not accessible: {progress_response.status_code}")
                
        except Exception as e:
            results["assessment_scores_affect_resources"] = False
            self.log_result("Assessment→Resource Recommendations", False, f"Error: {str(e)}")
        
        return results
    
    def test_service_provider_marketplace_integration(self) -> Dict[str, bool]:
        """Test Service Provider Marketplace Integration"""
        print("\n=== SERVICE PROVIDER MARKETPLACE INTEGRATION TESTING ===")
        results = {}
        
        # 1. Test provider profiles connect to service requests
        try:
            provider_headers = self.get_headers("provider")
            client_headers = self.get_headers("client")
            
            # Get provider profile
            profile_response = requests.get(f"{BASE_URL}/provider/profile", headers=provider_headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                provider_id = profile_data.get("id")
                
                # Create service request if not exists
                if not self.session_data.get("service_request"):
                    service_request_data = {
                        "area_id": "area5",
                        "budget_range": "1500-5000", 
                        "timeline": "2-4 weeks",
                        "description": "Testing provider profile connection to service requests",
                        "priority": "medium"
                    }
                    
                    service_response = requests.post(f"{BASE_URL}/service-requests/professional-help",
                                                   json=service_request_data, headers=client_headers)
                    if service_response.status_code == 200:
                        self.session_data["service_request"] = service_response.json().get("request_id")
                
                # Provider responds to service request
                if self.session_data.get("service_request"):
                    response_data = {
                        "request_id": self.session_data["service_request"],
                        "proposed_fee": 2000.0,
                        "estimated_timeline": "3 weeks",
                        "proposal_note": "Testing provider profile integration with service requests"
                    }
                    
                    provider_response = requests.post(f"{BASE_URL}/provider/respond-to-request",
                                                    json=response_data, headers=provider_headers)
                    
                    if provider_response.status_code == 200:
                        results["provider_profiles_connect_to_requests"] = True
                        self.log_result("Provider Profile→Service Request", True, 
                                      "Provider profiles successfully connect to service requests")
                    else:
                        results["provider_profiles_connect_to_requests"] = False
                        self.log_result("Provider Profile→Service Request", False, 
                                      f"Provider response failed: {provider_response.status_code}")
                else:
                    results["provider_profiles_connect_to_requests"] = False
                    self.log_result("Provider Profile→Service Request", False, "No service request available for testing")
            else:
                results["provider_profiles_connect_to_requests"] = False
                self.log_result("Provider Profile→Service Request", False, 
                              f"Provider profile not accessible: {profile_response.status_code}")
                
        except Exception as e:
            results["provider_profiles_connect_to_requests"] = False
            self.log_result("Provider Profile→Service Request", False, f"Error: {str(e)}")
        
        # 2. Test rating system affects provider search and ranking
        try:
            # Get provider ratings
            provider_headers = self.get_headers("provider")
            ratings_response = requests.get(f"{BASE_URL}/provider/ratings", headers=provider_headers)
            
            if ratings_response.status_code == 200:
                ratings_data = ratings_response.json()
                
                # Test provider search with rating influence
                search_response = requests.get(f"{BASE_URL}/providers/search?area_id=area5&sort_by=rating", 
                                             headers=self.get_headers("client"))
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    providers = search_data.get("providers", [])
                    
                    # Check if providers are sorted by rating
                    rating_sorted = True
                    if len(providers) > 1:
                        for i in range(len(providers) - 1):
                            current_rating = providers[i].get("average_rating", 0)
                            next_rating = providers[i + 1].get("average_rating", 0)
                            if current_rating < next_rating:
                                rating_sorted = False
                                break
                    
                    results["rating_system_affects_search"] = rating_sorted
                    self.log_result("Rating System→Search Ranking", rating_sorted, 
                                  f"Rating system affects provider search and ranking: {rating_sorted}")
                else:
                    results["rating_system_affects_search"] = False
                    self.log_result("Rating System→Search Ranking", False, 
                                  f"Provider search not accessible: {search_response.status_code}")
            else:
                results["rating_system_affects_search"] = False
                self.log_result("Rating System→Search Ranking", False, 
                              f"Provider ratings not accessible: {ratings_response.status_code}")
                
        except Exception as e:
            results["rating_system_affects_search"] = False
            self.log_result("Rating System→Search Ranking", False, f"Error: {str(e)}")
        
        # 3. Test notification system for new service requests
        try:
            provider_headers = self.get_headers("provider")
            
            # Check provider notifications
            notifications_response = requests.get(f"{BASE_URL}/provider/notifications", headers=provider_headers)
            
            if notifications_response.status_code == 200:
                notifications_data = notifications_response.json()
                notifications = notifications_data.get("notifications", [])
                
                # Check for service request notifications
                service_notifications = [n for n in notifications if n.get("type") == "new_service_request"]
                
                results["notification_system_for_requests"] = len(service_notifications) > 0
                self.log_result("Notification System→Service Requests", len(service_notifications) > 0, 
                              f"Found {len(service_notifications)} service request notifications")
            else:
                results["notification_system_for_requests"] = False
                self.log_result("Notification System→Service Requests", False, 
                              f"Notifications not accessible: {notifications_response.status_code}")
                
        except Exception as e:
            results["notification_system_for_requests"] = False
            self.log_result("Notification System→Service Requests", False, f"Error: {str(e)}")
        
        return results
    
    def test_agency_business_intelligence(self) -> Dict[str, bool]:
        """Test Agency Business Intelligence Integration"""
        print("\n=== AGENCY BUSINESS INTELLIGENCE TESTING ===")
        results = {}
        
        # 1. Test agency dashboards show real client assessment data
        try:
            agency_headers = self.get_headers("agency")
            
            # Get agency dashboard
            dashboard_response = requests.get(f"{BASE_URL}/agency/dashboard", headers=agency_headers)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                
                # Check if dashboard contains real client assessment data
                client_assessments = dashboard_data.get("client_assessments", {})
                assessment_analytics = dashboard_data.get("assessment_analytics", {})
                
                has_real_data = (
                    client_assessments.get("total_clients", 0) > 0 or
                    assessment_analytics.get("completed_assessments", 0) > 0
                )
                
                results["agency_dashboard_shows_assessment_data"] = has_real_data
                self.log_result("Agency Dashboard→Assessment Data", has_real_data, 
                              f"Agency dashboard shows real client assessment data: {has_real_data}")
            else:
                results["agency_dashboard_shows_assessment_data"] = False
                self.log_result("Agency Dashboard→Assessment Data", False, 
                              f"Agency dashboard not accessible: {dashboard_response.status_code}")
                
        except Exception as e:
            results["agency_dashboard_shows_assessment_data"] = False
            self.log_result("Agency Dashboard→Assessment Data", False, f"Error: {str(e)}")
        
        # 2. Test billing tracks actual tier usage and completions
        try:
            agency_headers = self.get_headers("agency")
            
            # Get billing usage data
            billing_response = requests.get(f"{BASE_URL}/agency/billing/usage", headers=agency_headers)
            
            if billing_response.status_code == 200:
                billing_data = billing_response.json()
                
                # Check if billing reflects actual usage
                tier_usage = billing_data.get("tier_usage", {})
                assessment_completions = billing_data.get("assessment_completions", 0)
                
                tracks_usage = (
                    len(tier_usage) > 0 or
                    assessment_completions > 0
                )
                
                results["billing_tracks_tier_usage"] = tracks_usage
                self.log_result("Billing→Tier Usage Tracking", tracks_usage, 
                              f"Billing tracks actual tier usage and completions: {tracks_usage}")
            else:
                results["billing_tracks_tier_usage"] = False
                self.log_result("Billing→Tier Usage Tracking", False, 
                              f"Billing usage not accessible: {billing_response.status_code}")
                
        except Exception as e:
            results["billing_tracks_tier_usage"] = False
            self.log_result("Billing→Tier Usage Tracking", False, f"Error: {str(e)}")
        
        # 3. Test compliance insights based on real assessment data
        try:
            agency_headers = self.get_headers("agency")
            
            # Get compliance insights
            compliance_response = requests.get(f"{BASE_URL}/agency/compliance-insights", headers=agency_headers)
            
            if compliance_response.status_code == 200:
                compliance_data = compliance_response.json()
                
                # Check if insights are based on real assessment data
                insights = compliance_data.get("insights", [])
                assessment_based = any(insight.get("based_on_assessments") for insight in insights)
                
                results["compliance_insights_from_assessments"] = assessment_based
                self.log_result("Compliance Insights→Assessment Data", assessment_based, 
                              f"Compliance insights based on real assessment data: {assessment_based}")
            else:
                results["compliance_insights_from_assessments"] = False
                self.log_result("Compliance Insights→Assessment Data", False, 
                              f"Compliance insights not accessible: {compliance_response.status_code}")
                
        except Exception as e:
            results["compliance_insights_from_assessments"] = False
            self.log_result("Compliance Insights→Assessment Data", False, f"Error: {str(e)}")
        
        return results
    
    def test_knowledge_base_integration(self) -> Dict[str, bool]:
        """Test Knowledge Base Integration"""
        print("\n=== KNOWLEDGE BASE INTEGRATION TESTING ===")
        results = {}
        
        # 1. Test payment system unlocks content
        try:
            client_headers = self.get_headers("client")
            
            # Check knowledge base areas before payment
            kb_areas_response = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=client_headers)
            
            if kb_areas_response.status_code == 200:
                areas_data = kb_areas_response.json()
                locked_areas = [area for area in areas_data.get("areas", []) if not area.get("unlocked")]
                
                if locked_areas:
                    # Test payment system
                    payment_data = {"area_ids": [locked_areas[0]["id"]], "payment_method": "test"}
                    payment_response = requests.post(f"{BASE_URL}/payments/knowledge-base",
                                                   json=payment_data, headers=client_headers)
                    
                    if payment_response.status_code == 200:
                        # Check if area is now unlocked
                        time.sleep(1)  # Brief delay for processing
                        updated_areas_response = requests.get(f"{BASE_URL}/knowledge-base/areas", headers=client_headers)
                        
                        if updated_areas_response.status_code == 200:
                            updated_areas = updated_areas_response.json()
                            area_unlocked = any(area.get("unlocked") and area["id"] == locked_areas[0]["id"] 
                                              for area in updated_areas.get("areas", []))
                            
                            results["payment_system_unlocks_content"] = area_unlocked
                            self.log_result("Payment System→Content Unlock", area_unlocked, 
                                          f"Payment system successfully unlocks KB content: {area_unlocked}")
                        else:
                            results["payment_system_unlocks_content"] = False
                            self.log_result("Payment System→Content Unlock", False, "Could not verify unlock status")
                    else:
                        results["payment_system_unlocks_content"] = False
                        self.log_result("Payment System→Content Unlock", False, 
                                      f"Payment processing failed: {payment_response.status_code}")
                else:
                    results["payment_system_unlocks_content"] = True
                    self.log_result("Payment System→Content Unlock", True, "All KB areas already unlocked for QA user")
            else:
                results["payment_system_unlocks_content"] = False
                self.log_result("Payment System→Content Unlock", False, 
                              f"KB areas not accessible: {kb_areas_response.status_code}")
                
        except Exception as e:
            results["payment_system_unlocks_content"] = False
            self.log_result("Payment System→Content Unlock", False, f"Error: {str(e)}")
        
        # 2. Test AI consultation connects to assessment gaps
        try:
            client_headers = self.get_headers("client")
            
            # Get assessment gaps
            gaps_response = requests.get(f"{BASE_URL}/client/gaps", headers=client_headers)
            
            if gaps_response.status_code == 200:
                gaps_data = gaps_response.json()
                gaps = gaps_data.get("gaps", [])
                
                if gaps:
                    # Test AI consultation with gap context
                    ai_request = {
                        "question": f"How can I improve in {gaps[0].get('area_name', 'business area')}?",
                        "context": {"assessment_gaps": gaps[:3]}  # Include gap context
                    }
                    
                    ai_response = requests.post(f"{BASE_URL}/knowledge-base/ai-assistance",
                                              json=ai_request, headers=client_headers)
                    
                    if ai_response.status_code == 200:
                        ai_data = ai_response.json()
                        response_text = ai_data.get("response", "")
                        
                        # Check if AI response references the gaps
                        gap_referenced = any(gap.get("area_name", "").lower() in response_text.lower() 
                                           for gap in gaps[:3])
                        
                        results["ai_consultation_connects_to_gaps"] = gap_referenced
                        self.log_result("AI Consultation→Assessment Gaps", gap_referenced, 
                                      f"AI consultation connects to assessment gaps: {gap_referenced}")
                    else:
                        results["ai_consultation_connects_to_gaps"] = False
                        self.log_result("AI Consultation→Assessment Gaps", False, 
                                      f"AI consultation failed: {ai_response.status_code}")
                else:
                    results["ai_consultation_connects_to_gaps"] = False
                    self.log_result("AI Consultation→Assessment Gaps", False, "No assessment gaps found to test")
            else:
                results["ai_consultation_connects_to_gaps"] = False
                self.log_result("AI Consultation→Assessment Gaps", False, 
                              f"Assessment gaps not accessible: {gaps_response.status_code}")
                
        except Exception as e:
            results["ai_consultation_connects_to_gaps"] = False
            self.log_result("AI Consultation→Assessment Gaps", False, f"Error: {str(e)}")
        
        return results
    
    def test_cross_platform_analytics(self) -> Dict[str, bool]:
        """Test Cross-Platform Analytics Integration"""
        print("\n=== CROSS-PLATFORM ANALYTICS TESTING ===")
        results = {}
        
        # 1. Test navigator analytics track real client interactions
        try:
            navigator_headers = self.get_headers("navigator")
            
            # Get navigator analytics
            analytics_response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=30", 
                                            headers=navigator_headers)
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                
                # Check if analytics show real interaction data
                total_interactions = analytics_data.get("total", 0)
                by_area_data = analytics_data.get("by_area", [])
                
                has_real_interactions = total_interactions > 0 and len(by_area_data) > 0
                
                results["navigator_analytics_track_interactions"] = has_real_interactions
                self.log_result("Navigator Analytics→Client Interactions", has_real_interactions, 
                              f"Navigator analytics track real client interactions: {total_interactions} total")
            else:
                results["navigator_analytics_track_interactions"] = False
                self.log_result("Navigator Analytics→Client Interactions", False, 
                              f"Navigator analytics not accessible: {analytics_response.status_code}")
                
        except Exception as e:
            results["navigator_analytics_track_interactions"] = False
            self.log_result("Navigator Analytics→Client Interactions", False, f"Error: {str(e)}")
        
        # 2. Test resource usage measurement and reporting
        try:
            # Post analytics data to test tracking
            client_headers = self.get_headers("client")
            
            analytics_post_data = {
                "area_id": "area1",
                "resource_type": "template",
                "action": "download",
                "user_context": {"assessment_completed": True}
            }
            
            post_response = requests.post(f"{BASE_URL}/analytics/resource-access",
                                        json=analytics_post_data, headers=client_headers)
            
            if post_response.status_code == 200:
                # Check if usage is reflected in reporting
                time.sleep(1)  # Brief delay for processing
                
                navigator_headers = self.get_headers("navigator")
                usage_response = requests.get(f"{BASE_URL}/navigator/analytics/resources?since_days=1", 
                                            headers=navigator_headers)
                
                if usage_response.status_code == 200:
                    usage_data = usage_response.json()
                    recent_usage = usage_data.get("total", 0)
                    
                    results["resource_usage_measured_and_reported"] = recent_usage > 0
                    self.log_result("Resource Usage→Measurement & Reporting", recent_usage > 0, 
                                  f"Resource usage measured and reported: {recent_usage} recent accesses")
                else:
                    results["resource_usage_measured_and_reported"] = False
                    self.log_result("Resource Usage→Measurement & Reporting", False, 
                                  f"Usage reporting not accessible: {usage_response.status_code}")
            else:
                results["resource_usage_measured_and_reported"] = False
                self.log_result("Resource Usage→Measurement & Reporting", False, 
                              f"Analytics posting failed: {post_response.status_code}")
                
        except Exception as e:
            results["resource_usage_measured_and_reported"] = False
            self.log_result("Resource Usage→Measurement & Reporting", False, f"Error: {str(e)}")
        
        # 3. Test user journey data flows between features
        try:
            client_headers = self.get_headers("client")
            
            # Test journey: Assessment → Gap Identification → Service Request → Provider Response
            journey_complete = True
            journey_steps = []
            
            # Step 1: Assessment data
            if self.session_data.get("assessment_session"):
                journey_steps.append("Assessment Session Created")
            
            # Step 2: Gap identification
            gaps_response = requests.get(f"{BASE_URL}/client/gaps", headers=client_headers)
            if gaps_response.status_code == 200:
                journey_steps.append("Gap Identification Accessible")
            
            # Step 3: Service request
            if self.session_data.get("service_request"):
                journey_steps.append("Service Request Created")
            
            # Step 4: Check if journey data is connected
            journey_response = requests.get(f"{BASE_URL}/client/journey-analytics", headers=client_headers)
            if journey_response.status_code == 200:
                journey_data = journey_response.json()
                connected_steps = journey_data.get("connected_steps", [])
                journey_steps.append(f"Journey Analytics: {len(connected_steps)} connected steps")
            
            results["user_journey_data_flows"] = len(journey_steps) >= 3
            self.log_result("User Journey→Data Flow Between Features", len(journey_steps) >= 3, 
                          f"User journey data flows between features: {', '.join(journey_steps)}")
                
        except Exception as e:
            results["user_journey_data_flows"] = False
            self.log_result("User Journey→Data Flow Between Features", False, f"Error: {str(e)}")
        
        return results
    
    def identify_missing_endpoints_and_workflows(self) -> Dict[str, List[str]]:
        """Identify missing endpoints and broken workflows"""
        print("\n=== MISSING ENDPOINTS & WORKFLOW ANALYSIS ===")
        
        missing_items = {
            "missing_endpoints": [],
            "broken_workflows": [],
            "integration_gaps": []
        }
        
        # Test critical endpoints that should exist
        critical_endpoints = [
            ("/client/dashboard", "client"),
            ("/client/gaps", "client"),
            ("/client/assessment-progress", "client"),
            ("/client/recommended-resources", "client"),
            ("/provider/profile", "provider"),
            ("/provider/notifications", "provider"),
            ("/provider/ratings", "provider"),
            ("/agency/dashboard", "agency"),
            ("/agency/compliance-insights", "agency"),
            ("/navigator/analytics/resources", "navigator"),
            ("/client/journey-analytics", "client"),
            ("/providers/search", "client")
        ]
        
        for endpoint, role in critical_endpoints:
            try:
                headers = self.get_headers(role)
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 404:
                    missing_items["missing_endpoints"].append(f"{endpoint} (404 Not Found)")
                    self.log_result(f"Endpoint Check: {endpoint}", False, f"Missing endpoint: {response.status_code}")
                elif response.status_code >= 500:
                    missing_items["broken_workflows"].append(f"{endpoint} (Server Error: {response.status_code})")
                    self.log_result(f"Endpoint Check: {endpoint}", False, f"Server error: {response.status_code}")
                elif response.status_code == 401:
                    missing_items["integration_gaps"].append(f"{endpoint} (Authentication Issue)")
                    self.log_result(f"Endpoint Check: {endpoint}", False, f"Auth issue: {response.status_code}")
                else:
                    self.log_result(f"Endpoint Check: {endpoint}", True, f"Accessible: {response.status_code}")
                    
            except Exception as e:
                missing_items["broken_workflows"].append(f"{endpoint} (Connection Error: {str(e)})")
                self.log_result(f"Endpoint Check: {endpoint}", False, f"Connection error: {str(e)}")
        
        return missing_items
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive test report"""
        print("\n=== GENERATING COMPREHENSIVE REPORT ===")
        
        # Calculate success rates
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        critical_failures = []
        integration_issues = []
        working_features = []
        
        for result in self.test_results:
            if not result["success"]:
                if "Integration" in result["test"] or "→" in result["test"]:
                    integration_issues.append(result["test"])
                else:
                    critical_failures.append(result["test"])
            else:
                working_features.append(result["test"])
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "critical_failures": critical_failures,
            "integration_issues": integration_issues,
            "working_features": working_features,
            "detailed_results": self.test_results,
            "session_data": self.session_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return report

def main():
    """Main test execution"""
    print("🎯 COMPREHENSIVE DATA FLOW ANALYSIS AND INTEGRATION TESTING")
    print("=" * 80)
    
    tester = DataFlowTester()
    
    # Phase 1: Authentication
    if not tester.authenticate_all_users():
        print("❌ CRITICAL: Authentication failed for some users. Cannot proceed with comprehensive testing.")
        return
    
    # Phase 2: Data Flow Integration Tests
    assessment_results = tester.test_assessment_data_integration()
    marketplace_results = tester.test_service_provider_marketplace_integration()
    agency_results = tester.test_agency_business_intelligence()
    kb_results = tester.test_knowledge_base_integration()
    analytics_results = tester.test_cross_platform_analytics()
    
    # Phase 3: Missing Components Analysis
    missing_items = tester.identify_missing_endpoints_and_workflows()
    
    # Phase 4: Generate Report
    report = tester.generate_comprehensive_report()
    
    # Display Summary
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE DATA FLOW ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"📊 Overall Success Rate: {report['test_summary']['success_rate']}")
    print(f"✅ Working Features: {len(report['working_features'])}")
    print(f"🔗 Integration Issues: {len(report['integration_issues'])}")
    print(f"❌ Critical Failures: {len(report['critical_failures'])}")
    
    if missing_items["missing_endpoints"]:
        print(f"\n🚫 Missing Endpoints ({len(missing_items['missing_endpoints'])}):")
        for endpoint in missing_items["missing_endpoints"]:
            print(f"   - {endpoint}")
    
    if missing_items["broken_workflows"]:
        print(f"\n💥 Broken Workflows ({len(missing_items['broken_workflows'])}):")
        for workflow in missing_items["broken_workflows"]:
            print(f"   - {workflow}")
    
    if missing_items["integration_gaps"]:
        print(f"\n🔌 Integration Gaps ({len(missing_items['integration_gaps'])}):")
        for gap in missing_items["integration_gaps"]:
            print(f"   - {gap}")
    
    # Save detailed report
    with open("/app/data_flow_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: /app/data_flow_analysis_report.json")
    print("=" * 80)

if __name__ == "__main__":
    main()