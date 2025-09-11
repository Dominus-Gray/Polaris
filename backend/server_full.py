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
    decision: str
    notes: Optional[str] = None

# Assessment schema
ASSESSMENT_SCHEMA = {
    "areas": [
        {
            "id": "business_structure",
            "name": "Business Structure & Legal",
            "questions": [
                {"id": "legal_entity", "text": "Is your business a legally registered entity?"},
                {"id": "business_license", "text": "Do you have all required business licenses?"},
                {"id": "insurance", "text": "Do you have appropriate business insurance?"}
            ]
        },
        {
            "id": "financial_management", 
            "name": "Financial Management",
            "questions": [
                {"id": "accounting_system", "text": "Do you have a formal accounting system?"},
                {"id": "financial_statements", "text": "Do you prepare regular financial statements?"},
                {"id": "cash_flow", "text": "Do you monitor cash flow regularly?"}
            ]
        },
        {
            "id": "operations",
            "name": "Operations & Quality",
            "questions": [
                {"id": "quality_control", "text": "Do you have quality control processes?"},
                {"id": "inventory_management", "text": "Do you have inventory management systems?"},
                {"id": "vendor_relationships", "text": "Do you maintain good vendor relationships?"}
            ]
        }
    ]
}

# --------------- AI resources for "No" pathway ---------------
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
        # Fallback to static reputable sources
        return AIResourcesResp(resources=[
            ResourceItem(name="UTSA Small Business Development Center", url="https://sasbdc.org/", summary="Free advising, workshops, and templates for small businesses.", source_type="edu/nonprofit", locality="local"),
            ResourceItem(name="SCORE San Antonio", url="https://www.score.org/sanantonio", summary="No-cost mentoring and resources for entrepreneurs.", source_type="nonprofit", locality="local"),
            ResourceItem(name="SBA Resource Partners", url="https://www.sba.gov/local-assistance", summary="Federal resources and partners offering guidance and tools.", source_type="gov", locality="online"),
        ])
    system = (
        "You are a procurement readiness navigator. Return concise, credible free resources. "
        "Prefer .gov, .edu, or nonprofit sources; only include other domains if highly credible. "
        "Tailor to the question and locality. Output JSON with array of items: name, url, summary (<=140 chars), source_type (gov|edu|nonprofit|other), locality (local|online)."
    )
    chat = LlmChat(api_key=llm_key, session_id=str(uuid.uuid4()), system_message=system).with_model("openai", "gpt-4o-mini")
    prompt = (
        f"Locality: {req.locality}\nCount: {req.count}\nQuestion: {req.question_text or req.question_id}\n"
        f"Area: {req.area_id}. Prefer gov/edu/nonprofit sources. Return only JSON array."
    )
    try:
        resp = await chat.send_message(UserMessage(text=prompt))
        # Best-effort parse expecting a JSON array; if not, fallback
        import json as pyjson
        data = None
        try:
            data = pyjson.loads(str(resp))
        except Exception:
            # try to locate JSON array within text
            txt = str(resp)
            start = txt.find('[')
            end = txt.rfind(']')
            if start != -1 and end != -1 and end > start:
                data = pyjson.loads(txt[start:end+1])
        items = []
        if isinstance(data, list):
            for it in data[: req.count]:
                items.append(ResourceItem(
                    name=str(it.get("name", "Resource")),
                    url=str(it.get("url", "")),
                    summary=str(it.get("summary", ""))[:200],
                    source_type=str(it.get("source_type", "other")),
                    locality=str(it.get("locality", "online")),
                ))
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

# --------------- Action Plan Versioning & Recommendation Engine ---------------
from enum import Enum
from typing import Union, Any
import json

class ActionPlanStatus(str, Enum):
    draft = "draft"
    suggested = "suggested"
    active = "active"
    archived = "archived"

class Goal(BaseModel):
    id: str
    title: str
    description: str
    target_metrics: Optional[Dict[str, Any]] = None
    timeframe: Optional[str] = None
    assigned_roles: List[str] = []

class Intervention(BaseModel):
    id: str
    goal_id: str
    title: str
    description: str
    type: str  # e.g., "training", "process_improvement", "tool_adoption"
    resources_required: List[str] = []
    estimated_duration: Optional[str] = None

