import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AgencySponsoredClients(){
  const [loading, setLoading] = useState(true);
  const [clients, setClients] = useState([]);
  const [q, setQ] = useState('');

  useEffect(()=>{ load(); },[]);
  const load = async()=>{
    setLoading(true);
    try{
      const {data} = await axios.get(`${API}/agency/clients/accepted`);
      setClients(data.clients||[]);
    }catch(e){ toast.error('Failed to load clients'); }
    finally{ setLoading(false); }
  };

  const filtered = useMemo(()=>{
    const s = q.toLowerCase();
    if(!s) return clients;
    return clients.filter(c => [c.email, c.business_name].some(v => (v||'').toLowerCase().includes(s)));
  },[q, clients]);

  const downloadCSV = async (client) => {
    try{
      const { data } = await axios.get(`${API}/agency/clients/${client.id}/assessment`);
      const headers = ['user_id','business_name','email','completion','gaps_count'];
      const row = [client.id, client.business_name||'', client.email||'', data.completion_percentage || 0, (data.gaps||[]).length];
      const csv = [headers.join(','), row.map(v => typeof v==='string'&&v.includes(',')?`"${v.replace(/"/g,'""')}"`:v).join(',')].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = `client_${client.id}_assessment.csv`; a.click(); URL.revokeObjectURL(url);
      toast.success('CSV downloaded');
    }catch(e){ toast.error('Download failed', { description: e.response?.data?.detail || e.message }); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Sponsored Companies</h2>
          <p className="text-sm text-slate-600">View company info and download assessment status</p>
        </div>
        <div className="flex items-center gap-2">
          <input className="input" placeholder="Search" value={q} onChange={e=>setQ(e.target.value)} />
          <button className="btn" onClick={load}>Refresh</button>
        </div>
      </div>

      <div className="bg-white border rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left p-3">Company</th>
              <th className="text-left p-3">Email</th>
              <th className="text-left p-3">Location</th>
            <th className="text-left p-3">Accepted</th>
              <th className="text-left p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} className="p-6"><div className="skel h-6 w-1/3 mb-2" /><div className="skel h-6 w-1/2" /></td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={4} className="p-6 text-slate-500">No sponsored companies found</td></tr>
            ) : (
              filtered.map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="p-3">
                    <div className="font-medium text-slate-900">{c.business_name || '—'}</div>
                    <div className="text-xs text-slate-500">{c.license_code ? `License: ${c.license_code}` : ''}</div>
                  </td>
                  <td className="p-3">{c.email}</td>
                  <td className="p-3">{c.accepted_at ? new Date(c.accepted_at).toLocaleDateString() : '—'}</td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <button className="btn btn-sm" onClick={()=>downloadCSV(c)}>Download Assessment CSV</button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
