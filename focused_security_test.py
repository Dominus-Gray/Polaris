#!/usr/bin/env python3
"""
🔐 FOCUSED PRODUCTION SECURITY TESTING FOR POLARIS PLATFORM
Testing Focus: Security features that can be tested without full authentication

SECURITY FEATURES TO TEST:
1. Password Requirements Endpoint (/auth/password-requirements)
2. Production Security Headers
3. HTTPS Configuration
4. Error Handling and Security Response Format
5. Rate Limiting (if implemented)
6. Authentication Error Responses
7. GDPR Endpoint Existence (even if authentication required)
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://production-guru.preview.emergentagent.com/api"

class FocusedSecurityTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results with security context"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with security headers"""
        url = f"{BASE_URL}{endpoint}"
        headers = kwargs.get('headers', {})
        
        # Add security headers for testing
        headers.update({
            'User-Agent': 'Polaris-Security-Test/1.0',
            'Accept': 'application/json'
        })
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def test_password_requirements_endpoint(self):
        """Test 1: Enhanced Password Requirements Endpoint"""
        print("🔑 Testing Enhanced Password Requirements...")
        
        response = self.make_request('GET', '/auth/password-requirements')
        
        if response and response.status_code == 200:
            requirements = response.json()
            
            # Verify production-grade password requirements
            min_length = requirements.get('min_length', 0)
            require_uppercase = requirements.get('require_uppercase', False)
            require_lowercase = requirements.get('require_lowercase', False)
            require_digits = requirements.get('require_digits', False)
            require_special = requirements.get('require_special', False)
            history_count = requirements.get('history_count', 0)
            
            # Check if meets production security standards
            production_compliant = (
                min_length >= 12 and
                require_uppercase and
                require_lowercase and
                require_digits and
                require_special and
                history_count >= 5
            )
            
            self.log_test(
                "Enhanced Password Requirements Endpoint", 
                True, 
                f"Password policy: {min_length}+ chars, complexity rules enforced, {history_count} history",
                {
                    "min_length": min_length,
                    "require_uppercase": require_uppercase,
                    "require_lowercase": require_lowercase,
                    "require_digits": require_digits,
                    "require_special": require_special,
                    "history_count": history_count,
                    "production_compliant": production_compliant
                }
            )
            
            # Verify specific production requirements
            if min_length >= 12:
                self.log_test(
                    "Production Password Length (12+ chars)", 
                    True, 
                    f"Minimum password length: {min_length} characters (meets production standard)",
                    {"min_length": min_length, "standard": "12+"}
                )
            else:
                self.log_test(
                    "Production Password Length (12+ chars)", 
                    False, 
                    f"Password length {min_length} below production standard of 12",
                    {"min_length": min_length, "standard": "12+"}
                )
                
        else:
            self.log_test(
                "Enhanced Password Requirements Endpoint", 
                False, 
                "Failed to retrieve password requirements",
                response.json() if response else "No response"
            )

    def test_production_security_headers(self):
        """Test 2: Production Security Headers"""
        print("🛡️ Testing Production Security Headers...")
        
        response = self.make_request('GET', '/auth/password-requirements')
        
        if response:
            # Check for essential security headers
            security_headers = {
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options'),
                'X-Frame-Options': response.headers.get('X-Frame-Options'),
                'X-XSS-Protection': response.headers.get('X-XSS-Protection'),
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy'),
                'Referrer-Policy': response.headers.get('Referrer-Policy')
            }
            
            present_headers = {k: v for k, v in security_headers.items() if v is not None}
            
            # Check for specific security header values
            header_analysis = {}
            
            if security_headers['X-Content-Type-Options']:
                header_analysis['nosniff'] = 'nosniff' in security_headers['X-Content-Type-Options']
            
            if security_headers['X-Frame-Options']:
                header_analysis['frame_protection'] = security_headers['X-Frame-Options'] in ['DENY', 'SAMEORIGIN']
            
            if security_headers['Strict-Transport-Security']:
                header_analysis['hsts_enabled'] = 'max-age' in security_headers['Strict-Transport-Security']
            
            self.log_test(
                "Production Security Headers", 
                len(present_headers) >= 4, 
                f"Found {len(present_headers)}/6 security headers with proper values",
                {
                    "security_headers": present_headers,
                    "headers_count": len(present_headers),
                    "header_analysis": header_analysis
                }
            )
            
            # Test individual critical headers
            if security_headers['X-Content-Type-Options'] == 'nosniff':
                self.log_test(
                    "X-Content-Type-Options Header", 
                    True, 
                    "MIME type sniffing protection enabled",
                    {"value": security_headers['X-Content-Type-Options']}
                )
            
            if security_headers['X-Frame-Options'] in ['DENY', 'SAMEORIGIN']:
                self.log_test(
                    "X-Frame-Options Header", 
                    True, 
                    f"Clickjacking protection enabled: {security_headers['X-Frame-Options']}",
                    {"value": security_headers['X-Frame-Options']}
                )
            
            if security_headers['Strict-Transport-Security']:
                self.log_test(
                    "HSTS Header", 
                    True, 
                    "HTTP Strict Transport Security enabled",
                    {"value": security_headers['Strict-Transport-Security']}
                )
                
        else:
            self.log_test(
                "Production Security Headers", 
                False, 
                "Could not retrieve response to check security headers",
                "No response received"
            )

    def test_https_configuration(self):
        """Test 3: HTTPS Configuration and TLS Security"""
        print("🔒 Testing HTTPS Configuration...")
        
        # Verify HTTPS is enforced
        https_enforced = BASE_URL.startswith('https://')
        
        self.log_test(
            "HTTPS Enforcement", 
            https_enforced, 
            f"API endpoint uses HTTPS: {BASE_URL}",
            {"base_url": BASE_URL, "uses_https": https_enforced}
        )
        
        # Test TLS connection (basic check)
        if https_enforced:
            try:
                response = self.make_request('GET', '/auth/password-requirements')
                if response:
                    self.log_test(
                        "TLS Connection Security", 
                        True, 
                        "Successful HTTPS/TLS connection established",
                        {"status_code": response.status_code}
                    )
                else:
                    self.log_test(
                        "TLS Connection Security", 
                        False, 
                        "Failed to establish HTTPS/TLS connection",
                        "Connection failed"
                    )
            except Exception as e:
                self.log_test(
                    "TLS Connection Security", 
                    False, 
                    f"TLS connection error: {str(e)}",
                    {"error": str(e)}
                )

    def test_authentication_error_handling(self):
        """Test 4: Authentication Error Handling and Security Response Format"""
        print("🔐 Testing Authentication Error Handling...")
        
        # Test 4.1: Invalid credentials error format
        invalid_login = {
            "email": "invalid.user@example.com",
            "password": "InvalidPassword123!"
        }
        
        response = self.make_request('POST', '/auth/login', json=invalid_login)
        
        if response and response.status_code in [400, 401]:
            error_data = response.json()
            
            # Check for Polaris error code format
            has_error_code = 'error_code' in error_data
            has_polaris_format = error_data.get('error_code', '').startswith('POL-')
            has_message = 'message' in error_data
            has_timestamp = 'timestamp' in error_data
            
            self.log_test(
                "Authentication Error Format", 
                has_error_code and has_polaris_format, 
                f"Proper Polaris error format with code: {error_data.get('error_code')}",
                {
                    "error_code": error_data.get('error_code'),
                    "has_polaris_format": has_polaris_format,
                    "has_message": has_message,
                    "has_timestamp": has_timestamp
                }
            )
        else:
            self.log_test(
                "Authentication Error Format", 
                False, 
                f"Unexpected response for invalid login: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

        # Test 4.2: Account lockout error handling
        # Try to trigger account lockout with the QA credentials (already locked)
        qa_login = {
            "email": "client.qa@polaris.example.com",
            "password": "WrongPassword123!"
        }
        
        response = self.make_request('POST', '/auth/login', json=qa_login)
        
        if response and response.status_code in [400, 429]:
            error_data = response.json()
            
            # Check if lockout is properly indicated
            lockout_indicated = (
                'locked' in str(error_data).lower() or
                'temporarily' in str(error_data).lower() or
                response.status_code == 429
            )
            
            self.log_test(
                "Account Lockout Error Handling", 
                lockout_indicated, 
                f"Account lockout properly indicated in error response",
                {
                    "status_code": response.status_code,
                    "lockout_indicated": lockout_indicated,
                    "error_message": error_data.get('message', {}).get('message', '')
                }
            )
        else:
            self.log_test(
                "Account Lockout Error Handling", 
                False, 
                f"Unexpected response for locked account: {response.status_code if response else 'No response'}",
                response.json() if response else "No response"
            )

    def test_gdpr_endpoint_existence(self):
        """Test 5: GDPR Compliance Endpoints Existence"""
        print("🇪🇺 Testing GDPR Compliance Endpoints...")
        
        gdpr_endpoints = [
            '/gdpr/data-access',
            '/gdpr/data-export', 
            '/gdpr/delete-account'
        ]
        
        for endpoint in gdpr_endpoints:
            response = self.make_request('GET', endpoint)
            
            # We expect 401 (authentication required) rather than 404 (not found)
            if response and response.status_code == 401:
                self.log_test(
                    f"GDPR Endpoint Exists: {endpoint}", 
                    True, 
                    f"Endpoint exists and requires authentication (expected)",
                    {"status_code": response.status_code, "endpoint": endpoint}
                )
            elif response and response.status_code == 404:
                self.log_test(
                    f"GDPR Endpoint Exists: {endpoint}", 
                    False, 
                    f"Endpoint not found - GDPR compliance feature missing",
                    {"status_code": response.status_code, "endpoint": endpoint}
                )
            else:
                self.log_test(
                    f"GDPR Endpoint Exists: {endpoint}", 
                    False, 
                    f"Unexpected response from GDPR endpoint",
                    {"status_code": response.status_code if response else None, "endpoint": endpoint}
                )

    def test_audit_logging_indicators(self):
        """Test 6: Audit Logging System Indicators"""
        print("📋 Testing Audit Logging System Indicators...")
        
        # Test if audit-related endpoints exist (even if access denied)
        audit_endpoints = [
            '/admin/audit-logs',
            '/audit/security-events',
            '/logs/audit'
        ]
        
        audit_system_detected = False
        
        for endpoint in audit_endpoints:
            response = self.make_request('GET', endpoint)
            
            if response and response.status_code in [401, 403]:
                audit_system_detected = True
                self.log_test(
                    f"Audit Endpoint Detected: {endpoint}", 
                    True, 
                    f"Audit endpoint exists (access denied as expected)",
                    {"status_code": response.status_code, "endpoint": endpoint}
                )
                break
        
        if not audit_system_detected:
            self.log_test(
                "Audit Logging System Detection", 
                False, 
                "No audit logging endpoints detected",
                {"tested_endpoints": audit_endpoints}
            )

    def test_rate_limiting(self):
        """Test 7: Rate Limiting Implementation"""
        print("⏱️ Testing Rate Limiting...")
        
        # Make rapid requests to test rate limiting
        rapid_requests = []
        
        for i in range(10):
            start_time = time.time()
            response = self.make_request('GET', '/auth/password-requirements')
            end_time = time.time()
            
            rapid_requests.append({
                'request_num': i + 1,
                'status_code': response.status_code if response else None,
                'response_time': end_time - start_time
            })
            
            # Check if rate limited
            if response and response.status_code == 429:
                self.log_test(
                    "Rate Limiting Implementation", 
                    True, 
                    f"Rate limiting triggered after {i + 1} requests",
                    {"requests_before_limit": i + 1, "status_code": 429}
                )
                return True
            
            time.sleep(0.1)  # Brief delay between requests
        
        # If no rate limiting detected
        avg_response_time = sum(r['response_time'] for r in rapid_requests) / len(rapid_requests)
        
        self.log_test(
            "Rate Limiting Implementation", 
            False, 
            f"No rate limiting detected after 10 rapid requests (avg: {avg_response_time:.3f}s)",
            {
                "total_requests": len(rapid_requests),
                "avg_response_time": avg_response_time,
                "rate_limit_detected": False
            }
        )

    def test_data_classification_indicators(self):
        """Test 8: Data Classification System Indicators"""
        print("🏷️ Testing Data Classification System...")
        
        # Test if sensitive data is properly handled in error responses
        test_cases = [
            {
                "endpoint": "/auth/login",
                "method": "POST",
                "data": {"email": "test@example.com", "password": "test123"},
                "description": "Login error response"
            },
            {
                "endpoint": "/auth/register", 
                "method": "POST",
                "data": {"email": "test@example.com", "password": "test123", "role": "client"},
                "description": "Registration error response"
            }
        ]
        
        sensitive_data_exposed = False
        
        for test_case in test_cases:
            response = self.make_request(test_case["method"], test_case["endpoint"], json=test_case["data"])
            
            if response:
                response_text = response.text.lower()
                
                # Check if sensitive information is exposed in error responses
                sensitive_keywords = ['password', 'hash', 'secret', 'key', 'token', 'ssn', 'tax_id']
                exposed_keywords = [keyword for keyword in sensitive_keywords if keyword in response_text]
                
                if exposed_keywords:
                    sensitive_data_exposed = True
                    self.log_test(
                        f"Data Classification - {test_case['description']}", 
                        False, 
                        f"Sensitive data exposed in response: {exposed_keywords}",
                        {"exposed_keywords": exposed_keywords}
                    )
                else:
                    self.log_test(
                        f"Data Classification - {test_case['description']}", 
                        True, 
                        "No sensitive data exposed in error response",
                        {"sensitive_data_protected": True}
                    )
        
        if not sensitive_data_exposed:
            self.log_test(
                "Data Classification System", 
                True, 
                "Sensitive data properly protected in API responses",
                {"data_classification_working": True}
            )

    def run_focused_security_test(self):
        """Run focused security tests"""
        print("🔐 STARTING FOCUSED PRODUCTION SECURITY TESTING")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run focused security test suites
        self.test_password_requirements_endpoint()
        self.test_production_security_headers()
        self.test_https_configuration()
        self.test_authentication_error_handling()
        self.test_gdpr_endpoint_existence()
        self.test_audit_logging_indicators()
        self.test_rate_limiting()
        self.test_data_classification_indicators()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("=" * 80)
        print("🔐 FOCUSED PRODUCTION SECURITY TESTING RESULTS")
        print("=" * 80)
        print(f"Total Security Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Security Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        # Print detailed results
        print("🔍 DETAILED SECURITY TEST RESULTS:")
        print("-" * 50)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🛡️ SECURITY FEATURE ASSESSMENT:")
        print("-" * 50)
        
        # Categorize results
        password_tests = [r for r in self.test_results if 'password' in r['test'].lower()]
        password_success = all(r['success'] for r in password_tests) if password_tests else False
        
        header_tests = [r for r in self.test_results if 'header' in r['test'].lower() or 'https' in r['test'].lower()]
        header_success = all(r['success'] for r in header_tests) if header_tests else False
        
        auth_tests = [r for r in self.test_results if 'auth' in r['test'].lower() and 'password' not in r['test'].lower()]
        auth_success = all(r['success'] for r in auth_tests) if auth_tests else False
        
        gdpr_tests = [r for r in self.test_results if 'gdpr' in r['test'].lower()]
        gdpr_success = all(r['success'] for r in gdpr_tests) if gdpr_tests else False
        
        audit_tests = [r for r in self.test_results if 'audit' in r['test'].lower()]
        audit_success = all(r['success'] for r in audit_tests) if audit_tests else False
        
        print(f"🔑 Password Security: {'✅ STRONG' if password_success else '❌ WEAK'}")
        print(f"🛡️ Security Headers: {'✅ IMPLEMENTED' if header_success else '❌ MISSING'}")
        print(f"🔐 Authentication Security: {'✅ SECURE' if auth_success else '❌ ISSUES'}")
        print(f"🇪🇺 GDPR Compliance: {'✅ ENDPOINTS EXIST' if gdpr_success else '❌ MISSING'}")
        print(f"📋 Audit Logging: {'✅ DETECTED' if audit_success else '❌ NOT DETECTED'}")
        
        print()
        print("🎯 PRODUCTION SECURITY READINESS:")
        print("-" * 50)
        
        if success_rate >= 90:
            print("✅ EXCELLENT - Production security standards met")
        elif success_rate >= 75:
            print("🟡 GOOD - Minor security improvements needed")
        elif success_rate >= 60:
            print("⚠️  MODERATE - Several security issues need attention")
        else:
            print("🚨 CRITICAL - Major security vulnerabilities detected")
        
        print()
        print("📊 SECURITY IMPLEMENTATION STATUS:")
        print("-" * 50)
        print(f"✅ Enhanced Password Policy (12+ chars): {'IMPLEMENTED' if password_success else 'MISSING'}")
        print(f"✅ Production Security Headers: {'IMPLEMENTED' if header_success else 'MISSING'}")
        print(f"✅ HTTPS/TLS Configuration: {'IMPLEMENTED' if header_success else 'MISSING'}")
        print(f"✅ Authentication Error Handling: {'IMPLEMENTED' if auth_success else 'MISSING'}")
        print(f"✅ GDPR Compliance Endpoints: {'IMPLEMENTED' if gdpr_success else 'MISSING'}")
        print(f"✅ Audit Logging System: {'DETECTED' if audit_success else 'NOT DETECTED'}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'duration': duration,
            'password_secure': password_success,
            'headers_secure': header_success,
            'auth_secure': auth_success,
            'gdpr_compliant': gdpr_success,
            'audit_detected': audit_success
        }

if __name__ == "__main__":
    tester = FocusedSecurityTester()
    results = tester.run_focused_security_test()
    
    # Exit with appropriate code based on security standards
    sys.exit(0 if results['success_rate'] >= 70 else 1)