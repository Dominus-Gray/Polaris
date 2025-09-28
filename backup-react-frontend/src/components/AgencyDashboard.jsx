import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const API = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

const AgencyDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [pipelineData, setPipelineData] = useState(null);
  const [businessData, setBusinessData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load dashboard data
  useEffect(() => {
    const loadData = async () => {
      try {
        const [pipelineRes, businessRes] = await Promise.all([
          axios.get(`${API}/agency/contract-pipeline`),
          axios.get(`${API}/agency/business-readiness`)
        ]);
        
        setPipelineData(pipelineRes.data);
        setBusinessData(businessRes.data);
      } catch (error) {
        console.error('Error loading agency data:', error);
        // Use fallback data
        setPipelineData({
          totalOpportunities: 15,
          pipelineValue: 2400000,
          contractReady: 8,
          avgReadiness: 74,
          winRate: 65
        });
        setBusinessData({
          totalBusinesses: 23,
          assessmentComplete: 18,
          tier3Ready: 8
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Quick action handlers
  const handleQuickAction = async (action) => {
    switch (action) {
      case 'add_opportunity':
        setActiveTab('opportunities');
        setTimeout(() => {
          const element = document.getElementById('add-opportunity-form');
          if (element) element.scrollIntoView({ behavior: 'smooth' });
        }, 100);
        break;
        
      case 'review_businesses':
        setActiveTab('businesses');
        break;
        
      case 'generate_report':
        try {
          const response = await axios.get(`${API}/agency/reports/pipeline`, {
            responseType: 'blob'
          });
          
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `pipeline_report_${new Date().toISOString().split('T')[0]}.pdf`);
          document.body.appendChild(link);
          link.click();
          link.remove();
          
          toast.success('Pipeline report generated successfully');
        } catch (error) {
          toast.error('Failed to generate report');
        }
        break;
        
      case 'manage_licenses':
        setActiveTab('settings');
        setTimeout(() => {
          const element = document.getElementById('subscription-billing');
          if (element) element.scrollIntoView({ behavior: 'smooth' });
        }, 100);
        break;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading contract pipeline...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-slate-900">Contract Pipeline Management</h1>
            </div>
            <div className="flex items-center space-x-8">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-2 text-sm font-medium ${
                  activeTab === 'dashboard'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Contract Pipeline
              </button>
              <button
                onClick={() => setActiveTab('businesses')}
                className={`px-3 py-2 text-sm font-medium ${
                  activeTab === 'businesses'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Business Readiness
              </button>
              <button
                onClick={() => setActiveTab('opportunities')}
                className={`px-3 py-2 text-sm font-medium ${
                  activeTab === 'opportunities'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Opportunity Matching
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`px-3 py-2 text-sm font-medium ${
                  activeTab === 'settings'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Account Settings
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <div>
            {/* Contract Pipeline Overview */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Contract Opportunity Pipeline</h2>
              <p className="text-slate-600 mb-6">Track and manage contract opportunities for your sponsored small businesses</p>
              
              {/* Pipeline Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-slate-900">{businessData?.totalBusinesses || 23}</div>
                      <div className="text-sm text-slate-600">Sponsored Businesses</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-slate-900">{pipelineData?.contractReady || 8}</div>
                      <div className="text-sm text-slate-600">Contract Ready</div>
                      <div className="text-xs text-green-600 mt-1">Tier 3 Certified</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-purple-100 rounded-lg">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-slate-900">{pipelineData?.totalOpportunities || 15}</div>
                      <div className="text-sm text-slate-600">Active Opportunities</div>
                      <div className="text-xs text-purple-600 mt-1">5 closing this month</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-yellow-100 rounded-lg">
                      <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-slate-900">${((pipelineData?.pipelineValue || 2400000) / 1000000).toFixed(1)}M</div>
                      <div className="text-sm text-slate-600">Pipeline Value</div>
                      <div className="text-xs text-yellow-600 mt-1">6-month forecast</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-indigo-100 rounded-lg">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2-2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-slate-900">{pipelineData?.winRate || 65}%</div>
                      <div className="text-sm text-slate-600">Win Rate</div>
                      <div className="text-xs text-indigo-600 mt-1">↗ +8% this quarter</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-lg border p-6 mb-8">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <button
                    onClick={() => handleQuickAction('add_opportunity')}
                    className="flex items-center gap-3 p-4 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Contract Opportunity
                  </button>
                  
                  <button
                    onClick={() => handleQuickAction('review_businesses')}
                    className="flex items-center gap-3 p-4 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    Review Business Readiness
                  </button>
                  
                  <button
                    onClick={() => handleQuickAction('generate_report')}
                    className="flex items-center gap-3 p-4 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Generate Pipeline Report
                  </button>
                  
                  <button
                    onClick={() => handleQuickAction('manage_licenses')}
                    className="flex items-center gap-3 p-4 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                    Manage Assessment Licenses
                  </button>
                </div>
              </div>

              {/* Contract Opportunity Pipeline Table */}
              <div className="bg-white rounded-lg border">
                <div className="p-6 border-b">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">Active Contract Opportunities</h3>
                      <p className="text-sm text-slate-600 mt-1">Contract opportunities with business readiness matching</p>
                    </div>
                    <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 transition-colors">
                      View All Opportunities
                    </button>
                  </div>
                </div>
                <div className="p-6">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="text-left py-3 px-2">Contract Title</th>
                          <th className="text-left py-3 px-2">Value</th>
                          <th className="text-left py-3 px-2">Closing Date</th>
                          <th className="text-left py-3 px-2">Matched Businesses</th>
                          <th className="text-left py-3 px-2">Readiness Score</th>
                          <th className="text-left py-3 px-2">Action</th>
                        </tr>
                      </thead>
                      <tbody className="text-slate-600">
                        <tr className="border-b border-slate-100">
                          <td className="py-3 px-2 font-medium">IT Services & Support Contract</td>
                          <td className="py-3 px-2">$150,000</td>
                          <td className="py-3 px-2">March 15, 2025</td>
                          <td className="py-3 px-2">
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">3 Qualified</span>
                          </td>
                          <td className="py-3 px-2">
                            <span className="font-medium text-green-600">87%</span>
                          </td>
                          <td className="py-3 px-2">
                            <button className="text-indigo-600 hover:text-indigo-800 text-xs underline">Review Matches</button>
                          </td>
                        </tr>
                        <tr className="border-b border-slate-100">
                          <td className="py-3 px-2 font-medium">Construction Management</td>
                          <td className="py-3 px-2">$350,000</td>
                          <td className="py-3 px-2">April 2, 2025</td>
                          <td className="py-3 px-2">
                            <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">2 In Progress</span>
                          </td>
                          <td className="py-3 px-2">
                            <span className="font-medium text-yellow-600">72%</span>
                          </td>
                          <td className="py-3 px-2">
                            <button className="text-blue-600 hover:text-blue-800 text-xs underline">Support Readiness</button>
                          </td>
                        </tr>
                        <tr className="border-b border-slate-100">
                          <td className="py-3 px-2 font-medium">Marketing & Communications</td>
                          <td className="py-3 px-2">$75,000</td>
                          <td className="py-3 px-2">March 28, 2025</td>
                          <td className="py-3 px-2">
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">1 Needs Help</span>
                          </td>
                          <td className="py-3 px-2">
                            <span className="font-medium text-red-600">58%</span>
                          </td>
                          <td className="py-3 px-2">
                            <button className="text-purple-600 hover:text-purple-800 text-xs underline">Schedule Training</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs will be added here */}
      </div>
    </div>
  );
};

export default AgencyDashboard;