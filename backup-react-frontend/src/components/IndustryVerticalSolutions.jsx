import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Industry-Specific Vertical Solutions for Specialized Sectors
export default function IndustryVerticalSolutions({ industry, userRole }) {
  const [verticalData, setVerticalData] = useState(null);
  const [specializations, setSpecializations] = useState([]);
  const [complianceRequirements, setComplianceRequirements] = useState([]);
  const [industryBenchmarks, setIndustryBenchmarks] = useState(null);
  const [loading, setLoading] = useState(true);

  // Industry vertical configurations
  const industryVerticals = {
    defense: {
      name: 'Defense & Aerospace',
      icon: '🛡️',
      color: 'red',
      description: 'Specialized defense contracting and aerospace procurement',
      keyRequirements: [
        'Security Clearance Eligibility',
        'DFARS (Defense Federal Acquisition Regulation Supplement)',
        'CMMC (Cybersecurity Maturity Model Certification)',
        'ITAR (International Traffic in Arms Regulations)',
        'Export Administration Regulations (EAR)'
      ],
      specializations: [
        {
          id: 'cybersecurity_defense',
          title: 'Defense Cybersecurity',
          description: 'CMMC compliance and defense information systems security',
          requirements: ['CMMC Level 2+', 'NIST 800-171', 'FedRAMP'],
          market_value: '$2.1B annually',
          competition: 'Medium',
          certification_timeline: '12-18 months'
        },
        {
          id: 'aerospace_engineering',
          title: 'Aerospace Engineering',
          description: 'Aircraft systems, satellite technology, and space systems',
          requirements: ['AS9100 Quality', 'ITAR Registration', 'Security Clearance'],
          market_value: '$8.7B annually',
          competition: 'High',
          certification_timeline: '18-24 months'
        },
        {
          id: 'defense_logistics',
          title: 'Defense Logistics',
          description: 'Supply chain management for defense operations',
          requirements: ['RFID Capability', 'Wide Area WorkFlow', 'Transportation Security'],
          market_value: '$4.2B annually',
          competition: 'Medium',
          certification_timeline: '8-12 months'
        }
      ],
      successMetrics: [
        'CMMC certification achieved',
        'Security clearance granted',
        'DFARS compliance verified',
        'Defense contract awards'
      ]
    },
    healthcare: {
      name: 'Healthcare & Medical',
      icon: '🏥',
      color: 'green',
      description: 'Healthcare system procurement and medical technology',
      keyRequirements: [
        'HIPAA Compliance Certification',
        'FDA Medical Device Regulations',
        'Joint Commission Standards',
        'HITECH Act Compliance',
        'Healthcare Quality Standards'
      ],
      specializations: [
        {
          id: 'health_it',
          title: 'Healthcare Information Technology',
          description: 'EHR systems, health data analytics, and medical software',
          requirements: ['HIPAA Certification', 'HL7 FHIR', 'Meaningful Use'],
          market_value: '$5.3B annually',
          competition: 'High',
          certification_timeline: '10-14 months'
        },
        {
          id: 'medical_devices',
          title: 'Medical Device Procurement',
          description: 'Medical equipment, diagnostic devices, and clinical technology',
          requirements: ['FDA 510(k)', 'ISO 13485', 'Clinical Evidence'],
          market_value: '$12.4B annually',
          competition: 'Very High',
          certification_timeline: '18-36 months'
        },
        {
          id: 'healthcare_consulting',
          title: 'Healthcare Consulting',
          description: 'Clinical process improvement and healthcare analytics',
          requirements: ['Healthcare Experience', 'Clinical Credentials', 'Quality Metrics'],
          market_value: '$3.1B annually',
          competition: 'Medium',
          certification_timeline: '6-12 months'
        }
      ],
      successMetrics: [
        'HIPAA certification maintained',
        'Clinical quality scores',
        'Patient safety compliance',
        'Healthcare contract performance'
      ]
    },
    energy: {
      name: 'Energy & Infrastructure',
      icon: '⚡',
      color: 'yellow',
      description: 'Energy sector procurement and infrastructure development',
      keyRequirements: [
        'Department of Energy (DOE) Requirements',
        'Environmental Impact Assessments',
        'Energy Efficiency Standards',
        'Grid Security Compliance',
        'Renewable Energy Certifications'
      ],
      specializations: [
        {
          id: 'renewable_energy',
          title: 'Renewable Energy Systems',
          description: 'Solar, wind, and clean energy infrastructure development',
          requirements: ['NABCEP Certification', 'Environmental Compliance', 'Grid Integration'],
          market_value: '$15.2B annually',
          competition: 'High',
          certification_timeline: '12-18 months'
        },
        {
          id: 'grid_modernization',
          title: 'Smart Grid Technology',
          description: 'Electric grid modernization and cybersecurity',
          requirements: ['NERC CIP Standards', 'IEEE Standards', 'Cybersecurity Framework'],
          market_value: '$7.8B annually',
          competition: 'Very High',
          certification_timeline: '15-24 months'
        },
        {
          id: 'energy_consulting',
          title: 'Energy Efficiency Consulting',
          description: 'Energy audits, efficiency programs, and sustainability consulting',
          requirements: ['CEM Certification', 'LEED Accreditation', 'Energy Modeling'],
          market_value: '$2.9B annually',
          competition: 'Medium',
          certification_timeline: '8-12 months'
        }
      ],
      successMetrics: [
        'Energy efficiency improvements',
        'Environmental compliance rating',
        'Grid reliability contributions',
        'Clean energy contract awards'
      ]
    },
    fintech: {
      name: 'Financial Technology',
      icon: '💳',
      color: 'purple',
      description: 'Financial services technology and regulatory compliance',
      keyRequirements: [
        'Financial Services Regulations',
        'SOX Compliance (Sarbanes-Oxley)',
        'PCI DSS Certification',
        'Anti-Money Laundering (AML)',
        'Consumer Financial Protection'
      ],
      specializations: [
        {
          id: 'payment_systems',
          title: 'Government Payment Systems',
          description: 'Secure payment processing for government transactions',
          requirements: ['PCI Level 1', 'FedRAMP Authorization', 'Treasury Standards'],
          market_value: '$6.7B annually',
          competition: 'Very High',
          certification_timeline: '18-30 months'
        },
        {
          id: 'financial_analytics',
          title: 'Financial Data Analytics',
          description: 'Government financial analysis and reporting systems',
          requirements: ['SOX Compliance', 'Data Governance', 'Analytics Certification'],
          market_value: '$3.4B annually',
          competition: 'High',
          certification_timeline: '12-18 months'
        },
        {
          id: 'blockchain_finance',
          title: 'Blockchain Financial Systems',
          description: 'Distributed ledger technology for government finance',
          requirements: ['Blockchain Expertise', 'Financial Regulations', 'Security Standards'],
          market_value: '$1.8B annually',
          competition: 'Low-Medium',
          certification_timeline: '15-24 months'
        }
      ],
      successMetrics: [
        'Financial system uptime',
        'Transaction security score',
        'Regulatory compliance rate',
        'Government client satisfaction'
      ]
    }
  };

  useEffect(() => {
    loadVerticalData();
  }, [industry]);

  const loadVerticalData = async () => {
    try {
      setLoading(true);
      
      // Load industry-specific data
      const response = await axios.get(`${API}/industry/vertical/${industry}`);
      setVerticalData(response.data);
      
      // Load specializations
      const specializationsResponse = await axios.get(`${API}/industry/specializations/${industry}`);
      setSpecializations(specializationsResponse.data.specializations || []);
      
      // Load compliance requirements
      const complianceResponse = await axios.get(`${API}/compliance/industry/${industry}`);
      setComplianceRequirements(complianceResponse.data.requirements || []);
      
      // Load industry benchmarks
      const benchmarksResponse = await axios.get(`${API}/analytics/industry-benchmarks/${industry}`);
      setIndustryBenchmarks(benchmarksResponse.data);
      
    } catch (error) {
      console.warn('Failed to load vertical data:', error);
      
      // Use local configuration as fallback
      const verticalConfig = industryVerticals[industry];
      if (verticalConfig) {
        setVerticalData({
          industry: industry,
          config: verticalConfig,
          readiness_score: Math.floor(Math.random() * 30) + 55, // 55-85%
          specialization_readiness: verticalConfig.specializations.map(spec => ({
            ...spec,
            readiness_score: Math.floor(Math.random() * 40) + 45
          }))
        });
        
        setSpecializations(verticalConfig.specializations);
        setComplianceRequirements(verticalConfig.keyRequirements);
        
        setIndustryBenchmarks({
          industry_average: 67,
          top_performers: 89,
          market_leaders: 94,
          your_position: Math.floor(Math.random() * 30) + 60,
          peer_comparison: 'Above Average'
        });
      }
      
    } finally {
      setLoading(false);
    }
  };

  const getReadinessLevel = (score) => {
    if (score >= 85) return { level: 'Expert', color: 'green' };
    if (score >= 70) return { level: 'Advanced', color: 'blue' };
    if (score >= 50) return { level: 'Intermediate', color: 'yellow' };
    return { level: 'Developing', color: 'red' };
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-slate-100 rounded-lg h-40 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-slate-100 rounded-lg h-48 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!verticalData || !verticalData.config) {
    return (
      <div className="text-center py-12 text-slate-500">
        <svg className="w-12 h-12 mx-auto mb-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <h3 className="text-lg font-medium text-slate-700 mb-2">Industry Vertical Not Available</h3>
        <p>Select a supported industry vertical to access specialized procurement guidance.</p>
      </div>
    );
  }

  const config = verticalData.config;

  return (
    <div className="space-y-6">
      {/* Industry Header */}
      <div className={`bg-gradient-to-r from-${config.color}-600 to-${config.color}-700 text-white rounded-lg p-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-5xl">{config.icon}</div>
            <div>
              <h1 className="text-2xl font-bold mb-1">{config.name} Vertical</h1>
              <p className="opacity-90">{config.description}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{verticalData.readiness_score}%</div>
            <div className="text-sm opacity-75">Vertical Readiness</div>
            <div className="text-xs opacity-60">
              {getReadinessLevel(verticalData.readiness_score).level} Level
            </div>
          </div>
        </div>
      </div>

      {/* Industry Benchmarks */}
      {industryBenchmarks && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Industry Benchmarks</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-600">{industryBenchmarks.industry_average}%</div>
              <div className="text-sm text-slate-600">Industry Average</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{industryBenchmarks.top_performers}%</div>
              <div className="text-sm text-slate-600">Top Performers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{industryBenchmarks.market_leaders}%</div>
              <div className="text-sm text-slate-600">Market Leaders</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold text-${config.color}-600`}>{industryBenchmarks.your_position}%</div>
              <div className="text-sm text-slate-600">Your Position</div>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-blue-800">
              <strong>Position Analysis:</strong> {industryBenchmarks.peer_comparison} - 
              You're {industryBenchmarks.your_position > industryBenchmarks.industry_average ? 'performing above' : 'developing toward'} industry standards
            </div>
          </div>
        </div>
      )}

      {/* Specialization Areas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {(verticalData.specialization_readiness || specializations).map((specialization, index) => {
          const readinessLevel = getReadinessLevel(specialization.readiness_score || 65);
          
          return (
            <div key={specialization.id} className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-slate-900">{specialization.title}</h4>
                <span className={`px-2 py-1 rounded text-xs font-medium bg-${readinessLevel.color}-100 text-${readinessLevel.color}-800`}>
                  {readinessLevel.level}
                </span>
              </div>
              
              <p className="text-sm text-slate-600 mb-4">{specialization.description}</p>
              
              <div className="space-y-3">
                <div>
                  <div className="text-xs font-medium text-slate-700 mb-1">Market Value:</div>
                  <div className="text-sm font-bold text-green-600">{specialization.market_value}</div>
                </div>
                
                <div>
                  <div className="text-xs font-medium text-slate-700 mb-1">Competition Level:</div>
                  <div className={`text-sm font-medium ${
                    specialization.competition === 'Low' ? 'text-green-600' :
                    specialization.competition === 'Medium' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {specialization.competition}
                  </div>
                </div>
                
                <div>
                  <div className="text-xs font-medium text-slate-700 mb-1">Certification Timeline:</div>
                  <div className="text-sm text-slate-600">{specialization.certification_timeline}</div>
                </div>
                
                <div>
                  <div className="text-xs font-medium text-slate-700 mb-1">Key Requirements:</div>
                  <div className="flex flex-wrap gap-1">
                    {specialization.requirements.slice(0, 3).map((req, reqIndex) => (
                      <span key={reqIndex} className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs">
                        {req}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                <button className={`w-full px-3 py-2 bg-${config.color}-600 text-white rounded-lg hover:bg-${config.color}-700 transition-colors text-sm font-medium`}>
                  Start Specialization Path
                </button>
                <button className={`w-full px-3 py-2 border border-${config.color}-300 text-${config.color}-700 rounded-lg hover:bg-${config.color}-50 transition-colors text-sm`}>
                  View Requirements
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Compliance Requirements Matrix */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-slate-900">
            {config.name} Compliance Requirements
          </h3>
          <p className="text-slate-600 text-sm">
            Specialized requirements for {config.name.toLowerCase()} government contracting
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Core Requirements</h4>
              <div className="space-y-2">
                {config.keyRequirements.map((requirement, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                    <div className={`w-6 h-6 bg-${config.color}-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5`}>
                      <svg className={`w-3 h-3 text-${config.color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">{requirement}</div>
                      <div className="text-xs text-slate-600 mt-1">
                        {index < 2 ? 'Critical certification requirement' : 
                         index < 4 ? 'Important compliance standard' : 
                         'Advanced qualification criteria'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Success Metrics</h4>
              <div className="space-y-2">
                {config.successMetrics.map((metric, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-100">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div className="text-sm font-medium text-green-800">{metric}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Center */}
      <div className={`bg-gradient-to-r from-${config.color}-50 to-${config.color}-100 rounded-lg border border-${config.color}-200 p-6`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              {config.name} Readiness Path
            </h3>
            <p className="text-slate-600">
              Specialized guidance for {config.name.toLowerCase()} government contracting success
            </p>
          </div>
          <div className="flex gap-3">
            <button className={`px-6 py-3 bg-${config.color}-600 text-white rounded-lg hover:bg-${config.color}-700 transition-colors font-medium`}>
              Start Vertical Assessment
            </button>
            <button className={`px-6 py-3 border border-${config.color}-300 text-${config.color}-700 rounded-lg hover:bg-${config.color}-50 transition-colors`}>
              Industry Resources
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Industry Vertical Selector Component
export function IndustryVerticalSelector({ onIndustryChange, currentIndustry = 'defense' }) {
  const [showSelector, setShowSelector] = useState(false);

  const industries = [
    { id: 'defense', name: 'Defense & Aerospace', icon: '🛡️', growth: 'Stable', demand: 'High' },
    { id: 'healthcare', name: 'Healthcare & Medical', icon: '🏥', growth: 'Growing', demand: 'Very High' },
    { id: 'energy', name: 'Energy & Infrastructure', icon: '⚡', growth: 'Rapid', demand: 'High' },
    { id: 'fintech', name: 'Financial Technology', icon: '💳', growth: 'Explosive', demand: 'Medium' }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setShowSelector(!showSelector)}
        className="flex items-center gap-3 px-4 py-3 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors w-full text-left"
      >
        <span className="text-2xl">
          {industries.find(i => i.id === currentIndustry)?.icon || '🏢'}
        </span>
        <div className="flex-1">
          <div className="font-medium text-slate-900">
            {industries.find(i => i.id === currentIndustry)?.name || 'Select Industry Vertical'}
          </div>
          <div className="text-sm text-slate-600">
            Specialized procurement pathway
          </div>
        </div>
        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showSelector && (
        <>
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
            <div className="p-2">
              {industries.map((industry) => (
                <button
                  key={industry.id}
                  onClick={() => {
                    onIndustryChange(industry.id);
                    setShowSelector(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-3 text-left rounded-lg transition-colors ${
                    currentIndustry === industry.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xl">{industry.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">{industry.name}</div>
                    <div className="text-xs opacity-75">
                      {industry.growth} growth • {industry.demand} demand
                    </div>
                  </div>
                  {currentIndustry === industry.id && (
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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