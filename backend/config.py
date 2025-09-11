"""
Production Deployment Configuration for Polaris Platform
Environment-specific settings and production hardening
"""

import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    """Production environment configuration"""
    
    # Application Settings
    APP_NAME = "Polaris Platform"
    VERSION = "1.0.0"
    DEBUG = False
    TESTING = False
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 8  # 8 hours
    JWT_REFRESH_TOKEN_EXPIRES = 3600 * 24 * 30  # 30 days
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_BURST = 100
    
    # Database Configuration
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "polaris_production")
    MONGODB_TIMEOUT = 30
    MONGODB_MAX_POOL_SIZE = 100
    MONGODB_MIN_POOL_SIZE = 10
    
    # SSL/TLS Configuration
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH")
    FORCE_HTTPS = True
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "https://polaris.example.com",
        "https://www.polaris.example.com",
        "https://app.polaris.example.com"
    ]
    
    # Email Configuration
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@polaris.example.com")
    
    # File Upload Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = [".pdf", ".doc", ".docx", ".txt", ".png", ".jpg", ".jpeg"]
    UPLOAD_FOLDER = "/var/polaris/uploads"
    
    # External API Configuration
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # AI Integration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_ENABLED = bool(os.getenv("AI_ENABLED", "true").lower() == "true")
    
    # Monitoring and Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/polaris/application.log"
    ENABLE_METRICS = True
    PROMETHEUS_PORT = 9090
    
    # Performance Settings
    WORKERS = int(os.getenv("WORKERS", "4"))
    WORKER_CONNECTIONS = int(os.getenv("WORKER_CONNECTIONS", "1000"))
    KEEPALIVE = 2
    
    # Backup Configuration
    BACKUP_ENABLED = True
    BACKUP_SCHEDULE = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = 30
    S3_BACKUP_BUCKET = os.getenv("S3_BACKUP_BUCKET")
    
    # Cache Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL = 3600  # 1 hour
    
    # Feature Flags
    FEATURES = {
        "ai_assistance": True,
        "advanced_analytics": True,
        "bulk_operations": True,
        "integration_apis": True,
        "mobile_app": False,  # Not yet implemented
        "advanced_reporting": True
    }

class DevelopmentConfig:
    """Development environment configuration"""
    
    # Application Settings
    APP_NAME = "Polaris Platform (Development)"
    VERSION = "1.0.0-dev"
    DEBUG = True
    TESTING = False
    
    # Security Settings (less strict for development)
    SECRET_KEY = "dev-secret-key"
    JWT_SECRET_KEY = "dev-jwt-secret"
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24  # 24 hours
    
    # Rate Limiting (more lenient)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_REQUESTS_PER_MINUTE = 1000
    
    # Database Configuration
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "polaris_development"
    
    # CORS Configuration (allow all for development)
    ALLOWED_ORIGINS = ["*"]
    
    # Development-specific features
    FEATURES = {
        "ai_assistance": True,
        "advanced_analytics": True,
        "bulk_operations": True,
        "integration_apis": True,
        "mobile_app": True,  # Enable for testing
        "advanced_reporting": True,
        "debug_endpoints": True  # Special debug endpoints
    }

class TestingConfig:
    """Testing environment configuration"""
    
    APP_NAME = "Polaris Platform (Testing)"
    VERSION = "1.0.0-test"
    DEBUG = False
    TESTING = True
    
    # Use in-memory or test database
    DATABASE_NAME = "polaris_test"
    
    # Disable external services in testing
    AI_ENABLED = False
    SENDGRID_API_KEY = None
    STRIPE_SECRET_KEY = "sk_test_..."
    
    # Features for testing
    FEATURES = {
        "ai_assistance": False,  # Mock AI responses
        "advanced_analytics": True,
        "bulk_operations": True,
        "integration_apis": False,
        "mobile_app": False,
        "advanced_reporting": True
    }

# Configuration selector
def get_config():
    """Get configuration based on environment"""
    env = os.getenv("POLARIS_ENV", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Export current configuration
config = get_config()