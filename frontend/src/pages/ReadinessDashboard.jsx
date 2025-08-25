import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polaris-inspector.preview.emergentagent.com/api';

function ReadinessDashboard() {
  const [planner, setPlanner] = useState({ loading: true, tasks: [] });
  const loadPlanner = async () => {
    try {
      const { data } = await axios.get(`${API}/planner/tasks`);
      setPlanner({ loading: false, tasks: data || [] });
    } catch (e) {
      console.warn('Failed to load planner', e);
      setPlanner({ loading: false, tasks: [] });
    }
  };
  const markTask = async (taskId, status) => {
    try {
      await axios.patch(`${API}/planner/tasks/${taskId}`, { status });
      setPlanner(p => ({ ...p, tasks: p.tasks.map(t => t.id === taskId ? { ...t, status } : t) }));
    } catch (e) {
      console.warn('Failed to update task', e);
    }
  };
  useEffect(() => { loadPlanner(); }, []);
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('6months'); // 3months, 6months, 1year, all

  useEffect(() => {
    loadDashboardData();
  }, [timeframe]);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/readiness/dashboard?timeframe=${timeframe}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Mock data for demo
      setDashboardData({
        current_score: 68,
        previous_score: 45,
        score_trend: 'increasing',
        assessments_completed: 3,
        last_assessment: '2025-01-20',
        next_recommended: '2025-04-20',
        area_scores: [
          { area: 'Business Formation', score: 85, trend: 'stable', last_updated: '2025-01-20' },
          { area: 'Financial Operations', score: 72, trend: 'increasing', last_updated: '2025-01-18' },
          { area: 'Legal Compliance', score: 45, trend: 'decreasing', last_updated: '2025-01-15' },
          { area: 'Quality Management', score: 78, trend: 'increasing', last_updated: '2025-01-20' },
          { area: 'Technology & Security', score: 52, trend: 'stable', last_updated: '2025-01-10' },
          { area: 'Human Resources', score: 69, trend: 'increasing', last_updated: '2025-01-18' },
          { area: 'Performance Tracking', score: 61, trend: 'stable', last_updated: '2025-01-12' },
          { area: 'Risk Management', score: 75, trend: 'increasing', last_updated: '2025-01-20' },
          { area: 'Supply Chain', score: 38, trend: 'stable', last_updated: '2025-01-08' }
        ],
        goals: [
          { id: 1, title: 'Achieve 70% Overall Score', progress: 97, target_date: '2025-03-01', status: 'on_track' },
          { id: 2, title: 'Complete Legal Compliance Gap', progress: 60, target_date: '2025-02-15', status: 'at_risk' },
          { id: 3, title: 'Strengthen Supply Chain Management', progress: 25, target_date: '2025-04-01', status: 'behind' }
        ],
        recent_activities: [
          { date: '2025-01-20', type: 'assessment', description: 'Completed full 9-area assessment' },
          { date: '2025-01-18', type: 'improvement', description: 'Updated financial management processes' },
          { date: '2025-01-15', type: 'consultation', description: 'Scheduled consultation with legal compliance expert' },
          { date: '2025-01-12', type: 'milestone', description: 'Achieved Quality Management certification' }
        ],
        certifications: [
          { name: 'Business Formation Readiness', earned_date: '2025-01-10', expires_date: '2026-01-10', status: 'active' },
          { name: 'Quality Management Standards', earned_date: '2025-01-12', expires_date: '2026-01-12', status: 'active' }
        ],
        benchmarks: {
          industry_average: 62,
          similar_businesses: 59,
          top_performers: 88
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return <span className="text-green-500">↗️</span>;
      case 'decreasing': return <span className="text-red-500">↘️</span>;
      default: return <span className="text-slate-500">→</span>;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'on_track': return 'bg-green-100 text-green-800';
      case 'at_risk': return 'bg-yellow-100 text-yellow-800';
      case 'behind': return 'bg-red-100 text-red-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-7xl">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/2 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1,2,3,4].map(i => (
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
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Procurement Readiness Dashboard</h1>
            <p className="text-blue-100">Track your progress toward procurement success</p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold mb-2">{dashboardData?.current_score}%</div>
            <div className="text-blue-100">Current Readiness</div>
            <div className="flex items-center gap-2 mt-2 justify-end">
              {getTrendIcon(dashboardData?.score_trend)}
              <span className="text-sm text-blue-200">
                {dashboardData?.score_trend === 'increasing' && `+${dashboardData?.current_score - dashboardData?.previous_score} from last assessment`}
                {dashboardData?.score_trend === 'decreasing' && `-${dashboardData?.previous_score - dashboardData?.current_score} from last assessment`}
                {dashboardData?.score_trend === 'stable' && 'No change from last assessment'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Overall Progress */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Overall Progress</h3>
            <span className="text-2xl">📈</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.current_score}%</div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${dashboardData?.current_score}%` }}
            ></div>
          </div>
          <div className="text-xs text-slate-500 mt-2">
            Target: 70% for certification
          </div>
        </div>

        {/* Assessments Completed */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Assessments</h3>
            <span className="text-2xl">✅</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.assessments_completed}</div>
          <div className="text-sm text-slate-600">Completed</div>
          <div className="text-xs text-slate-500 mt-1">
            Last: {new Date(dashboardData?.last_assessment).toLocaleDateString()}
          </div>
        </div>

        {/* Active Goals */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Active Goals</h3>
            <span className="text-2xl">🎯</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.goals?.length || 0}</div>
          <div className="text-sm text-slate-600">In Progress</div>
          <div className="text-xs text-slate-500 mt-1">
            {dashboardData?.goals?.filter(g => g.status === 'on_track').length || 0} on track
          </div>
        </div>

        {/* Certifications */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-600">Certifications</h3>
            <span className="text-2xl">🏆</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{dashboardData?.certifications?.length || 0}</div>
          <div className="text-sm text-slate-600">Earned</div>
          <div className="text-xs text-slate-500 mt-1">
            {dashboardData?.certifications?.filter(c => c.status === 'active').length || 0} active
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Business Area Scores */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900">Business Area Performance</h2>
              <select 
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="form-select text-sm"
              >
                <option value="3months">Last 3 Months</option>
                <option value="6months">Last 6 Months</option>
                <option value="1year">Last Year</option>
                <option value="all">All Time</option>
              </select>
            </div>

            <div className="space-y-4">
              {dashboardData?.area_scores?.map((area, index) => (
                <div key={index} className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-slate-900">{area.area}</h3>
                        {getTrendIcon(area.trend)}
                      </div>
                      <div className="text-xs text-slate-500">
                        Last updated: {new Date(area.last_updated).toLocaleDateString()}
                      </div>
                    </div>
                    <div className={`text-right ml-4 ${getScoreColor(area.score)}`}>
                      <div className="text-2xl font-bold">{area.score}%</div>
                    </div>
                  </div>
                  
                  <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        area.score >= 80 ? 'bg-green-500' :
                        area.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${area.score}%` }}
                    ></div>
                  </div>

                  {area.score < 60 && (
                    <div className="flex gap-2 mt-3">
                      <button 
                        className="btn btn-xs btn-primary"
                        onClick={() => navigate(`/area-deliverables/${index + 1}`)}
                      >
                        Get Resources
                      </button>
                      <button 
                        className="btn btn-xs btn-secondary"
                        onClick={() => navigate('/service-request')}
                      >
                        Find Expert Help
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Benchmarking */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Benchmarking</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <div className="font-medium text-slate-900">Your Score</div>
                  <div className="text-sm text-slate-600">Current readiness level</div>
                </div>
                <div className="text-2xl font-bold text-blue-600">{dashboardData?.current_score}%</div>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <div className="font-medium text-slate-900">Industry Average</div>
                  <div className="text-sm text-slate-600">Similar business size</div>
                </div>
                <div className="text-2xl font-bold text-slate-600">{dashboardData?.benchmarks?.industry_average}%</div>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <div className="font-medium text-slate-900">Similar Businesses</div>
                  <div className="text-sm text-slate-600">Same industry & location</div>
                </div>
                <div className="text-2xl font-bold text-slate-600">{dashboardData?.benchmarks?.similar_businesses}%</div>
              </div>

              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div>
                  <div className="font-medium text-green-900">Top Performers</div>
                  <div className="text-sm text-green-600">Best in class</div>
                </div>
                <div className="text-2xl font-bold text-green-600">{dashboardData?.benchmarks?.top_performers}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Goals & Activities Sidebar */}
        <div className="lg:col-span-1">
          {/* Active Goals */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900">Active Goals</h3>
              <button 
                className="btn btn-xs btn-primary"
                onClick={() => navigate('/goals')}
              >
                Manage
              </button>
            </div>
            
            <div className="space-y-3">
              {dashboardData?.goals?.map((goal) => (
                <div key={goal.id} className="border rounded-lg p-3">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-slate-900 text-sm">{goal.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(goal.status)}`}>
                      {goal.status.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div className="w-full bg-slate-200 rounded-full h-1.5 mb-2">
                    <div 
                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${goal.progress}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>{goal.progress}% complete</span>
                    <span>Due: {new Date(goal.target_date).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activities */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Activities</h3>
            
            <div className="space-y-3">
              {dashboardData?.recent_activities?.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900">{activity.description}</div>
                    <div className="text-xs text-slate-500">{new Date(activity.date).toLocaleDateString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
            
            <div className="space-y-3">
              <button 
                className="w-full btn btn-primary btn-sm"
                onClick={() => navigate('/assessment')}
              >
                Take New Assessment
              </button>
              <button 
                className="w-full btn btn-secondary btn-sm"
                onClick={() => navigate('/tools/capability-statement')}
              >
                Update Capability Statement
              </button>
              <button 
                className="w-full btn btn-outline btn-sm"
                onClick={() => navigate('/service-request')}
              >
                Find Service Providers
              </button>
              <button 
                className="w-full btn btn-outline btn-sm"
                onClick={() => navigate('/certifications')}
              >
                View Certifications
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReadinessDashboard;