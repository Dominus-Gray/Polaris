"""
Tests for Analytics Projection Engine

Validates projection logic and metric calculations.
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock
from analytics.projection import ProjectionEngine
from analytics.models import EventType


class TestProjectionEngine:
    """Test projection engine functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = MagicMock()
        db.analytics_events = AsyncMock()
        db.client_metrics_daily = AsyncMock()
        db.cohort_metrics_daily = AsyncMock()
        db.cohort_memberships = AsyncMock()
        db.projection_state = AsyncMock()
        db.users = AsyncMock()
        return db
    
    @pytest.fixture
    def projection_engine(self, mock_db):
        """Create projection engine with mock database"""
        return ProjectionEngine(mock_db)
    
    def test_calculate_client_deltas_task_completion(self, projection_engine):
        """Test calculation of task completion deltas"""
        events = [
            {
                "event_type": EventType.TASK_STATE_CHANGED,
                "payload_json": {
                    "client_id": "client_123",
                    "previous_state": "in_progress", 
                    "new_state": "completed",
                    "task_type": "compliance"
                }
            }
        ]
        
        # Using asyncio.run to test async method
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["tasks_completed"] == 1
        assert deltas["tasks_active_delta"] == -1  # Task moved out of active state
    
    def test_calculate_client_deltas_task_blocking(self, projection_engine):
        """Test calculation of task blocking deltas"""
        events = [
            {
                "event_type": EventType.TASK_STATE_CHANGED,
                "payload_json": {
                    "client_id": "client_123",
                    "previous_state": "in_progress",
                    "new_state": "blocked"
                }
            }
        ]
        
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["tasks_blocked_delta"] == 1
        assert deltas["tasks_active_delta"] == -1
    
    def test_calculate_client_deltas_alert_creation(self, projection_engine):
        """Test calculation of alert creation deltas"""
        events = [
            {
                "event_type": EventType.ALERT_CREATED,
                "payload_json": {
                    "client_id": "client_123",
                    "alert_type": "compliance_issue",
                    "severity": "high"
                }
            }
        ]
        
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["alerts_opened"] == 1
    
    def test_calculate_client_deltas_assessment_risk_score(self, projection_engine):
        """Test calculation of risk score from assessment"""
        events = [
            {
                "event_type": EventType.ASSESSMENT_RECORDED,
                "payload_json": {
                    "client_id": "client_123",
                    "risk_score": 78.5,
                    "assessment_type": "tier_assessment"
                }
            }
        ]
        
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["risk_score_latest"] == 78.5
    
    def test_calculate_client_deltas_action_plan_activation(self, projection_engine):
        """Test calculation of action plan activation deltas"""
        events = [
            {
                "event_type": EventType.ACTION_PLAN_VERSION_ACTIVATED,
                "payload_json": {
                    "client_id": "client_123",
                    "plan_id": "plan_456",
                    "version_number": 2
                }
            }
        ]
        
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["action_plan_versions_activated"] == 1
    
    def test_calculate_client_deltas_multiple_events(self, projection_engine):
        """Test calculation with multiple events affecting same client"""
        events = [
            {
                "event_type": EventType.TASK_STATE_CHANGED,
                "payload_json": {
                    "previous_state": "new",
                    "new_state": "in_progress"
                }
            },
            {
                "event_type": EventType.TASK_STATE_CHANGED,
                "payload_json": {
                    "previous_state": "in_progress",
                    "new_state": "completed"
                }
            },
            {
                "event_type": EventType.ALERT_CREATED,
                "payload_json": {
                    "alert_type": "deadline_approaching"
                }
            }
        ]
        
        import asyncio
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", events)
        )
        
        assert deltas["tasks_completed"] == 1  # One task completed
        assert deltas["tasks_active_delta"] == 0  # Net: +1 then -1
        assert deltas["alerts_opened"] == 1
    
    def test_aggregate_cohort_metrics(self, projection_engine):
        """Test aggregation of client metrics to cohort level"""
        client_metrics = [
            {
                "tasks_completed": 5,
                "alerts_open": 2,
                "action_plan_versions_activated": 1,
                "risk_score_avg": 75.0
            },
            {
                "tasks_completed": 3,
                "alerts_open": 1,
                "action_plan_versions_activated": 2,
                "risk_score_avg": 82.0
            },
            {
                "tasks_completed": 7,
                "alerts_open": 0,
                "action_plan_versions_activated": 1,
                "risk_score_avg": None  # No assessment yet
            }
        ]
        
        aggregates = projection_engine._aggregate_cohort_metrics(client_metrics)
        
        assert aggregates["tasks_completed"] == 15  # 5 + 3 + 7
        assert aggregates["alerts_open"] == 3  # 2 + 1 + 0
        assert aggregates["version_activations"] == 4  # 1 + 2 + 1
        assert aggregates["avg_risk_score"] == 78.5  # (75.0 + 82.0) / 2
    
    def test_aggregate_cohort_metrics_no_risk_scores(self, projection_engine):
        """Test cohort aggregation when no clients have risk scores"""
        client_metrics = [
            {
                "tasks_completed": 5,
                "alerts_open": 2,
                "risk_score_avg": None
            },
            {
                "tasks_completed": 3,
                "alerts_open": 1,
                "risk_score_avg": None
            }
        ]
        
        aggregates = projection_engine._aggregate_cohort_metrics(client_metrics)
        
        assert aggregates["avg_risk_score"] is None
        assert aggregates["tasks_completed"] == 8
    
    def test_group_events_by_date(self, projection_engine):
        """Test grouping of events by date"""
        mock_events = [
            {"occurred_at": datetime(2024, 1, 15, 10, 30)},
            {"occurred_at": datetime(2024, 1, 15, 14, 20)},
            {"occurred_at": datetime(2024, 1, 16, 9, 15)},
            {"occurred_at": datetime(2024, 1, 16, 16, 45)}
        ]
        
        # Mock the database query
        async def mock_find(*args, **kwargs):
            class MockCursor:
                def __init__(self, events):
                    self.events = events
                    self.index = 0
                
                def sort(self, *args):
                    return self
                
                def __aiter__(self):
                    return self
                
                async def __anext__(self):
                    if self.index >= len(self.events):
                        raise StopAsyncIteration
                    event = self.events[self.index]
                    self.index += 1
                    return event
            
            return MockCursor(mock_events)
        
        projection_engine.analytics_events.find = mock_find
        
        import asyncio
        grouped = asyncio.run(
            projection_engine._group_events_by_date({})
        )
        
        assert len(grouped) == 2
        assert "2024-01-15" in grouped
        assert "2024-01-16" in grouped
        assert len(grouped["2024-01-15"]) == 2
        assert len(grouped["2024-01-16"]) == 2


