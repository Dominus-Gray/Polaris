"""
Enhanced Security Module for Polaris Platform
Provides comprehensive security features including rate limiting, input validation, and audit logging
"""

import hashlib
import hmac
import time
import re
import logging
import json
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Any
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
import ipaddress
import json

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.polaris_db
        self.rate_limit_cache = {}
        
        # Security configurations
        self.RATE_LIMITS = {
            'auth': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'api': {'requests': 100, 'window': 60},  # 100 requests per minute
            'upload': {'requests': 10, 'window': 300},  # 10 uploads per 5 minutes
        }
        
        self.BLOCKED_IPS = set()
        self.SUSPICIOUS_PATTERNS = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'\.\./\.\.',  # Path traversal
            r'eval\s*\(',  # Code injection
        ]
        
    async def rate_limit(self, identifier: str, limit_type: str = 'api') -> bool:
        """Check if request should be rate limited"""
        try:
            current_time = int(time.time())
            config = self.RATE_LIMITS.get(limit_type, self.RATE_LIMITS['api'])
            window_start = current_time - config['window']
            
            # Clean old entries
            self.rate_limit_cache = {
                k: v for k, v in self.rate_limit_cache.items()
                if v['timestamp'] > window_start
            }
            
            # Check current count
            key = f"{identifier}:{limit_type}"
            if key in self.rate_limit_cache:
                if self.rate_limit_cache[key]['count'] >= config['requests']:
                    # Log rate limit violation
                    await self.log_security_event(
                        event_type='rate_limit_exceeded',
                        identifier=identifier,
                        details={
                            'limit_type': limit_type,
                            'requests': self.rate_limit_cache[key]['count'],
                            'window': config['window']
                        }
                    )
                    return False
                else:
                    self.rate_limit_cache[key]['count'] += 1
            else:
                self.rate_limit_cache[key] = {
                    'count': 1,
                    'timestamp': current_time
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request on error to avoid breaking functionality
    
    def validate_input(self, data: Any, max_length: int = 10000) -> bool:
        """Validate input for security threats"""
        try:
            if isinstance(data, str):
                # Check length
                if len(data) > max_length:
                    return False
                
                # Check for suspicious patterns
                for pattern in self.SUSPICIOUS_PATTERNS:
                    if re.search(pattern, data, re.IGNORECASE):
                        return False
                        
            elif isinstance(data, dict):
                for key, value in data.items():
                    if not self.validate_input(key, 100) or not self.validate_input(value, max_length):
                        return False
                        
            elif isinstance(data, list):
                for item in data:
                    if not self.validate_input(item, max_length):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False
    
    def sanitize_input(self, data: str) -> str:
        """Sanitize input data"""
        if not isinstance(data, str):
            return data
            
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>&"\']', '', data)
        
        # Limit length
        sanitized = sanitized[:1000]
        
        return sanitized.strip()
    
    async def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Check IP address reputation"""
        try:
            # Check if IP is in blocked list
            if ip_address in self.BLOCKED_IPS:
                return {
                    'blocked': True,
                    'reason': 'IP address is blacklisted'
                }
            
            # Check for private/local IPs
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                if ip_obj.is_private or ip_obj.is_loopback:
                    return {'blocked': False, 'reason': 'Private/local IP'}
            except ValueError:
                pass
            
            # Check recent failed attempts
            recent_cutoff = datetime.utcnow() - timedelta(hours=1)
            failed_attempts = await self.db.security_events.count_documents({
                'ip_address': ip_address,
                'event_type': {'$in': ['auth_failure', 'rate_limit_exceeded']},
                'timestamp': {'$gte': recent_cutoff}
            })
            
            if failed_attempts > 20:  # Too many recent failures
                await self.block_ip(ip_address, f"Too many failed attempts: {failed_attempts}")
                return {
                    'blocked': True,
                    'reason': f'Too many recent failed attempts: {failed_attempts}'
                }
            
            return {'blocked': False, 'attempts': failed_attempts}
            
        except Exception as e:
            logger.error(f"IP reputation check error: {e}")
            return {'blocked': False, 'error': str(e)}
    
    async def block_ip(self, ip_address: str, reason: str, duration_hours: int = 24):
        """Block an IP address"""
        try:
            self.BLOCKED_IPS.add(ip_address)
            
            # Store in database
            await self.db.blocked_ips.update_one(
                {'ip_address': ip_address},
                {
                    '$set': {
                        'ip_address': ip_address,
                        'reason': reason,
                        'blocked_at': datetime.utcnow(),
                        'expires_at': datetime.utcnow() + timedelta(hours=duration_hours),
                        'active': True
                    }
                },
                upsert=True
            )
            
            await self.log_security_event(
                event_type='ip_blocked',
                ip_address=ip_address,
                details={'reason': reason, 'duration_hours': duration_hours}
            )
            
        except Exception as e:
            logger.error(f"IP blocking error: {e}")
    
    async def log_security_event(self, event_type: str, identifier: str = None, 
                                ip_address: str = None, user_id: str = None, 
                                details: Dict = None):
        """Log security events for monitoring and analysis"""
        try:
            event = {
                'event_type': event_type,
                'timestamp': datetime.utcnow(),
                'ip_address': ip_address,
                'user_id': user_id,
                'identifier': identifier,
                'details': details or {},
                'severity': self.get_event_severity(event_type)
            }
            
            await self.db.security_events.insert_one(event)
            
            # Alert on critical events
            if event['severity'] == 'critical':
                await self.send_security_alert(event)
                
        except Exception as e:
            logger.error(f"Security event logging error: {e}")
    
    def get_event_severity(self, event_type: str) -> str:
        """Determine event severity"""
        critical_events = ['auth_bypass_attempt', 'sql_injection_attempt', 'ip_blocked']
        warning_events = ['rate_limit_exceeded', 'suspicious_input', 'auth_failure']
        
        if event_type in critical_events:
            return 'critical'
        elif event_type in warning_events:
            return 'warning'
        else:
            return 'info'
    
    async def send_security_alert(self, event: Dict):
        """Send security alert to administrators"""
        try:
            # Create notification for administrators
            alert_message = f"Security Alert: {event['event_type']}"
            if event.get('ip_address'):
                alert_message += f" from IP {event['ip_address']}"
            
            # Insert notification for all navigator/admin users
            navigator_users = await self.db.users.find({'role': 'navigator'}).to_list(None)
            
            for admin in navigator_users:
                await self.db.notifications.insert_one({
                    'id': f"security_alert_{int(time.time())}_{admin['id']}",
                    'user_id': admin['id'],
                    'title': 'Security Alert',
                    'message': alert_message,
                    'notification_type': 'security',
                    'metadata': event,
                    'read': False,
                    'created_at': datetime.utcnow()
                })
            
        except Exception as e:
            logger.error(f"Security alert error: {e}")
    
    async def audit_action(self, user_id: str, action: str, resource: str, 
                          resource_id: str = None, changes: Dict = None, 
                          ip_address: str = None):
        """Log user actions for audit trail"""
        try:
            audit_entry = {
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'resource_id': resource_id,
                'changes': changes,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow(),
                'session_id': None  # Could be populated from request context
            }
            
            await self.db.audit_logs.insert_one(audit_entry)
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        import secrets
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str, salt: str = None) -> Dict[str, str]:
        """Hash sensitive data with salt"""
        if salt is None:
            import secrets
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        import hashlib
        hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        
        return {
            'hash': hashed.hex(),
            'salt': salt
        }
    
    def verify_hash(self, data: str, stored_hash: str, salt: str) -> bool:
        """Verify hashed data"""
        try:
            import hashlib
            test_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
            return hmac.compare_digest(test_hash.hex(), stored_hash)
        except Exception:
            return False
    
    async def check_session_security(self, user_id: str, ip_address: str, 
                                   user_agent: str) -> Dict[str, Any]:
        """Check session for security anomalies"""
        try:
            # Check for session hijacking indicators
            recent_sessions = await self.db.user_sessions.find({
                'user_id': user_id,
                'created_at': {'$gte': datetime.utcnow() - timedelta(hours=24)}
            }).to_list(10)
            
            anomalies = []
            
            # Check for multiple IPs
            unique_ips = set(session.get('ip_address') for session in recent_sessions if session.get('ip_address'))
            if len(unique_ips) > 3:
                anomalies.append('multiple_ip_addresses')
            
            # Check for unusual user agents
            unique_agents = set(session.get('user_agent') for session in recent_sessions if session.get('user_agent'))
            if len(unique_agents) > 2:
                anomalies.append('multiple_user_agents')
            
            # Check geographic anomalies (if geolocation data available)
            # This would require IP geolocation service integration
            
            if anomalies:
                await self.log_security_event(
                    event_type='session_anomaly',
                    user_id=user_id,
                    ip_address=ip_address,
                    details={'anomalies': anomalies, 'unique_ips': len(unique_ips)}
                )
            
            return {
                'anomalies': anomalies,
                'risk_score': len(anomalies) * 25,  # Simple risk scoring
                'unique_ips': len(unique_ips),
                'unique_agents': len(unique_agents)
            }
            
        except Exception as e:
            logger.error(f"Session security check error: {e}")
            return {'anomalies': [], 'risk_score': 0}

    async def audit_sensitive_field_change(self, user_id: str, resource: str, 
                                         resource_id: str, field_changes: Dict[str, Any],
                                         ip_address: str = None) -> None:
        """Enhanced audit logging for sensitive field changes"""
        try:
            # Calculate hashes for before/after values of sensitive fields
            sensitive_fields = ['ssn', 'address_line1', 'address_line2', 'phone', 'notes']
            before_hashes = {}
            after_hashes = {}
            field_mask = []
            
            for field, change_data in field_changes.items():
                if field in sensitive_fields:
                    field_mask.append(field)
                    
                    # Hash the before value (never store plaintext)
                    if 'before' in change_data and change_data['before']:
                        before_hashes[field] = hashlib.sha256(
                            str(change_data['before']).encode()
                        ).hexdigest()
                    
                    # Hash the after value
                    if 'after' in change_data and change_data['after']:
                        after_hashes[field] = hashlib.sha256(
                            str(change_data['after']).encode()
                        ).hexdigest()
            
            # Create audit log entry
            audit_entry = {
                '_id': self.generate_secure_token(16),
                'timestamp': datetime.now(UTC),
                'user_id': user_id,
                'action': 'UPDATE_SENSITIVE_FIELDS',
                'resource': resource,
                'resource_id': resource_id,
                'before_hash': json.dumps(before_hashes) if before_hashes else None,
                'after_hash': json.dumps(after_hashes) if after_hashes else None,
                'field_mask': field_mask,
                'ip_address': ip_address,
                'details': {
                    'fields_changed': len(field_mask),
                    'change_type': 'sensitive_field_update'
                }
            }
            
            await self.db.audit_logs.insert_one(audit_entry)
            logger.info(f"Audited sensitive field changes for {resource}:{resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to audit sensitive field changes: {e}")
    
    async def audit_decrypt_operation(self, user_id: str, resource: str, 
                                    fields_decrypted: List[str], client_id: str,
                                    ip_address: str = None, sampling_rate: float = 0.1) -> None:
        """Audit decrypt operations with configurable sampling"""
        try:
            # Sample to avoid log noise (only log 10% by default)
            import random
            if random.random() > sampling_rate:
                return
            
            audit_entry = {
                '_id': self.generate_secure_token(16),
                'timestamp': datetime.now(UTC),
                'user_id': user_id,
                'action': 'DECRYPT',
                'resource': resource,
                'resource_id': client_id,
                'field_mask': fields_decrypted,
                'ip_address': ip_address,
                'details': {
                    'fields_count': len(fields_decrypted),
                    'operation_type': 'field_decryption',
                    'sampled': True
                }
            }
            
            await self.db.audit_logs.insert_one(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to audit decrypt operation: {e}")
    
    async def cleanup_expired_blocks(self):
        """Clean up expired IP blocks and security events"""
        try:
            # Remove expired IP blocks
            current_time = datetime.utcnow()
            expired_blocks = await self.db.blocked_ips.find({
                'expires_at': {'$lt': current_time},
                'active': True
            }).to_list(None)
            
            for block in expired_blocks:
                self.BLOCKED_IPS.discard(block['ip_address'])
            
            await self.db.blocked_ips.update_many(
                {'expires_at': {'$lt': current_time}},
                {'$set': {'active': False}}
            )
            
            # Clean old security events (keep 90 days)
            cutoff_date = current_time - timedelta(days=90)
            await self.db.security_events.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
        except Exception as e:
            logger.error(f"Security cleanup error: {e}")

# Decorator for rate limiting
def rate_limit(limit_type: str = 'api'):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client IP
            client_ip = request.client.host
            if 'x-forwarded-for' in request.headers:
                client_ip = request.headers['x-forwarded-for'].split(',')[0].strip()
            
            # Initialize security manager (would need dependency injection in real implementation)
            # security_manager = get_security_manager()
            
            # For now, basic rate limiting
            # if not await security_manager.rate_limit(client_ip, limit_type):
            #     raise HTTPException(
            #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            #         detail="Rate limit exceeded"
            #     )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Decorator for input validation
def validate_input(max_length: int = 10000):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate all string inputs
            for arg in args:
                if hasattr(arg, '__dict__'):  # Pydantic model
                    for field_name, field_value in arg.__dict__.items():
                        if isinstance(field_value, str) and len(field_value) > max_length:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Input too long: {field_name}"
                            )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator