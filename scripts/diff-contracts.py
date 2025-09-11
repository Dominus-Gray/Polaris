#!/usr/bin/env python3
"""
OpenAPI Contract Diff Engine for Polaris Platform

This script compares two OpenAPI specifications and analyzes the differences,
classifying changes as breaking, additive, or informational for contract
diff pipeline enforcement.

Usage:
    python scripts/diff-contracts.py [--old-spec PATH] [--new-spec PATH] [--format FORMAT]

Options:
    --old-spec      Path to the old/baseline OpenAPI specification 
    --new-spec      Path to the new/current OpenAPI specification
    --format        Output format: json, yaml, or text (default: text)
    --output        Output file path (default: stdout)
    --strict        Use strict mode for breaking change detection
    --help          Show this help message

Examples:
    # Compare current against committed spec
    python scripts/diff-contracts.py --old-spec contracts/openapi/public-v1.json --new-spec /tmp/current-spec.json

    # Generate JSON diff report
    python scripts/diff-contracts.py --old contracts/openapi/public-v1.json --new /tmp/current.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict


class ChangeType(Enum):
    """Classification of API changes"""
    BREAKING = "breaking"
    ADDITIVE = "additive" 
    INFORMATIONAL = "informational"
    DEPRECATED = "deprecated"


@dataclass
class ChangeItem:
    """Represents a single change in the API specification"""
    type: ChangeType
    category: str  # e.g., "path", "parameter", "response", "schema"
    location: str  # e.g., "/api/users", "POST /api/users.parameters[0]"
    description: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    severity: str = "medium"  # low, medium, high, critical


@dataclass 
class DiffReport:
    """Complete diff report between two API specifications"""
    summary: Dict[str, int]
    changes: List[ChangeItem]
    breaking_changes: List[ChangeItem]
    additive_changes: List[ChangeItem]
    informational_changes: List[ChangeItem]
    metadata: Dict[str, Any]


class OpenAPIDiffer:
    """OpenAPI specification differ with breaking change detection"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        
    def diff_specs(self, old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> DiffReport:
        """Compare two OpenAPI specifications and generate a diff report"""
        changes: List[ChangeItem] = []
        
        # Compare paths
        changes.extend(self._diff_paths(old_spec.get('paths', {}), new_spec.get('paths', {})))
        
        # Compare info
        changes.extend(self._diff_info(old_spec.get('info', {}), new_spec.get('info', {})))
        
        # Compare servers
        changes.extend(self._diff_servers(old_spec.get('servers', []), new_spec.get('servers', [])))
        
        # Compare components/schemas
        old_components = old_spec.get('components', {})
        new_components = new_spec.get('components', {})
        changes.extend(self._diff_components(old_components, new_components))
        
        # Categorize changes
        breaking_changes = [c for c in changes if c.type == ChangeType.BREAKING]
        additive_changes = [c for c in changes if c.type == ChangeType.ADDITIVE]
        informational_changes = [c for c in changes if c.type == ChangeType.INFORMATIONAL]
        
        # Generate summary
        summary = {
            "total_changes": len(changes),
            "breaking_changes": len(breaking_changes),
            "additive_changes": len(additive_changes),
            "informational_changes": len(informational_changes),
            "deprecated_changes": len([c for c in changes if c.type == ChangeType.DEPRECATED])
        }
        
        # Metadata
        metadata = {
            "compared_at": datetime.utcnow().isoformat() + 'Z',
            "old_spec_version": old_spec.get('info', {}).get('version', 'unknown'),
            "new_spec_version": new_spec.get('info', {}).get('version', 'unknown'),
            "strict_mode": self.strict_mode,
            "differ_version": "1.0.0"
        }
        
        return DiffReport(
            summary=summary,
            changes=changes,
            breaking_changes=breaking_changes,
            additive_changes=additive_changes,
            informational_changes=informational_changes,
            metadata=metadata
        )
    
    def _diff_paths(self, old_paths: Dict[str, Any], new_paths: Dict[str, Any]) -> List[ChangeItem]:
        """Compare paths sections of OpenAPI specs"""
        changes = []
        
        old_path_set = set(old_paths.keys())
        new_path_set = set(new_paths.keys())
        
        # Removed paths (breaking)
        for path in old_path_set - new_path_set:
            changes.append(ChangeItem(
                type=ChangeType.BREAKING,
                category="path",
                location=path,
                description=f"Path '{path}' was removed",
                severity="high",
                old_value=path
            ))
        
        # Added paths (additive)
        for path in new_path_set - old_path_set:
            changes.append(ChangeItem(
                type=ChangeType.ADDITIVE,
                category="path",
                location=path,
                description=f"Path '{path}' was added",
                severity="low",
                new_value=path
            ))
        
        # Modified paths
        for path in old_path_set & new_path_set:
            path_changes = self._diff_path_methods(path, old_paths[path], new_paths[path])
            changes.extend(path_changes)
        
        return changes
    
    def _diff_path_methods(self, path: str, old_methods: Dict[str, Any], new_methods: Dict[str, Any]) -> List[ChangeItem]:
        """Compare HTTP methods for a specific path"""
        changes = []
        
        old_method_set = set(old_methods.keys())
        new_method_set = set(new_methods.keys())
        
        # Removed methods (breaking)
        for method in old_method_set - new_method_set:
            changes.append(ChangeItem(
                type=ChangeType.BREAKING,
                category="method",
                location=f"{method.upper()} {path}",
                description=f"Method '{method.upper()}' was removed from '{path}'",
                severity="high",
                old_value=method
            ))
        
        # Added methods (additive)
        for method in new_method_set - old_method_set:
            changes.append(ChangeItem(
                type=ChangeType.ADDITIVE,
                category="method",
                location=f"{method.upper()} {path}",
                description=f"Method '{method.upper()}' was added to '{path}'",
                severity="low",
                new_value=method
            ))
        
        # Modified methods
        for method in old_method_set & new_method_set:
            method_changes = self._diff_method_details(path, method, old_methods[method], new_methods[method])
            changes.extend(method_changes)
        
        return changes
    
    def _diff_method_details(self, path: str, method: str, old_method: Dict[str, Any], new_method: Dict[str, Any]) -> List[ChangeItem]:
        """Compare details of a specific HTTP method"""
        changes = []
        location_prefix = f"{method.upper()} {path}"
        
        # Compare parameters
        old_params = old_method.get('parameters', [])
        new_params = new_method.get('parameters', [])
        changes.extend(self._diff_parameters(location_prefix, old_params, new_params))
        
        # Compare request body
        old_body = old_method.get('requestBody')
        new_body = new_method.get('requestBody')
        changes.extend(self._diff_request_body(location_prefix, old_body, new_body))
        
        # Compare responses
        old_responses = old_method.get('responses', {})
        new_responses = new_method.get('responses', {})
        changes.extend(self._diff_responses(location_prefix, old_responses, new_responses))
        
        # Compare operation ID changes (informational)
        old_op_id = old_method.get('operationId')
        new_op_id = new_method.get('operationId')
        if old_op_id != new_op_id:
            changes.append(ChangeItem(
                type=ChangeType.INFORMATIONAL,
                category="operation",
                location=f"{location_prefix}.operationId",
                description=f"Operation ID changed from '{old_op_id}' to '{new_op_id}'",
                old_value=old_op_id,
                new_value=new_op_id
            ))
        
        return changes
    
    def _diff_parameters(self, location_prefix: str, old_params: List[Dict], new_params: List[Dict]) -> List[ChangeItem]:
        """Compare parameters between method versions"""
        changes = []
        
        # Create lookup by name and location
        old_param_map = {f"{p.get('name', '')}:{p.get('in', '')}": p for p in old_params}
        new_param_map = {f"{p.get('name', '')}:{p.get('in', '')}": p for p in new_params}
        
        old_keys = set(old_param_map.keys())
        new_keys = set(new_param_map.keys())
        
        # Removed parameters
        for key in old_keys - new_keys:
            param = old_param_map[key]
            severity = "high" if param.get('required', False) else "medium"
            change_type = ChangeType.BREAKING if param.get('required', False) else ChangeType.INFORMATIONAL
            
            changes.append(ChangeItem(
                type=change_type,
                category="parameter",
                location=f"{location_prefix}.parameters[{param.get('name')}]",
                description=f"Parameter '{param.get('name')}' was removed",
                severity=severity,
                old_value=param
            ))
        
        # Added parameters
        for key in new_keys - old_keys:
            param = new_param_map[key]
            severity = "medium" if param.get('required', False) else "low"
            change_type = ChangeType.BREAKING if param.get('required', False) else ChangeType.ADDITIVE
            
            changes.append(ChangeItem(
                type=change_type,
                category="parameter",
                location=f"{location_prefix}.parameters[{param.get('name')}]",
                description=f"Parameter '{param.get('name')}' was added{' (required)' if param.get('required') else ''}",
                severity=severity,
                new_value=param
            ))
        
        # Modified parameters
        for key in old_keys & new_keys:
            old_param = old_param_map[key]
            new_param = new_param_map[key]
            
            # Check required status change
            old_required = old_param.get('required', False)
            new_required = new_param.get('required', False)
            
            if old_required != new_required:
                if new_required:  # Became required - breaking
                    changes.append(ChangeItem(
                        type=ChangeType.BREAKING,
                        category="parameter",
                        location=f"{location_prefix}.parameters[{old_param.get('name')}].required",
                        description=f"Parameter '{old_param.get('name')}' is now required",
                        severity="high",
                        old_value=old_required,
                        new_value=new_required
                    ))
                else:  # Became optional - additive
                    changes.append(ChangeItem(
                        type=ChangeType.ADDITIVE,
                        category="parameter",
                        location=f"{location_prefix}.parameters[{old_param.get('name')}].required",
                        description=f"Parameter '{old_param.get('name')}' is now optional",
                        severity="low",
                        old_value=old_required,
                        new_value=new_required
                    ))
        
        return changes
    
    def _diff_request_body(self, location_prefix: str, old_body: Optional[Dict], new_body: Optional[Dict]) -> List[ChangeItem]:
        """Compare request body schemas"""
        changes = []
        
        if old_body is None and new_body is not None:
            # Request body added
            severity = "medium" if new_body.get('required', False) else "low"
            change_type = ChangeType.BREAKING if new_body.get('required', False) else ChangeType.ADDITIVE
            
            changes.append(ChangeItem(
                type=change_type,
                category="request_body",
                location=f"{location_prefix}.requestBody",
                description="Request body was added" + (" (required)" if new_body.get('required') else ""),
                severity=severity,
                new_value=new_body
            ))
        
        elif old_body is not None and new_body is None:
            # Request body removed
            changes.append(ChangeItem(
                type=ChangeType.BREAKING,
                category="request_body",
                location=f"{location_prefix}.requestBody",
                description="Request body was removed",
                severity="high",
                old_value=old_body
            ))
        
        elif old_body is not None and new_body is not None:
            # Request body modified - simplified comparison
            if old_body.get('required', False) != new_body.get('required', False):
                if new_body.get('required', False):
                    changes.append(ChangeItem(
                        type=ChangeType.BREAKING,
                        category="request_body",
                        location=f"{location_prefix}.requestBody.required",
                        description="Request body is now required",
                        severity="high",
                        old_value=old_body.get('required', False),
                        new_value=new_body.get('required', False)
                    ))
        
        return changes
    
    def _diff_responses(self, location_prefix: str, old_responses: Dict[str, Any], new_responses: Dict[str, Any]) -> List[ChangeItem]:
        """Compare response definitions"""
        changes = []
        
        old_status_codes = set(old_responses.keys())
        new_status_codes = set(new_responses.keys())
        
        # Removed response codes (potentially breaking)
        for status_code in old_status_codes - new_status_codes:
            # 2xx removals are breaking, others are informational
            is_success = status_code.startswith('2')
            change_type = ChangeType.BREAKING if is_success else ChangeType.INFORMATIONAL
            severity = "high" if is_success else "low"
            
            changes.append(ChangeItem(
                type=change_type,
                category="response",
                location=f"{location_prefix}.responses[{status_code}]",
                description=f"Response code '{status_code}' was removed",
                severity=severity,
                old_value=status_code
            ))
        
        # Added response codes (generally additive)
        for status_code in new_status_codes - old_status_codes:
            changes.append(ChangeItem(
                type=ChangeType.ADDITIVE,
                category="response",
                location=f"{location_prefix}.responses[{status_code}]",
                description=f"Response code '{status_code}' was added",
                severity="low",
                new_value=status_code
            ))
        
        return changes
    
    def _diff_info(self, old_info: Dict[str, Any], new_info: Dict[str, Any]) -> List[ChangeItem]:
        """Compare info sections (mostly informational)"""
        changes = []
        
        # Version changes
        old_version = old_info.get('version')
        new_version = new_info.get('version') 
        if old_version != new_version:
            changes.append(ChangeItem(
                type=ChangeType.INFORMATIONAL,
                category="version",
                location="info.version",
                description=f"API version changed from '{old_version}' to '{new_version}'",
                old_value=old_version,
                new_value=new_version
            ))
        
        # Title changes
        old_title = old_info.get('title')
        new_title = new_info.get('title')
        if old_title != new_title:
            changes.append(ChangeItem(
                type=ChangeType.INFORMATIONAL,
                category="title",
                location="info.title", 
                description=f"API title changed",
                old_value=old_title,
                new_value=new_title
            ))
        
        return changes
    
    def _diff_servers(self, old_servers: List[Dict], new_servers: List[Dict]) -> List[ChangeItem]:
        """Compare server definitions"""
        changes = []
        
        old_urls = {s.get('url') for s in old_servers}
        new_urls = {s.get('url') for s in new_servers}
        
        # Removed servers (potentially breaking)
        for url in old_urls - new_urls:
            changes.append(ChangeItem(
                type=ChangeType.BREAKING,
                category="server",
                location=f"servers[{url}]",
                description=f"Server '{url}' was removed",
                severity="medium",
                old_value=url
            ))
        
        # Added servers (additive)
        for url in new_urls - old_urls:
            changes.append(ChangeItem(
                type=ChangeType.ADDITIVE,
                category="server",
                location=f"servers[{url}]",
                description=f"Server '{url}' was added",
                severity="low",
                new_value=url
            ))
        
        return changes
    
    def _diff_components(self, old_components: Dict[str, Any], new_components: Dict[str, Any]) -> List[ChangeItem]:
        """Compare components sections (schemas, security schemes, etc.)"""
        changes = []
        
        # Compare schemas
        old_schemas = old_components.get('schemas', {})
        new_schemas = new_components.get('schemas', {})
        
        old_schema_names = set(old_schemas.keys())
        new_schema_names = set(new_schemas.keys())
        
        # Removed schemas (breaking)
        for schema_name in old_schema_names - new_schema_names:
            changes.append(ChangeItem(
                type=ChangeType.BREAKING,
                category="schema",
                location=f"components.schemas.{schema_name}",
                description=f"Schema '{schema_name}' was removed",
                severity="high",
                old_value=schema_name
            ))
        
        # Added schemas (additive)
        for schema_name in new_schema_names - old_schema_names:
            changes.append(ChangeItem(
                type=ChangeType.ADDITIVE,
                category="schema",
                location=f"components.schemas.{schema_name}",
                description=f"Schema '{schema_name}' was added",
                severity="low",
                new_value=schema_name
            ))
        
        return changes


def load_spec(file_path: Path) -> Dict[str, Any]:
    """Load OpenAPI specification from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Specification file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in specification file {file_path}: {e}")
        sys.exit(1)


def format_diff_report(report: DiffReport, format_type: str) -> str:
    """Format diff report for output"""
    if format_type == 'json':
        # Convert dataclasses to dict for JSON serialization
        report_dict = {
            'summary': report.summary,
            'metadata': report.metadata,
            'changes': [asdict(change) for change in report.changes],
            'breaking_changes': [asdict(change) for change in report.breaking_changes],
            'additive_changes': [asdict(change) for change in report.additive_changes],
            'informational_changes': [asdict(change) for change in report.informational_changes]
        }
        # Convert enums to strings
        for changes_list in ['changes', 'breaking_changes', 'additive_changes', 'informational_changes']:
            for change in report_dict[changes_list]:
                change['type'] = change['type'].value if hasattr(change['type'], 'value') else str(change['type'])
        
        return json.dumps(report_dict, indent=2, ensure_ascii=False)
    
    elif format_type == 'text':
        lines = []
        lines.append("=" * 70)
        lines.append("OpenAPI Contract Diff Report")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary
        lines.append("📊 SUMMARY")
        lines.append("-" * 20)
        for key, value in report.summary.items():
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
        lines.append("")
        
        # Breaking changes
        if report.breaking_changes:
            lines.append("💥 BREAKING CHANGES")
            lines.append("-" * 30)
            for change in report.breaking_changes:
                lines.append(f"❌ {change.description}")
                lines.append(f"   Location: {change.location}")
                lines.append(f"   Severity: {change.severity}")
                if change.old_value is not None:
                    lines.append(f"   Old: {change.old_value}")
                if change.new_value is not None:
                    lines.append(f"   New: {change.new_value}")
                lines.append("")
        
        # Additive changes
        if report.additive_changes:
            lines.append("➕ ADDITIVE CHANGES") 
            lines.append("-" * 30)
            for change in report.additive_changes:
                lines.append(f"✅ {change.description}")
                lines.append(f"   Location: {change.location}")
                if change.new_value is not None:
                    lines.append(f"   Added: {change.new_value}")
                lines.append("")
        
        # Informational changes
        if report.informational_changes:
            lines.append("ℹ️  INFORMATIONAL CHANGES")
            lines.append("-" * 30)
            for change in report.informational_changes:
                lines.append(f"📝 {change.description}")
                lines.append(f"   Location: {change.location}")
                lines.append("")
        
        # Metadata
        lines.append("📋 METADATA")
        lines.append("-" * 20)
        for key, value in report.metadata.items():
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(lines)
    
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare OpenAPI specifications and detect breaking changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Usage:')[1] if 'Usage:' in __doc__ else ''
    )
    
    parser.add_argument(
        '--old-spec',
        type=Path,
        default=Path('contracts/openapi/public-v1.json'),
        help='Path to old/baseline OpenAPI specification'
    )
    
    parser.add_argument(
        '--new-spec', 
        type=Path,
        required=True,
        help='Path to new/current OpenAPI specification'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'yaml'],
        default='text',
        help='Output format'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Use strict mode for breaking change detection'
    )
    
    args = parser.parse_args()
    
    print("🔍 Analyzing OpenAPI contract differences...")
    print(f"   Old spec: {args.old_spec}")
    print(f"   New spec: {args.new_spec}")
    print(f"   Format: {args.format}")
    print(f"   Strict mode: {args.strict}")
    print()
    
    # Load specifications
    old_spec = load_spec(args.old_spec)
    new_spec = load_spec(args.new_spec)
    
    # Perform diff
    differ = OpenAPIDiffer(strict_mode=args.strict)
    report = differ.diff_specs(old_spec, new_spec)
    
    # Format output
    formatted_report = format_diff_report(report, args.format)
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(formatted_report)
        print(f"✅ Diff report saved to: {args.output}")
    else:
        print(formatted_report)
    
    # Exit with appropriate code
    if report.breaking_changes:
        print(f"\n⚠️  Found {len(report.breaking_changes)} breaking changes!")
        return 1
    else:
        print(f"\n✅ No breaking changes detected. Found {report.summary['total_changes']} total changes.")
        return 0


if __name__ == '__main__':
    sys.exit(main())