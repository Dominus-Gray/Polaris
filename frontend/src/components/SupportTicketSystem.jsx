import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SupportTicketSystem() {
  const [tickets, setTickets] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTicket, setNewTicket] = useState({
    subject: '',
    category: 'general',
    priority: 'medium',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);

  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/support/tickets`);
      setTickets(response.data.tickets || []);
    } catch (error) {
      console.warn('Failed to load support tickets:', error);
      // Create mock tickets for demonstration
      setTickets([
        {
          id: 'ticket_demo_1',
          subject: 'Help with Financial Management Assessment',
          category: 'assessment',
          priority: 'medium',
          status: 'open',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          last_reply: new Date(Date.now() - 3600000).toISOString(),
          replies_count: 2
        },
        {
          id: 'ticket_demo_2',  
          subject: 'Service Provider Not Responding',
          category: 'service_providers',
          priority: 'high',
          status: 'in_progress',
          created_at: new Date(Date.now() - 172800000).toISOString(),
          last_reply: new Date(Date.now() - 7200000).toISOString(),
          replies_count: 4
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createTicket = async () => {
    if (!newTicket.subject.trim() || !newTicket.description.trim()) {
      alert('Please fill in subject and description');
      return;
    }

    const ticketData = {
      subject: newTicket.subject.trim(),
      category: newTicket.category,
      priority: newTicket.priority,
      description: newTicket.description.trim(),
      user_id: me?.id,
      user_role: me?.role,
      user_email: me?.email,
      status: 'open',
      created_at: new Date().toISOString()
    };

    try {
      const response = await axios.post(`${API}/support/tickets/create`, ticketData);
      
      // Add to local state
      const newTicketObj = {
        id: response.data.ticket_id || `ticket_${Date.now()}`,
        ...ticketData,
        replies_count: 0
      };
      
      setTickets(prev => [newTicketObj, ...prev]);
      setNewTicket({ subject: '', category: 'general', priority: 'medium', description: '' });
      setShowCreateForm(false);
      
      // Show success notification
      const toast = document.createElement('div');
      toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      toast.textContent = '✅ Support ticket created successfully!';
      document.body.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
      }, 3000);
      
    } catch (error) {
      console.error('Failed to create ticket:', error);
      alert('Failed to create support ticket. Please try again.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'resolved': return 'bg-green-100 text-green-800 border-green-200';
      case 'closed': return 'bg-slate-100 text-slate-800 border-slate-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-slate-600';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'assessment': return '📝';
      case 'service_providers': return '🤝';
      case 'technical': return '⚙️';
      case 'billing': return '💳';
      case 'account': return '👤';
      default: return '❓';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Support Center</h1>
          <p className="text-slate-600">Get help with your procurement readiness journey</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Ticket
        </button>
      </div>

      {/* Quick Help Section */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Help</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="font-medium text-slate-900">Knowledge Base</h3>
            </div>
            <p className="text-sm text-slate-600 mb-3">Find answers in our comprehensive resource library</p>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              Browse Articles →
            </button>
          </div>
          
          <div className="bg-white rounded-lg p-4 border">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="font-medium text-slate-900">AI Coach</h3>
            </div>
            <p className="text-sm text-slate-600 mb-3">Get instant answers from our AI procurement coach</p>
            <button className="text-emerald-600 hover:text-emerald-700 text-sm font-medium">
              Start Chat →
            </button>
          </div>
          
          <div className="bg-white rounded-lg p-4 border">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M12 7a4 4 0 01-4 4v2a1 1 0 01-1 1H5a1 1 0 01-1-1v-2a4 4 0 01-4-4V5a1 1 0 011-1h12a1 1 0 011 1v2z" />
                </svg>
              </div>
              <h3 className="font-medium text-slate-900">Tutorials</h3>
            </div>
            <p className="text-sm text-slate-600 mb-3">Interactive guided tours of platform features</p>
            <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">
              Watch Tutorials →
            </button>
          </div>
        </div>
      </div>

      {/* Support Tickets List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold text-slate-900">Your Support Tickets</h2>
        </div>
        
        <div className="divide-y">
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-slate-600">Loading your tickets...</p>
            </div>
          ) : tickets.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              <svg className="w-12 h-12 mx-auto mb-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 className="text-lg font-medium text-slate-700 mb-2">No support tickets yet</h3>
              <p className="mb-4">Need help? Create your first support ticket or try our other support options.</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Support Ticket
              </button>
            </div>
          ) : (
            tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="p-6 hover:bg-slate-50 cursor-pointer transition-colors"
                onClick={() => setSelectedTicket(ticket)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="text-2xl">{getCategoryIcon(ticket.category)}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-slate-900">{ticket.subject}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(ticket.status)}`}>
                          {ticket.status}
                        </span>
                        <span className={`text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                          {ticket.priority} priority
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span>Created {new Date(ticket.created_at).toLocaleDateString()}</span>
                        <span>{ticket.replies_count} replies</span>
                        <span>Last reply {new Date(ticket.last_reply || ticket.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Create Ticket Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-primary bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900">Create Support Ticket</h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-slate-500 hover:text-slate-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Subject</label>
                <input
                  type="text"
                  value={newTicket.subject}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, subject: e.target.value }))}
                  placeholder="Brief description of your issue"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Category and Priority */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Category</label>
                  <select
                    value={newTicket.category}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="general">General Question</option>
                    <option value="assessment">Assessment Help</option>
                    <option value="service_providers">Service Providers</option>
                    <option value="technical">Technical Issue</option>
                    <option value="billing">Billing & Account</option>
                    <option value="rp_crm">Resource Partner CRM</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Priority</label>
                  <select
                    value={newTicket.priority}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, priority: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Description</label>
                <textarea
                  value={newTicket.description}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Please provide detailed information about your issue or question..."
                  rows="6"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={createTicket}
                  disabled={!newTicket.subject.trim() || !newTicket.description.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Create Ticket
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Ticket Detail Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getCategoryIcon(selectedTicket.category)}</span>
                    <h2 className="text-xl font-bold text-slate-900">{selectedTicket.subject}</h2>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(selectedTicket.status)}`}>
                      {selectedTicket.status}
                    </span>
                    <span className={`text-sm font-medium ${getPriorityColor(selectedTicket.priority)}`}>
                      {selectedTicket.priority} priority
                    </span>
                    <span className="text-sm text-slate-500">
                      Created {new Date(selectedTicket.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTicket(null)}
                  className="text-slate-500 hover:text-slate-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-96">
              <div className="bg-slate-50 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    {(me?.name || me?.email || 'You').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">You</div>
                    <div className="text-xs text-slate-500">
                      {new Date(selectedTicket.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-slate-700">
                  {selectedTicket.description || 'No description provided.'}
                </p>
              </div>

              {/* Mock support response */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">
                    S
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">Support Team</div>
                    <div className="text-xs text-slate-500">
                      {new Date(selectedTicket.last_reply || selectedTicket.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-slate-700">
                  Thank you for contacting Polaris support! We've received your request and our team is reviewing it. 
                  We typically respond within 24 hours. In the meantime, you might find helpful resources in our 
                  Knowledge Base or try our AI Coach for instant assistance.
                </p>
              </div>
            </div>

            <div className="p-6 border-t">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Type your reply..."
                  className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Reply
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}