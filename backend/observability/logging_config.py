"""
Structured Logging Configuration for Polaris Platform
Implements JSON logging with correlation ID propagation
"""
import os
import json
import logging
import logging.config
import uuid
from typing import Dict, Any, Optional
from contextvars import ContextVar
from datetime import datetime
import traceback

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIdFilter(logging.Filter):
    """Adds correlation ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        correlation_id = correlation_id_var.get()
        record.correlation_id = correlation_id or 'unknown'
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = os.getenv('HOSTNAME', 'localhost')
        self.service_name = os.getenv('SERVICE_NAME', 'polaris-platform')
        self.environment = os.getenv('ENVIRONMENT', 'development')
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            '@timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': self.service_name,
            'environment': self.environment,
            'hostname': self.hostname,
            'correlation_id': getattr(record, 'correlation_id', 'unknown'),
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
                'correlation_id', 'getMessage'
            }:
                log_data[key] = value
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class LoggingConfig:
    """Configuration for structured logging"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_format = os.getenv('LOG_FORMAT', 'json')  # json or console
        
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    '()': JSONFormatter,
                },
                'console': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'filters': {
                'correlation_id': {
                    '()': CorrelationIdFilter,
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': log_level,
                    'formatter': log_format,
                    'filters': ['correlation_id'],
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'polaris': {
                    'level': log_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'uvicorn': {
                    'level': log_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'uvicorn.access': {
                    'level': log_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'motor': {
                    'level': 'WARNING',  # Reduce MongoDB driver noise
                    'handlers': ['console'],
                    'propagate': False
                },
                'pymongo': {
                    'level': 'WARNING',
                    'handlers': ['console'],
                    'propagate': False
                }
            },
            'root': {
                'level': log_level,
                'handlers': ['console']
            }
        }
        
        # Add file logging in production
        if os.getenv('ENVIRONMENT') == 'production':
            log_file = os.getenv('LOG_FILE', '/var/log/polaris/application.log')
            config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'json',
                'filters': ['correlation_id'],
                'filename': log_file,
                'maxBytes': 100 * 1024 * 1024,  # 100MB
                'backupCount': 10,
                'encoding': 'utf-8'
            }
            
            # Add file handler to loggers
            for logger_name in ['polaris', 'uvicorn', 'uvicorn.access']:
                config['loggers'][logger_name]['handlers'].append('file')
            config['root']['handlers'].append('file')
        
        return config
    
    @staticmethod
    def setup_logging():
        """Setup structured logging"""
        config = LoggingConfig.get_config()
        logging.config.dictConfig(config)


class CorrelationIdManager:
    """Manages correlation ID propagation"""
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a new correlation ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def set_correlation_id(correlation_id: str):
        """Set correlation ID in context"""
        correlation_id_var.set(correlation_id)
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get current correlation ID"""
        return correlation_id_var.get()
    
    @staticmethod
    def clear_correlation_id():
        """Clear correlation ID from context"""
        correlation_id_var.set(None)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f"polaris.{name}")


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context
):
    """Log a message with additional context"""
    extra = dict(context)
    logger.log(level, message, extra=extra)


# Convenience functions for common logging patterns

def log_request_start(
    logger: logging.Logger,
    method: str,
    path: str,
    user_id: Optional[str] = None,
    **context
):
    """Log the start of an HTTP request"""
    log_with_context(
        logger,
        logging.INFO,
        f"Request started: {method} {path}",
        http_method=method,
        http_path=path,
        user_id=user_id,
        event_type="request_start",
        **context
    )


def log_request_end(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    **context
):
    """Log the end of an HTTP request"""
    log_with_context(
        logger,
        logging.INFO,
        f"Request completed: {method} {path} - {status_code} ({duration_ms:.2f}ms)",
        http_method=method,
        http_path=path,
        http_status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
        event_type="request_end",
        **context
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    collection: str,
    duration_ms: float,
    document_count: Optional[int] = None,
    **context
):
    """Log a database operation"""
    log_with_context(
        logger,
        logging.DEBUG,
        f"Database operation: {operation} on {collection} ({duration_ms:.2f}ms)",
        db_operation=operation,
        db_collection=collection,
        duration_ms=duration_ms,
        document_count=document_count,
        event_type="database_operation",
        **context
    )


def log_rbac_decision(
    logger: logging.Logger,
    user_id: str,
    permission: str,
    resource_type: str,
    resource_id: str,
    decision: bool,
    reason: str,
    duration_ms: float,
    **context
):
    """Log an RBAC policy decision"""
    log_with_context(
        logger,
        logging.INFO if not decision else logging.DEBUG,
        f"RBAC decision: {permission} on {resource_type}:{resource_id} - {'ALLOW' if decision else 'DENY'} ({reason})",
        user_id=user_id,
        rbac_permission=permission,
        rbac_resource_type=resource_type,
        rbac_resource_id=resource_id,
        rbac_decision=decision,
        rbac_reason=reason,
        duration_ms=duration_ms,
        event_type="rbac_decision",
        **context
    )


def log_domain_event(
    logger: logging.Logger,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    event_id: str,
    **context
):
    """Log a domain event"""
    log_with_context(
        logger,
        logging.INFO,
        f"Domain event: {event_type} for {aggregate_type}:{aggregate_id}",
        domain_event_type=event_type,
        domain_aggregate_type=aggregate_type,
        domain_aggregate_id=aggregate_id,
        domain_event_id=event_id,
        event_type="domain_event",
        **context
    )


def log_business_metric(
    logger: logging.Logger,
    metric_name: str,
    metric_value: float,
    metric_unit: str,
    **context
):
    """Log a business metric"""
    log_with_context(
        logger,
        logging.INFO,
        f"Business metric: {metric_name} = {metric_value} {metric_unit}",
        business_metric_name=metric_name,
        business_metric_value=metric_value,
        business_metric_unit=metric_unit,
        event_type="business_metric",
        **context
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    operation: str,
    **context
):
    """Log an error with context"""
    log_with_context(
        logger,
        logging.ERROR,
        f"Error in {operation}: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        operation=operation,
        event_type="error",
        **context
    )


# Initialize logging on module import
LoggingConfig.setup_logging()