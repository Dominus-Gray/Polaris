"""
Database migration script for Analytics & Cohort Projection Layer

Creates MongoDB collections with proper schema validation and indexes.
"""

import asyncio
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from analytics.models import ANALYTICS_COLLECTIONS_SCHEMA

logger = logging.getLogger(__name__)


async def initialize_analytics_collections(db):
    """Initialize analytics collections with schema validation and indexes"""
    
    logger.info("Initializing analytics collections...")
    
    for collection_name, schema_config in ANALYTICS_COLLECTIONS_SCHEMA.items():
        try:
            # Check if collection exists
            collection_names = await db.list_collection_names()
            
            if collection_name not in collection_names:
                # Create collection with schema validation
                logger.info(f"Creating collection: {collection_name}")
                await db.create_collection(
                    collection_name,
                    validator=schema_config.get("validator")
                )
            else:
                logger.info(f"Collection {collection_name} already exists")
                # Update validator if needed
                await db.command({
                    "collMod": collection_name,
                    "validator": schema_config.get("validator")
                })
            
            # Create indexes
            collection = db[collection_name]
            existing_indexes = await collection.index_information()
            
            for index_spec in schema_config.get("indexes", []):
                index_name = index_spec.get("name")
                if index_name not in existing_indexes:
                    logger.info(f"Creating index {index_name} on {collection_name}")
                    await collection.create_index(
                        index_spec["key"],
                        name=index_name,
                        unique=index_spec.get("unique", False),
                        sparse=index_spec.get("sparse", False)
                    )
                else:
                    logger.info(f"Index {index_name} already exists on {collection_name}")
                    
        except Exception as e:
            logger.error(f"Error initializing collection {collection_name}: {e}")
            raise
    
    logger.info("Analytics collections initialization completed")


async def seed_projection_state(db):
    """Seed initial projection state"""
    
    projection_states = [
        {
            "id": "client_metrics_projection",
            "projection_name": "client_metrics_daily",
            "last_processed_event_id": None,
            "last_processed_timestamp": None,
            "updated_at": None
        },
        {
            "id": "cohort_metrics_projection", 
            "projection_name": "cohort_metrics_daily",
            "last_processed_event_id": None,
            "last_processed_timestamp": None,
            "updated_at": None
        }
    ]
    
    collection = db.projection_state
    
    for state in projection_states:
        existing = await collection.find_one({"projection_name": state["projection_name"]})
        if not existing:
            logger.info(f"Seeding projection state: {state['projection_name']}")
            await collection.insert_one(state)
        else:
            logger.info(f"Projection state already exists: {state['projection_name']}")


async def main():
    """Main migration function"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Get database connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'polaris')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {db_name}")
        
        # Initialize collections
        await initialize_analytics_collections(db)
        
        # Seed initial data
        await seed_projection_state(db)
        
        logger.info("Analytics migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())