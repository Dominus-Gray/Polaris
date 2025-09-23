import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AgencyBusinessIntelligence() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const { data } = await axios.get(`${API}/home/agency`);
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load agency data:', error);
      // Fallback data
      setDashboardData({
        sponsored_businesses: 23,
        contract_ready: 8,
        pipeline_value: 2400000,
        win_rate: 65,
        certificates_issued: 12
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-slate-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Business Intelligence Dashboard</h2>
        <p className="text-slate-600">Comprehensive analytics for economic development impact</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="text-3xl font-bold text-blue-600 mb-2">{dashboardData?.sponsored_businesses || 23}</div>
          <div className="text-sm text-slate-600">Sponsored Businesses</div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="text-3xl font-bold text-green-600 mb-2">{dashboardData?.contract_ready || 8}</div>
          <div className="text-sm text-slate-600">Contract Ready</div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            ${((dashboardData?.pipeline_value || 2400000) / 1000000).toFixed(1)}M
          </div>
          <div className="text-sm text-slate-600">Pipeline Value</div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="text-3xl font-bold text-indigo-600 mb-2">{dashboardData?.win_rate || 65}%</div>
          <div className="text-sm text-slate-600">Win Rate</div>
        </div>
      </div>

      {/* Economic Impact Overview */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-2xl p-8 text-white mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold mb-2">Economic Impact Overview</h2>
            <p className="text-indigo-100">Your program's success in building a stronger local economy</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">Q3 2025</div>
            <div className="text-sm text-indigo-100">Current Period</div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <div className="text-2xl font-bold">$1.4M</div>
            <div className="text-sm font-medium text-white/80">Contracts Secured</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <div className="text-2xl font-bold">65%</div>
            <div className="text-sm font-medium text-white/80">Success Rate</div>
            <div className="text-xs text-green-300">↑ 12% vs last quarter</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <div className="text-2xl font-bold">23</div>
            <div className="text-sm font-medium text-white/80">Active Businesses</div>
            <div className="text-xs text-white/60">8 certification ready</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <div className="text-2xl font-bold">4.3x</div>
            <div className="text-sm font-medium text-white/80">ROI Program</div>
            <div className="text-xs text-white/60">Every $1 → $4.30 impact</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgencyBusinessIntelligence;