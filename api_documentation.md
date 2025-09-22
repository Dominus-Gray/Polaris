# Polaris Platform API Documentation

## 🌟 Polaris API Reference

**Version**: 2.0.0  
**Base URL**: `https://your-domain.com/api`  
**Authentication**: Bearer JWT Token  

---

## 📚 Quick Start Guide

### 1. Authentication
```bash
# Login to get JWT token
curl -X POST "https://your-domain.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "role": "client"
  }
}
```

### 2. Making Authenticated Requests
```bash
# Use the JWT token in Authorization header
curl -X GET "https://your-domain.com/api/home/client" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔐 Authentication Endpoints

### POST /auth/login
**Description**: Authenticate user and receive JWT token  
**Rate Limit**: 10 requests per 5 minutes  

**Request Body**:
```json
{
  "email": "string",
  "password": "string"
}
```

**Response**: JWT token and user information

### POST /auth/register
**Description**: Register new user account  
**Rate Limit**: 5 requests per hour  

**Request Body**:
```json
{
  "email": "string",
  "password": "string",
  "role": "client|provider|navigator|agency",
  "license_code": "string (required for clients)",
  "terms_accepted": true
}
```

### GET /auth/me
**Description**: Get current user information  
**Authentication**: Required  

**Response**: Current user profile and permissions

---

## 📊 Assessment System API

### GET /assessment/schema/tier-based
**Description**: Get tier-based assessment schema  
**Authentication**: Required  

**Response**: Complete assessment structure with 10 business areas

### POST /assessment/tier-session
**Description**: Create new tier-based assessment session  
**Authentication**: Required (client role)  

**Request Body**:
```json
{
  "area_id": "area1",
  "tier_level": 1
}
```

### POST /assessment/tier-session/{session_id}/response
**Description**: Submit assessment responses  
**Authentication**: Required  

**Request Body**:
```json
{
  "responses": [
    {
      "question_id": "string",
      "response": "compliant|nearing_completion|incomplete",
      "evidence_notes": "string"
    }
  ]
}
```

---

## 🤝 Service Provider Marketplace API

### POST /service-requests/professional-help
**Description**: Create service request for professional help  
**Authentication**: Required (client role)  

**Request Body**:
```json
{
  "area_id": "area1",
  "budget_range": "1000-5000",
  "timeline": "2-4 weeks",
  "description": "string",
  "priority": "high|medium|low"
}
```

### GET /service-requests/{request_id}/responses/enhanced
**Description**: Get enhanced provider responses for service request  
**Authentication**: Required  

**Response**: Provider proposals with enhanced data

### POST /provider/respond-to-request
**Description**: Submit provider response to service request  
**Authentication**: Required (provider role)  

**Request Body**:
```json
{
  "request_id": "string",
  "proposed_fee": 2500.00,
  "estimated_timeline": "4-6 weeks",
  "proposal_note": "string"
}
```

---

## 🤖 AI-Powered Features API

### POST /ai/coach/conversation
**Description**: Conversational AI coaching for procurement readiness  
**Authentication**: Required  

**Request Body**:
```json
{
  "message": "How do I improve my financial management?",
  "session_id": "coach_session_123",
  "context_area": "area2"
}
```

**Response**:
```json
{
  "response": "To improve financial management for procurement readiness...",
  "session_id": "coach_session_123",
  "context": {
    "completion_percentage": 45.0,
    "assessment_completion": 4
  },
  "suggestions": [
    "Review cash flow requirements",
    "Implement accounting controls"
  ]
}
```

### GET /ai/recommendations/{role}
**Description**: Get role-specific AI recommendations  
**Authentication**: Required  

**Parameters**:
- `role`: client|provider|agency|navigator

**Response**: Contextual recommendations based on user progress

### POST /ai/predictive-analytics
**Description**: Generate predictive analytics for success probability  
**Authentication**: Required (navigator, agency, admin roles)  

**Request Body**:
```json
{
  "type": "success_prediction",
  "target_user_id": "user-uuid"
}
```

---

## 🏢 Resource Partner (RP) CRM-lite API

### GET /v2/rp/requirements/all
**Description**: Get all RP requirement configurations  
**Authentication**: Required  

**Response**: List of RP types and their required fields

### POST /v2/rp/leads
**Description**: Create new RP lead with data package  
**Authentication**: Required (client role)  

**Request Body**:
```json
{
  "rp_type": "lenders",
  "rp_id": "optional-rp-identifier"
}
```

### GET /v2/rp/package-preview
**Description**: Preview data package for RP sharing  
**Authentication**: Required (client role)  

**Parameters**:
- `rp_type`: Type of resource partner

**Response**: Current data package and missing prerequisites

---

## 💬 Real-Time Collaboration API

### POST /chat/send
**Description**: Send message in chat context  
**Authentication**: Required  

**Request Body**:
```json
{
  "chat_id": "service_request_123",
  "content": "Discussion about project requirements",
  "context": "service_request",
  "context_id": "request_123"
}
```

### GET /chat/messages/{chat_id}
**Description**: Get messages for specific chat  
**Authentication**: Required  

**Response**: Array of chat messages with timestamps and sender info

### GET /chat/online/{chat_id}
**Description**: Get online users in chat  
**Authentication**: Required  

**Response**: List of currently online participants

---

## 📈 Analytics and Reporting API

### GET /navigator/analytics/resources
**Description**: Get resource usage analytics for navigators  
**Authentication**: Required (navigator role)  

**Parameters**:
- `since_days`: Number of days to analyze (default: 30)

**Response**: Resource usage statistics and trends

### GET /home/{role}
**Description**: Get role-specific dashboard data  
**Authentication**: Required  

**Parameters**:
- `role`: client|provider|navigator|agency

**Response**: Dashboard metrics and data for specific role

---

## 🔧 System Administration API

### GET /system/health
**Description**: Basic health check  
**Authentication**: None  

**Response**: Simple health status

### GET /system/health/detailed
**Description**: Comprehensive system health check  
**Authentication**: Required (admin role)  

**Response**: Detailed system metrics and service status

### GET /metrics
**Description**: Prometheus metrics endpoint  
**Authentication**: None (internal monitoring)  

**Response**: Prometheus-formatted metrics

---

## 📋 Error Codes Reference

| Code | Description | Resolution |
|------|-------------|------------|
| POL-1001 | Invalid authentication credentials | Check email/password combination |
| POL-1002 | Account temporarily locked | Wait for lock period to expire |
| POL-1003 | Account pending approval | Contact administrator for approval |
| POL-1004 | Insufficient permissions | Check role-based access requirements |
| POL-1005 | Resource access denied | Verify subscription or license status |
| POL-6000 | General request error | Check request format and authentication |

---

## 📊 Rate Limits

| Endpoint Category | Limit | Window |
|------------------|-------|---------|
| Authentication | 10 requests | 5 minutes |
| Registration | 5 requests | 1 hour |
| Assessment Submission | 50 requests | 1 hour |
| Service Requests | 20 requests | 1 hour |
| AI Features | 100 requests | 1 hour |
| General API | 500 requests | 1 minute |

---

## 🔗 Webhook System

### Webhook Events
The platform supports webhooks for real-time event notifications:

#### Available Events
- `assessment.completed` - Assessment session finished
- `service_request.created` - New service request submitted
- `service_request.responded` - Provider responded to request
- `engagement.status_changed` - Service engagement status updated
- `rp_lead.created` - New RP lead generated
- `rp_lead.status_changed` - RP lead status updated
- `user.registered` - New user registration
- `certificate.issued` - Certificate generated

#### Webhook Payload Example
```json
{
  "event": "assessment.completed",
  "timestamp": "2025-09-22T10:30:00Z",
  "data": {
    "user_id": "user-uuid",
    "session_id": "session-uuid",
    "area_id": "area2",
    "completion_score": 78.5,
    "tier_level": 2
  },
  "metadata": {
    "webhook_id": "webhook-uuid",
    "attempt": 1,
    "signature": "sha256=..."
  }
}
```

### Setting Up Webhooks
```bash
# Register webhook endpoint
curl -X POST "https://your-domain.com/api/webhooks/register" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/polaris-webhook",
    "events": ["assessment.completed", "service_request.created"],
    "secret": "your-webhook-secret"
  }'
```

---

## 📱 SDK Libraries

### JavaScript/TypeScript SDK
```javascript
import { PolarisClient } from '@polaris/js-sdk';

const polaris = new PolarisClient({
  apiUrl: 'https://your-domain.com/api',
  apiKey: 'your-api-key'
});

// Get user dashboard
const dashboard = await polaris.dashboard.get('client');

// Create assessment session
const session = await polaris.assessment.createSession({
  areaId: 'area1',
  tierLevel: 2
});

// AI coaching conversation
const response = await polaris.ai.coach({
  message: 'How do I improve my readiness score?',
  sessionId: 'coach_session_123'
});
```

### Python SDK
```python
from polaris_sdk import PolarisClient

client = PolarisClient(
    api_url='https://your-domain.com/api',
    api_key='your-api-key'
)

# Get assessment schema
schema = client.assessment.get_schema()

# Create service request
request = client.service_requests.create(
    area_id='area5',
    budget_range='5000-15000',
    description='Need cybersecurity assessment'
)

# Get predictive analytics
analytics = client.ai.predictive_analytics(
    user_id='target-user-id',
    analysis_type='success_prediction'
)
```

---

## 🎯 Integration Examples

### CRM Integration
```javascript
// Sync Polaris readiness data with your CRM
const readinessData = await polaris.client.getReadinessProfile(clientId);

await yourCRM.updateContact(clientId, {
  procurementReadiness: readinessData.overallScore,
  certificationStatus: readinessData.certificationReady,
  lastAssessment: readinessData.lastActivity,
  criticalGaps: readinessData.gaps.filter(g => g.priority === 'high')
});
```

### Accounting Software Integration
```javascript
// Push financial readiness data to accounting software
const financialAssessment = await polaris.assessment.getAreaProgress('area2');

await accountingSoftware.addNote(clientId, {
  category: 'compliance',
  note: `Procurement readiness - Financial Management: ${financialAssessment.score}%`,
  tags: ['procurement', 'compliance', 'readiness']
});
```

### External Learning Management System
```javascript
// Sync assessment completion with LMS
const completedAreas = await polaris.assessment.getCompletedAreas(userId);

for (const area of completedAreas) {
  await lms.markCourseComplete(userId, `procurement_${area.id}`, {
    score: area.completionScore,
    completedAt: area.completedAt,
    certificateEligible: area.score >= 70
  });
}
```

---

## 🔍 API Testing

### Postman Collection
Download our comprehensive Postman collection for API testing:
- Authentication flows
- Assessment workflows  
- Service provider interactions
- RP CRM-lite features
- AI-powered endpoints

### Test Data
Use our QA credentials for testing:
```json
{
  "client": {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
  },
  "provider": {
    "email": "provider.qa@polaris.example.com",
    "password": "Polaris#2025!"
  },
  "agency": {
    "email": "agency.qa@polaris.example.com", 
    "password": "Polaris#2025!"
  },
  "navigator": {
    "email": "navigator.qa@polaris.example.com",
    "password": "Polaris#2025!"
  }
}
```

---

## 🚀 Getting Started for Developers

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/your-org/polaris-platform

# Install dependencies
cd polaris-platform/backend
pip install -r requirements.txt

cd ../frontend  
yarn install

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 2. Development Workflow
```bash
# Start development servers
cd backend && uvicorn server:app --reload
cd frontend && yarn start

# Run tests
pytest backend/tests/
yarn test frontend/
```

### 3. Production Deployment
```bash
# Build production frontend
yarn build

# Deploy with Docker
docker-compose up -d

# Monitor health
curl https://your-domain.com/api/system/health
```

---

## 📞 Support and Resources

- **Documentation**: [https://docs.polaris.platform](https://docs.polaris.platform)
- **API Status**: [https://status.polaris.platform](https://status.polaris.platform)  
- **Developer Support**: developers@polaris.platform
- **Community Forum**: [https://community.polaris.platform](https://community.polaris.platform)

---

## 📄 License and Terms

This API is provided under the Polaris Platform License Agreement. See [LICENSE.md](LICENSE.md) for full terms and conditions.

**Rate Limits**: All API endpoints are subject to rate limiting. Upgrade your plan for higher limits.  
**SLA**: 99.9% uptime guarantee for production deployments.  
**Support**: 24/7 support available for enterprise customers.

---

**Last Updated**: September 22, 2025  
**API Version**: 2.0.0  
**Documentation Version**: 1.0.0