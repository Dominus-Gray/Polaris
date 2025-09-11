# Polaris Contract Specifications

This directory contains canonical contract specifications for the Polaris platform, including OpenAPI specifications for public and internal APIs, and event schemas for webhooks and SLA monitoring.

## 📁 Directory Structure

```
contracts/
├── config.yml                           # Pipeline configuration
├── openapi/                            # OpenAPI specifications
│   ├── public-v1.json                  # Filtered public API spec
│   └── internal-reference.json         # Internal API reference
├── events/                             # Event schemas
│   ├── webhook-envelope.schema.json    # Standard webhook envelope
│   └── sla-breach.schema.json         # SLA breach event schema
└── README.md                          # This file
```

## 🔄 Contract Diff Pipeline

The automated contract diff pipeline continuously guards the stability of public APIs and event schemas by:

1. **Generating canonical snapshots** from the FastAPI application
2. **Comparing changes** on pull requests and nightly builds
3. **Classifying impact** as breaking, additive, or informational
4. **Enforcing policy** with blocking or warning behaviors
5. **Supporting controlled overrides** for emergency changes

### Change Classification

| Change Type | Description | Impact |
|-------------|-------------|---------|
| **Breaking** | Removes endpoints, adds required fields, removes enum values | ❌ Blocks PR by default |
| **Additive** | Adds endpoints, adds optional fields, adds enum values | ✅ Allowed |
| **Informational** | Version updates, description changes | ℹ️ Logged only |

### Policy Enforcement

The pipeline enforces the following policies:

- **No breaking changes** without explicit override
- **Maximum breaking changes** per PR (configurable)
- **Path-based exceptions** for internal APIs
- **Override tokens** for emergency releases

## 🚀 Usage

### Extract Current Specifications

```bash
# Extract OpenAPI specs from FastAPI app
python scripts/extract_openapi_spec.py contracts/openapi
```

### Run Contract Diff Analysis

```bash
# Compare current vs canonical contracts
python scripts/contract_diff_pipeline.py diff

# Validate contracts against policy
python scripts/contract_diff_pipeline.py validate

# Generate new canonical snapshots
python scripts/contract_diff_pipeline.py generate
```

### Override Breaking Changes

For emergency releases that require breaking changes:

```bash
# Set override token
export CONTRACT_OVERRIDE_TOKEN="EMERGENCY_OVERRIDE"

# Run validation with override
python scripts/contract_diff_pipeline.py validate
```

## 📋 OpenAPI Specifications

### Public API (`public-v1.json`)

The public API specification contains only endpoints that are intended for external consumption:

- Authentication endpoints (`/api/auth/`)
- Assessment endpoints (`/api/assessments/`)
- User profile endpoints (`/api/users/profile`)
- Marketplace provider endpoints (`/api/marketplace/providers`)
- Health check endpoints (`/api/health`)

**Filtering Rules:**
- Excludes admin and internal endpoints
- Removes internal-only parameters and headers
- Includes only schemas referenced by public endpoints

### Internal Reference (`internal-reference.json`)

The internal reference specification contains the complete API surface:

- All public endpoints
- Admin and internal endpoints
- Debug and system endpoints
- Complete schema definitions

**Purpose:**
- Detect unintended public exposure of internal APIs
- Provide reference for internal development
- Enable comprehensive testing

## 📡 Event Schemas

### Webhook Envelope (`webhook-envelope.schema.json`)

Standard envelope for all webhook events sent to external systems:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "assessment.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": { /* event-specific payload */ },
  "signature": "sha256=...",
  "version": "1.0"
}
```

**Supported Event Types:**
- `assessment.completed` - Assessment workflow finished
- `assessment.started` - Assessment workflow initiated
- `user.registered` - New user account created
- `payment.processed` - Payment transaction completed
- `license.activated` - Software license activated
- `provider.matched` - Provider matched to client need

### SLA Breach Events (`sla-breach.schema.json`)

Schema for internal SLA monitoring and alerting:

```json
{
  "breach_type": "response_time",
  "service": "assessment-api",
  "threshold": 500,
  "actual": 1200,
  "user_id": "user123",
  "duration": "PT5M",
  "severity": "high"
}
```

## 🔧 Configuration

The pipeline behavior is controlled by `config.yml`:

```yaml
policy:
  allow_breaking_changes: false
  require_override_for_breaking: true
  max_breaking_changes: 0

openapi_filter:
  public_path_prefixes:
    - "/api/auth/"
    - "/api/assessments/"
  internal_only_paths:
    - "/api/admin/"
    - "/api/internal/"
```

## 🏃 GitHub Actions Integration

The pipeline runs automatically on:

- **Pull Requests** - Analyzes contract changes and comments results
- **Main Branch Pushes** - Updates canonical specifications
- **Nightly Schedule** - Validates contract integrity
- **Manual Dispatch** - Supports emergency overrides

### Workflow Triggers

```yaml
on:
  pull_request:
    paths: ['backend/**', 'contracts/**']
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:
    inputs:
      override_breaking_changes: # Emergency override
```

## 🧪 Testing

Run the contract diff pipeline tests:

```bash
# Run all contract diff tests
python tests/test_contract_diff_pipeline.py

# Run specific test categories
python -m unittest tests.test_contract_diff_pipeline.TestContractDiffAnalyzer
python -m unittest tests.test_contract_diff_pipeline.TestPolicyEnforcer
```

## 📚 Best Practices

### For API Development

1. **Design for backward compatibility** - Add optional fields, don't remove existing ones
2. **Version breaking changes** - Use API versioning for incompatible changes
3. **Test contract changes** - Run diff analysis before submitting PRs
4. **Document breaking changes** - Provide migration guides for consumers

### For Event Schema Changes

1. **Extend, don't modify** - Add new event types rather than changing existing ones
2. **Maintain envelope compatibility** - Keep the webhook envelope schema stable
3. **Version event schemas** - Use semantic versioning for schema changes
4. **Test event consumers** - Validate that webhook consumers handle changes

### for Policy Overrides

1. **Use sparingly** - Override only for critical fixes or planned breaking changes
2. **Document rationale** - Explain why the override is necessary
3. **Coordinate with consumers** - Notify API consumers of breaking changes
4. **Plan rollback strategy** - Have a plan to revert if issues arise

## 🔗 Related Documentation

- [API Development Guide](../docs/api-development.md)
- [Webhook Implementation Guide](../docs/webhooks.md)
- [SLA Monitoring Setup](../docs/sla-monitoring.md)
- [Emergency Response Procedures](../docs/emergency-procedures.md)

## 🤝 Contributing

When modifying contract specifications:

1. Understand the change classification (breaking/additive/informational)
2. Update relevant documentation and migration guides
3. Test changes against existing consumers
4. Follow the review process for contract changes
5. Monitor production impact after deployment

For questions or issues with the contract diff pipeline, please contact the platform team or open an issue in this repository.