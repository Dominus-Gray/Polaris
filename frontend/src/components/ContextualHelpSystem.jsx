import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ContextualHelpSystem({ currentPage, userRole }) {
  const [helpContent, setHelpContent] = useState(null);
  const [showHelp, setShowHelp] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeHelpTab, setActiveHelpTab] = useState('guide');

  // Contextual help content based on page and role
  const helpDatabase = {
    client: {
      dashboard: {
        title: 'Understanding Your Dashboard',
        sections: [
          {
            title: 'Readiness Score',
            content: 'Your overall procurement readiness percentage. Aim for 70% or higher to qualify for certification and competitive contract opportunities.',
            tips: ['Complete assessments in all 10 business areas', 'Focus on critical gaps first', 'Use service providers for expert help']
          },
          {
            title: 'Critical Gaps',
            content: 'Areas that need immediate attention for procurement readiness. These represent the biggest obstacles to contract eligibility.',
            tips: ['Prioritize red areas over yellow or green', 'Consider professional help for complex gaps', 'Track progress weekly']
          },
          {
            title: 'Service Requests',
            content: 'Professional services to help improve your readiness. Service providers are matched based on your assessment gaps.',
            tips: ['Be specific about your needs', 'Review provider profiles carefully', 'Communicate timeline and budget clearly']
          }
        ],
        quickActions: [
          { label: 'Start Assessment', action: 'assessment', icon: '📝' },
          { label: 'Find Expert Help', action: 'service-request', icon: '🔍' },
          { label: 'Browse Resources', action: 'knowledge', icon: '📚' }
        ]
      },
      assessment: {
        title: 'Assessment System Guide',
        sections: [
          {
            title: 'Business Areas',
            content: 'Ten critical areas for procurement readiness. Each area builds toward overall contract eligibility and competitive advantage.',
            tips: ['Start with Legal & Compliance', 'Complete Financial Management early', 'Use evidence to support responses']
          },
          {
            title: 'Tier System',
            content: 'Three tiers per area: Tier 1 (self-assessment), Tier 2 (evidence required), Tier 3 (verification). Your agency controls tier access.',
            tips: ['Complete lower tiers first', 'Gather evidence before Tier 2', 'Tier 3 may require third-party verification']
          },
          {
            title: 'Scoring',
            content: 'Responses are scored as Compliant (100%), Nearing Completion (67%), or Incomplete (33%). Higher scores improve readiness.',
            tips: ['Be honest in responses', 'Use "Nearing Completion" for work in progress', 'Add evidence notes for clarity']
          }
        ],
        quickActions: [
          { label: 'Assessment Tips', action: 'knowledge', icon: '💡' },
          { label: 'Evidence Examples', action: 'knowledge', icon: '📄' },
          { label: 'Get Expert Help', action: 'service-request', icon: '🤝' }
        ]
      }
    },
    provider: {
      dashboard: {
        title: 'Provider Success Guide',
        sections: [
          {
            title: 'Smart Opportunities',
            content: 'AI-matched client opportunities based on your expertise and their assessment gaps. Higher match scores indicate better fit.',
            tips: ['Respond quickly to high-match opportunities', 'Customize proposals based on client gaps', 'Follow up within 24 hours']
          },
          {
            title: 'Match Scoring',
            content: 'Our algorithm considers your specializations, client assessment gaps, geographic proximity, and historical success patterns.',
            tips: ['Update your profile regularly', 'Add relevant certifications', 'Maintain high response rates']
          },
          {
            title: 'Competitive Intelligence',
            content: 'Information about other providers bidding and your historical performance against them.',
            tips: ['Differentiate your proposals', 'Highlight unique expertise', 'Price competitively but sustainably']
          }
        ],
        quickActions: [
          { label: 'Update Profile', action: 'profile', icon: '👤' },
          { label: 'View Opportunities', action: 'opportunities', icon: '🎯' },
          { label: 'Success Tips', action: 'knowledge', icon: '🏆' }
        ]
      }
    },
    agency: {
      dashboard: {
        title: 'Agency Impact Optimization',
        sections: [
          {
            title: 'Economic Impact Metrics',
            content: 'Track the economic value your program creates: contracts secured, jobs created, business growth enabled.',
            tips: ['Use metrics for stakeholder reporting', 'Track ROI to justify program investment', 'Celebrate success stories']
          },
          {
            title: 'Contract Pipeline',
            content: 'Monitor businesses as they progress toward contract readiness. Focus resources on 60-80% ready businesses for maximum impact.',
            tips: ['Prioritize businesses close to certification', 'Intervene early for at-risk businesses', 'Celebrate certification achievements']
          },
          {
            title: 'Resource Partner Management',
            content: 'Connect ready businesses with lenders, investors, and contracting opportunities through the RP CRM-lite system.',
            tips: ['Seed RP requirements regularly', 'Review leads weekly', 'Facilitate introductions actively']
          }
        ],
        quickActions: [
          { label: 'Manage Licenses', action: 'licenses', icon: '🎫' },
          { label: 'RP Dashboard', action: 'rp', icon: '🤝' },
          { label: 'Analytics', action: 'analytics', icon: '📊' }
        ]
      }
    },
    navigator: {
      dashboard: {
        title: 'Navigator Coaching Excellence',
        sections: [
          {
            title: 'AI Coaching Insights',
            content: 'Leverage predictive analytics to identify at-risk clients and success opportunities for targeted intervention.',
            tips: ['Review at-risk clients weekly', 'Use success predictions for resource allocation', 'Follow AI recommendations for optimal outcomes']
          },
          {
            title: 'Regional Impact Tracking',
            content: 'Monitor the economic development impact of your guidance across the region.',
            tips: ['Track regional readiness trends', 'Identify industry-specific needs', 'Measure long-term economic impact']
          },
          {
            title: 'Intervention Strategies',
            content: 'Proactive coaching strategies based on client progress patterns and risk indicators.',
            tips: ['Reach out to inactive clients within 14 days', 'Focus on businesses 50-70% ready', 'Celebrate milestones and achievements']
          }
        ],
        quickActions: [
          { label: 'Review Approvals', action: 'approvals', icon: '✅' },
          { label: 'View Analytics', action: 'analytics', icon: '📈' },
          { label: 'AI Insights', action: 'insights', icon: '🤖' }
        ]
      }
    }
  };

  useEffect(() => {
    loadContextualHelp();
  }, [currentPage, userRole]);

  const loadContextualHelp = () => {
    const roleHelp = helpDatabase[userRole] || {};
    const pageHelp = roleHelp[currentPage] || roleHelp.dashboard || null;
    setHelpContent(pageHelp);
  };

  const searchHelp = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      // In production, this would search a comprehensive help database
      const mockResults = [
        {
          id: 'help_1',
          title: 'How to complete Financial Management assessment',
          excerpt: 'Step-by-step guide to completing the financial management assessment with required documentation...',
          category: 'Assessment',
          relevance: 95
        },
        {
          id: 'help_2',
          title: 'Understanding readiness scores and certification',
          excerpt: 'Learn how readiness scores are calculated and what percentage you need for certification eligibility...',
          category: 'Scoring',
          relevance: 87
        },
        {
          id: 'help_3',
          title: 'Working with service providers effectively',
          excerpt: 'Best practices for engaging service providers and managing professional service relationships...',
          category: 'Service Providers',
          relevance: 78
        }
      ].filter(result => 
        result.title.toLowerCase().includes(query.toLowerCase()) ||
        result.excerpt.toLowerCase().includes(query.toLowerCase())
      );

      setSearchResults(mockResults);
    } catch (error) {
      console.error('Help search failed:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        searchHelp(searchQuery);
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  if (!helpContent && !showHelp) {
    return (
      <button
        onClick={() => setShowHelp(true)}
        className="fixed bottom-4 left-36 w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-40"
        title="Get Help"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
    );
  }

  return (
    <>
      {/* Help Toggle Button */}
      <button
        onClick={() => setShowHelp(!showHelp)}
        className="fixed bottom-4 left-36 w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-40"
        title="Get Help"
      >
        {showHelp ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
      </button>

      {/* Help Panel */}
      {showHelp && (
        <div className="fixed bottom-20 right-4 w-80 h-96 bg-white rounded-lg shadow-2xl border z-50 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900">Help & Support</h3>
                <p className="text-xs text-slate-600">
                  {helpContent ? helpContent.title : 'Search for help topics'}
                </p>
              </div>
              <button
                onClick={() => setShowHelp(false)}
                className="text-slate-500 hover:text-slate-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b">
            <nav className="flex">
              {[
                { id: 'guide', label: 'Guide', icon: '📖' },
                { id: 'search', label: 'Search', icon: '🔍' },
                { id: 'contact', label: 'Contact', icon: '💬' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveHelpTab(tab.id)}
                  className={`flex-1 flex items-center justify-center gap-1 py-3 text-xs font-medium transition-colors ${
                    activeHelpTab === tab.id
                      ? 'text-purple-600 bg-purple-50 border-b-2 border-purple-600'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <span>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeHelpTab === 'guide' && helpContent && (
              <div className="space-y-4">
                {helpContent.sections.map((section, index) => (
                  <div key={index} className="border-b border-slate-100 pb-4 last:border-b-0">
                    <h4 className="font-medium text-slate-900 mb-2">{section.title}</h4>
                    <p className="text-sm text-slate-600 mb-3">{section.content}</p>
                    {section.tips && (
                      <div>
                        <div className="text-xs font-medium text-slate-700 mb-1">💡 Tips:</div>
                        <ul className="space-y-1">
                          {section.tips.map((tip, tipIndex) => (
                            <li key={tipIndex} className="text-xs text-slate-600 flex items-start gap-2">
                              <div className="w-1 h-1 bg-slate-400 rounded-full mt-1.5 flex-shrink-0"></div>
                              {tip}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}

                {/* Quick Actions */}
                {helpContent.quickActions && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="text-xs font-medium text-slate-700 mb-2">Quick Actions:</div>
                    <div className="space-y-2">
                      {helpContent.quickActions.map((action, index) => (
                        <button
                          key={index}
                          className="w-full flex items-center gap-2 p-2 text-left text-xs bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                          <span>{action.icon}</span>
                          {action.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeHelpTab === 'search' && (
              <div className="space-y-4">
                {/* Search Input */}
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search help topics..."
                    className="w-full px-3 py-2 pr-8 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                  <svg className="absolute right-2 top-2.5 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>

                {/* Search Results */}
                {loading ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto mb-2"></div>
                    <p className="text-xs text-slate-600">Searching...</p>
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="space-y-3">
                    {searchResults.map((result) => (
                      <div key={result.id} className="border rounded-lg p-3 hover:bg-slate-50 cursor-pointer transition-colors">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h5 className="font-medium text-slate-900 text-sm mb-1">{result.title}</h5>
                            <p className="text-xs text-slate-600 mb-2">{result.excerpt}</p>
                            <div className="flex items-center gap-2">
                              <span className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs">
                                {result.category}
                              </span>
                              <span className="text-xs text-slate-500">
                                {result.relevance}% relevant
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : searchQuery ? (
                  <div className="text-center py-4 text-slate-500">
                    <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-sm">No results found</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <h5 className="font-medium text-slate-900 text-sm">Popular Topics:</h5>
                    {[
                      'How to complete assessments',
                      'Understanding readiness scores',
                      'Working with service providers',
                      'Resource partner connections',
                      'Certification requirements'
                    ].map((topic) => (
                      <button
                        key={topic}
                        onClick={() => setSearchQuery(topic)}
                        className="block w-full text-left p-2 text-xs text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeHelpTab === 'contact' && (
              <div className="space-y-4">
                <div className="text-center">
                  <h4 className="font-medium text-slate-900 mb-2">Need Personal Assistance?</h4>
                  <p className="text-sm text-slate-600 mb-4">Our support team is here to help you succeed</p>
                </div>

                <div className="space-y-3">
                  <button className="w-full flex items-center gap-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">Start Live Chat</div>
                      <div className="text-xs text-slate-600">Average response: 2 minutes</div>
                    </div>
                  </button>

                  <button className="w-full flex items-center gap-3 p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-left">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">Email Support</div>
                      <div className="text-xs text-slate-600">Response within 24 hours</div>
                    </div>
                  </button>

                  <button className="w-full flex items-center gap-3 p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors text-left">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">Create Support Ticket</div>
                      <div className="text-xs text-slate-600">Detailed assistance</div>
                    </div>
                  </button>

                  <button className="w-full flex items-center gap-3 p-3 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors text-left">
                    <div className="p-2 bg-emerald-100 rounded-lg">
                      <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-slate-900 text-sm">AI Coach</div>
                      <div className="text-xs text-slate-600">Instant answers</div>
                    </div>
                  </button>
                </div>

                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center gap-2 text-sm text-yellow-800 mb-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">Pro Tip</span>
                  </div>
                  <p className="text-xs text-yellow-700">
                    Try our AI Coach first for instant answers, then reach out to human support for complex issues.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}