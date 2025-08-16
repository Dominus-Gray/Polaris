import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

function VerifyCert(){
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(()=>{ const load=async()=>{ try{ const {data} = await axios.get(`${API}/certificates/${id}/public`); setData(data); }catch(e){ setError(e?.response?.data?.detail || 'Unavailable'); } }; load(); },[id]);
  return (
    <div className="container mt-10 max-w-2xl">
      <h1 className="text-xl font-semibold mb-3">Certificate Verification</h1>
      {error && <div className="alert">{error}</div>}
      {!error && !data && <div className="skel h-24 w-full" />}
      {data && (
        <div className="p-4 border rounded bg-white shadow-sm">
          <div className="text-lg font-medium">{data.title || 'Small Business Maturity Assurance'}</div>
          <div className="text-sm text-slate-600">Certificate ID: {data.id}</div>
          <div className="mt-2 text-sm">Readiness: <span className="font-semibold">{data.readiness_percent}%</span></div>
          <div className="text-sm">Issued at: {new Date(data.issued_at).toLocaleString()}</div>
          <div className="text-xs text-slate-500 mt-2">Sponsoring Agency ID: {data.agency_user_id}</div>
          <div className="mt-3 text-xs text-slate-500">This verification page confirms the certificate details recorded in Polaris.</div>
        </div>
      )}
    </div>
  );
}

// ---------------- Business Profile Form (client & provider) ----------------
function BusinessProfileForm(){
  const navigate = useNavigate();
  const [form, setForm] = useState({ company_name:'', legal_entity_type:'LLC', tax_id:'', registered_address:'', mailing_address:'', website_url:'', industry:'', primary_products_services:'', revenue_range:'', revenue_currency:'USD', employees_count:'', year_founded:'', ownership_structure:'private', contact_name:'', contact_title:'', contact_email:'', contact_phone:'', billing_contact_name:'', billing_contact_email:'', billing_contact_phone:'', payment_methods:'Card, ACH', subscription_plan:'Basic', subscription_features:'', billing_frequency:'monthly' });
  const [logo, setLogo] = useState(null);
  const [missing, setMissing] = useState([]);
  useEffect(()=>{ const load=async()=>{ try{ const {data} = await axios.get(`${API}/business/profile/me`); if(data){ setForm({ ...form, ...data, payment_methods: (data.payment_methods||[]).join(', ')}); } const c = await axios.get(`${API}/business/profile/me/completion`); setMissing(c.data.missing||[]);}catch{} }; load(); },[]);
  const save = async()=>{
    try{
      const payload = { ...form, payment_methods: form.payment_methods.split(',').map(s=>s.trim()).filter(Boolean) };
      const { data } = await axios.post(`${API}/business/profile`, payload); toast.success('Profile saved', { description: data.company_name });
      if (logo){
        const init = await axios.post(`${API}/business/logo/initiate`, new URLSearchParams({ file_name: logo.name, total_size: String(logo.size), mime_type: logo.type }));
        const uploadId = init.data.upload_id; const chunkSize = init.data.chunk_size; const totalChunks = Math.ceil(logo.size / chunkSize);
        for(let i=0;i<totalChunks;i++){
          const start=i*chunkSize; const end=Math.min(start+chunkSize, logo.size); const blob=logo.slice(start,end); const fd=new FormData(); fd.append('upload_id', uploadId); fd.append('chunk_index', String(i)); fd.append('file', blob, `${logo.name}.part`); await fetch(`${API}/business/logo/chunk`, { method:'POST', body: fd }); }
        await axios.post(`${API}/business/logo/complete`, new URLSearchParams({ upload_id: uploadId, total_chunks: String(totalChunks) }));
      }
      navigate('/home');
    }catch(e){ toast.error('Save failed', { description: e?.response?.data?.detail || e.message}); }
  };
  return (
    <div className="container max-w-4xl mt-6">
      <h2 className="text-xl font-semibold mb-1">Business Profile</h2>
      <p className="text-sm text-slate-600 mb-4">Complete these details to unlock your personalized home dashboard.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input className="input" placeholder="Company name" value={form.company_name} onChange={e=>setForm({...form, company_name:e.target.value})} />
        <select className="input" value={form.legal_entity_type} onChange={e=>setForm({...form, legal_entity_type:e.target.value})}>
          <option>LLC</option><option>C-Corp</option><option>S-Corp</option><option>Partnership</option><option>Sole Proprietorship</option>
        </select>
        <input className="input" placeholder="EIN / Tax ID" value={form.tax_id} onChange={e=>setForm({...form, tax_id:e.target.value})} />
        <input className="input" placeholder="Registered business address" value={form.registered_address} onChange={e=>setForm({...form, registered_address:e.target.value})} />
        <input className="input" placeholder="Mailing address" value={form.mailing_address} onChange={e=>setForm({...form, mailing_address:e.target.value})} />
        <input className="input" placeholder="Website URL" value={form.website_url} onChange={e=>setForm({...form, website_url:e.target.value})} />
        <input className="input" placeholder="Industry / Sector" value={form.industry} onChange={e=>setForm({...form, industry:e.target.value})} />
        <input className="input" placeholder="Primary products / services" value={form.primary_products_services} onChange={e=>setForm({...form, primary_products_services:e.target.value})} />
        <input className="input" placeholder="Revenue range (e.g., $0-$100k)" value={form.revenue_range} onChange={e=>setForm({...form, revenue_range:e.target.value})} />
        <select className="input" value={form.revenue_currency} onChange={e=>setForm({...form, revenue_currency:e.target.value})}><option>USD</option><option>MXN</option><option>EUR</option></select>
        <input className="input" placeholder="Employees (range or exact)" value={form.employees_count} onChange={e=>setForm({...form, employees_count:e.target.value})} />
        <input className="input" placeholder="Year founded" value={form.year_founded} onChange={e=>setForm({...form, year_founded:e.target.value})} />
        <input className="input" placeholder="Ownership structure (private/public)" value={form.ownership_structure} onChange={e=>setForm({...form, ownership_structure:e.target.value})} />
        <input className="input" placeholder="Contact name" value={form.contact_name} onChange={e=>setForm({...form, contact_name:e.target.value})} />
        <input className="input" placeholder="Contact title" value={form.contact_title} onChange={e=>setForm({...form, contact_title:e.target.value})} />
        <input className="input" placeholder="Contact email" value={form.contact_email} onChange={e=>setForm({...form, contact_email:e.target.value})} />
        <input className="input" placeholder="Contact phone" value={form.contact_phone} onChange={e=>setForm({...form, contact_phone:e.target.value})} />
        <input className="input" placeholder="Billing contact name" value={form.billing_contact_name} onChange={e=>setForm({...form, billing_contact_name:e.target.value})} />
        <input className="input" placeholder="Billing contact email" value={form.billing_contact_email} onChange={e=>setForm({...form, billing_contact_email:e.target.value})} />
        <input className="input" placeholder="Billing contact phone" value={form.billing_contact_phone} onChange={e=>setForm({...form, billing_contact_phone:e.target.value})} />
        <input className="input" placeholder="Payment methods accepted" value={form.payment_methods} onChange={e=>setForm({...form, payment_methods:e.target.value})} />
        <input className="input" placeholder="Subscription plan (tier)" value={form.subscription_plan} onChange={e=>setForm({...form, subscription_plan:e.target.value})} />
        <input className="input" placeholder="Subscription features (optional)" value={form.subscription_features} onChange={e=>setForm({...form, subscription_features:e.target.value})} />
        <select className="input" value={form.billing_frequency} onChange={e=>setForm({...form, billing_frequency:e.target.value})}><option>monthly</option><option>annual</option></select>
        <div className="col-span-1 md:col-span-2">
          <label className="text-sm font-medium">Business logo</label>
          <input type="file" className="input mt-1" onChange={e=>setLogo(e.target.files?.[0]||null)} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        {missing?.length>0 && <div className="text-xs text-amber-600">Missing: {missing.join(', ')}</div>}
        <button className="btn btn-primary" onClick={save}>Save & Continue</button>
      </div>
    </div>
  );
}

// ---------------- Home Pages ----------------
function ClientHome(){
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/client`); setData(data); }; load(); },[]);
  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="tile"><div className="tile-title">Readiness</div><div className="tile-num">{data.readiness}%</div><div className="tile-sub">Evidence-approved</div></div>
        <div className="tile"><div className="tile-title">Opportunities</div><div className="tile-num">{data.opportunities}</div><div className="tile-sub">Available to you</div></div>
        <div className="tile"><div className="tile-title">Certificate</div><div className="tile-num">{data.has_certificate? 'Yes' : 'No'}</div><div className="tile-sub">Download once issued</div></div>
        <div className="tile"><div className="tile-title">Assessment</div><div className="tile-num">→</div><div className="tile-sub">Continue</div></div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/assessment')}>Continue Assessment</button>
        <button className="btn" onClick={()=>navigate('/matching')}>Request a provider</button>
      </div>
    </div>
  );
}

function ProviderHome(){
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/provider`); setData(data); }; load(); },[]);
  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="tile"><div className="tile-title">Eligible Requests</div><div className="tile-num">{data.eligible_requests}</div><div className="tile-sub">by expertise</div></div>
        <div className="tile"><div className="tile-title">Responses</div><div className="tile-num">{data.responses}</div><div className="tile-sub">submitted</div></div>
        <div className="tile"><div className="tile-title">Profile</div><div className="tile-num">✓</div><div className="tile-sub">Complete</div></div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/provider')}>Edit Provider Profile</button>
      </div>
    </div>
  );
}

function NavigatorHome(){
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/navigator`); setData(data); }; load(); },[]);
  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="tile"><div className="tile-title">Pending Reviews</div><div className="tile-num">{data.pending_reviews}</div><div className="tile-sub">awaiting review</div></div>
        <div className="tile"><div className="tile-title">Active Engagements</div><div className="tile-num">{data.active_engagements}</div></div>
        <div className="tile"><div className="tile-title">Queue</div><div className="tile-num">→</div><div className="tile-sub">Open</div></div>
      </div>
      <div className="mt-4"><button className="btn btn-primary" onClick={()=>navigate('/navigator')}>Open review queue</button></div>
    </div>
  );
}

function AgencyHome(){
  const [impact, setImpact] = useState(null);
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/agency`); setImpact(data); }; load(); },[]);
  if(!impact) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="tile"><div className="tile-title">Invites</div><div className="tile-num">{impact.invites.total}</div><div className="tile-sub">total</div></div>
        <div className="tile"><div className="tile-title">Paid</div><div className="tile-num">{impact.invites.paid}</div><div className="tile-sub">assessments</div></div>
        <div className="tile"><div className="tile-title">Revenue</div><div className="tile-num">${impact.revenue.assessment_fees}</div><div className="tile-sub">assessment fees</div></div>
        <div className="tile"><div className="tile-title">Opportunities</div><div className="tile-num">{impact.opportunities.count}</div></div>
      </div>
      <div className="mt-4 flex gap-2">
        <Link className="btn btn-primary" to="/agency">Open Agency Dashboard</Link>
      </div>
    </div>
  );
}

function HomeRouter(){
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  if(!me) return <Navigate to="/" replace />;
  if(me.role==='client') return <ClientHome/>;
  if(me.role==='provider') return <ProviderHome/>;
  if(me.role==='navigator') return <NavigatorHome/>;
  if(me.role==='agency') return <AgencyHome/>;
  return <Navigate to="/" replace />;
}

function Header(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  return (
    <header className="header">
      <div className="header-inner">
        <PolarisLogo />
        <nav className="nav">
          {me && <Link className="link" to="/home">Home</Link>}
          {me && me.role==='client' && <Link className="link" to="/assessment">Assessment</Link>}
          {me && me.role==='client' && <Link className="link" to="/matching">Matching</Link>}
          {me && me.role==='provider' && <Link className="link" to="/provider">Provider</Link>}
          {me && me.role==='navigator' && <Link className="link" to="/navigator">Navigator</Link>}
          {me && me.role==='agency' && <Link className="link" to="/agency">Agency</Link>}
        </nav>
        <div className="flex-1" />
        <button className="btn" onClick={()=>navigate('/home')}>Dashboard</button>
      </div>
    </header>
  );
}

function AppShell(){
  return (
    <div className="app-shell">
      <Header />
      <Routes>
        <Route path="/verify/cert/:id" element={<VerifyCert />} />
        <Route path="/home" element={<HomeRouter />} />
        <Route path="/business/profile" element={<BusinessProfileForm />} />
        {/* Existing routes preserved elsewhere */}
        <Route path="/" element={<div className="container mt-10"><h1 className="text-2xl font-semibold mb-2">Welcome to Polaris</h1><p className="text-slate-600">Sign in to access your personalized dashboard.</p></div>} />
      </Routes>
      <Toaster richColors position="top-center" />
    </div>
  );
}

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }