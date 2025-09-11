"""
Domain Event Infrastructure for Polaris Platform
Implements event sourcing and outbox pattern for reliable event delivery
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, TypeVar, Callable
import uuid
import json
import logging
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='DomainEvent')


class EventType(Enum):
    """Domain event types following naming conventions"""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_STATUS_CHANGED = "user.status_changed"
    USER_LOGIN = "user.login"
    
    # Organization events
    ORGANIZATION_CREATED = "organization.created"
    ORGANIZATION_UPDATED = "organization.updated"
    MEMBERSHIP_CREATED = "organization.membership_created"
    MEMBERSHIP_REMOVED = "organization.membership_removed"
    
    # Client events
    CLIENT_PROFILE_CREATED = "client.profile_created"
    CLIENT_PROFILE_UPDATED = "client.profile_updated"
    CLIENT_ASSIGNED = "client.assigned_to_provider"
    
    # Assessment events
    ASSESSMENT_STARTED = "assessment.started"
    ASSESSMENT_COMPLETED = "assessment.completed"
    ASSESSMENT_SCORED = "assessment.scored"
    
    # Action Plan events
    ACTION_PLAN_CREATED = "action_plan.created"
    ACTION_PLAN_PUBLISHED = "action_plan.published"
    ACTION_PLAN_ARCHIVED = "action_plan.archived"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_STATE_CHANGED = "task.state_changed"
    TASK_COMPLETED = "task.completed"
    
    # Outcome events
    OUTCOME_RECORDED = "outcome.recorded"
    MILESTONE_ACHIEVED = "outcome.milestone_achieved"
    
    # Alert events
    ALERT_RAISED = "alert.raised"
    ALERT_ACKNOWLEDGED = "alert.acknowledged"
    
    # SLA events
    SLA_BREACH_WARNING = "sla.breach_warning"
    SLA_BREACHED = "sla.breached"
    
    # System events
    AUDIT_LOG_CREATED = "system.audit_log_created"


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events"""
    
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: datetime
    correlation_id: str
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.occurred_at:
            self.occurred_at = datetime.utcnow()
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create event from dictionary"""
        return cls(**data)


# Specific Domain Events

@dataclass
class UserCreatedEvent(DomainEvent):
    """User was created"""
    user_id: str
    email: str
    name: str
    role: str
    
    def __post_init__(self):
        self.event_type = EventType.USER_CREATED.value
        self.aggregate_type = "User"
        self.aggregate_id = self.user_id
        super().__post_init__()


@dataclass
class ClientProfileCreatedEvent(DomainEvent):
    """Client profile was created"""
    client_id: str
    organization_id: str
    primary_identifier: str
    user_id: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = EventType.CLIENT_PROFILE_CREATED.value
        self.aggregate_type = "ClientProfile"
        self.aggregate_id = self.client_id
        super().__post_init__()


@dataclass
class AssessmentCompletedEvent(DomainEvent):
    """Assessment was completed"""
    assessment_id: str
    client_id: str
    template_version: str
    risk_band: str
    score_vector: Dict[str, Any]
    
    def __post_init__(self):
        self.event_type = EventType.ASSESSMENT_COMPLETED.value
        self.aggregate_type = "Assessment"
        self.aggregate_id = self.assessment_id
        super().__post_init__()


@dataclass
class TaskStateChangedEvent(DomainEvent):
    """Task state was changed"""
    task_id: str
    action_plan_id: str
    old_state: str
    new_state: str
    changed_by: str
    
    def __post_init__(self):
        self.event_type = EventType.TASK_STATE_CHANGED.value
        self.aggregate_type = "Task"
        self.aggregate_id = self.task_id
        super().__post_init__()


class EventDispatcher:
    """Dispatches domain events using the outbox pattern"""
    
    def __init__(self, db: AsyncIOMotorDatabase, enable_sync_dispatch: bool = True):
        self.db = db
        self.enable_sync_dispatch = enable_sync_dispatch
        self._handlers: Dict[str, List[Callable]] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event using the outbox pattern"""
        # 1. Store in outbox for reliable delivery
        await self._store_in_outbox(event)
        
        # 2. Optionally dispatch synchronously for immediate consistency
        if self.enable_sync_dispatch:
            await self._dispatch_sync(event)
    
    async def _store_in_outbox(self, event: DomainEvent) -> None:
        """Store event in outbox collection"""
        outbox_record = {
            "id": event.event_id,
            "event_type": event.event_type,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": event.aggregate_id,
            "payload_json": event.to_dict(),
            "occurred_at": event.occurred_at,
            "processed_at": None
        }
        
        await self.db.outbox_events.insert_one(outbox_record)
        logger.debug(f"Stored event {event.event_id} in outbox")
    
    async def _dispatch_sync(self, event: DomainEvent) -> None:
        """Dispatch event synchronously to registered handlers"""
        handlers = self._handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                logger.debug(f"Handler {handler.__name__} processed event {event.event_id}")
            except Exception as e:
                logger.error(f"Handler {handler.__name__} failed for event {event.event_id}: {e}")
                # Continue processing other handlers


