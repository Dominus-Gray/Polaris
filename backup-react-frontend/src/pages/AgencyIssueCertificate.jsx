import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${API_BASE}/api`;

function AgencyIssueCertificate() {
  const [clients, setClients] = useState([]);
  const [clientId, setClientId] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/agency/clients?status=accepted`);
      setClients(data.clients || []);
    } catch (e) {
      console.error('Failed to load clients', e);
      toast.error('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const issue = async () => {
    if (!clientId) {
      toast.error('Select a client');
      return;
    }
    setSubmitting(true);
    try {
      const { data } = await axios.post(`${API}/agency/certificates/issue`, { client_user_id: clientId });
      toast.success('Certificate issued', { description: `Verification: ${data.verification_code}` });
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      toast.error('Failed to issue certificate', { description: msg });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="p-6"><div className="skel h-5 w-40" /></div>;

  return (
    <div className="space-y-6">
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Issue Certificate</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Client</label>
            <select className="input w-full" value={clientId} onChange={(e) => setClientId(e.target.value)}>
              <option value="">— Choose —</option>
              {clients.map(c => (
                <option key={c.id} value={c.id}>{c.business_name || c.email}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button className="btn btn-primary w-full" onClick={issue} disabled={submitting}>
              {submitting ? 'Issuing…' : 'Issue Certificate'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgencyIssueCertificate;
