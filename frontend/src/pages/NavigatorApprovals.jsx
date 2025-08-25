import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${API_BASE}/api`;

function NavigatorApprovals() {
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('providers');
  const [providers, setProviders] = useState([]);
  const [agencies, setAgencies] = useState([]);
  const [query, setQuery] = useState('');
  const [actionBusy, setActionBusy] = useState(null);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [provRes, agRes] = await Promise.all([
        axios.get(`${API}/navigator/providers/pending`),
        axios.get(`${API}/navigator/agencies/pending`)
      ]);
      setProviders(provRes.data.providers || []);
      setAgencies(agRes.data.agencies || []);
    } catch (e) {
      console.error('Failed to load approvals', e);
      toast.error('Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const filteredProviders = useMemo(() => filterList(providers, query), [providers, query]);
  const filteredAgencies = useMemo(() => filterList(agencies, query), [agencies, query]);

  const act = async (type, id, approved, notes) => {
    setActionBusy(id + type);
    try {
      const url = type === 'provider' ? `${API}/navigator/providers/approve` : `${API}/navigator/agencies/approve`;
      await axios.post(url, { id, approved, notes: notes || '' });
      toast.success(`${type} ${approved ? 'approved' : 'rejected'}`);
      await loadAll();
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      toast.error('Action failed', { description: msg });
    } finally {
      setActionBusy(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Approvals Queue</h2>
          <p className="text-sm text-slate-600">Review and approve pending provider and agency accounts</p>
        </div>
        <div className="flex gap-2">
          <input className="input" placeholder="Search by name or email" value={query} onChange={e => setQuery(e.target.value)} />
          <button className="btn" onClick={loadAll}>Refresh</button>
        </div>
      </div>

      <div className="flex gap-2">
        <TabButton onClick={() => setTab('providers')} active={tab==='providers'} label={`Providers (${providers.length})`} />
        <TabButton onClick={() => setTab('agencies')} active={tab==='agencies'} label={`Agencies (${agencies.length})`} />
        <button className="btn" onClick={exportCSV}>Export CSV</button>
      </div>

      {loading ? (
        <div className="p-6"><div className="skel h-6 w-1/3 mb-3" /><div className="skel h-6 w-1/2" /></div>
      ) : (
        <div className="space-y-6">
          {tab === 'providers' && (
            <List type="provider" data={filteredProviders} busy={actionBusy} onAct={act} />
          )}
          {tab === 'agencies' && (
            <List type="agency" data={filteredAgencies} busy={actionBusy} onAct={act} />
          )}
        </div>
      )}
    </div>
  );
}

function TabButton({ active, onClick, label }) {
  return (
    <button onClick={onClick} className={`btn ${active ? 'btn-primary' : ''}`}>{label}</button>
  );
}

function List({ type, data, busy, onAct }) {
  if (!data.length) {
    return <div className="p-6 text-slate-500">No pending {type}s</div>;
  }
  return (
    <div className="bg-white border rounded-lg">
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="text-left p-3">Business / Agency</th>
            <th className="text-left p-3">Email</th>
            <th className="text-left p-3">Submitted</th>
            <th className="text-left p-3">Status</th>
            <th className="text-left p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id} className="border-t">
              <td className="p-3">
                <div className="font-medium text-slate-900">{row.business_name || row.agency_name || '—'}</div>
                <div className="text-xs text-slate-500">{row.name || 'Pending Profile'}</div>
              </td>
              <td className="p-3">{row.email}</td>
              <td className="p-3">{row.created_at ? new Date(row.created_at).toLocaleDateString() : '—'}</td>
              <td className="p-3"><span className="px-2 py-1 text-xs rounded-full bg-amber-100 text-amber-800">{row.approval_status || 'pending'}</span></td>
              <td className="p-3">
                <div className="flex gap-2">
                  <button className="btn btn-sm" disabled={busy === row.id + type} onClick={() => onAct(type, row.id, false)}>
                    Reject
                  </button>
                  <button className="btn btn-sm btn-primary" disabled={busy === row.id + type} onClick={() => onAct(type, row.id, true)}>
                    Approve
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function filterList(list, q) {
  const s = (q || '').toLowerCase();
  if (!s) return list;
  return list.filter(x => [x.business_name, x.agency_name, x.name, x.email].some(v => (v||'').toLowerCase().includes(s)));
}

export default NavigatorApprovals;
