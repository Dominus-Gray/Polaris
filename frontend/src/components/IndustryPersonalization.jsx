import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Industry Personalization Context
const IndustryContext = createContext();

// Industry-specific configurations
const industryConfigurations = {
  technology: {
    name: 'Technology & Software',
    icon: '💻',
    color: 'blue',
    priorityAreas: ['area5', 'area3', 'area2'], // Tech, Legal, Financial
    keyRequirements: [
      'Cybersecurity compliance (NIST, FedRAMP)',
      'Software development lifecycle documentation',
      'Data protection and privacy policies',
      'Intellectual property management'
    ],
    commonChallenges: [
      'Meeting government cybersecurity standards',
      'Scaling operations for large contracts',
      'Compliance documentation requirements',
      'Technical proposal writing'
    ],
    successMetrics: [
      'NIST compliance certification',
      'FedRAMP authorization',
      'Security clearance eligibility',
      'Agile development processes'
    ],
    recommendedProviders: ['cybersecurity', 'compliance', 'technical_writing'],
    averageTimeToReady: '12-16 weeks'
  },
  
  construction: {
    name: 'Construction & Engineering',
    icon: '🏗️',
    color: 'orange',
    priorityAreas: ['area8', 'area6', 'area4'], // Risk, HR, Operations
    keyRequirements: [
      'Safety management systems',
      'Bonding and insurance requirements',
      'Quality control processes',
      'Environmental compliance'
    ],
    commonChallenges: [
      'Meeting safety and environmental standards',
      'Obtaining adequate bonding capacity',
      'Managing subcontractor relationships',
      'Documentation for past performance'
    ],
    successMetrics: [
      'OSHA safety record',
      'Bonding capacity verification',
      'Past performance portfolio',
      'Quality certifications (ISO 9001)'
    ],
    recommendedProviders: ['safety_consulting', 'bonding_agents', 'quality_management'],
    averageTimeToReady: '16-20 weeks'
  },
  
  healthcare: {
    name: 'Healthcare & Medical',
    icon: '🏥',
    color: 'green',
    priorityAreas: ['area3', 'area8', 'area5'], // Legal, Risk, Technology
    keyRequirements: [
      'HIPAA compliance protocols',
      'Medical device regulations',
      'Clinical quality standards',
      'Healthcare IT security'
    ],
    commonChallenges: [
      'HIPAA and privacy compliance',
      'Medical device approval processes',
      'Clinical trial documentation',
      'Healthcare IT security requirements'
    ],
    successMetrics: [
      'HIPAA compliance certification',
      'FDA approvals and clearances',
      'Joint Commission accreditation',
      'Healthcare security standards'
    ],
    recommendedProviders: ['healthcare_compliance', 'medical_consulting', 'hipaa_security'],
    averageTimeToReady: '20-24 weeks'
  },
  
  manufacturing: {
    name: 'Manufacturing & Production',
    icon: '🏭',
    color: 'purple',
    priorityAreas: ['area4', 'area9', 'area7'], // Operations, Supply Chain, Performance
    keyRequirements: [
      'ISO quality management systems',
      'Supply chain security protocols',
      'Environmental compliance',
      'Production capacity documentation'
    ],
    commonChallenges: [
      'Supply chain transparency and security',
      'Quality management system implementation',
      'Environmental and safety compliance',
      'Scaling production for large contracts'
    ],
    successMetrics: [
      'ISO 9001 certification',
      'Supply chain security compliance',
      'Environmental certifications',
      'Production capacity verification'
    ],
    recommendedProviders: ['iso_consulting', 'supply_chain', 'environmental_compliance'],
    averageTimeToReady: '14-18 weeks'
  },
  
  professional_services: {
    name: 'Professional Services',
    icon: '💼',
    color: 'indigo',
    priorityAreas: ['area6', 'area3', 'area10'], // HR, Legal, Competitive Advantage
    keyRequirements: [
      'Professional liability insurance',
      'Certifications and credentials',
      'Quality assurance processes',
      'Client confidentiality protocols'
    ],
    commonChallenges: [
      'Demonstrating expertise and credentials',
      'Building client reference portfolio',
      'Meeting professional standards',
      'Competitive differentiation'
    ],
    successMetrics: [
      'Professional certifications current',
      'Client testimonials and references',
      'Quality management processes',
      'Competitive positioning'
    ],
    recommendedProviders: ['professional_development', 'business_coaching', 'marketing'],
    averageTimeToReady: '8-12 weeks'
  }
};

// Industry Provider Component
export function IndustryProvider({ children }) {
  const [selectedIndustry, setSelectedIndustry] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [industryInsights, setIndustryInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserIndustryData();
  }, []);

  const loadUserIndustryData = async () => {
    try {
      // Get user profile to determine industry
      const profileResponse = await axios.get(`${API}/profile/me`);
      const profile = profileResponse.data;
      
      setUserProfile(profile);
      
      // Determine industry from profile or set default
      const industry = profile.industry?.toLowerCase().replace(/\s+/g, '_') || 'professional_services';
      const industryConfig = industryConfigurations[industry] || industryConfigurations.professional_services;
      
      setSelectedIndustry(industryConfig);
      
      // Load industry-specific insights
      await loadIndustryInsights(industry);
      
    } catch (error) {
      console.warn('Failed to load industry data:', error);
      // Default to professional services
      setSelectedIndustry(industryConfigurations.professional_services);
    } finally {
      setLoading(false);
    }
  };

  const loadIndustryInsights = async (industry) => {
    try {
      const response = await axios.get(`${API}/industry/insights/${industry}`);
      setIndustryInsights(response.data);
    } catch (error) {
      console.warn('Failed to load industry insights:', error);
      // Generate default insights
      const config = industryConfigurations[industry];
      if (config) {
        setIndustryInsights({
          industry: industry,
          benchmarks: {
            average_readiness: 65,
            top_performers: 85,
            common_weak_areas: config.priorityAreas.slice(0, 2)
          },
          trends: [
            `${config.name} businesses typically need ${config.averageTimeToReady} to achieve readiness`,
            `Most successful companies focus on ${config.keyRequirements[0]} first`,
            `${config.commonChallenges[0]} is the most common challenge`
          ]
        });
      }
    }
  };

  const updateUserIndustry = async (newIndustry) => {
    try {
      await axios.patch(`${API}/profile/me`, { industry: newIndustry });
      const industryConfig = industryConfigurations[newIndustry] || industryConfigurations.professional_services;
      setSelectedIndustry(industryConfig);
      await loadIndustryInsights(newIndustry);
    } catch (error) {
      console.error('Failed to update industry:', error);
    }
  };

  const value = {
    selectedIndustry,
    industryInsights,
    userProfile,
    loading,
    updateUserIndustry,
    availableIndustries: Object.entries(industryConfigurations).map(([key, config]) => ({
      id: key,
      ...config
    }))
  };

  return (
    <IndustryContext.Provider value={value}>
      {children}
    </IndustryContext.Provider>
  );
}

// Hook to use industry context
export function useIndustry() {
  const context = useContext(IndustryContext);
  if (!context) {
    throw new Error('useIndustry must be used within an IndustryProvider');
  }
  return context;
}

