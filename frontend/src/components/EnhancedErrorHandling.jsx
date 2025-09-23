import React, { useState, useCallback } from 'react';
import axios from 'axios';

// Smart Retry Hook with exponential backoff
export function useSmartRetry(apiCall, maxRetries = 3) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const executeWithRetry = useCallback(async (...args) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        setRetryCount(i);
        setIsRetrying(i > 0);
        
        const result = await apiCall(...args);
        
        // Success - reset retry state
        setIsRetrying(false);
        setRetryCount(0);
        return result;
        
      } catch (error) {
        if (i === maxRetries - 1) {
          // Final attempt failed
          setIsRetrying(false);
          throw new Error(`Failed after ${maxRetries} attempts: ${error.message}`);
        }
        
        // Wait before retry with exponential backoff
        const delay = 1000 * Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }, [apiCall, maxRetries]);

  return { executeWithRetry, isRetrying, retryCount };
}

// Enhanced Empty State Component with Actionable Guidance
export function EmptyStateWithGuidance({ type, userRole, onAction }) {
  const getEmptyStateConfig = (type, userRole) => {
    const configs = {
      assessments: {
        client: {
          icon: '📝',
          title: 'Ready to Start Your Assessment Journey?',
          description: 'Discover your procurement readiness across 10 critical business areas.',
          actions: [
            { id: 'start_assessment', label: 'Start First Assessment', primary: true },
            { id: 'learn_more', label: 'Learn About Assessments', primary: false }
          ]
        }
      },
      service_requests: {
        client: {
          icon: '🔍',
          title: 'No Service Requests Yet',
          description: 'Connect with expert service providers to accelerate your readiness.',
          actions: [
            { id: 'create_request', label: 'Find Expert Help', primary: true },
            { id: 'browse_providers', label: 'Browse Service Providers', primary: false }
          ]
        }
      },
      rp_leads: {
        client: {
          icon: '🤝',
          title: 'Share Your Progress with Resource Partners',
          description: 'Connect with lenders, investors, and contractors looking for qualified businesses.',
          actions: [
            { id: 'create_package', label: 'Create Share Package', primary: true },
            { id: 'learn_rp', label: 'Learn About Resource Partners', primary: false }
          ]
        },
        agency: {
          icon: '📊',
          title: 'No RP Leads to Review',
          description: 'Client-generated leads will appear here for your review and management.',
          actions: [
            { id: 'manage_requirements', label: 'Configure RP Requirements', primary: true },
            { id: 'invite_clients', label: 'Invite More Clients', primary: false }
          ]
        }
      },
      opportunities: {
        provider: {
          icon: '🎯',
          title: 'No Opportunities Available',
          description: 'New client opportunities will appear here based on your expertise.',
          actions: [
            { id: 'update_profile', label: 'Update Your Profile', primary: true },
            { id: 'expand_services', label: 'Add Service Areas', primary: false }
          ]
        }
      }
    };

    return configs[type]?.[userRole] || {
      icon: '📂',
      title: 'No Data Available',
      description: 'Content will appear here as you use the platform.',
      actions: [{ id: 'refresh', label: 'Refresh', primary: true }]
    };
  };

  const config = getEmptyStateConfig(type, userRole);

  return (
    <div className="text-center py-12 px-6">
      <div className="text-6xl mb-4">{config.icon}</div>
      <h3 className="text-xl font-semibold text-slate-900 mb-3">{config.title}</h3>
      <p className="text-slate-600 mb-6 max-w-md mx-auto leading-relaxed">{config.description}</p>
      
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        {config.actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction?.(action.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              action.primary
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                : 'border border-slate-300 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {action.label}
          </button>
        ))}
      </div>
      
      {/* Helpful tips based on context */}
      <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 max-w-lg mx-auto">
        <div className="flex items-center gap-2 text-sm text-blue-800 mb-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium">💡 Pro Tip</span>
        </div>
        <p className="text-sm text-blue-700">
          {type === 'assessments' ? 'Start with Legal & Compliance - it provides the foundation for all other areas.' :
           type === 'service_requests' ? 'Be specific about your needs and timeline for better provider matches.' :
           type === 'rp_leads' ? 'Complete more assessments to strengthen your data package appeal.' :
           'Regular activity helps maintain momentum and improves your readiness score.'}
        </p>
      </div>
    </div>
  );
}

// Enhanced Error Boundary with Recovery Options
export class SmartErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    
    // Log error to monitoring system
    console.error('Error Boundary caught error:', error, errorInfo);
    
    // Send error to backend for tracking
    axios.post('/api/errors/report', {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
      user_agent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }).catch(() => {
      // Silent fail for error reporting
    });
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-slate-900 mb-3">
              Oops! Something went wrong
            </h2>
            <p className="text-slate-600 mb-6">
              We encountered an unexpected error. Don't worry - your data is safe and we're working to fix this.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={this.handleRetry}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Try Again {this.state.retryCount > 0 && `(Attempt ${this.state.retryCount + 1})`}
              </button>
              
              <button
                onClick={this.handleReload}
                className="w-full px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              >
                Reload Page
              </button>
              
              <button
                onClick={() => window.location.href = 'mailto:support@polaris.platform?subject=Error Report'}
                className="w-full px-4 py-3 text-blue-600 hover:text-blue-700 transition-colors text-sm"
              >
                Report This Issue
              </button>
            </div>
            
            {/* Error details for debugging (only in development) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="text-sm text-slate-500 cursor-pointer">
                  Error Details (Development Only)
                </summary>
                <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Network Status Indicator
export function NetworkStatusIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineMessage(false);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineMessage(true);
      // Hide message after 5 seconds
      setTimeout(() => setShowOfflineMessage(false), 5000);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOnline || showOfflineMessage) {
    return (
      <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300 ${
        isOnline ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      }`}>
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-200' : 'bg-red-200 animate-pulse'}`} />
          {isOnline ? 'Connection restored' : 'You\'re offline - some features may be limited'}
        </div>
      </div>
    );
  }

  return null;
}