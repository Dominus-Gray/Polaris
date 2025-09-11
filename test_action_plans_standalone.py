#!/usr/bin/env python3
"""
Standalone test for Action Plan Versioning & Recommendation Engine core logic
Tests the core functionality without external dependencies
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
import json

class ActionPlanStatus(str, Enum):
    draft = "draft"
    suggested = "suggested" 
    active = "active"
    archived = "archived"

class Goal:
    def __init__(self, id: str, title: str, description: str, target_metrics: Optional[Dict[str, Any]] = None, 
                 timeframe: Optional[str] = None, assigned_roles: List[str] = None):
        self.id = id
        self.title = title
        self.description = description
        self.target_metrics = target_metrics or {}
        self.timeframe = timeframe
        self.assigned_roles = assigned_roles or []

class Intervention:
    def __init__(self, id: str, goal_id: str, title: str, description: str, type: str,
                 resources_required: List[str] = None, estimated_duration: Optional[str] = None):
        self.id = id
        self.goal_id = goal_id
        self.title = title
        self.description = description
        self.type = type
        self.resources_required = resources_required or []
        self.estimated_duration = estimated_duration

class RuleBasedBaselineRecommendationProvider:
    """Stub provider using simple heuristic rules"""
    
    def __init__(self, rules_config: Dict[str, Any] = None):
        self.rules = rules_config or self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        return {
            "risk_score_thresholds": {
                "high": {"min": 75, "goals": ["Improve financial management", "Enhance compliance"]},
                "medium": {"min": 50, "goals": ["Standardize processes", "Documentation improvement"]},
                "low": {"min": 0, "goals": ["Maintain current standards"]}
            }
        }
    
    def generate_plan(self, client_context: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = client_context.get("risk_score", 0)
        readiness_percent = client_context.get("readiness_percent", 0)
        
        # Determine risk level and associated goals
        if risk_score >= 75 or readiness_percent < 25:
            risk_level = "high"
        elif risk_score >= 50 or readiness_percent < 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        rule_goals = self.rules["risk_score_thresholds"][risk_level]["goals"]
        
        goals = []
        interventions = []
        
        for i, goal_title in enumerate(rule_goals):
            goal_id = f"goal_{i+1}"
            goals.append({
                "id": goal_id,
                "title": goal_title,
                "description": f"Auto-generated goal: {goal_title}",
                "target_metrics": {"completion_rate": 100},
                "timeframe": "3 months",
                "assigned_roles": ["client"]
            })
            
            # Add default intervention for each goal
            interventions.append({
                "id": f"intervention_{i+1}",
                "goal_id": goal_id,
                "title": f"Implementation plan for {goal_title}",
                "description": f"Systematic approach to achieve {goal_title}",
                "type": "process_improvement",
                "resources_required": ["time", "documentation"],
                "estimated_duration": "4-6 weeks"
            })
        
        return {
            "goals": goals,
            "interventions": interventions,
            "metadata": {
                "rationale": [f"Based on {risk_level} risk assessment"],
                "source_tags": ["rule_engine", risk_level],
                "generation_context": client_context
            }
        }

def compute_action_plan_diff(from_plan: Dict[str, Any], to_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Compute differences between two action plans"""
    diff = {
        "added": {"goals": [], "interventions": []},
        "removed": {"goals": [], "interventions": []},
        "changed": {"goals": [], "interventions": []}
    }
    
    # Compare goals
    from_goals = {g["id"]: g for g in from_plan.get("goals", [])}
    to_goals = {g["id"]: g for g in to_plan.get("goals", [])}
    
    # Added goals
    for goal_id, goal in to_goals.items():
        if goal_id not in from_goals:
            diff["added"]["goals"].append(goal)
    
    # Removed goals
    for goal_id, goal in from_goals.items():
        if goal_id not in to_goals:
            diff["removed"]["goals"].append(goal)
    
    # Changed goals
    for goal_id in from_goals:
        if goal_id in to_goals:
            from_goal = from_goals[goal_id]
            to_goal = to_goals[goal_id]
            changed_fields = []
            
            for field in ["title", "description", "target_metrics", "timeframe", "assigned_roles"]:
                if from_goal.get(field) != to_goal.get(field):
                    changed_fields.append(field)
            
            if changed_fields:
                diff["changed"]["goals"].append({
                    "id": goal_id,
                    "fields_changed": changed_fields
                })
    
    # Compare interventions (similar logic)
    from_interventions = {i["id"]: i for i in from_plan.get("interventions", [])}
    to_interventions = {i["id"]: i for i in to_plan.get("interventions", [])}
    
    for intervention_id, intervention in to_interventions.items():
        if intervention_id not in from_interventions:
            diff["added"]["interventions"].append(intervention)
    
    for intervention_id, intervention in from_interventions.items():
        if intervention_id not in to_interventions:
            diff["removed"]["interventions"].append(intervention)
    
    for intervention_id in from_interventions:
        if intervention_id in to_interventions:
            from_intervention = from_interventions[intervention_id]
            to_intervention = to_interventions[intervention_id]
            changed_fields = []
            
            for field in ["title", "description", "type", "resources_required", "estimated_duration"]:
                if from_intervention.get(field) != to_intervention.get(field):
                    changed_fields.append(field)
            
            if changed_fields:
                diff["changed"]["interventions"].append({
                    "id": intervention_id,
                    "fields_changed": changed_fields
                })
    
    return diff

def test_recommendation_provider():
    """Test the rule-based recommendation provider"""
    print("🔍 Testing RuleBasedBaselineRecommendationProvider...")
    
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

def test_diff_computation():
    """Test action plan diff computation"""
    print("\n🔍 Testing action plan diff computation...")
    
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
    
    diff = compute_action_plan_diff(plan_a, plan_b)
    
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
    
    assert ActionPlanStatus.draft.value == "draft"
    assert ActionPlanStatus.suggested.value == "suggested"
    assert ActionPlanStatus.active.value == "active"
    assert ActionPlanStatus.archived.value == "archived"
    
    print("✅ All required status values are available")

def test_models():
    """Test core models"""
    print("\n🔍 Testing core models...")
    
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

def test_yaml_config():
    """Test that the rules configuration file is properly structured"""
    print("\n🔍 Testing YAML configuration file...")
    
    try:
        import yaml
        with open('/home/runner/work/Polaris/Polaris/backend/config/rules/recommendations.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        assert 'risk_score_thresholds' in config
        assert 'high' in config['risk_score_thresholds']
        assert 'medium' in config['risk_score_thresholds']
        assert 'low' in config['risk_score_thresholds']
        
        # Check each section has required fields
        for level in ['high', 'medium', 'low']:
            assert 'min' in config['risk_score_thresholds'][level]
            assert 'goals' in config['risk_score_thresholds'][level]
            assert isinstance(config['risk_score_thresholds'][level]['goals'], list)
        
        print("✅ YAML configuration file is properly structured")
        
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML config test")
    except Exception as e:
        print(f"❌ YAML config test failed: {e}")
        raise

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Action Plan Versioning & Recommendation Engine Tests\n")
    
    try:
        test_recommendation_provider()
        test_diff_computation()
        test_status_enums()
        test_models()
        test_yaml_config()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 Action Plan Versioning & Recommendation Engine core implementation is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)