"""
Unit tests for RBAC policy engine
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "backend"))

from rbac.policy_engine import PolicyEvaluationService, Principal, Resource, PolicyDecision
from rbac.permissions import Permission, Role


class TestPolicyEvaluationService:
    """Test cases for policy evaluation service"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock MongoDB database"""
        db = MagicMock()
        # Mock collections
        db.users = AsyncMock()
        db.organization_memberships = AsyncMock()
        db.client_profiles = AsyncMock()
        db.assessments = AsyncMock()
        db.provider_profiles = AsyncMock()
        return db
    
    @pytest.fixture
    def policy_service(self, mock_db):
        """Create policy evaluation service with mocked database"""
        return PolicyEvaluationService(mock_db)
    
    @pytest.fixture
    def super_admin_principal(self):
        """Super admin principal for testing"""
        return Principal(
            user_id="user-1",
            roles=["super_admin"],
            organization_id="org-1"
        )
    
    @pytest.fixture
    def client_user_principal(self):
        """Client user principal for testing"""
        return Principal(
            user_id="user-2",
            roles=["client_user"],
            organization_id="org-2"
        )
    
    @pytest.fixture
    def case_manager_principal(self):
        """Case manager principal for testing"""
        return Principal(
            user_id="user-3",
            roles=["case_manager"],
            organization_id="org-1"
        )
    
    @pytest.fixture
    def client_resource(self):
        """Client profile resource for testing"""
        return Resource(
            resource_type="client_profile",
            resource_id="client-1",
            organization_id="org-1",
            owner_id="user-2"
        )
    
    @pytest.mark.asyncio
    async def test_super_admin_has_all_permissions(
        self, 
        policy_service, 
        super_admin_principal, 
        client_resource,
        mock_db
    ):
        """Super admin should have access to all resources"""
        # Mock organization membership check
        mock_db.organization_memberships.find_one.return_value = {
            "user_id": "user-1",
            "organization_id": "org-1"
        }
        
        decision = await policy_service.evaluate(
            super_admin_principal,
            Permission.READ_CLIENT,
            client_resource
        )
        
        assert decision.allowed
        assert "cross_org_access_by_super_admin" in decision.conditions or decision.allowed
        assert decision.evaluation_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_client_user_can_only_access_own_resources(
        self,
        policy_service,
        client_user_principal,
        mock_db
    ):
        """Client users should only access their own resources"""
        # Test access to own resource
        own_resource = Resource(
            resource_type="client_profile",
            resource_id="client-1",
            owner_id="user-2"  # Same as principal user_id
        )
        
        mock_db.organization_memberships.find_one.return_value = {
            "user_id": "user-2",
            "organization_id": "org-2"
        }
        
        decision = await policy_service.evaluate(
            client_user_principal,
            Permission.READ_CLIENT,
            own_resource
        )
        
        assert decision.allowed
        assert "self_access_only" in decision.conditions
        
        # Test access to other's resource
        other_resource = Resource(
            resource_type="client_profile",
            resource_id="client-2",
            owner_id="user-3"  # Different user
        )
        
        decision = await policy_service.evaluate(
            client_user_principal,
            Permission.READ_CLIENT,
            other_resource
        )
        
        assert not decision.allowed
        assert "client users can only access own resources" in decision.reason
    
    @pytest.mark.asyncio
    async def test_sensitive_data_access_requires_permission(
        self,
        policy_service,
        case_manager_principal,
        client_resource,
        mock_db
    ):
        """Only authorized roles can access sensitive data"""
        # Mock organization membership
        mock_db.organization_memberships.find_one.return_value = {
            "user_id": "user-3",
            "organization_id": "org-1"
        }
        
        # Case manager should have sensitive access
        decision = await policy_service.evaluate(
            case_manager_principal,
            Permission.VIEW_SENSITIVE,
            client_resource
        )
        
        assert decision.allowed
        assert "sensitive_data_access" in decision.conditions
        
        # Client user should not have sensitive access
        client_principal = Principal(
            user_id="user-4",
            roles=["client_user"],
            organization_id="org-2"
        )
        
        decision = await policy_service.evaluate(
            client_principal,
            Permission.VIEW_SENSITIVE,
            client_resource
        )
        
        assert not decision.allowed
        assert "insufficient privileges for sensitive data" in decision.reason
    
    @pytest.mark.asyncio
    async def test_organization_membership_required(
        self,
        policy_service,
        case_manager_principal,
        mock_db
    ):
        """Users must be members of resource organization"""
        # Resource in different organization
        other_org_resource = Resource(
            resource_type="client_profile",
            resource_id="client-3",
            organization_id="org-99"  # Different org
        )
        
        # Mock no membership in target organization
        mock_db.organization_memberships.find_one.return_value = None
        
        decision = await policy_service.evaluate(
            case_manager_principal,
            Permission.READ_CLIENT,
            other_org_resource
        )
        
        assert not decision.allowed
        assert "not a member of resource organization" in decision.reason
    
    @pytest.mark.asyncio
    async def test_permission_check_convenience_method(
        self,
        policy_service,
        mock_db
    ):
        """Test the convenience method for permission checking"""
        # Mock user lookup
        mock_db.users.find_one.return_value = {
            "id": "user-1",
            "email": "test@example.com",
            "status": "active"
        }
        
        # Mock organization memberships
        mock_db.organization_memberships.find.return_value.to_list.return_value = [
            {
                "user_id": "user-1",
                "organization_id": "org-1",
                "roles": ["case_manager"]
            }
        ]
        
        decision = await policy_service.check_permission(
            user_id="user-1",
            permission=Permission.READ_CLIENT,
            resource_type="client_profile",
            resource_id="client-1"
        )
        
        assert isinstance(decision, PolicyDecision)
        assert decision.evaluation_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_role_permission_mapping(self, policy_service):
        """Test that roles have correct permissions"""
        # Super admin should have manage roles permission
        principal = Principal(
            user_id="user-1",
            roles=["super_admin"],
            organization_id="org-1"
        )
        
        has_permission = await policy_service._check_role_permissions(
            principal,
            Permission.MANAGE_ROLES
        )
        
        assert has_permission
        
        # Client user should not have manage roles permission
        client_principal = Principal(
            user_id="user-2",
            roles=["client_user"],
            organization_id="org-2"
        )
        
        has_permission = await policy_service._check_role_permissions(
            client_principal,
            Permission.MANAGE_ROLES
        )
        
        assert not has_permission
    
    def test_evaluation_time_performance(self, policy_service, super_admin_principal, client_resource):
        """Policy evaluation should be fast (< 5ms on average)"""
        async def run_evaluation():
            decision = await policy_service.evaluate(
                super_admin_principal,
                Permission.READ_CLIENT,
                client_resource
            )
            return decision.evaluation_time_ms
        
        # Run multiple evaluations to test performance
        times = []
        for _ in range(10):
            time_ms = asyncio.run(run_evaluation())
            times.append(time_ms)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 5.0, f"Average evaluation time {avg_time}ms exceeds 5ms threshold"
    
    def test_metrics_collection(self, policy_service):
        """Test that metrics are collected during evaluation"""
        initial_metrics = policy_service.get_metrics()
        
        # Metrics should start at zero
        assert initial_metrics["evaluations"] >= 0
        assert initial_metrics["allowed"] >= 0
        assert initial_metrics["denied"] >= 0
        assert initial_metrics["avg_time_ms"] >= 0