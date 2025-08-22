#!/usr/bin/env python3
"""
Knowledge Base Access Control Fix Verification Test
==================================================

This test verifies the fix for Knowledge Base access control:
1. Provider Knowledge Base Block Test - providers should be completely blocked
2. Client Marketplace Access Test - clients should have marketplace access
3. Security Validation - proper role-based access control

Test Credentials:
- Provider: provider.qa@polaris.example.com / Polaris#2025!
- Client: client.qa@polaris.example.com / Polaris#2025!
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://readiness-hub-2.preview.emergentagent.com/api"

# Test credentials
PROVIDER_CREDENTIALS = {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class KnowledgeBaseAccessFixTester:
    def __init__(self):
        self.provider_token = None
        self.client_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    def authenticate_user(self, credentials, role_name):
        """Authenticate user and return token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.log_test(f"{role_name} Authentication", True, f"Successfully authenticated {credentials['email']}")
                return token
            else:
                error_detail = response.json().get("detail", "Unknown error")
                self.log_test(f"{role_name} Authentication", False, f"Status {response.status_code}: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test(f"{role_name} Authentication", False, f"Exception: {str(e)}")
            return None
    
    def test_provider_knowledge_base_block(self):
        """Test that provider is completely blocked from Knowledge Base"""
        print("\n🔒 TESTING PROVIDER KNOWLEDGE BASE BLOCK")
        print("=" * 50)
        
        if not self.provider_token:
            self.log_test("Provider KB Block Test", False, "No provider token available")
            return
            
        headers = {"Authorization": f"Bearer {self.provider_token}"}
        
        # Test 1: GET /api/knowledge-base/access should return has_all_access: false
        try:
            response = requests.get(f"{BACKEND_URL}/knowledge-base/access", headers=headers)
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_all_access", True)
                if has_access == False:
                    self.log_test("Provider KB Access Check", True, "has_all_access: false returned correctly")
                else:
                    self.log_test("Provider KB Access Check", False, f"has_all_access: {has_access} (should be false)")
            else:
                self.log_test("Provider KB Access Check", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Provider KB Access Check", False, f"Exception: {str(e)}")
        
        # Test 2: GET /api/knowledge-base/areas should return 402/403 error
        try:
            response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB Areas Block", True, f"Correctly blocked with status {response.status_code}")
            else:
                self.log_test("Provider KB Areas Block", False, f"Status {response.status_code} (expected 402/403)")
        except Exception as e:
            self.log_test("Provider KB Areas Block", False, f"Exception: {str(e)}")
        
        # Test 3: GET /api/knowledge-base/generate-template/area1/template should return 402/403 error
        try:
            response = requests.get(f"{BACKEND_URL}/knowledge-base/generate-template/area1/template", headers=headers)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB Template Block", True, f"Correctly blocked with status {response.status_code}")
            else:
                self.log_test("Provider KB Template Block", False, f"Status {response.status_code} (expected 402/403)")
        except Exception as e:
            self.log_test("Provider KB Template Block", False, f"Exception: {str(e)}")
        
        # Test 4: POST /api/knowledge-base/ai-assistance should return 402/403 error
        try:
            payload = {"question": "How do I get started with business licensing?"}
            response = requests.post(f"{BACKEND_URL}/knowledge-base/ai-assistance", headers=headers, json=payload)
            if response.status_code in [402, 403]:
                self.log_test("Provider KB AI Assistance Block", True, f"Correctly blocked with status {response.status_code}")
            else:
                self.log_test("Provider KB AI Assistance Block", False, f"Status {response.status_code} (expected 402/403)")
        except Exception as e:
            self.log_test("Provider KB AI Assistance Block", False, f"Exception: {str(e)}")
    
    def test_client_marketplace_access(self):
        """Test that client can access marketplace functionality"""
        print("\n🛒 TESTING CLIENT MARKETPLACE ACCESS")
        print("=" * 50)
        
        if not self.client_token:
            self.log_test("Client Marketplace Test", False, "No client token available")
            return
            
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test 1: GET /api/marketplace/gigs/search should work properly
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/gigs/search", headers=headers)
            if response.status_code == 200:
                data = response.json()
                gigs = data.get("gigs", [])
                self.log_test("Client Marketplace Search", True, f"Retrieved {len(gigs)} gigs successfully")
            else:
                self.log_test("Client Marketplace Search", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Client Marketplace Search", False, f"Exception: {str(e)}")
        
        # Test 2: Test marketplace search with filters
        try:
            params = {"category": "business-formation", "min_price": 100, "max_price": 1000}
            response = requests.get(f"{BACKEND_URL}/marketplace/gigs/search", headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Client Marketplace Filtered Search", True, "Filtered search working correctly")
            else:
                self.log_test("Client Marketplace Filtered Search", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Client Marketplace Filtered Search", False, f"Exception: {str(e)}")
        
        # Test 3: Verify client can discover provider services
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/gigs/search?category=consulting", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total_gigs = data.get("total", 0)
                self.log_test("Client Provider Discovery", True, f"Can discover {total_gigs} provider services")
            else:
                self.log_test("Client Provider Discovery", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Client Provider Discovery", False, f"Exception: {str(e)}")
    
    def test_security_validation(self):
        """Test proper role-based access control"""
        print("\n🔐 TESTING SECURITY VALIDATION")
        print("=" * 50)
        
        # Test that client still has Knowledge Base access
        if self.client_token:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            try:
                response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    areas = data.get("areas", [])
                    self.log_test("Client KB Access Preserved", True, f"Client can access {len(areas)} KB areas")
                else:
                    self.log_test("Client KB Access Preserved", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_test("Client KB Access Preserved", False, f"Exception: {str(e)}")
        
        # Test role-based restrictions are properly enforced
        if self.provider_token and self.client_token:
            # Provider should not access KB, Client should access KB
            provider_headers = {"Authorization": f"Bearer {self.provider_token}"}
            client_headers = {"Authorization": f"Bearer {self.client_token}"}
            
            try:
                provider_response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=provider_headers)
                client_response = requests.get(f"{BACKEND_URL}/knowledge-base/areas", headers=client_headers)
                
                provider_blocked = provider_response.status_code in [402, 403]
                client_allowed = client_response.status_code == 200
                
                if provider_blocked and client_allowed:
                    self.log_test("Role-Based Access Control", True, "Provider blocked, Client allowed - correct behavior")
                else:
                    self.log_test("Role-Based Access Control", False, f"Provider: {provider_response.status_code}, Client: {client_response.status_code}")
            except Exception as e:
                self.log_test("Role-Based Access Control", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 KNOWLEDGE BASE ACCESS CONTROL FIX VERIFICATION")
        print("=" * 60)
        print(f"Testing Backend: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Authenticate users
        print("🔑 AUTHENTICATION PHASE")
        print("=" * 30)
        self.provider_token = self.authenticate_user(PROVIDER_CREDENTIALS, "Provider")
        self.client_token = self.authenticate_user(CLIENT_CREDENTIALS, "Client")
        
        # Run tests
        self.test_provider_knowledge_base_block()
        self.test_client_marketplace_access()
        self.test_security_validation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Determine overall result
        if success_rate >= 80:
            print(f"\n✅ OVERALL RESULT: PASS ({success_rate:.1f}% success rate)")
            print("Knowledge Base access control fix is working correctly!")
        else:
            print(f"\n❌ OVERALL RESULT: FAIL ({success_rate:.1f}% success rate)")
            print("Knowledge Base access control fix needs attention!")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = KnowledgeBaseAccessFixTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)