from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse
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
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

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

# ---------- Assessment Schema (Expanded 10 Q per area) ----------

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
            "Is your business legally registered in Texas and San Antonio?",
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
    return {"message": "Hello World"}

@api.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    doc = StatusCheck(**input.dict()).dict()
    doc["_id"] = doc["id"]  # Avoid ObjectId
    await db.status_checks.insert_one(doc)
    return StatusCheck(**doc)

@api.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**sc) for sc in status_checks]

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

# ---------- Assessment Routes ----------
@api.get("/assessment/schema")
async def get_schema():
    return ASSESSMENT_SCHEMA

@api.post("/assessment/session", response_model=CreateSessionResp)
async def create_session(current=Depends(get_current_user)):
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    doc = {"_id": session_id, "id": session_id, "created_at": now, "status": "active"}
    if current:
        doc["user_id"] = current["id"]
    await db.sessions.insert_one(doc)
    return CreateSessionResp(session_id=session_id, created_at=now)

@api.get("/assessment/session/{session_id}")
async def get_session(session_id: str):
    sess = await db.sessions.find_one({"_id": session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    return {"session": sess, "answers": answers}

@api.post("/assessment/answers/bulk")
async def save_answers(payload: BulkAnswersReq):
    for item in payload.answers:
        existing = await db.answers.find_one({
            "session_id": payload.session_id,
            "area_id": item.area_id,
            "question_id": item.question_id,
        })
        now = datetime.utcnow()
        doc = {
            "session_id": payload.session_id,
            "area_id": item.area_id,
            "question_id": item.question_id,
            "value": item.value,
            "evidence_ids": item.evidence_ids or [],
            "updated_at": now,
        }
        if existing:
            await db.answers.update_one({"_id": existing["_id"]}, {"$set": doc})
        else:
            doc_id = str(uuid.uuid4())
            doc.update({"_id": doc_id, "id": doc_id, "created_at": now})
            await db.answers.insert_one(doc)
    return {"ok": True}

@api.get("/assessment/session/{session_id}/answer/{area_id}/{question_id}/evidence")
async def list_evidence(session_id: str, area_id: str, question_id: str):
    ans = await db.answers.find_one({"session_id": session_id, "area_id": area_id, "question_id": question_id})
    if not ans:
        return {"evidence": []}
    eids = ans.get("evidence_ids", [])
    if not eids:
        return {"evidence": []}
    uploads = await db.uploads.find({"_id": {"$in": eids}}).to_list(100)
    # attach review status
    reviews = await db.reviews.find({"evidence_id": {"$in": eids}}).to_list(500)
    status_by_eid = {}
    for r in reviews:
        status_by_eid.setdefault(r["evidence_id"], r.get("status", "pending"))
    enriched = []
    for u in uploads:
        enriched.append({
            "upload_id": u["_id"],
            "file_name": u.get("file_name"),
            "mime_type": u.get("mime_type"),
            "size": u.get("final_size", u.get("total_size")),
            "status": status_by_eid.get(u["_id"], "pending"),
        })
    return {"evidence": enriched}

@api.delete("/upload/{upload_id}")
async def delete_evidence(upload_id: str, current=Depends(require_user)):
    up = await db.uploads.find_one({"_id": upload_id})
    if not up:
        raise HTTPException(status_code=404, detail="Upload not found")
    sess = await db.sessions.find_one({"_id": up.get("session_id")})
    # allow owner (client) or navigator
    if current.get("role") != "navigator":
        if not sess or sess.get("user_id") != current.get("id"):
            raise HTTPException(status_code=403, detail="Forbidden")
    # remove file(s)
    final_path = up.get("stored_path")
    try:
        if final_path and os.path.exists(final_path):
            os.remove(final_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {final_path}: {e}")
    # remove chunk dir
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
    # unlink from answers
    await db.answers.update_many({"session_id": up.get("session_id"), "area_id": up.get("area_id"), "question_id": up.get("question_id")}, {"$pull": {"evidence_ids": upload_id}})
    # mark review as deleted
    await db.reviews.update_many({"evidence_id": upload_id}, {"$set": {"status": "deleted", "updated_at": datetime.utcnow()}})
    # mark upload as deleted
    await db.uploads.update_one({"_id": upload_id}, {"$set": {"status": "deleted", "deleted_at": datetime.utcnow()}})
    return {"ok": True}

@api.get("/assessment/session/{session_id}/progress", response_model=ProgressResp)
async def get_progress(session_id: str):
    total_questions = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
    answers = await db.answers.find({"session_id": session_id}).to_list(2000)
    answered = sum(1 for a in answers if a.get("value") is not None)

    # requires evidence lookup
    requires = {}
    for area in ASSESSMENT_SCHEMA["areas"]:
        for q in area["questions"]:
            requires[(area["id"], q["id"])] = q["requires_evidence_on_yes"]

    # gather approvals by evidence id
    evidence_ids = []
    for a in answers:
        evidence_ids.extend(a.get("evidence_ids", []) or [])
    if evidence_ids:
        approved = await db.reviews.find({"evidence_id": {"$in": evidence_ids}, "status": "approved"}).to_list(5000)
        approved_set = set([r["evidence_id"] for r in approved])
    else:
        approved_set = set()

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
            # no evidence required or answer is no -> counts as answered
            approved_evidence_answers += 1

    percent = round((approved_evidence_answers / total_questions) * 100, 2) if total_questions else 0.0
    return ProgressResp(session_id=session_id, total_questions=total_questions, answered=answered, approved_evidence_answers=approved_evidence_answers, percent_complete=percent)

# ---------- Chunked Upload ----------
CHUNK_SIZE_DEFAULT = 5 * 1024 * 1024  # 5MB

@api.post("/upload/initiate", response_model=UploadInitiateResp)
async def initiate_upload(req: UploadInitiateReq, current=Depends(get_current_user)):
    upload_id = str(uuid.uuid4())
    # Create staging dir
    stage_dir = UPLOAD_BASE / upload_id / "chunks"
    stage_dir.mkdir(parents=True, exist_ok=True)
    rec = {
        "_id": upload_id,
        "id": upload_id,
        "file_name": req.file_name,
        "total_size": req.total_size,
        "mime_type": req.mime_type,
        "session_id": req.session_id,
        "area_id": req.area_id,
        "question_id": req.question_id,
        "status": "initiated",
        "created_at": datetime.utcnow(),
        "uploader_user_id": current.get("id") if current else None,
    }
    await db.uploads.insert_one(rec)
    return UploadInitiateResp(upload_id=upload_id, chunk_size=CHUNK_SIZE_DEFAULT)

@api.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
):
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
async def complete_upload(req: UploadCompleteReq):
    rec = await db.uploads.find_one({"_id": req.upload_id})
    if not rec:
        raise HTTPException(status_code=404, detail="Upload not found")
    stage_dir = UPLOAD_BASE / req.upload_id / "chunks"
    if not stage_dir.exists():
        raise HTTPException(status_code=400, detail="Chunks not found")
    # Merge
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

    # Attach to answer record
    existing = await db.answers.find_one({
        "session_id": rec["session_id"],
        "area_id": rec["area_id"],
        "question_id": rec["question_id"],
    })
    if existing:
        ev = list(set((existing.get("evidence_ids") or []) + [req.upload_id]))
        await db.answers.update_one({"_id": existing["_id"]}, {"$set": {"evidence_ids": ev, "updated_at": datetime.utcnow()}})
    else:
        doc_id = str(uuid.uuid4())
        doc = {
            "_id": doc_id,
            "id": doc_id,
            "session_id": rec["session_id"],
            "area_id": rec["area_id"],
            "question_id": rec["question_id"],
            "value": True,
            "evidence_ids": [req.upload_id],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db.answers.insert_one(doc)

    # Create review record (pending)
    review_id = str(uuid.uuid4())
    rdoc = {
        "_id": review_id,
        "id": review_id,
        "session_id": rec["session_id"],
        "area_id": rec["area_id"],
        "question_id": rec["question_id"],
        "evidence_id": req.upload_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewer_user_id": None,
        "notes": None,
    }
    await db.reviews.insert_one(rdoc)

    return {"ok": True, "upload_id": req.upload_id, "size": size, "review_id": review_id}

# ---------- AI Explain ----------
@api.post("/ai/explain", response_model=AIExplainResp)
async def ai_explain(req: AIExplainReq):
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        return AIExplainResp(ok=False, message="AI key missing. Please set EMERGENT_LLM_KEY in backend/.env and restart backend.")
    if not EMERGENT_OK:
        return AIExplainResp(ok=False, message="AI library not installed. Please install emergentintegrations.")

    provider = (req.provider or "openai").lower()
    model = req.model or "gpt-4o-mini"

    system_message = "You are a procurement readiness coach for San Antonio's SBAP. Be concise, specific, and action-oriented."
    chat = LlmChat(api_key=llm_key, session_id=req.session_id or str(uuid.uuid4()), system_message=system_message).with_model(provider, model)

    qtext = req.question_text or ""
    prompt = f"Explain why this requirement matters for procurement readiness and what evidence typically satisfies it.\nArea: {req.area_id}\nQuestion: {req.question_id} {qtext}\nContext: {req.context or {}}\nKeep it under 120 words."
    user_message = UserMessage(text=prompt)

    try:
        response = await chat.send_message(user_message)
        return AIExplainResp(ok=True, message=str(response))
    except Exception as e:
        logger.exception("AI call failed")
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

# ---------- Navigator Review ----------
@api.get("/navigator/reviews")
async def get_reviews(status: str = Query("pending"), current=Depends(require_role("navigator"))):
    q = {"status": status}
    reviews = await db.reviews.find(q).to_list(2000)
    # enrich with question text and file name
    # build lookup
    text_by_key = {}
    for area in ASSESSMENT_SCHEMA["areas"]:
        for qobj in area["questions"]:
            text_by_key[(area["id"], qobj["id"]) ] = {"area": area["title"], "question": qobj["text"]}
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