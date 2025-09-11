#!/usr/bin/env python3
"""
Demo script showing Action Plan Versioning & Recommendation Engine workflow
Simulates the key user journeys and API interactions
"""

import json
from datetime import datetime
from test_action_plans_standalone import (
    RuleBasedBaselineRecommendationProvider, 
    compute_action_plan_diff,
    ActionPlanStatus
)

def demo_recommendation_generation():
    """Demo: Generate recommendations for different risk profiles"""
    print("🎭 DEMO: Recommendation Generation for Different Risk Profiles")
    print("=" * 70)
    
    provider = RuleBasedBaselineRecommendationProvider()
    
    # Demo clients with different risk profiles
    clients = [
        {
            "id": "startup_tech",
            "name": "TechStart Inc.",
            "context": {
                "client_id": "startup_tech",
                "risk_score": 85,
                "readiness_percent": 15,
                "assessment_gaps": ["financial_management", "compliance", "operations"],
                "industry": "technology"
            }
        },
        {
            "id": "growing_retail",
            "name": "Growing Retail Co.",
            "context": {
                "client_id": "growing_retail", 
                "risk_score": 55,
                "readiness_percent": 60,
                "assessment_gaps": ["operations", "documentation"],
                "industry": "retail"
            }
        },
        {
            "id": "established_services",
            "name": "Established Services LLC",
            "context": {
                "client_id": "established_services",
                "risk_score": 25,
                "readiness_percent": 85,
                "assessment_gaps": [],
                "industry": "professional_services"
            }
        }
    ]
    
    for client in clients:
        print(f"\n📋 Client: {client['name']} (ID: {client['id']})")
        print(f"   Risk Score: {client['context']['risk_score']}")
        print(f"   Readiness: {client['context']['readiness_percent']}%")
        print(f"   Industry: {client['context']['industry']}")
        
        proposal = provider.generate_plan(client['context'])
        
        print(f"   📝 Generated Plan:")
        print(f"      Goals: {len(proposal['goals'])}")
        for i, goal in enumerate(proposal['goals'], 1):
            print(f"        {i}. {goal['title']}")
        
        print(f"      Interventions: {len(proposal['interventions'])}")
        for i, intervention in enumerate(proposal['interventions'], 1):
            print(f"        {i}. {intervention['title']} ({intervention['type']})")
        
        print(f"      Risk Level: {proposal['metadata']['source_tags'][1]}")

def demo_version_workflow():
    """Demo: Action plan version workflow and diff computation"""
    print("\n\n🔄 DEMO: Action Plan Version Workflow")
    print("=" * 70)
    
    # Simulate plan evolution over time
    plans = [
        {
            "version": 1,
            "status": "suggested",
            "goals": [
                {"id": "goal_1", "title": "Establish accounting system", "description": "Basic bookkeeping"},
                {"id": "goal_2", "title": "Obtain business license", "description": "Legal compliance"}
            ],
            "interventions": [
                {"id": "int_1", "goal_id": "goal_1", "title": "QuickBooks setup", "type": "tool_adoption"}
            ]
        },
        {
            "version": 2, 
            "status": "active",
            "goals": [
                {"id": "goal_1", "title": "Implement comprehensive financial management", "description": "Advanced financial tracking and reporting"},
                {"id": "goal_3", "title": "Enhance operational efficiency", "description": "Process optimization"}
            ],
            "interventions": [
                {"id": "int_1", "goal_id": "goal_1", "title": "QuickBooks setup", "type": "tool_adoption"},
                {"id": "int_2", "goal_id": "goal_3", "title": "Process documentation", "type": "process_improvement"}
            ]
        },
        {
            "version": 3,
            "status": "suggested",
            "goals": [
                {"id": "goal_1", "title": "Implement comprehensive financial management", "description": "Advanced financial tracking and reporting"},
                {"id": "goal_3", "title": "Enhance operational efficiency", "description": "Process optimization"},
                {"id": "goal_4", "title": "Prepare for compliance audit", "description": "Audit readiness"}
            ],
            "interventions": [
                {"id": "int_1", "goal_id": "goal_1", "title": "QuickBooks setup", "type": "tool_adoption"},
                {"id": "int_2", "goal_id": "goal_3", "title": "Process documentation", "type": "process_improvement"},
                {"id": "int_3", "goal_id": "goal_4", "title": "Compliance review", "type": "audit_preparation"}
            ]
        }
    ]
    
    print("📈 Plan Evolution Timeline:")
    print(f"   Client ID: client_demo_001")
    
    for plan in plans:
        print(f"\n   Version {plan['version']} ({plan['status'].upper()})")
        print(f"     Goals: {len(plan['goals'])}")
        for goal in plan['goals']:
            print(f"       • {goal['title']}")
        print(f"     Interventions: {len(plan['interventions'])}")
        
    # Show version diffs
    print(f"\n🔍 Version Differences:")
    
    for i in range(len(plans) - 1):
        from_plan = plans[i]
        to_plan = plans[i + 1]
        
        print(f"\n   v{from_plan['version']} → v{to_plan['version']}:")
        
        diff = compute_action_plan_diff(from_plan, to_plan)
        
        if diff['added']['goals']:
            print(f"     ➕ Added Goals:")
            for goal in diff['added']['goals']:
                print(f"        • {goal['title']}")
        
        if diff['removed']['goals']:
            print(f"     ➖ Removed Goals:")
            for goal in diff['removed']['goals']:
                print(f"        • {goal['title']}")
        
        if diff['changed']['goals']:
            print(f"     🔄 Changed Goals:")
            for change in diff['changed']['goals']:
                print(f"        • {change['id']}: {', '.join(change['fields_changed'])}")
        
        if diff['added']['interventions']:
            print(f"     ➕ Added Interventions:")
            for intervention in diff['added']['interventions']:
                print(f"        • {intervention['title']} ({intervention['type']})")

def demo_api_workflow():
    """Demo: API endpoint workflow simulation"""
    print("\n\n🌐 DEMO: API Workflow Simulation")
    print("=" * 70)
    
    # Simulate API calls and responses
    print("📡 API Call Sequence:")
    
    # 1. Generate recommendation
    print(f"\n1. 📝 POST /clients/client_123/action-plans/recommend")
    print(f"   Request: (authenticated as navigator)")
    print(f"   Response: 201 Created")
    response_1 = {
        "id": "plan_abc123",
        "client_id": "client_123", 
        "version": 1,
        "status": "suggested",
        "goals": [
            {
                "id": "goal_1",
                "title": "Improve financial management",
                "description": "Auto-generated goal: Improve financial management",
                "timeframe": "3 months"
            }
        ],
        "interventions": [
            {
                "id": "intervention_1",
                "goal_id": "goal_1",
                "title": "Implementation plan for Improve financial management",
                "type": "process_improvement"
            }
        ],
        "generated_by_type": "rule_engine",
        "created_at": "2024-01-01T00:00:00Z"
    }
    print(f"   Plan ID: {response_1['id']}")
    print(f"   Status: {response_1['status']}")
    print(f"   Goals: {len(response_1['goals'])}")
    
    # 2. Activate plan
    print(f"\n2. 🚀 POST /action-plans/{response_1['id']}/activate")
    print(f"   Request: (authenticated as agency)")
    print(f"   Response: 200 OK")
    print(f"   Actions performed:")
    print(f"     • Previous active plan archived")
    print(f"     • Plan status changed to 'active'")
    print(f"     • Plan series updated")
    print(f"     • Diff computed and stored")
    print(f"     • Domain events emitted")
    
    # 3. List client plans
    print(f"\n3. 📋 GET /clients/client_123/action-plans")
    print(f"   Request: (authenticated as client)")
    print(f"   Response: 200 OK")
    print(f"   Found plans:")
    print(f"     • v1: active (current)")
    print(f"     • v0: archived (superseded)")
    
    # 4. Get plan diffs
    print(f"\n4. 🔍 GET /action-plans/{response_1['id']}/diffs")
    print(f"   Request: (authenticated as navigator)")
    print(f"   Response: 200 OK")
    print(f"   Diffs found: 1")
    print(f"     • v0 → v1: 2 goals added, 1 intervention added")

def demo_permission_matrix():
    """Demo: Permission and role-based access control"""
    print("\n\n🔐 DEMO: Permission Matrix & RBAC")
    print("=" * 70)
    
    roles = ["Navigator", "Agency", "Client", "Provider"]
    permissions = [
        ("Generate Recommendation", ["Navigator", "Agency"]),
        ("View Plan Diffs", ["Navigator", "Agency", "Client"]),
        ("Activate Plans", ["Navigator", "Agency", "Client"]),
        ("Create Manual Plans", ["Navigator", "Agency", "Client"]),
        ("View All Client Plans", ["Navigator", "Agency"]),
        ("View Own Plans Only", ["Client"])
    ]
    
    print("🎭 Role-Permission Matrix:")
    print(f"{'Permission':<25} {'Navigator':<10} {'Agency':<10} {'Client':<10} {'Provider':<10}")
    print("-" * 70)
    
    for permission, allowed_roles in permissions:
        row = f"{permission:<25}"
        for role in roles:
            symbol = "✅" if role in allowed_roles else "❌"
            row += f" {symbol:<9}"
        print(row)

def main():
    """Run all demos"""
    print("🎬 Action Plan Versioning & Recommendation Engine Demo")
    print("🎯 Demonstrating key workflows and capabilities")
    print("=" * 70)
    
    demo_recommendation_generation()
    demo_version_workflow()
    demo_api_workflow()
    demo_permission_matrix()
    
    print("\n" + "=" * 70)
    print("🎉 Demo Complete!")
    print("📚 See docs/architecture/action_plan_versioning.md for full documentation")
    print("🛠️  Use action_plan_cli.py for administrative operations")
    print("🧪 Run test_action_plans_standalone.py for validation")

if __name__ == "__main__":
    main()