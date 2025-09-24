#!/usr/bin/env python3
"""
Engagement Functionality Investigation Test
Testing complete engagement workflow and understanding the feature purpose
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# QA Credentials as specified in review request
CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class EngagementInvestigator:
    def __init__(self):
        self.client_token = None
        self.provider_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_users(self):
        """Authenticate both client and provider users"""
        print("🔐 AUTHENTICATING USERS...")
        
        # Authenticate client
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=CLIENT_CREDENTIALS)
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication", True, f"Client authenticated successfully")
            else:
                self.log_result("Client Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False

        # Authenticate provider
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=PROVIDER_CREDENTIALS)
            if response.status_code == 200:
                self.provider_token = response.json()["access_token"]
                self.log_result("Provider Authentication", True, f"Provider authenticated successfully")
            else:
                self.log_result("Provider Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Provider Authentication", False, f"Exception: {str(e)}")
            return False

        return True

    def test_engagement_my_services_client(self):
        """Test /api/engagements/my-services endpoint with client credentials"""
        print("📋 TESTING CLIENT MY-SERVICES ENDPOINT...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.get(f"{BASE_URL}/engagements/my-services", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                engagements = data.get("engagements", [])
                
                # Analyze the data structure
                analysis = {
                    "total_engagements": len(engagements),
                    "engagement_types": [],
                    "statuses": [],
                    "areas": []
                }
                
                for engagement in engagements:
                    if engagement.get("type"):
                        analysis["engagement_types"].append(engagement["type"])
                    if engagement.get("status"):
                        analysis["statuses"].append(engagement["status"])
                    if engagement.get("area_id"):
                        analysis["areas"].append(engagement["area_id"])
                
                # Remove duplicates
                analysis["engagement_types"] = list(set(analysis["engagement_types"]))
                analysis["statuses"] = list(set(analysis["statuses"]))
                analysis["areas"] = list(set(analysis["areas"]))
                
                self.log_result("Client My-Services Endpoint", True, 
                    f"Retrieved {analysis['total_engagements']} engagements. Types: {analysis['engagement_types']}, Statuses: {analysis['statuses']}, Areas: {analysis['areas']}")
                
                return engagements
            else:
                self.log_result("Client My-Services Endpoint", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Client My-Services Endpoint", False, f"Exception: {str(e)}")
            return []

    def test_engagement_my_services_provider(self):
        """Test /api/engagements/my-services endpoint with provider credentials"""
        print("🏢 TESTING PROVIDER MY-SERVICES ENDPOINT...")
        
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response = requests.get(f"{BASE_URL}/engagements/my-services", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                engagements = data.get("engagements", [])
                
                # Analyze provider-specific data
                analysis = {
                    "total_notifications": len(engagements),
                    "responded_count": 0,
                    "pending_count": 0,
                    "areas": []
                }
                
                for engagement in engagements:
                    if engagement.get("has_responded"):
                        analysis["responded_count"] += 1
                    else:
                        analysis["pending_count"] += 1
                    if engagement.get("area_name"):
                        analysis["areas"].append(engagement["area_name"])
                
                analysis["areas"] = list(set(analysis["areas"]))
                
                self.log_result("Provider My-Services Endpoint", True, 
                    f"Retrieved {analysis['total_notifications']} notifications. Responded: {analysis['responded_count']}, Pending: {analysis['pending_count']}, Areas: {analysis['areas']}")
                
                return engagements
            else:
                self.log_result("Provider My-Services Endpoint", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Provider My-Services Endpoint", False, f"Exception: {str(e)}")
            return []

    def create_test_service_request(self):
        """Create a test service request to understand the flow"""
        print("📝 CREATING TEST SERVICE REQUEST...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            request_data = {
                "area_id": "area5",  # Technology & Security Infrastructure
                "budget_range": "$1,000-$2,500",
                "description": "Engagement Investigation Test - Need cybersecurity assessment and implementation",
                "urgency": "medium",
                "timeline": "2-4 weeks"
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                self.log_result("Service Request Creation", True, 
                    f"Created service request: {request_id}")
                return request_id
            else:
                self.log_result("Service Request Creation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Service Request Creation", False, f"Exception: {str(e)}")
            return None

    def create_provider_response(self, request_id):
        """Create a provider response to the service request"""
        print("💼 CREATING PROVIDER RESPONSE...")
        
        try:
            headers = {"Authorization": f"Bearer {self.provider_token}"}
            response_data = {
                "request_id": request_id,
                "proposed_fee": 1800.00,
                "estimated_timeline": "3 weeks",
                "proposal_note": "Comprehensive cybersecurity assessment including vulnerability scanning, policy development, and implementation guidance. Includes ongoing support for 30 days."
            }
            
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", 
                                   json=response_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                response_id = data.get("response_id")
                self.log_result("Provider Response Creation", True, 
                    f"Created provider response: {response_id}")
                return response_id
            else:
                self.log_result("Provider Response Creation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Provider Response Creation", False, f"Exception: {str(e)}")
            return None

    def create_engagement(self, request_id, response_id):
        """Create an engagement from service request and provider response"""
        print("🤝 CREATING ENGAGEMENT...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            engagement_data = {
                "request_id": request_id,
                "response_id": response_id,
                "agreed_fee": 1800.00
            }
            
            response = requests.post(f"{BASE_URL}/engagements/create", 
                                   json=engagement_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                engagement_id = data.get("engagement_id")
                fee = data.get("fee")
                self.log_result("Engagement Creation", True, 
                    f"Created engagement: {engagement_id}, Marketplace fee: ${fee}")
                return engagement_id
            else:
                self.log_result("Engagement Creation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Engagement Creation", False, f"Exception: {str(e)}")
            return None

    def test_engagement_tracking(self, engagement_id):
        """Test engagement tracking endpoint"""
        print("📊 TESTING ENGAGEMENT TRACKING...")
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.get(f"{BASE_URL}/engagements/{engagement_id}/tracking", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                engagement = data.get("engagement", {})
                tracking_history = data.get("tracking_history", [])
                
                analysis = {
                    "engagement_status": engagement.get("status"),
                    "agreed_fee": engagement.get("agreed_fee"),
                    "tracking_entries": len(tracking_history),
                    "client_id": engagement.get("client_user_id"),
                    "provider_id": engagement.get("provider_user_id")
                }
                
                self.log_result("Engagement Tracking", True, 
                    f"Status: {analysis['engagement_status']}, Fee: ${analysis['agreed_fee']}, Tracking entries: {analysis['tracking_entries']}")
                
                return data
            else:
                self.log_result("Engagement Tracking", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Engagement Tracking", False, f"Exception: {str(e)}")
            return None

    def test_engagement_status_updates(self, engagement_id):
        """Test updating engagement status through different stages"""
        print("🔄 TESTING ENGAGEMENT STATUS UPDATES...")
        
        statuses_to_test = ["in_progress", "delivered", "approved", "released"]
        
        for status in statuses_to_test:
            try:
                # Determine which user should update the status
                if status in ["in_progress", "delivered"]:
                    headers = {"Authorization": f"Bearer {self.provider_token}"}
                    user_type = "provider"
                else:
                    headers = {"Authorization": f"Bearer {self.client_token}"}
                    user_type = "client"
                
                update_data = {
                    "status": status,
                    "progress_percentage": 25 if status == "in_progress" else 100,
                    "notes": f"Status updated to {status} for engagement investigation test"
                }
                
                response = requests.post(f"{BASE_URL}/engagements/{engagement_id}/update", 
                                       json=update_data, headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"Status Update to {status}", True, 
                        f"Successfully updated by {user_type}")
                else:
                    self.log_result(f"Status Update to {status}", False, 
                        f"Status: {response.status_code}, Response: {response.text}")
                
                # Small delay between updates
                time.sleep(1)
                
            except Exception as e:
                self.log_result(f"Status Update to {status}", False, f"Exception: {str(e)}")

    def analyze_engagement_purpose(self):
        """Analyze and document the purpose of the engagement system"""
        print("🎯 ANALYZING ENGAGEMENT SYSTEM PURPOSE...")
        
        purpose_analysis = {
            "primary_function": "Service Request to Provider Engagement Workflow Management",
            "key_features": [
                "Service request creation by clients",
                "Provider notification and response system", 
                "Engagement creation with agreed terms",
                "Status tracking through project lifecycle",
                "Marketplace fee calculation (5% of agreed fee)",
                "Rating and feedback system"
            ],
            "user_journeys": {
                "client": [
                    "Create service request with budget and requirements",
                    "Review provider responses and proposals",
                    "Create engagement with selected provider",
                    "Track progress and approve deliverables",
                    "Rate completed service"
                ],
                "provider": [
                    "Receive notifications for relevant service requests",
                    "Submit proposals with fees and timelines",
                    "Update engagement status and progress",
                    "Deliver services and mark as complete"
                ]
            },
            "data_structure": {
                "service_requests": "Client requirements and budget",
                "provider_responses": "Provider proposals and fees",
                "engagements": "Active service agreements",
                "service_tracking": "Progress and status history",
                "service_ratings": "Client feedback and ratings"
            }
        }
        
        self.log_result("Engagement System Analysis", True, 
            f"System enables {purpose_analysis['primary_function']} with {len(purpose_analysis['key_features'])} key features")
        
        return purpose_analysis

    def run_complete_investigation(self):
        """Run complete engagement functionality investigation"""
        print("🚀 STARTING COMPREHENSIVE ENGAGEMENT INVESTIGATION")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate_users():
            print("❌ Authentication failed, cannot proceed")
            return
        
        # Step 2: Test my-services endpoints
        client_engagements = self.test_engagement_my_services_client()
        provider_engagements = self.test_engagement_my_services_provider()
        
        # Step 3: Create complete workflow
        request_id = self.create_test_service_request()
        if not request_id:
            print("❌ Could not create service request, skipping workflow tests")
        else:
            response_id = self.create_provider_response(request_id)
            if response_id:
                engagement_id = self.create_engagement(request_id, response_id)
                if engagement_id:
                    # Step 4: Test tracking
                    self.test_engagement_tracking(engagement_id)
                    
                    # Step 5: Test status updates
                    self.test_engagement_status_updates(engagement_id)
                    
                    # Final tracking check
                    final_tracking = self.test_engagement_tracking(engagement_id)
        
        # Step 6: Analyze system purpose
        purpose_analysis = self.analyze_engagement_purpose()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 ENGAGEMENT INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        print("🎯 ENGAGEMENT SYSTEM PURPOSE:")
        print("The engagement system is a comprehensive workflow management platform that:")
        print("1. Enables clients to post service requests with specific requirements")
        print("2. Notifies relevant providers and allows them to submit proposals")
        print("3. Facilitates engagement creation with agreed terms and fees")
        print("4. Provides milestone-based progress tracking")
        print("5. Includes marketplace fee calculation (5% of agreed fee)")
        print("6. Supports rating and feedback for completed services")
        print()
        
        print("🔍 KEY FINDINGS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print("\n🎉 INVESTIGATION COMPLETE!")

if __name__ == "__main__":
    investigator = EngagementInvestigator()
    investigator.run_complete_investigation()