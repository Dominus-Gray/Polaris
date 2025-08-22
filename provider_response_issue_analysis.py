#!/usr/bin/env python3
"""
Provider Response Issue Analysis
Detailed analysis of the specific validation issues identified.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://readiness-hub-2.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "provider": {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class ProviderResponseIssueAnalyzer:
    def __init__(self):
        self.tokens = {}
        self.issues_found = []
        
    def log_result(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def add_issue(self, issue_type, description, severity="HIGH", recommendation=""):
        issue = {
            "type": issue_type,
            "description": description,
            "severity": severity,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }
        self.issues_found.append(issue)
        
        severity_icon = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "HIGH" else "ℹ️"
        self.log_result(f"{severity_icon} {issue_type}: {description}")
    
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
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def analyze_database_field_mismatch(self):
        """Analyze the database field mismatch issue"""
        self.log_result("🔍 ANALYZING: Database Field Mismatch Issue")
        
        # Create a service request
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        payload = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Analysis test - database field mismatch investigation",
            "priority": "high"
        }
        
        try:
            # Create service request
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                
                # Try to retrieve using different endpoints
                retrieval_tests = [
                    {"endpoint": f"/service-requests/{request_id}", "description": "Individual service request retrieval"},
                    {"endpoint": f"/service-requests/{request_id}/responses", "description": "Service request responses retrieval"},
                    {"endpoint": "/service-requests/my", "description": "My service requests list"}
                ]
                
                for test in retrieval_tests:
                    try:
                        get_response = requests.get(f"{BASE_URL}{test['endpoint']}", headers=headers)
                        
                        if get_response.status_code == 404:
                            self.add_issue(
                                "DATABASE_FIELD_MISMATCH",
                                f"{test['description']} returns 404 even though service request was created successfully. "
                                f"This indicates a field name mismatch between creation and retrieval queries.",
                                "CRITICAL",
                                "Fix the database query field names to match the document structure. "
                                "Service requests are created with 'client_id' but retrieved using 'user_id'."
                            )
                        elif get_response.status_code == 200:
                            self.log_result(f"✅ {test['description']} works correctly")
                            
                    except Exception as e:
                        self.add_issue(
                            "RETRIEVAL_ERROR",
                            f"Error testing {test['description']}: {str(e)}",
                            "HIGH"
                        )
                        
            else:
                self.add_issue(
                    "SERVICE_REQUEST_CREATION_FAILED",
                    f"Service request creation failed with status {response.status_code}",
                    "CRITICAL"
                )
                
        except Exception as e:
            self.add_issue(
                "ANALYSIS_ERROR",
                f"Error during database field mismatch analysis: {str(e)}",
                "HIGH"
            )
    
    def analyze_provider_response_validation(self):
        """Analyze provider response validation logic"""
        self.log_result("🔍 ANALYZING: Provider Response Validation Logic")
        
        # Create a service request first
        headers = {"Authorization": f"Bearer {self.tokens['client']}"}
        payload = {
            "area_id": "area5",
            "budget_range": "1500-5000",
            "timeline": "2-4 weeks",
            "description": "Provider response validation analysis test",
            "priority": "high"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                
                # Test provider response creation
                provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
                provider_payload = {
                    "request_id": request_id,
                    "proposed_fee": 2500.00,
                    "estimated_timeline": "2-4 weeks",
                    "proposal_note": "Analysis test response - comprehensive proposal for validation testing."
                }
                
                provider_response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=provider_payload, headers=provider_headers)
                
                if provider_response.status_code == 200:
                    self.log_result("✅ Provider response creation works correctly")
                    
                    # Test edge cases
                    edge_cases = [
                        {"fee": -100, "expected": "rejection", "description": "Negative fee"},
                        {"fee": 0, "expected": "rejection", "description": "Zero fee"},
                        {"fee": 75000, "expected": "rejection", "description": "Excessive fee"},
                    ]
                    
                    for case in edge_cases:
                        # Create new service request for each test
                        new_response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
                        if new_response.status_code == 200:
                            new_request_id = new_response.json().get("request_id")
                            
                            test_payload = provider_payload.copy()
                            test_payload["request_id"] = new_request_id
                            test_payload["proposed_fee"] = case["fee"]
                            
                            test_response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=test_payload, headers=provider_headers)
                            
                            if test_response.status_code in [400, 422] and case["expected"] == "rejection":
                                self.log_result(f"✅ {case['description']} correctly rejected")
                            elif test_response.status_code == 200 and case["expected"] == "acceptance":
                                self.log_result(f"✅ {case['description']} correctly accepted")
                            else:
                                self.add_issue(
                                    "VALIDATION_LOGIC_ERROR",
                                    f"{case['description']} validation failed: expected {case['expected']} but got status {test_response.status_code}",
                                    "HIGH",
                                    "Review and fix the validation logic for provider response fields"
                                )
                else:
                    self.add_issue(
                        "PROVIDER_RESPONSE_CREATION_FAILED",
                        f"Provider response creation failed with status {provider_response.status_code}: {provider_response.text}",
                        "CRITICAL"
                    )
                    
        except Exception as e:
            self.add_issue(
                "VALIDATION_ANALYSIS_ERROR",
                f"Error during provider response validation analysis: {str(e)}",
                "HIGH"
            )
    
    def analyze_data_consistency(self):
        """Analyze data consistency between collections"""
        self.log_result("🔍 ANALYZING: Data Consistency Between Collections")
        
        # This analysis focuses on the relationship between:
        # - service_requests collection
        # - provider_responses collection
        # - notifications collection
        
        try:
            # Create service request and provider response
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            payload = {
                "area_id": "area5",
                "budget_range": "1500-5000",
                "timeline": "2-4 weeks",
                "description": "Data consistency analysis test",
                "priority": "high"
            }
            
            response = requests.post(f"{BASE_URL}/service-requests/professional-help", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                
                # Create provider response
                provider_headers = {"Authorization": f"Bearer {self.tokens['provider']}"}
                provider_payload = {
                    "request_id": request_id,
                    "proposed_fee": 3000.00,
                    "estimated_timeline": "1-2 months",
                    "proposal_note": "Data consistency test response - comprehensive analysis and implementation proposal."
                }
                
                provider_response = requests.post(f"{BASE_URL}/provider/respond-to-request", json=provider_payload, headers=provider_headers)
                
                if provider_response.status_code == 200:
                    provider_data = provider_response.json()
                    response_id = provider_data.get("response_id")
                    
                    # Check if data is consistent
                    consistency_checks = [
                        {"field": "request_id", "expected": request_id, "actual": provider_data.get("request_id")},
                        {"field": "proposed_fee", "expected": "$3,000.00", "actual": provider_data.get("proposed_fee")},
                        {"field": "estimated_timeline", "expected": "1-2 months", "actual": provider_data.get("estimated_timeline")}
                    ]
                    
                    for check in consistency_checks:
                        if check["expected"] != check["actual"]:
                            self.add_issue(
                                "DATA_CONSISTENCY_ERROR",
                                f"Field {check['field']} inconsistency: expected '{check['expected']}', got '{check['actual']}'",
                                "HIGH",
                                "Ensure data transformation and storage maintains consistency"
                            )
                        else:
                            self.log_result(f"✅ {check['field']} data consistency verified")
                            
                    # Try to retrieve the response through client endpoint
                    get_response = requests.get(f"{BASE_URL}/service-requests/{request_id}/responses", headers=headers)
                    
                    if get_response.status_code == 404:
                        self.add_issue(
                            "RESPONSE_RETRIEVAL_FAILURE",
                            "Provider response was created successfully but cannot be retrieved through client endpoint",
                            "CRITICAL",
                            "Fix the database query mismatch between service request creation and retrieval"
                        )
                    elif get_response.status_code == 200:
                        self.log_result("✅ Provider response retrieval works correctly")
                        
                else:
                    self.add_issue(
                        "PROVIDER_RESPONSE_FAILED",
                        f"Provider response creation failed: {provider_response.status_code}",
                        "HIGH"
                    )
                    
        except Exception as e:
            self.add_issue(
                "CONSISTENCY_ANALYSIS_ERROR",
                f"Error during data consistency analysis: {str(e)}",
                "HIGH"
            )
    
    def run_comprehensive_analysis(self):
        """Run comprehensive analysis of provider response validation issues"""
        self.log_result("🔬 Starting Comprehensive Provider Response Issue Analysis")
        self.log_result("=" * 70)
        
        # Login users
        if not self.login_user("client") or not self.login_user("provider"):
            self.log_result("❌ Failed to login users - cannot proceed with analysis")
            return False
        
        # Run analysis modules
        analysis_modules = [
            self.analyze_database_field_mismatch,
            self.analyze_provider_response_validation,
            self.analyze_data_consistency
        ]
        
        for module in analysis_modules:
            try:
                module()
                self.log_result("")  # Add spacing
            except Exception as e:
                self.add_issue(
                    "ANALYSIS_MODULE_ERROR",
                    f"Error in {module.__name__}: {str(e)}",
                    "HIGH"
                )
        
        return True
    
    def print_final_analysis_report(self):
        """Print comprehensive analysis report"""
        self.log_result("=" * 70)
        self.log_result("📋 PROVIDER RESPONSE VALIDATION ISSUE ANALYSIS REPORT")
        self.log_result("=" * 70)
        
        if not self.issues_found:
            self.log_result("✅ NO CRITICAL ISSUES IDENTIFIED")
            return
        
        # Group issues by severity
        critical_issues = [i for i in self.issues_found if i["severity"] == "CRITICAL"]
        high_issues = [i for i in self.issues_found if i["severity"] == "HIGH"]
        medium_issues = [i for i in self.issues_found if i["severity"] == "MEDIUM"]
        
        self.log_result(f"📊 ISSUE SUMMARY:")
        self.log_result(f"  🚨 Critical Issues: {len(critical_issues)}")
        self.log_result(f"  ⚠️  High Priority Issues: {len(high_issues)}")
        self.log_result(f"  ℹ️  Medium Priority Issues: {len(medium_issues)}")
        self.log_result(f"  📈 Total Issues: {len(self.issues_found)}")
        
        # Detail critical issues
        if critical_issues:
            self.log_result(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            for i, issue in enumerate(critical_issues, 1):
                self.log_result(f"  {i}. {issue['type']}")
                self.log_result(f"     Description: {issue['description']}")
                if issue['recommendation']:
                    self.log_result(f"     Recommendation: {issue['recommendation']}")
                self.log_result("")
        
        # Detail high priority issues
        if high_issues:
            self.log_result(f"⚠️ HIGH PRIORITY ISSUES ({len(high_issues)}):")
            for i, issue in enumerate(high_issues, 1):
                self.log_result(f"  {i}. {issue['type']}")
                self.log_result(f"     Description: {issue['description']}")
                if issue['recommendation']:
                    self.log_result(f"     Recommendation: {issue['recommendation']}")
                self.log_result("")
        
        # Key recommendations
        self.log_result("🔧 KEY RECOMMENDATIONS:")
        recommendations = set()
        for issue in self.issues_found:
            if issue['recommendation']:
                recommendations.add(issue['recommendation'])
        
        for i, rec in enumerate(recommendations, 1):
            self.log_result(f"  {i}. {rec}")

def main():
    """Main analysis execution"""
    analyzer = ProviderResponseIssueAnalyzer()
    
    try:
        success = analyzer.run_comprehensive_analysis()
        analyzer.print_final_analysis_report()
        
        critical_count = len([i for i in analyzer.issues_found if i["severity"] == "CRITICAL"])
        
        if success and critical_count == 0:
            print("\n✅ ANALYSIS COMPLETED - NO CRITICAL ISSUES FOUND")
            sys.exit(0)
        elif success:
            print(f"\n🚨 ANALYSIS COMPLETED - {critical_count} CRITICAL ISSUES IDENTIFIED")
            sys.exit(1)
        else:
            print("\n❌ ANALYSIS FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()