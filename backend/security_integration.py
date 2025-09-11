"""
Integration module to initialize security features in the main server
"""

import os
import logging
from .encryption import EncryptionProvider, FieldEncryptionManager
from .consent import ConsentManager, ConsentScopeResolver
from .security_middleware import ConsentEnforcementMiddleware, SecurityMiddleware
from .security_endpoints import create_security_router, create_client_router_extensions
from .security import SecurityManager

logger = logging.getLogger(__name__)

async def init_security_features(app, db, get_current_user, require_role):
    """
    Initialize all security features and add them to the FastAPI app
    """
    try:
        logger.info("Initializing security features...")
        
        # Check if security features are enabled
        enable_encryption = os.environ.get("ENABLE_FIELD_ENCRYPTION", "true").lower() == "true"
        enable_consent = os.environ.get("ENABLE_CONSENT_ENFORCEMENT", "true").lower() == "true"
        
        if not enable_encryption:
            logger.warning("Field encryption is disabled")
            return
        
        # Initialize core components
        encryption_provider = EncryptionProvider(db)
        field_manager = FieldEncryptionManager(encryption_provider, db)
        consent_manager = ConsentManager(db)
        consent_resolver = ConsentScopeResolver(consent_manager)
        
        # Initialize middleware
        consent_middleware = ConsentEnforcementMiddleware(
            consent_manager, consent_resolver, field_manager
        )
        
        security_manager = SecurityManager(db.client)  # Pass the MongoDB client
        
        security_middleware = SecurityMiddleware(db, security_manager)
        
        # Create API routers
        security_router = create_security_router(
            db, consent_manager, field_manager, security_manager,
            get_current_user, require_role
        )
        
        client_extensions = create_client_router_extensions(
            db, field_manager, consent_middleware, security_manager,
            get_current_user, require_role
        )
        
        # Include routers in the app
        app.include_router(security_router)
        app.include_router(client_extensions)
        
        # Initialize field metadata for standard encrypted fields
        await init_field_metadata(field_manager)
        
        logger.info("✅ Security features initialized successfully")
        
        return {
            "encryption_provider": encryption_provider,
            "field_manager": field_manager,
            "consent_manager": consent_manager,
            "consent_middleware": consent_middleware,
            "security_manager": security_manager
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize security features: {e}")
        # Don't raise - allow server to start without security features for development
        return None

async def init_field_metadata(field_manager):
    """Initialize standard field encryption metadata"""
    try:
        logger.info("Initializing field encryption metadata...")
        
        # Client profiles encrypted fields
        client_fields = [
            ("ssn", "client_data_key", True),  # deterministic for lookups
            ("address_line1", "client_data_key", False),
            ("address_line2", "client_data_key", False),
            ("phone", "client_data_key", False)
        ]
        
        for field_name, key_alias, deterministic in client_fields:
            try:
                existing = await field_manager.get_field_metadata("client_profiles", field_name)
                if not existing:
                    await field_manager.register_encrypted_field(
                        "client_profiles", field_name, key_alias, deterministic
                    )
                    logger.info(f"Registered encryption for client_profiles.{field_name}")
            except Exception as e:
                logger.warning(f"Failed to register {field_name}: {e}")
        
        # Assessment encrypted fields
        assessment_fields = [
            ("notes", "assessment_data_key", False)
        ]
        
        for field_name, key_alias, deterministic in assessment_fields:
            try:
                existing = await field_manager.get_field_metadata("assessments", field_name)
                if not existing:
                    await field_manager.register_encrypted_field(
                        "assessments", field_name, key_alias, deterministic
                    )
                    logger.info(f"Registered encryption for assessments.{field_name}")
            except Exception as e:
                logger.warning(f"Failed to register {field_name}: {e}")
        
        logger.info("✅ Field encryption metadata initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize field metadata: {e}")


def get_security_metrics():
    """Get security-related metrics for observability"""
    # This would be called by a metrics endpoint or monitoring system
    return {
        "encryption_operations_total": {
            "encrypt": 0,  # Would be tracked by EncryptionProvider
            "decrypt": 0
        },
        "consent_checks_total": {
            "granted": 0,  # Would be tracked by ConsentManager
            "denied": 0
        },
        "key_rotation_cycles_total": {
            "successful": 0,
            "failed": 0
        }
    }