"""
Health Check Endpoints for Polaris Platform
Provides comprehensive health monitoring endpoints
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import psutil
import os
from ..observability.telemetry import trace_function, metrics_collector

logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    """Health status response model"""
    status: str
    timestamp: str
    service: str
    version: str
    environment: str
    uptime_seconds: float
    checks: Dict[str, Any]


class DatabaseHealth(BaseModel):
    """Database health details"""
    status: str
    connection_time_ms: float
    collections_count: int
    last_operation_time_ms: Optional[float] = None


class SystemHealth(BaseModel):
    """System resource health"""
    status: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    connections_active: int


class ExternalServiceHealth(BaseModel):
    """External service health"""
    status: str
    response_time_ms: Optional[float] = None
    last_check: str


# Global variable to track service start time
service_start_time = time.time()


def create_health_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create health check router with database dependency"""
    router = APIRouter(prefix="/health", tags=["health"])
    
    @router.get("/system", response_model=HealthStatus)
    @trace_function("health_check_system")
    async def system_health():
        """
        Comprehensive system health check
        SLA: <100ms response time
        """
        start_time = time.time()
        
        try:
            checks = {}
            overall_status = "healthy"
            
            # Database health
            db_health = await check_database_health(db)
            checks["database"] = db_health.dict()
            if db_health.status != "healthy":
                overall_status = "degraded"
            
            # System resources
            sys_health = check_system_health()
            checks["system"] = sys_health.dict()
            if sys_health.status != "healthy" and overall_status == "healthy":
                overall_status = "degraded"
            
            # Service metadata
            checks["service"] = {
                "build_info": get_build_info(),
                "configuration": get_configuration_info(),
                "metrics": get_service_metrics()
            }
            
            response_time = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics_collector.http_requests_total.labels(
                method="GET",
                endpoint="/health/system",
                status_code=200 if overall_status != "unhealthy" else 503
            ).inc()
            
            metrics_collector.http_request_duration.labels(
                method="GET",
                endpoint="/health/system"
            ).observe(response_time / 1000)
            
            return HealthStatus(
                status=overall_status,
                timestamp=datetime.utcnow().isoformat() + "Z",
                service="polaris-platform",
                version=os.getenv("SERVICE_VERSION", "1.0.0"),
                environment=os.getenv("ENVIRONMENT", "development"),
                uptime_seconds=time.time() - service_start_time,
                checks=checks
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Health check failed")
    
    @router.get("/database", response_model=DatabaseHealth)
    @trace_function("health_check_database")
    async def database_health():
        """
        Database-specific health check
        SLA: <200ms response time
        """
        try:
            db_health = await check_database_health(db)
            
            if db_health.status != "healthy":
                raise HTTPException(status_code=503, detail="Database unhealthy")
            
            return db_health
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise HTTPException(status_code=503, detail="Database health check failed")
    
    @router.get("/external", response_model=Dict[str, ExternalServiceHealth])
    @trace_function("health_check_external")
    async def external_services_health():
        """
        External services health check
        SLA: <500ms response time
        """
        try:
            services = {}
            
            # Check external services (placeholder for actual integrations)
            services["stripe"] = await check_stripe_health()
            services["emergent_llm"] = await check_emergent_llm_health()
            services["email_service"] = await check_email_service_health()
            
            return services
            
        except Exception as e:
            logger.error(f"External services health check failed: {e}")
            raise HTTPException(status_code=503, detail="External services check failed")
    
    @router.get("/ready")
    @trace_function("readiness_check")
    async def readiness_check():
        """
        Kubernetes readiness probe
        Returns 200 if service is ready to accept traffic
        """
        try:
            # Check critical dependencies
            db_health = await check_database_health(db)
            
            if db_health.status != "healthy":
                raise HTTPException(status_code=503, detail="Service not ready")
            
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat() + "Z"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            raise HTTPException(status_code=503, detail="Service not ready")
    
    @router.get("/live")
    @trace_function("liveness_check")
    async def liveness_check():
        """
        Kubernetes liveness probe
        Returns 200 if service is alive (basic health)
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": time.time() - service_start_time
        }
    
    return router


@trace_function("check_database_health")
async def check_database_health(db: AsyncIOMotorDatabase) -> DatabaseHealth:
    """Check MongoDB database health"""
    start_time = time.time()
    
    try:
        # Test connection with ping
        await db.command("ping")
        connection_time = (time.time() - start_time) * 1000
        
        # Count collections
        collections = await db.list_collection_names()
        collections_count = len(collections)
        
        # Test a simple operation
        op_start = time.time()
        await db.users.count_documents({}, limit=1)
        operation_time = (time.time() - op_start) * 1000
        
        status = "healthy"
        if connection_time > 100:  # 100ms threshold
            status = "degraded"
        if connection_time > 500:  # 500ms threshold
            status = "unhealthy"
        
        return DatabaseHealth(
            status=status,
            connection_time_ms=connection_time,
            collections_count=collections_count,
            last_operation_time_ms=operation_time
        )
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return DatabaseHealth(
            status="unhealthy",
            connection_time_ms=(time.time() - start_time) * 1000,
            collections_count=0
        )


def check_system_health() -> SystemHealth:
    """Check system resource health"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network connections
        connections = len(psutil.net_connections())
        
        # Determine status based on thresholds
        status = "healthy"
        if cpu_percent > 80 or memory_percent > 85 or disk_percent > 90:
            status = "degraded"
        if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
            status = "unhealthy"
        
        return SystemHealth(
            status=status,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            connections_active=connections
        )
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return SystemHealth(
            status="unhealthy",
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_percent=0.0,
            connections_active=0
        )


async def check_stripe_health() -> ExternalServiceHealth:
    """Check Stripe API health (placeholder)"""
    # In a real implementation, this would make a test API call
    return ExternalServiceHealth(
        status="healthy",
        response_time_ms=50.0,
        last_check=datetime.utcnow().isoformat() + "Z"
    )


async def check_emergent_llm_health() -> ExternalServiceHealth:
    """Check Emergent LLM API health (placeholder)"""
    # In a real implementation, this would test the AI service
    return ExternalServiceHealth(
        status="healthy",
        response_time_ms=150.0,
        last_check=datetime.utcnow().isoformat() + "Z"
    )


async def check_email_service_health() -> ExternalServiceHealth:
    """Check email service health (placeholder)"""
    # In a real implementation, this would test SendGrid or other email service
    return ExternalServiceHealth(
        status="healthy",
        response_time_ms=25.0,
        last_check=datetime.utcnow().isoformat() + "Z"
    )


def get_build_info() -> Dict[str, Any]:
    """Get build and deployment information"""
    return {
        "version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "build_time": os.getenv("BUILD_TIME", "unknown"),
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
        "build_number": os.getenv("BUILD_NUMBER", "unknown")
    }


def get_configuration_info() -> Dict[str, Any]:
    """Get service configuration information (non-sensitive)"""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "tracing_enabled": os.getenv("ENABLE_TRACING", "true"),
        "metrics_enabled": os.getenv("ENABLE_METRICS", "true"),
        "database_name": os.getenv("DB_NAME", "polaris_dev")
    }


def get_service_metrics() -> Dict[str, Any]:
    """Get service-level metrics"""
    uptime = time.time() - service_start_time
    
    return {
        "uptime_seconds": uptime,
        "uptime_human": format_uptime(uptime),
        "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "open_files": len(psutil.Process().open_files()),
    }


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"