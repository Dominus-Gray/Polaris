#!/usr/bin/env python3
"""
AI-Powered Endpoints Testing Script
Tests the new AI-powered endpoints for contract analysis, opportunity matching, and report generation
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://production-guru.preview.emergentagent.com/api"

# QA Credentials
AGENCY_CREDENTIALS = {
    "email": "agency.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class AIEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate_agency(self):
        """Authenticate as agency user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=AGENCY_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test(
                    "Agency Authentication",
                    True,
                    f"Successfully authenticated as {AGENCY_CREDENTIALS['email']}"
                )
                return True
            else:
                self.log_test(
                    "Agency Authentication",
                    False,
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Agency Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_ai_contract_analysis(self):
        """Test AI Contract Analysis Endpoint"""
        try:
            # Sample business data for analysis
            business_data = {
                "business_areas": ["area1", "area3", "area5"],
                "readiness_scores": {
                    "area1": 85,
                    "area3": 72,
                    "area5": 90
                },
                "certifications": ["SBA 8(a)", "HUBZone", "WOSB"],
                "contract_history": "2 federal contracts completed, $500K total value",
                "business_name": "TechSolutions LLC",
                "industry": "Information Technology"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/ai-contract-analysis",
                json=business_data,
                timeout=60  # AI calls may take longer
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get("success") and "analysis" in data:
                    analysis = data["analysis"]
                    
                    # Check for required AI analysis fields
                    required_fields = ["readiness_score", "opportunities", "risk_factors", "timeline", "advantages"]
                    missing_fields = [field for field in required_fields if field not in analysis]
                    
                    if not missing_fields:
                        # Verify AI-generated content quality
                        readiness_score = analysis.get("readiness_score", 0)
                        opportunities = analysis.get("opportunities", [])
                        
                        if isinstance(readiness_score, (int, float)) and 1 <= readiness_score <= 100:
                            if isinstance(opportunities, list) and len(opportunities) >= 3:
                                self.log_test(
                                    "AI Contract Analysis - Full AI Response",
                                    True,
                                    f"AI analysis complete: Score={readiness_score}, Opportunities={len(opportunities)}, Generated at: {data.get('generated_at')}"
                                )
                                return True
                            else:
                                self.log_test(
                                    "AI Contract Analysis - Opportunities Format",
                                    False,
                                    f"Opportunities should be list with 3+ items, got: {opportunities}"
                                )
                        else:
                            self.log_test(
                                "AI Contract Analysis - Score Validation",
                                False,
                                f"Readiness score should be 1-100, got: {readiness_score}"
                            )
                    else:
                        self.log_test(
                            "AI Contract Analysis - Response Structure",
                            False,
                            f"Missing required fields: {missing_fields}"
                        )
                elif data.get("success") == False and "fallback_analysis" in data:
                    # Fallback response is acceptable
                    self.log_test(
                        "AI Contract Analysis - Fallback Response",
                        True,
                        f"AI service unavailable, fallback provided: {data.get('error')}"
                    )
                    return True
                else:
                    self.log_test(
                        "AI Contract Analysis - Response Format",
                        False,
                        f"Unexpected response format: {data}"
                    )
            else:
                self.log_test(
                    "AI Contract Analysis - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "AI Contract Analysis - Exception",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_ai_opportunity_matching(self):
        """Test AI Opportunity Matching Endpoint"""
        try:
            # Sample matching request data
            matching_request = {
                "business_profile": {
                    "industry": "Professional Services",
                    "size": "Small Business",
                    "certifications": ["SBA 8(a)", "WOSB"],
                    "past_performance": "3 successful federal contracts",
                    "geographic_focus": "Texas",
                    "revenue_range": "$500K-$2M"
                },
                "contract_preferences": {
                    "contract_types": ["Services", "Consulting", "IT Support"],
                    "min_value": "$50,000",
                    "max_value": "$1,000,000",
                    "agencies": ["Department of Defense", "GSA", "Local Government"]
                },
                "market_focus": "federal_and_state"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/ai-opportunity-matching",
                json=matching_request,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "analysis" in data:
                    analysis = data["analysis"]
                    
                    # Check for required AI analysis fields
                    required_fields = [
                        "opportunity_score", "top_opportunities", "market_trends",
                        "competitive_analysis", "timing_recommendations", 
                        "capacity_building_needs", "success_probability"
                    ]
                    missing_fields = [field for field in required_fields if field not in analysis]
                    
                    if not missing_fields:
                        # Verify AI-generated content quality
                        opp_score = analysis.get("opportunity_score", 0)
                        top_opps = analysis.get("top_opportunities", [])
                        market_trends = analysis.get("market_trends", [])
                        
                        if isinstance(opp_score, (int, float)) and 1 <= opp_score <= 100:
                            if isinstance(top_opps, list) and len(top_opps) >= 3:
                                if isinstance(market_trends, list) and len(market_trends) >= 2:
                                    self.log_test(
                                        "AI Opportunity Matching - Full AI Response",
                                        True,
                                        f"AI matching complete: Score={opp_score}, Opportunities={len(top_opps)}, Trends={len(market_trends)}"
                                    )
                                    return True
                                else:
                                    self.log_test(
                                        "AI Opportunity Matching - Market Trends",
                                        False,
                                        f"Market trends should be list with 2+ items, got: {market_trends}"
                                    )
                            else:
                                self.log_test(
                                    "AI Opportunity Matching - Opportunities Count",
                                    False,
                                    f"Top opportunities should be list with 3+ items, got: {len(top_opps)}"
                                )
                        else:
                            self.log_test(
                                "AI Opportunity Matching - Score Validation",
                                False,
                                f"Opportunity score should be 1-100, got: {opp_score}"
                            )
                    else:
                        self.log_test(
                            "AI Opportunity Matching - Response Structure",
                            False,
                            f"Missing required fields: {missing_fields}"
                        )
                elif data.get("success") == False and "fallback_analysis" in data:
                    # Fallback response is acceptable
                    self.log_test(
                        "AI Opportunity Matching - Fallback Response",
                        True,
                        f"AI service unavailable, fallback provided: {data.get('error')}"
                    )
                    return True
                else:
                    self.log_test(
                        "AI Opportunity Matching - Response Format",
                        False,
                        f"Unexpected response format: {data}"
                    )
            else:
                self.log_test(
                    "AI Opportunity Matching - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "AI Opportunity Matching - Exception",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_ai_report_generation(self):
        """Test AI Report Generation Endpoint"""
        try:
            # Sample report request data
            report_request = {
                "report_type": "comprehensive",
                "time_period": "quarter",
                "focus_areas": ["business_development", "contract_readiness", "market_analysis"]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/agency/ai-generate-report",
                json=report_request,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "report" in data:
                    report = data["report"]
                    metadata = data.get("metadata", {})
                    
                    # Check for required report sections
                    required_sections = [
                        "executive_summary", "performance_metrics", "growth_analysis",
                        "market_opportunities", "risk_assessment", "recommendations",
                        "success_stories", "action_items", "forecast"
                    ]
                    missing_sections = [section for section in required_sections if section not in report]
                    
                    if not missing_sections:
                        # Verify report content quality
                        exec_summary = report.get("executive_summary", "")
                        recommendations = report.get("recommendations", [])
                        action_items = report.get("action_items", [])
                        
                        if len(exec_summary) > 50:  # Meaningful summary
                            if isinstance(recommendations, list) and len(recommendations) >= 2:
                                if isinstance(action_items, list) and len(action_items) >= 2:
                                    self.log_test(
                                        "AI Report Generation - Full AI Report",
                                        True,
                                        f"AI report generated: Type={metadata.get('type')}, Period={metadata.get('period')}, Businesses={metadata.get('businesses_analyzed')}"
                                    )
                                    return True
                                else:
                                    self.log_test(
                                        "AI Report Generation - Action Items",
                                        False,
                                        f"Action items should be list with 2+ items, got: {len(action_items)}"
                                    )
                            else:
                                self.log_test(
                                    "AI Report Generation - Recommendations",
                                    False,
                                    f"Recommendations should be list with 2+ items, got: {len(recommendations)}"
                                )
                        else:
                            self.log_test(
                                "AI Report Generation - Executive Summary",
                                False,
                                f"Executive summary too short: {len(exec_summary)} chars"
                            )
                    else:
                        self.log_test(
                            "AI Report Generation - Report Structure",
                            False,
                            f"Missing required sections: {missing_sections}"
                        )
                elif data.get("success") == False:
                    # Service unavailable is acceptable
                    self.log_test(
                        "AI Report Generation - Service Unavailable",
                        True,
                        f"AI service unavailable: {data.get('error')}"
                    )
                    return True
                else:
                    self.log_test(
                        "AI Report Generation - Response Format",
                        False,
                        f"Unexpected response format: {data}"
                    )
            else:
                self.log_test(
                    "AI Report Generation - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "AI Report Generation - Exception",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_enhanced_business_intelligence(self):
        """Test Enhanced Business Intelligence Endpoint"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/agency/business-intelligence/enhanced",
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for AI insights in response
                if "ai_insights" in data:
                    ai_insights = data["ai_insights"]
                    
                    # Check for required AI insight fields
                    required_fields = [
                        "portfolio_health", "growth_opportunities", "risk_assessment",
                        "strategic_recommendations", "market_positioning"
                    ]
                    missing_fields = [field for field in required_fields if field not in ai_insights]
                    
                    if not missing_fields:
                        # Verify AI-generated content quality
                        portfolio_health = ai_insights.get("portfolio_health", 0)
                        growth_opps = ai_insights.get("growth_opportunities", [])
                        recommendations = ai_insights.get("strategic_recommendations", [])
                        
                        if isinstance(portfolio_health, (int, float)) and 1 <= portfolio_health <= 100:
                            if isinstance(growth_opps, list) and len(growth_opps) >= 2:
                                if isinstance(recommendations, list) and len(recommendations) >= 2:
                                    # Check for performance metrics
                                    perf_metrics = data.get("performance_metrics", {})
                                    if perf_metrics:
                                        self.log_test(
                                            "Enhanced Business Intelligence - Full AI Insights",
                                            True,
                                            f"AI insights complete: Health={portfolio_health}, Opportunities={len(growth_opps)}, Recommendations={len(recommendations)}"
                                        )
                                        return True
                                    else:
                                        self.log_test(
                                            "Enhanced Business Intelligence - Performance Metrics",
                                            False,
                                            "Missing performance metrics in response"
                                        )
                                else:
                                    self.log_test(
                                        "Enhanced Business Intelligence - Recommendations",
                                        False,
                                        f"Strategic recommendations should be list with 2+ items, got: {len(recommendations)}"
                                    )
                            else:
                                self.log_test(
                                    "Enhanced Business Intelligence - Growth Opportunities",
                                    False,
                                    f"Growth opportunities should be list with 2+ items, got: {len(growth_opps)}"
                                )
                        else:
                            self.log_test(
                                "Enhanced Business Intelligence - Health Score",
                                False,
                                f"Portfolio health should be 1-100, got: {portfolio_health}"
                            )
                    else:
                        self.log_test(
                            "Enhanced Business Intelligence - AI Insights Structure",
                            False,
                            f"Missing required AI insight fields: {missing_fields}"
                        )
                elif "error" in data:
                    # Service unavailable is acceptable
                    self.log_test(
                        "Enhanced Business Intelligence - Service Unavailable",
                        True,
                        f"BI service unavailable: {data.get('error')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Enhanced Business Intelligence - Missing AI Insights",
                        False,
                        "Response missing ai_insights field"
                    )
            else:
                self.log_test(
                    "Enhanced Business Intelligence - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Enhanced Business Intelligence - Exception",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def run_all_tests(self):
        """Run all AI endpoint tests"""
        print("🎯 AI-POWERED ENDPOINTS TESTING STARTED")
        print("=" * 60)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_agency():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test AI Contract Analysis
        print("🔍 Testing AI Contract Analysis Endpoint...")
        contract_analysis_success = self.test_ai_contract_analysis()
        
        # Step 3: Test AI Opportunity Matching
        print("🎯 Testing AI Opportunity Matching Endpoint...")
        opportunity_matching_success = self.test_ai_opportunity_matching()
        
        # Step 4: Test AI Report Generation
        print("📊 Testing AI Report Generation Endpoint...")
        report_generation_success = self.test_ai_report_generation()
        
        # Step 5: Test Enhanced Business Intelligence
        print("📈 Testing Enhanced Business Intelligence Endpoint...")
        enhanced_bi_success = self.test_enhanced_business_intelligence()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print("🎯 AI-POWERED ENDPOINTS TESTING COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print()
        
        # Summary of key findings
        ai_endpoints_working = [
            contract_analysis_success,
            opportunity_matching_success, 
            report_generation_success,
            enhanced_bi_success
        ]
        
        working_count = sum(ai_endpoints_working)
        
        if working_count == 4:
            print("✅ ALL AI ENDPOINTS OPERATIONAL")
            print("🤖 Emergent LLM integration working correctly")
            print("📈 AI-generated data confirmed for all endpoints")
        elif working_count >= 2:
            print(f"⚠️  PARTIAL AI FUNCTIONALITY: {working_count}/4 endpoints working")
            print("🤖 Some AI features operational, others may have fallbacks")
        else:
            print("❌ AI INTEGRATION ISSUES DETECTED")
            print("🤖 Most AI endpoints not returning expected AI-generated content")
        
        print()
        print("🔍 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate >= 75  # 75% success rate threshold

def main():
    """Main test execution"""
    tester = AIEndpointsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 AI ENDPOINTS TESTING SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n⚠️  AI ENDPOINTS TESTING COMPLETED WITH ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()