import React from 'react';

export default function ClientRemediationFilters(){
  const [setAsides, setSetAsides] = React.useState(()=>new Set(JSON.parse(localStorage.getItem('polaris_filters_setasides')||'[]')));
  const [location, setLocation] = React.useState(localStorage.getItem('polaris_filters_location')||'local');
  const [budget, setBudget] = React.useState(localStorage.getItem('polaris_filters_budget')||'any');
  const [naics, setNaics] = React.useState(localStorage.getItem('polaris_filters_naics')||'');

  const toggle = (code)=>{
    const s = new Set(setAsides);
    if(s.has(code)) s.delete(code); else s.add(code);
    setSetAsides(s);
  };

  const apply = ()=>{
    localStorage.setItem('polaris_filters_setasides', JSON.stringify(Array.from(setAsides)));
    localStorage.setItem('polaris_filters_location', location);
    localStorage.setItem('polaris_filters_budget', budget);
    localStorage.setItem('polaris_filters_naics', naics);
    if(window?.toast){ window.toast.success('Filters saved'); }
  };

  const options = ['MBE','WOSB','SDVOSB','VOSB','HUBZone','8(a)','DBE','SBE'];

  return (
    <div className="bg-white border rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-900">Filter Free Help & Providers</h3>
        <button className="btn btn-sm" onClick={apply}>Apply</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div>
          <div className="text-xs text-slate-600 mb-1">Set-aside</div>
          <div className="flex flex-wrap gap-2">
            {options.map(o => (
              <button key={o} className={`px-2 py-1 rounded-full text-xs border ${setAsides.has(o)?'bg-primary text-white':'bg-gray-50 text-gray-700'}`} onClick={()=>toggle(o)}>{o}</button>
            ))}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-600 mb-1">Location</div>
          <select className="input w-full bg-white text-gray-700" value={location} onChange={e=>setLocation(e.target.value)}>
            <option value="local">Local</option>
            <option value="state">State</option>
            <option value="national">National</option>
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-600 mb-1">Budget</div>
          <select className="input w-full bg-white text-gray-700" value={budget} onChange={e=>setBudget(e.target.value)}>
            <option value="any">Any</option>
            <option value="<1000">Under $1,000</option>
            <option value="1000-2500">$1,000 - $2,500</option>
            <option value=">2500">Above $2,500</option>
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-600 mb-1">NAICS</div>
          <input className="input w-full" placeholder="e.g., 541611" value={naics} onChange={e=>setNaics(e.target.value)} />
        </div>
      </div>
    </div>
  );
}