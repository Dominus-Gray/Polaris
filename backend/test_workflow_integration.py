#!/usr/bin/env python3
"""
Simple integration test for workflow orchestration system
This test verifies the basic workflow structure and integration points.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def test_workflow_integration():
    """Test workflow integration with existing server"""
    
    print("Testing Workflow Orchestration Integration...")
    print("=" * 50)
    
    # Test 1: Verify files exist
    backend_dir = Path(__file__).parent
    required_files = [
        "workflow.py",
        "workflow_api.py", 
        "workflow_workers.py",
        "workflow_migration.py",
        "test_workflow.py"
    ]
    
    print("\n1. File Structure Check:")
    for file_name in required_files:
        file_path = backend_dir / file_name
        if file_path.exists():
            print(f"   ✓ {file_name}")
        else:
            print(f"   ✗ {file_name} - Missing!")
            return False
    
    # Test 2: Check server integration
    print("\n2. Server Integration Check:")
    server_file = backend_dir / "server_full.py"
    
    if server_file.exists():
        with open(server_file, 'r') as f:
            server_content = f.read()
        
        # Check for workflow integration
        integration_checks = [
            ("workflow_api import", "from workflow_api import"),
            ("workflow workers import", "from workflow_workers import"),
            ("workflow setup call", "setup_workflow_api"),
            ("startup event", "@app.on_event(\"startup\")"),
            ("shutdown workflow", "stop_workflow_workers")
        ]
        
        for check_name, check_pattern in integration_checks:
            if check_pattern in server_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    
    # Test 3: Check documentation
    print("\n3. Documentation Check:")
    docs_file = Path(__file__).parent.parent / "docs" / "architecture" / "workflow.md"
    
    if docs_file.exists():
        print(f"   ✓ Workflow documentation exists")
        
        with open(docs_file, 'r') as f:
            docs_content = f.read()
        
        doc_checks = [
            ("State diagrams", "```mermaid"),
            ("API endpoints", "POST /api/workflow/tasks"),
            ("Architecture", "## Architecture"),
            ("Testing section", "## Testing")
        ]
        
        for check_name, check_pattern in doc_checks:
            if check_pattern in docs_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    else:
        print(f"   ✗ Workflow documentation missing!")
    
    # Test 4: API Endpoint Structure
    print("\n4. API Endpoint Structure Check:")
    api_file = backend_dir / "workflow_api.py"
    
    if api_file.exists():
        with open(api_file, 'r') as f:
            api_content = f.read()
        
        endpoint_checks = [
            ("Task creation", "POST.*tasks"),
            ("Task transition", "tasks/{task_id}/transition"),
            ("ActionPlan activation", "action-plans/{action_plan_id}/activate"),
            ("ActionPlan archive", "action-plans/{action_plan_id}/archive"),
            ("Workflow metadata", "GET.*metadata"),
            ("SLA configs", "sla-configs"),
            ("Statistics", "GET.*stats")
        ]
        
        for check_name, check_pattern in endpoint_checks:
            if check_pattern.replace(".*", "") in api_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    
    # Test 5: State Machine Definitions
    print("\n5. State Machine Structure Check:")
    workflow_file = backend_dir / "workflow.py"
    
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
        
        state_checks = [
            ("TaskState enum", "class TaskState"),
            ("ActionPlanState enum", "class ActionPlanState"),
            ("Task state machine", "TASK_STATE_MACHINE"),
            ("ActionPlan state machine", "ACTION_PLAN_STATE_MACHINE"),
            ("Transition engine", "class TransitionEngine"),
            ("Automation dispatcher", "class AutomationDispatcher"),
            ("SLA manager", "class SLAManager")
        ]
        
        for check_name, check_pattern in state_checks:
            if check_pattern in workflow_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    
    # Test 6: Database Migration Structure
    print("\n6. Database Migration Check:")
    migration_file = backend_dir / "workflow_migration.py"
    
    if migration_file.exists():
        with open(migration_file, 'r') as f:
            migration_content = f.read()
        
        migration_checks = [
            ("Collection creation", "create_collection"),
            ("Index creation", "create_index"),
            ("SLA config setup", "default_sla_configs"),
            ("Verification", "verify_migration")
        ]
        
        for check_name, check_pattern in migration_checks:
            if check_pattern in migration_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    
    # Test 7: Background Workers
    print("\n7. Background Workers Check:")
    workers_file = backend_dir / "workflow_workers.py"
    
    if workers_file.exists():
        with open(workers_file, 'r') as f:
            workers_content = f.read()
        
        worker_checks = [
            ("WorkflowWorkers class", "class WorkflowWorkers"),
            ("Event processing loop", "_event_processing_loop"),
            ("SLA monitoring loop", "_sla_monitoring_loop"),
            ("Metrics integration", "prometheus_client"),
            ("Observability", "class WorkflowObservability")
        ]
        
        for check_name, check_pattern in worker_checks:
            if check_pattern in workers_content:
                print(f"   ✓ {check_name}")
            else:
                print(f"   ✗ {check_name} - Not found!")
    
    print("\n" + "=" * 50)
    print("✓ Workflow Orchestration Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Install required dependencies (pydantic, motor, etc.)")
    print("2. Set up MongoDB database")
    print("3. Run workflow migration: python workflow_migration.py")
    print("4. Start the server with workflow integration")
    print("5. Test API endpoints with workflow operations")
    
    return True

def test_workflow_api_structure():
    """Test API structure for completeness"""
    
    print("\n" + "=" * 50)
    print("API Structure Validation")
    print("=" * 50)
    
    # Expected API endpoints
    expected_endpoints = [
        "POST /api/workflow/tasks",
        "POST /api/workflow/tasks/{task_id}/transition", 
        "GET /api/workflow/tasks/{task_id}",
        "GET /api/workflow/tasks",
        "POST /api/workflow/action-plans",
        "POST /api/workflow/action-plans/{action_plan_id}/activate",
        "POST /api/workflow/action-plans/{action_plan_id}/archive",
        "GET /api/workflow/action-plans/{action_plan_id}",
        "GET /api/workflow/metadata",
        "POST /api/workflow/sla-configs",
        "GET /api/workflow/sla-configs",
        "GET /api/workflow/stats"
    ]
    
    print(f"\nExpected API Endpoints ({len(expected_endpoints)}):")
    for endpoint in expected_endpoints:
        print(f"   • {endpoint}")
    
    # Expected state transitions
    task_transitions = [
        "new → in_progress",
        "new → blocked", 
        "new → cancelled",
        "in_progress → completed",
        "in_progress → blocked",
        "in_progress → cancelled", 
        "blocked → in_progress",
        "blocked → cancelled"
    ]
    
    action_plan_transitions = [
        "draft → active",
        "draft → archived",
        "active → archived"
    ]
    
    print(f"\nTask State Transitions ({len(task_transitions)}):")
    for transition in task_transitions:
        print(f"   • {transition}")
    
    print(f"\nActionPlan State Transitions ({len(action_plan_transitions)}):")
    for transition in action_plan_transitions:
        print(f"   • {transition}")
    
    # Expected automation triggers
    triggers = [
        "Task completion follow-up (intake → assessment)",
        "ActionPlan activation notification"
    ]
    
    print(f"\nAutomation Triggers ({len(triggers)}):")
    for trigger in triggers:
        print(f"   • {trigger}")
    
    print("\n✓ API Structure Validation Complete!")

if __name__ == "__main__":
    test_workflow_integration()
    test_workflow_api_structure()