import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://smartbiz-assess.preview.emergentagent.com';

function AgencyBusinessIntelligence() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [filterCompliance, setFilterCompliance] = useState('all');

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/api/agency/business-intelligence`, authHeaders);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading agency dashboard:', error);
      alert('Failed to load business intelligence dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'needs_attention': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'high_risk': return 'bg-red-50 border-red-200 text-red-800';
      case 'evidence_missing': return 'bg-amber-50 border-amber-200 text-amber-800';
      default: return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const filteredClients = dashboardData?.client_details?.filter(client => {
    if (filterCompliance === 'all') return true;
    return client.compliance_status === filterCompliance;
  }) || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading business intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-600">Unable to load business intelligence data.</p>
        </div>
      </div>
    );
  }

  const { agency_overview, monthly_activity, client_details, governance_alerts } = dashboardData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agency Business Intelligence Dashboard</h1>
          <p className="text-gray-600">Monitor and govern your sponsored business compliance and readiness</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              <div className="p-3 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        {governance_alerts.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-md mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🚨 Governance Alerts</h3>
            <div className="space-y-3">
              {governance_alerts.map((alert, index) => (
                <div key={index} className={`p-4 rounded-lg border ${getAlertColor(alert.type)}`}>
                  <div className="flex items-start gap-3">
                    <div className="font-medium">{alert.client_email}</div>
                    <div className="text-sm">{alert.message}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Client Compliance Table */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Client Compliance Overview</h3>
              <select
                value={filterCompliance}
                onChange={(e) => setFilterCompliance(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="all">All Clients</option>
                <option value="compliant">Compliant Only</option>
                <option value="needs_attention">Needs Attention</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Client</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Readiness Score</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Assessment Progress</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Critical Gaps</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Evidence Status</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Compliance</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredClients.map((client) => (
                  <tr key={client.client_id} className="hover:bg-gray-50">
                    <td className="py-4 px-6">
                      <div>
                        <div className="font-medium text-gray-900">{client.company_name}</div>
                        <div className="text-sm text-gray-500">{client.client_email}</div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="text-lg font-semibold text-gray-900">{client.readiness_score}%</div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{width: `${client.assessment_completion}%`}}
                        ></div>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">{client.assessment_completion}% complete</div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                        client.critical_gaps > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {client.critical_gaps} gaps
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className="text-sm">
                        <div>Required: {client.evidence_required}</div>
                        <div>Submitted: {client.evidence_submitted}</div>
                        <div>Approved: {client.evidence_approved}</div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(client.compliance_status)}`}>
                        {client.compliance_status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <button
                        onClick={() => setSelectedClient(client)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Monthly Activity Summary */}
        <div className="mt-8 bg-white rounded-xl p-6 shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Activity Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-2xl font-bold text-blue-600">{monthly_activity.assessments_completed}</div>
              <div className="text-sm text-gray-600">Assessments Completed (Last 30 days)</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{monthly_activity.evidence_submissions}</div>
              <div className="text-sm text-gray-600">Evidence Submissions (Last 30 days)</div>
            </div>
          </div>
        </div>

        {/* Client Detail Modal */}
        {selectedClient && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {selectedClient.company_name} - Detailed View
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

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-700">Client Email</div>
                      <div className="text-gray-900">{selectedClient.client_email}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Registration Date</div>
                      <div className="text-gray-900">
                        {new Date(selectedClient.registration_date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-700">Assessment Progress</div>
                      <div className="text-2xl font-bold text-blue-600">{selectedClient.assessment_completion}%</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Readiness Score</div>
                      <div className="text-2xl font-bold text-green-600">{selectedClient.readiness_score}%</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-700">Critical Gaps</div>
                      <div className="text-xl font-bold text-red-600">{selectedClient.critical_gaps}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Active Services</div>
                      <div className="text-xl font-bold text-blue-600">{selectedClient.active_services}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Completed Services</div>
                      <div className="text-xl font-bold text-green-600">{selectedClient.completed_services}</div>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="text-sm font-medium text-gray-700 mb-2">Evidence Management</div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-lg font-bold text-gray-900">{selectedClient.evidence_required}</div>
                        <div className="text-xs text-gray-600">Required</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-blue-600">{selectedClient.evidence_submitted}</div>
                        <div className="text-xs text-gray-600">Submitted</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">{selectedClient.evidence_approved}</div>
                        <div className="text-xs text-gray-600">Approved</div>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center pt-4">
                    <span className={`px-4 py-2 rounded-full font-medium ${getStatusColor(selectedClient.compliance_status)}`}>
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

export default AgencyBusinessIntelligence;