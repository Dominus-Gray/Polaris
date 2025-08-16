import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ---------- Inline brand illustrations (SVG) ----------
function IlluAssessment() {
  return (
    <svg width="160" height="120" viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="20" width="220" height="120" rx="10" fill="#EAF2FF"/>
      <rect x="25" y="40" width="140" height="10" rx="5" fill="#1B365D"/>
      <circle cx="50" cy="90" r="10" fill="#1B365D"/>
      <rect x="65" y="84" width="120" height="12" rx="6" fill="#BFD7FF"/>
      <circle cx="50" cy="120" r="10" fill="#1B365D"/>
      <rect x="65" y="114" width="100" height="12" rx="6" fill="#D7E6FF"/>
      <path d="M25 65 H210" stroke="#4A90C2" strokeWidth="2" strokeDasharray="4 6" />
      <circle cx="90" cy="65" r="5" fill="#4A90C2"/>
      <circle cx="150" cy="65" r="5" fill="#4A90C2"/>
      <circle cx="210" cy="65" r="5" fill="#4A90C2"/>
    </svg>
  );
}
function IlluEvidence() {
  return (
    <svg width="160" height="120" viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg">
      <rect x="40" y="20" width="160" height="120" rx="8" fill="#EAF7F0"/>
      <rect x="55" y="35" width="130" height="12" rx="6" fill="#1B365D"/>
      <rect x="55" y="60" width="100" height="8" rx="4" fill="#A3E3C2"/>
      <rect x="55" y="78" width="120" height="8" rx="4" fill="#C8F0DA"/>
      <rect x="55" y="96" width="80" height="8" rx="4" fill="#E8FFF3"/>
      <circle cx="185" cy="105" r="18" fill="#28A745"/>
      <path d="M178 106 l6 6 l12 -14" stroke="#fff" strokeWidth="4" fill="none" strokeLinecap="round"/>
      <rect x="20" y="140" width="200" height="6" rx="3" fill="#CCEAD8"/>
    </svg>
  );
}
function IlluMatching() {
  return (
    <svg width="160" height="120" viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg">
      <circle cx="120" cy="90" r="60" fill="#EAF2FF"/>
      <circle cx="80" cy="70" r="14" fill="#1B365D"/>
      <circle cx="160" cy="70" r="14" fill="#1B365D"/>
      <circle cx="120" cy="120" r="14" fill="#1B365D"/>
      <path d="M80 70 L160 70 L120 120 Z" fill="none" stroke="#4A90C2" strokeWidth="3"/>
      <text x="118" y="92" fontSize="14" fill="#1B365D" textAnchor="middle">$</text>
    </svg>
  );
}

// ---------- Branding ----------
function PolarisLogo({ size = 22 }) {
  return (
    <div className="flex items-center gap-2" aria-label="Polaris">
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 1 L13.8 8.2 L21 10 L13.8 11.8 L12 19 L10.2 11.8 L3 10 L10.2 8.2 Z" fill="#1B365D"/>
        <path d="M12 5 L12.9 7.8 L15.5 8.6 L12.9 9.4 L12 12.2 L11.1 9.4 L8.5 8.6 L11.1 7.8 Z" fill="#4A90C2"/>
      </svg>
      <span className="font-semibold tracking-tight" style={{color:'#1B365D'}}>POLARIS</span>
    </div>
  );
}

// ---------- Auth Hooks ----------
function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("polaris_token") || "");
  const [me, setMe] = useState(() => {
    const cached = localStorage.getItem("polaris_me");
    return cached ? JSON.parse(cached) : null;
  });
  useEffect(() => { if (token) axios.defaults.headers.common["Authorization"] = `Bearer ${token}`; else delete axios.defaults.headers.common["Authorization"]; }, [token]);
  const login = async (email, password) => { const { data } = await axios.post(`${API}/auth/login`, { email, password }); axios.defaults.headers.common["Authorization"] = `Bearer ${data.access_token}`; setToken(data.access_token); localStorage.setItem("polaris_token", data.access_token); const { data: profile } = await axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${data.access_token}` } }); setMe(profile); localStorage.setItem("polaris_me", JSON.stringify(profile)); toast.success("Welcome back!", { description: profile.email }); };
  const register = async (email, password, role) => { await axios.post(`${API}/auth/register`, { email, password, role }); await login(email, password); toast.success("Account created", { description: `Role: ${role}` }); };
  const logout = () => { setToken(""); setMe(null); localStorage.removeItem("polaris_token"); localStorage.removeItem("polaris_me"); toast("Logged out"); };
  return { token, me, login, register, logout };
}

function useSession(isAuthed) {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("polaris_session_id") || "");
  useEffect(() => { async function ensure(){ if(!isAuthed) return; if(!sessionId){ const { data } = await axios.post(`${API}/assessment/session`); setSessionId(data.session_id); localStorage.setItem("polaris_session_id", data.session_id); } } ensure(); }, [sessionId, isAuthed]);
  return sessionId;
}

function useSchema(isAuthed) {
  const [schema, setSchema] = useState(null);
  useEffect(() => { if(!isAuthed) return; axios.get(`${API}/assessment/schema`).then(({data})=>setSchema(data)).catch(()=>{}); }, [isAuthed]);
  return schema;
}

// ---------- Shared UI ----------
function ProgressBar({ sessionId }) {
  const [progress, setProgress] = useState(null);
  useEffect(() => { if(!sessionId) return; const fetcher = async ()=>{ try{ const { data } = await axios.get(`${API}/assessment/session/${sessionId}/progress`); setProgress(data);}catch{}}; fetcher(); const t=setInterval(fetcher,5000); return ()=>clearInterval(t); }, [sessionId]);
  const pct = progress?.percent_complete || 0; return (<div className="mt-2"><div className="progress-wrap"><div className="progress-bar" style={{ width: `${pct}%` }} /></div><div className="text-xs text-slate-600 mt-1">Readiness: {pct}%</div></div>);
}

function HeaderCTA({ authed }){
  const scrollToAuth = (mode) => { if (mode) localStorage.setItem('polaris_auth_mode', mode); const el=document.getElementById('auth'); if(el) el.scrollIntoView({behavior:'smooth'}); };
  if (authed) return null;
  return (
    <div className="flex items-center gap-2">
      <button className="btn" onClick={()=>scrollToAuth('login')}>Sign in</button>
      <button className="btn btn-primary" onClick={()=>scrollToAuth('register')}>Create account</button>
    </div>
  );
}

function AuthBar({ auth }) {
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [role, setRole] = useState("client"); const [mode, setMode] = useState(() => localStorage.getItem('polaris_auth_mode') || 'login'); const navigate = useNavigate();
  if (auth.me) { return (<div className="auth"><span className="text-sm">{auth.me.email} • {auth.me.role}</span><Link className="link" to="/assessment">Assessment</Link>{auth.me.role === "client" && <Link className="link" to="/matching">Matching</Link>}{auth.me.role === "provider" && <Link className="link" to="/provider">Provider</Link>}{auth.me.role === "navigator" && <Link className="link" to="/navigator">Navigator</Link>}<button className="btn" onClick={()=>{auth.logout(); navigate("/");}}>Logout</button></div>); }
  return (
    <div className="auth" id="auth">
      <select className="input" value={mode} onChange={(e)=>{ setMode(e.target.value); localStorage.setItem('polaris_auth_mode', e.target.value); }}>
        <option value="login">Login</option>
        <option value="register">Register</option>
      </select>
      <input className="input" placeholder="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
      <input className="input" placeholder="password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
      {mode==='register' && (<select className="input" value={role} onChange={(e)=>setRole(e.target.value)}><option value="client">client</option><option value="navigator">navigator</option><option value="provider">provider</option></select>)}
      <button className="btn btn-primary" onClick={async()=>{ try{ if(mode==='login') await auth.login(email,password); else await auth.register(email,password,role);}catch(e){ toast.error("Auth failed", { description: e?.response?.data?.detail || e.message }); } }}>{mode==='login'? 'Sign in':'Create account'}</button>
    </div>
  );
}

// ---------- Landing ----------
function BrandHero() {
  const scrollToAuth = (mode) => { if (mode) localStorage.setItem('polaris_auth_mode', mode); const el=document.getElementById('auth'); if(el) el.scrollIntoView({ behavior: 'smooth' }); };
  return (
    <section className="hero">
      <div className="hero-bg" style={{ backgroundImage: 'linear-gradient(135deg,#0b1224 0%,#1B365D 60%,#0b1224 100%)' }} />
      <div className="hero-inner">
        <div className="flex-1 text-white">
          <PolarisLogo size={28} />
          <h1 className="hero-title mt-2">Your North Star for Procurement Readiness</h1>
          <p className="hero-sub">Polaris streamlines small business maturity to prepare for opportunity readiness — all in one place</p>
          <div className="hero-ctas">
            <button className="btn btn-primary" onClick={()=>scrollToAuth('register')}>Create an account</button>
            <button className="btn" onClick={()=>scrollToAuth('login')}>Sign in</button>
          </div>
        </div>
      </div>
    </section>
  );
}

function FeatureHighlights() {
  return (
    <div className="container">
      <div className="features">
        <div className="card">
          <div className="card-visual"><IlluAssessment /></div>
          <div className="card-body"><div className="card-title">Small Business Maturity Assessment</div><div className="card-sub">Over 80 guided assessment questions across 8 key business areas with progress tracking.</div></div>
        </div>
        <div className="card">
          <div className="card-visual"><IlluEvidence /></div>
          <div className="card-body"><div className="card-title">Evidence Review</div><div className="card-sub">Chunked uploads, navigator approvals, secure downloads, audit notes.</div></div>
        </div>
        <div className="card">
          <div className="card-visual"><IlluMatching /></div>
          <div className="card-body"><div className="card-title">Provider Matching</div><div className="card-sub">Budget-aware ranking and first-5 response to accelerate engagements.</div></div>
        </div>
      </div>
    </div>
  );
}

function ValueForSMBs() { const go=()=>{ localStorage.setItem('polaris_auth_mode','register'); const el=document.getElementById('auth'); if(el) el.scrollIntoView({behavior:'smooth'}); }; return (<section className="section container"><h3 className="section-title">Why small businesses choose Polaris</h3><p className="section-sub">Reduce months of uncertainty into weeks of guided progress with clear next steps and measurable outcomes.</p><div className="pillars"><div className="pillar"><div className="icon">✓</div><div className="card-title mt-2">Clear roadmap</div><div className="card-sub">Straightforward questions with concise guidance and action tips for every requirement.</div></div><div className="pillar"><div className="icon">🔒</div><div className="card-title mt-2">Secure evidence</div><div className="card-sub">Encrypted uploads, approvals, and audit notes—designed for trust and compliance.</div></div><div className="pillar"><div className="icon">⭐</div><div className="card-title mt-2">Faster wins</div><div className="card-sub">Get matched to the right providers within budget and timeline—first five respond fast.</div></div></div><div className="mt-4"><button className="btn btn-primary" onClick={go}>Create free account</button></div></section>); }
function ValueForProviders() { const go=()=>{ localStorage.setItem('polaris_auth_mode','register'); const el=document.getElementById('auth'); if(el) el.scrollIntoView({behavior:'smooth'}); }; return (<section className="section container"><h3 className="section-title">Why service providers partner with Polaris</h3><p className="section-sub">Predictable, qualified opportunities with budget visibility and faster onboarding.</p><div className="pillars"><div className="pillar"><div className="icon">🎯</div><div className="card-title mt-2">Qualified leads</div><div className="card-sub">Requests include budget, timeline, and needs so you engage where you win.</div></div><div className="pillar"><div className="icon">⚡</div><div className="card-title mt-2">First-5 advantage</div><div className="card-sub">Respond early, earn visibility, and convert faster with a streamlined intake.</div></div><div className="pillar"><div className="icon">📈</div><div className="card-title mt-2">Reputation that grows</div><div className="card-sub">Track outcomes, build trust, and stand out for future matches.</div></div></div><div className="mt-4"><button className="btn" onClick={go}>Join as provider</button></div></section>); }

// ---------- App Pages (Assessment/Navigator/Provider/Matching) ----------
function QuestionCard({ area, q, sessionId, saveAnswer, current }) { const [aiMsg,setAiMsg]=useState(""); const [uploadPct,setUploadPct]=useState(0); const [files,setFiles]=useState([]); useEffect(()=>{ let cancelled=false; async function load(){ if(!sessionId) return; try{ const {data}=await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`); if(!cancelled) setFiles(data.evidence||[]);}catch{}} load(); return ()=>{cancelled=true}; },[sessionId,area.id,q.id]); const yes=current?.value===true; const no=current?.value===false; const askAI=async()=>{ try{ setAiMsg("Thinking..."); const {data}=await axios.post(`${API}/ai/explain`, { session_id: sessionId, area_id: area.id, question_id: q.id, question_text: q.text }); setAiMsg(data.message);}catch{ setAiMsg("AI unavailable."); } }; const onFile=async(e)=>{ const file=e.target.files?.[0]; if(!file) return; setUploadPct(0); const res=await (async()=>{ const init=await axios.post(`${API}/upload/initiate`, { file_name:file.name, total_size:file.size, mime_type:file.type, session_id:sessionId, area_id:area.id, question_id:q.id }); const uploadId=init.data.upload_id; const chunkSize=init.data.chunk_size; const totalChunks=Math.ceil(file.size/chunkSize); for(let i=0;i<totalChunks;i++){ const start=i*chunkSize; const end=Math.min(start+chunkSize,file.size); const blob=file.slice(start,end); const fd=new FormData(); fd.append("upload_id",uploadId); fd.append("chunk_index",String(i)); fd.append("file",blob,`${file.name}.part`); await fetch(`${API}/upload/chunk`,{method:'POST',body:fd}); setUploadPct(Math.round(((i+1)/totalChunks)*100)); } const done=await axios.post(`${API}/upload/complete`, { upload_id: uploadId, total_chunks: totalChunks }); return { uploadId, ...done.data }; })(); toast.success("File uploaded", { description: res.upload_id.slice(0,8) }); const evidence_ids=[res.upload_id,...((current?.evidence_ids)||[])]; await saveAnswer(area.id,q.id,true,evidence_ids); const {data}=await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`); setFiles(data.evidence||[]); }; const removeFile=async(upload_id)=>{ try{ await axios.delete(`${API}/upload/${upload_id}`); const {data}=await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`); setFiles(data.evidence||[]); const remaining=(current?.evidence_ids||[]).filter((id)=>id!==upload_id); await saveAnswer(area.id,q.id,current?.value ?? true,remaining); toast("Attachment removed"); }catch(e){ toast.error("Failed to remove file", { description: e?.response?.data?.detail || e.message }); } }; const downloadFile=async(upload_id,file_name)=>{ try{ const {data}=await axios.get(`${API}/upload/${upload_id}/download`, { responseType:'blob' }); const url=window.URL.createObjectURL(new Blob([data])); const a=document.createElement('a'); a.href=url; a.download=file_name||'evidence'; document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url); toast.success("Download started"); }catch(e){ toast.error("Download failed", { description: e?.response?.data?.detail || e.message }); } }; return (<div className="q-card"><div className="q-label">{q.text}</div><div className="q-actions"><div className="toggle border-slate-300"><button className={yes?"on":""} onClick={()=>saveAnswer(area.id,q.id,true,current?.evidence_ids||[])}>Yes</button><button className={no?"off":""} onClick={()=>saveAnswer(area.id,q.id,false,[])}>No</button></div><button className="btn" onClick={askAI}>Why this matters? (AI)</button>{yes && (<div className="upload-box"><div className="text-xs mb-1">Upload supporting evidence</div><input type="file" onChange={onFile} />{uploadPct>0 && uploadPct<100 && (<div className="mt-1 text-xs">Uploading... {uploadPct}%</div>)}{files?.length ? (<div className="mt-2"><div className="text-xs font-medium mb-1">Attached</div><ul className="list-disc pl-5">{files.map((f)=>(<li key={f.upload_id} className="flex items-center gap-2"><span>{f.file_name}</span><span className={`status-pill ${f.status==='approved'?'status-approved':f.status==='rejected'?'status-rejected':'status-pending'}`}>{f.status}</span><button className="link" onClick={()=>downloadFile(f.upload_id,f.file_name)}>download</button><button className="link" onClick={()=>removeFile(f.upload_id)}>remove</button></li>))}</ul></div>):null}</div>)}</div>{aiMsg && <div className="ai-note">{aiMsg}</div>}</div>); }

