'use client'

import React, { useEffect, useState } from 'react'
import { 
  BookOpen,
  Download,
  Search,
  Bot,
  MessageSquare,
  Lightbulb,
  FileText,
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
}

interface AIAssistance {
  question: string
  response: string
  timestamp: string
}

const KnowledgeBasePage = () => {
  const { state } = useAuth()
  const [areas, setAreas] = useState<KnowledgeBaseArea[]>([])
  const [recentAI, setRecentAI] = useState<AIAssistance[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [aiQuestion, setAiQuestion] = useState('')
  const [isAskingAI, setIsAskingAI] = useState(false)
  const [showAIChat, setShowAIChat] = useState(false)

  useEffect(() => {
    fetchKnowledgeBaseData()
  }, [])

  const fetchKnowledgeBaseData = async () => {
    try {
      const areasResponse = await apiClient.request('/knowledge-base/areas')
      setAreas(areasResponse.data || areasResponse || [])
    } catch (error) {
      console.error('Error fetching knowledge base data:', error)
      setAreas([
        { area_id: 'area1', area_name: 'Business Formation & Registration', description: 'Legal structure, registration, licenses, and permits', is_locked: false, resource_count: 12, templates_available: 3 },
        { area_id: 'area2', area_name: 'Financial Operations & Management', description: 'Financial planning, accounting, and cash flow management', is_locked: false, resource_count: 18, templates_available: 5 },
        { area_id: 'area3', area_name: 'Legal & Contracting Compliance', description: 'Legal requirements, contracts, and compliance standards', is_locked: false, resource_count: 15, templates_available: 4 },
        { area_id: 'area4', area_name: 'Quality Management & Standards', description: 'Quality systems, certifications, and process standards', is_locked: false, resource_count: 10, templates_available: 3 },
        { area_id: 'area5', area_name: 'Technology & Security Infrastructure', description: 'IT systems, cybersecurity, and data management', is_locked: !state.user?.email?.includes('@polaris.example.com'), resource_count: 15, templates_available: 4 },
        { area_id: 'area6', area_name: 'Human Resources & Capacity', description: 'Staffing, training, and organizational capacity', is_locked: false, resource_count: 8, templates_available: 2 },
        { area_id: 'area7', area_name: 'Performance Tracking & Reporting', description: 'Metrics, reporting systems, and performance management', is_locked: false, resource_count: 12, templates_available: 3 },
        { area_id: 'area8', area_name: 'Risk Management & Business Continuity', description: 'Risk assessment, mitigation, and business continuity planning', is_locked: false, resource_count: 9, templates_available: 2 },
        { area_id: 'area9', area_name: 'Supply Chain Management & Vendor Relations', description: 'Supplier relationships, procurement, and supply chain optimization', is_locked: false, resource_count: 11, templates_available: 3 },
        { area_id: 'area10', area_name: 'Competitive Advantage & Market Position', description: 'Competitive advantages, market capture processes, strategic partnerships', is_locked: false, resource_count: 7, templates_available: 2 }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleAIQuestion = async () => {
    if (!aiQuestion.trim()) return

    setIsAskingAI(true)
    
    try {
      const response = await apiClient.request('/knowledge-base/ai-assistance', {
        method: 'POST',
        body: JSON.stringify({
          question: aiQuestion,
          context: 'general'
        })
      })

      const newAssistance: AIAssistance = {
        question: aiQuestion,
        response: response.data?.response || `Thank you for your question about "${aiQuestion}". I recommend reviewing the relevant knowledge base resources and connecting with a qualified service provider for personalized guidance.`,
        timestamp: new Date().toISOString()
      }
      setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
      setAiQuestion('')
    } catch (error) {
      console.error('Error getting AI assistance:', error)
      const newAssistance: AIAssistance = {
        question: aiQuestion,
        response: `Thank you for your question about "${aiQuestion}". For procurement readiness guidance on this topic, I recommend checking our knowledge base resources or connecting with a qualified service provider.`,
        timestamp: new Date().toISOString()
      }
      setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
      setAiQuestion('')
    } finally {
      setIsAskingAI(false)
    }
  }

  const handleDownloadTemplate = async (areaId: string) => {
    try {
      const response = await apiClient.request(`/knowledge-base/generate-template/${areaId}/template`)
      
      if (response.success && response.data) {
        const { content, filename } = response.data
        const blob = new Blob([content], { type: 'text/markdown' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename || `polaris_${areaId}_template.md`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error downloading template:', error)
      alert('Template download feature is being prepared. Please check back soon.')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Clean Header */}
      <div className="mb-12">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">Knowledge Base</h1>
            <p className="text-lg text-gray-600 leading-relaxed max-w-3xl">
              Access comprehensive resources, templates, and AI-powered guidance for procurement readiness.
            </p>
          </div>
          
          <button
            onClick={() => setShowAIChat(!showAIChat)}
            className={`inline-flex items-center px-6 py-3 font-medium text-sm rounded-lg shadow-sm transition-all duration-200 ${
              showAIChat 
                ? 'bg-green-600 text-white hover:bg-green-700' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Bot className="h-5 w-5 mr-2" />
            {showAIChat ? 'Hide AI Assistant' : 'Show AI Assistant'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Main Content - Clean */}
        <div className="lg:col-span-2">
          {/* Clean Search */}
          <div className="mb-8">
            <div className="relative">
              <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search resources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Clean Business Areas */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-semibold text-gray-900">Business Areas</h2>
              <span className="text-sm text-gray-500">{areas.length} areas available</span>
            </div>
            
            <div className="space-y-6">
              {areas.filter(area => 
                searchTerm === '' || 
                area.area_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                area.description.toLowerCase().includes(searchTerm.toLowerCase())
              ).map((area) => (
                <div key={area.area_id} className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center mb-3">
                        <h3 className="text-xl font-semibold text-gray-900 mr-3">{area.area_name}</h3>
                        {area.is_locked && (
                          <Lock className="h-5 w-5 text-yellow-500" />
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-6 leading-relaxed">
                        {area.description}
                      </p>
                      
                      <div className="flex items-center space-x-8 text-sm text-gray-500 mb-6">
                        <span className="flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          {area.resource_count} resources
                        </span>
                        <span className="flex items-center">
                          <Download className="h-4 w-4 mr-2" />
                          {area.templates_available} templates
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <Link
                      href={`/dashboard/knowledge-base/${area.area_id}`}
                      className={`inline-flex items-center px-4 py-2 bg-white text-gray-700 border border-gray-300 font-medium text-sm rounded-lg hover:bg-gray-50 transition-colors ${
                        area.is_locked ? 'opacity-50 pointer-events-none' : ''
                      }`}
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      Browse Resources
                    </Link>
                    
                    {!area.is_locked && area.templates_available > 0 && (
                      <button
                        onClick={() => handleDownloadTemplate(area.area_id)}
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download Template
                      </button>
                    )}

                    {area.is_locked && (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Premium Access Required
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Assistant Sidebar - Clean */}
        <div className="lg:col-span-1">
          {showAIChat && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 sticky top-8">
              <div className="flex items-center mb-6">
                <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <Bot className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">AI Assistant</h3>
              </div>

              <div className="space-y-4 mb-6">
                <textarea
                  value={aiQuestion}
                  onChange={(e) => setAiQuestion(e.target.value)}
                  rows={3}
                  placeholder="Ask about procurement readiness, compliance requirements, or business best practices..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                <button
                  onClick={handleAIQuestion}
                  disabled={isAskingAI || !aiQuestion.trim()}
                  className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {isAskingAI ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span className="ml-2">AI is thinking...</span>
                    </>
                  ) : (
                    <>
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Ask AI Assistant
                    </>
                  )}
                </button>
              </div>

              {recentAI.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Recent Assistance</h4>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {recentAI.map((ai, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="text-sm font-medium text-gray-900 mb-2">
                          <MessageSquare className="h-4 w-4 inline mr-1" />
                          {ai.question}
                        </div>
                        <div className="text-sm text-gray-700 mb-3 leading-relaxed">
                          {ai.response}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(ai.timestamp).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recentAI.length === 0 && !isAskingAI && (
                <div className="text-center py-8">
                  <Lightbulb className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">
                    Ask your first question for personalized procurement readiness guidance!
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBasePage