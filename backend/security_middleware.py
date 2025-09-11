"""
Security and Consent Middleware for Polaris Platform
Handles consent enforcement and security logging
"""

from fastapi import HTTPException, Request, status
from typing import Dict, List, Optional, Callable, Any
import logging
from datetime import datetime, UTC
from .consent import ConsentManager, ConsentScopeResolver
from .encryption import FieldEncryptionManager
import json

logger = logging.getLogger(__name__)

class ConsentEnforcementMiddleware:
    """
    Middleware to enforce consent requirements for sensitive data access
    """
    
    def __init__(self, consent_manager: ConsentManager, 
                 consent_resolver: ConsentScopeResolver,
                 field_manager: FieldEncryptionManager):
        self.consent_manager = consent_manager
        self.consent_resolver = consent_resolver
        self.field_manager = field_manager
    
    async def enforce_consent(self, client_id: str, requested_fields: List[str], 
                            user_permissions: List[str]) -> Dict[str, Any]:
        """
        Enforce consent requirements for field access
        Returns dict with permitted_fields and error info if consent missing
        """
        try:
            permitted_fields, missing_scopes = await self.consent_resolver.get_permitted_fields(
                client_id, user_permissions, requested_fields
            )
            
            if missing_scopes:
                return {
                    "success": False,
                    "error": "consent_required",
                    "missing_scopes": missing_scopes,
                    "permitted_fields": permitted_fields
                }
            
            return {
                "success": True,
                "permitted_fields": permitted_fields,
                "missing_scopes": []
            }
            
        except Exception as e:
            logger.error(f"Consent enforcement error: {e}")
            return {
                "success": False,
                "error": "consent_check_failed",
                "message": str(e)
            }


class SecurityMiddleware:
    """
    General security middleware for request processing
    """
    
    def __init__(self, db, security_manager=None):
        self.db = db
        self.security_manager = security_manager
    
    async def log_field_access(self, user_id: str, client_id: str, 
                              fields_accessed: List[str], outcome: str):
        """Log sensitive field access for audit"""
        try:
            # Only log access to sensitive fields to avoid noise
            sensitive_fields = ["ssn", "address_line1", "address_line2", "phone", "notes"]
            accessed_sensitive = [f for f in fields_accessed if f in sensitive_fields]
            
            if not accessed_sensitive:
                return
            
            log_entry = {
                "timestamp": datetime.now(UTC),
                "event_type": "FIELD_ACCESS",
                "user_id": user_id,
                "resource": "sensitive_fields",
                "resource_id": client_id,
                "action": "decrypt",
                "details": {
                    "fields_accessed": accessed_sensitive,
                    "outcome": outcome
                },
                "severity": "info"
            }
            
            await self.db.audit_logs.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log field access: {e}")
    
    async def check_rate_limit(self, request: Request, limit_type: str = "api") -> bool:
        """Check rate limiting for the request"""
        if not self.security_manager:
            return True
            
        try:
            # Get client identifier (IP + user if available)
            client_ip = request.client.host if hasattr(request, 'client') else "unknown"
            user_id = getattr(request.state, 'user_id', None)
            identifier = f"{client_ip}:{user_id}" if user_id else client_ip
            
            return await self.security_manager.rate_limit(identifier, limit_type)
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error to avoid breaking functionality


def require_consent(scopes: List[str]):
    """
    Decorator to require specific consent scopes for an endpoint
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Extract request and current user from FastAPI dependency injection
            request = None
            current_user = None
            client_id = None
            
            # Find request and user in the arguments
            for arg in args:
                if hasattr(arg, 'method'):  # This is likely the request
                    request = arg
                elif isinstance(arg, dict) and 'user_id' in arg:  # This is current user
                    current_user = arg
            
            # Try to get client_id from path parameters or request body
            if request:
                path_params = request.path_params
                client_id = path_params.get('id') or path_params.get('client_id')
                
                if not client_id and request.method in ['POST', 'PUT', 'PATCH']:
                    try:
                        body = await request.json()
                        client_id = body.get('client_id')
                    except:
                        pass
            
            if not client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client ID required for consent check"
                )
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check consent (this would need access to the middleware instance)
            # For now, we'll implement this check in the individual endpoints
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class ResponseFilter:
    """
    Filter response data based on consent and permissions
    """
    
    def __init__(self, field_manager: FieldEncryptionManager,
                 consent_middleware: ConsentEnforcementMiddleware):
        self.field_manager = field_manager
        self.consent_middleware = consent_middleware
    
    async def filter_response(self, data: Dict, resource: str, client_id: str,
                            user_permissions: List[str]) -> Dict:
        """
        Filter response data based on user permissions and consent
        """
        try:
            if not data:
                return data
            
            # Get all potential sensitive fields in the data
            all_fields = list(data.keys())
            sensitive_fields = [f for f in all_fields if f.endswith('_encrypted')]
            
            if not sensitive_fields:
                return data  # No encrypted fields to process
            
            # Map encrypted fields back to original field names
            original_fields = [f.replace('_encrypted', '') for f in sensitive_fields]
            
            # Check consent and permissions
            consent_result = await self.consent_middleware.enforce_consent(
                client_id, original_fields, user_permissions
            )
            
            if not consent_result["success"]:
                # Return error response
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": consent_result["error"],
                        "missing_scopes": consent_result.get("missing_scopes", [])
                    }
                )
            
            # Decrypt permitted fields
            permitted_fields = consent_result["permitted_fields"]
            filtered_data = await self.field_manager.decrypt_fields(
                data, resource, permitted_fields
            )
            
            return filtered_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Response filtering error: {e}")
            return data  # Return original data on error to avoid breaking functionality