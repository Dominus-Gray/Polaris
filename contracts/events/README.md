# Event Schema Contracts

This directory contains event schema contracts for webhook and SLA event validation.

## Directory Structure

```
events/
├── README.md                 # This file
├── webhooks/                 # Webhook payload schemas
│   ├── user-events.json     # User lifecycle events
│   ├── assessment-events.json # Assessment completion events
│   └── system-events.json   # System status events
├── sla-events/              # SLA breach and monitoring events
│   ├── performance-events.json
│   └── availability-events.json
└── schemas/                 # Common schema definitions
    ├── base-event.json      # Base event structure
    └── common-types.json    # Reusable type definitions
```

## Event Types

### Webhook Events
- **User Events**: Registration, login, profile updates
- **Assessment Events**: Session creation, completion, scoring
- **System Events**: Health checks, maintenance windows

### SLA Events  
- **Performance Events**: Response time breaches, throughput issues
- **Availability Events**: Service outages, degradation alerts

## Schema Validation

Event schemas follow JSON Schema specification and are validated as part of the contract diff pipeline.

## Usage

```bash
# Validate event schemas
python scripts/validate-event-schemas.py

# Generate event schema documentation
python scripts/generate-event-docs.py
```

## Contract Evolution

Event schema changes are subject to the same contract diff policies as API changes:
- **Breaking Changes**: Removing fields, changing types, adding required fields
- **Additive Changes**: Adding optional fields, new event types
- **Informational Changes**: Description updates, examples

All changes are tracked and reviewed through the contract diff pipeline.