#!/usr/bin/env python3
"""
Backend V2 QA Enabled Smoke Test
Quick verification for v2 endpoints with QA credentials
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://nextjs-mongo-polaris.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"},
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class V2EndpointTester:
    def __init__(self):
        self.tokens = {}
        self.results = []
        
    def log_result(self, endpoint, method, status_code, success, details="", body_snippet=""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "details": details,
            "body_snippet": body_snippet[:200] if body_snippet else ""
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint} - {status_code} - {details}")
        if body_snippet:
            print(f"   Body: {body_snippet[:100]}...")
    
    def authenticate(self, role):
        """Authenticate and store token"""
        try:
            creds = QA_CREDENTIALS[role]
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=creds,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.tokens[role] = f"Bearer {token}"
                    self.log_result("/auth/login", "POST", 200, True, f"{role} auth success")
                    return True
                else:
                    self.log_result("/auth/login", "POST", 200, False, f"{role} auth failed - no token")
                    return False
            else:
                self.log_result("/auth/login", "POST", response.status_code, False, 
                              f"{role} auth failed", response.text)
                return False
                
        except Exception as e:
            self.log_result("/auth/login", "POST", 0, False, f"{role} auth error: {str(e)}")
            return False
    
    def make_request(self, method, endpoint, role=None, json_data=None, params=None):
        """Make authenticated request"""
        headers = {}
        if role and role in self.tokens:
            headers["Authorization"] = self.tokens[role]
        
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=json_data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
            
        except Exception as e:
            print(f"Request error for {method} {endpoint}: {str(e)}")
            return None
    
    def test_zip_centroids(self):
        """Test POST /api/admin/zip-centroids"""
        print("\n🔍 Testing ZIP Centroids Admin Endpoint...")
        
        # Try with agency credentials
        zip_data = {"zip_codes": ["78205", "78229"]}
        response = self.make_request("POST", "/admin/zip-centroids", "agency", zip_data)
        
        if response:
            success = response.status_code == 200
            body_snippet = response.text[:200] if response.text else ""
            self.log_result("/admin/zip-centroids", "POST", response.status_code, success,
                          "ZIP centroids admin", body_snippet)
        else:
            self.log_result("/admin/zip-centroids", "POST", 0, False, "Request failed")
    
    def test_v2_matching_search(self):
        """Test POST /api/v2/matching/search-by-zip"""
        print("\n🔍 Testing V2 Matching Search by ZIP...")
        
        search_data = {"zip": "78205", "radius_miles": 50}
        response = self.make_request("POST", "/v2/matching/search-by-zip", "client", search_data)
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    has_providers = "providers" in data
                    has_count = "count" in data
                    structure_valid = has_providers and has_count
                    body_snippet = f"providers: {has_providers}, count: {has_count}"
                    if not structure_valid:
                        success = False
                        body_snippet += " - Missing required structure"
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/matching/search-by-zip", "POST", response.status_code, success,
                          "V2 matching search", body_snippet)
        else:
            self.log_result("/v2/matching/search-by-zip", "POST", 0, False, "Request failed")
    
    def test_v2_rp_requirements_post(self):
        """Test POST /api/v2/rp/requirements"""
        print("\n🔍 Testing V2 RP Requirements POST...")
        
        rp_data = {
            "rp_type": "bank",
            "required_fields": [
                "business_name",
                "tax_id", 
                "annual_revenue",
                "years_in_business"
            ]
        }
        response = self.make_request("POST", "/v2/rp/requirements", "agency", rp_data)
        
        if response:
            success = response.status_code == 200
            body_snippet = response.text[:200] if response.text else ""
            self.log_result("/v2/rp/requirements", "POST", response.status_code, success,
                          "V2 RP requirements create", body_snippet)
        else:
            self.log_result("/v2/rp/requirements", "POST", 0, False, "Request failed")
    
    def test_v2_rp_requirements_get(self):
        """Test GET /api/v2/rp/requirements?rp_type=bank"""
        print("\n🔍 Testing V2 RP Requirements GET...")
        
        params = {"rp_type": "bank"}
        response = self.make_request("GET", "/v2/rp/requirements", "client", params=params)
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    has_required_fields = "required_fields" in data
                    body_snippet = f"required_fields present: {has_required_fields}"
                    if not has_required_fields:
                        success = False
                        body_snippet += " - Missing required_fields"
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/rp/requirements", "GET", response.status_code, success,
                          "V2 RP requirements get", body_snippet)
        else:
            self.log_result("/v2/rp/requirements", "GET", 0, False, "Request failed")
    
    def test_v2_rp_package_preview(self):
        """Test GET /api/v2/rp/package-preview?rp_type=bank"""
        print("\n🔍 Testing V2 RP Package Preview...")
        
        params = {"rp_type": "bank"}
        response = self.make_request("GET", "/v2/rp/package-preview", "client", params=params)
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    has_package = "package" in data
                    has_missing = "missing" in data
                    structure_valid = has_package and has_missing
                    body_snippet = f"package: {has_package}, missing: {has_missing}"
                    if not structure_valid:
                        success = False
                        body_snippet += " - Missing package/missing arrays"
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/rp/package-preview", "GET", response.status_code, success,
                          "V2 RP package preview", body_snippet)
        else:
            self.log_result("/v2/rp/package-preview", "GET", 0, False, "Request failed")
    
    def test_v2_rp_leads_post(self):
        """Test POST /api/v2/rp/leads"""
        print("\n🔍 Testing V2 RP Leads POST...")
        
        lead_data = {"rp_type": "bank"}
        response = self.make_request("POST", "/v2/rp/leads", "client", lead_data)
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    has_lead_id = "lead_id" in data
                    body_snippet = f"lead_id present: {has_lead_id}"
                    if not has_lead_id:
                        success = False
                        body_snippet += " - Missing lead_id"
                    else:
                        # Store lead_id for later tests
                        self.lead_id = data.get("lead_id")
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/rp/leads", "POST", response.status_code, success,
                          "V2 RP leads create", body_snippet)
        else:
            self.log_result("/v2/rp/leads", "POST", 0, False, "Request failed")
    
    def test_v2_rp_leads_get_client(self):
        """Test GET /api/v2/rp/leads as client"""
        print("\n🔍 Testing V2 RP Leads GET (Client)...")
        
        response = self.make_request("GET", "/v2/rp/leads", "client")
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        body_snippet = f"Client leads count: {len(data)}"
                    else:
                        body_snippet = f"Response type: {type(data)}"
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/rp/leads", "GET", response.status_code, success,
                          "V2 RP leads get (client)", body_snippet)
        else:
            self.log_result("/v2/rp/leads", "GET", 0, False, "Request failed")
    
    def test_v2_rp_leads_get_agency(self):
        """Test GET /api/v2/rp/leads as agency"""
        print("\n🔍 Testing V2 RP Leads GET (Agency)...")
        
        response = self.make_request("GET", "/v2/rp/leads", "agency")
        
        if response:
            success = response.status_code == 200
            body_snippet = ""
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        body_snippet = f"Agency leads count: {len(data)}"
                    else:
                        body_snippet = f"Response type: {type(data)}"
                except:
                    success = False
                    body_snippet = "Invalid JSON response"
            else:
                body_snippet = response.text[:200]
            
            self.log_result("/v2/rp/leads", "GET", response.status_code, success,
                          "V2 RP leads get (agency)", body_snippet)
        else:
            self.log_result("/v2/rp/leads", "GET", 0, False, "Request failed")
    
    def run_all_tests(self):
        """Run all V2 endpoint tests"""
        print("🚀 Starting Backend V2 QA Enabled Smoke Test")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        # Step 1: Authenticate both roles
        print("\n🔐 Authentication Phase...")
        agency_auth = self.authenticate("agency")
        client_auth = self.authenticate("client")
        
        if not (agency_auth and client_auth):
            print("❌ Authentication failed - cannot proceed with V2 tests")
            return False
        
        # Step 2: Run V2 endpoint tests
        print("\n🧪 V2 Endpoint Testing Phase...")
        
        self.test_zip_centroids()
        self.test_v2_matching_search()
        self.test_v2_rp_requirements_post()
        self.test_v2_rp_requirements_get()
        self.test_v2_rp_package_preview()
        self.test_v2_rp_leads_post()
        self.test_v2_rp_leads_get_client()
        self.test_v2_rp_leads_get_agency()
        
        return True
    
    def generate_report(self):
        """Generate compact test report"""
        print("\n" + "="*60)
        print("📊 BACKEND V2 QA SMOKE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['method']} {result['endpoint']} - {result['status_code']}")
            if result["body_snippet"]:
                print(f"   {result['body_snippet']}")
        
        # Summary for test_result.md
        print("\n📝 Summary for test_result.md:")
        print("Backend v2 – QA Enabled Smoke:")
        print(f"- V2 endpoints tested: {total_tests}")
        print(f"- Success rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"- Authentication: {'✅ Working' if passed_tests >= 2 else '❌ Failed'}")
        print(f"- Key findings: {self.get_key_findings()}")
        
        return success_rate >= 70  # Consider 70%+ as acceptable
    
    def get_key_findings(self):
        """Get key findings summary"""
        findings = []
        
        # Check authentication
        auth_results = [r for r in self.results if "/auth/login" in r["endpoint"]]
        if all(r["success"] for r in auth_results):
            findings.append("QA credentials working")
        else:
            findings.append("Authentication issues")
        
        # Check V2 endpoints
        v2_results = [r for r in self.results if "/v2/" in r["endpoint"]]
        v2_success = sum(1 for r in v2_results if r["success"])
        v2_total = len(v2_results)
        
        if v2_success == v2_total:
            findings.append("All V2 endpoints operational")
        elif v2_success > v2_total // 2:
            findings.append(f"Most V2 endpoints working ({v2_success}/{v2_total})")
        else:
            findings.append(f"V2 endpoints need attention ({v2_success}/{v2_total})")
        
        return ", ".join(findings) if findings else "Mixed results"

def main():
    """Main test execution"""
    tester = V2EndpointTester()
    
    try:
        success = tester.run_all_tests()
        overall_success = tester.generate_report()
        
        # Exit with appropriate code
        sys.exit(0 if overall_success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()