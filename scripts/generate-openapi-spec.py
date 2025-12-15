#!/usr/bin/env python3
"""
OpenAPI Specification Generator for Polaris Platform

This script generates the current OpenAPI specification from the FastAPI application,
with filtering for public vs internal endpoints, and outputs clean JSON snapshots
for contract diff pipeline.

Usage:
    python scripts/generate-openapi-spec.py [--public-only] [--output-dir PATH]

Options:
    --public-only   Generate only public API endpoints (excludes admin/internal routes)
    --output-dir    Directory to save generated specs (default: contracts/openapi/)
    --format        Output format: json or yaml (default: json)
    --validate      Validate generated OpenAPI spec before saving
    --help          Show this help message

Examples:
    # Generate both public and internal reference specs
    python scripts/generate-openapi-spec.py

    # Generate only public API spec
    python scripts/generate-openapi-spec.py --public-only

    # Save to custom directory
    python scripts/generate-openapi-spec.py --output-dir ./api-specs/
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Set
from datetime import datetime

# Add backend to path to import server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def get_fastapi_app():
    """Import and return the FastAPI application instance"""
    try:
        from server import app
        return app
    except ImportError as e:
        print(f"Error importing FastAPI app: {e}")
        print("Make sure you're running this from the repository root directory")
        sys.exit(1)

def is_public_endpoint(path: str, method: str, route_info: Dict[str, Any]) -> bool:
    """
    Determine if an endpoint should be included in the public API specification.
    
    Filters out:
    - Admin endpoints (/admin)
    - Internal endpoints (/internal) 
    - Development/debug endpoints (/docs, /redoc, /openapi.json)
    - Metrics endpoints (/metrics)
    """
    # Admin endpoints are internal
    if path.startswith('/admin'):
        return False
    
    # Internal endpoints
    if path.startswith('/internal'):
        return False
    
    # Development/debug endpoints
    if path in ['/docs', '/redoc', '/openapi.json']:
        return False
    
    # Metrics endpoints
    if path.startswith('/metrics'):
        return False
    
    # Health check is generally considered public for status monitoring
    if path == '/health':
        return True
    
    # API routes are generally public unless specifically marked
    if path.startswith('/api'):
        return True
    
    # By default, include endpoints unless explicitly excluded
    return True

def filter_openapi_spec(openapi_spec: Dict[str, Any], public_only: bool = False) -> Dict[str, Any]:
    """
    Filter OpenAPI specification to include only public endpoints if requested.
    
    Args:
        openapi_spec: The complete OpenAPI specification
        public_only: If True, filter to only public endpoints
        
    Returns:
        Filtered OpenAPI specification
    """
    if not public_only:
        return openapi_spec
    
    filtered_spec = openapi_spec.copy()
    filtered_paths = {}
    
    for path, methods in openapi_spec.get('paths', {}).items():
        filtered_methods = {}
        
        for method, route_info in methods.items():
            if is_public_endpoint(path, method, route_info):
                filtered_methods[method] = route_info
        
        if filtered_methods:
            filtered_paths[path] = filtered_methods
    
    filtered_spec['paths'] = filtered_paths
    
    # Add metadata about filtering
    filtered_spec['info']['x-filtered'] = True
    filtered_spec['info']['x-filter-type'] = 'public-only'
    filtered_spec['info']['x-generated-at'] = datetime.utcnow().isoformat() + 'Z'
    
    return filtered_spec

def add_contract_metadata(spec: Dict[str, Any], spec_type: str) -> Dict[str, Any]:
    """Add contract diff pipeline metadata to the specification"""
    spec = spec.copy()
    
    # Add contract metadata
    spec['info']['x-contract-metadata'] = {
        'spec-type': spec_type,
        'generated-at': datetime.utcnow().isoformat() + 'Z',
        'generator': 'polaris-contract-diff-pipeline',
        'version': '1.0.0'
    }
    
    return spec

def validate_openapi_spec(spec: Dict[str, Any]) -> bool:
    """
    Basic validation of OpenAPI specification.
    
    Returns True if valid, False otherwise.
    """
    required_fields = ['openapi', 'info', 'paths']
    
    for field in required_fields:
        if field not in spec:
            print(f"Error: Missing required field '{field}' in OpenAPI spec")
            return False
    
    if not isinstance(spec['paths'], dict):
        print("Error: 'paths' field must be a dictionary")
        return False
    
    # Check OpenAPI version
    if not spec.get('openapi', '').startswith('3.'):
        print(f"Warning: OpenAPI version '{spec.get('openapi')}' may not be supported")
    
    return True

def save_spec(spec: Dict[str, Any], filepath: Path, format_type: str = 'json') -> bool:
    """Save OpenAPI specification to file"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if format_type == 'json':
                json.dump(spec, f, indent=2, ensure_ascii=False)
            else:
                # YAML support could be added here if needed
                raise ValueError(f"Unsupported format: {format_type}")
        
        print(f"✓ Saved {format_type.upper()} specification to: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving specification to {filepath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI specifications for contract diff pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Usage:')[1] if 'Usage:' in __doc__ else ''
    )
    
    parser.add_argument(
        '--public-only',
        action='store_true',
        help='Generate only public API endpoints (excludes admin/internal routes)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('contracts/openapi'),
        help='Directory to save generated specs (default: contracts/openapi/)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'yaml'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate generated OpenAPI spec before saving'
    )
    
    args = parser.parse_args()
    
    print("🚀 Generating OpenAPI specifications for Polaris Platform")
    print(f"   Output directory: {args.output_dir}")
    print(f"   Format: {args.format}")
    print(f"   Public only: {args.public_only}")
    print()
    
    # Get FastAPI app and generate OpenAPI spec
    print("📡 Loading FastAPI application...")
    app = get_fastapi_app()
    
    print("📋 Generating OpenAPI specification...")
    try:
        openapi_spec = app.openapi()
    except Exception as e:
        print(f"Error generating OpenAPI spec: {e}")
        return 1
    
    print(f"   Found {len(openapi_spec.get('paths', {}))} total endpoints")
    
    success = True
    
    if args.public_only:
        # Generate public-only specification
        print("🔍 Filtering for public endpoints only...")
        public_spec = filter_openapi_spec(openapi_spec, public_only=True)
        public_spec = add_contract_metadata(public_spec, 'public-v1')
        
        print(f"   Filtered to {len(public_spec.get('paths', {}))} public endpoints")
        
        if args.validate and not validate_openapi_spec(public_spec):
            print("❌ Public specification validation failed")
            return 1
        
        # Save public specification
        public_file = args.output_dir / f"public-v1.{args.format}"
        if not save_spec(public_spec, public_file, args.format):
            success = False
    
    else:
        # Generate both public and internal reference specifications
        print("🔍 Generating public API specification...")
        public_spec = filter_openapi_spec(openapi_spec, public_only=True)
        public_spec = add_contract_metadata(public_spec, 'public-v1')
        
        print("🔍 Generating internal reference specification...")
        internal_spec = filter_openapi_spec(openapi_spec, public_only=False)
        internal_spec = add_contract_metadata(internal_spec, 'internal-reference')
        
        print(f"   Public endpoints: {len(public_spec.get('paths', {}))}")
        print(f"   Total endpoints: {len(internal_spec.get('paths', {}))}")
        
        # Validate specifications
        if args.validate:
            if not validate_openapi_spec(public_spec):
                print("❌ Public specification validation failed")
                return 1
            if not validate_openapi_spec(internal_spec):
                print("❌ Internal specification validation failed")  
                return 1
            print("✓ All specifications passed validation")
        
        # Save specifications
        public_file = args.output_dir / f"public-v1.{args.format}"
        internal_file = args.output_dir / f"internal-reference.{args.format}"
        
        if not save_spec(public_spec, public_file, args.format):
            success = False
        if not save_spec(internal_spec, internal_file, args.format):
            success = False
    
    if success:
        print("\n✅ OpenAPI specification generation completed successfully!")
        print("\nNext steps:")
        print("1. Review generated specifications for accuracy")
        print("2. Commit specifications to version control")
        print("3. Run contract diff pipeline to validate changes")
        return 0
    else:
        print("\n❌ Some specifications failed to generate")
        return 1

if __name__ == '__main__':
    sys.exit(main())