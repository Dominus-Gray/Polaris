# CONTRIBUTING.md - Polaris Platform

## Platform Foundations Development Guide

This guide covers the foundational architecture and development practices for the Polaris platform.

## Architecture Overview

The Polaris platform is built on a foundation of:
- **MongoDB** for document storage with custom migration system
- **Domain Event Sourcing** with outbox pattern for reliability
- **RBAC Policy Engine** for fine-grained access control
- **OpenTelemetry Observability** for comprehensive monitoring
- **FastAPI** with structured API patterns

## Getting Started

### Prerequisites
- Python 3.11+
- MongoDB 7.0+
- Docker & Docker Compose
- Make

### Development Setup
```bash
# Clone and setup
git clone <repo-url>
cd Polaris

# Bootstrap development environment
make bootstrap

# Run database migrations
make migrate

# Seed with sample data
make seed

# Start development server
make run-dev
```

## Domain Model Conventions

### Collection Naming
- Use plural nouns: `users`, `organizations`, `client_profiles`
- Use underscores for multi-word names: `action_plans`, `outcome_records`
- Include audit fields: `created_at`, `updated_at`

### Document Structure
```javascript
{
  "id": "uuid-string",           // Required: Unique identifier
  "created_at": "ISODate",       // Required: Creation timestamp  
  "updated_at": "ISODate",       // Required: Last modification
  // ... domain-specific fields
}
```

### Adding New Collections

1. **Create Migration**: Add new migration file in `backend/migrations/`
```python
from .migration_base import Migration

class Migration002(Migration):
    def __init__(self):
        super().__init__("002", "Add new domain collection")
    
    async def up(self, db):
        # Define collection schema with validation
        await self._create_new_collection(db)
    
    async def down(self, db):
        # Rollback changes
        await db.drop_collection("new_collection")
```

2. **Register Migration**: Add to `migrations/migrate.py`
3. **Add Indexes**: Include performance-critical indexes
4. **Update Documentation**: Document in `docs/architecture/`

## Event Sourcing Patterns

### Event Naming Conventions
- Use past tense: `user.created`, `assessment.completed`
- Include aggregate type: `client.profile_updated`
- Be specific: `task.state_changed` not just `task.updated`

### Creating Domain Events
```python
from domain.events import DomainEvent, EventDispatcher

@dataclass
class ClientAssignedEvent(DomainEvent):
    client_id: str
    provider_id: str
    assigned_by: str
    
    def __post_init__(self):
        self.event_type = "client.assigned_to_provider"
        self.aggregate_type = "ClientProfile"
        self.aggregate_id = self.client_id
        super().__post_init__()

# Usage in business logic
async def assign_client(client_id, provider_id, assigned_by):
    # ... business logic ...
    
    event = ClientAssignedEvent(
        client_id=client_id,
        provider_id=provider_id,
        assigned_by=assigned_by
    )
    await event_dispatcher.dispatch(event)
```

## RBAC Implementation Patterns

### Adding New Permissions
1. **Define Permission**: Add to `rbac/permissions.py`
```python
class Permission(Enum):
    NEW_PERMISSION = "new:permission"
```

2. **Assign to Roles**: Update `ROLE_PERMISSIONS` mapping
3. **Implement Checks**: Use in API endpoints
```python
@router.get("/resource")
async def get_resource(
    current_user=Depends(security.get_current_user),
    _=Depends(security.require_permission(Permission.NEW_PERMISSION))
):
    # ... endpoint logic ...
```

### Resource-Level Permissions
```python
@router.get("/clients/{client_id}")
async def get_client(
    client_id: str,
    current_user=Depends(security.get_current_user),
    _=Depends(security.require_resource_permission(
        Permission.READ_CLIENT, 
        "client_profile"
    ))
):
    # Policy engine automatically checks:
    # - User has READ_CLIENT permission
    # - User can access this specific client
    # - Organization membership if required
```

## API Development Guidelines

### Endpoint Structure
```
/api/v1/{resource}
├── GET    /           # List resources (with filtering)
├── POST   /           # Create new resource
├── GET    /{id}       # Get specific resource
├── PUT    /{id}       # Update entire resource
├── PATCH  /{id}       # Partial update
└── DELETE /{id}       # Delete resource
```

### Response Patterns
```python
# Success responses
{
    "success": true,
    "data": { ... },
    "meta": {
        "count": 10,
        "page": 1,
        "total": 100
    }
}

# Error responses
{
    "success": false,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "Insufficient permissions",
        "details": { ... }
    }
}
```

