import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ProviderRequestsCenter(){
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [tab, setTab] = React.useState('new');
  const [sort, setSort] = React.useState('newest');
  const [query, setQuery] = React.useState('');
  const navigate = useNavigate();

  React.useEffect(()=>{ load(); },[]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try{
      // Use provider orders endpoint as Requests Center source
      const { data } = await axios.get(`${API}/marketplace/orders/my?role_filter=provider`);
      const orders = data.orders || [];
      setItems(orders.map(o => ({
        id: o.engagement_id || o.order_id,
        title: o.title || 'Service Request',
        client_name: o.client_name,
        created_at: o.created_at,
        status: o.status,
        price: o.price,
        unread: !!o.unread,
        age_days: Math.floor((Date.now() - new Date(o.created_at)) / (1000*60*60*24))
      })));
    }catch(e){
      setError(e.response?.data?.detail || e.message);
    }finally{
      setLoading(false);
    }
  };

  const filtered = React.useMemo(()=>{
    let list = items.slice();
    // filter by tab
    const statusMap = {
      new: ['new','in_review'],
      awaiting_client: ['delivered','revision_requested'],
      in_progress: ['in_progress'],
      completed: ['completed']
    };
    list = list.filter(x => statusMap[tab].includes(x.status));
    if(query){
      const s = query.toLowerCase();
      list = list.filter(x => (
        (x.title||'').toLowerCase().includes(s) ||
        (x.client_name||'').toLowerCase().includes(s)
      ));
    }
    if(sort==='newest') list.sort((a,b)=> new Date(b.created_at) - new Date(a.created_at));
    if(sort==='unread') list.sort((a,b)=> (b.unread?1:0) - (a.unread?1:0));
    return list;
  }, [items, tab, sort, query]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <Tab label={`New (${items.filter(i=>['new','in_review'].includes(i.status)).length})`} active={tab==='new'} onClick={()=>setTab('new')} />
          <Tab label={`Awaiting Client (${items.filter(i=>['delivered','revision_requested'].includes(i.status)).length})`} active={tab==='awaiting_client'} onClick={()=>setTab('awaiting_client')} />
          <Tab label={`In Progress (${items.filter(i=>i.status==='in_progress').length})`} active={tab==='in_progress'} onClick={()=>setTab('in_progress')} />
          <Tab label={`Completed (${items.filter(i=>i.status==='completed').length})`} active={tab==='completed'} onClick={()=>setTab('completed')} />
        </div>
        <div className="flex items-center gap-2">
          <input className="input" placeholder="Search by client or title" value={query} onChange={e=>setQuery(e.target.value)} />
          <select className="input" value={sort} onChange={e=>setSort(e.target.value)}>
            <option value="newest">Newest</option>
            <option value="unread">Unread first</option>
          </select>
          <button className="btn" onClick={load}>Refresh</button>
        </div>
      </div>

      {loading ? (
        <div className="p-4"><div className="skel h-6 w-40 mb-2" /><div className="skel h-6 w-64" /></div>
      ) : error ? (
        <div className="p-4 text-amber-700 bg-amber-50 border border-amber-200 rounded">{error}</div>
      ) : filtered.length === 0 ? (
        <div className="text-slate-500 p-6">No items to show</div>
      ) : (
        <div className="space-y-2">
          {filtered.map(it => (
            <div key={it.id} className={`border rounded-lg p-4 bg-white flex items-center justify-between ${it.age_days>7?'ring-1 ring-amber-300':''}`}>
              <div>
                <div className="font-medium text-slate-900">{it.title}</div>
                <div className="text-sm text-slate-600">Client: {it.client_name || '—'} • ${ (it.price/100).toFixed(2) } • {new Date(it.created_at).toLocaleString()}</div>
                <div className="text-xs text-slate-500 mt-1">Status: <span className="px-2 py-0.5 rounded-full bg-slate-100">{it.status.replace('_',' ')}</span> {it.unread && <span className="ml-2 text-blue-700">• Unread</span>}</div>
              </div>
              <div className="flex items-center gap-2">
                <button className="btn btn-sm" onClick={()=>navigate(`/engagements/${it.id}`)}>Open</button>
                <button className="btn btn-sm" onClick={()=>navigate(`/engagements/${it.id}`)}>Respond</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Tab({label, active, onClick}){
  return (
    <button onClick={onClick} className={`btn ${active?'btn-primary':''}`}>{label}</button>
  );
}