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

function useAuthHeader(){
  useEffect(()=>{
    const t = localStorage.getItem('polaris_token');
    if (t) axios.defaults.headers.common['Authorization'] = `Bearer ${t}`; else delete axios.defaults.headers.common['Authorization'];
  },[]);
}

function AuthWidget(){
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [role, setRole] = useState('client');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const submit = async()=>{
    try{
      if(mode==='register'){
        await axios.post(`${API}/auth/register`, { email, password, role });
      }
      const { data } = await axios.post(`${API}/auth/login`, { email, password });
      localStorage.setItem('polaris_token', data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      const me = await axios.get(`${API}/auth/me`);
      localStorage.setItem('polaris_me', JSON.stringify(me.data));
      toast.success('Welcome', { description: me.data.email });
      navigate('/home');
    }catch(e){ toast.error('Auth failed', { description: e?.response?.data?.detail || e.message }); }
  };
  return (
    <div className="auth" id="auth">
      <div className="flex gap-2 items-center mb-2">
        <select className="input" value={mode} onChange={e=>setMode(e.target.value)}>
          <option value="login">Login</option>
          <option value="register">Register</option>
        </select>
        {mode==='register' && (
          <select className="input" value={role} onChange={e=>setRole(e.target.value)}>
            <option value="client">client</option>
            <option value="provider">provider</option>
            <option value="navigator">navigator</option>
            <option value="agency">agency</option>
          </select>
        )}
      </div>
      <input className="input" placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="input" placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button className="btn btn-primary mt-2" onClick={submit}>{mode==='login' ? 'Sign in' : 'Create account'}</button>
    </div>
  );
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

// ---------------- Business Profile Form ----------------
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
  const [certificates, setCertificates] = useState([]);
  const navigate = useNavigate();
  useEffect(()=>{ 
    const load=async()=>{ 
      const {data} = await axios.get(`${API}/home/client`); 
      setData(data); 
      try{
        const certs = await axios.get(`${API}/client/certificates`);
        setCertificates(certs.data.certificates || []);
      }catch{}
    }; 
    load(); 
  },[]);

  const downloadCertificate = async(certId) => {
    try{
      const response = await fetch(`${API}/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
      });
      if(!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Polaris_Certificate_${certId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Certificate downloaded');
    }catch(e){ toast.error('Download failed', { description: e.message }); }
  };

  const copyVerificationLink = async(certId) => {
    try{
      const link = `${window.location.origin}/verify/cert/${certId}`;
      await navigator.clipboard.writeText(link);
      toast.success('Verification link copied to clipboard');
    }catch(e){ toast.error('Failed to copy link', { description: e.message }); }
  };

  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="tile"><div className="tile-title">Readiness</div><div className="tile-num">{String(data.readiness || 0)}%</div><div className="tile-sub">Evidence-approved</div></div>
        <div className="tile"><div className="tile-title">Opportunities</div><div className="tile-num">{String(data.opportunities || 0)}</div><div className="tile-sub">Available to you</div></div>
        <div className="tile"><div className="tile-title">Certificate</div><div className="tile-num">{data.has_certificate? 'Yes' : 'No'}</div><div className="tile-sub">Download once issued</div></div>
        <div className="tile"><div className="tile-title">Assessment</div><div className="tile-num">→</div><div className="tile-sub">Continue</div></div>
      </div>
      
      {certificates.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Your Certificates</h3>
          <div className="space-y-2">
            {certificates.map(cert => (
              <div key={cert.id} className="p-4 border rounded bg-white shadow-sm flex items-center justify-between">
                <div>
                  <div className="font-medium">{cert.title}</div>
                  <div className="text-sm text-slate-600">Readiness: {cert.readiness_percent}% • Issued: {cert.issued_at ? new Date(cert.issued_at).toLocaleDateString() : 'Unknown'}</div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-sm" onClick={()=>downloadCertificate(cert.id)}>Download PDF</button>
                  <button className="btn btn-sm" onClick={()=>copyVerificationLink(cert.id)}>Copy verification link</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/matching')}>Request a provider</button>
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
        <div className="tile"><div className="tile-title">Eligible Requests</div><div className="tile-num">{String(data.eligible_requests || 0)}</div><div className="tile-sub">by expertise</div></div>
        <div className="tile"><div className="tile-title">Responses</div><div className="tile-num">{String(data.responses || 0)}</div><div className="tile-sub">submitted</div></div>
        <div className="tile"><div className="tile-title">Profile</div><div className="tile-num">✓</div><div className="tile-sub">Complete</div></div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/provider/proposals')}>Open Proposal Composer</button>
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
        <div className="tile"><div className="tile-title">Pending Reviews</div><div className="tile-num">{String(data.pending_reviews || 0)}</div><div className="tile-sub">awaiting review</div></div>
        <div className="tile"><div className="tile-title">Active Engagements</div><div className="tile-num">{String(data.active_engagements || 0)}</div></div>
        <div className="tile"><div className="tile-title">Queue</div><div className="tile-num">→</div><div className="tile-sub">Open</div></div>
      </div>
      <div className="mt-4"><Link className="btn btn-primary" to="/navigator">Open review queue</Link></div>
    </div>
  );
}

function AgencyHome(){
  const [impact, setImpact] = useState(null);
  const [certificates, setCertificates] = useState([]);
  useEffect(()=>{ 
    const load=async()=>{ 
      const {data} = await axios.get(`${API}/home/agency`); 
      setImpact(data); 
      try{
        const certs = await axios.get(`${API}/agency/certificates`);
        setCertificates(certs.data.certificates || []);
      }catch{}
    }; 
    load(); 
  },[]);

  const downloadCertificate = async(certId) => {
    try{
      const response = await fetch(`${API}/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
      });
      if(!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Polaris_Certificate_${certId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Certificate downloaded');
    }catch(e){ toast.error('Download failed', { description: e.message }); }
  };

  const copyVerificationLink = async(certId) => {
    try{
      const link = `${window.location.origin}/verify/cert/${certId}`;
      await navigator.clipboard.writeText(link);
      toast.success('Verification link copied to clipboard');
    }catch(e){ toast.error('Failed to copy link', { description: e.message }); }
  };

  // Calculate current tier based on invites
  const getTierInfo = () => {
    if (!impact) return { tier: 'Basic', price: 100, next: 'Volume' };
    const total = impact.invites.total || 0;
    if (total >= 100) return { tier: 'Enterprise', price: 60, next: null };
    if (total >= 25) return { tier: 'Growth', price: 75, next: 'Enterprise (100+ invites = $60 each)' };
    if (total >= 5) return { tier: 'Volume', price: 85, next: 'Growth (25+ invites = $75 each)' };
    return { tier: 'Basic', price: 100, next: 'Volume (5+ invites = $85 each)' };
  };

  if(!impact) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  
  const tierInfo = getTierInfo();
  
  return (
    <div className="container mt-6">
      {/* Tier Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-lg mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-semibold text-lg">{tierInfo.tier} Plan</div>
            <div className="text-blue-100">Current price: ${tierInfo.price} per invitation</div>
            {tierInfo.next && <div className="text-blue-200 text-sm mt-1">Next tier: {tierInfo.next}</div>}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{String(impact.invites?.total || 0)}</div>
            <div className="text-blue-100 text-sm">Total invitations</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="tile"><div className="tile-title">Invites</div><div className="tile-num">{String(impact.invites?.total || 0)}</div><div className="tile-sub">total</div></div>
        <div className="tile"><div className="tile-title">Paid</div><div className="tile-num">{String(impact.invites?.paid || 0)}</div><div className="tile-sub">assessments</div></div>
        <div className="tile"><div className="tile-title">Revenue</div><div className="tile-num">${String(impact.revenue?.assessment_fees || 0)}</div><div className="tile-sub">assessment fees</div></div>
        <div className="tile"><div className="tile-title">Opportunities</div><div className="tile-num">{String(impact.opportunities?.count || 0)}</div></div>
      </div>

      {certificates.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Issued Certificates</h3>
          <div className="space-y-2">
            {certificates.map(cert => (
              <div key={cert.id} className="p-4 border rounded bg-white shadow-sm flex items-center justify-between">
                <div>
                  <div className="font-medium">{cert.title}</div>
                  <div className="text-sm text-slate-600">Client: {cert.client_user_id} • Readiness: {cert.readiness_percent}% • Issued: {cert.issued_at ? new Date(cert.issued_at).toLocaleDateString() : 'Unknown'}</div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-sm" onClick={()=>downloadCertificate(cert.id)}>Download PDF</button>
                  <button className="btn btn-sm" onClick={()=>copyVerificationLink(cert.id)}>Copy verification link</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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

// ---------------- Matching with Accept → Engagement ----------------
function MatchingPage(){
  const location = useLocation();
  const [req, setReq] = useState({ budget: '', payment_pref: '', timeline: '', area_id: 'area6', description: '' });
  const [requestId, setRequestId] = useState('');
  const [matches, setMatches] = useState([]);
  const [responses, setResponses] = useState([]);
  const [agreedFee, setAgreedFee] = useState('');
  useEffect(()=>{
    const params = new URLSearchParams(location.search);
    const area = params.get('area_id'); const desc = params.get('desc');
    if (area || desc) setReq(prev=>({ ...prev, area_id: area || prev.area_id, description: desc || prev.description }));
  }, [location.search]);
  const createReq = async()=>{
    try{
      const payload = { ...req, budget: Number(req.budget) };
      const {data} = await axios.post(`${API}/match/request`, payload);
      setRequestId(data.request_id);
      toast.success('Request created');
      const r2 = await axios.get(`${API}/match/${data.request_id}/matches`); setMatches(r2.data.matches||[]);
      const r3 = await axios.get(`${API}/match/${data.request_id}/responses`); setResponses(r3.data.responses||[]);
    }catch(e){ toast.error('Create request failed'); }
  };
  const refresh = async()=>{
    if(!requestId) return;
    const r2 = await axios.get(`${API}/match/${requestId}/matches`); setMatches(r2.data.matches||[]);
    const r3 = await axios.get(`${API}/match/${requestId}/responses`); setResponses(r3.data.responses||[]);
  };
  const inviteTop5 = async()=>{ try{ await axios.post(`${API}/match/${requestId}/invite-top5`); toast.success('Invited top 5'); }catch{ toast.error('Invite failed'); } };
  const acceptResponse = async(resp)=>{
    try{
      const { data } = await axios.post(`${API}/engagements/create`, { request_id: requestId, response_id: resp.id || resp._id, agreed_fee: Number(agreedFee||0) });
      toast.success('Engagement created', { description: data.engagement_id });
      await refresh();
    }catch(e){ toast.error('Accept failed', { description: e?.response?.data?.detail || e.message }); }
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
            <option value="area1">Business Formation & Registration</option>
            <option value="area2">Financial Operations</option>
            <option value="area3">Legal & Contracting</option>
            <option value="area4">Technology & Cybersecurity</option>
            <option value="area5">People & HR</option>
            <option value="area6">Marketing & Sales</option>
            <option value="area7">Procurement & Supply Chain</option>
            <option value="area8">Quality & Continuous Improvement</option>
          </select>
          <input className="input" placeholder="Short description" value={req.description} onChange={e=>setReq({...req, description:e.target.value})} />
        </div>
      )}
      {!requestId ? (<div className="mt-3"><button className="btn btn-primary" onClick={createReq}>Create request</button></div>) : (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2"><div className="text-sm text-slate-600">Top matches</div><div className="flex gap-2"><button className="btn" onClick={inviteTop5}>Invite top-5</button><button className="btn" onClick={refresh}>Refresh</button></div></div>
          <table className="table">
            <thead><tr><th>Company</th><th>Areas</th><th>Location</th><th>Price range</th><th>Score</th></tr></thead>
            <tbody>
              {matches.map(m => (
                <tr key={m.provider_id}><td>{m.company_name}</td><td>{(m.service_areas||[]).join(', ')}</td><td>{m.location||'-'}</td><td>{m.price_min||'-'} - {m.price_max||'-'}</td><td>{m.score}</td></tr>
              ))}
            </tbody>
          </table>
          <div className="mt-6">
            <div className="text-sm font-medium mb-2">Responses</div>
            <table className="table">
              <thead><tr><th>Response</th><th>Provider</th><th>Created</th><th>Agree fee</th><th>Action</th></tr></thead>
              <tbody>
                {responses.map(r => (
                  <tr key={r.id || r._id}><td className="max-w-md truncate" title={r.proposal_note}>{r.proposal_note||'-'}</td><td>{r.provider_user_id}</td><td>{r.created_at}</td><td><input className="input" style={{width:120}} placeholder="$" onChange={e=>setAgreedFee(e.target.value)} /></td><td><button className="btn btn-primary" onClick={()=>acceptResponse(r)}>Accept</button></td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------- Provider Proposal Composer ----------------
function ProviderProposalsPage(){
  const [eligible, setEligible] = useState([]);
  const [notes, setNotes] = useState({});
  const [attachments, setAttachments] = useState({}); // responseId -> files[] local
  const load = async()=>{ try{ const {data} = await axios.get(`${API}/match/eligible`); setEligible(data.requests||[]);}catch{} };
  useEffect(()=>{ load(); },[]);
  const respond = async(reqId)=>{
    try{
      const fd = new FormData(); fd.append('request_id', reqId); fd.append('proposal_note', notes[reqId] || '');
      const res = await fetch(`${API}/match/respond`, { method:'POST', body: fd });
      const data = await res.json();
      if(!data.ok){ toast.error(data.reason || 'Respond failed'); return; }
      toast.success('Response sent');
      if (data.response_id && attachments[reqId]?.length){
        for (const file of attachments[reqId]){
          const init = await fetch(`${API}/provider/proposals/upload/initiate`, { method:'POST', body: new URLSearchParams({ response_id: data.response_id, file_name: file.name, total_size: String(file.size), mime_type: file.type })});
          const initJson = await init.json(); const uploadId = initJson.upload_id; const chunkSize = initJson.chunk_size; const totalChunks = Math.ceil(file.size / chunkSize);
          for(let i=0;i<totalChunks;i++){
            const start=i*chunkSize; const end=Math.min(start+chunkSize, file.size); const blob=file.slice(start,end); const fd2=new FormData(); fd2.append('upload_id', uploadId); fd2.append('chunk_index', String(i)); fd2.append('file', blob, `${file.name}.part`); await fetch(`${API}/provider/proposals/upload/chunk`, { method:'POST', body: fd2 });
          }
          await fetch(`${API}/provider/proposals/upload/complete`, { method:'POST', body: new URLSearchParams({ upload_id: uploadId, total_chunks: String(totalChunks) })});
        }
      }
      setNotes(prev=>({ ...prev, [reqId]: '' })); setAttachments(prev=>({ ...prev, [reqId]: [] }));
      await load();
    }catch(e){ toast.error('Respond failed'); }
  };
  return (
    <div className="container mt-6">
      <h2 className="text-lg font-semibold mb-3">Proposal Composer</h2>
      <table className="table">
        <thead><tr><th>Area</th><th>Budget</th><th>Timeline</th><th>Invited</th><th>Proposal</th><th>Attachments</th><th>Action</th></tr></thead>
        <tbody>
          {eligible.map(r => (
            <tr key={r.id}>
              <td>{r.area_id}</td><td>{r.budget}</td><td>{r.timeline||'-'}</td><td>{r.invited ? 'Yes' : 'No'}</td>
              <td><input className="input" placeholder="Short proposal note" value={notes[r.id]||''} onChange={e=>setNotes(prev=>({ ...prev, [r.id]: e.target.value }))} /></td>
              <td><input type="file" multiple onChange={e=>{ const files = Array.from(e.target.files||[]); setAttachments(prev=>({ ...prev, [r.id]: files })); }} /></td>
              <td><button className="btn btn-primary" onClick={()=>respond(r.id)}>Send</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Header(){
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  return (
    <header className="header">
      <div className="header-inner">
        <PolarisLogo />
        <nav className="nav">
          {me && <Link className="link" to="/home">Home</Link>}
          {me && me.role==='client' && <Link className="link" to="/matching">Matching</Link>}
          {me && me.role==='provider' && <Link className="link" to="/provider/proposals">Proposals</Link>}
          {me && me.role==='navigator' && <Link className="link" to="/navigator">Navigator</Link>}
          {me && me.role==='agency' && <Link className="link" to="/agency">Agency</Link>}
        </nav>
        <div className="flex-1" />
        {!me ? <a className="btn" href="#auth">Sign in</a> : <Link className="btn" to="/home">Dashboard</Link>}
      </div>
    </header>
  );
}

function Landing(){
  return (
    <div>
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-inner">
          <div className="flex-1 text-white">
            <PolarisLogo size={28} />
            <h1 className="hero-title mt-2">Your North Star for Procurement Readiness</h1>
            <p className="hero-sub">Assess your business, match with providers, and unlock local opportunities.</p>
            <div className="hero-ctas">
              <a className="btn btn-primary" href="#auth">Create an account</a>
              <a className="btn" href="#auth">Sign in</a>
            </div>
          </div>
          <div className="w-[420px] max-w-full"><AuthWidget /></div>
        </div>
      </section>
      <section className="container section">
        <h3 className="section-title">Why Polaris</h3>
        <p className="section-sub">Designed with the City of San Antonio to accelerate procurement readiness for small businesses.</p>
        <div className="features">
          <div className="card"><div className="card-visual">📋</div><div className="card-body"><div className="card-title">Focused Assessment</div><div className="card-sub">Concrete, non-sensitive deliverables with AI guidance and free resources.</div></div></div>
          <div className="card"><div className="card-visual">🤝</div><div className="card-body"><div className="card-title">Expert Matching</div><div className="card-sub">Providers by area of expertise; accept and create engagements in a click.</div></div></div>
          <div className="card"><div className="card-visual">📈</div><div className="card-body"><div className="card-title">Impact & Certificates</div><div className="card-sub">Certificates verified publicly, with agency impact dashboards.</div></div></div>
        </div>
      </section>
    </div>
  );
}

function AppShell(){
  useAuthHeader();
  const location = useLocation();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const showLanding = location.pathname === '/' && !me;
  return (
    <div className="app-shell">
      <Header />
      {showLanding ? (
        <Landing />
      ) : (
        <Routes>
          <Route path="/verify/cert/:id" element={<VerifyCert />} />
          <Route path="/home" element={<HomeRouter />} />
          <Route path="/business/profile" element={<BusinessProfileForm />} />
          <Route path="/matching" element={<MatchingPage />} />
          <Route path="/provider/proposals" element={<ProviderProposalsPage />} />
          <Route path="/" element={<Navigate to={me?'/home':'/'} replace />} />
        </Routes>
      )}
      <Toaster richColors position="top-center" />
    </div>
  );
}

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }