"""
Analytics CLI Commands

Command-line interface for analytics operations including backfill and maintenance.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from analytics.migration import initialize_analytics_collections, seed_projection_state
from analytics.projection import ProjectionEngine
from analytics.ingestion import EventIngestionService, create_sample_events
from analytics.observability import (
    get_ingestion_logger, get_projection_logger, track_backfill_metrics
)
import typer

app = typer.Typer()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def get_database():
    """Get database connection"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'polaris')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Test connection
    try:
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {db_name}")
        return db, client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


@app.command()
def migrate():
    """Initialize analytics collections and indexes"""
    
    async def run_migration():
        db, client = await get_database()
        try:
            await initialize_analytics_collections(db)
            await seed_projection_state(db)
            logger.info("Analytics migration completed successfully")
        finally:
            client.close()
    
    asyncio.run(run_migration())


@app.command()
def backfill(
    from_date: str = typer.Argument(..., help="Start date in YYYY-MM-DD format"),
    to_date: str = typer.Argument(..., help="End date in YYYY-MM-DD format"),
    projection_name: str = typer.Option("client_metrics_daily", help="Projection to backfill")
):
    """Backfill analytics metrics for a date range"""
    
    @track_backfill_metrics()
    async def run_backfill():
        db, client = await get_database()
        try:
            # Validate dates
            try:
                start_date = datetime.fromisoformat(from_date).date()
                end_date = datetime.fromisoformat(to_date).date()
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                return
            
            if end_date < start_date:
                logger.error("End date must be after start date")
                return
            
            if (end_date - start_date).days > 365:
                logger.error("Date range cannot exceed 365 days")
                return
            
            logger.info(f"Starting backfill from {from_date} to {to_date}")
            
            # Run backfill
            projection_engine = ProjectionEngine(db)
            results = await projection_engine.backfill_metrics(from_date, to_date)
            
            # Log results
            backfill_logger = get_projection_logger()
            backfill_logger.log_backfill_operation(from_date, to_date, results)
            
            if results.get("success"):
                logger.info(f"Backfill completed successfully: {results['dates_processed']} dates processed")
            else:
                logger.error(f"Backfill failed: {results.get('error')}")
                
        finally:
            client.close()
    
    asyncio.run(run_backfill())


@app.command()
def project():
    """Run incremental projection from last watermark"""
    
    async def run_projection():
        db, client = await get_database()
        try:
            logger.info("Starting incremental projection")
            
            projection_engine = ProjectionEngine(db)
            results = await projection_engine.run_incremental_projection()
            
            # Log results
            projection_logger = get_projection_logger()
            projection_logger.log_projection_cycle("client_metrics_daily", results)
            
            if results.get("success"):
                logger.info(f"Projection completed: {results}")
            else:
                logger.error(f"Projection failed: {results.get('error')}")
                
        finally:
            client.close()
    
    asyncio.run(run_projection())


@app.command()
def seed_events(count: int = typer.Option(50, help="Number of sample events to create")):
    """Seed sample analytics events for testing"""
    
    async def run_seed():
        db, client = await get_database()
        try:
            logger.info(f"Creating {count} sample events")
            
            # Create sample events
            sample_events = await create_sample_events(db, count)
            
            # Ingest them
            ingestion_service = EventIngestionService(db)
            results = await ingestion_service.ingest_batch(sample_events)
            
            logger.info(f"Sample events ingested: {results}")
            
        finally:
            client.close()
    
    asyncio.run(run_seed())


@app.command()
def stats():
    """Show analytics statistics"""
    
    async def show_stats():
        db, client = await get_database()
        try:
            ingestion_service = EventIngestionService(db)
            stats = await ingestion_service.get_ingestion_stats()
            
            logger.info("Analytics Statistics:")
            logger.info(f"  Enabled: {stats.get('enabled')}")
            logger.info(f"  Total Events: {stats.get('total_events', 0)}")
            
            if stats.get('data_lag_seconds') is not None:
                logger.info(f"  Data Lag: {stats['data_lag_seconds']:.1f} seconds")
            
            if stats.get('oldest_event'):
                logger.info(f"  Oldest Event: {stats['oldest_event']}")
            
            if stats.get('newest_event'):
                logger.info(f"  Newest Event: {stats['newest_event']}")
            
            event_types = stats.get('event_types', [])
            if event_types:
                logger.info("  Event Types:")
                for et in event_types:
                    logger.info(f"    {et['event_type']}: {et['count']} (latest: {et.get('latest')})")
            
            # Collection counts
            collections = ['client_metrics_daily', 'cohort_metrics_daily', 'cohort_memberships']
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                logger.info(f"  {collection_name}: {count} documents")
                
        finally:
            client.close()
    
    asyncio.run(show_stats())


@app.command()
def validate(
    from_date: str = typer.Argument(..., help="Start date in YYYY-MM-DD format"),
    to_date: str = typer.Argument(..., help="End date in YYYY-MM-DD format")
):
    """Validate consistency between incremental and backfill results"""
    
    async def run_validation():
        db, client = await get_database()
        try:
            logger.info(f"Validating consistency from {from_date} to {to_date}")
            
            # Store original metrics
            original_metrics = {}
            
            # Get current metrics for date range
            cursor = db.client_metrics_daily.find({
                "date": {"$gte": from_date, "$lte": to_date}
            })
            
            async for metric in cursor:
                key = f"{metric['client_id']}:{metric['date']}"
                original_metrics[key] = metric
            
            logger.info(f"Found {len(original_metrics)} existing metrics")
            
            # Run backfill (this will overwrite existing metrics)
            projection_engine = ProjectionEngine(db)
            backfill_results = await projection_engine.backfill_metrics(from_date, to_date)
            
            if not backfill_results.get("success"):
                logger.error(f"Backfill failed during validation: {backfill_results.get('error')}")
                return
            
            # Compare results
            cursor = db.client_metrics_daily.find({
                "date": {"$gte": from_date, "$lte": to_date}
            })
            
            mismatches = 0
            matches = 0
            
            async for metric in cursor:
                key = f"{metric['client_id']}:{metric['date']}"
                original = original_metrics.get(key)
                
                if original:
                    # Compare key metrics
                    fields_to_compare = [
                        'tasks_completed', 'tasks_active', 'tasks_blocked',
                        'alerts_open', 'action_plan_versions_activated'
                    ]
                    
                    mismatch_found = False
                    for field in fields_to_compare:
                        if original.get(field) != metric.get(field):
                            logger.warning(
                                f"Mismatch in {key}.{field}: "
                                f"original={original.get(field)} vs backfill={metric.get(field)}"
                            )
                            mismatch_found = True
                    
                    if mismatch_found:
                        mismatches += 1
                    else:
                        matches += 1
                else:
                    logger.info(f"New metric found in backfill: {key}")
            
            logger.info(f"Validation completed: {matches} matches, {mismatches} mismatches")
            
            if mismatches > 0:
                logger.warning("Inconsistencies found between incremental and backfill results")
                sys.exit(1)
            else:
                logger.info("Validation successful: incremental and backfill results are consistent")
                
        finally:
            client.close()
    
    asyncio.run(run_validation())


@app.command() 
def clean(
    older_than_days: int = typer.Option(90, help="Remove events older than this many days")
):
    """Clean old analytics events"""
    
    async def run_clean():
        db, client = await get_database()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            logger.info(f"Removing analytics events older than {cutoff_date}")
            
            result = await db.analytics_events.delete_many({
                "occurred_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"Removed {result.deleted_count} old analytics events")
            
        finally:
            client.close()
    
    asyncio.run(run_clean())


if __name__ == "__main__":
    app()