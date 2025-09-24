import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polar-docs-ai.preview.emergentagent.com/api';

function ActionPlanPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [actionPlan, setActionPlan] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [progressStats, setProgressStats] = useState({ completed: 0, total: 0 });

  useEffect(() => {
    loadActionPlan();
    loadTasks();
  }, [sessionId]);

  const loadActionPlan = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      // Get assessment results to generate action plan
      const response = await axios.get(`${API}/assessment/results/${sessionId}`, { headers });
      const results = response.data;
      
      // Generate personalized action plan based on results
      const generatedPlan = generateActionPlan(results);
      setActionPlan(generatedPlan);
    } catch (error) {
      console.error('Error loading action plan:', error);
      setError('Failed to load action plan');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API}/planner/tasks`, { headers });
      const allTasks = response.data || [];
      
      // Filter tasks related to this session
      const sessionTasks = allTasks.filter(task => 
        task.metadata?.sessionId === sessionId || task.category === 'assessment'
      );
      
      setTasks(sessionTasks);
      
      // Calculate progress
      const completed = sessionTasks.filter(task => task.status === 'completed').length;
      setProgressStats({ completed, total: sessionTasks.length });
    } catch (error) {
      console.error('Error loading tasks:', error);
      // Continue with empty tasks - not critical
    }
  };

  const generateActionPlan = (results) => {
    if (!results) return null;

    const weakAreas = results.area_scores?.filter(area => area.score < 60) || [];
    const moderateAreas = results.area_scores?.filter(area => area.score >= 60 && area.score < 80) || [];
    
    return {
      overall_score: results.overall_score,
      priority_actions: weakAreas.slice(0, 3).map(area => ({
        title: `Improve ${area.area_name}`,
        description: `Current score: ${area.score}%. Focus on addressing key gaps in this area.`,
        urgency: 'high',
        estimated_time: '2-4 weeks',
        area_id: area.area_id
      })),
      improvement_actions: moderateAreas.slice(0, 2).map(area => ({
        title: `Enhance ${area.area_name}`,
        description: `Current score: ${area.score}%. Build on existing strengths to reach excellence.`,
        urgency: 'medium',
        estimated_time: '1-2 weeks',
        area_id: area.area_id
      })),
      recommended_resources: [
        {
          title: 'Knowledge Base Templates',
          description: 'Download industry-specific templates and checklists',
          action_url: '/knowledge-base'
        },
        {
          title: 'Service Provider Consultation',
          description: 'Get expert help from verified professionals',
          action_url: '/service-request'
        },
        {
          title: 'Capability Statement Builder',
          description: 'Create professional capability statements',
          action_url: '/tools/capability-statement'
        }
      ],
      next_assessment: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString() // 90 days from now
    };
  };

  const createTask = async (title, description, priority = 'medium') => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      await axios.post(`${API}/planner/quick-task`, {
        title,
        description,
        priority,
        category: 'assessment',
        metadata: { sessionId }
      }, { headers });
      
      // Reload tasks
      await loadTasks();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const toggleTask = async (taskId, currentStatus) => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      await axios.patch(`${API}/planner/tasks/${taskId}`, {
        status: newStatus
      }, { headers });
      
      // Update local state
      setTasks(tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
      
      // Update progress
      const newTasks = tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      );
      const completed = newTasks.filter(task => task.status === 'completed').length;
      setProgressStats({ completed, total: newTasks.length });
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-5xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-slate-200 rounded w-3/4 mb-6"></div>
            <div className="space-y-4">
              {[1,2,3].map(i => (
                <div key={i} className="h-16 bg-slate-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-6 max-w-5xl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Action Plan</h2>
          <p className="text-red-700 mb-6">{error}</p>
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/assessment')}
          >
            Back to Assessment
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Personalized Action Plan</h1>
            <p className="text-blue-100">Strategic next steps based on your assessment results</p>
            {sessionId && (
              <div className="text-sm text-blue-200 mt-2">Session: {sessionId}</div>
            )}
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold mb-1">{actionPlan?.overall_score || 0}%</div>
            <div className="text-blue-100 text-sm">Current Score</div>
          </div>
        </div>
        
        {/* Progress Bar */}
        {progressStats.total > 0 && (
          <div className="mt-6">
            <div className="flex justify-between text-sm text-blue-100 mb-2">
              <span>Action Plan Progress</span>
              <span>{progressStats.completed} of {progressStats.total} completed</span>
            </div>
            <div className="w-full bg-blue-700 rounded-full h-2">
              <div 
                className="bg-white rounded-full h-2 transition-all duration-300"
                style={{ width: `${(progressStats.completed / progressStats.total) * 100}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Priority Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* High Priority Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6 border">
            <h2 className="text-xl font-semibold text-slate-900 mb-6 flex items-center gap-2">
              <span className="text-red-500">🔥</span>
              High Priority Actions
            </h2>
            
            <div className="space-y-4">
              {actionPlan?.priority_actions?.map((action, index) => (
                <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-medium text-slate-900">{action.title}</h3>
                      <p className="text-sm text-slate-600 mt-1">{action.description}</p>
                    </div>
                    <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                      {action.estimated_time}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => createTask(action.title, action.description, 'high')}
                    >
                      Add to Tasks
                    </button>
                    <button 
                      className="btn btn-sm btn-outline"
                      onClick={() => navigate('/knowledge-base')}
                    >
                      View Resources
                    </button>
                  </div>
                </div>
              )) || (
                <div className="text-center py-8 text-slate-500">
                  <span className="text-4xl mb-2 block">🎉</span>
                  <p>No high-priority actions needed! You're doing great.</p>
                </div>
              )}
            </div>
          </div>

          {/* Improvement Actions */}
          {actionPlan?.improvement_actions?.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6 border">
              <h2 className="text-xl font-semibold text-slate-900 mb-6 flex items-center gap-2">
                <span className="text-yellow-500">📈</span>
                Growth Opportunities
              </h2>
              
              <div className="space-y-4">
                {actionPlan.improvement_actions.map((action, index) => (
                  <div key={index} className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-medium text-slate-900">{action.title}</h3>
                        <p className="text-sm text-slate-600 mt-1">{action.description}</p>
                      </div>
                      <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-medium">
                        {action.estimated_time}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button 
                        className="btn btn-sm btn-secondary"
                        onClick={() => createTask(action.title, action.description, 'medium')}
                      >
                        Add to Tasks
                      </button>
                      <button 
                        className="btn btn-sm btn-outline"
                        onClick={() => navigate('/knowledge-base')}
                      >
                        View Resources
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* My Tasks */}
          <div className="bg-white rounded-lg shadow-sm p-6 border">
            <h2 className="text-xl font-semibold text-slate-900 mb-6 flex items-center gap-2">
              <span>✅</span>
              My Action Items
            </h2>
            
            {tasks.length > 0 ? (
              <div className="space-y-3">
                {tasks.map(task => (
                  <div key={task.id} className="flex items-center gap-3 p-3 rounded-lg border hover:bg-slate-50">
                    <input 
                      type="checkbox"
                      checked={task.status === 'completed'}
                      onChange={() => toggleTask(task.id, task.status)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                        {task.title}
                      </h4>
                      {task.description && (
                        <p className={`text-sm ${task.status === 'completed' ? 'text-slate-400' : 'text-slate-600'}`}>
                          {task.description}
                        </p>
                      )}
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      task.priority === 'high' ? 'bg-red-100 text-red-800' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <span className="text-4xl mb-2 block">📝</span>
                <p>No tasks yet. Add some actions from above to get started!</p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6 border">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
            
            <div className="space-y-3">
              <button 
                className="w-full btn btn-primary"
                onClick={() => navigate(`/assessment/results/${sessionId}`)}
              >
                <span className="mr-2">📊</span>
                View Results
              </button>
              
              <button 
                className="w-full btn btn-secondary"
                onClick={() => navigate('/tools/capability-statement')}
              >
                <span className="mr-2">📄</span>
                Build Capability Statement
              </button>
              
              <button 
                className="w-full btn btn-outline"
                onClick={() => navigate('/service-request')}
              >
                <span className="mr-2">🔍</span>
                Find Expert Help
              </button>
              
              <button 
                className="w-full btn btn-outline"
                onClick={() => navigate('/readiness-dashboard')}
              >
                <span className="mr-2">📈</span>
                Progress Dashboard
              </button>
            </div>
          </div>

          {/* Recommended Resources */}
          <div className="bg-white rounded-lg shadow-sm p-6 border">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Recommended Resources</h3>
            
            <div className="space-y-3">
              {actionPlan?.recommended_resources?.map((resource, index) => (
                <div key={index} className="border rounded-lg p-3 hover:bg-slate-50">
                  <h4 className="font-medium text-slate-900 text-sm">{resource.title}</h4>
                  <p className="text-xs text-slate-600 mt-1">{resource.description}</p>
                  <button 
                    className="text-blue-600 text-xs mt-2 hover:underline"
                    onClick={() => navigate(resource.action_url)}
                  >
                    Learn More →
                  </button>
                </div>
              )) || (
                <p className="text-sm text-slate-600">Loading recommendations...</p>
              )}
            </div>
          </div>

          {/* Next Assessment */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Next Assessment</h3>
            <p className="text-sm text-blue-800 mb-4">
              Track your progress with a follow-up assessment
            </p>
            <div className="text-xs text-blue-700">
              Recommended: {actionPlan?.next_assessment ? 
                new Date(actionPlan.next_assessment).toLocaleDateString() : 
                '90 days from completion'
              }
            </div>
            <button 
              className="btn btn-sm btn-primary mt-3"
              onClick={() => navigate('/assessment')}
            >
              Schedule Assessment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ActionPlanPage;