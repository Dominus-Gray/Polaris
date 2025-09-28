import React from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AgencyContractMatching(){
  const [contracts, setContracts] = React.useState([]);
  const [form, setForm] = React.useState({ title:'', buyer:'', naics:'', setaside:'', location:'local', min_maturity:60, capacity:'', due:'', link:'' });
  const [clients, setClients] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(()=>{ load(); },[]);
  const load = async()=>{
    setLoading(true);
    try{
      const { data } = await axios.get(`${API}/agency/clients/accepted`);
      setClients(data.clients||[]);
    }catch(e){ setClients([]); }
    finally{ setLoading(false); }
  };

  const addContract = ()=>{
    if(!form.title) return;
    setContracts(prev=>[...prev, {...form, id: crypto.randomUUID()}]);
    setForm({ title:'', buyer:'', naics:'', setaside:'', location:'local', min_maturity:60, capacity:'', due:'', link:'' });
  };

  const suggestions = (c)=>{
    const comp = c.completion_percentage || 0; // we don't have directly; will fetch on demand
    return comp; // placeholder
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Add Contract Opportunity (UI-only)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="input" placeholder="Title" value={form.title} onChange={e=>setForm({...form, title:e.target.value})} />
          <input className="input" placeholder="Buyer" value={form.buyer} onChange={e=>setForm({...form, buyer:e.target.value})} />
          <input className="input" placeholder="NAICS" value={form.naics} onChange={e=>setForm({...form, naics:e.target.value})} />
          <input className="input" placeholder="Set-aside (e.g., MBE, WOSB)" value={form.setaside} onChange={e=>setForm({...form, setaside:e.target.value})} />
          <select className="input" value={form.location} onChange={e=>setForm({...form, location:e.target.value})}>
            <option value="local">Local</option>
            <option value="state">State</option>
            <option value="national">National</option>
          </select>
          <input className="input" placeholder="Min Maturity %" type="number" value={form.min_maturity} onChange={e=>setForm({...form, min_maturity:Number(e.target.value)})} />
          <input className="input" placeholder="Capacity Needed (e.g., staff)" value={form.capacity} onChange={e=>setForm({...form, capacity:e.target.value})} />
          <input className="input" placeholder="Due Date" value={form.due} onChange={e=>setForm({...form, due:e.target.value})} />
          <input className="input" placeholder="Link" value={form.link} onChange={e=>setForm({...form, link:e.target.value})} />
        </div>
        <div className="mt-3 text-right">
          <button className="btn" onClick={addContract}>Add Contract</button>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Contract Matches (read-only)</h3>
        {contracts.length === 0 ? (
          <div className="text-slate-500">No contracts added yet</div>
        ) : (
          <div className="space-y-4">
            {contracts.map(ct => (
              <div key={ct.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold text-slate-900">{ct.title}</div>
                  <a className="text-blue-600 text-sm" href={ct.link||'#'} target="_blank" rel="noreferrer">View</a>
                </div>
                <div className="text-xs text-slate-500 mb-3">Buyer: {ct.buyer || '—'} • NAICS: {ct.naics || '—'} • Set-aside: {ct.setaside || '—'} • Min Maturity: {ct.min_maturity}% • Location: {ct.location}</div>
                <MatchesList contract={ct} clients={clients} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MatchesList({ contract, clients }){
  const [rows, setRows] = React.useState([]);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(()=>{ load(); },[contract, clients]);
  const load = async()=>{
    setLoading(true);
    try{
      // fetch completion for each client
      const arr = [];
      for(const c of clients.slice(0, 30)){
        try{
          const { data } = await axios.get(`${API}/agency/clients/${c.id}/assessment`);
          const ok = (data.completion_percentage||0) >= (contract.min_maturity||0);
          arr.push({ client: c, completion: data.completion_percentage||0, ok });
        }catch{
          arr.push({ client: c, completion: 0, ok: false });
        }
      }
      // simple sort by completion desc
      arr.sort((a,b)=>b.completion - a.completion);
      setRows(arr);
    } finally {
      setLoading(false);
    }
  };

  if(loading) return <div className="text-slate-500 text-sm">Scanning sponsored companies…</div>;
  if(rows.length===0) return <div className="text-slate-500 text-sm">No sponsored companies available for matching</div>;

  return (
    <div className="space-y-2">
      {rows.map((r, idx)=> (
        <div key={idx} className={`p-3 border rounded-lg flex items-center justify-between ${r.ok?'bg-emerald-50':'bg-slate-50'}`}>
          <div>
            <div className="font-medium text-slate-900">{r.client.business_name || r.client.email}</div>
            <div className="text-xs text-slate-500">Completion: {r.completion}%</div>
          </div>
          <div>
            <span className={`px-2 py-1 rounded-full text-xs ${r.ok?'bg-emerald-100 text-emerald-800':'bg-slate-200 text-slate-700'}`}>{r.ok?'Good Fit':'Needs Improvement'}</span>
          </div>
        </div>
      ))}
    </div>
  );
}