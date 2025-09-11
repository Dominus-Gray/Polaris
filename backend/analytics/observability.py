"""
Analytics Observability

Prometheus metrics, structured logging, and tracing for analytics operations.
"""

from prometheus_client import Counter, Histogram, Gauge
import logging
import time
import functools
from typing import Dict, Any, Optional
from datetime import datetime

# Prometheus Metrics
analytics_events_ingested_total = Counter(
    'analytics_events_ingested_total',
    'Total analytics events ingested',
    ['event_type', 'source']
)

analytics_projection_cycles_total = Counter(
    'analytics_projection_cycles_total', 
    'Total analytics projection cycles',
    ['result', 'projection_name']
)

analytics_projection_cycle_duration_seconds = Histogram(
    'analytics_projection_cycle_duration_seconds',
    'Analytics projection cycle duration',
    ['projection_name']
)

analytics_backfill_runtime_seconds = Histogram(
    'analytics_backfill_runtime_seconds',
    'Analytics backfill operation duration'
)

analytics_data_lag_seconds = Gauge(
    'analytics_data_lag_seconds',
    'Current analytics data lag in seconds'
)

# Additional metrics for detailed monitoring
analytics_events_processing_errors_total = Counter(
    'analytics_events_processing_errors_total',
    'Total analytics events processing errors',
    ['error_type', 'event_type']
)

analytics_api_requests_total = Counter(
    'analytics_api_requests_total',
    'Total analytics API requests',
    ['endpoint', 'method', 'status_code']
)

analytics_api_request_duration_seconds = Histogram(
    'analytics_api_request_duration_seconds',
    'Analytics API request duration',
    ['endpoint', 'method']
)

# Structured Logger
class AnalyticsLogger:
    """Structured logger for analytics operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"analytics.{name}")
    
    def log_ingestion_batch(self, results: Dict[str, int], duration: float):
        """Log batch ingestion results"""
        self.logger.info(
            "Analytics ingestion batch completed",
            extra={
                "operation": "ingestion_batch",
                "events_ingested": results.get("ingested", 0),
                "events_duplicates": results.get("duplicates", 0),
                "events_errors": results.get("errors", 0),
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_projection_cycle(self, projection_name: str, results: Dict[str, Any]):
        """Log projection cycle results"""
        self.logger.info(
            "Analytics projection cycle completed",
            extra={
                "operation": "projection_cycle",
                "projection_name": projection_name,
                "success": results.get("success", False),
                "events_processed": results.get("events_processed", 0),
                "clients_updated": results.get("clients_updated", 0),
                "cohorts_updated": results.get("cohorts_updated", 0),
                "duration_seconds": results.get("duration_seconds", 0),
                "error": results.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_backfill_operation(self, from_date: str, to_date: str, results: Dict[str, Any]):
        """Log backfill operation results"""
        self.logger.info(
            "Analytics backfill operation completed",
            extra={
                "operation": "backfill",
                "from_date": from_date,
                "to_date": to_date,
                "success": results.get("success", False),
                "dates_processed": results.get("dates_processed", 0),
                "error": results.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, duration: float, user_id: Optional[str] = None):
        """Log analytics API request"""
        self.logger.info(
            "Analytics API request",
            extra={
                "operation": "api_request",
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_seconds": duration,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Decorators for instrumentation
def track_ingestion_metrics(event_type: str, source: str = "polaris"):
    """Decorator to track event ingestion metrics"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                analytics_events_ingested_total.labels(
                    event_type=event_type,
                    source=source
                ).inc()
                return result
            except Exception as e:
                analytics_events_processing_errors_total.labels(
                    error_type=type(e).__name__,
                    event_type=event_type
                ).inc()
                raise
        return wrapper
    return decorator

def track_projection_metrics(projection_name: str):
    """Decorator to track projection cycle metrics"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                analytics_projection_cycle_duration_seconds.labels(
                    projection_name=projection_name
                ).observe(duration)
                
                success = result.get("success", False)
                analytics_projection_cycles_total.labels(
                    result="success" if success else "error",
                    projection_name=projection_name
                ).inc()
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                analytics_projection_cycle_duration_seconds.labels(
                    projection_name=projection_name
                ).observe(duration)
                
                analytics_projection_cycles_total.labels(
                    result="error",
                    projection_name=projection_name
                ).inc()
                raise
        return wrapper
    return decorator

def track_api_metrics(endpoint: str, method: str):
    """Decorator to track API request metrics"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # Extract status code from HTTP exceptions
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                duration = time.time() - start_time
                
                analytics_api_requests_total.labels(
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code
                ).inc()
                
                analytics_api_request_duration_seconds.labels(
                    endpoint=endpoint,
                    method=method
                ).observe(duration)
        return wrapper
    return decorator

def track_backfill_metrics():
    """Decorator to track backfill operation metrics"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                analytics_backfill_runtime_seconds.observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                analytics_backfill_runtime_seconds.observe(duration)
                raise
        return wrapper
    return decorator


class DataLagMonitor:
    """Monitor and update data lag metrics"""
    
    def __init__(self, db):
        self.db = db
        self.logger = AnalyticsLogger("data_lag")
    
    async def update_data_lag_metric(self):
        """Update the data lag gauge metric"""
        try:
            # Get latest event timestamp
            latest_event = await self.db.analytics_events.find_one(
                {},
                sort=[("occurred_at", -1)]
            )
            
            if latest_event:
                lag_seconds = (datetime.utcnow() - latest_event["occurred_at"]).total_seconds()
                analytics_data_lag_seconds.set(lag_seconds)
                
                # Log if lag is significant
                if lag_seconds > 60:  # More than 1 minute lag
                    self.logger.logger.warning(
                        "Significant analytics data lag detected",
                        extra={
                            "lag_seconds": lag_seconds,
                            "latest_event_time": latest_event["occurred_at"].isoformat(),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
            else:
                # No events found, set lag to -1 to indicate no data
                analytics_data_lag_seconds.set(-1)
                
        except Exception as e:
            self.logger.logger.error(f"Error updating data lag metric: {e}")


# Tracing context manager
class AnalyticsTracer:
    """Simple tracing context for analytics operations"""
    
    def __init__(self, operation_name: str, logger: AnalyticsLogger):
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        self.context = {}
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.logger.debug(
            f"Starting analytics operation: {self.operation_name}",
            extra={
                "operation": self.operation_name,
                "phase": "start",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.logger.debug(
                f"Completed analytics operation: {self.operation_name}",
                extra={
                    "operation": self.operation_name,
                    "phase": "complete",
                    "duration_seconds": duration,
                    "context": self.context,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        else:
            self.logger.logger.error(
                f"Failed analytics operation: {self.operation_name}",
                extra={
                    "operation": self.operation_name,
                    "phase": "error",
                    "duration_seconds": duration,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                    "context": self.context,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    def add_context(self, key: str, value: Any):
        """Add context data to the trace"""
        self.context[key] = value


# Factory functions for common loggers
def get_ingestion_logger() -> AnalyticsLogger:
    """Get logger for ingestion operations"""
    return AnalyticsLogger("ingestion")

def get_projection_logger() -> AnalyticsLogger:
    """Get logger for projection operations"""
    return AnalyticsLogger("projection")

def get_api_logger() -> AnalyticsLogger:
    """Get logger for API operations"""
    return AnalyticsLogger("api")