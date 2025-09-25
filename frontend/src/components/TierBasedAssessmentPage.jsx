import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = BACKEND_URL;

function TierBasedAssessmentPage() {
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [availableAreas, setAvailableAreas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAssessmentData();
  }, []);

  const loadAssessmentData = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const { data } = await axios.get(`${API}/assessment/schema/tier-based`, { headers });
      setAvailableAreas(data.areas || []);
    } catch (error) {
      console.error('Error loading assessment data:', error);
      // Fallback data - Complete 10 areas
      setAvailableAreas([
        { id: 'area1', name: 'Business Formation & Registration', description: 'Business formation, licenses, and legal requirements' },
        { id: 'area2', name: 'Financial Operations & Management', description: 'Accounting, cash flow, and financial controls' },
        { id: 'area3', name: 'Legal & Contracting Compliance', description: 'Contract management and legal compliance' },
        { id: 'area4', name: 'Quality Management & Standards', description: 'Quality systems and operational standards' },
        { id: 'area5', name: 'Technology & Security Infrastructure', description: 'IT infrastructure and cybersecurity' },
        { id: 'area6', name: 'Human Resources & Capacity', description: 'Staff management and HR policies' },
        { id: 'area7', name: 'Performance Tracking & Reporting', description: 'KPI tracking and client reporting' },
        { id: 'area8', name: 'Risk Management & Business Continuity', description: 'Risk mitigation and emergency planning' },
        { id: 'area9', name: 'Supply Chain Management & Vendor Relations', description: 'Vendor management and supply chain resilience' },
        { id: 'area10', name: 'Competitive Advantage & Market Position', description: 'Market differentiation and competitive strategy' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-slate-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Enhanced Tier-Based Assessment System</h1>
        <p className="text-xl text-slate-600">Comprehensive evaluation across 10 critical business areas</p>
      </div>

      {/* Business Areas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {availableAreas.map((area) => (
          <div key={area.id} className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-all duration-200">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{area.name}</h3>
                <p className="text-sm text-slate-600">{area.description}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-bold">{area.id.replace('area', '')}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-sm text-slate-500">
                3-Tier Assessment
              </div>
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                onClick={() => {
                  // Navigate to area-specific assessment
                  navigate(`/assessment/${area.id}`);
                }}
              >
                Start Assessment
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TierBasedAssessmentPage;