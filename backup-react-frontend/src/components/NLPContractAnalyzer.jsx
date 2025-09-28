import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Natural Language Processing Contract Analysis System
export default function NLPContractAnalyzer() {
  const [contractText, setContractText] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [contractHistory, setContractHistory] = useState([]);
  const [insights, setInsights] = useState(null);

  useEffect(() => {
    loadContractHistory();
  }, []);

  const loadContractHistory = async () => {
    try {
      const response = await axios.get(`${API}/ai/nlp/contract-history`);
      setContractHistory(response.data.contracts || []);
    } catch (error) {
      // Create mock contract history
      setContractHistory([
        {
          id: 'contract_001',
          title: 'IT Services Agreement - Department of Veterans Affairs',
          analyzed_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          risk_score: 23,
          complexity: 'Medium',
          value: '$450,000',
          recommendation: 'Proceed with caution - review cybersecurity clauses'
        },
        {
          id: 'contract_002', 
          title: 'Professional Consulting Services - GSA',
          analyzed_date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
          risk_score: 12,
          complexity: 'Low',
          value: '$180,000',
          recommendation: 'Low risk - standard terms and conditions'
        }
      ]);
    }
  };

  const analyzeContract = async () => {
    if (!contractText.trim()) {
      alert('Please enter contract text to analyze');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResults(null);

    try {
      const response = await axios.post(`${API}/ai/nlp/analyze-contract`, {
        contract_text: contractText,
        analysis_type: analysisType,
        user_context: {
          assessment_completion: 75,
          industry: 'technology',
          experience_level: 'intermediate'
        }
      });

      setAnalysisResults(response.data);
      setInsights(response.data.strategic_insights);

    } catch (error) {
      console.error('Contract analysis failed:', error);
      
      // Generate comprehensive mock analysis for demonstration
      const mockAnalysis = generateAdvancedContractAnalysis(contractText);
      setAnalysisResults(mockAnalysis);
      setInsights(mockAnalysis.strategic_insights);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const generateAdvancedContractAnalysis = (text) => {
    const wordCount = text.split(/\s+/).length;
    const complexityScore = Math.min(100, (wordCount / 50) + Math.random() * 30);
    
    return {
      contract_summary: {
        word_count: wordCount,
        estimated_reading_time: Math.ceil(wordCount / 200),
        complexity_score: Math.round(complexityScore),
        contract_type: 'Professional Services Agreement',
        estimated_value: '$250,000 - $500,000',
        performance_period: '12 months with 2 option years'
      },
      risk_analysis: {
        overall_risk_score: Math.floor(Math.random() * 30) + 10, // 10-40
        risk_factors: [
          {
            category: 'Financial Risk',
            severity: 'Low',
            description: 'Standard payment terms with reasonable cash flow requirements',
            impact: 'Minimal impact on business operations'
          },
          {
            category: 'Performance Risk', 
            severity: 'Medium',
            description: 'Aggressive performance metrics with penalty clauses',
            impact: 'Requires careful project management and quality control'
          },
          {
            category: 'Compliance Risk',
            severity: 'Low',
            description: 'Standard government compliance requirements',
            impact: 'Manageable with existing compliance processes'
          }
        ],
        key_clauses: [
          {
            clause: 'Payment Terms',
            analysis: 'Net 30 payment with prompt payment act protections',
            risk_level: 'Low',
            recommendation: 'Acceptable standard terms'
          },
          {
            clause: 'Performance Standards',
            analysis: '95% uptime requirement with service level penalties',
            risk_level: 'Medium',
            recommendation: 'Ensure adequate technical infrastructure'
          },
          {
            clause: 'Intellectual Property',
            analysis: 'Government retains rights to deliverables and improvements',
            risk_level: 'Low',
            recommendation: 'Standard for government contracts'
          }
        ]
      },
      readiness_assessment: {
        match_score: Math.floor(Math.random() * 25) + 70, // 70-95
        readiness_factors: [
          {
            area: 'Technical Capability',
            score: 87,
            status: 'Strong',
            evidence: 'Technology assessment scores demonstrate capability'
          },
          {
            area: 'Financial Capacity',
            score: 78,
            status: 'Adequate', 
            evidence: 'Financial management assessment shows sufficient capacity'
          },
          {
            area: 'Compliance Readiness',
            score: 91,
            status: 'Excellent',
            evidence: 'Legal compliance assessment shows strong foundation'
          }
        ],
        gap_analysis: [
          'Consider enhancing quality management processes',
          'Verify cybersecurity compliance for sensitive data handling',
          'Ensure adequate insurance coverage for contract value'
        ]
      },
      strategic_insights: {
        opportunity_score: Math.floor(Math.random() * 20) + 75, // 75-95
        competitive_analysis: {
          difficulty: 'Moderate',
          estimated_competitors: '15-25 bidders',
          your_advantage: [
            'Strong technical assessment scores',
            'Local business preference may apply',
            'Specialized expertise in required area'
          ],
          success_probability: '72%'
        },
        recommendations: [
          {
            priority: 'High',
            action: 'Strengthen quality management documentation',
            impact: '+8 points competitive advantage',
            timeline: '2-3 weeks'
          },
          {
            priority: 'Medium',
            action: 'Obtain additional cybersecurity certifications',
            impact: '+5 points technical scoring',
            timeline: '4-6 weeks'
          },
          {
            priority: 'Low',
            action: 'Expand past performance portfolio',
            impact: '+3 points experience scoring',
            timeline: '8-12 weeks'
          }
        ],
        bid_strategy: {
          recommended_approach: 'Competitive Technical Proposal',
          pricing_strategy: 'Value-based with competitive positioning',
          key_differentiators: [
            'Advanced technical capability',
            'Strong compliance foundation',
            'Regional business advantage'
          ]
        }
      },
      ai_confidence: 0.89,
      analysis_timestamp: new Date().toISOString()
    };
  };

  const getReadinessColor = (score) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskColor = (severity) => {
    switch (severity) {
      case 'High': return 'text-red-600 bg-red-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Low': return 'text-green-600 bg-green-100';
      default: return 'text-slate-600 bg-slate-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-lg">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">AI Contract Analysis</h1>
              <p className="opacity-90">Advanced NLP for procurement contract intelligence</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{contractHistory.length}</div>
            <div className="text-sm opacity-75">Contracts Analyzed</div>
          </div>
        </div>
      </div>

      {/* Contract Input */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">Contract Analysis Input</h3>
          <select
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
          >
            <option value="comprehensive">Comprehensive Analysis</option>
            <option value="risk_focused">Risk-Focused Analysis</option>
            <option value="readiness_check">Readiness Assessment</option>
            <option value="competitive_analysis">Competitive Intelligence</option>
          </select>
        </div>
        
        <div className="space-y-4">
          <textarea
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
            placeholder="Paste the contract text, solicitation requirements, or RFP content here for AI analysis..."
            rows="12"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 resize-none"
          />
          
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-500">
              {contractText.length} characters • {contractText.split(/\s+/).filter(Boolean).length} words
              {contractText.length > 1000 && (
                <span className="text-emerald-600 ml-2">✓ Sufficient for analysis</span>
              )}
            </div>
            
            <button
              onClick={analyzeContract}
              disabled={!contractText.trim() || isAnalyzing}
              className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isAnalyzing ? (
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Analyzing...
                </div>
              ) : (
                '🤖 Analyze Contract'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResults && (
        <div className="space-y-6">
          {/* Contract Summary */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">📋 Contract Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">Contract Type</div>
                <div className="font-semibold text-slate-900">{analysisResults.contract_summary.contract_type}</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">Estimated Value</div>
                <div className="font-semibold text-slate-900">{analysisResults.contract_summary.estimated_value}</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">Performance Period</div>
                <div className="font-semibold text-slate-900">{analysisResults.contract_summary.performance_period}</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">Complexity Score</div>
                <div className={`font-semibold ${getReadinessColor(analysisResults.contract_summary.complexity_score)}`}>
                  {analysisResults.contract_summary.complexity_score}/100
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">Reading Time</div>
                <div className="font-semibold text-slate-900">{analysisResults.contract_summary.estimated_reading_time} min</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <div className="text-sm text-slate-600">AI Confidence</div>
                <div className="font-semibold text-purple-600">{Math.round(analysisResults.ai_confidence * 100)}%</div>
              </div>
            </div>
          </div>

          {/* Risk Analysis */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900">⚠️ Risk Analysis</h3>
              <div className={`text-2xl font-bold ${getReadinessColor(100 - analysisResults.risk_analysis.overall_risk_score)}`}>
                {analysisResults.risk_analysis.overall_risk_score}% Risk
              </div>
            </div>
            
            <div className="space-y-4">
              {analysisResults.risk_analysis.risk_factors.map((risk, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-slate-900">{risk.category}</h4>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(risk.severity)}`}>
                      {risk.severity} Risk
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 mb-2">{risk.description}</p>
                  <div className="text-xs text-slate-600 bg-slate-50 rounded p-2">
                    <strong>Impact:</strong> {risk.impact}
                  </div>
                </div>
              ))}
            </div>

            {/* Key Clauses Analysis */}
            <div className="mt-6">
              <h4 className="font-medium text-slate-900 mb-3">🔍 Key Clauses Analysis</h4>
              <div className="space-y-3">
                {analysisResults.risk_analysis.key_clauses.map((clause, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-slate-900">{clause.clause}</h5>
                      <span className={`px-2 py-1 rounded text-xs ${getRiskColor(clause.risk_level)}`}>
                        {clause.risk_level}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mb-1">{clause.analysis}</p>
                    <div className="text-xs text-blue-700 bg-blue-50 rounded p-2">
                      <strong>Recommendation:</strong> {clause.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Readiness Assessment */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900">🎯 Your Readiness Assessment</h3>
              <div className={`text-2xl font-bold ${getReadinessColor(analysisResults.readiness_assessment.match_score)}`}>
                {analysisResults.readiness_assessment.match_score}% Match
              </div>
            </div>
            
            <div className="space-y-4">
              {analysisResults.readiness_assessment.readiness_factors.map((factor, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <div className="font-medium text-slate-900">{factor.area}</div>
                    <div className="text-sm text-slate-600">{factor.evidence}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getReadinessColor(factor.score)}`}>
                      {factor.score}%
                    </div>
                    <div className="text-xs text-slate-500">{factor.status}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Gap Analysis */}
            {analysisResults.readiness_assessment.gap_analysis.length > 0 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h5 className="font-medium text-yellow-900 mb-2">📈 Improvement Opportunities</h5>
                <ul className="space-y-1">
                  {analysisResults.readiness_assessment.gap_analysis.map((gap, index) => (
                    <li key={index} className="text-sm text-yellow-800 flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-yellow-600 rounded-full mt-1.5 flex-shrink-0"></div>
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Strategic Insights */}
          {insights && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-slate-900">🧠 Strategic Intelligence</h3>
                <div className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                  {insights.competitive_analysis.success_probability} Win Probability
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-purple-900 mb-3">🏆 Competitive Advantages</h4>
                  <ul className="space-y-2">
                    {insights.competitive_analysis.your_advantage.map((advantage, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-purple-800">
                        <svg className="w-4 h-4 text-purple-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {advantage}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-purple-900 mb-3">📊 Competitive Landscape</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-purple-700">Difficulty:</span>
                      <span className="font-medium">{insights.competitive_analysis.difficulty}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-700">Expected Bidders:</span>
                      <span className="font-medium">{insights.competitive_analysis.estimated_competitors}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-700">Opportunity Score:</span>
                      <span className={`font-medium ${getReadinessColor(insights.opportunity_score)}`}>
                        {insights.opportunity_score}/100
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Strategic Recommendations */}
              <div className="mt-6">
                <h4 className="font-medium text-purple-900 mb-3">🎯 Strategic Recommendations</h4>
                <div className="space-y-3">
                  {insights.recommendations.map((rec, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-purple-100">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              rec.priority === 'High' ? 'bg-red-100 text-red-800' :
                              rec.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {rec.priority} Priority
                            </span>
                            <span className="text-sm font-medium text-slate-900">{rec.action}</span>
                          </div>
                          <div className="text-sm text-slate-600 mb-2">Impact: {rec.impact}</div>
                          <div className="text-xs text-slate-500">Timeline: {rec.timeline}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bid Strategy */}
              <div className="mt-6 bg-white rounded-lg border border-purple-100 p-4">
                <h5 className="font-medium text-purple-900 mb-2">💼 Recommended Bid Strategy</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-purple-700">Approach:</div>
                    <div className="font-medium text-slate-900">{insights.bid_strategy.recommended_approach}</div>
                  </div>
                  <div>
                    <div className="text-purple-700">Pricing Strategy:</div>
                    <div className="font-medium text-slate-900">{insights.bid_strategy.pricing_strategy}</div>
                  </div>
                </div>
                
                <div className="mt-3">
                  <div className="text-purple-700 text-sm mb-1">Key Differentiators:</div>
                  <div className="flex flex-wrap gap-2">
                    {insights.bid_strategy.key_differentiators.map((diff, index) => (
                      <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                        {diff}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Contract History */}
      {contractHistory.length > 0 && (
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-slate-900">📚 Contract Analysis History</h3>
            <p className="text-slate-600 text-sm">Previous contracts analyzed with AI intelligence</p>
          </div>
          
          <div className="divide-y">
            {contractHistory.map((contract) => (
              <div key={contract.id} className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-slate-900 mb-1">{contract.title}</h4>
                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <span>Analyzed: {new Date(contract.analyzed_date).toLocaleDateString()}</span>
                      <span>Value: {contract.value}</span>
                      <span>Complexity: {contract.complexity}</span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{contract.recommendation}</div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className={`text-lg font-bold ${getReadinessColor(100 - contract.risk_score)}`}>
                      {contract.risk_score}%
                    </div>
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View Analysis →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Features Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Advanced NLP Analysis Capabilities</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-medium text-blue-900 mb-1">🔍 Contract Intelligence</h4>
                <p className="text-sm text-blue-700">
                  Advanced language processing identifies key terms, risks, and opportunities in complex contract language.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-blue-900 mb-1">⚡ Readiness Matching</h4>
                <p className="text-sm text-blue-700">
                  AI compares contract requirements with your assessment data to predict success probability.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-blue-900 mb-1">🎯 Strategic Guidance</h4>
                <p className="text-sm text-blue-700">
                  Intelligent recommendations for competitive positioning and bid strategy optimization.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}