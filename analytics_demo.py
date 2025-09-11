#!/usr/bin/env python3
"""
Analytics & Cohort Projection Layer Demo

This script demonstrates the key functionality of the analytics system
without requiring external dependencies.
"""

from datetime import datetime, date
import json
import uuid


def demo_event_mapping():
    """Demonstrate event mapping functionality"""
    print("=== Analytics Event Mapping Demo ===")
    
    # Simulate a task state change event
    task_event = {
        "task_id": "task_123",
        "client_id": "client_456", 
        "user_id": "user_789",
        "previous_state": "new",
        "new_state": "in_progress",
        "task_type": "compliance_check",
        "timestamp": datetime.utcnow(),
        "correlation_id": "task_123_transition_001"
    }
    
    # Simulate analytics event creation
    analytics_event = {
        "id": str(uuid.uuid4()),
        "event_type": "TaskStateChanged",
        "entity_type": "task",
        "entity_id": task_event["task_id"],
        "actor_user_id": task_event["user_id"],
        "occurred_at": task_event["timestamp"],
        "correlation_id": task_event["correlation_id"],
        "payload_json": {
            "client_id": task_event["client_id"],
            "previous_state": task_event["previous_state"],
            "new_state": task_event["new_state"],
            "task_type": task_event["task_type"]
        },
        "source": "polaris",
        "ingested_at": datetime.utcnow()
    }
    
    print(f"Domain Event: {task_event['task_id']} changed from {task_event['previous_state']} to {task_event['new_state']}")
    print(f"Analytics Event: {analytics_event['event_type']} for entity {analytics_event['entity_id']}")
    print(f"Correlation ID: {analytics_event['correlation_id']}")
    print()


def demo_projection_calculation():
    """Demonstrate projection calculation logic"""
    print("=== Projection Calculation Demo ===")
    
    # Simulate events for a client on a day
    daily_events = [
        {"event_type": "TaskStateChanged", "payload": {"previous_state": "new", "new_state": "in_progress"}},
        {"event_type": "TaskStateChanged", "payload": {"previous_state": "in_progress", "new_state": "completed"}},
        {"event_type": "AlertCreated", "payload": {"alert_type": "compliance_issue", "severity": "medium"}},
        {"event_type": "AssessmentRecorded", "payload": {"risk_score": 78.5, "assessment_type": "tier_assessment"}},
        {"event_type": "ActionPlanVersionActivated", "payload": {"plan_id": "plan_123", "version_number": 2}}
    ]
    
    # Calculate deltas
    deltas = {
        "tasks_completed": 0,
        "tasks_active_delta": 0,
        "tasks_blocked_delta": 0,
        "alerts_opened": 0,
        "action_plan_versions_activated": 0,
        "risk_score_latest": None
    }
    
    for event in daily_events:
        event_type = event["event_type"]
        payload = event["payload"]
        
        if event_type == "TaskStateChanged":
            previous_state = payload.get("previous_state")
            new_state = payload.get("new_state")
            
            if new_state == "completed":
                deltas["tasks_completed"] += 1
            
            if new_state in ["in_progress", "pending"] and previous_state not in ["in_progress", "pending"]:
                deltas["tasks_active_delta"] += 1
            elif previous_state in ["in_progress", "pending"] and new_state not in ["in_progress", "pending"]:
                deltas["tasks_active_delta"] -= 1
                
        elif event_type == "AlertCreated":
            deltas["alerts_opened"] += 1
            
        elif event_type == "AssessmentRecorded":
            deltas["risk_score_latest"] = payload.get("risk_score")
            
        elif event_type == "ActionPlanVersionActivated":
            deltas["action_plan_versions_activated"] += 1
    
    print(f"Daily Deltas for Client:")
    print(f"  Tasks Completed: {deltas['tasks_completed']}")
    print(f"  Tasks Active Delta: {deltas['tasks_active_delta']}")
    print(f"  Alerts Opened: {deltas['alerts_opened']}")
    print(f"  Latest Risk Score: {deltas['risk_score_latest']}")
    print(f"  Action Plan Activations: {deltas['action_plan_versions_activated']}")
    print()


def demo_cohort_aggregation():
    """Demonstrate cohort aggregation"""
    print("=== Cohort Aggregation Demo ===")
    
    # Simulate client metrics for a cohort
    client_metrics = [
        {
            "client_id": "client_1",
            "tasks_completed": 5,
            "alerts_open": 2,
            "action_plan_versions_activated": 1,
            "risk_score_avg": 75.0
        },
        {
            "client_id": "client_2", 
            "tasks_completed": 3,
            "alerts_open": 1,
            "action_plan_versions_activated": 2,
            "risk_score_avg": 82.0
        },
        {
            "client_id": "client_3",
            "tasks_completed": 7,
            "alerts_open": 0,
            "action_plan_versions_activated": 1,
            "risk_score_avg": None  # No assessment yet
        }
    ]
    
    # Aggregate to cohort level
    total_tasks_completed = sum(m["tasks_completed"] for m in client_metrics)
    total_alerts_open = sum(m["alerts_open"] for m in client_metrics)
    total_version_activations = sum(m["action_plan_versions_activated"] for m in client_metrics)
    
    # Calculate average risk score
    risk_scores = [m["risk_score_avg"] for m in client_metrics if m["risk_score_avg"] is not None]
    avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else None
    
    cohort_metrics = {
        "cohort_tag": "small_business",
        "date": "2024-01-15",
        "client_count": len(client_metrics),
        "avg_risk_score": avg_risk_score,
        "tasks_completed": total_tasks_completed,
        "alerts_open": total_alerts_open,
        "version_activations": total_version_activations
    }
    
    print(f"Cohort '{cohort_metrics['cohort_tag']}' metrics for {cohort_metrics['date']}:")
    print(f"  Client Count: {cohort_metrics['client_count']}")
    print(f"  Average Risk Score: {cohort_metrics['avg_risk_score']:.1f}" if cohort_metrics['avg_risk_score'] else "  Average Risk Score: No data")
    print(f"  Total Tasks Completed: {cohort_metrics['tasks_completed']}")
    print(f"  Total Open Alerts: {cohort_metrics['alerts_open']}")
    print(f"  Total Version Activations: {cohort_metrics['version_activations']}")
    print()


def demo_rbac_logic():
    """Demonstrate RBAC logic"""
    print("=== RBAC Logic Demo ===")
    
    # Test scenarios
    scenarios = [
        {
            "user": {"id": "admin_1", "role": "SuperAdmin"},
            "target_client": "any_client",
            "expected": True,
            "reason": "SuperAdmin has full access"
        },
        {
            "user": {"id": "client_1", "role": "client"},
            "target_client": "client_1",
            "expected": True,
            "reason": "Client can view own analytics"
        },
        {
            "user": {"id": "client_1", "role": "client"},
            "target_client": "client_2",
            "expected": False,
            "reason": "Client cannot view other's analytics"
        },
        {
            "user": {"id": "orgadmin_1", "role": "OrgAdmin", "license_code": "org_123"},
            "target_client": "client_1",
            "target_client_org": "org_123",
            "expected": True,
            "reason": "OrgAdmin can view same org client"
        },
        {
            "user": {"id": "provider_1", "role": "ProviderStaff"},
            "target_client": "any_client",
            "expected": False,
            "reason": "ProviderStaff has no access by default"
        }
    ]
    
    for scenario in scenarios:
        user = scenario["user"]
        target_client = scenario["target_client"]
        expected = scenario["expected"]
        reason = scenario["reason"]
        
        # Simulate RBAC check
        result = check_client_analytics_permission_demo(user, target_client, scenario.get("target_client_org"))
        
        status = "✓" if result == expected else "✗"
        print(f"{status} {user['role']} accessing {target_client}: {result} ({reason})")
    
    print()


def check_client_analytics_permission_demo(user, target_client_id, target_client_org=None):
    """Demo version of RBAC check"""
    role = user.get("role")
    
    # SuperAdmin and Analyst can view all
    if role in ["SuperAdmin", "Analyst"]:
        return True
    
    # Client can only view their own
    if role == "client":
        return user["id"] == target_client_id
    
    # OrgAdmin can view same organization
    if role == "OrgAdmin":
        user_org = user.get("organization") or user.get("license_code")
        return user_org == target_client_org
    
    # CaseManager can view same organization
    if role == "CaseManager":
        user_org = user.get("organization") or user.get("license_code")
        return user_org == target_client_org
    
    # Default deny
    return False


def demo_api_response():
    """Demonstrate API response format"""
    print("=== API Response Demo ===")
    
    # Simulate API response
    api_response = {
        "metrics": [
            {
                "client_id": "client_123",
                "date": "2024-01-15",
                "risk_score_avg": 75.5,
                "tasks_completed": 3,
                "tasks_active": 2,
                "tasks_blocked": 1,
                "alerts_open": 0,
                "action_plan_versions_activated": 1,
                "updated_at": datetime.utcnow().isoformat()
            }
        ],
        "metadata": {
            "generation_timestamp": datetime.utcnow().isoformat(),
            "source_version": "abc123ef",
            "data_lag_seconds": 5.2
        }
    }
    
    print("GET /api/analytics/clients/client_123/daily?from_date=2024-01-15&to_date=2024-01-15")
    print(json.dumps(api_response, indent=2, default=str))
    print()


def main():
    """Run all demo functions"""
    print("🔍 Analytics & Cohort Projection Layer Demo")
    print("=" * 50)
    print()
    
    demo_event_mapping()
    demo_projection_calculation()
    demo_cohort_aggregation()
    demo_rbac_logic()
    demo_api_response()
    
    print("✅ Analytics system demonstration completed!")
    print()
    print("Key Features Demonstrated:")
    print("• Domain event mapping to analytics events")
    print("• Incremental projection calculations")
    print("• Cohort-level metric aggregation")
    print("• Role-based access control")
    print("• REST API response format")
    print()
    print("Ready for production deployment with MongoDB backend!")


if __name__ == "__main__":
    main()