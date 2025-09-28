import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ReadinessDashboard() {
  const [planner, setPlanner] = useState({ loading: true, tasks: [] });
  const loadPlanner = async () => {
    try {
      const { data } = await axios.get(`${API}/planner/tasks`);
      setPlanner({ loading: false, tasks: data || [] });
    } catch (e) {
      console.warn('Failed to load planner', e);
      setPlanner({ loading: false, tasks: [] });
    }
  };
  const markTask = async (taskId, status) => {
    try {
      await axios.patch(`${API}/planner/tasks/${taskId}`, { status });
      setPlanner(p => ({ ...p, tasks: p.tasks.map(t => t.id === taskId ? { ...t, status } : t) }));
    } catch (e) {
      console.warn('Failed to update task', e);
    }
  };
  useEffect(() => { loadPlanner(); }, []);
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('6months'); // 3months, 6months, 1year, all
  // RP CRM-lite summary
  const [rpCounts, setRpCounts] = useState({ total: 0, new: 0, working: 0, approved: 0 });
  const [rpLoading, setRpLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [timeframe]);

  const loadRpcCounts = async () => {
    try{
      setRpLoading(true);
      const { data } = await axios.get(`${API}/v2/rp/leads`);
      const items = data.leads || [];
      const counts = {
        total: items.length,
        new: items.filter(x=>x.status==='new').length,
        working: items.filter(x=>x.status==='working').length,
        approved: items.filter(x=>x.status==='approved').length
      };
      setRpCounts(counts);
    }catch(e){ console.warn('RP counts failed', e); }
    finally{ setRpLoading(false); }
  };
  
  useEffect(()=>{ loadRpcCounts(); }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const { data } = await axios.get(`${API}/dashboard/readiness`, {
        params: { timeframe }
      });
      setDashboardData(data);
    } catch (error) {
      console.warn('Failed to load dashboard data:', error);
      // Fallback data
      setDashboardData({
        current_score: 0,
        completion_percentage: 0,
        critical_gaps: 0,
        assessments_completed: 0,
        last_assessment: new Date().toISOString(),
        goals: [],
        certifications: []
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-6xl">
        <div className="space-y-6">
          <div className="bg-slate-100 rounded-lg h-32 animate-pulse" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-slate-100 rounded-lg h-24 animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Welcome back! 👋</h1>
            <p className="opacity-90">Track your procurement readiness progress and next steps</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{dashboardData?.current_score || 0}%</div>
            <div className="text-sm opacity-75">Overall Readiness</div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Procurement Readiness Journey</span>
            <span className="text-sm">
              {Math.round((dashboardData?.current_score || 0) / 70 * 100)}% to certification
            </span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-3">
            <div 
              className="bg-white rounded-full h-3 transition-all duration-500"
              style={{ width: `${Math.min((dashboardData?.current_score || 0), 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* RP CRM-lite Summary */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Resource Partner Leads</h3>
            <span className="text-2xl">🤝</span>
          </div>
          {rpLoading ? (
            <div className="h-6 bg-slate-200 rounded" />
          ) : (
            <div className="text-sm text-slate-700 space-y-1">
              <div className="flex items-center justify-between"><span>Total</span><span className="font-semibold">{rpCounts.total}</span></div>
              <div className="flex items-center justify-between"><span>New</span><span className="font-semibold">{rpCounts.new}</span></div>
              <div className="flex items-center justify-between"><span>Working</span><span className="font-semibold">{rpCounts.working}</span></div>
              <div className="flex items-center justify-between"><span>Approved</span><span className="font-semibold">{rpCounts.approved}</span></div>
            </div>
          )}
          <div className="mt-3 text-right">
            <button className="btn btn-primary btn-sm" onClick={()=>window.location.href='/rp/share'}>Create Share Package</button>
          </div>
        </div>

        {/* Current Score */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Readiness Score</h3>
            <span className="text-2xl">⭐</span>
          </div>
          <div className="text-3xl font-bold text-blue-600 mb-2">{dashboardData?.current_score || 0}%</div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${dashboardData?.current_score || 0}%` }}
            ></div>
          </div>
          <div className="text-xs text-slate-500 mt-2">
            Target: 70% for certification
          </div>
        </div>

        {/* Assessments Completed */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Assessments</h3>
            <span className="text-2xl">✅</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.assessments_completed}</div>
          <div className="text-sm text-slate-600">Completed</div>
          <div className="text-xs text-slate-500 mt-1">
            Last: {new Date(dashboardData?.last_assessment).toLocaleDateString()}
          </div>
        </div>

        {/* Active Goals */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Active Goals</h3>
            <span className="text-2xl">🎯</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.goals?.length || 0}</div>
          <div className="text-sm text-slate-600">In Progress</div>
          <div className="text-xs text-slate-500 mt-1">
            {dashboardData?.goals?.filter(g => g.status === 'on_track').length || 0} on track
          </div>
        </div>
      </div>

      {/* Personalized Action Items & Recommendations */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Recommended Next Steps</h3>
          </div>
          <span className="text-sm text-green-600 font-medium">Priority Actions</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Smart recommendations based on current state */}
          {(dashboardData?.completion_percentage || 0) < 30 && (
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 font-semibold text-sm">1</span>
                </div>
                <div>
                  <h4 className="font-medium text-slate-900 mb-1">Complete Your Assessment</h4>
                  <p className="text-sm text-slate-600 mb-3">Start with the Legal & Compliance area - it's foundational for procurement readiness.</p>
                  <button 
                    className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors"
                    onClick={() => navigate('/assessment')}
                  >
                    Start Assessment →
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {(dashboardData?.critical_gaps || 0) > 0 && (
            <div className="bg-white rounded-lg p-4 border border-orange-100">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-orange-600 font-semibold text-sm">!</span>
                </div>
                <div>
                  <h4 className="font-medium text-slate-900 mb-1">Address Critical Gaps</h4>
                  <p className="text-sm text-slate-600 mb-3">You have {dashboardData.critical_gaps} areas needing immediate attention for procurement readiness.</p>
                  <button 
                    className="text-sm bg-orange-600 text-white px-3 py-1.5 rounded-lg hover:bg-orange-700 transition-colors"
                    onClick={() => navigate('/service-request')}
                  >
                    Find Expert Help →
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {(dashboardData?.current_score || 0) >= 50 && (dashboardData?.current_score || 0) < 70 && (
            <div className="bg-white rounded-lg p-4 border border-purple-100">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-purple-600 font-semibold text-sm">🎯</span>
                </div>
                <div>
                  <h4 className="font-medium text-slate-900 mb-1">You're Making Great Progress!</h4>
                  <p className="text-sm text-slate-600 mb-3">Just {70 - (dashboardData.current_score || 0)}% more to reach certification threshold.</p>
                  <button 
                    className="text-sm bg-purple-600 text-white px-3 py-1.5 rounded-lg hover:bg-purple-700 transition-colors"
                    onClick={() => navigate('/assessment')}
                  >
                    Continue Assessment →
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {(dashboardData?.current_score || 0) >= 70 && (
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-green-600 font-semibold text-sm">🏆</span>
                </div>
                <div>
                  <h4 className="font-medium text-slate-900 mb-1">Certification Ready!</h4>
                  <p className="text-sm text-slate-600 mb-3">Congratulations! You've achieved procurement readiness. Time to apply for opportunities.</p>
                  <button 
                    className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700 transition-colors"
                    onClick={() => window.open('https://sam.gov', '_blank')}
                  >
                    Browse Opportunities →
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Always show knowledge base recommendation */}
          <div className="bg-white rounded-lg p-4 border border-indigo-100">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-slate-900 mb-1">Explore Resources</h4>
                <p className="text-sm text-slate-600 mb-3">Access templates, guides, and best practices to accelerate your progress.</p>
                <button 
                  className="text-sm bg-indigo-600 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors"
                  onClick={() => navigate('/knowledge')}
                >
                  Browse Knowledge Base →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReadinessDashboard;