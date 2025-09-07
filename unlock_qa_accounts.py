#!/usr/bin/env python3
"""
Unlock QA accounts that were locked during security testing
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def unlock_qa_accounts():
    """Unlock QA test accounts"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.polaris
    
    qa_emails = [
        "client.qa@polaris.example.com",
        "agency.qa@polaris.example.com", 
        "provider.qa@polaris.example.com",
        "navigator.qa@polaris.example.com"
    ]
    
    print("🔓 Unlocking QA accounts...")
    
    for email in qa_emails:
        result = await db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "locked_until": None,
                    "last_unlock": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Unlocked: {email}")
        else:
            user = await db.users.find_one({"email": email})
            if user:
                print(f"⚠️  Already unlocked: {email}")
            else:
                print(f"❌ Not found: {email}")
    
    print("\n🔓 QA account unlock completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(unlock_qa_accounts())