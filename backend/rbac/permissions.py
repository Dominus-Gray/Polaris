"""
RBAC Permissions and Constants for Polaris Platform
"""
from enum import Enum


class Permission(Enum):
    """System permissions for role-based access control"""
    
    # User management
    READ_USER = "read:user"
    UPDATE_USER = "update:user"
    DELETE_USER = "delete:user"
    MANAGE_USERS = "manage:users"
    
    # Client management
    READ_CLIENT = "read:client"
    CREATE_CLIENT = "create:client"
    UPDATE_CLIENT = "update:client"
    DELETE_CLIENT = "delete:client"
    VIEW_SENSITIVE = "view:sensitive"  # PII, demographics, etc.
    
    # Organization management
    READ_ORGANIZATION = "read:organization"
    UPDATE_ORGANIZATION = "update:organization"
    MANAGE_MEMBERSHIPS = "manage:memberships"
    
    # Assessment permissions
    READ_ASSESSMENT = "read:assessment"
    CREATE_ASSESSMENT = "create:assessment"
    UPDATE_ASSESSMENT = "update:assessment"
    COMPLETE_ASSESSMENT = "complete:assessment"
    
    # Action plan permissions
    READ_ACTION_PLAN = "read:action_plan"
    CREATE_ACTION_PLAN = "create:action_plan"
    UPDATE_ACTION_PLAN = "update:action_plan"
    PUBLISH_ACTION_PLAN = "publish:action_plan"
    ARCHIVE_ACTION_PLAN = "archive:action_plan"
    
    # Task management
    READ_TASK = "read:task"
    CREATE_TASK = "create:task"
    UPDATE_TASK = "update:task"
    ASSIGN_TASK = "assign:task"
    COMPLETE_TASK = "complete:task"
    
    # Provider management
    READ_PROVIDER = "read:provider"
    UPDATE_PROVIDER = "update:provider"
    MANAGE_PROVIDER_PROFILES = "manage:provider_profiles"
    
    # System administration
    MANAGE_ROLES = "manage:roles"
    VIEW_AUDIT_LOGS = "view:audit_logs"
    MANAGE_SYSTEM_CONFIG = "manage:system_config"
    
    # Data export and analytics
    EXPORT_DATA = "export:data"
    VIEW_ANALYTICS = "view:analytics"
    GENERATE_REPORTS = "generate:reports"
    
    # SLA and monitoring
    VIEW_SLA_METRICS = "view:sla_metrics"
    MANAGE_SLA_CONFIG = "manage:sla_config"
    
    # Alert management
    READ_ALERTS = "read:alerts"
    ACKNOWLEDGE_ALERTS = "acknowledge:alerts"
    
    def __str__(self):
        return self.value


class Role(Enum):
    """System roles with associated permissions"""
    
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    PROVIDER_STAFF = "provider_staff"
    CASE_MANAGER = "case_manager"
    ANALYST = "analyst"
    CLIENT_USER = "client_user"
    SYSTEM_SERVICE = "system_service"
    
    def __str__(self):
        return self.value


