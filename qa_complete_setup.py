#!/usr/bin/env python3
"""
QA Account Setup and Approval Script
Testing Agent: testing
Test Date: January 2025

This script completes the QA account setup by:
1. Using navigator account to approve agency and provider accounts
2. Generating license codes for client account
3. Creating client account with license code
4. Running final authentication test
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL configuration
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "navigator": {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "agency": {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!"
    },
    "provider": {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!"
    },
    "client": {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client",
        "terms_accepted": True
    }
}

class QASetupManager:
    def __init__(self):
        self.session = None
        self.results = []
        self.navigator_token = None
        self.agency_token = None
        self.license_code = None
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "QA-Setup-Manager/1.0"
            }
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str, data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.results.append(result)
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if data and isinstance(data, dict):
            if "token" in str(data):
                # Mask token for security
                masked_data = {k: v if k != "access_token" else f"{v[:10]}..." if v else None for k, v in data.items()}
                print(f"   Data: {json.dumps(masked_data, indent=2)}")
            else:
                print(f"   Data: {json.dumps(data, indent=2)}")
        print()
        
    async def login_navigator(self) -> bool:
        """Login as navigator to get admin token"""
        try:
            login_url = f"{BACKEND_URL}/auth/login"
            
            async with self.session.post(login_url, json=QA_CREDENTIALS["navigator"]) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if "access_token" in data:
                        self.navigator_token = data["access_token"]
                        self.log_result(
                            "Navigator Login",
                            True,
                            f"Successfully logged in as navigator",
                            {"token_length": len(data["access_token"])}
                        )
                        return True
                
                self.log_result(
                    "Navigator Login",
                    False,
                    f"Login failed with status {response.status}: {response_text[:200]}",
                    {"status": response.status}
                )
                return False
                    
        except Exception as e:
            self.log_result(
                "Navigator Login",
                False,
                f"Exception during login: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def approve_agency(self) -> bool:
        """Approve agency account using navigator token"""
        if not self.navigator_token:
            self.log_result("Agency Approval", False, "No navigator token available", None)
            return False
            
        try:
            # First, get list of pending agencies
            agencies_url = f"{BACKEND_URL}/navigator/agencies/pending"
            headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            async with self.session.get(agencies_url, headers=headers) as response:
                if response.status == 200:
                    agencies_data = json.loads(await response.text())
                    agencies = agencies_data.get("agencies", [])
                    
                    # Find the QA agency
                    qa_agency = None
                    for agency in agencies:
                        if agency.get("email") == "agency.qa@polaris.example.com":
                            qa_agency = agency
                            break
                    
                    if not qa_agency:
                        self.log_result(
                            "Agency Approval",
                            False,
                            "QA agency not found in pending list",
                            {"agencies_found": len(agencies)}
                        )
                        return False
                    
                    # Approve the agency
                    approve_url = f"{BACKEND_URL}/navigator/agencies/approve"
                    approval_data = {
                        "agency_user_id": qa_agency["id"],
                        "approval_status": "approved",
                        "notes": "QA account approval"
                    }
                    
                    async with self.session.post(approve_url, json=approval_data, headers=headers) as approve_response:
                        if approve_response.status == 200:
                            self.log_result(
                                "Agency Approval",
                                True,
                                f"Successfully approved agency {qa_agency['email']}",
                                {"agency_id": qa_agency["id"]}
                            )
                            return True
                        else:
                            response_text = await approve_response.text()
                            self.log_result(
                                "Agency Approval",
                                False,
                                f"Approval failed with status {approve_response.status}: {response_text[:200]}",
                                {"status": approve_response.status}
                            )
                            return False
                else:
                    response_text = await response.text()
                    self.log_result(
                        "Agency Approval",
                        False,
                        f"Failed to get pending agencies: {response_text[:200]}",
                        {"status": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Agency Approval",
                False,
                f"Exception during agency approval: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def login_agency(self) -> bool:
        """Login as agency to get agency token for license generation"""
        try:
            login_url = f"{BACKEND_URL}/auth/login"
            
            async with self.session.post(login_url, json=QA_CREDENTIALS["agency"]) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if "access_token" in data:
                        self.agency_token = data["access_token"]
                        self.log_result(
                            "Agency Login",
                            True,
                            f"Successfully logged in as agency",
                            {"token_length": len(data["access_token"])}
                        )
                        return True
                
                self.log_result(
                    "Agency Login",
                    False,
                    f"Login failed with status {response.status}: {response_text[:200]}",
                    {"status": response.status}
                )
                return False
                    
        except Exception as e:
            self.log_result(
                "Agency Login",
                False,
                f"Exception during login: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def generate_license_code(self) -> bool:
        """Generate license code using agency token"""
        if not self.agency_token:
            self.log_result("License Generation", False, "No agency token available", None)
            return False
            
        try:
            license_url = f"{BACKEND_URL}/agency/licenses/generate"
            headers = {"Authorization": f"Bearer {self.agency_token}"}
            license_data = {
                "quantity": 1,
                "expires_days": 365
            }
            
            async with self.session.post(license_url, json=license_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    licenses = data.get("licenses", [])
                    if licenses:
                        # Extract just the license code string
                        license_obj = licenses[0]
                        if isinstance(license_obj, dict) and "license_code" in license_obj:
                            self.license_code = license_obj["license_code"]
                        else:
                            self.license_code = str(license_obj)
                        
                        self.log_result(
                            "License Generation",
                            True,
                            f"Successfully generated license code: {self.license_code}",
                            {"license_code": self.license_code, "total_generated": len(licenses)}
                        )
                        return True
                    else:
                        self.log_result(
                            "License Generation",
                            False,
                            "No licenses returned in response",
                            data
                        )
                        return False
                else:
                    self.log_result(
                        "License Generation",
                        False,
                        f"License generation failed with status {response.status}: {response_text[:200]}",
                        {"status": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "License Generation",
                False,
                f"Exception during license generation: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def create_client_account(self) -> bool:
        """Create client account with license code"""
        if not self.license_code:
            self.log_result("Client Account Creation", False, "No license code available", None)
            return False
            
        try:
            register_url = f"{BACKEND_URL}/auth/register"
            client_data = QA_CREDENTIALS["client"].copy()
            client_data["license_code"] = self.license_code
            
            async with self.session.post(register_url, json=client_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    self.log_result(
                        "Client Account Creation",
                        True,
                        f"Successfully created client account with license {self.license_code}",
                        {"user_id": data.get("id", "N/A"), "email": data.get("email")}
                    )
                    return True
                elif response.status == 400 and "already registered" in response_text.lower():
                    self.log_result(
                        "Client Account Creation",
                        True,
                        f"Client account already exists (this is good)",
                        {"status": response.status}
                    )
                    return True
                else:
                    self.log_result(
                        "Client Account Creation",
                        False,
                        f"Registration failed with status {response.status}: {response_text[:200]}",
                        {"status": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Client Account Creation",
                False,
                f"Exception during client registration: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def approve_provider(self) -> bool:
        """Approve provider account using navigator token"""
        if not self.navigator_token:
            self.log_result("Provider Approval", False, "No navigator token available", None)
            return False
            
        try:
            # First, get list of pending providers
            providers_url = f"{BACKEND_URL}/navigator/providers/pending"
            headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            async with self.session.get(providers_url, headers=headers) as response:
                if response.status == 200:
                    providers_data = json.loads(await response.text())
                    providers = providers_data.get("providers", [])
                    
                    # Find the QA provider
                    qa_provider = None
                    for provider in providers:
                        if provider.get("email") == "provider.qa@polaris.example.com":
                            qa_provider = provider
                            break
                    
                    if not qa_provider:
                        self.log_result(
                            "Provider Approval",
                            False,
                            "QA provider not found in pending list",
                            {"providers_found": len(providers)}
                        )
                        return False
                    
                    # Approve the provider
                    approve_url = f"{BACKEND_URL}/navigator/providers/approve"
                    approval_data = {
                        "provider_user_id": qa_provider["id"],
                        "approval_status": "approved",
                        "notes": "QA account approval"
                    }
                    
                    async with self.session.post(approve_url, json=approval_data, headers=headers) as approve_response:
                        if approve_response.status == 200:
                            self.log_result(
                                "Provider Approval",
                                True,
                                f"Successfully approved provider {qa_provider['email']}",
                                {"provider_id": qa_provider["id"]}
                            )
                            return True
                        else:
                            response_text = await approve_response.text()
                            self.log_result(
                                "Provider Approval",
                                False,
                                f"Approval failed with status {approve_response.status}: {response_text[:200]}",
                                {"status": approve_response.status}
                            )
                            return False
                else:
                    response_text = await response.text()
                    self.log_result(
                        "Provider Approval",
                        False,
                        f"Failed to get pending providers: {response_text[:200]}",
                        {"status": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Provider Approval",
                False,
                f"Exception during provider approval: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def run_complete_setup(self):
        """Run complete QA setup process"""
        print("🔧 QA ACCOUNT COMPLETE SETUP")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Setup Time: {datetime.now().isoformat()}")
        print()
        
        await self.setup_session()
        
        try:
            total_steps = 7
            completed_steps = 0
            
            # Step 1: Login as navigator
            print("🔑 Step 1: Navigator Login")
            print("-" * 30)
            if await self.login_navigator():
                completed_steps += 1
            print()
            
            # Step 2: Approve agency
            print("🏢 Step 2: Agency Approval")
            print("-" * 30)
            if await self.approve_agency():
                completed_steps += 1
            print()
            
            # Step 3: Login as agency
            print("🔑 Step 3: Agency Login")
            print("-" * 30)
            if await self.login_agency():
                completed_steps += 1
            print()
            
            # Step 4: Generate license code
            print("🎫 Step 4: License Code Generation")
            print("-" * 30)
            if await self.generate_license_code():
                completed_steps += 1
            print()
            
            # Step 5: Create client account
            print("👤 Step 5: Client Account Creation")
            print("-" * 30)
            if await self.create_client_account():
                completed_steps += 1
            print()
            
            # Step 6: Approve provider
            print("🔧 Step 6: Provider Approval")
            print("-" * 30)
            if await self.approve_provider():
                completed_steps += 1
            print()
            
            # Summary
            success_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            print("📊 QA SETUP SUMMARY")
            print("=" * 60)
            print(f"Total Steps: {total_steps}")
            print(f"Completed: {completed_steps}")
            print(f"Failed: {total_steps - completed_steps}")
            print(f"Success Rate: {success_rate:.1f}%")
            print()
            
            if success_rate >= 85.0:  # Allow for some minor failures
                print("✅ QA SETUP COMPLETE - RUNNING AUTHENTICATION TEST")
                print()
                
                # Now run the authentication test
                import subprocess
                result = subprocess.run([sys.executable, "qa_auth_test.py"], 
                                      capture_output=True, text=True, cwd="/app")
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                
                return result.returncode == 0
            else:
                print("🚨 QA SETUP INCOMPLETE")
                failed_results = [r for r in self.results if not r["success"]]
                for failed in failed_results:
                    print(f"❌ {failed['test']}: {failed['details']}")
                return False
            
        finally:
            await self.cleanup_session()

async def main():
    """Main execution"""
    setup_manager = QASetupManager()
    
    try:
        success = await setup_manager.run_complete_setup()
        
        if success:
            print("\n🎉 QA SETUP AND AUTHENTICATION: COMPLETE SUCCESS")
            sys.exit(0)
        else:
            print("\n⚠️  QA SETUP: ISSUES FOUND")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 QA SETUP: CRITICAL ERROR")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())