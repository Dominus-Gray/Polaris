"""
Database migrations for Workflow Orchestration

This script creates the necessary collections and indexes for the workflow system.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_workflow_collections():
    """Create workflow collections and indexes"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'polaris_db')
    db = client[db_name]
    
    try:
        logger.info("Creating workflow collections and indexes...")
        
        # Create collections
        collections_to_create = [
            "tasks",
            "actionplans", 
            "sla_configs",
            "sla_records",
            "outbox_events"
        ]
        
        existing_collections = await db.list_collection_names()
        
        for collection_name in collections_to_create:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection already exists: {collection_name}")
        
        # Create indexes for tasks
        await db.tasks.create_index("id", unique=True)
        await db.tasks.create_index("state")
        await db.tasks.create_index("created_by")
        await db.tasks.create_index("assigned_to")
        await db.tasks.create_index("task_type")
        await db.tasks.create_index("action_plan_id")
        await db.tasks.create_index("created_at")
        logger.info("Created indexes for tasks collection")
        
        # Create indexes for actionplans
        await db.actionplans.create_index("id", unique=True)
        await db.actionplans.create_index("state")
        await db.actionplans.create_index("created_by")
        await db.actionplans.create_index("created_at")
        logger.info("Created indexes for actionplans collection")
        
        # Create indexes for sla_configs
        await db.sla_configs.create_index("id", unique=True)
        await db.sla_configs.create_index("service_area")
        await db.sla_configs.create_index("task_type")
        await db.sla_configs.create_index("active")
        logger.info("Created indexes for sla_configs collection")
        
        # Create indexes for sla_records
        await db.sla_records.create_index("id", unique=True)
        await db.sla_records.create_index("task_id")
        await db.sla_records.create_index("sla_config_id")
        await db.sla_records.create_index("breached")
        await db.sla_records.create_index("completed_at")
        await db.sla_records.create_index("started_at")
        logger.info("Created indexes for sla_records collection")
        
        # Create indexes for outbox_events
        await db.outbox_events.create_index("id", unique=True)
        await db.outbox_events.create_index("processed")
        await db.outbox_events.create_index("event_type")
        await db.outbox_events.create_index("aggregate_id")
        await db.outbox_events.create_index("aggregate_type")
        await db.outbox_events.create_index("created_at")
        await db.outbox_events.create_index("correlation_id")
        logger.info("Created indexes for outbox_events collection")
        
        # Insert default SLA configurations
        default_sla_configs = [
            {
                "id": "default_intake",
                "service_area": "intake",
                "target_minutes": 60,  # 1 hour
                "task_type": "intake",
                "active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "default_assessment",
                "service_area": "assessment",
                "target_minutes": 240,  # 4 hours
                "task_type": "assessment",
                "active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "default_review",
                "service_area": "review",
                "target_minutes": 120,  # 2 hours
                "task_type": "review",
                "active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "default_general",
                "service_area": "general",
                "target_minutes": 480,  # 8 hours
                "task_type": None,  # Applies to all task types without specific SLA
                "active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        for sla_config in default_sla_configs:
            existing = await db.sla_configs.find_one({"id": sla_config["id"]})
            if not existing:
                await db.sla_configs.insert_one(sla_config)
                logger.info(f"Inserted default SLA config: {sla_config['id']}")
            else:
                logger.info(f"SLA config already exists: {sla_config['id']}")
        
        logger.info("Workflow database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        client.close()

async def verify_migration():
    """Verify the migration was successful"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'polaris_db')
    db = client[db_name]
    
    try:
        logger.info("Verifying workflow migration...")
        
        # Check collections exist
        collections = await db.list_collection_names()
        required_collections = ["tasks", "actionplans", "sla_configs", "sla_records", "outbox_events"]
        
        for collection_name in required_collections:
            if collection_name in collections:
                logger.info(f"✓ Collection exists: {collection_name}")
            else:
                logger.error(f"✗ Collection missing: {collection_name}")
                return False
        
        # Check SLA configs
        sla_count = await db.sla_configs.count_documents({})
        logger.info(f"✓ SLA configs count: {sla_count}")
        
        # Check indexes (basic verification)
        tasks_indexes = await db.tasks.list_indexes().to_list(100)
        logger.info(f"✓ Tasks indexes count: {len(tasks_indexes)}")
        
        logger.info("Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    async def main():
        await create_workflow_collections()
        await verify_migration()
    
    asyncio.run(main())