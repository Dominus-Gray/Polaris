"""
OpenTelemetry Tracing and Metrics Setup for Polaris Platform
"""
import os
import logging
from typing import Optional, Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.motor import MotorInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

logger = logging.getLogger(__name__)


class ObservabilityConfig:
    """Configuration for observability features"""
    
    def __init__(self):
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.service_name = os.getenv("SERVICE_NAME", "polaris-platform")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.otel_exporter_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8090"))


class TelemetryManager:
    """Manages OpenTelemetry setup and instrumentation"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize OpenTelemetry tracing and metrics"""
        if self._initialized:
            return
        
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "environment": self.config.environment,
        })
        
        if self.config.enable_tracing:
            self._setup_tracing(resource)
        
        if self.config.enable_metrics:
            self._setup_metrics(resource)
        
        # Setup propagation
        set_global_textmap(B3MultiFormat())
        
        self._initialized = True
        logger.info("OpenTelemetry initialized successfully")
    
    def _setup_tracing(self, resource: Resource):
        """Setup distributed tracing"""
        trace_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(trace_provider)
        
        # Setup OTLP exporter if endpoint is configured
        if self.config.otel_exporter_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.otel_exporter_endpoint,
                insecure=True  # Use TLS in production
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace_provider.add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(self.config.service_name)
        logger.info("Distributed tracing configured")
    
    def _setup_metrics(self, resource: Resource):
        """Setup metrics collection"""
        # Setup OTLP metrics exporter if endpoint is configured
        metric_readers = []
        if self.config.otel_exporter_endpoint:
            otlp_exporter = OTLPMetricExporter(
                endpoint=self.config.otel_exporter_endpoint,
                insecure=True
            )
            metric_reader = PeriodicExportingMetricReader(
                exporter=otlp_exporter,
                export_interval_millis=30000  # Export every 30 seconds
            )
            metric_readers.append(metric_reader)
        
        metric_provider = MeterProvider(
            resource=resource,
            metric_readers=metric_readers
        )
        metrics.set_meter_provider(metric_provider)
        
        self.meter = metrics.get_meter(self.config.service_name)
        logger.info("Metrics collection configured")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        if self.config.enable_tracing:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
    
    def instrument_motor(self):
        """Instrument Motor (MongoDB) client"""
        if self.config.enable_tracing:
            MotorInstrumentor().instrument()
            logger.info("Motor instrumentation enabled")
    
    def instrument_requests(self):
        """Instrument requests library"""
        if self.config.enable_tracing:
            RequestsInstrumentor().instrument()
            logger.info("Requests instrumentation enabled")
    
    def instrument_logging(self):
        """Instrument logging for trace correlation"""
        if self.config.enable_tracing:
            LoggingInstrumentor().instrument(set_logging_format=True)
            logger.info("Logging instrumentation enabled")


class MetricsCollector:
    """Prometheus metrics collector for Polaris Platform"""
    
    def __init__(self):
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Database metrics
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['collection', 'operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections'
        )
        
        # RBAC metrics
        self.rbac_decisions_total = Counter(
            'rbac_decisions_total',
            'Total RBAC policy decisions',
            ['decision', 'permission', 'resource_type']
        )
        
        self.rbac_decision_duration = Histogram(
            'rbac_decision_duration_seconds',
            'RBAC policy evaluation duration',
            ['permission', 'resource_type'],
            buckets=[0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1]
        )
        
        # Outbox metrics
        self.outbox_events_total = Counter(
            'outbox_events_total',
            'Total outbox events',
            ['event_type', 'status']
        )
        
        self.outbox_dispatch_latency = Histogram(
            'outbox_dispatch_latency_seconds',
            'Outbox event dispatch latency',
            ['event_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Business metrics
        self.assessments_completed = Counter(
            'assessments_completed_total',
            'Total assessments completed',
            ['risk_band', 'template_version']
        )
        
        self.action_plans_created = Counter(
            'action_plans_created_total',
            'Total action plans created',
            ['status', 'generated_by_type']
        )
        
        self.tasks_state_changes = Counter(
            'tasks_state_changes_total',
            'Total task state changes',
            ['from_state', 'to_state']
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_db_query(self, collection: str, operation: str, duration: float):
        """Record database query metrics"""
        self.db_query_duration.labels(
            collection=collection,
            operation=operation
        ).observe(duration)
    
    def record_rbac_decision(
        self, 
        decision: str, 
        permission: str, 
        resource_type: str, 
        duration: float
    ):
        """Record RBAC decision metrics"""
        self.rbac_decisions_total.labels(
            decision=decision,
            permission=permission,
            resource_type=resource_type
        ).inc()
        
        self.rbac_decision_duration.labels(
            permission=permission,
            resource_type=resource_type
        ).observe(duration)
    
    def record_outbox_event(self, event_type: str, status: str):
        """Record outbox event metrics"""
        self.outbox_events_total.labels(
            event_type=event_type,
            status=status
        ).inc()
    
    def record_outbox_dispatch_latency(self, event_type: str, latency: float):
        """Record outbox dispatch latency"""
        self.outbox_dispatch_latency.labels(event_type=event_type).observe(latency)
    
    def start_prometheus_server(self, port: int = 8090):
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")


# Global instances
config = ObservabilityConfig()
telemetry = TelemetryManager(config)
metrics_collector = MetricsCollector()


def trace_function(operation_name: Optional[str] = None):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not telemetry.tracer:
                return await func(*args, **kwargs)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            with telemetry.tracer.start_as_current_span(op_name) as span:
                try:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not telemetry.tracer:
                return func(*args, **kwargs)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            with telemetry.tracer.start_as_current_span(op_name) as span:
                try:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    result = func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def time_operation(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to time operation duration"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                # Record metric (implementation depends on metric system)
                return result
            except Exception:
                duration = time.time() - start_time
                # Record metric with error label
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                # Record metric
                return result
            except Exception:
                duration = time.time() - start_time
                # Record metric with error label
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Import asyncio at the end to avoid circular imports
import asyncio