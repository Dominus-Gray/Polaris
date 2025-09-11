"""
Consent Management for Polaris Platform
Handles consent scope enforcement and tracking
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import secrets

logger = logging.getLogger(__name__)

class ConsentScope:
    """Defined consent scopes for the platform"""
    VIEW_SENSITIVE_IDENTIFIERS = "VIEW_SENSITIVE_IDENTIFIERS"  # SSN, full address
    VIEW_CONFIDENTIAL_NOTES = "VIEW_CONFIDENTIAL_NOTES"      # Assessment notes
    
    # Mapping of scopes to fields they control
    SCOPE_FIELD_MAPPING = {
        VIEW_SENSITIVE_IDENTIFIERS: [
            "ssn", "address_line1", "address_line2", "phone"
        ],
        VIEW_CONFIDENTIAL_NOTES: [
            "notes"
        ]
    }
    
    @classmethod
    def get_all_scopes(cls) -> List[str]:
        """Get all available consent scopes"""
        return [cls.VIEW_SENSITIVE_IDENTIFIERS, cls.VIEW_CONFIDENTIAL_NOTES]
    
    @classmethod
    def get_fields_for_scope(cls, scope: str) -> List[str]:
        """Get fields controlled by a specific scope"""
        return cls.SCOPE_FIELD_MAPPING.get(scope, [])
    
    @classmethod
    def get_scopes_for_field(cls, field: str) -> List[str]:
        """Get scopes that control access to a specific field"""
        scopes = []
        for scope, fields in cls.SCOPE_FIELD_MAPPING.items():
            if field in fields:
                scopes.append(scope)
        return scopes


class ConsentManager:
    """
    Manages consent records and enforcement
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def grant_consent(self, client_id: str, scope: str, granted_by_user_id: str, 
                          notes: Optional[str] = None) -> str:
        """Grant consent for a specific scope"""
        try:
            # Check if consent already exists and is active
            existing = await self.db.consent_records.find_one({
                "client_id": client_id,
                "scope": scope,
                "revoked_at": None
            })
            
            if existing:
                logger.info(f"Consent already granted for client {client_id}, scope {scope}")
                return str(existing["_id"])
            
            consent_id = secrets.token_hex(16)
            consent_record = {
                "_id": consent_id,
                "client_id": client_id,
                "scope": scope,
                "granted_at": datetime.now(UTC),
                "revoked_at": None,
                "granted_by_user_id": granted_by_user_id,
                "notes": notes
            }
            
            await self.db.consent_records.insert_one(consent_record)
            
            # Log the consent grant
            await self._log_consent_event("consent_granted", client_id, scope, granted_by_user_id)
            
            return consent_id
            
        except Exception as e:
            logger.error(f"Failed to grant consent: {e}")
            raise
    
    async def revoke_consent(self, client_id: str, scope: str, revoked_by_user_id: str) -> bool:
        """Revoke consent for a specific scope"""
        try:
            result = await self.db.consent_records.update_one(
                {
                    "client_id": client_id,
                    "scope": scope,
                    "revoked_at": None
                },
                {
                    "$set": {
                        "revoked_at": datetime.now(UTC),
                        "revoked_by_user_id": revoked_by_user_id
                    }
                }
            )
            
            if result.modified_count > 0:
                await self._log_consent_event("consent_revoked", client_id, scope, revoked_by_user_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke consent: {e}")
            raise
    
    async def check_consent(self, client_id: str, scope: str) -> bool:
        """Check if consent is granted for a specific scope"""
        try:
            consent = await self.db.consent_records.find_one({
                "client_id": client_id,
                "scope": scope,
                "revoked_at": None
            })
            
            return consent is not None
            
        except Exception as e:
            logger.error(f"Failed to check consent: {e}")
            return False
    
    async def get_client_consents(self, client_id: str, include_revoked: bool = False) -> List[Dict]:
        """Get all consents for a client"""
        try:
            query = {"client_id": client_id}
            if not include_revoked:
                query["revoked_at"] = None
            
            consents = []
            async for consent in self.db.consent_records.find(query):
                consent["id"] = consent["_id"]
                consents.append(consent)
            
            return consents
            
        except Exception as e:
            logger.error(f"Failed to get client consents: {e}")
            return []
    
    async def get_missing_consents(self, client_id: str, required_scopes: List[str]) -> List[str]:
        """Get list of scopes that don't have active consent"""
        missing = []
        
        for scope in required_scopes:
            has_consent = await self.check_consent(client_id, scope)
            if not has_consent:
                missing.append(scope)
        
        return missing
    
    async def _log_consent_event(self, event_type: str, client_id: str, scope: str, user_id: str):
        """Log consent events for audit trail"""
        try:
            event_data = {
                "_id": secrets.token_hex(16),
                "timestamp": datetime.now(UTC),
                "event_type": event_type,
                "user_id": user_id,
                "resource": "consent_records",
                "resource_id": client_id,
                "action": event_type,
                "details": {
                    "scope": scope,
                    "client_id": client_id
                },
                "ip_address": None,  # Will be filled by middleware
                "user_agent": None   # Will be filled by middleware
            }
            
            await self.db.audit_logs.insert_one(event_data)
            
        except Exception as e:
            logger.error(f"Failed to log consent event: {e}")


class ConsentScopeResolver:
    """
    Resolves what fields a user can access based on permissions and consent
    """
    
    def __init__(self, consent_manager: ConsentManager):
        self.consent_manager = consent_manager
    
    async def get_permitted_fields(self, client_id: str, user_permissions: List[str], 
                                 requested_fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        Get fields that user can access and missing consent scopes
        Returns: (permitted_fields, missing_consent_scopes)
        """
        permitted_fields = []
        missing_scopes = set()
        
        for field in requested_fields:
            # Check if user has RBAC permission for this field
            required_scopes = ConsentScope.get_scopes_for_field(field)
            
            if not required_scopes:
                # Field doesn't require consent, check RBAC only
                if self._has_field_permission(field, user_permissions):
                    permitted_fields.append(field)
                continue
            
            # Field requires consent - check both RBAC and consent
            has_permission = self._has_field_permission(field, user_permissions)
            if not has_permission:
                continue
                
            # Check consent for each required scope
            field_permitted = True
            for scope in required_scopes:
                has_consent = await self.consent_manager.check_consent(client_id, scope)
                if not has_consent:
                    missing_scopes.add(scope)
                    field_permitted = False
            
            if field_permitted:
                permitted_fields.append(field)
        
        return permitted_fields, list(missing_scopes)
    
    def _has_field_permission(self, field: str, user_permissions: List[str]) -> bool:
        """Check if user has RBAC permission for a field"""
        # Map fields to required permissions
        field_permission_map = {
            "ssn": "view_sensitive_data",
            "address_line1": "view_sensitive_data", 
            "address_line2": "view_sensitive_data",
            "phone": "view_sensitive_data",
            "notes": "view_confidential_notes"
        }
        
        required_permission = field_permission_map.get(field)
        if not required_permission:
            return True  # No special permission required
            
        return required_permission in user_permissions