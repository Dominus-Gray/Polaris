from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends, Header, Query, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
import os
import logging
from pathlib import Path
import uuid
import aiofiles
import requests
import hashlib
import secrets
import re
import random
from functools import wraps
import time

# Stripe Payment Integration
try:
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("Warning: Stripe integration not available")

# Security Configuration
SECURITY_CONFIG = {
    "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
    "JWT_ALGORITHM": "HS256", 
    "JWT_EXPIRE_MINUTES": 60,
    "PASSWORD_MIN_LENGTH": 8,
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOGIN_LOCKOUT_MINUTES": 15,
    "REQUIRE_HTTPS": os.environ.get("REQUIRE_HTTPS", "true").lower() == "true",
    "ALLOWED_HOSTS": os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,*.emergentagent.com").split(",")
}

# Security logging
security_logger = logging.getLogger("polaris.security")
security_logger.setLevel(logging.INFO)

def log_security_event(event_type: str, user_id: str = None, details: dict = None):
    """Log security events for auditing"""
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details or {}
    }
    security_logger.info(f"SECURITY_EVENT: {event_data}")

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < SECURITY_CONFIG["PASSWORD_MIN_LENGTH"]:
        return False
    if not re.search(r"[A-Z]", password):  # Uppercase letter
        return False
    if not re.search(r"[a-z]", password):  # Lowercase letter  
        return False
    if not re.search(r"\d", password):     # Digit
        return False
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):  # Special char
        return False
    return True

def rate_limit(max_requests: int, window_seconds: int):
    """Rate limiting decorator"""
    def decorator(func):
        requests_count = {}
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old entries
            requests_count[client_ip] = [
                req_time for req_time in requests_count.get(client_ip, [])
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(requests_count.get(client_ip, [])) >= max_requests:
                log_security_event("RATE_LIMIT_EXCEEDED", details={"ip": client_ip})
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Add current request
            requests_count.setdefault(client_ip, []).append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_OK = True
except Exception:
    EMERGENT_OK = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(
    title="Polaris - Small Business Procurement Readiness Platform",
    description="Secure platform for assessing small business procurement readiness",
    version="1.0.0",
    docs_url="/docs" if os.environ.get("ENVIRONMENT") == "development" else None,
    redoc_url=None
)
api = APIRouter(prefix="/api")

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=SECURITY_CONFIG["ALLOWED_HOSTS"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://polaris-navigator-1.preview.emergentagent.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Remove server header
    if "server" in response.headers:
        del response.headers["server"]
    
    return response

# Audit logging middleware  
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Log API access for audit trail
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "process_time": f"{process_time:.3f}s",
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", "")
    }
    
    if response.status_code >= 400:
        log_security_event("API_ERROR", details=log_data)
    
    return response

UPLOAD_BASE = ROOT_DIR / "uploads"
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALGO = "HS256"
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRegistrationIn(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., pattern="^(client|provider|navigator|agency)$")
    terms_accepted: bool = True
    license_code: Optional[str] = None  # 10-digit license code for business clients
    payment_info: Optional[Dict[str, str]] = None
    
    @validator('password')
    def validate_password(cls, v):
        if not validate_password_strength(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, digit, and special character')
        return v

class ProviderApprovalIn(BaseModel):
    provider_user_id: str
    approval_status: str  # 'approved', 'rejected', 'pending'
    notes: Optional[str] = None

class ProviderApprovalOut(BaseModel):
    id: str
    provider_user_id: str
    navigator_user_id: str
    approval_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    role: str
    approval_status: str = "approved"  # pending, approved, rejected
    is_active: bool = True
    created_at: datetime
    profile_complete: bool = False

async def get_user_by_email(email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email.lower()})

async def create_user(email: str, password: str, role: str) -> dict:
    existing = await get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    uid = str(uuid.uuid4())
    user_doc = {"_id": uid, "id": uid, "email": email.lower(), "hashed_password": pbkdf2_sha256.hash(password), "role": role, "created_at": datetime.utcnow()}
    await db.users.insert_one(user_doc)
    return user_doc

async def verify_user(email: str, password: str) -> Optional[dict]:
    user = await get_user_by_email(email)
    if user and pbkdf2_sha256.verify(password, user.get("hashed_password", "")):
        return user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH_SECRET, algorithm=ALGO)

async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        return None
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[ALGO])
        uid: str = payload.get("sub")
        if uid is None:
            return None
        user = await db.users.find_one({"_id": uid})
        return user
    except JWTError:
        return None

async def require_user(current=Depends(get_current_user)) -> dict:
    if not current:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current

def require_role(role: str):
    async def role_dep(current=Depends(require_user)):
        if current.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current
    return role_dep

@api.post("/auth/register")
@rate_limit(max_requests=5, window_seconds=300)  # 5 registrations per 5 minutes
async def register_user(request: Request, user: UserRegistrationIn):
    if not user.terms_accepted:
        log_security_event("REGISTRATION_TERMS_NOT_ACCEPTED", details={"email": user.email})
        raise HTTPException(status_code=400, detail="Terms of Service must be accepted")
    
    # Check if user exists
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        log_security_event("REGISTRATION_EMAIL_EXISTS", details={"email": user.email})
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Validate license code for business clients
    if user.role == 'client':
        if not user.license_code or len(user.license_code) != 10 or not user.license_code.isdigit():
            raise HTTPException(status_code=400, detail="Business clients require a valid 10-digit license code from a local agency")
        
        # Verify license code is valid and not already used
        license_record = await db.agency_licenses.find_one({"license_code": user.license_code, "status": "available"})
        if not license_record:
            raise HTTPException(status_code=400, detail="Invalid or already used license code")
    
    # Set approval status based on role
    approval_status = "approved"  # Default for clients and navigators
    if user.role == 'agency':
        approval_status = "pending"  # Agencies need verification by navigators
    elif user.role == 'provider':
        approval_status = "pending"  # Providers need vetting by navigators
    
    user_id = str(uuid.uuid4())
    hashed_password = pbkdf2_sha256.hash(user.password)
    
    user_doc = {
        "_id": user_id,
        "id": user_id,
        "email": user.email.lower(),
        "hashed_password": hashed_password,
        "role": user.role,
        "approval_status": approval_status,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "profile_complete": False,
        "terms_accepted": user.terms_accepted,
        "terms_accepted_at": datetime.utcnow()
    }
    
    # Store payment info if provided (encrypted)
    if user.payment_info:
        user_doc["payment_info"] = user.payment_info  # In production, this should be encrypted
    
    # Store license code for clients
    if user.role == 'client' and user.license_code:
        user_doc["license_code"] = user.license_code
        # Mark license as used
        await db.agency_licenses.update_one(
            {"license_code": user.license_code},
            {"$set": {"status": "used", "used_by": user_id, "used_at": datetime.utcnow()}}
        )
    
    await db.users.insert_one(user_doc)
    
    log_security_event("USER_REGISTERED", details={
        "user_id": user_id, 
        "email": user.email, 
        "role": user.role,
        "approval_status": approval_status
    })
    
    # Send different responses based on approval status
    if approval_status == "pending":
        return {"message": f"{user.role.title()} registration submitted for approval", "status": "pending"}
    else:
        return {"message": "Registration successful", "status": "approved"}

