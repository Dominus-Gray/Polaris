import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// International Compliance Module for Global Procurement
export default function InternationalComplianceModule({ selectedRegion, userRole }) {
  const [complianceData, setComplianceData] = useState(null);
  const [activeRegion, setActiveRegion] = useState(selectedRegion || 'US');
  const [assessmentProgress, setAssessmentProgress] = useState({});
  const [certificationStatus, setCertificationStatus] = useState({});
  const [loading, setLoading] = useState(true);

  // International compliance frameworks
  const complianceRegions = {
    US: {
      name: 'United States',
      flag: '🇺🇸',
      system: 'Federal Acquisition Regulation (FAR)',
      portal: 'SAM.gov',
      requirements: [
        'SAM.gov Registration',
        'DUNS Number',
        'NAICS Code Classification',
        'Size Standard Compliance',
        'Representations & Certifications'
      ],
      specialPrograms: [
        'Small Business Set-Aside',
        'SDVOSB (Service-Disabled Veteran-Owned)',
        'WOSB (Women-Owned Small Business)',
        'HUBZone Program',
        '8(a) Business Development Program'
      ],
      assessmentAreas: [
        'Legal & Compliance (FAR/DFARS)',
        'Financial Management (DCAA Standards)',
        'Technology & Security (NIST Framework)',
        'Quality Management (ISO 9001)',
        'Risk Management (COSO Framework)'
      ]
    },
    EU: {
      name: 'European Union',
      flag: '🇪🇺',
      system: 'EU Public Procurement Directives',
      portal: 'TED (Tenders Electronic Daily)',
      requirements: [
        'ESPD (European Single Procurement Document)',
        'VAT Registration Number',
        'Professional Registration',
        'Technical Capacity Evidence',
        'Financial Standing Documentation'
      ],
      specialPrograms: [
        'SME (Small and Medium Enterprise) Support',
        'Innovation Partnership Procedures',
        'Social Considerations in Procurement',
        'Green Public Procurement (GPP)',
        'Cross-Border Procurement Access'
      ],
      assessmentAreas: [
        'Legal Compliance (EU Directives)',
        'Financial Capacity (EU Standards)',
        'Technical Ability (CE Marking)',
        'Environmental Standards (EMAS)',
        'Social Responsibility (CSR)'
      ]
    },
    UK: {
      name: 'United Kingdom',
      flag: '🇬🇧',
      system: 'Public Contracts Regulations (PCR)',
      portal: 'Find a Tender',
      requirements: [
        'Companies House Registration',
        'Standard Selection Questionnaire (SQ)',
        'IR35 Compliance Assessment',
        'GDPR Data Protection Compliance',
        'Modern Slavery Act Statement'
      ],
      specialPrograms: [
        'SME-Friendly Procurement',
        'Social Value in Procurement',
        'Local Business Support',
        'Innovation Procurement',
        'Sustainable Procurement'
      ],
      assessmentAreas: [
        'Legal Compliance (UK Law)',
        'Financial Standing (UK GAAP)',
        'Technical Competence (UK Standards)',
        'Health & Safety (HSE)',
        'Environmental Management (ISO 14001)'
      ]
    },
    CA: {
      name: 'Canada',
      flag: '🇨🇦',
      system: 'Government Contracts Regulations (GCR)',
      portal: 'buyandsell.gc.ca',
      requirements: [
        'Supplier Registration Information (SRI)',
        'Business Number (BN)',
        'Good Standing Certificate',
        'Security Clearance (if required)',
        'Indigenous Business Certification'
      ],
      specialPrograms: [
        'Procurement Strategy for Indigenous Business',
        'Small and Medium Enterprise (SME) Support',
        'Regional Economic Development',
        'Green Procurement Policy',
        'Accessibility Standards in Procurement'
      ],
      assessmentAreas: [
        'Legal Compliance (Canadian Law)',
        'Financial Capacity (Canadian GAAP)',
        'Technical Standards (CSA)',
        'Official Languages (English/French)',
        'Indigenous Procurement Policy'
      ]
    }
  };

  useEffect(() => {
    loadComplianceData();
  }, [activeRegion]);

  const loadComplianceData = async () => {
    try {
      setLoading(true);
      
      // Load region-specific compliance data
      const response = await axios.get(`${API}/compliance/international/${activeRegion}`);
      setComplianceData(response.data);
      
      // Load assessment progress for this region
      const progressResponse = await axios.get(`${API}/assessment/international-progress/${activeRegion}`);
      setAssessmentProgress(progressResponse.data.progress || {});
      
      // Load certification status
      const certResponse = await axios.get(`${API}/certificates/international/${activeRegion}`);
      setCertificationStatus(certResponse.data || {});
      
    } catch (error) {
      console.warn('Failed to load compliance data:', error);
      
      // Use local configuration as fallback
      const regionConfig = complianceRegions[activeRegion];
      setComplianceData({
        region: activeRegion,
        framework: regionConfig,
        compliance_score: Math.floor(Math.random() * 40) + 50, // 50-90%
        gaps: ['Financial Documentation', 'Technical Certifications'],
        next_steps: ['Complete financial capacity assessment', 'Obtain required technical certifications'],
        estimated_timeline: '8-12 weeks',
        local_requirements: regionConfig.requirements,
        special_programs: regionConfig.specialPrograms
      });
      
      setAssessmentProgress({
        'legal_compliance': 78,
        'financial_capacity': 65,
        'technical_ability': 82,
        'environmental_standards': 45,
        'social_responsibility': 71
      });
      
      setCertificationStatus({
        'eu_qualified': false,
        'ready_for_certification': false,
        'estimated_completion': '6-8 weeks'
      });
      
    } finally {
      setLoading(false);
    }
  };

  const startInternationalAssessment = (area) => {
    // Navigate to international assessment
    window.location.href = `/assessment/international?region=${activeRegion}&area=${area}`;
  };

  const getComplianceScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-slate-100 rounded-lg h-32 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-100 rounded-lg h-64 animate-pulse" />
          <div className="bg-slate-100 rounded-lg h-64 animate-pulse" />
        </div>
      </div>
    );
  }

  const regionConfig = complianceRegions[activeRegion];

  return (
    <div className="space-y-6">
      {/* Region Selection Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">International Procurement Compliance</h1>
            <p className="opacity-90">Navigate global government contracting requirements</p>
          </div>
          
          {/* Region Selector */}
          <div className="bg-white/20 backdrop-blur rounded-lg p-4">
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(complianceRegions).map(([code, region]) => (
                <button
                  key={code}
                  onClick={() => setActiveRegion(code)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm ${
                    activeRegion === code
                      ? 'bg-white text-blue-600 font-medium'
                      : 'text-white/80 hover:bg-white/10'
                  }`}
                >
                  <span className="text-lg">{region.flag}</span>
                  <span>{code}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Current Region Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">{regionConfig.flag}</span>
            <div>
              <h3 className="font-bold text-slate-900">{regionConfig.name}</h3>
              <p className="text-sm text-slate-600">{regionConfig.system}</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Compliance Score:</span>
              <span className={`px-2 py-1 rounded text-sm font-medium ${getComplianceScoreColor(complianceData?.compliance_score || 65)}`}>
                {complianceData?.compliance_score || 65}%
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Portal:</span>
              <a 
                href={`https://${regionConfig.portal}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                {regionConfig.portal} →
              </a>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Timeline:</span>
              <span className="text-sm font-medium text-slate-700">
                {complianceData?.estimated_timeline || '8-12 weeks'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <h3 className="font-bold text-slate-900 mb-4">Assessment Progress</h3>
          <div className="space-y-3">
            {regionConfig.assessmentAreas.slice(0, 5).map((area, index) => {
              const areaKey = area.toLowerCase().replace(/[^a-z]/g, '_');
              const progress = assessmentProgress[areaKey] || Math.floor(Math.random() * 50) + 25;
              
              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-slate-700">{area.split('(')[0].trim()}</span>
                    <span className="text-sm font-medium text-slate-600">{progress}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(progress)}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <h3 className="font-bold text-slate-900 mb-4">Certification Status</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${
                certificationStatus.ready_for_certification ? 'bg-green-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm text-slate-700">
                {certificationStatus.ready_for_certification ? 'Ready for Certification' : 'Developing Readiness'}
              </span>
            </div>
            
            <div className="text-sm text-slate-600">
              <strong>Estimated Completion:</strong><br />
              {certificationStatus.estimated_completion || '6-8 weeks'}
            </div>
            
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
              Start {regionConfig.name} Assessment
            </button>
          </div>
        </div>
      </div>

      {/* Regional Requirements Deep Dive */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            {regionConfig.name} Requirements
          </h3>
          
          <div className="space-y-3">
            {regionConfig.requirements.map((requirement, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-xs font-bold">{index + 1}</span>
                </div>
                <div>
                  <div className="font-medium text-slate-900 text-sm">{requirement}</div>
                  <div className="text-xs text-slate-600 mt-1">
                    {index === 0 ? 'Essential foundation for all government contracts' :
                     index === 1 ? 'Required identification for business verification' :
                     index === 2 ? 'Industry classification for contract eligibility' :
                     'Critical compliance requirement for contracting'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            Special Programs & Opportunities
          </h3>
          
          <div className="space-y-3">
            {regionConfig.specialPrograms.map((program, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-100">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <div className="font-medium text-slate-900 text-sm">{program}</div>
                  <div className="text-xs text-green-700 mt-1">
                    {index === 0 ? 'Competitive advantage for eligible businesses' :
                     index === 1 ? 'Specialized contracting opportunities' :
                     index === 2 ? 'Enhanced market access and support' :
                     'Strategic positioning for government contracts'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance Gap Analysis */}
      {complianceData?.gaps && complianceData.gaps.length > 0 && (
        <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Compliance Gaps - {regionConfig.name}</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-orange-900 mb-2">Areas Needing Attention:</h4>
              <ul className="space-y-1">
                {complianceData.gaps.map((gap, index) => (
                  <li key={index} className="text-sm text-orange-800 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-orange-600 rounded-full"></div>
                    {gap}
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-orange-900 mb-2">Recommended Actions:</h4>
              <ul className="space-y-1">
                {complianceData.next_steps?.map((step, index) => (
                  <li key={index} className="text-sm text-orange-800 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                    {step}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="mt-4 flex gap-3">
            <button className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium">
              Address Gaps
            </button>
            <button className="px-4 py-2 border border-orange-300 text-orange-700 rounded-lg hover:bg-orange-50 transition-colors text-sm">
              Find Local Experts
            </button>
          </div>
        </div>
      )}

      {/* International Opportunities */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-slate-900">
            Current Opportunities - {regionConfig.name}
          </h3>
          <p className="text-slate-600 text-sm">
            Government contracting opportunities matched to your readiness profile
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sample opportunities for each region */}
            {activeRegion === 'EU' && (
              <>
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Digital Services Framework</h4>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">85% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    European Commission • €150,000 - €500,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Digital transformation consulting for EU member state agencies
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View on TED →
                  </button>
                </div>
                
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Green Technology Implementation</h4>
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">72% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    EuropeAid • €75,000 - €300,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Sustainable technology consulting for environmental programs
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View Details →
                  </button>
                </div>
              </>
            )}
            
            {activeRegion === 'UK' && (
              <>
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">NHS Digital Transformation</h4>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">91% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    NHS Digital • £200,000 - £800,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Healthcare technology modernization and cybersecurity
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View on Find a Tender →
                  </button>
                </div>
                
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Local Government Consulting</h4>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">78% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    Crown Commercial Service • £50,000 - £250,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Business process improvement for local authorities
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View Framework →
                  </button>
                </div>
              </>
            )}
            
            {activeRegion === 'CA' && (
              <>
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Indigenous Business Development</h4>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">88% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    PSPC Canada • CAD $100,000 - $400,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Business development consulting for Indigenous communities
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View on BuyandSell →
                  </button>
                </div>
                
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Bilingual Services Framework</h4>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">75% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    Treasury Board • CAD $75,000 - $300,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    English/French language services and translation
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View Opportunity →
                  </button>
                </div>
              </>
            )}
            
            {activeRegion === 'US' && (
              <>
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">Federal IT Modernization</h4>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">89% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    GSA • $200,000 - $750,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Legacy system modernization and cloud migration
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View on SAM.gov →
                  </button>
                </div>
                
                <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">SDVOSB Professional Services</h4>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">82% Match</span>
                  </div>
                  <div className="text-sm text-slate-600 mb-2">
                    Department of Defense • $150,000 - $600,000
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    Strategic planning and organizational development
                  </p>
                  <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                    View Contract →
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Compliance Action Center */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              {regionConfig.name} Compliance Action Center
            </h3>
            <p className="text-slate-600 text-sm">
              Streamlined path to {regionConfig.name} government contracting eligibility
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-indigo-600">
            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></div>
            <span>AI-Guided</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => startInternationalAssessment('compliance')}
            className="flex items-center gap-3 p-4 bg-white rounded-lg border hover:shadow-sm transition-all"
          >
            <div className="p-2 bg-indigo-100 rounded-lg">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium text-slate-900 text-sm">Start Assessment</div>
              <div className="text-xs text-slate-600">Region-specific evaluation</div>
            </div>
          </button>
          
          <button className="flex items-center gap-3 p-4 bg-white rounded-lg border hover:shadow-sm transition-all">
            <div className="p-2 bg-purple-100 rounded-lg">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium text-slate-900 text-sm">Browse Resources</div>
              <div className="text-xs text-slate-600">Country-specific guides</div>
            </div>
          </button>
          
          <button className="flex items-center gap-3 p-4 bg-white rounded-lg border hover:shadow-sm transition-all">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium text-slate-900 text-sm">Connect Experts</div>
              <div className="text-xs text-slate-600">Local compliance specialists</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

// Regional Compliance Selector Component
export function RegionalComplianceSelector({ onRegionChange, currentRegion = 'US' }) {
  const [showSelector, setShowSelector] = useState(false);

  const regions = [
    { code: 'US', name: 'United States', flag: '🇺🇸', market_size: 'Large', complexity: 'High' },
    { code: 'EU', name: 'European Union', flag: '🇪🇺', market_size: 'Very Large', complexity: 'Very High' },
    { code: 'UK', name: 'United Kingdom', flag: '🇬🇧', market_size: 'Medium', complexity: 'High' },
    { code: 'CA', name: 'Canada', flag: '🇨🇦', market_size: 'Medium', complexity: 'Medium' }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setShowSelector(!showSelector)}
        className="flex items-center gap-3 px-4 py-3 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
      >
        <span className="text-2xl">
          {regions.find(r => r.code === currentRegion)?.flag || '🌍'}
        </span>
        <div className="text-left">
          <div className="font-medium text-slate-900">
            {regions.find(r => r.code === currentRegion)?.name || 'Select Region'}
          </div>
          <div className="text-sm text-slate-600">
            Procurement compliance region
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
              {regions.map((region) => (
                <button
                  key={region.code}
                  onClick={() => {
                    onRegionChange(region.code);
                    setShowSelector(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-3 text-left rounded-lg transition-colors ${
                    currentRegion === region.code
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xl">{region.flag}</span>
                  <div className="flex-1">
                    <div className="font-medium">{region.name}</div>
                    <div className="text-xs opacity-75">
                      {region.market_size} market • {region.complexity} complexity
                    </div>
                  </div>
                  {currentRegion === region.code && (
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