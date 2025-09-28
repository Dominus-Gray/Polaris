import React, { useState, useEffect } from 'react';

// Performance Monitoring Widget for Development and User Feedback
export function PerformanceMonitoringWidget({ showInProduction = false }) {
  const [metrics, setMetrics] = useState({});
  const [isVisible, setIsVisible] = useState(false);
  const [performanceScore, setPerformanceScore] = useState(100);

  useEffect(() => {
    // Only show in development or when explicitly enabled
    if (process.env.NODE_ENV === 'development' || showInProduction) {
      initializePerformanceMonitoring();
    }
  }, [showInProduction]);

  const initializePerformanceMonitoring = () => {
    // Navigation Timing API
    if ('performance' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        
        entries.forEach((entry) => {
          if (entry.entryType === 'navigation') {
            const navigationEntry = entry;
            setMetrics(prev => ({
              ...prev,
              loadTime: Math.round(navigationEntry.loadEventEnd - navigationEntry.loadEventStart),
              domReady: Math.round(navigationEntry.domContentLoadedEventEnd - navigationEntry.domContentLoadedEventStart),
              firstPaint: Math.round(navigationEntry.responseEnd - navigationEntry.requestStart),
              ttfb: Math.round(navigationEntry.responseStart - navigationEntry.requestStart)
            }));
            
            // Calculate performance score
            const loadTime = navigationEntry.loadEventEnd - navigationEntry.loadEventStart;
            let score = 100;
            if (loadTime > 3000) score -= 30;
            else if (loadTime > 2000) score -= 20;
            else if (loadTime > 1000) score -= 10;
            
            setPerformanceScore(score);
          }
          
          if (entry.entryType === 'measure') {
            setMetrics(prev => ({
              ...prev,
              [entry.name]: Math.round(entry.duration)
            }));
          }
        });
      });

      observer.observe({ entryTypes: ['navigation', 'measure'] });
      
      // Clean up observer
      return () => observer.disconnect();
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMetricStatus = (metric, value) => {
    const thresholds = {
      loadTime: { good: 1000, fair: 2000 },
      domReady: { good: 500, fair: 1000 },
      firstPaint: { good: 1500, fair: 2500 },
      ttfb: { good: 200, fair: 500 }
    };

    const threshold = thresholds[metric];
    if (!threshold) return 'good';
    
    if (value <= threshold.good) return 'good';
    if (value <= threshold.fair) return 'fair';
    return 'poor';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return 'text-green-600';
      case 'fair': return 'text-yellow-600';
      case 'poor': return 'text-red-600';
      default: return 'text-slate-600';
    }
  };

  if (!isVisible && Object.keys(metrics).length === 0) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-32 w-8 h-8 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-full text-xs flex items-center justify-center z-30 transition-colors"
        title="Performance Metrics"
      >
        ⚡
      </button>
    );
  }

  return (
    <div className={`fixed bottom-4 right-32 bg-white border rounded-lg shadow-lg z-30 transition-all duration-200 ${
      isVisible ? 'w-64 p-3' : 'w-8 h-8'
    }`}>
      {!isVisible ? (
        <button
          onClick={() => setIsVisible(true)}
          className="w-full h-full flex items-center justify-center text-slate-600 hover:text-slate-900"
          title="Performance Metrics"
        >
          ⚡
        </button>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">⚡</span>
              <span className="font-medium text-slate-900 text-sm">Performance</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-bold ${getPerformanceColor(performanceScore)}`}>
                {performanceScore}
              </span>
              <button
                onClick={() => setIsVisible(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="space-y-2">
            {Object.entries(metrics).map(([metric, value]) => {
              const status = getMetricStatus(metric, value);
              const label = {
                loadTime: 'Load Time',
                domReady: 'DOM Ready',
                firstPaint: 'First Paint',
                ttfb: 'TTFB'
              }[metric] || metric;

              return (
                <div key={metric} className="flex items-center justify-between text-xs">
                  <span className="text-slate-600">{label}:</span>
                  <span className={`font-medium ${getStatusColor(status)}`}>
                    {value}ms
                  </span>
                </div>
              );
            })}
          </div>

          {/* Performance Tips */}
          {performanceScore < 80 && (
            <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
              <div className="font-medium text-yellow-800 mb-1">💡 Performance Tip</div>
              <div className="text-yellow-700">
                {performanceScore < 60 ? 
                  'Try refreshing the page or check your internet connection' :
                  'Performance is slightly slow - this may improve as content loads'
                }
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Page Load Progress Indicator
export function PageLoadProgress() {
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const handleStart = () => {
      setIsLoading(true);
      setProgress(0);
    };

    const handleProgress = (e) => {
      if (e.lengthComputable) {
        setProgress((e.loaded / e.total) * 100);
      }
    };

    const handleComplete = () => {
      setProgress(100);
      setTimeout(() => {
        setIsLoading(false);
        setProgress(0);
      }, 500);
    };

    // Listen for fetch events (requires custom implementation)
    window.addEventListener('fetchStart', handleStart);
    window.addEventListener('fetchProgress', handleProgress);
    window.addEventListener('fetchComplete', handleComplete);

    return () => {
      window.removeEventListener('fetchStart', handleStart);
      window.removeEventListener('fetchProgress', handleProgress);
      window.removeEventListener('fetchComplete', handleComplete);
    };
  }, []);

  if (!isLoading) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <div className="h-1 bg-slate-200">
        <div 
          className="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

// Resource Usage Monitor
export function ResourceUsageMonitor() {
  const [usage, setUsage] = useState({ memory: 0, timing: {} });

  useEffect(() => {
    const updateUsage = () => {
      // Memory usage (if available)
      if ('memory' in performance) {
        setUsage(prev => ({
          ...prev,
          memory: performance.memory.usedJSHeapSize / 1024 / 1024 // MB
        }));
      }

      // Timing measurements
      if ('now' in performance) {
        const now = performance.now();
        setUsage(prev => ({
          ...prev,
          timing: {
            ...prev.timing,
            lastUpdate: now
          }
        }));
      }
    };

    const interval = setInterval(updateUsage, 5000); // Update every 5 seconds
    updateUsage(); // Initial update

    return () => clearInterval(interval);
  }, []);

  // Only show in development
  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div className="fixed bottom-20 right-4 bg-gray-100 text-gray-700 text-xs p-2 rounded opacity-75 z-20">
      <div>Mem: {usage.memory.toFixed(1)}MB</div>
      {usage.timing.lastUpdate && (
        <div>Uptime: {(usage.timing.lastUpdate / 1000 / 60).toFixed(1)}m</div>
      )}
    </div>
  );
}