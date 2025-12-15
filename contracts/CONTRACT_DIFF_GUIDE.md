# Automated Spec & Event Contract Diff Pipeline

## Overview

The Automated Spec & Event Contract Diff Pipeline provides continuous validation of API and event contracts to prevent accidental breaking changes and maintain backward compatibility. The system automatically generates snapshots, compares changes, classifies impact, and enforces policies.

## Features

- **Automatic OpenAPI Spec Generation**: Extracts current API specifications from FastAPI application
- **Public/Internal Filtering**: Separates public-facing APIs from internal/admin endpoints  
- **Breaking Change Detection**: Identifies changes that could break existing integrations
- **Impact Classification**: Categorizes changes as breaking, additive, or informational
- **CI/CD Integration**: Automated validation on pull requests and nightly monitoring
- **Policy Enforcement**: Configurable rules with override capabilities
- **Multiple Output Formats**: Text, JSON, and YAML reporting
- **Event Schema Validation**: Contract management for webhook and SLA events

## Quick Start

### 1. Generate Current API Specification

```bash
# Generate both public and internal reference specs
python scripts/generate-openapi-spec.py

# Generate only public API spec
python scripts/generate-openapi-spec.py --public-only

# Save to custom directory
python scripts/generate-openapi-spec.py --output-dir ./api-specs/
```

### 2. Compare Contract Changes

```bash
# Compare against committed baseline
python scripts/diff-contracts.py \
  --old-spec contracts/openapi/public-v1.json \
  --new-spec /tmp/current-spec.json

# Generate JSON report
python scripts/diff-contracts.py \
  --old-spec contracts/openapi/public-v1.json \
  --new-spec /tmp/current-spec.json \
  --format json \
  --output contract-diff-report.json
```

### 3. Validate Pipeline

```bash
# Run full validation suite
python scripts/validate-contracts.py

# Test breaking change detection
python scripts/validate-contracts.py --test-breaking --verbose
```

## Directory Structure

```
contracts/
├── README.md                          # This documentation
├── openapi/                           # OpenAPI specifications
│   ├── public-v1.json                # Public API contract (filtered)
│   └── internal-reference.json       # Full API reference (optional)
├── events/                            # Event schema contracts
│   ├── README.md                     # Event documentation
│   ├── webhooks/                     # Webhook payload schemas
│   ├── sla-events/                   # SLA monitoring events
│   └── schemas/                      # Common schema definitions
└── policies/                         # Contract policies (future)

scripts/
├── generate-openapi-spec.py          # OpenAPI spec generator
├── generate-openapi-mock.py          # Mock generator (for testing)
├── diff-contracts.py                 # Contract diff engine
└── validate-contracts.py             # Pipeline validator

.github/workflows/
└── contract-diff.yml                 # CI/CD integration
```

## CI/CD Integration

The pipeline integrates with GitHub Actions to provide:

### Pull Request Validation
- Automatic contract diff analysis on PR creation/updates
- Comments with detailed change summaries
- Breaking change detection and blocking
- Override mechanisms with commit message flags

### Nightly Monitoring  
- Scheduled contract drift detection
- Automatic snapshot updates via pull requests
- Monitoring and alerting for contract violations

### Manual Triggers
- On-demand pipeline execution
- Force contract snapshot updates
- Testing and validation workflows

## Change Classification

### Breaking Changes ❌
Changes that could break existing integrations:
- Removing API endpoints or methods
- Removing required parameters or response fields
- Changing parameter types or constraints
- Making optional parameters required
- Removing successful response codes (2xx)

### Additive Changes ✅
New functionality that maintains backward compatibility:
- Adding new API endpoints or methods
- Adding optional parameters
- Adding response fields
- Adding new response codes
- Adding new event types or optional fields

### Informational Changes ℹ️
Changes that don't affect functionality:
- Documentation updates
- Description changes
- Version number updates
- Operation ID changes
- Example updates

## Policy Enforcement

### Default Policies
- **Breaking Changes**: Block PR merge, require manual review
- **Additive Changes**: Allow but notify stakeholders
- **Informational Changes**: Allow without restriction

### Override Mechanisms
1. **Commit Message Override**: Add `[skip contract-diff]` to bypass enforcement
2. **Repository Settings**: Configure branch protection rules
3. **Emergency Override**: Manual approval workflow for critical fixes

