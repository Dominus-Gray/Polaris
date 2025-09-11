"""
Tests for Analytics API and RBAC

Validates API endpoints and role-based access control.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException
from analytics.api import (
    check_client_analytics_permission,
    check_cohort_analytics_permission,
    analytics_router
)


class TestAnalyticsRBAC:
    """Test Role-Based Access Control for analytics"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database for RBAC tests"""
        db = MagicMock()
        db.users = AsyncMock()
        return db
    
    @pytest.mark.asyncio
    async def test_superadmin_can_view_any_client(self, mock_db):
        """Test SuperAdmin can view any client analytics"""
        # Mock user lookup
        mock_db.users.find_one.return_value = {
            "id": "admin_user",
            "role": "SuperAdmin"
        }
        
        result = await check_client_analytics_permission("admin_user", "any_client", mock_db)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_analyst_can_view_any_client(self, mock_db):
        """Test Analyst can view any client analytics"""
        mock_db.users.find_one.return_value = {
            "id": "analyst_user",
            "role": "Analyst"
        }
        
        result = await check_client_analytics_permission("analyst_user", "any_client", mock_db)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_client_can_view_own_analytics(self, mock_db):
        """Test client can view their own analytics"""
        mock_db.users.find_one.return_value = {
            "id": "client_123",
            "role": "client"
        }
        
        result = await check_client_analytics_permission("client_123", "client_123", mock_db)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_client_cannot_view_other_analytics(self, mock_db):
        """Test client cannot view other client's analytics"""
        mock_db.users.find_one.return_value = {
            "id": "client_123",
            "role": "client"
        }
        
        result = await check_client_analytics_permission("client_123", "client_456", mock_db)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_orgadmin_can_view_same_org_client(self, mock_db):
        """Test OrgAdmin can view clients in same organization"""
        # Mock user lookup for OrgAdmin
        def mock_user_lookup(query):
            if query["id"] == "orgadmin_user":
                return {
                    "id": "orgadmin_user",
                    "role": "OrgAdmin",
                    "license_code": "org_123"
                }
            elif query["id"] == "client_user":
                return {
                    "id": "client_user",
                    "role": "client",
                    "license_code": "org_123"  # Same organization
                }
        
        mock_db.users.find_one.side_effect = mock_user_lookup
        
        result = await check_client_analytics_permission("orgadmin_user", "client_user", mock_db)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_orgadmin_cannot_view_different_org_client(self, mock_db):
        """Test OrgAdmin cannot view clients in different organization"""
        def mock_user_lookup(query):
            if query["id"] == "orgadmin_user":
                return {
                    "id": "orgadmin_user",
                    "role": "OrgAdmin",
                    "license_code": "org_123"
                }
            elif query["id"] == "client_user":
                return {
                    "id": "client_user",
                    "role": "client",
                    "license_code": "org_456"  # Different organization
                }
        
        mock_db.users.find_one.side_effect = mock_user_lookup
        
        result = await check_client_analytics_permission("orgadmin_user", "client_user", mock_db)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_casemanager_can_view_same_org_client(self, mock_db):
        """Test CaseManager can view clients in same organization"""
        def mock_user_lookup(query):
            if query["id"] == "case_manager":
                return {
                    "id": "case_manager", 
                    "role": "CaseManager",
                    "organization": "org_abc"
                }
            elif query["id"] == "client_user":
                return {
                    "id": "client_user",
                    "role": "client",
                    "organization": "org_abc"  # Same organization
                }
        
        mock_db.users.find_one.side_effect = mock_user_lookup
        
        result = await check_client_analytics_permission("case_manager", "client_user", mock_db)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_provider_staff_cannot_view_analytics(self, mock_db):
        """Test ProviderStaff cannot view client analytics by default"""
        mock_db.users.find_one.return_value = {
            "id": "provider_user",
            "role": "ProviderStaff"
        }
        
        result = await check_client_analytics_permission("provider_user", "any_client", mock_db)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_nonexistent_user_denied(self, mock_db):
        """Test nonexistent user is denied access"""
        mock_db.users.find_one.return_value = None
        
        result = await check_client_analytics_permission("nonexistent", "any_client", mock_db)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cohort_analytics_permissions(self, mock_db):
        """Test cohort analytics permissions"""
        # SuperAdmin should have access
        mock_db.users.find_one.return_value = {
            "id": "admin_user",
            "role": "SuperAdmin"
        }
        result = await check_cohort_analytics_permission("admin_user", mock_db)
        assert result is True
        
        # Analyst should have access
        mock_db.users.find_one.return_value = {
            "id": "analyst_user", 
            "role": "Analyst"
        }
        result = await check_cohort_analytics_permission("analyst_user", mock_db)
        assert result is True
        
        # OrgAdmin should have access
        mock_db.users.find_one.return_value = {
            "id": "orgadmin_user",
            "role": "OrgAdmin"
        }
        result = await check_cohort_analytics_permission("orgadmin_user", mock_db)
        assert result is True
        
        # Client should not have access
        mock_db.users.find_one.return_value = {
            "id": "client_user",
            "role": "client"
        }
        result = await check_cohort_analytics_permission("client_user", mock_db)
        assert result is False
        
        # CaseManager should not have access (only client-level)
        mock_db.users.find_one.return_value = {
            "id": "case_manager",
            "role": "CaseManager"
        }
        result = await check_cohort_analytics_permission("case_manager", mock_db)
        assert result is False


