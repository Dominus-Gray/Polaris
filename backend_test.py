#!/usr/bin/env python3
"""
Polaris Backend Testing Suite - Tier-Based Assessment System
Testing the enhanced tier-based assessment system and service provider features
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://quality-match-1.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class TierBasedAssessmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.session_ids = {}
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: dict = None):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_user(self, role: str) -> bool:
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"Authentication - {role}", True, f"Token obtained for {creds['email']}")
                return True
            else:
                self.log_result(f"Authentication - {role}", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for role"""
        return {
            "Authorization": f"Bearer {self.tokens[role]}",
            "Content-Type": "application/json"
        }

    def test_tier_based_assessment_schema(self) -> bool:
        """Test GET /api/assessment/schema/tier-based - should return areas with tier information"""
        try:
            headers = self.get_headers("client")
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "areas" in data and isinstance(data["areas"], list):
                    # Check if areas have tier information
                    has_tier_info = False
                    for area in data["areas"]:
                        if "tiers" in area or "tier_levels" in area:
                            has_tier_info = True
                            break
                    
                    if has_tier_info:
                        self.log_result("Tier-Based Assessment Schema", True, 
                                      f"Found {len(data['areas'])} areas with tier information")
                        return True
                    else:
                        self.log_result("Tier-Based Assessment Schema", False, 
                                      "Areas found but no tier information detected", data)
                        return False
                else:
                    self.log_result("Tier-Based Assessment Schema", False, 
                                  "Invalid response structure - missing 'areas' array", data)
                    return False
            else:
                self.log_result("Tier-Based Assessment Schema", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier-Based Assessment Schema", False, f"Exception: {str(e)}")
            return False

    def test_create_tier_session(self) -> bool:
        """Test POST /api/assessment/tier-session - create tier-based assessment sessions"""
        try:
            headers = self.get_headers("client")
            
            # Test data for tier-based session
            session_data = {
                "area_id": "area1",
                "tier_level": 2,
                "session_type": "tier_based"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       json=session_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                if "session_id" in data:
                    self.session_ids["tier_session"] = data["session_id"]
                    self.log_result("Create Tier-Based Session", True, 
                                  f"Session created: {data['session_id']}")
                    return True
                else:
                    self.log_result("Create Tier-Based Session", False, 
                                  "Session created but no session_id returned", data)
                    return False
            else:
                self.log_result("Create Tier-Based Session", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Tier-Based Session", False, f"Exception: {str(e)}")
            return False

    def test_submit_tier_response(self) -> bool:
        """Test POST /api/assessment/tier-session/{session_id}/response - submit responses"""
        try:
            if "tier_session" not in self.session_ids:
                self.log_result("Submit Tier Response", False, "No tier session available")
                return False
                
            headers = self.get_headers("client")
            session_id = self.session_ids["tier_session"]
            
            # Test response data
            response_data = {
                "question_id": "q1",
                "response": "yes",
                "evidence_provided": True,
                "evidence_url": "https://example.com/evidence.pdf",
                "tier_level": 2
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{session_id}/response", 
                                       json=response_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("Submit Tier Response", True, 
                              f"Response submitted successfully")
                return True
            else:
                self.log_result("Submit Tier Response", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Submit Tier Response", False, f"Exception: {str(e)}")
            return False

    def test_tier_session_progress(self) -> bool:
        """Test GET /api/assessment/tier-session/{session_id}/progress - get session progress"""
        try:
            if "tier_session" not in self.session_ids:
                self.log_result("Tier Session Progress", False, "No tier session available")
                return False
                
            headers = self.get_headers("client")
            session_id = self.session_ids["tier_session"]
            
            response = self.session.get(f"{BASE_URL}/assessment/tier-session/{session_id}/progress", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate progress structure
                if "completion_percentage" in data or "progress" in data:
                    self.log_result("Tier Session Progress", True, 
                                  f"Progress retrieved successfully")
                    return True
                else:
                    self.log_result("Tier Session Progress", False, 
                                  "Progress data missing expected fields", data)
                    return False
            else:
                self.log_result("Tier Session Progress", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Tier Session Progress", False, f"Exception: {str(e)}")
            return False

    def test_enhanced_provider_profile(self) -> bool:
        """Test POST /api/provider/profile/enhanced - create enhanced provider profiles"""
        try:
            headers = self.get_headers("provider")
            
            # Enhanced provider profile data
            profile_data = {
                "business_name": "Elite Business Solutions",
                "tagline": "Your trusted partner for government contracting success",
                "overview": "We specialize in helping small businesses navigate government contracting requirements with over 10 years of experience.",
                "service_areas": ["area1", "area2", "area5"],
                "specializations": ["Government Contracting", "Compliance", "Business Formation"],
                "certifications": ["PTAC Certified", "SBA Approved"],
                "years_experience": 10,
                "team_size": "5-10 employees",
                "pricing_model": "Project-based with transparent pricing",
                "availability": "Available for new projects",
                "location": "San Antonio, TX",
                "portfolio_highlights": [
                    "Helped 50+ businesses win government contracts",
                    "100% compliance success rate",
                    "Average contract value increase of 40%"
                ],
                "client_testimonials": [
                    "Outstanding service and results - highly recommended!",
                    "Professional team that delivers on promises"
                ],
                "response_time_avg": "4 hours",
                "success_metrics": {
                    "contracts_won": 150,
                    "client_satisfaction": 4.8,
                    "repeat_clients": 85
                }
            }
            
            response = self.session.post(f"{BASE_URL}/provider/profile/enhanced", 
                                       json=profile_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("Enhanced Provider Profile", True, 
                              f"Enhanced profile created successfully")
                return True
            else:
                self.log_result("Enhanced Provider Profile", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Enhanced Provider Profile", False, f"Exception: {str(e)}")
            return False

    def test_service_request_responses_enhanced(self) -> bool:
        """Test GET /api/service-requests/{request_id}/responses/enhanced - view all 5 responses at once"""
        try:
            # First create a service request
            headers = self.get_headers("client")
            
            request_data = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need technology security infrastructure assessment and implementation",
                "priority": "high"
            }
            
            response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                       json=request_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                request_data = response.json()
                request_id = request_data.get("request_id") or request_data.get("id")
                
                if request_id:
                    # Test enhanced responses endpoint
                    response = self.session.get(f"{BASE_URL}/service-requests/{request_id}/responses/enhanced", 
                                              headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result("Enhanced Service Request Responses", True, 
                                      f"Enhanced responses retrieved for request {request_id}")
                        return True
                    else:
                        self.log_result("Enhanced Service Request Responses", False, 
                                      f"Status: {response.status_code}", response.json())
                        return False
                else:
                    self.log_result("Enhanced Service Request Responses", False, 
                                  "Service request created but no ID returned")
                    return False
            else:
                self.log_result("Enhanced Service Request Responses", False, 
                              f"Failed to create service request. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Enhanced Service Request Responses", False, f"Exception: {str(e)}")
            return False

    def test_service_rating_system(self) -> bool:
        """Test POST /api/service/rating - submit 1-5 star ratings"""
        try:
            headers = self.get_headers("client")
            
            # Rating data
            rating_data = {
                "service_request_id": "test_request_123",
                "provider_id": "test_provider_456",
                "overall_rating": 5,
                "quality_rating": 5,
                "communication_rating": 4,
                "timeliness_rating": 5,
                "value_rating": 4,
                "review_text": "Excellent service! Professional team that delivered exactly what was promised on time.",
                "would_recommend": True
            }
            
            response = self.session.post(f"{BASE_URL}/service/rating", 
                                       json=rating_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("Service Rating System", True, 
                              f"Rating submitted successfully")
                return True
            else:
                self.log_result("Service Rating System", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Service Rating System", False, f"Exception: {str(e)}")
            return False

    def test_provider_ratings_retrieval(self) -> bool:
        """Test GET /api/provider/ratings - get provider ratings"""
        try:
            headers = self.get_headers("provider")
            
            response = self.session.get(f"{BASE_URL}/provider/ratings", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate ratings structure
                if "ratings" in data or "average_rating" in data:
                    self.log_result("Provider Ratings Retrieval", True, 
                                  f"Provider ratings retrieved successfully")
                    return True
                else:
                    self.log_result("Provider Ratings Retrieval", False, 
                                  "Ratings data missing expected structure", data)
                    return False
            else:
                self.log_result("Provider Ratings Retrieval", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Provider Ratings Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_ai_localized_resources(self) -> bool:
        """Test GET /api/free-resources/localized - should generate dynamic localized resources"""
        try:
            headers = self.get_headers("client")
            
            # Test with location parameters
            params = {
                "city": "San Antonio",
                "state": "Texas",
                "area_context": "Technology & Security Infrastructure"
            }
            
            response = self.session.get(f"{BASE_URL}/free-resources/localized", 
                                      params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate localized resources structure
                if "resources" in data and isinstance(data["resources"], list):
                    # Check for AI-generated or location-specific content
                    has_localized_content = False
                    for resource in data["resources"]:
                        if ("San Antonio" in str(resource) or "Texas" in str(resource) or 
                            resource.get("location_specific") == True):
                            has_localized_content = True
                            break
                    
                    if has_localized_content:
                        self.log_result("AI Localized Resources", True, 
                                      f"Found {len(data['resources'])} localized resources")
                        return True
                    else:
                        self.log_result("AI Localized Resources", False, 
                                      "Resources found but no localized content detected", data)
                        return False
                else:
                    self.log_result("AI Localized Resources", False, 
                                  "Invalid response structure", data)
                    return False
            else:
                self.log_result("AI Localized Resources", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("AI Localized Resources", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_configuration(self) -> bool:
        """Test GET /api/agency/tier-configuration - get tier access and pricing"""
        try:
            headers = self.get_headers("agency")
            
            response = self.session.get(f"{BASE_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate tier configuration structure
                if ("tier_access_levels" in data or "pricing_per_tier" in data or 
                    "tiers" in data):
                    self.log_result("Agency Tier Configuration", True, 
                                  f"Tier configuration retrieved successfully")
                    return True
                else:
                    self.log_result("Agency Tier Configuration", False, 
                                  "Configuration missing tier information", data)
                    return False
            else:
                self.log_result("Agency Tier Configuration", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Tier Configuration", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_upgrade(self) -> bool:
        """Test POST /api/agency/tier-configuration/upgrade - upgrade tier access"""
        try:
            headers = self.get_headers("agency")
            
            # Upgrade data
            upgrade_data = {
                "area_id": "area1",
                "new_tier_level": 3,
                "payment_method": "stripe"
            }
            
            response = self.session.post(f"{BASE_URL}/agency/tier-configuration/upgrade", 
                                       json=upgrade_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.log_result("Agency Tier Upgrade", True, 
                              f"Tier upgrade processed successfully")
                return True
            else:
                self.log_result("Agency Tier Upgrade", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Tier Upgrade", False, f"Exception: {str(e)}")
            return False

    def test_agency_billing_usage(self) -> bool:
        """Test GET /api/agency/billing/usage - get usage billing information"""
        try:
            headers = self.get_headers("agency")
            
            response = self.session.get(f"{BASE_URL}/agency/billing/usage", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate billing structure
                if ("usage" in data or "billing_period" in data or 
                    "total_cost" in data or "tier_usage" in data):
                    self.log_result("Agency Billing Usage", True, 
                                  f"Billing usage retrieved successfully")
                    return True
                else:
                    self.log_result("Agency Billing Usage", False, 
                                  "Billing data missing expected fields", data)
                    return False
            else:
                self.log_result("Agency Billing Usage", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Agency Billing Usage", False, f"Exception: {str(e)}")
            return False

    def test_client_tier_access(self) -> bool:
        """Test GET /api/client/tier-access - get available tier levels"""
        try:
            headers = self.get_headers("client")
            
            response = self.session.get(f"{BASE_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate tier access structure
                if ("tier_levels" in data or "access_levels" in data or 
                    "available_tiers" in data):
                    self.log_result("Client Tier Access", True, 
                                  f"Client tier access retrieved successfully")
                    return True
                else:
                    self.log_result("Client Tier Access", False, 
                                  "Tier access data missing expected fields", data)
                    return False
            else:
                self.log_result("Client Tier Access", False, 
                              f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Client Tier Access", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all tier-based assessment and enhanced service provider tests"""
        print("🎯 TIER-BASED ASSESSMENT SYSTEM TESTING")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()

        # Authentication phase
        print("📋 AUTHENTICATION PHASE")
        print("-" * 30)
        auth_success = True
        for role in ["client", "provider", "agency", "navigator"]:
            if not self.authenticate_user(role):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication failed for some users. Stopping tests.")
            return False

        print("\n🔬 TIER-BASED ASSESSMENT TESTING")
        print("-" * 40)
        
        # Tier-based assessment tests
        tier_tests = [
            self.test_tier_based_assessment_schema,
            self.test_create_tier_session,
            self.test_submit_tier_response,
            self.test_tier_session_progress
        ]
        
        tier_passed = 0
        for test in tier_tests:
            if test():
                tier_passed += 1

        print("\n🏢 ENHANCED SERVICE PROVIDER TESTING")
        print("-" * 40)
        
        # Enhanced service provider tests
        provider_tests = [
            self.test_enhanced_provider_profile,
            self.test_service_request_responses_enhanced,
            self.test_service_rating_system,
            self.test_provider_ratings_retrieval
        ]
        
        provider_passed = 0
        for test in provider_tests:
            if test():
                provider_passed += 1

        print("\n🤖 AI & LOCALIZATION TESTING")
        print("-" * 35)
        
        # AI and localization tests
        ai_tests = [
            self.test_ai_localized_resources
        ]
        
        ai_passed = 0
        for test in ai_tests:
            if test():
                ai_passed += 1

        print("\n🏛️ AGENCY TIER MANAGEMENT TESTING")
        print("-" * 40)
        
        # Agency tier management tests
        agency_tests = [
            self.test_agency_tier_configuration,
            self.test_agency_tier_upgrade,
            self.test_agency_billing_usage
        ]
        
        agency_passed = 0
        for test in agency_tests:
            if test():
                agency_passed += 1

        print("\n👤 CLIENT TIER ACCESS TESTING")
        print("-" * 35)
        
        # Client tier access tests
        client_tests = [
            self.test_client_tier_access
        ]
        
        client_passed = 0
        for test in client_tests:
            if test():
                client_passed += 1

        # Summary
        total_tests = len(tier_tests) + len(provider_tests) + len(ai_tests) + len(agency_tests) + len(client_tests)
        total_passed = tier_passed + provider_passed + ai_passed + agency_passed + client_passed
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"🎯 Tier-Based Assessment: {tier_passed}/{len(tier_tests)} passed")
        print(f"🏢 Enhanced Service Provider: {provider_passed}/{len(provider_tests)} passed")
        print(f"🤖 AI & Localization: {ai_passed}/{len(ai_tests)} passed")
        print(f"🏛️ Agency Tier Management: {agency_passed}/{len(agency_tests)} passed")
        print(f"👤 Client Tier Access: {client_passed}/{len(client_tests)} passed")
        print("-" * 60)
        print(f"📈 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({(total_passed/total_tests*100):.1f}%)")
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Tier-based assessment system is fully operational.")
        elif total_passed >= total_tests * 0.8:
            print("✅ GOOD: Most tests passed. Minor issues may need attention.")
        elif total_passed >= total_tests * 0.6:
            print("⚠️ PARTIAL: Some major features working. Significant issues need fixing.")
        else:
            print("❌ CRITICAL: Major functionality broken. Immediate attention required.")
        
        print(f"\nTest completed: {datetime.now().isoformat()}")
        return total_passed >= total_tests * 0.8

def main():
    """Main test execution"""
    tester = TierBasedAssessmentTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()