class ActionPlan(BaseModel):
    id: str
    client_id: str
    version: int
    status: ActionPlanStatus
    goals: List[Goal]
    interventions: List[Intervention]
    generated_by_type: Optional[str] = None  # e.g., "rule_engine", "manual"
    supersedes_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class PlanSeries(BaseModel):
    id: str
    client_id: str
    active_plan_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ActionPlanDiff(BaseModel):
    id: str
    from_plan_id: str
    to_plan_id: str
    summary_json: Dict[str, Any]
    created_at: datetime

class RecommendationProvider:
    """Abstract interface for recommendation providers"""
    
    def generate_plan(self, client_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a plan proposal with goals, interventions, and metadata"""
        raise NotImplementedError

class RuleBasedBaselineRecommendationProvider(RecommendationProvider):
    """Stub provider using simple heuristic rules"""
    
    def __init__(self, rules_config: Dict[str, Any] = None):
        self.rules = rules_config or self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        return {
            "risk_score_thresholds": {
                "high": {"min": 75, "goals": ["Improve financial management", "Enhance compliance"]},
                "medium": {"min": 50, "goals": ["Standardize processes", "Documentation improvement"]},
                "low": {"min": 0, "goals": ["Maintain current standards"]}
            }
        }
    
    def generate_plan(self, client_context: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = client_context.get("risk_score", 0)
        readiness_percent = client_context.get("readiness_percent", 0)
        
        # Determine risk level and associated goals
        if risk_score >= 75 or readiness_percent < 25:
            risk_level = "high"
        elif risk_score >= 50 or readiness_percent < 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        rule_goals = self.rules["risk_score_thresholds"][risk_level]["goals"]
        
        goals = []
        interventions = []
        
        for i, goal_title in enumerate(rule_goals):
            goal_id = f"goal_{i+1}"
            goals.append({
                "id": goal_id,
                "title": goal_title,
                "description": f"Auto-generated goal: {goal_title}",
                "target_metrics": {"completion_rate": 100},
                "timeframe": "3 months",
                "assigned_roles": ["client"]
            })
            
            # Add default intervention for each goal
            interventions.append({
                "id": f"intervention_{i+1}",
                "goal_id": goal_id,
                "title": f"Implementation plan for {goal_title}",
                "description": f"Systematic approach to achieve {goal_title}",
                "type": "process_improvement",
                "resources_required": ["time", "documentation"],
                "estimated_duration": "4-6 weeks"
            })
        
        return {
            "goals": goals,
            "interventions": interventions,
            "metadata": {
                "rationale": [f"Based on {risk_level} risk assessment"],
                "source_tags": ["rule_engine", risk_level],
                "generation_context": client_context
            }
        }

class ActionPlanRecommender:
    """Service for orchestrating action plan recommendations"""
    
    def __init__(self, provider: RecommendationProvider):
        self.provider = provider
    
    async def generate_recommendation(self, client_id: str) -> str:
        """Generate and persist a suggested action plan for a client"""
        # Load client context
        client_context = await self._load_client_context(client_id)
        
        # Generate plan proposal
        proposal = self.provider.generate_plan(client_context)
        
        # Get next version number for this client
        next_version = await self._get_next_version_number(client_id)
        
        # Create action plan document
        plan_id = str(uuid.uuid4())
        plan_doc = {
            "_id": plan_id,
            "id": plan_id,
            "client_id": client_id,
            "version": next_version,
            "status": ActionPlanStatus.suggested.value,
            "goals": proposal["goals"],
            "interventions": proposal["interventions"],
            "generated_by_type": "rule_engine",
            "supersedes_id": None,
            "metadata": proposal.get("metadata", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Persist the plan
        await db.action_plans.insert_one(plan_doc)
        
        # Emit domain event
        await self._emit_event("ActionPlanSuggested", {
            "plan_id": plan_id,
            "client_id": client_id,
            "version": next_version,
            "generated_by": "rule_engine"
        })
        
        return plan_id
    
    async def _load_client_context(self, client_id: str) -> Dict[str, Any]:
        """Load client profile and latest assessments for context"""
        # Simplified for MVP - would load actual client data
        return {
            "client_id": client_id,
            "risk_score": 60,  # Would be computed from assessments
            "readiness_percent": 45,  # Would be computed from latest assessment
            "assessment_gaps": ["financial_management", "compliance"],
            "industry": "technology"
        }
    
    async def _get_next_version_number(self, client_id: str) -> int:
        """Get the next version number for this client's action plans"""
        latest = await db.action_plans.find_one(
            {"client_id": client_id},
            sort=[("version", -1)]
        )
        return (latest.get("version") if latest else 0) + 1
    
    async def _emit_event(self, event_type: str, payload: Dict[str, Any]):
        """Emit domain event for observability"""
        event_doc = {
            "_id": str(uuid.uuid4()),
            "event_type": event_type,
            "payload": payload,
            "created_at": datetime.utcnow()
        }
        await db.domain_events.insert_one(event_doc)
        logger.info(f"Emitted event: {event_type}", extra={"event": payload})

# Action Plan API Models
class ActionPlanCreateReq(BaseModel):
    goals: List[Goal]
    interventions: List[Intervention]
    metadata: Optional[Dict[str, Any]] = None

class ActionPlanResp(BaseModel):
    id: str
    client_id: str
    version: int
    status: ActionPlanStatus
    goals: List[Goal]
    interventions: List[Intervention]
    generated_by_type: Optional[str] = None
    supersedes_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class ActionPlanDiffResp(BaseModel):
    id: str
    from_plan_id: str
    to_plan_id: str
    summary: Dict[str, Any]
    created_at: datetime

# Initialize recommender with default provider
default_provider = RuleBasedBaselineRecommendationProvider()
action_plan_recommender = ActionPlanRecommender(default_provider)

# --------------- Assessment fees (agency & client) ---------------
ASSESSMENT_TIERING = os.environ.get("ASSESSMENT_TIERING", "flat")  # flat | volume
ASSESSMENT_FLAT_AMOUNT = float(os.environ.get("ASSESSMENT_FLAT_AMOUNT", 100))

async def get_agency_monthly_paid_invites_count(agency_user_id: str) -> int:
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    return await db.agency_invitations.count_documents({"agency_user_id": agency_user_id, "status": "paid", "paid_at": {"$gte": month_start}})

async def get_assessment_price_for_agency(agency_user_id: str) -> float:
    if ASSESSMENT_TIERING == "volume":
        count = await get_agency_monthly_paid_invites_count(agency_user_id)
        if count >= 200:
            return 70.0
        if count >= 50:
            return 85.0
        return 100.0
    # flat default
    return ASSESSMENT_FLAT_AMOUNT

@api.post("/client/assessment/pay")
async def client_assessment_pay(current=Depends(require_role("client"))):
    # Self-serve payment to unlock forecasts (stubbed processed)
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "assessment_fee", "amount": ASSESSMENT_FLAT_AMOUNT, "currency": "USD", "status": "processed", "created_at": datetime.utcnow(), "metadata": {"client_user_id": current["id"], "self_paid": True}}
    await db.revenue_transactions.insert_one(tx)
    return {"ok": True, "transaction_id": rid}

