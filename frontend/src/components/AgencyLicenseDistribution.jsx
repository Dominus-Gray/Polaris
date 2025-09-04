import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://agencydash.preview.emergentagent.com';

function AgencyLicenseDistribution() {
  const [licenseBalance, setLicenseBalance] = useState({ tier1: 0, tier2: 0, tier3: 0 });
  const [activeTab, setActiveTab] = useState('distribute');
  const [invitationForm, setInvitationForm] = useState({
    recipient_email: '',
    tier_level: 1,
    custom_message: '',
    business_areas: [],
    expires_in_days: 30
  });
  const [sentInvitations, setSentInvitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [purchaseForm, setPurchaseForm] = useState({
    tier1_count: 0,
    tier2_count: 0,
    tier3_count: 0
  });

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  // License pricing (per license)
  const licensePricing = {
    tier1: 25,  // Basic Assessment
    tier2: 75,  // Enhanced Assessment with Evidence
    tier3: 150  // Comprehensive Assessment with Full Evidence & Review
  };

  const businessAreas = [
    { id: 'area1', name: 'Financial Management', description: 'Banking, accounting, and financial controls' },
    { id: 'area2', name: 'Legal Structure', description: 'Business registration and legal compliance' },
    { id: 'area3', name: 'Human Resources', description: 'Personnel management and policies' },
    { id: 'area4', name: 'Operations', description: 'Daily operations and process management' },
    { id: 'area5', name: 'Marketing & Sales', description: 'Customer acquisition and retention' },
    { id: 'area6', name: 'Technology', description: 'IT infrastructure and digital capabilities' },
    { id: 'area7', name: 'Quality Management', description: 'Quality control and assurance systems' },
    { id: 'area8', name: 'Risk Management', description: 'Risk assessment and mitigation strategies' },
    { id: 'area9', name: 'Compliance', description: 'Regulatory compliance and reporting' },
    { id: 'area10', name: 'Competitive Advantage', description: 'Strategic positioning and differentiation' }
  ];

  useEffect(() => {
    loadLicenseData();
  }, []);

  const loadLicenseData = async () => {
    try {
      setLoading(true);
      const [balanceRes, invitationsRes] = await Promise.all([
        axios.get(`${API}/api/agency/license-balance`, authHeaders),
        axios.get(`${API}/api/agency/invitations`, authHeaders)
      ]);
      
      setLicenseBalance(balanceRes.data);
      setSentInvitations(invitationsRes.data.invitations || []);
    } catch (error) {
      console.error('Error loading license data:', error);
      alert('Failed to load license information');
    } finally {
      setLoading(false);
    }
  };

  const handleSendInvitation = async (e) => {
    e.preventDefault();
    
    // Check if agency has sufficient licenses
    const tierKey = `tier${invitationForm.tier_level}`;
    if (licenseBalance[tierKey] <= 0) {
      alert(`Insufficient Tier ${invitationForm.tier_level} licenses. Please purchase more licenses.`);
      setShowPurchaseModal(true);
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/api/agency/send-invitation`, invitationForm, authHeaders);
      
      alert('Invitation sent successfully!');
      setInvitationForm({
        recipient_email: '',
        tier_level: 1,
        custom_message: '',
        business_areas: [],
        expires_in_days: 30
      });
      
      // Reload data to update balance
      loadLicenseData();
    } catch (error) {
      console.error('Error sending invitation:', error);
      alert('Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchaseLicenses = async (e) => {
    e.preventDefault();
    
    const totalCost = (
      (purchaseForm.tier1_count * licensePricing.tier1) +
      (purchaseForm.tier2_count * licensePricing.tier2) +
      (purchaseForm.tier3_count * licensePricing.tier3)
    );

    if (totalCost === 0) {
      alert('Please select at least one license to purchase');
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/api/agency/purchase-licenses`, {
        ...purchaseForm,
        total_cost: totalCost
      }, authHeaders);
      
      alert(`Successfully purchased licenses for $${totalCost.toFixed(2)}!`);
      setPurchaseForm({ tier1_count: 0, tier2_count: 0, tier3_count: 0 });
      setShowPurchaseModal(false);
      
      // Reload balance
      loadLicenseData();
    } catch (error) {
      console.error('Error purchasing licenses:', error);
      alert('Failed to purchase licenses');
    } finally {
      setLoading(false);
    }
  };

  const getTierDescription = (tier) => {
    switch (tier) {
      case 1:
        return {
          name: 'Tier 1 - Basic Assessment',
          scope: 'Self-reported responses for fundamental business readiness',
          features: ['10 Business Areas', 'Basic Questions', 'Self-Assessment', 'Basic Reporting'],
          color: 'bg-blue-100 text-blue-800'
        };
      case 2:
        return {
          name: 'Tier 2 - Enhanced Assessment',
          scope: 'Evidence-backed validation for intermediate business verification',
          features: ['10 Business Areas', 'Evidence Upload Required', 'Document Verification', 'Enhanced Reporting'],
          color: 'bg-indigo-100 text-indigo-800'
        };
      case 3:
        return {
          name: 'Tier 3 - Comprehensive Assessment',
          scope: 'Full evidence review with navigator validation for procurement readiness',
          features: ['10 Business Areas', 'Comprehensive Evidence', 'Navigator Review', 'Certification Eligible'],
          color: 'bg-purple-100 text-purple-800'
        };
      default:
        return { name: 'Unknown Tier', scope: '', features: [], color: 'bg-gray-100 text-gray-800' };
    }
  };

  const calculateTotalCost = () => {
    return (
      (purchaseForm.tier1_count * licensePricing.tier1) +
      (purchaseForm.tier2_count * licensePricing.tier2) +
      (purchaseForm.tier3_count * licensePricing.tier3)
    );
  };

  if (loading && !licenseBalance.tier1 && !licenseBalance.tier2 && !licenseBalance.tier3) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading License Distribution Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">License Distribution Dashboard</h1>
          <p className="text-gray-600">Manage and distribute assessment licenses to sponsored businesses</p>
        </div>

        {/* License Balance Banner */}
        <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 rounded-xl p-6 text-white mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-xl font-semibold">License Balance</h3>
              <p className="text-purple-100">Available licenses for distribution</p>
            </div>
            <button
              onClick={() => setShowPurchaseModal(true)}
              className="bg-white text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Purchase More
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-6">
            {[1, 2, 3].map((tier) => {
              const tierInfo = getTierDescription(tier);
              const balance = licenseBalance[`tier${tier}`];
              return (
                <div key={tier} className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-2xl font-bold mb-1">{balance}</div>
                  <div className="text-sm text-purple-100">Tier {tier} Licenses</div>
                  <div className="text-xs text-purple-200 mt-1">${licensePricing[`tier${tier}`]} each</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {[
              { id: 'distribute', label: 'Distribute Licenses', icon: '📧' },
              { id: 'invitations', label: 'Sent Invitations', icon: '📋' },
              { id: 'tiers', label: 'Tier Information', icon: '📊' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Distribute Licenses Tab */}
        {activeTab === 'distribute' && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Send Assessment Invitation</h3>
            
            <form onSubmit={handleSendInvitation} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recipient Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={invitationForm.recipient_email}
                    onChange={(e) => setInvitationForm(prev => ({ ...prev, recipient_email: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="client@business.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assessment Tier Level
                  </label>
                  <select
                    value={invitationForm.tier_level}
                    onChange={(e) => setInvitationForm(prev => ({ ...prev, tier_level: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value={1}>Tier 1 - Basic Assessment ($25)</option>
                    <option value={2}>Tier 2 - Enhanced Assessment ($75)</option>
                    <option value={3}>Tier 3 - Comprehensive Assessment ($150)</option>
                  </select>
                </div>
              </div>

              {/* Tier Information Display */}
              <div className="bg-gray-50 rounded-lg p-4">
                {(() => {
                  const tierInfo = getTierDescription(invitationForm.tier_level);
                  return (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${tierInfo.color}`}>
                          {tierInfo.name}
                        </span>
                        <span className="text-sm text-gray-600">
                          Available: {licenseBalance[`tier${invitationForm.tier_level}`]} licenses
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{tierInfo.scope}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {tierInfo.features.map((feature, index) => (
                          <div key={index} className="flex items-center gap-1 text-sm text-gray-600">
                            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            {feature}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Areas (Optional - Select specific areas to focus on)
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto p-3 border border-gray-300 rounded-lg">
                  {businessAreas.map((area) => (
                    <label key={area.id} className="flex items-start gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={invitationForm.business_areas.includes(area.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setInvitationForm(prev => ({
                              ...prev,
                              business_areas: [...prev.business_areas, area.id]
                            }));
                          } else {
                            setInvitationForm(prev => ({
                              ...prev,
                              business_areas: prev.business_areas.filter(id => id !== area.id)
                            }));
                          }
                        }}
                        className="mt-1"
                      />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{area.name}</div>
                        <div className="text-xs text-gray-600">{area.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to include all business areas
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Message (Optional)
                </label>
                <textarea
                  rows={3}
                  value={invitationForm.custom_message}
                  onChange={(e) => setInvitationForm(prev => ({ ...prev, custom_message: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Add a personalized message for your client..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Invitation Expires In
                </label>
                <select
                  value={invitationForm.expires_in_days}
                  onChange={(e) => setInvitationForm(prev => ({ ...prev, expires_in_days: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value={7}>7 days</option>
                  <option value={14}>14 days</option>
                  <option value={30}>30 days</option>
                  <option value={60}>60 days</option>
                  <option value={90}>90 days</option>
                </select>
              </div>

              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  onClick={() => setInvitationForm({
                    recipient_email: '',
                    tier_level: 1,
                    custom_message: '',
                    business_areas: [],
                    expires_in_days: 30
                  })}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Clear Form
                </button>
                <button
                  type="submit"
                  disabled={loading || licenseBalance[`tier${invitationForm.tier_level}`] <= 0}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Sending...' : 'Send Invitation'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Sent Invitations Tab */}
        {activeTab === 'invitations' && (
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Sent Invitations</h3>
              <p className="text-sm text-gray-600">Track and manage your distributed assessment invitations</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Recipient</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Tier Level</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Sent Date</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Status</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Expires</th>
                    <th className="text-left py-3 px-6 font-medium text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {sentInvitations.map((invitation) => (
                    <tr key={invitation.id} className="hover:bg-gray-50">
                      <td className="py-4 px-6">
                        <div className="font-medium text-gray-900">{invitation.recipient_email}</div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          getTierDescription(invitation.tier_level).color
                        }`}>
                          Tier {invitation.tier_level}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="text-sm text-gray-900">
                          {new Date(invitation.sent_date).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          invitation.status === 'completed' ? 'bg-green-100 text-green-800' :
                          invitation.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          invitation.status === 'expired' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {invitation.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="text-sm text-gray-900">
                          {new Date(invitation.expires_date).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <button className="text-purple-600 hover:text-purple-800 text-sm font-medium">
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tier Information Tab */}
        {activeTab === 'tiers' && (
          <div className="space-y-6">
            {[1, 2, 3].map((tier) => {
              const tierInfo = getTierDescription(tier);
              return (
                <div key={tier} className="bg-white rounded-xl shadow-md p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className={`px-4 py-2 rounded-full text-sm font-medium ${tierInfo.color}`}>
                        {tierInfo.name}
                      </span>
                      <div className="mt-2">
                        <div className="text-2xl font-bold text-gray-900">${licensePricing[`tier${tier}`]}</div>
                        <div className="text-sm text-gray-600">per license</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-900">{licenseBalance[`tier${tier}`]}</div>
                      <div className="text-sm text-gray-600">available</div>
                    </div>
                  </div>

                  <p className="text-gray-700 mb-4">{tierInfo.scope}</p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {tierInfo.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-sm text-gray-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Purchase Licenses Modal */}
        {showPurchaseModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">Purchase License Packages</h3>
                  <button
                    onClick={() => setShowPurchaseModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <form onSubmit={handlePurchaseLicenses} className="space-y-6">
                  {[1, 2, 3].map((tier) => {
                    const tierInfo = getTierDescription(tier);
                    const tierKey = `tier${tier}_count`;
                    
                    return (
                      <div key={tier} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-3">
                          <div>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${tierInfo.color}`}>
                              {tierInfo.name}
                            </span>
                            <div className="text-lg font-bold text-gray-900 mt-1">
                              ${licensePricing[`tier${tier}`]} per license
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600">Current Balance</div>
                            <div className="text-lg font-semibold">{licenseBalance[`tier${tier}`]}</div>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          <label className="text-sm font-medium text-gray-700">Quantity:</label>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={purchaseForm[tierKey]}
                            onChange={(e) => setPurchaseForm(prev => ({
                              ...prev,
                              [tierKey]: parseInt(e.target.value) || 0
                            }))}
                            className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center"
                          />
                          <span className="text-sm text-gray-600">
                            = ${(purchaseForm[tierKey] * licensePricing[`tier${tier}`]).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    );
                  })}

                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-lg font-semibold text-gray-900">Total Cost:</span>
                      <span className="text-2xl font-bold text-purple-600">${calculateTotalCost().toFixed(2)}</span>
                    </div>

                    <div className="flex gap-4">
                      <button
                        type="button"
                        onClick={() => setShowPurchaseModal(false)}
                        className="flex-1 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={loading || calculateTotalCost() === 0}
                        className="flex-1 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {loading ? 'Processing...' : `Purchase for $${calculateTotalCost().toFixed(2)}`}
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgencyLicenseDistribution;