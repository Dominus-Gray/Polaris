import React, { useEffect, useMemo, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
      <div className="progress-wrap">
        <div className="progress-bar" style={{ width: `${pct}%` }} />
      </div>
      <div className="text-xs text-slate-600 mt-1">Procurement readiness: {pct}%</div>
    </div>
  );
}

async function uploadFileChunked({ file, sessionId, areaId, questionId, onProgress }) {
  // 1) Initiate
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
  // 2) Upload chunks sequentially
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
  // 3) Complete
  const { data: done } = await axios.post(`${API}/upload/complete`, { upload_id: uploadId, total_chunks: totalChunks });
  return { uploadId, ...done };
}

function QuestionCard({ area, q, sessionId, saveAnswer, current }) {
  const [aiMsg, setAiMsg] = useState("");
  const [uploadPct, setUploadPct] = useState(0);

  const yes = current?.value === true;
  const no = current?.value === false;

  const askAI = async () => {
    try {
      setAiMsg("Thinking...");
      const { data } = await axios.post(`${API}/ai/explain`, {
        session_id: sessionId,
        area_id: area.id,
        question_id: q.id,
        question_text: q.text,
      });
      setAiMsg(data.message);
    } catch (e) {
      setAiMsg("AI unavailable. We'll enable after key is set.");
    }
  };

  const onFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadPct(0);
    const res = await uploadFileChunked({ file, sessionId, areaId: area.id, questionId: q.id, onProgress: setUploadPct });
    // After upload, mark answer yes and attach evidence id
    const evidence_ids = [res.upload_id];
    await saveAnswer(area.id, q.id, true, evidence_ids);
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
            {uploadPct > 0 && uploadPct < 100 && (
              <div className="mt-1 text-xs">Uploading... {uploadPct}%</div>
            )}
            {current?.evidence_ids?.length ? (
              <div className="mt-1 badge">{current.evidence_ids.length} file(s) attached</div>
            ) : null}
          </div>
        )}
      </div>
      {aiMsg && <div className="ai-note">{aiMsg}</div>}
    </div>
  );
}

export default function App() {
  const sessionId = useSession();
  const schema = useSchema();
  const [activeArea, setActiveArea] = useState(null);
  const [answers, setAnswers] = useState({}); // { [areaId]: { [qId]: { value, evidence_ids } } }

  useEffect(() => {
    if (schema && !activeArea) setActiveArea(schema.areas[0]);
  }, [schema]);

  const saveAnswer = async (areaId, qId, value, evidence_ids) => {
    setAnswers((prev) => ({
      ...prev,
      [areaId]: {
        ...(prev[areaId] || {}),
        [qId]: { value, evidence_ids: evidence_ids || [] },
      },
    }));
    if (!sessionId) return;
    await axios.post(`${API}/assessment/answers/bulk`, {
      session_id: sessionId,
      answers: [ { area_id: areaId, question_id: qId, value, evidence_ids } ],
    });
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
    <div className="app-shell">
      <header className="header">
        <div className="header-inner">
          <div className="brand">Polaris • SBAP Assessment</div>
          <div className="text-sm text-slate-600">Session: {sessionId?.slice(0,8)}</div>
        </div>
        <div className="container"><ProgressBar sessionId={sessionId} /></div>
      </header>

      <main className="container">
        <div className="grid-layout">
          <aside className="sidebar">
            <div className="text-sm font-semibold mb-2">Business Areas</div>
            {schema.areas.map((a) => (
              <div key={a.id}
                   className={`area-item ${activeArea?.id === a.id ? "area-active" : ""}`}
                   onClick={() => setActiveArea(a)}>
                <span className="w-2 h-2 rounded-full bg-indigo-500" />
                <span>{a.title}</span>
              </div>
            ))}
            <div className="mt-4">
              <button className="btn btn-primary w-full" onClick={saveAll}>Save Progress</button>
            </div>
          </aside>

          <section className="main">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">{activeArea?.title}</h2>
              <div className="text-xs text-slate-500">Answer Yes/No. If Yes, upload evidence.</div>
            </div>
            {activeArea?.questions.map((q) => (
              <QuestionCard key={q.id}
                area={activeArea}
                q={q}
                sessionId={sessionId}
                saveAnswer={saveAnswer}
                current={(answers[activeArea.id]||{})[q.id]}
              />
            ))}
          </section>
        </div>
      </main>
    </div>
  );
}