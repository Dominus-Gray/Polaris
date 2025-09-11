# Webhook Infrastructure Documentation

## Overview

The Polaris platform includes a comprehensive webhook infrastructure that enables external systems and partners to react to key domain and SLA events in near real-time. This system provides secure outbound event delivery with HMAC signatures, automatic retry logic, event versioning, and observability features.

## Architecture

### Core Components

1. **Webhook Endpoints**: Organization-scoped webhook subscriptions
2. **Webhook Events**: Standardized event envelope with versioning
3. **Delivery System**: Background worker with retry logic and failure tracking
4. **Security Layer**: HMAC SHA256 signing for payload integrity

### Database Schema

#### webhook_endpoints
```sql
{
  "id": "UUID (Primary Key)",
  "org_id": "UUID (Nullable for global webhooks)",
  "name": "TEXT (Display name)",
  "url": "TEXT (Webhook endpoint URL)",
  "secret_hash": "TEXT (HMAC secret hash)",
  "active": "BOOLEAN (Default: true)",
  "created_at": "TIMESTAMP",
  "updated_at": "TIMESTAMP", 
  "events": "TEXT[] (Subscribed event types)",
  "failure_count": "INT (Default: 0)",
  "last_failure_at": "TIMESTAMP (Nullable)",
  "last_success_at": "TIMESTAMP (Nullable)",
  "auth_type": "TEXT (Default: 'hmac')"
}
```

#### webhook_events
```sql
{
  "id": "UUID (Primary Key)",
  "type": "TEXT (Event type)",
  "version": "INT (Default: 1)",
  "payload": "JSONB (Event data)",
  "created_at": "TIMESTAMP",
  "delivered_count": "INT (Default: 0)"
}
```

#### webhook_delivery_attempts
```sql
{
  "id": "UUID (Primary Key)",
  "event_id": "UUID (Foreign Key to webhook_events)",
  "endpoint_id": "UUID (Foreign Key to webhook_endpoints)",
  "attempt_number": "INT",
  "status": "TEXT (PENDING|DELIVERED|FAILED|GAVE_UP)",
  "response_status": "INT (Nullable)",
  "response_body": "TEXT (Nullable, truncated to 1000 chars)",
  "error": "TEXT (Nullable, truncated to 1000 chars)",
  "latency_ms": "INT (Nullable)",
  "created_at": "TIMESTAMP",
  "next_attempt_at": "TIMESTAMP (Nullable)"
}
```

## API Endpoints

### Webhook Management

#### Create Webhook Endpoint
```http
POST /api/webhooks/endpoints
Authorization: Bearer <agency_token>
Content-Type: application/json

{
  "org_id": "optional_org_id",
  "name": "My Webhook",
  "url": "https://api.example.com/webhook",
  "events": ["assessment.finalized", "action_plan.updated"],
  "secret": "optional_custom_secret"
}
```

Response:
```json
{
  "id": "webhook_endpoint_id",
  "secret": "generated_or_provided_secret",
  "message": "Webhook endpoint created successfully"
}
```

#### List Webhook Endpoints
```http
GET /api/webhooks/endpoints
Authorization: Bearer <agency_token>
```

#### Get Webhook Endpoint
```http
GET /api/webhooks/endpoints/{endpoint_id}
Authorization: Bearer <agency_token>
```

#### Update Webhook Endpoint
```http
PUT /api/webhooks/endpoints/{endpoint_id}
Authorization: Bearer <agency_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "events": ["assessment.finalized"],
  "active": false
}
```

#### Delete Webhook Endpoint
```http
DELETE /api/webhooks/endpoints/{endpoint_id}
Authorization: Bearer <agency_token>
```

#### List Webhook Events
```http
GET /api/webhooks/events?limit=50
Authorization: Bearer <agency_token>
```

#### Test Webhook Endpoint
```http
POST /api/webhooks/test/{endpoint_id}
Authorization: Bearer <agency_token>
```

## Event Types

### Domain Events

#### assessment.created
Triggered when a new assessment session is started.
```json
{
  "assessment_id": "string",
  "user_id": "string", 
  "session_type": "standard|tier",
  "area_id": "string (for tier assessments)"
}
```

#### assessment.finalized
Triggered when an assessment is completed.
```json
{
  "assessment_id": "string",
  "user_id": "string",
  "completion_score": "number",
  "completed_questions": "number",
  "total_questions": "number",
  "tier_level": "number (for tier assessments)"
}
```

#### action_plan.updated
Triggered when an action plan is modified.
```json
{
  "plan_id": "string",
  "user_id": "string",
  "updated_sections": "array<string>"
}
```

#### consent.granted
Triggered when user consent is provided.
```json
{
  "user_id": "string",
  "consent_type": "string",
  "granted_at": "ISO8601 timestamp"
}
```

#### analytics.projection.completed
Triggered when analytics calculations finish.
```json
{
  "projection_id": "string",
  "user_id": "string",
  "metrics": "object"
}
```

### Reliability Events

#### sla.breach.opened
Triggered when an SLA threshold is breached.
```json
{
  "sla_id": "string",
  "metric": "string",
  "threshold": "number",
  "actual_value": "number"
}
```

