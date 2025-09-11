# Deprecation Policy

## Overview

This document outlines the deprecation policy for the Polaris API contract governance system. It defines the lifecycle for API changes, versioning requirements, and the process for safely removing deprecated features.

## Deprecation Lifecycle

### 1. Mark Phase
When a field, endpoint, or schema element needs to be removed:

1. **Add deprecation metadata** to the schema:
   ```yaml
   # OpenAPI example
   someField:
     type: string
     description: "Legacy field - use newField instead"
     deprecated: true
     x-status: deprecated
     x-sunset: "2025-04-15T00:00:00Z"
   ```

2. **Update documentation** with migration guidance
3. **Log the deprecation** in the version notes

### 2. Announce Phase
- **Communication**: Notify API consumers via:
  - Release notes
  - Developer documentation
  - Direct notification to known consumers
  - API response headers (when applicable)

- **Timeline**: Minimum 90-day notice period (configurable via `DEPRECATION_WINDOW_DAYS`)

### 3. Monitor Phase
- **Track usage** of deprecated endpoints/fields
- **Provide migration support** to consumers
- **Verify** consumers have migrated away from deprecated features

### 4. Remove Phase
- **Automated governance** ensures deprecation window has passed
- **Breaking change detection** allows removal only after proper deprecation
- **Version bumping** follows semantic versioning (major bump for removals)

## Classification System

### Breaking Changes (Major Version Bump)
- Removing endpoints, fields, or response codes
- Changing field types or formats
- Making optional fields required
- Removing required fields without replacement

### Additive Changes (Minor Version Bump)
- Adding new endpoints or fields
- Adding optional parameters
- Adding new response codes
- Expanding enum values

### Documentation Changes (Patch Version Bump)
- Updating descriptions, examples, or comments
- Clarifying existing behavior
- Adding usage examples

### Refactor/Internal Changes (No Version Bump)
- Implementation details marked with `x-internal`
- Code generation hints (`x-codegen`)
- Private extensions (`x-private`)

## Override Process

### When Overrides Are Needed
- Emergency breaking changes for security fixes
- Removing unused deprecated features ahead of schedule
- Breaking changes with pre-approved business justification

### Creating an Override
1. **Create override file**: `.deprecation-override.yml`
   ```yaml
   overrides:
     - issueNumber: "ISSUE-123"
       reason: "Security vulnerability requires immediate removal"
       impactedPaths:
         - "paths./legacy-endpoint.get"
         - "components.schemas.LegacyModel"
       approver: "security-team"
       expiresAt: "2025-02-01T00:00:00Z"
   ```

2. **Reference an approved issue** that documents:
   - Business justification
   - Impact assessment
   - Migration plan
   - Stakeholder approval

### Override Validation
- Must reference a valid GitHub issue
- Cannot use wildcards for bulk removals
- Requires explicit path listing
- Optional expiration for time-limited overrides

## Enforcement Modes

### Warn Mode (Default)
- **Reports violations** without blocking the build
- **Logs recommendations** for proper deprecation
- **Suitable for** development and staging environments

### Block Mode
- **Prevents deployment** of unapproved breaking changes
- **Requires override** or proper deprecation for breaking changes
- **Recommended for** production deployments

Set via environment variable:
```bash
export DIFF_ENFORCEMENT_MODE=block  # or 'warn'
```

## Version Management

