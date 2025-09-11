#!/usr/bin/env python3
"""
Security API Demo Script
Demonstrates the security and consent management API endpoints
"""

import json
from datetime import datetime

def demo_security_api():
    """Demonstrate the security API endpoints"""
    
    print("🔐 Security, Encryption & Consent API Demo")
    print("=" * 50)
    
    # Demo 1: Grant Consent
    print("\n1. Grant Consent API")
    print("POST /api/security/clients/client_123/consents")
    
    consent_request = {
        "scope": "VIEW_SENSITIVE_IDENTIFIERS",
        "notes": "Support ticket #12345 - verify client identity"
    }
    
    consent_response = {
        "consent_id": "consent_abc123",
        "granted_at": datetime.now().isoformat(),
        "scope": "VIEW_SENSITIVE_IDENTIFIERS"
    }
    
    print(f"Request:  {json.dumps(consent_request, indent=2)}")
    print(f"Response: {json.dumps(consent_response, indent=2)}")
    
    # Demo 2: List Consents
    print("\n2. List Consents API")
    print("GET /api/security/clients/client_123/consents")
    
    consents_response = {
        "consents": [
            {
                "id": "consent_abc123",
                "client_id": "client_123",
                "scope": "VIEW_SENSITIVE_IDENTIFIERS",
                "granted_at": "2025-01-08T10:30:00Z",
                "revoked_at": None,
                "granted_by_user_id": "user_456",
                "notes": "Support ticket #12345"
            },
            {
                "id": "consent_def456", 
                "client_id": "client_123",
                "scope": "VIEW_CONFIDENTIAL_NOTES",
                "granted_at": "2025-01-08T09:15:00Z",
                "revoked_at": None,
                "granted_by_user_id": "user_789",
                "notes": "Case review consent"
            }
        ]
    }
    
    print(f"Response: {json.dumps(consents_response, indent=2)}")
    
    # Demo 3: Access Secure Client Profile
    print("\n3. Secure Client Profile API")
    print("GET /api/clients/client_123/profile-secure")
    
    # Without consent - returns 403
    no_consent_response = {
        "detail": {
            "error": "consent_required",
            "missing_scopes": ["VIEW_SENSITIVE_IDENTIFIERS"]
        }
    }
    
    print("Without consent (403 Forbidden):")
    print(f"Response: {json.dumps(no_consent_response, indent=2)}")
    
    # With consent - returns decrypted data
    secure_profile_response = {
        "id": "client_123",
        "name": "John Doe",
        "ssn": "123-45-6789",  # Decrypted
        "address_line1": "123 Main Street",  # Decrypted
        "address_line2": "Apt 4B",  # Decrypted  
        "phone": "555-123-4567",  # Decrypted
        "email": "john.doe@example.com",
        "created_at": "2025-01-01T00:00:00Z"
    }
    
    print("\nWith consent (200 OK):")
    print(f"Response: {json.dumps(secure_profile_response, indent=2)}")
    
    # Demo 4: Revoke Consent
    print("\n4. Revoke Consent API")
    print("POST /api/security/clients/client_123/consents/revoke")
    
    revoke_request = {
        "scope": "VIEW_SENSITIVE_IDENTIFIERS"
    }
    
    revoke_response = {
        "success": True,
        "message": "Consent revoked successfully"
    }
    
    print(f"Request:  {json.dumps(revoke_request, indent=2)}")
    print(f"Response: {json.dumps(revoke_response, indent=2)}")
    
    # Demo 5: Encryption Fields Introspection
    print("\n5. Encryption Fields Introspection API")
    print("GET /api/security/encryption/fields")
    
    fields_response = {
        "fields": [
            {
                "resource": "client_profiles",
                "field_name": "ssn",
                "deterministic": True,
                "created_at": "2025-01-08T08:00:00Z"
            },
            {
                "resource": "client_profiles", 
                "field_name": "address_line1",
                "deterministic": False,
                "created_at": "2025-01-08T08:00:00Z"
            },
            {
                "resource": "client_profiles",
                "field_name": "phone",
                "deterministic": False,
                "created_at": "2025-01-08T08:00:00Z"
            },
            {
                "resource": "assessments",
                "field_name": "notes", 
                "deterministic": False,
                "created_at": "2025-01-08T08:00:00Z"
            }
        ]
    }
    
    print(f"Response: {json.dumps(fields_response, indent=2)}")
    
    # Demo 6: Key Rotation (Admin only)
    print("\n6. Key Rotation API (Admin Only)")
    print("POST /api/security/rotate-keys")
    
    rotation_request = {
        "key_alias": "client_data_key",
        "batch_size": 100
    }
    
    rotation_response = {
        "rotation_id": "rot_xyz789",
        "status": "started",
        "message": "Key rotation initiated successfully"
    }
    
    print(f"Request:  {json.dumps(rotation_request, indent=2)}")
    print(f"Response: {json.dumps(rotation_response, indent=2)}")
    
    # Check rotation status
    print("\nGET /api/security/rotate-keys/rot_xyz789")
    
    status_response = {
        "rotation_id": "rot_xyz789",
        "status": "in_progress",
        "started_at": "2025-01-08T11:00:00Z",
        "progress": {
            "current_resource": "client_profiles",
            "last_processed_id": "client_100", 
            "total_records": 1000,
            "processed_records": 250
        }
    }
    
    print(f"Response: {json.dumps(status_response, indent=2)}")
    
    # Demo 7: Masked Data Access (No Consent)
    print("\n7. Data Access Without Consent (Masked)")
    print("GET /api/clients/client_123/profile (without consent)")
    
    masked_profile_response = {
        "id": "client_123",
        "name": "John Doe", 
        "ssn": "***-**-6789",  # Masked
        "address_line1": "***********reet",  # Masked
        "address_line2": "****B",  # Masked
        "phone": "***-***-4567",  # Masked
        "email": "john.doe@example.com",
        "created_at": "2025-01-01T00:00:00Z"
    }
    
    print(f"Response: {json.dumps(masked_profile_response, indent=2)}")
    
    print("\n📊 Security Implementation Benefits:")
    print("✅ Field-level encryption protects sensitive data at rest")
    print("✅ Consent enforcement prevents unauthorized access")
    print("✅ Deterministic hashing enables encrypted field lookups")
    print("✅ Audit trails track all sensitive data operations")
    print("✅ Key rotation ensures long-term security")
    print("✅ Data masking provides controlled information disclosure")
    print("✅ API introspection enables security monitoring")
    
    print("\n🔒 Compliance Features:")
    print("✅ HIPAA: PHI encryption and access controls")
    print("✅ SOC2: Key management and audit logging")
    print("✅ Data minimization through consent scopes")
    print("✅ Right to access through consent management")

if __name__ == "__main__":
    demo_security_api()