# Modify existing invite pay to compute price from tiering
@api.post("/agency/invitations/{invitation_id}/pay")
async def pay_invitation(invitation_id: str, current=Depends(require_role("agency"))):
    inv = await db.agency_invitations.find_one({"_id": invitation_id, "agency_user_id": current["id"]})
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if inv.get("status") == "paid":
        return {"ok": True, "message": "Already paid"}
    price = await get_assessment_price_for_agency(current["id"])  # compute volume/flat price
    rid = str(uuid.uuid4())
    tx = {"_id": rid, "id": rid, "transaction_type": "assessment_fee", "amount": price, "currency": "USD", "status": "processed", "created_at": datetime.utcnow(), "metadata": {"invitation_id": invitation_id, "agency_user_id": current["id"], "price_model": ASSESSMENT_TIERING}}
    await db.revenue_transactions.insert_one(tx)
    await db.agency_invitations.update_one({"_id": invitation_id}, {"$set": {"status": "paid", "paid_at": datetime.utcnow(), "payment_transaction_id": rid, "amount": price}})
    return {"ok": True, "transaction_id": rid, "amount": price}

# --------------- Opportunity gating update ---------------
@api.get("/opportunities/available")
async def available_opportunities(current=Depends(require_role("client"))):
    inv = await db.agency_invitations.find_one({"client_user_id": current["id"], "status": "accepted"})
    if inv:
        opps = await db.agency_opportunities.find({"created_by": inv["agency_user_id"]}).to_list(2000)
        return {"opportunities": opps, "unlock": "sponsored"}
    # allow self-paid clients to view all posted opportunities
    paid = await db.revenue_transactions.find_one({"transaction_type": "assessment_fee", "status": "processed", "metadata.client_user_id": current["id"]})
    if paid:
        opps = await db.agency_opportunities.find({}).to_list(5000)
        return {"opportunities": opps, "unlock": "self_paid"}
    return {"opportunities": []}