#### sla.breach.closed
Triggered when an SLA breach is resolved.
```json
{
  "sla_id": "string",
  "resolution_time": "number (minutes)",
  "resolved_by": "string"
}
```

### Security Events (Internal Only)

#### key_rotation.started
#### key_rotation.completed
Internal-only events for key rotation tracking.

## Event Envelope Structure

All webhook events follow a standardized envelope format:

```json
{
  "id": "unique_event_id",
  "type": "event.type.name",
  "occurred_at": "2025-01-20T10:30:00.000Z",
  "version": 1,
  "data": {
    // Event-specific data
  },
  "meta": {
    "source": "polaris",
    "schema": "polaris.event/1"
  }
}
```

## Security

### HMAC Signature Verification

All webhook payloads are signed using HMAC SHA256. The signature is included in the `X-Polaris-Signature` header:

```
X-Polaris-Signature: sha256=<hex_encoded_signature>
```

#### Verification Process (Python)
```python
import hashlib
import hmac
import secrets

def verify_webhook_signature(payload_bytes, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    expected_full = f"sha256={expected_signature}"
    return secrets.compare_digest(signature, expected_full)
```

#### Verification Process (Node.js)
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payloadBuffer, signature, secret) {
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(payloadBuffer)
        .digest('hex');
    const expectedFull = `sha256=${expectedSignature}`;
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedFull)
    );
}
```

### Best Practices

1. **Always verify signatures** before processing webhook payloads
2. **Use HTTPS endpoints** for webhook URLs
3. **Implement idempotency** using the event `id` field
4. **Handle retries gracefully** - return 2xx status codes for successful processing
5. **Process webhooks asynchronously** to avoid timeouts
6. **Log webhook activity** for debugging and monitoring

## Delivery Reliability

### Retry Logic

Failed webhook deliveries are automatically retried with exponential backoff:

- Attempt 1: Immediate
- Attempt 2: 2 minutes later
- Attempt 3: 4 minutes later  
- Attempt 4: 8 minutes later
- Attempt 5: 16 minutes later

After 5 failed attempts, the delivery is marked as `GAVE_UP`.

### Status Codes

- `PENDING`: Delivery attempt scheduled
- `DELIVERED`: Successfully delivered (2xx response)
- `FAILED`: Delivery failed (will retry if under max attempts)
- `GAVE_UP`: Maximum retry attempts exceeded

### Timeouts

HTTP requests timeout after 30 seconds. Endpoints should respond quickly to avoid timeouts.

## Monitoring and Observability

### Metrics Tracked

- Delivery success/failure rates
- Response latencies
- Retry attempt counts
- Endpoint failure counts

### Logs

All webhook activities are logged with structured data:
- Event publication
- Delivery attempts  
- Success/failure outcomes
- Error details

## Implementation Examples

### Creating a Webhook Endpoint

```python
import requests

# Create webhook endpoint
response = requests.post(
    "https://api.polaris.example.com/api/webhooks/endpoints",
    headers={"Authorization": "Bearer <your_token>"},
    json={
        "name": "Assessment Notifications",
        "url": "https://your-api.com/polaris-webhooks",
        "events": ["assessment.finalized", "action_plan.updated"]
    }
)

endpoint_data = response.json()
webhook_secret = endpoint_data["secret"]  # Store this securely!
```

### Processing Webhooks

```python
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route('/polaris-webhooks', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Polaris-Signature')
    if not verify_signature(request.data, signature, WEBHOOK_SECRET):
        abort(401)
    
    # Process event
    event = request.json
    event_type = event['type']
    event_data = event['data']
    
    if event_type == 'assessment.finalized':
        handle_assessment_completion(event_data)
    elif event_type == 'action_plan.updated':
        handle_action_plan_update(event_data)
    
    return '', 200

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    expected_full = f"sha256={expected}"
    return hmac.compare_digest(signature, expected_full)
```

## Troubleshooting

### Common Issues

1. **Signature Verification Fails**
   - Ensure you're using the correct webhook secret
   - Verify you're hashing the raw payload bytes, not JSON
   - Check for consistent encoding (UTF-8)

2. **Delivery Timeouts**
   - Endpoint must respond within 30 seconds
   - Process webhooks asynchronously if needed
   - Return 2xx status code quickly

3. **Missing Events**
   - Check webhook endpoint is active
   - Verify event type subscription
   - Check organization scope (org_id)

4. **High Failure Rates**
   - Monitor endpoint health
   - Check for 5xx server errors
   - Implement proper error handling

### Support

For webhook-related issues:
1. Check delivery attempt logs via API
2. Verify endpoint configuration
3. Test endpoint connectivity
4. Contact platform support with event IDs

## Migration and Versioning

### Event Versioning

Events include a `version` field for schema evolution:
- Version 1: Initial implementation
- Future versions will maintain backward compatibility
- Deprecated fields will be marked before removal

### API Versioning

The webhook API is versioned as part of the main platform API:
- Current: `/api/webhooks/*`
- Future versions will be clearly documented