#!/usr/bin/env python3
"""
Seed script for Polaris Platform
Populates the database with minimal sample data for development and testing
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import pbkdf2_sha256
from domain.events import EventDispatcher, UserCreatedEvent, ClientProfileCreatedEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSeeder:
    """Seeds the database with sample data"""
    
    def __init__(self, mongo_url: str, database_name: str):
        self.mongo_url = mongo_url
        self.database_name = database_name
        self.client = None
        self.db = None
        self.event_dispatcher = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.database_name]
        self.event_dispatcher = EventDispatcher(self.db, enable_sync_dispatch=False)
        logger.info(f"Connected to database: {self.database_name}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def seed_all(self):
        """Seed all sample data"""
        logger.info("Starting database seeding...")
        
        # Seed in dependency order
        organizations = await self.seed_organizations()
        users = await self.seed_users(organizations)
        await self.seed_organization_memberships(users, organizations)
        provider_profiles = await self.seed_provider_profiles(organizations)
        client_profiles = await self.seed_client_profiles(organizations, users)
        assessments = await self.seed_assessments(client_profiles, users)
        action_plans = await self.seed_action_plans(client_profiles, users)
        tasks = await self.seed_tasks(action_plans, users)
        await self.seed_outcome_records(client_profiles, tasks, users)
        await self.seed_alerts()
        await self.seed_sla_records(tasks)
        
        logger.info("Database seeding completed successfully!")
        await self.print_summary()
    
    async def seed_organizations(self):
        """Seed sample organizations"""
        logger.info("Seeding organizations...")
        
        organizations = [
            {
                "id": str(uuid.uuid4()),
                "name": "Acme Business Development Agency",
                "org_type": "agency",
                "status": "active",
                "compliance_tier": "tier_3",
                "settings_json": {
                    "max_clients": 1000,
                    "assessment_tiers": [1, 2, 3],
                    "notification_preferences": {
                        "email": True,
                        "sms": False
                    }
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "TechStart Consulting Group",
                "org_type": "provider",
                "status": "active",
                "compliance_tier": "tier_2",
                "settings_json": {
                    "service_areas": ["technology", "finance", "legal"],
                    "capacity": 50
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Small Business Alliance",
                "org_type": "client",
                "status": "active",
                "compliance_tier": "tier_1",
                "settings_json": {
                    "industry": "mixed",
                    "size": "small"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await self.db.organizations.insert_many(organizations)
        logger.info(f"Created {len(organizations)} organizations")
        
        return {org["org_type"]: org for org in organizations}
    
    async def seed_users(self, organizations):
        """Seed sample users"""
        logger.info("Seeding users...")
        
        users = [
            {
                "id": str(uuid.uuid4()),
                "email": "admin@acme-agency.com",
                "name": "Agency Administrator",
                "status": "active",
                "auth_provider_id": None,
                "mfa_enabled": True,
                "last_login_at": datetime.utcnow() - timedelta(hours=2),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "role": "org_admin",
                "organization_type": "agency"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "consultant@techstart.com",
                "name": "Lead Business Consultant",
                "status": "active",
                "auth_provider_id": None,
                "mfa_enabled": False,
                "last_login_at": datetime.utcnow() - timedelta(minutes=30),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "role": "provider_staff",
                "organization_type": "provider"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "manager@techstart.com",
                "name": "Case Manager",
                "status": "active",
                "auth_provider_id": None,
                "mfa_enabled": False,
                "last_login_at": datetime.utcnow() - timedelta(hours=1),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "role": "case_manager",
                "organization_type": "provider"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "owner@smallbiz.com",
                "name": "Jane Smith",
                "status": "active",
                "auth_provider_id": None,
                "mfa_enabled": False,
                "last_login_at": datetime.utcnow() - timedelta(days=2),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "role": "client_user",
                "organization_type": "client"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "system@polaris.platform",
                "name": "System Service Account",
                "status": "active",
                "auth_provider_id": "system",
                "mfa_enabled": False,
                "last_login_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "role": "system_service",
                "organization_type": "system"
            }
        ]
        
        await self.db.users.insert_many(users)
        logger.info(f"Created {len(users)} users")
        
        # Dispatch user created events
        for user in users:
            if user["role"] != "system_service":  # Skip system accounts
                event = UserCreatedEvent(
                    user_id=user["id"],
                    email=user["email"],
                    name=user["name"],
                    role=user["role"]
                )
                await self.event_dispatcher.dispatch(event)
        
        return {user["role"]: user for user in users}
    
    async def seed_organization_memberships(self, users, organizations):
        """Seed organization memberships"""
        logger.info("Seeding organization memberships...")
        
        memberships = [
            {
                "id": str(uuid.uuid4()),
                "user_id": users["org_admin"]["id"],
                "organization_id": organizations["agency"]["id"],
                "roles": ["org_admin", "case_manager"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users["provider_staff"]["id"],
                "organization_id": organizations["provider"]["id"],
                "roles": ["provider_staff"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users["case_manager"]["id"],
                "organization_id": organizations["provider"]["id"],
                "roles": ["case_manager"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users["client_user"]["id"],
                "organization_id": organizations["client"]["id"],
                "roles": ["client_user"],
                "created_at": datetime.utcnow()
            }
        ]
        
        await self.db.organization_memberships.insert_many(memberships)
        logger.info(f"Created {len(memberships)} organization memberships")
    
    async def seed_provider_profiles(self, organizations):
        """Seed provider profiles"""
        logger.info("Seeding provider profiles...")
        
        provider_profiles = [
            {
                "id": str(uuid.uuid4()),
                "organization_id": organizations["provider"]["id"],
                "taxonomy_codes": ["541611", "541618", "541990"],  # Management consulting codes
                "service_regions": ["TX", "CA", "NY"],
                "capacity_metrics_json": {
                    "max_clients": 25,
                    "current_clients": 12,
                    "specializations": ["technology_startups", "financial_planning", "regulatory_compliance"],
                    "certifications": ["NAICS_541611", "MBE", "WBE"]
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await self.db.provider_profiles.insert_many(provider_profiles)
        logger.info(f"Created {len(provider_profiles)} provider profiles")
        
        return provider_profiles
    
    async def seed_client_profiles(self, organizations, users):
        """Seed client profiles"""
        logger.info("Seeding client profiles...")
        
        client_profiles = [
            {
                "id": str(uuid.uuid4()),
                "primary_identifier": "SB-2024-001",
                "user_id": users["client_user"]["id"],
                "organization_id": organizations["client"]["id"],
                "demographics_json": {
                    "business_type": "LLC",
                    "industry": "Technology Services",
                    "employee_count": 5,
                    "annual_revenue": 250000,
                    "founded_year": 2022,
                    "location": {
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78701"
                    }
                },
                "risk_score": 0.65,
                "consent_policies_json": {
                    "data_sharing": True,
                    "marketing_communications": False,
                    "analytics_tracking": True,
                    "third_party_services": True
                },
                "assigned_provider_id": None,
                "cohort_tags": ["tech_startup", "early_stage", "tx_based"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await self.db.client_profiles.insert_many(client_profiles)
        logger.info(f"Created {len(client_profiles)} client profiles")
        
        # Dispatch client profile created events
        for profile in client_profiles:
            event = ClientProfileCreatedEvent(
                client_id=profile["id"],
                organization_id=profile["organization_id"],
                primary_identifier=profile["primary_identifier"],
                user_id=profile["user_id"]
            )
            await self.event_dispatcher.dispatch(event)
        
        return client_profiles
    
    async def seed_assessments(self, client_profiles, users):
        """Seed sample assessments"""
        logger.info("Seeding assessments...")
        
        assessments = [
            {
                "id": str(uuid.uuid4()),
                "client_id": client_profiles[0]["id"],
                "template_version": "v2.1",
                "responses_json": {
                    "area1_score": 75,
                    "area2_score": 60,
                    "area3_score": 80,
                    "responses": [
                        {"question": "Q1", "response": "Yes", "evidence": "Business plan exists"},
                        {"question": "Q2", "response": "Partial", "evidence": "Financial projections for 12 months"},
                        {"question": "Q3", "response": "Yes", "evidence": "Legal structure established"}
                    ]
                },
                "score_vector_json": {
                    "overall_score": 71.7,
                    "readiness_score": 75,
                    "risk_factors": ["limited_financial_history", "new_market_entry"],
                    "strengths": ["strong_technical_team", "clear_value_proposition"]
                },
                "risk_band": "medium",
                "created_by": users["case_manager"]["id"],
                "created_at": datetime.utcnow()
            }
        ]
        
        await self.db.assessments.insert_many(assessments)
        logger.info(f"Created {len(assessments)} assessments")
        
        return assessments
    
    async def seed_action_plans(self, client_profiles, users):
        """Seed sample action plans"""
        logger.info("Seeding action plans...")
        
        action_plans = [
            {
                "id": str(uuid.uuid4()),
                "client_id": client_profiles[0]["id"],
                "version": 1,
                "status": "active",
                "goals_json": {
                    "primary_goals": [
                        "Achieve certification readiness",
                        "Improve financial documentation",
                        "Establish compliance framework"
                    ],
                    "target_completion": "2024-06-30",
                    "success_metrics": [
                        "Complete business plan review",
                        "Implement accounting system",
                        "Obtain required certifications"
                    ]
                },
                "interventions_json": {
                    "recommended_actions": [
                        {
                            "category": "financial",
                            "description": "Implement QuickBooks accounting system",
                            "priority": "high",
                            "estimated_hours": 8
                        },
                        {
                            "category": "compliance",
                            "description": "Complete NAICS code verification",
                            "priority": "medium",
                            "estimated_hours": 4
                        },
                        {
                            "category": "documentation",
                            "description": "Develop standard operating procedures",
                            "priority": "medium",
                            "estimated_hours": 12
                        }
                    ]
                },
                "generated_by_type": "user",
                "generated_by_id": users["case_manager"]["id"],
                "supersedes_id": None,
                "created_at": datetime.utcnow(),
                "published_at": datetime.utcnow(),
                "archived_at": None
            }
        ]
        
        await self.db.action_plans.insert_many(action_plans)
        logger.info(f"Created {len(action_plans)} action plans")
        
        return action_plans
    
    async def seed_tasks(self, action_plans, users):
        """Seed sample tasks"""
        logger.info("Seeding tasks...")
        
        tasks = [
            {
                "id": str(uuid.uuid4()),
                "action_plan_id": action_plans[0]["id"],
                "type": "documentation",
                "title": "Set up QuickBooks accounting system",
                "description": "Install and configure QuickBooks for business accounting, including chart of accounts setup and initial data entry.",
                "state": "in_progress",
                "due_at": datetime.utcnow() + timedelta(days=14),
                "assigned_to": users["client_user"]["id"],
                "priority": "high",
                "automation_trigger_ref": None,
                "sla_deadline_at": datetime.utcnow() + timedelta(days=10),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": None
            },
            {
                "id": str(uuid.uuid4()),
                "action_plan_id": action_plans[0]["id"],
                "type": "compliance",
                "title": "Verify NAICS code classification",
                "description": "Review current NAICS code assignment and ensure it accurately reflects business activities.",
                "state": "new",
                "due_at": datetime.utcnow() + timedelta(days=7),
                "assigned_to": users["case_manager"]["id"],
                "priority": "medium",
                "automation_trigger_ref": None,
                "sla_deadline_at": datetime.utcnow() + timedelta(days=5),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": None
            },
            {
                "id": str(uuid.uuid4()),
                "action_plan_id": action_plans[0]["id"],
                "type": "process",
                "title": "Develop standard operating procedures",
                "description": "Create documented SOPs for key business processes including client onboarding, service delivery, and quality assurance.",
                "state": "new",
                "due_at": datetime.utcnow() + timedelta(days=21),
                "assigned_to": users["provider_staff"]["id"],
                "priority": "medium",
                "automation_trigger_ref": None,
                "sla_deadline_at": datetime.utcnow() + timedelta(days=18),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "completed_at": None
            }
        ]
        
        await self.db.tasks.insert_many(tasks)
        logger.info(f"Created {len(tasks)} tasks")
        
        return tasks
    
    async def seed_outcome_records(self, client_profiles, tasks, users):
        """Seed sample outcome records"""
        logger.info("Seeding outcome records...")
        
        outcome_records = [
            {
                "id": str(uuid.uuid4()),
                "client_id": client_profiles[0]["id"],
                "related_task_id": tasks[0]["id"],
                "metric_type": "progress_milestone",
                "value_json": {
                    "milestone": "accounting_system_research",
                    "completion_percentage": 25,
                    "notes": "Completed research on QuickBooks vs alternatives",
                    "evidence_urls": []
                },
                "evaluator_id": users["case_manager"]["id"],
                "recorded_at": datetime.utcnow() - timedelta(days=2),
                "created_at": datetime.utcnow()
            }
        ]
        
        await self.db.outcome_records.insert_many(outcome_records)
        logger.info(f"Created {len(outcome_records)} outcome records")
    
    async def seed_alerts(self):
        """Seed sample alerts"""
        logger.info("Seeding alerts...")
        
        alerts = [
            {
                "id": str(uuid.uuid4()),
                "entity_type": "task",
                "entity_id": str(uuid.uuid4()),  # Reference to a task
                "category": "sla_warning",
                "severity": "medium",
                "acknowledged_by": None,
                "acknowledged_at": None,
                "created_at": datetime.utcnow() - timedelta(hours=6)
            }
        ]
        
        await self.db.alerts.insert_many(alerts)
        logger.info(f"Created {len(alerts)} alerts")
    
    async def seed_sla_records(self, tasks):
        """Seed sample SLA records"""
        logger.info("Seeding SLA records...")
        
        sla_records = [
            {
                "id": str(uuid.uuid4()),
                "task_id": tasks[0]["id"],
                "service_area": "business_consulting",
                "target_minutes": 1440,  # 24 hours
                "started_at": datetime.utcnow() - timedelta(hours=18),
                "stopped_at": None,
                "breached": False,
                "breach_reason": None
            }
        ]
        
        await self.db.sla_records.insert_many(sla_records)
        logger.info(f"Created {len(sla_records)} SLA records")
    
    async def print_summary(self):
        """Print a summary of seeded data"""
        collections = [
            "organizations", "users", "organization_memberships", "provider_profiles",
            "client_profiles", "assessments", "action_plans", "tasks", 
            "outcome_records", "alerts", "sla_records", "outbox_events"
        ]
        
        print("\n" + "="*50)
        print("DATABASE SEEDING SUMMARY")
        print("="*50)
        
        for collection_name in collections:
            count = await self.db[collection_name].count_documents({})
            print(f"{collection_name:25}: {count:5} documents")
        
        print("="*50)
        print("Sample data created successfully!")
        print("\nNext steps:")
        print("1. Start the application: make run-dev")
        print("2. View health status: make health")
        print("3. Check API docs: http://localhost:8000/docs")
        print("4. View Jaeger traces: http://localhost:16686")
        print("="*50)


async def main():
    """Main seeding function"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DB_NAME", "polaris_dev")
    
    seeder = DataSeeder(mongo_url, database_name)
    
    try:
        await seeder.connect()
        await seeder.seed_all()
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await seeder.disconnect()


if __name__ == "__main__":
    asyncio.run(main())