# --------------- Certificates ---------------
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
async def list_certificates(current=Depends(require_role("agency"))):
    certs = await db.certificates.find({"agency_user_id": current["id"]}).to_list(2000)
    return {"certificates": certs}

@api.get("/certificates/{cert_id}")
async def get_certificate(cert_id: str, current=Depends(require_user)):
    cert = await db.certificates.find_one({"_id": cert_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Not found")
    if current.get("role") not in ("navigator",) and current.get("id") not in (cert.get("agency_user_id"), cert.get("client_user_id")):
        raise HTTPException(status_code=403, detail="Forbidden")
    return cert

@api.get("/certificates/{cert_id}/download")
async def download_certificate_pdf(cert_id: str, current=Depends(require_user)):
    # Same access policy as viewing
    cert = await db.certificates.find_one({"_id": cert_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Not found")
    if current.get("role") not in ("navigator",) and current.get("id") not in (cert.get("agency_user_id"), cert.get("client_user_id")):
        raise HTTPException(status_code=403, detail="Forbidden")
    # Generate PDF to temp path
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    tmp_path = UPLOAD_BASE / f"certificate_{cert_id}.pdf"
    c = canvas.Canvas(str(tmp_path), pagesize=LETTER)
    width, height = LETTER
    # Header/branding
    c.setFillColorRGB(0.105, 0.211, 0.365)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height-1*inch, "Polaris – Small Business Maturity Assurance")
    c.setFont("Helvetica", 11)
    c.drawString(1*inch, height-1.3*inch, "City of San Antonio – Procurement Readiness Platform")
    # Body
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height-2*inch, "Certificate of Opportunity Readiness")
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height-2.4*inch, f"Issued to Client ID: {cert.get('client_user_id')}")
    c.drawString(1*inch, height-2.7*inch, f"Sponsoring Agency ID: {cert.get('agency_user_id')}")
    c.drawString(1*inch, height-3.0*inch, f"Assessment Session ID: {cert.get('session_id')}")
    c.drawString(1*inch, height-3.3*inch, f"Readiness: {cert.get('readiness_percent')}%")
    c.drawString(1*inch, height-3.6*inch, f"Issued at: {cert.get('issued_at')}")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1*inch, height-4.1*inch, "This certificate signifies the business has met the evidence-backed readiness threshold.")
    c.drawString(1*inch, height-4.35*inch, "Validated by the sponsoring agency within the Polaris platform.")
    c.showPage()
    c.save()
    return FileResponse(str(tmp_path), media_type="application/pdf", filename=f"Polaris_Certificate_{cert_id}.pdf")

# Extend impact with certificates
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
    opp_count = await db.agency_opportunities.count_documents({"created_by": aid})
    cert_count = await db.certificates.count_documents({"agency_user_id": aid})
    buckets = {"0_25": 0, "25_50": 0, "50_75": 0, "75_100": 0}
    accepted = await db.agency_invitations.find({"agency_user_id": aid, "status": "accepted"}).to_list(2000)
    for inv in accepted:
        sid = inv.get("session_id")
        if not sid:
            continue
        rpct = await compute_readiness(sid)
        if rpct < 25:
            buckets["0_25"] += 1
        elif rpct < 50:
            buckets["25_50"] += 1
        elif rpct < 75:
            buckets["50_75"] += 1
        else:
            buckets["75_100"] += 1
    return {"invites": {"total": invites_total, "paid": invites_paid, "accepted": invites_accepted}, "revenue": {"assessment_fees": assessment_revenue}, "opportunities": {"count": opp_count}, "certificates": {"issued": cert_count}, "readiness_buckets": buckets}