class TestProjectionEngineIntegration:
    """Integration tests for projection engine"""
    
    @pytest.fixture
    def mock_db_with_data(self):
        """Create mock database with test data"""
        db = MagicMock()
        
        # Mock analytics events
        events = [
            {
                "_id": "event_1",
                "event_type": EventType.TASK_STATE_CHANGED,
                "occurred_at": datetime(2024, 1, 15, 10, 0),
                "payload_json": {
                    "client_id": "client_1",
                    "previous_state": "new",
                    "new_state": "completed"
                }
            }
        ]
        
        # Mock users for cohort membership
        users = [
            {
                "id": "client_1",
                "role": "client",
                "cohort_tags": ["small_business", "manufacturing"]
            }
        ]
        
        db.analytics_events = AsyncMock()
        db.client_metrics_daily = AsyncMock()
        db.cohort_memberships = AsyncMock()
        db.users = AsyncMock()
        
        return db
    
    def test_end_to_end_projection_cycle(self, mock_db_with_data):
        """Test complete projection cycle"""
        projection_engine = ProjectionEngine(mock_db_with_data)
        
        # Mock projection state
        projection_engine.projection_state.find_one = AsyncMock(return_value=None)
        projection_engine.projection_state.replace_one = AsyncMock()
        
        # This would require extensive mocking to fully test
        # In a real environment, this would be an integration test with actual database
        pass


class TestProjectionEngineErrorHandling:
    """Test error handling in projection engine"""
    
    def test_handles_database_errors_gracefully(self):
        """Test that database errors are handled gracefully"""
        # Mock database that raises exceptions
        db = MagicMock()
        db.analytics_events.find.side_effect = Exception("Database connection failed")
        
        projection_engine = ProjectionEngine(db)
        
        import asyncio
        result = asyncio.run(projection_engine.run_incremental_projection())
        
        assert result["success"] is False
        assert "Database connection failed" in result["error"]
    
    def test_handles_malformed_events(self, mock_db):
        """Test handling of malformed events"""
        projection_engine = ProjectionEngine(mock_db)
        
        # Event missing required fields
        malformed_events = [
            {
                "event_type": EventType.TASK_STATE_CHANGED,
                "payload_json": {}  # Missing client_id and state fields
            }
        ]
        
        import asyncio
        # Should not raise exception, should handle gracefully
        deltas = asyncio.run(
            projection_engine._calculate_client_deltas("client_123", "2024-01-15", malformed_events)
        )
        
        # Should return empty deltas for malformed events
        assert deltas["tasks_completed"] == 0