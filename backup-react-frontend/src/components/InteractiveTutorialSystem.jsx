import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function InteractiveTutorialSystem({ userRole, currentPage }) {
  const [activeTutorial, setActiveTutorial] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [tutorialProgress, setTutorialProgress] = useState({});
  const [showTutorialHub, setShowTutorialHub] = useState(false);
  const [availableTutorials, setAvailableTutorials] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);

  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  // Tutorial definitions for each user role and page
  const tutorialLibrary = {
    client: {
      dashboard: {
        id: 'client_dashboard_intro',
        title: 'Welcome to Your Dashboard',
        description: 'Learn how to navigate your procurement readiness dashboard',
        estimatedTime: '3 minutes',
        steps: [
          {
            target: '.procurement-readiness-header',
            title: 'Your Readiness Overview',
            content: 'This header shows your overall procurement readiness percentage and progress toward certification. The progress bar helps you visualize how close you are to the 70% certification threshold.',
            position: 'bottom',
            action: 'highlight'
          },
          {
            target: '.recommended-next-steps',
            title: 'Smart Recommendations',
            content: 'These personalized recommendations adapt based on your progress. They guide you to the most impactful next steps for improving your readiness score.',
            position: 'top',
            action: 'highlight'
          },
          {
            target: '.recent-activity-feed',
            title: 'Live Activity Updates',
            content: 'Stay informed with real-time updates about your assessment progress, service provider responses, and new resources available to you.',
            position: 'left',
            action: 'highlight'
          },
          {
            target: '[data-tab="assessment"]',
            title: 'Assessment Center',
            content: 'Click here to access the 10 business area assessments. Start with Legal & Compliance for the best foundation.',
            position: 'bottom',
            action: 'click-hint'
          }
        ]
      },
      assessment: {
        id: 'client_assessment_guide',
        title: 'Assessment System Guide',
        description: 'Master the tier-based assessment system',
        estimatedTime: '5 minutes',
        steps: [
          {
            target: '.business-areas-grid',
            title: '10 Business Areas',
            content: 'Each area represents a critical aspect of procurement readiness. Green areas are complete, yellow need attention, and red require immediate focus.',
            position: 'top',
            action: 'highlight'
          },
          {
            target: '.tier-indicators',
            title: 'Tier System',
            content: 'Each area has 3 tiers: Tier 1 (self-assessment), Tier 2 (evidence required), Tier 3 (verification). Your agency determines which tiers you can access.',
            position: 'right',
            action: 'highlight'
          },
          {
            target: '[data-area="area1"]',
            title: 'Start with Legal & Compliance',
            content: 'This foundational area covers business formation, licenses, and legal requirements. Complete this first for the strongest foundation.',
            position: 'bottom',
            action: 'click-hint'
          }
        ]
      }
    },
    provider: {
      dashboard: {
        id: 'provider_dashboard_intro',
        title: 'Provider Dashboard Overview',
        description: 'Maximize your success with intelligent client matching',
        estimatedTime: '4 minutes',
        steps: [
          {
            target: '.smart-opportunities',
            title: 'Smart Opportunities',
            content: 'Our AI analyzes client needs and matches them with your expertise. Higher match scores mean better client fit and higher success rates.',
            position: 'top',
            action: 'highlight'
          },
          {
            target: '.match-scoring',
            title: 'Understanding Match Scores',
            content: 'Match scores consider client assessment gaps, your specializations, geographic proximity, and historical success patterns.',
            position: 'bottom',
            action: 'highlight'
          },
          {
            target: '.opportunity-details',
            title: 'Rich Client Context',
            content: 'Each opportunity includes detailed client information: industry, size, budget, timeline, and competition level to help you craft winning proposals.',
            position: 'left',
            action: 'highlight'
          }
        ]
      }
    },
    agency: {
      dashboard: {
        id: 'agency_dashboard_intro',
        title: 'Agency Impact Dashboard',
        description: 'Track and optimize your program\'s economic impact',
        estimatedTime: '6 minutes',
        steps: [
          {
            target: '.economic-impact-overview',
            title: 'Economic Impact Metrics',
            content: 'This executive summary shows your program\'s economic impact: contracts secured, success rates, and ROI. Use these metrics for stakeholder reporting.',
            position: 'bottom',
            action: 'highlight'
          },
          {
            target: '.contract-pipeline',
            title: 'Contract Opportunity Pipeline',
            content: 'Track your sponsored businesses through the contract readiness pipeline. Monitor which businesses are ready for opportunities.',
            position: 'top',
            action: 'highlight'
          },
          {
            target: '.rp-navigation',
            title: 'Resource Partner Tools',
            content: 'Use RP Leads and RP Admin to manage connections between your businesses and resource partners like lenders and investors.',
            position: 'bottom',
            action: 'click-hint'
          }
        ]
      }
    },
    navigator: {
      dashboard: {
        id: 'navigator_dashboard_intro',
        title: 'Navigator Coaching Tools',
        description: 'Leverage AI insights for effective client guidance',
        estimatedTime: '5 minutes',
        steps: [
          {
            target: '.ai-coaching-insights',
            title: 'AI Coaching Dashboard',
            content: 'Get real-time insights about client risks, success predictions, and intervention recommendations to maximize your coaching effectiveness.',
            position: 'bottom',
            action: 'highlight'
          },
          {
            target: '.at-risk-clients',
            title: 'Proactive Client Support',
            content: 'Identify clients who haven\'t engaged recently and need intervention to prevent dropouts from the program.',
            position: 'right',
            action: 'highlight'
          },
          {
            target: '.success-predictions',
            title: 'Success Forecasting',
            content: 'AI analyzes client progress patterns to predict likelihood of success and recommend optimal support strategies.',
            position: 'left',
            action: 'highlight'
          }
        ]
      }
    }
  };

  useEffect(() => {
    loadTutorialProgress();
    generateAvailableTutorials();
  }, [userRole, currentPage]);

  const loadTutorialProgress = async () => {
    try {
      const response = await axios.get(`${API}/tutorials/progress`);
      setTutorialProgress(response.data.progress || {});
    } catch (error) {
      // Load from localStorage as fallback
      const localProgress = localStorage.getItem('tutorial_progress');
      setTutorialProgress(localProgress ? JSON.parse(localProgress) : {});
    }
  };

  const generateAvailableTutorials = () => {
    const roleTutorials = tutorialLibrary[userRole] || {};
    const tutorials = Object.entries(roleTutorials).map(([page, tutorial]) => ({
      ...tutorial,
      page,
      completed: tutorialProgress[tutorial.id] || false,
      available: page === currentPage || tutorialProgress[tutorial.id]
    }));
    
    setAvailableTutorials(tutorials);
  };

  const startTutorial = (tutorialId) => {
    const tutorial = availableTutorials.find(t => t.id === tutorialId);
    if (tutorial) {
      setActiveTutorial(tutorial);
      setCurrentStep(0);
      setIsPlaying(true);
      setShowTutorialHub(false);
      
      // Add tutorial overlay
      document.body.style.overflow = 'hidden';
      addTutorialOverlay();
    }
  };

  const nextStep = () => {
    if (activeTutorial && currentStep < activeTutorial.steps.length - 1) {
      setCurrentStep(currentStep + 1);
      highlightTargetElement();
    } else {
      completeTutorial();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      highlightTargetElement();
    }
  };

  const completeTutorial = async () => {
    if (activeTutorial) {
      try {
        await axios.post(`${API}/tutorials/complete`, {
          tutorial_id: activeTutorial.id,
          user_id: me?.id,
          completed_at: new Date().toISOString()
        });
      } catch (error) {
        // Save to localStorage as fallback
        const progress = { ...tutorialProgress, [activeTutorial.id]: true };
        setTutorialProgress(progress);
        localStorage.setItem('tutorial_progress', JSON.stringify(progress));
      }
      
      closeTutorial();
      
      // Show completion celebration
      showCompletionCelebration();
    }
  };

  const closeTutorial = () => {
    setActiveTutorial(null);
    setCurrentStep(0);
    setIsPlaying(false);
    removeTutorialOverlay();
    document.body.style.overflow = 'auto';
  };

  const addTutorialOverlay = () => {
    const overlay = document.createElement('div');
    overlay.id = 'tutorial-overlay';
    overlay.className = 'fixed inset-0 bg-primary bg-opacity-50 z-40 pointer-events-none';
    document.body.appendChild(overlay);
  };

  const removeTutorialOverlay = () => {
    const overlay = document.getElementById('tutorial-overlay');
    if (overlay) {
      document.body.removeChild(overlay);
    }
    
    // Remove any highlights
    document.querySelectorAll('.tutorial-highlight').forEach(el => {
      el.classList.remove('tutorial-highlight');
    });
  };

  const highlightTargetElement = () => {
    if (!activeTutorial || !activeTutorial.steps[currentStep]) return;
    
    const step = activeTutorial.steps[currentStep];
    const targetElement = document.querySelector(step.target);
    
    if (targetElement) {
      // Remove previous highlights
      document.querySelectorAll('.tutorial-highlight').forEach(el => {
        el.classList.remove('tutorial-highlight');
      });
      
      // Add highlight to current target
      targetElement.classList.add('tutorial-highlight');
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const showCompletionCelebration = () => {
    const celebration = document.createElement('div');
    celebration.className = 'fixed inset-0 z-50 flex items-center justify-center pointer-events-none';
    celebration.innerHTML = `
      <div class="bg-white rounded-2xl shadow-2xl p-8 text-center transform animate-bounce pointer-events-auto">
        <div class="text-6xl mb-4">🎉</div>
        <h3 class="text-xl font-bold text-slate-900 mb-2">Tutorial Completed!</h3>
        <p class="text-slate-600 mb-4">You're now ready to make the most of this feature!</p>
        <button onclick="this.parentElement.parentElement.remove()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Continue
        </button>
      </div>
    `;
    
    document.body.appendChild(celebration);
    
    setTimeout(() => {
      if (celebration.parentNode) {
        document.body.removeChild(celebration);
      }
    }, 5000);
  };

  useEffect(() => {
    if (isPlaying && activeTutorial) {
      highlightTargetElement();
    }
  }, [currentStep, isPlaying]);

  // Tutorial Hub Component
  const TutorialHub = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Interactive Tutorials</h2>
              <p className="text-slate-600">Learn at your own pace with guided walkthroughs</p>
            </div>
            <button
              onClick={() => setShowTutorialHub(false)}
              className="text-slate-500 hover:text-slate-700 p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tutorial Grid */}
        <div className="p-6 overflow-y-auto max-h-96">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {availableTutorials.map((tutorial) => (
              <div
                key={tutorial.id}
                className={`border rounded-xl p-6 transition-all duration-200 ${
                  tutorial.completed
                    ? 'bg-green-50 border-green-200'
                    : tutorial.available
                    ? 'bg-white border-slate-200 hover:shadow-md'
                    : 'bg-slate-50 border-slate-200 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-2">{tutorial.title}</h3>
                    <p className="text-sm text-slate-600 mb-3">{tutorial.description}</p>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {tutorial.estimatedTime}
                      </span>
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {tutorial.steps.length} steps
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    {tutorial.completed ? (
                      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    ) : tutorial.available ? (
                      <button
                        onClick={() => startTutorial(tutorial.id)}
                        className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white hover:bg-blue-700 transition-colors"
                      >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M12 7a4 4 0 01-4 4v2a1 1 0 01-1 1H5a1 1 0 01-1-1v-2a4 4 0 01-4-4V5a1 1 0 011-1h12a1 1 0 011 1v2z" />
                        </svg>
                      </button>
                    ) : (
                      <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center">
                        <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    tutorial.completed
                      ? 'bg-green-100 text-green-800'
                      : tutorial.available
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-slate-100 text-slate-600'
                  }`}>
                    {tutorial.completed ? 'Completed' : tutorial.available ? 'Available' : 'Locked'}
                  </span>
                  
                  {tutorial.available && !tutorial.completed && (
                    <button
                      onClick={() => startTutorial(tutorial.id)}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      Start Tutorial →
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Active Tutorial Overlay
  const TutorialOverlay = () => {
    if (!activeTutorial || !isPlaying) return null;

    const step = activeTutorial.steps[currentStep];
    const progress = ((currentStep + 1) / activeTutorial.steps.length) * 100;

    return (
      <div className="fixed inset-0 z-50 pointer-events-none">
        {/* Tutorial Card */}
        <div className="absolute top-4 right-4 w-80 bg-white rounded-lg shadow-2xl border pointer-events-auto">
          <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-slate-900">{activeTutorial.title}</h3>
              <button
                onClick={closeTutorial}
                className="text-slate-500 hover:text-slate-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Step {currentStep + 1} of {activeTutorial.steps.length}</span>
              <span>{Math.round(progress)}% complete</span>
            </div>
          </div>

          <div className="p-4">
            <h4 className="font-medium text-slate-900 mb-2">{step.title}</h4>
            <p className="text-sm text-slate-600 mb-4">{step.content}</p>
            
            <div className="flex items-center justify-between">
              <button
                onClick={prevStep}
                disabled={currentStep === 0}
                className="px-3 py-2 text-sm border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              <button
                onClick={nextStep}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {currentStep === activeTutorial.steps.length - 1 ? 'Complete' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Tutorial Hub Button */}
      <button
        onClick={() => setShowTutorialHub(true)}
        className="fixed bottom-4 left-20 w-12 h-12 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-40"
        title="Interactive Tutorials"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </button>

      {/* Tutorial Hub Modal */}
      {showTutorialHub && <TutorialHub />}

      {/* Active Tutorial Overlay */}
      <TutorialOverlay />

      {/* Tutorial Highlight CSS */}
      <style jsx>{`
        .tutorial-highlight {
          position: relative;
          z-index: 41;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5), 0 0 0 2000px rgba(0, 0, 0, 0.3);
          border-radius: 8px;
        }
      `}</style>
    </>
  );
}