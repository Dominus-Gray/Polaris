#!/usr/bin/env python3
"""
Targeted Backend Testing for Failed Endpoints
Focuses on the specific endpoints that failed in the production readiness test
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://polaris-inspector.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class TargetedEndpointTester:
    def __init__(self):
        self.tokens = {}
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def authenticate_all_users(self):
        """Authenticate all QA users"""
        self.log_result("🔐 Authenticating users...")
        
        for role, creds in QA_CREDENTIALS.items():
            try:
                response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": creds["email"],
                    "password": creds["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data["access_token"]
                    self.log_result(f"✅ {role.title()} authenticated")
                else:
                    self.log_result(f"❌ {role.title()} auth failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_result(f"❌ {role.title()} auth error: {str(e)}")
                return False
        
        return True
    
    def test_failed_endpoints(self):
        """Test the specific endpoints that failed"""
        self.log_result("\n🔍 Testing Failed Endpoints with Detailed Error Analysis...")
        
        # Test 1: AI Content Generation (422 error)
        self.log_result("\n1. Testing AI Content Generation...")
        try:
            content_request = {
                "content_type": "checklist",
                "area_id": "area5",
                "topic": "Cybersecurity Compliance for Government Contracting",
                "target_audience": "small_business"
            }
            response = requests.post(f"{BASE_URL}/knowledge-base/generate-content", 
                                   json=content_request, 
                                   headers={"Authorization": f"Bearer {self.tokens['navigator']}"})
            self.log_result(f"   Status: {response.status_code}")
            if response.status_code != 200:
                self.log_result(f"   Error: {response.text}")
        except Exception as e:
            self.log_result(f"   Exception: {str(e)}")
        
        # Test 2: Agency Theme Configuration (422 error)
        self.log_result("\n2. Testing Agency Theme Configuration...")
        try:
            theme_config = {
                "primary_color": "#1e40af",
                "secondary_color": "#f59e0b",
                "logo_url": "https://example.com/agency-logo.png",
                "branding_name": "San Antonio Business Development Agency",
                "contact_info": {
                    "phone": "(210) 555-0123",
                    "email": "contact@sabda.gov",
                    "address": "123 Main St, San Antonio, TX 78205"
                }
            }
            response = requests.post(f"{BASE_URL}/agency/theme", 
                                   json=theme_config, 
                                   headers={"Authorization": f"Bearer {self.tokens['agency']}"})
            self.log_result(f"   Status: {response.status_code}")
            if response.status_code != 200:
                self.log_result(f"   Error: {response.text}")
        except Exception as e:
            self.log_result(f"   Exception: {str(e)}")
        
        # Test 3: Certificate Generation with Branding (403 error)
        self.log_result("\n3. Testing Enhanced Certificate Generation...")
        try:
            cert_request = {
                "client_id": "test-client-id",
                "assessment_results": {
                    "overall_score": 85,
                    "areas_completed": ["area1", "area2", "area5"],
                    "certification_level": "procurement_ready"
                },
                "agency_branding": True
            }
            response = requests.post(f"{BASE_URL}/certificates/generate-branded", 
                                   json=cert_request, 
                                   headers={"Authorization": f"Bearer {self.tokens['agency']}"})
            self.log_result(f"   Status: {response.status_code}")
            if response.status_code != 200:
                self.log_result(f"   Error: {response.text}")
        except Exception as e:
            self.log_result(f"   Exception: {str(e)}")
        
        # Test 4: Notification System
        self.log_result("\n4. Testing Notification System...")
        try:
            # Test correct endpoint path
            response = requests.get(f"{BASE_URL}/notifications/my", 
                                  headers={"Authorization": f"Bearer {self.tokens['client']}"})
            self.log_result(f"   GET /notifications/my Status: {response.status_code}")
            if response.status_code != 200:
                self.log_result(f"   Error: {response.text}")
            
            # Test send notification
            notification_data = {
                "recipient_id": "test-user-id",
                "type": "service_request_update",
                "title": "Service Request Update",
                "message": "Your service request has been updated",
                "action_url": "/service-requests/123"
            }
            response = requests.post(f"{BASE_URL}/notifications/send", 
                                   json=notification_data, 
                                   headers={"Authorization": f"Bearer {self.tokens['navigator']}"})
            self.log_result(f"   POST /notifications/send Status: {response.status_code}")
            if response.status_code != 200:
                self.log_result(f"   Error: {response.text}")
        except Exception as e:
            self.log_result(f"   Exception: {str(e)}")
        
        # Test 5: Check what endpoints actually exist
        self.log_result("\n5. Testing Endpoint Existence...")
        test_endpoints = [
            ("/public/white-label/test-agency-id", "POST"),
            ("/og-image/generate", "POST"),
            ("/opportunities/search", "GET"),
            ("/business-profile/verify-document", "POST"),
            ("/data/export", "POST"),
            ("/admin/bulk-operations", "POST")
        ]
        
        for endpoint, method in test_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}", 
                                          headers={"Authorization": f"Bearer {self.tokens['client']}"})
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", 
                                           json={}, 
                                           headers={"Authorization": f"Bearer {self.tokens['client']}"})
                self.log_result(f"   {method} {endpoint}: {response.status_code}")
                if response.status_code == 404:
                    self.log_result(f"      ❌ Endpoint not implemented")
                elif response.status_code in [422, 400]:
                    self.log_result(f"      ✅ Endpoint exists but validation failed")
                elif response.status_code == 403:
                    self.log_result(f"      ✅ Endpoint exists but permission denied")
                elif response.status_code == 405:
                    self.log_result(f"      ❌ Method not allowed")
            except Exception as e:
                self.log_result(f"   {method} {endpoint}: Exception - {str(e)}")

def main():
    """Main test execution"""
    tester = TargetedEndpointTester()
    
    try:
        if not tester.authenticate_all_users():
            print("❌ Authentication failed")
            sys.exit(1)
        
        tester.test_failed_endpoints()
        print("\n✅ Targeted endpoint testing completed")
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()