"""
Workflow API Endpoints

This module provides FastAPI endpoints for workflow orchestration:
- Task state transitions
- ActionPlan lifecycle management
- Workflow metadata and introspection
- SLA management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from workflow import (
    TransitionEngine, 
    SLAManager, 
    Task, 
    ActionPlan, 
    TaskState, 
    ActionPlanState, 
    SLAConfig,
    STATE_MACHINE_REGISTRY
)
from workflow_workers import WorkflowObservability, increment_transition_metric

logger = logging.getLogger(__name__)

# Create workflow router
workflow_router = APIRouter(prefix="/workflow", tags=["workflow"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TaskTransitionRequest(BaseModel):
    """Request model for task state transition"""
    target_state: TaskState
    context: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class TaskTransitionResponse(BaseModel):
    """Response model for task transition"""
    success: bool
    message: str
    old_state: Optional[str] = None
    new_state: Optional[str] = None


class ActionPlanResponse(BaseModel):
    """Response model for action plan operations"""
    success: bool
    message: str
    action_plan: Optional[Dict[str, Any]] = None


class WorkflowMetadataResponse(BaseModel):
    """Response model for workflow metadata"""
    state_machines: Dict[str, Any]
    task_states: List[str]
    action_plan_states: List[str]
    transition_rules: Dict[str, List[Dict[str, str]]]


class TaskCreateRequest(BaseModel):
    """Request model for task creation"""
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    priority: str = "medium"
    assigned_to: Optional[str] = None
    action_plan_id: Optional[str] = None
    due_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ActionPlanCreateRequest(BaseModel):
    """Request model for action plan creation"""
    title: str
    description: Optional[str] = None
    goals: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SLAConfigRequest(BaseModel):
    """Request model for SLA configuration"""
    service_area: str
    target_minutes: int
    task_type: Optional[str] = None
    active: bool = True


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

async def get_transition_engine(db_client=None) -> TransitionEngine:
    """Get transition engine instance"""
    # In a real application, this would be injected properly
    # For now, we'll need to pass the db client from the main app
    if db_client is None:
        raise HTTPException(
            status_code=500,
            detail="Database client not available"
        )
    return TransitionEngine(db_client)


async def get_sla_manager(db_client=None) -> SLAManager:
    """Get SLA manager instance"""
    if db_client is None:
        raise HTTPException(
            status_code=500,
            detail="Database client not available"
        )
    return SLAManager(db_client)


async def get_workflow_observability(db_client=None) -> WorkflowObservability:
    """Get workflow observability instance"""
    if db_client is None:
        raise HTTPException(
            status_code=500,
            detail="Database client not available"
        )
    return WorkflowObservability(db_client)


# =============================================================================
# TASK ENDPOINTS
# =============================================================================

@workflow_router.post("/tasks", response_model=Dict[str, Any])
async def create_task(
    request: TaskCreateRequest,
    current_user: Dict = None,  # Will be injected by auth middleware
    db_client = None  # Will be injected
):
    """Create a new task"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        task_data = request.model_dump()
        task_data["created_by"] = current_user["id"]
        task_data["state"] = TaskState.NEW
        
        task = Task(**task_data)
        
        # Insert into database
        db = db_client.polaris_db
        await db.tasks.insert_one(task.model_dump())
        
        # Start SLA tracking if needed
        if task.task_type:
            sla_manager = SLAManager(db_client)
            await sla_manager.start_sla_tracking(task.id, task.task_type)
        
        logger.info(f"Created task: {task.id}")
        
        return {
            "success": True,
            "message": "Task created successfully",
            "task": task.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.post("/tasks/{task_id}/transition", response_model=TaskTransitionResponse)
async def transition_task(
    task_id: str,
    request: TaskTransitionRequest,
    current_user: Dict = None,
    db_client = None
):
    """Transition a task to a new state"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if task exists
        db = db_client.polaris_db
        task = await db.tasks.find_one({"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check permissions (basic check - could be enhanced)
        if task["created_by"] != current_user["id"] and current_user.get("role") not in ["admin", "agency"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        old_state = task["state"]
        
        # Execute transition
        transition_engine = TransitionEngine(db_client)
        success = await transition_engine.execute_transition(
            entity_type="Task",
            entity_id=task_id,
            target_state=request.target_state,
            actor_id=current_user["id"],
            context=request.context or {}
        )
        
        if success:
            # Handle SLA tracking state changes
            sla_manager = SLAManager(db_client)
            
            if request.target_state == TaskState.IN_PROGRESS and old_state == TaskState.NEW:
                await sla_manager.start_sla_tracking(task_id, task.get("task_type"))
            elif request.target_state in [TaskState.COMPLETED, TaskState.CANCELLED]:
                await sla_manager.complete_sla_tracking(task_id)
            
            # Metrics
            increment_transition_metric("Task", "success")
            
            return TaskTransitionResponse(
                success=True,
                message=f"Task transitioned from {old_state} to {request.target_state}",
                old_state=old_state,
                new_state=request.target_state
            )
        else:
            increment_transition_metric("Task", "failure")
            return TaskTransitionResponse(
                success=False,
                message="Transition not allowed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transitioning task: {e}")
        increment_transition_metric("Task", "error")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    current_user: Dict = None,
    db_client = None
):
    """Get task details"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = db_client.polaris_db
        task = await db.tasks.find_one({"id": task_id})
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Basic permission check
        if (task["created_by"] != current_user["id"] and 
            task.get("assigned_to") != current_user["id"] and
            current_user.get("role") not in ["admin", "agency"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.get("/tasks")
async def list_tasks(
    state: Optional[TaskState] = None,
    assigned_to: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
    current_user: Dict = None,
    db_client = None
):
    """List tasks with filters"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Build query
        query = {}
        
        # Users can see tasks they created or are assigned to (unless admin/agency)
        if current_user.get("role") not in ["admin", "agency"]:
            query["$or"] = [
                {"created_by": current_user["id"]},
                {"assigned_to": current_user["id"]}
            ]
        
        if state:
            query["state"] = state
        if assigned_to:
            query["assigned_to"] = assigned_to
        if task_type:
            query["task_type"] = task_type
        
        db = db_client.polaris_db
        tasks = await db.tasks.find(query).limit(limit).to_list(limit)
        
        return {"tasks": tasks, "count": len(tasks)}
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ACTION PLAN ENDPOINTS
# =============================================================================

@workflow_router.post("/action-plans", response_model=ActionPlanResponse)
async def create_action_plan(
    request: ActionPlanCreateRequest,
    current_user: Dict = None,
    db_client = None
):
    """Create a new action plan"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        action_plan_data = request.model_dump()
        action_plan_data["created_by"] = current_user["id"]
        action_plan_data["state"] = ActionPlanState.DRAFT
        action_plan_data["goals"] = action_plan_data.get("goals") or []
        
        action_plan = ActionPlan(**action_plan_data)
        
        # Insert into database
        db = db_client.polaris_db
        await db.actionplans.insert_one(action_plan.model_dump())
        
        logger.info(f"Created action plan: {action_plan.id}")
        
        return ActionPlanResponse(
            success=True,
            message="Action plan created successfully",
            action_plan=action_plan.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error creating action plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.post("/action-plans/{action_plan_id}/activate", response_model=ActionPlanResponse)
async def activate_action_plan(
    action_plan_id: str,
    current_user: Dict = None,
    db_client = None
):
    """Activate an action plan"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if action plan exists
        db = db_client.polaris_db
        action_plan = await db.actionplans.find_one({"id": action_plan_id})
        if not action_plan:
            raise HTTPException(status_code=404, detail="Action plan not found")
        
        # Check permissions
        if (action_plan["created_by"] != current_user["id"] and 
            current_user.get("role") not in ["admin", "agency"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Execute transition
        transition_engine = TransitionEngine(db_client)
        success = await transition_engine.execute_transition(
            entity_type="ActionPlan",
            entity_id=action_plan_id,
            target_state=ActionPlanState.ACTIVE,
            actor_id=current_user["id"]
        )
        
        if success:
            increment_transition_metric("ActionPlan", "success")
            
            # Get updated action plan
            updated_action_plan = await db.actionplans.find_one({"id": action_plan_id})
            
            return ActionPlanResponse(
                success=True,
                message="Action plan activated successfully",
                action_plan=updated_action_plan
            )
        else:
            increment_transition_metric("ActionPlan", "failure")
            return ActionPlanResponse(
                success=False,
                message="Cannot activate action plan in current state"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating action plan: {e}")
        increment_transition_metric("ActionPlan", "error")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.post("/action-plans/{action_plan_id}/archive", response_model=ActionPlanResponse)
async def archive_action_plan(
    action_plan_id: str,
    current_user: Dict = None,
    db_client = None
):
    """Archive an action plan"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if action plan exists
        db = db_client.polaris_db
        action_plan = await db.actionplans.find_one({"id": action_plan_id})
        if not action_plan:
            raise HTTPException(status_code=404, detail="Action plan not found")
        
        # Check permissions
        if (action_plan["created_by"] != current_user["id"] and 
            current_user.get("role") not in ["admin", "agency"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Execute transition
        transition_engine = TransitionEngine(db_client)
        success = await transition_engine.execute_transition(
            entity_type="ActionPlan",
            entity_id=action_plan_id,
            target_state=ActionPlanState.ARCHIVED,
            actor_id=current_user["id"]
        )
        
        if success:
            increment_transition_metric("ActionPlan", "success")
            
            # Get updated action plan
            updated_action_plan = await db.actionplans.find_one({"id": action_plan_id})
            
            return ActionPlanResponse(
                success=True,
                message="Action plan archived successfully",
                action_plan=updated_action_plan
            )
        else:
            increment_transition_metric("ActionPlan", "failure")
            return ActionPlanResponse(
                success=False,
                message="Cannot archive action plan in current state"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving action plan: {e}")
        increment_transition_metric("ActionPlan", "error")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.get("/action-plans/{action_plan_id}")
async def get_action_plan(
    action_plan_id: str,
    current_user: Dict = None,
    db_client = None
):
    """Get action plan details"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = db_client.polaris_db
        action_plan = await db.actionplans.find_one({"id": action_plan_id})
        
        if not action_plan:
            raise HTTPException(status_code=404, detail="Action plan not found")
        
        # Basic permission check
        if (action_plan["created_by"] != current_user["id"] and 
            current_user.get("role") not in ["admin", "agency"]):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return action_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting action plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WORKFLOW METADATA ENDPOINTS
# =============================================================================

@workflow_router.get("/metadata", response_model=WorkflowMetadataResponse)
async def get_workflow_metadata():
    """Get workflow metadata for UI introspection"""
    try:
        # Build transition rules for UI
        transition_rules = {}
        
        for entity_type, state_machine in STATE_MACHINE_REGISTRY.items():
            transitions = []
            for transition in state_machine.transitions:
                transitions.append({
                    "from": transition.from_state,
                    "to": transition.to_state,
                    "guard": transition.guard_condition
                })
            transition_rules[entity_type] = transitions
        
        return WorkflowMetadataResponse(
            state_machines=STATE_MACHINE_REGISTRY,
            task_states=[state.value for state in TaskState],
            action_plan_states=[state.value for state in ActionPlanState],
            transition_rules=transition_rules
        )
        
    except Exception as e:
        logger.error(f"Error getting workflow metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SLA ENDPOINTS
# =============================================================================

@workflow_router.post("/sla-configs", response_model=Dict[str, Any])
async def create_sla_config(
    request: SLAConfigRequest,
    current_user: Dict = None,
    db_client = None
):
    """Create SLA configuration"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check permissions (only admin/agency can create SLA configs)
        if current_user.get("role") not in ["admin", "agency"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        sla_config = SLAConfig(**request.model_dump())
        
        # Insert into database
        db = db_client.polaris_db
        await db.sla_configs.insert_one(sla_config.model_dump())
        
        logger.info(f"Created SLA config: {sla_config.id}")
        
        return {
            "success": True,
            "message": "SLA configuration created successfully",
            "sla_config": sla_config.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Error creating SLA config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@workflow_router.get("/sla-configs")
async def list_sla_configs(
    active_only: bool = True,
    current_user: Dict = None,
    db_client = None
):
    """List SLA configurations"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        query = {}
        if active_only:
            query["active"] = True
        
        db = db_client.polaris_db
        sla_configs = await db.sla_configs.find(query).to_list(100)
        
        return {"sla_configs": sla_configs, "count": len(sla_configs)}
        
    except Exception as e:
        logger.error(f"Error listing SLA configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MONITORING ENDPOINTS
# =============================================================================

@workflow_router.get("/stats")
async def get_workflow_stats(
    current_user: Dict = None,
    db_client = None
):
    """Get workflow statistics"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check permissions (only admin/agency can view stats)
        if current_user.get("role") not in ["admin", "agency"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        observability = WorkflowObservability(db_client)
        stats = await observability.get_workflow_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting workflow stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Function to integrate with main FastAPI app
def setup_workflow_api(app, db_client):
    """Setup workflow API with dependency injection"""
    
    # Create wrapper functions that inject the db_client
    async def inject_db_client():
        return db_client
    
    # Override dependency functions to inject db_client
    workflow_router.dependency_overrides[get_transition_engine] = lambda: TransitionEngine(db_client)
    workflow_router.dependency_overrides[get_sla_manager] = lambda: SLAManager(db_client)
    workflow_router.dependency_overrides[get_workflow_observability] = lambda: WorkflowObservability(db_client)
    
    # Include the router
    app.include_router(workflow_router)
    
    return workflow_router