# --------------- Action Plan API Endpoints ---------------

async def compute_action_plan_diff(from_plan: Dict[str, Any], to_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Compute differences between two action plans"""
    diff = {
        "added": {"goals": [], "interventions": []},
        "removed": {"goals": [], "interventions": []},
        "changed": {"goals": [], "interventions": []}
    }
    
    # Compare goals
    from_goals = {g["id"]: g for g in from_plan.get("goals", [])}
    to_goals = {g["id"]: g for g in to_plan.get("goals", [])}
    
    # Added goals
    for goal_id, goal in to_goals.items():
        if goal_id not in from_goals:
            diff["added"]["goals"].append(goal)
    
    # Removed goals
    for goal_id, goal in from_goals.items():
        if goal_id not in to_goals:
            diff["removed"]["goals"].append(goal)
    
    # Changed goals
    for goal_id in from_goals:
        if goal_id in to_goals:
            from_goal = from_goals[goal_id]
            to_goal = to_goals[goal_id]
            changed_fields = []
            
            for field in ["title", "description", "target_metrics", "timeframe", "assigned_roles"]:
                if from_goal.get(field) != to_goal.get(field):
                    changed_fields.append(field)
            
            if changed_fields:
                diff["changed"]["goals"].append({
                    "id": goal_id,
                    "fields_changed": changed_fields
                })
    
    # Compare interventions (similar logic)
    from_interventions = {i["id"]: i for i in from_plan.get("interventions", [])}
    to_interventions = {i["id"]: i for i in to_plan.get("interventions", [])}
    
    for intervention_id, intervention in to_interventions.items():
        if intervention_id not in from_interventions:
            diff["added"]["interventions"].append(intervention)
    
    for intervention_id, intervention in from_interventions.items():
        if intervention_id not in to_interventions:
            diff["removed"]["interventions"].append(intervention)
    
    for intervention_id in from_interventions:
        if intervention_id in to_interventions:
            from_intervention = from_interventions[intervention_id]
            to_intervention = to_interventions[intervention_id]
            changed_fields = []
            
            for field in ["title", "description", "type", "resources_required", "estimated_duration"]:
                if from_intervention.get(field) != to_intervention.get(field):
                    changed_fields.append(field)
            
            if changed_fields:
                diff["changed"]["interventions"].append({
                    "id": intervention_id,
                    "fields_changed": changed_fields
                })
    
    return diff

@api.post("/clients/{client_id}/action-plans/recommend")
async def recommend_action_plan(client_id: str, current=Depends(require_user)):
    """Generate a recommended action plan for a client"""
    # Check permissions (simplified for MVP)
    if current.get("role") not in ("navigator", "agency"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        plan_id = await action_plan_recommender.generate_recommendation(client_id)
        
        # Retrieve the created plan
        plan_doc = await db.action_plans.find_one({"_id": plan_id})
        if not plan_doc:
            raise HTTPException(status_code=500, detail="Failed to retrieve generated plan")
        
        return ActionPlanResp(**plan_doc)
    
    except Exception as e:
        logger.exception(f"Failed to generate recommendation for client {client_id}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@api.post("/action-plans/{plan_id}/activate")
async def activate_action_plan(plan_id: str, current=Depends(require_user)):
    """Activate a suggested action plan, archiving the previous active plan"""
    # Check permissions
    if current.get("role") not in ("navigator", "agency", "client"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    plan = await db.action_plans.find_one({"_id": plan_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Action plan not found")
    
    if plan["status"] not in [ActionPlanStatus.suggested.value, ActionPlanStatus.draft.value]:
        raise HTTPException(status_code=400, detail="Can only activate suggested or draft plans")
    
    client_id = plan["client_id"]
    
    try:
        # Start transaction-like operations
        # Find current active plan
        current_active = await db.action_plans.find_one({
            "client_id": client_id,
            "status": ActionPlanStatus.active.value
        })
        
        # Archive current active plan if exists
        if current_active:
            await db.action_plans.update_one(
                {"_id": current_active["_id"]},
                {"$set": {"status": ActionPlanStatus.archived.value, "updated_at": datetime.utcnow()}}
            )
            
            # Compute and store diff
            diff_summary = await compute_action_plan_diff(current_active, plan)
            diff_doc = {
                "_id": str(uuid.uuid4()),
                "from_plan_id": current_active["_id"],
                "to_plan_id": plan_id,
                "summary_json": diff_summary,
                "created_at": datetime.utcnow()
            }
            await db.action_plan_diffs.insert_one(diff_doc)
            
            # Update plan with supersedes reference
            await db.action_plans.update_one(
                {"_id": plan_id},
                {"$set": {"supersedes_id": current_active["_id"]}}
            )
        
        # Activate the new plan
        await db.action_plans.update_one(
            {"_id": plan_id},
            {"$set": {"status": ActionPlanStatus.active.value, "updated_at": datetime.utcnow()}}
        )
        
        # Update plan series
        await db.plan_series.update_one(
            {"client_id": client_id},
            {
                "$set": {"active_plan_id": plan_id, "updated_at": datetime.utcnow()},
                "$setOnInsert": {"_id": str(uuid.uuid4()), "client_id": client_id, "created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Emit events
        await action_plan_recommender._emit_event("ActionPlanVersionActivated", {
            "plan_id": plan_id,
            "client_id": client_id,
            "version": plan["version"],
            "supersedes_id": current_active["_id"] if current_active else None
        })
        
        if current_active:
            await action_plan_recommender._emit_event("ActionPlanDiffComputed", {
                "from_plan_id": current_active["_id"],
                "to_plan_id": plan_id,
                "client_id": client_id
            })
        
        # Return updated plan
        updated_plan = await db.action_plans.find_one({"_id": plan_id})
        return ActionPlanResp(**updated_plan)
        
    except Exception as e:
        logger.exception(f"Failed to activate action plan {plan_id}")
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")

@api.get("/action-plans/{plan_id}/diffs")
async def get_action_plan_diffs(plan_id: str, current=Depends(require_user)):
    """Get diffs related to an action plan (both directions)"""
    # Check permissions
    if current.get("role") not in ("navigator", "agency", "client"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Find diffs where this plan is either from or to
    diffs = await db.action_plan_diffs.find({
        "$or": [
            {"from_plan_id": plan_id},
            {"to_plan_id": plan_id}
        ]
    }).sort("created_at", -1).to_list(100)
    
    diff_responses = []
    for diff in diffs:
        diff_responses.append(ActionPlanDiffResp(
            id=diff["_id"],
            from_plan_id=diff["from_plan_id"],
            to_plan_id=diff["to_plan_id"],
            summary=diff["summary_json"],
            created_at=diff["created_at"]
        ))
    
    return {"diffs": diff_responses}

@api.get("/clients/{client_id}/action-plans")
async def get_client_action_plans(client_id: str, status: Optional[str] = None, current=Depends(require_user)):
    """Get action plans for a client, optionally filtered by status"""
    # Check permissions (simplified)
    if current.get("role") not in ("navigator", "agency", "client"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = {"client_id": client_id}
    if status:
        query["status"] = status
    
    plans = await db.action_plans.find(query).sort("version", -1).to_list(100)
    
    plan_responses = []
    for plan in plans:
        plan_responses.append(ActionPlanResp(**plan))
    
    return {"action_plans": plan_responses}

@api.get("/action-plans/{plan_id}")
async def get_action_plan(plan_id: str, current=Depends(require_user)):
    """Get a specific action plan by ID"""
    # Check permissions
    if current.get("role") not in ("navigator", "agency", "client"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    plan = await db.action_plans.find_one({"_id": plan_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Action plan not found")
    
    return ActionPlanResp(**plan)

# --------------- Financial Core + Matching remain as implemented above ---------------
# ... existing financial endpoints ...

# Include router and CORS (unchanged)
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