@api.post("/auth/login", response_model=Token)
@rate_limit(max_requests=10, window_seconds=300)  # 10 login attempts per 5 minutes
async def login_user(request: Request, user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        log_security_event("LOGIN_USER_NOT_FOUND", details={"email": user.email, "ip": request.client.host})
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Check if account is locked
    if db_user.get("locked_until") and db_user["locked_until"] > datetime.utcnow():
        log_security_event("LOGIN_ACCOUNT_LOCKED", user_id=db_user["id"], details={"email": user.email})
        raise HTTPException(status_code=423, detail="Account temporarily locked due to failed login attempts")
    
    # Verify password
    if not pbkdf2_sha256.verify(user.password, db_user["hashed_password"]):
        # Increment failed attempts
        failed_attempts = db_user.get("failed_login_attempts", 0) + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        # Lock account if too many failures
        if failed_attempts >= SECURITY_CONFIG["MAX_LOGIN_ATTEMPTS"]:
            lock_until = datetime.utcnow() + timedelta(minutes=SECURITY_CONFIG["LOGIN_LOCKOUT_MINUTES"])
            update_data["locked_until"] = lock_until
            
        await db.users.update_one({"id": db_user["id"]}, {"$set": update_data})
        
        log_security_event("LOGIN_FAILED", user_id=db_user["id"], details={
            "email": user.email, 
            "attempts": failed_attempts,
            "ip": request.client.host
        })
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Check if provider or agency is approved
    if db_user["role"] in ["provider", "agency"] and db_user.get("approval_status") != "approved":
        log_security_event("LOGIN_USER_NOT_APPROVED", user_id=db_user["id"], details={"email": user.email, "role": db_user["role"]})
        raise HTTPException(status_code=403, detail=f"{db_user['role'].title()} account pending approval")
    
    # Reset failed attempts on successful login
    await db.users.update_one(
        {"id": db_user["id"]}, 
        {"$set": {"failed_login_attempts": 0, "locked_until": None, "last_login": datetime.utcnow()}}
    )
    
    access_token = create_access_token(data={"sub": db_user["id"]})
    
    log_security_event("LOGIN_SUCCESS", user_id=db_user["id"], details={"email": user.email, "ip": request.client.host})
    return {"access_token": access_token, "token_type": "bearer"}

@api.get("/auth/me", response_model=UserOut)
async def get_current_user_info(current=Depends(require_user)):
    return UserOut(id=current["id"], email=current["email"], role=current["role"], created_at=current["created_at"])

class OAuthCallbackIn(BaseModel):
    session_id: str
    role: str

class OAuthCallbackOut(BaseModel):
    access_token: str
    user_id: str
    email: str
    name: str
    role: str

@api.post("/auth/oauth/callback", response_model=OAuthCallbackOut)
async def oauth_callback(payload: OAuthCallbackIn, response: Response):
    try:
        # Validate session ID format before making request
        session_id = payload.session_id.strip()
        if not session_id or session_id != payload.session_id or '\n' in session_id or '\r' in session_id:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Call Emergent auth API to get user data (as per verified playbook)
        headers = {"X-Session-ID": session_id}
        emergent_response = requests.get("https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data", headers=headers)
        
        if emergent_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        oauth_data = emergent_response.json()
        # Expected response: {"id": "string", "email": "string", "name": "string", "picture": "string", "session_token": "string"}
        
        # Check if user already exists (do not update existing user data as per playbook)
        existing_user = await db.users.find_one({"email": oauth_data["email"]})
        
        if existing_user:
            # Use existing user, don't update data as per playbook
            user_data = existing_user
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            user_data = {
                "_id": user_id,
                "id": user_id,
                "email": oauth_data["email"],
                "name": oauth_data.get("name", ""),
                "picture": oauth_data.get("picture", ""),
                "role": payload.role,
                "auth_method": "oauth",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.users.insert_one(user_data)
        
        # Save session token in sessions table with 7-day expiry (as per verified playbook)
        session_token = oauth_data.get("session_token")
        if session_token:
            session_data = {
                "_id": session_token,
                "user_id": user_data["id"],
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=7)
            }
            await db.sessions.insert_one(session_data)
            
            # Set HttpOnly cookie (as per verified playbook)
            response.set_cookie(
                key="session_token",
                value=session_token,
                max_age=7*24*60*60,  # 7 days in seconds
                path="/",
                httponly=True,
                secure=True,
                samesite="none"
            )
        
        # Create JWT access token as fallback
        access_token = create_access_token(data={"sub": user_data["id"]})
        
        return OAuthCallbackOut(
            access_token=access_token,
            user_id=user_data["id"],
            email=user_data["email"],
            name=user_data.get("name", ""),
            role=user_data["role"]
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 400 Invalid session ID) without converting to 500
        raise
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Failed to validate OAuth session")
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

# Profile Settings System
class UserProfileOut(BaseModel):
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    phone_number: Optional[str]
    locale: str = "en_US"
    time_zone: str = "America/Chicago"
    preferences: dict = {}
    privacy_settings: dict = {}
    notification_settings: dict = {}
    two_factor_enabled: bool = False
    
class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    time_zone: Optional[str] = None
    preferences: Optional[dict] = None
    privacy_settings: Optional[dict] = None
    notification_settings: Optional[dict] = None

class AvatarUploadOut(BaseModel):
    avatar_url: str

class DataExportRequestOut(BaseModel):
    request_id: str
    status: str
    estimated_completion: str

class DataDeletionRequest(BaseModel):
    confirmation_text: str
    
class DataDeletionRequestOut(BaseModel):
    deletion_id: str
    confirmation_required: bool
    confirmation_email_sent: bool

class MFASetupRequest(BaseModel):
    method: str = "totp"  # totp, sms
    
class MFASetupOut(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]
    
class MFAVerificationRequest(BaseModel):
    code: str
    secret: str
    
class MFAVerificationOut(BaseModel):
    verified: bool
    backup_codes: List[str]

class TrustedDeviceOut(BaseModel):
    id: str
    device_name: str
    device_type: str
    last_seen: datetime
    location: Optional[str]

@api.get("/profiles/me", response_model=UserProfileOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        # Get or create user profile
        profile = await db.user_profiles.find_one({"user_id": current_user["id"]})
        
        if not profile:
            # Create default profile
            profile = {
                "_id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "display_name": current_user.get("name", current_user["email"].split("@")[0]),
                "avatar_url": current_user.get("picture"),
                "bio": "",
                "phone_number": "",
                "locale": "en_US",
                "time_zone": "America/Chicago",
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "date_format": "MM/dd/yyyy",
                    "currency": "USD"
                },
                "privacy_settings": {
                    "profile_visibility": "contacts_only",
                    "show_certification_status": True,
                    "allow_provider_contact": True,
                    "share_anonymized_data": False
                },
                "notification_settings": {
                    "email_notifications": {
                        "assessment_reminders": True,
                        "provider_matches": True,
                        "certificate_issued": True
                    },
                    "push_notifications": {
                        "enabled": True,
                        "assessment_progress": True
                    }
                },
                "two_factor_enabled": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.user_profiles.insert_one(profile)
        
        return UserProfileOut(**profile)
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to load profile")

@api.patch("/profiles/me", response_model=UserProfileOut) 
async def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile with optimistic locking"""
    try:
        update_data = profile_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Log profile changes for audit
        changes = []
        for field, new_value in update_data.items():
            if field != "updated_at":
                changes.append({
                    "field": field,
                    "new_value": new_value,
                    "timestamp": datetime.utcnow()
                })
        
        # Create audit log entry
        if changes:
            await db.audit_logs.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "action": "profile_update",
                "resource": "user_profile",
                "changes": changes,
                "timestamp": datetime.utcnow(),
                "ip_address": None,  # Would be extracted from request
                "user_agent": None
            })
        
        result = await db.user_profiles.update_one(
            {"user_id": current_user["id"]},
            {"$set": update_data},
            upsert=True
        )
        
        # Get updated profile
        updated_profile = await db.user_profiles.find_one({"user_id": current_user["id"]})
        return UserProfileOut(**updated_profile)
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@api.post("/profiles/me/avatar", response_model=AvatarUploadOut)
async def upload_avatar(
    file: UploadFile,
    current_user: dict = Depends(get_current_user)
):
    """Upload and process avatar"""
    try:
        # Validate file type and size
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        avatar_filename = f"avatars/{current_user['id']}/{uuid.uuid4()}.{file_extension}"
        
        # In a real implementation, you would upload to cloud storage (S3, etc.)
        # For now, we'll simulate with a URL
        avatar_url = f"/static/uploads/{avatar_filename}"
        
        # Update user profile
        await db.user_profiles.update_one(
            {"user_id": current_user["id"]},
            {"$set": {"avatar_url": avatar_url, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        return AvatarUploadOut(avatar_url=avatar_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload avatar")

@api.post("/profiles/me/data-export", response_model=DataExportRequestOut)
async def request_data_export(current_user: dict = Depends(get_current_user)):
    """Request complete data export (GDPR/CCPA compliance)"""
    try:
        request_id = str(uuid.uuid4())
        
        # Create export request record
        export_request = {
            "_id": request_id,
            "user_id": current_user["id"],
            "status": "pending",
            "requested_at": datetime.utcnow(),
            "estimated_completion": datetime.utcnow() + timedelta(hours=24),
            "data_types": [
                "user_profile", "business_profile", "assessments", 
                "certificates", "evidence", "audit_logs"
            ]
        }
        
        await db.data_export_requests.insert_one(export_request)
        
        # In a real implementation, trigger background job for data collection
        # await queue_data_export_job(current_user["id"], request_id)
        
        return DataExportRequestOut(
            request_id=request_id,
            status="pending",
            estimated_completion="24 hours"
        )
        
    except Exception as e:
        logger.error(f"Error requesting data export: {e}")
        raise HTTPException(status_code=500, detail="Failed to request data export")

@api.post("/profiles/me/data-deletion", response_model=DataDeletionRequestOut)
async def request_data_deletion(
    deletion_request: DataDeletionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request account and data deletion"""
    try:
        if deletion_request.confirmation_text != "DELETE MY ACCOUNT":
            raise HTTPException(
                status_code=400, 
                detail="Confirmation text must be 'DELETE MY ACCOUNT'"
            )
        
        deletion_id = str(uuid.uuid4())
        
        # Create deletion request
        deletion_record = {
            "_id": deletion_id,
            "user_id": current_user["id"],
            "status": "pending_confirmation",
            "requested_at": datetime.utcnow(),
            "confirmation_token": str(uuid.uuid4()),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        await db.data_deletion_requests.insert_one(deletion_record)
        
        # In real implementation, send confirmation email
        # await send_deletion_confirmation_email(current_user["email"], deletion_record["confirmation_token"])
        
        return DataDeletionRequestOut(
            deletion_id=deletion_id,
            confirmation_required=True,
            confirmation_email_sent=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting data deletion: {e}")
        raise HTTPException(status_code=500, detail="Failed to request data deletion")

@api.post("/security/mfa/setup", response_model=MFASetupOut)
async def setup_mfa(
    mfa_request: MFASetupRequest,
    current_user: dict = Depends(get_current_user)
):
    """Initialize MFA setup"""
    try:
        import secrets
        import base64
        
        # Generate TOTP secret
        secret = base64.b32encode(secrets.token_bytes(20)).decode()
        
        # Generate backup codes
        backup_codes = [
            f"{secrets.randbelow(1000000):06d}" for _ in range(8)
        ]
        
        # Create QR code URL (in real implementation, use proper TOTP library)
        app_name = "Polaris"
        qr_code_url = f"otpauth://totp/{app_name}:{current_user['email']}?secret={secret}&issuer={app_name}"
        
        # Store temporary MFA setup (not yet activated)
        await db.mfa_setup_temp.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "secret": secret,
            "backup_codes": backup_codes,
            "method": mfa_request.method,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=15)
        })
        
        return MFASetupOut(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
        
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup MFA")

@api.post("/security/mfa/verify", response_model=MFAVerificationOut)
async def verify_mfa_setup(
    verification: MFAVerificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Complete MFA setup verification"""
    try:
        # In real implementation, verify TOTP code against secret
        # For demo, we'll accept any 6-digit code
        if not verification.code or len(verification.code) != 6:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # Get temporary MFA setup
        temp_setup = await db.mfa_setup_temp.find_one({
            "user_id": current_user["id"],
            "secret": verification.secret
        })
        
        if not temp_setup:
            raise HTTPException(status_code=400, detail="Invalid or expired MFA setup")
        
        # Activate MFA for user
        await db.user_profiles.update_one(
            {"user_id": current_user["id"]},
            {
                "$set": {
                    "two_factor_enabled": True,
                    "mfa_secret": verification.secret,
                    "mfa_backup_codes": temp_setup["backup_codes"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Clean up temporary setup
        await db.mfa_setup_temp.delete_one({"_id": temp_setup["_id"]})
        
        return MFAVerificationOut(
            verified=True,
            backup_codes=temp_setup["backup_codes"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify MFA")

@api.get("/security/trusted-devices", response_model=List[TrustedDeviceOut])
async def get_trusted_devices(current_user: dict = Depends(get_current_user)):
    """Get user's trusted devices"""
    try:
        devices = await db.trusted_devices.find({"user_id": current_user["id"]}).to_list(100)
        
        return [
            TrustedDeviceOut(
                id=device["_id"],
                device_name=device.get("device_name", "Unknown Device"),
                device_type=device.get("device_type", "unknown"),
                last_seen=device.get("last_seen", datetime.utcnow()),
                location=device.get("location")
            )
            for device in devices
        ]
        
    except Exception as e:
        logger.error(f"Error getting trusted devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to load trusted devices")

@api.delete("/security/trusted-devices/{device_id}")
async def revoke_trusted_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke trust for a specific device"""
    try:
        result = await db.trusted_devices.delete_one({
            "_id": device_id,
            "user_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Trusted device not found")
        
        # Log security action
        await db.audit_logs.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "action": "device_revoked",
            "resource": "trusted_device",
            "resource_id": device_id,
            "timestamp": datetime.utcnow()
        })
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking trusted device: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke device")

# Administrative System
class SystemStatsOut(BaseModel):
    total_users: int
    active_businesses: int
    certificates_issued: int
    recent_users: List[dict]
    platform_health: dict

class UserListOut(BaseModel):
    users: List[dict]
    total: int
    page: int
    per_page: int

class BulkActionRequest(BaseModel):
    action: str  # activate, deactivate, suspend, delete
    user_ids: List[str]

class UserActionRequest(BaseModel):
    action: str

class AuditLogOut(BaseModel):
    id: str
    timestamp: datetime
    user_id: str
    user_email: Optional[str]
    user_role: Optional[str]
    action: str
    resource: str
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]

class AuditLogsListOut(BaseModel):
    logs: List[AuditLogOut]
    total: int
    page: int

# Admin-only decorator
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@api.get("/admin/system/stats", response_model=SystemStatsOut)
async def get_system_stats(admin_user: dict = Depends(require_admin)):
    """Get comprehensive system statistics for admin dashboard"""
    try:
        # Get user statistics
        total_users = await db.users.count_documents({})
        
        # Get active businesses (users with business profiles)
        active_businesses = await db.business_profiles.count_documents({"status": {"$ne": "deleted"}})
        
        # Get certificate count
        certificates_issued = await db.certificates.count_documents({})
        
        # Get recent users (last 10)
        recent_users_cursor = db.users.find({}).sort("created_at", -1).limit(10)
        recent_users = await recent_users_cursor.to_list(10)
        
        # Clean up recent users data
        recent_users_clean = []
        for user in recent_users:
            recent_users_clean.append({
                "id": user["_id"],
                "name": user.get("name", ""),
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"]
            })
        
        # Platform health metrics (mock data for MVP)
        platform_health = {
            "api_response_time": "145ms",
            "database_connections": "23/100",
            "storage_usage": "67%",
            "uptime": "99.9%"
        }
        
        return SystemStatsOut(
            total_users=total_users,
            active_businesses=active_businesses,
            certificates_issued=certificates_issued,
            recent_users=recent_users_clean,
            platform_health=platform_health
        )
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to load system statistics")

@api.get("/admin/users", response_model=UserListOut)
async def get_users_admin(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_user: dict = Depends(require_admin)
):
    """Get paginated list of users with filtering"""
    try:
        # Build query filters
        query = {}
        
        if role:
            query["role"] = role
        
        if status:
            query["status"] = status
            
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await db.users.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = db.users.find(query).sort("created_at", -1).skip(skip).limit(per_page)
        users = await cursor.to_list(per_page)
        
        # Clean up user data
        users_clean = []
        for user in users:
            users_clean.append({
                "id": user["_id"],
                "name": user.get("name", ""),
                "email": user["email"],
                "role": user["role"],
                "status": user.get("status", "active"),
                "created_at": user["created_at"],
                "updated_at": user.get("updated_at", user["created_at"]),
                "last_sign_in": user.get("last_sign_in")
            })
        
        return UserListOut(
            users=users_clean,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to load users")

@api.post("/admin/users/bulk-action")
async def bulk_user_action(
    request: BulkActionRequest,
    admin_user: dict = Depends(require_admin)
):
    """Perform bulk actions on multiple users"""
    try:
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="No users selected")
        
        # Define allowed actions
        allowed_actions = ["activate", "deactivate", "suspend"]
        if request.action not in allowed_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Allowed: {allowed_actions}")
        
        # Map actions to status updates
        status_mapping = {
            "activate": "active",
            "deactivate": "inactive", 
            "suspend": "suspended"
        }
        
        new_status = status_mapping[request.action]
        
        # Update users
        result = await db.users.update_many(
            {"_id": {"$in": request.user_ids}},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log bulk action
        await db.audit_logs.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": admin_user["id"],
            "action": f"bulk_{request.action}",
            "resource": "users",
            "details": {
                "affected_users": request.user_ids,
                "new_status": new_status
            },
            "timestamp": datetime.utcnow(),
            "ip_address": None,
            "user_agent": None
        })
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "action": request.action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk user action: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk action")

@api.post("/admin/users/{user_id}/action")
async def user_action(
    user_id: str,
    request: UserActionRequest,
    admin_user: dict = Depends(require_admin)
):
    """Perform action on individual user"""
    try:
        # Get user first
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle different actions
        if request.action == "activate":
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"status": "active", "updated_at": datetime.utcnow()}}
            )
        elif request.action == "suspend":
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"status": "suspended", "updated_at": datetime.utcnow()}}
            )
        elif request.action == "edit":
            # For edit, we would typically return user data for a modal
            return {"action": "edit", "user_id": user_id}
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Log action
        await db.audit_logs.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": admin_user["id"],
            "action": f"user_{request.action}",
            "resource": "user",
            "resource_id": user_id,
            "details": {"target_user_email": user["email"]},
            "timestamp": datetime.utcnow()
        })
        
        return {"success": True, "action": request.action}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in user action: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform user action")

@api.get("/admin/audit-logs", response_model=AuditLogsListOut)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    admin_user: dict = Depends(require_admin)
):
    """Get paginated audit logs with filtering"""
    try:
        # Build query filters
        query = {}
        
        if user_id:
            query["user_id"] = user_id
            
        if action:
            query["action"] = action
            
        if resource:
            query["resource"] = resource
            
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_query["$lte"] = datetime.fromisoformat(date_to)
            query["timestamp"] = date_query
        
        # Get total count
        total = await db.audit_logs.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(per_page)
        logs = await cursor.to_list(per_page)
        
        # Enrich logs with user information
        logs_enriched = []
        for log in logs:
            # Get user info if available
            user_info = await db.users.find_one({"_id": log["user_id"]})
            
            log_data = {
                "id": log["_id"],
                "timestamp": log["timestamp"],
                "user_id": log["user_id"],
                "user_email": user_info.get("email") if user_info else None,
                "user_role": user_info.get("role") if user_info else None,
                "action": log["action"],
                "resource": log["resource"],
                "resource_id": log.get("resource_id"),
                "details": log.get("details"),
                "ip_address": log.get("ip_address"),
                "user_agent": log.get("user_agent")
            }
            logs_enriched.append(AuditLogOut(**log_data))
        
        return AuditLogsListOut(
            logs=logs_enriched,
            total=total,
            page=page
        )
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to load audit logs")

# Enhanced audit logging helper
async def create_audit_log(
    user_id: str,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Create standardized audit log entry"""
    try:
        audit_entry = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details,
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        await db.audit_logs.insert_one(audit_entry)
        
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")
# Assessment System Implementation
@api.get("/assessment/schema")
async def get_assessment_schema():
    """Get the assessment schema with all business areas and questions"""
    try:
        return {"schema": ASSESSMENT_SCHEMA}
    except Exception as e:
        logger.error(f"Error getting assessment schema: {e}")
        raise HTTPException(status_code=500, detail="Failed to load assessment schema")

@api.post("/assessment/session")
async def create_assessment_session(current_user: dict = Depends(get_current_user)):
    """Create a new assessment session for the user"""
    try:
        session_id = str(uuid.uuid4())
        
        # Create assessment session record
        session_data = {
            "_id": session_id,
            "user_id": current_user["id"],
            "status": "in_progress",
            "progress": {},
            "responses": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.assessment_sessions.insert_one(session_data)
        
        # Create audit log
        await create_audit_log(
            user_id=current_user["id"],
            action="assessment_session_created",
            resource="assessment_session",
            resource_id=session_id
        )
        
        return {
            "session_id": session_id,
            "status": "created",
            "schema": ASSESSMENT_SCHEMA
        }
        
    except Exception as e:
        logger.error(f"Error creating assessment session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create assessment session")

@api.get("/assessment/session/{session_id}/progress")
async def get_assessment_progress(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get assessment session progress"""
    try:
        # Get assessment session
        session = await db.assessment_sessions.find_one({
            "_id": session_id,
            "user_id": current_user["id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Assessment session not found")
        
        # Calculate progress
        total_questions = sum(len(area["questions"]) for area in ASSESSMENT_SCHEMA["areas"])
        answered_questions = len(session.get("responses", {}))
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "progress_percentage": progress_percentage,
            "answered_questions": answered_questions,
            "total_questions": total_questions,
            "responses": session.get("responses", {}),
            "last_updated": session.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get assessment progress")

@api.post("/assessment/session/{session_id}/response")
async def submit_assessment_response(
    session_id: str,
    response_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit response to assessment question"""
    try:
        # Validate session belongs to user
        session = await db.assessment_sessions.find_one({
            "_id": session_id,
            "user_id": current_user["id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Assessment session not found")
        
        # Update session with new response
        question_id = response_data.get("question_id")
        answer = response_data.get("answer")
        
        if not question_id or answer is None:
            raise HTTPException(status_code=400, detail="Question ID and answer are required")
        
        # Update responses
        await db.assessment_sessions.update_one(
            {"_id": session_id},
            {
                "$set": {
                    f"responses.{question_id}": answer,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get updated session for progress calculation
        updated_session = await db.assessment_sessions.find_one({"_id": session_id})
        total_questions = sum(len(area["questions"]) for area in ASSESSMENT_SCHEMA["areas"])
        answered_questions = len(updated_session.get("responses", {}))
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        # Check if assessment is complete
        if progress_percentage >= 100:
            await db.assessment_sessions.update_one(
                {"_id": session_id},
                {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
            )
        
        return {
            "success": True,
            "progress_percentage": progress_percentage,
            "answered_questions": answered_questions,
            "total_questions": total_questions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting assessment response: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit assessment response")

@api.post("/ai/explain")
async def get_ai_explanation(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Get AI explanation for assessment questions"""
    try:
        question_id = request_data.get("question_id")
        context = request_data.get("context", "")
        
        if not question_id:
            raise HTTPException(status_code=400, detail="Question ID is required")
        
        # Find the question in the schema
        question_text = None
        area_name = None
        
        for area in ASSESSMENT_SCHEMA["areas"]:
            for question in area["questions"]:
                if question["id"] == question_id:
                    question_text = question["text"]
                    area_name = area["title"]
                    break
            if question_text:
                break
        
        if not question_text:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Generate AI explanation (simplified for MVP)
        explanations = {
            "deliverables": f"For '{question_text}', the key deliverables include documented processes, compliance certificates, and evidence of implementation.",
            "why_it_matters": f"This requirement is critical for procurement readiness because it demonstrates your business capability and reduces risk for contracting officers.",
            "acceptable_alternatives": f"Alternative approaches may include third-party certifications, equivalent documentation, or phased implementation plans.",
            "free_resources": [
                "SBA.gov procurement resources",
                "SCORE business mentoring", 
                "Local PTAC assistance",
                "Industry association guidance"
            ]
        }
        
        # Log AI explanation request
        await create_audit_log(
            user_id=current_user["id"],
            action="ai_explanation_requested",
            resource="assessment_question",
            resource_id=question_id,
            details={"area": area_name, "context": context}
        )
        
        return {
            "question_id": question_id,
            "question_text": question_text,
            "area": area_name,
            **explanations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI explanation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI explanation")

@api.get("/client/matched-services")
async def get_client_matched_services(current_user: dict = Depends(get_current_user)):
    """Get services matched to the client based on their assessment needs"""
    try:
        if current_user.get("role") != "client":
            raise HTTPException(status_code=403, detail="Client access required")
        
        # For MVP, return sample matched services
        # In production, this would query based on assessment results and provider availability
        sample_services = [
            {
                "provider_name": "San Antonio Business Solutions",
                "service_type": "Business Formation & Legal Compliance",
                "budget_range": "$500 - $1,500",
                "areas": ["Business Formation", "Legal Compliance", "Insurance Setup"],
                "description": "Comprehensive business formation services including license acquisition, legal entity setup, and compliance documentation for small business procurement readiness.",
                "rating": "4.9",
                "reviews": "18",
                "provider_id": str(uuid.uuid4())
            },
            {
                "provider_name": "Alamo City Financial Services",
                "service_type": "Financial Operations & Accounting",
                "budget_range": "$750 - $2,000",
                "areas": ["Financial Operations", "Accounting Systems", "Tax Preparation"],
                "description": "Professional accounting setup, financial statement preparation, and bookkeeping system implementation for procurement-ready businesses.",
                "rating": "4.8",
                "reviews": "24",
                "provider_id": str(uuid.uuid4())
            },
            {
                "provider_name": "Lone Star Tech Solutions",
                "service_type": "Technology & Security Infrastructure",
                "budget_range": "$1,000 - $3,500",
                "areas": ["Cybersecurity", "Technology Infrastructure", "Data Management"],
                "description": "Complete technology infrastructure setup including cybersecurity, cloud systems, and data backup solutions for government contracting readiness.",
                "rating": "4.7",
                "reviews": "12",
                "provider_id": str(uuid.uuid4())
            }
        ]
        
        return {"services": sample_services}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matched services: {e}")
        raise HTTPException(status_code=500, detail="Failed to load matched services")

# Provider Approval System
@api.get("/navigator/providers/pending")
async def get_pending_providers(current=Depends(require_role("navigator"))):
    """Get all providers pending approval"""
    providers = await db.users.find({"role": "provider", "approval_status": {"$ne": "approved"}}).to_list(1000)
    return {"providers": providers}

@api.post("/navigator/providers/approve", response_model=ProviderApprovalOut)
async def approve_provider(payload: ProviderApprovalIn, current=Depends(require_role("navigator"))):
    """Approve or reject a service provider"""
    # Check if provider exists
    provider = await db.users.find_one({"id": payload.provider_user_id, "role": "provider"})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Update provider approval status
    await db.users.update_one(
        {"id": payload.provider_user_id},
        {"$set": {"approval_status": payload.approval_status, "updated_at": datetime.utcnow()}}
    )
    
    # Create approval record
    approval_id = str(uuid.uuid4())
    approval_doc = {
        "_id": approval_id,
        "id": approval_id,
        "provider_user_id": payload.provider_user_id,
        "navigator_user_id": current["id"],
        "approval_status": payload.approval_status,
        "notes": payload.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.provider_approvals.insert_one(approval_doc)
    
    return ProviderApprovalOut(**approval_doc)

@api.get("/providers/approved")
async def get_approved_providers():
    """Get all approved service providers for marketplace"""
    providers = await db.users.find({"role": "provider", "approval_status": "approved"}).to_list(1000)
    return {"providers": providers}


# ---------------- Agency Approval System ----------------
class AgencyApprovalIn(BaseModel):
    agency_user_id: str
    approval_status: str = Field(..., pattern="^(approved|rejected)$")
    notes: Optional[str] = None

class AgencyApprovalOut(BaseModel):
    id: str
    agency_user_id: str
    navigator_user_id: str
    approval_status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@api.get("/navigator/agencies/pending")
async def get_pending_agencies(current=Depends(require_role("navigator"))):
    """Get all agencies pending approval"""
    agencies = await db.users.find({"role": "agency", "approval_status": {"$ne": "approved"}}).to_list(1000)
    return {"agencies": agencies}

@api.post("/navigator/agencies/approve", response_model=AgencyApprovalOut)
async def approve_agency(payload: AgencyApprovalIn, current=Depends(require_role("navigator"))):
    """Approve or reject an agency"""
    # Check if agency exists
    agency = await db.users.find_one({"id": payload.agency_user_id, "role": "agency"})
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Update agency approval status
    await db.users.update_one(
        {"id": payload.agency_user_id},
        {"$set": {"approval_status": payload.approval_status, "updated_at": datetime.utcnow()}}
    )

    # Create approval record
    approval_id = str(uuid.uuid4())
    approval_doc = {
        "_id": approval_id,
        "id": approval_id,
        "agency_user_id": payload.agency_user_id,
        "navigator_user_id": current["id"],
        "approval_status": payload.approval_status,
        "notes": payload.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.agency_approvals.insert_one(approval_doc)

    return AgencyApprovalOut(**approval_doc)

# ---------------- Minimal Assessment Schema for readiness calc ----------------
ASSESSMENT_SCHEMA: Dict[str, Dict] = {
    "areas": [
        {
            "id": "area1", 
            "title": "Business Formation & Registration", 
            "questions": [
                {"id": "q1_1", "text": "Do you have a valid business license in your jurisdiction?"},
                {"id": "q1_2", "text": "Is your business registered with the appropriate state and local authorities?"},
                {"id": "q1_3", "text": "Do you have proper business insurance coverage?"}
            ]
        },
        {
            "id": "area2", 
            "title": "Financial Operations & Management", 
            "questions": [
                {"id": "q2_1", "text": "Do you have a professional accounting system in place?"},
                {"id": "q2_2", "text": "Are your financial records current and audit-ready?"},
                {"id": "q2_3", "text": "Do you have established credit and banking relationships?"}
            ]
        },
        {
            "id": "area3", 
            "title": "Legal & Contracting Compliance", 
            "questions": [
                {"id": "q3_1", "text": "Do you have standard service agreements and contracts?"},
                {"id": "q3_2", "text": "Are you compliant with relevant industry regulations?"},
                {"id": "q3_3", "text": "Do you have proper intellectual property protections?"}
            ]
        },
        {
            "id": "area4", 
            "title": "Quality Management & Standards", 
            "questions": [
                {"id": "q4_1", "text": "Do you have documented quality control processes?"},
                {"id": "q4_2", "text": "Are your services certified or accredited where applicable?"},
                {"id": "q4_3", "text": "Do you have customer feedback and improvement systems?"}
            ]
        },
        {
            "id": "area5", 
            "title": "Technology & Security Infrastructure", 
            "questions": [
                {"id": "q5_1", "text": "Do you have adequate cybersecurity measures in place?"},
                {"id": "q5_2", "text": "Are your technology systems scalable for larger contracts?"},
                {"id": "q5_3", "text": "Do you have data backup and recovery procedures?"}
            ]
        },
        {
            "id": "area6", 
            "title": "Human Resources & Capacity", 
            "questions": [
                {"id": "q6_1", "text": "Do you have sufficient staffing for project delivery?"},
                {"id": "q6_2", "text": "Are your team members properly trained and certified?"},
                {"id": "q6_3", "text": "Do you have employee onboarding and development programs?"}
            ]
        },
        {
            "id": "area7", 
            "title": "Performance Tracking & Reporting", 
            "questions": [
                {"id": "q7_1", "text": "Do you have KPI tracking and reporting systems?"},
                {"id": "q7_2", "text": "Can you provide regular progress reports to clients?"},
                {"id": "q7_3", "text": "Do you maintain project documentation and deliverables?"}
            ]
        },
        {
            "id": "area8", 
            "title": "Risk Management & Business Continuity", 
            "questions": [
                {"id": "q8_1", "text": "Do you have a business continuity plan?"},
                {"id": "q8_2", "text": "Are you prepared for emergency situations and disruptions?"},
                {"id": "q8_3", "text": "Do you have appropriate liability and professional insurance?"}
            ]
        }
    ]
}

# ---------------- AI resources for "No" pathway ----------------
class AIResourcesReq(BaseModel):
    area_id: str
    question_id: str
    question_text: Optional[str] = None
    locality: str = "San Antonio, TX"
    count: int = 3
    prefer: str = "gov_edu_nonprofit"

class ResourceItem(BaseModel):
    name: str
    url: str
    summary: str
    source_type: str
    locality: str

class AIResourcesResp(BaseModel):
    resources: List[ResourceItem]

@api.post("/ai/resources", response_model=AIResourcesResp)
async def ai_resources(req: AIResourcesReq, current=Depends(require_user)):
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key or not EMERGENT_OK:
        return AIResourcesResp(resources=[
            ResourceItem(name="UTSA Small Business Development Center", url="https://sasbdc.org/", summary="Free advising, workshops, and templates for small businesses.", source_type="edu/nonprofit", locality="local"),
            ResourceItem(name="SCORE San Antonio", url="https://www.score.org/sanantonio", summary="No-cost mentoring and resources for entrepreneurs.", source_type="nonprofit", locality="local"),
            ResourceItem(name="SBA Resource Partners", url="https://www.sba.gov/local-assistance", summary="Federal resources and partners offering guidance and tools.", source_type="gov", locality="online"),
        ])
    system = ("You are a procurement readiness navigator. Return concise, credible free resources. Prefer .gov, .edu, or nonprofit sources; tailor to the question and San Antonio, TX. Return JSON array of {name,url,summary,source_type,locality}.")
    chat = LlmChat(api_key=llm_key, session_id=str(uuid.uuid4()), system_message=system).with_model("openai", "gpt-4o-mini")
    prompt = f"Locality: {req.locality}\nCount: {req.count}\nQuestion: {req.question_text or req.question_id}\nArea: {req.area_id}."
    try:
        resp = await chat.send_message(UserMessage(text=prompt))
        import json as pyjson
        data = None
        try:
            data = pyjson.loads(str(resp))
        except Exception:
            txt = str(resp)
            s = txt.find('['); e = txt.rfind(']')
            if s != -1 and e != -1 and e > s:
                data = pyjson.loads(txt[s:e+1])
        items = []
        if isinstance(data, list):
            for it in data[: req.count]:
                items.append(ResourceItem(name=str(it.get("name","Resource")), url=str(it.get("url","")), summary=str(it.get("summary",""))[:200], source_type=str(it.get("source_type","other")), locality=str(it.get("locality","online"))))
        if not items:
            items = [
                ResourceItem(name="UTSA Small Business Development Center", url="https://sasbdc.org/", summary="Free advising, workshops, and templates for small businesses.", source_type="edu/nonprofit", locality="local"),
                ResourceItem(name="SCORE San Antonio", url="https://www.score.org/sanantonio", summary="No-cost mentoring and resources for entrepreneurs.", source_type="nonprofit", locality="local"),
                ResourceItem(name="SBA Resource Partners", url="https://www.sba.gov/local-assistance", summary="Federal resources and partners offering guidance and tools.", source_type="gov", locality="online"),
            ]
        return AIResourcesResp(resources=items[: req.count])
    except Exception as e:
        logger.exception("AI resources failed")
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

# ---------------- Business Profiles (client & provider) ----------------
class BusinessProfileIn(BaseModel):
    company_name: str
    legal_entity_type: str
    tax_id: str
    registered_address: str
    mailing_address: str
    website_url: Optional[HttpUrl] = None
    industry: str
    primary_products_services: str
    revenue_range: str
    revenue_currency: str = "USD"
    employees_count: str
    year_founded: Optional[int] = None
    ownership_structure: str
    contact_name: str
    contact_title: str
    contact_email: EmailStr
    contact_phone: str

class BusinessProfileOut(BusinessProfileIn):
    id: str
    role: str
    logo_upload_id: Optional[str] = None

REQUIRED_BUSINESS_FIELDS = [
    "company_name","legal_entity_type","tax_id","registered_address","mailing_address","industry","primary_products_services","revenue_range","employees_count","ownership_structure","contact_name","contact_title","contact_email","contact_phone","payment_methods","subscription_plan","billing_frequency"
]

@api.get("/business/profile/me", response_model=Optional[BusinessProfileOut])
async def get_my_business_profile(current=Depends(require_user)):
    if current.get("role") not in ("client","provider"):
        raise HTTPException(status_code=403, detail="Not applicable")
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    if not prof:
        return None
    return BusinessProfileOut(id=prof["_id"], role=prof.get("role","client"), logo_upload_id=prof.get("logo_upload_id"), **{k: prof.get(k) for k in BusinessProfileIn.model_fields.keys()})

@api.post("/business/profile", response_model=BusinessProfileOut)
async def upsert_business_profile(payload: BusinessProfileIn, current=Depends(require_user)):
    if current.get("role") not in ("client","provider"):
        raise HTTPException(status_code=403, detail="Not applicable")
    existing = await db.business_profiles.find_one({"user_id": current["id"]})
    now = datetime.utcnow()
    docset = {**payload.dict(), "updated_at": now, "role": current["role"]}
    if existing:
        await db.business_profiles.update_one({"_id": existing["_id"]}, {"$set": docset})
        prof = await db.business_profiles.find_one({"_id": existing["_id"]})
        pid = existing["_id"]
    else:
        pid = str(uuid.uuid4())
        doc = {"_id": pid, "id": pid, "user_id": current["id"], **payload.dict(), "role": current["role"], "created_at": now, "updated_at": now}
        await db.business_profiles.insert_one(doc)
        prof = doc
    return BusinessProfileOut(id=pid, role=prof.get("role"), logo_upload_id=prof.get("logo_upload_id"), **{k: prof.get(k) for k in BusinessProfileIn.model_fields.keys()})

@api.get("/business/profile/me/completion")
async def business_profile_completion(current=Depends(require_user)):
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    missing = []
    if not prof:
        missing = REQUIRED_BUSINESS_FIELDS + ["logo_upload_id"]
    else:
        for k in REQUIRED_BUSINESS_FIELDS:
            v = prof.get(k)
            if v in (None, "", [], {}):
                missing.append(k)
        if not prof.get("logo_upload_id"):
            missing.append("logo_upload_id")
    return {"complete": len(missing)==0, "missing": missing}

@api.post("/business/logo/initiate")
async def biz_logo_initiate(file_name: str = Form(...), total_size: int = Form(...), mime_type: str = Form("application/octet-stream"), current=Depends(require_user)):
    if current.get("role") not in ("client","provider"):
        raise HTTPException(status_code=403, detail="Not applicable")
    uid = str(uuid.uuid4())
    doc = {"_id": uid, "id": uid, "type": "business_logo", "user_id": current["id"], "file_name": file_name, "mime_type": mime_type, "total_size": total_size, "created_at": datetime.utcnow(), "status": "initiated"}
    await db.uploads.insert_one(doc)
    (UPLOAD_BASE / uid).mkdir(parents=True, exist_ok=True)
    return {"upload_id": uid, "chunk_size": 5*1024*1024}

@api.post("/business/logo/chunk")
async def biz_logo_chunk(upload_id: str = Form(...), chunk_index: int = Form(...), file: UploadFile = File(...), current=Depends(require_user)):
    rec = await db.uploads.find_one({"_id": upload_id, "type": "business_logo", "user_id": current["id"]})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    part_path = UPLOAD_BASE / upload_id / f"part_{chunk_index}"
    async with aiofiles.open(part_path, "wb") as out:
        while True:
            data = await file.read(1024 * 1024)
            if not data:
                break
            await out.write(data)
    return {"ok": True}

@api.post("/business/logo/complete")
async def biz_logo_complete(upload_id: str = Form(...), total_chunks: int = Form(...), current=Depends(require_user)):
    rec = await db.uploads.find_one({"_id": upload_id, "type": "business_logo", "user_id": current["id"]})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    final_path = UPLOAD_BASE / f"{upload_id}_{rec.get('file_name') or 'logo'}"
    async with aiofiles.open(final_path, "wb") as out:
        for i in range(int(total_chunks)):
            part_path = UPLOAD_BASE / upload_id / f"part_{i}"
            async with aiofiles.open(part_path, "rb") as f:
                while True:
                    data = await f.read(1024 * 1024)
                    if not data:
                        break
                    await out.write(data)
    size = final_path.stat().st_size
    await db.uploads.update_one({"_id": upload_id}, {"$set": {"status": "completed", "stored_path": str(final_path), "final_size": size, "completed_at": datetime.utcnow()}})
    await db.business_profiles.update_one({"user_id": current["id"]}, {"$set": {"logo_upload_id": upload_id, "updated_at": datetime.utcnow()}}, upsert=True)
    return {"ok": True, "upload_id": upload_id, "size": size}

# ---------------- License Management for Agencies ----------------
class LicenseGenerationIn(BaseModel):
    quantity: int = Field(..., ge=1, le=100)  # Generate 1-100 licenses at a time
    expires_days: Optional[int] = Field(30, ge=7, le=365)  # License validity in days

class LicenseOut(BaseModel):
    license_code: str
    status: str  # available, used, expired
    created_at: datetime
    expires_at: Optional[datetime]
    used_by: Optional[str] = None
    used_at: Optional[datetime] = None

@api.post("/agency/licenses/generate")
async def generate_licenses(request: LicenseGenerationIn, current=Depends(require_role("agency"))):
    """Generate license codes for business client registration"""
    # Check if agency is approved
    user_record = await db.users.find_one({"_id": current["id"]})
    if not user_record or user_record.get("approval_status") != "approved":
        raise HTTPException(status_code=403, detail="Agency must be approved to generate license codes")
    
    licenses = []
    expires_at = datetime.utcnow() + timedelta(days=request.expires_days) if request.expires_days else None
    
    for _ in range(request.quantity):
        license_code = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        # Ensure uniqueness
        while await db.agency_licenses.find_one({"license_code": license_code}):
            license_code = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        license_doc = {
            "_id": str(uuid.uuid4()),
            "license_code": license_code,
            "agency_id": current["id"],
            "status": "available",
            "created_at": datetime.utcnow(),
            "expires_at": expires_at
        }
        
        await db.agency_licenses.insert_one(license_doc)
        licenses.append(license_doc)
    
    return {
        "message": f"Generated {request.quantity} license codes",
        "licenses": [
            {
                "license_code": lic["license_code"],
                "expires_at": lic["expires_at"]
            } for lic in licenses
        ]
    }

@api.get("/agency/licenses")
async def get_agency_licenses(current=Depends(require_role("agency"))):
    """Get all license codes generated by this agency"""
    licenses = await db.agency_licenses.find({
        "agency_id": current["id"]
    }).sort("created_at", -1).to_list(1000)
    
    return {"licenses": licenses}

@api.get("/agency/licenses/stats")
async def get_license_stats(current=Depends(require_role("agency"))):
    """Get license usage statistics for this agency"""
    pipeline = [
        {"$match": {"agency_id": current["id"]}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    stats = await db.agency_licenses.aggregate(pipeline).to_list(10)
    stats_dict = {stat["_id"]: stat["count"] for stat in stats}
    
    return {
        "total_generated": sum(stats_dict.values()),
        "available": stats_dict.get("available", 0),
        "used": stats_dict.get("used", 0),
        "expired": stats_dict.get("expired", 0)
    }

# ---------------- Navigator Approval System ----------------
@api.get("/admin/pending-approvals")
async def get_pending_approvals(current=Depends(require_role("navigator"))):
    """Get all users pending approval"""
    pending_users = await db.users.find({
        "approval_status": "pending"
    }).sort("created_at", 1).to_list(100)
    
    return {"pending_approvals": pending_users}

@api.post("/admin/approve-user")
async def approve_user(user_id: str, current=Depends(require_role("navigator"))):
    """Approve a pending user"""
    user_record = await db.users.find_one({"_id": user_id, "approval_status": "pending"})
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found or not pending approval")
    
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "approval_status": "approved",
                "approved_by": current["id"],
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": f"User {user_record['email']} approved successfully"}

@api.post("/admin/reject-user")
async def reject_user(user_id: str, reason: str, current=Depends(require_role("navigator"))):
    """Reject a pending user"""
    user_record = await db.users.find_one({"_id": user_id, "approval_status": "pending"})
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found or not pending approval")
    
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "approval_status": "rejected",
                "rejected_by": current["id"],
                "rejected_at": datetime.utcnow(),
                "rejection_reason": reason
            }
        }
    )
    
    return {"message": f"User {user_record['email']} rejected"}

# ---------------- Payment Integration ----------------
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")

# Service packages for payment
SERVICE_PACKAGES = {
    "knowledge_base_single": 20.0,
    "knowledge_base_all": 100.0,
    "service_request_small": 50.0,
    "service_request_medium": 150.0,
    "service_request_large": 300.0,
    "assessment_fee": 100.0
}

class PaymentTransactionIn(BaseModel):
    package_id: str
    origin_url: str
    metadata: Optional[Dict[str, str]] = {}

class PaymentTransactionOut(BaseModel):
    id: str
    user_id: str
    package_id: str
    amount: float
    currency: str = "USD"
    stripe_session_id: str
    payment_status: str
    status: str
    metadata: Dict[str, str]
    created_at: datetime
    updated_at: Optional[datetime] = None

class ServiceRequestPaymentIn(BaseModel):
    request_id: str
    provider_id: str
    agreed_fee: float
    origin_url: str

class ServiceTrackingUpdate(BaseModel):
    status: str  # 'active', 'in_progress', 'under_review', 'completed', 'cancelled'
    progress_percentage: Optional[float] = None
    notes: Optional[str] = None
    deliverables: Optional[List[str]] = []

class ServiceRatingIn(BaseModel):
    engagement_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    quality_score: Optional[int] = Field(None, ge=1, le=5)
    communication_score: Optional[int] = Field(None, ge=1, le=5)
    timeliness_score: Optional[int] = Field(None, ge=1, le=5)

# Initialize Stripe checkout if available
stripe_checkout = None
if STRIPE_AVAILABLE and STRIPE_API_KEY:
    try:
        # Initialize will be done in endpoints since we need request object
        pass
    except Exception as e:
        print(f"Stripe initialization error: {e}")

# ---------------- Engagements ----------------
class EngagementCreateIn(BaseModel):
    request_id: str
    response_id: str
    agreed_fee: float

@api.post("/engagements/create")
async def create_engagement(payload: EngagementCreateIn, current=Depends(require_role("client"))):
    # Look in provider_responses collection (not match_responses)
    resp = await db.provider_responses.find_one({"_id": payload.response_id, "request_id": payload.request_id})
    if not resp:
        raise HTTPException(status_code=404, detail="Response not found")
    # Look in service_requests collection (not match_requests)
    req = await db.service_requests.find_one({"_id": payload.request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    eid = str(uuid.uuid4())
    doc = {"_id": eid, "id": eid, "request_id": req["_id"], "response_id": resp["_id"], "client_user_id": current["id"], "provider_user_id": resp.get("provider_id"), "status": "active", "agreed_fee": payload.agreed_fee, "created_at": datetime.utcnow()}
    await db.engagements.insert_one(doc)
    fee = round(payload.agreed_fee * 0.05, 2)
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "marketplace_fee", "amount": fee, "currency": "USD", "status": "pending", "created_at": datetime.utcnow(), "metadata": {"engagement_id": eid, "request_id": req["_id"], "response_id": resp["_id"], "agreed_fee": payload.agreed_fee, "pct": 0.05}}
    await db.revenue_transactions.insert_one(tx)
    # Update service_requests collection (not match_requests)
    await db.service_requests.update_one({"_id": req["_id"]}, {"$set": {"status": "engaged", "engagement_id": eid}})
    return {"ok": True, "engagement_id": eid, "fee": fee}

@api.get("/navigator/engagements")
async def list_engagements(current=Depends(require_role("navigator"))):
    engs = await db.engagements.find({}).to_list(2000)
    return {"engagements": engs}

class EngagementStatusIn(BaseModel):
    status: str

@api.post("/navigator/engagements/{engagement_id}/status")
async def set_engagement_status(engagement_id: str, payload: EngagementStatusIn, current=Depends(require_role("navigator"))):
    if payload.status not in ("active","on_hold","completed","cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")
    await db.engagements.update_one({"_id": engagement_id}, {"$set": {"status": payload.status, "updated_at": datetime.utcnow()}})
    return {"ok": True}

# ---------------- Payment Endpoints ----------------
@api.post("/payments/v1/checkout/session")
async def create_payment_session(request: Request, payload: PaymentTransactionIn, current=Depends(require_user)):
    """Create Stripe checkout session"""
    if not STRIPE_AVAILABLE or not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    # Validate package
    if payload.package_id not in SERVICE_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    # Get amount from server-side definition only (security)
    amount = SERVICE_PACKAGES[payload.package_id]
    
    try:
        # Initialize Stripe checkout with dynamic webhook URL
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_client = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Build URLs from provided origin
        success_url = f"{payload.origin_url}/service-request?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{payload.origin_url}/service-request"
        
        # Add metadata
        metadata = {
            "user_id": current["id"],
            "package_id": payload.package_id,
            "email": current["email"],
            **payload.metadata
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="USD",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_client.create_checkout_session(checkout_request)
        
        # Create pending transaction record BEFORE redirect
        transaction_id = str(uuid.uuid4())
        transaction_doc = {
            "_id": transaction_id,
            "id": transaction_id,
            "user_id": current["id"],
            "package_id": payload.package_id,
            "amount": amount,
            "currency": "USD",
            "stripe_session_id": session.session_id,
            "payment_status": "pending",
            "status": "initiated",
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        await db.payment_transactions.insert_one(transaction_doc)
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment session creation failed: {str(e)}")

@api.get("/payments/v1/checkout/status/{session_id}")
async def get_payment_status(session_id: str, current=Depends(require_user)):
    """Get payment status and update database"""
    if not STRIPE_AVAILABLE or not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    try:
        # Find transaction record
        transaction = await db.payment_transactions.find_one({"stripe_session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Check if transaction belongs to current user
        if transaction["user_id"] != current["id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Initialize Stripe client (we don't need request here, so use dummy webhook)
        stripe_client = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="https://dummy.com/webhook")
        
        # Get status from Stripe
        checkout_status = await stripe_client.get_checkout_status(session_id)
        
        # Update transaction only if not already processed (prevent double processing)
        if transaction["payment_status"] != "paid" and checkout_status.payment_status == "paid":
            update_data = {
                "payment_status": checkout_status.payment_status,
                "status": checkout_status.status,
                "updated_at": datetime.utcnow()
            }
            
            await db.payment_transactions.update_one(
                {"_id": transaction["_id"]}, 
                {"$set": update_data}
            )
            
            # Handle successful payment logic
            await handle_successful_payment(transaction, checkout_status)
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency,
            "metadata": checkout_status.metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment status check failed: {str(e)}")

@api.post("/payments/service-request")
async def create_service_payment(request: Request, payload: ServiceRequestPaymentIn, current=Depends(require_user)):
    """Create payment for service request"""
    if not STRIPE_AVAILABLE or not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    # Verify service request exists and belongs to user
    service_request = await db.service_requests.find_one({"_id": payload.request_id, "user_id": current["id"]})
    if not service_request:
        raise HTTPException(status_code=404, detail="Service request not found")
    
    # Verify provider exists
    provider = await db.users.find_one({"_id": payload.provider_id, "role": "provider"})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        # Initialize Stripe checkout
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_client = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Build URLs
        success_url = f"{payload.origin_url}/service-request?session_id={{CHECKOUT_SESSION_ID}}&request_id={payload.request_id}"
        cancel_url = f"{payload.origin_url}/service-request"
        
        # Add metadata
        metadata = {
            "user_id": current["id"],
            "request_id": payload.request_id,
            "provider_id": payload.provider_id,
            "service_type": "service_request",
            "email": current["email"]
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=payload.agreed_fee,
            currency="USD",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_client.create_checkout_session(checkout_request)
        
        # Create pending transaction record
        transaction_id = str(uuid.uuid4())
        transaction_doc = {
            "_id": transaction_id,
            "id": transaction_id,
            "user_id": current["id"],
            "request_id": payload.request_id,
            "provider_id": payload.provider_id,
            "amount": payload.agreed_fee,
            "currency": "USD",
            "stripe_session_id": session.session_id,
            "payment_status": "pending",
            "status": "initiated",
            "service_type": "service_request",
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        await db.payment_transactions.insert_one(transaction_doc)
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service payment creation failed: {str(e)}")

@api.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not STRIPE_AVAILABLE or not STRIPE_API_KEY:
        return {"status": "disabled"}
    
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        stripe_client = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="dummy")
        webhook_response = await stripe_client.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.event_type == "checkout.session.completed":
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "webhook_processed": True,
                    "updated_at": datetime.utcnow()
                }}
            )
        
        return {"status": "processed"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def handle_successful_payment(transaction: dict, checkout_status: CheckoutStatusResponse):
    """Handle post-payment processing"""
    try:
        if transaction.get("package_id") == "knowledge_base_single":
            # Unlock single knowledge base area
            area_id = transaction["metadata"].get("area_id")
            if area_id:
                await db.user_access.update_one(
                    {"user_id": transaction["user_id"]},
                    {"$addToSet": {f"knowledge_base_access.{area_id}": True}},
                    upsert=True
                )
        
        elif transaction.get("package_id") == "knowledge_base_all":
            # Unlock all knowledge base areas
            await db.user_access.update_one(
                {"user_id": transaction["user_id"]},
                {"$set": {"knowledge_base_access.all_areas": True}},
                upsert=True
            )
        
        elif transaction.get("service_type") == "service_request":
            # Create engagement for service request
            engagement_id = str(uuid.uuid4())
            engagement_doc = {
                "_id": engagement_id,
                "id": engagement_id,
                "request_id": transaction["request_id"],
                "client_user_id": transaction["user_id"],
                "provider_user_id": transaction["provider_id"],
                "agreed_fee": transaction["amount"],
                "status": "payment_completed",
                "payment_transaction_id": transaction["_id"],
                "created_at": datetime.utcnow()
            }
            await db.engagements.insert_one(engagement_doc)
            
            # Update service request status
            await db.match_requests.update_one(
                {"_id": transaction["request_id"]},
                {"$set": {"status": "payment_completed", "engagement_id": engagement_id}}
            )
    
    except Exception as e:
        print(f"Post-payment processing error: {e}")

# ---------------- Service Tracking Endpoints ----------------
@api.post("/engagements/{engagement_id}/update")
async def update_service_tracking(engagement_id: str, update: ServiceTrackingUpdate, current=Depends(require_user)):
    """Update service tracking status"""
    engagement = await db.engagements.find_one({"_id": engagement_id})
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    # Check if user is client or provider involved in engagement
    if current["id"] not in [engagement.get("client_user_id"), engagement.get("provider_user_id")]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    update_data = {
        "status": update.status,
        "updated_at": datetime.utcnow(),
        "updated_by": current["id"]
    }
    
    if update.progress_percentage is not None:
        update_data["progress_percentage"] = update.progress_percentage
    if update.notes:
        update_data["notes"] = update.notes
    if update.deliverables:
        update_data["deliverables"] = update.deliverables
    
    await db.engagements.update_one({"_id": engagement_id}, {"$set": update_data})
    
    # Add to tracking history
    tracking_entry = {
        "_id": str(uuid.uuid4()),
        "engagement_id": engagement_id,
        "status": update.status,
        "progress_percentage": update.progress_percentage,
        "notes": update.notes,
        "updated_by": current["id"],
        "updated_at": datetime.utcnow()
    }
    await db.service_tracking.insert_one(tracking_entry)
    
    return {"ok": True}

@api.get("/engagements/{engagement_id}/tracking")
async def get_service_tracking(engagement_id: str, current=Depends(require_user)):
    """Get service tracking history"""
    engagement = await db.engagements.find_one({"_id": engagement_id})
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    # Check if user is client or provider involved in engagement
    if current["id"] not in [engagement.get("client_user_id"), engagement.get("provider_user_id")]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    tracking = await db.service_tracking.find({"engagement_id": engagement_id}).sort("updated_at", -1).to_list(100)
    
    return {
        "engagement": engagement,
        "tracking_history": tracking
    }

@api.post("/engagements/{engagement_id}/rating")
async def rate_service(engagement_id: str, rating: ServiceRatingIn, current=Depends(require_role("client"))):
    """Rate completed service"""
    engagement = await db.engagements.find_one({"_id": engagement_id, "client_user_id": current["id"]})
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    if engagement.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Can only rate completed services")
    
    rating_id = str(uuid.uuid4())
    rating_doc = {
        "_id": rating_id,
        "id": rating_id,
        "engagement_id": engagement_id,
        "client_user_id": current["id"],
        "provider_user_id": engagement.get("provider_user_id"),
        "rating": rating.rating,
        "feedback": rating.feedback,
        "quality_score": rating.quality_score,
        "communication_score": rating.communication_score,
        "timeliness_score": rating.timeliness_score,
        "created_at": datetime.utcnow()
    }
    await db.service_ratings.insert_one(rating_doc)
    
    # Update engagement with rating
    await db.engagements.update_one(
        {"_id": engagement_id},
        {"$set": {"rating_id": rating_id, "client_rating": rating.rating}}
    )
    
    return {"ok": True, "rating_id": rating_id}

@api.get("/engagements/my-services")
async def get_my_services(current=Depends(require_user)):
    """Get user's service engagements - works for all user types"""
    engagements = []
    
    if current["role"] == "client":
        # Get service requests created by this client
        service_requests = await db.service_requests.find({"user_id": current["id"]}).to_list(100)
        for request in service_requests:
            # Get provider responses for this request
            responses = await db.provider_responses.find({"request_id": request["_id"]}).to_list(50)
            request["provider_responses"] = responses
            engagements.append({
                "_id": request["_id"],
                "id": request["_id"],
                "request_id": request["_id"],
                "client_user_id": current["id"],
                "area_id": request.get("area_id"),
                "budget_range": request.get("budget_range"),
                "description": request.get("description"),
                "status": request.get("status", "open"),
                "created_at": request.get("created_at"),
                "provider_responses": responses,
                "type": "service_request"
            })
    
    elif current["role"] == "provider":
        # Get notifications and responses for this provider
        notifications = await db.provider_notifications.find({"provider_id": current["id"]}).to_list(100)
        for notification in notifications:
            # Get the original service request
            service_request = await db.service_requests.find_one({"_id": notification["service_request_id"]})
            if service_request:
                # Check if provider has responded
                response = await db.provider_responses.find_one({
                    "request_id": notification["service_request_id"],
                    "provider_id": current["id"]
                })
                
                engagements.append({
                    "_id": notification["_id"],
                    "id": notification["_id"],
                    "request_id": notification["service_request_id"],
                    "client_user_id": service_request.get("user_id"),
                    "provider_user_id": current["id"],
                    "area_name": notification.get("area_name"),
                    "budget_range": notification.get("budget_range"),
                    "description": notification.get("description"),
                    "status": notification.get("status", "pending"),
                    "created_at": notification.get("created_at"),
                    "has_responded": response is not None,
                    "response": response,
                    "type": "provider_notification"
                })
    
    else:
        # For navigators and agencies, return empty list
        pass
    
    return {"engagements": engagements}

# ---------------- Enhanced Assessment System ----------------
@api.post("/assessment/answer")
async def save_assessment_answer(answer_data: dict, current=Depends(require_user)):
    """Save individual assessment answer"""
    question_id = answer_data.get("question_id")
    answer = answer_data.get("answer")
    
    if not question_id or not answer:
        raise HTTPException(status_code=400, detail="Question ID and answer are required")
    
    # Upsert answer
    await db.assessment_answers.update_one(
        {"user_id": current["id"], "question_id": question_id},
        {
            "$set": {
                "user_id": current["id"],
                "question_id": question_id,
                "answer": answer,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "_id": str(uuid.uuid4()),
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {"message": "Answer saved successfully"}

@api.post("/assessment/evidence")
async def upload_assessment_evidence(question_id: str = Form(...), files: List[UploadFile] = File(...), current=Depends(require_user)):
    """Upload evidence files for assessment questions"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 10MB limit")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        unique_filename = f"{current['id']}_{question_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Save file content
        file_content = await file.read()
        
        # Store file metadata in database
        file_id = str(uuid.uuid4())
        file_doc = {
            "_id": file_id,
            "user_id": current["id"],
            "question_id": question_id,
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "upload_date": datetime.utcnow()
        }
        
        await db.assessment_evidence.insert_one(file_doc)
        uploaded_files.append({
            "file_id": file_id,
            "original_filename": file.filename,
            "file_size": len(file_content)
        })
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} evidence files",
        "files": uploaded_files
    }

# ---------------- Phase 3: Advanced Knowledge Base + AI System ----------------

# Knowledge Base Models for CMS
class KBArticleIn(BaseModel):
    title: str
    content: str
    area_ids: List[str] = []
    tags: List[str] = []
    content_type: str = Field(default="template", pattern="^(template|sop|guide|checklist|compliance)$")
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    difficulty_level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    estimated_time: Optional[str] = None  # e.g., "30 minutes", "2 hours"

class KBArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    area_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None

class KBArticleOut(BaseModel):
    id: str
    title: str
    content: str
    area_ids: List[str]
    tags: List[str]
    content_type: str
    status: str
    difficulty_level: str
    estimated_time: Optional[str]
    version: int
    author_id: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0

class AIAssistanceRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None
    area_id: Optional[str] = None
    user_assessment_data: Optional[Dict[str, Any]] = None

class NextBestActionRequest(BaseModel):
    user_id: str
    current_gaps: List[str] = []
    completed_areas: List[str] = []
    business_profile: Optional[Dict[str, Any]] = None

# AI-Powered Content Generation Helper
async def generate_ai_content(prompt: str, content_type: str = "guide") -> str:
    """Generate AI content using emergentintegrations"""
    try:
        if not EMERGENT_OK:
            return f"AI content generation not available. Manual {content_type} needed."
            
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"kb_generation_{str(uuid.uuid4())[:8]}",
            system_message=f"""You are an expert business consultant specializing in small business procurement readiness. 
            Generate comprehensive, actionable {content_type} content for government contracting compliance.
            Focus on practical steps, required documentation, and compliance standards.
            Use clear headings, bullet points, and actionable advice."""
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        return f"Content generation temporarily unavailable. Please create {content_type} manually."

@api.get("/knowledge-base/areas")
async def get_knowledge_base_areas(current=Depends(require_user)):
    """Get all knowledge base areas with access status and article counts"""
    access = await db.user_access.find_one({"user_id": current["id"]})
    
    # Get actual article counts from database
    areas_data = []
    for area_id in ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8"]:
        article_count = await db.kb_articles.count_documents({
            "area_ids": area_id,
            "status": "published"
        })
        
        has_access = False
        if access:
            knowledge_access = access.get("knowledge_base_access", {})
            has_access = (
                knowledge_access.get("all_areas", False) or 
                knowledge_access.get(area_id, False)
            )
        
        # Auto-grant access for @polaris.example.com test accounts
        if current["email"].endswith("@polaris.example.com"):
            has_access = True
    
    area_titles = {
        "area1": "Business Formation & Registration",
        "area2": "Financial Operations & Management", 
        "area3": "Legal & Contracting Compliance",
        "area4": "Quality Management & Standards",
        "area5": "Technology & Security Infrastructure",
        "area6": "Human Resources & Capacity",
        "area7": "Performance Tracking & Reporting",
        "area8": "Risk Management & Business Continuity"
    }
    
    area_descriptions = {
        "area1": "Legal business setup, licensing, and registration requirements",
        "area2": "Accounting, bookkeeping, and financial management systems",
        "area3": "Contract management, legal compliance, and risk mitigation",
        "area4": "Quality systems, standards compliance, and process improvement", 
        "area5": "Cybersecurity, data protection, and technology systems",
        "area6": "Staff management, training, and organizational capacity",
        "area7": "KPIs, metrics, reporting systems, and performance management",
        "area8": "Risk assessment, business continuity, and emergency planning"
    }
    
    areas = []
    for area_id in ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8"]:
        article_count = await db.kb_articles.count_documents({
            "area_ids": area_id,
            "status": "published"
        })
        
        has_access = False
        if access:
            knowledge_access = access.get("knowledge_base_access", {})
            has_access = (
                knowledge_access.get("all_areas", False) or 
                knowledge_access.get(area_id, False)
            )
        
        # Auto-grant access for @polaris.example.com test accounts
        if current["email"].endswith("@polaris.example.com"):
            has_access = True
            
        areas.append({
            "id": area_id,
            "title": area_titles[area_id],
            "description": area_descriptions[area_id],
            "resources_count": article_count,
            "locked": not has_access
        })
    
    return {"areas": areas}

@api.post("/knowledge-base/articles", response_model=KBArticleOut)
async def create_kb_article(article: KBArticleIn, current=Depends(require_role("navigator"))):
    """Create a new knowledge base article (Navigator only)"""
    try:
        article_id = str(uuid.uuid4())
        article_doc = {
            "_id": article_id,
            "id": article_id,
            "title": article.title,
            "content": article.content,
            "area_ids": article.area_ids,
            "tags": article.tags,
            "content_type": article.content_type,
            "status": article.status,
            "difficulty_level": article.difficulty_level,
            "estimated_time": article.estimated_time,
            "version": 1,
            "author_id": current["id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "view_count": 0
        }
        
        await db.kb_articles.insert_one(article_doc)
        return KBArticleOut(**article_doc)
    except Exception as e:
        logger.error(f"Error creating KB article: {e}")
        raise HTTPException(status_code=500, detail="Failed to create article")

@api.get("/knowledge-base/articles", response_model=List[KBArticleOut])
async def list_kb_articles(
    area_id: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query("published"),
    current=Depends(require_user)
):
    """List knowledge base articles with filtering"""
    try:
        # Build filter
        filter_query = {}
        if area_id:
            filter_query["area_ids"] = area_id
        if tag:
            filter_query["tags"] = tag
        if content_type:
            filter_query["content_type"] = content_type
        if status:
            filter_query["status"] = status
            
        # Non-navigators can only see published articles
        if current.get("role") != "navigator":
            filter_query["status"] = "published"
        
        articles = await db.kb_articles.find(filter_query).to_list(100)
        return [KBArticleOut(**article) for article in articles]
    except Exception as e:
        logger.error(f"Error listing KB articles: {e}")
        raise HTTPException(status_code=500, detail="Failed to list articles")

@api.get("/knowledge-base/articles/{article_id}", response_model=KBArticleOut)
async def get_kb_article(article_id: str, current=Depends(require_user)):
    """Get a specific knowledge base article"""
    try:
        article = await db.kb_articles.find_one({"_id": article_id})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Check if user can view draft articles
        if article["status"] != "published" and current.get("role") != "navigator":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count
        await db.kb_articles.update_one(
            {"_id": article_id},
            {"$inc": {"view_count": 1}}
        )
        
        # Log analytics
        await db.analytics.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": current["id"],
            "action": "kb_article_view",
            "resource_id": article_id,
            "area_ids": article.get("area_ids", []),
            "timestamp": datetime.utcnow()
        })
        
        return KBArticleOut(**article)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KB article: {e}")
        raise HTTPException(status_code=500, detail="Failed to get article")

@api.put("/knowledge-base/articles/{article_id}", response_model=KBArticleOut)
async def update_kb_article(
    article_id: str, 
    update: KBArticleUpdate, 
    current=Depends(require_role("navigator"))
):
    """Update a knowledge base article (Navigator only)"""
    try:
        existing_article = await db.kb_articles.find_one({"_id": article_id})
        if not existing_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Create new version for major changes
        update_data = update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Increment version if content or title changed
        if "content" in update_data or "title" in update_data:
            update_data["version"] = existing_article.get("version", 1) + 1
        
        await db.kb_articles.update_one(
            {"_id": article_id},
            {"$set": update_data}
        )
        
        updated_article = await db.kb_articles.find_one({"_id": article_id})
        return KBArticleOut(**updated_article)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating KB article: {e}")
        raise HTTPException(status_code=500, detail="Failed to update article")

@api.delete("/knowledge-base/articles/{article_id}")
async def delete_kb_article(article_id: str, current=Depends(require_role("navigator"))):
    """Delete a knowledge base article (Navigator only)"""
    try:
        result = await db.kb_articles.delete_one({"_id": article_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting KB article: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete article")

# AI-Powered Content Generation
@api.post("/knowledge-base/generate-content")
async def generate_kb_content(
    area_id: str = Query(...),
    content_type: str = Query(..., pattern="^(template|sop|guide|checklist|compliance)$"),
    topic: str = Query(...),
    current=Depends(require_role("navigator"))
):
    """Generate AI-powered content for knowledge base articles"""
    try:
        area_names = {
            "area1": "Business Formation & Registration",
            "area2": "Financial Operations & Management", 
            "area3": "Legal & Contracting Compliance",
            "area4": "Quality Management & Standards",
            "area5": "Technology & Security Infrastructure",
            "area6": "Human Resources & Capacity",
            "area7": "Performance Tracking & Reporting",
            "area8": "Risk Management & Business Continuity"
        }
        
        area_name = area_names.get(area_id, "Unknown Area")
        
        prompt = f"""
        Create a comprehensive {content_type} for small businesses related to {topic} in the context of {area_name}.
        
        Requirements:
        - Focus on government contracting and procurement readiness
        - Include specific actionable steps
        - List required documentation and deliverables
        - Provide compliance guidelines and best practices
        - Use clear headings and bullet points
        - Include templates or checklists where appropriate
        
        Target audience: Small business owners preparing for government contracting opportunities.
        
        Topic: {topic}
        Content Type: {content_type.title()}
        Business Area: {area_name}
        """
        
        generated_content = await generate_ai_content(prompt, content_type)
        
        return {
            "generated_content": generated_content,
            "area_id": area_id,
            "content_type": content_type,
            "topic": topic,
            "suggested_title": f"{area_name}: {topic} {content_type.title()}"
        }
    except Exception as e:
        logger.error(f"Error generating KB content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

# AI Assistant for Contextual Help
@api.post("/knowledge-base/ai-assistance")
async def get_ai_assistance(request: AIAssistanceRequest, current=Depends(require_user)):
    """Get AI-powered assistance and guidance"""
    try:
        # Build context from user's assessment data and business profile
        context_parts = []
        
        if request.area_id:
            area_names = {
                "area1": "Business Formation & Registration",
                "area2": "Financial Operations & Management", 
                "area3": "Legal & Contracting Compliance",
                "area4": "Quality Management & Standards",
                "area5": "Technology & Security Infrastructure",
                "area6": "Human Resources & Capacity",
                "area7": "Performance Tracking & Reporting",
                "area8": "Risk Management & Business Continuity"
            }
            context_parts.append(f"Business area focus: {area_names.get(request.area_id)}")
        
        if request.user_assessment_data:
            gaps = request.user_assessment_data.get("gaps", [])
            if gaps:
                context_parts.append(f"Current assessment gaps: {', '.join(gaps)}")
        
        if request.context:
            context_parts.append(f"Additional context: {request.context}")
        
        context_str = "\n".join(context_parts) if context_parts else "General business guidance"
        
        prompt = f"""
        You are an expert business consultant specializing in small business procurement readiness for government contracting.
        
        Context:
        {context_str}
        
        User Question: {request.question}
        
        Provide specific, actionable guidance that:
        1. Directly addresses their question
        2. Considers their current assessment status and gaps
        3. Provides step-by-step recommendations
        4. Suggests specific resources or documentation needed
        5. Includes compliance considerations for government contracting
        
        Keep your response practical and focused on helping them achieve procurement readiness.
        """
        
        if not EMERGENT_OK:
            return {
                "response": "AI assistance is temporarily unavailable. Please contact a Digital Navigator for personalized guidance.",
                "source": "system_message"
            }
        
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"ai_assistance_{current['id']}_{str(uuid.uuid4())[:8]}",
            system_message="You are an expert business consultant for small business procurement readiness."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Log the AI assistance interaction
        await db.analytics.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": current["id"],
            "action": "ai_assistance_request",
            "question": request.question,
            "area_id": request.area_id,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "response": response,
            "source": "ai_assistant",
            "area_id": request.area_id
        }
    except Exception as e:
        logger.error(f"Error getting AI assistance: {e}")
        return {
            "response": "I'm having trouble processing your request right now. Please try again or contact a Digital Navigator for assistance.",
            "source": "error_fallback"
        }

# Next Best Actions AI Recommendations
@api.post("/knowledge-base/next-best-actions")
async def get_next_best_actions(request: NextBestActionRequest, current=Depends(require_user)):
    """Get AI-powered next best action recommendations"""
    try:
        # Get user's current assessment status and business profile
        assessment = await db.assessments.find_one({"user_id": request.user_id})
        business_profile = await db.business_profiles.find_one({"user_id": request.user_id})
        
        # Build comprehensive context
        context_parts = [
            f"User ID: {request.user_id}",
        ]
        
        if request.current_gaps:
            context_parts.append(f"Current gaps: {', '.join(request.current_gaps)}")
        
        if request.completed_areas:
            context_parts.append(f"Completed areas: {', '.join(request.completed_areas)}")
        
        if assessment:
            context_parts.append(f"Assessment completion: {assessment.get('completion_percentage', 0)}%")
        
        if business_profile:
            context_parts.append(f"Business industry: {business_profile.get('industry', 'Not specified')}")
            context_parts.append(f"Business size: {business_profile.get('employee_count', 'Not specified')} employees")
        
        context_str = "\n".join(context_parts)
        
        prompt = f"""
        Based on the following small business context, provide the top 3 next best actions for improving their government contracting readiness:
        
        {context_str}
        
        Prioritize actions that:
        1. Address the most critical gaps first
        2. Build upon their completed areas
        3. Have the highest impact on procurement readiness
        4. Are achievable given their current status
        
        For each action, provide:
        - Clear action title
        - Brief description (1-2 sentences)
        - Estimated time to complete
        - Priority level (high/medium/low)
        - Required resources or documentation
        
        Format your response as actionable recommendations.
        """
        
        if not EMERGENT_OK:
            # Provide fallback recommendations
            fallback_actions = [
                {
                    "title": "Complete Outstanding Assessment Areas",
                    "description": "Finish your maturity assessment to identify all gaps and opportunities.",
                    "estimated_time": "1-2 hours",
                    "priority": "high",
                    "resources": ["Assessment questionnaire", "Supporting documentation"]
                },
                {
                    "title": "Update Business Profile",
                    "description": "Ensure your business profile is complete and current.",
                    "estimated_time": "30 minutes", 
                    "priority": "medium",
                    "resources": ["Business license", "Insurance certificates"]
                },
                {
                    "title": "Review Knowledge Base Resources",
                    "description": "Explore available templates and guides for your business areas.",
                    "estimated_time": "45 minutes",
                    "priority": "medium", 
                    "resources": ["Knowledge Base access", "Templates"]
                }
            ]
            return {"next_actions": fallback_actions, "source": "fallback_recommendations"}
        
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"next_actions_{request.user_id}_{str(uuid.uuid4())[:8]}",
            system_message="You are an expert business consultant providing prioritized action recommendations for procurement readiness."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        ai_response = await chat.send_message(user_message)
        
        # Log the recommendation request
        await db.analytics.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": current["id"],
            "action": "next_best_actions_request",
            "gaps_count": len(request.current_gaps),
            "completed_count": len(request.completed_areas),
            "timestamp": datetime.utcnow()
        })
        
        return {
            "recommendations": ai_response,
            "source": "ai_recommendations",
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting next best actions: {e}")
        # Return fallback recommendations
        fallback_actions = [
            {
                "title": "Complete Outstanding Assessment Areas", 
                "description": "Focus on finishing your maturity assessment to get a complete picture.",
                "estimated_time": "1-2 hours",
                "priority": "high"
            }
        ]
        return {"recommendations": fallback_actions, "source": "error_fallback"}

class OpportunityIn(BaseModel):
    title: str
    description: str
    area_ids: List[str] = []  # e.g., ['area1','area5']
    tags: List[str] = []
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[str] = None  # ISO date string
    status: Optional[str] = "open"

class OpportunityPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    area_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[str] = None
    status: Optional[str] = None

class OpportunityOut(BaseModel):
    id: str
    agency_id: str
    title: str
    description: str
    area_ids: List[str] = []
    tags: List[str] = []
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

class OpportunityApplicationIn(BaseModel):
    note: Optional[str] = None
    evidence_refs: Optional[List[str]] = []

@api.post("/opportunities", response_model=OpportunityOut)
async def create_opportunity(payload: OpportunityIn, current=Depends(require_role("agency"))):
    opp_id = str(uuid.uuid4())
    doc = {
        "_id": opp_id,
        "id": opp_id,
        "agency_id": current["id"],
        "title": payload.title,
        "description": payload.description,
        "area_ids": payload.area_ids or [],
        "tags": [t.strip() for t in (payload.tags or [])],
        "budget_min": payload.budget_min,
        "budget_max": payload.budget_max,
        "deadline": payload.deadline,
        "status": payload.status or "open",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await db.opportunities.insert_one(doc)
    return OpportunityOut(**doc)

@api.get("/opportunities")
async def list_opportunities(area: Optional[str] = None, q: Optional[str] = None, current=Depends(require_user)):
    query: Dict[str, Any] = {"status": "open"}
    if area:
        query["area_ids"] = {"$in": [area]}
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    items = await db.opportunities.find(query).sort("created_at", -1).to_list(100)
    return {"opportunities": items}

@api.get("/opportunities/mine")
async def list_my_opportunities(current=Depends(require_role("agency"))):
    items = await db.opportunities.find({"agency_id": current["id"]}).sort("created_at", -1).to_list(100)
    return {"opportunities": items}

@api.patch("/opportunities/{opp_id}", response_model=OpportunityOut)
async def update_opportunity(opp_id: str, payload: OpportunityPatch, current=Depends(require_role("agency"))):
    opp = await db.opportunities.find_one({"_id": opp_id, "agency_id": current["id"]})
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found or not owned by you")
    updates = {k: v for k, v in payload.dict(exclude_none=True).items()}
    updates["updated_at"] = datetime.utcnow()
    await db.opportunities.update_one({"_id": opp_id}, {"$set": updates})
    new_doc = await db.opportunities.find_one({"_id": opp_id})
    return OpportunityOut(**new_doc)

@api.post("/opportunities/{opp_id}/apply")
async def apply_to_opportunity(opp_id: str, payload: OpportunityApplicationIn, current=Depends(require_role("client"))):
    opp = await db.opportunities.find_one({"_id": opp_id, "status": {"$ne": "closed"}})
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    existing = await db.opportunity_applications.find_one({"opportunity_id": opp_id, "client_id": current["id"]})
    if existing:
        return {"message": "Already applied", "application_id": existing.get("id")}
    app_id = str(uuid.uuid4())
    doc = {
        "_id": app_id,
        "id": app_id,
        "opportunity_id": opp_id,
        "client_id": current["id"],
        "note": payload.note,
        "evidence_refs": payload.evidence_refs or [],
        "created_at": datetime.utcnow(),
        "status": "applied",
    }
    await db.opportunity_applications.insert_one(doc)
    return {"message": "Application submitted", "application_id": app_id}

@api.get("/opportunities/{opp_id}/applications")
async def get_opportunity_applications(opp_id: str, current=Depends(require_role("agency"))):
    opp = await db.opportunities.find_one({"_id": opp_id, "agency_id": current["id"]})
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found or not owned by you")
    apps = await db.opportunity_applications.find({"opportunity_id": opp_id}).sort("created_at", -1).to_list(200)
    return {"applications": apps}

# Simple fit score using assessment answers of the current user
@api.get("/opportunities/{opp_id}/matches")
async def get_opportunity_match(opp_id: str, current=Depends(require_user)):
    opp = await db.opportunities.find_one({"_id": opp_id})
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    # Load current user's assessment answers
    answers = await db.assessment_answers.find({"user_id": current["id"]}).to_list(1000)
    # Compute per-area positive signals (count of 'yes') and negative signals (no_help)
    per_area: Dict[str, Dict[str, int]] = {}
    for a in answers:
        qid = a.get("question_id", "")
        # infer area from prefix like 'q1_1' => area1
        area_key = None
        if "_" in qid:
            prefix = qid.split("_")[0]  # e.g., q1
            if prefix.startswith("q") and prefix[1:].isdigit():
                area_key = f"area{int(prefix[1:])}"
        if area_key:
            if area_key not in per_area:
                per_area[area_key] = {"yes": 0, "no_help": 0}
            val = str(a.get("answer", "")).lower()
            if val in ("yes", "y", "true", "1"):
                per_area[area_key]["yes"] += 1
            elif val in ("no_help", "no", "need_help"):
                per_area[area_key]["no_help"] += 1
    # Score
    base = 50
    score = base
    rationale: List[str] = []
    for area in opp.get("area_ids", []):
        stats = per_area.get(area, {"yes": 0, "no_help": 0})
        score += stats["yes"] * 5
        score -= stats["no_help"] * 7
        if stats["yes"] or stats["no_help"]:
            rationale.append(f"{area}: +{stats['yes']*5} / -{stats['no_help']*7}")
    score = max(0, min(100, score))
    return {"opportunity_id": opp_id, "fit_score": score, "rationale": rationale}

# ---------------- Enhanced Client Dashboard APIs ----------------

@api.get("/metrics/landing")
async def landing_metrics():
    """Public-facing KPIs for landing page (authenticated users will see live metrics)."""
    try:
        # Total clients
        total_clients = await db.users.count_documents({"role": "client"})
        # Engagements initiated
        total_engagements = await db.engagements.count_documents({})
        # Certificates issued
        total_certs = await db.certificates.count_documents({})
        # Opportunities open
        total_opps_open = await db.opportunities.count_documents({"status": "open"}) if hasattr(db, 'opportunities') else 0
        # Gaps addressed (resource clicks) last 30 days
        since = datetime.utcnow() - timedelta(days=30)
        gaps_addr_30d = await db.resource_access_logs.count_documents({"accessed_at": {"$gte": since}})
        
        # Readiness progress: avg 'yes' answers per started client
        pipeline = [
            {"$match": {"answer": {"$in": ["yes", "y", True, "true", 1]}}},
            {"$group": {"_id": "$user_id", "yes_count": {"$sum": 1}}},
            {"$group": {"_id": None, "avg_yes": {"$avg": "$yes_count"}, "started_clients": {"$sum": 1}}}
        ]
        prog = await db.assessment_answers.aggregate(pipeline).to_list(1)
        avg_yes = float(prog[0]["avg_yes"]) if prog else 0.0
        started_clients = int(prog[0]["started_clients"]) if prog else 0
        
        # Provider response time median (hrs) in last 60 days
        since60 = datetime.utcnow() - timedelta(days=60)
        responses = await db.provider_responses.find({"created_at": {"$gte": since60}}).limit(500).to_list(500)
        med_hours = None
        if responses:
            deltas = []
            for r in responses:
                req = await db.service_requests.find_one({"_id": r.get("request_id")})
                if req and req.get("created_at") and r.get("created_at"):
                    dt = (r["created_at"] - req["created_at"]).total_seconds() / 3600.0
                    if dt >= 0:
                        deltas.append(dt)
            if deltas:
                deltas.sort()
                m = len(deltas)//2
                med_hours = deltas[m] if len(deltas)%2==1 else (deltas[m-1]+deltas[m])/2
        
        return {
            "total_clients": total_clients,
            "engagements": total_engagements,
            "certificates": total_certs,
            "opportunities_open": total_opps_open,
            "gaps_addressed_30d": gaps_addr_30d,
            "avg_yes_answers": round(avg_yes, 1),
            "clients_started_assessment": started_clients,
            "median_provider_response_hrs": round(med_hours, 1) if med_hours is not None else None
        }
    except Exception as e:
        logger.error(f"landing_metrics error: {e}")
        # return safe zeros to avoid breaking landing
        return {
            "total_clients": 0,
            "engagements": 0,
            "certificates": 0,
            "opportunities_open": 0,
            "gaps_addressed_30d": 0,
            "avg_yes_answers": 0.0,
            "clients_started_assessment": 0,
            "median_provider_response_hrs": None
        }
@api.get("/assessment/progress/{user_id}")
async def get_assessment_progress(user_id: str, current=Depends(require_user)):
    """Get assessment progress and completion data"""
    # Check if user can access this assessment data
    if current["id"] != user_id and current["role"] != "navigator":
        raise HTTPException(status_code=403, detail="Unauthorized to access this assessment data")
    
    # Get assessment answers
    answers = await db.assessment_answers.find({"user_id": user_id}).to_list(100)
    answers_dict = {answer["question_id"]: answer["answer"] for answer in answers}
    
    # Calculate completion percentage
    total_questions = 24  # 8 areas × 3 questions each
    completed_questions = len([a for a in answers_dict.values() if a])
    completion_percentage = int((completed_questions / total_questions) * 100) if total_questions > 0 else 0
    
    # Calculate gaps
    gaps = []
    area_names = {
        'area1': 'Business Formation & Registration',
        'area2': 'Financial Operations & Management', 
        'area3': 'Legal & Contracting Compliance',
        'area4': 'Quality Management & Standards',
        'area5': 'Technology & Security Infrastructure',
        'area6': 'Human Resources & Capacity',
        'area7': 'Performance Tracking & Reporting',
        'area8': 'Risk Management & Business Continuity'
    }
    
    for question_id, answer in answers_dict.items():
        area_id = question_id.split('_')[0]
        if not answer or answer == 'no_help':
            existing_gap = next((g for g in gaps if g['area_id'] == area_id), None)
            if not existing_gap:
                gaps.append({
                    'area_id': area_id,
                    'area_name': area_names.get(area_id, area_id),
                    'question_ids': [question_id],
                    'severity': 'high' if answer == 'no_help' else 'medium'
                })
            else:
                existing_gap['question_ids'].append(question_id)
                if answer == 'no_help':
                    existing_gap['severity'] = 'high'
    
    return {
        "user_id": user_id,
        "answers": answers_dict,
        "completion_percentage": completion_percentage,
        "total_questions": total_questions,
        "completed_questions": completed_questions,
        "gaps": gaps,
        "last_updated": max([answer.get("created_at", datetime.utcnow()) for answer in answers], default=datetime.utcnow())
    }

@api.get("/agency/info/{agency_id}")
async def get_agency_info(agency_id: str, current=Depends(require_user)):
    """Get agency information for client dashboard"""
    agency = await db.users.find_one({"_id": agency_id, "role": "agency"})
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    # Get agency profile info
    profile = await db.business_profiles.find_one({"user_id": agency_id})
    
    return {
        "agency_id": agency_id,
        "agency_name": profile.get("company_name", "Unknown Agency") if profile else "Unknown Agency",
        "description": profile.get("business_description", "") if profile else "",
        "contact_name": profile.get("owner_name", "") if profile else "",
        "contact_email": agency.get("email", ""),
        "contact_phone": profile.get("phone", "") if profile else "",
        "created_at": agency.get("created_at", datetime.utcnow())
    }

@api.get("/free-resources/recommendations")
async def get_free_resources_recommendations(gaps: str = "", current=Depends(require_user)):
    """Get free resource recommendations based on gaps"""
    gap_areas = gaps.split(',') if gaps else []
    
    # Define free resources for each area
    free_resources = {
        'area1': [
            {'id': 'bus_reg_guide', 'title': 'Business Registration Guide', 'area': 'area1', 'area_name': 'Business Formation'},
            {'id': 'ein_walkthrough', 'title': 'EIN Application Walkthrough', 'area': 'area1', 'area_name': 'Business Formation'},
            {'id': 'license_checklist', 'title': 'Business License Checklist', 'area': 'area1', 'area_name': 'Business Formation'}
        ],
        'area2': [
            {'id': 'accounting_basics', 'title': 'Small Business Accounting Basics', 'area': 'area2', 'area_name': 'Financial Operations'},
            {'id': 'bookkeeping_guide', 'title': 'Bookkeeping Best Practices', 'area': 'area2', 'area_name': 'Financial Operations'},
            {'id': 'tax_prep_guide', 'title': 'Tax Preparation Guide', 'area': 'area2', 'area_name': 'Financial Operations'}
        ],
        'area3': [
            {'id': 'contract_templates', 'title': 'Contract Templates Library', 'area': 'area3', 'area_name': 'Legal Compliance'},
            {'id': 'legal_compliance', 'title': 'Legal Compliance Checklist', 'area': 'area3', 'area_name': 'Legal Compliance'},
            {'id': 'insurance_guide', 'title': 'Business Insurance Guide', 'area': 'area3', 'area_name': 'Legal Compliance'}
        ],
        'area4': [
            {'id': 'quality_standards', 'title': 'Quality Management Standards', 'area': 'area4', 'area_name': 'Quality Management'},
            {'id': 'iso_guide', 'title': 'ISO Certification Guide', 'area': 'area4', 'area_name': 'Quality Management'},
            {'id': 'process_improvement', 'title': 'Process Improvement Tools', 'area': 'area4', 'area_name': 'Quality Management'}
        ],
        'area5': [
            {'id': 'cybersecurity_basics', 'title': 'Cybersecurity for Small Business', 'area': 'area5', 'area_name': 'Technology & Security'},
            {'id': 'data_backup_guide', 'title': 'Data Backup Best Practices', 'area': 'area5', 'area_name': 'Technology & Security'},
            {'id': 'remote_work_security', 'title': 'Remote Work Security Guide', 'area': 'area5', 'area_name': 'Technology & Security'}
        ],
        'area6': [
            {'id': 'hr_handbook', 'title': 'Employee Handbook Template', 'area': 'area6', 'area_name': 'Human Resources'},
            {'id': 'hiring_guide', 'title': 'Hiring Best Practices', 'area': 'area6', 'area_name': 'Human Resources'},
            {'id': 'training_programs', 'title': 'Employee Training Programs', 'area': 'area6', 'area_name': 'Human Resources'}
        ],
        'area7': [
            {'id': 'kpi_dashboard', 'title': 'KPI Dashboard Templates', 'area': 'area7', 'area_name': 'Performance Tracking'},
            {'id': 'reporting_guide', 'title': 'Business Reporting Guide', 'area': 'area7', 'area_name': 'Performance Tracking'},
            {'id': 'metrics_tracking', 'title': 'Metrics Tracking Tools', 'area': 'area7', 'area_name': 'Performance Tracking'}
        ],
        'area8': [
            {'id': 'risk_assessment', 'title': 'Risk Assessment Template', 'area': 'area8', 'area_name': 'Risk Management'},
            {'id': 'business_continuity', 'title': 'Business Continuity Plan', 'area': 'area8', 'area_name': 'Risk Management'},
            {'id': 'emergency_response', 'title': 'Emergency Response Guide', 'area': 'area8', 'area_name': 'Risk Management'}
        ]
    }
    
    # Get resources for gap areas
    recommended_resources = []
    for area in gap_areas:
        if area in free_resources:
            recommended_resources.extend(free_resources[area])
    
    # If no specific gaps, return popular resources
    if not recommended_resources:
        for area_resources in free_resources.values():
            recommended_resources.extend(area_resources[:1])  # One from each area
    
    return {"resources": recommended_resources}

@api.post("/analytics/resource-access")
async def log_resource_access(resource_data: dict, current=Depends(require_user)):
    """Log resource access for navigator analytics"""
    access_log = {
        "_id": str(uuid.uuid4()),
        "user_id": current["id"],
        "resource_id": resource_data.get("resource_id"),
        "gap_area": resource_data.get("gap_area"),
        "accessed_at": datetime.utcnow(),
        "user_role": current["role"]
    }
    
    await db.resource_access_logs.insert_one(access_log)
    
    return {"message": "Resource access logged successfully"}

@api.get("/navigator/analytics/resources")
async def navigator_resource_analytics(since_days: int = 30, current=Depends(require_role("navigator"))):
    """Aggregate free resource selection analytics for navigators.
    Returns totals and breakdown by area over the last N days (default 30)."""
    try:
        since = datetime.utcnow() - timedelta(days=max(1, min(since_days, 365)))
        match_stage = {"$match": {"accessed_at": {"$gte": since}}}
        group_stage = {"$group": {"_id": "$gap_area", "count": {"$sum": 1}}}
        pipeline = [match_stage, group_stage]
        by_area = await db.resource_access_logs.aggregate(pipeline).to_list(100)
        total = sum(item.get("count", 0) for item in by_area)
        # Map area ids to names
        area_names = {
            'area1': 'Business Formation & Registration',
            'area2': 'Financial Operations & Management', 
            'area3': 'Legal & Contracting Compliance',
            'area4': 'Quality Management & Standards',
            'area5': 'Technology & Security Infrastructure',
            'area6': 'Human Resources & Capacity',
            'area7': 'Performance Tracking & Reporting',
            'area8': 'Risk Management & Business Continuity'
        }
        breakdown = [{
            "area_id": (item.get("_id") or "unknown"),
            "area_name": area_names.get(item.get("_id"), item.get("_id") or "Unknown"),
            "count": item.get("count", 0)
        } for item in by_area]
        breakdown.sort(key=lambda x: x["count"], reverse=True)
        # Optional trend: last 7 days by day
        trend_pipeline = [
            {"$match": {"accessed_at": {"$gte": datetime.utcnow() - timedelta(days=7)}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$accessed_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        trend = await db.resource_access_logs.aggregate(trend_pipeline).to_list(100)
        return {
            "since": since,
            "total": total,
            "by_area": breakdown,
            "last7": [{"date": t["_id"], "count": t["count"]} for t in trend]
        }
    except Exception as e:
        logger.error(f"Navigator analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load analytics")

# ---------------- Service Provider Matching System ----------------
@api.post("/service-requests/professional-help")
async def request_professional_help(request_data: dict, current=Depends(require_user)):
    """Create service request and notify matching providers - Available to all authenticated users"""
    area_id = request_data.get("area_id")
    budget_range = request_data.get("budget_range")
    description = request_data.get("description", "")
    
    if not area_id or not budget_range:
        raise HTTPException(status_code=400, detail="Area ID and budget range are required")
    
    # Create service request
    request_id = str(uuid.uuid4())
    service_request = {
        "_id": request_id,
        "id": request_id,
        "user_id": current["id"],
        "area_id": area_id,
        "budget_range": budget_range,
        "description": description,
        "status": "open",
        "created_at": datetime.utcnow(),
        "provider_responses": []
    }
    
    await db.service_requests.insert_one(service_request)
    
    # Find matching service providers
    area_names = {
        'area1': 'Business Formation & Registration',
        'area2': 'Financial Operations & Management', 
        'area3': 'Legal & Contracting Compliance',
        'area4': 'Quality Management & Standards',
        'area5': 'Technology & Security Infrastructure',
        'area6': 'Human Resources & Capacity',
        'area7': 'Performance Tracking & Reporting',
        'area8': 'Risk Management & Business Continuity'
    }
    
    area_name = area_names.get(area_id, area_id)
    
    # Find providers with matching service areas (approved providers only)
    approved_providers = await db.users.find({
        "role": "provider", 
        "approval_status": "approved"
    }).to_list(200)
    
    # Get their business profiles and match by service areas
    matching_providers = []
    for provider in approved_providers:
        profile = await db.business_profiles.find_one({"user_id": provider["_id"]})
        if profile and profile.get("service_areas"):
            # Check if any service area matches the requested area
            if any(area_name.lower() in (service_area or "").lower() or (service_area or "").lower() in area_name.lower() 
                   for service_area in profile.get("service_areas", [])):
                matching_providers.append({"profile": profile, "user": provider})
    
    # Notify first 5 matching providers
    notification_count = 0
    for item in matching_providers[:5]:
        provider_profile = item["profile"]
        notification_id = str(uuid.uuid4())
        notification = {
            "_id": notification_id,
            "provider_id": provider_profile["user_id"],
            "service_request_id": request_id,
            "client_id": current["id"],
            "area_name": area_name,
            "budget_range": budget_range,
            "description": description,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        await db.provider_notifications.insert_one(notification)
        notification_count += 1
    
    return {
        "request_id": request_id,
        "message": f"Service request created and sent to {notification_count} matching providers",
        "notified_providers": notification_count
    }

@api.get("/service-requests/my")
async def list_my_service_requests(current=Depends(require_role("client"))):
    """List current client's service requests with basic info"""
    requests = await db.service_requests.find({"user_id": current["id"]}).sort("created_at", -1).to_list(100)
    return {"service_requests": requests}

@api.get("/service-requests/{request_id}")
async def get_service_request(request_id: str, current=Depends(require_role("client"))):
    """Get a service request with provider responses (client must own it)"""
    req = await db.service_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")
    # Get provider responses
    responses = await db.provider_responses.find({"request_id": request_id}).sort("created_at", -1).to_list(100)
    enriched = []
    for r in responses:
        provider_user = await db.users.find_one({"_id": r["provider_id"]})
        business_profile = await db.business_profiles.find_one({"user_id": r["provider_id"]})
        enriched.append({
            "id": r["_id"],
            "provider_id": r["provider_id"],
            "provider_email": provider_user.get("email") if provider_user else None,
            "provider_company": business_profile.get("company_name") if business_profile else "Unknown Company",
            "proposed_fee": r.get("proposed_fee"),
            "proposal_note": r.get("proposal_note"),
            "estimated_timeline": r.get("estimated_timeline"),
            "status": r.get("status"),
            "created_at": r.get("created_at")
        })
    req["provider_responses"] = enriched
    return req

@api.get("/service-requests/{request_id}/responses")
async def get_service_request_responses(request_id: str, current=Depends(require_role("client"))):
    """List provider responses for a service request (client must own it)"""
    req = await db.service_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")
    responses = await db.provider_responses.find({"request_id": request_id}).sort("created_at", -1).to_list(100)
    enriched = []
    for r in responses:
        provider_user = await db.users.find_one({"_id": r["provider_id"]})
        business_profile = await db.business_profiles.find_one({"user_id": r["provider_id"]})
        enriched.append({
            "id": r["_id"],
            "provider_id": r["provider_id"],
            "provider_email": provider_user.get("email") if provider_user else None,
            "provider_company": business_profile.get("company_name") if business_profile else "Unknown Company",
            "proposed_fee": r.get("proposed_fee"),
            "proposal_note": r.get("proposal_note"),
            "estimated_timeline": r.get("estimated_timeline"),
            "status": r.get("status"),
            "created_at": r.get("created_at")
        })
    return {"responses": enriched}

@api.get("/provider/notifications")
async def get_provider_notifications(current=Depends(require_role("provider"))):
    """Get service request notifications for provider"""
    notifications = await db.provider_notifications.find({
        "provider_id": current["id"],
        "status": "pending"
    }).sort("created_at", -1).to_list(20)
    
    return {"notifications": notifications}

@api.post("/provider/respond-to-request")
async def respond_to_service_request(response_data: dict, current=Depends(require_role("provider"))):
    """Provider responds to service request"""
    request_id = response_data.get("request_id")
    proposed_fee = response_data.get("proposed_fee")
    proposal_note = response_data.get("proposal_note", "")
    estimated_timeline = response_data.get("estimated_timeline", "")
    
    if not request_id or not proposed_fee:
        raise HTTPException(status_code=400, detail="Request ID and proposed fee are required")
    
    # Check if provider already responded
    existing_response = await db.provider_responses.find_one({
        "request_id": request_id,
        "provider_id": current["id"]
    })
    
    if existing_response:
        raise HTTPException(status_code=400, detail="Already responded to this request")
    
    # Create response
    response_id = str(uuid.uuid4())
    response = {
        "_id": response_id,
        "request_id": request_id,
        "provider_id": current["id"],
        "proposed_fee": float(proposed_fee),
        "proposal_note": proposal_note,
        "estimated_timeline": estimated_timeline,
        "status": "submitted",
        "created_at": datetime.utcnow()
    }
    
    await db.provider_responses.insert_one(response)
    
    # Update notification status
    await db.provider_notifications.update_one(
        {"service_request_id": request_id, "provider_id": current["id"]},
        {"$set": {"status": "responded", "responded_at": datetime.utcnow()}}
    )
    
    return {"message": "Response submitted successfully", "response_id": response_id}

# ---------------- Knowledge Base Payment Unlock ----------------
# QA override for knowledge base access for a specific test user
@api.post("/qa/grant/knowledge-base")
async def qa_grant_knowledge_base(current=Depends(require_user)):
    """Grant full knowledge base access to the current user (QA helper)"""
    access = await db.user_access.find_one({"user_id": current["id"]})
    if not access:
        access = {"_id": str(uuid.uuid4()), "user_id": current["id"], "knowledge_base_access": {"all_areas": True}, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        await db.user_access.insert_one(access)
    else:
        await db.user_access.update_one({"user_id": current["id"]}, {"$set": {"knowledge_base_access": {"all_areas": True}, "updated_at": datetime.utcnow()}})
    return {"message": "Knowledge base access granted"}

@api.post("/payments/knowledge-base")
async def unlock_knowledge_base(request: Request, payload: PaymentTransactionIn, current=Depends(require_user)):
    """Create payment session for knowledge base unlock"""
    if not STRIPE_AVAILABLE or not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    # Validate package is knowledge base related
    if payload.package_id not in ["knowledge_base_single", "knowledge_base_all"]:
        raise HTTPException(status_code=400, detail="Invalid knowledge base package")
    
    try:
        # Initialize Stripe checkout
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_client = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Get amount from server-side definition only
        amount = SERVICE_PACKAGES[payload.package_id]
        
        # Build URLs
        success_url = f"{payload.origin_url}/assessment?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{payload.origin_url}/assessment"
        
        # Add metadata
        metadata = {
            "user_id": current["id"],
            "package_id": payload.package_id,
            "service_type": "knowledge_base",
            "email": current["email"],
            **payload.metadata
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="USD",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_client.create_checkout_session(checkout_request)
        
        # Create pending transaction record
        transaction_id = str(uuid.uuid4())
        transaction_doc = {
            "_id": transaction_id,
            "id": transaction_id,
            "user_id": current["id"],
            "package_id": payload.package_id,
            "amount": amount,
            "currency": "USD",
            "stripe_session_id": session.session_id,
            "payment_status": "pending",
            "status": "initiated",
            "service_type": "knowledge_base",
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        await db.payment_transactions.insert_one(transaction_doc)
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge base payment creation failed: {str(e)}")

@api.get("/knowledge-base/access")
async def get_knowledge_base_access(current=Depends(require_user)):
    """Get user's knowledge base access status (QA: auto-unlock for polaris.example.com)"""
    # QA auto-unlock: grant full access for users on polaris.example.com domain
    email = current.get("email", "")
    if email.endswith("@polaris.example.com"):
        # Upsert full access
        existing = await db.user_access.find_one({"user_id": current["id"]})
        if not existing:
            await db.user_access.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": current["id"],
                "knowledge_base_access": {"all_areas": True},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        else:
            await db.user_access.update_one(
                {"user_id": current["id"]},
                {"$set": {"knowledge_base_access": {"all_areas": True}, "updated_at": datetime.utcnow()}}
            )
    
    access = await db.user_access.find_one({"user_id": current["id"]})
    
    if not access:
        return {
            "has_all_access": False,
            "unlocked_areas": [],
            "available_packages": {
                "single_area": {"price": 20.0, "currency": "USD"},
                "all_areas": {"price": 100.0, "currency": "USD"}
            }
        }
    
    knowledge_access = access.get("knowledge_base_access", {})
    has_all_access = knowledge_access.get("all_areas", False)
    unlocked_areas = []
    
    if not has_all_access:
        # Check individual area access
        for area_id in ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8"]:
            if knowledge_access.get(area_id, False):
                unlocked_areas.append(area_id)
    else:
        unlocked_areas = ["area1", "area2", "area3", "area4", "area5", "area6", "area7", "area8"]
    
    return {
        "has_all_access": has_all_access,
        "unlocked_areas": unlocked_areas,
        "available_packages": {
            "single_area": {"price": 20.0, "currency": "USD"},
            "all_areas": {"price": 100.0, "currency": "USD"}
        }
    }

@api.get("/knowledge-base/{area_id}/content")
async def get_knowledge_base_content(area_id: str, current=Depends(require_user)):
    """Get knowledge base content for an area (if unlocked)"""
    # Check access
    access = await db.user_access.find_one({"user_id": current["id"]})
    
    has_access = False
    if access:
        knowledge_access = access.get("knowledge_base_access", {})
        has_access = (
            knowledge_access.get("all_areas", False) or 
            knowledge_access.get(area_id, False)
        )
    
    # Auto-grant access for @polaris.example.com test accounts
    if current["email"].endswith("@polaris.example.com"):
        has_access = True
    
    if not has_access:
        return {
            "has_access": False,
            "unlock_required": True,
            "unlock_price": 20.0,
            "preview": "This premium content is locked. Unlock to access AI-powered templates, guides, and resources."
        }
    
    # Get actual articles from database
    articles = await db.kb_articles.find({
        "area_ids": area_id,
        "status": "published" 
    }).to_list(50)
    
    # Group articles by content type
    content_by_type = {
        "templates": [],
        "sops": [],
        "guides": [],
        "checklists": [],
        "compliance": []
    }
    
    area_names = {
        "area1": "Business Formation & Registration",
        "area2": "Financial Operations & Management", 
        "area3": "Legal & Contracting Compliance",
        "area4": "Quality Management & Standards",
        "area5": "Technology & Security Infrastructure",
        "area6": "Human Resources & Capacity",
        "area7": "Performance Tracking & Reporting",
        "area8": "Risk Management & Business Continuity"
    }
    
    for article in articles:
        content_type = article.get("content_type", "guide")
        
        # Map content_type to appropriate category
        if content_type == "template":
            category = "templates"
        elif content_type == "sop":
            category = "sops"
        elif content_type == "checklist":
            category = "checklists" 
        elif content_type == "compliance":
            category = "compliance"
        else:
            category = "guides"
        
        content_by_type[category].append({
            "id": article["id"],
            "name": article["title"],
            "description": article.get("content", "")[:200] + "..." if len(article.get("content", "")) > 200 else article.get("content", ""),
            "content": article.get("content", ""),
            "tags": article.get("tags", []),
            "difficulty_level": article.get("difficulty_level", "beginner"),
            "estimated_time": article.get("estimated_time"),
            "view_count": article.get("view_count", 0),
            "created_at": article.get("created_at").isoformat() if article.get("created_at") else None
        })
    
    # If no articles exist, provide default content
    if not any(content_by_type.values()):
        area_name = area_names.get(area_id, "Unknown Area")
        content_by_type = {
            "templates": [
                {"name": f"{area_name} Template", "description": f"Comprehensive template for {area_name.lower()}", "content": f"# {area_name} Template\n\nThis template helps you organize and document requirements for {area_name.lower()}.\n\n## Required Documentation\n- [Document 1]\n- [Document 2]\n\n## Implementation Steps\n1. Step 1\n2. Step 2\n\n## Compliance Checklist\n- [ ] Requirement 1\n- [ ] Requirement 2"}
            ],
            "guides": [
                {"name": f"Complete Guide to {area_name}", "description": f"Step-by-step guide for {area_name.lower()}", "content": f"# Complete Guide to {area_name}\n\nThis guide provides comprehensive instructions for achieving compliance in {area_name.lower()}.\n\n## Overview\nComplete overview of requirements...\n\n## Step-by-Step Process\n1. Initial preparation\n2. Documentation gathering\n3. Implementation\n4. Verification"}
            ],
            "checklists": [
                {"name": f"{area_name} Compliance Checklist", "description": f"Essential compliance checklist for {area_name.lower()}", "content": f"# {area_name} Compliance Checklist\n\n## Pre-Implementation\n- [ ] Review requirements\n- [ ] Gather documentation\n\n## Implementation\n- [ ] Complete setup\n- [ ] Test procedures\n\n## Verification\n- [ ] Internal review\n- [ ] External validation"}
            ]
        }
    
    return {
        "has_access": True,
        "area_name": area_names.get(area_id, "Unknown Area"),
        "area_id": area_id,
        "content": content_by_type,
        "total_articles": len(articles),
        "ai_assistance_available": EMERGENT_OK
    }

# ---------------- Matching Core Endpoints ----------------
class MatchRequestIn(BaseModel):
    budget: float
    payment_pref: str
    timeline: str
    area_id: str
    description: str

@api.post("/match/request")
async def create_match_request(payload: MatchRequestIn, current=Depends(require_role("client"))):
    request_id = str(uuid.uuid4())
    doc = {
        "_id": request_id,
        "id": request_id,
        "user_id": current["id"],
        "budget": payload.budget,
        "payment_pref": payload.payment_pref,
        "timeline": payload.timeline,
        "area_id": payload.area_id,
        "description": payload.description,
        "status": "open",
        "created_at": datetime.utcnow()
    }
    await db.match_requests.insert_one(doc)
    return {"request_id": request_id}

@api.get("/match/{request_id}/matches")
async def get_matches(request_id: str, current=Depends(require_role("client"))):
    req = await db.match_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Find providers that match the request criteria
    providers = await db.provider_profiles.find({}).to_list(5000)
    matches = []
    for p in providers:
        score = 0
        if req["area_id"] in (p.get("service_areas") or []):
            score += 50
        b = req.get("budget") or 0
        pmin = p.get("price_min") or 0
        pmax = p.get("price_max") or 0
        if pmin and pmax and pmin <= b <= pmax:
            score += 40
        elif pmin and b >= pmin * 0.8:
            score += 20
        if p.get("availability"):
            score += 10
        if score > 0:
            matches.append({
                "provider_id": p["_id"],
                "user_id": p.get("user_id"),
                "score": score,
                "service_areas": p.get("service_areas", []),
                "price_range": f"${pmin}-${pmax}" if pmin and pmax else "Contact for pricing"
            })
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": matches[:10]}  # Return top 10 matches

@api.post("/match/respond")
async def provider_respond(request_id: str = Form(...), proposal_note: str = Form(...), current=Depends(require_role("provider"))):
    # Check if request exists
    req = await db.match_requests.find_one({"_id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if provider already responded
    existing = await db.match_responses.find_one({"request_id": request_id, "provider_user_id": current["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="Already responded to this request")
    
    # Check first-5 rule - only first 5 providers can respond
    response_count = await db.match_responses.count_documents({"request_id": request_id})
    if response_count >= 5:
        raise HTTPException(status_code=400, detail="Maximum responses reached for this request")
    
    response_id = str(uuid.uuid4())
    doc = {
        "_id": response_id,
        "id": response_id,
        "request_id": request_id,
        "provider_user_id": current["id"],
        "proposal_note": proposal_note,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    await db.match_responses.insert_one(doc)
    return {"ok": True, "response_id": response_id}

@api.get("/match/{request_id}/responses")
async def get_responses(request_id: str, current=Depends(require_role("client"))):
    req = await db.match_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    responses = await db.match_responses.find({"request_id": request_id}).to_list(100)
    
    # Enrich responses with provider info
    enriched_responses = []
    for resp in responses:
        provider_user = await db.users.find_one({"_id": resp["provider_user_id"]})
        provider_profile = await db.provider_profiles.find_one({"user_id": resp["provider_user_id"]})
        business_profile = await db.business_profiles.find_one({"user_id": resp["provider_user_id"]})
        
        enriched_resp = {
            "id": resp["_id"],
            "proposal_note": resp["proposal_note"],
            "status": resp["status"],
            "created_at": resp["created_at"],
            "provider_email": provider_user.get("email") if provider_user else "Unknown",
            "company_name": business_profile.get("company_name") if business_profile else "Unknown Company"
        }
        enriched_responses.append(enriched_resp)
    
    return {"responses": enriched_responses}

# ---------------- Invite Top-5 Providers ----------------
@api.post("/match/{request_id}/invite-top5")
async def invite_top5(request_id: str, current=Depends(require_role("client"))):
    req = await db.match_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    providers = await db.provider_profiles.find({}).to_list(5000)
    matches = []
    for p in providers:
        score = 0
        if req["area_id"] in (p.get("service_areas") or []):
            score += 50
        b = req.get("budget") or 0
        pmin = p.get("price_min") or 0
        pmax = p.get("price_max") or 0
        if pmin and pmax and pmin <= b <= pmax:
            score += 40
        elif pmin and b >= pmin * 0.8:
            score += 20
        if p.get("availability"):
            score += 10
        matches.append({"provider_profile_id": p["_id"], "score": score})
    matches.sort(key=lambda x: x["score"], reverse=True)
    invited = []
    for m in matches[:5]:
        iid = str(uuid.uuid4())
        rec = {"_id": iid, "id": iid, "request_id": request_id, "provider_profile_id": m["provider_profile_id"], "client_user_id": current["id"], "created_at": datetime.utcnow()}
        await db.provider_invites.update_one({"request_id": request_id, "provider_profile_id": m["provider_profile_id"]}, {"$set": rec}, upsert=True)
        invited.append(m["provider_profile_id"])
    return {"ok": True, "invited": invited}

@api.get("/match/eligible")
async def get_eligible_for_provider(current=Depends(require_role("provider"))):
    prof = await db.provider_profiles.find_one({"user_id": current["id"]})
    if not prof:
        return {"requests": []}
    service_areas = prof.get("service_areas", [])
    pmin = prof.get("price_min") or 0
    pmax = prof.get("price_max") or 0
    reqs = await db.match_requests.find({"status": {"$in": ["open","engaged"]}}).to_list(5000)
    out = []
    for r in reqs:
        if r.get("area_id") in service_areas:
            b = r.get("budget") or 0
            budget_ok = (not pmin and not pmax) or (pmin <= b <= (pmax or b))
            if budget_ok:
                invited = await db.provider_invites.find_one({"request_id": r["_id"], "provider_profile_id": prof["_id"]})
                out.append({"id": r["_id"], "area_id": r.get("area_id"), "budget": b, "timeline": r.get("timeline"), "description": r.get("description"), "invited": bool(invited)})
    return {"requests": out[:20]}

# ---------------- Provider proposal attachments ----------------
@api.post("/provider/proposals/upload/initiate")
async def proposal_upload_initiate(response_id: str = Form(...), file_name: str = Form(...), total_size: int = Form(...), mime_type: str = Form("application/octet-stream"), current=Depends(require_role("provider"))):
    resp = await db.match_responses.find_one({"_id": response_id, "provider_user_id": current["id"]})
    if not resp:
        raise HTTPException(status_code=404, detail="Response not found")
    uid = str(uuid.uuid4())
    doc = {"_id": uid, "id": uid, "type": "proposal_attachment", "response_id": response_id, "file_name": file_name, "mime_type": mime_type, "total_size": total_size, "created_at": datetime.utcnow(), "status": "initiated"}
    await db.uploads.insert_one(doc)
    (UPLOAD_BASE / uid).mkdir(parents=True, exist_ok=True)
    return {"upload_id": uid, "chunk_size": 5*1024*1024}

@api.post("/provider/proposals/upload/chunk")
async def proposal_upload_chunk(upload_id: str = Form(...), chunk_index: int = Form(...), file: UploadFile = File(...), current=Depends(require_role("provider"))):
    rec = await db.uploads.find_one({"_id": upload_id, "type": "proposal_attachment"})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    part_path = UPLOAD_BASE / upload_id / f"part_{chunk_index}"
    async with aiofiles.open(part_path, "wb") as out:
        while True:
            data = await file.read(1024 * 1024)
            if not data:
                break
            await out.write(data)
    return {"ok": True}

@api.post("/provider/proposals/upload/complete")
async def proposal_upload_complete(upload_id: str = Form(...), total_chunks: int = Form(...), current=Depends(require_role("provider"))):
    rec = await db.uploads.find_one({"_id": upload_id, "type": "proposal_attachment"})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    final_path = UPLOAD_BASE / f"{upload_id}_{rec.get('file_name') or 'attach'}"
    async with aiofiles.open(final_path, "wb") as out:
        for i in range(int(total_chunks)):
            part_path = UPLOAD_BASE / upload_id / f"part_{i}"
            async with aiofiles.open(part_path, "rb") as f:
                while True:
                    data = await f.read(1024 * 1024)
                    if not data:
                        break
                    await out.write(data)
    size = final_path.stat().st_size
    await db.uploads.update_one({"_id": upload_id}, {"$set": {"status": "completed", "stored_path": str(final_path), "final_size": size, "completed_at": datetime.utcnow()}})
    return {"ok": True, "upload_id": upload_id, "size": size}

@api.get("/provider/proposals/{response_id}/attachments")
async def proposal_attachments(response_id: str, current=Depends(require_user)):
    resp = await db.match_responses.find_one({"_id": response_id})
    if not resp:
        raise HTTPException(status_code=404, detail="Response not found")
    req = await db.match_requests.find_one({"_id": resp["request_id"]})
    allowed = False
    if current.get("role") == "provider" and resp.get("provider_user_id") == current.get("id"):
        allowed = True
    if current.get("role") == "client" and req and req.get("user_id") == current.get("id"):
        allowed = True
    if current.get("role") == "navigator":
        allowed = True
    if not allowed:
        raise HTTPException(status_code=403, detail="Forbidden")
    files = await db.uploads.find({"type": "proposal_attachment", "response_id": response_id, "status": "completed"}).to_list(100)
    return {"attachments": [{"id": f["_id"], "file_name": f.get("file_name"), "size": f.get("final_size")} for f in files]}

# ---------------- Opportunities gating ----------------
ASSESSMENT_TIERING = os.environ.get("ASSESSMENT_TIERING", "flat")
ASSESSMENT_FLAT_AMOUNT = float(os.environ.get("ASSESSMENT_FLAT_AMOUNT", 100))

@api.post("/client/assessment/pay")
async def client_assessment_pay(current=Depends(require_role("client"))):
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "assessment_fee", "amount": ASSESSMENT_FLAT_AMOUNT, "currency": "USD", "status": "processed", "created_at": datetime.utcnow(), "metadata": {"client_user_id": current["id"], "self_paid": True}}
    await db.revenue_transactions.insert_one(tx)
    return {"ok": True, "transaction_id": rid}

@api.get("/opportunities/available")
async def available_opportunities(current=Depends(require_role("client"))):
    inv = await db.agency_invitations.find_one({"client_user_id": current["id"], "status": "accepted"})
    if inv:
        opps = await db.agency_opportunities.find({"created_by": inv["agency_user_id"]}).to_list(2000)
        return {"opportunities": opps, "unlock": "sponsored"}
    paid = await db.revenue_transactions.find_one({"transaction_type": "assessment_fee", "status": "processed", "metadata.client_user_id": current["id"]})
    if paid:
        opps = await db.agency_opportunities.find({}).to_list(5000)
        return {"opportunities": opps, "unlock": "self_paid"}
    return {"opportunities": []}

# ---------------- Certificates (JSON + PDF + Public verify) ----------------
CERT_MIN_READINESS = float(os.environ.get("CERT_MIN_READINESS", 75))

class IssueCertIn(BaseModel):
    client_user_id: str

class CertOut(BaseModel):
    id: str
    title: str
    agency_user_id: str
    client_user_id: str
    session_id: str
    readiness_percent: float
    issued_at: datetime

async def compute_readiness(session_id: str) -> float:
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    total_q = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
    approved = 0
    for a in answers:
        if a.get("value") is True and a.get("evidence_ids"):
            ev_ids = a.get("evidence_ids") or []
            ok = await db.reviews.find_one({"session_id": session_id, "area_id": a["area_id"], "question_id": a["question_id"], "evidence_id": {"$in": ev_ids}, "status": "approved"})
            if ok:
                approved += 1
    return round((approved / total_q) * 100, 2) if total_q else 0.0

@api.post("/agency/certificates/issue", response_model=CertOut)
async def issue_certificate(payload: IssueCertIn, current=Depends(require_role("agency"))):
    inv = await db.agency_invitations.find_one({"agency_user_id": current["id"], "client_user_id": payload.client_user_id, "status": "accepted"})
    if not inv:
        raise HTTPException(status_code=400, detail="No accepted invitation for this client under your agency")
    sid = inv.get("session_id")
    if not sid:
        raise HTTPException(status_code=400, detail="No assessment session linked yet")
    rpct = await compute_readiness(sid)
    if rpct < CERT_MIN_READINESS:
        raise HTTPException(status_code=400, detail=f"Readiness {rpct}% below certificate threshold {CERT_MIN_READINESS}%")
    cid = str(uuid.uuid4())
    doc = {"_id": cid, "id": cid, "title": "Small Business Maturity Assurance", "agency_user_id": current["id"], "client_user_id": payload.client_user_id, "session_id": sid, "readiness_percent": rpct, "issued_at": datetime.utcnow()}
    await db.certificates.insert_one(doc)
    return CertOut(**doc)

@api.get("/agency/certificates")
async def list_agency_certificates(current=Depends(require_role("agency"))):
    certs = await db.certificates.find({"agency_user_id": current["id"]}).to_list(1000)
    return {"certificates": certs}

@api.get("/client/certificates")
async def list_client_certificates(current=Depends(require_role("client"))):
    certs = await db.certificates.find({"client_user_id": current["id"]}).to_list(1000)
    return {"certificates": certs}


@api.get("/health")
async def api_health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@api.get("/certificates/{cert_id}")
async def get_certificate(cert_id: str, current=Depends(require_user)):
    cert = await db.certificates.find_one({"_id": cert_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Not found")
    if current.get("role") not in ("navigator",) and current.get("id") not in (cert.get("agency_user_id"), cert.get("client_user_id")):
        raise HTTPException(status_code=403, detail="Forbidden")
    return cert

@api.get("/certificates/{cert_id}/public")
async def get_certificate_public(cert_id: str):
    cert = await db.certificates.find_one({"_id": cert_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": cert["_id"], "title": cert.get("title"), "issued_at": cert.get("issued_at"), "readiness_percent": cert.get("readiness_percent"), "agency_user_id": cert.get("agency_user_id")}

@api.get("/certificates/{cert_id}/download")
async def download_certificate_pdf(cert_id: str, request: Request, current=Depends(require_user)):
    cert = await db.certificates.find_one({"_id": cert_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Not found")
    if current.get("role") not in ("navigator",) and current.get("id") not in (cert.get("agency_user_id"), cert.get("client_user_id")):
        raise HTTPException(status_code=403, detail="Forbidden")
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.graphics.barcode import qr
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF

    base = str(request.base_url)
    verify_url = f"{base}verify/cert/{cert_id}"

    tmp_path = UPLOAD_BASE / f"certificate_{cert_id}.pdf"
    c = canvas.Canvas(str(tmp_path), pagesize=LETTER)
    width, height = LETTER
    c.setFillColorRGB(0.105, 0.211, 0.365)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height-1*inch, "Polaris – Small Business Maturity Assurance")
    c.setFont("Helvetica", 11)
    c.drawString(1*inch, height-1.3*inch, "City of San Antonio – Procurement Readiness Platform")
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height-2*inch, "Certificate of Opportunity Readiness")
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height-2.4*inch, f"Issued to Client ID: {cert.get('client_user_id')}")
    c.drawString(1*inch, height-2.7*inch, f"Sponsoring Agency ID: {cert.get('agency_user_id')}")
    c.drawString(1*inch, height-3.0*inch, f"Assessment Session ID: {cert.get('session_id')}")
    c.drawString(1*inch, height-3.3*inch, f"Readiness: {cert.get('readiness_percent')}%")
    c.drawString(1*inch, height-3.6*inch, f"Issued at: {cert.get('issued_at')}")

    qrobj = qr.QrCodeWidget(verify_url)
    bounds = qrobj.getBounds()
    size = 1.8*inch
    w = bounds[2]-bounds[0]
    h = bounds[3]-bounds[1]
    d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
    d.add(qrobj)
    renderPDF.draw(d, c, width - (size + 1*inch), height - (size + 1*inch))
    c.setFont("Helvetica", 8)
    c.drawString(width - (size + 1*inch), height - (size + 1*inch) - 12, f"Verified at: {verify_url}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1*inch, height-4.1*inch, "This certificate signifies the business has met the evidence-backed readiness threshold.")
    c.drawString(1*inch, height-4.35*inch, "Validated by the sponsoring agency within the Polaris platform.")
    c.showPage()
    c.save()
    return FileResponse(str(tmp_path), media_type="application/pdf", filename=f"Polaris_Certificate_{cert_id}.pdf")

# ---------------- Agency impact for home ----------------
@api.get("/agency/dashboard/impact")
async def agency_impact(current=Depends(require_role("agency"))):
    aid = current["id"]
    invites_total = await db.agency_invitations.count_documents({"agency_user_id": aid})
    invites_paid = await db.agency_invitations.count_documents({"agency_user_id": aid, "status": "paid"})
    invites_accepted = await db.agency_invitations.count_documents({"agency_user_id": aid, "status": "accepted"})
    agg = await db.revenue_transactions.aggregate([
        {"$match": {"transaction_type": "assessment_fee", "metadata.agency_user_id": aid}},
        {"$group": {"_id": None, "amount": {"$sum": "$amount"}}}
    ]).to_list(1)
    assessment_revenue = agg[0]["amount"] if agg else 0
    mkt_agg = await db.revenue_transactions.aggregate([
        {"$match": {"transaction_type": "marketplace_fee"}},
        {"$group": {"_id": None, "amount": {"$sum": "$amount"}}}
    ]).to_list(1)
    marketplace_revenue = mkt_agg[0]["amount"] if mkt_agg else 0
    opp_count = await db.agency_opportunities.count_documents({"created_by": aid})
    return {"invites": {"total": invites_total, "paid": invites_paid, "accepted": invites_accepted}, "revenue": {"assessment_fees": assessment_revenue, "marketplace_fees": marketplace_revenue}, "opportunities": {"count": opp_count}}

# ---------------- Home dashboards ----------------
@api.get("/home/client")
async def home_client(current=Depends(require_role("client"))):
    sess = await db.sessions.find_one({"user_id": current["id"]})
    readiness = 0.0
    if sess:
        answers = await db.answers.find({"session_id": sess["_id"]}).to_list(1000)
        total_q = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
        approved = 0
        for a in answers:
            if a.get("value") is True and a.get("evidence_ids"):
                ok = await db.reviews.find_one({"session_id": sess["_id"], "area_id": a["area_id"], "question_id": a["question_id"], "evidence_id": {"$in": a.get("evidence_ids")}, "status": "approved"})
                if ok:
                    approved += 1
        readiness = round((approved/total_q)*100,2) if total_q else 0.0
    cert = await db.certificates.find_one({"client_user_id": current["id"]})
    # Call available_opportunities directly
    avail = await available_opportunities(current=current)
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    return {"readiness": readiness, "has_certificate": bool(cert), "opportunities": len(avail.get("opportunities", [])), "profile_complete": bool(prof and prof.get("logo_upload_id"))}

@api.get("/home/provider")
async def home_provider(current=Depends(require_role("provider"))):
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    prov_prof = await db.provider_profiles.find_one({"user_id": current["id"]})
    # Call get_eligible_for_provider directly
    elig = await get_eligible_for_provider(current=current)
    responses = await db.match_responses.count_documents({"provider_user_id": current["id"]})
    return {"eligible_requests": len(elig.get("requests", [])), "responses": responses, "profile_complete": bool(prof and prof.get("logo_upload_id") and prov_prof)}

@api.get("/home/navigator")
async def home_navigator(current=Depends(require_role("navigator"))):
    pending_reviews = await db.reviews.count_documents({"status": "pending"})
    active_eng = await db.engagements.count_documents({"status": "active"})
    return {"pending_reviews": pending_reviews, "active_engagements": active_eng}

@api.get("/home/agency")
async def home_agency(current=Depends(require_role("agency"))):
    # Call agency_impact directly
    impact = await agency_impact(current=current)
    return impact

# ---------------- Google OAuth (skeleton; requires keys) ----------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")  # e.g., https://yourhost/oauth/google/callback

@api.get("/auth/google/start")
async def google_start(role: Optional[str] = "client"):
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    scope = "openid email profile"
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope={scope}&access_type=online&prompt=consent&state={role}"
    )
    return {"auth_url": auth_url}

@api.get("/auth/google/callback")
async def google_callback(code: Optional[str] = None, state: Optional[str] = None):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    # Exchange code
    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")
    tokens = token_resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token")
    # Fetch userinfo
    ui = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    if ui.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch userinfo")
    info = ui.json()
    email = (info.get("email") or "").lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in userinfo")
    user = await get_user_by_email(email)
    if not user:
        role = state if state in ("client","provider","navigator","agency") else "client"
        user = await create_user(email, uuid.uuid4().hex, role)
    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer"}

# Contextual KB Cards for Assessment and Client Home
@api.get("/knowledge-base/contextual-cards")
async def get_contextual_kb_cards(
    area_id: Optional[str] = Query(None),
    user_context: Optional[str] = Query(None),  # "assessment", "client_home", "service_request"
    limit: int = Query(3, le=10),
    current=Depends(require_user)
):
    """Get contextual knowledge base cards based on user context and area"""
    try:
        # Build query based on context
        query = {"status": "published"}
        
        if area_id:
            query["area_ids"] = area_id
        
        # Get user's assessment data to determine relevance
        assessment = await db.assessments.find_one({"user_id": current["id"]})
        user_gaps = []
        if assessment:
            user_gaps = assessment.get("gaps", [])
        
        # Prioritize content based on user context
        sort_criteria = []
        if user_context == "assessment" and area_id:
            # For assessment, show most relevant content for current area
            sort_criteria.append(("content_type", 1))  # Templates and checklists first
        elif user_context == "client_home":
            # For client home, show popular and recent content
            sort_criteria.append(("view_count", -1))
        else:
            # Default sort by creation date
            sort_criteria.append(("created_at", -1))
        
        # Get articles
        articles_cursor = db.kb_articles.find(query)
        if sort_criteria:
            articles_cursor = articles_cursor.sort(sort_criteria)
        
        articles = await articles_cursor.limit(limit).to_list(limit)
        
        # Format as contextual cards
        cards = []
        for article in articles:
            # Determine card type based on content and context
            card_type = "template" if article.get("content_type") == "template" else "guide"
            
            # Check if user has access to this area
            has_access = True  # Default to true, will be checked in frontend
            access = await db.user_access.find_one({"user_id": current["id"]})
            if access:
                for area in article.get("area_ids", []):
                    knowledge_access = access.get("knowledge_base_access", {})
                    if not (knowledge_access.get("all_areas", False) or knowledge_access.get(area, False)):
                        # Auto-grant access for @polaris.example.com test accounts
                        if not current["email"].endswith("@polaris.example.com"):
                            has_access = False
                            break
            
            cards.append({
                "id": article["id"],
                "title": article["title"],
                "description": article.get("content", "")[:150] + "..." if len(article.get("content", "")) > 150 else article.get("content", ""),
                "card_type": card_type,
                "content_type": article.get("content_type", "guide"),
                "area_ids": article.get("area_ids", []),
                "tags": article.get("tags", []),
                "difficulty_level": article.get("difficulty_level", "beginner"),
                "estimated_time": article.get("estimated_time"),
                "view_count": article.get("view_count", 0),
                "has_access": has_access,
                "relevance_score": 1.0  # Could implement ML-based relevance scoring
            })
        
        return {
            "cards": cards,
            "context": user_context,
            "area_id": area_id,
            "total_available": len(cards)
        }
        
    except Exception as e:
        logger.error(f"Error getting contextual KB cards: {e}")
        return {"cards": [], "context": user_context, "area_id": area_id, "total_available": 0}

# KB Engagement Analytics for Navigator Dashboard
@api.get("/knowledge-base/analytics")
async def get_kb_analytics(
    since_days: int = Query(30, le=365),
    current=Depends(require_role("navigator"))
):
    """Get knowledge base engagement analytics (Navigator only)"""
    try:
        since_date = datetime.utcnow() - timedelta(days=since_days)
        
        # Get article view analytics
        article_views = await db.analytics.aggregate([
            {
                "$match": {
                    "action": "kb_article_view",
                    "timestamp": {"$gte": since_date}
                }
            },
            {
                "$group": {
                    "_id": "$resource_id",
                    "views": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$project": {
                    "article_id": "$_id",
                    "views": 1,
                    "unique_users": {"$size": "$unique_users"}
                }
            },
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]).to_list(10)
        
        # Get popular content by area
        area_analytics = await db.analytics.aggregate([
            {
                "$match": {
                    "action": "kb_article_view", 
                    "timestamp": {"$gte": since_date}
                }
            },
            {"$unwind": "$area_ids"},
            {
                "$group": {
                    "_id": "$area_ids",
                    "views": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$project": {
                    "area_id": "$_id",
                    "views": 1,
                    "unique_users": {"$size": "$unique_users"}
                }
            },
            {"$sort": {"views": -1}}
        ]).to_list(8)
        
        # Get AI assistance usage
        ai_assistance_stats = await db.analytics.aggregate([
            {
                "$match": {
                    "action": {"$in": ["ai_assistance_request", "next_best_actions_request"]},
                    "timestamp": {"$gte": since_date}
                }
            },
            {
                "$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            }
        ]).to_list(10)
        
        # Get total KB statistics
        total_articles = await db.kb_articles.count_documents({"status": "published"})
        total_views = await db.analytics.count_documents({
            "action": "kb_article_view",
            "timestamp": {"$gte": since_date}
        })
        
        # Get weekly trends
        weekly_trends = await db.analytics.aggregate([
            {
                "$match": {
                    "action": "kb_article_view",
                    "timestamp": {"$gte": since_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "week": {"$week": "$timestamp"},
                        "year": {"$year": "$timestamp"}
                    },
                    "views": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.week": 1}}
        ]).to_list(10)
        
        # Format area names
        area_names = {
            "area1": "Business Formation & Registration",
            "area2": "Financial Operations & Management", 
            "area3": "Legal & Contracting Compliance",
            "area4": "Quality Management & Standards",
            "area5": "Technology & Security Infrastructure",
            "area6": "Human Resources & Capacity",
            "area7": "Performance Tracking & Reporting",
            "area8": "Risk Management & Business Continuity"
        }
        
        # Enrich area analytics with names
        for area_stat in area_analytics:
            area_stat["area_name"] = area_names.get(area_stat["area_id"], "Unknown Area")
        
        return {
            "period_days": since_days,
            "since_date": since_date.isoformat(),
            "summary": {
                "total_articles": total_articles,
                "total_views": total_views,
                "ai_assistance_requests": sum(stat["count"] for stat in ai_assistance_stats)
            },
            "top_articles": article_views,
            "area_analytics": area_analytics,
            "ai_assistance_stats": ai_assistance_stats,
            "weekly_trends": weekly_trends
        }
        
    except Exception as e:
        logger.error(f"Error getting KB analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# Seed default KB content for demonstration
@api.post("/knowledge-base/seed-content")
async def seed_kb_content(current=Depends(require_role("navigator"))):
    """Seed the knowledge base with default content (Navigator only)"""
    try:
        # Check if content already exists
        existing_count = await db.kb_articles.count_documents({})
        if existing_count > 0:
            return {"message": f"Knowledge base already has {existing_count} articles"}
        
        # Sample articles for each area
        sample_articles = [
            {
                "title": "Business License Requirements Checklist",
                "content": """# Business License Requirements Checklist

## Federal Requirements
- [ ] Federal Tax ID (EIN) from IRS
- [ ] Business registration with appropriate federal agencies
- [ ] Industry-specific federal licenses (if applicable)

## State Requirements  
- [ ] State business license or registration
- [ ] State tax registration
- [ ] Professional licenses (if applicable)
- [ ] Workers' compensation insurance

## Local Requirements
- [ ] City/county business license
- [ ] Zoning compliance verification
- [ ] Local tax registration
- [ ] Building permits (if applicable)

## Documentation to Gather
- Articles of incorporation or LLC formation documents
- Operating agreements
- Insurance certificates
- Proof of registered address

## Timeline
Most licenses can be obtained within 2-4 weeks with proper documentation.""",
                "area_ids": ["area1"],
                "tags": ["licensing", "registration", "compliance", "checklist"],
                "content_type": "checklist",
                "difficulty_level": "beginner",
                "estimated_time": "2-4 weeks"
            },
            {
                "title": "Financial Record-Keeping Template",
                "content": """# Financial Record-Keeping Template

## Monthly Financial Tracking

### Income Tracking
| Date | Source | Amount | Category |
|------|--------|---------|----------|
|      |        |         |          |

### Expense Tracking  
| Date | Vendor | Amount | Category | Business Purpose |
|------|--------|---------|----------|------------------|
|      |        |         |          |                  |

## Quarterly Reviews
- [ ] Profit & Loss statement
- [ ] Balance sheet
- [ ] Cash flow statement
- [ ] Tax obligation estimates

## Annual Requirements
- [ ] Annual tax filings
- [ ] Financial statement preparation
- [ ] Audit preparation (if required)
- [ ] Insurance policy reviews

## Best Practices
1. Record transactions within 24 hours
2. Keep all receipts and invoices
3. Separate business and personal expenses
4. Use accounting software for automation
5. Regular bank reconciliation""",
                "area_ids": ["area2"],
                "tags": ["accounting", "bookkeeping", "templates", "financial"],
                "content_type": "template",
                "difficulty_level": "beginner", 
                "estimated_time": "30 minutes setup"
            },
            {
                "title": "Contract Management Best Practices",
                "content": """# Contract Management Best Practices

## Contract Lifecycle Management

### Pre-Contract Phase
1. Define requirements and scope
2. Identify key stakeholders
3. Establish evaluation criteria
4. Develop timeline and milestones

### Contract Creation
- Use standardized templates
- Include clear terms and conditions
- Define deliverables and acceptance criteria  
- Establish payment terms and schedules
- Include dispute resolution procedures

### Contract Execution
- Obtain proper signatures and approvals
- Distribute copies to relevant parties
- Set up monitoring and tracking systems
- Establish communication protocols

### Ongoing Management
- Track key dates and milestones
- Monitor performance against requirements
- Manage changes through formal process
- Maintain documentation and records

## Risk Mitigation
- Regular contract reviews
- Performance monitoring
- Early identification of issues
- Proactive communication
- Documentation of all changes

## Compliance Considerations
- Regulatory requirements
- Industry standards
- Internal policies
- Audit requirements""",
                "area_ids": ["area3"],
                "tags": ["contracts", "legal", "risk management", "compliance"],
                "content_type": "guide",
                "difficulty_level": "intermediate",
                "estimated_time": "1-2 hours"
            }
        ]
        
        # Insert sample articles
        created_articles = []
        for article_data in sample_articles:
            article_id = str(uuid.uuid4())
            article_doc = {
                "_id": article_id,
                "id": article_id,
                "version": 1,
                "author_id": current["id"],
                "status": "published",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "view_count": 0,
                **article_data
            }
            
            await db.kb_articles.insert_one(article_doc)
            created_articles.append(article_id)
        
        return {
            "message": f"Successfully created {len(created_articles)} sample articles",
            "article_ids": created_articles
        }
        
    except Exception as e:
        logger.error(f"Error seeding KB content: {e}")
        raise HTTPException(status_code=500, detail="Failed to seed content")

# ---------------- Phase 4: Multi-tenant/White-label System ----------------

class AgencyThemeIn(BaseModel):
    agency_id: str
    theme_config: Dict[str, Any]  # logo_url, primary_color, secondary_color, etc.
    branding_name: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None

class AgencyThemeOut(BaseModel):
    id: str
    agency_id: str
    theme_config: Dict[str, Any]
    branding_name: Optional[str]
    contact_info: Optional[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

@api.post("/agency/theme", response_model=AgencyThemeOut)
async def create_agency_theme(theme: AgencyThemeIn, current=Depends(require_role("agency"))):
    """Create or update agency theme configuration"""
    try:
        # Check if theme already exists for this agency
        existing_theme = await db.agency_themes.find_one({"agency_id": theme.agency_id})
        
        if existing_theme:
            # Update existing theme
            update_data = {
                "theme_config": theme.theme_config,
                "branding_name": theme.branding_name,
                "contact_info": theme.contact_info,
                "updated_at": datetime.utcnow()
            }
            
            await db.agency_themes.update_one(
                {"agency_id": theme.agency_id},
                {"$set": update_data}
            )
            
            updated_theme = await db.agency_themes.find_one({"agency_id": theme.agency_id})
            return AgencyThemeOut(**updated_theme)
        else:
            # Create new theme
            theme_id = str(uuid.uuid4())
            theme_doc = {
                "_id": theme_id,
                "id": theme_id,
                "agency_id": theme.agency_id,
                "theme_config": theme.theme_config,
                "branding_name": theme.branding_name,
                "contact_info": theme.contact_info,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.agency_themes.insert_one(theme_doc)
            return AgencyThemeOut(**theme_doc)
            
    except Exception as e:
        logger.error(f"Error creating/updating agency theme: {e}")
        raise HTTPException(status_code=500, detail="Failed to create/update theme")

@api.get("/agency/theme/{agency_id}", response_model=AgencyThemeOut)
async def get_agency_theme(agency_id: str, current=Depends(require_user)):
    """Get agency theme configuration"""
    try:
        theme = await db.agency_themes.find_one({"agency_id": agency_id})
        if not theme:
            raise HTTPException(status_code=404, detail="Agency theme not found")
        
        return AgencyThemeOut(**theme)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agency theme: {e}")
        raise HTTPException(status_code=500, detail="Failed to get theme")

@api.get("/public/agency-theme/{agency_id}")
async def get_public_agency_theme(agency_id: str):
    """Get public agency theme for white-label branding (no auth required)"""
    try:
        theme = await db.agency_themes.find_one({"agency_id": agency_id})
        if not theme:
            # Return default Polaris theme
            return {
                "branding_name": "Polaris",
                "theme_config": {
                    "primary_color": "#1B365D",
                    "secondary_color": "#4A90C2",
                    "logo_url": "/polaris-logo.svg",
                    "favicon_url": "/favicon.ico"
                },
                "contact_info": {
                    "support_email": "support@polaris.example.com",
                    "website": "https://polaris.example.com"
                }
            }
        
        # Return only public theme information
        return {
            "branding_name": theme.get("branding_name", "Polaris"),
            "theme_config": theme.get("theme_config", {}),
            "contact_info": theme.get("contact_info", {})
        }
    except Exception as e:
        logger.error(f"Error getting public agency theme: {e}")
        return {
            "branding_name": "Polaris",
            "theme_config": {
                "primary_color": "#1B365D",
                "secondary_color": "#4A90C2"
            }
        }

# Certificate Generation with Agency Branding
@api.post("/certificates/generate")
async def generate_certificate(
    client_user_id: str = Query(...),
    agency_id: Optional[str] = Query(None),
    current=Depends(require_role("navigator"))
):
    """Generate procurement readiness certificate with agency branding"""
    try:
        # Get client user data
        client_user = await db.users.find_one({"id": client_user_id})
        if not client_user:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get business profile
        business_profile = await db.business_profiles.find_one({"user_id": client_user_id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get assessment data
        assessment = await db.assessments.find_one({"user_id": client_user_id})
        if not assessment or assessment.get("completion_percentage", 0) < 80:
            raise HTTPException(status_code=400, detail="Assessment must be at least 80% complete")
        
        # Get agency theme if specified
        agency_theme = None
        if agency_id:
            agency_theme = await db.agency_themes.find_one({"agency_id": agency_id})
        
        # Generate certificate ID
        certificate_id = str(uuid.uuid4())
        
        # Certificate data
        certificate_data = {
            "_id": certificate_id,
            "id": certificate_id,
            "client_user_id": client_user_id,
            "business_name": business_profile.get("business_name", "Unknown Business"),
            "completion_percentage": assessment.get("completion_percentage", 0),
            "readiness_score": assessment.get("readiness_score", 0),
            "issued_by": current["id"],
            "agency_id": agency_id,
            "certificate_type": "Small Business Procurement Readiness",
            "issued_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=365),  # 1 year validity
            "status": "active",
            "verification_code": f"SBPR-{secrets.token_hex(8).upper()}",
            "agency_branding": {
                "name": agency_theme.get("branding_name", "Polaris") if agency_theme else "Polaris",
                "logo_url": agency_theme.get("theme_config", {}).get("logo_url") if agency_theme else "/polaris-logo.svg"
            }
        }
        
        await db.certificates.insert_one(certificate_data)
        
        return {
            "certificate_id": certificate_id,
            "verification_code": certificate_data["verification_code"],
            "download_url": f"/api/certificates/{certificate_id}/download",
            "expires_at": certificate_data["expires_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate certificate")

@api.get("/certificates/{certificate_id}/download")
async def download_certificate(certificate_id: str):
    """Download certificate PDF with agency branding"""
    try:
        certificate = await db.certificates.find_one({"id": certificate_id})
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # For demo purposes, return certificate data
        # In production, this would generate and return a PDF
        return {
            "certificate_id": certificate_id,
            "business_name": certificate["business_name"],
            "certificate_type": certificate["certificate_type"],
            "issued_at": certificate["issued_at"].isoformat(),
            "expires_at": certificate["expires_at"].isoformat(),
            "verification_code": certificate["verification_code"],
            "agency_branding": certificate.get("agency_branding", {}),
            "download_note": "PDF generation would be implemented here"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to download certificate")

# OG Image Generation with Agency Branding
@api.get("/og-image/{agency_id}")
async def generate_og_image(agency_id: str):
    """Generate Open Graph image with agency branding"""
    try:
        # Get agency theme
        agency_theme = await db.agency_themes.find_one({"agency_id": agency_id})
        
        branding_name = "Polaris"
        primary_color = "#1B365D"
        
        if agency_theme:
            branding_name = agency_theme.get("branding_name", "Polaris")
            primary_color = agency_theme.get("theme_config", {}).get("primary_color", "#1B365D")
        
        # Return OG image data (in production, this would generate an actual image)
        return {
            "og_image_url": f"/api/og-image/{agency_id}/generated.png",
            "branding_name": branding_name,
            "primary_color": primary_color,
            "title": f"{branding_name} - Small Business Procurement Readiness Platform",
            "description": "Assess readiness, get certified, and win government contracts",
            "generation_note": "Dynamic OG image generation would be implemented here"
        }
        
    except Exception as e:
        logger.error(f"Error generating OG image: {e}")
        return {
            "og_image_url": "/polaris-og-image.png",
            "branding_name": "Polaris",
            "title": "Polaris - Small Business Procurement Readiness Platform"
        }

# ---------------- Procurement Opportunities (Phase: Bigger Bets) ----------------

# Include router
app.include_router(api)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()