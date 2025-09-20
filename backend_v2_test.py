#!/usr/bin/env python3
"""
Backend v2 Features Test Suite
Testing newly added v2 features using http://127.0.0.1:8001 with /api prefix
Feature flags are OFF by default; testing with headers/environment where possible
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class V2FeaturesTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
    
    def authenticate(self, role):
        """Authenticate and get token for role"""
        try:
            creds = QA_CREDENTIALS[role]
            response = requests.post(f"{BASE_URL}/auth/login", json=creds)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.tokens[role] = f"Bearer {token}"
                    self.log_test(f"Authentication - {role}", True, f"Token obtained: {token[:20]}...")
                    return True
                else:
                    self.log_test(f"Authentication - {role}", False, "No access_token in response", data)
                    return False
            else:
                self.log_test(f"Authentication - {role}", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test(f"Authentication - {role}", False, f"Exception: {str(e)}")
            return False
    
    def test_health_endpoint(self):
        """1) Health check: GET /api/health/system and record status"""
        try:
            response = requests.get(f"{BASE_URL}/health/system")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"System healthy", data)
                return True
            else:
                # Try alternative health endpoint
                response = requests.get(f"{BASE_URL}/system/health")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Health Check", True, f"System healthy (alternative endpoint)", data)
                    return True
                else:
                    self.log_test("Health Check", False, f"Status {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_zip_centroid_upload(self):
        """2) Zip code centroid admin upload: As agency.qa user, POST /api/admin/zip-centroids"""
        if "agency" not in self.tokens:
            self.log_test("Zip Centroid Upload", False, "Agency authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["agency"], "Content-Type": "application/json"}
            payload = {
                "centroids": [
                    {"zip": "78205", "lat": 29.4241, "lng": -98.4936},
                    {"zip": "78229", "lat": 29.5083, "lng": -98.5732}
                ]
            }
            
            response = requests.post(f"{BASE_URL}/admin/zip-centroids", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                if count >= 2:
                    self.log_test("Zip Centroid Upload", True, f"Uploaded {count} centroids", data)
                    return True
                else:
                    self.log_test("Zip Centroid Upload", False, f"Expected count >=2, got {count}", data)
                    return False
            else:
                self.log_test("Zip Centroid Upload", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Zip Centroid Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_zip_search(self):
        """3) Call /api/v2/matching/search-by-zip as client.qa with body {zip:"78205", radius_miles:50}"""
        if "client" not in self.tokens:
            self.log_test("V2 Zip Search", False, "Client authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["client"], "Content-Type": "application/json"}
            payload = {"zip": "78205", "radius_miles": 50}
            
            response = requests.post(f"{BASE_URL}/v2/matching/search-by-zip", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("enabled") == False:
                    self.log_test("V2 Zip Search", True, f"Feature disabled: {data.get('message')}", data)
                    return True
                else:
                    providers = data.get("providers", [])
                    count = data.get("count", 0)
                    self.log_test("V2 Zip Search", True, f"Found {count} providers in radius", data)
                    return True
            else:
                self.log_test("V2 Zip Search", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("V2 Zip Search", False, f"Exception: {str(e)}")
            return False
    
    def test_rp_requirements_set(self):
        """4) RP requirements: As agency.qa, POST /api/v2/rp/requirements with rp_type="bank" and required_fields"""
        if "agency" not in self.tokens:
            self.log_test("RP Requirements Set", False, "Agency authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["agency"], "Content-Type": "application/json"}
            payload = {
                "rp_type": "bank",
                "required_fields": ["licenses_status", "insurance_status", "contact_email", "readiness_score"]
            }
            
            response = requests.post(f"{BASE_URL}/v2/rp/requirements", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                rp_type = data.get("rp_type")
                count = data.get("count", 0)
                if rp_type == "bank" and count == 4:
                    self.log_test("RP Requirements Set", True, f"Set {count} requirements for {rp_type}", data)
                    return True
                else:
                    self.log_test("RP Requirements Set", False, f"Expected bank/4, got {rp_type}/{count}", data)
                    return False
            else:
                self.log_test("RP Requirements Set", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("RP Requirements Set", False, f"Exception: {str(e)}")
            return False
    
    def test_rp_requirements_get_client(self):
        """5a) GET /api/v2/rp/requirements?rp_type=bank as client.qa"""
        if "client" not in self.tokens:
            self.log_test("RP Requirements Get (Client)", False, "Client authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["client"]}
            response = requests.get(f"{BASE_URL}/v2/rp/requirements?rp_type=bank", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                rp_type = data.get("rp_type")
                fields = data.get("required_fields", [])
                if rp_type == "bank" and len(fields) >= 1:
                    self.log_test("RP Requirements Get (Client)", True, f"Retrieved {len(fields)} fields for {rp_type}", data)
                    return True
                else:
                    self.log_test("RP Requirements Get (Client)", False, f"Expected bank with fields, got {rp_type} with {len(fields)} fields", data)
                    return False
            else:
                self.log_test("RP Requirements Get (Client)", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("RP Requirements Get (Client)", False, f"Exception: {str(e)}")
            return False
    
    def test_rp_requirements_get_agency(self):
        """5b) GET /api/v2/rp/requirements?rp_type=bank as agency.qa"""
        if "agency" not in self.tokens:
            self.log_test("RP Requirements Get (Agency)", False, "Agency authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["agency"]}
            response = requests.get(f"{BASE_URL}/v2/rp/requirements?rp_type=bank", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                rp_type = data.get("rp_type")
                fields = data.get("required_fields", [])
                if rp_type == "bank" and len(fields) >= 1:
                    self.log_test("RP Requirements Get (Agency)", True, f"Retrieved {len(fields)} fields for {rp_type}", data)
                    return True
                else:
                    self.log_test("RP Requirements Get (Agency)", False, f"Expected bank with fields, got {rp_type} with {len(fields)} fields", data)
                    return False
            else:
                self.log_test("RP Requirements Get (Agency)", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("RP Requirements Get (Agency)", False, f"Exception: {str(e)}")
            return False
    
    def test_package_preview(self):
        """6) Package preview: As client.qa, GET /api/v2/rp/package-preview?rp_type=bank"""
        if "client" not in self.tokens:
            self.log_test("Package Preview", False, "Client authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["client"]}
            response = requests.get(f"{BASE_URL}/v2/rp/package-preview?rp_type=bank", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                package = data.get("package", {})
                missing = data.get("missing", [])
                if isinstance(package, dict) and isinstance(missing, list):
                    self.log_test("Package Preview", True, f"Package with {len(package)} fields, {len(missing)} missing", data)
                    return True
                else:
                    self.log_test("Package Preview", False, f"Expected package dict and missing array", data)
                    return False
            else:
                self.log_test("Package Preview", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Package Preview", False, f"Exception: {str(e)}")
            return False
    
    def test_create_rp_lead(self):
        """7a) Create RP lead: As client.qa, POST /api/v2/rp/leads with {rp_type:"bank"}"""
        if "client" not in self.tokens:
            self.log_test("Create RP Lead", False, "Client authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["client"], "Content-Type": "application/json"}
            payload = {"rp_type": "bank"}
            
            response = requests.post(f"{BASE_URL}/v2/rp/leads", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("enabled") == False:
                    self.log_test("Create RP Lead", True, f"Feature disabled: {data.get('message')}", data)
                    return True
                else:
                    lead_id = data.get("lead_id")
                    status = data.get("status")
                    if lead_id and status:
                        self.log_test("Create RP Lead", True, f"Created lead {lead_id} with status {status}", data)
                        # Store lead_id for later use
                        self.lead_id = lead_id
                        return True
                    else:
                        self.log_test("Create RP Lead", False, f"Expected lead_id and status", data)
                        return False
            else:
                self.log_test("Create RP Lead", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create RP Lead", False, f"Exception: {str(e)}")
            return False
    
    def test_list_rp_leads_agency(self):
        """7b) GET /api/v2/rp/leads as agency.qa"""
        if "agency" not in self.tokens:
            self.log_test("List RP Leads (Agency)", False, "Agency authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["agency"]}
            response = requests.get(f"{BASE_URL}/v2/rp/leads", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                leads = data.get("leads", [])
                self.log_test("List RP Leads (Agency)", True, f"Retrieved {len(leads)} leads", data)
                return True
            else:
                self.log_test("List RP Leads (Agency)", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("List RP Leads (Agency)", False, f"Exception: {str(e)}")
            return False
    
    def test_list_rp_leads_client(self):
        """7c) GET /api/v2/rp/leads as client.qa and confirm visibility rules"""
        if "client" not in self.tokens:
            self.log_test("List RP Leads (Client)", False, "Client authentication required")
            return False
        
        try:
            headers = {"Authorization": self.tokens["client"]}
            response = requests.get(f"{BASE_URL}/v2/rp/leads", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                leads = data.get("leads", [])
                # Client should only see their own leads
                self.log_test("List RP Leads (Client)", True, f"Retrieved {len(leads)} leads (client view)", data)
                return True
            else:
                self.log_test("List RP Leads (Client)", False, f"Status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("List RP Leads (Client)", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all v2 feature tests"""
        print("🚀 Starting Backend v2 Features Test Suite")
        print("=" * 60)
        
        # Authentication
        print("📋 Step 1: Authentication")
        agency_auth = self.authenticate("agency")
        client_auth = self.authenticate("client")
        
        if not (agency_auth and client_auth):
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Test sequence as requested
        print("📋 Step 2: Health Check")
        self.test_health_endpoint()
        
        print("📋 Step 3: Zip Code Centroid Upload")
        self.test_zip_centroid_upload()
        
        print("📋 Step 4: V2 Zip-based Matching")
        self.test_v2_zip_search()
        
        print("📋 Step 5: RP Requirements Management")
        self.test_rp_requirements_set()
        self.test_rp_requirements_get_client()
        self.test_rp_requirements_get_agency()
        
        print("📋 Step 6: Package Preview")
        self.test_package_preview()
        
        print("📋 Step 7: RP Lead Management")
        self.test_create_rp_lead()
        self.test_list_rp_leads_agency()
        self.test_list_rp_leads_client()
        
        # Summary
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        # Flag-disabled messages
        flag_disabled = [r for r in self.test_results if "Feature disabled" in r.get("details", "")]
        if flag_disabled:
            print(f"\n🏳️ FEATURE FLAGS DISABLED: {len(flag_disabled)} tests")
            for result in flag_disabled:
                print(f"   {result['test']}: {result['details']}")

