"""
Security and Consent API Endpoints for Polaris Platform
Extends the main server with encryption and consent management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import secrets

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ConsentGrantRequest(BaseModel):
    scope: str
    notes: Optional[str] = None

class ConsentGrantResponse(BaseModel):
    consent_id: str
    granted_at: datetime
    scope: str

class ConsentRevokeRequest(BaseModel):
    scope: str

class ConsentListResponse(BaseModel):
    consents: List[Dict[str, Any]]

class EncryptionFieldInfo(BaseModel):
    resource: str
    field_name: str
    deterministic: bool
    created_at: datetime

class EncryptionIntrospectionResponse(BaseModel):
    fields: List[EncryptionFieldInfo]

class KeyRotationRequest(BaseModel):
    key_alias: Optional[str] = None  # If None, rotate all keys
    batch_size: Optional[int] = 100

class KeyRotationResponse(BaseModel):
    rotation_id: str
    status: str
    message: str

def create_security_router(db, consent_manager, field_manager, security_manager, 
                         get_current_user, require_role):
    """Create the security API router with all dependencies injected"""
    
    security_api = APIRouter(prefix="/security", tags=["security"])
    
    # Consent Management Endpoints
    @security_api.post("/clients/{client_id}/consents", response_model=ConsentGrantResponse)
    async def grant_consent(
        client_id: str,
        request: ConsentGrantRequest,
        current=Depends(get_current_user)
    ):
        """Grant consent for a specific scope"""
        try:
            # Validate scope
            from .consent import ConsentScope
            if request.scope not in ConsentScope.get_all_scopes():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid scope: {request.scope}"
                )
            
            # Grant consent
            consent_id = await consent_manager.grant_consent(
                client_id=client_id,
                scope=request.scope,
                granted_by_user_id=current["user_id"],
                notes=request.notes
            )
            
            return ConsentGrantResponse(
                consent_id=consent_id,
                granted_at=datetime.now(),
                scope=request.scope
            )
            
        except Exception as e:
            logger.error(f"Failed to grant consent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @security_api.post("/clients/{client_id}/consents/revoke")
    async def revoke_consent(
        client_id: str,
        request: ConsentRevokeRequest,
        current=Depends(get_current_user)
    ):
        """Revoke consent for a specific scope"""
        try:
            success = await consent_manager.revoke_consent(
                client_id=client_id,
                scope=request.scope,
                revoked_by_user_id=current["user_id"]
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active consent not found"
                )
            
            return {"success": True, "message": "Consent revoked successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to revoke consent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @security_api.get("/clients/{client_id}/consents", response_model=ConsentListResponse)
    async def list_consents(
        client_id: str,
        include_revoked: bool = False,
        current=Depends(get_current_user)
    ):
        """List all consents for a client"""
        try:
            consents = await consent_manager.get_client_consents(
                client_id=client_id,
                include_revoked=include_revoked
            )
            
            return ConsentListResponse(consents=consents)
            
        except Exception as e:
            logger.error(f"Failed to list consents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    # Encryption Introspection Endpoint
    @security_api.get("/encryption/fields", response_model=EncryptionIntrospectionResponse)
    async def list_encrypted_fields(current=Depends(get_current_user)):
        """List all fields configured for encryption"""
        try:
            fields = []
            
            # Get all encryption field metadata
            async for metadata in db.encryption_field_metadata.find():
                fields.append(EncryptionFieldInfo(
                    resource=metadata["resource"],
                    field_name=metadata["field_name"],
                    deterministic=metadata["deterministic"],
                    created_at=metadata["created_at"]
                ))
            
            return EncryptionIntrospectionResponse(fields=fields)
            
        except Exception as e:
            logger.error(f"Failed to list encrypted fields: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    # Key Rotation Endpoint (Admin only)
    @security_api.post("/rotate-keys", response_model=KeyRotationResponse)
    async def rotate_encryption_keys(
        request: KeyRotationRequest,
        current=Depends(require_role("admin"))
    ):
        """Trigger key rotation (admin only, feature-flag protected)"""
        try:
            # Check feature flag
            import os
            if not os.environ.get("ENABLE_KEY_ROTATION", "false").lower() == "true":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Key rotation feature is disabled"
                )
            
            rotation_id = secrets.token_hex(16)
            
            # Create rotation state record
            rotation_state = {
                "_id": rotation_id,
                "rotation_id": rotation_id,
                "status": "started",
                "key_alias": request.key_alias,
                "batch_size": request.batch_size or 100,
                "started_at": datetime.now(),
                "started_by": current["user_id"],
                "progress": {
                    "current_resource": None,
                    "last_processed_id": None,
                    "total_records": 0,
                    "processed_records": 0
                }
            }
            
            await db.rotation_state.insert_one(rotation_state)
            
            # Log the rotation start
            await security_manager.log_security_event(
                event_type='key_rotation_started',
                user_id=current["user_id"],
                details={'rotation_id': rotation_id, 'key_alias': request.key_alias}
            )
            
            # TODO: Implement async background key rotation task
            # For now, just return the rotation ID
            logger.info(f"Key rotation {rotation_id} initiated by {current['user_id']}")
            
            return KeyRotationResponse(
                rotation_id=rotation_id,
                status="started",
                message="Key rotation initiated successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start key rotation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @security_api.get("/rotate-keys/{rotation_id}")
    async def get_rotation_status(
        rotation_id: str,
        current=Depends(require_role("admin"))
    ):
        """Get status of a key rotation operation"""
        try:
            rotation_state = await db.rotation_state.find_one({"rotation_id": rotation_id})
            
            if not rotation_state:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rotation not found"
                )
            
            return {
                "rotation_id": rotation_id,
                "status": rotation_state["status"],
                "started_at": rotation_state["started_at"],
                "progress": rotation_state["progress"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get rotation status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    return security_api


def create_client_router_extensions(db, field_manager, consent_middleware, security_manager,
                                  get_current_user, require_role):
    """Create extensions to client endpoints for encrypted fields"""
    
    client_extensions = APIRouter(prefix="/clients", tags=["clients-security"])
    
    @client_extensions.get("/{client_id}/profile-secure")
    async def get_client_profile_secure(
        client_id: str,
        current=Depends(get_current_user)
    ):
        """Get client profile with consent-based field decryption"""
        try:
            # Get client profile from database
            profile = await db.client_profiles.find_one({"_id": client_id})
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client not found"
                )
            
            # Get user permissions (simplified - would normally come from RBAC)
            user_permissions = ["view_sensitive_data", "view_confidential_notes"]
            
            # Check consent and decrypt permitted fields
            consent_result = await consent_middleware.enforce_consent(
                client_id=client_id,
                requested_fields=["ssn", "address_line1", "address_line2", "phone"],
                user_permissions=user_permissions
            )
            
            if not consent_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": consent_result["error"],
                        "missing_scopes": consent_result.get("missing_scopes", [])
                    }
                )
            
            # Decrypt permitted fields
            decrypted_profile = await field_manager.decrypt_fields(
                profile, "client_profiles", consent_result["permitted_fields"]
            )
            
            # Log the access
            await security_manager.audit_decrypt_operation(
                user_id=current["user_id"],
                resource="client_profiles",
                fields_decrypted=consent_result["permitted_fields"],
                client_id=client_id
            )
            
            return decrypted_profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get secure client profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    return client_extensions