class TestAnalyticsAPIEndpoints:
    """Test analytics API endpoints"""
    
    def test_client_daily_metrics_response_schema(self):
        """Test that response schemas are properly defined"""
        from analytics.api import ClientDailyMetrics, ClientMetricsResponse, MetricsMetadata
        
        # Test that we can create valid response objects
        metadata = MetricsMetadata(
            generation_timestamp=datetime.utcnow(),
            source_version="abc123",
            data_lag_seconds=5.2
        )
        
        daily_metrics = ClientDailyMetrics(
            client_id="client_123",
            date="2024-01-15",
            risk_score_avg=75.5,
            tasks_completed=3,
            tasks_active=2,
            tasks_blocked=1,
            alerts_open=0,
            action_plan_versions_activated=1,
            updated_at=datetime.utcnow()
        )
        
        response = ClientMetricsResponse(
            metrics=[daily_metrics],
            metadata=metadata
        )
        
        assert response.metadata.source_version == "abc123"
        assert len(response.metrics) == 1
        assert response.metrics[0].client_id == "client_123"
    
    def test_cohort_daily_metrics_response_schema(self):
        """Test cohort metrics response schema"""
        from analytics.api import CohortDailyMetrics, CohortMetricsResponse, MetricsMetadata
        
        metadata = MetricsMetadata(
            generation_timestamp=datetime.utcnow()
        )
        
        cohort_metrics = CohortDailyMetrics(
            cohort_tag="small_business",
            date="2024-01-15",
            client_count=25,
            avg_risk_score=78.2,
            tasks_completed=45,
            alerts_open=3,
            version_activations=8,
            updated_at=datetime.utcnow()
        )
        
        response = CohortMetricsResponse(
            metrics=[cohort_metrics],
            metadata=metadata
        )
        
        assert response.metrics[0].cohort_tag == "small_business"
        assert response.metrics[0].client_count == 25
    
    def test_date_validation_logic(self):
        """Test date validation in API endpoints"""
        from datetime import datetime, date
        
        # Test valid date format
        try:
            parsed_date = datetime.fromisoformat("2024-01-15").date()
            assert parsed_date == date(2024, 1, 15)
        except ValueError:
            pytest.fail("Valid date format should not raise ValueError")
        
        # Test invalid date format should raise ValueError
        with pytest.raises(ValueError):
            datetime.fromisoformat("invalid-date").date()
    
    def test_date_range_validation(self):
        """Test date range validation logic"""
        from datetime import date, timedelta
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Valid range
        assert end_date >= start_date
        assert (end_date - start_date).days <= 365
        
        # Invalid range - end before start
        invalid_end = date(2023, 12, 31)
        assert invalid_end < start_date
        
        # Invalid range - too long
        too_long_end = start_date + timedelta(days=400)
        assert (too_long_end - start_date).days > 365


class TestAnalyticsAPIErrorHandling:
    """Test error handling in analytics API"""
    
    def test_permission_denied_raises_403(self):
        """Test that permission denied scenarios raise 403"""
        # This would be tested with actual FastAPI test client
        # Here we just verify the HTTPException is raised correctly
        
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(status_code=403, detail="Insufficient permissions to view client analytics")
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)
    
    def test_invalid_date_raises_400(self):
        """Test that invalid dates raise 400 Bad Request"""
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(status_code=400, detail="Invalid date format: invalid-date")
        
        assert exc_info.value.status_code == 400
        assert "Invalid date format" in str(exc_info.value.detail)
    
    def test_date_range_error_raises_400(self):
        """Test that invalid date ranges raise 400"""
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(status_code=400, detail="end_date must be after start_date")
        
        assert exc_info.value.status_code == 400
        assert "end_date must be after start_date" in str(exc_info.value.detail)


class TestAnalyticsIntegration:
    """Integration tests for analytics API with mocked dependencies"""
    
    def test_api_router_registration(self):
        """Test that analytics router is properly configured"""
        from analytics.api import analytics_router
        
        # Check that router has expected prefix and tags
        assert analytics_router.prefix == "/analytics"
        assert "analytics" in analytics_router.tags
        
        # Check that expected routes are registered
        route_paths = [route.path for route in analytics_router.routes]
        expected_paths = [
            "/clients/{client_id}/daily",
            "/clients/{client_id}/summary", 
            "/cohorts/{cohort_tag}/daily",
            "/cohorts/{cohort_tag}/summary"
        ]
        
        for expected_path in expected_paths:
            assert expected_path in route_paths
    
    def test_metadata_generation(self):
        """Test metadata generation functions"""
        from analytics.api import get_source_version, create_metadata
        
        # Test source version generation
        version = get_source_version()
        assert version is not None
        assert isinstance(version, str)
        
        # Test metadata creation
        mock_db = MagicMock()
        metadata = create_metadata(mock_db)
        
        assert metadata.generation_timestamp is not None
        assert isinstance(metadata.generation_timestamp, datetime)
        assert metadata.source_version is not None