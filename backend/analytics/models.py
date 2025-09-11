"""
Analytics Data Models

MongoDB collection schemas for analytics and cohort tracking.
Adapted from relational design to MongoDB with proper validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class AnalyticsEvent(BaseModel):
    """Domain event for analytics ingestion"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Type of domain event")
    entity_type: str = Field(..., description="Type of entity (task, alert, etc.)")
    entity_id: str = Field(..., description="UUID of the entity")
    actor_user_id: Optional[str] = Field(None, description="User who triggered the event")
    occurred_at: datetime = Field(..., description="When the event occurred")
    correlation_id: str = Field(..., description="Correlation ID for idempotency")
    payload_json: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    source: str = Field(default="polaris", description="Source system")
    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="When event was ingested")

    class Config:
        # MongoDB collection name
        collection_name = "analytics_events"


class ClientMetricsDaily(BaseModel):
    """Daily aggregated metrics per client"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = Field(..., description="Client user ID")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    risk_score_avg: Optional[float] = Field(None, description="Average risk score (or latest)")
    tasks_completed: int = Field(default=0, description="Tasks completed that day")
    tasks_active: int = Field(default=0, description="Tasks currently active")
    tasks_blocked: int = Field(default=0, description="Tasks currently blocked")
    alerts_open: int = Field(default=0, description="Currently open alerts")
    action_plan_versions_activated: int = Field(default=0, description="Action plan versions activated")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        collection_name = "client_metrics_daily"


class CohortMembership(BaseModel):
    """Temporal cohort membership tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = Field(..., description="Client user ID")
    cohort_tag: str = Field(..., description="Cohort identifier")
    added_at: datetime = Field(..., description="When client was added to cohort")
    removed_at: Optional[datetime] = Field(None, description="When client was removed from cohort")

    class Config:
        collection_name = "cohort_memberships"


class CohortMetricsDaily(BaseModel):
    """Daily aggregated metrics per cohort"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cohort_tag: str = Field(..., description="Cohort identifier")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    client_count: int = Field(..., description="Number of clients in cohort")
    avg_risk_score: Optional[float] = Field(None, description="Average risk score across cohort")
    tasks_completed: int = Field(default=0, description="Total tasks completed by cohort")
    alerts_open: int = Field(default=0, description="Total open alerts in cohort")
    version_activations: int = Field(default=0, description="Total action plan version activations")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        collection_name = "cohort_metrics_daily"


class OutcomeMetricSnapshot(BaseModel):
    """Placeholder for outcome metrics (minimal MVP implementation)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = Field(..., description="Client user ID")
    metric_type: str = Field(..., description="Type of outcome metric")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value_agg_json: Dict[str, Any] = Field(default_factory=dict, description="Aggregated metric values")

    class Config:
        collection_name = "outcome_metric_snapshots"


class EventType(str, Enum):
    """Supported event types for analytics ingestion"""
    TASK_STATE_CHANGED = "TaskStateChanged"
    ACTION_PLAN_VERSION_ACTIVATED = "ActionPlanVersionActivated"
    ALERT_CREATED = "AlertCreated"
    ASSESSMENT_RECORDED = "AssessmentRecorded"


class ProjectionState(BaseModel):
    """Tracks projection watermarks and state"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projection_name: str = Field(..., description="Name of the projection")
    last_processed_event_id: Optional[str] = Field(None, description="Last processed event ID")
    last_processed_timestamp: Optional[datetime] = Field(None, description="Last processed event timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection_name = "projection_state"


# MongoDB Collection Schema Definitions
ANALYTICS_COLLECTIONS_SCHEMA = {
    "analytics_events": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "event_type", "entity_type", "entity_id", "occurred_at", "correlation_id"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "event_type": {"bsonType": "string"},
                    "entity_type": {"bsonType": "string"},
                    "entity_id": {"bsonType": "string"},
                    "actor_user_id": {"bsonType": ["string", "null"]},
                    "occurred_at": {"bsonType": "date"},
                    "correlation_id": {"bsonType": "string"},
                    "payload_json": {"bsonType": "object"},
                    "source": {"bsonType": "string"},
                    "ingested_at": {"bsonType": "date"}
                }
            }
        },
        "indexes": [
            {"key": {"occurred_at": 1}, "name": "occurred_at_1"},
            {"key": {"event_type": 1, "occurred_at": 1}, "name": "event_type_occurred_at_1"},
            {"key": {"correlation_id": 1, "event_type": 1, "entity_id": 1}, "name": "correlation_unique", "unique": True},
            {"key": {"payload_json": "text"}, "name": "payload_json_text"}
        ]
    },
    "client_metrics_daily": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "date"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "date": {"bsonType": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
                    "risk_score_avg": {"bsonType": ["double", "null"]},
                    "tasks_completed": {"bsonType": "int", "minimum": 0},
                    "tasks_active": {"bsonType": "int", "minimum": 0},
                    "tasks_blocked": {"bsonType": "int", "minimum": 0},
                    "alerts_open": {"bsonType": "int", "minimum": 0},
                    "action_plan_versions_activated": {"bsonType": "int", "minimum": 0},
                    "updated_at": {"bsonType": "date"}
                }
            }
        },
        "indexes": [
            {"key": {"client_id": 1, "date": 1}, "name": "client_date_unique", "unique": True},
            {"key": {"date": 1}, "name": "date_1"}
        ]
    },
    "cohort_memberships": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "cohort_tag", "added_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "cohort_tag": {"bsonType": "string"},
                    "added_at": {"bsonType": "date"},
                    "removed_at": {"bsonType": ["date", "null"]}
                }
            }
        },
        "indexes": [
            {"key": {"client_id": 1, "cohort_tag": 1, "added_at": 1}, "name": "client_cohort_added_unique", "unique": True},
            {"key": {"cohort_tag": 1, "removed_at": 1}, "name": "cohort_active_members"}
        ]
    },
    "cohort_metrics_daily": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "cohort_tag", "date", "client_count"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "cohort_tag": {"bsonType": "string"},
                    "date": {"bsonType": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
                    "client_count": {"bsonType": "int", "minimum": 0},
                    "avg_risk_score": {"bsonType": ["double", "null"]},
                    "tasks_completed": {"bsonType": "int", "minimum": 0},
                    "alerts_open": {"bsonType": "int", "minimum": 0},
                    "version_activations": {"bsonType": "int", "minimum": 0},
                    "updated_at": {"bsonType": "date"}
                }
            }
        },
        "indexes": [
            {"key": {"cohort_tag": 1, "date": 1}, "name": "cohort_date_unique", "unique": True},
            {"key": {"date": 1}, "name": "date_1"}
        ]
    },
    "outcome_metric_snapshots": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "metric_type", "date"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "metric_type": {"bsonType": "string"},
                    "date": {"bsonType": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
                    "value_agg_json": {"bsonType": "object"}
                }
            }
        },
        "indexes": [
            {"key": {"client_id": 1, "metric_type": 1, "date": 1}, "name": "client_metric_date_unique", "unique": True}
        ]
    },
    "projection_state": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "projection_name"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "projection_name": {"bsonType": "string"},
                    "last_processed_event_id": {"bsonType": ["string", "null"]},
                    "last_processed_timestamp": {"bsonType": ["date", "null"]},
                    "updated_at": {"bsonType": "date"}
                }
            }
        },
        "indexes": [
            {"key": {"projection_name": 1}, "name": "projection_name_unique", "unique": True}
        ]
    }
}