function AssessmentApp() { const authed=!!localStorage.getItem('polaris_token'); const sessionId=useSession(authed); const schema=useSchema(authed); const [activeArea,setActiveArea]=useState(null); const [answers,setAnswers]=useState({}); useEffect(()=>{ async function load(){ if(!sessionId) return; try{ const {data}=await axios.get(`${API}/assessment/session/${sessionId}`); const amap={}; for(const a of data.answers||[]){ if(!amap[a.area_id]) amap[a.area_id]={}; amap[a.area_id][a.question_id]={ value:a.value, evidence_ids:a.evidence_ids||[]}; } setAnswers(amap);}catch{} } load(); },[sessionId]); useEffect(()=>{ if(schema && !activeArea) setActiveArea(schema.areas[0]); },[schema]); const saveAnswer=async(areaId,qId,value,evidence_ids)=>{ setAnswers(prev=>({...prev,[areaId]:{...(prev[areaId]||{}),[qId]:{ value, evidence_ids:evidence_ids||[] }}})); if(!sessionId) return; await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers:[{ area_id: areaId, question_id: qId, value, evidence_ids }]}); }; const saveAll=async()=>{ if(!sessionId || !schema) return; const payload=[]; for(const area of schema.areas){ const amap=answers[area.id]||{}; for(const q of area.questions){ const a=amap[q.id]; if(a) payload.push({ area_id:area.id, question_id:q.id, value:a.value, evidence_ids:a.evidence_ids||[] }); } } if(payload.length){ await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers: payload }); toast.success("Progress saved"); } }; if(!schema) return <div className="container mt-6"><div className="skel h-8 w-40"/><div className="skel h-32 w-full mt-2"/></div>; return (<div className="container" id="assessment-root"><div className="grid-layout"><aside className="sidebar"><div className="text-sm font-semibold mb-2">Business Areas</div>{schema.areas.map((a)=>(<div key={a.id} className={`area-item ${activeArea?.id===a.id?"area-active":""}`} onClick={()=>setActiveArea(a)}><span className="w-2 h-2 rounded-full bg-indigo-500"/><span>{a.title}</span></div>))}<div className="mt-4"><button className="btn btn-primary w-full" onClick={saveAll}>Save Progress</button></div></aside><section className="main"><div className="flex items-center justify-between mb-3"><h2 className="text-lg font-semibold">{activeArea?.title}</h2><div className="text-xs text-slate-500">Answer Yes/No. If Yes, upload evidence. Approved evidence counts toward readiness.</div></div>{activeArea?.questions.map((q)=>(<QuestionCard key={q.id} area={activeArea} q={q} sessionId={sessionId} saveAnswer={saveAnswer} current={(answers[activeArea.id]||{})[q.id]} />))}</section></div></div>); }

function NavigatorPanel(){ const [items,setItems]=useState([]); const load=async()=>{ const {data}=await axios.get(`${API}/navigator/reviews?status=pending`); setItems(data.reviews||[]); }; useEffect(()=>{ load(); },[]); const decide=async(id,decision)=>{ const notes=decision==='approved'?'OK':prompt('Reason for rejection?')||''; await axios.post(`${API}/navigator/reviews/${id}/decision`, { decision, notes }); toast.success(decision==='approved'?'Approved':'Rejected'); await load(); }; return (<div className="container"><h2 className="text-lg font-semibold mt-6 mb-3">Navigator • Evidence Reviews</h2><table className="table"><thead><tr><th>Area</th><th>Question</th><th>File</th><th>Status</th><th>Action</th></tr></thead><tbody>{items.map((r)=>(<tr key={r.id}><td>{r.area_title}</td><td>{r.question_text}</td><td>{r.file_name}</td><td><span className={`status-pill ${r.status==='approved'?'status-approved':r.status==='rejected'?'status-rejected':'status-pending'}`}>{r.status}</span></td><td className="space-x-2"><button className="btn" onClick={()=>decide(r.id,'approved')}>Approve</button><button className="btn" onClick={()=>decide(r.id,'rejected')}>Reject</button></td></tr>))}{!items.length && (<tr><td colSpan="5" className="text-center text-slate-500">No pending items</td></tr>)}</tbody></table></div>); }

