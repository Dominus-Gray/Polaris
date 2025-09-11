"""
Tests for SLA Breach Detection & Notification System
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
import sys
import os

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server import (
    SLAEvaluationEngine, 
    SLADataCollector, 
    SLABreachManager,
    SLADefinition,
    SLAInstance,
    SLABreach
)

class TestSLAEvaluationEngine:
    """Test the core SLA evaluation logic"""
    
    def test_evaluate_objective_less_than(self):
        """Test less than operator evaluation"""
        # Should pass when current < target
        assert SLAEvaluationEngine.evaluate_objective("latency", 25.0, 30.0, "lt") == True
        # Should fail when current >= target
        assert SLAEvaluationEngine.evaluate_objective("latency", 30.0, 30.0, "lt") == False
        assert SLAEvaluationEngine.evaluate_objective("latency", 35.0, 30.0, "lt") == False
    
    def test_evaluate_objective_less_than_equal(self):
        """Test less than or equal operator evaluation"""
        # Should pass when current <= target
        assert SLAEvaluationEngine.evaluate_objective("latency", 25.0, 30.0, "lte") == True
        assert SLAEvaluationEngine.evaluate_objective("latency", 30.0, 30.0, "lte") == True
        # Should fail when current > target
        assert SLAEvaluationEngine.evaluate_objective("latency", 35.0, 30.0, "lte") == False
    
    def test_evaluate_objective_greater_than(self):
        """Test greater than operator evaluation"""
        # Should pass when current > target
        assert SLAEvaluationEngine.evaluate_objective("success_rate", 95.0, 90.0, "gt") == True
        # Should fail when current <= target
        assert SLAEvaluationEngine.evaluate_objective("success_rate", 90.0, 90.0, "gt") == False
        assert SLAEvaluationEngine.evaluate_objective("success_rate", 85.0, 90.0, "gt") == False
    
    def test_calculate_severity_latency(self):
        """Test severity calculation for latency metrics"""
        # Critical: 3x over target
        assert SLAEvaluationEngine.calculate_severity(90.0, 30.0, "latency") == "critical"
        # High: 2x over target
        assert SLAEvaluationEngine.calculate_severity(60.0, 30.0, "latency") == "high"
        # Medium: 1.5x over target
        assert SLAEvaluationEngine.calculate_severity(45.0, 30.0, "latency") == "medium"
        # Low: just over target
        assert SLAEvaluationEngine.calculate_severity(35.0, 30.0, "latency") == "low"
    
    def test_calculate_severity_success_rate(self):
        """Test severity calculation for success rate metrics"""
        # Critical: 50+ points below target
        assert SLAEvaluationEngine.calculate_severity(40.0, 95.0, "success_rate") == "critical"
        # High: 25+ points below target
        assert SLAEvaluationEngine.calculate_severity(65.0, 95.0, "success_rate") == "high"
        # Medium: 10+ points below target
        assert SLAEvaluationEngine.calculate_severity(80.0, 95.0, "success_rate") == "medium"
        # Low: slightly below target
        assert SLAEvaluationEngine.calculate_severity(90.0, 95.0, "success_rate") == "low"

class TestSLADataCollector:
    """Test SLA data collection functionality"""
    
    @pytest.mark.asyncio
    async def test_collect_assessment_completion_latency_no_data(self):
        """Test assessment latency collection with no data"""
        with patch('server.db') as mock_db:
            # Mock empty result
            mock_db.assessments.find.return_value.to_list = AsyncMock(return_value=[])
            
            result = await SLADataCollector.collect_assessment_completion_latency()
            
            assert result == {"avg_latency": 0.0, "max_latency": 0.0, "count": 0}
    
    @pytest.mark.asyncio
    async def test_collect_assessment_completion_latency_with_data(self):
        """Test assessment latency collection with sample data"""
        with patch('server.db') as mock_db:
            # Mock assessment data
            now = datetime.utcnow()
            assessments = [
                {
                    "created_at": now - timedelta(minutes=60),
                    "completed_at": now - timedelta(minutes=30),  # 30 minute latency
                },
                {
                    "created_at": now - timedelta(minutes=90),
                    "completed_at": now - timedelta(minutes=30),  # 60 minute latency
                }
            ]
            mock_db.assessments.find.return_value.to_list = AsyncMock(return_value=assessments)
            
            result = await SLADataCollector.collect_assessment_completion_latency()
            
            assert result["count"] == 2
            assert result["avg_latency"] == 45.0  # Average of 30 and 60
            assert result["max_latency"] == 60.0
    
    @pytest.mark.asyncio
    async def test_collect_analytics_job_freshness_no_data(self):
        """Test analytics freshness collection with no data"""
        with patch('server.db') as mock_db:
            # Mock empty result
            mock_db.analytics_jobs.find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
            
            result = await SLADataCollector.collect_analytics_job_freshness()
            
            assert result["freshness_minutes"] == float('inf')
            assert result["last_run"] is None

class TestSLABreachManager:
    """Test SLA breach management functionality"""
    
    @pytest.mark.asyncio
    async def test_get_current_metric_value_assessment(self):
        """Test getting current metric value for assessment completion"""
        sla_def = {"slug": "assessment_completion_latency"}
        
        with patch.object(SLADataCollector, 'collect_assessment_completion_latency') as mock_collect:
            mock_collect.return_value = {"avg_latency": 45.0}
            
            result = await SLABreachManager._get_current_metric_value(sla_def)
            
            assert result == 45.0
    
    @pytest.mark.asyncio
    async def test_get_current_metric_value_consent(self):
        """Test getting current metric value for consent processing"""
        sla_def = {"slug": "consent_processing_latency"}
        
        with patch.object(SLADataCollector, 'collect_consent_processing_latency') as mock_collect:
            mock_collect.return_value = {"avg_latency": 120.0}
            
            result = await SLABreachManager._get_current_metric_value(sla_def)
            
            assert result == 120.0
    
    @pytest.mark.asyncio
    async def test_get_current_metric_value_analytics(self):
        """Test getting current metric value for analytics freshness"""
        sla_def = {"slug": "analytics_freshness"}
        
        with patch.object(SLADataCollector, 'collect_analytics_job_freshness') as mock_collect:
            mock_collect.return_value = {"freshness_minutes": 480.0}
            
            result = await SLABreachManager._get_current_metric_value(sla_def)
            
            assert result == 480.0
    
    @pytest.mark.asyncio
    async def test_get_or_create_instance_new(self):
        """Test creating a new SLA instance"""
        sla_def = {"id": "test-sla-id"}
        current_value = 45.0
        
        with patch('server.db') as mock_db:
            # Mock no existing instance
            mock_db.sla_instances.find_one = AsyncMock(return_value=None)
            mock_db.sla_instances.insert_one = AsyncMock()
            
            result = await SLABreachManager._get_or_create_instance(sla_def, current_value)
            
            assert result["sla_definition_id"] == "test-sla-id"
            assert result["current_value"] == 45.0
            assert result["status"] == "active"
            assert result["breach_count"] == 0
    
    @pytest.mark.asyncio 
    async def test_get_or_create_instance_existing(self):
        """Test updating an existing SLA instance"""
        sla_def = {"id": "test-sla-id"}
        current_value = 45.0
        existing_instance = {
            "id": "instance-id",
            "sla_definition_id": "test-sla-id",
            "status": "active"
        }
        
        with patch('server.db') as mock_db:
            mock_db.sla_instances.find_one = AsyncMock(return_value=existing_instance)
            mock_db.sla_instances.update_one = AsyncMock()
            
            result = await SLABreachManager._get_or_create_instance(sla_def, current_value)
            
            assert result["current_value"] == 45.0
            mock_db.sla_instances.update_one.assert_called_once()

class TestSLAModels:
    """Test SLA Pydantic models"""
    
    def test_sla_definition_model(self):
        """Test SLA definition model validation"""
        sla_def = SLADefinition(
            slug="test_sla",
            description="Test SLA",
            objective_type="latency",
            target_numeric=30.0,
            window_minutes=1440,
            threshold_operator="lte"
        )
        
        assert sla_def.slug == "test_sla"
        assert sla_def.objective_type == "latency"
        assert sla_def.target_numeric == 30.0
        assert sla_def.enabled == True  # Default value
    
    def test_sla_definition_invalid_objective_type(self):
        """Test SLA definition with invalid objective type"""
        with pytest.raises(ValueError):
            SLADefinition(
                slug="test_sla",
                description="Test SLA",
                objective_type="invalid_type",
                target_numeric=30.0,
                window_minutes=1440,
                threshold_operator="lte"
            )
    
    def test_sla_definition_invalid_operator(self):
        """Test SLA definition with invalid threshold operator"""
        with pytest.raises(ValueError):
            SLADefinition(
                slug="test_sla",
                description="Test SLA",
                objective_type="latency",
                target_numeric=30.0,
                window_minutes=1440,
                threshold_operator="invalid_op"
            )
    
    def test_sla_breach_model(self):
        """Test SLA breach model validation"""
        breach = SLABreach(
            sla_instance_id="instance-id",
            sla_definition_id="def-id",
            breach_value=45.0,
            target_value=30.0,
            severity="medium"
        )
        
        assert breach.sla_instance_id == "instance-id"
        assert breach.breach_value == 45.0
        assert breach.status == "open"  # Default value
        assert breach.escalation_level == 0  # Default value

if __name__ == "__main__":
    pytest.main([__file__])