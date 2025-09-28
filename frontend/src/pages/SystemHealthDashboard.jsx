import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://nextjs-mongo-polaris.preview.emergentagent.com/api';

function SystemHealthDashboard() {
  const [healthData, setHealthData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [slaData, setSlaData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadHealthData();
    loadAlerts();
    loadSlaData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadHealthData();
        loadAlerts();
      }, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadHealthData = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API}/system/health-report`, { headers });
      setHealthData(response.data);
    } catch (error) {
      console.error('Error loading health data:', error);
      // Fallback to basic health check
      try {
        const response = await axios.get(`${API}/system/health`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('polaris_token')}` } });
        setHealthData({
          status: response.data.status,
          status_score: response.data.overall_score,
          metrics: { system: {}, application: {}, database: {} },
          timestamp: new Date().toISOString()
        });
      } catch (fallbackError) {
        console.error('Error loading fallback health data:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadAlerts = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API}/system/alerts`, { headers });
      setAlerts(response.data.current_alerts || []);
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const loadSlaData = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API}/system/sla-compliance`, { headers });
      setSlaData(response.data);
    } catch (error) {
      console.error('Error loading SLA data:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-100 border-red-200 text-red-800';
      case 'warning': return 'bg-yellow-100 border-yellow-200 text-yellow-800';
      case 'info': return 'bg-blue-100 border-blue-200 text-blue-800';
      default: return 'bg-gray-100 border-gray-200 text-gray-800';
    }
  };

  const formatMetricValue = (value, unit = '') => {
    if (typeof value === 'number') {
      return `${value.toFixed(2)}${unit}`;
    }
    return value || 'N/A';
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-7xl">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/2 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[1,2,3].map(i => (
              <div key={i} className="h-32 bg-slate-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-7xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-600 to-slate-700 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">System Health Dashboard</h1>
            <p className="text-slate-100">Production monitoring and performance metrics</p>
            <div className="text-sm text-slate-200 mt-2">
              Last updated: {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleString() : 'N/A'}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(healthData?.status)}`}>
                <span className="w-2 h-2 rounded-full bg-current mr-2"></span>
                {healthData?.status?.toUpperCase() || 'UNKNOWN'}
              </div>
              <div className="text-slate-200 text-xs mt-1">System Status</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{healthData?.status_score || 0}%</div>
              <div className="text-slate-200 text-xs">Health Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            className="btn btn-primary btn-sm"
            onClick={() => {
              loadHealthData();
              loadAlerts();
              loadSlaData();
            }}
          >
            🔄 Refresh
          </button>
          
          <label className="flex items-center gap-2">
            <input 
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4"
            />
            <span className="text-sm">Auto-refresh</span>
          </label>
          
          <select 
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="input input-sm"
            disabled={!autoRefresh}
          >
            <option value={10}>10 seconds</option>
            <option value={30}>30 seconds</option>
            <option value={60}>1 minute</option>
            <option value={300}>5 minutes</option>
          </select>
        </div>

        <div className="text-sm text-slate-600">
          {alerts.length > 0 && (
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
            🚨 Active Alerts
          </h2>
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div key={index} className={`border rounded-lg p-4 ${getAlertColor(alert.level)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium">{alert.message}</h3>
                    <p className="text-sm mt-1">Type: {alert.type}</p>
                    {alert.current_value && alert.threshold && (
                      <p className="text-xs mt-1">
                        Current: {formatMetricValue(alert.current_value)} | Threshold: {formatMetricValue(alert.threshold)}
                      </p>
                    )}
                  </div>
                  <div className="text-xs text-right">
                    <div className="font-medium uppercase">{alert.level}</div>
                    <div>{new Date(alert.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* System Metrics */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">System Resources</h2>
          
          <div className="space-y-4">
            {healthData?.metrics?.system && (
              <>
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">Memory Usage</span>
                  <div className="text-right">
                    <div className="font-bold">{formatMetricValue(healthData.metrics.system.memory_percent, '%')}</div>
                    <div className="text-xs text-slate-600">
                      Available: {formatMetricValue(healthData.metrics.system.memory_available_gb, 'GB')}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">CPU Usage</span>
                  <div className="text-right">
                    <div className="font-bold">{formatMetricValue(healthData.metrics.system.cpu_percent, '%')}</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">Disk Usage</span>
                  <div className="text-right">
                    <div className="font-bold">{formatMetricValue(healthData.metrics.system.disk_percent, '%')}</div>
                    <div className="text-xs text-slate-600">
                      Free: {formatMetricValue(healthData.metrics.system.disk_free_gb, 'GB')}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Database Metrics */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">Database Performance</h2>
          
          <div className="space-y-4">
            {healthData?.metrics?.database && (
              <>
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">Response Time</span>
                  <div className="font-bold">{formatMetricValue(healthData.metrics.database.response_time_ms, 'ms')}</div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">Active Connections</span>
                  <div className="font-bold">{formatMetricValue(healthData.metrics.database.active_connections)}</div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Application Metrics */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">Application Metrics</h2>
          
          <div className="space-y-4">
            {healthData?.metrics?.application && (
              <>
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium">Active Users (24h)</span>
                  <div className="font-bold">{formatMetricValue(healthData.metrics.application.active_users_24h)}</div>
                </div>
                
                {healthData.metrics.application.feature_usage && (
                  <>
                    <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                      <span className="font-medium">Assessments Completed</span>
                      <div className="font-bold">{formatMetricValue(healthData.metrics.application.feature_usage.assessments_completed)}</div>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
                      <span className="font-medium">Service Requests</span>
                      <div className="font-bold">{formatMetricValue(healthData.metrics.application.feature_usage.service_requests_created)}</div>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        {/* SLA Compliance */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-6">SLA Compliance</h2>
          
          {slaData?.sla_metrics ? (
            <div className="space-y-4">
              <div className="text-center mb-4">
                <div className="text-3xl font-bold text-blue-600">{slaData.overall_sla_score}%</div>
                <div className="text-sm text-slate-600">Overall SLA Score</div>
              </div>
              
              {Object.entries(slaData.sla_metrics).map(([key, metric]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-slate-50 rounded">
                  <span className="font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                  <div className="text-right">
                    <div className={`font-bold ${metric.compliance ? 'text-green-600' : 'text-red-600'}`}>
                      {metric.compliance ? '✅' : '❌'} {metric.score.toFixed(1)}%
                    </div>
                    <div className="text-xs text-slate-600">
                      Target: {formatMetricValue(metric.target_ms || metric.target_percent, metric.target_ms ? 'ms' : '%')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-slate-500 py-8">
              <div className="text-4xl mb-2">📊</div>
              <p>SLA data loading...</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {healthData?.recommendations && healthData.recommendations.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">💡 Recommendations</h2>
          <ul className="space-y-2">
            {healthData.recommendations.map((recommendation, index) => (
              <li key={index} className="text-blue-800 text-sm flex items-start gap-2">
                <span className="text-blue-500 mt-1">•</span>
                <span>{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SystemHealthDashboard;