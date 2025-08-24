import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = process.env.REACT_APP_BACKEND_URL; // Frontend must use env
const API = `${API_BASE}/api`;

function ActionPlanPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="container mt-6 max-w-5xl">
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Action Plan</h1>
            <p className="text-blue-100">Personalized next steps based on your assessment</p>
            {sessionId && (
              <div className="text-sm text-blue-200 mt-2">Session: {sessionId}</div>
            )}
          </div>
          <button className="btn glass" onClick={() => navigate('/assessment')}>
            Back to Assessment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">High Priority Actions</h2>
          <ul className="space-y-3 text-sm text-slate-700">
            <li>• Address critical compliance gaps in your weakest areas</li>
            <li>• Upload missing evidence for completed requirements</li>
            <li>• Schedule a consultation with a verified provider</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Resources</h2>
          <div className="space-y-2 text-sm text-slate-700">
            <p>• Use the Knowledge Base to download templates and checklists</p>
            <p>• Explore external free resources recommended for your gaps</p>
            <p>• Track progress on the Readiness Dashboard</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ActionPlanPage;