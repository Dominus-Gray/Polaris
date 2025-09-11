"""
API Dependencies and Security Guards for Polaris Platform
"""
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import jwt, JWTError
from ..rbac.policy_engine import PolicyEvaluationService, Principal
from ..rbac.permissions import Permission
from ..rbac.redaction import DataRedactor
from ..observability.logging_config import CorrelationIdManager, get_logger
from ..observability.telemetry import trace_function, metrics_collector
import time

logger = get_logger("api.dependencies")


class SecurityDependencies:
    """FastAPI dependencies for security and RBAC"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.policy_service = PolicyEvaluationService(db)
        self.redactor = DataRedactor(self.policy_service)
        self.jwt_secret = "dev-secret-change-in-production"  # Should come from config
    
    async def get_current_user(
        self,
        request: Request,
        authorization: Optional[str] = Header(None)
    ) -> Dict[str, Any]:
        """
        Extract and validate current user from JWT token
        """
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.split(" ")[1]
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing user ID"
                )
            
            # Load user from database
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if user.get("status") != "active":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is not active"
                )
            
            # Set correlation ID for request tracing
            correlation_id = request.headers.get("x-correlation-id")
            if not correlation_id:
                correlation_id = CorrelationIdManager.generate_correlation_id()
            CorrelationIdManager.set_correlation_id(correlation_id)
            
            # Log user authentication
            logger.info(
                f"User authenticated: {user['email']}",
                user_id=user_id,
                user_email=user["email"],
                user_role=user.get("role"),
                event_type="user_authenticated"
            )
            
            return user
            
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def require_permission(self, permission: Permission):
        """
        Dependency factory for requiring specific permissions
        
        Usage:
        @app.get("/clients")
        async def get_clients(
            current_user=Depends(security.get_current_user),
            _=Depends(security.require_permission(Permission.READ_CLIENT))
        ):
        """
        @trace_function(f"permission_check_{permission.value}")
        async def permission_dependency(
            current_user: Dict[str, Any] = Depends(self.get_current_user)
        ):
            start_time = time.time()
            
            try:
                # Check permission
                decision = await self.policy_service.check_permission(
                    user_id=current_user["id"],
                    permission=permission,
                    resource_type="system",  # Generic system permission
                    resource_id="*"
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record metrics
                metrics_collector.record_rbac_decision(
                    decision="allow" if decision.allowed else "deny",
                    permission=permission.value,
                    resource_type="system",
                    duration=duration_ms / 1000
                )
                
                if not decision.allowed:
                    logger.warning(
                        f"Permission denied: {permission.value}",
                        user_id=current_user["id"],
                        permission=permission.value,
                        reason=decision.reason,
                        event_type="permission_denied"
                    )
                    
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: {decision.reason}"
                    )
                
                logger.debug(
                    f"Permission granted: {permission.value}",
                    user_id=current_user["id"],
                    permission=permission.value,
                    duration_ms=duration_ms,
                    event_type="permission_granted"
                )
                
                return decision
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Permission check failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Permission check failed"
                )
        
        return permission_dependency
    
    def require_resource_permission(self, permission: Permission, resource_type: str):
        """
        Dependency factory for requiring permissions on specific resources
        
        Usage:
        @app.get("/clients/{client_id}")
        async def get_client(
            client_id: str,
            current_user=Depends(security.get_current_user),
            _=Depends(security.require_resource_permission(Permission.READ_CLIENT, "client_profile"))
        ):
        """
        @trace_function(f"resource_permission_check_{permission.value}")
        async def resource_permission_dependency(
            request: Request,
            current_user: Dict[str, Any] = Depends(self.get_current_user)
        ):
            start_time = time.time()
            
            try:
                # Extract resource ID from path
                resource_id = None
                path_params = request.path_params
                
                # Try common patterns for resource ID
                for param_name in ["id", "client_id", "user_id", "plan_id", "task_id"]:
                    if param_name in path_params:
                        resource_id = path_params[param_name]
                        break
                
                if not resource_id:
                    # For endpoints without specific resource ID, use wildcard
                    resource_id = "*"
                
                # Check permission
                decision = await self.policy_service.check_permission(
                    user_id=current_user["id"],
                    permission=permission,
                    resource_type=resource_type,
                    resource_id=resource_id
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record metrics
                metrics_collector.record_rbac_decision(
                    decision="allow" if decision.allowed else "deny",
                    permission=permission.value,
                    resource_type=resource_type,
                    duration=duration_ms / 1000
                )
                
                if not decision.allowed:
                    logger.warning(
                        f"Resource permission denied: {permission.value} on {resource_type}:{resource_id}",
                        user_id=current_user["id"],
                        permission=permission.value,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        reason=decision.reason,
                        event_type="resource_permission_denied"
                    )
                    
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions for resource: {decision.reason}"
                    )
                
                logger.debug(
                    f"Resource permission granted: {permission.value} on {resource_type}:{resource_id}",
                    user_id=current_user["id"],
                    permission=permission.value,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    duration_ms=duration_ms,
                    event_type="resource_permission_granted"
                )
                
                return decision
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Resource permission check failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Resource permission check failed"
                )
        
        return resource_permission_dependency
    
    async def redact_response(
        self,
        data: Any,
        resource_type: str,
        current_user: Dict[str, Any],
        resource_id: Optional[str] = None
    ) -> Any:
        """
        Apply data redaction to response based on user permissions
        """
        if not data:
            return data
        
        # Create principal for redaction
        memberships = await self.db.organization_memberships.find({
            "user_id": current_user["id"]
        }).to_list(length=None)
        
        roles = []
        org_id = None
        for membership in memberships:
            roles.extend(membership.get("roles", []))
            if not org_id:
                org_id = membership.get("organization_id")
        
        principal = Principal(
            user_id=current_user["id"],
            roles=list(set(roles)),
            organization_id=org_id,
            organization_memberships=memberships
        )
        
        # Apply redaction
        if isinstance(data, list):
            return await self.redactor.redact_document_list(
                data, resource_type, principal
            )
        elif isinstance(data, dict):
            return await self.redactor.redact_document(
                data, resource_type, principal, resource_id
            )
        else:
            return data