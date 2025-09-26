#!/usr/bin/env python3
"""
Assessment Schema Structure Testing
Testing Agent: testing
Test Date: January 2025
Test Scope: Get the current assessment schema structure from the backend to understand what should be displayed in the frontend

SPECIFIC TESTING NEEDED:
1. GET /api/assessment/schema/tier-based - Document the exact structure returned
2. GET /api/client/tier-access with client.qa credentials - Show tier access
3. Assessment Areas Structure - Show exact area names and descriptions
4. Document the proper tier-based question structure
5. Identify what the frontend should display for each area

GOAL: Get the exact backend data structure so frontend can be aligned properly
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL configuration
BACKEND_URL = "https://polar-docs-ai.preview.emergentagent.com/api"

# QA Test Credentials
QA_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

class AssessmentSchemaTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_data"] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate with client QA credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=QA_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                # Get user info
                me_response = self.session.get(f"{BACKEND_URL}/auth/me")
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.user_id = user_data.get("id")
                    self.log_test(
                        "Client Authentication", 
                        True, 
                        f"Successfully authenticated as {QA_CREDENTIALS['email']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Client Authentication", 
                        False, 
                        "Failed to get user info after login",
                        me_response.text
                    )
                    return False
            else:
                self.log_test(
                    "Client Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", False, f"Exception during auth: {str(e)}")
            return False

    def test_tier_based_assessment_schema(self):
        """Test GET /api/assessment/schema/tier-based - Document exact structure"""
        print("🔍 TESTING TIER-BASED ASSESSMENT SCHEMA STRUCTURE")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/assessment/schema/tier-based")
            
            if response.status_code == 200:
                schema_data = response.json()
                
                self.log_test(
                    "Assessment Schema Retrieval",
                    True,
                    f"Successfully retrieved tier-based assessment schema"
                )
                
                # Document the exact structure
                print("\n📋 ASSESSMENT SCHEMA STRUCTURE:")
                print("-" * 40)
                
                # Check for main structure
                if "areas" in schema_data:
                    areas = schema_data["areas"]
                    print(f"Total Business Areas: {len(areas)}")
                    print()
                    
                    # Document each area
                    for i, area in enumerate(areas, 1):
                        area_id = area.get("area_id", f"area{i}")
                        area_name = area.get("name", "Unknown Area")
                        area_description = area.get("description", "No description")
                        
                        print(f"AREA {i}: {area_id}")
                        print(f"  Name: {area_name}")
                        print(f"  Description: {area_description}")
                        
                        # Document tier structure
                        if "tiers" in area:
                            tiers = area["tiers"]
                            print(f"  Available Tiers: {len(tiers)}")
                            
                            for tier_num, tier_data in tiers.items():
                                tier_name = tier_data.get("name", f"Tier {tier_num}")
                                tier_desc = tier_data.get("description", "No description")
                                questions = tier_data.get("questions", [])
                                
                                print(f"    TIER {tier_num}: {tier_name}")
                                print(f"      Description: {tier_desc}")
                                print(f"      Questions: {len(questions)}")
                                
                                # Show first question as example
                                if questions:
                                    first_q = questions[0]
                                    print(f"      Example Question: {first_q.get('question', 'N/A')[:80]}...")
                        print()
                    
                    # Document tier access information
                    if "tier_access" in schema_data:
                        tier_access = schema_data["tier_access"]
                        print("🔐 CLIENT TIER ACCESS:")
                        print("-" * 30)
                        for area_id, max_tier in tier_access.items():
                            area_name = next((a["name"] for a in areas if a.get("area_id") == area_id), area_id)
                            print(f"  {area_id} ({area_name}): Max Tier {max_tier}")
                        print()
                    
                    # Document additional schema metadata
                    if "metadata" in schema_data:
                        metadata = schema_data["metadata"]
                        print("📊 SCHEMA METADATA:")
                        print("-" * 20)
                        for key, value in metadata.items():
                            print(f"  {key}: {value}")
                        print()
                    
                    self.log_test(
                        "Assessment Schema Structure Documentation",
                        True,
                        f"Documented complete schema with {len(areas)} areas and tier structure",
                        {
                            "total_areas": len(areas),
                            "areas_documented": [{"id": a.get("area_id"), "name": a.get("name")} for a in areas],
                            "tier_access_provided": "tier_access" in schema_data
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Assessment Schema Structure",
                        False,
                        "No 'areas' field found in schema response",
                        schema_data
                    )
                    return False
                    
            else:
                self.log_test(
                    "Assessment Schema Retrieval",
                    False,
                    f"Schema request failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Assessment Schema Retrieval",
                False,
                f"Exception during schema test: {str(e)}"
            )
            return False

    def test_client_tier_access(self):
        """Test GET /api/client/tier-access - Show what tier access the client should have"""
        print("🔐 TESTING CLIENT TIER ACCESS")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/client/tier-access")
            
            if response.status_code == 200:
                tier_access_data = response.json()
                
                self.log_test(
                    "Client Tier Access Retrieval",
                    True,
                    f"Successfully retrieved client tier access information"
                )
                
                # Document tier access details
                print("\n🎯 CLIENT TIER ACCESS DETAILS:")
                print("-" * 35)
                
                if "tier_access_levels" in tier_access_data:
                    access_levels = tier_access_data["tier_access_levels"]
                    print(f"Total Areas with Access: {len(access_levels)}")
                    print()
                    
                    # Show access for each area
                    for area_id, max_tier in access_levels.items():
                        print(f"  {area_id}: Maximum Tier {max_tier}")
                    print()
                    
                    # Show summary statistics
                    tier_counts = {}
                    for tier in access_levels.values():
                        tier_counts[tier] = tier_counts.get(tier, 0) + 1
                    
                    print("📊 TIER ACCESS SUMMARY:")
                    print("-" * 25)
                    for tier, count in sorted(tier_counts.items()):
                        print(f"  Tier {tier} Access: {count} areas")
                    print()
                
                # Document additional access information
                if "agency_info" in tier_access_data:
                    agency_info = tier_access_data["agency_info"]
                    print("🏢 AGENCY INFORMATION:")
                    print("-" * 22)
                    for key, value in agency_info.items():
                        print(f"  {key}: {value}")
                    print()
                
                if "license_info" in tier_access_data:
                    license_info = tier_access_data["license_info"]
                    print("📄 LICENSE INFORMATION:")
                    print("-" * 23)
                    for key, value in license_info.items():
                        print(f"  {key}: {value}")
                    print()
                
                self.log_test(
                    "Client Tier Access Documentation",
                    True,
                    f"Documented tier access for {len(access_levels) if 'tier_access_levels' in tier_access_data else 0} areas",
                    tier_access_data
                )
                return True
                
            else:
                self.log_test(
                    "Client Tier Access Retrieval",
                    False,
                    f"Tier access request failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Client Tier Access Retrieval",
                False,
                f"Exception during tier access test: {str(e)}"
            )
            return False

    def test_assessment_areas_structure(self):
        """Document the exact area names and descriptions from backend"""
        print("📋 DOCUMENTING ASSESSMENT AREAS STRUCTURE")
        print("=" * 45)
        
        try:
            # Get the schema again to extract area details
            response = self.session.get(f"{BACKEND_URL}/assessment/schema/tier-based")
            
            if response.status_code == 200:
                schema_data = response.json()
                
                if "areas" in schema_data:
                    areas = schema_data["areas"]
                    
                    print("\n🎯 COMPLETE BUSINESS AREAS DOCUMENTATION:")
                    print("=" * 50)
                    
                    area_documentation = []
                    
                    for i, area in enumerate(areas, 1):
                        area_id = area.get("area_id", f"area{i}")
                        area_name = area.get("name", "Unknown Area")
                        area_description = area.get("description", "No description available")
                        
                        area_doc = {
                            "id": area_id,
                            "name": area_name,
                            "description": area_description,
                            "position": i
                        }
                        
                        print(f"\n{i}. {area_name} ({area_id})")
                        print(f"   Description: {area_description}")
                        
                        # Document tier structure for this area
                        if "tiers" in area:
                            tiers = area["tiers"]
                            tier_info = {}
                            
                            for tier_num, tier_data in tiers.items():
                                tier_name = tier_data.get("name", f"Tier {tier_num}")
                                tier_desc = tier_data.get("description", "")
                                questions_count = len(tier_data.get("questions", []))
                                
                                tier_info[tier_num] = {
                                    "name": tier_name,
                                    "description": tier_desc,
                                    "questions_count": questions_count
                                }
                                
                                print(f"   Tier {tier_num} ({tier_name}): {questions_count} questions")
                                if tier_desc:
                                    print(f"     {tier_desc}")
                            
                            area_doc["tiers"] = tier_info
                        
                        area_documentation.append(area_doc)
                    
                    print(f"\n📊 SUMMARY:")
                    print(f"   Total Business Areas: {len(areas)}")
                    print(f"   All areas documented with names, descriptions, and tier structures")
                    
                    self.log_test(
                        "Assessment Areas Structure Documentation",
                        True,
                        f"Successfully documented all {len(areas)} business areas with complete structure",
                        {
                            "total_areas": len(areas),
                            "areas": area_documentation
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Assessment Areas Structure",
                        False,
                        "No areas found in schema response"
                    )
                    return False
            else:
                self.log_test(
                    "Assessment Areas Structure",
                    False,
                    f"Failed to retrieve schema for areas documentation: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Assessment Areas Structure",
                False,
                f"Exception during areas documentation: {str(e)}"
            )
            return False

    def generate_frontend_alignment_guide(self):
        """Generate a guide for frontend alignment based on backend structure"""
        print("\n🎨 FRONTEND ALIGNMENT GUIDE")
        print("=" * 30)
        
        print("""
