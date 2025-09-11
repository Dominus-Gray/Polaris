# SLA Breach Detection & Notification System

## Overview

The SLA (Service Level Agreement) Breach Detection & Notification system provides automated monitoring and alerting for key Polaris platform reliability and performance metrics. This system establishes trust with customers through transparent reliability targets and creates internal feedback loops for platform hardening.

## Strategic Value

- **Customer Trust**: Transparent reliability targets build confidence with early customers
- **Internal Feedback**: Creates data-driven prioritization for platform improvements
- **Measurable KPIs**: Provides metrics for customer success and onboarding velocity
- **Enterprise Readiness**: Foundation for contract-backed SLAs and enterprise upsell

## Architecture

### Components

1. **SLA Catalog Data Model**: Defines service level objectives and targets
2. **Data Collectors**: Gather metrics from various platform workflows
3. **Evaluation Engine**: Assesses compliance and detects breaches
4. **Breach State Machine**: Manages breach lifecycle from detection to resolution
5. **Notification System**: Alerts administrators and stakeholders
6. **Observability Metrics**: Prometheus metrics for monitoring and dashboards

### Data Models

#### SLA Definition
```python
{
    "id": "uuid",
    "slug": "assessment_completion_latency",
    "description": "Assessment completion should average under 30 minutes",
    "objective_type": "latency|freshness|cadence|success_rate",
    "target_numeric": 30.0,
    "window_minutes": 1440,
    "threshold_operator": "lt|lte|gt|gte|eq",
    "enabled": true,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### SLA Instance
```python
{
    "id": "uuid",
    "sla_definition_id": "uuid",
    "workflow_id": "optional_workflow_id",
    "entity_id": "optional_entity_id",
    "status": "active|breached|resolved|disabled",
    "last_evaluated": "timestamp",
    "current_value": 45.0,
    "breach_count": 2,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### SLA Breach
```python
{
    "id": "uuid",
    "sla_instance_id": "uuid",
    "sla_definition_id": "uuid", 
    "breach_value": 45.0,
    "target_value": 30.0,
    "severity": "low|medium|high|critical",
    "status": "open|acknowledged|resolved",
    "detected_at": "timestamp",
    "acknowledged_at": "timestamp",
    "resolved_at": "timestamp",
    "resolution_notes": "text",
    "escalation_level": 0
}
```

## Default SLA Definitions

The system initializes with these default SLAs for key Polaris workflows:

### 1. Assessment Completion Latency
- **Objective**: Assessment completion should average under 30 minutes
- **Type**: Latency
- **Target**: 30 minutes
- **Evaluation Window**: 24 hours
- **Operator**: ≤ (less than or equal)

### 2. Consent Processing Latency  
- **Objective**: Consent requests should be processed within 2 hours
- **Type**: Latency
- **Target**: 120 minutes
- **Evaluation Window**: 24 hours
- **Operator**: ≤ (less than or equal)

### 3. Analytics Job Freshness
- **Objective**: Analytics jobs should run at least every 6 hours
- **Type**: Freshness
- **Target**: 360 minutes
- **Evaluation Window**: 6 hours
- **Operator**: ≤ (less than or equal)

### 4. Action Plan Update Cadence
- **Objective**: Action plan updates should occur weekly
- **Type**: Cadence
- **Target**: 7 days (10,080 minutes)
- **Evaluation Window**: 7 days
- **Operator**: ≤ (less than or equal)

## API Endpoints

### SLA Definition Management

- `POST /api/sla/definitions` - Create new SLA definition
- `GET /api/sla/definitions` - List all SLA definitions
- `GET /api/sla/definitions/{id}` - Get specific SLA definition
- `PUT /api/sla/definitions/{id}` - Update SLA definition
- `DELETE /api/sla/definitions/{id}` - Delete SLA definition

### SLA Monitoring

- `GET /api/sla/instances` - List SLA instances with current status
- `GET /api/sla/breaches` - List SLA breaches (filterable by status/severity)
- `PUT /api/sla/breaches/{id}/acknowledge` - Acknowledge breach
- `PUT /api/sla/breaches/{id}/resolve` - Resolve breach
- `GET /api/sla/metrics` - Get current SLA metrics and compliance
- `POST /api/sla/evaluate` - Manually trigger SLA evaluation
- `GET /api/sla/notifications` - List SLA notifications/alerts

### Authentication & Authorization

All SLA endpoints require `admin` or `navigator` role access.

## Monitoring & Observability

### Prometheus Metrics

The system exports these Prometheus metrics:

- `polaris_sla_breaches_total{sla_slug, severity, objective_type}` - Counter of total breaches
- `polaris_sla_compliance_ratio{sla_slug, objective_type}` - Gauge of compliance ratio (0-1)
- `polaris_sla_current_value{sla_slug, objective_type}` - Gauge of current measured value
- `polaris_sla_target_value{sla_slug, objective_type}` - Gauge of target value
- `polaris_sla_evaluation_duration_seconds` - Histogram of evaluation duration

### Background Monitoring

The system runs a background monitoring service that:

1. Evaluates all enabled SLA definitions every 5 minutes
2. Collects current metrics from data sources
3. Compares against targets and detects breaches
4. Updates Prometheus metrics
5. Triggers notifications for new breaches
6. Resolves breaches when compliance is restored

## Severity Calculation

### Latency & Freshness Metrics
- **Critical**: 3x or more over target
- **High**: 2x to 3x over target  
- **Medium**: 1.5x to 2x over target
- **Low**: Just over target

### Success Rate Metrics
- **Critical**: 50+ percentage points below target
- **High**: 25-50 percentage points below target
- **Medium**: 10-25 percentage points below target
- **Low**: Slightly below target

## Data Collection

### Assessment Completion Latency
Measures time from assessment creation to completion for assessments completed in the last 24 hours.

### Consent Processing Latency
Measures time from consent request creation to approval/denial for requests processed in the last 24 hours.

### Analytics Job Freshness
Measures time since the last completed analytics job execution.

### Action Plan Update Cadence
Measures frequency of action plan updates (implementation pending based on action plan data model).

## Notification System

Currently logs breaches and creates notification records for audit trail. The system can be extended to support:

- Email notifications via SendGrid
- Webhook notifications to external systems
- Dashboard alerts and badges
- Escalation workflows based on severity and time

## Testing

Run the SLA system tests:

```bash
cd /path/to/polaris
python -m pytest tests/test_sla_system.py -v
```

Tests cover:
- SLA evaluation logic
- Data collection functions
- Breach management
- Model validation
- Severity calculation

## Operations

### Manual SLA Evaluation
```bash
curl -X POST http://localhost:8000/api/sla/evaluate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Current Metrics
```bash
curl http://localhost:8000/api/sla/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Breach Status
```bash
curl http://localhost:8000/api/sla/breaches?status=open \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Configuration

### Environment Variables

The SLA system uses existing database and monitoring infrastructure:

- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- Standard Polaris environment configuration

### Customization

1. **Add New SLA Types**: Extend `SLADataCollector` with new metric collection methods
2. **Custom Notification Channels**: Enhance `SLABreachManager._send_breach_notifications`
3. **Evaluation Frequency**: Modify the monitoring loop interval in `SLAMonitorService`
4. **Severity Logic**: Customize `SLAEvaluationEngine.calculate_severity` for different metric types

## Future Enhancements

1. **Advanced Notifications**: Email, SMS, Slack integration
2. **Predictive Alerting**: ML-based trend analysis
3. **Customer-Facing Status Page**: Public SLA dashboard
4. **Contract Integration**: Link SLAs to customer contracts
5. **Automated Remediation**: Trigger scaling or recovery actions
6. **Historical Analysis**: Trend analysis and capacity planning
7. **Multi-tenancy**: Per-customer SLA definitions and targets

## Troubleshooting

### Common Issues

1. **No Metrics Collected**: Check data collection methods for database connection and schema
2. **Breaches Not Detected**: Verify SLA definitions are enabled and evaluation is running
3. **Missing Prometheus Metrics**: Ensure metrics endpoints are accessible
4. **Background Service Issues**: Check logs for monitoring loop errors

### Debugging

Enable debug logging to see detailed SLA evaluation information:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

View SLA evaluation logs:
```bash
grep "SLA" /path/to/logs/polaris.log
```