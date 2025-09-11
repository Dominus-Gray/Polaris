"""
Event Ingestion Service

Handles ingestion of domain events into analytics_events collection.
Provides idempotent ingestion with correlation-based deduplication.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from analytics.models import AnalyticsEvent
from analytics.mapping import EventMapper, extract_from_audit_log
import os

logger = logging.getLogger(__name__)


class EventIngestionService:
    """Service for ingesting domain events into analytics"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.analytics_events = db.analytics_events
        self.enabled = os.environ.get("ENABLE_ANALYTICS", "true").lower() == "true"
        
    async def ingest_event(self, analytics_event: AnalyticsEvent) -> bool:
        """
        Ingest a single analytics event with idempotency protection
        
        Returns:
            bool: True if event was ingested, False if it was a duplicate
        """
        if not self.enabled:
            logger.debug("Analytics ingestion disabled via ENABLE_ANALYTICS flag")
            return False
            
        try:
            # Convert to dict for MongoDB
            event_dict = analytics_event.dict()
            
            # Attempt upsert with idempotency constraint
            result = await self.analytics_events.replace_one(
                {
                    "correlation_id": analytics_event.correlation_id,
                    "event_type": analytics_event.event_type,
                    "entity_id": analytics_event.entity_id
                },
                event_dict,
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"Ingested new analytics event: {analytics_event.event_type} for {analytics_event.entity_id}")
                return True
            else:
                logger.debug(f"Duplicate analytics event ignored: {analytics_event.correlation_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error ingesting analytics event: {e}")
            raise

    async def ingest_batch(self, analytics_events: List[AnalyticsEvent]) -> Dict[str, int]:
        """
        Ingest a batch of analytics events
        
        Returns:
            Dict with counts of ingested, duplicates, and errors
        """
        if not self.enabled:
            return {"ingested": 0, "duplicates": 0, "errors": 0}
            
        results = {"ingested": 0, "duplicates": 0, "errors": 0}
        
        for event in analytics_events:
            try:
                ingested = await self.ingest_event(event)
                if ingested:
                    results["ingested"] += 1
                else:
                    results["duplicates"] += 1
            except Exception as e:
                logger.error(f"Error in batch ingestion: {e}")
                results["errors"] += 1
                
        logger.info(f"Batch ingestion completed: {results}")
        return results

    async def ingest_from_audit_logs(self, since: Optional[datetime] = None) -> Dict[str, int]:
        """
        Ingest events from existing audit logs
        
        Args:
            since: Only process audit logs after this timestamp
        """
        if not self.enabled:
            return {"ingested": 0, "duplicates": 0, "errors": 0}
            
        # Query audit logs
        query = {}
        if since:
            query["timestamp"] = {"$gte": since}
            
        cursor = self.db.audit_logs.find(query).sort("timestamp", 1)
        
        analytics_events = []
        
        async for audit_entry in cursor:
            analytics_event = extract_from_audit_log(audit_entry)
            if analytics_event:
                analytics_events.append(analytics_event)
        
        if analytics_events:
            return await self.ingest_batch(analytics_events)
        else:
            logger.info("No mappable audit log entries found")
            return {"ingested": 0, "duplicates": 0, "errors": 0}

    async def ingest_domain_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Ingest a domain event by mapping it to analytics event
        
        Args:
            event_type: Type of domain event
            event_data: Event payload
        """
        analytics_event = EventMapper.map_event(event_type, event_data)
        if analytics_event:
            return await self.ingest_event(analytics_event)
        else:
            logger.warning(f"Could not map domain event: {event_type}")
            return False

    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get statistics about ingested events"""
        
        if not self.enabled:
            return {"enabled": False}
            
        try:
            # Count by event type
            pipeline = [
                {"$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "latest": {"$max": "$occurred_at"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            event_type_counts = []
            async for result in self.analytics_events.aggregate(pipeline):
                event_type_counts.append({
                    "event_type": result["_id"],
                    "count": result["count"],
                    "latest": result["latest"]
                })
            
            # Total count and time range
            total_count = await self.analytics_events.count_documents({})
            
            oldest_event = await self.analytics_events.find_one(
                {},
                sort=[("occurred_at", 1)]
            )
            
            newest_event = await self.analytics_events.find_one(
                {},
                sort=[("occurred_at", -1)]
            )
            
            return {
                "enabled": True,
                "total_events": total_count,
                "event_types": event_type_counts,
                "oldest_event": oldest_event.get("occurred_at") if oldest_event else None,
                "newest_event": newest_event.get("occurred_at") if newest_event else None,
                "data_lag_seconds": (
                    (datetime.utcnow() - newest_event["occurred_at"]).total_seconds()
                    if newest_event else None
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting ingestion stats: {e}")
            return {"enabled": True, "error": str(e)}


async def create_sample_events(db: AsyncIOMotorDatabase, count: int = 10) -> List[AnalyticsEvent]:
    """Create sample events for testing"""
    
    from analytics.mapping import create_synthetic_event
    from analytics.models import EventType
    
    sample_events = []
    
    # Create sample task state changes
    for i in range(count // 4):
        event = create_synthetic_event(
            EventType.TASK_STATE_CHANGED,
            task_id=f"task_{i}",
            client_id=f"client_{i % 3}",
            previous_state="new",
            new_state="in_progress",
            task_type="compliance_check"
        )
        if event:
            sample_events.append(event)
    
    # Create sample assessments
    for i in range(count // 4):
        event = create_synthetic_event(
            EventType.ASSESSMENT_RECORDED,
            assessment_id=f"assessment_{i}",
            client_id=f"client_{i % 3}",
            risk_score=75.5 + (i * 2),
            assessment_type="tier_assessment"
        )
        if event:
            sample_events.append(event)
    
    # Create sample alerts
    for i in range(count // 4):
        event = create_synthetic_event(
            EventType.ALERT_CREATED,
            alert_id=f"alert_{i}",
            client_id=f"client_{i % 3}",
            alert_type="compliance_issue",
            severity="medium"
        )
        if event:
            sample_events.append(event)
    
    # Create sample action plan activations
    for i in range(count // 4):
        event = create_synthetic_event(
            EventType.ACTION_PLAN_VERSION_ACTIVATED,
            version_id=f"version_{i}",
            plan_id=f"plan_{i}",
            client_id=f"client_{i % 3}",
            version_number=i + 1
        )
        if event:
            sample_events.append(event)
    
    return sample_events