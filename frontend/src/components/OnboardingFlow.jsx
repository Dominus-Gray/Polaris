import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function OnboardingFlow({ userRole, onComplete }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [userData, setUserData] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  // Role-specific onboarding steps
  const onboardingSteps = {
    client: [
      {
        id: 1,
        title: "Welcome to Polaris! 🌟",
        subtitle: "Your journey to procurement readiness starts here",
        content: "We'll guide you through 4 simple steps to get started with your business assessment and connect you with the right resources.",
        action: "Let's Begin",
        icon: "🚀"
      },
      {
        id: 2,
        title: "Complete Your Business Profile",
        subtitle: "Help us understand your business better",
        content: "Share basic information about your business so we can provide personalized recommendations and match you with relevant opportunities.",
        action: "Complete Profile",
        icon: "🏢"
      },
      {
        id: 3,
        title: "Take Your First Assessment",
        subtitle: "Discover your procurement readiness",
        content: "Start with our Legal & Compliance assessment - it's the foundation for government contracting success. It takes about 10-15 minutes.",
        action: "Start Assessment",
        icon: "📋"
      },
      {
        id: 4,
        title: "Explore Your Resources",
        subtitle: "Access templates and expert guidance",
        content: "Browse our knowledge base for templates, guides, and best practices. Plus, connect with service providers when you need expert help.",
        action: "Explore Resources",
        icon: "📚"
      }
    ],
    provider: [
      {
        id: 1,
        title: "Welcome, Service Provider! 💼",
        subtitle: "Connect with businesses that need your expertise",
        content: "Polaris connects you with assessment-qualified small businesses seeking professional services for procurement readiness.",
        action: "Get Started",
        icon: "🤝"
      },
      {
        id: 2,
        title: "Build Your Professional Profile",
        subtitle: "Showcase your expertise and experience",
        content: "Create a compelling profile that highlights your certifications, past successes, and specializations to attract the right clients.",
        action: "Build Profile",
        icon: "⭐"
      },
      {
        id: 3,
        title: "Understand Smart Matching",
        subtitle: "How we connect you with ideal clients",
        content: "Our AI analyzes client assessment gaps and matches them with your expertise. Higher match scores mean better client fit and success rates.",
        action: "View Opportunities",
        icon: "🎯"
      },
      {
        id: 4,
        title: "Start Engaging Clients",
        subtitle: "Respond to service requests and build relationships",
        content: "Browse available client requests, submit competitive proposals, and track your engagements through our platform.",
        action: "Find Clients",
        icon: "📈"
      }
    ],
    agency: [
      {
        id: 1,
        title: "Welcome to Agency Dashboard! 🏛️",
        subtitle: "Empower your regional economic development",
        content: "Manage sponsored businesses, track contract pipeline, and measure your program's economic impact on the community.",
        action: "Explore Dashboard",
        icon: "🌟"
      },
      {
        id: 2,
        title: "License Management System",
        subtitle: "Distribute assessment licenses to businesses",
        content: "Generate and distribute licenses to small businesses in your region. Track usage and measure program effectiveness.",
        action: "Manage Licenses",
        icon: "🎫"
      },
      {
        id: 3,
        title: "Resource Partner Network",
        subtitle: "Connect businesses with lenders and investors",
        content: "Use our RP CRM-lite system to facilitate connections between your sponsored businesses and resource partners like banks and investors.",
        action: "Explore RP Tools",
        icon: "🤝"
      },
      {
        id: 4,
        title: "Track Economic Impact",
        subtitle: "Measure and report program success",
        content: "Monitor contract awards, job creation, and economic development metrics to demonstrate your program's value to stakeholders.",
        action: "View Analytics",
        icon: "📊"
      }
    ],
    navigator: [
      {
        id: 1,
        title: "Welcome, Digital Navigator! 🧭",
        subtitle: "Guide businesses to procurement success",
        content: "Use AI-powered insights to provide personalized coaching and support to small businesses on their readiness journey.",
        action: "Start Guiding",
        icon: "🌟"
      },
      {
        id: 2,
        title: "AI Coaching Tools",
        subtitle: "Leverage intelligent insights for client support",
        content: "Identify at-risk clients, predict success rates, and get AI recommendations for improving client outcomes.",
        action: "Explore AI Tools",
        icon: "🤖"
      },
      {
        id: 3,
        title: "Regional Impact Tracking",
        subtitle: "Monitor community economic development",
        content: "Track regional procurement readiness improvements and measure the economic impact of your guidance.",
        action: "View Impact",
        icon: "🌍"
      },
      {
        id: 4,
        title: "Quality Assurance",
        subtitle: "Maintain platform standards and user success",
        content: "Review platform activity, approve new agencies and providers, and ensure quality standards across the ecosystem.",
        action: "Access Controls",
        icon: "✅"
      }
    ]
  };

  const steps = onboardingSteps[userRole] || [];
  const totalSteps = steps.length;
  const currentStepData = steps.find(step => step.id === currentStep);

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      completeOnboarding();
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const completeOnboarding = async () => {
    try {
      setLoading(true);
      
      // Mark onboarding as completed for this user
      await fetch(`${API}/users/onboarding-complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
        },
        body: JSON.stringify({ 
          user_id: me?.id,
          role: userRole,
          completed_at: new Date().toISOString()
        })
      });

      // Store completion in localStorage as backup
      localStorage.setItem(`onboarding_completed_${userRole}`, 'true');
      
      if (onComplete) {
        onComplete();
      }
    } catch (error) {
      console.error('Onboarding completion error:', error);
      // Complete anyway to not block the user
      if (onComplete) {
        onComplete();
      }
    } finally {
      setLoading(false);
    }
  };

  const skipOnboarding = () => {
    localStorage.setItem(`onboarding_completed_${userRole}`, 'true');
    if (onComplete) {
      onComplete();
    }
  };

  const executeStepAction = () => {
    switch (userRole) {
      case 'client':
        switch (currentStep) {
          case 2:
            navigate('/profile');
            break;
          case 3:
            navigate('/assessment');
            break;
          case 4:
            navigate('/knowledge');
            break;
          default:
            nextStep();
        }
        break;
      case 'provider':
        switch (currentStep) {
          case 2:
            navigate('/profile');
            break;
          case 3:
            // Stay on dashboard to show smart opportunities
            nextStep();
            break;
          case 4:
            navigate('/orders');
            break;
          default:
            nextStep();
        }
        break;
      case 'agency':
        switch (currentStep) {
          case 2:
            // Navigate to license management (would need to implement this route)
            nextStep();
            break;
          case 3:
            navigate('/rp');
            break;
          case 4:
            // Stay on dashboard to show analytics
            nextStep();
            break;
          default:
            nextStep();
        }
        break;
      case 'navigator':
        switch (currentStep) {
          case 2:
            // Stay on dashboard to show AI tools
            nextStep();
            break;
          case 3:
            // Stay on dashboard to show impact metrics
            nextStep();
            break;
          case 4:
            navigate('/approvals');
            break;
          default:
            nextStep();
        }
        break;
      default:
        nextStep();
    }
  };

  if (!currentStepData) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-primary bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full transform transition-all duration-300">
        {/* Progress Bar */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Getting Started</h3>
            <button 
              onClick={skipOnboarding}
              className="text-slate-500 hover:text-slate-700 text-sm"
            >
              Skip Guide
            </button>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>Step {currentStep} of {totalSteps}</span>
            <span>{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
          </div>
        </div>

        {/* Step Content */}
        <div className="p-8 text-center">
          <div className="text-6xl mb-6">{currentStepData.icon}</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">{currentStepData.title}</h2>
          <h3 className="text-lg text-blue-600 mb-4">{currentStepData.subtitle}</h3>
          <p className="text-slate-600 mb-8 leading-relaxed">{currentStepData.content}</p>
          
          {/* Action Buttons */}
          <div className="flex items-center justify-center gap-4">
            {currentStep > 1 && (
              <button
                onClick={prevStep}
                className="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              >
                ← Previous
              </button>
            )}
            <button
              onClick={currentStep === totalSteps ? completeOnboarding : executeStepAction}
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium shadow-lg"
            >
              {loading ? 'Completing...' : (currentStep === totalSteps ? 'Complete Onboarding' : currentStepData.action)}
            </button>
          </div>
        </div>

        {/* Step Indicators */}
        <div className="px-8 pb-6">
          <div className="flex justify-center gap-2">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  step.id <= currentStep
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500'
                    : 'bg-slate-200'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Hook to check onboarding status
export function useOnboardingStatus(userRole) {
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkOnboardingStatus = () => {
      // Check localStorage first for quick response
      const localStatus = localStorage.getItem(`onboarding_completed_${userRole}`);
      if (localStatus === 'true') {
        setNeedsOnboarding(false);
        setLoading(false);
        return;
      }

      // For new users or first-time login, show onboarding
      const lastLogin = localStorage.getItem('last_login_date');
      const today = new Date().toDateString();
      
      if (lastLogin !== today) {
        setNeedsOnboarding(true);
        localStorage.setItem('last_login_date', today);
      } else {
        setNeedsOnboarding(false);
      }
      
      setLoading(false);
    };

    if (userRole) {
      checkOnboardingStatus();
    }
  }, [userRole]);

  const completeOnboarding = () => {
    localStorage.setItem(`onboarding_completed_${userRole}`, 'true');
    setNeedsOnboarding(false);
  };

  return { needsOnboarding, loading, completeOnboarding };
}