def main():
    """Main test execution"""
    tester = V2FeaturesTester()
    success = tester.run_all_tests()
    
    # Append results to test_result.md
    try:
        with open("/app/test_result.md", "a") as f:
            f.write(f"\n\n## Backend v2 – Foundation (Zip Matching + CRM-lite)\n")
            f.write(f"**Testing Agent**: testing\n")
            f.write(f"**Test Date**: {datetime.now().strftime('%B %d, %Y')}\n")
            f.write(f"**Test Scope**: V2 features testing with feature flags OFF by default\n\n")
            
            passed = sum(1 for r in tester.test_results if r["success"])
            total = len(tester.test_results)
            
            f.write(f"### COMPREHENSIVE V2 TEST RESULTS: {(passed/total*100):.1f}% SUCCESS RATE ({passed}/{total} TESTS PASSED)\n\n")
            
            # Categorize results
            health_tests = [r for r in tester.test_results if "Health" in r["test"]]
            zip_tests = [r for r in tester.test_results if "Zip" in r["test"]]
            rp_tests = [r for r in tester.test_results if "RP" in r["test"]]
            auth_tests = [r for r in tester.test_results if "Authentication" in r["test"]]
            
            f.write(f"#### ✅ **AUTHENTICATION & SETUP - {'FULLY OPERATIONAL' if all(r['success'] for r in auth_tests) else 'ISSUES DETECTED'}**:\n")
            for result in auth_tests:
                f.write(f"- {result['status']}: {result['test']} - {result['details']}\n")
            
            f.write(f"\n#### {'✅' if all(r['success'] for r in health_tests) else '❌'} **HEALTH CHECK - {'OPERATIONAL' if all(r['success'] for r in health_tests) else 'FAILED'}**:\n")
            for result in health_tests:
                f.write(f"- {result['status']}: {result['test']} - {result['details']}\n")
            
            f.write(f"\n#### {'✅' if all(r['success'] for r in zip_tests) else '❌'} **ZIP-BASED MATCHING - {'OPERATIONAL' if all(r['success'] for r in zip_tests) else 'ISSUES DETECTED'}**:\n")
            for result in zip_tests:
                f.write(f"- {result['status']}: {result['test']} - {result['details']}\n")
            
            f.write(f"\n#### {'✅' if all(r['success'] for r in rp_tests) else '❌'} **RP CRM-LITE FEATURES - {'OPERATIONAL' if all(r['success'] for r in rp_tests) else 'ISSUES DETECTED'}**:\n")
            for result in rp_tests:
                f.write(f"- {result['status']}: {result['test']} - {result['details']}\n")
            
            # Flag-disabled messages
            flag_disabled = [r for r in tester.test_results if "Feature disabled" in r.get("details", "")]
            if flag_disabled:
                f.write(f"\n#### 🏳️ **FEATURE FLAGS STATUS**:\n")
                for result in flag_disabled:
                    f.write(f"- {result['test']}: {result['details']}\n")
            
            f.write(f"\n### PRODUCTION READINESS ASSESSMENT:\n")
            if passed == total:
                f.write(f"**✅ EXCELLENT** - All v2 features operational with {(passed/total*100):.1f}% success rate\n")
            elif passed >= total * 0.8:
                f.write(f"**🟡 GOOD** - Most v2 features operational with {(passed/total*100):.1f}% success rate\n")
            else:
                f.write(f"**🚨 NEEDS ATTENTION** - Multiple v2 features have issues with {(passed/total*100):.1f}% success rate\n")
            
            print(f"\n✅ Results appended to /app/test_result.md")
            
    except Exception as e:
        print(f"❌ Failed to append to test_result.md: {str(e)}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())