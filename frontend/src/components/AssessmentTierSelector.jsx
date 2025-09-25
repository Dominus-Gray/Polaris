import React from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TIER1 = {
  area1: [
    'Entity is legally formed and in good standing with the state',
    'EIN is active and bank account is in business name',
    'DUNS/UEI obtained and active'
  ],
  area2: [
    'Dedicated business bank account with monthly reconciliation',
    'Basic accounting system in use (QB/Xero)',
    'Invoices/receipts tracked systematically'
  ],
  area3: [
    'Standard T&C and NDA templates maintained',
    'Insurance coverage meets baseline',
    'Active registrations for target contracts exist'
  ],
  area4: [
    'Documented SOPs for core services/products',
    'Basic QC checklist used for deliveries',
    'Nonconformance and corrective action process exists'
  ],
  area5: [
    'Endpoint protection and patching schedule enforced',
    'MFA enabled for business accounts',
    'Regular data backups implemented'
  ],
  area6: [
    'Employee handbook and job descriptions exist',
    'Payroll and timekeeping systems in place',
    'Onboarding and offboarding checklists documented'
  ],
  area7: [
    'Defined delivery KPIs (OTD, quality, satisfaction)',
    'Milestone tracking exists for engagements',
    'Monthly KPI review occurs'
  ],
  area8: [
    'Risk register exists for key projects',
    'Basic Business Continuity Plan drafted',
    'Data backup and recovery documented'
  ],
  area9: [
    'Approved vendor list maintained',
    'Basic vendor evaluation criteria used',
    'PO and receiving controls exist'
  ]
};

export default function AssessmentTierSelector(){
  const [tier, setTier] = React.useState('tier1');
  const [saving, setSaving] = React.useState(false);

  const onToggle = async (areaId, idx, value)=>{
    const qid = `${areaId}_t1_q${idx+1}`;
    try{
      setSaving(true);
      await axios.post(`${API}/assessment/answer`, { question_id: qid, answer: value?'yes':'no_help' });
    }catch(e){ /* non-blocking */ }
    finally{ setSaving(false); }
  };

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Assessment Tier</span>
          <div className="inline-flex rounded-full overflow-hidden border">
            <button className={`px-3 py-1 text-sm ${tier==='tier1'?'bg-primary text-white':'bg-gray-100'}`} onClick={()=>setTier('tier1')}>Tier 1</button>
            <button className="px-3 py-1 text-sm bg-slate-50 text-slate-400 cursor-not-allowed" disabled>Tier 2</button>
            <button className="px-3 py-1 text-sm bg-slate-50 text-slate-400 cursor-not-allowed" disabled>Tier 3</button>
          </div>
        </div>
        {saving && <div className="text-xs text-slate-500">Saving…</div>}
      </div>

      {tier==='tier1' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(TIER1).map(([areaId, statements]) => (
            <div key={areaId} className="p-4 border rounded-lg">
              <div className="font-semibold text-slate-900 mb-2">{areaLabel(areaId)}</div>
              <ul className="space-y-2">
                {statements.map((s, i)=> (
                  <li key={i} className="flex items-center justify-between gap-3">
                    <span className="text-sm text-slate-700">{s}</span>
                    <div className="toggle">
                      <button className="off" onClick={()=>onToggle(areaId, i, false)}>No</button>
                      <button className="on" onClick={()=>onToggle(areaId, i, true)}>Yes</button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function areaLabel(id){
  const m = {
    area1: 'Business Formation & Registration',
    area2: 'Financial Operations & Management',
    area3: 'Legal & Contracting Compliance',
    area4: 'Quality Management & Standards',
    area5: 'Technology & Security Infrastructure',
    area6: 'Human Resources & Capacity',
    area7: 'Performance Tracking & Reporting',
    area8: 'Risk Management & Business Continuity',
    area9: 'Supply Chain Management & Vendor Relations',
  };
  return m[id] || id;
}