import React, { useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DEFAULT_ITEMS = [
  { rp_type: 'lenders', required_fields: [
    'contact_email','readiness_score','annual_revenue','average_monthly_revenue','ar_ap_summary','merchant_processing_history','years_in_business','beneficial_owners','licenses_status','insurance_status','good_standing_attestation'
  ]},
  { rp_type: 'bonding_agents', required_fields: [
    'contact_email','readiness_score','years_in_business','licenses_status','insurance_status','bonding_history_summary','prior_contract_values','financial_summary_bands','good_standing_attestation'
  ]},
  { rp_type: 'investors', required_fields: [
    'contact_email','readiness_score','annual_revenue','growth_plan_summary','pitch_deck_url','cap_table_summary','beneficial_owners','prior_funding_history','financial_summary_bands'
  ]},
  { rp_type: 'business_development_orgs', required_fields: [
    'contact_email','readiness_score','capabilities_statement','growth_plan_summary','past_performance_summary','certifications_list'
  ]},
  { rp_type: 'procurement_offices', required_fields: [
    'contact_email','readiness_score','sam_registration_status','cage_code','naics_codes','past_performance_summary','quality_certifications','capabilities_statement'
  ]},
  { rp_type: 'prime_contractors', required_fields: [
    'contact_email','readiness_score','capabilities_statement','past_performance_summary','quality_certifications','safety_program_attestation'
  ]},
  { rp_type: 'accelerators', required_fields: [
    'contact_email','readiness_score','growth_plan_summary','pitch_deck_url','value_proposition_summary','mentor_fit_preferences'
  ]},
  { rp_type: 'banks', required_fields: [
    'contact_email','readiness_score','annual_revenue','employee_count','beneficial_owners','banking_readiness','licenses_status','insurance_status','financial_summary_bands','good_standing_attestation'
  ]}
];

export default function RPRequirementsAdmin(){
  const [items, setItems] = useState([]);
  const [rpType, setRpType] = useState('lenders');
  const [fields, setFields] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  const loadAll = async () => {
    setLoading(true); setMsg('');
    try {
      const { data } = await axios.get(`${API}/v2/rp/requirements/all`);
      setItems(data.items || []);
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message);
    } finally { setLoading(false); }
  };
  useEffect(()=>{ loadAll(); }, []);

  const seedDefaults = async () => {
    try{
      await axios.post('/v2/rp/requirements/bulk', { items: DEFAULT_ITEMS });
      await loadAll();
    }catch(e){ setMsg(e.response?.data?.detail || e.message); }
  };

  const saveOne = async () => {
    try{
      const arr = fields.split('\n').map(s=>s.trim()).filter(Boolean);
      await axios.post('/v2/rp/requirements', { rp_type: rpType, required_fields: arr });
      setFields('');
      await loadAll();
    }catch(e){ setMsg(e.response?.data?.detail || e.message); }
  };

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">RP Requirements (Admin/Agency)</h2>
        <button className="btn btn-outline" onClick={seedDefaults}>Seed Defaults</button>
      </div>
      {loading && (<div className="state-loading"><div className="spinner" /></div>)}
      {msg && (<div className="state-error mb-3"><div className="title">Notice</div><div className="sub">{msg}</div></div>)}

      <div className="bg-white border rounded-xl p-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="form-label">RP Type</label>
            <select className="input" value={rpType} onChange={e=>setRpType(e.target.value)}>
              {['lenders','bonding_agents','investors','business_development_orgs','procurement_offices','prime_contractors','accelerators','banks'].map(t=> <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="form-label">Required Fields (one per line)</label>
            <textarea className="input" rows={6} value={fields} onChange={e=>setFields(e.target.value)} placeholder="contact_email\nreadiness_score\n..." />
          </div>
        </div>
        <div className="mt-3"><button className="btn btn-primary" onClick={saveOne}>Save</button></div>
      </div>

      <div className="bg-white border rounded-xl p-4">
        <div className="text-sm font-medium mb-2">Configured RP Types</div>
        <ul className="list-disc pl-6 text-sm">
          {items.map(it => (
            <li key={it.rp_type}><span className="font-medium">{it.rp_type}:</span> {(it.required_fields||[]).join(', ')}</li>
          ))}
          {!items.length && <li>No items yet.</li>}
        </ul>
      </div>
    </div>
  );
}