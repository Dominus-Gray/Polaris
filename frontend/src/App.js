import React, { useEffect, useMemo, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Axios auth setup
function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("polaris_token") || "");
  const [me, setMe] = useState(() => {
    const cached = localStorage.getItem("polaris_me");
    return cached ? JSON.parse(cached) : null;
  });

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common["Authorization"];
    }
  }, [token]);

  const login = async (email, password) => {
    const { data } = await axios.post(`${API}/auth/login`, { email, password });
    // Immediately set Authorization header for subsequent calls
    axios.defaults.headers.common["Authorization"] = `Bearer ${data.access_token}`;
    setToken(data.access_token);
    localStorage.setItem("polaris_token", data.access_token);
    const { data: profile } = await axios.get(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    setMe(profile);
    localStorage.setItem("polaris_me", JSON.stringify(profile));
  };

  const register = async (email, password, role) => {
    await axios.post(`${API}/auth/register`, { email, password, role });
    await login(email, password);
  };

  const logout = () => {
    setToken("");
    setMe(null);
    localStorage.removeItem("polaris_token");
    localStorage.removeItem("polaris_me");
  };

  return { token, me, login, register, logout };
}

function useSession() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("polaris_session_id") || "");
  useEffect(() => {
    async function ensure() {
      if (!sessionId) {
        const { data } = await axios.post(`${API}/assessment/session`);
        setSessionId(data.session_id);
        localStorage.setItem("polaris_session_id", data.session_id);
      }
    }
    ensure();
  }, [sessionId]);
  return sessionId;
}

function useSchema() {
  const [schema, setSchema] = useState(null);
  useEffect(() => {
    axios.get(`${API}/assessment/schema`).then(({ data }) => setSchema(data));
  }, []);
  return schema;
}

async function uploadFileChunked({ file, sessionId, areaId, questionId, onProgress }) {
  const { data: init } = await axios.post(`${API}/upload/initiate`, {
    file_name: file.name,
    total_size: file.size,
    mime_type: file.type,
    session_id: sessionId,
    area_id: areaId,
    question_id: questionId,
  });
  const uploadId = init.upload_id;
  const chunkSize = init.chunk_size;
  const totalChunks = Math.ceil(file.size / chunkSize);
  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const blob = file.slice(start, end);
    const fd = new FormData();
    fd.append("upload_id", uploadId);
    fd.append("chunk_index", String(i));
    fd.append("file", blob, `${file.name}.part`);
    await fetch(`${API}/upload/chunk`, { method: "POST", body: fd });
    onProgress && onProgress(Math.round(((i + 1) / totalChunks) * 100));
  }
  const { data: done } = await axios.post(`${API}/upload/complete`, { upload_id: uploadId, total_chunks: totalChunks });
  return { uploadId, ...done };
}

function ProgressBar({ sessionId }) {
  const [progress, setProgress] = useState(null);
  useEffect(() => {
    if (!sessionId) return;
    const fetcher = async () => {
      const { data } = await axios.get(`${API}/assessment/session/${sessionId}/progress`);
      setProgress(data);
    };
    fetcher();
    const t = setInterval(fetcher, 5000);
    return () => clearInterval(t);
  }, [sessionId]);
  const pct = progress?.percent_complete || 0;
  return (
    <div className="mt-2">
      <div className="progress-wrap"><div className="progress-bar" style={{ width: `${pct}%` }} /></div>
      <div className="text-xs text-slate-600 mt-1">Procurement readiness: {pct}%</div>
    </div>
  );
}

function AuthBar({ auth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("client");
  const [mode, setMode] = useState("login");
  const navigate = useNavigate();

  if (auth.me) {
    return (
      <div className="auth">
        <span className="text-sm">{auth.me.email} • {auth.me.role}</span>
        <Link className="link" to="/">Assessment</Link>
        {auth.me.role === "navigator" && <Link className="link" to="/navigator">Navigator</Link>}
        <button className="btn" onClick={() => { auth.logout(); navigate("/"); }}>Logout</button>
      </div>
    );
  }
  return (
    <div className="auth">
      <select className="input" value={mode} onChange={(e) => setMode(e.target.value)}>
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
      <button className="btn btn-primary" onClick={async () => {
        if (mode === "login") await auth.login(email, password); else await auth.register(email, password, role);
      }}>{mode === "login" ? "Login" : "Register"}</button>
    </div>
  );
}

function QuestionCard({ area, q, sessionId, saveAnswer, current }) {
  const [aiMsg, setAiMsg] = useState("");
  const [uploadPct, setUploadPct] = useState(0);
  const [files, setFiles] = useState([]); // [{upload_id, file_name, status}]

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!sessionId) return;
      const { data } = await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`);
      if (!cancelled) setFiles(data.evidence || []);
    }
    load();
    return () => { cancelled = true; };
  }, [sessionId, area.id, q.id]);

  const yes = current?.value === true;
  const no = current?.value === false;

  const askAI = async () => {
    try {
      setAiMsg("Thinking...");
      const { data } = await axios.post(`${API}/ai/explain`, { session_id: sessionId, area_id: area.id, question_id: q.id, question_text: q.text });
      setAiMsg(data.message);
    } catch {
      setAiMsg("AI unavailable.");
    }
  };

  const onFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadPct(0);
    const res = await uploadFileChunked({ file, sessionId, areaId: area.id, questionId: q.id, onProgress: setUploadPct });
    const evidence_ids = [res.upload_id, ...((current?.evidence_ids) || [])];
    await saveAnswer(area.id, q.id, true, evidence_ids);
    const { data } = await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`);
    setFiles(data.evidence || []);
  };

  const removeFile = async (upload_id) => {
    try {
      await axios.delete(`${API}/upload/${upload_id}`);
      const { data } = await axios.get(`${API}/assessment/session/${sessionId}/answer/${area.id}/${q.id}/evidence`);
      setFiles(data.evidence || []);
      const remaining = (current?.evidence_ids || []).filter((id) => id !== upload_id);
      await saveAnswer(area.id, q.id, current?.value ?? true, remaining);
    } catch (e) {
      alert("Failed to remove file");
    }
  };

  return (
    <div className="q-card">
      <div className="q-label">{q.text}</div>
      <div className="q-actions">
        <div className="toggle border-slate-300">
          <button className={yes ? "on" : ""} onClick={() => saveAnswer(area.id, q.id, true, current?.evidence_ids || [])}>Yes</button>
          <button className={no ? "off" : ""} onClick={() => saveAnswer(area.id, q.id, false, [])}>No</button>
        </div>
        <button className="btn" onClick={askAI}>Why this matters? (AI)</button>
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
                      <button className="link" onClick={() => removeFile(f.upload_id)}>remove</button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        )}
      </div>
      {aiMsg && <div className="ai-note">{aiMsg}</div>}
    </div>
  );
}

function AssessmentApp({ auth }) {
  const sessionId = useSession();
  const schema = useSchema();
  const [activeArea, setActiveArea] = useState(null);
  const [answers, setAnswers] = useState({}); // { [areaId]: { [qId]: { value, evidence_ids } } }

  // Hydration
  useEffect(() => {
    async function load() {
      if (!sessionId) return;
      const { data } = await axios.get(`${API}/assessment/session/${sessionId}`);
      const amap = {};
      for (const a of data.answers || []) {
        if (!amap[a.area_id]) amap[a.area_id] = {};
        amap[a.area_id][a.question_id] = { value: a.value, evidence_ids: a.evidence_ids || [] };
      }
      setAnswers(amap);
    }
    load();
  }, [sessionId]);

  useEffect(() => {
    if (schema && !activeArea) setActiveArea(schema.areas[0]);
  }, [schema]);

  const saveAnswer = async (areaId, qId, value, evidence_ids) => {
    setAnswers((prev) => ({ ...prev, [areaId]: { ...(prev[areaId] || {}), [qId]: { value, evidence_ids: evidence_ids || [] } } }));
    if (!sessionId) return;
    await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers: [ { area_id: areaId, question_id: qId, value, evidence_ids } ] });
  };

  const saveAll = async () => {
    if (!sessionId || !schema) return;
    const payload = [];
    for (const area of schema.areas) {
      const amap = answers[area.id] || {};
      for (const q of area.questions) {
        const a = amap[q.id];
        if (a) payload.push({ area_id: area.id, question_id: q.id, value: a.value, evidence_ids: a.evidence_ids || [] });
      }
    }
    if (payload.length) {
      await axios.post(`${API}/assessment/answers/bulk`, { session_id: sessionId, answers: payload });
      alert("Progress saved.");
    }
  };

  if (!schema) return <div className="p-6">Loading...</div>;

  return (
    <div className="container">
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
            <div className="text-xs text-slate-500">Answer Yes/No. If Yes, upload evidence. Approved evidence counts towards readiness.</div>
          </div>
          {activeArea?.questions.map((q) => (
            <QuestionCard key={q.id} area={activeArea} q={q} sessionId={sessionId} saveAnswer={saveAnswer} current={(answers[activeArea.id]||{})[q.id]} />
          ))}
        </section>
      </div>
    </div>
  );
}

function NavigatorPanel() {
  const [items, setItems] = useState([]);
  const load = async () => {
    const { data } = await axios.get(`${API}/navigator/reviews?status=pending`);
    setItems(data.reviews || []);
  };
  useEffect(() => { load(); }, []);

  const decide = async (id, decision) => {
    const notes = decision === 'approved' ? 'OK' : prompt('Reason for rejection?') || '';
    await axios.post(`${API}/navigator/reviews/${id}/decision`, { decision, notes });
    await load();
  };

  return (
    <div className="container">
      <h2 className="text-lg font-semibold mt-6 mb-3">Navigator • Evidence Reviews</h2>
      <table className="table">
        <thead><tr><th>Area</th><th>Question</th><th>File</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id}>
              <td>{r.area_title}</td>
              <td>{r.question_text}</td>
              <td>{r.file_name}</td>
              <td><span className={`status-pill ${r.status === 'approved' ? 'status-approved' : r.status === 'rejected' ? 'status-rejected' : 'status-pending'}`}>{r.status}</span></td>
              <td className="space-x-2">
                <button className="btn" onClick={() => decide(r.id, 'approved')}>Approve</button>
                <button className="btn" onClick={() => decide(r.id, 'rejected')}>Reject</button>
              </td>
            </tr>
          ))}
          {!items.length && (<tr><td colSpan="5" className="text-center text-slate-500">No pending items</td></tr>)}
        </tbody>
      </table>
    </div>
  );
}

function AppShell() {
  const auth = useAuth();
  const sessionId = useSession();
  return (
    <div className="app-shell">
      <header className="header">
        <div className="header-inner">
          <div className="brand">Polaris • SBAP Assessment</div>
          <div className="flex-1"><ProgressBar sessionId={sessionId} /></div>
          <AuthBar auth={auth} />
        </div>
      </header>
      <Routes>
        <Route path="/" element={<AssessmentApp auth={auth} />} />
        <Route path="/navigator" element={<NavigatorPanel />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}