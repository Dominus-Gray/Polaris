import React from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AgencySponsorKPIs(){
  const [loading, setLoading] = React.useState(true);
  const [kpis, setKpis] = React.useState({ total_invited: 0, accepted: 0, avg_completion: 0, top_gaps: [] });
  const [error, setError] = React.useState(null);

  React.useEffect(()=>{
    let mounted = true;
    const load = async()=>{
      setLoading(true);
      try{
        const { data } = await axios.get(`${API}/agency/clients/accepted`);
        const clients = data.clients || [];
        const accepted = clients.length;
        let avg = 0;
        let count = 0;
        const gapMap = {};
        for(const c of clients.slice(0,50)){
          try{
            const { data: a } = await axios.get(`${API}/agency/clients/${c.id}/assessment`);
            const comp = a.completion_percentage || 0;
            avg += comp; count += 1;
            (a.gaps||[]).forEach(g => { gapMap[g.area_id] = (gapMap[g.area_id]||0)+1; });
          }catch{}
        }
        const top_gaps = Object.entries(gapMap).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,v])=>({ area_id:k, count:v }));
        const avg_completion = count ? Math.round(avg / count) : 0;
        if(mounted) setKpis({ total_invited: undefined, accepted, avg_completion, top_gaps });
      }catch(e){ if(mounted) setError(e.message); }
      finally{ if(mounted) setLoading(false); }
    };
    load();
    return ()=>{ mounted=false };
  },[]);

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-slate-900">Sponsor Impact</h3>
        <button className="btn btn-sm" onClick={()=>window.location.reload()}>Refresh</button>
      </div>
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i=> <div key={i} className="skel h-16" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Kpi label="Accepted Companies" value={kpis.accepted} />
          <Kpi label="Avg Completion" value={`${kpis.avg_completion}%`} />
          <Kpi label="Top Gap 1" value={(kpis.top_gaps[0]?.area_id||'—').toUpperCase()} />
          <Kpi label="Top Gap 2" value={(kpis.top_gaps[1]?.area_id||'—').toUpperCase()} />
        </div>
      )}
      {error && <div className="mt-3 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">{String(error)}</div>}
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