import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LiveChatSystem from './LiveChatSystem';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SharedWorkspace({ workspaceId, workspaceType, title }) {
  const [workspace, setWorkspace] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [notes, setNotes] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [newNote, setNewNote] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(() => {
    loadWorkspace();
  }, [workspaceId]);

  const loadWorkspace = async () => {
    try {
      setLoading(true);
      
      // Load workspace data
      const [workspaceRes, tasksRes, documentsRes, notesRes] = await Promise.all([
        axios.get(`${API}/workspace/${workspaceId}`),
        axios.get(`${API}/workspace/${workspaceId}/tasks`),
        axios.get(`${API}/workspace/${workspaceId}/documents`),
        axios.get(`${API}/workspace/${workspaceId}/notes`)
      ]);

      setWorkspace(workspaceRes.data);
      setTasks(tasksRes.data.tasks || []);
      setDocuments(documentsRes.data.documents || []);
      setNotes(notesRes.data.notes || []);
    } catch (error) {
      console.error('Failed to load workspace:', error);
      // Create default workspace structure
      setWorkspace({
        id: workspaceId,
        type: workspaceType,
        title: title,
        participants: [me],
        created_at: new Date().toISOString()
      });
      setTasks([]);
      setDocuments([]);
      setNotes([]);
    } finally {
      setLoading(false);
    }
  };

  const addTask = async () => {
    if (!newTask.trim()) return;

    const task = {
      id: `task_${Date.now()}`,
      title: newTask.trim(),
      status: 'pending',
      assigned_to: me.id,
      assigned_by: me.id,
      created_at: new Date().toISOString(),
      due_date: null,
      priority: 'medium'
    };

    try {
      await axios.post(`${API}/workspace/${workspaceId}/tasks`, task);
      setTasks(prev => [...prev, task]);
      setNewTask('');
    } catch (error) {
      console.error('Failed to add task:', error);
      // Add locally for now
      setTasks(prev => [...prev, task]);
      setNewTask('');
    }
  };

  const updateTaskStatus = async (taskId, status) => {
    try {
      await axios.patch(`${API}/workspace/${workspaceId}/tasks/${taskId}`, { status });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status, updated_at: new Date().toISOString() } : t));
    } catch (error) {
      console.error('Failed to update task:', error);
      // Update locally for now
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status, updated_at: new Date().toISOString() } : t));
    }
  };

  const addNote = async () => {
    if (!newNote.trim()) return;

    const note = {
      id: `note_${Date.now()}`,
      content: newNote.trim(),
      author_id: me.id,
      author_name: me.name || me.email,
      author_role: me.role,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    try {
      await axios.post(`${API}/workspace/${workspaceId}/notes`, note);
      setNotes(prev => [note, ...prev]);
      setNewNote('');
    } catch (error) {
      console.error('Failed to add note:', error);
      // Add locally for now
      setNotes(prev => [note, ...prev]);
      setNewNote('');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'blocked': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-center text-slate-600">Loading workspace...</p>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg border">
        {/* Workspace Header */}
        <div className="p-6 border-b bg-gradient-to-r from-slate-50 to-blue-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-slate-900">{workspace?.title || title}</h2>
              <p className="text-slate-600 text-sm mt-1">
                Collaborative workspace • {workspace?.participants?.length || 1} participants
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Participant Avatars */}
              <div className="flex -space-x-2">
                {(workspace?.participants || [me]).slice(0, 4).map((participant, index) => (
                  <div
                    key={participant.id || index}
                    className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm border-2 border-white"
                    title={participant.name || participant.email}
                  >
                    {(participant.name || participant.email || 'U').charAt(0).toUpperCase()}
                  </div>
                ))}
                {(workspace?.participants?.length || 0) > 4 && (
                  <div className="w-8 h-8 bg-slate-300 rounded-full flex items-center justify-center text-slate-600 text-xs border-2 border-white">
                    +{(workspace?.participants?.length || 0) - 4}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-1 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b">
          <nav className="flex">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'tasks', label: 'Tasks', icon: '✅', badge: tasks.filter(t => t.status === 'pending').length },
              { id: 'documents', label: 'Documents', icon: '📄', badge: documents.length },
              { id: 'notes', label: 'Notes', icon: '📝', badge: notes.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
                {tab.badge > 0 && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    {tab.badge}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Workspace Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 4h6m-6 4h6m-6 4h6" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-blue-600">{tasks.length}</div>
                      <div className="text-sm text-blue-700">Total Tasks</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {tasks.filter(t => t.status === 'completed').length}
                      </div>
                      <div className="text-sm text-green-700">Completed</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">{documents.length}</div>
                      <div className="text-sm text-purple-700">Documents</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  {(tasks.slice(0, 3).map(task => ({
                    type: 'task',
                    content: `Task "${task.title}" ${task.status === 'completed' ? 'completed' : 'updated'}`,
                    time: task.updated_at || task.created_at,
                    user: task.assigned_by,
                    icon: '✅'
                  })).concat(
                    notes.slice(0, 2).map(note => ({
                      type: 'note',
                      content: `Note added: "${note.content.substring(0, 50)}..."`,
                      time: note.created_at,
                      user: note.author_name,
                      icon: '📝'
                    }))
                  )).sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5).map((activity, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                      <span className="text-lg">{activity.icon}</span>
                      <div className="flex-1">
                        <p className="text-sm text-slate-900">{activity.content}</p>
                        <p className="text-xs text-slate-500">
                          {activity.user} • {new Date(activity.time).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {tasks.length === 0 && notes.length === 0 && (
                    <div className="text-center py-8 text-slate-500">
                      <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 4h6m-6 4h6m-6 4h6" />
                      </svg>
                      <p>No activity yet. Start collaborating!</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="space-y-4">
              {/* Add New Task */}
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={newTask}
                    onChange={(e) => setNewTask(e.target.value)}
                    placeholder="Add a new task..."
                    className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    onKeyPress={(e) => e.key === 'Enter' && addTask()}
                  />
                  <button
                    onClick={addTask}
                    disabled={!newTask.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Add Task
                  </button>
                </div>
              </div>

              {/* Task List */}
              <div className="space-y-3">
                {tasks.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 4h6m-6 4h6m-6 4h6" />
                    </svg>
                    <p>No tasks yet. Add one above to get started!</p>
                  </div>
                ) : (
                  tasks.map((task) => (
                    <div key={task.id} className="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 flex-1">
                          <button
                            onClick={() => updateTaskStatus(task.id, 
                              task.status === 'completed' ? 'pending' : 'completed'
                            )}
                            className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                              task.status === 'completed'
                                ? 'bg-green-600 border-green-600'
                                : 'border-slate-300 hover:border-green-500'
                            }`}
                          >
                            {task.status === 'completed' && (
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </button>
                          <div className="flex-1">
                            <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                              {task.title}
                            </h4>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="text-xs text-slate-500">
                                {new Date(task.created_at).toLocaleDateString()}
                              </span>
                              <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(task.status)}`}>
                                {task.status.replace('_', ' ')}
                              </span>
                              <span className="text-sm">{getPriorityIcon(task.priority)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-4">
              {/* Add New Note */}
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="space-y-3">
                  <textarea
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Add a note or update..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    rows="3"
                  />
                  <div className="flex justify-end">
                    <button
                      onClick={addNote}
                      disabled={!newNote.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Add Note
                    </button>
                  </div>
                </div>
              </div>

              {/* Notes List */}
              <div className="space-y-3">
                {notes.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <p>No notes yet. Add your first note above!</p>
                  </div>
                ) : (
                  notes.map((note) => (
                    <div key={note.id} className="bg-white border rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center text-sm">
                          {(note.author_name || 'U').charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-slate-900">{note.author_name}</span>
                            <span className="text-xs text-slate-500">
                              {new Date(note.created_at).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm text-slate-700 whitespace-pre-wrap">{note.content}</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="text-center py-8 text-slate-500">
              <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>Document sharing coming soon!</p>
              <p className="text-xs mt-1">Upload and collaborate on documents</p>
            </div>
          )}
        </div>
      </div>

      {/* Integrated Chat System */}
      <LiveChatSystem 
        context={workspaceType} 
        contextId={workspaceId}
        participants={workspace?.participants || []}
      />
    </>
  );
}