class OutboxProcessor:
    """Processes events from the outbox for eventual consistency"""
    
    def __init__(self, db: AsyncIOMotorDatabase, batch_size: int = 100):
        self.db = db
        self.batch_size = batch_size
        self._running = False
        self._handlers: Dict[str, List[Callable]] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def start(self, poll_interval: int = 5):
        """Start the outbox processor"""
        self._running = True
        logger.info("Outbox processor started")
        
        while self._running:
            try:
                await self._process_batch()
                await asyncio.sleep(poll_interval)
            except Exception as e:
                logger.error(f"Outbox processor error: {e}")
                await asyncio.sleep(poll_interval)
    
    def stop(self):
        """Stop the outbox processor"""
        self._running = False
        logger.info("Outbox processor stopped")
    
    async def _process_batch(self):
        """Process a batch of unprocessed events"""
        # Find unprocessed events
        cursor = self.db.outbox_events.find(
            {"processed_at": None}
        ).sort("occurred_at", 1).limit(self.batch_size)
        
        events = await cursor.to_list(length=self.batch_size)
        
        for event_doc in events:
            try:
                await self._process_event(event_doc)
                
                # Mark as processed
                await self.db.outbox_events.update_one(
                    {"_id": event_doc["_id"]},
                    {"$set": {"processed_at": datetime.utcnow()}}
                )
                
            except Exception as e:
                logger.error(f"Failed to process outbox event {event_doc['id']}: {e}")
    
    async def _process_event(self, event_doc: Dict[str, Any]):
        """Process a single event from the outbox"""
        event_type = event_doc["event_type"]
        handlers = self._handlers.get(event_type, [])
        
        # Reconstruct event from payload
        payload = event_doc["payload_json"]
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
                logger.debug(f"Outbox handler {handler.__name__} processed event {event_doc['id']}")
            except Exception as e:
                logger.error(f"Outbox handler {handler.__name__} failed for event {event_doc['id']}: {e}")


class EventFactory:
    """Factory for creating domain events"""
    
    _event_registry: Dict[str, Type[DomainEvent]] = {
        EventType.USER_CREATED.value: UserCreatedEvent,
        EventType.CLIENT_PROFILE_CREATED.value: ClientProfileCreatedEvent,
        EventType.ASSESSMENT_COMPLETED.value: AssessmentCompletedEvent,
        EventType.TASK_STATE_CHANGED.value: TaskStateChangedEvent,
    }
    
    @classmethod
    def register_event(cls, event_type: str, event_class: Type[DomainEvent]):
        """Register a new event type"""
        cls._event_registry[event_type] = event_class
    
    @classmethod
    def create_event(cls, event_type: str, **kwargs) -> DomainEvent:
        """Create an event instance"""
        event_class = cls._event_registry.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return event_class(**kwargs)
    
    @classmethod
    def from_dict(cls, event_data: Dict[str, Any]) -> DomainEvent:
        """Create event from dictionary"""
        event_type = event_data.get("event_type")
        if not event_type:
            raise ValueError("Missing event_type in event data")
        
        event_class = cls._event_registry.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return event_class.from_dict(event_data)


# Configuration for disabling async dispatch in test mode
class EventConfig:
    """Event system configuration"""
    
    enable_async_dispatch = True
    enable_sync_dispatch = True
    
    @classmethod
    def disable_async_dispatch(cls):
        """Disable async dispatch (for testing)"""
        cls.enable_async_dispatch = False
    
    @classmethod
    def enable_async_dispatch_mode(cls):
        """Enable async dispatch"""
        cls.enable_async_dispatch = True