### Data Redaction
```python
# Automatic redaction based on user permissions
@router.get("/clients/{client_id}")
async def get_client(client_id: str, security=Depends(get_security)):
    client = await get_client_from_db(client_id)
    
    # Apply redaction based on user's permissions
    redacted_client = await security.redact_response(
        client, 
        "client_profile", 
        current_user,
        client_id
    )
    
    return {"success": True, "data": redacted_client}
```

## Testing Strategies

### Unit Tests
- Test business logic in isolation
- Mock external dependencies
- Focus on edge cases and error conditions

```python
@pytest.mark.asyncio
async def test_policy_evaluation():
    policy_service = PolicyEvaluationService(mock_db)
    decision = await policy_service.evaluate(principal, permission, resource)
    assert decision.allowed
    assert decision.evaluation_time_ms < 5.0
```

### Integration Tests
- Test API endpoints with real database
- Verify RBAC enforcement
- Test event processing flows

```python
async def test_create_client_with_rbac(client):
    response = await client.post(
        "/api/clients",
        json={"name": "Test Client"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
```

### Performance Tests
- Benchmark critical paths
- Verify SLA compliance
- Load test with realistic data volumes

## Observability Practices

### Structured Logging
```python
from observability.logging_config import get_logger

logger = get_logger("my_module")

# Log with context
logger.info(
    "Client created successfully",
    client_id=client_id,
    user_id=current_user["id"],
    organization_id=org_id,
    event_type="client_created"
)
```

### Metrics Collection
```python
from observability.telemetry import metrics_collector

# Record business metrics
metrics_collector.assessments_completed.labels(
    risk_band="medium",
    template_version="v2.1"
).inc()
```

### Tracing
```python
from observability.telemetry import trace_function

@trace_function("create_action_plan")
async def create_action_plan(client_id: str):
    # Automatically traced with OpenTelemetry
    pass
```

## Performance Guidelines

### Database Operations
- Use indexes for frequent queries
- Limit result sets with pagination
- Use aggregation pipelines for complex queries
- Monitor query performance with metrics

### RBAC Optimization
- Cache permission checks when possible
- Minimize database calls in policy evaluation
- Use efficient organization membership lookups
- Target < 5ms average evaluation time

### API Response Times
- Health endpoints: < 100ms
- Simple CRUD: < 200ms
- Complex operations: < 500ms
- Use async/await throughout

## Security Best Practices

### Input Validation
- Use Pydantic models for request validation
- Sanitize all user inputs
- Validate file uploads
- Implement rate limiting

### Authentication & Authorization
- Always validate JWT tokens
- Check user status (active/inactive)
- Implement proper session management
- Log authentication events

### Data Protection
- Apply field-level redaction
- Encrypt sensitive data at rest
- Use secure communication (TLS)
- Implement audit trails

## Deployment & Operations

### Environment Configuration
```bash
# Required environment variables
MONGO_URL=mongodb://localhost:27017
DB_NAME=polaris_production
JWT_SECRET=secure-random-key
ENABLE_TRACING=true
LOG_LEVEL=INFO
```

### Health Monitoring
- Monitor `/health/system` endpoint
- Set up alerts for critical metrics
- Track business KPIs
- Implement graceful degradation

### Migration Management
```bash
# Check current status
make migrate-status

# Apply migrations
make migrate

# Rollback if needed
make rollback TARGET=001
```

## Code Review Guidelines

### Architecture Compliance
- [ ] Follows domain model conventions
- [ ] Implements proper RBAC checks
- [ ] Includes appropriate logging/metrics
- [ ] Has comprehensive error handling

### Performance & Security
- [ ] No N+1 query problems
- [ ] Proper input validation
- [ ] Sensitive data is redacted
- [ ] Includes performance tests

### Documentation
- [ ] Updates API documentation
- [ ] Includes migration notes
- [ ] Documents breaking changes
- [ ] Updates architecture diagrams

## Getting Help

### Resources
- **Architecture**: `docs/architecture/foundations.md`
- **API Documentation**: Run `make run-dev` and visit `/docs`
- **Metrics Dashboard**: Grafana at `http://localhost:3000`
- **Tracing**: Jaeger at `http://localhost:16686`

### Development Commands
```bash
make help              # Show all available commands
make test              # Run comprehensive test suite
make lint              # Code quality checks
make benchmark         # Performance testing
make security-scan     # Security vulnerability scan
```

### Common Issues

**Migration Failures**: Check MongoDB connection and permissions
**Permission Denied**: Verify user roles and RBAC configuration  
**Performance Issues**: Check database indexes and query patterns
**Event Processing**: Monitor outbox processor and event handlers

---

For questions or contributions, please follow the project's issue templates and pull request guidelines.