#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Polaris Platform
Tests all user journeys, API endpoints, and production readiness features
"""

import asyncio
import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolarisE2ETester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.test_results = []
        self.tokens = {}
        self.test_data = {}
        
    def log_test_result(self, category: str, test_name: str, success: bool, 
                       details: str = "", response_time: float = 0):
        """Log test result with standardized format"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time_ms': round(response_time * 1000, 2)
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {category} - {test_name} ({response_time*1000:.2f}ms)")
        if details and not success:
            logger.error(f"   Details: {details}")
    
    async def test_system_health(self):
        """Test system health and monitoring endpoints"""
        logger.info("\n🏥 Testing System Health & Monitoring...")
        
        # Basic health check
        start_time = time.time()
        try:
            response = self.session.get(f"{self.api_url}/system/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "system_health", "Basic Health Check", True, 
                    f"Status: {data.get('status', 'unknown')}", response_time
                )
            else:
                self.log_test_result(
                    "system_health", "Basic Health Check", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "system_health", "Basic Health Check", False, str(e), time.time() - start_time
            )
        
        # Performance metrics
        start_time = time.time()
        try:
            response = self.session.get(f"{self.api_url}/system/metrics")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "system_health", "Performance Metrics", True, 
                    f"Metrics available: {len(data.keys())}", response_time
                )
            else:
                self.log_test_result(
                    "system_health", "Performance Metrics", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "system_health", "Performance Metrics", False, str(e), time.time() - start_time
            )
        
        # Enhanced health report (if available)
        start_time = time.time()
        try:
            response = self.session.get(f"{self.api_url}/system/health-report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "system_health", "Enhanced Health Report", True, 
                    f"Status: {data.get('status', 'unknown')}", response_time
                )
            else:
                self.log_test_result(
                    "system_health", "Enhanced Health Report", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "system_health", "Enhanced Health Report", False, str(e), time.time() - start_time
            )
    
    async def test_authentication_flows(self):
        """Test authentication for all user roles"""
        logger.info("\n🔐 Testing Authentication Flows...")
        
        test_users = [
            ("client", "test_client@polaris.example.com", "ClientPass123!"),
            ("provider", "test_provider@polaris.example.com", "ProviderPass123!"),
            ("agency", "test_agency@polaris.example.com", "AgencyPass123!"),
            ("navigator", "test_navigator@polaris.example.com", "NavigatorPass123!")
        ]
        
        for role, email, password in test_users:
            # Test registration
            start_time = time.time()
            try:
                registration_data = {
                    "email": email,
                    "password": password,
                    "role": role
                }
                response = self.session.post(
                    f"{self.api_url}/auth/register", 
                    json=registration_data
                )
                response_time = time.time() - start_time
                
                if response.status_code in [200, 201, 409]:  # 409 = already exists
                    self.log_test_result(
                        "authentication", f"{role.title()} Registration", True, 
                        f"Status: {response.status_code}", response_time
                    )
                else:
                    self.log_test_result(
                        "authentication", f"{role.title()} Registration", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time
                    )
            except Exception as e:
                self.log_test_result(
                    "authentication", f"{role.title()} Registration", False, 
                    str(e), time.time() - start_time
                )
            
            # Test login
            start_time = time.time()
            try:
                login_data = {
                    "email": email,
                    "password": password
                }
                response = self.session.post(
                    f"{self.api_url}/auth/login", 
                    json=login_data
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if 'access_token' in data:
                        self.tokens[role] = data['access_token']
                        self.log_test_result(
                            "authentication", f"{role.title()} Login", True, 
                            "Token obtained", response_time
                        )
                    else:
                        self.log_test_result(
                            "authentication", f"{role.title()} Login", False, 
                            "No access token in response", response_time
                        )
                else:
                    self.log_test_result(
                        "authentication", f"{role.title()} Login", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time
                    )
            except Exception as e:
                self.log_test_result(
                    "authentication", f"{role.title()} Login", False, 
                    str(e), time.time() - start_time
                )
    
    async def test_client_journey(self):
        """Test complete client user journey"""
        logger.info("\n👤 Testing Client User Journey...")
        
        if 'client' not in self.tokens:
            logger.warning("No client token available, skipping client tests")
            return
        
        headers = {'Authorization': f'Bearer {self.tokens["client"]}'}
        
        # Test assessment session creation
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.api_url}/assessment/session", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'session_id' in data:
                    self.test_data['assessment_session_id'] = data['session_id']
                    self.log_test_result(
                        "client_journey", "Assessment Session Creation", True, 
                        f"Session ID: {data['session_id']}", response_time
                    )
                else:
                    self.log_test_result(
                        "client_journey", "Assessment Session Creation", False, 
                        "No session ID in response", response_time
                    )
            else:
                self.log_test_result(
                    "client_journey", "Assessment Session Creation", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "client_journey", "Assessment Session Creation", False, 
                str(e), time.time() - start_time
            )
        
        # Test knowledge base access
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/knowledge-base/areas", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "client_journey", "Knowledge Base Access", True, 
                    f"Areas available: {len(data)}", response_time
                )
            else:
                self.log_test_result(
                    "client_journey", "Knowledge Base Access", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "client_journey", "Knowledge Base Access", False, 
                str(e), time.time() - start_time
            )
        
        # Test service request creation
        start_time = time.time()
        try:
            service_request_data = {
                "area_id": "area5",
                "description": "Need help with cybersecurity assessment",
                "budget_range": "$1000-$5000",
                "timeline": "1-2 weeks",
                "urgency": "medium"
            }
            response = self.session.post(
                f"{self.api_url}/service-requests/professional-help", 
                json=service_request_data,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_data['service_request_id'] = data.get('request_id')
                self.log_test_result(
                    "client_journey", "Service Request Creation", True, 
                    f"Request ID: {data.get('request_id')}", response_time
                )
            else:
                self.log_test_result(
                    "client_journey", "Service Request Creation", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "client_journey", "Service Request Creation", False, 
                str(e), time.time() - start_time
            )
    
    async def test_provider_journey(self):
        """Test provider user journey"""
        logger.info("\n🔧 Testing Provider User Journey...")
        
        if 'provider' not in self.tokens:
            logger.warning("No provider token available, skipping provider tests")
            return
        
        headers = {'Authorization': f'Bearer {self.tokens["provider"]}'}
        
        # Test business profile creation/update
        start_time = time.time()
        try:
            profile_data = {
                "company_name": "Test Tech Solutions",
                "business_type": "Technology Services",
                "description": "Cybersecurity and technology services",
                "service_areas": ["Technology & Security Infrastructure"],
                "contact_phone": "555-0123",
                "website": "https://testtechsolutions.com",
                "years_in_business": 5,
                "certifications": ["ISO 27001"],
                "hourly_rate": 150
            }
            
            # Try POST first
            response = self.session.post(
                f"{self.api_url}/business/profile", 
                json=profile_data,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                # Try PUT if POST fails
                response = self.session.put(
                    f"{self.api_url}/business/profile/me", 
                    json=profile_data,
                    headers=headers
                )
            
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                self.log_test_result(
                    "provider_journey", "Business Profile Setup", True, 
                    "Profile created/updated", response_time
                )
            else:
                self.log_test_result(
                    "provider_journey", "Business Profile Setup", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "provider_journey", "Business Profile Setup", False, 
                str(e), time.time() - start_time
            )
        
        # Test provider dashboard access
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/provider/dashboard", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result(
                    "provider_journey", "Provider Dashboard Access", True, 
                    "Dashboard accessible", response_time
                )
            else:
                self.log_test_result(
                    "provider_journey", "Provider Dashboard Access", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "provider_journey", "Provider Dashboard Access", False, 
                str(e), time.time() - start_time
            )
    
    async def test_agency_features(self):
        """Test agency-specific features"""
        logger.info("\n🏢 Testing Agency Features...")
        
        if 'agency' not in self.tokens:
            logger.warning("No agency token available, skipping agency tests")
            return
        
        headers = {'Authorization': f'Bearer {self.tokens["agency"]}'}
        
        # Test agency dashboard
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/agency/dashboard", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result(
                    "agency_features", "Agency Dashboard", True, 
                    "Dashboard accessible", response_time
                )
            else:
                self.log_test_result(
                    "agency_features", "Agency Dashboard", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "agency_features", "Agency Dashboard", False, 
                str(e), time.time() - start_time
            )
        
        # Test license management
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/agency/licenses", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result(
                    "agency_features", "License Management", True, 
                    "License endpoints accessible", response_time
                )
            else:
                self.log_test_result(
                    "agency_features", "License Management", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "agency_features", "License Management", False, 
                str(e), time.time() - start_time
            )
    
    async def test_navigator_features(self):
        """Test navigator/admin features"""
        logger.info("\n🧭 Testing Navigator Features...")
        
        if 'navigator' not in self.tokens:
            logger.warning("No navigator token available, skipping navigator tests")
            return
        
        headers = {'Authorization': f'Bearer {self.tokens["navigator"]}'}
        
        # Test system analytics
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/navigator/analytics/resources", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result(
                    "navigator_features", "System Analytics", True, 
                    "Analytics accessible", response_time
                )
            else:
                self.log_test_result(
                    "navigator_features", "System Analytics", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "navigator_features", "System Analytics", False, 
                str(e), time.time() - start_time
            )
        
        # Test approval queue
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.api_url}/navigator/approvals", 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result(
                    "navigator_features", "Approval Queue", True, 
                    "Approval queue accessible", response_time
                )
            else:
                self.log_test_result(
                    "navigator_features", "Approval Queue", False, 
                    f"HTTP {response.status_code}", response_time
                )
        except Exception as e:
            self.log_test_result(
                "navigator_features", "Approval Queue", False, 
                str(e), time.time() - start_time
            )
    
    async def test_api_performance(self):
        """Test API performance and response times"""
        logger.info("\n⚡ Testing API Performance...")
        
        test_endpoints = [
            ("GET", "/system/health", None),
            ("GET", "/knowledge-base/areas", None),
            ("GET", "/auth/password-requirements", None),
        ]
        
        for method, endpoint, data in test_endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = self.session.get(f"{self.api_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.api_url}{endpoint}", json=data)
                
                response_time = time.time() - start_time
                
                # Check if response time meets SLA (< 500ms for most endpoints)
                performance_ok = response_time < 0.5
                
                self.log_test_result(
                    "api_performance", f"{method} {endpoint}", 
                    performance_ok and response.status_code < 500,
                    f"Status: {response.status_code}, SLA: {'✓' if performance_ok else '✗'}", 
                    response_time
                )
            except Exception as e:
                self.log_test_result(
                    "api_performance", f"{method} {endpoint}", False, 
                    str(e), time.time() - start_time
                )
    
    async def test_security_features(self):
        """Test security features and error handling"""
        logger.info("\n🔒 Testing Security Features...")
        
        # Test rate limiting (should be handled gracefully)
        start_time = time.time()
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(10):
                response = self.session.get(f"{self.api_url}/system/health")
                responses.append(response.status_code)
            
            response_time = time.time() - start_time
            
            # All requests should either succeed or be rate limited gracefully
            all_valid = all(code in [200, 429] for code in responses)
            
            self.log_test_result(
                "security", "Rate Limiting Handling", all_valid,
                f"Response codes: {set(responses)}", response_time
            )
        except Exception as e:
            self.log_test_result(
                "security", "Rate Limiting Handling", False, 
                str(e), time.time() - start_time
            )
        
        # Test invalid input handling
        start_time = time.time()
        try:
            invalid_data = {
                "email": "not_an_email",
                "password": "x" * 10000,  # Too long
                "role": "invalid_role"
            }
            response = self.session.post(
                f"{self.api_url}/auth/register", 
                json=invalid_data
            )
            response_time = time.time() - start_time
            
            # Should return 400 or 422 for invalid data
            error_handled = response.status_code in [400, 422]
            
            self.log_test_result(
                "security", "Invalid Input Handling", error_handled,
                f"Status: {response.status_code}", response_time
            )
        except Exception as e:
            self.log_test_result(
                "security", "Invalid Input Handling", False, 
                str(e), time.time() - start_time
            )
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        # Calculate average response time by category
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        category_stats = {}
        for cat, results in categories.items():
            category_stats[cat] = {
                'total': len(results),
                'passed': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'avg_response_time': sum(r['response_time_ms'] for r in results) / len(results)
            }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                'total_duration': sum(r['response_time_ms'] for r in self.test_results),
                'avg_response_time': sum(r['response_time_ms'] for r in self.test_results) / total_tests if total_tests > 0 else 0
            },
            'category_breakdown': category_stats,
            'failed_tests': [r for r in self.test_results if not r['success']],
            'all_results': self.test_results
        }
        
        return report
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        logger.info("🚀 Starting Polaris Platform E2E Test Suite")
        logger.info(f"Target URL: {self.base_url}")
        logger.info(f"Test started at: {datetime.now()}")
        
        # Run all test categories
        await self.test_system_health()
        await self.test_authentication_flows()
        await self.test_client_journey()
        await self.test_provider_journey()
        await self.test_agency_features()
        await self.test_navigator_features()
        await self.test_api_performance()
        await self.test_security_features()
        
        # Generate and save report
        report = self.generate_report()
        
        # Save report to file
        with open('e2e_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 E2E TEST SUITE SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"✅ Passed: {report['summary']['passed']}")
        logger.info(f"❌ Failed: {report['summary']['failed']}")
        logger.info(f"📈 Success Rate: {report['summary']['success_rate']}%")
        logger.info(f"⏱️  Average Response Time: {report['summary']['avg_response_time']:.2f}ms")
        logger.info(f"📄 Detailed report saved to: e2e_test_report.json")
        
        if report['summary']['failed'] > 0:
            logger.warning("\n❌ FAILED TESTS:")
            for failed_test in report['failed_tests']:
                logger.warning(f"  - {failed_test['category']}/{failed_test['test_name']}: {failed_test['details']}")
        
        return report

async def main():
    """Main test execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polaris Platform E2E Test Suite')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the Polaris platform')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    tester = PolarisE2ETester(args.url)
    
    try:
        report = await tester.run_all_tests()
        
        # Exit with error code if tests failed
        if report['summary']['failed'] > 0:
            exit(1)
        else:
            logger.info("🎉 All tests passed!")
            exit(0)
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())