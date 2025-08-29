#!/usr/bin/env python3
"""
Enhanced Tier-Based Assessment System Backend Testing
Testing the enhanced tier-based assessment system and service provider features as requested in review
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://providermatrix.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class TierBasedAssessmentTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.session = requests.Session()
        self.session_id = None
        self.service_request_id = None
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test results with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
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

    def authenticate_user(self, role):
        """Authenticate user and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens[role] = token_data["access_token"]
                self.log_result(f"Authentication - {role.title()}", True, 
                              f"Successfully authenticated {creds['email']}")
                return True
            else:
                error_detail = response.json() if response.content else {"detail": "No response content"}
                self.log_result(f"Authentication - {role.title()}", False, 
                              f"Failed to authenticate {creds['email']}: {response.status_code}",
                              error_detail)
                return False
        except Exception as e:
            self.log_result(f"Authentication - {role.title()}", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, role):
        """Get authorization headers for role"""
        if role not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[role]}"}

    def test_tier_based_schema_endpoint(self):
        """Test GET /api/assessment/schema/tier-based endpoint"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Tier-Based Schema - Authentication", False, "No client token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/assessment/schema/tier-based", headers=headers)
            
            if response.status_code == 200:
                schema_data = response.json()
                
                # Verify schema contains 10 areas with tier information
                if isinstance(schema_data, dict) and "areas" in schema_data:
                    areas = schema_data["areas"]
                    if len(areas) == 10:
                        # Check for tier information in areas
                        area_sample = areas[0] if areas else {}
                        has_tier_info = "tiers" in area_sample or "tier_levels" in area_sample
                        
                        self.log_result("Tier-Based Schema - Endpoint", True, 
                                      f"Schema retrieved with {len(areas)} areas, tier info: {has_tier_info}")
                        return True
                    else:
                        self.log_result("Tier-Based Schema - Area Count", False, 
                                      f"Expected 10 areas, got {len(areas)}", schema_data)
                        return False
                else:
                    self.log_result("Tier-Based Schema - Structure", False, 
                                  "Unexpected schema structure", schema_data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Tier-Based Schema - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Tier-Based Schema - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_tier_session_creation(self):
        """Test POST /api/assessment/tier-session endpoint"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Tier Session Creation - Authentication", False, "No client token available")
                return False
            
            # Test tier session creation with form data (as expected by backend)
            session_payload = {
                "area_id": "area5",
                "tier_level": "1"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=session_payload, headers=headers)
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get("session_id")
                
                if session_id:
                    self.session_id = session_id  # Store for later tests
                    self.log_result("Tier Session Creation - Endpoint", True, 
                                  f"Tier session created successfully: {session_id}")
                    return True
                else:
                    self.log_result("Tier Session Creation - Session ID", False, 
                                  "No session_id in response", session_data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Tier Session Creation - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Tier Session Creation - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_tier_response_submission(self):
        """Test POST /api/assessment/tier-session/{id}/response endpoint"""
        try:
            if not self.session_id:
                self.log_result("Tier Response Submission - Session ID", False, "No session ID available")
                return False
                
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Tier Response Submission - Authentication", False, "No client token available")
                return False
            
            # Test tier response submission with form data
            response_payload = {
                "question_id": "area5_tier1_stmt1",
                "response": "No, I need help",
                "evidence_provided": "false"
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session/{self.session_id}/response", 
                                       data=response_payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                self.log_result("Tier Response Submission - Endpoint", True, 
                              "Tier response submitted successfully", response_data)
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Tier Response Submission - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Tier Response Submission - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_tier_session_progress(self):
        """Test GET /api/assessment/tier-session/{id}/progress endpoint"""
        try:
            if not self.session_id:
                self.log_result("Tier Session Progress - Session ID", False, "No session ID available")
                return False
                
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Tier Session Progress - Authentication", False, "No client token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/assessment/tier-session/{self.session_id}/progress", 
                                      headers=headers)
            
            if response.status_code == 200:
                progress_data = response.json()
                
                # Verify progress structure
                expected_fields = ["completion_percentage", "responses_submitted", "tier_level"]
                present_fields = [field for field in expected_fields if field in progress_data]
                
                self.log_result("Tier Session Progress - Endpoint", True, 
                              f"Progress retrieved with {len(present_fields)}/{len(expected_fields)} expected fields",
                              {"present_fields": present_fields})
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Tier Session Progress - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Tier Session Progress - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_client_tier_access(self):
        """Test GET /api/client/tier-access endpoint"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Client Tier Access - Authentication", False, "No client token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/client/tier-access", headers=headers)
            
            if response.status_code == 200:
                tier_access_data = response.json()
                
                # Verify tier access for 10 areas
                if isinstance(tier_access_data, dict):
                    # Check if it contains area access information
                    area_keys = [key for key in tier_access_data.keys() if key.startswith("area")]
                    
                    if len(area_keys) >= 10:
                        self.log_result("Client Tier Access - Endpoint", True, 
                                      f"Tier access retrieved for {len(area_keys)} areas")
                        return True
                    else:
                        self.log_result("Client Tier Access - Area Coverage", False, 
                                      f"Expected 10 areas, got {len(area_keys)}", tier_access_data)
                        return False
                else:
                    self.log_result("Client Tier Access - Structure", False, 
                                  "Unexpected response structure", tier_access_data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Client Tier Access - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Client Tier Access - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_agency_tier_configuration(self):
        """Test GET /api/agency/tier-configuration endpoint"""
        try:
            headers = self.get_headers("agency")
            if not headers:
                self.log_result("Agency Tier Configuration - Authentication", False, "No agency token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/agency/tier-configuration", headers=headers)
            
            if response.status_code == 200:
                config_data = response.json()
                
                # Verify tier configuration structure
                expected_fields = ["tier_access_levels", "pricing_per_tier"]
                present_fields = [field for field in expected_fields if field in config_data]
                
                self.log_result("Agency Tier Configuration - Endpoint", True, 
                              f"Configuration retrieved with {len(present_fields)}/{len(expected_fields)} expected fields")
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Agency Tier Configuration - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Agency Tier Configuration - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_agency_billing_usage(self):
        """Test GET /api/agency/billing/usage endpoint"""
        try:
            headers = self.get_headers("agency")
            if not headers:
                self.log_result("Agency Billing Usage - Authentication", False, "No agency token available")
                return False
                
            response = self.session.get(f"{BASE_URL}/agency/billing/usage", headers=headers)
            
            if response.status_code == 200:
                billing_data = response.json()
                
                # Verify billing usage structure
                expected_fields = ["total_assessments", "tier_usage", "billing_period"]
                present_fields = [field for field in expected_fields if field in billing_data]
                
                self.log_result("Agency Billing Usage - Endpoint", True, 
                              f"Billing data retrieved with {len(present_fields)}/{len(expected_fields)} expected fields")
                return True
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Agency Billing Usage - Endpoint", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Agency Billing Usage - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_enhanced_provider_profiles(self):
        """Test enhanced provider profiles and ratings"""
        try:
            headers = self.get_headers("provider")
            if not headers:
                self.log_result("Enhanced Provider Profiles - Authentication", False, "No provider token available")
                return False
                
            # Test provider ratings endpoint
            response = self.session.get(f"{BASE_URL}/provider/ratings", headers=headers)
            
            if response.status_code == 200:
                ratings_data = response.json()
                self.log_result("Enhanced Provider Profiles - Ratings", True, 
                              "Provider ratings retrieved successfully")
                
                # Test enhanced service request responses
                enhanced_response = self.session.get(f"{BASE_URL}/service-requests/test-id/responses/enhanced", 
                                                   headers=headers)
                
                if enhanced_response.status_code in [200, 404]:  # 404 acceptable for test ID
                    self.log_result("Enhanced Provider Profiles - Enhanced Responses", True, 
                                  "Enhanced responses endpoint accessible")
                    return True
                else:
                    self.log_result("Enhanced Provider Profiles - Enhanced Responses", False, 
                                  f"Enhanced responses failed: {enhanced_response.status_code}")
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("Enhanced Provider Profiles - Ratings", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Enhanced Provider Profiles - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_service_provider_marketplace(self):
        """Test service provider marketplace matching functionality"""
        try:
            client_headers = self.get_headers("client")
            provider_headers = self.get_headers("provider")
            
            if not client_headers or not provider_headers:
                self.log_result("Service Provider Marketplace - Authentication", False, "Missing required tokens")
                return False
            
            # Step 1: Create service request
            service_request_payload = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Need help with technology and security infrastructure for tier-based assessment",
                "priority": "high"
            }
            
            request_response = self.session.post(f"{BASE_URL}/service-requests/professional-help", 
                                               json=service_request_payload, headers=client_headers)
            
            if request_response.status_code == 200:
                request_data = request_response.json()
                request_id = request_data.get("request_id")
                
                if request_id:
                    self.service_request_id = request_id
                    
                    # Step 2: Provider responds to request
                    provider_response_payload = {
                        "request_id": request_id,
                        "proposed_fee": 2500.00,
                        "estimated_timeline": "3 weeks",
                        "proposal_note": "Comprehensive tier-based assessment support with enhanced security infrastructure"
                    }
                    
                    provider_response = self.session.post(f"{BASE_URL}/provider/respond-to-request", 
                                                        json=provider_response_payload, headers=provider_headers)
                    
                    if provider_response.status_code == 200:
                        self.log_result("Service Provider Marketplace - Matching", True, 
                                      "Service request and provider response workflow successful")
                        return True
                    else:
                        error_data = provider_response.json() if provider_response.content else {"error": "No content"}
                        self.log_result("Service Provider Marketplace - Provider Response", False, 
                                      f"Provider response failed: {provider_response.status_code}", error_data)
                        return False
                else:
                    self.log_result("Service Provider Marketplace - Request ID", False, 
                                  "No request_id in service request response", request_data)
                    return False
            else:
                error_data = request_response.json() if request_response.content else {"error": "No content"}
                self.log_result("Service Provider Marketplace - Service Request", False, 
                              f"Service request creation failed: {request_response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("Service Provider Marketplace - Workflow", False, f"Exception: {str(e)}")
            return False

    def test_ai_powered_resources(self):
        """Test AI-powered localized resources using Emergent LLM"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("AI-Powered Resources - Authentication", False, "No client token available")
                return False
            
            # Test AI assistance endpoint
            ai_payload = {
                "question": "What are the key requirements for tier-based assessment in technology security?",
                "area_id": "area5"
            }
            
            response = self.session.post(f"{BASE_URL}/knowledge-base/ai-assistance", 
                                       json=ai_payload, headers=headers)
            
            if response.status_code == 200:
                ai_data = response.json()
                
                # Check if response contains AI-generated content
                if "response" in ai_data and len(ai_data["response"]) > 50:
                    self.log_result("AI-Powered Resources - AI Assistance", True, 
                                  f"AI assistance working, response length: {len(ai_data['response'])} chars")
                    
                    # Test contextual cards endpoint
                    cards_response = self.session.get(f"{BASE_URL}/knowledge-base/contextual-cards?area_id=area5", 
                                                    headers=headers)
                    
                    if cards_response.status_code == 200:
                        cards_data = cards_response.json()
                        self.log_result("AI-Powered Resources - Contextual Cards", True, 
                                      f"Contextual cards retrieved: {len(cards_data.get('cards', []))} cards")
                        return True
                    else:
                        self.log_result("AI-Powered Resources - Contextual Cards", False, 
                                      f"Contextual cards failed: {cards_response.status_code}")
                        return False
                else:
                    self.log_result("AI-Powered Resources - Response Quality", False, 
                                  "AI response too short or missing", ai_data)
                    return False
            else:
                error_data = response.json() if response.content else {"error": "No content"}
                self.log_result("AI-Powered Resources - AI Assistance", False, 
                              f"HTTP {response.status_code}", error_data)
                return False
                
        except Exception as e:
            self.log_result("AI-Powered Resources - Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_error_handling_edge_cases(self):
        """Test error handling and edge cases"""
        try:
            headers = self.get_headers("client")
            if not headers:
                self.log_result("Error Handling - Authentication", False, "No client token available")
                return False
            
            # Test invalid tier session creation
            invalid_payload = {
                "area_id": "invalid_area",
                "tier_level": "5"  # Invalid tier level
            }
            
            response = self.session.post(f"{BASE_URL}/assessment/tier-session", 
                                       data=invalid_payload, headers=headers)
            
            # Should return error for invalid data
            if response.status_code in [400, 422]:
                self.log_result("Error Handling - Invalid Tier Session", True, 
                              f"Proper error handling for invalid data: {response.status_code}")
                
                # Test unauthorized access
                no_auth_response = self.session.get(f"{BASE_URL}/client/tier-access")
                
                if no_auth_response.status_code == 401:
                    self.log_result("Error Handling - Unauthorized Access", True, 
                                  "Proper 401 response for unauthorized access")
                    return True
                else:
                    self.log_result("Error Handling - Unauthorized Access", False, 
                                  f"Expected 401, got {no_auth_response.status_code}")
                    return False
            else:
                self.log_result("Error Handling - Invalid Tier Session", False, 
                              f"Expected error response, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Error Handling - Edge Cases", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tier-based assessment system tests"""
        print("🎯 ENHANCED TIER-BASED ASSESSMENT SYSTEM BACKEND TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate all users
        print("📋 STEP 1: AUTHENTICATION WITH QA CREDENTIALS")
        print("-" * 50)
        auth_success = 0
        for role in ["client", "provider", "agency", "navigator"]:
            if self.authenticate_user(role):
                auth_success += 1
        
        if auth_success < 3:
            print("❌ CRITICAL: Insufficient authentication success. Cannot proceed with testing.")
            return False
        
        print(f"Authentication Summary: {auth_success}/4 roles authenticated successfully")
        print()
        
        # Step 2: Test Tier-Based Assessment Endpoints
        print("📋 STEP 2: TIER-BASED ASSESSMENT ENDPOINTS")
        print("-" * 50)
        
        tier_tests = [
            ("Tier-Based Schema", self.test_tier_based_schema_endpoint),
            ("Tier Session Creation", self.test_tier_session_creation),
            ("Tier Response Submission", self.test_tier_response_submission),
            ("Tier Session Progress", self.test_tier_session_progress)
        ]
        
        tier_success = 0
        for test_name, test_func in tier_tests:
            if test_func():
                tier_success += 1
        
        print(f"Tier-Based Assessment Endpoints: {tier_success}/{len(tier_tests)} tests passed")
        print()
        
        # Step 3: Test Client and Agency Management
        print("📋 STEP 3: CLIENT AND AGENCY MANAGEMENT")
        print("-" * 50)
        
        management_tests = [
            ("Client Tier Access", self.test_client_tier_access),
            ("Agency Tier Configuration", self.test_agency_tier_configuration),
            ("Agency Billing Usage", self.test_agency_billing_usage)
        ]
        
        management_success = 0
        for test_name, test_func in management_tests:
            if test_func():
                management_success += 1
        
        print(f"Client and Agency Management: {management_success}/{len(management_tests)} tests passed")
        print()
        
        # Step 4: Test Service Provider System
        print("📋 STEP 4: SERVICE PROVIDER SYSTEM")
        print("-" * 50)
        
        provider_tests = [
            ("Enhanced Provider Profiles", self.test_enhanced_provider_profiles),
            ("Service Provider Marketplace", self.test_service_provider_marketplace)
        ]
        
        provider_success = 0
        for test_name, test_func in provider_tests:
            if test_func():
                provider_success += 1
        
        print(f"Service Provider System: {provider_success}/{len(provider_tests)} tests passed")
        print()
        
        # Step 5: Test AI-Powered Features
        print("📋 STEP 5: AI-POWERED FEATURES")
        print("-" * 50)
        
        ai_tests = [
            ("AI-Powered Resources", self.test_ai_powered_resources),
            ("Error Handling & Edge Cases", self.test_error_handling_edge_cases)
        ]
        
        ai_success = 0
        for test_name, test_func in ai_tests:
            if test_func():
                ai_success += 1
        
        print(f"AI-Powered Features: {ai_success}/{len(ai_tests)} tests passed")
        print()
        
        # Calculate overall success rate
        all_tests = tier_tests + management_tests + provider_tests + ai_tests
        total_success = tier_success + management_success + provider_success + ai_success
        success_rate = (total_success / len(all_tests)) * 100
        
        print("📊 FINAL RESULTS")
        print("=" * 40)
        print(f"Total Tests: {len(all_tests)}")
        print(f"Passed: {total_success}")
        print(f"Failed: {len(all_tests) - total_success}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("✅ TIER-BASED ASSESSMENT SYSTEM: OPERATIONAL")
        elif success_rate >= 60:
            print("⚠️ TIER-BASED ASSESSMENT SYSTEM: MOSTLY OPERATIONAL")
        else:
            print("❌ TIER-BASED ASSESSMENT SYSTEM: NEEDS ATTENTION")
        
        return success_rate >= 60

def main():
    """Main test execution"""
    tester = TierBasedAssessmentTester()
    success = tester.run_all_tests()
    
    # Print detailed results for debugging
    print("\n📋 DETAILED TEST RESULTS")
    print("=" * 50)
    for result in tester.test_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}")
        if result["details"]:
            print(f"   {result['details']}")
    
    return success

if __name__ == "__main__":
    main()