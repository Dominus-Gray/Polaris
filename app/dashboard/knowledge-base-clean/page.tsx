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
  Lock,
  ArrowRight
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

const CleanKnowledgeBasePage = () => {
  const { state } = useAuth()
  const [areas, setAreas] = useState<KnowledgeBaseArea[]>([])
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
      const areasResponse = await apiClient.request('/knowledge-base/areas')
      setAreas(areasResponse.data || areasResponse || [])
    } catch (error) {
      console.error('Error fetching knowledge base data:', error)
      // Comprehensive operational data
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
          context: selectedArea || 'general'
        })
      })

      const newAssistance: AIAssistance = {
        question: aiQuestion,
        response: response.data?.response || `Thank you for your question about "${aiQuestion}". I recommend reviewing the relevant knowledge base resources and connecting with a qualified service provider for personalized guidance on procurement readiness requirements.`,
        timestamp: new Date().toISOString()
      }
      setRecentAI(prev => [newAssistance, ...prev.slice(0, 4)])
      setAiQuestion('')
    } catch (error) {
      console.error('Error getting AI assistance:', error)
      const newAssistance: AIAssistance = {
        question: aiQuestion,
        response: `Thank you for your question about "${aiQuestion}". I recommend reviewing the relevant knowledge base resources and connecting with a qualified service provider for personalized guidance.`,
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
      // Create comprehensive fallback
      const areaNames = {
        'area1': 'Business Formation & Registration',
        'area2': 'Financial Operations & Management',
        'area3': 'Legal & Contracting Compliance',
        'area4': 'Quality Management & Standards',
        'area5': 'Technology & Security Infrastructure',
        'area6': 'Human Resources & Capacity',
        'area7': 'Performance Tracking & Reporting',
        'area8': 'Risk Management & Business Continuity',
        'area9': 'Supply Chain Management & Vendor Relations',
        'area10': 'Competitive Advantage & Market Position'
      }
      
      const areaName = areaNames[areaId] || 'Business Area'
      const template = `# ${areaName} - Procurement Readiness Framework

## Assessment Guidelines
Complete framework for achieving procurement readiness in ${areaName}.

### Tier 1 Requirements (Basic)
- Foundational compliance measures
- Basic documentation requirements
- Essential process establishment

### Tier 2 Requirements (Enhanced)
- Advanced capability development
- Comprehensive documentation
- Evidence-based validation

### Tier 3 Requirements (Advanced)
- Industry best practices
- Continuous improvement systems
- Competitive advantage development

Generated by Polaris Platform - ${new Date().toLocaleDateString()}
`
      
      const blob = new Blob([template], { type: 'text/markdown' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `polaris_${areaId}_framework.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  }

  const filteredAreas = areas.filter(area => 
    (selectedArea === '' || area.area_id === selectedArea) &&
    (searchTerm === '' || 
     area.area_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     area.description.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="polaris-page-container">
      {/* Clean Header */}
      <div className="polaris-page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="polaris-heading-xl">Knowledge Base</h1>
            <p className="polaris-body-lg mt-2">
              Access comprehensive resources, templates, and AI-powered guidance for procurement readiness.
            </p>
          </div>
          
          <button
            onClick={() => setShowAIChat(!showAIChat)}
            className={`polaris-btn-primary ${showAIChat ? 'bg-green-600 hover:bg-green-700' : ''}`}
          >
            <Bot className="polaris-icon-md mr-2" />
            {showAIChat ? 'Hide AI Assistant' : 'Show AI Assistant'}
          </button>
        </div>
      </div>

      <div className="polaris-grid-2">
        {/* Main Content */}
        <div className="lg:col-span-1">
          {/* Clean Search */}
          <div className="polaris-section">
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1">
                <Search className="polaris-icon-md absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="polaris-input-clean pl-10"
                />
              </div>
              
              <select
                value={selectedArea}
                onChange={(e) => setSelectedArea(e.target.value)}
                className="polaris-select-clean"
              >
                <option value="">All Areas</option>
                {areas.map((area) => (
                  <option key={area.area_id} value={area.area_id}>{area.area_name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Clean Business Areas Grid */}
          <div className="polaris-section">
            <div className="polaris-section-header">
              <h2 className="polaris-section-title">Business Areas</h2>
              <span className="polaris-body-sm text-gray-500">
                {filteredAreas.length} areas available
              </span>
            </div>
            
            <div className="polaris-space-y-lg">
              {filteredAreas.map((area) => (
                <div key={area.area_id} className="polaris-card-clean">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-3">
                        <h3 className="polaris-heading-md mr-3">{area.area_name}</h3>
                        {area.is_locked && (
                          <Lock className="polaris-icon-md text-yellow-500" />
                        )}
                      </div>
                      
                      <p className="polaris-body-sm text-gray-600 mb-4 leading-relaxed">
                        {area.description}
                      </p>
                      
                      <div className="flex items-center space-x-6 text-sm text-gray-500 mb-6">
                        <span className="flex items-center">
                          <FileText className="polaris-icon-sm mr-1" />
                          {area.resource_count} resources
                        </span>
                        <span className="flex items-center">
                          <Download className="polaris-icon-sm mr-1" />
                          {area.templates_available} templates
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <Link
                      href={`/dashboard/knowledge-base/${area.area_id}`}
                      className={`polaris-btn-secondary ${area.is_locked ? 'opacity-50 pointer-events-none' : ''}`}
                    >
                      <BookOpen className="polaris-icon-sm mr-2" />
                      Browse Resources
                    </Link>
                    
                    {!area.is_locked && area.templates_available > 0 && (
                      <button
                        onClick={() => handleDownloadTemplate(area.area_id)}
                        className="polaris-btn-primary"
                        data-area={area.area_id}
                      >
                        <Download className="polaris-icon-sm mr-2" />
                        Download Template
                      </button>
                    )}

                    {area.is_locked && (
                      <span className="polaris-badge-warning-clean">
                        Premium Access Required
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Clean AI Assistant Sidebar */}
        <div className="lg:col-span-1">
          {showAIChat && (
            <div className="polaris-card-clean sticky top-8">
              <div className="flex items-center mb-6">
                <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <Bot className="polaris-icon-md text-blue-600" />
                </div>
                <h3 className="polaris-heading-md">AI Assistant</h3>
              </div>

              {/* Clean AI Input */}
              <div className="polaris-space-y-md mb-6">
                <textarea
                  value={aiQuestion}
                  onChange={(e) => setAiQuestion(e.target.value)}
                  rows={3}
                  placeholder="Ask about procurement readiness, compliance requirements, or business best practices..."
                  className="polaris-input-clean resize-none"
                />
                <button
                  onClick={handleAIQuestion}
                  disabled={isAskingAI || !aiQuestion.trim()}
                  className="polaris-btn-primary w-full disabled:opacity-50"
                >
                  {isAskingAI ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span className="ml-2">AI is thinking...</span>
                    </>
                  ) : (
                    <>
                      <MessageSquare className="polaris-icon-sm mr-2" />
                      Ask AI Assistant
                    </>
                  )}
                </button>
              </div>

              {/* Clean AI Conversations */}
              {recentAI.length > 0 && (
                <div className="polaris-space-y-md">
                  <h4 className="polaris-heading-sm">Recent Assistance</h4>
                  <div className="polaris-space-y-md max-h-96 overflow-y-auto">
                    {recentAI.map((ai, index) => (
                      <div key={index} className="polaris-card-minimal">
                        <div className="polaris-body-sm font-medium text-gray-900 mb-2">
                          <MessageSquare className="polaris-icon-sm inline mr-1" />
                          {ai.question}
                        </div>
                        <div className="polaris-body-sm text-gray-700 mb-3 leading-relaxed">
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
                  <p className="polaris-body-sm text-gray-500">
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

export default CleanKnowledgeBasePage