### Semantic Versioning
Following [semver.org](https://semver.org/) standards:
- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: Additive changes (backward-compatible functionality)
- **PATCH**: Documentation and bug fixes (backward-compatible fixes)

### Version File Format
```json
{
  "apiVersion": "1.2.0",
  "updated": "2025-01-11T10:30:00Z",
  "notes": "Added new authentication endpoints, deprecated legacy login"
}
```

### Automated Version Bumping
The governance system automatically:
1. **Analyzes changes** in schema directories
2. **Calculates required version bump** based on classification
3. **Suggests new version** following semantic versioning
4. **Validates consistency** between changes and version updates

## Integration Points

### CI/CD Pipeline
- **Automated analysis** on every PR touching schemas
- **Governance report** uploaded as build artifact
- **Job summary** with change classification and recommendations

### Development Workflow
1. **Make schema changes** in `schemas/` or `events/` directories
2. **Run diff tool** locally: `npm run contract-diff`
3. **Review classification** and version impact
4. **Add deprecation metadata** for breaking changes
5. **Create PR** with governance checks

### Tooling Integration
- **Contract diff library**: Analyzes structural changes
- **Classification engine**: Categorizes impact of changes
- **Governance linter**: Enforces deprecation and versioning rules
- **GitHub Actions**: Automates analysis in CI/CD

## Configuration

### Environment Variables
```bash
# Enforcement mode: 'warn' or 'block'
DIFF_ENFORCEMENT_MODE=warn

# Deprecation window in days
DEPRECATION_WINDOW_DAYS=90

# Override file location
OVERRIDE_FILE_PATH=.deprecation-override.yml
```

### Tool Configuration
File: `tooling/contract-diff/config.json`
```json
{
  "docsOnlyPatterns": ["description", "example", "summary"],
  "ignoreOrdering": true,
  "deprecationFields": ["x-status", "x-sunset", "deprecated"],
  "deprecationWindowDays": 90,
  "enforcement": "warn"
}
```

## Communication Channels

### Internal Notifications
- **Build status** via CI/CD pipeline
- **PR comments** with change summary (future enhancement)
- **Slack/Teams integration** for breaking change alerts (future enhancement)

### External Communications
- **Release notes** with deprecation announcements
- **API documentation** with migration guides
- **Developer newsletters** for major changes
- **Direct outreach** to known API consumers

## Monitoring and Metrics

### Tracking (Future Enhancement)
- `contract_breaking_attempts_blocked_total`: Counter of blocked changes
- `contract_deprecation_window_violations`: Premature removals
- `contract_version_bumps_by_type`: Version bump frequency by type

### Reporting
- **Monthly governance reports** with deprecation status
- **API health dashboards** with breaking change trends
- **Consumer impact assessments** for major versions

## Best Practices

### For API Designers
1. **Plan for deprecation** when designing new features
2. **Use extension points** to avoid breaking changes
3. **Version strategically** with clear migration paths
4. **Document thoroughly** with examples and use cases

### For API Consumers
1. **Monitor deprecation notices** in API responses and documentation
2. **Test against new versions** early and often
3. **Migrate proactively** before deprecation deadlines
4. **Provide feedback** on proposed breaking changes

## Examples

### Proper Deprecation Flow
1. **Initial Implementation** (v1.0.0):
   ```yaml
   UserProfile:
     properties:
       username:
         type: string
   ```

2. **Add New Field** (v1.1.0):
   ```yaml
   UserProfile:
     properties:
       username:
         type: string
       email:
         type: string
   ```

3. **Deprecate Old Field** (v1.2.0):
   ```yaml
   UserProfile:
     properties:
       username:
         type: string
         deprecated: true
         x-status: deprecated
         x-sunset: "2025-04-15T00:00:00Z"
         description: "Use email field instead"
       email:
         type: string
   ```

4. **Remove Deprecated Field** (v2.0.0):
   ```yaml
   UserProfile:
     properties:
       email:
         type: string
   ```

### Override Example
```yaml
# .deprecation-override.yml
overrides:
  - issueNumber: "SEC-456"
    reason: "Security vulnerability in legacy authentication"
    impactedPaths:
      - "paths./auth/legacy.post"
      - "components.schemas.LegacyToken"
    approver: "security-team"
    expiresAt: "2025-02-01T00:00:00Z"
```

## Governance Committee

### Responsibilities
- **Review override requests** for breaking changes
- **Approve emergency changes** outside normal deprecation window
- **Update policy** based on operational experience
- **Resolve disputes** about change classification

### Escalation Process
1. **Developer raises concern** about governance decision
2. **Team lead reviews** classification and policy application
3. **Architecture review** for complex or disputed cases
4. **Governance committee** for final decision on overrides

---

*This policy is version controlled and subject to the same governance processes it defines.*