function ProviderProfilePage(){ const schema=useSchema(true); const [company_name,setCompany]=useState(""); const [service_areas,setAreas]=useState([]); const [price_min,setPmin]=useState(""); const [price_max,setPmax]=useState(""); const [availability,setAvail]=useState(""); const [location,setLoc]=useState("San Antonio, TX"); const [eligible,setEligible]=useState([]); useEffect(()=>{(async()=>{ try{ const {data}=await axios.get(`${API}/provider/profile/me`); if(data){ setCompany(data.company_name||""); setAreas(data.service_areas||[]); setPmin(data.price_min||""); setPmax(data.price_max||""); setAvail(data.availability||""); setLoc(data.location||""); } }catch{} try{ const {data:elig}=await axios.get(`${API}/match/eligible`); setEligible(elig.requests||[]);}catch{} })();},[]); const toggleArea=(id)=>{ setAreas(prev=>prev.includes(id)?prev.filter(x=>x!==id):[...prev,id]); }; const save=async()=>{ await axios.post(`${API}/provider/profile`, { company_name, service_areas, price_min: price_min?Number(price_min):null, price_max: price_max?Number(price_max):null, availability, location }); toast.success("Profile saved"); }; const respond=async(id)=>{ const note=prompt("Short proposal note (optional)")||""; const fd=new FormData(); fd.append("request_id", id); fd.append("proposal_note", note); const {data}=await axios.post(`${API}/match/respond`, fd); if(data.ok) toast.success("Responded"); else toast.error(data.reason||"Response failed"); }; return (<div className="container"><h2 className="text-lg font-semibold mt-6 mb-3">Provider Profile</h2><div className="grid grid-cols-1 lg:grid-cols-2 gap-4"><div className="p-4 border rounded bg-white"><div className="mb-2"><label className="block text-sm">Company Name</label><input className="input w-full" value={company_name} onChange={(e)=>setCompany(e.target.value)} /></div><div className="mb-2"><label className="block text-sm">Price Range</label><div className="flex gap-2"><input className="input w-full" placeholder="min" value={price_min} onChange={(e)=>setPmin(e.target.value)} /><input className="input w-full" placeholder="max" value={price_max} onChange={(e)=>setPmax(e.target.value)} /></div></div><div className="mb-2"><label className="block text-sm">Availability</label><input className="input w-full" value={availability} onChange={(e)=>setAvail(e.target.value)} /></div><div className="mb-2"><label className="block text-sm">Location</label><input className="input w-full" value={location} onChange={(e)=>setLoc(e.target.value)} /></div><button className="btn btn-primary" onClick={save}>Save Profile</button></div><div className="p-4 border rounded bg-white"><div className="text-sm font-medium mb-2">Service Areas</div><div className="flex flex-col gap-1">{schema?.areas.map(a=>(<label key={a.id} className="flex items-center gap-2"><input type="checkbox" checked={service_areas.includes(a.id)} onChange={()=>toggleArea(a.id)} />{a.title}</label>))}</div></div></div><div className="mt-6 p-4 border rounded bg-white"><div className="flex items-center justify-between mb-2"><div className="text-sm font-medium">Eligible Requests</div><button className="btn" onClick={async()=>{ const {data}=await axios.get(`${API}/match/eligible`); setEligible(data.requests||[]); }}>Refresh</button></div><table className="table"><thead><tr><th>ID</th><th>Area</th><th>Budget</th><th>Timeline</th><th>Action</th></tr></thead><tbody>{eligible.map(r=>(<tr key={r.id}><td>{r.id.slice(0,8)}</td><td>{r.area_id}</td><td>${r.budget}</td><td>{r.timeline}</td><td><button className="btn" onClick={()=>respond(r.id)}>Respond</button></td></tr>))}{!eligible.length && <tr><td colSpan="5" className="text-center text-slate-500">No eligible requests yet</td></tr>}</tbody></table></div></div>); }

function MatchingPage(){ const schema=useSchema(true); const [area_id,setArea]=useState(""); const [budget,setBudget]=useState(""); const [payment_pref,setPay]=useState("Net 30"); const [timeline,setTime]=useState("2-4 weeks"); const [description,setDesc]=useState(""); const [matches,setMatches]=useState([]); const [requestId,setRequestId]=useState(""); const [responses,setResponses]=useState([]); const submit=async()=>{ if(!area_id || !budget){ toast.error("Select area and budget"); return; } const {data}=await axios.post(`${API}/match/request`, { area_id, budget:Number(budget), payment_pref, timeline, description }); setRequestId(data.request_id); toast.success("Request submitted", { description: data.request_id.slice(0,8) }); const { data: mm } = await axios.get(`${API}/match/${data.request_id}/matches`); setMatches(mm.matches||[]); }; const refreshResponses=async()=>{ if(!requestId) return; const {data}=await axios.get(`${API}/match/${requestId}/responses`); setResponses(data.responses||[]); }; return (<div className="container"><div className="grid lg:grid-cols-3 gap-4 mt-6"><div className="lg:col-span-2"><div className="p-4 border rounded bg-white"><div className="grid grid-cols-1 lg:grid-cols-2 gap-4"><div><label className="block text-sm">Business Area</label><select className="input w-full" value={area_id} onChange={(e)=>setArea(e.target.value)}><option value="">Select area</option>{schema?.areas.map(a=>(<option key={a.id} value={a.id}>{a.title}</option>))}</select></div><div><label className="block text-sm">Budget (USD)</label><input className="input w-full" value={budget} onChange={(e)=>setBudget(e.target.value)} /></div><div><label className="block text-sm">Payment Preference</label><select className="input w-full" value={payment_pref} onChange={(e)=>setPay(e.target.value)}><option>Net 30</option><option>Net 15</option><option>Advance</option></select></div><div><label className="block text-sm">Timeline</label><input className="input w-full" value={timeline} onChange={(e)=>setTime(e.target.value)} /></div><div className="lg:col-span-2"><label className="block text-sm">Describe your need</label><textarea className="input w-full" rows={3} value={description} onChange={(e)=>setDesc(e.target.value)} /></div></div><div className="mt-4 flex items-center gap-2"><button className="btn btn-primary" onClick={submit}>Get Matches</button>{requestId && <button className="btn" onClick={refreshResponses}>Refresh Responses</button>}</div></div>{matches.length>0 && (<div className="mt-6 p-4 border rounded bg-white"><div className="text-sm font-medium mb-2">Top Matches</div><table className="table"><thead><tr><th>Provider</th><th>Areas</th><th>Price Range</th><th>Score</th></tr></thead><tbody>{matches.map(m=>(<tr key={m.provider_id}><td>{m.company_name}</td><td>{(m.service_areas||[]).join(', ')}</td><td>{m.price_min||'-'} - {m.price_max||'-'}</td><td>{m.score}</td></tr>))}</tbody></table></div>)}</div><div className="lg:col-span-1"><div className="p-4 border rounded bg-white"><div className="flex items-center justify-between mb-2"><div className="text-sm font-medium">Responses</div>{requestId && <span className="text-xs text-slate-500">Request {requestId.slice(0,8)}</span>}</div><ul className="space-y-2">{responses.map(r=>(<li key={r.id} className="p-3 border rounded bg-slate-50"><div className="text-sm">Provider: {r.provider_user_id.slice(0,8)}</div><div className="text-xs text-slate-500">{new Date(r.created_at).toLocaleString()}</div>{r.proposal_note && <div className="text-sm mt-1">“{r.proposal_note}”</div>}</li>))}{!responses.length && <li className="text-xs text-slate-500">No responses yet. Providers can respond—first five are accepted.</li>}</ul></div></div></div></div>); }

function ProtectedRoute({ authed, children }) { return authed ? children : <Navigate to="/" replace />; }

function AppShell(){ const auth=useAuth(); const location=useLocation(); const authed=!!auth.me; const showHero=!authed && location.pathname==='/' ; const sessionId=useSession(authed); return (<div className="app-shell"><header className="header"><div className="header-inner"><PolarisLogo /><div className="flex-1">{authed && <ProgressBar sessionId={sessionId} />}</div><HeaderCTA authed={authed} /><AuthBar auth={auth} /></div></header>{showHero && (<><BrandHero /><FeatureHighlights /><ValueForSMBs /><ValueForProviders /></>)}<Routes><Route path="/" element={authed ? <Navigate to="/assessment" /> : <div />} /><Route path="/assessment" element={<ProtectedRoute authed={authed}><AssessmentApp /></ProtectedRoute>} /><Route path="/navigator" element={<ProtectedRoute authed={authed && auth.me?.role==='navigator'}><NavigatorPanel /></ProtectedRoute>} /><Route path="/provider" element={<ProtectedRoute authed={authed && auth.me?.role==='provider'}><ProviderProfilePage /></ProtectedRoute>} /><Route path="/matching" element={<ProtectedRoute authed={authed && auth.me?.role==='client'}><MatchingPage /></ProtectedRoute>} /></Routes><Toaster richColors position="top-center" /></div>); }

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }