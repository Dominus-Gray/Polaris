import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function RPSharePage(){
  const [rpTypes, setRpTypes] = useState([]);
  const [rpType, setRpType] = useState('lenders');
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const loadTypes = async () => {
    try{
      const { data } = await axios.get('/v2/rp/requirements/all');
      const items = data.items || [];
      setRpTypes(items.map(i=>i.rp_type));
      if(items.length && !items.find(i=>i.rp_type===rpType)) setRpType(items[0].rp_type);
    }catch(e){ /* ignore */ }
  };
  useEffect(()=>{ loadTypes(); }, []);

  const loadPreview = async () => {
    setLoading(true); setError(''); setPreview(null);
    try{
      const { data } = await axios.get('/v2/rp/package-preview', { params: { rp_type: rpType } });
      setPreview(data);
    }catch(e){ setError(e.response?.data?.detail || e.message); }
    finally{ setLoading(false); }
  };

  const createLead = async () => {
    try{
      await axios.post('/api/v2/rp/leads', { rp_type: rpType });
      navigate('/rp');
    }catch(e){ alert(e.response?.data?.detail || e.message); }
  };

  return (
    <div className="container mt-6 max-w-5xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Share with Resource Partner</h2>
      </div>

      <div className="bg-white border rounded-xl p-4 mb-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="form-label">Resource Partner Type</label>
            <select className="input" value={rpType} onChange={e=>setRpType(e.target.value)}>
              {rpTypes.length ? rpTypes.map(t=> <option key={t} value={t}>{t}</option>) : (
                ['lenders','bonding_agents','investors','business_development_orgs','procurement_offices','prime_contractors','accelerators','banks'].map(t=> <option key={t} value={t}>{t}</option>)
              )}
            </select>
          </div>
          <div className="flex items-end">
            <button className="btn btn-primary" onClick={loadPreview}>Preview Package</button>
          </div>
        </div>
      </div>

      {loading && (<div className="state-loading"><div className="spinner" /></div>)}
      {error && (<div className="state-error mb-3"><div className="title">Failed to load preview</div><div className="sub">{error}</div></div>)}

      {preview && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white border rounded-xl p-4">
            <div className="text-sm font-medium mb-2">Package</div>
            <pre className="bg-slate-50 rounded p-3 text-xs overflow-auto">{JSON.stringify(preview.package, null, 2)}</pre>
          </div>
          <div className="bg-white border rounded-xl p-4">
            <div className="text-sm font-medium mb-2">Missing Prerequisites</div>
            {(preview.missing||[]).length ? (
              <ul className="list-disc pl-6 text-sm">
                {preview.missing.map(m => <li key={m}>{m}</li>)}
              </ul>
            ) : (
              <div className="text-sm text-emerald-700">None</div>
            )}
            { (preview.missing||[]).length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="text-sm text-slate-700">Remediate using:</div>
                <div className="flex flex-wrap gap-2">
                  <button className="btn" onClick={()=>navigate('/service-request')}>Request Professional Help</button>
                  <button className="btn" onClick={()=>navigate('/external-resources/area1')}>Find Local Resources</button>
                  <button className="btn" onClick={()=>navigate('/knowledge-base')}>Self-Serve Knowledge Base</button>
                </div>
              </div>
            )}
            <div className="mt-4"><button className="btn btn-primary" onClick={createLead}>Create Lead</button></div>
          </div>
        </div>
      )}
    </div>
  );
}