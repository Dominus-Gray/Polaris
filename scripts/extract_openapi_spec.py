#!/usr/bin/env python3
"""
OpenAPI Spec Extractor for Polaris

Extracts OpenAPI specifications from the FastAPI application and applies
filtering to generate public and internal reference specs.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Set


class OpenAPIFilter:
    """Filters OpenAPI specifications to create public and internal versions."""
    
    def __init__(self):
        self.public_path_prefixes = {
            "/api/auth/",
            "/api/assessments/",
            "/api/users/profile",
            "/api/marketplace/providers",
            "/api/health"
        }
        
        self.internal_only_paths = {
            "/api/admin/",
            "/api/internal/",
            "/api/debug/",
            "/api/system/"
        }
    
    def filter_public_spec(self, full_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create public API specification by filtering internal endpoints."""
        public_spec = {
            "openapi": full_spec.get("openapi", "3.0.2"),
            "info": {
                "title": "Polaris Public API",
                "description": "Public API for Polaris - Small Business Procurement Readiness Platform",
                "version": full_spec.get("info", {}).get("version", "1.0.0")
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {})
            },
            "security": [{"BearerAuth": []}]
        }
        
        # Filter paths - only include public endpoints
        for path, path_item in full_spec.get("paths", {}).items():
            if self._is_public_path(path):
                # Remove internal-only operations
                filtered_path_item = {}
                for method, operation in path_item.items():
                    if method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                        # Check if operation has public tag or is explicitly public
                        tags = operation.get("tags", [])
                        if not any(tag.startswith("internal") or tag.startswith("admin") for tag in tags):
                            filtered_path_item[method] = self._filter_operation(operation)
                
                if filtered_path_item:
                    public_spec["paths"][path] = filtered_path_item
        
        # Extract only schemas used by public endpoints
        used_schemas = self._extract_used_schemas(public_spec["paths"])
        full_schemas = full_spec.get("components", {}).get("schemas", {})
        
        for schema_name in used_schemas:
            if schema_name in full_schemas:
                public_spec["components"]["schemas"][schema_name] = full_schemas[schema_name]
        
        return public_spec
    
    def _is_public_path(self, path: str) -> bool:
        """Determine if a path should be included in the public API."""
        # Exclude internal-only paths
        for internal_prefix in self.internal_only_paths:
            if path.startswith(internal_prefix):
                return False
        
        # Include paths that match public prefixes
        for public_prefix in self.public_path_prefixes:
            if path.startswith(public_prefix):
                return True
        
        # Default to internal unless explicitly marked as public
        return False
    
    def _filter_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Filter operation to remove internal details."""
        filtered_op = operation.copy()
        
        # Remove internal parameters
        if "parameters" in filtered_op:
            filtered_op["parameters"] = [
                param for param in filtered_op["parameters"]
                if not param.get("name", "").startswith("x-internal-")
            ]
        
        # Remove internal response headers
        if "responses" in filtered_op:
            for response_code, response in filtered_op["responses"].items():
                if "headers" in response:
                    response["headers"] = {
                        name: header for name, header in response["headers"].items()
                        if not name.startswith("x-internal-")
                    }
        
        return filtered_op
    
    def _extract_used_schemas(self, paths: Dict[str, Any]) -> Set[str]:
        """Extract all schema references used in the given paths."""
        used_schemas = set()
        
        def extract_refs(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    if ref.startswith("#/components/schemas/"):
                        schema_name = ref.split("/")[-1]
                        used_schemas.add(schema_name)
                else:
                    for value in obj.values():
                        extract_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_refs(item)
        
        extract_refs(paths)
        return used_schemas


def extract_openapi_spec(app_module_path: str = "backend.server") -> Dict[str, Any]:
    """Extract OpenAPI specification from FastAPI app."""
    try:
        # Add the backend directory to the Python path
        current_dir = Path(__file__).parent.parent
        backend_dir = current_dir / "backend"
        sys.path.insert(0, str(backend_dir))
        
        # Import the FastAPI app
        from server import app
        
        # Generate OpenAPI spec
        openapi_spec = app.openapi()
        return openapi_spec
    
    except ImportError as e:
        print(f"Error importing FastAPI app: {e}")
        print("Note: This requires the FastAPI dependencies to be installed.")
        
        # Return a minimal spec for demonstration
        return {
            "openapi": "3.0.2",
            "info": {
                "title": "Polaris API",
                "description": "API for Polaris - Small Business Procurement Readiness Platform",
                "version": "1.0.0"
            },
            "paths": {
                "/api/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {
                            "200": {
                                "description": "Health check response"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }


def main():
    """Main entry point for OpenAPI spec extraction."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python extract_openapi_spec.py [output_dir]")
        print("Extracts OpenAPI specifications and saves them to the contracts directory.")
        sys.exit(0)
    
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("contracts/openapi")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Extracting OpenAPI specification from FastAPI app...")
    
    # Extract full specification
    full_spec = extract_openapi_spec()
    
    # Create filter instance
    api_filter = OpenAPIFilter()
    
    # Generate public specification
    public_spec = api_filter.filter_public_spec(full_spec)
    
    # Save specifications
    public_spec_path = output_dir / "public-v1.json"
    internal_spec_path = output_dir / "internal-reference.json"
    
    with open(public_spec_path, "w") as f:
        json.dump(public_spec, f, indent=2)
    
    with open(internal_spec_path, "w") as f:
        json.dump(full_spec, f, indent=2)
    
    print(f"Public API specification saved to: {public_spec_path}")
    print(f"Internal reference specification saved to: {internal_spec_path}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total paths in full spec: {len(full_spec.get('paths', {}))}")
    print(f"  Public paths: {len(public_spec.get('paths', {}))}")
    print(f"  Public schemas: {len(public_spec.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    main()