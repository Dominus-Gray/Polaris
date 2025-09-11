"""
Analytics API Endpoints

Provides REST API for accessing analytics and cohort metrics with proper RBAC.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import jwt, JWTError
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

# JWT Configuration (should match main server configuration)
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Response Models
class MetricsMetadata(BaseModel):
    """Metadata for analytics responses"""
    generation_timestamp: datetime
    source_version: Optional[str] = None
    data_lag_seconds: Optional[float] = None

class ClientDailyMetrics(BaseModel):
    """Client daily metrics response"""
    client_id: str
    date: str
    risk_score_avg: Optional[float]
    tasks_completed: int
    tasks_active: int
    tasks_blocked: int
    alerts_open: int
    action_plan_versions_activated: int
    updated_at: datetime

class ClientMetricsResponse(BaseModel):
    """Response for client metrics endpoints"""
    metrics: List[ClientDailyMetrics]
    metadata: MetricsMetadata

class ClientSummaryResponse(BaseModel):
    """Response for client summary endpoint"""
    client_id: str
    latest_metrics: Optional[ClientDailyMetrics]
    metadata: MetricsMetadata

class CohortDailyMetrics(BaseModel):
    """Cohort daily metrics response"""
    cohort_tag: str
    date: str
    client_count: int
    avg_risk_score: Optional[float]
    tasks_completed: int
    alerts_open: int
    version_activations: int
    updated_at: datetime

class CohortMetricsResponse(BaseModel):
    """Response for cohort metrics endpoints"""
    metrics: List[CohortDailyMetrics]
    metadata: MetricsMetadata

class CohortSummaryResponse(BaseModel):
    """Response for cohort summary endpoint"""
    cohort_tag: str
    latest_metrics: Optional[CohortDailyMetrics]
    metadata: MetricsMetadata

# Analytics Permissions
class AnalyticsPermissions:
    VIEW_ANALYTICS_CLIENT = "VIEW_ANALYTICS_CLIENT"
    VIEW_ANALYTICS_COHORT = "VIEW_ANALYTICS_COHORT"

# Create router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_source_version() -> Optional[str]:
    """Get current git SHA for source version tracking"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Short SHA
    except Exception:
        pass
    return os.environ.get("GIT_SHA", "unknown")

async def calculate_data_lag(db: AsyncIOMotorDatabase) -> Optional[float]:
    """Calculate data lag in seconds"""
    try:
        latest_event = await db.analytics_events.find_one(
            {},
            sort=[("occurred_at", -1)]
        )
        if latest_event:
            lag = (datetime.utcnow() - latest_event["occurred_at"]).total_seconds()
            return lag
    except Exception as e:
        logger.error(f"Error calculating data lag: {e}")
    return None

def create_metadata(db: AsyncIOMotorDatabase) -> MetricsMetadata:
    """Create response metadata"""
    return MetricsMetadata(
        generation_timestamp=datetime.utcnow(),
        source_version=get_source_version()
        # data_lag_seconds will be calculated async if needed
    )

async def check_client_analytics_permission(user_id: str, target_client_id: str, db: AsyncIOMotorDatabase) -> bool:
    """Check if user has permission to view client analytics"""
    
    # Get user details
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    role = user.get("role")
    
    # SuperAdmin and Analyst can view all client analytics
    if role in ["SuperAdmin", "Analyst"]:
        return True
    
    # OrgAdmin can view analytics for clients in their organization
    if role == "OrgAdmin":
        # Check if target client is in same organization
        target_client = await db.users.find_one({"id": target_client_id})
        if target_client:
            # Both users should have same organization (via license or direct org field)
            user_org = user.get("organization") or user.get("license_code")
            target_org = target_client.get("organization") or target_client.get("license_code")
            return user_org == target_org
    
    # CaseManager can view analytics for clients in their organization
    if role == "CaseManager":
        target_client = await db.users.find_one({"id": target_client_id})
        if target_client:
            user_org = user.get("organization") or user.get("license_code")
            target_org = target_client.get("organization") or target_client.get("license_code")
            return user_org == target_org
    
    # Client can only view their own analytics
    if role == "client":
        return user_id == target_client_id
    
    return False

async def check_cohort_analytics_permission(user_id: str, db: AsyncIOMotorDatabase) -> bool:
    """Check if user has permission to view cohort analytics"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    role = user.get("role")
    
    # SuperAdmin, Analyst, and OrgAdmin can view cohort analytics
    return role in ["SuperAdmin", "Analyst", "OrgAdmin"]

# Dependency for database access
async def get_analytics_db() -> AsyncIOMotorDatabase:
    """Dependency to get database connection for analytics"""
    return db

# Dependency for current user (extracted from JWT)
async def get_current_user_id_analytics(token: str = Header(None, alias="Authorization")) -> str:
    """Get current user ID from JWT token for analytics endpoints"""
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract token from "Bearer <token>" format
        if token.startswith("Bearer "):
            token = token[7:]
        
        # Decode JWT token (reusing existing verification logic)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@analytics_router.get("/clients/{client_id}/daily", response_model=ClientMetricsResponse)
async def get_client_daily_metrics(
    client_id: str,
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncIOMotorDatabase = Depends(get_analytics_db),
    current_user_id: str = Depends(get_current_user_id_analytics)
):
    """Get daily metrics for a specific client"""
    
    # Check permissions
    has_permission = await check_client_analytics_permission(current_user_id, client_id, db)
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view client analytics")
    
    try:
        # Validate date format and range
        start_date = datetime.fromisoformat(from_date).date()
        end_date = datetime.fromisoformat(to_date).date()
        
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="end_date must be after start_date")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
        
        # Query metrics
        cursor = db.client_metrics_daily.find({
            "client_id": client_id,
            "date": {"$gte": from_date, "$lte": to_date}
        }).sort("date", 1)
        
        metrics = []
        async for metric in cursor:
            metrics.append(ClientDailyMetrics(**metric))
        
        # Create metadata
        metadata = create_metadata(db)
        metadata.data_lag_seconds = await calculate_data_lag(db)
        
        return ClientMetricsResponse(
            metrics=metrics,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting client daily metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@analytics_router.get("/clients/{client_id}/summary", response_model=ClientSummaryResponse)
async def get_client_summary(
    client_id: str,
    db: AsyncIOMotorDatabase = Depends(get_analytics_db),
    current_user_id: str = Depends(get_current_user_id_analytics)
):
    """Get latest metrics summary for a specific client"""
    
    # Check permissions
    has_permission = await check_client_analytics_permission(current_user_id, client_id, db)
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view client analytics")
    
    try:
        # Get latest metrics
        latest_metric = await db.client_metrics_daily.find_one(
            {"client_id": client_id},
            sort=[("date", -1)]
        )
        
        latest_metrics = None
        if latest_metric:
            latest_metrics = ClientDailyMetrics(**latest_metric)
        
        # Create metadata
        metadata = create_metadata(db)
        metadata.data_lag_seconds = await calculate_data_lag(db)
        
        return ClientSummaryResponse(
            client_id=client_id,
            latest_metrics=latest_metrics,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error getting client summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@analytics_router.get("/cohorts/{cohort_tag}/daily", response_model=CohortMetricsResponse)
async def get_cohort_daily_metrics(
    cohort_tag: str,
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncIOMotorDatabase = Depends(get_analytics_db),
    current_user_id: str = Depends(get_current_user_id_analytics)
):
    """Get daily metrics for a specific cohort"""
    
    # Check permissions
    has_permission = await check_cohort_analytics_permission(current_user_id, db)
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view cohort analytics")
    
    try:
        # Validate date format and range
        start_date = datetime.fromisoformat(from_date).date()
        end_date = datetime.fromisoformat(to_date).date()
        
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="end_date must be after start_date")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
        
        # Query metrics
        cursor = db.cohort_metrics_daily.find({
            "cohort_tag": cohort_tag,
            "date": {"$gte": from_date, "$lte": to_date}
        }).sort("date", 1)
        
        metrics = []
        async for metric in cursor:
            metrics.append(CohortDailyMetrics(**metric))
        
        # Create metadata
        metadata = create_metadata(db)
        metadata.data_lag_seconds = await calculate_data_lag(db)
        
        return CohortMetricsResponse(
            metrics=metrics,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting cohort daily metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@analytics_router.get("/cohorts/{cohort_tag}/summary", response_model=CohortSummaryResponse)
async def get_cohort_summary(
    cohort_tag: str,
    db: AsyncIOMotorDatabase = Depends(get_analytics_db),
    current_user_id: str = Depends(get_current_user_id_analytics)
):
    """Get latest metrics summary for a specific cohort"""
    
    # Check permissions
    has_permission = await check_cohort_analytics_permission(current_user_id, db)
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view cohort analytics")
    
    try:
        # Get latest metrics
        latest_metric = await db.cohort_metrics_daily.find_one(
            {"cohort_tag": cohort_tag},
            sort=[("date", -1)]
        )
        
        latest_metrics = None
        if latest_metric:
            latest_metrics = CohortDailyMetrics(**latest_metric)
        
        # Create metadata
        metadata = create_metadata(db)
        metadata.data_lag_seconds = await calculate_data_lag(db)
        
        return CohortSummaryResponse(
            cohort_tag=cohort_tag,
            latest_metrics=latest_metrics,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error getting cohort summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")