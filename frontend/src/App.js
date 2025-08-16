import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
  useEffect(() => {
    if (token) axios.defaults.headers.common["Authorization"] = `Bearer ${token}`; else delete axios.defaults.headers.common["Authorization"];
  }, [token]);
  const login = async (email, password) => {
    const { data } = await axios.post(`${API}/auth/login`, { email, password });
    axios.defaults.headers.common["Authorization"] = `Bearer ${data.access_token}`;
    setToken(data.access_token);
    localStorage.setItem("polaris_token", data.access_token);
    const { data: profile } = await axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${data.access_token}` } });
    setMe(profile);
    localStorage.setItem("polaris_me", JSON.stringify(profile));
    toast.success("Welcome back!", { description: profile.email });
  };
  const register = async (email, password, role) => {
    await axios.post(`${API}/auth/register`, { email, password, role });
    await login(email, password);
    toast.success("Account created", { description: `Role: ${role}` });
  };
  const logout = () => { setToken(""); setMe(null); localStorage.removeItem("polaris_token"); localStorage.removeItem("polaris_me"); toast("Logged out"); };
  return { token, me, login, register, logout };
}

function useSession(isAuthed) {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("polaris_session_id") || "");
  useEffect(() => {
    async function ensure() {
      if (!isAuthed) return;
      if (!sessionId) {
        const { data } = await axios.post(`${API}/assessment/session`);
        setSessionId(data.session_id);
        localStorage.setItem("polaris_session_id", data.session_id);
      }
    }
    ensure();
  }, [sessionId, isAuthed]);
  return sessionId;
}

function useSchema(isAuthed) {
  const [schema, setSchema] = useState(null);
  useEffect(() => {
    if (!isAuthed) return;
    axios.get(`${API}/assessment/schema`).then(({ data }) => setSchema(data)).catch(()=>{});
  }, [isAuthed]);
  return schema;
}

// ---------- Shared UI ----------
function ProgressBar({ sessionId }) {
  const [progress, setProgress] = useState(null);
  useEffect(() => {
    if (!sessionId) return;
    const fetcher = async () => { try { const { data } = await axios.get(`${API}/assessment/session/${sessionId}/progress`); setProgress(data); } catch {} };
    fetcher(); const t = setInterval(fetcher, 5000); return () => clearInterval(t);
  }, [sessionId]);
  const pct = progress?.percent_complete || 0;
  return (
    <div className="mt-2">
      <div className="progress-wrap"><div className="progress-bar" style={{ width: `${pct}%` }} /></div>
      <div className="text-xs text-slate-600 mt-1">Readiness: {pct}%</div>
    </div>
  );
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
  if (auth.me) { return (<div className="auth"><span className="text-sm">{auth.me.email} • {auth.me.role}</span><Link className="link" to="/assessment">Assessment</Link>{auth.me.role === "client" && <Link className="link" to="/matching">Matching</Link>}{auth.me.role === "provider" && <Link className="link" to="/provider">Provider</Link>}{auth.me.role === "navigator" && <Link className="link" to="/navigator">Navigator</Link>}{auth.me.role === "agency" && <Link className="link" to="/agency">Agency</Link>}<button className="btn" onClick={()=>{auth.logout(); navigate("/");}}>Logout</button></div>); }
  return (
    <div className="auth" id="auth">
      <select className="input" value={mode} onChange={(e)=>{ setMode(e.target.value); localStorage.setItem('polaris_auth_mode', e.target.value); }}>
        <option value="login">Login</option>
        <option value="register">Register</option>
      </select>
      <input className="input" placeholder="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
      <input className="input" placeholder="password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
      {mode==='register' && (<select className="input" value={role} onChange={(e)=>setRole(e.target.value)}><option value="client">client</option><option value="navigator">navigator</option><option value="provider">provider</option><option value="agency">agency</option></select>)}
      <button className="btn btn-primary" onClick={async()=>{ try{ if(mode==='login') await auth.login(email,password); else await auth.register(email,password,role); const profile = JSON.parse(localStorage.getItem('polaris_me') || '{}'); if (profile?.role === 'navigator') navigate('/navigator'); else if (profile?.role === 'provider') navigate('/provider'); else if (profile?.role === 'client') navigate('/assessment'); else navigate('/assessment'); }catch(e){ const msg = e?.response?.data?.detail || e.message; toast.error("Auth failed", { description: msg.includes('Invalid credentials') ? 'No account found. Please switch to Register.' : msg }); } }}>{mode==='login'? 'Sign in':'Create account'}</button>
    </div>
  );
}

// ---------- Assessment UI ----------
function DeliverablesHint({ sessionId, area, q }){
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const get = async () => {
    try {
      setLoading(true);
      const { data } = await axios.post(`${API}/ai/explain`, { session_id: sessionId, area_id: area.id, question_id: q.id, question_text: q.text });
      setMsg(data.message);
    } catch (e) { setMsg("AI unavailable."); }
    finally { setLoading(false); }
  };
  return (
    <div className="mt-2">
      <button className="btn" onClick={get} disabled={loading}>{loading ? 'Thinking…' : 'Deliverables (AI)'}</button>
      {msg && <div className="ai-note whitespace-pre-wrap">{msg}</div>}
    </div>
  );
}

function QuestionCard({ area, q, sessionId, saveAnswer, current }) {
  const [uploadPct, setUploadPct] = useState(0);
  const [files, setFiles] = useState([]);
  useEffect(() => { let cancelled=false; async function load(){ if(!sessionId) return; try{ const {data}=await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`); if(!cancelled) setFiles(data.evidence||[]);}catch{}} load(); return ()=>{cancelled=true}; }, [sessionId, area.id, q.id]);
  const yes = current?.value === true; const no = current?.value === false;
  const onFile = async (e) => { const file = e.target.files?.[0]; if(!file) return; setUploadPct(0); const res = await (async()=>{ const init = await axios.post(`${API}/upload/initiate`, { file_name: file.name, total_size: file.size, mime_type: file.type, session_id: sessionId, area_id: area.id, question_id: q.id }); const uploadId=init.data.upload_id; const chunkSize=init.data.chunk_size; const totalChunks=Math.ceil(file.size / chunkSize); for(let i=0;i<totalChunks;i++){ const start=i*chunkSize; const end=Math.min(start+chunkSize, file.size); const blob=file.slice(start,end); const fd=new FormData(); fd.append("upload_id", uploadId); fd.append("chunk_index", String(i)); fd.append("file", blob, `${file.name}.part`); await fetch(`${API}/upload/chunk`, { method: 'POST', body: fd }); setUploadPct(Math.round(((i+1)/totalChunks)*100)); } const done = await axios.post(`${API}/upload/complete`, { upload_id: uploadId, total_chunks: totalChunks }); return { uploadId, ...done.data }; })(); toast.success("File uploaded", { description: res.upload_id.slice(0,8) }); const evidence_ids = [res.upload_id, ...((current?.evidence_ids) || [])]; await saveAnswer(area.id, q.id, true, evidence_ids); const { data } = await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`); setFiles(data.evidence || []); };
  return (
    <div className="q-card">
      <div className="q-label flex items-center gap-2">
        <span>{q.text}</span>
        <span className="badge" title="We never ask for PII or sensitive financials">Sensitive-safe</span>
      </div>
      <div className="q-actions">
        <div className="toggle border-slate-300">
          <button className={yes ? "on" : ""} onClick={() => saveAnswer(area.id, q.id, true, current?.evidence_ids || [])}>Yes</button>
          <button className={no ? "off" : ""} onClick={() => saveAnswer(area.id, q.id, false, [])}>No</button>
        </div>
        <DeliverablesHint sessionId={sessionId} area={area} q={q} />
        {yes && (
          <div className="upload-box">
            <div className="text-xs mb-1">Upload supporting evidence</div>
            <input type="file" onChange={onFile} />
            {uploadPct > 0 && uploadPct < 100 && (<div className="mt-1 text-xs">Uploading... {uploadPct}%</div>)}
            {files?.length ? (
              <div className="mt-2">
                <div className="text-xs font-medium mb-1">Attached</div>
                <ul className="list-disc pl-5">
                  {files.map((f) => (
                    <li key={f.upload_id} className="flex items-center gap-2">
                      <span>{f.file_name}</span>
                      <span className={`status-pill ${f.status === 'approved' ? 'status-approved' : f.status === 'rejected' ? 'status-rejected' : 'status-pending'}`}>{f.status}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

function AssessmentApp() {
  const authed = !!localStorage.getItem('polaris_token');
  const sessionId = useSession(authed);
  const schema = useSchema(authed);
  const [activeArea, setActiveArea] = useState(null);
  const [answers, setAnswers] = useState({});
  useEffect(()=>{ async function load(){ if(!sessionId) return; try{ const { data } = await axios.get(`${API}/assessment/session/${sessionId}`); const amap={}; for(const a of data.answers||[]){ if(!amap[a.area_id]) amap[a.area_id]={}; amap[a.area_id][a.question_id]={ value:a.value, evidence_ids:a.evidence_ids||[]}; } setAnswers(amap);}catch{}} load(); },[sessionId]);
  useEffect(()=>{ if(schema && !activeArea) setActiveArea(schema.areas[0]); },[schema]);
  const saveAnswer = async (areaId,qId,value,evidence_ids)=>{ setAnswers(prev=>({...prev,[areaId]:{...(prev[areaId]||{}),[qId]:{ value, evidence_ids:evidence_ids||[] }}})); if(!sessionId) return; await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers:[{ area_id: areaId, question_id: qId, value, evidence_ids }]}); };
  const saveAll = async ()=>{ if(!sessionId || !schema) return; const payload=[]; for(const area of schema.areas){ const amap=answers[area.id]||{}; for(const q of area.questions){ const a=amap[q.id]; if(a) payload.push({ area_id:area.id, question_id:q.id, value:a.value, evidence_ids:a.evidence_ids||[] }); } } if(payload.length){ await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers: payload }); toast.success("Progress saved"); } };
  if(!schema) return <div className="container mt-6"><div className="skel h-8 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  return (
    <div className="container" id="assessment-root">
      <div className="grid-layout">
        <aside className="sidebar">
          <div className="text-sm font-semibold mb-2">Business Areas</div>
          {schema.areas.map((a) => (
            <div key={a.id} className={`area-item ${activeArea?.id === a.id ? "area-active" : ""}`} onClick={() => setActiveArea(a)}>
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              <span>{a.title}</span>
            </div>
          ))}
          <div className="mt-4"><button className="btn btn-primary w-full" onClick={saveAll}>Save Progress</button></div>
        </aside>
        <section className="main">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">{activeArea?.title}</h2>
            <div className="text-xs text-slate-500">Answer Yes/No and attach the specific deliverable(s) for attestation.</div>
          </div>
          {activeArea?.questions.map((q) => (
            <QuestionCard key={q.id} area={activeArea} q={q} sessionId={sessionId} saveAnswer={saveAnswer} current={(answers[activeArea.id]||{})[q.id]} />
          ))}
        </section>
      </div>
    </div>
  );
}

// ---------- Navigator / Provider / Matching (re-enabled minimal pages) ----------
function NavigatorPanel(){
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState('pending');
  useEffect(()=>{ const load = async()=>{ try{ const {data} = await axios.get(`${API}/navigator/reviews?status=${status}`); setItems(data.reviews||[]);}catch(e){}}; load(); },[status]);
  const decide = async(id, decision)=>{ try{ await axios.post(`${API}/navigator/reviews/${id}/decision`, { decision }); toast.success(`Marked ${decision}`); const {data}=await axios.get(`${API}/navigator/reviews?status=pending`); setItems(data.reviews||[]);}catch(e){ toast.error('Action failed'); } };
  return (
    <div className="container mt-6">
      <div className="flex items-center justify-between mb-3"><h2 className="text-lg font-semibold">Navigator Review Queue</h2>
        <select className="input" value={status} onChange={(e)=>setStatus(e.target.value)}>
          <option value="pending">pending</option>
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
        </select>
      </div>
      <table className="table">
        <thead><tr><th>Area</th><th>Question</th><th>File</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {items.map(it=> (
            <tr key={it.id}><td>{it.area_title}</td><td className="max-w-md truncate" title={it.question_text}>{it.question_text}</td><td>{it.file_name}</td><td>{it.status}</td><td className="flex gap-2">{it.status==='pending' && (<>
              <button className="btn" onClick={()=>decide(it.id,'approved')}>Approve</button>
              <button className="btn" onClick={()=>decide(it.id,'rejected')}>Reject</button>
            </>)}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProviderProfilePage(){
  const [form, setForm] = useState({ company_name: '', service_areas: '', price_min: '', price_max: '', availability: '', location: '' });
  useEffect(()=>{ const load = async()=>{ try{ const {data} = await axios.get(`${API}/provider/profile/me`); if(data){ setForm({ company_name: data.company_name||'', service_areas: (data.service_areas||[]).join(', '), price_min: data.price_min||'', price_max: data.price_max||'', availability: data.availability||'', location: data.location||'' }); } }catch{} }; load(); },[]);
  const save = async()=>{
    try{
      const payload = { ...form, service_areas: form.service_areas.split(',').map(s=>s.trim()).filter(Boolean), price_min: form.price_min? Number(form.price_min): null, price_max: form.price_max? Number(form.price_max): null };
      const {data} = await axios.post(`${API}/provider/profile`, payload);
      toast.success('Profile saved', { description: data.company_name });
    }catch(e){ toast.error('Save failed'); }
  };
  return (
    <div className="container mt-6">
      <h2 className="text-lg font-semibold mb-3">Provider Profile</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input className="input" placeholder="Company name" value={form.company_name} onChange={e=>setForm({...form, company_name:e.target.value})} />
        <input className="input" placeholder="Service areas (comma-separated)" value={form.service_areas} onChange={e=>setForm({...form, service_areas:e.target.value})} />
        <input className="input" placeholder="Min price" value={form.price_min} onChange={e=>setForm({...form, price_min:e.target.value})} />
        <input className="input" placeholder="Max price" value={form.price_max} onChange={e=>setForm({...form, price_max:e.target.value})} />
        <input className="input" placeholder="Availability" value={form.availability} onChange={e=>setForm({...form, availability:e.target.value})} />
        <input className="input" placeholder="Location" value={form.location} onChange={e=>setForm({...form, location:e.target.value})} />
      </div>
      <div className="mt-3"><button className="btn btn-primary" onClick={save}>Save profile</button></div>
    </div>
  );
}

function MatchingPage(){
  const [req, setReq] = useState({ budget: '', payment_pref: '', timeline: '', area_id: 'area6', description: '' });
  const [requestId, setRequestId] = useState('');
  const [matches, setMatches] = useState([]);
  const createReq = async()=>{
    try{
      const payload = { ...req, budget: Number(req.budget) };
      const {data} = await axios.post(`${API}/match/request`, payload);
      setRequestId(data.request_id);
      toast.success('Request created');
      const r2 = await axios.get(`${API}/match/${data.request_id}/matches`);
      setMatches(r2.data.matches||[]);
    }catch(e){ toast.error('Create request failed'); }
  };
  return (
    <div className="container mt-6">
      <h2 className="text-lg font-semibold mb-3">Provider Matching</h2>
      {!requestId && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input className="input" placeholder="Budget" value={req.budget} onChange={e=>setReq({...req, budget:e.target.value})} />
          <input className="input" placeholder="Payment preference (optional)" value={req.payment_pref} onChange={e=>setReq({...req, payment_pref:e.target.value})} />
          <input className="input" placeholder="Timeline" value={req.timeline} onChange={e=>setReq({...req, timeline:e.target.value})} />
          <select className="input" value={req.area_id} onChange={e=>setReq({...req, area_id:e.target.value})}>
            <option value="area1">Business Formation &amp; Registration</option>
            <option value="area2">Financial Operations</option>
            <option value="area3">Legal &amp; Contracting</option>
            <option value="area4">Technology &amp; Cybersecurity</option>
            <option value="area5">People &amp; HR</option>
            <option value="area6">Marketing &amp; Sales</option>
            <option value="area7">Procurement &amp; Supply Chain</option>
            <option value="area8">Quality &amp; Continuous Improvement</option>
          </select>
          <input className="input" placeholder="Short description" value={req.description} onChange={e=>setReq({...req, description:e.target.value})} />
        </div>
      )}
      {!requestId ? (<div className="mt-3"><button className="btn btn-primary" onClick={createReq}>Create request</button></div>) : (
        <div className="mt-4">
          <div className="text-sm text-slate-600 mb-2">Top matches</div>
          <table className="table">
            <thead><tr><th>Company</th><th>Areas</th><th>Location</th><th>Price range</th><th>Score</th></tr></thead>
            <tbody>
              {matches.map(m => (
                <tr key={m.provider_id}><td>{m.company_name}</td><td>{(m.service_areas||[]).join(', ')}</td><td>{m.location||'-'}</td><td>{m.price_min||'-'} - {m.price_max||'-'}</td><td>{m.score}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function ProtectedRoute({ authed, children }) { return authed ? children : <Navigate to="/" replace />; }
function RoleRoute({ me, role, children }){ return (me &amp;&amp; me.role===role) ? children : <Navigate to="/" replace />; }

function AppShell(){ const auth=useAuth(); const location=useLocation(); const authed=!!auth.me; const showHero=!authed &amp;&amp; location.pathname==='/' ; const sessionId=useSession(authed); return (<div className="app-shell"><header className="header"><div className="header-inner"><PolarisLogo /><div className="flex-1">{authed &amp;&amp; <ProgressBar sessionId={sessionId} />}</div><HeaderCTA authed={authed} /><AuthBar auth={auth} /></div></header>{showHero &amp;&amp; (<><section className="hero"><div className="hero-inner"><div className="flex-1 text-white"><PolarisLogo size={28} /><h1 className="hero-title mt-2">Your North Star for Procurement Readiness</h1><p className="hero-sub">Polaris streamlines small business maturity to prepare for opportunity</p><div className="hero-ctas"><button className="btn btn-primary" onClick={()=>{ const el=document.getElementById('auth'); if(el) el.scrollIntoView({behavior:'smooth'}); localStorage.setItem('polaris_auth_mode','register'); }}>Create an account</button><button className="btn" onClick={()=>{ const el=document.getElementById('auth'); if(el) el.scrollIntoView({behavior:'smooth'}); localStorage.setItem('polaris_auth_mode','login'); }}>Sign in</button></div></div></div></section></>)}<Routes><Route path="/" element={authed ? <Navigate to="/assessment" /> : <div />} /><Route path="/assessment" element={<ProtectedRoute authed={authed}><AssessmentApp /></ProtectedRoute>} /><Route path="/navigator" element={<RoleRoute me={auth.me} role="navigator"><NavigatorPanel /></RoleRoute>} /><Route path="/provider" element={<RoleRoute me={auth.me} role="provider"><ProviderProfilePage /></RoleRoute>} /><Route path="/matching" element={<RoleRoute me={auth.me} role="client"><MatchingPage /></RoleRoute>} /></Routes><Toaster richColors position="top-center" /></div>); }

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }