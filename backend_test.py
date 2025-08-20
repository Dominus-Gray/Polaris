#!/usr/bin/env python3
"""
QA Credentials E2E Backend Testing
Tests the exact workflow specified in the review request.
Note: Using .example.com domains due to backend email validation restrictions on .test domains.
The workflow and credentials structure match the review request exactly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://polaris-navigator-1.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "navigator": {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class QAWorkflowTester:
    def __init__(self):
        self.tokens = {}
        self.license_code = None
        self.results = {
            "navigator": {"registration": "PENDING", "login": "PENDING"},
            "agency": {"registration": "PENDING", "login": "PENDING"},
            "client": {"registration": "PENDING", "login": "PENDING"},
            "provider": {"registration": "PENDING", "login": "PENDING"},
            "license_code": None,
            "errors": []
        }
    
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def register_user(self, role, email, password, license_code=None):
        """Register a user with the specified role"""
        payload = {
            "email": email,
            "password": password,
            "role": role,
            "terms_accepted": True
        }
        
        if license_code:
            payload["license_code"] = license_code
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            
            if response.status_code == 400 and ("already registered" in response.text.lower() or "already exists" in response.text.lower()):
                self.log_result(f"✅ {role.title()} already exists, proceeding to login")
                self.results[role]["registration"] = "EXISTS"
                return True
            elif response.status_code == 200:
                self.log_result(f"✅ {role.title()} registration successful")
                self.results[role]["registration"] = "SUCCESS"
                return True
            else:
                self.log_result(f"❌ {role.title()} registration failed: {response.status_code} - {response.text}")
                self.results[role]["registration"] = f"FAILED ({response.status_code})"
                self.results["errors"].append(f"{role} registration: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} registration error: {str(e)}")
            self.results[role]["registration"] = f"ERROR ({str(e)})"
            self.results["errors"].append(f"{role} registration error: {str(e)}")
            return False
    
    def login_user(self, role, email, password):
        """Login user and store token"""
        payload = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.log_result(f"✅ {role.title()} login successful")
                self.results[role]["login"] = "SUCCESS"
                return True
            else:
                self.log_result(f"❌ {role.title()} login failed: {response.status_code} - {response.text}")
                self.results[role]["login"] = f"FAILED ({response.status_code})"
                self.results["errors"].append(f"{role} login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ {role.title()} login error: {str(e)}")
            self.results[role]["login"] = f"ERROR ({str(e)})"
            self.results["errors"].append(f"{role} login error: {str(e)}")
            return False
    
    def get_pending_agencies(self):
        """Get pending agencies as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/navigator/agencies/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                agencies = data.get("agencies", [])
                
                # Find our QA agency
                qa_agency = None
                for agency in agencies:
                    if agency.get("email") == QA_CREDENTIALS["agency"]["email"]:
                        qa_agency = agency
                        break
                
                if qa_agency:
                    self.log_result(f"✅ Found QA agency in pending list: {qa_agency['email']}")
                    return qa_agency["id"]
                else:
                    self.log_result(f"⚠️ QA agency not found in pending list - may already be approved")
                    # Try to login directly to check if already approved
                    return "already_approved"
            else:
                self.log_result(f"❌ Failed to get pending agencies: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Error getting pending agencies: {str(e)}")
            return None
    
    def approve_agency(self, agency_id):
        """Approve agency as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        payload = {
            "agency_user_id": agency_id,
            "approval_status": "approved"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/navigator/agencies/approve", json=payload, headers=headers)
            
            if response.status_code == 200:
                self.log_result(f"✅ Agency approval successful")
                return True
            else:
                self.log_result(f"❌ Agency approval failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"Agency approval: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error approving agency: {str(e)}")
            self.results["errors"].append(f"Agency approval error: {str(e)}")
            return False
    
    def generate_licenses(self):
        """Generate license codes as agency"""
        headers = {"Authorization": f"Bearer {self.tokens['agency']}"}
        payload = {"quantity": 3}
        
        try:
            response = requests.post(f"{BASE_URL}/agency/licenses/generate", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                licenses = data.get("licenses", [])
                
                if licenses:
                    # Get first license code
                    first_license = licenses[0]
                    if isinstance(first_license, dict):
                        self.license_code = first_license.get("license_code")
                    else:
                        self.license_code = str(first_license)
                    
                    self.results["license_code"] = f"****{self.license_code[-4:]}" if self.license_code else "NONE"
                    self.log_result(f"✅ Generated {len(licenses)} licenses, first: ****{self.license_code[-4:]}")
                    return True
                else:
                    self.log_result(f"❌ No licenses generated")
                    return False
            else:
                self.log_result(f"❌ License generation failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"License generation: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error generating licenses: {str(e)}")
            self.results["errors"].append(f"License generation error: {str(e)}")
            return False
    
    def get_pending_providers(self):
        """Get pending providers as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        
        try:
            response = requests.get(f"{BASE_URL}/navigator/providers/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                # Find our QA provider
                qa_provider = None
                for provider in providers:
                    if provider.get("email") == QA_CREDENTIALS["provider"]["email"]:
                        qa_provider = provider
                        break
                
                if qa_provider:
                    self.log_result(f"✅ Found QA provider in pending list: {qa_provider['email']}")
                    return qa_provider["id"]
                else:
                    self.log_result(f"⚠️ QA provider not found in pending list - may already be approved")
                    return "already_approved"
            else:
                self.log_result(f"❌ Failed to get pending providers: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Error getting pending providers: {str(e)}")
            return None
    
    def approve_provider(self, provider_id):
        """Approve provider as navigator"""
        headers = {"Authorization": f"Bearer {self.tokens['navigator']}"}
        payload = {
            "provider_user_id": provider_id,
            "approval_status": "approved"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/navigator/providers/approve", json=payload, headers=headers)
            
            if response.status_code == 200:
                self.log_result(f"✅ Provider approval successful")
                return True
            else:
                self.log_result(f"❌ Provider approval failed: {response.status_code} - {response.text}")
                self.results["errors"].append(f"Provider approval: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"❌ Error approving provider: {str(e)}")
            self.results["errors"].append(f"Provider approval error: {str(e)}")
            return False
    
    def run_complete_workflow(self):
        """Execute the complete QA workflow"""
        self.log_result("🚀 Starting QA Credentials E2E Workflow Test")
        self.log_result("=" * 60)
        
        # Step 1: Register and login navigator
        self.log_result("📋 Step 1: Navigator Registration & Login")
        nav_creds = QA_CREDENTIALS["navigator"]
        if self.register_user("navigator", nav_creds["email"], nav_creds["password"]):
            if not self.login_user("navigator", nav_creds["email"], nav_creds["password"]):
                return False
        else:
            return False
        
        # Step 2: Register agency and approve
        self.log_result("\n📋 Step 2: Agency Registration & Approval")
        agency_creds = QA_CREDENTIALS["agency"]
        if self.register_user("agency", agency_creds["email"], agency_creds["password"]):
            # Get pending agencies and approve
            agency_id = self.get_pending_agencies()
            if agency_id == "already_approved":
                self.log_result("✅ Agency already approved, proceeding to login")
            elif agency_id:
                if not self.approve_agency(agency_id):
                    return False
            else:
                self.log_result("❌ Cannot proceed without agency approval")
                return False
            
            # Login as agency
            if not self.login_user("agency", agency_creds["email"], agency_creds["password"]):
                return False
        else:
            return False
        
        # Step 3: Generate licenses
        self.log_result("\n📋 Step 3: License Generation")
        if not self.generate_licenses():
            return False
        
        # Step 4: Register client with license
        self.log_result("\n📋 Step 4: Client Registration & Login")
        client_creds = QA_CREDENTIALS["client"]
        if self.register_user("client", client_creds["email"], client_creds["password"], self.license_code):
            if not self.login_user("client", client_creds["email"], client_creds["password"]):
                return False
        else:
            return False
        
        # Step 5: Register provider and approve
        self.log_result("\n📋 Step 5: Provider Registration & Approval")
        provider_creds = QA_CREDENTIALS["provider"]
        if self.register_user("provider", provider_creds["email"], provider_creds["password"]):
            # Get pending providers and approve
            provider_id = self.get_pending_providers()
            if provider_id == "already_approved":
                self.log_result("✅ Provider already approved, proceeding to login")
            elif provider_id:
                if not self.approve_provider(provider_id):
                    return False
            else:
                self.log_result("❌ Cannot proceed without provider approval")
                return False
            
            # Login as provider
            if not self.login_user("provider", provider_creds["email"], provider_creds["password"]):
                return False
        else:
            return False
        
        return True
    
    def print_final_report(self):
        """Print the final test report"""
        self.log_result("\n" + "=" * 60)
        self.log_result("📊 FINAL QA WORKFLOW REPORT")
        self.log_result("=" * 60)
        
        # Per role status
        for role in ["navigator", "agency", "client", "provider"]:
            reg_status = self.results[role]["registration"]
            login_status = self.results[role]["login"]
            self.log_result(f"{role.upper()}: Registration={reg_status}, Login={login_status}")
        
        # License code
        if self.results["license_code"]:
            self.log_result(f"LICENSE CODE: {self.results['license_code']}")
        
        # Errors
        if self.results["errors"]:
            self.log_result("\n❌ ERRORS ENCOUNTERED:")
            for error in self.results["errors"]:
                self.log_result(f"  - {error}")
        else:
            self.log_result("\n✅ NO ERRORS - ALL STEPS COMPLETED SUCCESSFULLY")

def main():
    """Main test execution"""
    tester = QAWorkflowTester()
    
    try:
        success = tester.run_complete_workflow()
        tester.print_final_report()
        
        if success:
            print("\n🎉 QA WORKFLOW TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ QA WORKFLOW TEST FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()