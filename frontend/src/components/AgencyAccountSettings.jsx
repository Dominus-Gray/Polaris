import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://smallbiz-assist.preview.emergentagent.com';

function AgencyAccountSettings() {
  const [activeTab, setActiveTab] = useState('subscription');
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [brandingData, setBrandingData] = useState({
    logo_url: '',
    primary_color: '#6366f1',
    secondary_color: '#8b5cf6',
    agency_name: '',
    contact_email: '',
    website_url: '',
    custom_domain: '',
    email_footer: ''
  });
  const [loading, setLoading] = useState(false);
  const [logoFile, setLogoFile] = useState(null);

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    loadAccountSettings();
  }, []);

  const loadAccountSettings = async () => {
    try {
      setLoading(true);
      const [subscriptionRes, brandingRes] = await Promise.all([
        axios.get(`${API}/api/agency/subscription`, authHeaders),
        axios.get(`${API}/api/agency/branding`, authHeaders)
      ]);
      
      setSubscriptionData(subscriptionRes.data);
      setBrandingData(brandingRes.data);
    } catch (error) {
      console.error('Error loading account settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBranding = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Handle logo upload if file is selected
      let logoUrl = brandingData.logo_url;
      if (logoFile) {
        const formData = new FormData();
        formData.append('logo', logoFile);
        
        const uploadRes = await axios.post(`${API}/api/agency/upload-logo`, formData, {
          ...authHeaders,
          headers: {
            ...authHeaders.headers,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        logoUrl = uploadRes.data.logo_url;
      }
      
      // Update branding settings
      await axios.put(`${API}/api/agency/branding`, {
        ...brandingData,
        logo_url: logoUrl
      }, authHeaders);
      
      alert('Branding settings updated successfully!');
      setLogoFile(null);
      loadAccountSettings();
    } catch (error) {
      console.error('Error updating branding:', error);
      alert('Failed to update branding settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscriptionChange = async (newPlan) => {
    try {
      setLoading(true);
      await axios.post(`${API}/api/agency/change-subscription`, {
        plan: newPlan
      }, authHeaders);
      
      alert('Subscription updated successfully!');
      loadAccountSettings();
    } catch (error) {
      console.error('Error updating subscription:', error);
      alert('Failed to update subscription');
    } finally {
      setLoading(false);
    }
  };

  const subscriptionPlans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 99,
      features: [
        '25 Tier 1 Licenses/month',
        '5 Tier 2 Licenses/month',
        '2 Tier 3 Licenses/month',
        'Basic Analytics',
        'Email Support',
        'Standard Branding'
      ]
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 299,
      features: [
        '100 Tier 1 Licenses/month',
        '25 Tier 2 Licenses/month',
        '10 Tier 3 Licenses/month',
        'Advanced Analytics',
        'Priority Support',
        'Custom Branding',
        'AI Contract Matching'
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 699,
      features: [
        'Unlimited Tier 1 Licenses',
        '100 Tier 2 Licenses/month',
        '50 Tier 3 Licenses/month',
        'Premium Analytics',
        'Dedicated Support',
        'White-label Solution',
        'API Access',
        'Custom Integrations'
      ]
    }
  ];

  if (loading && !subscriptionData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Account Settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Account Settings</h1>
          <p className="text-gray-600">Manage your subscription, billing, and branding preferences</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {[
              { id: 'subscription', label: 'Subscription & Billing', icon: '💳' },
              { id: 'branding', label: 'Branding & Theme', icon: '🎨' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-slate-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Subscription & Billing Tab */}
        {activeTab === 'subscription' && (
          <div className="space-y-6">
            {/* Current Subscription */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Subscription</h3>
              
              {subscriptionData && (
                <div className="bg-slate-50 rounded-lg p-4 mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <div className="text-lg font-semibold text-gray-900">{subscriptionData.plan_name}</div>
                      <div className="text-sm text-gray-600">Active since {new Date(subscriptionData.start_date).toLocaleDateString()}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-600">${subscriptionData.monthly_cost}</div>
                      <div className="text-sm text-gray-600">per month</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 mt-4 text-center">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{subscriptionData.licenses_used}</div>
                      <div className="text-xs text-gray-600">Licenses Used This Month</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-gray-900">{subscriptionData.licenses_remaining}</div>
                      <div className="text-xs text-gray-600">Licenses Remaining</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-gray-900">{new Date(subscriptionData.next_billing_date).toLocaleDateString()}</div>
                      <div className="text-xs text-gray-600">Next Billing Date</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Billing History */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Recent Billing History</h4>
                <div className="space-y-2">
                  {subscriptionData?.billing_history?.map((bill, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{bill.description}</div>
                        <div className="text-xs text-gray-600">{new Date(bill.date).toLocaleDateString()}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">${bill.amount}</div>
                        <div className={`text-xs ${bill.status === 'paid' ? 'text-green-600' : 'text-red-600'}`}>
                          {bill.status.toUpperCase()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Payment Method */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Payment Method</h4>
                <div className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg">
                  <div className="w-12 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                    VISA
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">•••• •••• •••• {subscriptionData?.payment_method?.last_four || '1234'}</div>
                    <div className="text-xs text-gray-600">Expires {subscriptionData?.payment_method?.expiry || '12/26'}</div>
                  </div>
                  <button className="text-slate-600 hover:text-slate-800 text-sm font-medium">
                    Update
                  </button>
                </div>
              </div>
            </div>

            {/* Available Plans */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Available Plans</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {subscriptionPlans.map((plan) => (
                  <div key={plan.id} className={`border-2 rounded-xl p-6 ${
                    subscriptionData?.plan_id === plan.id 
                      ? 'border-slate-600 bg-slate-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <div className="text-center mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">{plan.name}</h4>
                      <div className="text-3xl font-bold text-slate-600 mt-2">${plan.price}</div>
                      <div className="text-sm text-gray-600">per month</div>
                    </div>
                    
                    <ul className="space-y-2 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-gray-700">
                          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    
                    <button
                      onClick={() => handleSubscriptionChange(plan.id)}
                      disabled={loading || subscriptionData?.plan_id === plan.id}
                      className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                        subscriptionData?.plan_id === plan.id
                          ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                          : 'bg-slate-600 text-white hover:bg-slate-700'
                      }`}
                    >
                      {subscriptionData?.plan_id === plan.id ? 'Current Plan' : 'Upgrade'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Branding & Theme Tab */}
        {activeTab === 'branding' && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Branding & Theme Customization</h3>
            
            <form onSubmit={handleUpdateBranding} className="space-y-6">
              {/* Logo Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Agency Logo</label>
                <div className="flex items-center gap-4">
                  {brandingData.logo_url && (
                    <img 
                      src={brandingData.logo_url} 
                      alt="Current Logo" 
                      className="w-16 h-16 object-contain border border-gray-200 rounded-lg"
                    />
                  )}
                  <div className="flex-1">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setLogoFile(e.target.files[0])}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100"
                    />
                    <p className="text-xs text-gray-500 mt-1">PNG, JPG up to 2MB. Recommended size: 200x200px</p>
                  </div>
                </div>
              </div>

              {/* Agency Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Agency Name</label>
                  <input
                    type="text"
                    value={brandingData.agency_name}
                    onChange={(e) => setBrandingData(prev => ({ ...prev, agency_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                    placeholder="Your Agency Name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                  <input
                    type="email"
                    value={brandingData.contact_email}
                    onChange={(e) => setBrandingData(prev => ({ ...prev, contact_email: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                    placeholder="contact@youragency.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
                  <input
                    type="url"
                    value={brandingData.website_url}
                    onChange={(e) => setBrandingData(prev => ({ ...prev, website_url: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                    placeholder="https://www.youragency.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Custom Domain</label>
                  <input
                    type="text"
                    value={brandingData.custom_domain}
                    onChange={(e) => setBrandingData(prev => ({ ...prev, custom_domain: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                    placeholder="assess.youragency.com"
                  />
                  <p className="text-xs text-gray-500 mt-1">Optional: Custom domain for client assessments</p>
                </div>
              </div>

              {/* Color Scheme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">Color Scheme</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Primary Color</label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={brandingData.primary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, primary_color: e.target.value }))}
                        className="w-12 h-10 border border-gray-300 rounded-lg cursor-pointer"
                      />
                      <input
                        type="text"
                        value={brandingData.primary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, primary_color: e.target.value }))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Secondary Color</label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={brandingData.secondary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, secondary_color: e.target.value }))}
                        className="w-12 h-10 border border-gray-300 rounded-lg cursor-pointer"
                      />
                      <input
                        type="text"
                        value={brandingData.secondary_color}
                        onChange={(e) => setBrandingData(prev => ({ ...prev, secondary_color: e.target.value }))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Email Footer */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Footer</label>
                <textarea
                  rows={4}
                  value={brandingData.email_footer}
                  onChange={(e) => setBrandingData(prev => ({ ...prev, email_footer: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                  placeholder="Custom footer text for assessment invitation emails..."
                />
                <p className="text-xs text-gray-500 mt-1">This will appear at the bottom of all assessment invitation emails</p>
              </div>

              {/* Preview */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">Theme Preview</label>
                <div 
                  className="border border-gray-200 rounded-lg p-6"
                  style={{ 
                    background: `linear-gradient(135deg, ${brandingData.primary_color}15, ${brandingData.secondary_color}15)` 
                  }}
                >
                  <div className="flex items-center gap-4 mb-4">
                    {brandingData.logo_url && (
                      <img src={brandingData.logo_url} alt="Logo" className="w-12 h-12 object-contain" />
                    )}
                    <div>
                      <h4 className="text-lg font-semibold" style={{ color: brandingData.primary_color }}>
                        {brandingData.agency_name || 'Your Agency Name'}
                      </h4>
                      <p className="text-sm text-gray-600">Business Assessment Platform</p>
                    </div>
                  </div>
                  <button 
                    type="button"
                    className="px-4 py-2 rounded-lg text-white font-medium"
                    style={{ backgroundColor: brandingData.primary_color }}
                  >
                    Start Assessment
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Reset to Default
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Saving...' : 'Save Branding Settings'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgencyAccountSettings;