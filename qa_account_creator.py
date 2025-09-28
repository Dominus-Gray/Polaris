#!/usr/bin/env python3
"""
QA Account Creation Script
Testing Agent: testing
Test Date: January 2025

This script creates the QA user accounts that are missing from the database.
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"

# QA Test Credentials to create
QA_ACCOUNTS = {
    "client": {
        "email": "client.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "client",
        "terms_accepted": True
    },
    "provider": {
        "email": "provider.qa@polaris.example.com", 
        "password": "Polaris#2025!",
        "role": "provider",
        "terms_accepted": True
    },
    "navigator": {
        "email": "navigator.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "navigator",
        "terms_accepted": True
    },
    "agency": {
        "email": "agency.qa@polaris.example.com",
        "password": "Polaris#2025!",
        "role": "agency",
        "terms_accepted": True
    }
}

class QAAccountCreator:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "QA-Account-Creator/1.0"
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
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()
        
    async def create_account(self, role: str, account_data: Dict[str, Any]) -> bool:
        """Create a QA account"""
        try:
            register_url = f"{BACKEND_URL}/auth/register"
            
            async with self.session.post(register_url, json=account_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        self.log_result(
                            f"Create {role.title()} Account",
                            True,
                            f"Successfully created account for {account_data['email']}",
                            {"user_id": data.get("id", "N/A"), "email": data.get("email"), "role": data.get("role")}
                        )
                        return True
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Create {role.title()} Account",
                            False,
                            f"Invalid JSON response: {response_text[:200]}",
                            {"status": response.status}
                        )
                        return False
                elif response.status == 400:
                    try:
                        error_data = json.loads(response_text)
                        if "already registered" in error_data.get("detail", "").lower():
                            self.log_result(
                                f"Create {role.title()} Account",
                                True,
                                f"Account {account_data['email']} already exists (this is good)",
                                {"status": response.status, "message": "Account already exists"}
                            )
                            return True
                        else:
                            self.log_result(
                                f"Create {role.title()} Account",
                                False,
                                f"Registration failed: {error_data.get('detail', response_text[:200])}",
                                {"status": response.status, "error": error_data}
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Create {role.title()} Account",
                            False,
                            f"Registration failed with status {response.status}: {response_text[:200]}",
                            {"status": response.status}
                        )
                        return False
                else:
                    try:
                        error_data = json.loads(response_text)
                        self.log_result(
                            f"Create {role.title()} Account",
                            False,
                            f"Registration failed with status {response.status}: {error_data.get('detail', response_text[:200])}",
                            {"status": response.status, "error": error_data}
                        )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Create {role.title()} Account",
                            False,
                            f"Registration failed with status {response.status}: {response_text[:200]}",
                            {"status": response.status}
                        )
                    return False
                    
        except Exception as e:
            self.log_result(
                f"Create {role.title()} Account",
                False,
                f"Exception during registration: {str(e)}",
                {"exception": str(e)}
            )
            return False
            
    async def run_account_creation(self):
        """Create all QA accounts"""
        print("🔧 QA ACCOUNT CREATION")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Creation Time: {datetime.now().isoformat()}")
        print()
        
        await self.setup_session()
        
        try:
            total_accounts = len(QA_ACCOUNTS)
            created_accounts = 0
            
            # Create each account
            for role, account_data in QA_ACCOUNTS.items():
                print(f"🔨 Creating {role.upper()} Account")
                print("-" * 30)
                
                success = await self.create_account(role, account_data)
                if success:
                    created_accounts += 1
                
                print()
            
            # Summary
            success_rate = (created_accounts / total_accounts * 100) if total_accounts > 0 else 0
            print("📊 QA ACCOUNT CREATION SUMMARY")
            print("=" * 50)
            print(f"Total Accounts: {total_accounts}")
            print(f"Created/Verified: {created_accounts}")
            print(f"Failed: {total_accounts - created_accounts}")
            print(f"Success Rate: {success_rate:.1f}%")
            print()
            
            # Detailed results
            print("📋 DETAILED RESULTS:")
            print("-" * 30)
            for result in self.results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}: {result['details']}")
            
            print()
            
            if success_rate >= 100.0:
                print("✅ ALL QA ACCOUNTS READY")
                print("   - All 4 QA accounts are now available for testing")
                print("   - You can now run authentication tests")
            else:
                failed_results = [r for r in self.results if not r["success"]]
                print("🚨 SOME ACCOUNTS FAILED TO CREATE:")
                print("-" * 40)
                for failed in failed_results:
                    print(f"❌ {failed['test']}: {failed['details']}")
            
            return success_rate >= 100.0
            
        finally:
            await self.cleanup_session()

async def main():
    """Main execution"""
    creator = QAAccountCreator()
    
    try:
        success = await creator.run_account_creation()
        
        if success:
            print("\n🎉 QA ACCOUNT CREATION: COMPLETE SUCCESS")
            print("Now running authentication test...")
            print()
            
            # Now run the authentication test
            import subprocess
            result = subprocess.run([sys.executable, "qa_auth_test.py"], 
                                  capture_output=True, text=True, cwd="/app")
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            sys.exit(result.returncode)
        else:
            print("\n⚠️  QA ACCOUNT CREATION: SOME ISSUES FOUND")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 QA ACCOUNT CREATION: CRITICAL ERROR")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())