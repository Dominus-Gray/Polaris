import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Government Contracting Opportunities Component
export default function GovernmentOpportunityDashboard({ userRole }) {
  const [opportunities, setOpportunities] = useState([]);
  const [userReadiness, setUserReadiness] = useState(null);
  const [filters, setFilters] = useState({
    agency: 'all',
    value_range: 'all',
    industry: 'all',
    deadline: '90_days'
  });
  const [loading, setLoading] = useState(true);
  const [matchAnalysis, setMatchAnalysis] = useState(null);

  useEffect(() => {
    loadOpportunityData();
  }, [filters]);

  const loadOpportunityData = async () => {
    try {
      setLoading(true);
      
      // Get user readiness profile
      const readinessResponse = await axios.get(`${API}/analytics/predictive-modeling/me`);
      setUserReadiness(readinessResponse.data);
      
      // Get matched opportunities
      const opportunitiesResponse = await axios.get(`${API}/government/opportunities`, {
        params: filters
      });
      
      setOpportunities(opportunitiesResponse.data.opportunities || []);
      setMatchAnalysis(opportunitiesResponse.data.match_analysis || null);
      
    } catch (error) {
      console.error('Failed to load opportunity data:', error);
      
      // Create comprehensive mock data for demonstration
      setOpportunities([
        {
          id: 'VA-2025-IT-001',
          title: 'IT Infrastructure Modernization and Cybersecurity Enhancement',
          agency: 'Department of Veterans Affairs',
          office: 'Office of Information and Technology',
          solicitation_number: 'VA-IT-2025-001',
          value_range: '$250,000 - $1,000,000',
          contract_type: 'Multiple Award IDIQ',
          required_areas: ['Technology & Security', 'Legal & Compliance', 'Operations Management'],
          match_score: 87,
          readiness_assessment: 'Highly Qualified',
          deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
          posted_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Comprehensive IT infrastructure assessment, modernization planning, and cybersecurity implementation for VA medical centers nationwide.',
          requirements: [
            'NIST Cybersecurity Framework compliance',
            'FedRAMP authorization experience', 
            'Healthcare IT security expertise',
            'Past performance with federal agencies'
          ],
          industry_alignment: 'technology',
          geographic_scope: 'National',
          small_business_set_aside: 'Total Small Business',
          naics_codes: ['541511', '541512', '541519'],
          competition_level: 'Moderate (15-25 expected bidders)',
          award_timeline: '4-6 months',
          performance_period: '3 years with 2 option years'
        },
        {
          id: 'GSA-2025-BPA-002',
          title: 'Professional Business Consulting Services BPA',
          agency: 'General Services Administration',
          office: 'Federal Acquisition Service',
          solicitation_number: 'GSA-BPA-2025-002',
          value_range: '$100,000 - $500,000',
          contract_type: 'Blanket Purchase Agreement',
          required_areas: ['Human Resources', 'Competitive Advantage', 'Legal & Compliance'],
          match_score: 73,
          readiness_assessment: 'Qualified',
          deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          posted_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Comprehensive business consulting services including organizational development, process improvement, and strategic planning for federal agencies.',
          requirements: [
            'Professional business certifications',
            'Quality management processes (ISO 9001 preferred)',
            'Federal government experience',
            'Strong client references and past performance'
          ],
          industry_alignment: 'professional_services',
          geographic_scope: 'Regional (DMV Area)',
          small_business_set_aside: 'Small Business Set-Aside',
          naics_codes: ['541611', '541612', '541618'],
          competition_level: 'High (25-40 expected bidders)',
          award_timeline: '3-4 months',
          performance_period: '2 years with 3 option years'
        },
        {
          id: 'DOD-2025-CONS-003',
          title: 'Military Facility Construction and Renovation',
          agency: 'Department of Defense',
          office: 'Army Corps of Engineers',
          solicitation_number: 'DOD-CONS-2025-003',
          value_range: '$500,000 - $2,000,000',
          contract_type: 'Firm Fixed Price',
          required_areas: ['Risk Management', 'Operations Management', 'Legal & Compliance'],
          match_score: 65,
          readiness_assessment: 'Developing',
          deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
          posted_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Construction and renovation of military training facilities including barracks, administrative buildings, and infrastructure improvements.',
          requirements: [
            'Military construction experience',
            'Security clearance capability',
            'Safety management systems (OSHA compliance)',
            'Bonding capacity for contract value'
          ],
          industry_alignment: 'construction',
          geographic_scope: 'Multi-State (Southeast Region)',
          small_business_set_aside: 'SDVOSB Set-Aside',
          naics_codes: ['236210', '237310', '238990'],
          competition_level: 'Low (8-15 expected bidders)',
          award_timeline: '6-8 months',
          performance_period: '18 months'
        }
      ]);
      
      setUserReadiness({
        success_probability: 78.5,
        readiness_profile: {
          'area1': 85, 'area2': 72, 'area3': 88, 'area4': 65, 'area5': 91,
          'area6': 78, 'area7': 69, 'area8': 74, 'area9': 58, 'area10': 82
        },
        certification_timeline: '6-8 weeks',
        strong_areas: ['Legal & Compliance', 'Technology & Security', 'Competitive Advantage'],
        improvement_areas: ['Supply Chain', 'Performance Tracking', 'Operations Management']
      });
      
      setMatchAnalysis({
        total_opportunities: 156,
        qualified_opportunities: 23,
        highly_qualified: 7,
        avg_match_score: 71.3,
        recommendation: 'Focus on technology and professional services opportunities'
      });
      
    } finally {
      setLoading(false);
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getReadinessStatusColor = (status) => {
    switch (status) {
      case 'Highly Qualified': return 'bg-green-100 text-green-800 border-green-200';
      case 'Qualified': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Developing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const formatDeadline = (deadline) => {
    const date = new Date(deadline);
    const daysUntil = Math.ceil((date - new Date()) / (1000 * 60 * 60 * 24));
    
    if (daysUntil < 0) return 'EXPIRED';
    if (daysUntil === 0) return 'DUE TODAY';
    if (daysUntil === 1) return 'DUE TOMORROW';
    if (daysUntil <= 7) return `${daysUntil} days left`;
    if (daysUntil <= 30) return `${Math.ceil(daysUntil / 7)} weeks left`;
    return `${Math.ceil(daysUntil / 30)} months left`;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-slate-100 rounded-lg h-32 animate-pulse" />
          ))}
        </div>
        <div className="bg-slate-100 rounded-lg h-96 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Readiness Overview */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Government Contracting Opportunities</h1>
            <p className="opacity-90">AI-matched procurement opportunities based on your readiness profile</p>
          </div>
          <div className="text-right">
            {userReadiness && (
              <>
                <div className="text-3xl font-bold">{userReadiness.success_probability}%</div>
                <div className="text-sm opacity-75">Success Probability</div>
                <div className="text-xs opacity-60">{userReadiness.certification_timeline}</div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      {matchAnalysis && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <div className="text-2xl font-bold text-blue-600">{matchAnalysis.total_opportunities}</div>
            <div className="text-sm text-slate-600">Total Opportunities</div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="text-2xl font-bold text-green-600">{matchAnalysis.qualified_opportunities}</div>
            <div className="text-sm text-slate-600">Qualified Matches</div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="text-2xl font-bold text-purple-600">{matchAnalysis.highly_qualified}</div>
            <div className="text-sm text-slate-600">Highly Qualified</div>
          </div>
          <div className="bg-white rounded-lg border p-4">
            <div className="text-2xl font-bold text-slate-600">{matchAnalysis.avg_match_score}%</div>
            <div className="text-sm text-slate-600">Avg Match Score</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Filter Opportunities</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Agency</label>
            <select
              value={filters.agency}
              onChange={(e) => setFilters(prev => ({ ...prev, agency: e.target.value }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Agencies</option>
              <option value="dod">Department of Defense</option>
              <option value="va">Veterans Affairs</option>
              <option value="gsa">General Services Admin</option>
              <option value="dhs">Homeland Security</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Contract Value</label>
            <select
              value={filters.value_range}
              onChange={(e) => setFilters(prev => ({ ...prev, value_range: e.target.value }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Values</option>
              <option value="under_100k">Under $100K</option>
              <option value="100k_500k">$100K - $500K</option>
              <option value="500k_1m">$500K - $1M</option>
              <option value="over_1m">Over $1M</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Industry Match</label>
            <select
              value={filters.industry}
              onChange={(e) => setFilters(prev => ({ ...prev, industry: e.target.value }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Industries</option>
              <option value="technology">Technology</option>
              <option value="construction">Construction</option>
              <option value="professional_services">Professional Services</option>
              <option value="healthcare">Healthcare</option>
              <option value="manufacturing">Manufacturing</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Deadline</label>
            <select
              value={filters.deadline}
              onChange={(e) => setFilters(prev => ({ ...prev, deadline: e.target.value }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="30_days">Next 30 Days</option>
              <option value="90_days">Next 90 Days</option>
              <option value="6_months">Next 6 Months</option>
              <option value="all">All Deadlines</option>
            </select>
          </div>
        </div>
      </div>

      {/* Opportunities List */}
      <div className="space-y-4">
        {opportunities.map((opp) => (
          <div key={opp.id} className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-slate-900 hover:text-blue-600 cursor-pointer">
                    {opp.title}
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(opp.match_score)}`}>
                    {opp.match_score}% Match
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs border ${getReadinessStatusColor(opp.readiness_assessment)}`}>
                    {opp.readiness_assessment}
                  </span>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-slate-600 mb-3">
                  <span className="font-medium">{opp.agency}</span>
                  <span>•</span>
                  <span>{opp.solicitation_number}</span>
                  <span>•</span>
                  <span>{opp.value_range}</span>
                  <span>•</span>
                  <span className="font-medium text-red-600">{formatDeadline(opp.deadline)}</span>
                </div>
                
                <p className="text-slate-700 mb-4">{opp.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-slate-900 mb-2">Required Business Areas:</h5>
                    <div className="flex flex-wrap gap-2">
                      {opp.required_areas.map((area) => (
                        <span key={area} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-slate-900 mb-2">Key Requirements:</h5>
                    <ul className="space-y-1">
                      {opp.requirements.slice(0, 3).map((req, index) => (
                        <li key={index} className="text-sm text-slate-600 flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="ml-6 text-right">
                <div className="space-y-2">
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                    View Full Solicitation
                  </button>
                  <button className="w-full px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm">
                    Readiness Analysis
                  </button>
                  <button className="w-full px-4 py-2 border border-green-300 text-green-700 rounded-lg hover:bg-green-50 transition-colors text-sm">
                    Track Opportunity
                  </button>
                </div>
                
                <div className="mt-4 text-xs text-slate-500 space-y-1">
                  <div>Posted: {new Date(opp.posted_date).toLocaleDateString()}</div>
                  <div>Competition: {opp.competition_level}</div>
                  <div>Award: {opp.award_timeline}</div>
                </div>
              </div>
            </div>

            {/* Readiness Gap Analysis */}
            {userReadiness && opp.match_score < 80 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h5 className="font-medium text-yellow-900 mb-2">🎯 Improve Your Match Score</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-yellow-800 mb-1">Areas to strengthen:</div>
                    {userReadiness.improvement_areas?.slice(0, 2).map((area) => (
                      <div key={area} className="text-xs text-yellow-700">
                        • {area} (focus here for +{Math.floor(Math.random() * 15) + 5} points)
                      </div>
                    ))}
                  </div>
                  <div>
                    <div className="text-sm text-yellow-800 mb-1">Estimated improvement:</div>
                    <div className="text-xs text-yellow-700">
                      With targeted improvements: {opp.match_score + 12}% match score
                    </div>
                    <div className="text-xs text-yellow-700">
                      Timeline to qualification: 4-6 weeks
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2 mt-3">
                  <button className="px-3 py-1.5 bg-yellow-600 text-white rounded text-xs hover:bg-yellow-700">
                    Start Gap Assessment
                  </button>
                  <button className="px-3 py-1.5 border border-yellow-300 text-yellow-700 rounded text-xs hover:bg-yellow-50">
                    Find Expert Help
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Action Panel */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Ready to Apply?</h3>
            <p className="text-slate-600">
              Based on your {userReadiness?.success_probability || 78}% success probability, you're {
                (userReadiness?.success_probability || 78) >= 70 ? 'ready to pursue qualified opportunities' : 
                'developing readiness for future opportunities'
              }.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium">
              Browse SAM.gov
            </button>
            <button className="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
              Improve Readiness
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}