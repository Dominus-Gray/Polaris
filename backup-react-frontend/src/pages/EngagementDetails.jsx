import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function EngagementDetails() {
  const { engagementId } = useParams();
  const navigate = useNavigate();
  const [eng, setEng] = useState(null);
  const [tracking, setTracking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionBusy, setActionBusy] = useState(false);

  useEffect(() => { load(); }, [engagementId]);

  const load = async () => {
    setLoading(true);
    try {
      // Load tracking first
      const { data: tr } = await axios.get(`${API}/engagements/${engagementId}/tracking`);
      setTracking(tr.tracking_entries || []);

      // Try to hydrate summary from my-services list
      try {
        const { data: mine } = await axios.get(`${API}/engagements/my-services`);
        const found = (mine.engagements || []).find(e => (e._id === engagementId) || (e.id === engagementId) || (e.engagement_id === engagementId));
        if (found) setEng(found);
      } catch {}

      if (!eng) setEng({ id: engagementId, status: (tr.engagement?.status || 'active'), title: tr.engagement?.title });
    } catch (e) {
      console.error('Failed to load engagement', e);
      toast.error('Unable to load engagement');
    } finally {
      setLoading(false);
    }
  };

  const setStatus = async (status) => {
    setActionBusy(true);
    try {
      await axios.post(`${API}/engagements/${engagementId}/update`, { status });
      toast.success(`Status updated to ${status}`);
      await load();
    } catch (e) {
      toast.error('Failed to update', { description: e.response?.data?.detail || e.message });
    } finally {
      setActionBusy(false);
    }
  };

  const requestRevision = async () => {
    toast.info('Revision request sent');
  };

  if (loading) return <div className="container mt-6"><div className="skel h-6 w-1/3" /><div className="skel h-32 w-full mt-3" /></div>;
  if (!eng) return <div className="container mt-6"><div className="bg-white border rounded-lg p-6">Engagement not found</div></div>;

  const events = buildTimeline(eng, tracking);

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="bg-white border rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Engagement Details</h1>
            <p className="text-slate-600 text-sm">Service: {eng.title || eng.service_title || 'Service Request'}</p>
          </div>
          <div>
            <span className={`px-3 py-1 rounded-full text-sm ${statusPill(eng.status)}`}>{String(eng.status||'active').replace('_',' ')}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-6">
          {/* Timeline */}
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Timeline</h3>
            <ol className="relative border-s border-slate-200">
              {events.map((t, idx) => (
                <li key={idx} className="ms-6 mb-6">
                  <span className={`absolute -start-2.5 flex h-5 w-5 items-center justify-center rounded-full ${t.color} ring-2 ring-white`}></span>
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-slate-900">{t.title}</h4>
                    <span className="text-xs text-slate-500">{new Date(t.at).toLocaleString()}</span>
                  </div>
                  {t.note && <p className="text-sm text-slate-600 mt-1">{t.note}</p>}
                </li>
              ))}
            </ol>
          </div>

          {/* Messages placeholder */}
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Messages</h3>
            <div className="text-slate-500 text-sm">Messaging coming soon.</div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Actions</h3>
            <div className="space-y-2">
              <button className="btn btn-primary w-full" disabled={actionBusy} onClick={() => setStatus('completed')}>Mark Complete</button>
              <button className="btn w-full" disabled={actionBusy} onClick={() => setStatus('on_hold')}>Put On Hold</button>
              <button className="btn w-full" disabled={actionBusy} onClick={requestRevision}>Request Revision</button>
              <button className="btn w-full" onClick={() => navigate('/home')}>Back to Dashboard</button>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Summary</h3>
            <div className="text-sm text-slate-600 space-y-1">
              <p><strong>Provider:</strong> {eng.provider_name || 'Assigned'}</p>
              <p><strong>Budget:</strong> {eng.budget ? `$${eng.budget}` : '—'}</p>
              <p><strong>Started:</strong> {eng.created_at ? new Date(eng.created_at).toLocaleDateString() : '—'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function buildTimeline(eng, tracking = []) {
  const events = [];
  if (eng?.created_at) events.push({ title: 'Requested', at: eng.created_at, color: 'bg-slate-400' });
  // Merge tracking entries
  for (const t of tracking){
    const mapColor = {
      accepted: 'bg-blue-500',
      in_progress: 'bg-indigo-500',
      delivered: 'bg-amber-500',
      completed: 'bg-emerald-600',
      on_hold: 'bg-slate-400'
    };
    events.push({ title: (t.status||'update').replace('_',' '), at: t.updated_at || t.timestamp || Date.now(), color: mapColor[t.status] || 'bg-slate-400', note: t.notes });
  }
  if (!events.length) events.push({ title: String(eng?.status||'active'), at: eng?.updated_at || eng?.created_at || Date.now(), color: 'bg-slate-400' });
  // Sort by time
  events.sort((a,b)=> new Date(a.at) - new Date(b.at));
  return events;
}

function statusPill(status) {
  switch (status) {
    case 'active': return 'bg-blue-100 text-blue-800';
    case 'on_hold': return 'bg-amber-100 text-amber-800';
    case 'completed': return 'bg-emerald-100 text-emerald-800';
    case 'cancelled': return 'bg-rose-100 text-rose-800';
    default: return 'bg-slate-100 text-slate-700';
  }
}

export default EngagementDetails;