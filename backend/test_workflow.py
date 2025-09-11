"""
Comprehensive Tests for Workflow Orchestration System

This module contains unit and integration tests for the workflow orchestration layer
including state machines, transitions, automation, and SLA tracking.
"""

import asyncio
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path

# Add backend directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

from workflow import (
    TransitionEngine,
    AutomationDispatcher, 
    SLAManager,
    Task,
    ActionPlan,
    TaskState,
    ActionPlanState,
    OutboxEvent,
    TASK_STATE_MACHINE,
    ACTION_PLAN_STATE_MACHINE
)

from workflow_workers import WorkflowWorkers, WorkflowObservability

class TestStateTransitions:
    """Test state machine transitions"""
    
    def test_task_state_machine_definition(self):
        """Test task state machine is properly defined"""
        assert TASK_STATE_MACHINE.entity_type == "Task"
        assert TaskState.NEW in TASK_STATE_MACHINE.states
        assert TASK_STATE_MACHINE.initial_state == TaskState.NEW
        
        # Check specific transitions
        transitions = TASK_STATE_MACHINE.transitions
        from_new = [t for t in transitions if t.from_state == TaskState.NEW]
        assert len(from_new) == 3  # to in_progress, blocked, cancelled
        
        from_in_progress = [t for t in transitions if t.from_state == TaskState.IN_PROGRESS]
        assert len(from_in_progress) == 3  # to completed, blocked, cancelled
    
    def test_action_plan_state_machine_definition(self):
        """Test action plan state machine is properly defined"""
        assert ACTION_PLAN_STATE_MACHINE.entity_type == "ActionPlan"
        assert ActionPlanState.DRAFT in ACTION_PLAN_STATE_MACHINE.states
        assert ACTION_PLAN_STATE_MACHINE.initial_state == ActionPlanState.DRAFT
        
        # Check transitions
        transitions = ACTION_PLAN_STATE_MACHINE.transitions
        from_draft = [t for t in transitions if t.from_state == ActionPlanState.DRAFT]
        assert len(from_draft) == 2  # to active, archived


