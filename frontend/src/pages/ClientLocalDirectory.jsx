import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SA_RESOURCES = [
  { name: 'City of San Antonio Vendor (Bonfire)', url: 'https://sanantonio.bonfirehub.com/portal', type: 'city_vendor' },
  { name: 'Bexar County Purchasing', url: 'https://www.bexar.org/3430/Purchasing', type: 'county_vendor' },
  { name: 'CPS Energy Procurement', url: 'https://www.cpsenergy.com/about/procurement.html', type: 'utility' },
  { name: 'SAWS Procurement', url: 'https://www.saws.org/business-center/purchasing/', type: 'utility' },
  { name: 'VIA Metro Transit Procurements', url: 'https://www.viainfo.net/current-procurements/', type: 'transit' },
  { name: 'UTSA SBDC (South Central Texas)', url: 'https://sasbdc.org/', type: 'sbdc' },
  { name: 'SCORE San Antonio', url: 'https://www.score.org/sanantonio', type: 'score' },
  { name: 'APEX Accelerator (PTAC) Locator', url: 'https://apexaccelerators.us/locator', type: 'ptac' },
  { name: 'Texas CMBL Vendor List', url: 'https://comptroller.texas.gov/purchasing/vendor/cmbl/', type: 'state_vendor' },
  { name: 'TxDOT Letting/Procurement', url: 'https://www.txdot.gov/business/let.htm', type: 'state_transport' },
];

function buildLocalList(profile){
  const city = profile?.city || profile?.business_city;
  const state = profile?.state || profile?.business_state;
  const list = [];
  if(city && state){
    const key = `${city}, ${state}`.toLowerCase();
    if(state?.toLowerCase() === 'texas' || state?.toLowerCase() === 'tx'){
      if(key.includes('san antonio')){
        list.push(...SA_RESOURCES);
      } else {
        list.push(
          { name: 'Texas CMBL Vendor List', url: 'https://comptroller.texas.gov/purchasing/vendor/cmbl/', type: 'state_vendor' },
          { name: 'APEX Accelerator (PTAC) Locator', url: 'https://apexaccelerators.us/locator', type: 'ptac' },
          { name: 'SBDC Texas Locator', url: 'https://txsbdc.org/locator/', type: 'sbdc' },
          { name: 'SBA Local Assistance', url: `https://www.sba.gov/local-assistance?state=${encodeURIComponent(state)}`, type: 'sba' }
        );
      }
    } else {
      list.push(
        { name: 'SBA Local Assistance', url: `https://www.sba.gov/local-assistance?state=${encodeURIComponent(state)}&city=${encodeURIComponent(city)}`, type: 'sba' },
        { name: 'APEX Accelerator (PTAC) Locator', url: 'https://apexaccelerators.us/locator', type: 'ptac' },
        { name: 'SBDC Locator', url: 'https://americassbdc.org/small-business-consulting-and-training/find-your-sbdc/', type: 'sbdc' },
        { name: 'SCORE Chapters', url: 'https://www.score.org/find-mentor', type: 'score' }
      );
    }
  } else {
    list.push(
      { name: 'SBA Local Assistance', url: 'https://www.sba.gov/local-assistance', type: 'sba' },
      { name: 'APEX Accelerator (PTAC) Locator', url: 'https://apexaccelerators.us/locator', type: 'ptac' },
      { name: 'SBDC Locator', url: 'https://americassbdc.org/small-business-consulting-and-training/find-your-sbdc/', type: 'sbdc' },
      { name: 'SCORE Chapters', url: 'https://www.score.org/find-mentor', type: 'score' }
    );
  }
  return list;
}

export default function ClientLocalDirectory(){
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    const load = async()=>{
      try{
        const { data } = await axios.get(`${API}/business/profile/me`);
        setProfile(data || null);
      }catch(e){ setProfile(null); }
      finally{ setLoading(false); }
    };
    load();
  },[]);

  const list = useMemo(()=>buildLocalList(profile), [profile]);

  return (
    <div className="container mt-6 max-w-5xl">
      <div className="bg-white border rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Local Resources Directory</h1>
        <p className="text-slate-600">Curated registration and assistance resources based on your business location.</p>
      </div>

      {loading ? (
        <div className="skel h-24 w-full" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {list.map((r, idx) => (
            <a key={idx} className="block p-4 border rounded-lg bg-white hover:shadow-sm transition" href={r.url} target="_blank" rel="noopener noreferrer" onClick={()=>{
              try{ axios.post(`${API}/analytics/resource-access`, { resource_id: r.url, gap_area: 'local_directory' }); }catch{}
            }}>
              <div className="font-semibold text-slate-900">{r.name}</div>
              <div className="text-xs text-slate-500 mt-1">{r.url}</div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}