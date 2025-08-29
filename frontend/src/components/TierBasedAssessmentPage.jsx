import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://quality-match-1.preview.emergentagent.com';

function TierBasedAssessmentPage() {
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [availableAreas, setAvailableAreas] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [selectedTier, setSelectedTier] = useState(1);
  const [currentSession, setCurrentSession] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showProgress, setShowProgress] = useState(false);

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  // Redirect non-clients to home
  if (!me || me.role !== 'client') {
    navigate('/home');
    return null;
  }

  // Load client's tier access information
  useEffect(() => {
    const loadTierAccess = async () => {
      try {
        console.log('Loading tier access from:', `${API}/api/client/tier-access`);
        console.log('Auth headers:', authHeaders);
        
        const response = await axios.get(`${API}/api/client/tier-access`, authHeaders);
        console.log('Tier access response:', response.data);
        
        if (response.data && response.data.areas) {
          setAvailableAreas(response.data.areas);
          console.log(`Loaded ${response.data.areas.length} areas:`, response.data.areas.map(a => a.area_title));
        } else {
          console.error('Invalid response structure:', response.data);
        }
        setLoading(false);
      } catch (error) {
        console.error('Error loading tier access:', error);
        console.error('Error response:', error.response?.data);
        setLoading(false);
      }
    };

    if (me && me.role === 'client') {
      loadTierAccess();
    } else {
      setLoading(false);
    }
  }, []);

  // Create assessment session
  const createSession = async () => {
    if (!selectedArea || !selectedTier) return;

    setSessionLoading(true);
    try {
      const formData = new FormData();
      formData.append('area_id', selectedArea.area_id);
      formData.append('tier_level', selectedTier.toString());

      const response = await axios.post(`${API}/api/assessment/tier-session`, formData, authHeaders);
      
      setCurrentSession(response.data);
      setQuestions(response.data.questions || []);
      setAnswers({});
      setCurrentQuestionIndex(0);
      setShowProgress(true);
      
    } catch (error) {
      console.error('Error creating assessment session:', error);
      alert('Failed to start assessment. Please try again.');
    } finally {
      setSessionLoading(false);
    }
  };

  // Submit answer to current question
  const submitAnswer = async (answer) => {
    if (!currentSession || currentQuestionIndex >= questions.length) return;

    const currentQuestion = questions[currentQuestionIndex];
    setSubmitLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('question_id', currentQuestion.id);
      formData.append('response', answer);

      await axios.post(
        `${API}/api/assessment/tier-session/${currentSession.session_id}/response`, 
        formData, 
        authHeaders
      );

      // Update local answers
      const newAnswers = { ...answers, [currentQuestion.id]: answer };
      setAnswers(newAnswers);

      // Move to next question or complete
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      } else {
        // Assessment complete - redirect to results
        navigate(`/assessment/results/${currentSession.session_id}`);
      }
      
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading your tier access information...</p>
          <p className="mt-2 text-sm text-gray-500">Connecting to enhanced assessment system...</p>
        </div>
      </div>
    );
  }

  // Show debug information if no areas loaded
  if (availableAreas.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-yellow-800 mb-4">Tier Access Loading Issue</h2>
            <p className="text-yellow-700 mb-4">
              Unable to load tier-based assessment areas. This might be a temporary connection issue.
            </p>
            <div className="space-y-2 text-sm text-yellow-600">
              <p><strong>Expected:</strong> 10 business areas with tier access information</p>
              <p><strong>API Endpoint:</strong> {`${API}/api/client/tier-access`}</p>
              <p><strong>User Role:</strong> {me?.role || 'Unknown'}</p>
            </div>
            <div className="mt-4">
              <button 
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
              >
                Retry Loading
              </button>
              <button 
                onClick={() => navigate('/home')}
                className="ml-3 px-4 py-2 border border-yellow-600 text-yellow-600 rounded-lg hover:bg-yellow-50"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Area and tier selection screen
  if (!currentSession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Enhanced Tier-Based Assessment</h1>
                <p className="text-gray-600 mt-2">Select a business area and tier level to begin your assessment</p>
              </div>
              <button 
                onClick={() => navigate('/home')}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Back to Dashboard
              </button>
            </div>
          </div>

          {/* Business Areas Grid */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {availableAreas.map((area) => (
              <div 
                key={area.area_id}
                className={`bg-white rounded-lg shadow-md p-6 cursor-pointer transition-all duration-200 ${
                  selectedArea?.area_id === area.area_id 
                    ? 'ring-2 ring-blue-500 shadow-lg' 
                    : 'hover:shadow-lg'
                }`}
                onClick={() => setSelectedArea(area)}
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{area.area_title}</h3>
                <p className="text-gray-600 text-sm mb-4">{area.area_description}</p>
                
                {/* Tier Access Indicators */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Max Access: Tier {area.max_tier_access}</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3].map((tier) => (
                      <div
                        key={tier}
                        className={`w-3 h-3 rounded-full ${
                          tier <= area.max_tier_access 
                            ? 'bg-green-400' 
                            : 'bg-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Tier Selection */}
          {selectedArea && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Available Tiers for {selectedArea.area_title}
              </h2>
              
              <div className="grid md:grid-cols-3 gap-4">
                {selectedArea.available_tiers.map((tier) => (
                  <div
                    key={tier.tier_level}
                    className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                      selectedTier === tier.tier_level
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedTier(tier.tier_level)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">Tier {tier.tier_level}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        tier.effort_level === 'low_moderate' ? 'bg-green-100 text-green-800' :
                        tier.effort_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {tier.effort_level.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-gray-900 mb-1">{tier.tier_name}</p>
                    <p className="text-sm text-gray-600 mb-2">{tier.description}</p>
                    <p className="text-xs text-gray-500">{tier.questions_count} questions</p>
                  </div>
                ))}
              </div>

              {/* Start Assessment Button */}
              {selectedTier && (
                <div className="mt-6 text-center">
                  <button
                    onClick={createSession}
                    disabled={sessionLoading}
                    className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                  >
                    {sessionLoading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Starting Assessment...
                      </>
                    ) : (
                      `Start Tier ${selectedTier} Assessment`
                    )}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Assessment in progress
  const currentQuestion = questions[currentQuestionIndex];
  const progressPercentage = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{currentSession.area_title}</h1>
              <p className="text-sm text-gray-600">{currentSession.tier_name}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Question {currentQuestionIndex + 1} of {questions.length}</p>
              <p className="text-xs text-gray-500">{Math.round(progressPercentage)}% Complete</p>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            {currentQuestion?.text}
          </h2>

          {/* Answer Options */}
          <div className="space-y-3">
            {['Yes', 'No', 'Partial', 'No, I need help'].map((option) => (
              <button
                key={option}
                onClick={() => submitAnswer(option)}
                disabled={submitLoading}
                className="w-full p-4 text-left border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{option}</span>
                  {submitLoading ? (
                    <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Question Info */}
          {currentQuestion?.type && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Question Type:</span> {currentQuestion.type.replace('_', ' ')}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TierBasedAssessmentPage;