import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const API = `${API_BASE}/api`;

function CertificationCenter() {
  const navigate = useNavigate();
  const [certs, setCerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

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

  const copyShareLink = async (certId) => {
    try {
      const shareUrl = `${window.location.origin}/verify/cert/${certId}`;
      await navigator.clipboard.writeText(shareUrl);
      toast.success('Share link copied');
    } catch (e) {
      toast.error('Failed to copy link');
    }
  };

  const downloadCertificate = async (certId) => {
    setDownloadingId(certId);
    try {
      // Hit the download endpoint; backend currently returns JSON (PDF coming soon)
      const { data } = await axios.get(`${API}/certificates/${certId}/download`);
      toast.success('Certificate ready', { description: data.download_note || 'Downloaded data returned' });
      // For now, open the JSON response in a new tab for visibility
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `certificate-${certId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      toast.error('Failed to download', { description: msg });
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="skel h-24 w-full" />
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-5xl">
      <div className="bg-gradient-to-r from-[#0F172A] to-[#1B365D] rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Certification Center</h1>
            <p className="text-blue-100">Generate and manage your procurement readiness certificates</p>
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
                  <button className="btn btn-sm" onClick={() => copyShareLink(c.id)}>Copy Share Link</button>
                  <button className="btn btn-sm btn-primary" disabled={downloadingId === c.id} onClick={() => downloadCertificate(c.id)}>
                    {downloadingId === c.id ? 'Preparing…' : 'Download'}
                  </button>
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