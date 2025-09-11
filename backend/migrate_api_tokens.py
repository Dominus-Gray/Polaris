"""
Database Migration Script for API Hardening
Creates the api_tokens collection with proper indexes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def create_api_tokens_collection():
    """Create api_tokens collection with proper indexes"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'polaris_db')]
    
    # Create indexes for api_tokens collection
    print("Creating API tokens collection indexes...")
    
    # Index on token_prefix for fast token lookups
    await db.api_tokens.create_index("token_prefix", unique=True)
    print("✅ Created index on token_prefix")
    
    # Index on owner_user_id for listing user tokens
    await db.api_tokens.create_index("owner_user_id")
    print("✅ Created index on owner_user_id")
    
    # Compound index for active tokens
    await db.api_tokens.create_index([
        ("owner_user_id", 1),
        ("is_active", 1),
        ("revoked_at", 1)
    ])
    print("✅ Created compound index for active tokens")
    
    # Index on expires_at for cleanup
    await db.api_tokens.create_index("expires_at", sparse=True)
    print("✅ Created index on expires_at")
    
    # Index on last_used_at for analytics
    await db.api_tokens.create_index("last_used_at", sparse=True)
    print("✅ Created index on last_used_at")
    
    print("API tokens collection setup complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_api_tokens_collection())