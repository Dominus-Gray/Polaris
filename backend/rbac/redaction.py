"""
Data Redaction Utilities for Polaris Platform
Provides utilities for redacting sensitive data based on RBAC permissions
"""
import logging
from typing import Dict, Any, List, Optional, Set
from copy import deepcopy
from .permissions import Permission
from .policy_engine import PolicyEvaluationService, Principal, Resource

logger = logging.getLogger(__name__)


class DataRedactor:
    """Handles redaction of sensitive data based on user permissions"""
    
    def __init__(self, policy_service: PolicyEvaluationService):
        self.policy_service = policy_service
        
        # Define sensitive fields for each resource type
        self.sensitive_fields = {
            "client_profile": {
                "demographics_json": Permission.VIEW_SENSITIVE,
                "consent_policies_json": Permission.VIEW_SENSITIVE,
                "risk_score": Permission.VIEW_SENSITIVE,
            },
            "assessment": {
                "responses_json": Permission.VIEW_SENSITIVE,
                "score_vector_json": Permission.VIEW_SENSITIVE,
            },
            "user": {
                "auth_provider_id": Permission.VIEW_SENSITIVE,
                "last_login_at": Permission.VIEW_SENSITIVE,
            },
            "outcome_record": {
                "value_json": Permission.VIEW_SENSITIVE,
            },
            "audit_event": {
                "before_json": Permission.VIEW_SENSITIVE,
                "after_json": Permission.VIEW_SENSITIVE,
                "ip_address": Permission.VIEW_SENSITIVE,
                "user_agent": Permission.VIEW_SENSITIVE,
            }
        }
        
        # PII fields that should always be redacted unless explicit permission
        self.pii_fields = {
            "email", "phone", "address", "ssn", "tax_id", "dob", "birth_date",
            "drivers_license", "passport", "credit_card", "bank_account"
        }
    
    async def redact_document(
        self, 
        document: Dict[str, Any], 
        resource_type: str,
        principal: Principal,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Redact sensitive fields from a document based on user permissions
        
        Args:
            document: The document to redact
            resource_type: Type of resource (client_profile, assessment, etc.)
            principal: The user requesting access
            resource_id: ID of the specific resource (if applicable)
            
        Returns:
            Redacted copy of the document
        """
        if not document:
            return document
        
        # Create a deep copy to avoid modifying the original
        redacted = deepcopy(document)
        
        # Get sensitive fields for this resource type
        sensitive_fields = self.sensitive_fields.get(resource_type, {})
        
        # Check if user has VIEW_SENSITIVE permission for this resource
        has_sensitive_access = False
        if resource_id:
            resource = Resource(
                resource_type=resource_type,
                resource_id=resource_id,
                organization_id=document.get("organization_id"),
                owner_id=document.get("user_id") or document.get("created_by")
            )
            
            decision = await self.policy_service.evaluate(
                principal, Permission.VIEW_SENSITIVE, resource
            )
            has_sensitive_access = decision.allowed
        
        # Redact sensitive fields if user lacks permission
        if not has_sensitive_access:
            for field, required_permission in sensitive_fields.items():
                if field in redacted:
                    redacted[field] = self._redact_value(redacted[field], field)
        
        # Always redact PII fields in nested JSON unless explicitly allowed
        redacted = self._redact_pii_in_json(redacted, has_sensitive_access)
        
        return redacted
    
    async def redact_document_list(
        self,
        documents: List[Dict[str, Any]],
        resource_type: str,
        principal: Principal
    ) -> List[Dict[str, Any]]:
        """Redact a list of documents"""
        redacted_list = []
        
        for doc in documents:
            resource_id = doc.get("id") or doc.get("_id")
            redacted_doc = await self.redact_document(
                doc, resource_type, principal, resource_id
            )
            redacted_list.append(redacted_doc)
        
        return redacted_list
    
    def _redact_value(self, value: Any, field_name: str) -> Any:
        """Redact a specific value based on its type and field name"""
        if value is None:
            return None
        
        if isinstance(value, str):
            if len(value) <= 4:
                return "***"
            else:
                return value[:2] + "***" + value[-2:]
        
        elif isinstance(value, dict):
            return {"[REDACTED]": "Sensitive data hidden"}
        
        elif isinstance(value, list):
            return ["[REDACTED]"] * len(value)
        
        elif isinstance(value, (int, float)):
            return "[REDACTED]"
        
        else:
            return "[REDACTED]"
    
    def _redact_pii_in_json(
        self, 
        data: Any, 
        has_sensitive_access: bool,
        path: str = ""
    ) -> Any:
        """Recursively redact PII fields in nested JSON structures"""
        if has_sensitive_access:
            return data
        
        if isinstance(data, dict):
            redacted_dict = {}
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this field contains PII
                if any(pii_field in key.lower() for pii_field in self.pii_fields):
                    redacted_dict[key] = self._redact_value(value, key)
                else:
                    redacted_dict[key] = self._redact_pii_in_json(
                        value, has_sensitive_access, current_path
                    )
            
            return redacted_dict
        
        elif isinstance(data, list):
            return [
                self._redact_pii_in_json(item, has_sensitive_access, f"{path}[{i}]")
                for i, item in enumerate(data)
            ]
        
        else:
            return data
    
    def redact_field_names(self, field_names: List[str]) -> List[str]:
        """Redact sensitive field names from lists (for schema introspection)"""
        redacted_names = []
        
        for field_name in field_names:
            if any(pii_field in field_name.lower() for pii_field in self.pii_fields):
                redacted_names.append("[SENSITIVE_FIELD]")
            else:
                redacted_names.append(field_name)
        
        return redacted_names
    
    async def can_access_field(
        self,
        principal: Principal,
        resource_type: str,
        resource_id: str,
        field_name: str
    ) -> bool:
        """Check if a user can access a specific field"""
        sensitive_fields = self.sensitive_fields.get(resource_type, {})
        
        if field_name not in sensitive_fields:
            # Non-sensitive field, check for PII
            if any(pii_field in field_name.lower() for pii_field in self.pii_fields):
                # PII field requires sensitive access
                resource = Resource(resource_type=resource_type, resource_id=resource_id)
                decision = await self.policy_service.evaluate(
                    principal, Permission.VIEW_SENSITIVE, resource
                )
                return decision.allowed
            else:
                return True
        
        # Sensitive field, check specific permission
        required_permission = sensitive_fields[field_name]
        resource = Resource(resource_type=resource_type, resource_id=resource_id)
        decision = await self.policy_service.evaluate(
            principal, required_permission, resource
        )
        return decision.allowed


class RedactionPreset:
    """Predefined redaction presets for common scenarios"""
    
    @staticmethod
    def public_view() -> Set[str]:
        """Fields that can be shown in public views"""
        return {
            "id", "name", "status", "created_at", "updated_at", 
            "type", "category", "title", "description"
        }
    
    @staticmethod
    def internal_view() -> Set[str]:
        """Fields for internal organizational views"""
        return {
            "id", "name", "status", "created_at", "updated_at",
            "type", "category", "title", "description", "organization_id",
            "assigned_to", "priority", "state"
        }
    
    @staticmethod
    def admin_view() -> Set[str]:
        """Fields for administrative views (minimal redaction)"""
        return {
            "id", "name", "email", "status", "created_at", "updated_at",
            "type", "category", "title", "description", "organization_id",
            "assigned_to", "priority", "state", "metadata", "settings_json"
        }
    
    @classmethod
    def apply_preset(
        cls, 
        document: Dict[str, Any], 
        preset_name: str
    ) -> Dict[str, Any]:
        """Apply a redaction preset to a document"""
        presets = {
            "public": cls.public_view(),
            "internal": cls.internal_view(),
            "admin": cls.admin_view()
        }
        
        allowed_fields = presets.get(preset_name, cls.public_view())
        
        return {
            key: value for key, value in document.items()
            if key in allowed_fields
        }


# Utility functions for common redaction patterns

def redact_email(email: str) -> str:
    """Redact an email address"""
    if not email or "@" not in email:
        return "[REDACTED]"
    
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        redacted_local = "***"
    else:
        redacted_local = local[0] + "***" + local[-1]
    
    return f"{redacted_local}@{domain}"


def redact_phone(phone: str) -> str:
    """Redact a phone number"""
    if not phone:
        return "[REDACTED]"
    
    # Keep last 4 digits
    digits_only = "".join(c for c in phone if c.isdigit())
    if len(digits_only) <= 4:
        return "***-***-****"
    
    return "***-***-" + digits_only[-4:]


def redact_id_number(id_number: str) -> str:
    """Redact an ID number (SSN, tax ID, etc.)"""
    if not id_number:
        return "[REDACTED]"
    
    if len(id_number) <= 4:
        return "*" * len(id_number)
    
    return "*" * (len(id_number) - 4) + id_number[-4:]


def should_redact_field(field_name: str, value: Any) -> bool:
    """Determine if a field should be redacted based on name patterns"""
    sensitive_patterns = [
        "password", "secret", "key", "token", "credential",
        "ssn", "social", "tax", "ein", "dob", "birth",
        "address", "phone", "email", "ip_address"
    ]
    
    field_lower = field_name.lower()
    return any(pattern in field_lower for pattern in sensitive_patterns)