from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import aiofiles

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
api_router = APIRouter(prefix="/api")

# Upload directory
UPLOAD_BASE = ROOT_DIR / "uploads"
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    answered_with_required_evidence: int
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

# ---------- Assessment Schema (MVP subset for aha) ----------
ASSESSMENT_SCHEMA: Dict[str, Dict] = {
    "areas": [
        {
            "id": "area1",
            "title": "Business Formation and Legal Structure",
            "questions": [
                {"id": "q1", "text": "Is your business legally registered in Texas and San Antonio?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Do you have all required licenses and permits?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Is your legal entity (LLC/Corp) properly documented?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area2",
            "title": "Financial Management and Accounting",
            "questions": [
                {"id": "q1", "text": "Is an accounting system (e.g., QuickBooks) implemented?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Do you produce monthly financial statements?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Are taxes current and filed on time?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area3",
            "title": "Human Resources and Employment Practices",
            "questions": [
                {"id": "q1", "text": "Do you have an employee handbook?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Is payroll system set up and compliant?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Do you follow EEO practices?", "requires_evidence_on_yes": False},
            ],
        },
        {
            "id": "area4",
            "title": "Operations and Quality Management",
            "questions": [
                {"id": "q1", "text": "Are SOPs documented?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Is a quality control process in place?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Do you manage vendors with written agreements?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area5",
            "title": "Technology and Information Security",
            "questions": [
                {"id": "q1", "text": "Are backups configured and tested?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Is antivirus/EDR deployed across devices?", "requires_evidence_on_yes": False},
                {"id": "q3", "text": "Is your website up to date and secure (HTTPS)?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area6",
            "title": "Marketing and Business Development",
            "questions": [
                {"id": "q1", "text": "Do you have a documented marketing plan?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Are there defined customer acquisition channels?", "requires_evidence_on_yes": False},
                {"id": "q3", "text": "Do you track marketing KPIs?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area7",
            "title": "Risk Management and Insurance",
            "questions": [
                {"id": "q1", "text": "Do you have general liability insurance?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Is business continuity plan documented?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Are contracts centrally stored and reviewed?", "requires_evidence_on_yes": True},
            ],
        },
        {
            "id": "area8",
            "title": "Growth and Scalability Planning",
            "questions": [
                {"id": "q1", "text": "Do you maintain a 12-24 month strategic plan?", "requires_evidence_on_yes": True},
                {"id": "q2", "text": "Is financial forecasting updated quarterly?", "requires_evidence_on_yes": True},
                {"id": "q3", "text": "Is succession planning defined?", "requires_evidence_on_yes": False},
            ],
        },
    ]
}

# ---------- Routes ----------
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    doc = StatusCheck(**input.dict()).dict()
    doc["_id"] = doc["id"]  # Avoid ObjectId
    await db.status_checks.insert_one(doc)
    return StatusCheck(**doc)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**sc) for sc in status_checks]

@api_router.get("/assessment/schema")
async def get_schema():
    return ASSESSMENT_SCHEMA

@api_router.post("/assessment/session", response_model=CreateSessionResp)
async def create_session():
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    doc = {"_id": session_id, "id": session_id, "created_at": now, "status": "active"}
    await db.sessions.insert_one(doc)
    return CreateSessionResp(session_id=session_id, created_at=now)

@api_router.get("/assessment/session/{session_id}")
async def get_session(session_id: str):
    sess = await db.sessions.find_one({"_id": session_id})
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    return {"session": sess, "answers": answers}

@api_router.post("/assessment/answers/bulk")
async def save_answers(payload: BulkAnswersReq):
    # Upsert without creating ObjectId
    ops = []
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
            doc["_id"] = doc_id
            doc["id"] = doc_id
            doc["created_at"] = now
            await db.answers.insert_one(doc)
    return {"ok": True}

@api_router.get("/assessment/session/{session_id}/progress", response_model=ProgressResp)
async def get_progress(session_id: str):
    # Count total questions from schema
    total_questions = sum(len(a["questions"]) for a in ASSESSMENT_SCHEMA["areas"])
    answers = await db.answers.find({"session_id": session_id}).to_list(1000)
    answered = sum(1 for a in answers if a.get("value") is not None)
    # Determine evidence requirement
    requires = {}
    for area in ASSESSMENT_SCHEMA["areas"]:
        for q in area["questions"]:
            requires[(area["id"], q["id"])] = q["requires_evidence_on_yes"]
    answered_with_required_evidence = 0
    for a in answers:
        key = (a["area_id"], a["question_id"])
        req = requires.get(key, False)
        if a.get("value") is True and req:
            if len(a.get("evidence_ids", [])) > 0:
                answered_with_required_evidence += 1
        elif a.get("value") in (False, None) or not req:
            # counts as answered regardless of evidence if not required
            if a.get("value") is not None:
                answered_with_required_evidence += 1
    percent = round((answered_with_required_evidence / total_questions) * 100, 2) if total_questions else 0.0
    return ProgressResp(
        session_id=session_id,
        total_questions=total_questions,
        answered=answered,
        answered_with_required_evidence=answered_with_required_evidence,
        percent_complete=percent,
    )

# ---------- Chunked Upload ----------
CHUNK_SIZE_DEFAULT = 5 * 1024 * 1024  # 5MB

@api_router.post("/upload/initiate", response_model=UploadInitiateResp)
async def initiate_upload(req: UploadInitiateReq):
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
    }
    await db.uploads.insert_one(rec)
    return UploadInitiateResp(upload_id=upload_id, chunk_size=CHUNK_SIZE_DEFAULT)

@api_router.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
):
    # Write chunk to disk as binary
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

@api_router.post("/upload/complete")
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

    # Attach to answer record if present
    if rec.get("session_id") and rec.get("area_id") and rec.get("question_id"):
        existing = await db.answers.find_one({
            "session_id": rec["session_id"],
            "area_id": rec["area_id"],
            "question_id": rec["question_id"],
        })
        if existing:
            ev = list(set((existing.get("evidence_ids") or []) + [req.upload_id]))
            await db.answers.update_one({"_id": existing["_id"]}, {"$set": {"evidence_ids": ev, "updated_at": datetime.utcnow()}})
        else:
            # Create placeholder answer with evidence only
            doc_id = str(uuid.uuid4())
            doc = {
                "_id": doc_id,
                "id": doc_id,
                "session_id": rec["session_id"],
                "area_id": rec["area_id"],
                "question_id": rec["question_id"],
                "value": True,  # assume affirmative if evidence uploaded
                "evidence_ids": [req.upload_id],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db.answers.insert_one(doc)

    return {"ok": True, "upload_id": req.upload_id, "size": size}

# ---------- AI Explain ----------
@api_router.post("/ai/explain", response_model=AIExplainResp)
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

    # Build prompt
    qtext = req.question_text or ""
    prompt = f"Explain why this requirement matters for procurement readiness and what evidence typically satisfies it.\nArea: {req.area_id}\nQuestion: {req.question_id} {qtext}\nContext: {req.context or {}}\nKeep it under 120 words."
    user_message = UserMessage(text=prompt)

    try:
        response = await chat.send_message(user_message)
        return AIExplainResp(ok=True, message=str(response))
    except Exception as e:
        logger.exception("AI call failed")
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

# Include router
app.include_router(api_router)

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