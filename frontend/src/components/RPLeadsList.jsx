import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function RPLeadsList() {
  const [leads, setLeads] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const me = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("polaris_me") || "null"); } catch { return null; }
  }, []);

  const loadLeads = async () => {
    setLoading(true); setError("");
    try {
      const params = {};
      if (status) params.status = status;
      const { data } = await axios.get(`${API}/v2/rp/leads`, { params });
      setLeads(data.leads || []);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadLeads(); }, [status]);

  return (
    <div className="container mt-6 max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Resource Partner Leads</h2>
        <div className="flex items-center gap-2">
          <select className="input" value={status} onChange={e=>setStatus(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="working">Working</option>
            <option value="contacted">Contacted</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          {me?.role === 'client' && (
            <Link to="/rp/share" className="btn btn-primary">Create Share Package</Link>
          )}
        </div>
      </div>

      {loading && (<div className="state-loading"><div className="spinner" /></div>)}
      {!loading && error && (
        <div className="state-error mb-3"><div className="title">Failed to load leads</div><div className="sub">{error}</div></div>
      )}
      {!loading && !error && leads.length === 0 && (
        <div className="state-empty">
          <div className="icon">📂</div>
          <div className="title">No leads found</div>
          <div className="sub">Create a share package or adjust filters.</div>
        </div>
      )}

      {!loading && !error && leads.length > 0 && (
        <div className="bg-white border rounded-xl overflow-hidden">
          <table className="table w-full">
            <thead>
              <tr className="text-left text-sm text-slate-600">
                <th className="p-3">Lead ID</th>
                <th className="p-3">RP Type</th>
                <th className="p-3">Status</th>
                <th className="p-3">Missing Prerequisites</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map(ld => (
                <tr key={ld.lead_id || ld._id} className="border-t">
                  <td className="p-3 text-sm">{ld.lead_id || ld._id}</td>
                  <td className="p-3 text-sm">{ld.rp_type}</td>
                  <td className="p-3 text-sm capitalize">{ld.status}</td>
                  <td className="p-3 text-sm">{(ld.missing_prerequisites||[]).slice(0,3).join(', ') || 'None'}</td>
                  <td className="p-3 text-sm">
                    <Link to={`/rp/lead/${ld.lead_id || ld._id}`} className="btn btn-outline btn-sm">Open</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}