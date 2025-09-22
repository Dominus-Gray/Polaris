import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function IntelligentNotifications({ userRole }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showPanel, setShowPanel] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, [userRole]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/ai/recommendations/${userRole}`);
      
      // Transform AI recommendations into notifications
      const recommendations = response.data.recommendations || [];
      const notificationData = recommendations.map((rec, index) => ({
        id: `rec_${index}`,
        type: rec.type,
        title: rec.title,
        message: rec.description,
        action: rec.action,
        priority: rec.priority,
        url: rec.url,
        timestamp: new Date().toISOString(),
        read: false,
        metadata: rec.metadata || {}
      }));

      setNotifications(notificationData);
      setUnreadCount(notificationData.filter(n => !n.read).length);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const handleNotificationAction = (notification) => {
    markAsRead(notification.id);
    setShowPanel(false);
    
    if (notification.url) {
      window.location.href = notification.url;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'assessment_start':
      case 'assessment_continue': return '📝';
      case 'service_discovery': return '🔍';
      case 'high_match_opportunity': return '🎯';
      case 'profile_optimization': return '⭐';
      case 'program_optimization': return '📊';
      case 'rp_expansion': return '🤝';
      case 'intervention_needed': return '⚠️';
      case 'success_opportunity': return '🏆';
      default: return '💡';
    }
  };

  return (
    <>
      {/* Notification Bell Icon */}
      <div className="relative">
        <button
          onClick={() => setShowPanel(!showPanel)}
          className="relative p-2 text-slate-600 hover:text-slate-900 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 3h11v2H4zm0 4h11v2H4zm0 4h11v2H4zm0 4h6v2H4z" />
          </svg>
          
          {unreadCount > 0 && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </div>
          )}
        </button>

        {/* Notification Panel */}
        {showPanel && (
          <div className="absolute top-12 right-0 w-80 bg-white rounded-lg shadow-xl border z-50 max-h-96 overflow-hidden">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-900">Smart Recommendations</h3>
                <button 
                  onClick={() => setShowPanel(false)}
                  className="text-slate-500 hover:text-slate-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {unreadCount > 0 && (
                <p className="text-sm text-slate-600 mt-1">{unreadCount} new recommendations</p>
              )}
            </div>
            
            <div className="max-h-80 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-sm text-slate-600 mt-2">Loading recommendations...</p>
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-4 text-center text-slate-500">
                  <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <p className="text-sm">No new recommendations</p>
                </div>
              ) : (
                <div className="divide-y">
                  {notifications.map((notification) => (
                    <div 
                      key={notification.id}
                      className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${
                        !notification.read ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleNotificationAction(notification)}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 text-lg">
                          {getTypeIcon(notification.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-slate-900 text-sm">{notification.title}</h4>
                            <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(notification.priority)}`}>
                              {notification.priority}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600 mb-2">{notification.message}</p>
                          {notification.action && (
                            <button className="text-blue-600 hover:text-blue-700 text-xs font-medium">
                              {notification.action} →
                            </button>
                          )}
                          {notification.metadata && Object.keys(notification.metadata).length > 0 && (
                            <div className="mt-2 text-xs text-slate-500">
                              {Object.entries(notification.metadata).map(([key, value]) => (
                                <span key={key} className="mr-3">
                                  {key.replace('_', ' ')}: {value}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {notifications.length > 0 && (
              <div className="p-3 border-t bg-slate-50">
                <button 
                  onClick={() => setNotifications(prev => prev.map(n => ({ ...n, read: true })))}
                  className="text-sm text-blue-600 hover:text-blue-700 w-full text-center"
                >
                  Mark all as read
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {showPanel && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowPanel(false)}
        />
      )}
    </>
  );
}