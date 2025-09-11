"""
Tests for Analytics Event Mapping

Validates that domain events are correctly mapped to analytics events.
"""

import pytest
from datetime import datetime
from analytics.mapping import EventMapper, extract_from_audit_log, create_synthetic_event
from analytics.models import EventType, AnalyticsEvent


class TestEventMapping:
    """Test event mapping functionality"""
    
    def test_map_task_state_changed(self):
        """Test task state change event mapping"""
        event_data = {
            "task_id": "task_123",
            "client_id": "client_456",
            "user_id": "user_789",
            "previous_state": "new",
            "new_state": "in_progress",
            "task_type": "compliance_check",
            "timestamp": datetime.utcnow(),
            "correlation_id": "corr_123"
        }
        
        analytics_event = EventMapper.map_task_state_changed(event_data)
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.TASK_STATE_CHANGED
        assert analytics_event.entity_type == "task"
        assert analytics_event.entity_id == "task_123"
        assert analytics_event.actor_user_id == "user_789"
        assert analytics_event.correlation_id == "corr_123"
        assert analytics_event.payload_json["client_id"] == "client_456"
        assert analytics_event.payload_json["previous_state"] == "new"
        assert analytics_event.payload_json["new_state"] == "in_progress"
    
    def test_map_assessment_recorded(self):
        """Test assessment recording event mapping"""
        event_data = {
            "assessment_id": "assessment_123",
            "client_id": "client_456",
            "user_id": "user_789",
            "risk_score": 75.5,
            "assessment_type": "tier_assessment",
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = EventMapper.map_assessment_recorded(event_data)
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.ASSESSMENT_RECORDED
        assert analytics_event.entity_type == "assessment"
        assert analytics_event.payload_json["risk_score"] == 75.5
        assert analytics_event.payload_json["client_id"] == "client_456"
    
    def test_map_alert_created(self):
        """Test alert creation event mapping"""
        event_data = {
            "alert_id": "alert_123",
            "client_id": "client_456",
            "alert_type": "compliance_issue",
            "severity": "medium",
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = EventMapper.map_alert_created(event_data)
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.ALERT_CREATED
        assert analytics_event.entity_type == "alert"
        assert analytics_event.payload_json["severity"] == "medium"
    
    def test_map_action_plan_version_activated(self):
        """Test action plan version activation mapping"""
        event_data = {
            "version_id": "version_123",
            "plan_id": "plan_456",
            "client_id": "client_789",
            "version_number": 2,
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = EventMapper.map_action_plan_version_activated(event_data)
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.ACTION_PLAN_VERSION_ACTIVATED
        assert analytics_event.entity_type == "action_plan_version"
        assert analytics_event.payload_json["version_number"] == 2
    
    def test_map_unsupported_event_type(self):
        """Test mapping of unsupported event type returns None"""
        event_data = {"some": "data"}
        
        analytics_event = EventMapper.map_event("UnsupportedEventType", event_data)
        
        assert analytics_event is None
    
    def test_extract_from_audit_log(self):
        """Test extraction from audit log entry"""
        audit_entry = {
            "action": "assessment_completed",
            "user_id": "user_123",
            "timestamp": datetime.utcnow(),
            "details": {
                "assessment_id": "assessment_456",
                "client_id": "client_789",
                "risk_score": 82.0
            }
        }
        
        analytics_event = extract_from_audit_log(audit_entry)
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.ASSESSMENT_RECORDED
        assert analytics_event.source == "audit_log"
    
    def test_extract_from_unmapped_audit_log(self):
        """Test extraction from unmapped audit log returns None"""
        audit_entry = {
            "action": "unmapped_action",
            "user_id": "user_123",
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = extract_from_audit_log(audit_entry)
        assert analytics_event is None
    
    def test_create_synthetic_event(self):
        """Test synthetic event creation"""
        analytics_event = create_synthetic_event(
            EventType.TASK_STATE_CHANGED,
            task_id="test_task",
            client_id="test_client",
            previous_state="new",
            new_state="completed"
        )
        
        assert analytics_event is not None
        assert analytics_event.event_type == EventType.TASK_STATE_CHANGED
        assert analytics_event.source == "synthetic"
        assert analytics_event.payload_json["task_id"] == "test_task"


class TestEventMappingEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_map_with_missing_required_fields(self):
        """Test mapping with missing required fields"""
        # Missing task_id
        event_data = {
            "client_id": "client_456",
            "previous_state": "new",
            "new_state": "in_progress"
        }
        
        analytics_event = EventMapper.map_task_state_changed(event_data)
        
        # Should still create event but with generated IDs
        assert analytics_event is not None
        assert analytics_event.entity_id is not None  # Generated UUID
    
    def test_map_with_none_values(self):
        """Test mapping with None values"""
        event_data = {
            "task_id": "task_123",
            "client_id": None,
            "user_id": None,
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = EventMapper.map_task_state_changed(event_data)
        
        assert analytics_event is not None
        assert analytics_event.actor_user_id is None
        assert analytics_event.payload_json["client_id"] is None
    
    def test_correlation_id_generation(self):
        """Test correlation ID generation when not provided"""
        event_data = {
            "task_id": "task_123",
            "timestamp": datetime.utcnow()
        }
        
        analytics_event = EventMapper.map_task_state_changed(event_data)
        
        assert analytics_event is not None
        assert analytics_event.correlation_id is not None
        assert "task_123" in analytics_event.correlation_id
    
    def test_timestamp_default(self):
        """Test timestamp default when not provided"""
        event_data = {
            "task_id": "task_123"
        }
        
        before_mapping = datetime.utcnow()
        analytics_event = EventMapper.map_task_state_changed(event_data)
        after_mapping = datetime.utcnow()
        
        assert analytics_event is not None
        assert before_mapping <= analytics_event.occurred_at <= after_mapping