"""
Migration Runner for Polaris Platform
Command-line interface for managing MongoDB migrations
"""
import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_base import MigrationManager
from migrations.001_core_domain_schema import migration_001


async def main():
    """Main migration runner"""
    parser = argparse.ArgumentParser(description="Polaris MongoDB Migration Manager")
    parser.add_argument("command", choices=["status", "migrate", "rollback"], help="Migration command")
    parser.add_argument("--target", help="Target migration version")
    parser.add_argument("--mongo-url", default=os.getenv("MONGO_URL", "mongodb://localhost:27017"), help="MongoDB URL")
    parser.add_argument("--database", default=os.getenv("DB_NAME", "polaris_dev"), help="Database name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Initialize migration manager
    manager = MigrationManager(args.mongo_url, args.database)
    
    # Register all migrations
    manager.register_migration(migration_001)
    
    try:
        await manager.connect()
        logger.info(f"Connected to database: {args.database}")
        
        if args.command == "status":
            await show_status(manager)
        elif args.command == "migrate":
            await migrate_up(manager, args.target)
        elif args.command == "rollback":
            if not args.target:
                logger.error("Target version required for rollback")
                return 1
            await migrate_down(manager, args.target)
        
        return 0
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    finally:
        await manager.disconnect()


async def show_status(manager: MigrationManager):
    """Show migration status"""
    logger = logging.getLogger(__name__)
    
    status = await manager.get_migration_status()
    
    print("\n=== Migration Status ===")
    print(f"Applied migrations: {status['applied_count']}")
    print(f"Total migrations: {status['total_count']}")
    print(f"Pending migrations: {status['pending_count']}")
    
    if status['applied_migrations']:
        print("\nApplied:")
        for version in status['applied_migrations']:
            print(f"  ✓ {version}")
    
    if status['pending_migrations']:
        print("\nPending:")
        for version in status['pending_migrations']:
            print(f"  ○ {version}")
    
    print()


async def migrate_up(manager: MigrationManager, target_version: str = None):
    """Apply migrations"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting migration...")
    applied = await manager.migrate_up(target_version)
    
    if applied:
        logger.info(f"Successfully applied {len(applied)} migrations:")
        for version in applied:
            logger.info(f"  ✓ {version}")
    else:
        logger.info("No migrations to apply")


async def migrate_down(manager: MigrationManager, target_version: str):
    """Rollback migrations"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Rolling back to version {target_version}...")
    rolled_back = await manager.migrate_down(target_version)
    
    if rolled_back:
        logger.info(f"Successfully rolled back {len(rolled_back)} migrations:")
        for version in rolled_back:
            logger.info(f"  ✗ {version}")
    else:
        logger.info("No migrations to rollback")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))