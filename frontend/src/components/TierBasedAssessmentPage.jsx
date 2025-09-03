import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://providermatrix.preview.emergentagent.com';

function TierBasedAssessmentPage() {
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [availableAreas, setAvailableAreas] = useState([]);
  const [assessmentProgress, setAssessmentProgress] = useState(null);
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
  const [showActionModal, setShowActionModal] = useState(false);
  const [completionResults, setCompletionResults] = useState(null);

  // Get URL parameters for direct navigation
  const urlParams = new URLSearchParams(window.location.search);
  const focusArea = urlParams.get('area');
  const focusTier = parseInt(urlParams.get('tier')) || null;
  const autoFocus = urlParams.get('focus') === 'true';

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

  // Load client's tier access information and progress
  useEffect(() => {
    const loadAssessmentData = async () => {
      try {
        console.log('Loading assessment data...');
        
        // Load tier access
        const tierResponse = await axios.get(`${API}/api/client/tier-access`, authHeaders);
        console.log('Tier access response:', tierResponse.data);
        
        // Load assessment progress
        const progressResponse = await axios.get(`${API}/api/client/assessment-progress`, authHeaders);
        console.log('Progress response:', progressResponse.data);
        
        if (tierResponse.data && tierResponse.data.areas) {
          // Merge tier access with progress data
          const areasWithProgress = tierResponse.data.areas.map(area => {
            const progress = progressResponse.data?.area_progress?.[area.area_id] || {};
            return {
              ...area,
              ...progress,
              status_color: getStatusColor(progress.status),
              progress_text: `${progress.questions_answered || 0}/${progress.total_questions || 0} questions`
            };
          });
          
          setAvailableAreas(areasWithProgress);
          setAssessmentProgress(progressResponse.data);
          console.log(`Loaded ${areasWithProgress.length} areas with progress data`);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error loading assessment data:', error);
        setLoading(false);
      }
    };

    if (me && me.role === 'client') {
      loadAssessmentData();
    } else {
      setLoading(false);
    }
  }, []);

  // Helper function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'bg-green-400';
      case 'nearing_completion': return 'bg-orange-400';  
      case 'incomplete': return 'bg-yellow-400';
      default: return 'bg-gray-300';
    }
  };

  // Comprehensive assessment completion handler with integrated workflow
  const handleAssessmentCompletion = async (sessionId) => {
    try {
      console.log('Assessment completed, triggering integrated workflow...');
      
      // 1. Get assessment results
      const resultsResponse = await axios.get(`${API}/api/assessment/results/${sessionId}`, authHeaders);
      const results = resultsResponse.data;
      
      // 2. Trigger dashboard updates
      await axios.post(`${API}/api/realtime/dashboard-update`, {
        user_id: me.id,
        update_type: 'assessment_completed',
        data: {
          session_id: sessionId,
          area_id: results.area_info?.area_id,
          score: results.completion_info?.tier_completion_score,
          tier_level: results.area_info?.tier_level
        }
      }, authHeaders);
      
      // 3. Check for gaps and generate recommendations
      const score = results.completion_info?.tier_completion_score || 0;
      const hasGaps = score < 80;
      
      if (hasGaps) {
        // Show integrated action modal
        setShowActionModal(true);
        setCompletionResults({
          ...results,
          hasGaps,
          recommendations: await generateActionRecommendations(results)
        });
      } else {
        // Navigate to results for high-scoring assessments
        navigate(`/assessment/results/${sessionId}`);
      }
      
    } catch (error) {
      console.error('Error in assessment completion workflow:', error);
      // Fallback to simple results page
      navigate(`/assessment/results/${sessionId}`);
    }
  };

  // Generate action recommendations based on assessment results
  const generateActionRecommendations = async (results) => {
    const recommendations = {
      immediate_actions: [],
      resource_suggestions: [],
      service_providers: []
    };
    
    const areaId = results.area_info?.area_id;
    const score = results.completion_info?.tier_completion_score || 0;
    
    // Immediate actions based on score
    if (score < 50) {
      recommendations.immediate_actions.push({
        title: 'Access Free Resources',
        description: `Get immediate help with ${results.area_info?.area_title}`,
        action: 'view_resources',
        priority: 'high'
      });
      
      recommendations.immediate_actions.push({
        title: 'Request Professional Help',
        description: 'Connect with certified service providers',
        action: 'create_service_request',
        priority: 'high'
      });
    } else if (score < 80) {
      recommendations.immediate_actions.push({
        title: 'Improve Your Score',
        description: 'Access targeted resources for improvement',
        action: 'view_resources',
        priority: 'medium'
      });
    }
    
    // Always suggest next assessment
    recommendations.immediate_actions.push({
      title: 'Continue Assessment Journey',
      description: 'Complete assessments for other business areas',
      action: 'next_assessment',
      priority: 'medium'
    });
    
    return recommendations;
  };



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
        // Assessment complete - trigger integrated workflow
        await handleAssessmentCompletion(currentSession.session_id);
      }
      
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setSubmitLoading(false);
    }
  };

  // Handle answer change for radio inputs
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // Handle solution path change for gap resolution
  const handleSolutionPathChange = (questionId, solutionPath) => {
    setAnswers(prev => ({
      ...prev,
      [`solution_${questionId}`]: solutionPath
    }));
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
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  <span className="text-blue-600 font-bold mr-2">{area.area_id.replace('area', '')}</span>
                  {area.area_title}
                </h3>
                <p className="text-gray-600 text-sm mb-4">{area.area_description}</p>
                
                {/* Status and Progress Indicators */}
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-gray-500">Max Access: Tier {area.max_tier_access}</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3].map((tier) => (
                      <div
                        key={tier}
                        className={`w-4 h-4 rounded-full border-2 ${
                          tier <= area.max_tier_access 
                            ? tier <= (area.highest_tier_completed || 0) 
                              ? area.status_color || 'bg-green-400'
                              : 'bg-gray-200 border-gray-400'
                            : 'bg-gray-300 border-gray-300'
                        }`}
                        title={`Tier ${tier} ${tier <= area.max_tier_access ? 'Available' : 'Not Available'}`}
                      />
                    ))}
                  </div>
                </div>

                {/* Progress Information */}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    Status: <span className={`font-medium ${
                      area.status === 'compliant' ? 'text-green-600' :
                      area.status === 'nearing_completion' ? 'text-orange-600' :
                      area.status === 'incomplete' ? 'text-yellow-600' : 'text-gray-600'
                    }`}>
                      {area.status === 'compliant' ? 'Compliant' :
                       area.status === 'nearing_completion' ? 'Nearing Completion' :
                       area.status === 'incomplete' ? 'In Progress' : 'Not Started'}
                    </span>
                  </span>
                  <span className="text-gray-500">{area.progress_text || '0/0 questions'}</span>
                </div>

                {/* Completion Score if available */}
                {area.completion_score && (
                  <div className="mt-2 text-xs text-gray-500">
                    Score: {area.completion_score}%
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Assessment Start Section */}
          {selectedArea && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {selectedArea.area_number}. {selectedArea.area_title}
              </h2>
              
              {/* Current Progress Display */}
              {selectedArea.progress_text && selectedArea.progress_text !== '0/0 questions' && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-blue-800 font-medium">Current Progress</span>
                    <span className="text-blue-600">{selectedArea.progress_text}</span>
                  </div>
                  {selectedArea.completion_score && (
                    <div className="mt-1 text-sm text-blue-600">
                      Latest Score: {selectedArea.completion_score}%
                    </div>
                  )}
                </div>
              )}

              {/* Assessment Information */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-medium text-gray-900 mb-2">Your Assessment Access</h3>
                <p className="text-gray-600 text-sm mb-3">{selectedArea.area_description}</p>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Maximum Tier Access:</span>
                    <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      Tier {selectedArea.max_tier_access}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">Total Questions:</span>
                    <span className="ml-2 text-sm text-gray-600">
                      {selectedArea.max_tier_access === 1 ? '3 questions (Self Assessment)' :
                       selectedArea.max_tier_access === 2 ? '6 questions (Self Assessment + Evidence Required)' :
                       '9 questions (Self Assessment + Evidence Required + Verification)'}
                    </span>
                  </div>
                </div>
                
                <div className="mt-3">
                  <span className="text-sm font-medium text-gray-700">Assessment Type:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {selectedArea.max_tier_access === 1 ? 'Self Assessment - Low to moderate effort maturity statements' :
                     selectedArea.max_tier_access === 2 ? 'Evidence Required - Includes self assessment + documented evidence' :
                     'Verification - Complete assessment with third-party validation requirements'}
                  </span>
                </div>
              </div>

              {/* Start Assessment Button */}
              <div className="text-center">
                <button
                  onClick={() => {
                    setSelectedTier(selectedArea.max_tier_access);
                    createSession();
                  }}
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
                    `Start Assessment (Tier ${selectedArea.max_tier_access})`
                  )}
                </button>
                <p className="mt-2 text-sm text-gray-500">
                  You'll receive all questions for your tier access level
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Assessment in progress - all questions for selected tier (cumulative)
  const currentQuestion = questions[currentQuestionIndex];
  const progressPercentage = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;

  return (
    <>
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
            {/* Question Tier Indicator */}
            {currentQuestion?.tier_level && (
              <div className="flex items-center gap-2 mb-4">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  currentQuestion.tier_level === 1 ? 'bg-blue-100 text-blue-800' :
                  currentQuestion.tier_level === 2 ? 'bg-orange-100 text-orange-800' :
                  'bg-purple-100 text-purple-800'
                }`}>
                  Tier {currentQuestion.tier_level}
                </span>
                <span className="text-sm text-gray-500">{currentQuestion.tier_name}</span>
              </div>
            )}
            
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {currentQuestion?.text}
            </h2>

            {/* Updated Assessment Response Options */}
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg">
                <label className="flex items-center gap-4 p-4 cursor-pointer hover:bg-green-100 transition-colors">
                  <input
                    type="radio"
                    name={`question_${currentQuestion.id}`}
                    value="compliant"
                    checked={answers[currentQuestion.id] === 'compliant'}
                    onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                    className="w-5 h-5 text-green-600 focus:ring-green-500"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium text-green-900">Compliant</span>
                    </div>
                    <p className="text-sm text-green-700 mt-1">This requirement is fully met and documented</p>
                  </div>
                </label>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg">
                <label className="flex items-center gap-4 p-4 cursor-pointer hover:bg-red-100 transition-colors">
                  <input
                    type="radio"
                    name={`question_${currentQuestion.id}`}
                    value="gap_exists"
                    checked={answers[currentQuestion.id] === 'gap_exists'}
                    onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                    className="w-5 h-5 text-red-600 focus:ring-red-500"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <span className="font-medium text-red-900">Gap Exists - I Need Help</span>
                    </div>
                    <p className="text-sm text-red-700 mt-1">This requirement is not met and I need assistance</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Gap Solution Pathway Selection */}
            {answers[currentQuestion.id] === 'gap_exists' && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-3">🎯 Select Your Preferred Solution Path:</h4>
                <div className="space-y-3">
                  <label className="flex items-center gap-3 p-3 bg-white border border-yellow-200 rounded-lg cursor-pointer hover:bg-yellow-50 transition-colors">
                    <input
                      type="radio"
                      name={`solution_${currentQuestion.id}`}
                      value="service_provider"
                      onChange={(e) => handleSolutionPathChange(currentQuestion.id, e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <span className="font-medium text-gray-900">Service Provider Matchmaking</span>
                    </div>
                  </label>
                  
                  <label className="flex items-center gap-3 p-3 bg-white border border-yellow-200 rounded-lg cursor-pointer hover:bg-yellow-50 transition-colors">
                    <input
                      type="radio"
                      name={`solution_${currentQuestion.id}`}
                      value="knowledge_base"
                      onChange={(e) => handleSolutionPathChange(currentQuestion.id, e.target.value)}
                      className="w-4 h-4 text-purple-600"
                    />
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                      <span className="font-medium text-gray-900">Knowledge Base Resources</span>
                    </div>
                  </label>
                  
                  <label className="flex items-center gap-3 p-3 bg-white border border-yellow-200 rounded-lg cursor-pointer hover:bg-yellow-50 transition-colors">
                    <input
                      type="radio"
                      name={`solution_${currentQuestion.id}`}
                      value="external_resources"
                      onChange={(e) => handleSolutionPathChange(currentQuestion.id, e.target.value)}
                      className="w-4 h-4 text-green-600"
                    />
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                      </svg>
                      <span className="font-medium text-gray-900">AI-Powered External Resources</span>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="mt-6 text-center">
              <button
                onClick={() => {
                  const answer = answers[currentQuestion.id];
                  if (answer) {
                    submitAnswer(answer);
                  } else {
                    alert('Please select an answer before continuing.');
                  }
                }}
                disabled={submitLoading || !answers[currentQuestion.id]}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {submitLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </>
                ) : (
                  currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Complete Assessment'
                )}
              </button>
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

      {/* Integrated Action Modal */}
      {showActionModal && completionResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="text-center mb-6">
                <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4 ${
                  completionResults.completion_info?.tier_completion_score >= 80 
                    ? 'bg-green-100' : 'bg-orange-100'
                }`}>
                  <span className={`text-2xl font-bold ${
                    completionResults.completion_info?.tier_completion_score >= 80 
                      ? 'text-green-600' : 'text-orange-600'
                  }`}>
                    {completionResults.completion_info?.tier_completion_score || 0}%
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Assessment Complete!</h2>
                <p className="text-gray-600">
                  {completionResults.area_info?.area_title} - {completionResults.area_info?.tier_name}
                </p>
              </div>

              {/* Recommendations */}
              {completionResults.hasGaps && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Next Steps</h3>
                  <div className="space-y-3">
                    {completionResults.recommendations?.immediate_actions?.map((action, idx) => (
                      <div 
                        key={idx}
                        className={`p-4 rounded-lg border-l-4 cursor-pointer hover:bg-gray-50 ${
                          action.priority === 'high' ? 'border-red-400 bg-red-50' :
                          action.priority === 'medium' ? 'border-yellow-400 bg-yellow-50' :
                          'border-blue-400 bg-blue-50'
                        }`}
                        onClick={() => handleRecommendedAction(action.action)}
                      >
                        <h4 className="font-medium text-gray-900">{action.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => navigate(`/assessment/results/${completionResults.session_id}`)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
                >
                  View Detailed Results
                </button>
                <button
                  onClick={() => {
                    setShowActionModal(false);
                    navigate('/assessment');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                >
                  Take Another Assessment
                </button>
                <button
                  onClick={() => {
                    setShowActionModal(false);
                    navigate('/home');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                >
                  Return to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // Handle recommended actions
  const handleRecommendedAction = (actionType) => {
    setShowActionModal(false);
    
    switch (actionType) {
      case 'view_resources':
        navigate('/home#resources');
        break;
      case 'create_service_request':
        navigate('/services/create');
        break;
      case 'next_assessment':
        navigate('/assessment');
        break;
      default:
        navigate('/home');
    }
  };
}

export default TierBasedAssessmentPage;