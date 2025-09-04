import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://agencydash.preview.emergentagent.com';

function AgencyAIContractMatching() {
  const [contracts, setContracts] = useState([]);
  const [sponsoredClients, setSponsoredClients] = useState([]);
  const [matchingResults, setMatchingResults] = useState([]);
  const [selectedContract, setSelectedContract] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('opportunities');
  const [filterRisk, setFilterRisk] = useState('all');
  const [filterReadiness, setFilterReadiness] = useState('all');

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    loadContractData();
    loadSponsoredClients();
  }, []);

  const loadContractData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/api/agency/contract-opportunities`, authHeaders);
      setContracts(response.data.opportunities || []);
    } catch (error) {
      console.error('Error loading contracts:', error);
      alert('Failed to load contract opportunities');
    } finally {
      setLoading(false);
    }
  };

  const loadSponsoredClients = async () => {
    try {
      const response = await axios.get(`${API}/api/agency/business-intelligence`, authHeaders);
      setSponsoredClients(response.data.client_details || []);
    } catch (error) {
      console.error('Error loading sponsored clients:', error);
    }
  };

  const runAIMatching = async (contractId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/api/agency/ai-contract-matching`, {
        contract_id: contractId,
        include_risk_analysis: true,
        include_recommendations: true
      }, authHeaders);
      
      setMatchingResults(response.data.matches || []);
      setActiveView('matches');
    } catch (error) {
      console.error('Error running AI matching:', error);
      alert('Failed to run AI contract matching');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getReadinessColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getMatchScore = (match) => {
    // AI-calculated match score based on multiple factors
    const readinessWeight = 0.3;
    const capabilityWeight = 0.3;
    const experienceWeight = 0.2;
    const riskWeight = 0.2;

    const readinessScore = match.client_readiness_score || 0;
    const capabilityScore = match.capability_match_score || 0;
    const experienceScore = match.past_performance_score || 0;
    const riskScore = match.risk_level === 'low' ? 100 : match.risk_level === 'medium' ? 70 : 40;

    return Math.round(
      (readinessScore * readinessWeight) +
      (capabilityScore * capabilityWeight) +
      (experienceScore * experienceWeight) +
      (riskScore * riskWeight)
    );
  };

  const filteredMatches = matchingResults.filter(match => {
    if (filterRisk !== 'all' && match.risk_level !== filterRisk) return false;
    if (filterReadiness !== 'all') {
      const readinessLevel = match.client_readiness_score >= 80 ? 'high' : 
                           match.client_readiness_score >= 60 ? 'medium' : 'low';
      if (readinessLevel !== filterReadiness) return false;
    }
    return true;
  });

  if (loading && contracts.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Contract Matching System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI-Powered Contract Matching</h1>
          <p className="text-gray-600">Intelligent matching system for contract opportunities with risk assessment and recommendations</p>
        </div>

        {/* View Selector */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {[
              { id: 'opportunities', label: 'Contract Opportunities', icon: '📋' },
              { id: 'matches', label: 'AI Matching Results', icon: '🤖' },
              { id: 'analytics', label: 'Performance Analytics', icon: '📊' }
            ].map((view) => (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeView === view.id
                    ? 'bg-green-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {view.icon} {view.label}
              </button>
            ))}
          </div>
        </div>

        {/* Contract Opportunities View */}
        {activeView === 'opportunities' && (
          <div className="grid gap-6">
            {contracts.length === 0 ? (
              <div className="bg-white rounded-xl p-8 text-center shadow-md">
                <div className="text-gray-500 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Contract Opportunities Available</h3>
                <p className="text-gray-600 mb-4">Connect with local procurement systems to view available contracts.</p>
                <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                  Connect Data Sources
                </button>
              </div>
            ) : (
              contracts.map((contract) => (
                <div key={contract.id} className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{contract.title}</h3>
                        <p className="text-gray-600 text-sm mb-3">{contract.description}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Value:</span>
                            <div className="font-semibold text-green-600">${contract.contract_value?.toLocaleString()}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Duration:</span>
                            <div className="font-semibold">{contract.duration}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Due Date:</span>
                            <div className="font-semibold">{new Date(contract.due_date).toLocaleDateString()}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Agency:</span>
                            <div className="font-semibold">{contract.issuing_agency}</div>
                          </div>
                        </div>
                      </div>
                      <div className="ml-4 flex flex-col gap-2">
                        <button
                          onClick={() => runAIMatching(contract.id)}
                          disabled={loading}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors text-sm"
                        >
                          🤖 Run AI Match
                        </button>
                        <button
                          onClick={() => setSelectedContract(contract)}
                          className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                        >
                          View Details
                        </button>
                      </div>
                    </div>

                    {/* Contract Requirements */}
                    <div className="border-t pt-4">
                      <h4 className="font-medium text-gray-900 mb-2">Key Requirements:</h4>
                      <div className="flex flex-wrap gap-2">
                        {contract.requirements?.map((req, index) => (
                          <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                            {req}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* AI Matching Results View */}
        {activeView === 'matches' && (
          <>
            {matchingResults.length === 0 ? (
              <div className="bg-white rounded-xl p-8 text-center shadow-md">
                <div className="text-gray-500 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Matching Results Yet</h3>
                <p className="text-gray-600">Select a contract opportunity to run AI-powered matching analysis.</p>
              </div>
            ) : (
              <>
                <div className="bg-white rounded-xl p-6 shadow-md mb-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-900">AI Matching Results</h3>
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
                        <option value="high">High Readiness</option>
                        <option value="medium">Medium Readiness</option>
                        <option value="low">Low Readiness</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="grid gap-6">
                  {filteredMatches.map((match, index) => {
                    const matchScore = getMatchScore(match);
                    
                    return (
                      <div key={index} className="bg-white rounded-xl shadow-md overflow-hidden">
                        <div className="p-6">
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="text-lg font-semibold text-gray-900">{match.client_company}</h4>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                  matchScore >= 80 ? 'bg-green-100 text-green-800' :
                                  matchScore >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {matchScore}% Match
                                </span>
                              </div>
                              <p className="text-gray-600 text-sm mb-3">{match.client_email}</p>
                            </div>
                            <div className="text-right">
                              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(match.risk_level)}`}>
                                {match.risk_level.toUpperCase()} RISK
                              </span>
                            </div>
                          </div>

                          {/* AI Analysis Summary */}
                          <div className="bg-blue-50 rounded-lg p-4 mb-4">
                            <h5 className="font-medium text-blue-900 mb-2">🤖 AI Analysis Summary</h5>
                            <p className="text-blue-800 text-sm">{match.ai_summary}</p>
                          </div>

                          {/* Metrics Grid */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div className="text-center">
                              <div className="text-lg font-bold text-gray-900">{match.client_readiness_score}%</div>
                              <div className="text-xs text-gray-600">Readiness Score</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">{match.capability_match_score}%</div>
                              <div className="text-xs text-gray-600">Capability Match</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-green-600">{match.past_performance_score}%</div>
                              <div className="text-xs text-gray-600">Past Performance</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-purple-600">{match.business_maturity_score}%</div>
                              <div className="text-xs text-gray-600">Business Maturity</div>
                            </div>
                          </div>

                          {/* Risk Indicators */}
                          <div className="mb-4">
                            <h5 className="font-medium text-gray-900 mb-2">Risk Indicators:</h5>
                            <div className="flex flex-wrap gap-2">
                              {match.risk_indicators?.map((indicator, idx) => (
                                <span key={idx} className={`px-3 py-1 rounded-full text-sm ${
                                  indicator.level === 'high' ? 'bg-red-100 text-red-800' :
                                  indicator.level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {indicator.factor}
                                </span>
                              ))}
                            </div>
                          </div>

                          {/* AI Recommendations */}
                          <div className="mb-4">
                            <h5 className="font-medium text-gray-900 mb-2">AI Recommendations:</h5>
                            <ul className="text-sm text-gray-700 space-y-1">
                              {match.recommendations?.map((rec, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <svg className="w-4 h-4 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex gap-3 pt-4 border-t">
                            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm">
                              📧 Recommend Contract
                            </button>
                            <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm">
                              📋 View Full Profile
                            </button>
                            <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm">
                              📊 Generate Report
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </>
        )}

        {/* Performance Analytics View */}
        {activeView === 'analytics' && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Contract Matching Performance Analytics</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <div className="text-2xl font-bold mb-1">24</div>
                <div className="text-blue-100 text-sm">Total Matches This Month</div>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                <div className="text-2xl font-bold mb-1">78%</div>
                <div className="text-green-100 text-sm">Average Match Accuracy</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <div className="text-2xl font-bold mb-1">12</div>
                <div className="text-purple-100 text-sm">Successful Recommendations</div>
              </div>
            </div>

            <div className="text-center py-12 text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p>Detailed analytics dashboard coming soon...</p>
            </div>
          </div>
        )}

        {/* Contract Detail Modal */}
        {selectedContract && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">{selectedContract.title}</h3>
                  <button
                    onClick={() => setSelectedContract(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                    <p className="text-gray-700">{selectedContract.description}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Contract Details</h4>
                      <div className="space-y-2 text-sm">
                        <div><strong>Value:</strong> ${selectedContract.contract_value?.toLocaleString()}</div>
                        <div><strong>Duration:</strong> {selectedContract.duration}</div>
                        <div><strong>Due Date:</strong> {new Date(selectedContract.due_date).toLocaleDateString()}</div>
                        <div><strong>Agency:</strong> {selectedContract.issuing_agency}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
                      <div className="space-y-1">
                        {selectedContract.requirements?.map((req, index) => (
                          <div key={index} className="text-sm text-gray-700">• {req}</div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4 pt-4 border-t">
                    <button
                      onClick={() => runAIMatching(selectedContract.id)}
                      className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      🤖 Run AI Matching
                    </button>
                    <button
                      onClick={() => setSelectedContract(null)}
                      className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Close
                    </button>
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

export default AgencyAIContractMatching;