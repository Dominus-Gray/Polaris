# Public API Hardening Implementation Guide

## Overview
This implementation adds comprehensive API hardening features to the Polaris platform, including:

1. **API Token System** with scope-based authentication
2. **Enhanced Rate Limiting** with HTTP headers  
3. **API Versioning** with deprecation signaling
4. **Standardized Error Responses** in Problem+JSON format
5. **Scope-based Access Control** mapping to RBAC

## API Token System

### Token Format
- **Prefix**: `pol_` + 8 random characters (e.g., `pol_abc12345`)
- **Full Token**: `{prefix}.{secret}` (e.g., `pol_abc12345.randomsecret123`)
- **Storage**: Hash of secret + salt stored in database

### Available Scopes
```python
API_SCOPES = {
    # Client data access
    "read:clients": "Read client information and profiles",
    "write:clients": "Create and update client information",
    
    # Action plan access  
    "read:action_plans": "Read action plans and assessments",
    "write:action_plans": "Create and update action plans",
    
    # Task management
    "read:tasks": "Read tasks and task status", 
    "write:tasks": "Create and update tasks",
    
    # Analytics access
    "read:analytics": "Read analytics and reports",
    "read:cohorts": "Read cohort and comparative data",
    
    # Token management
    "manage:tokens": "Create, revoke, and manage API tokens",
    
    # Consent management
    "read:consents": "Read consent and permission data",
    "write:consents": "Create and update consent records"
}
```

### Usage Examples

#### Creating an API Token
```bash
curl -X POST https://api.polaris.com/api/v1/tokens \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Client Integration Token",
    "scopes": ["read:clients", "read:action_plans"],
    "description": "Token for client portal integration",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

Response:
```json
{
  "token": "pol_abc12345.randomsecret123",
  "token_info": {
    "id": "token-uuid",
    "name": "Client Integration Token", 
    "token_prefix": "pol_abc12345",
    "scopes": ["read:clients", "read:action_plans"],
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_active": true
  }
}
```

#### Using an API Token
```bash
curl -X GET https://api.polaris.com/api/v1/clients \
  -H "Authorization: Bearer pol_abc12345.randomsecret123"
```

#### Listing Tokens
```bash
curl -X GET https://api.polaris.com/api/v1/tokens \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### Revoking a Token
```bash
curl -X DELETE https://api.polaris.com/api/v1/tokens/token-uuid \
  -H "Authorization: Bearer <your_jwt_token>"
```

## Rate Limiting

### Configuration
- **Default**: 120 requests/minute, burst 30 requests/10s
- **Auth endpoints**: 10 requests/5 minutes, burst 5 requests/minute  
- **Upload endpoints**: 10 requests/5 minutes, burst 3 requests/minute

### Headers Returned
```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60  (on 429 errors)
```

### Example 429 Response
```json
{
  "type": "https://polaris.example.com/problems/POL-2005",
  "title": "Rate limit exceeded", 
  "status": 429,
  "detail": "Rate limit exceeded",
  "instance": "urn:uuid:12345678-1234-1234-1234-123456789012",
  "code": "POL-2005",
  "metadata": {
    "rate_limit": {
      "limit": 120,
      "remaining": 0,
      "reset": 1640995200,
      "retry_after": 60
    }
  }
}
```

## API Versioning

### URL Structure
- **Versioned**: `/api/v1/...` (recommended)
- **Legacy**: `/api/...` (deprecated)

### Deprecation Headers
Legacy API responses include:
```
Sunset: 2025-12-31T00:00:00Z
Link: </api/v1/>; rel="successor-version"  
Deprecation: true
```

## Error Format (Problem+JSON)

All error responses follow RFC 7807 Problem Details format:

```json
{
  "type": "https://polaris.example.com/problems/POL-1003",
  "title": "Insufficient permissions for requested action",
  "status": 403,
  "detail": "Missing required scope: write:clients", 
  "instance": "urn:uuid:error-instance-id",
  "code": "POL-1003",
  "metadata": {
    "required_scope": "write:clients",
    "user_scopes": ["read:clients"],
    "user_role": "client"
  }
}
```

### Error Codes
- **POL-1xxx**: Authentication/Authorization errors
- **POL-2xxx**: System/Infrastructure errors  
- **POL-3xxx**: Validation/Business logic errors

## Scope-based Access Control

### Implementation Pattern
```python
@api_v1.get("/clients")
@require_scope("read:clients")
async def list_clients(auth_info=Depends(get_current_user_or_token)):
    # Endpoint implementation
    pass
```

### RBAC Mapping
Each scope maps to required user roles:
```python
SCOPE_RBAC_MAPPING = {
    "read:clients": ["client", "agency", "navigator"],
    "write:clients": ["agency", "navigator"],
    "manage:tokens": ["agency", "navigator"]
}
```

## Migration Guide

### For API Consumers
1. **Immediate**: Continue using existing JWT authentication
2. **Phase 1**: Migrate to versioned endpoints (`/api/v1/...`)
3. **Phase 2**: Consider API tokens for service-to-service communication
4. **Phase 3**: Update error handling for Problem+JSON format

### For Internal Services
1. Create API tokens with appropriate scopes
2. Update rate limiting configuration as needed
3. Monitor deprecation headers on legacy endpoints
4. Plan migration to versioned APIs before sunset date

## Security Considerations

1. **Token Storage**: API tokens should be stored securely (environment variables, secret managers)
2. **Scope Principle**: Request minimal scopes needed for functionality
3. **Token Rotation**: Regularly rotate long-lived tokens
4. **Monitoring**: Monitor rate limit headers to avoid throttling
5. **Error Handling**: Implement proper error handling for Problem+JSON responses

## OpenAPI Documentation

The enhanced API includes comprehensive OpenAPI documentation with:
- Token authentication schemes
- Rate limiting descriptions  
- Error response schemas
- Scope requirements per endpoint
- Deprecation notices

Access at: `https://api.polaris.com/docs` (development only)