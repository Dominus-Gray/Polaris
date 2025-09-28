import React, { Suspense, lazy, memo, useMemo, useCallback, useState, useEffect } from 'react';
import axios from 'axios';

// Performance-Optimized Component Loading
export const LazyComponentLoader = {
  // Lazy load heavy components for better initial load time
  AdvancedAnalyticsDashboard: lazy(() => import('./AdvancedAnalyticsDashboard')),
  SharedWorkspace: lazy(() => import('./SharedWorkspace')), 
  CommunityHub: lazy(() => import('./CommunityHub')),
  InteractiveTutorialSystem: lazy(() => import('./InteractiveTutorialSystem')),
  SupportTicketSystem: lazy(() => import('./SupportTicketSystem')),
  
  // Loading fallback component
  LoadingFallback: memo(({ componentName = 'Component' }) => (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading {componentName}...</p>
      </div>
    </div>
  ))
};

// Optimized Suspense Wrapper
export function OptimizedSuspense({ children, fallback, componentName }) {
  return (
    <Suspense fallback={fallback || <LazyComponentLoader.LoadingFallback componentName={componentName} />}>
      {children}
    </Suspense>
  );
}

// Memoized Dashboard Card Component
export const OptimizedDashboardCard = memo(({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = 'blue',
  trend = null,
  onClick = null 
}) => {
  const cardClass = useMemo(() => 
    `bg-gradient-to-r from-${color}-50 to-${color}-100 rounded-lg p-6 border border-${color}-200 transition-all duration-200 hover:shadow-lg ${onClick ? 'cursor-pointer' : ''}`,
    [color, onClick]
  );

  const handleClick = useCallback(() => {
    if (onClick) onClick();
  }, [onClick]);

  return (
    <div className={cardClass} onClick={handleClick}>
      <div className="flex items-center justify-between">
        <div>
          <div className={`text-3xl font-bold text-${color}-600`}>{value}</div>
          <div className="text-sm font-medium text-slate-700">{title}</div>
          {trend && (
            <div className={`text-xs font-medium ${trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
              {trend}
            </div>
          )}
        </div>
        <div className={`p-3 bg-${color}-200 rounded-lg`}>
          {icon}
        </div>
      </div>
      {subtitle && (
        <div className="text-xs text-slate-600 mt-2">{subtitle}</div>
      )}
    </div>
  );
});

// Virtual Scrolling for Large Lists
export function VirtualizedList({ 
  items, 
  renderItem, 
  itemHeight = 80, 
  containerHeight = 400,
  className = ""
}) {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerRef, setContainerRef] = useState(null);

  const visibleItems = useMemo(() => {
    const containerElement = containerRef;
    if (!containerElement) return items.slice(0, 10);

    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      ...item,
      originalIndex: startIndex + index
    }));
  }, [items, scrollTop, itemHeight, containerHeight, containerRef]);

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={setContainerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map((item) => (
          <div
            key={item.originalIndex}
            style={{
              position: 'absolute',
              top: item.originalIndex * itemHeight,
              height: itemHeight,
              width: '100%'
            }}
          >
            {renderItem(item, item.originalIndex)}
          </div>
        ))}
      </div>
    </div>
  );
}

// Optimized API Request Hook with Caching
export function useOptimizedAPIRequest(endpoint, dependencies = [], cacheTime = 300000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetch, setLastFetch] = useState(null);

  const cacheKey = useMemo(() => 
    `api_cache_${endpoint}_${JSON.stringify(dependencies)}`,
    [endpoint, dependencies]
  );

  const fetchData = useCallback(async (forceRefresh = false) => {
    try {
      // Check cache first
      if (!forceRefresh) {
        const cached = sessionStorage.getItem(cacheKey);
        const cacheTime = sessionStorage.getItem(`${cacheKey}_time`);
        
        if (cached && cacheTime) {
          const cacheAge = Date.now() - parseInt(cacheTime);
          if (cacheAge < 300000) { // 5 minutes
            setData(JSON.parse(cached));
            setLoading(false);
            return;
          }
        }
      }

      setLoading(true);
      setError(null);
      
      const response = await axios.get(endpoint);
      const result = response.data;
      
      // Cache the result
      sessionStorage.setItem(cacheKey, JSON.stringify(result));
      sessionStorage.setItem(`${cacheKey}_time`, Date.now().toString());
      
      setData(result);
      setLastFetch(Date.now());
      
    } catch (err) {
      setError(err);
      console.error('API request failed:', err);
    } finally {
      setLoading(false);
    }
  }, [endpoint, cacheKey]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refresh = useCallback(() => {
    fetchData(true);
  }, [fetchData]);

  return { data, loading, error, refresh, lastFetch };
}

// Performance-Optimized Component Factory
export function createOptimizedComponent(BaseComponent, displayName) {
  const OptimizedComponent = memo((props) => {
    return <BaseComponent {...props} />;
  });
  
  OptimizedComponent.displayName = displayName;
  return OptimizedComponent;
}

// Bundle Size Monitoring
export function BundleSizeMonitor() {
  const [bundleInfo, setBundleInfo] = useState(null);

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      // Monitor chunk loading
      const originalChunkLoad = window.__webpack_require__.e;
      if (originalChunkLoad) {
        window.__webpack_require__.e = function(chunkId) {
          console.log(`Loading chunk: ${chunkId}`);
          return originalChunkLoad.call(this, chunkId);
        };
      }

      // Get build info if available
      fetch('/build-manifest.json')
        .then(res => res.json())
        .then(data => setBundleInfo(data))
        .catch(() => {
          // No build manifest available
          setBundleInfo({ 
            totalSize: 'Unknown',
            chunkCount: 'Unknown',
            mainBundle: 'Unknown'
          });
        });
    }
  }, []);

  if (process.env.NODE_ENV !== 'development' || !bundleInfo) {
    return null;
  }

  return (
    <div className="fixed bottom-32 right-4 bg-gray-100 text-gray-700 text-xs p-2 rounded opacity-75 z-20">
      <div>Bundle: {bundleInfo.mainBundle}</div>
      <div>Chunks: {bundleInfo.chunkCount}</div>
    </div>
  );
}

// Memory Usage Optimization Hook
export function useMemoryOptimization() {
  const [memoryUsage, setMemoryUsage] = useState({ used: 0, limit: 0 });

  useEffect(() => {
    const checkMemory = () => {
      if ('memory' in performance) {
        setMemoryUsage({
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
        });
      }
    };

    checkMemory();
    const interval = setInterval(checkMemory, 10000); // Check every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const cleanupMemory = useCallback(() => {
    // Force garbage collection if available (development only)
    if (window.gc && process.env.NODE_ENV === 'development') {
      window.gc();
    }
    
    // Clear unnecessary caches
    const cacheKeys = Object.keys(sessionStorage);
    const oldCaches = cacheKeys.filter(key => {
      if (key.includes('api_cache_')) {
        const timeKey = `${key}_time`;
        const cacheTime = sessionStorage.getItem(timeKey);
        return cacheTime && (Date.now() - parseInt(cacheTime)) > 900000; // 15 minutes
      }
      return false;
    });
    
    oldCaches.forEach(key => {
      sessionStorage.removeItem(key);
      sessionStorage.removeItem(`${key}_time`);
    });
  }, []);

  return { memoryUsage, cleanupMemory };
}