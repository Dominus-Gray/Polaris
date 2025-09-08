import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://biz-matchmaker-1.preview.emergentagent.com';

function AssessmentResults() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    const loadResults = async () => {
      try {
        console.log('Loading results for session:', sessionId);
        const response = await axios.get(`${API}/api/assessment/results/${sessionId}`, authHeaders);
        console.log('Results loaded:', response.data);
        setResults(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading results:', error);
        setError(error.response?.data?.detail || 'Failed to load assessment results');
        setLoading(false);
      }
    };

    if (sessionId) {
      loadResults();
    } else {
      setError('No session ID provided');
      setLoading(false);
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading your assessment results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Results</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/assessment')}
                className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Back to Assessments
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Assessment Results</h1>
              <p className="text-gray-600">{results?.area_info?.area_title}</p>
            </div>
            <button
              onClick={() => navigate('/assessment')}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Back to Assessments
            </button>
          </div>
        </div>

        {/* Results Summary */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Score Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Score</h3>
            <div className="text-center">
              <div className={`text-4xl font-bold mb-2 ${
                results?.completion_info?.tier_completion_score >= 80 ? 'text-green-600' :
                results?.completion_info?.tier_completion_score >= 60 ? 'text-orange-600' :
                'text-red-600'
              }`}>
                {results?.completion_info?.tier_completion_score || 0}%
              </div>
              <div className={`text-lg font-medium ${
                results?.performance_analysis?.score_category === 'Excellent' ? 'text-green-600' :
                results?.performance_analysis?.score_category === 'Good' ? 'text-blue-600' :
                results?.performance_analysis?.score_category === 'Fair' ? 'text-orange-600' :
                'text-red-600'
              }`}>
                {results?.performance_analysis?.score_category}
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {results?.area_info?.tier_name} Assessment
              </p>
            </div>
          </div>

          {/* Progress Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Completion Details</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Questions Answered:</span>
                <span className="font-medium">
                  {results?.completion_info?.responses_submitted}/{results?.completion_info?.total_questions}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tier Level:</span>
                <span className="font-medium">Tier {results?.area_info?.tier_level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Completed:</span>
                <span className="font-medium">
                  {results?.completion_info?.completed_at ? 
                    new Date(results.completion_info.completed_at).toLocaleDateString() : 
                    'In Progress'
                  }
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Analysis</h3>
          
          {results?.performance_analysis?.strengths?.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-green-800 mb-2">✅ Strengths</h4>
              <ul className="list-disc list-inside space-y-1 text-green-700">
                {results.performance_analysis.strengths.map((strength, idx) => (
                  <li key={idx}>{strength}</li>
                ))}
              </ul>
            </div>
          )}

          {results?.performance_analysis?.improvement_areas?.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-orange-800 mb-2">📈 Areas for Improvement</h4>
              <ul className="list-disc list-inside space-y-1 text-orange-700">
                {results.performance_analysis.improvement_areas.map((area, idx) => (
                  <li key={idx}>{area}</li>
                ))}
              </ul>
            </div>
          )}

          {results?.performance_analysis?.next_steps?.length > 0 && (
            <div>
              <h4 className="font-medium text-blue-800 mb-2">🎯 Next Steps</h4>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                {results.performance_analysis.next_steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What's Next?</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/assessment')}
              className="px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
            >
              Take Another Assessment
            </button>
            <button
              onClick={() => navigate('/home')}
              className="px-4 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
            >
              Return to Dashboard
            </button>
            {results?.tier_progression?.next_tier_available && (
              <button
                onClick={() => {
                  navigate('/assessment');
                  // Could add logic to pre-select next tier
                }}
                className="px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700"
              >
                Try Next Tier
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AssessmentResults;