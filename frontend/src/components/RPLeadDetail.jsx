import React, { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function RPLeadDetail(){
  const { id } = useParams();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("");
  const me = useMemo(() => { try { return JSON.parse(localStorage.getItem('polaris_me')||'null'); } catch { return null; } }, []);

  const loadLead = async () => {
    setLoading(true); setError("");
    try {
      const { data } = await axios.get(`/v2/rp/leads`);
      const all = data.leads || [];
      const found = all.find(l => (l.lead_id||l._id) === id);
      if (!found) throw new Error('Lead not found');
      setLead(found);
      setNotes(found.notes || "");
      setStatus(found.status || "new");
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };
  useEffect(()=>{ loadLead(); }, [id]);

  const canEdit = me && ['admin','agency','rp','resource_partner','navigator'].includes(me.role);

  const save = async () => {
    try {
      await axios.patch(`/v2/rp/leads/${id}`, { status, notes });
      await loadLead();
    } catch (e) {
      alert(e.response?.data?.detail || e.message);
    }
  };

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold">Lead Detail</h2>
        <Link to="/rp" className="btn">Back</Link>
      </div>
      {loading && (<div className="state-loading"><div className="spinner" /></div>)}
      {!loading && error && (<div className="state-error"><div className="title">Failed to load lead</div><div className="sub">{error}</div></div>)}
      {!loading && !error && lead && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-4">
            <div className="text-sm text-slate-600">Lead ID</div>
            <div className="font-mono text-slate-900">{lead.lead_id || lead._id}</div>
            <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
              <div><span className="text-slate-600">RP Type:</span> {lead.rp_type}</div>
              <div className="capitalize"><span className="text-slate-600">Status:</span> {lead.status}</div>
            </div>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="text-sm font-medium mb-2">Package</div>
            <pre className="bg-slate-50 rounded p-3 text-xs overflow-auto">{JSON.stringify(lead.package_json, null, 2)}</pre>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="text-sm font-medium mb-2">Missing Prerequisites</div>
            {(lead.missing_prerequisites||[]).length ? (
              <ul className="list-disc pl-6 text-sm">
                {lead.missing_prerequisites.map(m => <li key={m}>{m}</li>)}
              </ul>
            ) : (
              <div className="text-sm text-emerald-700">None</div>
            )}
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="text-sm font-medium mb-2">Review Actions</div>
            {!canEdit ? (
              <div className="text-sm text-slate-600">Read-only view for your role.</div>
            ) : (
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="form-label">Status</label>
                    <select className="input" value={status} onChange={e=>setStatus(e.target.value)}>
                      {['new','working','contacted','approved','rejected'].map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Notes</label>
                    <textarea className="input" value={notes} onChange={e=>setNotes(e.target.value)} rows={3} />
                  </div>
                </div>
                <button className="btn btn-primary" onClick={save}>Save</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}