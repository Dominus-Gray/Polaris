import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enterprise Customer Onboarding and Customization System
export default function EnterpriseOnboardingSystem({ organizationType = 'agency' }) {
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [organizationData, setOrganizationData] = useState({});
  const [requirementsConfig, setRequirementsConfig] = useState({});
  const [customizationSettings, setCustomizationSettings] = useState({});
  const [deploymentOptions, setDeploymentOptions] = useState({});
  const [loading, setLoading] = useState(false);

  const totalSteps = 6;

  // Enterprise onboarding configuration
  const enterpriseConfigs = {
    federal_agency: {
      name: 'Federal Government Agency',
      icon: '🏛️',
      color: 'blue',
      requirements: [
        'Federal Agency Authorization',
        'ATO (Authority to Operate)',
        'FedRAMP Compliance Requirements',
        'FISMA Security Controls',
        'Government Performance Standards'
      ],
      customizations: [
        'Agency-Specific Assessment Areas',
        'Federal Compliance Tracking',
        'Government Reporting Dashboards',
        'Multi-Level Security Access',
        'Federal Branding Guidelines'
      ],
      deployment: [
        'Government Cloud (AWS GovCloud)',
        'Enhanced Security Monitoring',
        'Federal Audit Trail',
        'Compliance Reporting Automation',
        'Government-Grade Support SLA'
      ]
    },
    state_agency: {
      name: 'State Government Agency',
      icon: '🏢',
      color: 'green',
      requirements: [
        'State Government Authorization',
        'State Procurement Regulations',
        'Local Business Development Goals',
        'Regional Economic Impact Metrics',
        'State Compliance Standards'
      ],
      customizations: [
        'State-Specific Business Areas',
        'Regional Industry Focus',
        'Local Service Provider Network',
        'State Branding and Messaging',
        'Regional Performance Metrics'
      ],
      deployment: [
        'State Government Infrastructure',
        'Regional Data Center Hosting',
        'State Security Requirements',
        'Local Integration Capabilities',
        'Regional Support Team'
      ]
    },
    economic_development: {
      name: 'Economic Development Organization',
      icon: '📈',
      color: 'purple',
      requirements: [
        'Economic Development Mission',
        'Regional Business Support Authority',
        'Community Impact Measurement',
        'Business Development Programs',
        'Regional Partnership Network'
      ],
      customizations: [
        'Economic Impact Dashboards',
        'Regional Business Matching',
        'Community Success Metrics',
        'Local Resource Integration',
        'Partnership Network Management'
      ],
      deployment: [
        'Flexible Cloud Hosting',
        'Regional Customization',
        'Community Integration APIs',
        'Economic Impact Reporting',
        'Partnership Management Tools'
      ]
    },
    enterprise_corporation: {
      name: 'Enterprise Corporation',
      icon: '🏗️',
      color: 'indigo',
      requirements: [
        'Corporate Procurement Authority',
        'Supplier Diversity Programs',
        'Vendor Management Systems',
        'Corporate Compliance Standards',
        'Supply Chain Requirements'
      ],
      customizations: [
        'Corporate Procurement Standards',
        'Supplier Diversity Tracking',
        'Vendor Qualification Metrics',
        'Corporate Branding Integration',
        'Executive Reporting Dashboards'
      ],
      deployment: [
        'Enterprise Cloud Infrastructure',
        'Corporate Security Integration',
        'ERP System Connectivity',
        'Executive Analytics Dashboards',
        'Enterprise Support Services'
      ]
    }
  };

  const steps = [
    {
      id: 1,
      title: 'Organization Profile',
      description: 'Tell us about your organization and procurement goals',
      icon: '🏢'
    },
    {
      id: 2,
      title: 'Requirements Analysis',
      description: 'Configure compliance and regulatory requirements',
      icon: '📋'
    },
    {
      id: 3,
      title: 'Platform Customization',
      description: 'Customize features and user experience',
      icon: '🎨'
    },
    {
      id: 4,
      title: 'Deployment Configuration',
      description: 'Set up hosting and infrastructure options',
      icon: '⚙️'
    },
    {
      id: 5,
      title: 'Integration Setup',
      description: 'Configure external systems and data connections',
      icon: '🔗'
    },
    {
      id: 6,
      title: 'Launch Preparation',
      description: 'Review configuration and prepare for deployment',
      icon: '🚀'
    }
  ];

  const currentConfig = enterpriseConfigs[organizationType] || enterpriseConfigs.economic_development;

  const nextStep = () => {
    if (onboardingStep < totalSteps) {
      setOnboardingStep(onboardingStep + 1);
    }
  };

  const prevStep = () => {
    if (onboardingStep > 1) {
      setOnboardingStep(onboardingStep - 1);
    }
  };

  const completeOnboarding = async () => {
    try {
      setLoading(true);
      
      const onboardingData = {
        organization_type: organizationType,
        organization_data: organizationData,
        requirements_config: requirementsConfig,
        customization_settings: customizationSettings,
        deployment_options: deploymentOptions,
        completed_at: new Date().toISOString()
      };
      
      const response = await axios.post(`${API}/enterprise/onboarding/complete`, onboardingData);
      
      if (response.data.success) {
        // Show success and redirect to deployment dashboard
        window.location.href = `/enterprise/dashboard/${response.data.organization_id}`;
      }
      
    } catch (error) {
      console.error('Enterprise onboarding failed:', error);
      alert('Onboarding completion failed. Please review your configuration and try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (onboardingStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Organization Name</label>
                <input
                  type="text"
                  value={organizationData.name || ''}
                  onChange={(e) => setOrganizationData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Regional Economic Development Authority"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Primary Contact</label>
                <input
                  type="email"
                  value={organizationData.contact_email || ''}
                  onChange={(e) => setOrganizationData(prev => ({ ...prev, contact_email: e.target.value }))}
                  placeholder="director@regional-eda.gov"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Service Region</label>
              <select
                value={organizationData.service_region || ''}
                onChange={(e) => setOrganizationData(prev => ({ ...prev, service_region: e.target.value }))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Service Region</option>
                <option value="state">Single State</option>
                <option value="multi_state">Multi-State Region</option>
                <option value="national">National</option>
                <option value="international">International</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Expected User Volume</label>
              <select
                value={organizationData.user_volume || ''}
                onChange={(e) => setOrganizationData(prev => ({ ...prev, user_volume: e.target.value }))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Expected Volume</option>
                <option value="small">100-500 users</option>
                <option value="medium">500-2,000 users</option>
                <option value="large">2,000-10,000 users</option>
                <option value="enterprise">10,000+ users</option>
              </select>
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Core Requirements for {currentConfig.name}</h4>
              <div className="space-y-2">
                {currentConfig.requirements.map((requirement, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                    <input
                      type="checkbox"
                      checked={requirementsConfig[`req_${index}`] || false}
                      onChange={(e) => setRequirementsConfig(prev => ({ 
                        ...prev, 
                        [`req_${index}`]: e.target.checked 
                      }))}
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-slate-700">{requirement}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Additional Requirements</label>
              <textarea
                value={requirementsConfig.additional_requirements || ''}
                onChange={(e) => setRequirementsConfig(prev => ({ ...prev, additional_requirements: e.target.value }))}
                placeholder="Any additional compliance or regulatory requirements specific to your organization..."
                rows="4"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>
          </div>
        );
        
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Platform Customizations</h4>
              <div className="space-y-2">
                {currentConfig.customizations.map((customization, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <input
                      type="checkbox"
                      checked={customizationSettings[`custom_${index}`] || false}
                      onChange={(e) => setCustomizationSettings(prev => ({ 
                        ...prev, 
                        [`custom_${index}`]: e.target.checked 
                      }))}
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-blue-800">{customization}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Assessment Focus Areas</label>
                <select
                  value={customizationSettings.assessment_focus || ''}
                  onChange={(e) => setCustomizationSettings(prev => ({ ...prev, assessment_focus: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Focus</option>
                  <option value="general">General Procurement</option>
                  <option value="technology">Technology Contracts</option>
                  <option value="construction">Construction Projects</option>
                  <option value="professional">Professional Services</option>
                  <option value="specialized">Specialized Industry</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Reporting Level</label>
                <select
                  value={customizationSettings.reporting_level || ''}
                  onChange={(e) => setCustomizationSettings(prev => ({ ...prev, reporting_level: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Level</option>
                  <option value="basic">Basic Metrics</option>
                  <option value="advanced">Advanced Analytics</option>
                  <option value="executive">Executive Dashboards</option>
                  <option value="comprehensive">Comprehensive BI</option>
                </select>
              </div>
            </div>
          </div>
        );
        
      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Deployment Infrastructure</h4>
              <div className="space-y-2">
                {currentConfig.deployment.map((option, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                    <input
                      type="radio"
                      name="deployment_option"
                      checked={deploymentOptions.primary_option === index}
                      onChange={() => setDeploymentOptions(prev => ({ ...prev, primary_option: index }))}
                      className="text-green-600 focus:ring-green-500"
                    />
                    <span className="text-sm text-green-800">{option}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Custom Domain</label>
                <input
                  type="text"
                  value={deploymentOptions.custom_domain || ''}
                  onChange={(e) => setDeploymentOptions(prev => ({ ...prev, custom_domain: e.target.value }))}
                  placeholder="procurement.youragency.gov"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Support Level</label>
                <select
                  value={deploymentOptions.support_level || ''}
                  onChange={(e) => setDeploymentOptions(prev => ({ ...prev, support_level: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Support</option>
                  <option value="standard">Standard Support</option>
                  <option value="premium">Premium Support</option>
                  <option value="enterprise">Enterprise Support</option>
                  <option value="white_glove">White Glove Service</option>
                </select>
              </div>
            </div>
          </div>
        );
        
      case 6:
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
              <h4 className="text-lg font-semibold text-slate-900 mb-4">🎉 Ready for Launch!</h4>
              <p className="text-slate-700 mb-4">
                Your enterprise platform configuration is complete. Review the summary below and click "Launch Platform" to begin deployment.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium text-slate-900 mb-2">Organization Details</h5>
                  <div className="space-y-1 text-sm text-slate-600">
                    <div><strong>Name:</strong> {organizationData.name || 'Not specified'}</div>
                    <div><strong>Type:</strong> {currentConfig.name}</div>
                    <div><strong>Region:</strong> {organizationData.service_region || 'Not specified'}</div>
                    <div><strong>Expected Users:</strong> {organizationData.user_volume || 'Not specified'}</div>
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-slate-900 mb-2">Platform Configuration</h5>
                  <div className="space-y-1 text-sm text-slate-600">
                    <div><strong>Assessment Focus:</strong> {customizationSettings.assessment_focus || 'General'}</div>
                    <div><strong>Reporting:</strong> {customizationSettings.reporting_level || 'Basic'}</div>
                    <div><strong>Domain:</strong> {deploymentOptions.custom_domain || 'Standard'}</div>
                    <div><strong>Support:</strong> {deploymentOptions.support_level || 'Standard'}</div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 flex gap-3">
                <button
                  onClick={completeOnboarding}
                  disabled={loading}
                  className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
                >
                  {loading ? 'Launching...' : '🚀 Launch Platform'}
                </button>
                <button
                  onClick={prevStep}
                  className="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Review Configuration
                </button>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
              <div className="flex items-center gap-2 text-sm text-blue-800">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium">Deployment Timeline:</span>
                <span>2-4 business days for full platform deployment and configuration</span>
              </div>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="text-center py-12 text-slate-500">
            <h4 className="text-lg font-medium mb-2">Step {onboardingStep} Configuration</h4>
            <p>Configuration options for this step are being prepared...</p>
          </div>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Progress Header */}
      <div className={`bg-gradient-to-r from-${currentConfig.color}-600 to-${currentConfig.color}-700 text-white rounded-lg p-6 mb-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-4xl">{currentConfig.icon}</div>
            <div>
              <h1 className="text-2xl font-bold mb-1">Enterprise Platform Setup</h1>
              <p className="opacity-90">{currentConfig.name} Configuration</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">Step {onboardingStep}</div>
            <div className="text-sm opacity-75">of {totalSteps}</div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-6">
          <div className="w-full bg-white/20 rounded-full h-2">
            <div 
              className="bg-white rounded-full h-2 transition-all duration-500"
              style={{ width: `${(onboardingStep / totalSteps) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs mt-2 opacity-75">
            <span>Getting Started</span>
            <span>Configuration</span>
            <span>Deployment</span>
            <span>Launch Ready</span>
          </div>
        </div>
      </div>

      {/* Step Navigation */}
      <div className="bg-white rounded-lg border mb-6">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-slate-900">{steps[onboardingStep - 1].title}</h2>
              <p className="text-slate-600">{steps[onboardingStep - 1].description}</p>
            </div>
            <div className="text-3xl">{steps[onboardingStep - 1].icon}</div>
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      {onboardingStep < totalSteps && (
        <div className="flex items-center justify-between">
          <button
            onClick={prevStep}
            disabled={onboardingStep === 1}
            className="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ← Previous
          </button>
          
          <div className="flex items-center gap-2">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  step.id <= onboardingStep
                    ? `bg-${currentConfig.color}-500`
                    : 'bg-slate-200'
                }`}
              />
            ))}
          </div>
          
          <button
            onClick={nextStep}
            className={`px-6 py-3 bg-${currentConfig.color}-600 text-white rounded-lg hover:bg-${currentConfig.color}-700 transition-colors font-medium`}
          >
            Next →
          </button>
        </div>
      )}

      {/* Step Indicator */}
      <div className="mt-6 text-center text-sm text-slate-500">
        Step {onboardingStep} of {totalSteps} • {Math.round((onboardingStep / totalSteps) * 100)}% Complete
      </div>
    </div>
  );
}

// Enterprise Organization Type Selector
export function EnterpriseOrgTypeSelector({ onTypeChange, currentType = 'economic_development' }) {
  const [showSelector, setShowSelector] = useState(false);

  const orgTypes = [
    { 
      id: 'federal_agency', 
      name: 'Federal Government Agency', 
      icon: '🏛️', 
      description: 'Federal departments and agencies',
      complexity: 'Very High',
      timeline: '6-12 months'
    },
    { 
      id: 'state_agency', 
      name: 'State Government Agency', 
      icon: '🏢', 
      description: 'State and local government organizations',
      complexity: 'High', 
      timeline: '3-6 months'
    },
    { 
      id: 'economic_development', 
      name: 'Economic Development Organization', 
      icon: '📈', 
      description: 'Regional economic development authorities',
      complexity: 'Medium',
      timeline: '2-4 months'
    },
    { 
      id: 'enterprise_corporation', 
      name: 'Enterprise Corporation', 
      icon: '🏗️', 
      description: 'Large corporations with supplier diversity programs',
      complexity: 'Medium-High',
      timeline: '3-5 months'
    }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setShowSelector(!showSelector)}
        className="flex items-center gap-3 px-4 py-3 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors w-full text-left"
      >
        <span className="text-2xl">
          {orgTypes.find(t => t.id === currentType)?.icon || '🏢'}
        </span>
        <div className="flex-1">
          <div className="font-medium text-slate-900">
            {orgTypes.find(t => t.id === currentType)?.name || 'Select Organization Type'}
          </div>
          <div className="text-sm text-slate-600">
            {orgTypes.find(t => t.id === currentType)?.description || 'Choose your organization type'}
          </div>
        </div>
        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showSelector && (
        <>
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50">
            <div className="p-2">
              {orgTypes.map((orgType) => (
                <button
                  key={orgType.id}
                  onClick={() => {
                    onTypeChange(orgType.id);
                    setShowSelector(false);
                  }}
                  className={`w-full flex items-start gap-3 px-3 py-3 text-left rounded-lg transition-colors ${
                    currentType === orgType.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xl">{orgType.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">{orgType.name}</div>
                    <div className="text-xs opacity-75 mb-1">{orgType.description}</div>
                    <div className="flex items-center gap-3 text-xs">
                      <span>Complexity: {orgType.complexity}</span>
                      <span>Timeline: {orgType.timeline}</span>
                    </div>
                  </div>
                  {currentType === orgType.id && (
                    <svg className="w-4 h-4 text-blue-600 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setShowSelector(false)}
          />
        </>
      )}
    </div>
  );
}