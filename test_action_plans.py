#!/usr/bin/env python3
"""
Test script for Action Plan Versioning & Recommendation Engine
Tests the core functionality without requiring a full server setup
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append('/home/runner/work/Polaris/Polaris/backend')

# Mock the database and external dependencies
class MockDB:
    def __init__(self):
        self.collections = {
            'action_plans': [],
            'plan_series': [],
            'action_plan_diffs': [],
            'domain_events': []
        }
    
    def __getattr__(self, name):
        if name in self.collections:
            return MockCollection(self.collections[name])
        return MockCollection([])

class MockCollection:
    def __init__(self, data):
        self.data = data
    
    async def insert_one(self, doc):
        self.data.append(doc)
        return type('MockResult', (), {'inserted_id': doc['_id']})()
    
    async def find_one(self, query, **kwargs):
        # Simplified find logic for testing
        for item in self.data:
            if self._matches_query(item, query):
                return item
        return None
    
    async def find(self, query, **kwargs):
        return MockCursor([item for item in self.data if self._matches_query(item, query)])
    
    async def update_one(self, query, update, **kwargs):
        for item in self.data:
            if self._matches_query(item, query):
                if '$set' in update:
                    item.update(update['$set'])
                return type('MockResult', (), {'modified_count': 1})()
        return type('MockResult', (), {'modified_count': 0})()
    
    def _matches_query(self, item, query):
        if not query:
            return True
        for key, value in query.items():
            if key == '$or':
                return any(self._matches_query(item, subquery) for subquery in value)
            elif item.get(key) != value:
                return False
        return True

class MockCursor:
    def __init__(self, data):
        self.data = data
    
    def sort(self, field, direction=1):
        if field == 'version':
            self.data.sort(key=lambda x: x.get('version', 0), reverse=(direction == -1))
        elif field == 'created_at':
            self.data.sort(key=lambda x: x.get('created_at', datetime.min), reverse=(direction == -1))
        return self
    
    async def to_list(self, length):
        return self.data[:length]

# Mock the database instance
mock_db = MockDB()

# Mock environment and logging
import logging
logging.basicConfig(level=logging.INFO)

def test_recommendation_provider():
    """Test the rule-based recommendation provider"""
    print("🔍 Testing RuleBasedBaselineRecommendationProvider...")
    
    # Import after mocking
    from server_full import RuleBasedBaselineRecommendationProvider
    
    provider = RuleBasedBaselineRecommendationProvider()
    
    # Test high risk scenario
    high_risk_context = {
        "client_id": "test_client_1",
        "risk_score": 80,
        "readiness_percent": 20,
        "assessment_gaps": ["financial_management", "compliance"],
        "industry": "technology"
    }
    
    proposal = provider.generate_plan(high_risk_context)
    
    assert "goals" in proposal
    assert "interventions" in proposal
    assert "metadata" in proposal
    assert len(proposal["goals"]) > 0
    assert len(proposal["interventions"]) > 0
    
    print(f"✅ High risk scenario generated {len(proposal['goals'])} goals and {len(proposal['interventions'])} interventions")
    
    # Test medium risk scenario
    medium_risk_context = {
        "client_id": "test_client_2",
        "risk_score": 60,
        "readiness_percent": 45,
        "assessment_gaps": ["operations"],
        "industry": "manufacturing"
    }
    
    proposal = provider.generate_plan(medium_risk_context)
    assert len(proposal["goals"]) > 0
    print(f"✅ Medium risk scenario generated {len(proposal['goals'])} goals")
    
    # Test low risk scenario
    low_risk_context = {
        "client_id": "test_client_3", 
        "risk_score": 30,
        "readiness_percent": 80,
        "assessment_gaps": [],
        "industry": "services"
    }
    
    proposal = provider.generate_plan(low_risk_context)
    assert len(proposal["goals"]) > 0
    print(f"✅ Low risk scenario generated {len(proposal['goals'])} goals")

async def test_action_plan_recommender():
    """Test the ActionPlanRecommender service"""
    print("\n🔍 Testing ActionPlanRecommender...")
    
    # Import and patch
    import server_full
    server_full.db = mock_db
    
    from server_full import ActionPlanRecommender, RuleBasedBaselineRecommendationProvider
    
    provider = RuleBasedBaselineRecommendationProvider()
    recommender = ActionPlanRecommender(provider)
    
    # Test recommendation generation
    client_id = "test_client_recommender"
    plan_id = await recommender.generate_recommendation(client_id)
    
    assert plan_id is not None
    print(f"✅ Generated recommendation with plan ID: {plan_id}")
    
    # Verify plan was stored
    plans = mock_db.collections['action_plans']
    assert len(plans) == 1
    plan = plans[0]
    assert plan['client_id'] == client_id
    assert plan['status'] == 'suggested'
    assert plan['version'] == 1
    print(f"✅ Plan stored with status: {plan['status']}, version: {plan['version']}")
    
    # Test second recommendation (should increment version)
    plan_id_2 = await recommender.generate_recommendation(client_id)
    assert len(plans) == 2
    plan_2 = plans[1]
    assert plan_2['version'] == 2
    print(f"✅ Second recommendation incremented version to: {plan_2['version']}")

def test_diff_computation():
    """Test action plan diff computation"""
    print("\n🔍 Testing action plan diff computation...")
    
    # Import after patching
    import server_full
    server_full.db = mock_db
    
    plan_a = {
        "goals": [
            {"id": "goal_1", "title": "Goal 1", "description": "Original goal"},
            {"id": "goal_2", "title": "Goal 2", "description": "Another goal"}
        ],
        "interventions": [
            {"id": "int_1", "goal_id": "goal_1", "title": "Intervention 1", "type": "training"}
        ]
    }
    
    plan_b = {
        "goals": [
            {"id": "goal_1", "title": "Goal 1 Updated", "description": "Modified goal"},  # Changed
            {"id": "goal_3", "title": "Goal 3", "description": "New goal"}  # Added
            # goal_2 removed
        ],
        "interventions": [
            {"id": "int_1", "goal_id": "goal_1", "title": "Intervention 1", "type": "training"},
            {"id": "int_2", "goal_id": "goal_3", "title": "Intervention 2", "type": "process_improvement"}  # Added
        ]
    }
    
    diff = asyncio.run(server_full.compute_action_plan_diff(plan_a, plan_b))
    
    # Verify diff structure
    assert "added" in diff
    assert "removed" in diff
    assert "changed" in diff
    
    # Check specific changes
    assert len(diff["added"]["goals"]) == 1
    assert diff["added"]["goals"][0]["id"] == "goal_3"
    
    assert len(diff["removed"]["goals"]) == 1
    assert diff["removed"]["goals"][0]["id"] == "goal_2"
    
    assert len(diff["changed"]["goals"]) == 1
    assert diff["changed"]["goals"][0]["id"] == "goal_1"
    assert "title" in diff["changed"]["goals"][0]["fields_changed"]
    
    print("✅ Diff computation correctly identified added, removed, and changed elements")

def test_status_enums():
    """Test action plan status enumeration"""
    print("\n🔍 Testing ActionPlanStatus enum...")
    
    import server_full
    from server_full import ActionPlanStatus
    
    assert ActionPlanStatus.draft.value == "draft"
    assert ActionPlanStatus.suggested.value == "suggested"
    assert ActionPlanStatus.active.value == "active"
    assert ActionPlanStatus.archived.value == "archived"
    
    print("✅ All required status values are available")

def test_models():
    """Test Pydantic models"""
    print("\n🔍 Testing Pydantic models...")
    
    import server_full
    from server_full import Goal, Intervention, ActionPlan, ActionPlanStatus
    
    # Test Goal model
    goal = Goal(
        id="test_goal",
        title="Test Goal",
        description="A test goal",
        target_metrics={"completion": 100},
        timeframe="3 months",
        assigned_roles=["client"]
    )
    assert goal.id == "test_goal"
    print("✅ Goal model validation passed")
    
    # Test Intervention model
    intervention = Intervention(
        id="test_intervention",
        goal_id="test_goal",
        title="Test Intervention",
        description="A test intervention",
        type="training",
        resources_required=["time", "materials"],
        estimated_duration="4 weeks"
    )
    assert intervention.goal_id == "test_goal"
    print("✅ Intervention model validation passed")
    
    # Test ActionPlan model
    action_plan = ActionPlan(
        id="test_plan",
        client_id="test_client",
        version=1,
        status=ActionPlanStatus.draft,
        goals=[goal],
        interventions=[intervention],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert len(action_plan.goals) == 1
    print("✅ ActionPlan model validation passed")

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Action Plan Versioning & Recommendation Engine Tests\n")
    
    try:
        test_recommendation_provider()
        await test_action_plan_recommender()
        test_diff_computation()
        test_status_enums()
        test_models()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 Action Plan Versioning & Recommendation Engine implementation is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)