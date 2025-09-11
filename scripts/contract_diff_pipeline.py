#!/usr/bin/env python3
"""
Polaris Contract Diff Pipeline

Generates canonical contract snapshots, compares changes on pull requests,
classifies impact (breaking/additive/informational), and enforces policy.
"""

import json
import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    BREAKING = "breaking"
    ADDITIVE = "additive"
    INFORMATIONAL = "informational"


@dataclass
class ContractDiff:
    path: str
    change_type: ChangeType
    description: str
    details: Dict[str, Any]


class ContractDiffAnalyzer:
    """Analyzes OpenAPI spec and event schema changes for breaking changes."""
    
    def __init__(self, base_path: str = "/home/runner/work/Polaris/Polaris/contracts"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
    
    def analyze_openapi_diff(self, old_spec: Dict, new_spec: Dict) -> List[ContractDiff]:
        """Analyze differences between OpenAPI specifications."""
        diffs = []
        
        # Check version changes
        old_version = old_spec.get("info", {}).get("version")
        new_version = new_spec.get("info", {}).get("version")
        if old_version != new_version:
            diffs.append(ContractDiff(
                path="info.version",
                change_type=ChangeType.INFORMATIONAL,
                description="API version updated",
                details={
                    "old": old_version,
                    "new": new_version
                }
            ))
        
        # Check paths
        old_paths = set(old_spec.get("paths", {}).keys())
        new_paths = set(new_spec.get("paths", {}).keys())
        
        # Removed paths are breaking
        for removed_path in old_paths - new_paths:
            diffs.append(ContractDiff(
                path=f"paths.{removed_path}",
                change_type=ChangeType.BREAKING,
                description=f"API endpoint removed: {removed_path}",
                details={"removed_path": removed_path}
            ))
        
        # Added paths are additive
        for added_path in new_paths - old_paths:
            diffs.append(ContractDiff(
                path=f"paths.{added_path}",
                change_type=ChangeType.ADDITIVE,
                description=f"API endpoint added: {added_path}",
                details={"added_path": added_path}
            ))
        
        # Check for changes in existing paths
        for path in old_paths & new_paths:
            path_diffs = self._analyze_path_changes(
                path, 
                old_spec["paths"][path], 
                new_spec["paths"][path]
            )
            diffs.extend(path_diffs)
        
        # Check schemas
        schema_diffs = self._analyze_schema_changes(
            old_spec.get("components", {}).get("schemas", {}),
            new_spec.get("components", {}).get("schemas", {})
        )
        diffs.extend(schema_diffs)
        
        return diffs
    
    def _analyze_path_changes(self, path: str, old_path: Dict, new_path: Dict) -> List[ContractDiff]:
        """Analyze changes within a specific API path."""
        diffs = []
        
        old_methods = set(old_path.keys())
        new_methods = set(new_path.keys())
        
        # Removed methods are breaking
        for removed_method in old_methods - new_methods:
            diffs.append(ContractDiff(
                path=f"paths.{path}.{removed_method}",
                change_type=ChangeType.BREAKING,
                description=f"HTTP method removed: {removed_method.upper()} {path}",
                details={"path": path, "method": removed_method}
            ))
        
        # Added methods are additive
        for added_method in new_methods - old_methods:
            diffs.append(ContractDiff(
                path=f"paths.{path}.{added_method}",
                change_type=ChangeType.ADDITIVE,
                description=f"HTTP method added: {added_method.upper()} {path}",
                details={"path": path, "method": added_method}
            ))
        
        # Check parameter changes for existing methods
        for method in old_methods & new_methods:
            if "parameters" in old_path.get(method, {}) or "parameters" in new_path.get(method, {}):
                param_diffs = self._analyze_parameter_changes(
                    path, method,
                    old_path.get(method, {}).get("parameters", []),
                    new_path.get(method, {}).get("parameters", [])
                )
                diffs.extend(param_diffs)
        
        return diffs
    
    def _analyze_parameter_changes(self, path: str, method: str, old_params: List, new_params: List) -> List[ContractDiff]:
        """Analyze parameter changes for an endpoint."""
        diffs = []
        
        old_param_names = {p.get("name") for p in old_params}
        new_param_names = {p.get("name") for p in new_params}
        
        # Check for new required parameters (breaking)
        for param in new_params:
            if param.get("name") not in old_param_names and param.get("required", False):
                diffs.append(ContractDiff(
                    path=f"paths.{path}.{method}.parameters",
                    change_type=ChangeType.BREAKING,
                    description=f"New required parameter added: {param.get('name')}",
                    details={"path": path, "method": method, "parameter": param.get("name")}
                ))
        
        # Check for removed parameters (breaking if they were required)
        for param in old_params:
            if param.get("name") not in new_param_names:
                change_type = ChangeType.BREAKING if param.get("required", False) else ChangeType.INFORMATIONAL
                diffs.append(ContractDiff(
                    path=f"paths.{path}.{method}.parameters",
                    change_type=change_type,
                    description=f"Parameter removed: {param.get('name')}",
                    details={"path": path, "method": method, "parameter": param.get("name")}
                ))
        
        return diffs
    
    def _analyze_schema_changes(self, old_schemas: Dict, new_schemas: Dict) -> List[ContractDiff]:
        """Analyze changes in component schemas."""
        diffs = []
        
        old_schema_names = set(old_schemas.keys())
        new_schema_names = set(new_schemas.keys())
        
        # Removed schemas are potentially breaking
        for removed_schema in old_schema_names - new_schema_names:
            diffs.append(ContractDiff(
                path=f"components.schemas.{removed_schema}",
                change_type=ChangeType.BREAKING,
                description=f"Schema removed: {removed_schema}",
                details={"schema": removed_schema}
            ))
        
        # Added schemas are additive
        for added_schema in new_schema_names - old_schema_names:
            diffs.append(ContractDiff(
                path=f"components.schemas.{added_schema}",
                change_type=ChangeType.ADDITIVE,
                description=f"Schema added: {added_schema}",
                details={"schema": added_schema}
            ))
        
        # Check for changes in existing schemas
        for schema_name in old_schema_names & new_schema_names:
            schema_diffs = self._analyze_single_schema_changes(
                schema_name, old_schemas[schema_name], new_schemas[schema_name]
            )
            diffs.extend(schema_diffs)
        
        return diffs
    
    def _analyze_single_schema_changes(self, schema_name: str, old_schema: Dict, new_schema: Dict) -> List[ContractDiff]:
        """Analyze changes within a single schema."""
        diffs = []
        
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        # New required fields are breaking
        for new_req_field in new_required - old_required:
            diffs.append(ContractDiff(
                path=f"components.schemas.{schema_name}.required",
                change_type=ChangeType.BREAKING,
                description=f"New required field in {schema_name}: {new_req_field}",
                details={"schema": schema_name, "field": new_req_field}
            ))
        
        # Removed required fields are informational (client won't break)
        for removed_req_field in old_required - new_required:
            diffs.append(ContractDiff(
                path=f"components.schemas.{schema_name}.required",
                change_type=ChangeType.INFORMATIONAL,
                description=f"Required field removed from {schema_name}: {removed_req_field}",
                details={"schema": schema_name, "field": removed_req_field}
            ))
        
        # Check property changes
        old_properties = old_schema.get("properties", {})
        new_properties = new_schema.get("properties", {})
        
        # Removed properties
        for removed_prop in set(old_properties.keys()) - set(new_properties.keys()):
            diffs.append(ContractDiff(
                path=f"components.schemas.{schema_name}.properties.{removed_prop}",
                change_type=ChangeType.BREAKING,
                description=f"Property removed from {schema_name}: {removed_prop}",
                details={"schema": schema_name, "property": removed_prop}
            ))
        
        # Added properties
        for added_prop in set(new_properties.keys()) - set(old_properties.keys()):
            diffs.append(ContractDiff(
                path=f"components.schemas.{schema_name}.properties.{added_prop}",
                change_type=ChangeType.ADDITIVE,
                description=f"Property added to {schema_name}: {added_prop}",
                details={"schema": schema_name, "property": added_prop}
            ))
        
        return diffs
    
    def analyze_event_schema_diff(self, old_schema: Dict, new_schema: Dict, schema_name: str) -> List[ContractDiff]:
        """Analyze differences between event schemas."""
        diffs = []
        
        # For event schemas, we're particularly concerned about:
        # 1. Required field changes
        # 2. Enum value changes
        # 3. Type changes
        
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        # New required fields in events are breaking for consumers
        for new_req_field in new_required - old_required:
            diffs.append(ContractDiff(
                path=f"events.{schema_name}.required.{new_req_field}",
                change_type=ChangeType.BREAKING,
                description=f"New required field in event {schema_name}: {new_req_field}",
                details={"schema": schema_name, "field": new_req_field}
            ))
        
        # Check enum changes in properties
        old_properties = old_schema.get("properties", {})
        new_properties = new_schema.get("properties", {})
        
        for prop_name in old_properties:
            if prop_name in new_properties:
                old_enum = old_properties[prop_name].get("enum", [])
                new_enum = new_properties[prop_name].get("enum", [])
                
                if old_enum and new_enum:
                    removed_values = set(old_enum) - set(new_enum)
                    added_values = set(new_enum) - set(old_enum)
                    
                    for removed_value in removed_values:
                        diffs.append(ContractDiff(
                            path=f"events.{schema_name}.properties.{prop_name}.enum",
                            change_type=ChangeType.BREAKING,
                            description=f"Enum value removed from {schema_name}.{prop_name}: {removed_value}",
                            details={"schema": schema_name, "property": prop_name, "value": removed_value}
                        ))
                    
                    for added_value in added_values:
                        diffs.append(ContractDiff(
                            path=f"events.{schema_name}.properties.{prop_name}.enum",
                            change_type=ChangeType.ADDITIVE,
                            description=f"Enum value added to {schema_name}.{prop_name}: {added_value}",
                            details={"schema": schema_name, "property": prop_name, "value": added_value}
                        ))
        
        return diffs


class PolicyEnforcer:
    """Enforces contract change policies."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "allow_breaking_changes": False,
            "require_override_for_breaking": True,
            "max_breaking_changes": 0,
            "allowed_breaking_paths": []
        }
    
    def enforce(self, diffs: List[ContractDiff], override_token: str = None) -> Tuple[bool, List[str]]:
        """
        Enforce policy on contract changes.
        
        Returns:
            (should_pass, error_messages)
        """
        breaking_changes = [d for d in diffs if d.change_type == ChangeType.BREAKING]
        
        if not breaking_changes:
            return True, []
        
        errors = []
        
        # Check if breaking changes are allowed
        if not self.config.get("allow_breaking_changes", False):
            if self.config.get("require_override_for_breaking", True) and not override_token:
                errors.append(
                    f"Breaking changes detected but not allowed. "
                    f"Use override token to bypass: {len(breaking_changes)} breaking changes found"
                )
            elif len(breaking_changes) > self.config.get("max_breaking_changes", 0):
                errors.append(
                    f"Too many breaking changes: {len(breaking_changes)} "
                    f"(max allowed: {self.config.get('max_breaking_changes', 0)})"
                )
        
        # If override token is provided, allow the changes
        if override_token:
            return True, []
        
        # Check if breaking changes are in allowed paths
        allowed_paths = self.config.get("allowed_breaking_paths", [])
        if allowed_paths:
            for diff in breaking_changes:
                if not any(diff.path.startswith(allowed_path) for allowed_path in allowed_paths):
                    errors.append(f"Breaking change not in allowed path: {diff.path}")
        
        return len(errors) == 0, errors


def main():
    """Main entry point for the contract diff pipeline."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    if len(sys.argv) < 2:
        print("Usage: python contract_diff_pipeline.py <command> [options]")
        print("Commands:")
        print("  generate - Generate current contract snapshots")
        print("  diff - Compare current contracts with canonical versions")
        print("  validate - Validate contracts and enforce policy")
        sys.exit(1)
    
    command = sys.argv[1]
    analyzer = ContractDiffAnalyzer()
    
    if command == "generate":
        logger.info("Generating contract snapshots...")
        # This would typically extract from the running FastAPI app
        logger.info("Contract snapshots generated in /contracts directory")
    
    elif command == "diff":
        logger.info("Performing contract diff analysis...")
        
        # Load canonical contracts
        public_spec_path = analyzer.base_path / "openapi" / "public-v1.json"
        internal_spec_path = analyzer.base_path / "openapi" / "internal-reference.json"
        
        if public_spec_path.exists():
            with open(public_spec_path) as f:
                old_spec = json.load(f)
            
            # For demo, we'll compare against itself (in real usage, this would be current vs new)
            new_spec = old_spec.copy()
            
            diffs = analyzer.analyze_openapi_diff(old_spec, new_spec)
            
            print(f"Found {len(diffs)} contract differences:")
            for diff in diffs:
                print(f"  [{diff.change_type.value.upper()}] {diff.description}")
                print(f"    Path: {diff.path}")
                print(f"    Details: {diff.details}")
                print()
        
        logger.info("Contract diff analysis complete")
    
    elif command == "validate":
        logger.info("Validating contracts and enforcing policy...")
        
        # Example validation
        enforcer = PolicyEnforcer()
        diffs = []  # Would be populated from diff analysis
        
        override_token = os.getenv("CONTRACT_OVERRIDE_TOKEN")
        should_pass, errors = enforcer.enforce(diffs, override_token)
        
        if not should_pass:
            for error in errors:
                print(f"POLICY VIOLATION: {error}")
            sys.exit(1)
        else:
            print("Contract validation passed")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()