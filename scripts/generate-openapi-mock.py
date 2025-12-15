#!/usr/bin/env python3
"""
Simple OpenAPI Generator - Mock Implementation

This script generates a representative OpenAPI specification for the Polaris platform
without requiring the full server environment. This is used for demonstrating
the contract diff pipeline structure.

In production, this would connect to the actual FastAPI server.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def generate_mock_openapi_spec() -> Dict[str, Any]:
    """Generate a mock OpenAPI specification based on the Polaris platform structure"""
    return {
        "openapi": "3.0.2",
        "info": {
            "title": "Polaris - Small Business Procurement Readiness Platform",
            "description": "Secure platform for assessing small business procurement readiness",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://biz-matchmaker-1.preview.emergentagent.com/api",
                "description": "Production API"
            }
        ],
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "Health Check",
                    "operationId": "health_check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/auth/register": {
                "post": {
                    "summary": "Register User",
                    "operationId": "register_user",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"},
                                        "role": {"type": "string", "enum": ["client", "navigator", "provider", "agency"]},
                                        "terms_accepted": {"type": "boolean"}
                                    },
                                    "required": ["email", "password", "role", "terms_accepted"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "User registered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "user_id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid registration data"
                        }
                    }
                }
            },
            "/api/auth/login": {
                "post": {
                    "summary": "User Login",
                    "operationId": "login_user",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"},
                                            "token_type": {"type": "string"},
                                            "expires_in": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Invalid credentials"
                        }
                    }
                }
            },
            "/api/assessments": {
                "post": {
                    "summary": "Create Assessment Session",
                    "operationId": "create_assessment",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "area_id": {"type": "string"},
                                        "tier_level": {"type": "integer", "minimum": 1, "maximum": 3}
                                    },
                                    "required": ["area_id", "tier_level"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Assessment session created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_id": {"type": "string"},
                                            "questions": {"type": "array", "items": {"type": "object"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/knowledge-base/articles": {
                "get": {
                    "summary": "Get Knowledge Base Articles",
                    "operationId": "get_kb_articles",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "area_id",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Filter by business area"
                        },
                        {
                            "name": "tier_level",
                            "in": "query",
                            "schema": {"type": "integer"},
                            "description": "Filter by tier level"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Knowledge base articles",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "articles": {"type": "array", "items": {"type": "object"}},
                                            "total": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/admin/system/stats": {
                "get": {
                    "summary": "Get System Statistics (Admin Only)",
                    "operationId": "get_system_stats",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "System statistics",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "total_users": {"type": "integer"},
                                            "active_businesses": {"type": "integer"},
                                            "certificates_issued": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Admin access required"
                        }
                    }
                }
            },
            "/metrics": {
                "get": {
                    "summary": "Prometheus Metrics",
                    "operationId": "get_metrics",
                    "responses": {
                        "200": {
                            "description": "Prometheus metrics",
                            "content": {
                                "text/plain": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }


def is_public_endpoint(path: str, method: str, route_info: Dict[str, Any]) -> bool:
    """Determine if an endpoint should be included in the public API specification"""
    # Admin endpoints are internal
    if path.startswith('/admin'):
        return False
    
    # Metrics endpoints are internal
    if path.startswith('/metrics'):
        return False
    
    # Development/debug endpoints
    if path in ['/docs', '/redoc', '/openapi.json']:
        return False
    
    # API routes and health checks are generally public
    if path.startswith('/api') or path == '/health':
        return True
    
    return True


def filter_openapi_spec(openapi_spec: Dict[str, Any], public_only: bool = False) -> Dict[str, Any]:
    """Filter OpenAPI specification to include only public endpoints if requested"""
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


def save_spec(spec: Dict[str, Any], filepath: Path) -> bool:
    """Save OpenAPI specification to file"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved JSON specification to: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving specification to {filepath}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI specifications for contract diff pipeline")
    
    parser.add_argument(
        '--public-only',
        action='store_true',
        help='Generate only public API endpoints'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('contracts/openapi'),
        help='Directory to save generated specs'
    )
    
    args = parser.parse_args()
    
    print("🚀 Generating OpenAPI specifications for Polaris Platform")
    print(f"   Output directory: {args.output_dir}")
    print(f"   Public only: {args.public_only}")
    print()
    
    # Generate mock OpenAPI spec
    print("📋 Generating OpenAPI specification...")
    openapi_spec = generate_mock_openapi_spec()
    print(f"   Found {len(openapi_spec.get('paths', {}))} total endpoints")
    
    success = True
    
    if args.public_only:
        # Generate public-only specification
        print("🔍 Filtering for public endpoints only...")
        public_spec = filter_openapi_spec(openapi_spec, public_only=True)
        public_spec = add_contract_metadata(public_spec, 'public-v1')
        
        print(f"   Filtered to {len(public_spec.get('paths', {}))} public endpoints")
        
        # Save public specification
        public_file = args.output_dir / "public-v1.json"
        if not save_spec(public_spec, public_file):
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
        
        # Save specifications
        public_file = args.output_dir / "public-v1.json"
        internal_file = args.output_dir / "internal-reference.json"
        
        if not save_spec(public_spec, public_file):
            success = False
        if not save_spec(internal_spec, internal_file):
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
    exit(main())