# NOTE: This file contains all Polaris backend endpoints. Additions for homepages, business profiles, engagements, top-5 invites, and provider proposal attachments are appended near the end.
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends, Header, Query, Request
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
import aiofiles
from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256

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

app = FastAPI()
api = APIRouter(prefix="/api")

UPLOAD_BASE = ROOT_DIR / "uploads"
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------- Auth Core (omitted unchanged parts for brevity in this header block) ----------------
ALGO = "HS256"
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., pattern=r"^(client|navigator|provider|agency)$")

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

# ---------------- Existing models, schema, assessment, uploads, AI, navigator, provider, matching, agency, revenue, analytics, certificates ----------------
# NOTE: For brevity, we assume the previously-added endpoints in this file remain intact.

# ---------------- New: Business Profiles (client & provider) ----------------
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
    billing_contact_name: Optional[str] = None
    billing_contact_email: Optional[EmailStr] = None
    billing_contact_phone: Optional[str] = None
    payment_methods: List[str]
    subscription_plan: str
    subscription_features: Optional[str] = None
    billing_frequency: str

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

# Business logo uploads (chunked)
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
    # Link to business profile
    await db.business_profiles.update_one({"user_id": current["id"]}, {"$set": {"logo_upload_id": upload_id, "updated_at": datetime.utcnow()}}, upsert=True)
    return {"ok": True, "upload_id": upload_id, "size": size}

# ---------------- New: Engagements lifecycle ----------------
class EngagementCreateIn(BaseModel):
    request_id: str
    response_id: str
    agreed_fee: float

@api.post("/engagements/create")
async def create_engagement(payload: EngagementCreateIn, current=Depends(require_role("client"))):
    # Validate response belongs to request
    resp = await db.match_responses.find_one({"_id": payload.response_id, "request_id": payload.request_id})
    if not resp:
        raise HTTPException(status_code=404, detail="Response not found")
    req = await db.match_requests.find_one({"_id": payload.request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    # Create engagement
    eid = str(uuid.uuid4())
    doc = {"_id": eid, "id": eid, "request_id": req["_id"], "response_id": resp["_id"], "client_user_id": current["id"], "provider_user_id": resp.get("provider_user_id"), "status": "active", "agreed_fee": payload.agreed_fee, "created_at": datetime.utcnow()}
    await db.engagements.insert_one(doc)
    # Book 5% marketplace fee
    fee = round(payload.agreed_fee * 0.05, 2)
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "marketplace_fee", "amount": fee, "currency": "USD", "status": "pending", "created_at": datetime.utcnow(), "metadata": {"engagement_id": eid, "request_id": req["_id"], "response_id": resp["_id"], "agreed_fee": payload.agreed_fee, "pct": 0.05}}
    await db.revenue_transactions.insert_one(tx)
    # Mark request engaged
    await db.match_requests.update_one({"_id": req["_id"]}, {"$set": {"status": "engaged", "engagement_id": eid}})
    return {"ok": True, "engagement_id": eid, "fee": fee}

@api.get("/navigator/engagements")
async def list_engagements(current=Depends(require_role("navigator"))):
    engs = await db.engagements.find({}).to_list(2000)
    return {"engagements": engs}

class EngagementStatusIn(BaseModel):
    status: str  # active | on_hold | completed | cancelled

@api.post("/navigator/engagements/{engagement_id}/status")
async def set_engagement_status(engagement_id: str, payload: EngagementStatusIn, current=Depends(require_role("navigator"))):
    if payload.status not in ("active","on_hold","completed","cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")
    await db.engagements.update_one({"_id": engagement_id}, {"$set": {"status": payload.status, "updated_at": datetime.utcnow()}})
    return {"ok": True}

# ---------------- New: Invite Top-5 providers ----------------
@api.post("/match/{request_id}/invite-top5")
async def invite_top5(request_id: str, current=Depends(require_role("client"))):
    req = await db.match_requests.find_one({"_id": request_id, "user_id": current["id"]})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    # Reuse matching logic
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

# Enhance provider eligible endpoint to mark invited
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

# ---------------- New: Provider proposal attachments (chunked) ----------------
@api.post("/provider/proposals/upload/initiate")
async def proposal_upload_initiate(response_id: str = Form(...), file_name: str = Form(...), total_size: int = Form(...), mime_type: str = Form("application/octet-stream"), current=Depends(require_role("provider"))):
    # validate response belongs to provider
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
    # providers can see theirs; client/navigator can view if related to the request
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

# ---------------- New: Home dashboards endpoints ----------------
@api.get("/home/client")
async def home_client(current=Depends(require_role("client"))):
    # readiness
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
    avail = await available_opportunities.__wrapped__(current=current)  # reuse logic
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    return {"readiness": readiness, "has_certificate": bool(cert), "opportunities": len(avail.get("opportunities", [])), "profile_complete": bool(prof and prof.get("logo_upload_id"))}

@api.get("/home/provider")
async def home_provider(current=Depends(require_role("provider"))):
    prof = await db.business_profiles.find_one({"user_id": current["id"]})
    prov_prof = await db.provider_profiles.find_one({"user_id": current["id"]})
    elig = await get_eligible_for_provider.__wrapped__(current=current)
    responses = await db.match_responses.count_documents({"provider_user_id": current["id"]})
    return {"eligible_requests": len(elig.get("requests", [])), "responses": responses, "profile_complete": bool(prof and prof.get("logo_upload_id") and prov_prof)}

@api.get("/home/navigator")
async def home_navigator(current=Depends(require_role("navigator"))):
    pending_reviews = await db.reviews.count_documents({"status": "pending"})
    active_eng = await db.engagements.count_documents({"status": "active"})
    return {"pending_reviews": pending_reviews, "active_engagements": active_eng}

@api.get("/home/agency")
async def home_agency(current=Depends(require_role("agency"))):
    impact = await agency_impact.__wrapped__(current=current)
    return impact

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