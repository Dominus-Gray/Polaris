"""
Unit tests for Security, Encryption & Consent Baseline
"""

import pytest
import asyncio
import os
import base64
from unittest.mock import AsyncMock, MagicMock

# Mock motor for testing
class MockDatabase:
    def __init__(self):
        self.encryption_keys = MockCollection()
        self.encryption_field_metadata = MockCollection()
        self.consent_records = MockCollection()
        self.audit_logs = MockCollection()
        self.client_profiles = MockCollection()
        self.assessments = MockCollection()

class MockCollection:
    def __init__(self):
        self.data = {}
        
    async def find_one(self, query):
        # Simple mock implementation
        if query.get("_id"):
            return self.data.get(query["_id"])
        return None
    
    async def insert_one(self, document):
        self.data[document["_id"]] = document
        return MagicMock(inserted_id=document["_id"])
    
    async def update_one(self, query, update):
        # Simple mock implementation
        return MagicMock(modified_count=1)
    
    def find(self, query=None):
        return MockCursor(self.data.values())

class MockCursor:
    def __init__(self, data):
        self.data = list(data)
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.data:
            return self.data.pop(0)
        raise StopAsyncIteration

# Set up test environment
os.environ["MASTER_KEY_MATERIAL"] = base64.b64encode(b"test_master_key_32_bytes_long!!").decode()

@pytest.fixture
def mock_db():
    return MockDatabase()

@pytest.fixture
def encryption_provider(mock_db):
    from backend.encryption import EncryptionProvider
    return EncryptionProvider(mock_db)

@pytest.fixture
def field_manager(encryption_provider, mock_db):
    from backend.encryption import FieldEncryptionManager
    return FieldEncryptionManager(encryption_provider, mock_db)

@pytest.fixture  
def consent_manager(mock_db):
    from backend.consent import ConsentManager
    return ConsentManager(mock_db)

class TestEncryptionProvider:
    """Test the encryption provider functionality"""
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_roundtrip(self, encryption_provider):
        """Test basic encryption and decryption roundtrip"""
        test_data = "sensitive information 🔒"
        key_alias = "test_key"
        
        # Encrypt
        encrypted = await encryption_provider.encrypt(test_data.encode(), key_alias)
        assert encrypted != test_data.encode()
        assert len(encrypted) > len(test_data)
        
        # Decrypt
        decrypted = await encryption_provider.decrypt(encrypted)
        assert decrypted.decode() == test_data
    
    @pytest.mark.asyncio
    async def test_encrypt_empty_value(self, encryption_provider):
        """Test encryption of empty values"""
        encrypted = await encryption_provider.encrypt(b"", "test_key")
        assert encrypted == b""
        
        decrypted = await encryption_provider.decrypt(encrypted)
        assert decrypted == b""
    
    def test_deterministic_hash(self, encryption_provider):
        """Test deterministic hashing for lookups"""
        value = "123-45-6789"
        key_alias = "ssn_key"
        
        # Hash should be consistent
        hash1 = encryption_provider.deterministic_hash(value, key_alias)
        hash2 = encryption_provider.deterministic_hash(value, key_alias)
        assert hash1 == hash2
        
        # Different values should produce different hashes
        hash3 = encryption_provider.deterministic_hash("987-65-4321", key_alias)
        assert hash1 != hash3
        
        # Normalized values should produce same hash
        hash4 = encryption_provider.deterministic_hash("123456789", key_alias)  # No dashes
        assert hash1 == hash4  # Should be same after normalization
    
    @pytest.mark.asyncio
    async def test_key_wrapping(self, encryption_provider):
        """Test key wrapping and unwrapping"""
        data_key = b"test_data_key_32_bytes_long!!"
        
        wrapped = encryption_provider._wrap_key(data_key)
        unwrapped = encryption_provider._unwrap_key(wrapped)
        
        assert unwrapped == data_key
        assert wrapped != data_key


