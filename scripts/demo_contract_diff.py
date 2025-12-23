#!/usr/bin/env python3
"""
Contract Diff Pipeline Demo

Demonstrates the contract diff pipeline by creating a breaking change
and showing how it's detected and classified.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from contract_diff_pipeline import ContractDiffAnalyzer, PolicyEnforcer


def demo_breaking_change():
    """Demonstrate detection of breaking changes."""
    print("🔍 Contract Diff Pipeline Demo")
    print("=" * 50)
    
    # Original API spec
    original_spec = {
        "openapi": "3.0.2",
        "info": {"title": "Demo API", "version": "1.0.0"},
        "paths": {
            "/api/users": {
                "get": {
                    "summary": "List users",
                    "parameters": [
                        {"name": "limit", "in": "query", "required": False}
                    ],
                    "responses": {"200": {"description": "Success"}}
                }
            },
            "/api/posts": {
                "get": {
                    "summary": "List posts",
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
    
    # Modified spec with breaking changes
    modified_spec = {
        "openapi": "3.0.2",
        "info": {"title": "Demo API", "version": "1.1.0"},
        "paths": {
            "/api/users": {
                "get": {
                    "summary": "List users",
                    "parameters": [
                        {"name": "limit", "in": "query", "required": False},
                        {"name": "api_key", "in": "header", "required": True}  # NEW REQUIRED PARAM
                    ],
                    "responses": {"200": {"description": "Success"}}
                }
            }
            # REMOVED /api/posts endpoint
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id", "email", "phone"],  # NEW REQUIRED FIELD
                    "properties": {
                        "id": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"}  # NEW PROPERTY
                        # REMOVED name property
                    }
                }
            }
        }
    }
    
    print("📋 Analyzing contract differences...")
    print()
    
    # Analyze differences
    analyzer = ContractDiffAnalyzer()
    diffs = analyzer.analyze_openapi_diff(original_spec, modified_spec)
    
    # Categorize changes
    breaking_changes = [d for d in diffs if d.change_type.value == "breaking"]
    additive_changes = [d for d in diffs if d.change_type.value == "additive"]
    informational_changes = [d for d in diffs if d.change_type.value == "informational"]
    
    print(f"📊 Summary: {len(diffs)} total changes detected")
    print(f"  ❌ Breaking: {len(breaking_changes)}")
    print(f"  ✅ Additive: {len(additive_changes)}")
    print(f"  ℹ️  Informational: {len(informational_changes)}")
    print()
    
    # Show breaking changes in detail
    if breaking_changes:
        print("❌ BREAKING CHANGES:")
        for i, diff in enumerate(breaking_changes, 1):
            print(f"  {i}. {diff.description}")
            print(f"     Path: {diff.path}")
            print(f"     Details: {diff.details}")
            print()
    
    # Show additive changes
    if additive_changes:
        print("✅ ADDITIVE CHANGES:")
        for i, diff in enumerate(additive_changes, 1):
            print(f"  {i}. {diff.description}")
            print(f"     Path: {diff.path}")
            print()
    
    # Show informational changes
    if informational_changes:
        print("ℹ️  INFORMATIONAL CHANGES:")
        for i, diff in enumerate(informational_changes, 1):
            print(f"  {i}. {diff.description}")
            print(f"     Path: {diff.path}")
            print()
    
    # Test policy enforcement
    print("🛡️  Policy Enforcement:")
    print("-" * 25)
    
    enforcer = PolicyEnforcer()
    
    # Without override
    should_pass, errors = enforcer.enforce(diffs)
    print(f"Without override: {'✅ PASS' if should_pass else '❌ FAIL'}")
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    print()
    
    # With override
    should_pass, errors = enforcer.enforce(diffs, override_token="DEMO_OVERRIDE")
    print(f"With override token: {'✅ PASS' if should_pass else '❌ FAIL'}")
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    print()
    
    # Show policy recommendation
    print("💡 Recommendations:")
    if breaking_changes:
        print("  • Review breaking changes with API consumers")
        print("  • Consider API versioning for backward compatibility")
        print("  • Update documentation and migration guides")
        print("  • Use override token only if changes are intentional")
    else:
        print("  • Changes appear safe to deploy")
    print()
    
    print("✨ Demo completed! The pipeline successfully detected and classified contract changes.")


if __name__ == "__main__":
    demo_breaking_change()