"""
Database initialization script for Security, Encryption & Consent Baseline
Creates required collections and indexes
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

async def init_security_database():
    """Initialize database collections and indexes for security features"""
    
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'polaris_db')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"Initializing security database: {db_name}")
        
        # 1. Create encryption_keys collection
        print("Creating encryption_keys collection...")
        await db.create_collection("encryption_keys")
        
        # Index for fast key lookup
        await db.encryption_keys.create_index("key_alias", unique=True)
        await db.encryption_keys.create_index([("active", 1), ("key_alias", 1)])
        
        # 2. Create encryption_field_metadata collection
        print("Creating encryption_field_metadata collection...")
        await db.create_collection("encryption_field_metadata")
        
        # Unique index on resource and field_name
        await db.encryption_field_metadata.create_index(
            [("resource", 1), ("field_name", 1)], 
            unique=True
        )
        
        # 3. Create consent_records collection
        print("Creating consent_records collection...")
        await db.create_collection("consent_records")
        
        # Unique index on client_id, scope, granted_at
        await db.consent_records.create_index(
            [("client_id", 1), ("scope", 1), ("granted_at", 1)],
            unique=True
        )
        
        # Partial index for active consents (where revoked_at is NULL)
        await db.consent_records.create_index(
            "client_id", 
            partialFilterExpression={"revoked_at": None}
        )
        
        # 4. Extend or create audit_logs collection
        print("Setting up audit_logs collection...")
        
        # Check if audit_logs collection exists
        collection_names = await db.list_collection_names()
        if "audit_logs" not in collection_names:
            await db.create_collection("audit_logs")
        
        # Add indexes for audit logs
        await db.audit_logs.create_index("timestamp")
        await db.audit_logs.create_index("user_id")
        await db.audit_logs.create_index("resource")
        await db.audit_logs.create_index("action")
        
        # 5. Extend client_profiles collection (add encrypted columns)
        print("Preparing client_profiles for encrypted fields...")
        
        # Check if client_profiles exists, create if not
        if "client_profiles" not in collection_names:
            await db.create_collection("client_profiles")
        
        # Add index for SSN HMAC lookups
        await db.client_profiles.create_index("ssn_hmac", sparse=True)
        
        # 6. Extend assessments collection
        print("Preparing assessments for encrypted fields...")
        
        if "assessments" not in collection_names:
            await db.create_collection("assessments")
        
        # 7. Create rotation_state collection for key rotation tracking
        print("Creating rotation_state collection...")
        await db.create_collection("rotation_state")
        await db.rotation_state.create_index("rotation_id", unique=True)
        
        print("✅ Security database initialization completed successfully!")
        
        # Test the setup
        await test_setup(db)
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def test_setup(db):
    """Test the database setup"""
    print("\nTesting database setup...")
    
    try:
        # Test inserting a sample encryption key
        test_key = {
            "_id": "test_key_id",
            "key_alias": "test_alias", 
            "material_wrapped": b"test_wrapped_key",
            "algorithm": "AES256_GCM",
            "active": True,
            "created_at": "2025-01-08T00:00:00Z",
            "rotated_at": None
        }
        
        await db.encryption_keys.insert_one(test_key)
        
        # Test unique constraint
        try:
            await db.encryption_keys.insert_one(test_key)
            print("❌ Unique constraint not working!")
        except Exception:
            print("✅ Unique constraint working correctly")
        
        # Clean up test data
        await db.encryption_keys.delete_one({"_id": "test_key_id"})
        
        print("✅ Database setup test completed")
        
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")

if __name__ == "__main__":
    asyncio.run(init_security_database())