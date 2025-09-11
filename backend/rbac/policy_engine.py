"""
RBAC Policy Evaluation Engine for Polaris Platform
"""
import time
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
from .permissions import Permission, Role, ROLE_PERMISSIONS, get_role_permissions

logger = logging.getLogger(__name__)


@dataclass
class Principal:
    """Represents an actor (user, service) attempting to perform an action"""
    user_id: str
    roles: List[str]
    organization_id: Optional[str] = None
    organization_memberships: List[Dict[str, Any]] = None
    is_service_account: bool = False
    
    def __post_init__(self):
        if self.organization_memberships is None:
            self.organization_memberships = []


@dataclass
class Resource:
    """Represents a resource being accessed"""
    resource_type: str
    resource_id: str
    organization_id: Optional[str] = None
    owner_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PolicyDecision:
    """Result of a policy evaluation"""
    allowed: bool
    reason: str
    conditions: List[str] = None
    evaluation_time_ms: float = 0.0
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []


class PolicyEvaluationService:
    """Core RBAC policy evaluation service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._metrics = {
            "evaluations": 0,
            "allowed": 0,
            "denied": 0,
            "avg_time_ms": 0.0
        }
    
    async def evaluate(
        self, 
        principal: Principal, 
        permission: Permission, 
        resource: Resource
    ) -> PolicyDecision:
        """
        Evaluate whether a principal has permission to access a resource
        
        Args:
            principal: The actor attempting the action
            permission: The permission being requested  
            resource: The resource being accessed
            
        Returns:
            PolicyDecision with allow/deny and reasoning
        """
        start_time = time.time()
        
        try:
            # 1. Check if principal has the permission through any role
            has_permission = await self._check_role_permissions(principal, permission)
            if not has_permission:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Principal lacks required permission: {permission}",
                    evaluation_time_ms=(time.time() - start_time) * 1000
                )
            
            # 2. Apply attribute-based checks (organization, ownership, etc.)
            attribute_check = await self._check_attribute_constraints(
                principal, permission, resource
            )
            if not attribute_check.allowed:
                return attribute_check
            
            # 3. Apply resource-specific policies
            resource_check = await self._check_resource_policies(
                principal, permission, resource
            )
            if not resource_check.allowed:
                return resource_check
            
            # Success - allowed with any conditions
            decision = PolicyDecision(
                allowed=True,
                reason="Permission granted",
                conditions=attribute_check.conditions + resource_check.conditions,
                evaluation_time_ms=(time.time() - start_time) * 1000
            )
            
            # Update metrics
            self._update_metrics(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Policy evaluation error: {e}")
            return PolicyDecision(
                allowed=False,
                reason=f"Policy evaluation failed: {str(e)}",
                evaluation_time_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_role_permissions(
        self, 
        principal: Principal, 
        permission: Permission
    ) -> bool:
        """Check if any of the principal's roles grant the permission"""
        principal_permissions = set()
        
        for role_str in principal.roles:
            try:
                role = Role(role_str)
                role_perms = get_role_permissions(role)
                principal_permissions.update(role_perms)
            except ValueError:
                logger.warning(f"Unknown role: {role_str}")
                continue
        
        return permission in principal_permissions
    
    async def _check_attribute_constraints(
        self, 
        principal: Principal, 
        permission: Permission, 
        resource: Resource
    ) -> PolicyDecision:
        """Apply attribute-based access control checks"""
        conditions = []
        
        # Organization-based constraints
        if resource.organization_id and principal.organization_id:
            # Check if principal is member of resource organization
            is_member = await self._is_organization_member(
                principal.user_id, resource.organization_id
            )
            
            if not is_member:
                # Super admins can access across organizations
                if not self._has_role(principal, Role.SUPER_ADMIN):
                    return PolicyDecision(
                        allowed=False,
                        reason="Access denied: not a member of resource organization"
                    )
                else:
                    conditions.append("cross_org_access_by_super_admin")
        
        # Ownership-based constraints for client users
        if self._has_role(principal, Role.CLIENT_USER):
            # Client users can only access their own resources
            if resource.owner_id and resource.owner_id != principal.user_id:
                return PolicyDecision(
                    allowed=False,
                    reason="Access denied: client users can only access own resources"
                )
            conditions.append("self_access_only")
        
        # Sensitive data access constraints
        if permission == Permission.VIEW_SENSITIVE:
            # Only specific roles can view sensitive data
            allowed_roles = {Role.SUPER_ADMIN, Role.ORG_ADMIN, Role.PROVIDER_STAFF, Role.CASE_MANAGER}
            if not any(self._has_role(principal, role) for role in allowed_roles):
                return PolicyDecision(
                    allowed=False,
                    reason="Access denied: insufficient privileges for sensitive data"
                )
            conditions.append("sensitive_data_access")
        
        return PolicyDecision(allowed=True, reason="Attribute checks passed", conditions=conditions)
    
    async def _check_resource_policies(
        self, 
        principal: Principal, 
        permission: Permission, 
        resource: Resource
    ) -> PolicyDecision:
        """Apply resource-specific policies"""
        conditions = []
        
        # Client profile specific policies
        if resource.resource_type == "client_profile":
            # Check if client is assigned to provider
            if self._has_role(principal, Role.PROVIDER_STAFF):
                is_assigned = await self._is_client_assigned_to_provider(
                    resource.resource_id, principal.organization_id
                )
                if not is_assigned and not self._has_role(principal, Role.SUPER_ADMIN):
                    return PolicyDecision(
                        allowed=False,
                        reason="Access denied: client not assigned to your organization"
                    )
                conditions.append("provider_assignment_verified")
        
        # Assessment specific policies
        if resource.resource_type == "assessment":
            # Check assessment ownership/assignment
            if permission in [Permission.UPDATE_ASSESSMENT, Permission.COMPLETE_ASSESSMENT]:
                can_modify = await self._can_modify_assessment(
                    principal, resource.resource_id
                )
                if not can_modify:
                    return PolicyDecision(
                        allowed=False,
                        reason="Access denied: cannot modify this assessment"
                    )
                conditions.append("assessment_modification_allowed")
        
        return PolicyDecision(allowed=True, reason="Resource checks passed", conditions=conditions)
    
    async def _is_organization_member(self, user_id: str, organization_id: str) -> bool:
        """Check if user is a member of the organization"""
        membership = await self.db.organization_memberships.find_one({
            "user_id": user_id,
            "organization_id": organization_id
        })
        return membership is not None
    
    async def _is_client_assigned_to_provider(
        self, 
        client_id: str, 
        provider_organization_id: str
    ) -> bool:
        """Check if client is assigned to provider organization"""
        client = await self.db.client_profiles.find_one({"id": client_id})
        if not client:
            return False
        
        # Check if assigned provider belongs to the organization
        if client.get("assigned_provider_id"):
            provider = await self.db.provider_profiles.find_one({
                "id": client["assigned_provider_id"]
            })
            return provider and provider.get("organization_id") == provider_organization_id
        
        return False
    
    async def _can_modify_assessment(self, principal: Principal, assessment_id: str) -> bool:
        """Check if principal can modify the assessment"""
        assessment = await self.db.assessments.find_one({"id": assessment_id})
        if not assessment:
            return False
        
        # Creator can modify
        if assessment.get("created_by") == principal.user_id:
            return True
        
        # Case managers and above in same organization can modify
        if self._has_role(principal, Role.CASE_MANAGER):
            # Check if assessment client is in same organization
            client = await self.db.client_profiles.find_one({
                "id": assessment["client_id"]
            })
            if client and client.get("organization_id") == principal.organization_id:
                return True
        
        return False
    
    def _has_role(self, principal: Principal, role: Role) -> bool:
        """Check if principal has a specific role"""
        return role.value in principal.roles
    
    def _update_metrics(self, decision: PolicyDecision):
        """Update evaluation metrics"""
        self._metrics["evaluations"] += 1
        if decision.allowed:
            self._metrics["allowed"] += 1
        else:
            self._metrics["denied"] += 1
        
        # Update average time
        total_evals = self._metrics["evaluations"]
        current_avg = self._metrics["avg_time_ms"]
        self._metrics["avg_time_ms"] = (
            (current_avg * (total_evals - 1) + decision.evaluation_time_ms) / total_evals
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get evaluation metrics"""
        return self._metrics.copy()
    
    async def check_permission(
        self, 
        user_id: str, 
        permission: Permission, 
        resource_type: str, 
        resource_id: str,
        resource_metadata: Dict[str, Any] = None
    ) -> PolicyDecision:
        """
        Convenience method for checking permissions
        
        Args:
            user_id: User ID of the principal
            permission: Permission to check
            resource_type: Type of resource being accessed
            resource_id: ID of the resource
            resource_metadata: Additional resource metadata
            
        Returns:
            PolicyDecision
        """
        # Load principal information
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return PolicyDecision(
                allowed=False,
                reason="User not found"
            )
        
        # Get user's organization memberships
        memberships = await self.db.organization_memberships.find({
            "user_id": user_id
        }).to_list(length=None)
        
        # Extract roles from memberships
        roles = []
        org_id = None
        for membership in memberships:
            roles.extend(membership.get("roles", []))
            if not org_id:  # Use first organization as primary
                org_id = membership.get("organization_id")
        
        principal = Principal(
            user_id=user_id,
            roles=list(set(roles)),  # Deduplicate
            organization_id=org_id,
            organization_memberships=memberships
        )
        
        resource = Resource(
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=resource_metadata or {}
        )
        
        return await self.evaluate(principal, permission, resource)