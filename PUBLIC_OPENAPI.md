# Public OpenAPI Specification

This document describes the public OpenAPI specification endpoint for the Polaris platform.

## Endpoint

```
GET /openapi/public/v1/openapi.json
```

## Overview

The public OpenAPI specification endpoint provides a filtered, unauthenticated view of the Polaris API. This endpoint is designed for:

- Public API documentation
- Client SDK generation
- External integration planning
- Public-facing developer resources

## Features

### 🔓 **Unauthenticated Access**
- No authentication required
- Safe for public consumption
- Accessible in both development and production environments

### 🛡️ **Security Filtering**
The endpoint automatically filters out sensitive endpoints including:
- Authentication endpoints (`/auth/`, `/admin/`, `/internal/`)
- Administrative functions
- Debug and system endpoints
- Any endpoint containing sensitive keywords

### 📋 **Enhanced Versioning**
Version information follows the format: `{semantic_version}+{commit_sha}`
- Example: `0.1.0+595d144`
- Enables precise API version tracking
- Supports semantic versioning best practices

### ⚡ **Cache-Friendly**
- `Cache-Control: public, max-age=3600` (1 hour cache)
- ETag support for efficient caching
- Optimized for CDN distribution

## Response Format

The endpoint returns a standard OpenAPI 3.x specification with:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Polaris - Small Business Procurement Readiness Platform",
    "description": "Public API endpoints for the Polaris platform...",
    "version": "0.1.0+595d144"
  },
  "paths": {
    "/api/health": { ... },
    "/api/public/agency-theme/{agency_id}": { ... }
  },
  "components": {
    // Security schemes are excluded for public consumption
  }
}
```

## Public Endpoints

The filtered specification includes only public-safe endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/api/health` | API health status |
| `/api/health/database` | Database connectivity check |
| `/api/health/external` | External services status |
| `/api/public/agency-theme/{agency_id}` | Public agency branding |
| `/api/public/white-label/{agency_id}` | White-label configuration |

## Usage Examples

### Basic Request

```bash
curl -X GET https://api.polaris.example.com/openapi/public/v1/openapi.json
```

### With Caching Headers

```bash
curl -X GET \
  -H "If-None-Match: \"0.1.0+595d144\"" \
  https://api.polaris.example.com/openapi/public/v1/openapi.json
```

### Generate Client SDK

```bash
# Using OpenAPI Generator
openapi-generator-cli generate \
  -i https://api.polaris.example.com/openapi/public/v1/openapi.json \
  -g python \
  -o ./polaris-client
```

## Security Considerations

### What's Included ✅
- Health check endpoints
- Public branding/theme endpoints
- Read-only informational endpoints
- Non-sensitive utility endpoints

### What's Excluded ❌
- Authentication endpoints
- User data operations
- Administrative functions
- Internal system endpoints
- Debug and monitoring endpoints

## Development vs Production

- **Development**: Both `/docs` and public spec are available
- **Production**: Only public spec is available (internal docs disabled)

## Testing

Run the test suite to verify the endpoint:

```bash
python -m pytest test_public_openapi.py -v
```

The test suite validates:
- Endpoint accessibility
- Proper filtering
- Version format
- Caching headers
- Security exclusions

## Configuration

No additional configuration is required. The endpoint:
- Uses the same environment as the main application
- Inherits security middleware settings
- Automatically detects git commit for versioning
- Applies conservative filtering by default

## Integration Notes

This endpoint supports the requirements from PRs #14-#19 for:
- Public API hardening
- Cache-friendly specifications
- Version metadata consistency
- Security baseline compliance