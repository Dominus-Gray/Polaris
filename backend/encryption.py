"""
Field-level Encryption and Key Management for Polaris Platform
Implements envelope encryption pattern with deterministic hashing for lookups
"""

import os
import base64
import secrets
import hashlib
import hmac
import struct
from typing import Dict, Optional, Any, List, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, UTC
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class EncryptionProvider:
    """
    Encryption service implementing envelope encryption pattern.
    For MVP: simulates KMS using environment variable master key.
    Future: will support external KMS integration.
    """
    
    ALGORITHM_AES256_GCM = "AES256_GCM"
    VERSION = 1
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.master_key = self._get_master_key()
        
    def _get_master_key(self) -> bytes:
        """Get master key from environment (MVP) or KMS (future)"""
        master_key_material = os.environ.get("MASTER_KEY_MATERIAL")
        if not master_key_material:
            # Generate for development - WARNING: not production-grade
            logger.warning("MASTER_KEY_MATERIAL not set, generating temporary key")
            master_key_material = base64.b64encode(secrets.token_bytes(32)).decode()
            logger.warning(f"Generated master key: {master_key_material}")
            
        return base64.b64decode(master_key_material)
    
    async def _get_data_key(self, key_alias: str) -> Tuple[bytes, str]:
        """Get or create data encryption key"""
        # Try to find existing active key
        key_doc = await self.db.encryption_keys.find_one({
            "key_alias": key_alias,
            "active": True
        })
        
        if key_doc:
            # Unwrap the key material (simplified XOR for MVP)
            wrapped_key = key_doc["material_wrapped"]
            unwrapped_key = self._unwrap_key(wrapped_key)
            return unwrapped_key, str(key_doc["_id"])
        
        # Create new key
        data_key = secrets.token_bytes(32)  # 256-bit key
        wrapped_key = self._wrap_key(data_key)
        
        key_doc = {
            "_id": secrets.token_hex(16),
            "key_alias": key_alias,
            "material_wrapped": wrapped_key,
            "algorithm": self.ALGORITHM_AES256_GCM,
            "active": True,
            "created_at": datetime.now(UTC),
            "rotated_at": None
        }
        
        await self.db.encryption_keys.insert_one(key_doc)
        return data_key, key_doc["_id"]
    
    def _wrap_key(self, data_key: bytes) -> bytes:
        """Wrap data key with master key (simplified for MVP)"""
        # XOR wrapping - NOT production grade, just for MVP
        master_key_hash = hashlib.sha256(self.master_key).digest()
        wrapped = bytes(a ^ b for a, b in zip(data_key, master_key_hash))
        return wrapped
    
    def _unwrap_key(self, wrapped_key: bytes) -> bytes:
        """Unwrap data key using master key"""
        master_key_hash = hashlib.sha256(self.master_key).digest()
        unwrapped = bytes(a ^ b for a, b in zip(wrapped_key, master_key_hash))
        return unwrapped
    
    async def encrypt(self, value: bytes, key_alias: str) -> bytes:
        """
        Encrypt value using envelope encryption
        Returns: version(1) + key_id(16) + iv(12) + ciphertext + tag(16)
        """
        if not value:
            return b""
            
        try:
            data_key, key_id = await self._get_data_key(key_alias)
            
            # Generate random IV for GCM
            iv = secrets.token_bytes(12)
            
            # Encrypt using AES-256-GCM
            cipher = Cipher(algorithms.AES(data_key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(value) + encryptor.finalize()
            tag = encryptor.tag
            
            # Pack: version(1) + key_id(16) + iv(12) + ciphertext + tag(16)
            result = struct.pack("B", self.VERSION)
            result += key_id.encode()[:16].ljust(16, b'\0')
            result += iv
            result += ciphertext
            result += tag
            
            return result
            
        except Exception as e:
            logger.error(f"Encryption failed for key_alias {key_alias}: {e}")
            raise
    
    async def decrypt(self, blob: bytes) -> bytes:
        """
        Decrypt blob created by encrypt()
        """
        if not blob:
            return b""
            
        try:
            if len(blob) < 45:  # min: version(1) + key_id(16) + iv(12) + tag(16)
                raise ValueError("Invalid encrypted blob format")
            
            # Unpack the blob
            version = struct.unpack("B", blob[:1])[0]
            if version != self.VERSION:
                raise ValueError(f"Unsupported encryption version: {version}")
            
            key_id = blob[1:17].rstrip(b'\0').decode()
            iv = blob[17:29]
            ciphertext = blob[29:-16]
            tag = blob[-16:]
            
            # Get the data key
            key_doc = await self.db.encryption_keys.find_one({"_id": key_id})
            if not key_doc:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            data_key = self._unwrap_key(key_doc["material_wrapped"])
            
            # Decrypt using AES-256-GCM
            cipher = Cipher(algorithms.AES(data_key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def deterministic_hash(self, value: str, key_alias: str) -> str:
        """
        Generate deterministic HMAC-SHA256 hash for lookups
        """
        try:
            # Use master key for deterministic hashing
            # Normalize the value (remove spaces, convert to lowercase for things like SSN)
            normalized = value.strip().replace("-", "").replace(" ", "").lower()
            
            # Create HMAC with key_alias as salt
            key = hashlib.sha256(self.master_key + key_alias.encode()).digest()
            hmac_obj = hmac.new(key, normalized.encode(), hashlib.sha256)
            return hmac_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Deterministic hashing failed for key_alias {key_alias}: {e}")
            raise


class FieldEncryptionManager:
    """
    High-level field encryption management
    """
    
    def __init__(self, encryption_provider: EncryptionProvider, db: AsyncIOMotorDatabase):
        self.encryption_provider = encryption_provider
        self.db = db
    
    async def get_field_metadata(self, resource: str, field_name: str) -> Optional[Dict]:
        """Get encryption metadata for a field"""
        return await self.db.encryption_field_metadata.find_one({
            "resource": resource,
            "field_name": field_name
        })
    
    async def register_encrypted_field(self, resource: str, field_name: str, 
                                     key_alias: str, deterministic: bool = False) -> str:
        """Register a field for encryption"""
        metadata_id = secrets.token_hex(16)
        
        # Get or create encryption key
        await self.encryption_provider._get_data_key(key_alias)
        
        # Find the key document to get its ID
        key_doc = await self.db.encryption_keys.find_one({
            "key_alias": key_alias,
            "active": True
        })
        
        metadata = {
            "_id": metadata_id,
            "resource": resource,
            "field_name": field_name,
            "key_id": key_doc["_id"],
            "deterministic": deterministic,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        
        await self.db.encryption_field_metadata.insert_one(metadata)
        return metadata_id
    
    async def encrypt_fields(self, model_instance: Dict, resource: str) -> Dict:
        """
        Encrypt specified fields in a model instance
        """
        result = model_instance.copy()
        
        # Get all encryption metadata for this resource
        metadata_cursor = self.db.encryption_field_metadata.find({"resource": resource})
        
        async for metadata in metadata_cursor:
            field_name = metadata["field_name"]
            if field_name not in model_instance:
                continue
                
            value = model_instance[field_name]
            if value is None:
                continue
                
            # Get the key alias
            key_doc = await self.db.encryption_keys.find_one({"_id": metadata["key_id"]})
            if not key_doc:
                logger.warning(f"Key not found for field {field_name}")
                continue
                
            key_alias = key_doc["key_alias"]
            
            # Encrypt the field
            encrypted_field = f"{field_name}_encrypted"
            result[encrypted_field] = await self.encryption_provider.encrypt(
                str(value).encode(), key_alias
            )
            
            # If deterministic, also create hash field
            if metadata["deterministic"]:
                hash_field = f"{field_name}_hmac"
                result[hash_field] = self.encryption_provider.deterministic_hash(
                    str(value), key_alias
                )
            
            # Remove original field
            del result[field_name]
            
        return result
    
    async def decrypt_fields(self, model_instance: Dict, resource: str, 
                           permitted_fields: Optional[List[str]] = None) -> Dict:
        """
        Decrypt fields in a model instance based on permissions
        """
        result = model_instance.copy()
        
        # Get all encryption metadata for this resource  
        metadata_cursor = self.db.encryption_field_metadata.find({"resource": resource})
        
        async for metadata in metadata_cursor:
            field_name = metadata["field_name"]
            encrypted_field = f"{field_name}_encrypted"
            
            # Check if encrypted field exists and if we have permission
            if encrypted_field not in model_instance:
                continue
                
            if permitted_fields is not None and field_name not in permitted_fields:
                # Mask the field instead of decrypting
                result[field_name] = self._mask_value(str(model_instance.get(field_name, "")))
                continue
            
            encrypted_value = model_instance[encrypted_field]
            if encrypted_value is None:
                continue
                
            try:
                # Decrypt the field
                decrypted_bytes = await self.encryption_provider.decrypt(encrypted_value)
                result[field_name] = decrypted_bytes.decode()
                
                # Remove encrypted field from result
                del result[encrypted_field]
                
            except Exception as e:
                logger.error(f"Failed to decrypt field {field_name}: {e}")
                result[field_name] = "[DECRYPTION_ERROR]"
        
        return result
    
    def _mask_value(self, value: str) -> str:
        """Mask sensitive values for unauthorized access"""
        if not value:
            return value
            
        # SSN masking
        if len(value) == 11 and '-' in value:  # XXX-XX-XXXX format
            return f"***-**-{value[-4:]}"
        elif len(value) == 9 and value.isdigit():  # XXXXXXXXX format
            return f"*****{value[-4:]}"
            
        # General masking - show last 4 characters
        if len(value) > 4:
            return "*" * (len(value) - 4) + value[-4:]
        else:
            return "*" * len(value)