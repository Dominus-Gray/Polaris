import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polaris-migrate.preview.emergentagent.com';

function AgencyBusinessIntelligenceDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [filterRisk, setFilterRisk] = useState('all');
  const [filterReadiness, setFilterReadiness] = useState('all');
  const [activeView, setActiveView] = useState('overview');

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    loadBusinessIntelligence();
  }, []);

  const loadBusinessIntelligence = async () => {
    try {
      const response = await axios.get(`${API}/api/agency/business-intelligence`, authHeaders);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading business intelligence:', error);
      alert('Failed to load business intelligence dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getReadinessColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getBusinessAssuranceLevel = (client) => {
    const readiness = client.readiness_score;
    const evidenceRate = client.evidence_required > 0 ? (client.evidence_approved / client.evidence_required) * 100 : 100;
    const completionRate = client.assessment_completion;

    // Business assurance scoring algorithm
    const assuranceScore = (readiness * 0.4) + (evidenceRate * 0.4) + (completionRate * 0.2);
    
    if (assuranceScore >= 85) return { level: 'High', color: 'text-green-600 bg-green-100', score: assuranceScore };
    if (assuranceScore >= 70) return { level: 'Medium', color: 'text-yellow-600 bg-yellow-100', score: assuranceScore };
    return { level: 'Low', color: 'text-red-600 bg-red-100', score: assuranceScore };
  };

  const downloadFile = (evidenceId, fileName) => {
    const downloadUrl = `${API}/api/navigator/evidence/${evidenceId}/files/${fileName}`;
    window.open(downloadUrl, '_blank');
  };

  const filteredClients = dashboardData?.client_details?.filter(client => {
    const assurance = getBusinessAssuranceLevel(client);
    
    if (filterRisk !== 'all') {
      const riskLevel = client.critical_gaps > 5 ? 'high' : client.critical_gaps > 2 ? 'medium' : 'low';
      if (riskLevel !== filterRisk) return false;
    }
    
    if (filterReadiness !== 'all') {
      const readinessLevel = client.readiness_score >= 80 ? 'high' : client.readiness_score >= 60 ? 'medium' : 'low';
      if (readinessLevel !== filterReadiness) return false;
    }
    
    return true;
  }) || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Business Intelligence Dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Business Intelligence Data</h3>
          <p className="text-gray-600">Unable to load business intelligence dashboard.</p>
        </div>
      </div>
    );
  }

  const { agency_overview, client_details, governance_alerts } = dashboardData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Business Intelligence Dashboard</h1>
          <p className="text-gray-600">Comprehensive insights and analytics for sponsored business progression</p>
        </div>

        {/* View Selector */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'progression', label: 'Progression Tracking', icon: '📈' },
              { id: 'evidence', label: 'Evidence Review', icon: '📋' },
              { id: 'assurance', label: 'Business Assurance', icon: '🛡️' }
            ].map((view) => (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeView === view.id
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {view.icon} {view.label}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Cards */}
        {activeView === 'overview' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-indigo-100 rounded-lg">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{agency_overview.total_sponsored_clients}</div>
                    <div className="text-sm text-gray-600">Sponsored Clients</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{agency_overview.average_readiness_score}%</div>
                    <div className="text-sm text-gray-600">Avg Readiness Score</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{agency_overview.compliance_rate}%</div>
                    <div className="text-sm text-gray-600">Compliance Rate</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-red-100 rounded-lg">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{agency_overview.total_critical_gaps}</div>
                    <div className="text-sm text-gray-600">Critical Gaps</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Governance Alerts */}
            {governance_alerts && governance_alerts.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-md mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🚨 Governance Alerts</h3>
                <div className="space-y-3">
                  {governance_alerts.map((alert, index) => (
                    <div key={index} className={`p-4 rounded-lg border ${
                      alert.type === 'high_risk' ? 'bg-red-50 border-red-200 text-red-800' :
                      alert.type === 'evidence_missing' ? 'bg-amber-50 border-amber-200 text-amber-800' :
                      'bg-blue-50 border-blue-200 text-blue-800'
                    }`}>
                      <div className="flex items-start gap-3">
                        <div className="font-medium">{alert.client_email}</div>
                        <div className="text-sm">{alert.message}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Progression Tracking View */}
        {activeView === 'progression' && (
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Client Progression Tracking</h3>
                <div className="flex gap-4">
                  <select
                    value={filterRisk}
                    onChange={(e) => setFilterRisk(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="all">All Risk Levels</option>
                    <option value="low">Low Risk</option>
                    <option value="medium">Medium Risk</option>
                    <option value="high">High Risk</option>
                  </select>
                  <select
                    value={filterReadiness}
                    onChange={(e) => setFilterReadiness(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="all">All Readiness Levels</option>
                    <option value="high">High Readiness (80%+)</option>
                    <option value="medium">Medium Readiness (60-79%)</option>
                    <option value="low">Low Readiness (&lt;60%)</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Client</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Business Areas Progress</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Readiness Score</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Evidence Status</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Risk Level</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredClients.map((client) => {
                    const riskLevel = client.critical_gaps > 5 ? 'high' : client.critical_gaps > 2 ? 'medium' : 'low';
                    return (
                      <tr key={client.client_id} className="hover:bg-gray-50">
                        <td className="py-4 px-6">
                          <div>
                            <div className="font-medium text-gray-900">{client.company_name}</div>
                            <div className="text-sm text-gray-500">{client.client_email}</div>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-2">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-indigo-600 h-2 rounded-full" 
                                style={{width: `${client.assessment_completion}%`}}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">{client.assessment_completion}%</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {Math.round(client.assessment_completion / 10)} of 10 areas
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getReadinessColor(client.readiness_score)}`}>
                            {client.readiness_score}%
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <div className="text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-gray-600">Required:</span>
                              <span className="font-medium">{client.evidence_required}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-gray-600">Approved:</span>
                              <span className="font-medium text-green-600">{client.evidence_approved}</span>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(riskLevel)}`}>
                            {riskLevel.toUpperCase()} ({client.critical_gaps} gaps)
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <button
                            onClick={() => setSelectedClient(client)}
                            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Business Assurance View */}
        {activeView === 'assurance' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {filteredClients.map((client) => {
              const assurance = getBusinessAssuranceLevel(client);
              return (
                <div key={client.client_id} className="bg-white rounded-xl p-6 shadow-md">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="font-semibold text-gray-900">{client.company_name}</h4>
                      <p className="text-sm text-gray-600">{client.client_email}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${assurance.color}`}>
                      {assurance.level} Assurance
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Assurance Score:</span>
                      <span className="font-semibold">{Math.round(assurance.score)}%</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Readiness:</span>
                      <span className="font-medium">{client.readiness_score}%</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Evidence Rate:</span>
                      <span className="font-medium">
                        {client.evidence_required > 0 ? Math.round((client.evidence_approved / client.evidence_required) * 100) : 100}%
                      </span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Assessment:</span>
                      <span className="font-medium">{client.assessment_completion}%</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Critical Gaps:</span>
                      <span className={`font-medium ${client.critical_gaps === 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {client.critical_gaps}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => setSelectedClient(client)}
                      className="w-full text-center text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      View Full Assessment
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Client Detail Modal */}
        {selectedClient && (
          <div className="fixed inset-0 bg-primary bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {selectedClient.company_name} - Comprehensive Assessment
                  </h3>
                  <button
                    onClick={() => setSelectedClient(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Business Information</label>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm">
                          <div><strong>Email:</strong> {selectedClient.client_email}</div>
                          <div><strong>Registration:</strong> {new Date(selectedClient.registration_date).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-gray-700">Assessment Progress</label>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm">Completion Rate</span>
                          <span className="font-semibold">{selectedClient.assessment_completion}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-indigo-600 h-2 rounded-full" 
                            style={{width: `${selectedClient.assessment_completion}%`}}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Performance Metrics</label>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Readiness Score:</span>
                          <span className="font-semibold">{selectedClient.readiness_score}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Critical Gaps:</span>
                          <span className="font-semibold text-red-600">{selectedClient.critical_gaps}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Active Services:</span>
                          <span className="font-semibold">{selectedClient.active_services}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-gray-700">Evidence Management</label>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <div className="text-lg font-bold text-gray-900">{selectedClient.evidence_required}</div>
                            <div className="text-xs text-gray-600">Required</div>
                          </div>
                          <div>
                            <div className="text-lg font-bold text-blue-600">{selectedClient.evidence_submitted}</div>
                            <div className="text-xs text-gray-600">Submitted</div>
                          </div>
                          <div>
                            <div className="text-lg font-bold text-green-600">{selectedClient.evidence_approved}</div>
                            <div className="text-xs text-gray-600">Approved</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-center">
                    <span className={`px-4 py-2 rounded-full font-medium ${
                      selectedClient.compliance_status === 'compliant' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {selectedClient.compliance_status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgencyBusinessIntelligenceDashboard;