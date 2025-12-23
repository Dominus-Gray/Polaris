#!/usr/bin/env python3
"""
Tests for the Contract Diff Pipeline

Basic validation tests for the contract diff functionality.
"""

import json
import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from contract_diff_pipeline import ContractDiffAnalyzer, PolicyEnforcer, ChangeType


class TestContractDiffAnalyzer(unittest.TestCase):
    """Test the contract diff analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContractDiffAnalyzer()
        
        self.base_spec = {
            "openapi": "3.0.2",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/api/users": {
                    "get": {
                        "summary": "List users",
                        "parameters": [
                            {"name": "limit", "in": "query", "required": False}
                        ],
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["id", "email"],
                        "properties": {
                            "id": {"type": "string"},
                            "email": {"type": "string"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def test_no_changes(self):
        """Test that identical specs produce no diffs."""
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, self.base_spec)
        self.assertEqual(len(diffs), 0)
    
    def test_version_change(self):
        """Test version change detection."""
        new_spec = self.base_spec.copy()
        new_spec["info"] = self.base_spec["info"].copy()
        new_spec["info"]["version"] = "1.1.0"
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        version_diffs = [d for d in diffs if d.path == "info.version"]
        self.assertEqual(len(version_diffs), 1)
        self.assertEqual(version_diffs[0].change_type, ChangeType.INFORMATIONAL)
    
    def test_path_removal_is_breaking(self):
        """Test that removing a path is classified as breaking."""
        new_spec = self.base_spec.copy()
        new_spec["paths"] = {}
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        self.assertTrue(len(breaking_diffs) > 0)
        
        path_removals = [d for d in breaking_diffs if "removed" in d.description.lower()]
        self.assertTrue(len(path_removals) > 0)
    
    def test_path_addition_is_additive(self):
        """Test that adding a path is classified as additive."""
        import copy
        new_spec = copy.deepcopy(self.base_spec)
        new_spec["paths"]["/api/posts"] = {
            "get": {
                "summary": "List posts",
                "responses": {"200": {"description": "Success"}}
            }
        }
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        additive_diffs = [d for d in diffs if d.change_type == ChangeType.ADDITIVE]
        self.assertTrue(len(additive_diffs) > 0)
        
        path_additions = [d for d in additive_diffs if "added" in d.description.lower()]
        self.assertTrue(len(path_additions) > 0)
    
    def test_new_required_parameter_is_breaking(self):
        """Test that adding a required parameter is breaking."""
        import copy
        new_spec = copy.deepcopy(self.base_spec)
        new_spec["paths"]["/api/users"]["get"]["parameters"].append({
            "name": "api_key",
            "in": "header",
            "required": True
        })
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        param_diffs = [d for d in breaking_diffs if "parameter" in d.description.lower()]
        self.assertTrue(len(param_diffs) > 0)
    
    def test_new_required_field_in_schema_is_breaking(self):
        """Test that adding a required field to a schema is breaking."""
        import copy
        new_spec = copy.deepcopy(self.base_spec)
        new_spec["components"]["schemas"]["User"]["required"].append("phone")
        new_spec["components"]["schemas"]["User"]["properties"]["phone"] = {"type": "string"}
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        required_diffs = [d for d in breaking_diffs if "required field" in d.description.lower()]
        self.assertTrue(len(required_diffs) > 0)
    
    def test_removed_property_is_breaking(self):
        """Test that removing a property from a schema is breaking."""
        import copy
        new_spec = copy.deepcopy(self.base_spec)
        del new_spec["components"]["schemas"]["User"]["properties"]["name"]
        
        diffs = self.analyzer.analyze_openapi_diff(self.base_spec, new_spec)
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        property_diffs = [d for d in breaking_diffs if "property removed" in d.description.lower()]
        self.assertTrue(len(property_diffs) > 0)


class TestEventSchemaDiff(unittest.TestCase):
    """Test event schema diff analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContractDiffAnalyzer()
        
        self.base_event_schema = {
            "type": "object",
            "required": ["id", "type", "timestamp"],
            "properties": {
                "id": {"type": "string"},
                "type": {
                    "type": "string", 
                    "enum": ["user.created", "user.updated"]
                },
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {"type": "object"}
            }
        }
    
    def test_new_required_field_in_event_is_breaking(self):
        """Test that adding required fields to events is breaking."""
        import copy
        new_schema = copy.deepcopy(self.base_event_schema)
        new_schema["required"].append("signature")
        new_schema["properties"]["signature"] = {"type": "string"}
        
        diffs = self.analyzer.analyze_event_schema_diff(
            self.base_event_schema, new_schema, "webhook-event"
        )
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        self.assertTrue(len(breaking_diffs) > 0)
    
    def test_enum_value_removal_is_breaking(self):
        """Test that removing enum values is breaking."""
        import copy
        new_schema = copy.deepcopy(self.base_event_schema)
        new_schema["properties"]["type"]["enum"] = ["user.created"]  # Removed user.updated
        
        diffs = self.analyzer.analyze_event_schema_diff(
            self.base_event_schema, new_schema, "webhook-event"
        )
        
        breaking_diffs = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        enum_diffs = [d for d in breaking_diffs if "enum value removed" in d.description.lower()]
        self.assertTrue(len(enum_diffs) > 0)
    
    def test_enum_value_addition_is_additive(self):
        """Test that adding enum values is additive."""
        import copy
        new_schema = copy.deepcopy(self.base_event_schema)
        new_schema["properties"]["type"]["enum"].append("user.deleted")
        
        diffs = self.analyzer.analyze_event_schema_diff(
            self.base_event_schema, new_schema, "webhook-event"
        )
        
        additive_diffs = [d for d in diffs if d.change_type == ChangeType.ADDITIVE]
        enum_diffs = [d for d in additive_diffs if "enum value added" in d.description.lower()]
        self.assertTrue(len(enum_diffs) > 0)


class TestPolicyEnforcer(unittest.TestCase):
    """Test policy enforcement."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enforcer = PolicyEnforcer()
    
    def test_no_breaking_changes_passes(self):
        """Test that no breaking changes allows passing."""
        diffs = [
            type('MockDiff', (), {
                'change_type': ChangeType.ADDITIVE,
                'path': 'test.path'
            })()
        ]
        
        should_pass, errors = self.enforcer.enforce(diffs)
        self.assertTrue(should_pass)
        self.assertEqual(len(errors), 0)
    
    def test_breaking_changes_without_override_fails(self):
        """Test that breaking changes without override fail."""
        diffs = [
            type('MockDiff', (), {
                'change_type': ChangeType.BREAKING,
                'path': 'test.path'
            })()
        ]
        
        should_pass, errors = self.enforcer.enforce(diffs)
        self.assertFalse(should_pass)
        self.assertTrue(len(errors) > 0)
    
    def test_breaking_changes_with_override_passes(self):
        """Test that breaking changes with override pass."""
        diffs = [
            type('MockDiff', (), {
                'change_type': ChangeType.BREAKING,
                'path': 'test.path'
            })()
        ]
        
        should_pass, errors = self.enforcer.enforce(diffs, override_token="OVERRIDE-123")
        # Note: In this basic test, we accept any non-empty override token
        # In real implementation, you'd validate the token
        self.assertTrue(should_pass)
        self.assertEqual(len(errors), 0)
    
    def test_policy_with_allowed_breaking_changes(self):
        """Test policy that allows breaking changes."""
        config = {"allow_breaking_changes": True}
        enforcer = PolicyEnforcer(config)
        
        diffs = [
            type('MockDiff', (), {
                'change_type': ChangeType.BREAKING,
                'path': 'test.path'
            })()
        ]
        
        should_pass, errors = enforcer.enforce(diffs)
        self.assertTrue(should_pass)
        self.assertEqual(len(errors), 0)


class TestContractFiles(unittest.TestCase):
    """Test that contract files are valid JSON."""
    
    def test_public_openapi_spec_is_valid_json(self):
        """Test that the public OpenAPI spec is valid JSON."""
        spec_path = Path(__file__).parent.parent / "contracts" / "openapi" / "public-v1.json"
        if spec_path.exists():
            with open(spec_path) as f:
                try:
                    spec = json.load(f)
                    self.assertIn("openapi", spec)
                    self.assertIn("info", spec)
                    self.assertIn("paths", spec)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in public OpenAPI spec: {e}")
    
    def test_internal_openapi_spec_is_valid_json(self):
        """Test that the internal OpenAPI spec is valid JSON."""
        spec_path = Path(__file__).parent.parent / "contracts" / "openapi" / "internal-reference.json"
        if spec_path.exists():
            with open(spec_path) as f:
                try:
                    spec = json.load(f)
                    self.assertIn("openapi", spec)
                    self.assertIn("info", spec)
                    self.assertIn("paths", spec)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in internal OpenAPI spec: {e}")
    
    def test_event_schemas_are_valid_json(self):
        """Test that event schemas are valid JSON."""
        events_dir = Path(__file__).parent.parent / "contracts" / "events"
        if events_dir.exists():
            for schema_file in events_dir.glob("*.schema.json"):
                with open(schema_file) as f:
                    try:
                        schema = json.load(f)
                        self.assertIn("$schema", schema)
                        self.assertIn("type", schema)
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in event schema {schema_file.name}: {e}")


if __name__ == "__main__":
    unittest.main()