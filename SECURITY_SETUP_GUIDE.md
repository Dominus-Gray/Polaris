# Security, Encryption & Consent Baseline - Setup Guide

## Quick Setup

### 1. Environment Setup

Create a master encryption key and set environment variables:

```bash
# Generate a secure master key (32 bytes, base64 encoded)
export MASTER_KEY_MATERIAL=$(python -c "import base64, secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())")

# Enable security features
export ENABLE_FIELD_ENCRYPTION=true
export ENABLE_CONSENT_ENFORCEMENT=true

# Key rotation (admin feature)
export ENABLE_KEY_ROTATION=false  # Enable only for admin environments
```

### 2. Database Initialization

Initialize the security database collections and indexes:

```bash
cd backend
python init_security_db.py
```

This will create:
- `encryption_keys` collection with indexes
- `encryption_field_metadata` collection 
- `consent_records` collection
- Enhanced `audit_logs` collection
- Required indexes for performance

### 3. Server Integration

The security features are automatically initialized when the server starts. Add this to your environment:

```python
# In server_full.py - already integrated
from security_integration import init_security_features

@app.on_event("startup")
async def startup_security():
    security_components = await init_security_features(app, db, get_current_user, require_role)
```

### 4. API Usage Examples

#### Grant Consent
```bash
curl -X POST http://localhost:8000/api/security/clients/client_123/consents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "VIEW_SENSITIVE_IDENTIFIERS",
    "notes": "Support ticket #12345"
  }'
```

#### Access Secure Data
```bash
curl http://localhost:8000/api/clients/client_123/profile-secure \
  -H "Authorization: Bearer <token>"
```

#### List Client Consents
```bash
curl http://localhost:8000/api/security/clients/client_123/consents \
  -H "Authorization: Bearer <token>"
```

#### Revoke Consent
```bash
curl -X POST http://localhost:8000/api/security/clients/client_123/consents/revoke \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "VIEW_SENSITIVE_IDENTIFIERS"
  }'
```

### 5. Testing

Run the validation tests:

```bash
# Architecture validation
python validate_security_baseline.py

# API demo
python demo_security_api.py

# Unit tests (requires pytest)
cd backend
python test_security.py
```

## Security Configuration

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_FIELD_ENCRYPTION` | `true` | Master switch for encryption features |
| `ENABLE_CONSENT_ENFORCEMENT` | `true` | Master switch for consent checking |
| `ENABLE_KEY_ROTATION` | `false` | Admin key rotation capabilities |

### Encrypted Fields

| Resource | Field | Type | Purpose |
|----------|-------|------|---------|
| `client_profiles` | `ssn` | Deterministic | SSN with lookup capability |
| `client_profiles` | `address_line1` | Standard | Street address |
| `client_profiles` | `address_line2` | Standard | Apartment/Suite |
| `client_profiles` | `phone` | Standard | Phone number |
| `assessments` | `notes` | Standard | Confidential notes |

### Consent Scopes

- `VIEW_SENSITIVE_IDENTIFIERS`: Access to SSN, addresses, phone
- `VIEW_CONFIDENTIAL_NOTES`: Access to assessment notes

## Production Considerations

### Security Warnings

⚠️ **MVP Limitations**:
- XOR key wrapping is NOT production-grade
- In-memory rate limiting (use Redis in production)
- Simplified error handling for development

### Production Checklist

- [ ] Integrate with external KMS (AWS KMS, Azure Key Vault, etc.)
- [ ] Implement persistent rate limiting storage
- [ ] Enhanced monitoring and alerting
- [ ] Formal key rotation procedures
- [ ] Security audit and penetration testing

### Monitoring

Key metrics to monitor:
- `encryption_operations_total`
- `consent_checks_total`
- `key_rotation_duration_seconds`
- `sensitive_field_access_total`

## Compliance

### HIPAA Alignment
- ✅ Field-level PHI encryption
- ✅ Access logging and audit trails
- ✅ Consent-based access controls
- ✅ Data minimization through masking

### SOC2 Foundations
- ✅ Encryption key management
- ✅ Access control enforcement  
- ✅ Comprehensive audit logging
- ✅ Security monitoring metrics

## Troubleshooting

### Common Issues

**Import Errors**: Ensure all dependencies are installed:
```bash
pip install fastapi motor cryptography pydantic
```

**Missing Master Key**: Set the environment variable:
```bash
export MASTER_KEY_MATERIAL=$(python -c "import base64, secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())")
```

**Database Connection**: Verify MongoDB is running and accessible:
```bash
export MONGO_URL=mongodb://localhost:27017
export DB_NAME=polaris_db
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Integration Testing**: Test with real MongoDB instance
2. **Load Testing**: Validate encryption performance
3. **Security Review**: External security audit
4. **Documentation**: Update API documentation
5. **Training**: Team training on security features

For detailed architecture information, see `docs/architecture/security_encryption_consent.md`.