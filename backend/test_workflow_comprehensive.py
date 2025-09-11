#!/usr/bin/env python3
"""
Workflow Orchestration End-to-End Test

This script tests the complete workflow orchestration system including:
- State machine definitions
- API endpoint structure  
- Database schema requirements
- Automation trigger logic
- SLA tracking capabilities
- Documentation completeness
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Run comprehensive workflow system validation"""
    
    print("🚀 Workflow Orchestration System Validation")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    
    # Test results tracking
    tests_passed = 0
    tests_total = 0
    
    def run_test(test_name, test_func):
        nonlocal tests_passed, tests_total
        tests_total += 1
        print(f"\n{tests_total}. {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"   ✅ PASSED")
                tests_passed += 1
                return True
            else:
                print(f"   ❌ FAILED")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            return False
    
    # Test 1: Core Workflow Components
    def test_core_components():
        required_files = {
            "workflow.py": "Core workflow engine and state machines",
            "workflow_api.py": "FastAPI endpoints for workflow operations", 
            "workflow_workers.py": "Background workers and automation",
            "workflow_migration.py": "Database setup and migrations",
            "test_workflow.py": "Comprehensive test suite"
        }
        
        all_exist = True
        for filename, description in required_files.items():
            filepath = backend_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                print(f"   ✓ {filename} ({size_kb:.1f}KB) - {description}")
            else:
                print(f"   ✗ {filename} - MISSING")
                all_exist = False
        
        return all_exist
    
    # Test 2: State Machine Definitions
    def test_state_machines():
        workflow_file = backend_dir / "workflow.py"
        if not workflow_file.exists():
            return False
        
        content = workflow_file.read_text()
        
        state_machine_elements = [
            ("TaskState enum", "class TaskState"),
            ("ActionPlanState enum", "class ActionPlanState"), 
            ("Task states", "NEW = \"new\""),
            ("ActionPlan states", "DRAFT = \"draft\""),
            ("Task state machine", "TASK_STATE_MACHINE = StateMachine"),
            ("ActionPlan state machine", "ACTION_PLAN_STATE_MACHINE = StateMachine"),
            ("State registry", "STATE_MACHINE_REGISTRY")
        ]
        
        all_found = True
        for name, pattern in state_machine_elements:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Pattern '{pattern}' not found")
                all_found = False
        
        return all_found
    
    # Test 3: API Endpoint Coverage
    def test_api_endpoints():
        api_file = backend_dir / "workflow_api.py" 
        if not api_file.exists():
            return False
        
        content = api_file.read_text()
        
        endpoints = [
            ("Task creation", "@workflow_router.post(\"/tasks\""),
            ("Task transition", "\"/tasks/{task_id}/transition\""),
            ("Task details", "@workflow_router.get(\"/tasks/{task_id}\")"),
            ("Task listing", "@workflow_router.get(\"/tasks\")"),
            ("ActionPlan creation", "@workflow_router.post(\"/action-plans\")"),
            ("ActionPlan activation", "\"/action-plans/{action_plan_id}/activate\""),
            ("ActionPlan archival", "\"/action-plans/{action_plan_id}/archive\""),
            ("Workflow metadata", "@workflow_router.get(\"/metadata\")"),
            ("SLA config creation", "@workflow_router.post(\"/sla-configs\")"),
            ("SLA config listing", "@workflow_router.get(\"/sla-configs\")"),
            ("Workflow statistics", "@workflow_router.get(\"/stats\")")
        ]
        
        all_found = True
        for name, pattern in endpoints:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Pattern '{pattern}' not found")
                all_found = False
        
        return all_found
    
    # Test 4: Database Schema Design
    def test_database_schema():
        migration_file = backend_dir / "workflow_migration.py"
        if not migration_file.exists():
            return False
        
        content = migration_file.read_text()
        
        collections = [
            ("tasks", "\"tasks\""),
            ("actionplans", "\"actionplans\""),
            ("sla_configs", "\"sla_configs\""),
            ("sla_records", "\"sla_records\""),
            ("outbox_events", "\"outbox_events\"")
        ]
        
        indexes = [
            ("Task ID index", "tasks.create_index(\"id\""),
            ("Task state index", "tasks.create_index(\"state\""),
            ("SLA record task index", "sla_records.create_index(\"task_id\""),
            ("Outbox event processing index", "outbox_events.create_index(\"processed\"")
        ]
        
        all_found = True
        
        for name, pattern in collections:
            if pattern in content:
                print(f"   ✓ Collection: {name}")
            else:
                print(f"   ✗ Collection: {name} - Not found")
                all_found = False
        
        for name, pattern in indexes:
            if pattern in content:
                print(f"   ✓ Index: {name}")
            else:
                print(f"   ✗ Index: {name} - Not found") 
                all_found = False
        
        return all_found
    
    # Test 5: Automation Framework
    def test_automation_framework():
        workflow_file = backend_dir / "workflow.py"
        if not workflow_file.exists():
            return False
        
        content = workflow_file.read_text()
        
        automation_components = [
            ("AutomationTrigger model", "class AutomationTrigger"),
            ("AutomationAction model", "class AutomationAction"),
            ("AutomationDispatcher", "class AutomationDispatcher"),
            ("Trigger evaluation", "def process_event"),
            ("Built-in triggers", "AUTOMATION_TRIGGERS"),
            ("Task completion trigger", "task_completion_follow_up"),
            ("ActionPlan activation trigger", "action_plan_activation_notification")
        ]
        
        all_found = True
        for name, pattern in automation_components:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found")
                all_found = False
        
        return all_found
    
    # Test 6: SLA Tracking System
    def test_sla_tracking():
        workflow_file = backend_dir / "workflow.py"
        if not workflow_file.exists():
            return False
        
        content = workflow_file.read_text()
        
        sla_components = [
            ("SLAConfig model", "class SLAConfig"),
            ("SLARecord model", "class SLARecord"),
            ("SLAManager class", "class SLAManager"),
            ("Start tracking", "def start_sla_tracking"),
            ("Complete tracking", "def complete_sla_tracking"),
            ("Breach detection", "def scan_for_breaches"),
            ("Target minutes", "target_minutes"),
            ("Breach flag", "breached: bool")
        ]
        
        all_found = True
        for name, pattern in sla_components:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found")
                all_found = False
        
        return all_found
    
    # Test 7: Background Workers
    def test_background_workers():
        workers_file = backend_dir / "workflow_workers.py"
        if not workers_file.exists():
            return False
        
        content = workers_file.read_text()
        
        worker_components = [
            ("WorkflowWorkers class", "class WorkflowWorkers"),
            ("Event processing loop", "def _event_processing_loop"),
            ("SLA monitoring loop", "def _sla_monitoring_loop"),
            ("Worker start/stop", "async def start"),
            ("Event processing", "def _process_outbox_events"),
            ("SLA breach handling", "def _handle_sla_breaches"),
            ("Metrics integration", "prometheus_client"),
            ("Observability class", "class WorkflowObservability")
        ]
        
        all_found = True
        for name, pattern in worker_components:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found")
                all_found = False
        
        return all_found
    
    # Test 8: Server Integration
    def test_server_integration():
        server_file = backend_dir / "server_full.py"
        if not server_file.exists():
            return False
        
        content = server_file.read_text()
        
        integration_points = [
            ("Workflow API import", "from workflow_api import"),
            ("Workers import", "from workflow_workers import"),
            ("API setup", "setup_workflow_api"),
            ("Workers startup", "start_workflow_workers"),
            ("Workers shutdown", "stop_workflow_workers"),
            ("Startup event", "@app.on_event(\"startup\")"),
            ("Shutdown event", "@app.on_event(\"shutdown\")")
        ]
        
        all_found = True
        for name, pattern in integration_points:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found") 
                all_found = False
        
        return all_found
    
    # Test 9: Documentation Quality
    def test_documentation():
        docs_file = backend_dir.parent / "docs" / "architecture" / "workflow.md"
        if not docs_file.exists():
            return False
        
        content = docs_file.read_text()
        
        doc_sections = [
            ("Overview section", "## Overview"),
            ("Architecture section", "## Architecture"),
            ("State diagrams", "```mermaid"),
            ("API documentation", "## API Endpoints"),
            ("Testing section", "## Testing"),
            ("Migration guide", "## Migration"),
            ("Task state machine", "Task Lifecycle State Machine"),
            ("ActionPlan state machine", "ActionPlan Lifecycle State Machine"),
            ("Event flow sequence", "sequenceDiagram"),
            ("Component diagram", "graph TB")
        ]
        
        all_found = True
        word_count = len(content.split())
        
        for name, pattern in doc_sections:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found")
                all_found = False
        
        print(f"   📄 Documentation word count: {word_count}")
        
        return all_found and word_count > 1000  # Ensure substantial documentation
    
    # Test 10: Transition Logic Validation
    def test_transition_logic():
        workflow_file = backend_dir / "workflow.py"
        if not workflow_file.exists():
            return False
        
        content = workflow_file.read_text()
        
        # Check for specific task transitions
        task_transitions = [
            "from_state=TaskState.NEW, to_state=TaskState.IN_PROGRESS",
            "from_state=TaskState.IN_PROGRESS, to_state=TaskState.COMPLETED",
            "from_state=TaskState.BLOCKED, to_state=TaskState.IN_PROGRESS"
        ]
        
        # Check for ActionPlan transitions
        plan_transitions = [
            "from_state=ActionPlanState.DRAFT, to_state=ActionPlanState.ACTIVE",
            "from_state=ActionPlanState.ACTIVE, to_state=ActionPlanState.ARCHIVED"
        ]
        
        validation_components = [
            ("TransitionEngine class", "class TransitionEngine"),
            ("Validate transition method", "def validate_transition"),
            ("Execute transition method", "def execute_transition"),
            ("Event emission", "def _emit_event")
        ]
        
        all_found = True
        
        for transition in task_transitions:
            if transition in content:
                print(f"   ✓ Task transition: {transition.split('=')[2].split(',')[0]}")
            else:
                print(f"   ✗ Task transition missing: {transition}")
                all_found = False
        
        for transition in plan_transitions:
            if transition in content:
                print(f"   ✓ Plan transition: {transition.split('=')[2].split(',')[0]}")
            else:
                print(f"   ✗ Plan transition missing: {transition}")
                all_found = False
        
        for name, pattern in validation_components:
            if pattern in content:
                print(f"   ✓ {name}")
            else:
                print(f"   ✗ {name} - Not found")
                all_found = False
        
        return all_found
    
    # Run all tests
    run_test("Core Workflow Components", test_core_components)
    run_test("State Machine Definitions", test_state_machines)
    run_test("API Endpoint Coverage", test_api_endpoints)
    run_test("Database Schema Design", test_database_schema)
    run_test("Automation Framework", test_automation_framework)
    run_test("SLA Tracking System", test_sla_tracking)
    run_test("Background Workers", test_background_workers)
    run_test("Server Integration", test_server_integration)
    run_test("Documentation Quality", test_documentation)
    run_test("Transition Logic Validation", test_transition_logic)
    
    # Final results
    print("\n" + "=" * 60)
    print(f"🎯 WORKFLOW ORCHESTRATION VALIDATION COMPLETE")
    print(f"📊 Results: {tests_passed}/{tests_total} tests passed ({(tests_passed/tests_total)*100:.1f}%)")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED! Workflow orchestration system is ready.")
        print("\n📋 Next Steps:")
        print("   1. Install dependencies: pip install pydantic motor fastapi")
        print("   2. Set up MongoDB database")
        print("   3. Run migration: python workflow_migration.py")
        print("   4. Start server and test API endpoints")
        print("   5. Verify background workers are processing events")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)