class TestTransitionEngine:
    """Test transition engine functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock database client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.polaris_db = mock_db
        return mock_client
    
    @pytest.fixture
    def transition_engine(self, mock_db_client):
        """Create transition engine with mock DB"""
        return TransitionEngine(mock_db_client)
    
    def test_validate_valid_transition(self, transition_engine):
        """Test validation of valid transitions"""
        result = transition_engine.validate_transition(
            entity_type="Task",
            current_state=TaskState.NEW,
            target_state=TaskState.IN_PROGRESS
        )
        assert result.allowed is True
        assert len(result.reasons) == 0
    
    def test_validate_invalid_transition(self, transition_engine):
        """Test validation of invalid transitions"""
        result = transition_engine.validate_transition(
            entity_type="Task", 
            current_state=TaskState.COMPLETED,
            target_state=TaskState.IN_PROGRESS
        )
        assert result.allowed is False
        assert len(result.reasons) > 0
    
    def test_validate_unknown_entity_type(self, transition_engine):
        """Test validation with unknown entity type"""
        result = transition_engine.validate_transition(
            entity_type="UnknownEntity",
            current_state="state1",
            target_state="state2"
        )
        assert result.allowed is False
        assert "Unknown entity type" in result.reasons[0]
    
    def test_validate_invalid_target_state(self, transition_engine):
        """Test validation with invalid target state"""
        result = transition_engine.validate_transition(
            entity_type="Task",
            current_state=TaskState.NEW,
            target_state="invalid_state"
        )
        assert result.allowed is False
        assert "Invalid target state" in result.reasons[0]


class TestAutomationTriggers:
    """Test automation trigger system"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock database client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.polaris_db = mock_db
        
        # Mock collection methods
        mock_db.tasks = Mock()
        mock_db.actionplans = Mock()
        mock_db.tasks.insert_one = AsyncMock()
        mock_db.tasks.update_one = AsyncMock()
        mock_db.actionplans.update_one = AsyncMock()
        
        return mock_client
    
    @pytest.fixture
    def automation_dispatcher(self, mock_db_client):
        """Create automation dispatcher with mock DB"""
        return AutomationDispatcher(mock_db_client)
    
    @pytest.mark.asyncio
    async def test_trigger_evaluation_match(self, automation_dispatcher):
        """Test trigger evaluation with matching event"""
        # Create a task completion event
        event = OutboxEvent(
            event_type="TaskStateChanged",
            aggregate_id="task123",
            aggregate_type="Task",
            event_data={
                "new_state": "completed",
                "task_type": "intake",
                "old_state": "in_progress"
            }
        )
        
        # Process the event
        await automation_dispatcher.process_event(event)
        
        # Verify task creation was called
        automation_dispatcher.db.tasks.insert_one.assert_called_once()
        
        # Check the created task data
        call_args = automation_dispatcher.db.tasks.insert_one.call_args[0][0]
        assert call_args["title"] == "Assessment Task"
        assert call_args["task_type"] == "assessment"
        assert call_args["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_trigger_evaluation_no_match(self, automation_dispatcher):
        """Test trigger evaluation with non-matching event"""
        # Create an event that won't match any triggers
        event = OutboxEvent(
            event_type="TaskStateChanged",
            aggregate_id="task123",
            aggregate_type="Task",
            event_data={
                "new_state": "in_progress",
                "task_type": "review",
                "old_state": "new"
            }
        )
        
        # Process the event
        await automation_dispatcher.process_event(event)
        
        # Verify no task creation was called
        automation_dispatcher.db.tasks.insert_one.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_action_plan_activation_trigger(self, automation_dispatcher):
        """Test action plan activation trigger"""
        # Create action plan activation event
        event = OutboxEvent(
            event_type="ActionPlanActivated",
            aggregate_id="plan123",
            aggregate_type="ActionPlan",
            event_data={"new_state": "active"}
        )
        
        # Process the event (should trigger alert)
        await automation_dispatcher.process_event(event)
        
        # The alert action just logs, so we can't easily verify it
        # In a real system, this would emit to a notification service


class TestSLAManager:
    """Test SLA tracking functionality"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock database client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.polaris_db = mock_db
        
        # Mock collections
        mock_db.sla_configs = Mock()
        mock_db.sla_records = Mock()
        mock_db.sla_configs.find_one = AsyncMock()
        mock_db.sla_records.insert_one = AsyncMock()
        mock_db.sla_records.find_one = AsyncMock()
        mock_db.sla_records.update_one = AsyncMock()
        mock_db.sla_records.aggregate = Mock()
        
        return mock_client
    
    @pytest.fixture
    def sla_manager(self, mock_db_client):
        """Create SLA manager with mock DB"""
        return SLAManager(mock_db_client)
    
    @pytest.mark.asyncio
    async def test_start_sla_tracking(self, sla_manager):
        """Test starting SLA tracking for a task"""
        # Mock SLA config found
        sla_manager.db.sla_configs.find_one.return_value = {
            "id": "config123",
            "target_minutes": 120,
            "service_area": "test"
        }
        
        await sla_manager.start_sla_tracking("task123", "test_type")
        
        # Verify SLA record was created
        sla_manager.db.sla_records.insert_one.assert_called_once()
        
        # Check the created record
        call_args = sla_manager.db.sla_records.insert_one.call_args[0][0]
        assert call_args["task_id"] == "task123"
        assert call_args["target_minutes"] == 120
        assert call_args["started_at"] is not None
    
    @pytest.mark.asyncio
    async def test_start_sla_tracking_no_config(self, sla_manager):
        """Test starting SLA tracking when no config exists"""
        # Mock no SLA config found
        sla_manager.db.sla_configs.find_one.return_value = None
        
        await sla_manager.start_sla_tracking("task123", "unknown_type")
        
        # Verify no SLA record was created
        sla_manager.db.sla_records.insert_one.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_complete_sla_tracking_within_sla(self, sla_manager):
        """Test completing SLA tracking within SLA"""
        # Mock SLA record found
        started_at = datetime.utcnow() - timedelta(minutes=30)
        sla_manager.db.sla_records.find_one.return_value = {
            "id": "record123",
            "task_id": "task123",
            "target_minutes": 60,
            "started_at": started_at
        }
        
        await sla_manager.complete_sla_tracking("task123")
        
        # Verify record was updated
        sla_manager.db.sla_records.update_one.assert_called_once()
        
        # Check the update data
        call_args = sla_manager.db.sla_records.update_one.call_args[0][1]
        update_data = call_args["$set"]
        assert update_data["breached"] is False
        assert update_data["actual_minutes"] <= 60
    
    @pytest.mark.asyncio
    async def test_complete_sla_tracking_breached(self, sla_manager):
        """Test completing SLA tracking with breach"""
        # Mock SLA record found with old start time
        started_at = datetime.utcnow() - timedelta(minutes=120)
        sla_manager.db.sla_records.find_one.return_value = {
            "id": "record123",
            "task_id": "task123", 
            "target_minutes": 60,
            "started_at": started_at
        }
        
        await sla_manager.complete_sla_tracking("task123")
        
        # Verify record was updated with breach
        call_args = sla_manager.db.sla_records.update_one.call_args[0][1]
        update_data = call_args["$set"]
        assert update_data["breached"] is True
        assert update_data["actual_minutes"] > 60


class TestWorkflowIntegration:
    """Integration tests for the complete workflow system"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock database client with comprehensive setup"""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.polaris_db = mock_db
        
        # Setup collection mocks
        collections = ["tasks", "actionplans", "sla_configs", "sla_records", "outbox_events"]
        for collection in collections:
            mock_collection = Mock()
            mock_collection.find_one = AsyncMock()
            mock_collection.insert_one = AsyncMock()
            mock_collection.update_one = AsyncMock()
            mock_collection.find = Mock()
            mock_collection.aggregate = Mock()
            mock_collection.count_documents = AsyncMock()
            setattr(mock_db, collection, mock_collection)
        
        return mock_client
    
    @pytest.mark.asyncio
    async def test_complete_task_workflow(self, mock_db_client):
        """Test complete workflow from task creation to completion"""
        # Create transition engine
        transition_engine = TransitionEngine(mock_db_client)
        
        # Mock task in database
        task_data = {
            "id": "task123",
            "state": TaskState.NEW,
            "task_type": "intake",
            "created_by": "user123"
        }
        mock_db_client.polaris_db.tasks.find_one.return_value = task_data
        
        # Test transition to in_progress
        success = await transition_engine.execute_transition(
            entity_type="Task",
            entity_id="task123",
            target_state=TaskState.IN_PROGRESS,
            actor_id="user123"
        )
        
        assert success is True
        
        # Verify task was updated
        mock_db_client.polaris_db.tasks.update_one.assert_called()
        
        # Verify event was emitted
        mock_db_client.polaris_db.outbox_events.insert_one.assert_called()
    
    @pytest.mark.asyncio
    async def test_action_plan_lifecycle(self, mock_db_client):
        """Test action plan lifecycle workflow"""
        transition_engine = TransitionEngine(mock_db_client)
        
        # Mock action plan in database
        action_plan_data = {
            "id": "plan123",
            "state": ActionPlanState.DRAFT,
            "created_by": "user123"
        }
        mock_db_client.polaris_db.actionplans.find_one.return_value = action_plan_data
        
        # Test activation
        success = await transition_engine.execute_transition(
            entity_type="ActionPlan",
            entity_id="plan123",
            target_state=ActionPlanState.ACTIVE,
            actor_id="user123"
        )
        
        assert success is True
        
        # Update mock for next transition
        action_plan_data["state"] = ActionPlanState.ACTIVE
        
        # Test archival
        success = await transition_engine.execute_transition(
            entity_type="ActionPlan",
            entity_id="plan123",
            target_state=ActionPlanState.ARCHIVED,
            actor_id="user123"
        )
        
        assert success is True


class TestWorkflowAPI:
    """Test workflow API endpoints"""
    
    def test_task_transition_request_model(self):
        """Test task transition request model validation"""
        from workflow_api import TaskTransitionRequest
        
        # Valid request
        request = TaskTransitionRequest(
            target_state=TaskState.IN_PROGRESS,
            context={"reason": "starting work"},
            notes="Beginning task work"
        )
        
        assert request.target_state == TaskState.IN_PROGRESS
        assert request.context["reason"] == "starting work"
        assert request.notes == "Beginning task work"
    
    def test_workflow_metadata_response(self):
        """Test workflow metadata response structure"""
        from workflow_api import WorkflowMetadataResponse
        
        response = WorkflowMetadataResponse(
            state_machines={},
            task_states=[state.value for state in TaskState],
            action_plan_states=[state.value for state in ActionPlanState],
            transition_rules={}
        )
        
        assert len(response.task_states) == 5  # NEW, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED
        assert len(response.action_plan_states) == 3  # DRAFT, ACTIVE, ARCHIVED


class TestWorkflowObservability:
    """Test workflow monitoring and observability"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock database client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.polaris_db = mock_db
        
        # Mock aggregation results
        mock_aggregate = Mock()
        mock_aggregate.to_list = AsyncMock()
        mock_db.tasks.aggregate = Mock(return_value=mock_aggregate)
        mock_db.actionplans.aggregate = Mock(return_value=mock_aggregate)
        mock_db.sla_records.count_documents = AsyncMock()
        mock_db.outbox_events.count_documents = AsyncMock()
        
        return mock_client
    
    @pytest.mark.asyncio
    async def test_workflow_stats_collection(self, mock_db_client):
        """Test workflow statistics collection"""
        observability = WorkflowObservability(mock_db_client)
        
        # Mock aggregation results
        mock_db_client.polaris_db.tasks.aggregate().to_list.return_value = [
            {"_id": "new", "count": 5},
            {"_id": "in_progress", "count": 3}
        ]
        mock_db_client.polaris_db.actionplans.aggregate().to_list.return_value = [
            {"_id": "draft", "count": 2},
            {"_id": "active", "count": 1}
        ]
        mock_db_client.polaris_db.sla_records.count_documents.side_effect = [10, 2]  # breaches, active
        mock_db_client.polaris_db.outbox_events.count_documents.return_value = 5
        
        stats = await observability.get_workflow_stats()
        
        assert "tasks_by_state" in stats
        assert "action_plans_by_state" in stats
        assert "sla_breaches" in stats
        assert "active_sla_records" in stats
        assert "unprocessed_events" in stats
        assert stats["sla_breaches"] == 10
        assert stats["unprocessed_events"] == 5


if __name__ == "__main__":
    # Run tests with pytest if available, otherwise run basic tests
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not available, running basic tests...")
        
        # Run basic tests
        test_transitions = TestStateTransitions()
        test_transitions.test_task_state_machine_definition()
        test_transitions.test_action_plan_state_machine_definition()
        
        print("✓ Basic state machine tests passed")
        
        # Test models can be created
        task = Task(title="Test Task", created_by="user123")
        assert task.state == TaskState.NEW
        
        action_plan = ActionPlan(title="Test Plan", created_by="user123")
        assert action_plan.state == ActionPlanState.DRAFT
        
        print("✓ Model creation tests passed")
        print("\nAll basic tests completed successfully!")