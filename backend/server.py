from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends, Header, Query, Request
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
from functools import wraps
import time

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
    allow_origins=["https://polaris-sbap.preview.emergentagent.com", "http://localhost:3000"],
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

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str
    terms_accepted: bool = False

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
    updated_at: datetime = Field(..., pattern=r"^(client|navigator|provider|agency)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str
    created_at: datetime

async def get_user_by_email(email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email.lower()})

async def create_user(email: str, password: str, role: str) -> dict:
    existing = await get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    uid = str(uuid.uuid4())
    user_doc = {"_id": uid, "id": uid, "email": email.lower(), "password_hash": pbkdf2_sha256.hash(password), "role": role, "created_at": datetime.utcnow()}
    await db.users.insert_one(user_doc)
    return user_doc

async def verify_user(email: str, password: str) -> Optional[dict]:
    user = await get_user_by_email(email)
    if user and pbkdf2_sha256.verify(password, user.get("password_hash", "")):
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

@api.post("/auth/register", response_model=UserOut)
async def register(user: UserRegister):
    if not user.terms_accepted:
        raise HTTPException(status_code=400, detail="Terms of Service must be accepted")
    
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = pbkdf2_sha256.hash(user.password)
    user_id = str(uuid.uuid4())
    
    # Set approval status for providers
    approval_status = "pending" if user.role == "provider" else "approved"
    
    doc = {
        "_id": user_id, 
        "id": user_id, 
        "email": user.email, 
        "password_hash": hashed_pw, 
        "role": user.role,
        "approval_status": approval_status,
        "terms_accepted": user.terms_accepted,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(doc)
    return UserOut(id=doc["id"], email=doc["email"], role=doc["role"], created_at=doc["created_at"])

@api.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    verified_user = await verify_user(user.email, user.password)
    if not verified_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": verified_user["id"]})
    return Token(access_token=access_token)

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
async def oauth_callback(payload: OAuthCallbackIn):
    try:
        # Call Emergent auth API to get user data
        headers = {"X-Session-ID": payload.session_id}
        response = requests.get("https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        oauth_data = response.json()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": oauth_data["email"]})
        
        if existing_user:
            # Update existing user with OAuth data but keep original role
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
        
        # Create JWT access token
        access_token = create_access_token(data={"sub": user_data["id"]})
        
        return OAuthCallbackOut(
            access_token=access_token,
            user_id=user_data["id"],
            email=user_data["email"],
            name=user_data.get("name", ""),
            role=user_data["role"]
        )
        
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Failed to validate OAuth session")
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

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

# ---------------- Minimal Assessment Schema for readiness calc ----------------
ASSESSMENT_SCHEMA: Dict[str, Dict] = {
    "areas": [
        {"id": "area1", "title": "Business Formation & Registration", "questions": [{"id": "q1", "text": "Vendor registration confirmation"}]},
        {"id": "area2", "title": "Financial Operations", "questions": [{"id": "q1", "text": "Accounting system settings screenshot"}]},
        {"id": "area3", "title": "Legal & Contracting", "questions": [{"id": "q1", "text": "Services agreement template"}]},
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

# ---------------- Engagements ----------------
class EngagementCreateIn(BaseModel):
    request_id: str
    response_id: str
    agreed_fee: float

@api.post("/engagements/create")
async def create_engagement(payload: EngagementCreateIn, current=Depends(require_role("client"))):
    resp = await db.match_responses.find_one({"_id": payload.response_id, "request_id": payload.request_id})
    if not resp:
        raise HTTPException(status_code=404, detail="Response not found")
    req = await db.match_requests.find_one({"_id": payload.request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    eid = str(uuid.uuid4())
    doc = {"_id": eid, "id": eid, "request_id": req["_id"], "response_id": resp["_id"], "client_user_id": current["id"], "provider_user_id": resp.get("provider_user_id"), "status": "active", "agreed_fee": payload.agreed_fee, "created_at": datetime.utcnow()}
    await db.engagements.insert_one(doc)
    fee = round(payload.agreed_fee * 0.05, 2)
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "marketplace_fee", "amount": fee, "currency": "USD", "status": "pending", "created_at": datetime.utcnow(), "metadata": {"engagement_id": eid, "request_id": req["_id"], "response_id": resp["_id"], "agreed_fee": payload.agreed_fee, "pct": 0.05}}
    await db.revenue_transactions.insert_one(tx)
    await db.match_requests.update_one({"_id": req["_id"]}, {"$set": {"status": "engaged", "engagement_id": eid}})
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

# Include router and CORS
app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()