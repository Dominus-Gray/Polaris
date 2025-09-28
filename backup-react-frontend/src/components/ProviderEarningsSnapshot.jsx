import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ProviderEarningsSnapshot(){
  const [kpis, setKpis] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const navigate = useNavigate();

  React.useEffect(()=>{
    let mounted = true;
    const load = async()=>{
      try{
        const {data} = await axios.get(`${API}/provider/revenue/analytics`);
        if (mounted) setKpis(data);
      }catch(e){
        console.warn('Earnings snapshot failed', e);
        if (mounted) setError(e.response?.data?.detail || e.message);
      }finally{ if (mounted) setLoading(false); }
    };
    load();
    return () => { mounted = false; };
  },[]);

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Earnings Snapshot</h3>
        <button className="btn btn-sm" onClick={()=>navigate('/provider/revenue-optimization')}>Open Revenue Center</button>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="skel h-16" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Kpi label="This Month" value={kpis ? `$${(kpis.current_month_revenue||0).toLocaleString()}` : '—'} />
          <Kpi label="YTD" value={kpis ? `$${(kpis.year_to_date||0).toLocaleString()}` : '—'} />
          <Kpi label="Conversion" value={kpis ? `${kpis.conversion_rate||0}%` : '—'} />
          <Kpi label="Active Requests" value={kpis ? `${kpis.active_proposals||0}` : '—'} />
        </div>
      )}

      {error && (
        <div className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded p-2 mt-3">
          {String(error)}
        </div>
      )}
    </div>
  );
}

function Kpi({label, value}){
  return (
    <div className="p-4 rounded-lg border bg-slate-50">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">{label}</div>
      <div className="text-xl font-bold text-slate-900">{value}</div>
    </div>
  );
}