# Role-Permission Mappings
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [
        # Full system access
        Permission.MANAGE_USERS,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.READ_CLIENT,
        Permission.CREATE_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.DELETE_CLIENT,
        Permission.VIEW_SENSITIVE,
        Permission.READ_ORGANIZATION,
        Permission.UPDATE_ORGANIZATION,
        Permission.MANAGE_MEMBERSHIPS,
        Permission.READ_ASSESSMENT,
        Permission.CREATE_ASSESSMENT,
        Permission.UPDATE_ASSESSMENT,
        Permission.COMPLETE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.CREATE_ACTION_PLAN,
        Permission.UPDATE_ACTION_PLAN,
        Permission.PUBLISH_ACTION_PLAN,
        Permission.ARCHIVE_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.CREATE_TASK,
        Permission.UPDATE_TASK,
        Permission.ASSIGN_TASK,
        Permission.COMPLETE_TASK,
        Permission.READ_PROVIDER,
        Permission.UPDATE_PROVIDER,
        Permission.MANAGE_PROVIDER_PROFILES,
        Permission.MANAGE_ROLES,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_SYSTEM_CONFIG,
        Permission.EXPORT_DATA,
        Permission.VIEW_ANALYTICS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_SLA_METRICS,
        Permission.MANAGE_SLA_CONFIG,
        Permission.READ_ALERTS,
        Permission.ACKNOWLEDGE_ALERTS,
    ],
    
    Role.ORG_ADMIN: [
        # Organization-level administration
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.READ_CLIENT,
        Permission.CREATE_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.VIEW_SENSITIVE,
        Permission.READ_ORGANIZATION,
        Permission.UPDATE_ORGANIZATION,
        Permission.MANAGE_MEMBERSHIPS,
        Permission.READ_ASSESSMENT,
        Permission.CREATE_ASSESSMENT,
        Permission.UPDATE_ASSESSMENT,
        Permission.COMPLETE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.CREATE_ACTION_PLAN,
        Permission.UPDATE_ACTION_PLAN,
        Permission.PUBLISH_ACTION_PLAN,
        Permission.ARCHIVE_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.CREATE_TASK,
        Permission.UPDATE_TASK,
        Permission.ASSIGN_TASK,
        Permission.COMPLETE_TASK,
        Permission.READ_PROVIDER,
        Permission.EXPORT_DATA,
        Permission.VIEW_ANALYTICS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_SLA_METRICS,
        Permission.READ_ALERTS,
        Permission.ACKNOWLEDGE_ALERTS,
    ],
    
    Role.PROVIDER_STAFF: [
        # Provider organization management
        Permission.READ_USER,
        Permission.READ_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.VIEW_SENSITIVE,
        Permission.READ_ASSESSMENT,
        Permission.CREATE_ASSESSMENT,
        Permission.UPDATE_ASSESSMENT,
        Permission.COMPLETE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.CREATE_ACTION_PLAN,
        Permission.UPDATE_ACTION_PLAN,
        Permission.PUBLISH_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.CREATE_TASK,
        Permission.UPDATE_TASK,
        Permission.ASSIGN_TASK,
        Permission.COMPLETE_TASK,
        Permission.READ_PROVIDER,
        Permission.UPDATE_PROVIDER,
        Permission.MANAGE_PROVIDER_PROFILES,
        Permission.VIEW_ANALYTICS,
        Permission.READ_ALERTS,
    ],
    
    Role.CASE_MANAGER: [
        # Direct client service delivery
        Permission.READ_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.VIEW_SENSITIVE,
        Permission.READ_ASSESSMENT,
        Permission.CREATE_ASSESSMENT,
        Permission.UPDATE_ASSESSMENT,
        Permission.COMPLETE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.CREATE_ACTION_PLAN,
        Permission.UPDATE_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.CREATE_TASK,
        Permission.UPDATE_TASK,
        Permission.ASSIGN_TASK,
        Permission.COMPLETE_TASK,
        Permission.READ_ALERTS,
    ],
    
    Role.ANALYST: [
        # Data analysis and reporting
        Permission.READ_CLIENT,
        Permission.READ_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.READ_PROVIDER,
        Permission.EXPORT_DATA,
        Permission.VIEW_ANALYTICS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_SLA_METRICS,
        Permission.READ_ALERTS,
    ],
    
    Role.CLIENT_USER: [
        # Self-service for clients
        Permission.READ_CLIENT,  # Own profile only
        Permission.UPDATE_CLIENT,  # Own profile only
        Permission.READ_ASSESSMENT,  # Own assessments only
        Permission.CREATE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,  # Own action plans only
        Permission.READ_TASK,  # Own tasks only
    ],
    
    Role.SYSTEM_SERVICE: [
        # System service accounts
        Permission.READ_CLIENT,
        Permission.UPDATE_CLIENT,
        Permission.READ_ASSESSMENT,
        Permission.CREATE_ASSESSMENT,
        Permission.UPDATE_ASSESSMENT,
        Permission.READ_ACTION_PLAN,
        Permission.CREATE_ACTION_PLAN,
        Permission.READ_TASK,
        Permission.CREATE_TASK,
        Permission.UPDATE_TASK,
        Permission.READ_ALERTS,
        Permission.ACKNOWLEDGE_ALERTS,
    ],
}


def get_role_permissions(role: Role) -> list[Permission]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])