### Configuration
Policy enforcement can be customized via:
- GitHub repository settings
- Workflow environment variables
- Configuration files (future enhancement)

## Output Formats

### Text Format
Human-readable diff reports with:
- Executive summary of changes
- Detailed change listings with locations
- Severity indicators and recommendations
- Metadata about the comparison

### JSON Format
Machine-readable reports for:
- Integration with other tools
- Automated processing and alerting
- Storage and historical analysis
- Custom reporting and dashboards

### Example JSON Output
```json
{
  "summary": {
    "total_changes": 5,
    "breaking_changes": 1,
    "additive_changes": 3,
    "informational_changes": 1
  },
  "changes": [
    {
      "type": "breaking",
      "category": "path",
      "location": "/api/users",
      "description": "Path '/api/users' was removed",
      "severity": "high"
    }
  ],
  "metadata": {
    "compared_at": "2025-09-11T04:49:19.997170Z",
    "old_spec_version": "1.0.0",
    "new_spec_version": "1.1.0"
  }
}
```

## Best Practices

### API Development
1. **Design First**: Create OpenAPI specs before implementation
2. **Version Semantically**: Use semantic versioning for API changes
3. **Additive Changes**: Prefer adding new endpoints over modifying existing ones
4. **Backward Compatibility**: Maintain compatibility for at least 2 major versions
5. **Documentation**: Keep descriptions and examples up to date

### Contract Management
1. **Regular Updates**: Keep contract snapshots current with implementation
2. **Review Process**: Establish approval workflows for breaking changes
3. **Testing**: Validate changes against existing client integrations
4. **Communication**: Notify API consumers of upcoming changes
5. **Monitoring**: Track API usage to understand impact of changes

### Emergency Procedures
1. **Critical Fixes**: Use override mechanisms sparingly and with justification
2. **Rollback Plans**: Maintain ability to revert breaking changes quickly
3. **Post-Incident**: Review and update contracts after emergency changes
4. **Communication**: Immediately notify affected stakeholders

## Troubleshooting

### Common Issues

#### "No module named 'fastapi'" Error
```bash
# Install required dependencies
pip install fastapi uvicorn pydantic motor pymongo python-dotenv \
           passlib python-jose python-multipart aiofiles
```

#### Contract Diff Shows No Changes
- Verify specification files exist and are valid JSON
- Check file paths are correct
- Ensure specifications have different content
- Run with `--verbose` flag for detailed logging

#### Breaking Change False Positives
- Review change classification logic
- Consider using `--strict` mode for stricter validation
- Update policy rules if needed
- Use override mechanisms for legitimate edge cases

#### CI/CD Pipeline Failures
- Check GitHub Actions logs for specific errors
- Verify required secrets and permissions are configured
- Ensure workflow syntax is valid
- Test scripts locally before committing

### Getting Help

1. **Documentation**: Review this guide and inline script help
2. **Validation**: Run `python scripts/validate-contracts.py --verbose`
3. **Logs**: Check CI/CD logs for detailed error messages
4. **Testing**: Use mock generator for safe testing
5. **Support**: Contact development team for complex issues

## Roadmap

### Phase 1: Core Implementation ✅
- [x] OpenAPI spec generation and filtering
- [x] Contract diff engine with change classification
- [x] CI/CD integration with GitHub Actions
- [x] Basic policy enforcement and overrides
- [x] Validation and testing framework

### Phase 2: Enhanced Features 🚧
- [ ] Event schema validation and diff
- [ ] Advanced policy configuration
- [ ] Integration with external tools (Slack, email)
- [ ] Historical change tracking and analytics
- [ ] Performance optimization

### Phase 3: Enterprise Features 📋
- [ ] Multi-environment contract management
- [ ] SDK generation from contracts
- [ ] Advanced monitoring and alerting
- [ ] Integration with API gateways
- [ ] Custom rule engine

## Contributing

To contribute to the contract diff pipeline:

1. **Setup**: Follow the quick start guide to set up the environment
2. **Testing**: Run validation suite before submitting changes
3. **Documentation**: Update this guide for new features
4. **Standards**: Follow existing code style and patterns
5. **Review**: Submit pull requests for team review

## License

This contract diff pipeline is part of the Polaris platform and follows the same licensing terms.