class TestFieldEncryptionManager:
    """Test field-level encryption management"""
    
    @pytest.mark.asyncio
    async def test_register_encrypted_field(self, field_manager):
        """Test registering a field for encryption"""
        metadata_id = await field_manager.register_encrypted_field(
            "test_resource", "test_field", "test_key", deterministic=True
        )
        
        assert metadata_id is not None
        assert len(metadata_id) == 32  # hex(16)
    
    @pytest.mark.asyncio
    async def test_encrypt_fields(self, field_manager, mock_db):
        """Test encrypting fields in a model instance"""
        # Set up field metadata
        metadata = {
            "_id": "meta1",
            "resource": "test_resource",
            "field_name": "secret_field",
            "key_id": "key1",
            "deterministic": False
        }
        mock_db.encryption_field_metadata.data["meta1"] = metadata
        
        # Set up encryption key
        key_doc = {
            "_id": "key1",
            "key_alias": "test_key",
            "material_wrapped": b"wrapped_key",
            "algorithm": "AES256_GCM",
            "active": True
        }
        mock_db.encryption_keys.data["key1"] = key_doc
        
        # Test data
        model_instance = {
            "id": "123",
            "secret_field": "sensitive data",
            "public_field": "public data"
        }
        
        # Encrypt fields
        encrypted = await field_manager.encrypt_fields(model_instance, "test_resource")
        
        # Verify results
        assert "secret_field" not in encrypted
        assert "secret_field_encrypted" in encrypted
        assert "public_field" in encrypted  # Public field unchanged
        assert encrypted["public_field"] == "public data"
    
    def test_mask_value(self, field_manager):
        """Test value masking for unauthorized access"""
        # Test SSN masking
        assert field_manager._mask_value("123-45-6789") == "***-**-6789"
        assert field_manager._mask_value("123456789") == "*****6789"
        
        # Test general masking
        assert field_manager._mask_value("long_sensitive_value") == "***************alue"
        assert field_manager._mask_value("short") == "*****"
        assert field_manager._mask_value("ab") == "**"


class TestConsentManager:
    """Test consent management functionality"""
    
    @pytest.mark.asyncio
    async def test_grant_consent(self, consent_manager):
        """Test granting consent"""
        consent_id = await consent_manager.grant_consent(
            client_id="client123",
            scope="VIEW_SENSITIVE_IDENTIFIERS",
            granted_by_user_id="user456",
            notes="Test consent"
        )
        
        assert consent_id is not None
        assert len(consent_id) == 32
    
    @pytest.mark.asyncio
    async def test_check_consent(self, consent_manager, mock_db):
        """Test checking consent status"""
        # Set up existing consent
        consent_record = {
            "_id": "consent123",
            "client_id": "client123",
            "scope": "VIEW_SENSITIVE_IDENTIFIERS",
            "revoked_at": None
        }
        mock_db.consent_records.data["consent123"] = consent_record
        
        # Test consent check
        has_consent = await consent_manager.check_consent("client123", "VIEW_SENSITIVE_IDENTIFIERS")
        assert has_consent is True
        
        # Test non-existent consent
        has_consent = await consent_manager.check_consent("client123", "NONEXISTENT_SCOPE")
        assert has_consent is False
    
    @pytest.mark.asyncio
    async def test_revoke_consent(self, consent_manager, mock_db):
        """Test revoking consent"""
        # Set up existing consent
        consent_record = {
            "_id": "consent123",
            "client_id": "client123", 
            "scope": "VIEW_SENSITIVE_IDENTIFIERS",
            "revoked_at": None
        }
        mock_db.consent_records.data["consent123"] = consent_record
        
        # Revoke consent
        success = await consent_manager.revoke_consent(
            client_id="client123",
            scope="VIEW_SENSITIVE_IDENTIFIERS",
            revoked_by_user_id="user456"
        )
        
        assert success is True


class TestIntegration:
    """Integration tests for the complete security system"""
    
    @pytest.mark.asyncio
    async def test_consent_permission_matrix(self, field_manager, consent_manager, mock_db):
        """Test permission + consent matrix scenarios"""
        from backend.consent import ConsentScopeResolver
        
        resolver = ConsentScopeResolver(consent_manager)
        
        # Set up consent record
        consent_record = {
            "_id": "consent123",
            "client_id": "client123",
            "scope": "VIEW_SENSITIVE_IDENTIFIERS",
            "revoked_at": None
        }
        mock_db.consent_records.data["consent123"] = consent_record
        
        # Test with permission and consent
        permitted, missing = await resolver.get_permitted_fields(
            client_id="client123",
            user_permissions=["view_sensitive_data"],
            requested_fields=["ssn", "phone"]
        )
        
        assert "ssn" in permitted
        assert "phone" in permitted
        assert len(missing) == 0
        
        # Test with permission but no consent
        permitted, missing = await resolver.get_permitted_fields(
            client_id="client456",  # Different client, no consent
            user_permissions=["view_sensitive_data"],
            requested_fields=["ssn", "phone"]
        )
        
        assert len(permitted) == 0
        assert "VIEW_SENSITIVE_IDENTIFIERS" in missing


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])