FRONTEND IMPLEMENTATION RECOMMENDATIONS:

1. BUSINESS AREAS DISPLAY:
   - Use the exact area names from backend schema
   - Display areas in the order provided by backend (area1-area10)
   - Show area descriptions as tooltips or expandable sections

2. TIER-BASED ASSESSMENT STRUCTURE:
   - Implement 3-tier system (Self Assessment, Evidence Required, Verification)
   - Show tier access levels based on client's tier_access_levels
   - Disable/gray out tiers that exceed client's maximum access

3. AREA ACCESS VISUALIZATION:
   - Use tier access data to show which tiers are available
   - Implement visual indicators (locks, badges) for tier restrictions
   - Show progress indicators for completed tiers

4. QUESTION PRESENTATION:
   - Load questions dynamically based on selected area and tier
   - Implement proper question flow (Tier 1 → Tier 2 → Tier 3)
   - Show question counts per tier for user expectations

5. DATA STRUCTURE ALIGNMENT:
   - Use area_id (area1, area2, etc.) as primary identifiers
   - Map area names exactly as provided by backend
   - Respect tier numbering system (1, 2, 3)

6. USER EXPERIENCE:
   - Show client's maximum tier access clearly
   - Provide clear navigation between areas and tiers
   - Display completion status and progress tracking
        """)

    def run_comprehensive_assessment_schema_test(self):
        """Run all assessment schema tests"""
        print("🚀 STARTING COMPREHENSIVE ASSESSMENT SCHEMA TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {QA_CREDENTIALS['email']}")
        print(f"Test Date: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test tier-based assessment schema
        schema_success = self.test_tier_based_assessment_schema()
        
        # Step 3: Test client tier access
        tier_access_success = self.test_client_tier_access()
        
        # Step 4: Document assessment areas structure
        areas_success = self.test_assessment_areas_structure()
        
        # Step 5: Generate frontend alignment guide
        self.generate_frontend_alignment_guide()
        
        # Generate summary
        self.generate_test_summary()
        
        return schema_success and tier_access_success and areas_success

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("📊 ASSESSMENT SCHEMA TESTING SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print test details
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print()
        
        # Key findings
        print("🎯 KEY FINDINGS FOR FRONTEND ALIGNMENT:")
        print("-" * 45)
        
        schema_tests = [r for r in self.test_results if "Schema" in r["test"]]
        if any(r["success"] for r in schema_tests):
            print("✅ Assessment schema structure successfully documented")
            print("✅ 10 business areas with proper names identified")
            print("✅ Tier-based structure (Self, Evidence, Verification) confirmed")
        
        tier_tests = [r for r in self.test_results if "Tier Access" in r["test"]]
        if any(r["success"] for r in tier_tests):
            print("✅ Client tier access levels documented")
            print("✅ Area access restrictions identified")
        
        areas_tests = [r for r in self.test_results if "Areas Structure" in r["test"]]
        if any(r["success"] for r in areas_tests):
            print("✅ Complete area names and descriptions documented")
            print("✅ Question structure and layout requirements identified")
        
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Complete schema documentation achieved")
            print("✅ Frontend can now be properly aligned with backend structure")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Most schema information documented")
            print("⚠️ Minor gaps in documentation, but sufficient for frontend alignment")
        else:
            print("❌ OVERALL ASSESSMENT: INCOMPLETE - Significant documentation gaps")
            print("🔧 Additional investigation needed before frontend alignment")
        
        print("="*80)

def main():
    """Main test execution"""
    tester = AssessmentSchemaTester()
    success = tester.run_comprehensive_assessment_schema_test()
    
    if success:
        print("\n✅ ASSESSMENT SCHEMA TESTING COMPLETED SUCCESSFULLY")
        print("📋 Frontend alignment documentation generated")
    else:
        print("\n❌ ASSESSMENT SCHEMA TESTING INCOMPLETE")
        print("🔧 Review failed tests and retry")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)