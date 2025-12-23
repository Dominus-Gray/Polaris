# Contract Governance System

A comprehensive governance foundation for API contract management with automated diff analysis, semantic versioning, and deprecation policy enforcement.

## Overview

This system provides:
- **Contract Diff Analysis**: Automated detection and classification of schema changes
- **Semantic Versioning**: Automatic version bump calculations based on change impact
- **Deprecation Policy**: Enforced deprecation workflows with configurable windows
- **GitHub Integration**: CI/CD workflow for automated governance checks
- **Flexible Enforcement**: Warn or block modes with override mechanisms

## Quick Start

### 1. Analyze Schema Changes

```bash
# Compare schemas and generate diff report
cd tooling/contract-diff
node lib/run.js \
  --old-dir /path/to/old/schemas \
  --new-dir /path/to/new/schemas \
  --output contract-diff-report.json
```

### 2. Run Governance Linter

```bash
# Enforce governance rules
DIFF_ENFORCEMENT_MODE=warn node tooling/contract-linter/enforce.js contract-diff-report.json
```

### 3. GitHub Actions Integration

The system automatically runs on PRs touching:
- `schemas/**`
- `events/**` 
- `tooling/contract-diff/**`
- `tooling/contract-linter/**`

## Directory Structure

```
├── .github/workflows/
│   └── contract-governance.yml     # CI/CD workflow
├── docs/
│   └── deprecation-policy.md       # Governance policy documentation
├── schemas/
│   └── openapi/
│       ├── version.json            # API version tracking
│       └── *.json                  # OpenAPI schemas
├── events/
│   └── *.json                      # Event schemas
├── tooling/
│   ├── contract-diff/              # Diff analysis library
│   │   ├── src/                   
│   │   │   ├── loadSchemas.ts      # Schema loading and normalization
│   │   │   ├── diffSchemas.ts      # Structural diff generation
│   │   │   ├── classify.ts         # Change classification engine
│   │   │   ├── writeReport.ts      # Report generation and versioning
│   │   │   └── run.ts              # CLI entry point
│   │   ├── tests/
│   │   │   └── classify.test.ts    # Unit tests
│   │   └── config.json             # Tool configuration
│   └── contract-linter/
│       └── enforce.ts              # Governance rule enforcement
├── tests/integration/              # Integration test scenarios
└── .deprecation-override.example.yml  # Override template
```

## Change Classification

### Breaking Changes (Major Version Bump)
- ❌ Removing endpoints, schemas, or fields
- ❌ Changing field types or formats  
- ❌ Making optional fields required
- ❌ Removing response codes
- ❌ Removing required fields

### Additive Changes (Minor Version Bump)
- ✅ Adding new endpoints or fields
- ✅ Adding optional parameters
- ✅ Adding new response codes
- ✅ Making required fields optional
- ✅ Expanding enum values

### Documentation Changes (Patch Version Bump)
- 📝 Updating descriptions, examples, summaries
- 📝 Clarifying existing behavior
- 📝 Adding usage examples

### Refactor/Internal Changes (No Version Bump)
- 🔧 Implementation details (`x-internal`, `x-codegen`)
- 🔧 Private extensions (`x-private`)
- 🔧 Build/tooling configurations

## Deprecation Workflow

### 1. Mark Phase
Add deprecation metadata to schema:

```yaml
legacyField:
  type: string
  deprecated: true
  x-status: deprecated
  x-sunset: "2025-04-15T00:00:00Z"
  description: "Use newField instead"
```

### 2. Announce Phase
- Update documentation with migration guides
- Notify API consumers
- Provide transition timeline (default: 90 days)

### 3. Remove Phase
After deprecation window expires:
- Removal is allowed without breaking change classification
- Governance system validates proper deprecation metadata

## Configuration

### Environment Variables

```bash
# Enforcement mode: 'warn' (default) or 'block'
export DIFF_ENFORCEMENT_MODE=warn

# Deprecation window in days (default: 90)
export DEPRECATION_WINDOW_DAYS=90

# Override file path (default: .deprecation-override.yml)
export OVERRIDE_FILE_PATH=.deprecation-override.yml
```

### Tool Configuration

Edit `tooling/contract-diff/config.json`:

