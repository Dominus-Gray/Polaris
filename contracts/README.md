# Polaris Contract Repository

This directory contains the canonical API and event contracts for the Polaris platform.

## Directory Structure

### `/contracts/openapi/`
Contains OpenAPI specifications for API contract management:

- `public-v1.json` - Public API specification snapshot (filtered endpoints only)
- `internal-reference.json` - Internal API reference (optional, for detecting unintended exposure)

### `/contracts/events/`
Contains event schema contracts for webhook and event system validation:

- Event schema definitions (to be implemented)
- Webhook payload specifications 
- SLA event schemas

## Contract Diff Pipeline

This directory supports an automated contract diff pipeline that:

1. **Generates Snapshots**: Extracts current API specs from the running FastAPI application
2. **Compares Changes**: Analyzes differences between current and previous contract versions
3. **Classifies Impact**: Categorizes changes as breaking, additive, or informational
4. **Enforces Policy**: Blocks or warns on contract violations with override capabilities

## Usage

The contract diff pipeline is integrated into CI/CD and can be run manually:

```bash
# Generate current API snapshot
python scripts/generate-openapi-spec.py

# Compare against existing contracts
python scripts/diff-contracts.py

# Validate contract compliance
python scripts/validate-contracts.py
```

See individual script documentation for detailed usage instructions.