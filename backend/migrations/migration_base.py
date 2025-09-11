"""
MongoDB Migration Base Classes and Infrastructure
"""
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class Migration(ABC):
    """Base class for MongoDB migrations"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at: Optional[datetime] = None
    
    @abstractmethod
    async def up(self, db: AsyncIOMotorDatabase) -> None:
        """Apply the migration"""
        pass
    
    @abstractmethod
    async def down(self, db: AsyncIOMotorDatabase) -> None:
        """Rollback the migration"""
        pass


class MigrationManager:
    """Manages MongoDB migrations for Polaris Platform"""
    
    def __init__(self, mongo_url: str, database_name: str):
        self.mongo_url = mongo_url
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.migrations: List[Migration] = []
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.database_name]
        
        # Ensure migrations collection exists
        await self.ensure_migrations_collection()
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def ensure_migrations_collection(self):
        """Ensure the migrations tracking collection exists"""
        if 'migrations' not in await self.db.list_collection_names():
            await self.db.create_collection('migrations')
            
        # Create index on version field
        await self.db.migrations.create_index("version", unique=True)
    
    def register_migration(self, migration: Migration):
        """Register a migration"""
        self.migrations.append(migration)
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        cursor = self.db.migrations.find({}, {"version": 1}).sort("version", 1)
        return [doc["version"] async for doc in cursor]
    
    async def mark_migration_applied(self, migration: Migration):
        """Mark a migration as applied"""
        await self.db.migrations.insert_one({
            "version": migration.version,
            "description": migration.description,
            "applied_at": datetime.utcnow()
        })
    
    async def mark_migration_unapplied(self, version: str):
        """Mark a migration as unapplied (for rollback)"""
        await self.db.migrations.delete_one({"version": version})
    
    async def migrate_up(self, target_version: Optional[str] = None) -> List[str]:
        """Apply migrations up to target version"""
        applied_versions = await self.get_applied_migrations()
        applied_set = set(applied_versions)
        
        migrations_to_apply = []
        for migration in self.migrations:
            if migration.version not in applied_set:
                migrations_to_apply.append(migration)
                if target_version and migration.version == target_version:
                    break
        
        applied = []
        for migration in migrations_to_apply:
            try:
                logger.info(f"Applying migration {migration.version}: {migration.description}")
                await migration.up(self.db)
                await self.mark_migration_applied(migration)
                applied.append(migration.version)
                logger.info(f"Successfully applied migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to apply migration {migration.version}: {e}")
                raise
        
        return applied
    
    async def migrate_down(self, target_version: str) -> List[str]:
        """Rollback migrations down to target version"""
        applied_versions = await self.get_applied_migrations()
        
        # Find migrations to rollback (in reverse order)
        migrations_to_rollback = []
        for version in reversed(applied_versions):
            if version <= target_version:
                break
            # Find the migration object
            migration = next((m for m in self.migrations if m.version == version), None)
            if migration:
                migrations_to_rollback.append(migration)
        
        rolled_back = []
        for migration in migrations_to_rollback:
            try:
                logger.info(f"Rolling back migration {migration.version}: {migration.description}")
                await migration.down(self.db)
                await self.mark_migration_unapplied(migration.version)
                rolled_back.append(migration.version)
                logger.info(f"Successfully rolled back migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to rollback migration {migration.version}: {e}")
                raise
        
        return rolled_back
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        applied_versions = await self.get_applied_migrations()
        applied_set = set(applied_versions)
        
        status = {
            "applied_count": len(applied_versions),
            "total_count": len(self.migrations),
            "pending_count": len(self.migrations) - len(applied_versions),
            "applied_migrations": applied_versions,
            "pending_migrations": [
                m.version for m in self.migrations 
                if m.version not in applied_set
            ]
        }
        
        return status


def create_index_if_not_exists(collection, index_spec, **kwargs):
    """Helper to create index if it doesn't exist"""
    async def _create_index():
        try:
            await collection.create_index(index_spec, **kwargs)
        except Exception as e:
            # Index might already exist
            if "already exists" not in str(e):
                raise
    return _create_index