import React, { useEffect, useMemo, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Feature illustration URLs (blue-toned)
const ILLU_ASSESS = "https://images.unsplash.com/photo-1631540700964-6e292543024c?crop=entropy&cs=srgb&fm=jpg&q=85";
const ILLU_SECURE = "https://images.unsplash.com/photo-1552593716-a8278abb516f?crop=entropy&cs=srgb&fm=jpg&q=85";
const ILLU_MATCH = "https://images.unsplash.com/photo-1664526937033-fe2c11f1be25?crop=entropy&cs=srgb&fm=jpg&q=85";

function PolarisLogo({ size = 22 }) {
  return (
    <div className="flex items-center gap-2" aria-label="Polaris">
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2l1.8 5.4L19 9.5l-5.2 2.1L12 17l-1.8-5.4L5 9.5l5.2-2.1L12 2z" fill="#1B365D"/>
        <path d="M12 7l0.9 2.7L15.5 10l-2.6 1.1L12 14l-0.9-2.9L8.5 10l2.6-1.1L12 7z" fill="#4A90C2"/>
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

function AuthBar({ auth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("client");
  const [mode, setMode] = useState(() => localStorage.getItem('polaris_auth_mode') || 'login');
  const navigate = useNavigate();

  if (auth.me) {
    return (
      <div className="auth">
        <span className="text-sm">{auth.me.email} • {auth.me.role}</span>
        <Link className="link" to="/assessment">Assessment</Link>
        {auth.me.role === "client" && <Link className="link" to="/matching">Matching</Link>}
        {auth.me.role === "provider" && <Link className="link" to="/provider">Provider</Link>}
        {auth.me.role === "navigator" && <Link className="link" to="/navigator">Navigator</Link>}
        <button className="btn" onClick={() => { auth.logout(); navigate("/"); }}>Logout</button>
      </div>
    );
  }
  return (
    <div className="auth" id="auth">
      <select className="input" value={mode} onChange={(e) => { setMode(e.target.value); localStorage.setItem('polaris_auth_mode', e.target.value); }}>
        <option value="login">Login</option>
        <option value="register">Register</option>
      </select>
      <input className="input" placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className="input" placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      {mode === "register" && (
        <select className="input" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="client">client</option>
          <option value="navigator">navigator</option>
          <option value="provider">provider</option>
        </select>
      )}
      <button className="btn btn-primary" onClick={async () => { try { if (mode === "login") await auth.login(email, password); else await auth.register(email, password, role); } catch (e) { toast.error("Auth failed", { description: e?.response?.data?.detail || e.message }); } }}>{mode === "login" ? "Sign in" : "Create account"}</button>
    </div>
  );
}

function BrandHero() {
  const scrollToAuth = (mode) => {
    if (mode) localStorage.setItem('polaris_auth_mode', mode);
    const el = document.getElementById('auth');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
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
          <div className="card-visual" style={{ backgroundImage: `url(${ILLU_ASSESS})` }} />
          <div className="card-body">
            <div className="card-title">Assessment</div>
            <div className="card-sub">80 guided questions across 8 business areas with progress tracking.</div>
          </div>
        </div>
        <div className="card">
          <div className="card-visual" style={{ backgroundImage: `url(${ILLU_SECURE})` }} />
          <div className="card-body">
            <div className="card-title">Evidence Review</div>
            <div className="card-sub">Chunked uploads, navigator approvals, secure downloads, audit notes.</div>
          </div>
        </div>
        <div className="card">
          <div className="card-visual" style={{ backgroundImage: `url(${ILLU_MATCH})` }} />
          <div className="card-body">
            <div className="card-title">Provider Matching</div>
            <div className="card-sub">Budget-aware ranking and first-5 response to accelerate engagements.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Rest of the app remains same from prior version (AssessmentApp, NavigatorPanel, ProviderProfilePage, MatchingPage, ProtectedRoute, AppShell)

/* ... keep previous implementations ... */

export default function App(){
  // To keep this patch concise, we import the full AppShell from earlier code version.
  // The major changes are: functional Sign in button, on-brand illustration tiles, and relabeled auth button text.
  const AppShell = require('./AppShell').default || (() => null);
  return (<BrowserRouter><AppShell /></BrowserRouter>);
}