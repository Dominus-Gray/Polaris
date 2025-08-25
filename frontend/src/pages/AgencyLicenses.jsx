import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${API_BASE}/api`;

function AgencyLicenses() {
  const [licenses, setLicenses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [genLoading, setGenLoading] = useState(false);
  const [error, setError] = useState(null);

  const [quantity, setQuantity] = useState(5);
  const [expiresDays, setExpiresDays] = useState(90);

  const isApprovedError = useMemo(() => {
    if (!error) return false;
    return (error.status === 403) || (typeof error.message === 'string' && error.message.toLowerCase().includes('approved'));
  }, [error]);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, listRes] = await Promise.all([
        axios.get(`${API}/agency/licenses/stats`),
        axios.get(`${API}/agency/licenses`)
      ]);
      setStats(statsRes.data);
      setLicenses(listRes.data.licenses || []);
    } catch (e) {
      console.error('Failed to load licenses:', e);
      setError({ status: e.response?.status, message: e.response?.data?.detail || e.message });
    } finally {
      setLoading(false);
    }
  };

  const generateCodes = async () => {
    if (!quantity || quantity < 1 || quantity > 100) {
      toast.error('Quantity must be between 1 and 100');
      return;
    }
    if (!expiresDays || expiresDays < 7 || expiresDays > 365) {
      toast.error('Expiry must be between 7 and 365 days');
      return;
    }

    setGenLoading(true);
    try {
      const { data } = await axios.post(`${API}/agency/licenses/generate`, {
        quantity: Number(quantity),
        expires_days: Number(expiresDays)
      });
      toast.success(data.message || 'License codes generated');
      await loadAll();
      if (data.usage_update) {
        toast.info('Monthly usage updated', { description: `This month: ${data.usage_update.codes_generated_this_month} / ${data.usage_update.monthly_limit}` });
      }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      toast.error('Failed to generate codes', { description: msg });
      setError({ status: e.response?.status, message: msg });
    } finally {
      setGenLoading(false);
    }
  };

  const copyCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success('License code copied');
    } catch (e) {
      toast.error('Failed to copy');
    }
  };

  const exportCSV = () => {
    if (!licenses.length) return;
    const headers = ['license_code', 'status', 'created_at', 'expires_at', 'used_by', 'used_at'];
    const rows = licenses.map(l => ([
      l.license_code,
      l.status,
      l.created_at ? new Date(l.created_at).toISOString() : '',
      l.expires_at ? new Date(l.expires_at).toISOString() : '',
      l.used_by || '',
      l.used_at ? new Date(l.used_at).toISOString() : ''
    ]));
    const csv = [headers.join(','), ...rows.map(r => r.map(v => typeof v === 'string' && v.includes(',') ? `"${v.replace(/"/g, '""')}"` : v).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'agency_licenses.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (isApprovedError) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-amber-900 mb-2">Agency Approval Required</h3>
        <p className="text-sm text-amber-800">
          Your agency must be approved by a Digital Navigator before you can generate license codes for clients.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Generator */}
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">Generate License Codes</h3>
          <button className="btn btn-outline btn-sm" onClick={loadAll}>Refresh</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Quantity</label>
            <input type="number" className="input w-full" value={quantity} min={1} max={100} onChange={e => setQuantity(Number(e.target.value))} />
            <div className="text-xs text-slate-500 mt-1">1 - 100 per request</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Expires In (days)</label>
            <input type="number" className="input w-full" value={expiresDays} min={7} max={365} onChange={e => setExpiresDays(Number(e.target.value))} />
            <div className="text-xs text-slate-500 mt-1">7 - 365 days</div>
          </div>
          <div className="flex items-end">
            <button className="btn btn-primary w-full" onClick={generateCodes} disabled={genLoading}>
              {genLoading ? 'Generating...' : 'Generate Codes'}
            </button>
          </div>
        </div>
        {error && !isApprovedError && (
          <div className="mt-3 text-sm text-red-600">{error.message}</div>
        )}
      </div>

      {/* Stats */}
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">License Usage</h3>
        {stats ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatTile label="Total Generated" value={stats.total_generated} />
            <StatTile label="Available" value={stats.available} />
            <StatTile label="Used" value={stats.used} />
            <StatTile label="Expired" value={stats.expired} />
          </div>
        ) : (
          <div className="text-sm text-slate-500">No statistics available</div>
        )}
      </div>

      {/* List */}
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">License Codes</h3>
          <div className="flex gap-2">
            <button className="btn btn-sm" onClick={exportCSV}>Export CSV</button>
          </div>
        </div>

        {licenses.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No license codes generated yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left py-2 px-3">Code</th>
                  <th className="text-left py-2 px-3">Status</th>
                  <th className="text-left py-2 px-3">Created</th>
                  <th className="text-left py-2 px-3">Expires</th>
                  <th className="text-left py-2 px-3">Used By</th>
                  <th className="text-left py-2 px-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {licenses.map((l) => (
                  <tr key={l._id || l.license_code} className="border-t">
                    <td className="py-2 px-3 font-mono">{l.license_code}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusPill(l.status)}`}>
                        {l.status}
                      </span>
                    </td>
                    <td className="py-2 px-3">{l.created_at ? new Date(l.created_at).toLocaleDateString() : '—'}</td>
                    <td className="py-2 px-3">{l.expires_at ? new Date(l.expires_at).toLocaleDateString() : '—'}</td>
                    <td className="py-2 px-3">{l.used_by ? shortId(l.used_by) : '—'}</td>
                    <td className="py-2 px-3">
                      <button className="btn btn-xs" onClick={() => copyCode(l.license_code)}>Copy</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatTile({ label, value }) {
  return (
    <div className="p-4 border rounded-lg bg-slate-50">
      <div className="text-sm text-slate-600">{label}</div>
      <div className="text-2xl font-bold text-slate-900">{value}</div>
    </div>
  );
}

function statusPill(status) {
  switch (status) {
    case 'available':
      return 'bg-green-100 text-green-800';
    case 'used':
      return 'bg-blue-100 text-blue-800';
    case 'expired':
      return 'bg-slate-200 text-slate-700';
    default:
      return 'bg-slate-100 text-slate-800';
  }
}

function shortId(id) {
  if (!id) return '';
  return id.length > 8 ? `${id.slice(0, 4)}…${id.slice(-4)}` : id;
}

export default AgencyLicenses;
