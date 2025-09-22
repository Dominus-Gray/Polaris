import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdvancedAnalyticsDashboard({ userRole }) {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [timeframe, setTimeframe] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [predictiveInsights, setPredictiveInsights] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe, userRole]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load role-specific analytics
      const analyticsResponse = await axios.get(`${API}/analytics/advanced/${userRole}`, {
        params: { timeframe }
      });
      
      setAnalyticsData(analyticsResponse.data);
      
      // Load predictive insights if user has permission
      if (['navigator', 'agency', 'admin'].includes(userRole)) {
        const predictiveResponse = await axios.post(`${API}/ai/predictive-analytics`, {
          type: 'program_performance',
          timeframe: timeframe
        });
        setPredictiveInsights(predictiveResponse.data);
      }
      
    } catch (error) {
      console.error('Failed to load analytics:', error);
      // Create mock data for demonstration
      setAnalyticsData(generateMockAnalytics(userRole, timeframe));
    } finally {
      setLoading(false);
    }
  };

  const generateMockAnalytics = (role, timeframe) => {
    const baseMetrics = {
      client: {
        assessmentProgress: 67,
        areasCompleted: 7,
        serviceEngagements: 3,
        certificateProgress: 78,
        weeklyActivity: [45, 52, 38, 67, 71, 59, 43],
        trends: {
          readiness: '+12%',
          engagement: '+23%',
          completion: '+8%'
        }
      },
      provider: {
        clientMatches: 142,
        responseRate: 87,
        avgMatchScore: 78,
        revenue: 45680,
        weeklyOpportunities: [12, 15, 9, 18, 21, 16, 14],
        trends: {
          matches: '+18%',
          revenue: '+34%',
          satisfaction: '+11%'
        }
      },
      agency: {
        sponsoredBusinesses: 156,
        contractsSecured: 23,
        economicImpact: 2340000,
        successRate: 68,
        weeklyProgress: [12, 18, 15, 22, 19, 25, 21],
        trends: {
          businesses: '+15%',
          contracts: '+28%',
          impact: '+42%'
        }
      },
      navigator: {
        clientsGuided: 89,
        successRate: 82,
        interventions: 12,
        regionalImpact: 34,
        weeklyActivity: [28, 31, 26, 35, 33, 29, 32],
        trends: {
          guidance: '+19%',
          success: '+7%',
          impact: '+25%'
        }
      }
    };

    return baseMetrics[role] || baseMetrics.client;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value}%`;
  };

  const getMetricColor = (role) => {
    switch (role) {
      case 'client': return 'blue';
      case 'provider': return 'green';
      case 'agency': return 'purple';
      case 'navigator': return 'emerald';
      default: return 'slate';
    }
  };

  const renderKPICards = () => {
    if (!analyticsData) return null;

    const color = getMetricColor(userRole);
    
    switch (userRole) {
      case 'client':
        return (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className={`bg-gradient-to-r from-${color}-50 to-${color}-100 rounded-lg p-6 border border-${color}-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className={`text-3xl font-bold text-${color}-600`}>{analyticsData.assessmentProgress}%</div>
                  <div className="text-sm font-medium text-slate-700">Assessment Progress</div>
                  <div className={`text-xs text-${color}-600 font-medium`}>{analyticsData.trends.readiness}</div>
                </div>
                <div className={`p-3 bg-${color}-200 rounded-lg`}>
                  <svg className={`w-6 h-6 text-${color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-6 border border-green-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-green-600">{analyticsData.areasCompleted}/10</div>
                  <div className="text-sm font-medium text-slate-700">Areas Completed</div>
                  <div className="text-xs text-green-600 font-medium">{analyticsData.trends.completion}</div>
                </div>
                <div className="p-3 bg-green-200 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 4h6m-6 4h6m-6 4h6" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-purple-600">{analyticsData.serviceEngagements}</div>
                  <div className="text-sm font-medium text-slate-700">Service Engagements</div>
                  <div className="text-xs text-purple-600 font-medium">{analyticsData.trends.engagement}</div>
                </div>
                <div className="p-3 bg-purple-200 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-6 border border-yellow-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-yellow-600">{analyticsData.certificateProgress}%</div>
                  <div className="text-sm font-medium text-slate-700">Certificate Progress</div>
                  <div className="text-xs text-yellow-600 font-medium">Target: 70%</div>
                </div>
                <div className="p-3 bg-yellow-200 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        );
        
      case 'agency':
        return (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className={`bg-gradient-to-r from-${color}-50 to-${color}-100 rounded-lg p-6 border border-${color}-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className={`text-3xl font-bold text-${color}-600`}>{analyticsData.sponsoredBusinesses}</div>
                  <div className="text-sm font-medium text-slate-700">Sponsored Businesses</div>
                  <div className={`text-xs text-${color}-600 font-medium`}>{analyticsData.trends.businesses}</div>
                </div>
                <div className={`p-3 bg-${color}-200 rounded-lg`}>
                  <svg className={`w-6 h-6 text-${color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-6 border border-green-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-green-600">{analyticsData.contractsSecured}</div>
                  <div className="text-sm font-medium text-slate-700">Contracts Secured</div>
                  <div className="text-xs text-green-600 font-medium">{analyticsData.trends.contracts}</div>
                </div>
                <div className="p-3 bg-green-200 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-lg p-6 border border-indigo-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-indigo-600">{formatCurrency(analyticsData.economicImpact)}</div>
                  <div className="text-sm font-medium text-slate-700">Economic Impact</div>
                  <div className="text-xs text-indigo-600 font-medium">{analyticsData.trends.impact}</div>
                </div>
                <div className="p-3 bg-indigo-200 rounded-lg">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className={`bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-lg p-6 border border-emerald-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-3xl font-bold text-emerald-600">{analyticsData.successRate}%</div>
                  <div className="text-sm font-medium text-slate-700">Success Rate</div>
                  <div className="text-xs text-emerald-600 font-medium">Above Target</div>
                </div>
                <div className="p-3 bg-emerald-200 rounded-lg">
                  <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  const renderTrendChart = () => {
    if (!analyticsData || !analyticsData.weeklyActivity) return null;

    const maxValue = Math.max(...analyticsData.weeklyActivity);
    const color = getMetricColor(userRole);

    return (
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          {userRole === 'client' ? 'Weekly Activity Trend' :
           userRole === 'provider' ? 'Weekly Opportunities' :
           userRole === 'agency' ? 'Weekly Business Progress' :
           'Weekly Activity'}
        </h3>
        
        <div className="flex items-end justify-between h-32 gap-2">
          {analyticsData.weeklyActivity.map((value, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div
                className={`w-full bg-gradient-to-t from-${color}-600 to-${color}-400 rounded-t-sm transition-all duration-500`}
                style={{ height: `${(value / maxValue) * 100}%` }}
              />
              <div className="text-xs text-slate-500 mt-2">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-slate-600">
            Avg: {Math.round(analyticsData.weeklyActivity.reduce((a, b) => a + b, 0) / 7)}
          </div>
          <div className="text-sm text-slate-600">
            Peak: {maxValue}
          </div>
        </div>
      </div>
    );
  };

  const renderPredictiveInsights = () => {
    if (!predictiveInsights || !['navigator', 'agency'].includes(userRole)) return null;

    return (
      <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg border border-emerald-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-emerald-100 rounded-lg">
            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-slate-900">Predictive Insights</h3>
          <div className="bg-emerald-600 text-white px-2 py-1 rounded-full text-xs font-medium">AI-Powered</div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border">
            <div className="text-2xl font-bold text-emerald-600 mb-1">
              {predictiveInsights.success_probability || 87}%
            </div>
            <div className="text-sm font-medium text-slate-700">Success Probability</div>
            <div className="text-xs text-slate-500">Next 30 days</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {predictiveInsights.risk_level === 'low' ? '3' : predictiveInsights.risk_level === 'medium' ? '7' : '12'}
            </div>
            <div className="text-sm font-medium text-slate-700">At-Risk Clients</div>
            <div className="text-xs text-slate-500">Need intervention</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border">
            <div className="text-2xl font-bold text-purple-600 mb-1">
              {predictiveInsights.recommendations?.length || 5}
            </div>
            <div className="text-sm font-medium text-slate-700">Smart Actions</div>
            <div className="text-xs text-slate-500">AI recommendations</div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-slate-100 rounded-lg h-24 animate-pulse" />
          ))}
        </div>
        <div className="bg-slate-100 rounded-lg h-64 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Advanced Analytics</h2>
          <p className="text-slate-600">
            {userRole === 'client' ? 'Track your procurement readiness journey' :
             userRole === 'provider' ? 'Monitor your business performance' :
             userRole === 'agency' ? 'Measure your program impact' :
             'Platform performance insights'}
          </p>
        </div>
        
        {/* Timeframe Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Timeframe:</span>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 3 Months</option>
            <option value="1y">Last Year</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      {renderKPICards()}

      {/* Trend Chart */}
      {renderTrendChart()}

      {/* Predictive Insights */}
      {renderPredictiveInsights()}

      {/* Export Options */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Data Export & Reporting</h3>
        <div className="flex flex-wrap gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export PDF Report
          </button>
          
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Download CSV Data
          </button>
          
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
            Share Dashboard
          </button>
          
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Configure Alerts
          </button>
        </div>
      </div>
    </div>
  );
}