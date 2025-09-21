#!/usr/bin/env python3
"""
RP CRM-lite Backend Seed & Smoke Test
Testing RP requirements seeding and leads workflow as requested in review.
"""

import requests
import json
import sys
from datetime import datetime

# Use production URL from frontend/.env
BASE_URL = "https://production-guru.preview.emergentagent.com/api"

# QA Credentials
AGENCY_CREDENTIALS = {
    "email": "agency.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

# RP Requirements Templates to seed
RP_REQUIREMENTS_BULK = [
    {
        "rp_type": "lenders",
        "required_fields": [
            "contact_email", "readiness_score", "annual_revenue", "average_monthly_revenue",
            "ar_ap_summary", "merchant_processing_history", "years_in_business",
            "beneficial_owners", "licenses_status", "insurance_status", "good_standing_attestation"
        ]
    },
    {
        "rp_type": "bonding_agents", 
        "required_fields": [
            "contact_email", "readiness_score", "years_in_business", "licenses_status",
            "insurance_status", "bonding_history_summary", "prior_contract_values",
            "financial_summary_bands", "good_standing_attestation"
        ]
    },
    {
        "rp_type": "investors",
        "required_fields": [
            "contact_email", "readiness_score", "annual_revenue", "growth_plan_summary",
            "pitch_deck_url", "cap_table_summary", "beneficial_owners", "prior_funding_history",
            "financial_summary_bands"
        ]
    },
    {
        "rp_type": "business_development_orgs",
        "required_fields": [
            "contact_email", "readiness_score", "capabilities_statement", "growth_plan_summary",
            "past_performance_summary", "certifications_list"
        ]
    },
    {
        "rp_type": "procurement_offices",
        "required_fields": [
            "contact_email", "readiness_score", "sam_registration_status", "cage_code",
            "naics_codes", "past_performance_summary", "quality_certifications", "capabilities_statement"
        ]
    },
    {
        "rp_type": "prime_contractors",
        "required_fields": [
            "contact_email", "readiness_score", "capabilities_statement", "past_performance_summary",
            "quality_certifications", "safety_program_attestation"
        ]
    },
    {
        "rp_type": "accelerators",
        "required_fields": [
            "contact_email", "readiness_score", "growth_plan_summary", "pitch_deck_url",
            "value_proposition_summary", "mentor_fit_preferences"
        ]
    },
    {
        "rp_type": "banks",
        "required_fields": [
            "contact_email", "readiness_score", "annual_revenue", "employee_count",
            "beneficial_owners", "banking_readiness", "licenses_status", "insurance_status",
            "financial_summary_bands", "good_standing_attestation"
        ]
    }
]

def authenticate(credentials):
    """Authenticate and return JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=credentials, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_rp_crm_workflow():
    """Test complete RP CRM-lite workflow"""
    print("🎯 RP CRM-lite Backend Seed & Smoke Test")
    print("=" * 60)
    
    results = []
    
    # Step 1: Authenticate as agency
    print("\n1️⃣ Authenticating as agency.qa...")
    agency_token = authenticate(AGENCY_CREDENTIALS)
    if not agency_token:
        results.append("❌ Agency authentication failed")
        return results
    
    agency_headers = {"Authorization": f"Bearer {agency_token}"}
    results.append("✅ Agency authentication successful")
    
    # Step 2: Seed RP requirements via bulk endpoint
    print("\n2️⃣ Seeding RP requirements via bulk endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/v2/rp/requirements/bulk",
            json=RP_REQUIREMENTS_BULK,
            headers=agency_headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            updated_count = data.get("updated", 0)
            if updated_count >= 8:
                results.append(f"✅ Bulk seed successful: {updated_count} RP types updated")
                print(f"   📊 Updated {updated_count} RP requirement templates")
            else:
                results.append(f"⚠️ Bulk seed partial: only {updated_count}/8 updated")
        else:
            results.append(f"❌ Bulk seed failed: {response.status_code} - {response.text[:100]}")
            print(f"   Error: {response.status_code} - {response.text}")
    except Exception as e:
        results.append(f"❌ Bulk seed error: {str(e)}")
        print(f"   Exception: {e}")
    
    # Step 3: Verify requirements as agency
    print("\n3️⃣ Verifying requirements visibility as agency...")
    try:
        response = requests.get(
            f"{BASE_URL}/v2/rp/requirements/all",
            headers=agency_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 8:
                results.append(f"✅ Agency can see {len(data)} RP requirements")
                print(f"   📋 Agency sees {len(data)} requirement templates")
            else:
                results.append(f"⚠️ Agency sees {len(data) if isinstance(data, list) else 0} requirements (expected ≥8)")
        else:
            results.append(f"❌ Agency requirements fetch failed: {response.status_code}")
    except Exception as e:
        results.append(f"❌ Agency requirements error: {str(e)}")
    
    # Step 4: Authenticate as client
    print("\n4️⃣ Authenticating as client.qa...")
    client_token = authenticate(CLIENT_CREDENTIALS)
    if not client_token:
        results.append("❌ Client authentication failed")
        return results
    
    client_headers = {"Authorization": f"Bearer {client_token}"}
    results.append("✅ Client authentication successful")
    
    # Step 5: Verify requirements as client
    print("\n5️⃣ Verifying requirements visibility as client...")
    try:
        response = requests.get(
            f"{BASE_URL}/v2/rp/requirements/all",
            headers=client_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 8:
                results.append(f"✅ Client can see {len(data)} RP requirements")
                print(f"   📋 Client sees {len(data)} requirement templates")
            else:
                results.append(f"⚠️ Client sees {len(data) if isinstance(data, list) else 0} requirements (expected ≥8)")
        else:
            results.append(f"❌ Client requirements fetch failed: {response.status_code}")
    except Exception as e:
        results.append(f"❌ Client requirements error: {str(e)}")
    
    # Step 6: Test package preview for lenders
    print("\n6️⃣ Testing package preview for lenders...")
    try:
        response = requests.get(
            f"{BASE_URL}/v2/rp/package-preview?rp_type=lenders",
            headers=client_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "package" in data and "missing" in data:
                missing_count = len(data.get("missing", []))
                results.append(f"✅ Package preview working: {missing_count} missing items identified")
                print(f"   📦 Package preview shows {missing_count} missing prerequisites")
                if missing_count > 0:
                    print(f"   🔍 Sample missing: {data['missing'][:3]}")
            else:
                results.append("⚠️ Package preview missing required fields (package/missing)")
        else:
            results.append(f"❌ Package preview failed: {response.status_code}")
    except Exception as e:
        results.append(f"❌ Package preview error: {str(e)}")
    
    # Step 7: Create lead as client
    print("\n7️⃣ Creating lead as client...")
    try:
        response = requests.post(
            f"{BASE_URL}/v2/rp/leads",
            json={"rp_type": "lenders"},
            headers=client_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            lead_id = data.get("lead_id")
            status = data.get("status")
            if lead_id and status:
                results.append(f"✅ Lead created: {lead_id[:8]}... status={status}")
                print(f"   🎯 Lead ID: {lead_id}")
                print(f"   📊 Status: {status}")
            else:
                results.append("⚠️ Lead created but missing lead_id or status")
        else:
            results.append(f"❌ Lead creation failed: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        results.append(f"❌ Lead creation error: {str(e)}")
    
    # Step 8: Verify lead visibility as agency
    print("\n8️⃣ Verifying lead visibility as agency...")
    try:
        response = requests.get(
            f"{BASE_URL}/v2/rp/leads",
            headers=agency_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                lead_count = len(data)
                results.append(f"✅ Agency can see {lead_count} leads")
                print(f"   📋 Agency sees {lead_count} total leads")
                
                # Look for recent lead
                recent_leads = [lead for lead in data if lead.get("status") == "new"]
                if recent_leads:
                    print(f"   🆕 Found {len(recent_leads)} new leads")
            else:
                results.append("⚠️ Agency leads response not a list")
        else:
            results.append(f"❌ Agency leads fetch failed: {response.status_code}")
    except Exception as e:
        results.append(f"❌ Agency leads error: {str(e)}")
    
    return results

def main():
    """Run RP CRM-lite backend test"""
    print(f"🚀 Starting RP CRM-lite Backend Test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = test_rp_crm_workflow()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.startswith("✅"))
    failed = sum(1 for r in results if r.startswith("❌"))
    warnings = sum(1 for r in results if r.startswith("⚠️"))
    
    for result in results:
        print(f"  {result}")
    
    print(f"\n📈 FINAL SCORE: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("🎉 RP CRM-lite Backend: FULLY OPERATIONAL")
        return 0
    else:
        print("🚨 RP CRM-lite Backend: ISSUES DETECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())