#!/usr/bin/env python3
"""
Setup QA Users for Backend Smoke Testing
Creates the required QA test users directly in the database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import datetime

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'polaris')

async def setup_qa_users():
    """Create QA users for testing"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # QA users to create
    qa_users = [
        {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!", "role": "client"},
        {"email": "provider.qa@polaris.example.com", "password": "Polaris#2025!", "role": "provider"},
        {"email": "navigator.qa@polaris.example.com", "password": "Polaris#2025!", "role": "navigator"},
        {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!", "role": "agency"}
    ]
    
    created_count = 0
    
    for user_data in qa_users:
        # Check if user already exists
        existing = await db.users.find_one({"email": user_data["email"].lower()})
        
        if not existing:
            # Create new user
            uid = str(uuid.uuid4())
            user_doc = {
                "_id": uid,
                "id": uid,
                "email": user_data["email"].lower(),
                "hashed_password": pbkdf2_sha256.hash(user_data["password"]),
                "role": user_data["role"],
                "approval_status": "approved",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "profile_complete": True
            }
            
            await db.users.insert_one(user_doc)
            print(f"✅ Created QA user: {user_data['email']} ({user_data['role']})")
            created_count += 1
        else:
            print(f"ℹ️  QA user already exists: {user_data['email']} ({user_data['role']})")
    
    # Create default tier configuration for QA testing
    default_config = await db.agency_tier_configurations.find_one({"agency_id": "default"})
    if not default_config:
        tier_config = {
            "_id": str(uuid.uuid4()),
            "agency_id": "default",
            "tier_access_levels": {f"area{i}": 3 for i in range(1, 11)},  # Tier 3 access for all areas
            "pricing_per_tier": {"tier1": 25.0, "tier2": 50.0, "tier3": 100.0},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.agency_tier_configurations.insert_one(tier_config)
        print("✅ Created default tier configuration for QA testing")
    
    print(f"\n🎯 QA Setup Complete: {created_count} new users created")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_qa_users())