from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
import aiofiles
from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256

# Optional import for AI; guarded usage in handler
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_OK = True
except Exception:
    EMERGENT_OK = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (must use env vars)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# App and router with '/api' prefix
app = FastAPI()
api = APIRouter(prefix="/api")

# Upload directory
UPLOAD_BASE = ROOT_DIR / "uploads"
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------- Auth Utilities ----------
ALGO = "HS256"
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., pattern=r"^(client|navigator|provider)$")

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
    user_doc = {
        "_id": uid,
        "id": uid,
        "email": email.lower(),
        "password_hash": pbkdf2_sha256.hash(password),
        "role": role,
        "created_at": datetime.utcnow(),
    }
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

# ---------- Models ----------
class CreateSessionResp(BaseModel):
    session_id: str
    created_at: datetime

class UploadInitiateReq(BaseModel):
    file_name: str
    total_size: int
    mime_type: Optional[str] = None
    session_id: str
    area_id: str
    question_id: str

class UploadInitiateResp(BaseModel):
    upload_id: str
    chunk_size: int

class UploadCompleteReq(BaseModel):
    upload_id: str
    total_chunks: int

class AnswerItem(BaseModel):
    area_id: str
    question_id: str
    value: Optional[bool] = None
    evidence_ids: Optional[List[str]] = None

class BulkAnswersReq(BaseModel):
    session_id: str
    answers: List[AnswerItem]

class ProgressResp(BaseModel):
    session_id: str
    total_questions: int
    answered: int
    approved_evidence_answers: int
    percent_complete: float

class AIExplainReq(BaseModel):
    session_id: Optional[str] = None
    area_id: str
    question_id: str
    question_text: Optional[str] = None
    context: Optional[Dict] = None
    provider: Optional[str] = None
    model: Optional[str] = None

class AIExplainResp(BaseModel):
    ok: bool
    message: str

class ReviewDecisionReq(BaseModel):
    decision: str  # approved or rejected
    notes: Optional[str] = None

# ---------- Assessment Schema (refined: specific, non-sensitive, non-redundant) ----------
# Each question requests a concrete deliverable for attestation. Avoids sensitive financial data.

def qs(items: List[Dict]) -> List[Dict]:
    # items: list of dicts with keys: id, text, requires
    return [{"id": it["id"], "text": it["text"], "requires_evidence_on_yes": it.get("requires", True)} for it in items]

ASSESSMENT_SCHEMA: Dict[str, Dict] = {
    "areas": [
        {"id": "area1", "title": "Business Formation &amp; Registration", "questions": qs([
            {"id": "q1", "text": "Upload your City/County vendor registration confirmation or screenshot (no PII)."},
            {"id": "q2", "text": "Provide your entity formation certificate or assumed name certificate (redactions allowed)."},
            {"id": "q3", "text": "Upload your current business license/permit list (document listing license names &amp; IDs only)."},
            {"id": "q4", "text": "Provide an Operating Agreement or Governance Policy (signature page acceptable; redact sensitive details)."},
        ])},
        {"id": "area2", "title": "Financial Operations (Non-sensitive)", "questions": qs([
            {"id": "q1", "text": "Upload a screenshot of your accounting system settings page (name &amp; fiscal year, no balances)."},
            {"id": "q2", "text": "Provide your Financial Policies document (spend approvals, reimbursement, card usage)."},
            {"id": "q3", "text": "Provide a sample invoice template with dummy data (no customer info)."},
            {"id": "q4", "text": "Provide a Month-End Close checklist (template)."},
        ])},
        {"id": "area3", "title": "Legal &amp; Contracting", "questions": qs([
            {"id": "q1", "text": "Upload your standard services agreement or terms (template)."},
            {"id": "q2", "text": "Provide your NDA template (mutual or unilateral)."},
            {"id": "q3", "text": "Provide a Contracts Register (list file with contract name, counterparty, term)."},
        ])},
        {"id": "area4", "title": "Technology &amp; Cybersecurity", "questions": qs([
            {"id": "q1", "text": "Provide your Backup Policy or a screenshot of backup schedule (no hostnames)."},
            {"id": "q2", "text": "Provide your MFA Policy or screenshot showing MFA enabled (no usernames/emails)."},
            {"id": "q3", "text": "Provide an Asset Inventory list (categories &amp; counts acceptable)."},
            {"id": "q4", "text": "Provide your Incident Response Plan (latest version)."},
        ])},
        {"id": "area5", "title": "People &amp; HR (Non-sensitive)", "questions": qs([
            {"id": "q1", "text": "Upload the table of contents from your Employee Handbook (PDF page)."},
            {"id": "q2", "text": "Provide your Onboarding checklist template (roles generic)."},
            {"id": "q3", "text": "Provide your EEO/Anti-Discrimination policy statement (1 page)."},
        ])},
        {"id": "area6", "title": "Marketing &amp; Sales Enablement", "questions": qs([
            {"id": "q1", "text": "Provide your Brand Guidelines (logo usage, colors, typography)."},
            {"id": "q2", "text": "Upload a CRM pipeline screenshot with test data (no real customer names)."},
            {"id": "q3", "text": "Provide your proposal template (PDF or DOC template)."},
        ])},
        {"id": "area7", "title": "Procurement &amp; Supply Chain", "questions": qs([
            {"id": "q1", "text": "Provide your approved vendor list (names/categories; no pricing)."},
            {"id": "q2", "text": "Upload your standard PO or subcontract template (if applicable)."},
            {"id": "q3", "text": "Provide your insurance certificate page showing coverage types and dates (no premiums)."},
        ])},
        {"id": "area8", "title": "Quality &amp; Continuous Improvement", "questions": qs([
            {"id": "q1", "text": "Provide a SOP template (one completed example with non-sensitive content acceptable)."},
            {"id": "q2", "text": "Provide your Corrective Action template or log (redacted)."},
            {"id": "q3", "text": "Provide a simple KPI dashboard screenshot (test data acceptable)."},
        ])},
    ]
}

# ---------- Assessment Endpoints ----------
@api.get("/assessment/schema")
async def get_schema(current=Depends(require_user)):
    return ASSESSMENT_SCHEMA

@api.post("/assessment/session", response_model=CreateSessionResp)
async def create_session(current=Depends(require_user)):
    sid = str(uuid.uuid4())
    doc = {"_id": sid, "id": sid, "user_id": current["id"], "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    await db.sessions.insert_one(doc)
    return CreateSessionResp(session_id=sid, created_at=doc["created_at"])

@api.get("/assessment/session/{session_id}")
async def get_session(session_id: str, current=Depends(require_user)):
    s = await db.sessions.find_one({"_id": session_id})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    # Claim orphan session to current user to prevent 403s during evidence removal
    if not s.get("user_id"):
        await db.sessions.update_one({"_id": session_id}, {"$set": {"user_id": current["id"], "updated_at": datetime.utcnow()}})
        s["user_id"] = current["id"]
    if s.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    return {"id": s["_id"], "session_id": s["_id"], "answers": answers}

@api.post("/assessment/answers/bulk")
async def upsert_answers(payload: BulkAnswersReq, current=Depends(require_user)):
    s = await db.sessions.find_one({"_id": payload.session_id})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.get("user_id") not in (None, current.get("id")) and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    now = datetime.utcnow()
    for a in payload.answers:
        existing = await db.answers.find_one({"session_id": payload.session_id, "area_id": a.area_id, "question_id": a.question_id})
        if existing:
            await db.answers.update_one({"_id": existing["_id"]}, {"$set": {"value": a.value, "evidence_ids": a.evidence_ids or [], "updated_at": now}})
        else:
            aid = str(uuid.uuid4())
            await db.answers.insert_one({"_id": aid, "id": aid, "session_id": payload.session_id, "area_id": a.area_id, "question_id": a.question_id, "value": a.value, "evidence_ids": a.evidence_ids or [], "created_at": now, "updated_at": now})
    await db.sessions.update_one({"_id": payload.session_id}, {"$set": {"updated_at": now, "user_id": s.get("user_id") or current.get("id")}})
    return {"ok": True}

@api.get("/assessment/session/{session_id}/progress", response_model=ProgressResp)
async def progress(session_id: str, current=Depends(require_user)):
    s = await db.sessions.find_one({"_id": session_id})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    total_q = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
    answered = sum(1 for a in answers if a.get("value") is not None)
    # Count answers with approved evidence
    approved = 0
    for a in answers:
        if a.get("value") is True and a.get("evidence_ids"):
            # Check if there is at least one approved review for any evidence id
            ev_ids = a.get("evidence_ids") or []
            ok = await db.reviews.find_one({"session_id": session_id, "area_id": a["area_id"], "question_id": a["question_id"], "evidence_id": {"$in": ev_ids}, "status": "approved"})
            if ok:
                approved += 1
    pct = round((approved / total_q) * 100, 2) if total_q else 0.0
    return ProgressResp(session_id=session_id, total_questions=total_q, answered=answered, approved_evidence_answers=approved, percent_complete=pct)

@api.get("/assessment/session/{session_id}/answer/{area_id}/{question_id}/evidence")
async def list_evidence(session_id: str, area_id: str, question_id: str, current=Depends(require_user)):
    s = await db.sessions.find_one({"_id": session_id})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    up_ids = []
    ans = await db.answers.find_one({"session_id": session_id, "area_id": area_id, "question_id": question_id})
    if ans:
        up_ids = ans.get("evidence_ids") or []
    out = []
    for uid in up_ids:
        up = await db.uploads.find_one({"_id": uid})
        if not up:
            continue
        rev = await db.reviews.find_one({"session_id": session_id, "area_id": area_id, "question_id": question_id, "evidence_id": uid}, sort=[("updated_at", -1)])
        out.append({"upload_id": uid, "file_name": up.get("file_name"), "mime_type": up.get("mime_type"), "size": up.get("total_size"), "status": rev.get("status") if rev else "pending"})
    return {"evidence": out}

@api.get("/upload/{upload_id}/download")
async def download_evidence(upload_id: str, current=Depends(require_user)):
    up = await db.uploads.find_one({"_id": upload_id})
    if not up:
        raise HTTPException(status_code=404, detail="Not found")
    s = await db.sessions.find_one({"_id": up["session_id"]})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if current.get("role") not in ("navigator",) and s.get("user_id") != current.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return FileResponse(path=up["stored_path"], filename=up.get("file_name") or "evidence")

@api.delete("/upload/{upload_id}")
async def delete_evidence(upload_id: str, current=Depends(require_user)):
    up = await db.uploads.find_one({"_id": upload_id})
    if not up:
        raise HTTPException(status_code=404, detail="Not found")
    s = await db.sessions.find_one({"_id": up["session_id"]})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    # Claim orphan session if needed
    if not s.get("user_id"):
        await db.sessions.update_one({"_id": s["_id"]}, {"$set": {"user_id": current["id"], "updated_at": datetime.utcnow()}})
        s["user_id"] = current["id"]
    if current.get("role") != "navigator" and s.get("user_id") != current.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Remove file from disk
    try:
        p = Path(up["stored_path"]) if up.get("stored_path") else None
        if p and p.exists():
            p.unlink()
    except Exception:
        logger.warning("Failed to delete file from disk for %s", upload_id)

    # Update DB references
    await db.uploads.delete_one({"_id": upload_id})
    await db.answers.update_many({"session_id": up["session_id"], "area_id": up["area_id"], "question_id": up["question_id"]}, {"$pull": {"evidence_ids": upload_id}})
    await db.reviews.update_many({"session_id": up["session_id"], "area_id": up["area_id"], "question_id": up["question_id"], "evidence_id": upload_id}, {"$set": {"status": "deleted", "updated_at": datetime.utcnow()}})
    return {"ok": True}

# ---------- Chunked Uploads ----------
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB

@api.post("/upload/initiate", response_model=UploadInitiateResp)
async def upload_initiate(payload: UploadInitiateReq, current=Depends(require_user)):
    s = await db.sessions.find_one({"_id": payload.session_id})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.get("user_id") not in (None, current.get("id")) and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    uid = str(uuid.uuid4())
    doc = {"_id": uid, "id": uid, "session_id": payload.session_id, "area_id": payload.area_id, "question_id": payload.question_id, "file_name": payload.file_name, "mime_type": payload.mime_type, "total_size": payload.total_size, "created_at": datetime.utcnow(), "status": "initiated"}
    await db.uploads.insert_one(doc)
    (UPLOAD_BASE / uid).mkdir(parents=True, exist_ok=True)
    return UploadInitiateResp(upload_id=uid, chunk_size=CHUNK_SIZE)

@api.post("/upload/chunk")
async def upload_chunk(upload_id: str = Form(...), chunk_index: int = Form(...), file: UploadFile = File(...), current=Depends(require_user)):
    rec = await db.uploads.find_one({"_id": upload_id})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    s = await db.sessions.find_one({"_id": rec["session_id"]})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.get("user_id") not in (None, current.get("id")) and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    part_path = UPLOAD_BASE / upload_id / f"part_{chunk_index}"
    async with aiofiles.open(part_path, "wb") as out:
        while True:
            data = await file.read(1024 * 1024)
            if not data:
                break
            await out.write(data)
    return {"ok": True}

@api.post("/upload/complete")
async def upload_complete(req: UploadCompleteReq, current=Depends(require_user)):
    rec = await db.uploads.find_one({"_id": req.upload_id})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    s = await db.sessions.find_one({"_id": rec["session_id"]})
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.get("user_id") not in (None, current.get("id")) and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")

    final_path = UPLOAD_BASE / f"{req.upload_id}_{rec.get('file_name') or 'evidence'}"
    async with aiofiles.open(final_path, "wb") as out:
        for i in range(req.total_chunks):
            part_path = UPLOAD_BASE / req.upload_id / f"part_{i}"
            async with aiofiles.open(part_path, "rb") as f:
                while True:
                    data = await f.read(1024 * 1024)
                    if not data:
                        break
                    await out.write(data)
    size = final_path.stat().st_size
    await db.uploads.update_one({"_id": req.upload_id}, {"$set": {"status": "completed", "stored_path": str(final_path), "final_size": size, "completed_at": datetime.utcnow()}})

    existing = await db.answers.find_one({"session_id": rec["session_id"], "area_id": rec["area_id"], "question_id": rec["question_id"]})
    if existing:
        ev = list(set((existing.get("evidence_ids") or []) + [req.upload_id]))
        await db.answers.update_one({"_id": existing["_id"]}, {"$set": {"evidence_ids": ev, "updated_at": datetime.utcnow()}})
    else:
        did = str(uuid.uuid4())
        await db.answers.insert_one({"_id": did, "id": did, "session_id": rec["session_id"], "area_id": rec["area_id"], "question_id": rec["question_id"], "value": True, "evidence_ids": [req.upload_id], "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()})

    review_id = str(uuid.uuid4())
    rdoc = {"_id": review_id, "id": review_id, "session_id": rec["session_id"], "area_id": rec["area_id"], "question_id": rec["question_id"], "evidence_id": req.upload_id, "status": "pending", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "reviewer_user_id": None, "notes": None}
    await db.reviews.insert_one(rdoc)

    return {"ok": True, "upload_id": req.upload_id, "size": size, "review_id": review_id}

# ---------- AI Deliverables (auth gated) ----------
@api.post("/ai/explain", response_model=AIExplainResp)
async def ai_explain(req: AIExplainReq, current=Depends(require_user)):
    # Repurposed: return deliverables and brief importance (concise)
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        return AIExplainResp(ok=False, message="AI key missing. Please set EMERGENT_LLM_KEY in backend/.env and restart backend.")
    if not EMERGENT_OK:
        return AIExplainResp(ok=False, message="AI library not installed. Please install emergentintegrations.")
    provider = (req.provider or "openai").lower()
    model = req.model or "gpt-4o-mini"
    system_message = (
        "You are a procurement readiness coach. Respond concisely. "
        "Output three parts in plain text: "
        "1) Deliverables: bullet list (max 3) naming specific documents/templates/screenshots that satisfy the requirement (non-sensitive). "
        "2) Acceptable alternatives: bullet list (1-2) suggesting pragmatic substitutes if the ideal document is unavailable (keep non-sensitive). "
        "3) Why it matters: one short sentence tying to opportunity readiness. Avoid asking for financial statements or PII."
    )
    chat = LlmChat(api_key=llm_key, session_id=req.session_id or str(uuid.uuid4()), system_message=system_message).with_model(provider, model)
    qtext = req.question_text or ""
    prompt = (
        f"Area: {req.area_id}\nQuestion: {req.question_id} {qtext}\n"
        f"Context: {req.context or {}}\n"
        "Return format strictly as:\n"
        "- Deliverables:\n  - <up to 3 bullets>\n"
        "- Acceptable alternatives:\n  - <1-2 bullets>\n"
        "- Why it matters: <1 sentence>"
    )
    try:
        response = await chat.send_message(UserMessage(text=prompt))
        return AIExplainResp(ok=True, message=str(response))
    except Exception as e:
        logger.exception("AI call failed")
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

# ---------- Navigator Review &amp; Matching (unchanged from previous refined version) ----------
@api.get("/navigator/reviews")
async def get_reviews(status: str = Query("pending"), current=Depends(require_role("navigator"))):
    q = {"status": status}
    reviews = await db.reviews.find(q).to_list(2000)
    text_by_key = {(area["id"], qobj["id"]): {"area": area["title"], "question": qobj["text"]} for area in ASSESSMENT_SCHEMA["areas"] for qobj in area["questions"]}
    results = []
    for r in reviews:
        up = await db.uploads.find_one({"_id": r["evidence_id"]})
        meta = text_by_key.get((r["area_id"], r["question_id"]))
        results.append({
            "id": r["_id"],
            "session_id": r["session_id"],
            "area_id": r["area_id"],
            "question_id": r["question_id"],
            "file_name": up.get("file_name") if up else None,
            "status": r.get("status"),
            "notes": r.get("notes"),
            "area_title": meta.get("area") if meta else r.get("area_id"),
            "question_text": meta.get("question") if meta else r.get("question_id"),
            "created_at": r.get("created_at"),
        })
    return {"reviews": results}

@api.post("/navigator/reviews/{review_id}/decision")
async def review_decision(review_id: str, payload: ReviewDecisionReq, current=Depends(require_role("navigator"))):
    r = await db.reviews.find_one({"_id": review_id})
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid decision")
    await db.reviews.update_one({"_id": review_id}, {"$set": {"status": payload.decision, "notes": payload.notes, "reviewer_user_id": current["id"], "updated_at": datetime.utcnow()}})
    return {"ok": True}

class ProviderProfileIn(BaseModel):
    company_name: str
    service_areas: List[str]
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    availability: Optional[str] = None
    location: Optional[str] = None

class ProviderProfileOut(ProviderProfileIn):
    id: str

class MatchRequestIn(BaseModel):
    budget: float
    payment_pref: Optional[str] = None
    timeline: Optional[str] = None
    area_id: str
    description: Optional[str] = None

@api.get("/provider/profile/me", response_model=Optional[ProviderProfileOut])
async def get_my_profile(current=Depends(require_role("provider"))):
    prof = await db.provider_profiles.find_one({"user_id": current["id"]})
    if not prof:
        return None
    return ProviderProfileOut(
        id=prof["_id"],
        company_name=prof.get("company_name"),
        service_areas=prof.get("service_areas", []),
        price_min=prof.get("price_min"),
        price_max=prof.get("price_max"),
        availability=prof.get("availability"),
        location=prof.get("location"),
    )

@api.post("/provider/profile", response_model=ProviderProfileOut)
async def upsert_profile(payload: ProviderProfileIn, current=Depends(require_role("provider"))):
    existing = await db.provider_profiles.find_one({"user_id": current["id"]})
    now = datetime.utcnow()
    if existing:
        await db.provider_profiles.update_one({"_id": existing["_id"]}, {"$set": {**payload.dict(), "updated_at": now}})
        prof = await db.provider_profiles.find_one({"_id": existing["_id"]})
        prof_id = existing["_id"]
    else:
        prof_id = str(uuid.uuid4())
        doc = {"_id": prof_id, "id": prof_id, "user_id": current["id"], **payload.dict(), "created_at": now, "updated_at": now}
        await db.provider_profiles.insert_one(doc)
        prof = doc
    return ProviderProfileOut(id=prof_id, company_name=prof.get("company_name"), service_areas=prof.get("service_areas", []), price_min=prof.get("price_min"), price_max=prof.get("price_max"), availability=prof.get("availability"), location=prof.get("location"))

@api.post("/match/request")
async def create_match_request(payload: MatchRequestIn, current=Depends(require_role("client"))):
    req_id = str(uuid.uuid4())
    doc = {"_id": req_id, "id": req_id, "user_id": current["id"], "budget": payload.budget, "payment_pref": payload.payment_pref, "timeline": payload.timeline, "area_id": payload.area_id, "description": payload.description, "status": "open", "created_at": datetime.utcnow(), "responses_count": 0}
    await db.match_requests.insert_one(doc)
    return {"request_id": req_id, "ok": True}

@api.get("/match/{request_id}/matches")
async def get_matches(request_id: str, current=Depends(require_user)):
    req = await db.match_requests.find_one({"_id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if current.get("role") != "navigator" and req.get("user_id") != current.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    providers = await db.provider_profiles.find({}).to_list(5000)
    matches = []
    for p in providers:
        score = 0
        if req["area_id"] in (p.get("service_areas") or []):
            score += 50
        b = req.get("budget")
        pmin = p.get("price_min") or 0
        pmax = p.get("price_max") or 0
        if pmin and pmax and pmin <= b <= pmax:
            score += 40
        elif pmin and b &gt;= pmin * 0.8:
            score += 20
        if p.get("availability"):
            score += 10
        matches.append({"provider_id": p["_id"], "company_name": p.get("company_name"), "service_areas": p.get("service_areas", []), "price_min": p.get("price_min"), "price_max": p.get("price_max"), "location": p.get("location"), "score": score})
    matches.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": matches[:10]}

@api.get("/match/eligible")
async def get_eligible_for_provider(current=Depends(require_role("provider"))):
    prof = await db.provider_profiles.find_one({"user_id": current["id"]})
    if not prof:
        return {"requests": []}
    service_areas = prof.get("service_areas", [])
    pmin = prof.get("price_min") or 0
    pmax = prof.get("price_max") or 0
    reqs = await db.match_requests.find({"status": "open"}).to_list(5000)
    out = []
    for r in reqs:
        if r.get("area_id") in service_areas:
            b = r.get("budget") or 0
            budget_ok = (not pmin and not pmax) or (pmin <= b <= (pmax or b))
            if budget_ok:
                out.append({"id": r["_id"], "area_id": r.get("area_id"), "budget": b, "timeline": r.get("timeline"), "description": r.get("description")})
    return {"requests": out[:20]}

@api.post("/match/respond")
async def respond_to_match(request_id: str = Form(...), proposal_note: Optional[str] = Form(None), current=Depends(require_role("provider"))):
    req = await db.match_requests.find_one({"_id": request_id})
    if not req or req.get("status") != "open":
        raise HTTPException(status_code=400, detail="Request not open")
    resp_count = await db.match_responses.count_documents({"request_id": request_id})
    if resp_count &gt;= 5:
        return {"ok": False, "reason": "First-5 responses have already been received"}
    existing = await db.match_responses.find_one({"request_id": request_id, "provider_user_id": current["id"]})
    if existing:
        return {"ok": True, "message": "Already responded"}
    rid = str(uuid.uuid4())
    rdoc = {"_id": rid, "id": rid, "request_id": request_id, "provider_user_id": current["id"], "proposal_note": proposal_note, "created_at": datetime.utcnow()}
    await db.match_responses.insert_one(rdoc)
    await db.match_requests.update_one({"_id": request_id}, {"$set": {"responses_count": resp_count + 1}})
    return {"ok": True, "response_id": rid}

@api.get("/match/{request_id}/responses")
async def list_responses(request_id: str, current=Depends(require_user)):
    req = await db.match_requests.find_one({"_id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if current.get("role") != "navigator" and req.get("user_id") != current.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    resps = await db.match_responses.find({"request_id": request_id}).to_list(100)
    return {"responses": resps}

# Include router
app.include_router(api)

# CORS
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