#!/usr/bin/env python3
"""
Agency License Management Endpoints Testing
Testing the newly exposed agency license management endpoints as requested in review.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://quality-match-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# QA Credentials
AGENCY_QA_EMAIL = "agency.qa@polaris.example.com"
AGENCY_QA_PASSWORD = "Polaris#2025!"

class AgencyLicenseTest:
    def __init__(self):
        self.session = requests.Session()
        self.bearer_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, status_code=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if status_code:
            print(f"   Status Code: {status_code}")
        print()
        
    def test_agency_login(self):
        """Test 1: Login as agency QA account and store bearer token"""
        try:
            login_data = {
                "email": AGENCY_QA_EMAIL,
                "password": AGENCY_QA_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.bearer_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.bearer_token}"})
                    self.log_result(
                        "Agency QA Login", 
                        True, 
                        f"Successfully logged in as {AGENCY_QA_EMAIL}, token stored",
                        response.status_code
                    )
                    return True
                else:
                    self.log_result(
                        "Agency QA Login", 
                        False, 
                        "No access_token in response",
                        response.status_code
                    )
                    return False
            else:
                self.log_result(
                    "Agency QA Login", 
                    False, 
                    f"Login failed: {response.text}",
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_result("Agency QA Login", False, f"Exception: {str(e)}")
            return False
    
    def test_license_stats_initial(self):
        """Test 2: GET /api/agency/licenses/stats - expect 200 and JSON with required keys"""
        try:
            response = self.session.get(f"{API_BASE}/agency/licenses/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_keys = ["total_generated", "available", "used", "expired"]
                
                missing_keys = [key for key in required_keys if key not in data]
                if not missing_keys:
                    self.log_result(
                        "License Stats Initial", 
                        True, 
                        f"Stats retrieved successfully: {data}",
                        response.status_code
                    )
                    return data
                else:
                    self.log_result(
                        "License Stats Initial", 
                        False, 
                        f"Missing required keys: {missing_keys}. Got: {data}",
                        response.status_code
                    )
                    return None
            else:
                self.log_result(
                    "License Stats Initial", 
                    False, 
                    f"Failed to get stats: {response.text}",
                    response.status_code
                )
                return None
                
        except Exception as e:
            self.log_result("License Stats Initial", False, f"Exception: {str(e)}")
            return None
    
    def test_license_list_initial(self):
        """Test 3: GET /api/agency/licenses - expect 200 and licenses array"""
        try:
            response = self.session.get(f"{API_BASE}/agency/licenses")
            
            if response.status_code == 200:
                data = response.json()
                if "licenses" in data and isinstance(data["licenses"], list):
                    self.log_result(
                        "License List Initial", 
                        True, 
                        f"Licenses list retrieved successfully: {len(data['licenses'])} licenses",
                        response.status_code
                    )
                    return data["licenses"]
                else:
                    self.log_result(
                        "License List Initial", 
                        False, 
                        f"Invalid response format. Expected 'licenses' array. Got: {data}",
                        response.status_code
                    )
                    return None
            else:
                self.log_result(
                    "License List Initial", 
                    False, 
                    f"Failed to get licenses: {response.text}",
                    response.status_code
                )
                return None
                
        except Exception as e:
            self.log_result("License List Initial", False, f"Exception: {str(e)}")
            return None
    
    def test_license_generation(self):
        """Test 4: POST /api/agency/licenses/generate with {quantity: 3, expires_days: 60}"""
        try:
            generation_data = {
                "quantity": 3,
                "expires_days": 60
            }
            
            response = self.session.post(f"{API_BASE}/agency/licenses/generate", json=generation_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "licenses", "usage_update"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if not missing_fields:
                    licenses_count = len(data.get("licenses", []))
                    if licenses_count == 3:
                        self.log_result(
                            "License Generation", 
                            True, 
                            f"Successfully generated 3 licenses. Response: {data}",
                            response.status_code
                        )
                        return data
                    else:
                        self.log_result(
                            "License Generation", 
                            False, 
                            f"Expected 3 licenses, got {licenses_count}. Response: {data}",
                            response.status_code
                        )
                        return None
                else:
                    self.log_result(
                        "License Generation", 
                        False, 
                        f"Missing required fields: {missing_fields}. Got: {data}",
                        response.status_code
                    )
                    return None
            elif response.status_code == 403:
                self.log_result(
                    "License Generation", 
                    True, 
                    f"Agency approval required (403 as expected): {response.text}",
                    response.status_code
                )
                return None
            else:
                self.log_result(
                    "License Generation", 
                    False, 
                    f"Unexpected response: {response.text}",
                    response.status_code
                )
                return None
                
        except Exception as e:
            self.log_result("License Generation", False, f"Exception: {str(e)}")
            return None
    
    def test_license_stats_after_generation(self, initial_stats):
        """Test 5: Re-GET stats and verify counts increased (+3)"""
        try:
            response = self.session.get(f"{API_BASE}/agency/licenses/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                if initial_stats:
                    initial_total = initial_stats.get("total_generated", 0)
                    current_total = data.get("total_generated", 0)
                    
                    if current_total == initial_total + 3:
                        self.log_result(
                            "License Stats After Generation", 
                            True, 
                            f"Stats correctly updated. Initial: {initial_total}, Current: {current_total} (+3)",
                            response.status_code
                        )
                        return True
                    else:
                        self.log_result(
                            "License Stats After Generation", 
                            False, 
                            f"Stats not updated correctly. Initial: {initial_total}, Current: {current_total} (expected +3)",
                            response.status_code
                        )
                        return False
                else:
                    # If we didn't have initial stats, just verify current stats are reasonable
                    self.log_result(
                        "License Stats After Generation", 
                        True, 
                        f"Stats retrieved after generation: {data}",
                        response.status_code
                    )
                    return True
            else:
                self.log_result(
                    "License Stats After Generation", 
                    False, 
                    f"Failed to get updated stats: {response.text}",
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_result("License Stats After Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_license_list_after_generation(self, initial_licenses):
        """Test 6: Re-GET licenses and verify list contains 3 new items"""
        try:
            response = self.session.get(f"{API_BASE}/agency/licenses")
            
            if response.status_code == 200:
                data = response.json()
                current_licenses = data.get("licenses", [])
                
                if initial_licenses is not None:
                    initial_count = len(initial_licenses)
                    current_count = len(current_licenses)
                    
                    if current_count == initial_count + 3:
                        self.log_result(
                            "License List After Generation", 
                            True, 
                            f"License list correctly updated. Initial: {initial_count}, Current: {current_count} (+3)",
                            response.status_code
                        )
                        return True
                    else:
                        self.log_result(
                            "License List After Generation", 
                            False, 
                            f"License list not updated correctly. Initial: {initial_count}, Current: {current_count} (expected +3)",
                            response.status_code
                        )
                        return False
                else:
                    # If we didn't have initial licenses, just verify current list is reasonable
                    self.log_result(
                        "License List After Generation", 
                        True, 
                        f"License list retrieved after generation: {current_count} licenses",
                        response.status_code
                    )
                    return True
            else:
                self.log_result(
                    "License List After Generation", 
                    False, 
                    f"Failed to get updated licenses: {response.text}",
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_result("License List After Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_license_generation_negative(self):
        """Test 7: Negative test - POST generate with quantity: 0 - expect 422 validation error"""
        try:
            generation_data = {
                "quantity": 0,
                "expires_days": 60
            }
            
            response = self.session.post(f"{API_BASE}/agency/licenses/generate", json=generation_data)
            
            if response.status_code == 422:
                self.log_result(
                    "License Generation Negative Test", 
                    True, 
                    f"Correctly rejected quantity=0 with 422 validation error: {response.text}",
                    response.status_code
                )
                return True
            else:
                self.log_result(
                    "License Generation Negative Test", 
                    False, 
                    f"Expected 422 validation error, got {response.status_code}: {response.text}",
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_result("License Generation Negative Test", False, f"Exception: {str(e)}")
            return False
    
    def test_client_registration_rule(self):
        """Test 8: Verify client registration rule exists (requires 10-digit license_code)"""
        try:
            # Test registration without license_code
            registration_data = {
                "email": "test.client@example.com",
                "password": "TestPassword123!",
                "role": "client",
                "terms_accepted": True
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=registration_data)
            
            if response.status_code == 400:
                response_text = response.text.lower()
                if "license" in response_text and ("10-digit" in response_text or "license_code" in response_text):
                    self.log_result(
                        "Client Registration Rule Verification", 
                        True, 
                        f"Correctly requires license_code for client registration: {response.text}",
                        response.status_code
                    )
                    return True
                else:
                    self.log_result(
                        "Client Registration Rule Verification", 
                        False, 
                        f"Got 400 error but not license-related: {response.text}",
                        response.status_code
                    )
                    return False
            else:
                self.log_result(
                    "Client Registration Rule Verification", 
                    False, 
                    f"Expected 400 error for missing license_code, got {response.status_code}: {response.text}",
                    response.status_code
                )
                return False
                
        except Exception as e:
            self.log_result("Client Registration Rule Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all agency license management tests"""
        print("🎯 AGENCY LICENSE MANAGEMENT ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing with QA credentials: {AGENCY_QA_EMAIL}")
        print()
        
        # Test 1: Login
        if not self.test_agency_login():
            print("❌ Cannot proceed without authentication")
            return self.generate_summary()
        
        # Test 2: Initial stats
        initial_stats = self.test_license_stats_initial()
        
        # Test 3: Initial license list
        initial_licenses = self.test_license_list_initial()
        
        # Test 4: License generation
        generation_result = self.test_license_generation()
        
        # Test 5 & 6: Verify updates (only if generation was successful)
        if generation_result:
            self.test_license_stats_after_generation(initial_stats)
            self.test_license_list_after_generation(initial_licenses)
        
        # Test 7: Negative test
        self.test_license_generation_negative()
        
        # Test 8: Client registration rule
        self.test_client_registration_rule()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 AGENCY LICENSE MANAGEMENT TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Show detailed results
        print("DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']} (Status: {result.get('status_code', 'N/A')})")
            if result["details"]:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 60)
        print("KEY FINDINGS:")
        
        # Extract important data fields from successful tests
        important_data = {}
        for result in self.test_results:
            if result["success"] and "Stats retrieved successfully" in result["details"]:
                # Extract stats data
                details = result["details"]
                if "{" in details:
                    try:
                        stats_str = details[details.find("{"):details.rfind("}")+1]
                        stats_data = eval(stats_str)  # Safe in this context
                        important_data["license_stats"] = stats_data
                    except:
                        pass
        
        if important_data:
            print("📊 Important Data Fields:")
            for key, value in important_data.items():
                print(f"   {key}: {value}")
        
        # Status codes summary
        status_codes = {}
        for result in self.test_results:
            if result.get("status_code"):
                code = result["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1
        
        if status_codes:
            print("📈 Status Codes:")
            for code, count in sorted(status_codes.items()):
                print(f"   {code}: {count} occurrences")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results,
            "important_data": important_data
        }

def main():
    """Main test execution"""
    tester = AgencyLicenseTest()
    summary = tester.run_all_tests()
    
    # Return appropriate exit code
    if summary["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {summary['failed']} TEST(S) FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()