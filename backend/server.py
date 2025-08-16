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

# ---------- Assessment Schema (kept generic, not branded as SBAP) ----------

def mkqs(prefix: str, items: List[str]) -> List[Dict]:
    qs = []
    for i, text in enumerate(items, start=1):
        qs.append({"id": f"q{i}", "text": text, "requires_evidence_on_yes": True if i in (1,2,3,5,7,9) else False})
    return qs

ASSESSMENT_SCHEMA: Dict[str, Dict] = {
    "areas": [
        {"id": "area1", "title": "Business Operations", "questions": mkqs("ops", [
            "Do you maintain a documented strategic plan?",
            "Are standard operating procedures (SOPs) documented?",
            "Do you track KPIs for operations?",
            "Is there a documented risk register?",
            "Do you conduct quarterly review meetings?",
            "Do you have defined procurement processes?",
            "Are roles/responsibilities documented?",
            "Is there business continuity documentation?",
            "Do you manage vendor performance with SLAs?",
            "Do you maintain versioned policies?",
        ])},
        {"id": "area2", "title": "Financial Management", "questions": mkqs("fin", [
            "Is an accounting system (e.g., QuickBooks) implemented?",
            "Do you produce monthly financial statements?",
            "Are taxes current and filed on time?",
            "Is there a cash flow forecast updated monthly?",
            "Do you perform monthly reconciliations?",
            "Do you have spend controls/approvals?",
            "Is there a documented budgeting process?",
            "Do you maintain AR/AP aging reports?",
            "Is payroll compliant and timely?",
            "Are financial policies documented?",
        ])},
        {"id": "area3", "title": "Legal and Compliance", "questions": mkqs("legal", [
            "Is your business legally registered in the relevant jurisdictions?",
            "Do you have all required licenses and permits?",
            "Are contracts centrally stored and reviewed?",
            "Are NDAs/MSAs standard templates in use?",
            "Is IP registered/managed where applicable?",
            "Is there a compliance calendar?",
            "Is records retention policy implemented?",
            "Are regulatory filings tracked?",
            "Is whistleblower policy documented?",
            "Do you conduct annual compliance training?",
        ])},
        {"id": "area4", "title": "Technology and Cybersecurity", "questions": mkqs("tech", [
            "Are backups configured and tested?",
            "Is antivirus/EDR deployed across devices?",
            "Is your website up to date and secure (HTTPS)?",
            "Are admin accounts protected with MFA?",
            "Is there a patch management process?",
            "Are access controls role-based?",
            "Is incident response plan documented?",
            "Is vendor security reviewed?",
            "Are logs monitored centrally?",
            "Is data encrypted at rest?",
        ])},
        {"id": "area5", "title": "Human Resources", "questions": mkqs("hr", [
            "Do you have an employee handbook?",
            "Is payroll system set up and compliant?",
            "Are role descriptions maintained?",
            "Are onboarding/offboarding checklists used?",
            "Is EEO policy implemented?",
            "Are benefits documented and administered?",
            "Are training records tracked?",
            "Is workplace safety policy documented?",
            "Is time-off policy enforced consistently?",
            "Do you maintain signed policy acknowledgements?",
        ])},
        {"id": "area6", "title": "Marketing and Sales", "questions": mkqs("mkt", [
            "Do you have a documented marketing plan?",
            "Are there defined customer acquisition channels?",
            "Do you track marketing KPIs?",
            "Is CRM in place and used consistently?",
            "Is website content current and accurate?",
            "Do you maintain case studies/testimonials?",
            "Is pricing strategy documented?",
            "Is pipeline reviewed weekly?",
            "Are proposals templated and versioned?",
            "Is brand identity documented and enforced?",
        ])},
        {"id": "area7", "title": "Supply Chain Management", "questions": mkqs("scm", [
            "Do you have vetted supplier list?",
            "Are supplier contracts maintained?",
            "Do you track delivery SLAs?",
            "Is inventory management system in place?",
            "Is demand planning performed?",
            "Are supplier risks tracked?",
            "Is returns/RMA process documented?",
            "Are logistics KPIs reported?",
            "Is quality at intake measured?",
            "Are alternative suppliers identified?",
        ])},
        {"id": "area8", "title": "Quality Assurance", "questions": mkqs("qa", [
            "Is quality policy documented?",
            "Are QC checklists used?",
            "Are corrective actions tracked?",
            "Is customer feedback incorporated?",
            "Are processes audited periodically?",
            "Is continuous improvement plan in place?",
            "Are standards (e.g., ISO) referenced?",
            "Are test records retained?",
            "Is defect rate tracked?",
            "Are suppliers audited for quality?",
        ])},
    ]
}

# ---------- Basic Routes ----------
@api.get("/")
async def root():
    return {"message": "Hello from Polaris"}

# ---------- Auth Routes ----------
@api.post("/auth/register", response_model=UserOut)
async def register(payload: UserRegister):
    user = await create_user(payload.email, payload.password, payload.role)
    return UserOut(id=user["id"], email=user["email"], role=user["role"], created_at=user["created_at"])

@api.post("/auth/login", response_model=Token)
async def login(payload: UserLogin):
    user = await verify_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return Token(access_token=token)

@api.get("/auth/me", response_model=UserOut)
async def me(current=Depends(require_user)):
    return UserOut(id=current["id"], email=current["email"], role=current["role"], created_at=current["created_at"])

# ---------- Assessment Routes (Auth required) ----------
@api.get("/assessment/schema")
async def get_schema(current=Depends(require_user)):
    return ASSESSMENT_SCHEMA

@api.post("/assessment/session", response_model=CreateSessionResp)
async def create_session(current=Depends(require_user)):
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    doc = {"_id": session_id, "id": session_id, "created_at": now, "status": "active", "user_id": current["id"]}
    await db.sessions.insert_one(doc)
    return CreateSessionResp(session_id=session_id, created_at=now)

@api.get("/assessment/session/{session_id}")
async def get_session(session_id: str, current=Depends(require_user)):
    sess = await db.sessions.find_one({"_id": session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    # Claim orphan session to authenticated user (MVP fix)
    if not sess.get("user_id"):
        await db.sessions.update_one({"_id": session_id}, {"$set": {"user_id": current["id"], "claimed_at": datetime.utcnow()}})
        sess = await db.sessions.find_one({"_id": session_id})
    if sess.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    return {"session": sess, "answers": answers}

@api.post("/assessment/answers/bulk")
async def save_answers(payload: BulkAnswersReq, current=Depends(require_user)):
    sess = await db.sessions.find_one({"_id": payload.session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    for item in payload.answers:
        existing = await db.answers.find_one({"session_id": payload.session_id, "area_id": item.area_id, "question_id": item.question_id})
        now = datetime.utcnow()
        doc = {"session_id": payload.session_id, "area_id": item.area_id, "question_id": item.question_id, "value": item.value, "evidence_ids": item.evidence_ids or [], "updated_at": now}
        if existing:
            await db.answers.update_one({"_id": existing["_id"]}, {"$set": doc})
        else:
            did = str(uuid.uuid4())
            await db.answers.insert_one({"_id": did, "id": did, **doc, "created_at": now})
    return {"ok": True}

@api.get("/assessment/session/{session_id}/answer/{area_id}/{question_id}/evidence")
async def list_evidence(session_id: str, area_id: str, question_id: str, current=Depends(require_user)):
    sess = await db.sessions.find_one({"_id": session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    ans = await db.answers.find_one({"session_id": session_id, "area_id": area_id, "question_id": question_id})
    if not ans:
        return {"evidence": []}
    eids = ans.get("evidence_ids", [])
    if not eids:
        return {"evidence": []}
    uploads = await db.uploads.find({"_id": {"$in": eids}}).to_list(100)
    reviews = await db.reviews.find({"evidence_id": {"$in": eids}}).to_list(500)
    status_by_eid = {r["evidence_id"]: r.get("status", "pending") for r in reviews}
    enriched = [{"upload_id": u["_id"], "file_name": u.get("file_name"), "mime_type": u.get("mime_type"), "size": u.get("final_size", u.get("total_size")), "status": status_by_eid.get(u["_id"], "pending")} for u in uploads]
    return {"evidence": enriched}

@api.delete("/upload/{upload_id}")
async def delete_evidence(upload_id: str, current=Depends(require_user)):
    up = await db.uploads.find_one({"_id": upload_id})
    if not up:
        raise HTTPException(status_code=404, detail="Upload not found")
    sess = await db.sessions.find_one({"_id": up.get("session_id")})
    if current.get("role") != "navigator":
        if sess and not sess.get("user_id"):
            await db.sessions.update_one({"_id": sess["_id"]}, {"$set": {"user_id": current["id"], "claimed_at": datetime.utcnow()}})
            sess = await db.sessions.find_one({"_id": up.get("session_id")})
        if not sess or sess.get("user_id") != current.get("id"):
            raise HTTPException(status_code=403, detail="Forbidden")
    final_path = up.get("stored_path")
    try:
        if final_path and os.path.exists(final_path):
            os.remove(final_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {final_path}: {e}")
    stage_dir = UPLOAD_BASE / upload_id
    try:
        if stage_dir.exists():
            for p in stage_dir.rglob('*'):
                try:
                    if p.is_file():
                        p.unlink()
                except Exception:
                    pass
            for p in sorted(stage_dir.rglob('*'), reverse=True):
                try:
                    if p.is_dir():
                        p.rmdir()
                except Exception:
                    pass
            if stage_dir.exists():
                stage_dir.rmdir()
    except Exception:
        pass
    await db.answers.update_many({"session_id": up.get("session_id"), "area_id": up.get("area_id"), "question_id": up.get("question_id")}, {"$pull": {"evidence_ids": upload_id}})
    await db.reviews.update_many({"evidence_id": upload_id}, {"$set": {"status": "deleted", "updated_at": datetime.utcnow()}})
    await db.uploads.update_one({"_id": upload_id}, {"$set": {"status": "deleted", "deleted_at": datetime.utcnow()}})
    return {"ok": True}

@api.get("/upload/{upload_id}/download")
async def download_evidence(upload_id: str, current=Depends(require_user)):
    up = await db.uploads.find_one({"_id": upload_id})
    if not up:
        raise HTTPException(status_code=404, detail="Upload not found")
    sess = await db.sessions.find_one({"_id": up.get("session_id")})
    if current.get("role") != "navigator" and (not sess or sess.get("user_id") != current.get("id")):
        raise HTTPException(status_code=403, detail="Forbidden")
    final_path = up.get("stored_path")
    if not final_path or not os.path.exists(final_path):
        raise HTTPException(status_code=404, detail="File not found")
    filename = up.get("file_name") or os.path.basename(final_path)
    return FileResponse(path=final_path, media_type=up.get("mime_type") or 'application/octet-stream', filename=filename)

@api.get("/assessment/session/{session_id}/progress", response_model=ProgressResp)
async def get_progress(session_id: str, current=Depends(require_user)):
    sess = await db.sessions.find_one({"_id": session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.get("user_id") != current.get("id") and current.get("role") != "navigator":
        raise HTTPException(status_code=403, detail="Forbidden")
    total_questions = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
    answers = await db.answers.find({"session_id": session_id}).to_list(2000)
    answered = sum(1 for a in answers if a.get("value") is not None)
    requires = {(area["id"], q["id"]): q["requires_evidence_on_yes"] for area in ASSESSMENT_SCHEMA["areas"] for q in area["questions"]}
    evidence_ids = [eid for a in answers for eid in (a.get("evidence_ids") or [])]
    approved_set = set()
    if evidence_ids:
        approved = await db.reviews.find({"evidence_id": {"$in": evidence_ids}, "status": "approved"}).to_list(5000)
        approved_set = set([r["evidence_id"] for r in approved])
    approved_evidence_answers = 0
    for a in answers:
        key = (a["area_id"], a["question_id"])
        req = requires.get(key, False)
        val = a.get("value")
        if val is None:
            continue
        if req and val is True:
            eids = a.get("evidence_ids", []) or []
            if any(e in approved_set for e in eids):
                approved_evidence_answers += 1
        else:
            approved_evidence_answers += 1
    percent = round((approved_evidence_answers / total_questions) * 100, 2) if total_questions else 0.0
    return ProgressResp(session_id=session_id, total_questions=total_questions, answered=answered, approved_evidence_answers=approved_evidence_answers, percent_complete=percent)

# ---------- Chunked Upload (auth enforced) ----------
CHUNK_SIZE_DEFAULT = 5 * 1024 * 1024

@api.post("/upload/initiate", response_model=UploadInitiateResp)
async def initiate_upload(req: UploadInitiateReq, current=Depends(require_user)):
    # Verify session ownership
    sess = await db.sessions.find_one({"_id": req.session_id})
    if not sess or (sess.get("user_id") != current.get("id") and current.get("role") != "navigator"):
        raise HTTPException(status_code=403, detail="Forbidden")
    upload_id = str(uuid.uuid4())
    stage_dir = UPLOAD_BASE / upload_id / "chunks"
    stage_dir.mkdir(parents=True, exist_ok=True)
    rec = {"_id": upload_id, "id": upload_id, "file_name": req.file_name, "total_size": req.total_size, "mime_type": req.mime_type, "session_id": req.session_id, "area_id": req.area_id, "question_id": req.question_id, "status": "initiated", "created_at": datetime.utcnow(), "uploader_user_id": current.get("id")}
    await db.uploads.insert_one(rec)
    return UploadInitiateResp(upload_id=upload_id, chunk_size=CHUNK_SIZE_DEFAULT)

@api.post("/upload/chunk")
async def upload_chunk(upload_id: str = Form(...), chunk_index: int = Form(...), file: UploadFile = File(...)):
    stage_dir = UPLOAD_BASE / upload_id / "chunks"
    if not stage_dir.exists():
        raise HTTPException(status_code=400, detail="Upload ID not initiated")
    chunk_path = stage_dir / f"{chunk_index:06d}.part"
    try:
        async with aiofiles.open(chunk_path, 'wb') as out:
            while True:
                data = await file.read(1024 * 1024)
                if not data:
                    break
                await out.write(data)
    finally:
        await file.close()
    return {"ok": True, "chunk_index": chunk_index}

@api.post("/upload/complete")
async def complete_upload(req: UploadCompleteReq, current=Depends(require_user)):
    rec = await db.uploads.find_one({"_id": req.upload_id})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    # Verify ownership
    sess = await db.sessions.find_one({"_id": rec.get("session_id")})
    if not sess or (sess.get("user_id") != current.get("id") and current.get("role") != "navigator"):
        raise HTTPException(status_code=403, detail="Forbidden")
    stage_dir = UPLOAD_BASE / req.upload_id / "chunks"
    if not stage_dir.exists():
        raise HTTPException(status_code=400, detail="Chunks not found")
    final_dir = UPLOAD_BASE / req.upload_id
    final_dir.mkdir(parents=True, exist_ok=True)
    final_path = final_dir / rec["file_name"]

    async with aiofiles.open(final_path, 'wb') as out:
        for i in range(req.total_chunks):
            part_path = stage_dir / f"{i:06d}.part"
            if not part_path.exists():
                raise HTTPException(status_code=400, detail=f"Missing chunk {i}")
            async with aiofiles.open(part_path, 'rb') as part:
                while True:
                    data = await part.read(1024 * 1024)
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

# ---------- AI Explain (auth gated) ----------
@api.post("/ai/explain", response_model=AIExplainResp)
async def ai_explain(req: AIExplainReq, current=Depends(require_user)):
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        return AIExplainResp(ok=False, message="AI key missing. Please set EMERGENT_LLM_KEY in backend/.env and restart backend.")
    if not EMERGENT_OK:
        return AIExplainResp(ok=False, message="AI library not installed. Please install emergentintegrations.")
    provider = (req.provider or "openai").lower()
    model = req.model or "gpt-4o-mini"
    system_message = "You are a procurement readiness coach. Be concise, specific, and action-oriented."
    chat = LlmChat(api_key=llm_key, session_id=req.session_id or str(uuid.uuid4()), system_message=system_message).with_model(provider, model)
    prompt = f"Explain why this requirement matters for procurement readiness and what evidence typically satisfies it.\nArea: {req.area_id}\nQuestion: {req.question_id} {req.question_text or ''}\nContext: {req.context or {}}\nKeep it under 120 words."
    try:
        response = await chat.send_message(UserMessage(text=prompt))
        return AIExplainResp(ok=True, message=str(response))
    except Exception as e:
        logger.exception("AI call failed")
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

# ---------- Navigator Review ----------
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

# ---------- Provider Profiles & Matching (Phase 3 MVP) ----------
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
        elif pmin and b >= pmin * 0.8:
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
    if resp_count >= 5:
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