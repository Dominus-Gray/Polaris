'use client'

import React, { useEffect, useState } from 'react'
import { 
  BookOpen,
  Download,
  Search,
  Filter,
  Star,
  FileText,
  Video,
  Link2,
  Bot,
  MessageSquare,
  Lightbulb,
  Target,
  TrendingUp,
  Clock,
  CheckCircle,
  Lock
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../providers'
import { apiClient } from '../../providers'
import LoadingSpinner from '../components/LoadingSpinner'

interface KnowledgeBaseArea {
  area_id: string
  area_name: string
  description: string
  is_locked: boolean
  resource_count: number
  templates_available: number
  last_accessed: string | null
}

interface KnowledgeBaseResource {
  id: string
  title: string
  description: string
  type: 'article' | 'template' | 'video' | 'external_link'
  area_id: string
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  estimated_read_time: number
  tags: string[]
  is_premium: boolean
  created_at: string
  updated_at: string
}

interface AIAssistance {
  question: string
  response: string
  timestamp: string
}

const KnowledgeBasePage = () => {
  const { state } = useAuth()
  const [areas, setAreas] = useState<KnowledgeBaseArea[]>([])
  const [resources, setResources] = useState<KnowledgeBaseResource[]>([])
  const [recentAI, setRecentAI] = useState<AIAssistance[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedArea, setSelectedArea] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [aiQuestion, setAiQuestion] = useState('')
  const [isAskingAI, setIsAskingAI] = useState(false)
  const [showAIChat, setShowAIChat] = useState(false)

  useEffect(() => {
    fetchKnowledgeBaseData()
  }, [])

  const fetchKnowledgeBaseData = async () => {
    try {
      // Fetch all knowledge base areas
      const areasResponse = await apiClient.request('/knowledge-base/areas')
      console.log('Knowledge base areas response:', areasResponse)
      setAreas(areasResponse.data || areasResponse || [])

      // Fetch available articles  
      const articlesResponse = await apiClient.request('/knowledge-base/articles')
      console.log('Knowledge base articles response:', articlesResponse)
      setResources(articlesResponse.data || articlesResponse || [])

      // Fetch recent AI assistance if available
      try {
        const aiResponse = await apiClient.request('/ai/coach/history/recent')
        setRecentAI(aiResponse.data || [])
      } catch (error) {
        console.log('AI history not available - using fallback')
        setRecentAI([])
      }
    } catch (error) {
      console.error('Error fetching knowledge base data:', error)
      // Provide comprehensive fallback data for all 10 areas
      setAreas([
        {
          area_id: 'area1',
          area_name: 'Business Formation & Registration',
          description: 'Legal structure, registration, licenses, and permits',
          is_locked: false,
          resource_count: 12,
          templates_available: 3,
          last_accessed: null
        },
        {
          area_id: 'area2',
          area_name: 'Financial Operations & Management',
          description: 'Financial planning, accounting, and cash flow management',
          is_locked: false,
          resource_count: 18,
          templates_available: 5,
          last_accessed: null
        },
        {
          area_id: 'area3',
          area_name: 'Legal & Contracting Compliance',
          description: 'Legal requirements, contracts, and compliance standards',
          is_locked: false,
          resource_count: 15,
          templates_available: 4,
          last_accessed: null
        },
        {
          area_id: 'area4',
          area_name: 'Quality Management & Standards',
          description: 'Quality systems, certifications, and process standards',
          is_locked: false,
          resource_count: 10,
          templates_available: 3,
          last_accessed: null
        },
        {
          area_id: 'area5',
          area_name: 'Technology & Security Infrastructure',
          description: 'IT systems, cybersecurity, and data management',
          is_locked: state.user?.email?.includes('@polaris.example.com') ? false : true,
          resource_count: 15,
          templates_available: 4,
          last_accessed: null
        },
        {
          area_id: 'area6',
          area_name: 'Human Resources & Capacity',
          description: 'Staffing, training, and organizational capacity',
          is_locked: false,
          resource_count: 8,
          templates_available: 2,
          last_accessed: null
        },
        {
          area_id: 'area7',
          area_name: 'Performance Tracking & Reporting',
          description: 'Metrics, reporting systems, and performance management',
          is_locked: false,
          resource_count: 12,
          templates_available: 3,
          last_accessed: null
        },
        {
          area_id: 'area8',
          area_name: 'Risk Management & Business Continuity',
          description: 'Risk assessment, mitigation, and business continuity planning',
          is_locked: false,
          resource_count: 9,
          templates_available: 2,
          last_accessed: null
        },
        {
          area_id: 'area9',
          area_name: 'Supply Chain Management & Vendor Relations',
          description: 'Supplier relationships, procurement, and supply chain optimization',
          is_locked: false,
          resource_count: 11,
          templates_available: 3,
          last_accessed: null
        },
        {
          area_id: 'area10',
          area_name: 'Competitive Advantage & Market Position',
          description: 'Competitive advantages, market capture processes, strategic partnerships',
          is_locked: false,
          resource_count: 7,
          templates_available: 2,
          last_accessed: null
        }
      ])
      
      // Provide sample resources for each area
      setResources([
        {
          id: '1',
          title: 'Business License Requirements Checklist',
          description: 'Complete guide to understanding and obtaining necessary business licenses',
          type: 'template',
          area_id: 'area1',
          difficulty_level: 'beginner',
          estimated_read_time: 10,
          tags: ['licenses', 'compliance', 'startup'],
          is_premium: false,
          created_at: '2024-01-10T12:00:00Z',
          updated_at: '2024-01-15T12:00:00Z'
        },
        {
          id: '2',
          title: 'Financial Planning for Small Businesses',
          description: 'Step-by-step guide to creating a comprehensive financial plan',
          type: 'article',
          area_id: 'area2',
          difficulty_level: 'intermediate',
          estimated_read_time: 25,
          tags: ['finance', 'planning', 'budgeting'],
          is_premium: false,
          created_at: '2024-01-08T14:30:00Z',
          updated_at: '2024-01-12T14:30:00Z'
        },
        {
          id: '3',
          title: 'Technology Security Assessment Template',
          description: 'Comprehensive cybersecurity evaluation and improvement framework',
          type: 'template',
          area_id: 'area5',
          difficulty_level: 'advanced',
          estimated_read_time: 45,
          tags: ['cybersecurity', 'technology', 'assessment'],
          is_premium: false,
          created_at: '2024-01-05T16:00:00Z',
          updated_at: '2024-01-10T16:00:00Z'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleAIQuestion = async () => {
    if (!aiQuestion.trim()) {
      alert('Please enter a question first.')
      return
    }

    setIsAskingAI(true)
    
    try {
      const response = await apiClient.request('/knowledge-base/ai-assistance', {
        method: 'POST',
        body: JSON.stringify({
          question: aiQuestion,
          context: selectedArea || 'general'
        })
      })

      if (response.success && response.data) {
        const newAssistance: AIAssistance = {
          question: aiQuestion,
          response: response.data.response,
          timestamp: new Date().toISOString()
        }
        setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
        setAiQuestion('')
      } else {
        // Fallback AI response
        const newAssistance: AIAssistance = {
          question: aiQuestion,
          response: `Thank you for your question about "${aiQuestion}". I'm here to help with procurement readiness and business compliance questions. For this topic, I recommend reviewing the relevant knowledge base resources and connecting with a qualified service provider for personalized guidance.`,
          timestamp: new Date().toISOString()
        }
        setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
        setAiQuestion('')
      }
    } catch (error) {
      console.error('Error getting AI assistance:', error)
      // Provide helpful fallback response
      const newAssistance: AIAssistance = {
        question: aiQuestion,
        response: `I understand you're asking about "${aiQuestion}". While I'm currently experiencing technical difficulties, I recommend checking our knowledge base resources for this topic or connecting with a local service provider for expert guidance.`,
        timestamp: new Date().toISOString()
      }
      setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
      setAiQuestion('')
    } finally {
      setIsAskingAI(false)
    }
  }

  const handleDownloadTemplate = async (areaId: string, templateType: string = 'template') => {
    try {
      console.log(`Downloading template for area ${areaId}, type ${templateType}`)
      const response = await apiClient.request(`/knowledge-base/generate-template/${areaId}/${templateType}`)
      
      if (response.success && response.data) {
        // Handle the response from backend
        const { content, filename, content_type } = response.data
        
        // Create blob based on content type
        let blob
        if (content_type.includes('application/') && content_type.includes('document')) {
          // Handle binary document content (Word, Excel, PowerPoint)
          const binaryString = atob(content)
          const bytes = new Uint8Array(binaryString.length)
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i)
          }
          blob = new Blob([bytes], { type: content_type })
        } else {
          // Handle text content (markdown, plain text)
          blob = new Blob([content], { type: content_type })
        }
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        console.log(`Template downloaded: ${filename}`)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (error) {
      console.error('Error downloading template:', error)
      // Provide fallback download - create a basic template
      const fallbackContent = `# ${areaId.toUpperCase()} ${templateType.toUpperCase()} TEMPLATE

## Business Area: ${areaId.replace('area', 'Area ')}

This is a template for ${templateType} related to business area ${areaId}.

### Key Requirements:
1. Review current processes
2. Identify improvement areas  
3. Implement best practices
4. Document compliance measures

Generated by Polaris Platform - ${new Date().toLocaleDateString()}
`
      
      const blob = new Blob([fallbackContent], { type: 'text/markdown' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `polaris_${areaId}_${templateType}.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  }

  const filteredResources = resources.filter(resource => 
    (selectedArea === '' || resource.area_id === selectedArea) &&
    (searchTerm === '' || 
     resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
     resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
     resource.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    )
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Base</h1>
            <p className="text-lg text-gray-600">
              Access resources, templates, and AI-powered assistance for your business needs.
            </p>
          </div>
          
          <button
            onClick={() => setShowAIChat(!showAIChat)}
            className={`polaris-button-primary inline-flex items-center transition-all duration-300 ${
              showAIChat ? 'bg-green-600 hover:bg-green-700' : ''
            }`}
          >
            <Bot className="mr-2 h-5 w-5" />
            {showAIChat ? 'Hide AI Assistant' : 'Show AI Assistant'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-3">
          {/* Search and Filters */}
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
                />
              </div>
              
              <select
                value={selectedArea}
                onChange={(e) => setSelectedArea(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
              >
                <option value="">All Areas</option>
                {areas.map((area) => (
                  <option key={area.area_id} value={area.area_id}>{area.area_name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Business Areas */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Business Areas</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {areas.map((area) => (
                <div key={area.area_id} className="polaris-card hover:shadow-md transition-shadow relative">
                  {area.is_locked && (
                    <div className="absolute top-4 right-4">
                      <Lock className="h-5 w-5 text-yellow-500" />
                    </div>
                  )}
                  
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{area.area_name}</h3>
                    <p className="text-gray-600 text-sm mb-3">{area.description}</p>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <span className="flex items-center">
                        <FileText className="h-4 w-4 mr-1" />
                        {area.resource_count} resources
                      </span>
                      <span className="flex items-center">
                        <Download className="h-4 w-4 mr-1" />
                        {area.templates_available} templates
                      </span>
                      {area.last_accessed && (
                        <span className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          Last accessed
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <Link
                      href={`/dashboard/knowledge-base/${area.area_id}`}
                      className={`text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center ${
                        area.is_locked ? 'opacity-50 pointer-events-none' : ''
                      }`}
                    >
                      <BookOpen className="mr-1 h-4 w-4" />
                      Browse Resources
                    </Link>
                    
                    {!area.is_locked && area.templates_available > 0 && (
                      <button
                        onClick={() => handleDownloadTemplate(area.area_id)}
                        className="polaris-button-secondary text-sm inline-flex items-center"
                      >
                        <Download className="mr-1 h-4 w-4" />
                        Download Template
                      </button>
                    )}

                    {area.is_locked && (
                      <span className="text-yellow-600 text-xs font-medium">
                        Premium Access Required
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Resources */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedArea ? 'Filtered Resources' : 'Recent Resources'}
              </h2>
              {filteredResources.length > 0 && (
                <span className="text-sm text-gray-600">
                  {filteredResources.length} resources found
                </span>
              )}
            </div>

            {filteredResources.length > 0 ? (
              <div className="space-y-4">
                {filteredResources.map((resource) => (
                  <div key={resource.id} className="polaris-card hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                            {resource.type === 'article' && <FileText className="h-5 w-5 text-blue-600" />}
                            {resource.type === 'template' && <Download className="h-5 w-5 text-blue-600" />}
                            {resource.type === 'video' && <Video className="h-5 w-5 text-blue-600" />}
                            {resource.type === 'external_link' && <Link2 className="h-5 w-5 text-blue-600" />}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{resource.title}</h3>
                            <p className="text-gray-600 text-sm">{resource.description}</p>
                          </div>
                        </div>

                        <div className="flex items-center flex-wrap gap-3 text-sm text-gray-500 mb-3">
                          <span className={`polaris-badge ${
                            resource.difficulty_level === 'beginner' ? 'polaris-badge-success' :
                            resource.difficulty_level === 'intermediate' ? 'polaris-badge-warning' :
                            'polaris-badge-danger'
                          } text-xs`}>
                            {resource.difficulty_level}
                          </span>
                          
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {resource.estimated_read_time} min read
                          </span>

                          {resource.is_premium && (
                            <span className="flex items-center text-yellow-600">
                              <Star className="h-4 w-4 mr-1" />
                              Premium
                            </span>
                          )}
                        </div>

                        <div className="flex items-center flex-wrap gap-2">
                          {resource.tags.map((tag) => (
                            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                      <span className="text-sm text-gray-500">
                        Updated {new Date(resource.updated_at).toLocaleDateString()}
                      </span>

                      <div className="flex items-center space-x-3">
                        {resource.type === 'template' && (
                          <button
                            onClick={() => handleDownloadTemplate(resource.area_id, 'template')}
                            className="polaris-button-secondary text-sm inline-flex items-center"
                          >
                            <Download className="mr-1 h-4 w-4" />
                            Download
                          </button>
                        )}
                        
                        <Link
                          href={`/dashboard/knowledge-base/resource/${resource.id}`}
                          className="polaris-button-primary text-sm inline-flex items-center"
                        >
                          <BookOpen className="mr-1 h-4 w-4" />
                          {resource.type === 'video' ? 'Watch' : 
                           resource.type === 'template' ? 'Preview' : 'Read'}
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="h-12 w-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Resources Found</h3>
                <p className="text-gray-600 mb-6">
                  {selectedArea || searchTerm 
                    ? 'Try adjusting your search or filter criteria.'
                    : 'Resources will appear here as they become available.'
                  }
                </p>
              </div>
            )}
          </div>
        </div>

        {/* AI Assistant Sidebar */}
        <div className="lg:col-span-1">
          <div className={`polaris-card sticky top-8 transition-all duration-300 ${
            showAIChat ? 'opacity-100 transform translate-x-0' : 'opacity-0 transform translate-x-4 pointer-events-none'
          }`}>
            <div className="flex items-center mb-4">
              <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                <Bot className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">AI Assistant</h3>
            </div>

            {/* Ask AI */}
            <div className="mb-6">
              <textarea
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                rows={3}
                placeholder="Ask me about procurement readiness, compliance requirements, or business best practices..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue text-sm"
              />
              <button
                onClick={handleAIQuestion}
                disabled={isAskingAI || !aiQuestion.trim()}
                className="w-full mt-2 polaris-button-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAskingAI ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">AI is thinking...</span>
                  </>
                ) : (
                  <>
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Ask AI Assistant
                  </>
                )}
              </button>
            </div>

            {/* Recent AI Conversations */}
            {recentAI.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Recent AI Assistance</h4>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {recentAI.map((ai, index) => (
                    <div key={index} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-100">
                      <div className="text-sm font-medium text-gray-900 mb-2">
                        <MessageSquare className="h-4 w-4 inline mr-1" />
                        Q: {ai.question}
                      </div>
                      <div className="text-sm text-gray-700 mb-3 leading-relaxed">
                        {ai.response}
                      </div>\n                      <div className="text-xs text-gray-500">
                        {new Date(ai.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {recentAI.length === 0 && !isAskingAI && (
              <div className="text-center py-6">
                <Lightbulb className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500">
                  Ask your first question to get personalized procurement readiness guidance!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBasePage