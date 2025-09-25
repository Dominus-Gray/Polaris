import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function CommunityHub({ userRole }) {
  const [activeTab, setActiveTab] = useState('discussions');
  const [discussions, setDiscussions] = useState([]);
  const [successStories, setSuccessStories] = useState([]);
  const [events, setEvents] = useState([]);
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', content: '', category: 'general' });

  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(() => {
    loadCommunityData();
  }, [activeTab]);

  const loadCommunityData = async () => {
    try {
      setLoading(true);
      
      // In production, these would come from backend APIs
      // For now, creating comprehensive mock data
      
      if (activeTab === 'discussions') {
        setDiscussions([
          {
            id: 'disc_1',
            title: 'Best practices for Financial Management assessment?',
            author: 'TechStartup Mike',
            author_role: 'client',
            category: 'assessment',
            replies: 12,
            views: 134,
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            last_activity: new Date(Date.now() - 3600000).toISOString(),
            preview: 'I\'m struggling with the financial management section of my assessment. What documents should I prepare first?',
            tags: ['financial-management', 'assessment', 'documentation']
          },
          {
            id: 'disc_2',
            title: 'How to respond effectively to service requests?',
            author: 'ConsultingPro Sarah',
            author_role: 'provider',
            category: 'service_providers',
            replies: 8,
            views: 89,
            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
            last_activity: new Date(Date.now() - 7200000).toISOString(),
            preview: 'Looking for tips on writing compelling proposals that win client engagements...',
            tags: ['service-providers', 'proposals', 'best-practices']
          },
          {
            id: 'disc_3',
            title: 'Resource Partner integration success tips',
            author: 'Regional Agency',
            author_role: 'agency',
            category: 'rp_crm',
            replies: 15,
            views: 203,
            created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
            last_activity: new Date(Date.now() - 1800000).toISOString(),
            preview: 'We\'ve successfully connected 15 businesses with lenders through the RP system. Here\'s what worked...',
            tags: ['resource-partners', 'success-story', 'integration']
          }
        ]);
      } else if (activeTab === 'success_stories') {
        setSuccessStories([
          {
            id: 'story_1',
            title: 'From 23% to 89% Readiness in 12 Weeks',
            author: 'Martinez Construction LLC',
            author_role: 'client',
            industry: 'construction',
            readiness_improvement: 66,
            contract_value: 450000,
            timeline: '12 weeks',
            story: 'Started with basic business operations and achieved full procurement readiness through focused assessment completion and expert guidance...',
            key_actions: [
              'Completed all 10 business area assessments',
              'Worked with compliance specialist for legal requirements',
              'Implemented financial management systems',
              'Obtained required insurance and bonding'
            ],
            outcome: 'Secured first federal contract worth $450,000',
            created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
            likes: 34,
            comments: 8
          },
          {
            id: 'story_2',
            title: 'Building a Successful Provider Practice',
            author: 'CyberSec Solutions',
            author_role: 'provider',
            specialization: 'cybersecurity',
            clients_helped: 28,
            success_rate: 94,
            story: 'Joined Polaris 6 months ago and have helped 28 small businesses achieve cybersecurity compliance...',
            key_insights: [
              'Focus on businesses 50-70% ready for best conversion',
              'Respond within 2 hours for competitive advantage',
              'Provide detailed assessment-based proposals',
              'Follow up consistently throughout engagement'
            ],
            outcome: 'Built thriving practice with 94% client success rate',
            created_at: new Date(Date.now() - 86400000 * 14).toISOString(),
            likes: 52,
            comments: 16
          }
        ]);
      } else if (activeTab === 'events') {
        setEvents([
          {
            id: 'event_1',
            title: 'Procurement Readiness Webinar: Financial Management Best Practices',
            type: 'webinar',
            date: new Date(Date.now() + 86400000 * 7).toISOString(),
            duration: '1 hour',
            presenter: 'Sarah Johnson, CPA',
            description: 'Learn essential financial management practices for government contracting readiness',
            attendees: 127,
            max_capacity: 200,
            registration_required: true,
            topics: ['Cash flow management', 'Financial reporting', 'Cost accounting', 'Audit preparation']
          },
          {
            id: 'event_2',
            title: 'Office Hours: Ask the Experts',
            type: 'qa_session',
            date: new Date(Date.now() + 86400000 * 3).toISOString(),
            duration: '90 minutes',
            presenter: 'Polaris Expert Panel',
            description: 'Get your procurement readiness questions answered by our expert panel',
            attendees: 45,
            max_capacity: 100,
            registration_required: false,
            topics: ['Open Q&A', 'Assessment guidance', 'Service provider matching', 'Resource partners']
          }
        ]);
      }
      
    } catch (error) {
      console.error('Failed to load community data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createPost = async () => {
    if (!newPost.title.trim() || !newPost.content.trim()) {
      alert('Please fill in title and content');
      return;
    }

    const postData = {
      title: newPost.title.trim(),
      content: newPost.content.trim(),
      category: newPost.category,
      author: me?.name || me?.email || 'Anonymous',
      author_role: me?.role,
      created_at: new Date().toISOString(),
      replies: 0,
      views: 0
    };

    try {
      await axios.post(`${API}/community/discussions/create`, postData);
      
      // Add to local state
      setDiscussions(prev => [{ id: `disc_${Date.now()}`, ...postData }, ...prev]);
      setNewPost({ title: '', content: '', category: 'general' });
      setShowCreateForm(false);
      
    } catch (error) {
      console.error('Failed to create post:', error);
      // Add locally for demo
      setDiscussions(prev => [{ id: `disc_${Date.now()}`, ...postData }, ...prev]);
      setNewPost({ title: '', content: '', category: 'general' });
      setShowCreateForm(false);
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'assessment': return 'bg-blue-100 text-blue-800';
      case 'service_providers': return 'bg-green-100 text-green-800';
      case 'rp_crm': return 'bg-purple-100 text-purple-800';
      case 'technical': return 'bg-red-100 text-red-800';
      case 'success_story': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'client': return '🏢';
      case 'provider': return '🛠️';
      case 'agency': return '🏛️';
      case 'navigator': return '🧭';
      default: return '👤';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Community Hub</h1>
          <p className="text-slate-600">Connect, learn, and grow with the Polaris community</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>1,247 members online</span>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Post
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg border mb-6">
        <div className="border-b">
          <nav className="flex">
            {[
              { id: 'discussions', label: 'Discussions', icon: '💬', count: discussions.length },
              { id: 'success_stories', label: 'Success Stories', icon: '🏆', count: successStories.length },
              { id: 'events', label: 'Events & Webinars', icon: '📅', count: events.length },
              { id: 'resources', label: 'Community Resources', icon: '📚', count: 25 }
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
                <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded-full">
                  {tab.count}
                </span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'discussions' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-slate-600">Loading discussions...</p>
                </div>
              ) : (
                discussions.map((discussion) => (
                  <div key={discussion.id} className="border rounded-lg p-6 hover:shadow-sm transition-shadow cursor-pointer">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium text-slate-900 hover:text-blue-600">{discussion.title}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs ${getCategoryColor(discussion.category)}`}>
                            {discussion.category}
                          </span>
                        </div>
                        
                        <p className="text-sm text-slate-600 mb-3">{discussion.preview}</p>
                        
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            {getRoleIcon(discussion.author_role)}
                            {discussion.author}
                          </span>
                          <span>{discussion.replies} replies</span>
                          <span>{discussion.views} views</span>
                          <span>{new Date(discussion.created_at).toLocaleDateString()}</span>
                        </div>
                        
                        <div className="flex flex-wrap gap-1 mt-2">
                          {discussion.tags?.map((tag) => (
                            <span key={tag} className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="text-right ml-4">
                        <div className="text-xs text-slate-500">
                          Last activity
                        </div>
                        <div className="text-xs font-medium text-slate-700">
                          {new Date(discussion.last_activity).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'success_stories' && (
            <div className="space-y-6">
              {successStories.map((story) => (
                <div key={story.id} className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-green-100 rounded-full">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                      </svg>
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">{story.title}</h3>
                          <div className="flex items-center gap-3 text-sm text-slate-600">
                            <span className="flex items-center gap-1">
                              {getRoleIcon(story.author_role)}
                              {story.author}
                            </span>
                            {story.industry && <span>• {story.industry}</span>}
                            <span>• {new Date(story.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          {story.readiness_improvement && (
                            <div className="text-2xl font-bold text-green-600">
                              +{story.readiness_improvement}%
                            </div>
                          )}
                          {story.contract_value && (
                            <div className="text-sm text-slate-600">
                              ${story.contract_value.toLocaleString()} contract
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-slate-700 mb-4">{story.story}</p>
                      
                      {story.key_actions && (
                        <div className="mb-4">
                          <h4 className="font-medium text-slate-900 mb-2">Key Actions Taken:</h4>
                          <ul className="space-y-1">
                            {story.key_actions.map((action, index) => (
                              <li key={index} className="flex items-center gap-2 text-sm text-slate-600">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="bg-white rounded-lg p-4 border border-green-100">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          <span className="font-medium text-green-900">Outcome</span>
                        </div>
                        <p className="text-sm text-green-800">{story.outcome}</p>
                      </div>
                      
                      <div className="flex items-center justify-between mt-4">
                        <div className="flex items-center gap-4">
                          <button className="flex items-center gap-1 text-sm text-slate-600 hover:text-blue-600">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            </svg>
                            {story.likes} likes
                          </button>
                          <button className="flex items-center gap-1 text-sm text-slate-600 hover:text-blue-600">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            {story.comments} comments
                          </button>
                        </div>
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                          Read Full Story →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'events' && (
            <div className="space-y-6">
              {events.map((event) => (
                <div key={event.id} className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-indigo-100 rounded-lg">
                          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">{event.title}</h3>
                          <div className="flex items-center gap-4 text-sm text-slate-600">
                            <span>{new Date(event.date).toLocaleDateString()}</span>
                            <span>• {event.duration}</span>
                            <span>• {event.presenter}</span>
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-slate-700 mb-4">{event.description}</p>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        {event.topics.map((topic) => (
                          <span key={topic} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs">
                            {topic}
                          </span>
                        ))}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span>{event.attendees}/{event.max_capacity} registered</span>
                        <div className="w-32 bg-slate-200 rounded-full h-2">
                          <div 
                            className="bg-indigo-600 h-2 rounded-full"
                            style={{ width: `${(event.attendees / event.max_capacity) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-6">
                      <button className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium">
                        {event.registration_required ? 'Register Now' : 'Join Event'}
                      </button>
                      <div className="text-xs text-center text-slate-500 mt-2">
                        {event.registration_required ? 'Registration required' : 'Drop-in welcome'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'resources' && (
            <div className="text-center py-12 text-slate-500">
              <svg className="w-12 h-12 mx-auto mb-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <h3 className="text-lg font-medium text-slate-700 mb-2">Community Resources</h3>
              <p>Shared templates, guides, and resources from the community</p>
              <p className="text-sm mt-2">Coming soon!</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Post Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-primary bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900">Create Community Post</h2>
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
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Title</label>
                <input
                  type="text"
                  value={newPost.title}
                  onChange={(e) => setNewPost(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="What's your question or topic?"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Category</label>
                <select
                  value={newPost.category}
                  onChange={(e) => setNewPost(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="general">General Discussion</option>
                  <option value="assessment">Assessment Help</option>
                  <option value="service_providers">Service Providers</option>
                  <option value="rp_crm">Resource Partner CRM</option>
                  <option value="success_story">Success Story</option>
                  <option value="technical">Technical Support</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Description</label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Share your question, experience, or insights with the community..."
                  rows="6"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={createPost}
                  disabled={!newPost.title.trim() || !newPost.content.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Create Post
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}