```json
{
  "docsOnlyPatterns": ["description", "example", "summary"],
  "ignoreOrdering": true,
  "deprecationFields": ["x-status", "x-sunset", "deprecated"],
  "deprecationWindowDays": 90,
  "enforcement": "warn"
}
```

## Override Mechanism

Create `.deprecation-override.yml` for approved breaking changes:

```yaml
overrides:
  - issueNumber: "SEC-123"
    reason: "Security vulnerability requires immediate removal"
    impactedPaths:
      - "paths./legacy-endpoint.get"
      - "components.schemas.LegacyModel"
    approver: "security-team"
    expiresAt: "2025-02-01T00:00:00Z"
```

## Examples

### Example 1: Documentation Update

```bash
# Only description changes - classified as docsOnly
{
  "breaking": [],
  "additive": [],
  "docsOnly": [
    {
      "type": "modify",
      "path": ["api.json", "info", "description"],
      "oldValue": "Original description",
      "newValue": "Updated description"
    }
  ],
  "version": {
    "requiredBump": "patch",
    "suggestedNew": "1.0.1"
  }
}
```

### Example 2: Breaking Change

```bash
# Field removal - classified as breaking
{
  "breaking": [
    {
      "type": "remove", 
      "path": ["api.json", "components", "schemas", "User", "properties", "legacyField"],
      "oldValue": {"type": "string", "deprecated": true}
    }
  ],
  "version": {
    "requiredBump": "major",
    "suggestedNew": "2.0.0"
  }
}
```

## Testing

### Unit Tests
```bash
cd tooling/contract-diff
npm test
```

### Integration Tests
```bash
bash tests/integration/run-integration-tests.sh
```

### Acceptance Criteria Demo
```bash
./demo-governance-system.sh
```

## Version Management

### Version File Format
`schemas/openapi/version.json`:
```json
{
  "apiVersion": "1.0.0",
  "updated": "2025-01-11T10:30:00Z", 
  "notes": "Initial API version"
}
```

### Automatic Version Bumping
The system calculates required version bumps based on:
- **Major**: Breaking changes
- **Minor**: Additive changes  
- **Patch**: Documentation changes
- **None**: Refactor/internal changes

## CI/CD Integration

### GitHub Actions Workflow
- Automatically runs on schema changes
- Generates diff reports
- Uploads artifacts for review
- Posts job summaries
- Enforces governance rules

### Enforcement Modes
- **Warn Mode**: Reports violations without blocking
- **Block Mode**: Prevents deployment of unapproved breaking changes

## Best Practices

### For API Designers
1. Plan for deprecation when designing new features
2. Use extension points to avoid breaking changes
3. Version strategically with clear migration paths
4. Document thoroughly with examples

### For API Consumers  
1. Monitor deprecation notices
2. Test against new versions early
3. Migrate proactively before deadlines
4. Provide feedback on proposed changes

## Troubleshooting

### Common Issues

1. **Schema not detected**: Ensure files are in `schemas/` or `events/` directories
2. **Classification incorrect**: Check `config.json` patterns and deprecation fields
3. **Version bump wrong**: Verify change classification is accurate
4. **Linter failing**: Check enforcement mode and override files

### Debug Commands
```bash
# Generate detailed diff report
node tooling/contract-diff/lib/run.js --old-dir old --new-dir new --output debug.json

# Check classification details
cat debug.json | jq '.breaking[]'

# Test linter in different modes
DIFF_ENFORCEMENT_MODE=warn node tooling/contract-linter/enforce.js debug.json
DIFF_ENFORCEMENT_MODE=block node tooling/contract-linter/enforce.js debug.json
```

## Contributing

### Adding New Classification Rules
1. Update `classify.ts` with new detection logic
2. Add unit tests in `tests/classify.test.ts`
3. Update documentation with examples
4. Test against real schema changes

### Extending Tool Functionality
1. Follow existing patterns in the codebase
2. Maintain backward compatibility
3. Add appropriate tests
4. Update configuration options

## Support

- **Documentation**: See `docs/deprecation-policy.md` for detailed policy
- **Examples**: Check `tests/integration/` for usage scenarios  
- **Issues**: Reference GitHub issues in override files
- **Questions**: Create GitHub issues for clarification

---

*This governance system enforces API contract safety while maintaining developer productivity through automated tooling and clear policy guidelines.*