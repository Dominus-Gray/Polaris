import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${API_BASE}/api`;

function CertificationCenter() {
  const navigate = useNavigate();
  const [certs, setCerts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await axios.get(`${API}/client/certificates`);
        setCerts(data.certificates || []);
      } catch (e) {
        console.error('Failed to load certificates', e);
        setCerts([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="skel h-24 w-full" />
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-5xl">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Certification Center</h1>
            <p className="text-purple-100">Generate and manage your procurement readiness certificates</p>
          </div>
          <button className="btn glass" onClick={() => navigate('/readiness-dashboard')}>View Dashboard</button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6 border">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Your Certificates</h2>
        {(!certs || certs.length === 0) ? (
          <div className="text-slate-600 text-sm">No certificates yet. Complete your assessment and reach the required score to generate a certificate.</div>
        ) : (
          <div className="space-y-3">
            {certs.map((c) => (
              <div key={c.id} className="flex items-center justify-between border rounded-lg p-4">
                <div>
                  <div className="font-medium text-slate-900">{c.title || 'Small Business Maturity Assurance'}</div>
                  <div className="text-xs text-slate-500">Issued: {new Date(c.issued_at).toLocaleString()} • Score: {c.readiness_percent}%</div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-sm" onClick={() => navigate(`/verify/cert/${c.id}`)}>Verify</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CertificationCenter;