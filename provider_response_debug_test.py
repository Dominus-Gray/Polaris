#!/usr/bin/env python3
"""
Provider Response Debug Testing
Focused debugging of the specific validation issues identified.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://providermatrix.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ProviderResponseDebugger:
    def __init__(self):
        self.tokens = {}
        self.service_request_id = None
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def login_user(self, role):
        """Login user and store token"""
        creds = QA_CREDENTIALS[role]
        payload = {
            "email": creds["email"],
            "password": creds["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"✅ {role.title()} login successful")
                return True
            else:
                self.log_result(f"❌ {role.title()} login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} login error: {str(e)}")
            return False
    
    def debug_service_request_creation(self):
        """Debug service request creation and inspect response"""
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        payload = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Debug test - technology security infrastructure assessment",
            "priority": "high"
        }
        
        self.log_result("🔍 DEBUG: Creating service request...")
        self.log_result(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
            
            self.log_result(f"Response Status: {response.status_code}")
            self.log_result(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Response Data: {json.dumps(data, indent=2)}")
                self.service_request_id = data.get("request_id")
                self.log_result(f"✅ Service request created: {self.service_request_id}")
                return True
            else:
                self.log_result(f"❌ Service request creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Service request creation error: {str(e)}")
            return False
    
    def debug_provider_response_creation(self):
        """Debug provider response creation with detailed logging"""
        if not self.service_request_id:
            self.log_result("❌ No service request ID available")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        payload = {
            "request_id": self.service_request_id,
            "proposed_fee": 2500.00,
            "estimated_timeline": "2-4 weeks",
            "proposal_note": "Debug test response - comprehensive technology security infrastructure assessment including network security audit, vulnerability testing, and implementation of security protocols."
        }
        
        self.log_result("🔍 DEBUG: Creating provider response...")
        self.log_result(f"Service Request ID: {self.service_request_id}")
        self.log_result(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=payload, headers=headers)
            
            self.log_result(f"Response Status: {response.status_code}")
            self.log_result(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Response Data: {json.dumps(data, indent=2)}")
                self.log_result("✅ Provider response created successfully")
                return data
            else:
                self.log_result(f"❌ Provider response creation failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Provider response creation error: {str(e)}")
            return None
    
    def debug_response_retrieval(self):
        """Debug response retrieval endpoints"""
        if not self.service_request_id:
            self.log_result("❌ No service request ID available")
            return False
        
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        # Test different retrieval endpoints
        endpoints_to_test = [
            f"/service-requests/{self.service_request_id}/responses",
            f"/service-requests/{self.service_request_id}",
            f"/client/my-services"
        ]
        
        for endpoint in endpoints_to_test:
            self.log_result(f"🔍 DEBUG: Testing endpoint {endpoint}")
            
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=client_headers)
                
                self.log_result(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"Response Data: {json.dumps(data, indent=2)}")
                else:
                    self.log_result(f"Error Response: {response.text}")
                    
            except Exception as e:
                self.log_result(f"❌ Error testing {endpoint}: {str(e)}")
    
    def debug_database_collections(self):
        """Debug by checking what's in the database collections"""
        # This would require direct database access, but we can infer from API responses
        self.log_result("🔍 DEBUG: Checking database state via API...")
        
        # Check client's service requests
        client_headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/client/my-services", headers=client_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Client services: {json.dumps(data, indent=2)}")
            else:
                self.log_result(f"Failed to get client services: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result(f"❌ Error checking client services: {str(e)}")
        
        # Check provider's responses/notifications
        provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/provider/notifications", headers=provider_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Provider notifications: {json.dumps(data, indent=2)}")
            else:
                self.log_result(f"Failed to get provider notifications: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result(f"❌ Error checking provider notifications: {str(e)}")
    
    def run_debug_session(self):
        """Run comprehensive debugging session"""
        self.log_result("🐛 Starting Provider Response Debug Session")
        self.log_result("=" * 60)
        
        # Login users
        if not self.login_user("client") or not self.login_user("provider"):
            self.log_result("❌ Failed to login users")
            return False
        
        # Debug service request creation
        self.log_result("\n📋 STEP 1: Debug Service Request Creation")
        if not self.debug_service_request_creation():
            return False
        
        # Debug provider response creation
        self.log_result("\n📋 STEP 2: Debug Provider Response Creation")
        provider_response = self.debug_provider_response_creation()
        
        # Debug response retrieval
        self.log_result("\n📋 STEP 3: Debug Response Retrieval")
        self.debug_response_retrieval()
        
        # Debug database state
        self.log_result("\n📋 STEP 4: Debug Database State")
        self.debug_database_collections()
        
        return True

def main():
    """Main debug execution"""
    debugger = ProviderResponseDebugger()
    
    try:
        debugger.run_debug_session()
        print("\n🔍 DEBUG SESSION COMPLETED")
        
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()