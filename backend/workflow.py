"""
Workflow Orchestration and Automation Layer

This module implements the core workflow orchestration system including:
- State machines for Task and ActionPlan entities
- Transition engine with validation and event emission
- Automation trigger framework
- SLA tracking system
- Background processing workers
"""

from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import json

logger = logging.getLogger(__name__)


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class TaskState(str, Enum):
    """Task lifecycle states"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionPlanState(str, Enum):
    """ActionPlan lifecycle states"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


# =============================================================================
# CORE MODELS
# =============================================================================

class Task(BaseModel):
    """Task entity with state management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    state: TaskState = TaskState.NEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # user_id
    assigned_to: Optional[str] = None  # user_id
    action_plan_id: Optional[str] = None
    task_type: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    due_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActionPlan(BaseModel):
    """ActionPlan entity with state management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    state: ActionPlanState = ActionPlanState.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # user_id
    goals: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SLAConfig(BaseModel):
    """SLA configuration for services/task types"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_area: str
    target_minutes: int
    active: bool = True
    task_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SLARecord(BaseModel):
    """SLA tracking record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    sla_config_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    breached: bool = False
    actual_minutes: Optional[int] = None
    target_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OutboxEvent(BaseModel):
    """Event outbox for reliable event processing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    correlation_id: Optional[str] = None
    actor_id: Optional[str] = None
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


# =============================================================================
# DOMAIN EVENTS
# =============================================================================

class DomainEvent(BaseModel):
    """Base domain event"""
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    correlation_id: Optional[str] = None
    actor_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskStateChanged(DomainEvent):
    """Task state transition event"""
    event_type: str = "TaskStateChanged"
    aggregate_type: str = "Task"


class ActionPlanActivated(DomainEvent):
    """ActionPlan activation event"""
    event_type: str = "ActionPlanActivated"
    aggregate_type: str = "ActionPlan"


class ActionPlanArchived(DomainEvent):
    """ActionPlan archival event"""
    event_type: str = "ActionPlanArchived"
    aggregate_type: str = "ActionPlan"


# =============================================================================
# STATE MACHINE DEFINITIONS
# =============================================================================

class StateTransition(BaseModel):
    """Represents a state transition"""
    from_state: str
    to_state: str
    guard_condition: Optional[str] = None  # Python expression to evaluate


class StateMachine(BaseModel):
    """State machine definition"""
    entity_type: str
    states: Set[str]
    initial_state: str
    transitions: List[StateTransition]
    guards: Dict[str, Callable] = Field(default_factory=dict)
    hooks: Dict[str, List[Callable]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


# Task state machine configuration
TASK_STATE_MACHINE = StateMachine(
    entity_type="Task",
    states={
        TaskState.NEW,
        TaskState.IN_PROGRESS,
        TaskState.BLOCKED,
        TaskState.COMPLETED,
        TaskState.CANCELLED
    },
    initial_state=TaskState.NEW,
    transitions=[
        # From NEW
        StateTransition(from_state=TaskState.NEW, to_state=TaskState.IN_PROGRESS),
        StateTransition(from_state=TaskState.NEW, to_state=TaskState.BLOCKED),
        StateTransition(from_state=TaskState.NEW, to_state=TaskState.CANCELLED),
        
        # From IN_PROGRESS
        StateTransition(from_state=TaskState.IN_PROGRESS, to_state=TaskState.COMPLETED),
        StateTransition(from_state=TaskState.IN_PROGRESS, to_state=TaskState.BLOCKED),
        StateTransition(from_state=TaskState.IN_PROGRESS, to_state=TaskState.CANCELLED),
        
        # From BLOCKED
        StateTransition(from_state=TaskState.BLOCKED, to_state=TaskState.IN_PROGRESS),
        StateTransition(from_state=TaskState.BLOCKED, to_state=TaskState.CANCELLED),
    ]
)

# ActionPlan state machine configuration
ACTION_PLAN_STATE_MACHINE = StateMachine(
    entity_type="ActionPlan",
    states={
        ActionPlanState.DRAFT,
        ActionPlanState.ACTIVE,
        ActionPlanState.ARCHIVED
    },
    initial_state=ActionPlanState.DRAFT,
    transitions=[
        # From DRAFT
        StateTransition(from_state=ActionPlanState.DRAFT, to_state=ActionPlanState.ACTIVE),
        StateTransition(from_state=ActionPlanState.DRAFT, to_state=ActionPlanState.ARCHIVED),
        
        # From ACTIVE
        StateTransition(from_state=ActionPlanState.ACTIVE, to_state=ActionPlanState.ARCHIVED),
    ]
)

# Registry of all state machines
STATE_MACHINE_REGISTRY = {
    "Task": TASK_STATE_MACHINE,
    "ActionPlan": ACTION_PLAN_STATE_MACHINE
}


# =============================================================================
# AUTOMATION TRIGGERS
# =============================================================================

class AutomationAction(BaseModel):
    """Automation action definition"""
    action_type: str  # create_task, update_task_state, emit_alert, etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AutomationTrigger(BaseModel):
    """Automation trigger definition"""
    id: str
    event_type: str
    predicate: str  # Python expression for evaluation
    actions: List[AutomationAction]
    active: bool = True
    description: Optional[str] = None


# Sample automation triggers (hardcoded for MVP)
AUTOMATION_TRIGGERS = [
    AutomationTrigger(
        id="task_completion_follow_up",
        event_type="TaskStateChanged",
        predicate="event_data.get('new_state') == 'completed' and event_data.get('task_type') == 'intake'",
        actions=[
            AutomationAction(
                action_type="create_task",
                parameters={
                    "title": "Assessment Task",
                    "description": "Follow-up assessment task for completed intake",
                    "task_type": "assessment",
                    "priority": "high"
                }
            )
        ],
        description="Create assessment task when intake task is completed"
    ),
    AutomationTrigger(
        id="action_plan_activation_notification",
        event_type="ActionPlanActivated", 
        predicate="True",  # Always trigger
        actions=[
            AutomationAction(
                action_type="emit_alert",
                parameters={
                    "alert_type": "action_plan_activated",
                    "message": "Action plan has been activated"
                }
            )
        ],
        description="Send notification when action plan is activated"
    )
]


# =============================================================================
# TRANSITION ENGINE
# =============================================================================

class TransitionValidationResult(BaseModel):
    """Result of transition validation"""
    allowed: bool
    reasons: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransitionEngine:
    """Central engine for state transitions"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
        self.state_machines = STATE_MACHINE_REGISTRY
    
    def validate_transition(
        self,
        entity_type: str,
        current_state: str,
        target_state: str,
        context: Dict[str, Any] = None
    ) -> TransitionValidationResult:
        """Validate if a state transition is allowed"""
        context = context or {}
        
        if entity_type not in self.state_machines:
            return TransitionValidationResult(
                allowed=False,
                reasons=[f"Unknown entity type: {entity_type}"]
            )
        
        state_machine = self.state_machines[entity_type]
        
        # Check if target state exists
        if target_state not in state_machine.states:
            return TransitionValidationResult(
                allowed=False,
                reasons=[f"Invalid target state: {target_state}"]
            )
        
        # Check if transition is allowed
        allowed_transition = None
        for transition in state_machine.transitions:
            if (transition.from_state == current_state and 
                transition.to_state == target_state):
                allowed_transition = transition
                break
        
        if not allowed_transition:
            return TransitionValidationResult(
                allowed=False,
                reasons=[f"Transition from {current_state} to {target_state} not allowed"]
            )
        
        # Evaluate guard conditions if present
        if allowed_transition.guard_condition:
            try:
                # Simple evaluation - in production would use a safer eval approach
                guard_passed = eval(allowed_transition.guard_condition, {"context": context})
                if not guard_passed:
                    return TransitionValidationResult(
                        allowed=False,
                        reasons=[f"Guard condition failed: {allowed_transition.guard_condition}"]
                    )
            except Exception as e:
                return TransitionValidationResult(
                    allowed=False,
                    reasons=[f"Guard evaluation error: {str(e)}"]
                )
        
        return TransitionValidationResult(allowed=True)
    
    async def execute_transition(
        self,
        entity_type: str,
        entity_id: str,
        target_state: str,
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> bool:
        """Execute a state transition with validation and event emission"""
        context = context or {}
        
        # Get current entity
        collection_name = f"{entity_type.lower()}s"
        entity = await self.db[collection_name].find_one({"id": entity_id})
        
        if not entity:
            logger.error(f"Entity not found: {entity_type} {entity_id}")
            return False
        
        current_state = entity.get("state")
        
        # Validate transition
        validation = self.validate_transition(entity_type, current_state, target_state, context)
        if not validation.allowed:
            logger.warning(f"Transition denied: {validation.reasons}")
            return False
        
        # Update entity state
        update_data = {
            "state": target_state,
            "updated_at": datetime.utcnow()
        }
        
        await self.db[collection_name].update_one(
            {"id": entity_id},
            {"$set": update_data}
        )
        
        # Emit domain event
        event_data = {
            "entity_id": entity_id,
            "old_state": current_state,
            "new_state": target_state,
            "context": context
        }
        
        if entity_type == "Task":
            event_data["task_type"] = entity.get("task_type")
        
        await self._emit_event(
            event_type=f"{entity_type}StateChanged",
            aggregate_id=entity_id,
            aggregate_type=entity_type,
            event_data=event_data,
            actor_id=actor_id,
            correlation_id=correlation_id
        )
        
        logger.info(f"Transition executed: {entity_type} {entity_id} {current_state} -> {target_state}")
        return True
    
    async def _emit_event(
        self,
        event_type: str,
        aggregate_id: str,
        aggregate_type: str,
        event_data: Dict[str, Any],
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Emit domain event to outbox"""
        event = OutboxEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_data=event_data,
            actor_id=actor_id,
            correlation_id=correlation_id
        )
        
        await self.db.outbox_events.insert_one(event.model_dump())


# =============================================================================
# AUTOMATION DISPATCHER
# =============================================================================

class AutomationDispatcher:
    """Processes events and triggers automation"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
        self.triggers = {trigger.id: trigger for trigger in AUTOMATION_TRIGGERS}
    
    async def process_event(self, event: OutboxEvent):
        """Process an event and execute matching triggers"""
        matching_triggers = [
            trigger for trigger in self.triggers.values()
            if trigger.event_type == event.event_type and trigger.active
        ]
        
        for trigger in matching_triggers:
            try:
                # Evaluate predicate
                predicate_context = {
                    "event_data": event.event_data,
                    "event": event,
                    "aggregate_id": event.aggregate_id
                }
                
                if eval(trigger.predicate, predicate_context):
                    logger.info(f"Trigger matched: {trigger.id}")
                    await self._execute_actions(trigger.actions, event)
                
            except Exception as e:
                logger.error(f"Error evaluating trigger {trigger.id}: {e}")
    
    async def _execute_actions(self, actions: List[AutomationAction], event: OutboxEvent):
        """Execute automation actions"""
        for action in actions:
            try:
                if action.action_type == "create_task":
                    await self._create_task(action.parameters, event)
                elif action.action_type == "update_task_state":
                    await self._update_task_state(action.parameters, event)
                elif action.action_type == "emit_alert":
                    await self._emit_alert(action.parameters, event)
                elif action.action_type == "add_action_plan_goal_placeholder":
                    await self._add_action_plan_goal(action.parameters, event)
                elif action.action_type == "enqueue_external_webhook":
                    await self._enqueue_webhook(action.parameters, event)
                else:
                    logger.warning(f"Unknown action type: {action.action_type}")
                    
            except Exception as e:
                logger.error(f"Error executing action {action.action_type}: {e}")
    
    async def _create_task(self, parameters: Dict[str, Any], event: OutboxEvent):
        """Create a new task"""
        task_data = {
            "title": parameters.get("title", "Auto-generated Task"),
            "description": parameters.get("description"),
            "task_type": parameters.get("task_type"),
            "priority": parameters.get("priority", "medium"),
            "created_by": event.actor_id or "system",
            "state": TaskState.NEW,
            "metadata": {"auto_generated": True, "trigger_event": event.id}
        }
        
        task = Task(**task_data)
        await self.db.tasks.insert_one(task.model_dump())
        logger.info(f"Auto-created task: {task.id}")
    
    async def _update_task_state(self, parameters: Dict[str, Any], event: OutboxEvent):
        """Update task state"""
        task_id = parameters.get("task_id") or event.aggregate_id
        new_state = parameters.get("state")
        
        if task_id and new_state:
            await self.db.tasks.update_one(
                {"id": task_id},
                {"$set": {"state": new_state, "updated_at": datetime.utcnow()}}
            )
            logger.info(f"Auto-updated task {task_id} to state {new_state}")
    
    async def _emit_alert(self, parameters: Dict[str, Any], event: OutboxEvent):
        """Emit alert (placeholder - logs for now)"""
        alert_type = parameters.get("alert_type", "generic")
        message = parameters.get("message", "Alert triggered")
        
        logger.info(f"ALERT [{alert_type}]: {message} (Event: {event.id})")
    
    async def _add_action_plan_goal(self, parameters: Dict[str, Any], event: OutboxEvent):
        """Add goal to action plan"""
        action_plan_id = parameters.get("action_plan_id") or event.aggregate_id
        goal = parameters.get("goal", "Auto-added goal")
        
        if action_plan_id:
            await self.db.actionplans.update_one(
                {"id": action_plan_id},
                {"$push": {"goals": goal}, "$set": {"updated_at": datetime.utcnow()}}
            )
            logger.info(f"Added goal to action plan {action_plan_id}: {goal}")
    
    async def _enqueue_webhook(self, parameters: Dict[str, Any], event: OutboxEvent):
        """Enqueue external webhook (stub - logs for now)"""
        webhook_url = parameters.get("url")
        payload = parameters.get("payload", {})
        
        logger.info(f"WEBHOOK STUB: Would send to {webhook_url} with payload: {payload}")


# =============================================================================
# SLA MANAGER
# =============================================================================

class SLAManager:
    """Manages SLA tracking and breach detection"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
    
    async def start_sla_tracking(self, task_id: str, task_type: Optional[str] = None):
        """Start SLA tracking for a task"""
        # Find applicable SLA config
        query = {"active": True}
        if task_type:
            query["$or"] = [
                {"task_type": task_type},
                {"task_type": None}
            ]
        
        sla_config = await self.db.sla_configs.find_one(query)
        if not sla_config:
            logger.warning(f"No SLA config found for task {task_id} type {task_type}")
            return
        
        # Create SLA record
        sla_record = SLARecord(
            task_id=task_id,
            sla_config_id=sla_config["id"],
            started_at=datetime.utcnow(),
            target_minutes=sla_config["target_minutes"]
        )
        
        await self.db.sla_records.insert_one(sla_record.model_dump())
        logger.info(f"Started SLA tracking for task {task_id}")
    
    async def complete_sla_tracking(self, task_id: str):
        """Complete SLA tracking for a task"""
        sla_record = await self.db.sla_records.find_one({
            "task_id": task_id,
            "completed_at": None
        })
        
        if not sla_record:
            logger.warning(f"No active SLA record found for task {task_id}")
            return
        
        completed_at = datetime.utcnow()
        started_at = sla_record["started_at"]
        
        if started_at:
            actual_minutes = int((completed_at - started_at).total_seconds() / 60)
            breached = actual_minutes > sla_record["target_minutes"]
        else:
            actual_minutes = None
            breached = False
        
        await self.db.sla_records.update_one(
            {"id": sla_record["id"]},
            {
                "$set": {
                    "completed_at": completed_at,
                    "actual_minutes": actual_minutes,
                    "breached": breached
                }
            }
        )
        
        logger.info(f"Completed SLA tracking for task {task_id}, breached: {breached}")
    
    async def scan_for_breaches(self) -> List[str]:
        """Scan for potential SLA breaches (scheduled task)"""
        logger.info("Scanning for SLA breaches...")
        
        # Find active SLA records that might be breached
        current_time = datetime.utcnow()
        
        pipeline = [
            {
                "$match": {
                    "completed_at": None,
                    "started_at": {"$ne": None}
                }
            },
            {
                "$addFields": {
                    "elapsed_minutes": {
                        "$divide": [
                            {"$subtract": [current_time, "$started_at"]},
                            60000  # Convert to minutes
                        ]
                    }
                }
            },
            {
                "$match": {
                    "$expr": {"$gt": ["$elapsed_minutes", "$target_minutes"]}
                }
            }
        ]
        
        breached_records = await self.db.sla_records.aggregate(pipeline).to_list(1000)
        breached_task_ids = [record["task_id"] for record in breached_records]
        
        if breached_task_ids:
            logger.warning(f"Found {len(breached_task_ids)} SLA breaches: {breached_task_ids}")
        
        return breached_task_ids