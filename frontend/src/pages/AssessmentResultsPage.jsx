import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://providermatrix.preview.emergentagent.com';

function AssessmentResultsPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAssessmentResults();
  }, [sessionId]);

  const loadAssessmentResults = async () => {
    try {
      const response = await axios.get(`${API}/assessment/results/${sessionId}`);
      setResults(response.data);
    } catch (error) {
      console.error('Error loading assessment results:', error);
      setError('Failed to load assessment results');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-slate-200 rounded w-3/4 mb-6"></div>
            <div className="space-y-4">
              {[1,2,3,4,5].map(i => (
                <div key={i} className="h-16 bg-slate-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Results</h2>
          <p className="text-red-700 mb-6">{error}</p>
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/assessment')}
          >
            Back to Assessment
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-slate-50 border rounded-lg p-8 text-center">
          <h2 className="text-xl font-semibold text-slate-800 mb-2">No Results Found</h2>
          <p className="text-slate-600 mb-6">Assessment results are not available for this session.</p>
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/assessment')}
          >
            Take Assessment
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Assessment Results</h1>
            <p className="text-blue-100">Procurement Readiness Analysis & Recommendations</p>
            <div className="text-sm text-blue-200 mt-2">
              Completed: {new Date(results.completed_at).toLocaleDateString()}
            </div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-bold mb-2">{results.overall_score}%</div>
            <div className="text-blue-100">Overall Readiness</div>
            <div className="mt-2">
              {results.overall_score >= 80 && <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm">Excellent</span>}
              {results.overall_score >= 60 && results.overall_score < 80 && <span className="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm">Good</span>}
              {results.overall_score < 60 && <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm">Needs Improvement</span>}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Area Scores */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Business Area Scores</h2>
            
            <div className="space-y-4">
              {results.area_scores && results.area_scores.map((area, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-medium text-slate-900">{area.area_name}</h3>
                      <p className="text-sm text-slate-600">{area.description}</p>
                    </div>
                    <div className={`text-right ml-4 ${getScoreColor(area.score)}`}>
                      <div className="text-2xl font-bold">{area.score}%</div>
                      <div className="text-xs uppercase tracking-wide">
                        {area.score >= 80 ? 'Strong' : area.score >= 60 ? 'Moderate' : 'Weak'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-slate-200 rounded-full h-2 mb-3">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        area.score >= 80 ? 'bg-green-500' :
                        area.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${area.score}%` }}
                    ></div>
                  </div>

                  {/* Key Findings */}
                  {area.key_findings && area.key_findings.length > 0 && (
                    <div className="mt-3">
                      <h4 className="text-sm font-medium text-slate-700 mb-2">Key Findings:</h4>
                      <ul className="text-sm text-slate-600 space-y-1">
                        {area.key_findings.slice(0, 3).map((finding, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-slate-400 mt-1">•</span>
                            <span>{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Strengths */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center gap-2">
                <span>💪</span>
                Key Strengths
              </h3>
              <ul className="space-y-2">
                {results.strengths && results.strengths.map((strength, index) => (
                  <li key={index} className="text-green-700 text-sm flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-800 mb-4 flex items-center gap-2">
                <span>🎯</span>
                Improvement Areas
              </h3>
              <ul className="space-y-2">
                {results.improvement_areas && results.improvement_areas.map((area, index) => (
                  <li key={index} className="text-red-700 text-sm flex items-start gap-2">
                    <span className="text-red-500 mt-1">!</span>
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Action Items & Next Steps */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Next Steps</h3>
            
            {/* Action Plan Button */}
            <button 
              className="w-full btn btn-primary mb-4"
              onClick={() => navigate(`/assessment/action-plan/${sessionId}`)}
            >
              <span className="mr-2">📋</span>
              Generate Action Plan
            </button>

            {/* Capability Statement Button */}
            <button 
              className="w-full btn btn-secondary mb-4"
              onClick={() => navigate('/tools/capability-statement')}
            >
              <span className="mr-2">📄</span>
              Create Capability Statement
            </button>

            {/* Find Providers Button */}
            <button 
              className="w-full btn btn-outline mb-6"
              onClick={() => navigate('/service-request')}
            >
              <span className="mr-2">🔍</span>
              Find Service Providers
            </button>

            {/* Quick Stats */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-slate-700 mb-3">Assessment Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Areas Assessed:</span>
                  <span className="font-medium">{results.area_scores?.length || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Questions Answered:</span>
                  <span className="font-medium">{results.total_questions || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Time Invested:</span>
                  <span className="font-medium">{results.completion_time || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Certification Status */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Certification</h3>
            
            {results.overall_score >= 70 ? (
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏆</span>
                </div>
                <h4 className="font-medium text-green-800 mb-2">Certification Eligible</h4>
                <p className="text-sm text-green-700 mb-4">
                  You qualify for Small Business Maturity Assurance certification
                </p>
                <button 
                  className="btn btn-success btn-sm"
                  onClick={() => navigate('/certifications')}
                >
                  Generate Certificate
                </button>
              </div>
            ) : (
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📈</span>
                </div>
                <h4 className="font-medium text-yellow-800 mb-2">Continue Improving</h4>
                <p className="text-sm text-yellow-700 mb-4">
                  Reach 70% overall score to qualify for certification
                </p>
                <div className="text-xs text-slate-600">
                  You need {70 - results.overall_score} more points
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-slate-50 rounded-lg p-6 mt-8">
        <div className="flex flex-wrap gap-4 justify-center">
          <button 
            className="btn btn-secondary"
            onClick={() => navigate('/assessment')}
          >
            Retake Assessment
          </button>
          <button 
            className="btn btn-outline"
            onClick={() => navigate('/readiness-dashboard')}
          >
            View Progress Dashboard
          </button>
          <button 
            className="btn btn-outline"
            onClick={() => window.print()}
          >
            Print Results
          </button>
        </div>
      </div>
    </div>
  );
}

export default AssessmentResultsPage;