"""
Background Workers for Workflow Orchestration

This module implements background processing workers for:
- Processing outbox events for automation triggers
- SLA breach monitoring and alerts
- Scheduled maintenance tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from workflow import AutomationDispatcher, SLAManager, OutboxEvent

logger = logging.getLogger(__name__)


class WorkflowWorkers:
    """Background workers for workflow processing"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
        self.automation_dispatcher = AutomationDispatcher(db_client)
        self.sla_manager = SLAManager(db_client)
        self._running = False
        self._tasks = []
    
    async def start(self):
        """Start all background workers"""
        if self._running:
            logger.warning("Workers already running")
            return
        
        self._running = True
        logger.info("Starting workflow workers...")
        
        # Start event processing worker
        self._tasks.append(
            asyncio.create_task(self._event_processing_loop())
        )
        
        # Start SLA monitoring worker
        self._tasks.append(
            asyncio.create_task(self._sla_monitoring_loop())
        )
        
        logger.info("Workflow workers started")
    
    async def stop(self):
        """Stop all background workers"""
        if not self._running:
            return
        
        self._running = False
        logger.info("Stopping workflow workers...")
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for cancellation
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        logger.info("Workflow workers stopped")
    
    async def _event_processing_loop(self):
        """Main loop for processing outbox events"""
        logger.info("Event processing worker started")
        
        while self._running:
            try:
                # Process unprocessed events
                await self._process_outbox_events()
                
                # Sleep before next iteration
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except asyncio.CancelledError:
                logger.info("Event processing worker cancelled")
                break
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _sla_monitoring_loop(self):
        """Main loop for SLA monitoring"""
        logger.info("SLA monitoring worker started")
        
        while self._running:
            try:
                # Check for SLA breaches
                breached_tasks = await self.sla_manager.scan_for_breaches()
                
                if breached_tasks:
                    await self._handle_sla_breaches(breached_tasks)
                
                # Sleep before next check (every 5 minutes)
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("SLA monitoring worker cancelled")
                break
            except Exception as e:
                logger.error(f"Error in SLA monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _process_outbox_events(self):
        """Process unprocessed events from outbox"""
        # Get unprocessed events (oldest first)
        events_cursor = self.db.outbox_events.find(
            {"processed": False}
        ).sort("created_at", 1).limit(100)
        
        events = await events_cursor.to_list(100)
        
        for event_doc in events:
            try:
                # Convert to OutboxEvent model
                event = OutboxEvent(**event_doc)
                
                # Process the event
                await self.automation_dispatcher.process_event(event)
                
                # Mark as processed
                await self.db.outbox_events.update_one(
                    {"id": event.id},
                    {
                        "$set": {
                            "processed": True,
                            "processed_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.debug(f"Processed event: {event.id}")
                
            except Exception as e:
                logger.error(f"Error processing event {event_doc.get('id')}: {e}")
                
                # Mark as failed (could implement retry logic here)
                await self.db.outbox_events.update_one(
                    {"id": event_doc.get("id")},
                    {
                        "$set": {
                            "processed": True,  # Mark as processed to avoid infinite retry
                            "processed_at": datetime.utcnow(),
                            "error": str(e)
                        }
                    }
                )
    
    async def _handle_sla_breaches(self, breached_task_ids: list):
        """Handle SLA breaches"""
        for task_id in breached_task_ids:
            try:
                # Log the breach
                logger.warning(f"SLA breach detected for task: {task_id}")
                
                # Could emit an event for breach notification
                # or send alerts to monitoring systems
                
                # For now, just log - could be enhanced to:
                # - Send notifications to assignees
                # - Escalate to managers
                # - Update priority
                # - Create follow-up tasks
                
            except Exception as e:
                logger.error(f"Error handling SLA breach for task {task_id}: {e}")


# =============================================================================
# METRICS AND MONITORING
# =============================================================================

try:
    from prometheus_client import Counter, Histogram, Gauge
    
    # Workflow metrics
    workflow_transition_total = Counter(
        'workflow_transition_total',
        'Total number of workflow transitions',
        ['entity_type', 'result']
    )
    
    automation_trigger_evaluations_total = Counter(
        'automation_trigger_evaluations_total',
        'Total automation trigger evaluations',
        ['trigger_id', 'outcome']
    )
    
    sla_records_breached_total = Counter(
        'sla_records_breached_total',
        'Total SLA records breached'
    )
    
    outbox_events_processed_total = Counter(
        'outbox_events_processed_total',
        'Total outbox events processed',
        ['event_type', 'status']
    )
    
    active_tasks_gauge = Gauge(
        'active_tasks_total',
        'Total number of active tasks',
        ['state']
    )
    
    METRICS_AVAILABLE = True
    logger.info("Prometheus metrics initialized")
    
except ImportError:
    logger.warning("Prometheus client not available, metrics disabled")
    METRICS_AVAILABLE = False
    
    # Create dummy metrics
    class DummyMetric:
        def inc(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
    
    workflow_transition_total = DummyMetric()
    automation_trigger_evaluations_total = DummyMetric()
    sla_records_breached_total = DummyMetric()
    outbox_events_processed_total = DummyMetric()
    active_tasks_gauge = DummyMetric()


def increment_transition_metric(entity_type: str, result: str):
    """Increment transition metric"""
    workflow_transition_total.labels(entity_type=entity_type, result=result).inc()


def increment_trigger_metric(trigger_id: str, outcome: str):
    """Increment trigger evaluation metric"""
    automation_trigger_evaluations_total.labels(trigger_id=trigger_id, outcome=outcome).inc()


def increment_sla_breach_metric():
    """Increment SLA breach metric"""
    sla_records_breached_total.inc()


def increment_outbox_metric(event_type: str, status: str):
    """Increment outbox processing metric"""
    outbox_events_processed_total.labels(event_type=event_type, status=status).inc()


def update_active_tasks_gauge(state: str, count: int):
    """Update active tasks gauge"""
    active_tasks_gauge.labels(state=state).set(count)


# =============================================================================
# WORKFLOW OBSERVABILITY
# =============================================================================

class WorkflowObservability:
    """Workflow observability and monitoring"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
    
    async def update_metrics(self):
        """Update workflow metrics"""
        if not METRICS_AVAILABLE:
            return
        
        try:
            # Update active tasks by state
            pipeline = [
                {"$group": {"_id": "$state", "count": {"$sum": 1}}}
            ]
            
            state_counts = await self.db.tasks.aggregate(pipeline).to_list(100)
            
            for state_count in state_counts:
                state = state_count["_id"]
                count = state_count["count"]
                update_active_tasks_gauge(state, count)
            
        except Exception as e:
            logger.error(f"Error updating workflow metrics: {e}")
    
    async def get_workflow_stats(self) -> dict:
        """Get workflow statistics for monitoring"""
        try:
            # Task statistics
            task_stats = await self.db.tasks.aggregate([
                {"$group": {"_id": "$state", "count": {"$sum": 1}}}
            ]).to_list(100)
            
            # ActionPlan statistics  
            action_plan_stats = await self.db.actionplans.aggregate([
                {"$group": {"_id": "$state", "count": {"$sum": 1}}}
            ]).to_list(100)
            
            # SLA statistics
            sla_breach_count = await self.db.sla_records.count_documents({"breached": True})
            active_sla_count = await self.db.sla_records.count_documents({"completed_at": None})
            
            # Event processing statistics
            unprocessed_events = await self.db.outbox_events.count_documents({"processed": False})
            
            return {
                "tasks_by_state": {item["_id"]: item["count"] for item in task_stats},
                "action_plans_by_state": {item["_id"]: item["count"] for item in action_plan_stats},
                "sla_breaches": sla_breach_count,
                "active_sla_records": active_sla_count,
                "unprocessed_events": unprocessed_events,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow stats: {e}")
            return {"error": str(e)}


# Global worker instance
_workflow_workers: Optional[WorkflowWorkers] = None


async def start_workflow_workers(db_client: AsyncIOMotorClient):
    """Start global workflow workers"""
    global _workflow_workers
    
    if _workflow_workers is None:
        _workflow_workers = WorkflowWorkers(db_client)
    
    await _workflow_workers.start()


async def stop_workflow_workers():
    """Stop global workflow workers"""
    global _workflow_workers
    
    if _workflow_workers:
        await _workflow_workers.stop()


def get_workflow_workers() -> Optional[WorkflowWorkers]:
    """Get global workflow workers instance"""
    return _workflow_workers