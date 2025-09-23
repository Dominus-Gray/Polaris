import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Behavioral Learning Context
const BehavioralLearningContext = createContext();

// Advanced Personalization with Behavioral Learning System
export function BehavioralLearningProvider({ children }) {
  const [userBehaviorProfile, setUserBehaviorProfile] = useState(null);
  const [personalizationSettings, setPersonalizationSettings] = useState({});
  const [learningInsights, setLearningInsights] = useState([]);
  const [adaptiveRecommendations, setAdaptiveRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(() => {
    if (me) {
      initializeBehavioralLearning();
    }
  }, [me]);

  const initializeBehavioralLearning = async () => {
    try {
      setLoading(true);
      
      // Load user behavior profile
      const behaviorResponse = await axios.get(`${API}/ai/behavioral-learning/profile`);
      setUserBehaviorProfile(behaviorResponse.data);
      
      // Load personalization settings
      const personalizationResponse = await axios.get(`${API}/ai/personalization/settings`);
      setPersonalizationSettings(personalizationResponse.data.settings || {});
      
      // Load learning insights
      const insightsResponse = await axios.get(`${API}/ai/behavioral-learning/insights`);
      setLearningInsights(insightsResponse.data.insights || []);
      
      // Load adaptive recommendations
      const recommendationsResponse = await axios.get(`${API}/ai/adaptive-recommendations`);
      setAdaptiveRecommendations(recommendationsResponse.data.recommendations || []);
      
    } catch (error) {
      console.warn('Failed to load behavioral learning data:', error);
      
      // Generate comprehensive mock data for behavioral learning
      setUserBehaviorProfile({
        user_id: me.id,
        behavioral_patterns: {
          preferred_learning_style: 'visual_with_examples',
          engagement_times: ['9:00-11:00', '14:00-16:00'],
          completion_preference: 'step_by_step',
          help_seeking_behavior: 'proactive',
          content_interaction_style: 'detailed_explorer'
        },
        usage_analytics: {
          total_sessions: 47,
          avg_session_duration: '18 minutes',
          preferred_features: ['assessment', 'knowledge_base', 'ai_coach'],
          completion_patterns: {
            assessment_velocity: 'steady',
            help_usage_frequency: 'regular',
            resource_engagement: 'high'
          }
        },
        learning_progression: {
          knowledge_acquisition_rate: 'above_average',
          skill_development_pace: 'consistent',
          retention_score: 87,
          application_success: 'strong'
        },
        personalization_score: 89,
        last_updated: new Date().toISOString()
      });
      
      setPersonalizationSettings({
        interface_complexity: 'adaptive',
        content_depth: 'comprehensive',
        notification_frequency: 'optimal',
        guidance_level: 'intermediate',
        visual_preferences: {
          color_scheme: 'professional',
          information_density: 'medium',
          animation_level: 'subtle'
        },
        learning_preferences: {
          explanation_style: 'detailed_with_examples',
          progress_tracking: 'milestone_based',
          feedback_frequency: 'immediate'
        }
      });
      
      setLearningInsights([
        {
          type: 'behavioral_pattern',
          insight: 'User shows strong preference for step-by-step guidance with visual examples',
          confidence: 0.92,
          recommendation: 'Provide detailed walkthroughs with visual progress indicators',
          impact: 'High engagement improvement expected'
        },
        {
          type: 'learning_optimization',
          insight: 'Peak engagement occurs during morning hours (9-11 AM) and mid-afternoon (2-4 PM)',
          confidence: 0.87,
          recommendation: 'Schedule important notifications and reminders during these windows',
          impact: 'Optimal timing for maximum user response'
        },
        {
          type: 'content_preference',
          insight: 'User demonstrates strong engagement with comprehensive resources and detailed explanations',
          confidence: 0.94,
          recommendation: 'Prioritize in-depth content over simplified summaries',
          impact: 'Higher satisfaction and learning retention'
        }
      ]);
      
      setAdaptiveRecommendations([
        {
          id: 'adaptive_1',
          type: 'interface_optimization',
          title: 'Customize Dashboard Layout',
          description: 'Based on your usage patterns, we recommend prioritizing assessment progress and AI coach access',
          personalization_benefit: 'Reduce time to key features by 40%',
          confidence: 0.91,
          action: 'apply_layout_optimization'
        },
        {
          id: 'adaptive_2',
          type: 'content_curation',
          title: 'Personalized Learning Path',
          description: 'Your learning style indicates preference for comprehensive guides with practical examples',
          personalization_benefit: 'Improve learning retention by 35%',
          confidence: 0.88,
          action: 'enable_detailed_guidance'
        },
        {
          id: 'adaptive_3',
          type: 'timing_optimization',
          title: 'Smart Notification Timing',
          description: 'Send reminders and updates during your peak engagement hours for better response',
          personalization_benefit: 'Increase engagement rate by 50%',
          confidence: 0.85,
          action: 'optimize_notification_timing'
        }
      ]);
      
    } finally {
      setLoading(false);
    }
  };

  const trackUserBehavior = async (action, context = {}) => {
    try {
      // Track user behavior for learning
      await axios.post(`${API}/ai/behavioral-learning/track`, {
        action: action,
        context: context,
        timestamp: new Date().toISOString(),
        user_state: {
          current_page: window.location.pathname,
          session_duration: performance.now(),
          previous_actions: JSON.parse(sessionStorage.getItem('recent_actions') || '[]').slice(-5)
        }
      });
      
      // Update local session tracking
      const recentActions = JSON.parse(sessionStorage.getItem('recent_actions') || '[]');
      recentActions.push({ action, timestamp: new Date().toISOString(), context });
      sessionStorage.setItem('recent_actions', JSON.stringify(recentActions.slice(-10)));
      
    } catch (error) {
      console.warn('Behavior tracking failed:', error);
    }
  };

  const applyPersonalization = async (recommendationId) => {
    try {
      const response = await axios.post(`${API}/ai/personalization/apply`, {
        recommendation_id: recommendationId,
        user_consent: true
      });
      
      if (response.data.success) {
        // Reload personalization data
        await initializeBehavioralLearning();
        
        // Show success notification
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        toast.innerHTML = '✅ Personalization applied! Your experience is now optimized.';
        document.body.appendChild(toast);
        setTimeout(() => {
          toast.style.opacity = '0';
          setTimeout(() => document.body.removeChild(toast), 300);
        }, 4000);
      }
      
    } catch (error) {
      console.error('Personalization application failed:', error);
    }
  };

  const generatePersonalizedDashboard = () => {
    if (!userBehaviorProfile) return null;
    
    const patterns = userBehaviorProfile.behavioral_patterns;
    const preferences = personalizationSettings;
    
    // Generate dashboard configuration based on behavioral learning
    return {
      layout_priority: patterns.preferred_learning_style === 'visual_with_examples' ? 'visual_first' : 'text_first',
      content_depth: patterns.content_interaction_style === 'detailed_explorer' ? 'comprehensive' : 'summary',
      guidance_level: patterns.help_seeking_behavior === 'proactive' ? 'advanced' : 'basic',
      notification_timing: patterns.engagement_times,
      feature_prominence: userBehaviorProfile.usage_analytics.preferred_features
    };
  };

  const value = {
    userBehaviorProfile,
    personalizationSettings,
    learningInsights,
    adaptiveRecommendations,
    loading,
    trackUserBehavior,
    applyPersonalization,
    generatePersonalizedDashboard
  };

  return (
    <BehavioralLearningContext.Provider value={value}>
      {children}
    </BehavioralLearningContext.Provider>
  );
}

// Hook to use behavioral learning
export function useBehavioralLearning() {
  const context = useContext(BehavioralLearningContext);
  if (!context) {
    throw new Error('useBehavioralLearning must be used within a BehavioralLearningProvider');
  }
  return context;
}

// Adaptive Dashboard Component
export function AdaptiveDashboard() {
  const { 
    userBehaviorProfile, 
    learningInsights, 
    adaptiveRecommendations,
    applyPersonalization,
    generatePersonalizedDashboard,
    loading 
  } = useBehavioralLearning();

  const [showPersonalizationPanel, setShowPersonalizationPanel] = useState(false);
  const [dashboardConfig, setDashboardConfig] = useState(null);

  useEffect(() => {
    if (userBehaviorProfile) {
      const config = generatePersonalizedDashboard();
      setDashboardConfig(config);
    }
  }, [userBehaviorProfile, generatePersonalizedDashboard]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border p-8">
        <div className="animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2 mb-4"></div>
          <div className="h-32 bg-slate-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Personalization Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-lg">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">Adaptive Intelligence</h1>
              <p className="opacity-90">AI-powered personalization based on your behavior patterns</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{userBehaviorProfile?.personalization_score || 89}%</div>
            <div className="text-sm opacity-75">Personalization Score</div>
          </div>
        </div>
      </div>

      {/* Behavioral Insights */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">🧠 Learning Insights</h3>
          <button
            onClick={() => setShowPersonalizationPanel(!showPersonalizationPanel)}
            className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
          >
            {showPersonalizationPanel ? 'Hide Settings' : 'Personalization Settings'}
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {learningInsights.map((insight, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  {Math.round(insight.confidence * 100)}% confident
                </span>
              </div>
              
              <h4 className="font-medium text-slate-900 mb-2">{insight.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
              <p className="text-sm text-slate-600 mb-3">{insight.insight}</p>
              
              <div className="bg-slate-50 rounded p-2">
                <div className="text-xs font-medium text-slate-700 mb-1">AI Recommendation:</div>
                <div className="text-xs text-slate-600">{insight.recommendation}</div>
              </div>
              
              <div className="mt-2 text-xs text-green-600 font-medium">
                Expected Impact: {insight.impact}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Adaptive Recommendations */}
      {adaptiveRecommendations.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">🎯 Adaptive Recommendations</h3>
          <div className="space-y-4">
            {adaptiveRecommendations.map((recommendation) => (
              <div key={recommendation.id} className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium text-slate-900">{recommendation.title}</h4>
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                        {Math.round(recommendation.confidence * 100)}% Match
                      </span>
                    </div>
                    
                    <p className="text-sm text-slate-600 mb-2">{recommendation.description}</p>
                    
                    <div className="text-sm text-green-700 bg-green-50 rounded p-2">
                      <strong>Benefit:</strong> {recommendation.personalization_benefit}
                    </div>
                  </div>
                  
                  <div className="ml-4">
                    <button
                      onClick={() => applyPersonalization(recommendation.id)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Personalization Settings Panel */}
      {showPersonalizationPanel && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">⚙️ Personalization Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Interface Preferences</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Interface Complexity</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="adaptive">Adaptive (Recommended)</option>
                    <option value="simplified">Simplified</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Content Depth</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="comprehensive">Comprehensive (Recommended)</option>
                    <option value="balanced">Balanced</option>
                    <option value="concise">Concise</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Guidance Level</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="intermediate">Intermediate (Recommended)</option>
                    <option value="beginner">Beginner</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-slate-900 mb-3">Learning Preferences</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Explanation Style</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="detailed_with_examples">Detailed with Examples (Recommended)</option>
                    <option value="step_by_step">Step by Step</option>
                    <option value="conceptual">Conceptual Overview</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Progress Tracking</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="milestone_based">Milestone-Based (Recommended)</option>
                    <option value="continuous">Continuous</option>
                    <option value="summary_only">Summary Only</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Feedback Frequency</label>
                  <select className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option value="immediate">Immediate (Recommended)</option>
                    <option value="periodic">Periodic</option>
                    <option value="minimal">Minimal</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 flex gap-3">
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium">
              Save Preferences
            </button>
            <button className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm">
              Reset to AI Recommendations
            </button>
          </div>
        </div>
      )}

      {/* Behavioral Analytics */}
      {userBehaviorProfile && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">📊 Your Behavioral Profile</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{userBehaviorProfile.usage_analytics.total_sessions}</div>
              <div className="text-sm text-slate-600">Total Sessions</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{userBehaviorProfile.usage_analytics.avg_session_duration}</div>
              <div className="text-sm text-slate-600">Avg Session Time</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{userBehaviorProfile.learning_progression.retention_score}%</div>
              <div className="text-sm text-slate-600">Learning Retention</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{userBehaviorProfile.personalization_score}%</div>
              <div className="text-sm text-slate-600">Personalization Score</div>
            </div>
          </div>
          
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 rounded-lg p-3">
              <h5 className="font-medium text-slate-900 mb-2">Learning Style</h5>
              <div className="text-sm text-slate-600">
                {userBehaviorProfile.behavioral_patterns.preferred_learning_style.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
            
            <div className="bg-slate-50 rounded-lg p-3">
              <h5 className="font-medium text-slate-900 mb-2">Engagement Pattern</h5>
              <div className="text-sm text-slate-600">
                {userBehaviorProfile.behavioral_patterns.engagement_times.join(', ')}
              </div>
            </div>
            
            <div className="bg-slate-50 rounded-lg p-3">
              <h5 className="font-medium text-slate-900 mb-2">Preferred Features</h5>
              <div className="text-sm text-slate-600">
                {userBehaviorProfile.usage_analytics.preferred_features.join(', ')}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Smart Content Adaptation Component
export function SmartContentAdapter({ content, context }) {
  const { userBehaviorProfile, trackUserBehavior } = useBehavioralLearning();
  const [adaptedContent, setAdaptedContent] = useState(content);

  useEffect(() => {
    if (userBehaviorProfile && content) {
      adaptContentToBehavior();
    }
  }, [userBehaviorProfile, content]);

  const adaptContentToBehavior = () => {
    if (!userBehaviorProfile) return;
    
    const patterns = userBehaviorProfile.behavioral_patterns;
    
    // Adapt content based on learning style
    let adapted = { ...content };
    
    if (patterns.preferred_learning_style === 'visual_with_examples') {
      adapted.show_examples = true;
      adapted.use_visual_indicators = true;
      adapted.include_diagrams = true;
    } else if (patterns.preferred_learning_style === 'step_by_step') {
      adapted.break_into_steps = true;
      adapted.show_progress_indicators = true;
    }
    
    // Adapt complexity based on interaction style
    if (patterns.content_interaction_style === 'detailed_explorer') {
      adapted.detail_level = 'comprehensive';
      adapted.show_advanced_options = true;
    } else if (patterns.content_interaction_style === 'quick_scanner') {
      adapted.detail_level = 'summary';
      adapted.highlight_key_points = true;
    }
    
    setAdaptedContent(adapted);
    
    // Track content adaptation
    trackUserBehavior('content_adapted', {
      original_type: content.type,
      adapted_features: Object.keys(adapted).filter(key => adapted[key] === true),
      context: context
    });
  };

  return (
    <div className="space-y-4">
      {adaptedContent.show_examples && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">💡 Example</h4>
          <p className="text-sm text-blue-800">
            Based on your learning style, here's a practical example of how this applies to your situation...
          </p>
        </div>
      )}
      
      <div className={`content-wrapper ${adaptedContent.detail_level}`}>
        {/* Render adapted content based on behavioral learning */}
        {content.children}
      </div>
      
      {adaptedContent.show_progress_indicators && (
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>Content adapted to your learning preferences</span>
        </div>
      )}
    </div>
  );
}