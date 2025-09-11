"""
Projection Engine

Computes incremental daily metrics from analytics events.
Handles client and cohort aggregations with watermark tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from analytics.models import (
    ClientMetricsDaily, CohortMetricsDaily, CohortMembership, 
    EventType, ProjectionState
)
import asyncio

logger = logging.getLogger(__name__)


class ProjectionEngine:
    """Engine for computing daily metrics from analytics events"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.analytics_events = db.analytics_events
        self.client_metrics_daily = db.client_metrics_daily
        self.cohort_metrics_daily = db.cohort_metrics_daily
        self.cohort_memberships = db.cohort_memberships
        self.projection_state = db.projection_state
        self.users = db.users  # For cohort tag lookups

    async def run_incremental_projection(self, projection_name: str = "client_metrics_daily") -> Dict[str, Any]:
        """Run incremental projection from last watermark"""
        
        start_time = datetime.utcnow()
        
        try:
            # Get last processed watermark
            state = await self.projection_state.find_one({"projection_name": projection_name})
            
            last_processed = None
            if state and state.get("last_processed_timestamp"):
                last_processed = state["last_processed_timestamp"]
            
            logger.info(f"Starting incremental projection from: {last_processed}")
            
            # Get new events since last watermark
            query = {}
            if last_processed:
                query["occurred_at"] = {"$gt": last_processed}
            
            # Process events by date to ensure daily aggregations are complete
            events_by_date = await self._group_events_by_date(query)
            
            results = {
                "projection_name": projection_name,
                "events_processed": 0,
                "clients_updated": 0,
                "cohorts_updated": 0,
                "dates_processed": len(events_by_date)
            }
            
            new_watermark = last_processed
            
            for process_date, events in events_by_date.items():
                logger.info(f"Processing {len(events)} events for date: {process_date}")
                
                # Process client metrics for this date
                client_results = await self._project_client_metrics_for_date(process_date, events)
                results["clients_updated"] += client_results["clients_updated"]
                
                # Process cohort metrics for this date
                cohort_results = await self._project_cohort_metrics_for_date(process_date)
                results["cohorts_updated"] += cohort_results["cohorts_updated"]
                
                results["events_processed"] += len(events)
                
                # Update watermark to latest event in this date
                date_max_timestamp = max(event["occurred_at"] for event in events)
                if not new_watermark or date_max_timestamp > new_watermark:
                    new_watermark = date_max_timestamp
            
            # Update projection state
            if new_watermark:
                await self.projection_state.replace_one(
                    {"projection_name": projection_name},
                    {
                        "projection_name": projection_name,
                        "last_processed_timestamp": new_watermark,
                        "updated_at": datetime.utcnow()
                    },
                    upsert=True
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            results["duration_seconds"] = duration
            results["success"] = True
            
            logger.info(f"Incremental projection completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in incremental projection: {e}")
            duration = (datetime.utcnow() - start_time).total_seconds()
            return {
                "projection_name": projection_name,
                "success": False,
                "error": str(e),
                "duration_seconds": duration
            }

    async def _group_events_by_date(self, query: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by date for sequential processing"""
        
        cursor = self.analytics_events.find(query).sort("occurred_at", 1)
        events_by_date = {}
        
        async for event in cursor:
            event_date = event["occurred_at"].date().isoformat()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        return events_by_date

    async def _project_client_metrics_for_date(self, process_date: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Project client metrics for a specific date"""
        
        # Group events by client
        client_events = {}
        for event in events:
            client_id = event.get("payload_json", {}).get("client_id")
            if client_id:
                if client_id not in client_events:
                    client_events[client_id] = []
                client_events[client_id].append(event)
        
        clients_updated = 0
        
        for client_id, client_event_list in client_events.items():
            try:
                # Calculate metric deltas for this client and date
                deltas = await self._calculate_client_deltas(client_id, process_date, client_event_list)
                
                if deltas:
                    # Upsert client metrics
                    await self._upsert_client_metrics(client_id, process_date, deltas)
                    clients_updated += 1
                    
            except Exception as e:
                logger.error(f"Error projecting metrics for client {client_id}: {e}")
        
        return {"clients_updated": clients_updated}

    async def _calculate_client_deltas(self, client_id: str, date_str: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metric deltas for a client on a specific date"""
        
        deltas = {
            "tasks_completed": 0,
            "tasks_active_delta": 0,
            "tasks_blocked_delta": 0,
            "alerts_opened": 0,
            "action_plan_versions_activated": 0,
            "risk_score_latest": None
        }
        
        for event in events:
            event_type = event.get("event_type")
            payload = event.get("payload_json", {})
            
            if event_type == EventType.TASK_STATE_CHANGED:
                previous_state = payload.get("previous_state")
                new_state = payload.get("new_state")
                
                # Task completion
                if new_state == "completed":
                    deltas["tasks_completed"] += 1
                
                # Active task changes
                if new_state in ["in_progress", "pending"] and previous_state not in ["in_progress", "pending"]:
                    deltas["tasks_active_delta"] += 1
                elif previous_state in ["in_progress", "pending"] and new_state not in ["in_progress", "pending"]:
                    deltas["tasks_active_delta"] -= 1
                
                # Blocked task changes  
                if new_state == "blocked" and previous_state != "blocked":
                    deltas["tasks_blocked_delta"] += 1
                elif previous_state == "blocked" and new_state != "blocked":
                    deltas["tasks_blocked_delta"] -= 1
                    
            elif event_type == EventType.ALERT_CREATED:
                deltas["alerts_opened"] += 1
                
            elif event_type == EventType.ACTION_PLAN_VERSION_ACTIVATED:
                deltas["action_plan_versions_activated"] += 1
                
            elif event_type == EventType.ASSESSMENT_RECORDED:
                risk_score = payload.get("risk_score")
                if risk_score is not None:
                    deltas["risk_score_latest"] = float(risk_score)
        
        return deltas

    async def _upsert_client_metrics(self, client_id: str, date_str: str, deltas: Dict[str, Any]):
        """Upsert client metrics with calculated deltas"""
        
        # Get existing metrics for the date
        existing = await self.client_metrics_daily.find_one({
            "client_id": client_id,
            "date": date_str
        })
        
        if existing:
            # Update existing record
            updates = {
                "tasks_completed": existing.get("tasks_completed", 0) + deltas["tasks_completed"],
                "tasks_active": max(0, existing.get("tasks_active", 0) + deltas["tasks_active_delta"]),
                "tasks_blocked": max(0, existing.get("tasks_blocked", 0) + deltas["tasks_blocked_delta"]),
                "alerts_open": existing.get("alerts_open", 0) + deltas["alerts_opened"],
                "action_plan_versions_activated": existing.get("action_plan_versions_activated", 0) + deltas["action_plan_versions_activated"],
                "updated_at": datetime.utcnow()
            }
            
            # Update risk score if we have a new one
            if deltas["risk_score_latest"] is not None:
                updates["risk_score_avg"] = deltas["risk_score_latest"]
                
            await self.client_metrics_daily.update_one(
                {"client_id": client_id, "date": date_str},
                {"$set": updates}
            )
        else:
            # Create new record
            new_metrics = ClientMetricsDaily(
                client_id=client_id,
                date=date_str,
                risk_score_avg=deltas["risk_score_latest"],
                tasks_completed=deltas["tasks_completed"],
                tasks_active=max(0, deltas["tasks_active_delta"]),
                tasks_blocked=max(0, deltas["tasks_blocked_delta"]),
                alerts_open=deltas["alerts_opened"],
                action_plan_versions_activated=deltas["action_plan_versions_activated"]
            )
            
            await self.client_metrics_daily.insert_one(new_metrics.dict())

    async def _project_cohort_metrics_for_date(self, date_str: str) -> Dict[str, Any]:
        """Project cohort metrics by aggregating client metrics for the date"""
        
        # Update cohort memberships first
        await self._update_cohort_memberships(date_str)
        
        # Get all cohorts that have members
        active_cohorts = await self.cohort_memberships.distinct(
            "cohort_tag",
            {"removed_at": None}
        )
        
        cohorts_updated = 0
        
        for cohort_tag in active_cohorts:
            try:
                # Get clients in this cohort
                cohort_clients = await self.cohort_memberships.distinct(
                    "client_id",
                    {"cohort_tag": cohort_tag, "removed_at": None}
                )
                
                # Aggregate client metrics for this cohort and date
                client_metrics = await self.client_metrics_daily.find({
                    "client_id": {"$in": cohort_clients},
                    "date": date_str
                }).to_list(length=None)
                
                if client_metrics:
                    cohort_aggregates = self._aggregate_cohort_metrics(client_metrics)
                    cohort_aggregates["client_count"] = len(cohort_clients)
                    
                    # Upsert cohort metrics
                    await self._upsert_cohort_metrics(cohort_tag, date_str, cohort_aggregates)
                    cohorts_updated += 1
                    
            except Exception as e:
                logger.error(f"Error projecting cohort metrics for {cohort_tag}: {e}")
        
        return {"cohorts_updated": cohorts_updated}

    def _aggregate_cohort_metrics(self, client_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate client metrics to cohort level"""
        
        total_tasks_completed = sum(m.get("tasks_completed", 0) for m in client_metrics)
        total_alerts_open = sum(m.get("alerts_open", 0) for m in client_metrics)
        total_version_activations = sum(m.get("action_plan_versions_activated", 0) for m in client_metrics)
        
        # Calculate average risk score
        risk_scores = [m.get("risk_score_avg") for m in client_metrics if m.get("risk_score_avg") is not None]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else None
        
        return {
            "avg_risk_score": avg_risk_score,
            "tasks_completed": total_tasks_completed,
            "alerts_open": total_alerts_open,
            "version_activations": total_version_activations
        }

    async def _upsert_cohort_metrics(self, cohort_tag: str, date_str: str, aggregates: Dict[str, Any]):
        """Upsert cohort metrics for a date"""
        
        cohort_metrics = CohortMetricsDaily(
            cohort_tag=cohort_tag,
            date=date_str,
            **aggregates
        )
        
        await self.cohort_metrics_daily.replace_one(
            {"cohort_tag": cohort_tag, "date": date_str},
            cohort_metrics.dict(),
            upsert=True
        )

    async def _update_cohort_memberships(self, date_str: str):
        """Update cohort memberships based on current client profiles"""
        
        # Get all clients with cohort tags
        cursor = self.users.find(
            {"role": "client", "cohort_tags": {"$exists": True, "$ne": []}},
            {"id": 1, "cohort_tags": 1}
        )
        
        async for user in cursor:
            client_id = user.get("id")
            current_cohorts = set(user.get("cohort_tags", []))
            
            # Get existing memberships for this client
            existing_memberships = await self.cohort_memberships.find({
                "client_id": client_id,
                "removed_at": None
            }).to_list(length=None)
            
            existing_cohorts = set(m["cohort_tag"] for m in existing_memberships)
            
            # Add new cohort memberships
            new_cohorts = current_cohorts - existing_cohorts
            for cohort_tag in new_cohorts:
                membership = CohortMembership(
                    client_id=client_id,
                    cohort_tag=cohort_tag,
                    added_at=datetime.utcnow()
                )
                await self.cohort_memberships.insert_one(membership.dict())
            
            # Remove old cohort memberships
            removed_cohorts = existing_cohorts - current_cohorts
            if removed_cohorts:
                await self.cohort_memberships.update_many(
                    {
                        "client_id": client_id,
                        "cohort_tag": {"$in": list(removed_cohorts)},
                        "removed_at": None
                    },
                    {"$set": {"removed_at": datetime.utcnow()}}
                )

    async def backfill_metrics(self, from_date: str, to_date: str) -> Dict[str, Any]:
        """Backfill metrics for a date range using historical data"""
        
        logger.info(f"Starting backfill from {from_date} to {to_date}")
        
        # Parse dates
        start_date = datetime.fromisoformat(from_date).date()
        end_date = datetime.fromisoformat(to_date).date()
        
        current_date = start_date
        dates_processed = 0
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            # Get events for this date
            start_of_day = datetime.combine(current_date, datetime.min.time())
            end_of_day = datetime.combine(current_date, datetime.max.time())
            
            events = await self.analytics_events.find({
                "occurred_at": {"$gte": start_of_day, "$lte": end_of_day}
            }).to_list(length=None)
            
            if events:
                logger.info(f"Backfilling {len(events)} events for {date_str}")
                
                # Process this date
                await self._project_client_metrics_for_date(date_str, events)
                await self._project_cohort_metrics_for_date(date_str)
            
            current_date += timedelta(days=1)
            dates_processed += 1
        
        logger.info(f"Backfill completed: {dates_processed} dates processed")
        
        return {
            "success": True,
            "dates_processed": dates_processed,
            "from_date": from_date,
            "to_date": to_date
        }