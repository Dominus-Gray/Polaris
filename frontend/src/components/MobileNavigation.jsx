import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function MobileNavigation({ userRole }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Role-specific navigation items
  const navigationItems = {
    client: [
      { id: 'home', label: 'Dashboard', icon: '🏠', path: '/home' },
      { id: 'assessment', label: 'Assessment', icon: '📝', path: '/assessment' },
      { id: 'services', label: 'Find Help', icon: '🔍', path: '/service-request' },
      { id: 'knowledge', label: 'Resources', icon: '📚', path: '/knowledge' },
      { id: 'rp', label: 'Share Data', icon: '🤝', path: '/rp/share' }
    ],
    provider: [
      { id: 'home', label: 'Dashboard', icon: '📊', path: '/home' },
      { id: 'opportunities', label: 'Opportunities', icon: '🎯', path: '/home' },
      { id: 'orders', label: 'Orders', icon: '📋', path: '/orders' },
      { id: 'earnings', label: 'Earnings', icon: '💰', path: '/earnings' },
      { id: 'profile', label: 'Profile', icon: '👤', path: '/profile' }
    ],
    agency: [
      { id: 'home', label: 'Dashboard', icon: '🏛️', path: '/home' },
      { id: 'businesses', label: 'Businesses', icon: '🏢', path: '/home' },
      { id: 'rp-leads', label: 'RP Leads', icon: '📊', path: '/rp' },
      { id: 'rp-admin', label: 'RP Admin', icon: '⚙️', path: '/rp/requirements' },
      { id: 'analytics', label: 'Analytics', icon: '📈', path: '/analytics' }
    ],
    navigator: [
      { id: 'home', label: 'Control Center', icon: '🧭', path: '/home' },
      { id: 'approvals', label: 'Approvals', icon: '✅', path: '/approvals' },
      { id: 'analytics', label: 'Analytics', icon: '📈', path: '/analytics' },
      { id: 'insights', label: 'AI Insights', icon: '🤖', path: '/home' },
      { id: 'settings', label: 'Settings', icon: '⚙️', path: '/settings' }
    ]
  };

  const items = navigationItems[userRole] || [];
  const currentPath = location.pathname;

  // Don't show on desktop or if no items
  if (!isMobile || items.length === 0) {
    return null;
  }

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-40 md:hidden">
        <div className="grid grid-cols-5 gap-1">
          {items.map((item) => {
            const isActive = currentPath === item.path || 
                           (item.path === '/home' && currentPath === '/');
            
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`flex flex-col items-center justify-center py-2 px-1 text-xs transition-colors ${
                  isActive 
                    ? 'text-blue-600 bg-blue-50' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="text-lg mb-1">{item.icon}</span>
                <span className="truncate w-full">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Mobile Floating Action Button */}
      <div className="fixed bottom-20 right-4 z-50 md:hidden">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        >
          {isOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          )}
        </button>

        {/* Quick Actions Menu */}
        {isOpen && (
          <div className="absolute bottom-16 right-0 bg-white rounded-2xl shadow-xl border p-4 min-w-48">
            <h3 className="font-semibold text-slate-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {userRole === 'client' && (
                <>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/assessment'); setIsOpen(false); }}
                  >
                    <span>📝</span>
                    <span className="text-sm">Start Assessment</span>
                  </button>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/service-request'); setIsOpen(false); }}
                  >
                    <span>🔍</span>
                    <span className="text-sm">Find Expert Help</span>
                  </button>
                </>
              )}
              
              {userRole === 'provider' && (
                <>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/orders'); setIsOpen(false); }}
                  >
                    <span>📋</span>
                    <span className="text-sm">View Orders</span>
                  </button>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/profile'); setIsOpen(false); }}
                  >
                    <span>👤</span>
                    <span className="text-sm">Update Profile</span>
                  </button>
                </>
              )}
              
              {userRole === 'agency' && (
                <>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/rp'); setIsOpen(false); }}
                  >
                    <span>📊</span>
                    <span className="text-sm">RP Leads</span>
                  </button>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { window.location.href = '/rp/requirements'; setIsOpen(false); }}
                  >
                    <span>⚙️</span>
                    <span className="text-sm">RP Admin</span>
                  </button>
                </>
              )}
              
              {userRole === 'navigator' && (
                <>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/approvals'); setIsOpen(false); }}
                  >
                    <span>✅</span>
                    <span className="text-sm">Approvals</span>
                  </button>
                  <button 
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-50 flex items-center gap-3"
                    onClick={() => { navigate('/analytics'); setIsOpen(false); }}
                  >
                    <span>📈</span>
                    <span className="text-sm">Analytics</span>
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Mobile spacing for bottom navigation */}
      <div className="h-16 md:hidden" />
    </>
  );
}