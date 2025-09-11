"""
Database Migration Script for API Hardening
Creates the api_tokens and idempotency_records collections with proper indexes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def create_api_hardening_collections():
    """Create collections and indexes for API hardening features"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'polaris_db')]
    
    print("Creating API hardening collections and indexes...")
    
    # ========================================
    # API Tokens Collection
    # ========================================
    print("\n📋 Setting up api_tokens collection...")
    
    # Index on token_prefix for fast token lookups
    await db.api_tokens.create_index("token_prefix", unique=True)
    print("✅ Created unique index on token_prefix")
    
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
    
    # ========================================
    # Idempotency Records Collection
    # ========================================
    print("\n🔄 Setting up idempotency_records collection...")
    
    # Compound index for idempotency key lookups
    await db.idempotency_records.create_index([
        ("key", 1),
        ("user_id", 1),
        ("endpoint", 1),
        ("method", 1)
    ], unique=True)
    print("✅ Created compound unique index for idempotency lookups")
    
    # TTL index for automatic cleanup of expired records
    await db.idempotency_records.create_index("expires_at", expireAfterSeconds=0)
    print("✅ Created TTL index on expires_at for automatic cleanup")
    
    # Index on user_id for user-specific queries
    await db.idempotency_records.create_index("user_id")
    print("✅ Created index on user_id")
    
    # ========================================
    # Enhanced User Collection Indexes
    # ========================================
    print("\n👥 Enhancing users collection indexes...")
    
    # Text index for user search functionality
    try:
        await db.users.create_index([
            ("email", "text"),
            ("name", "text")
        ], name="user_text_search")
        print("✅ Created text search index on users")
    except Exception as e:
        print(f"⚠️  Text index creation skipped (may already exist): {e}")
    
    # Index on role for role-based queries
    await db.users.create_index("role")
    print("✅ Created index on user role")
    
    # ========================================
    # Service Requests Collection Enhancements
    # ========================================
    print("\n📋 Enhancing service_requests collection...")
    
    # Compound index for efficient filtering
    await db.service_requests.create_index([
        ("client_id", 1),
        ("status", 1),
        ("created_at", -1)
    ])
    print("✅ Created compound index for service request filtering")
    
    # Text search index
    try:
        await db.service_requests.create_index([
            ("title", "text"),
            ("description", "text")
        ], name="service_request_text_search")
        print("✅ Created text search index on service requests")
    except Exception as e:
        print(f"⚠️  Text index creation skipped: {e}")
    
    # ========================================
    # Audit Log Collection
    # ========================================
    print("\n📊 Setting up audit_logs collection...")
    
    # Index on user_id and timestamp for audit queries
    await db.audit_logs.create_index([
        ("user_id", 1),
        ("timestamp", -1)
    ])
    print("✅ Created compound index for audit log queries")
    
    # Index on event_type for filtering
    await db.audit_logs.create_index("event_type")
    print("✅ Created index on event_type")
    
    # TTL index for audit log retention (7 years for compliance)
    await db.audit_logs.create_index("timestamp", expireAfterSeconds=220752000)  # 7 years
    print("✅ Created TTL index for audit log retention")
    
    print("\n🎉 API hardening collections setup complete!")
    print("=" * 50)
    print("Collections created/enhanced:")
    print("- api_tokens (API token management)")
    print("- idempotency_records (request idempotency)")
    print("- users (enhanced search and filtering)")
    print("- service_requests (enhanced search and filtering)")
    print("- audit_logs (security and compliance)")
    print("=" * 50)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_api_hardening_collections())