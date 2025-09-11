"""
Event Mapping Module

Maps domain events to normalized analytics_events for ingestion.
Handles extraction and transformation of relevant data from different event types.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from analytics.models import AnalyticsEvent, EventType
import uuid

logger = logging.getLogger(__name__)


class EventMapper:
    """Maps domain events to analytics events"""
    
    @staticmethod
    def map_task_state_changed(event_data: Dict[str, Any]) -> Optional[AnalyticsEvent]:
        """Map task state change events"""
        try:
            return AnalyticsEvent(
                event_type=EventType.TASK_STATE_CHANGED,
                entity_type="task",
                entity_id=event_data.get("task_id", str(uuid.uuid4())),
                actor_user_id=event_data.get("user_id"),
                occurred_at=event_data.get("timestamp", datetime.utcnow()),
                correlation_id=event_data.get("correlation_id", f"task_{event_data.get('task_id')}_{int(datetime.utcnow().timestamp())}"),
                payload_json={
                    "previous_state": event_data.get("previous_state"),
                    "new_state": event_data.get("new_state"),
                    "task_type": event_data.get("task_type"),
                    "client_id": event_data.get("client_id"),
                    "transition_reason": event_data.get("reason")
                },
                source=event_data.get("source", "polaris")
            )
        except Exception as e:
            logger.error(f"Error mapping task state changed event: {e}")
            return None

    @staticmethod
    def map_action_plan_version_activated(event_data: Dict[str, Any]) -> Optional[AnalyticsEvent]:
        """Map action plan version activation events"""
        try:
            return AnalyticsEvent(
                event_type=EventType.ACTION_PLAN_VERSION_ACTIVATED,
                entity_type="action_plan_version",
                entity_id=event_data.get("version_id", str(uuid.uuid4())),
                actor_user_id=event_data.get("user_id"),
                occurred_at=event_data.get("timestamp", datetime.utcnow()),
                correlation_id=event_data.get("correlation_id", f"plan_{event_data.get('plan_id')}_{event_data.get('version_id')}"),
                payload_json={
                    "plan_id": event_data.get("plan_id"),
                    "version_number": event_data.get("version_number"),
                    "client_id": event_data.get("client_id"),
                    "activation_context": event_data.get("context"),
                    "previous_version_id": event_data.get("previous_version_id")
                },
                source=event_data.get("source", "polaris")
            )
        except Exception as e:
            logger.error(f"Error mapping action plan version activated event: {e}")
            return None

    @staticmethod
    def map_alert_created(event_data: Dict[str, Any]) -> Optional[AnalyticsEvent]:
        """Map alert creation events"""
        try:
            return AnalyticsEvent(
                event_type=EventType.ALERT_CREATED,
                entity_type="alert",
                entity_id=event_data.get("alert_id", str(uuid.uuid4())),
                actor_user_id=event_data.get("user_id"),
                occurred_at=event_data.get("timestamp", datetime.utcnow()),
                correlation_id=event_data.get("correlation_id", f"alert_{event_data.get('alert_id')}"),
                payload_json={
                    "alert_type": event_data.get("alert_type"),
                    "severity": event_data.get("severity"),
                    "client_id": event_data.get("client_id"),
                    "related_entity_type": event_data.get("related_entity_type"),
                    "related_entity_id": event_data.get("related_entity_id"),
                    "alert_data": event_data.get("alert_data", {})
                },
                source=event_data.get("source", "polaris")
            )
        except Exception as e:
            logger.error(f"Error mapping alert created event: {e}")
            return None

    @staticmethod
    def map_assessment_recorded(event_data: Dict[str, Any]) -> Optional[AnalyticsEvent]:
        """Map assessment recording events"""
        try:
            return AnalyticsEvent(
                event_type=EventType.ASSESSMENT_RECORDED,
                entity_type="assessment",
                entity_id=event_data.get("assessment_id", str(uuid.uuid4())),
                actor_user_id=event_data.get("user_id"),
                occurred_at=event_data.get("timestamp", datetime.utcnow()),
                correlation_id=event_data.get("correlation_id", f"assessment_{event_data.get('assessment_id')}"),
                payload_json={
                    "assessment_type": event_data.get("assessment_type"),
                    "client_id": event_data.get("client_id"),
                    "risk_score": event_data.get("risk_score"),
                    "area_scores": event_data.get("area_scores", {}),
                    "completion_status": event_data.get("completion_status"),
                    "session_id": event_data.get("session_id")
                },
                source=event_data.get("source", "polaris")
            )
        except Exception as e:
            logger.error(f"Error mapping assessment recorded event: {e}")
            return None

    @classmethod
    def map_event(cls, event_type: str, event_data: Dict[str, Any]) -> Optional[AnalyticsEvent]:
        """Map any supported domain event to analytics event"""
        
        mapper_methods = {
            EventType.TASK_STATE_CHANGED: cls.map_task_state_changed,
            EventType.ACTION_PLAN_VERSION_ACTIVATED: cls.map_action_plan_version_activated,
            EventType.ALERT_CREATED: cls.map_alert_created,
            EventType.ASSESSMENT_RECORDED: cls.map_assessment_recorded
        }
        
        mapper = mapper_methods.get(event_type)
        if not mapper:
            logger.warning(f"No mapper found for event type: {event_type}")
            return None
            
        return mapper(event_data)


def extract_from_audit_log(audit_log_entry: Dict[str, Any]) -> Optional[AnalyticsEvent]:
    """Extract analytics event from existing audit log entry"""
    
    # Map audit log action types to analytics event types
    action_type_mapping = {
        "assessment_completed": EventType.ASSESSMENT_RECORDED,
        "task_status_changed": EventType.TASK_STATE_CHANGED,
        "action_plan_activated": EventType.ACTION_PLAN_VERSION_ACTIVATED,
        "alert_generated": EventType.ALERT_CREATED
    }
    
    action_type = audit_log_entry.get("action")
    event_type = action_type_mapping.get(action_type)
    
    if not event_type:
        logger.debug(f"Audit log action '{action_type}' not mapped to analytics event")
        return None
    
    # Transform audit log data to event data format
    event_data = {
        "user_id": audit_log_entry.get("user_id"),
        "timestamp": audit_log_entry.get("timestamp", datetime.utcnow()),
        "source": "audit_log",
        **audit_log_entry.get("details", {})
    }
    
    return EventMapper.map_event(event_type, event_data)


def create_synthetic_event(event_type: str, **kwargs) -> Optional[AnalyticsEvent]:
    """Create synthetic analytics event for testing/seeding"""
    
    default_data = {
        "timestamp": datetime.utcnow(),
        "source": "synthetic",
        "correlation_id": f"synthetic_{int(datetime.utcnow().timestamp())}"
    }
    
    event_data = {**default_data, **kwargs}
    return EventMapper.map_event(event_type, event_data)