// Industry-Specific Assessment Guidance Component
export function IndustryAssessmentGuidance() {
  const { selectedIndustry, industryInsights, loading } = useIndustry();

  if (loading || !selectedIndustry) {
    return (
      <div className="bg-slate-50 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-r from-${selectedIndustry.color}-50 to-${selectedIndustry.color}-100 rounded-lg border border-${selectedIndustry.color}-200 p-6 mb-6`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-3 bg-${selectedIndustry.color}-100 rounded-lg`}>
          <span className="text-2xl">{selectedIndustry.icon}</span>
        </div>
        <div>
          <h3 className={`text-lg font-semibold text-${selectedIndustry.color}-900`}>
            {selectedIndustry.name} Guidance
          </h3>
          <p className={`text-sm text-${selectedIndustry.color}-700`}>
            Customized for your industry
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Priority Areas */}
        <div className="bg-white rounded-lg p-4 border">
          <h4 className="font-medium text-slate-900 mb-3">Priority Assessment Areas</h4>
          <div className="space-y-2">
            {selectedIndustry.priorityAreas.map((areaId, index) => (
              <div key={areaId} className="flex items-center gap-2">
                <div className={`w-6 h-6 bg-${selectedIndustry.color}-100 rounded-full flex items-center justify-center text-xs font-bold text-${selectedIndustry.color}-600`}>
                  {index + 1}
                </div>
                <span className="text-sm text-slate-700">
                  {areaId === 'area1' ? 'Legal & Compliance' :
                   areaId === 'area2' ? 'Financial Management' :
                   areaId === 'area3' ? 'Legal & Compliance' :
                   areaId === 'area4' ? 'Operations Management' :
                   areaId === 'area5' ? 'Technology & Security' :
                   areaId === 'area6' ? 'Human Resources' :
                   areaId === 'area7' ? 'Performance Tracking' :
                   areaId === 'area8' ? 'Risk Management' :
                   areaId === 'area9' ? 'Supply Chain' :
                   areaId === 'area10' ? 'Competitive Advantage' : 'Business Area'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Key Requirements */}
        <div className="bg-white rounded-lg p-4 border">
          <h4 className="font-medium text-slate-900 mb-3">Key Requirements</h4>
          <div className="space-y-2">
            {selectedIndustry.keyRequirements.slice(0, 4).map((requirement, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-slate-600">{requirement}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Industry Insights */}
      {industryInsights && (
        <div className="mt-4 bg-white rounded-lg p-4 border">
          <h4 className="font-medium text-slate-900 mb-3">Industry Benchmarks</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className={`text-2xl font-bold text-${selectedIndustry.color}-600`}>
                {industryInsights.benchmarks?.average_readiness || 65}%
              </div>
              <div className="text-xs text-slate-600">Industry Average</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold text-${selectedIndustry.color}-600`}>
                {industryInsights.benchmarks?.top_performers || 85}%
              </div>
              <div className="text-xs text-slate-600">Top Performers</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold text-${selectedIndustry.color}-600`}>
                {selectedIndustry.averageTimeToReady}
              </div>
              <div className="text-xs text-slate-600">Avg. Time to Ready</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button className={`px-3 py-1.5 bg-${selectedIndustry.color}-600 text-white rounded-lg hover:bg-${selectedIndustry.color}-700 transition-colors text-sm`}>
          View Industry Guide
        </button>
        <button className={`px-3 py-1.5 border border-${selectedIndustry.color}-300 text-${selectedIndustry.color}-700 rounded-lg hover:bg-${selectedIndustry.color}-50 transition-colors text-sm`}>
          Connect with Industry Experts
        </button>
        <button className={`px-3 py-1.5 border border-${selectedIndustry.color}-300 text-${selectedIndustry.color}-700 rounded-lg hover:bg-${selectedIndustry.color}-50 transition-colors text-sm`}>
          View Success Stories
        </button>
      </div>
    </div>
  );
}

// Industry Selector Component
export function IndustrySelector({ onSelect = null }) {
  const { selectedIndustry, updateUserIndustry, availableIndustries } = useIndustry();
  const [isOpen, setIsOpen] = useState(false);

  const handleIndustrySelect = async (industryId) => {
    try {
      await updateUserIndustry(industryId);
      setIsOpen(false);
      if (onSelect) {
        onSelect(industryId);
      }
    } catch (error) {
      console.error('Failed to select industry:', error);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-3 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors w-full text-left"
      >
        <span className="text-2xl">{selectedIndustry?.icon || '💼'}</span>
        <div className="flex-1">
          <div className="font-medium text-slate-900">
            {selectedIndustry?.name || 'Select Your Industry'}
          </div>
          <div className="text-sm text-slate-600">
            Customize your experience
          </div>
        </div>
        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
            <div className="p-2">
              {availableIndustries.map((industry) => (
                <button
                  key={industry.id}
                  onClick={() => handleIndustrySelect(industry.id)}
                  className={`w-full flex items-center gap-3 px-3 py-3 text-left rounded-lg transition-colors ${
                    selectedIndustry?.name === industry.name
                      ? `bg-${industry.color}-50 text-${industry.color}-900`
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xl">{industry.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">{industry.name}</div>
                    <div className="text-xs text-slate-500">
                      {industry.averageTimeToReady} typical timeline
                    </div>
                  </div>
                  {selectedIndustry?.name === industry.name && (
                    <svg className={`w-4 h-4 text-${industry.color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
        </>
      )}
    </div>
  );
}

// Hook to use industry context
export function useIndustryPersonalization() {
  const context = useContext(IndustryContext);
  if (!context) {
    throw new Error('useIndustryPersonalization must be used within an IndustryProvider');
  }
  return context;
}

// Industry-Specific Recommendations Component
export function IndustryRecommendations() {
  const { selectedIndustry, industryInsights } = useIndustry();
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    if (selectedIndustry) {
      generateIndustryRecommendations();
    }
  }, [selectedIndustry, industryInsights]);

  const generateIndustryRecommendations = () => {
    if (!selectedIndustry) return;

    const recs = [
      {
        type: 'priority_focus',
        title: `Start with ${selectedIndustry.name} Essentials`,
        description: `Focus on ${selectedIndustry.keyRequirements[0]} as your foundation.`,
        action: 'Begin Assessment',
        priority: 'high',
        icon: selectedIndustry.icon
      },
      {
        type: 'industry_expert',
        title: 'Connect with Industry Experts',
        description: `Find ${selectedIndustry.recommendedProviders[0]} specialists in your area.`,
        action: 'Find Experts',
        priority: 'medium',
        icon: '🎯'
      },
      {
        type: 'benchmark',
        title: 'Industry Benchmarking',
        description: `Compare your progress against ${selectedIndustry.name} leaders.`,
        action: 'View Benchmarks',
        priority: 'low',
        icon: '📊'
      }
    ];

    setRecommendations(recs);
  };

  if (!selectedIndustry) {
    return null;
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec, index) => (
        <div key={index} className={`bg-gradient-to-r from-${selectedIndustry.color}-50 to-white rounded-lg p-4 border border-${selectedIndustry.color}-100`}>
          <div className="flex items-start gap-3">
            <div className={`p-2 bg-${selectedIndustry.color}-100 rounded-lg`}>
              <span className="text-lg">{rec.icon}</span>
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-slate-900 mb-1">{rec.title}</h4>
              <p className="text-sm text-slate-600 mb-2">{rec.description}</p>
              <button className={`text-sm px-3 py-1.5 bg-${selectedIndustry.color}-600 text-white rounded-lg hover:bg-${selectedIndustry.color}-700 transition-colors`}>
                {rec.action} →
              </button>
            </div>
            <div className={`px-2 py-1 rounded-full text-xs ${
              rec.priority === 'high' ? 'bg-red-100 text-red-800' :
              rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {rec.priority}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}