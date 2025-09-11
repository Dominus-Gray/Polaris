"""
Migration 001: Core Domain Schema
Creates the foundational collections and indexes for the Polaris platform.
"""
from datetime import datetime
from .migration_base import Migration
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from pymongo import IndexModel, ASCENDING, DESCENDING
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Migration001(Migration):
    """Core Domain Schema Migration"""
    
    def __init__(self):
        super().__init__("001", "Create core domain schema and indexes")
    
    async def up(self, db: AsyncIOMotorDatabase) -> None:
        """Apply migration - create collections and indexes"""
        
        # Users collection with schema validation
        await self._create_users_collection(db)
        
        # Organizations collection
        await self._create_organizations_collection(db)
        
        # Organization memberships (many-to-many)
        await self._create_organization_memberships_collection(db)
        
        # Provider profiles
        await self._create_provider_profiles_collection(db)
        
        # Client profiles
        await self._create_client_profiles_collection(db)
        
        # Assessments
        await self._create_assessments_collection(db)
        
        # Action plans
        await self._create_action_plans_collection(db)
        
        # Tasks
        await self._create_tasks_collection(db)
        
        # Outcome records
        await self._create_outcome_records_collection(db)
        
        # Alerts
        await self._create_alerts_collection(db)
        
        # SLA records
        await self._create_sla_records_collection(db)
        
        # Audit events
        await self._create_audit_events_collection(db)
        
        # Outbox events (for event sourcing)
        await self._create_outbox_events_collection(db)
        
        logger.info("Core domain schema created successfully")
    
    async def down(self, db: AsyncIOMotorDatabase) -> None:
        """Rollback migration - drop collections"""
        collections_to_drop = [
            'users', 'organizations', 'organization_memberships',
            'provider_profiles', 'client_profiles', 'assessments',
            'action_plans', 'tasks', 'outcome_records', 'alerts',
            'sla_records', 'audit_events', 'outbox_events'
        ]
        
        for collection_name in collections_to_drop:
            await db.drop_collection(collection_name)
        
        logger.info("Core domain schema rolled back successfully")
    
    async def _create_users_collection(self, db: AsyncIOMotorDatabase):
        """Create users collection with validation"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "email", "name", "status", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "email": {"bsonType": "string", "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"},
                    "name": {"bsonType": "string", "minLength": 1},
                    "status": {"enum": ["active", "inactive", "suspended", "pending"]},
                    "auth_provider_id": {"bsonType": ["string", "null"]},
                    "mfa_enabled": {"bsonType": "bool"},
                    "last_login_at": {"bsonType": ["date", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("users", validator=validator)
        
        # Create indexes
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.users.create_index([("id", ASCENDING)], unique=True)
        await db.users.create_index([("status", ASCENDING)])
        await db.users.create_index([("created_at", DESCENDING)])
        await db.users.create_index([("auth_provider_id", ASCENDING)])
    
    async def _create_organizations_collection(self, db: AsyncIOMotorDatabase):
        """Create organizations collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "name", "org_type", "status", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "name": {"bsonType": "string", "minLength": 1},
                    "org_type": {"enum": ["agency", "provider", "client", "system"]},
                    "status": {"enum": ["active", "inactive", "pending", "suspended"]},
                    "compliance_tier": {"bsonType": ["string", "null"]},
                    "settings_json": {"bsonType": ["object", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("organizations", validator=validator)
        
        # Create indexes
        await db.organizations.create_index([("id", ASCENDING)], unique=True)
        await db.organizations.create_index([("name", ASCENDING)])
        await db.organizations.create_index([("org_type", ASCENDING), ("status", ASCENDING)])
        await db.organizations.create_index([("created_at", DESCENDING)])
    
    async def _create_organization_memberships_collection(self, db: AsyncIOMotorDatabase):
        """Create organization memberships collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "user_id", "organization_id", "roles", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "user_id": {"bsonType": "string"},
                    "organization_id": {"bsonType": "string"},
                    "roles": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("organization_memberships", validator=validator)
        
        # Create indexes
        await db.organization_memberships.create_index([("id", ASCENDING)], unique=True)
        await db.organization_memberships.create_index([("user_id", ASCENDING)])
        await db.organization_memberships.create_index([("organization_id", ASCENDING)])
        await db.organization_memberships.create_index([("user_id", ASCENDING), ("organization_id", ASCENDING)], unique=True)
    
    async def _create_provider_profiles_collection(self, db: AsyncIOMotorDatabase):
        """Create provider profiles collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "organization_id", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "organization_id": {"bsonType": "string"},
                    "taxonomy_codes": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "service_regions": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "capacity_metrics_json": {"bsonType": ["object", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("provider_profiles", validator=validator)
        
        # Create indexes
        await db.provider_profiles.create_index([("id", ASCENDING)], unique=True)
        await db.provider_profiles.create_index([("organization_id", ASCENDING)], unique=True)
        await db.provider_profiles.create_index([("service_regions", ASCENDING)])
    
    async def _create_client_profiles_collection(self, db: AsyncIOMotorDatabase):
        """Create client profiles collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "primary_identifier", "organization_id", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "primary_identifier": {"bsonType": "string"},
                    "user_id": {"bsonType": ["string", "null"]},
                    "organization_id": {"bsonType": "string"},
                    "demographics_json": {"bsonType": ["object", "null"]},
                    "risk_score": {"bsonType": ["number", "null"]},
                    "consent_policies_json": {"bsonType": ["object", "null"]},
                    "assigned_provider_id": {"bsonType": ["string", "null"]},
                    "cohort_tags": {"bsonType": ["array", "null"], "items": {"bsonType": "string"}},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("client_profiles", validator=validator)
        
        # Create indexes
        await db.client_profiles.create_index([("id", ASCENDING)], unique=True)
        await db.client_profiles.create_index([("primary_identifier", ASCENDING)], unique=True)
        await db.client_profiles.create_index([("user_id", ASCENDING)])
        await db.client_profiles.create_index([("organization_id", ASCENDING)])
        await db.client_profiles.create_index([("assigned_provider_id", ASCENDING)])
        await db.client_profiles.create_index([("cohort_tags", ASCENDING)])
    
    async def _create_assessments_collection(self, db: AsyncIOMotorDatabase):
        """Create assessments collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "template_version", "created_by", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "template_version": {"bsonType": "string"},
                    "responses_json": {"bsonType": ["object", "null"]},
                    "score_vector_json": {"bsonType": ["object", "null"]},
                    "risk_band": {"enum": ["low", "medium", "high", "critical", "unassessed"]},
                    "created_by": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("assessments", validator=validator)
        
        # Create indexes
        await db.assessments.create_index([("id", ASCENDING)], unique=True)
        await db.assessments.create_index([("client_id", ASCENDING), ("created_at", DESCENDING)])
        await db.assessments.create_index([("created_by", ASCENDING)])
        await db.assessments.create_index([("risk_band", ASCENDING)])
    
    async def _create_action_plans_collection(self, db: AsyncIOMotorDatabase):
        """Create action plans collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "version", "status", "generated_by_type", "generated_by_id", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "version": {"bsonType": "int", "minimum": 1},
                    "status": {"enum": ["draft", "active", "archived"]},
                    "goals_json": {"bsonType": ["object", "null"]},
                    "interventions_json": {"bsonType": ["object", "null"]},
                    "generated_by_type": {"enum": ["user", "system", "ai"]},
                    "generated_by_id": {"bsonType": "string"},
                    "supersedes_id": {"bsonType": ["string", "null"]},
                    "created_at": {"bsonType": "date"},
                    "published_at": {"bsonType": ["date", "null"]},
                    "archived_at": {"bsonType": ["date", "null"]}
                }
            }
        }
        
        await db.create_collection("action_plans", validator=validator)
        
        # Create indexes
        await db.action_plans.create_index([("id", ASCENDING)], unique=True)
        await db.action_plans.create_index([("client_id", ASCENDING), ("version", DESCENDING)])
        await db.action_plans.create_index([("status", ASCENDING)])
        await db.action_plans.create_index([("supersedes_id", ASCENDING)])
    
    async def _create_tasks_collection(self, db: AsyncIOMotorDatabase):
        """Create tasks collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "action_plan_id", "type", "title", "state", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "action_plan_id": {"bsonType": "string"},
                    "type": {"bsonType": "string"},
                    "title": {"bsonType": "string", "minLength": 1},
                    "description": {"bsonType": ["string", "null"]},
                    "state": {"enum": ["new", "in_progress", "blocked", "completed", "cancelled"]},
                    "due_at": {"bsonType": ["date", "null"]},
                    "assigned_to": {"bsonType": ["string", "null"]},
                    "priority": {"enum": ["low", "medium", "high", "urgent"]},
                    "automation_trigger_ref": {"bsonType": ["string", "null"]},
                    "sla_deadline_at": {"bsonType": ["date", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                    "completed_at": {"bsonType": ["date", "null"]}
                }
            }
        }
        
        await db.create_collection("tasks", validator=validator)
        
        # Create indexes
        await db.tasks.create_index([("id", ASCENDING)], unique=True)
        await db.tasks.create_index([("action_plan_id", ASCENDING)])
        await db.tasks.create_index([("state", ASCENDING)], partialFilterExpression={"state": "in_progress"})
        await db.tasks.create_index([("assigned_to", ASCENDING)])
        await db.tasks.create_index([("due_at", ASCENDING)])
        await db.tasks.create_index([("sla_deadline_at", ASCENDING)])
    
    async def _create_outcome_records_collection(self, db: AsyncIOMotorDatabase):
        """Create outcome records collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "client_id", "metric_type", "value_json", "evaluator_id", "recorded_at", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "client_id": {"bsonType": "string"},
                    "related_task_id": {"bsonType": ["string", "null"]},
                    "metric_type": {"bsonType": "string"},
                    "value_json": {"bsonType": "object"},
                    "evaluator_id": {"bsonType": "string"},
                    "recorded_at": {"bsonType": "date"},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("outcome_records", validator=validator)
        
        # Create indexes
        await db.outcome_records.create_index([("id", ASCENDING)], unique=True)
        await db.outcome_records.create_index([("client_id", ASCENDING), ("created_at", DESCENDING)])
        await db.outcome_records.create_index([("related_task_id", ASCENDING)])
        await db.outcome_records.create_index([("metric_type", ASCENDING)])
    
    async def _create_alerts_collection(self, db: AsyncIOMotorDatabase):
        """Create alerts collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "entity_type", "entity_id", "category", "severity", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "entity_type": {"bsonType": "string"},
                    "entity_id": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "severity": {"enum": ["low", "medium", "high", "critical"]},
                    "acknowledged_by": {"bsonType": ["string", "null"]},
                    "acknowledged_at": {"bsonType": ["date", "null"]},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("alerts", validator=validator)
        
        # Create indexes
        await db.alerts.create_index([("id", ASCENDING)], unique=True)
        await db.alerts.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)])
        await db.alerts.create_index([("severity", ASCENDING)])
        await db.alerts.create_index([("acknowledged_by", ASCENDING)])
        await db.alerts.create_index([("created_at", DESCENDING)])
    
    async def _create_sla_records_collection(self, db: AsyncIOMotorDatabase):
        """Create SLA records collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "service_area", "target_minutes", "started_at", "breached"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "task_id": {"bsonType": ["string", "null"]},
                    "service_area": {"bsonType": "string"},
                    "target_minutes": {"bsonType": "int", "minimum": 1},
                    "started_at": {"bsonType": "date"},
                    "stopped_at": {"bsonType": ["date", "null"]},
                    "breached": {"bsonType": "bool"},
                    "breach_reason": {"bsonType": ["string", "null"]}
                }
            }
        }
        
        await db.create_collection("sla_records", validator=validator)
        
        # Create indexes
        await db.sla_records.create_index([("id", ASCENDING)], unique=True)
        await db.sla_records.create_index([("task_id", ASCENDING)])
        await db.sla_records.create_index([("service_area", ASCENDING)])
        await db.sla_records.create_index([("breached", ASCENDING)])
        await db.sla_records.create_index([("started_at", DESCENDING)])
    
    async def _create_audit_events_collection(self, db: AsyncIOMotorDatabase):
        """Create audit events collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "event_type", "entity_type", "entity_id", "correlation_id", "created_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "actor_user_id": {"bsonType": ["string", "null"]},
                    "actor_service_id": {"bsonType": ["string", "null"]},
                    "event_type": {"bsonType": "string"},
                    "entity_type": {"bsonType": "string"},
                    "entity_id": {"bsonType": "string"},
                    "before_json": {"bsonType": ["object", "null"]},
                    "after_json": {"bsonType": ["object", "null"]},
                    "ip_address": {"bsonType": ["string", "null"]},
                    "user_agent": {"bsonType": ["string", "null"]},
                    "correlation_id": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
        
        await db.create_collection("audit_events", validator=validator)
        
        # Create indexes
        await db.audit_events.create_index([("id", ASCENDING)], unique=True)
        await db.audit_events.create_index([("correlation_id", ASCENDING)])
        await db.audit_events.create_index([("actor_user_id", ASCENDING)])
        await db.audit_events.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)])
        await db.audit_events.create_index([("event_type", ASCENDING)])
        await db.audit_events.create_index([("created_at", DESCENDING)])
    
    async def _create_outbox_events_collection(self, db: AsyncIOMotorDatabase):
        """Create outbox events collection"""
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "event_type", "aggregate_type", "aggregate_id", "payload_json", "occurred_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "event_type": {"bsonType": "string"},
                    "aggregate_type": {"bsonType": "string"},
                    "aggregate_id": {"bsonType": "string"},
                    "payload_json": {"bsonType": "object"},
                    "occurred_at": {"bsonType": "date"},
                    "processed_at": {"bsonType": ["date", "null"]}
                }
            }
        }
        
        await db.create_collection("outbox_events", validator=validator)
        
        # Create indexes
        await db.outbox_events.create_index([("id", ASCENDING)], unique=True)
        await db.outbox_events.create_index([("processed_at", ASCENDING)])  # For polling unprocessed events
        await db.outbox_events.create_index([("event_type", ASCENDING)])
        await db.outbox_events.create_index([("aggregate_type", ASCENDING), ("aggregate_id", ASCENDING)])
        await db.outbox_events.create_index([("occurred_at", DESCENDING)])


# Export the migration instance
migration_001 = Migration001()