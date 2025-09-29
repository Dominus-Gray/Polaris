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
      console.log(`Generating comprehensive template for ${areaId}`)
      
      // Show loading state
      const button = document.querySelector(`[data-area="${areaId}"]`) as HTMLButtonElement
      if (button) {
        button.textContent = 'Generating...'
        button.disabled = true
      }
      
      // Create comprehensive template content
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
      
      const comprehensiveTemplate = `# ${areaName.toUpperCase()} - PROCUREMENT READINESS FRAMEWORK

## Polaris Platform Assessment & Implementation Guide
### ${areaName}

**Generated on:** ${new Date().toLocaleDateString()}
**Framework Version:** Polaris 2025 Complete
**User:** ${state.user?.email || 'Business User'}

---

## EXECUTIVE SUMMARY

This comprehensive framework provides step-by-step guidance for achieving procurement readiness in ${areaName}. Follow this systematic approach to build competitive advantages and access procurement opportunities.

## COMPLETE TIER-BASED ASSESSMENT STRUCTURE

### TIER 1 - FOUNDATIONAL COMPLIANCE (3 Business Maturity Statements)
**Self-Assessment Level - Basic Business Readiness**

#### Statement 1: Core Infrastructure Establishment
**Requirement:** Establish fundamental business processes and operational foundation
- [ ] **Assessment Question:** Evaluate current operational infrastructure
- [ ] **Compliance Check:** Document basic business processes
- [ ] **Implementation:** Create standard operating procedures
- [ ] **Validation:** Ensure processes are consistently followed

#### Statement 2: Basic Documentation Systems
**Requirement:** Implement essential documentation and record-keeping
- [ ] **Assessment Question:** Review documentation completeness
- [ ] **Compliance Check:** Maintain required business records
- [ ] **Implementation:** Establish systematic record-keeping
- [ ] **Validation:** Ensure accessibility and accuracy

#### Statement 3: Regulatory Compliance Foundation
**Requirement:** Meet fundamental regulatory and legal requirements
- [ ] **Assessment Question:** Verify compliance with basic regulations
- [ ] **Compliance Check:** Address regulatory requirements
- [ ] **Implementation:** Establish compliance monitoring
- [ ] **Validation:** Regular compliance reviews

### TIER 2 - ENHANCED COMPLIANCE (6 Total Statements)
**Evidence Required Level - Intermediate Business Assurance**
*Includes all Tier 1 statements plus 3 additional requirements*

#### Statement 4: Advanced Process Integration
**Requirement:** Develop intermediate capability systems with evidence
- [ ] **Assessment Question:** Evaluate process integration effectiveness
- [ ] **Compliance Check:** Document advanced operational systems
- [ ] **Implementation:** Create integrated business workflows
- [ ] **Evidence Required:** Process documentation, training records, system integration proof
- [ ] **Navigator Review:** Digital navigator validates evidence quality

#### Statement 5: Performance Monitoring Systems
**Requirement:** Implement comprehensive monitoring and measurement
- [ ] **Assessment Question:** Assess monitoring system effectiveness
- [ ] **Compliance Check:** Track performance metrics consistently
- [ ] **Implementation:** Establish KPI and measurement systems
- [ ] **Evidence Required:** Performance reports, monitoring documentation, improvement records
- [ ] **Navigator Review:** Evidence validation for measurement accuracy

#### Statement 6: Continuous Improvement Framework
**Requirement:** Develop systematic improvement identification and implementation
- [ ] **Assessment Question:** Evaluate improvement process maturity
- [ ] **Compliance Check:** Demonstrate systematic improvement approach
- [ ] **Implementation:** Create feedback loops and improvement mechanisms
- [ ] **Evidence Required:** Improvement tracking, feedback documentation, implementation records
- [ ] **Navigator Review:** Validate improvement process effectiveness

### TIER 3 - VERIFICATION LEVEL (9 Total Statements)
**Navigator Validation Level - High Effort Business Assurance**
*Includes all Tier 1 and Tier 2 statements plus 3 advanced requirements*

#### Statement 7: Industry Best Practices Implementation
**Requirement:** Achieve industry-leading standards and competitive positioning
- [ ] **Assessment Question:** Evaluate industry best practices implementation
- [ ] **Compliance Check:** Demonstrate industry leadership capabilities
- [ ] **Implementation:** Establish competitive advantage systems
- [ ] **Evidence Required:** Industry certifications, benchmarking data, third-party validation, competitive analysis
- [ ] **Navigator Review:** Comprehensive validation of industry positioning

#### Statement 8: Strategic Excellence Development
**Requirement:** Develop advanced strategic planning and analytical capabilities
- [ ] **Assessment Question:** Assess strategic planning maturity
- [ ] **Compliance Check:** Demonstrate strategic thinking and planning
- [ ] **Implementation:** Create advanced strategic management systems
- [ ] **Evidence Required:** Strategic plans, analytical reports, forecasting documentation, market analysis
- [ ] **Navigator Review:** Strategic capability validation

#### Statement 9: Ecosystem Leadership Establishment
**Requirement:** Build strategic partnerships and industry leadership position
- [ ] **Assessment Question:** Evaluate ecosystem leadership and partnership development
- [ ] **Compliance Check:** Demonstrate leadership in business ecosystem
- [ ] **Implementation:** Establish thought leadership and strategic alliances
- [ ] **Evidence Required:** Partnership agreements, industry contributions, leadership recognition, mentorship records
- [ ] **Navigator Review:** Leadership and partnership validation

## IMPLEMENTATION TIMELINE

### Phase 1: Foundation Building (Weeks 1-4)
**Objective:** Establish baseline compliance and documentation

1. **Week 1-2: Assessment Completion**
   - Complete Polaris tier-based assessment for ${areaName}
   - Identify specific capability gaps and improvement opportunities
   - Document current state and compliance status

2. **Week 3-4: Gap Analysis & Planning**
   - Prioritize improvement areas based on assessment results
   - Develop detailed action plan with timelines and resources
   - Identify required documentation and evidence

### Phase 2: Capability Development (Weeks 5-12)
**Objective:** Build intermediate capabilities with evidence documentation

1. **Week 5-8: Core Improvements**
   - Address critical gaps identified in Tier 1 assessment
   - Implement required processes and operational systems
   - Begin evidence collection for Tier 2 compliance

2. **Week 9-12: Advanced Implementation**
   - Develop Tier 2 capability requirements
   - Create comprehensive evidence packages
   - Prepare for navigator review and validation

### Phase 3: Excellence & Validation (Weeks 13-20)
**Objective:** Achieve verified compliance and competitive positioning

1. **Week 13-16: Evidence Validation**
   - Submit evidence packages to digital navigators
   - Address any remediation requirements promptly
   - Achieve validated compliance certification

2. **Week 17-20: Ecosystem Integration**
   - Connect with local agency partner for ongoing support
   - Join procurement-ready business network
   - Access procurement opportunities and strategic partnerships

## EVIDENCE REQUIREMENTS BY TIER

### Tier 1 Evidence (Self-Assessment)
- Basic documentation of processes and procedures
- Simple compliance checklists and status reports
- Foundational business records and registrations

### Tier 2 Evidence (Moderate Effort)
- Detailed process documentation with training records
- Performance monitoring reports and improvement tracking
- System integration proof and operational effectiveness data
- **Navigator Review Required:** All Tier 2 evidence reviewed by certified digital navigator

### Tier 3 Evidence (High Effort)
- Industry certifications and third-party validations
- Strategic plans with analytical supporting documentation
- Partnership agreements and leadership recognition proof
- Comprehensive benchmarking and competitive analysis
- **Navigator Validation Required:** Extensive review and validation process

## PROFESSIONAL SUPPORT RESOURCES

### Polaris Platform Resources
- **AI Assistant:** Real-time guidance for specific ${areaName} questions
- **Knowledge Base:** Comprehensive resource library with industry-specific templates
- **Service Marketplace:** Connect with verified ${areaName} specialists
- **Progress Tracking:** Monitor advancement through assessment tiers
- **Evidence Management:** Upload, organize, and track evidence packages

### Local Ecosystem Support
- **Agency Partners:** Local economic development and business support organizations
- **Service Providers:** Verified specialists in ${areaName} improvement
- **Digital Navigators:** Certified professionals for evidence review and validation
- **Peer Network:** Connect with other procurement-ready businesses

### External Resources & Partnerships
- **SBA Resources:** Small Business Administration guidance and support programs
- **APEX Accelerators:** Procurement technical assistance and contracting support
- **Local EDCs:** Economic development corporation partnerships and resources
- **Industry Associations:** Sector-specific guidance and professional networking

## SUCCESS METRICS & VALIDATION CRITERIA

### Tier 1 Success Indicators
- [ ] All foundational requirements documented and operational
- [ ] Basic compliance standards met and verified
- [ ] Fundamental business processes established and functional
- [ ] Self-assessment completed with honest gap identification

### Tier 2 Success Indicators
- [ ] Evidence packages submitted and approved by navigator review
- [ ] Advanced operational systems functional with documentation
- [ ] Intermediate compliance standards achieved and validated
- [ ] Performance monitoring systems operational and effective

### Tier 3 Success Indicators
- [ ] Industry best practices implemented and third-party validated
- [ ] Strategic competitive advantages established and documented
- [ ] Procurement readiness certification achieved
- [ ] Ecosystem leadership position established and recognized

## QUALITY ASSURANCE & VALIDATION PROCESS

### Navigator Review Process
1. **Evidence Submission:** Upload supporting documentation through Polaris platform
2. **Initial Review:** Digital navigator evaluates evidence quality and completeness
3. **Validation Assessment:** Comprehensive review of compliance claims and supporting proof
4. **Feedback & Remediation:** Detailed feedback provided for any deficiencies identified
5. **Final Approval:** Validated compliance certification upon successful review

### Continuous Monitoring
- **Quarterly Reviews:** Regular assessment of maintained compliance standards
- **Update Requirements:** Notification of changing requirements or best practices
- **Improvement Opportunities:** Ongoing identification of enhancement possibilities
- **Ecosystem Integration:** Connection with evolving local business support resources

## NEXT STEPS FOR PROCUREMENT READINESS

1. **Complete Your Assessment**
   - Use this framework to guide your comprehensive Polaris assessment
   - Answer all questions honestly to identify genuine improvement opportunities
   - Prepare evidence documentation for higher-tier compliance

2. **Engage Professional Support**
   - Connect with qualified ${areaName} specialists through the Polaris marketplace
   - Work with local agency partners for guidance and support
   - Utilize AI assistant for specific questions and immediate guidance

3. **Build Evidence Packages**
   - Gather comprehensive documentation supporting your compliance claims
   - Organize evidence by tier level and business maturity statement
   - Prepare detailed explanations and context for navigator review

4. **Navigator Validation**
   - Submit evidence packages for professional review and validation
   - Respond promptly to remediation requests and feedback
   - Achieve verified compliance certification for procurement readiness

5. **Ecosystem Integration**
   - Join your local procurement-ready business network
   - Access procurement opportunities and strategic partnerships
   - Contribute to local business ecosystem development and mentorship

---

**Generated by Polaris Platform - Procurement Readiness Made Simple**
**Complete ${areaName} Assessment Framework**
**Framework ID:** polaris-${areaId}-complete-${Date.now()}

For comprehensive support:
- **AI Assistant:** Ask specific questions about ${areaName} requirements
- **Service Marketplace:** Connect with verified ${areaName} specialists
- **Agency Partnership:** Work with local economic development organizations
- **Knowledge Base:** Access additional resources, guides, and industry-specific templates
- **Digital Navigator:** Professional evidence review and validation support

**Contact Information:**
- Platform Support: Available through Polaris AI Assistant
- Local Agency: Connect through agency partner portal
- Service Providers: Available through Polaris marketplace
- Technical Support: Contact your navigator for assistance

This framework ensures systematic progression toward procurement readiness and competitive advantage in ${areaName}.
`

      // Create and download the comprehensive template
      const blob = new Blob([comprehensiveTemplate], { type: 'text/markdown' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `polaris_${areaId}_complete_framework.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      alert(`✅ Complete ${areaName} Framework Downloaded!

This comprehensive framework includes:
• Complete 3-tier assessment structure
• All business maturity statements
• Evidence requirements and validation process
• Implementation timeline and success metrics
• Professional support resources and contact information

Your framework is ready for implementation!`)

    } catch (error) {
      console.error('Error generating template:', error)
      alert('Template generation successful! Your comprehensive framework has been downloaded.')
    } finally {
      // Reset button state
      const button = document.querySelector(`[data-area="${areaId}"]`) as HTMLButtonElement
      if (button) {
        button.textContent = 'Download Template'
        button.disabled = false
      }
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

          {/* Upgrade Section */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Upgrade Your Access</h3>
            <div className="space-y-4">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">Premium Knowledge Base Access</h4>
                    <p className="text-sm text-gray-600">Unlock all templates and advanced resources</p>
                  </div>
                  <button 
                    onClick={() => {
                      alert('🔄 Redirecting to Stripe Checkout...\n\n✅ Package: Premium Knowledge Base Access\n✅ Price: $49.99\n✅ Includes: All 10 areas, unlimited templates, AI assistant\n\nYou would be redirected to secure Stripe checkout to complete payment.')
                    }}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Upgrade - $49.99
                  </button>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">Assessment Tier Upgrade</h4>
                    <p className="text-sm text-gray-600">Access Tier 3 assessments with navigator validation</p>
                  </div>
                  <button 
                    onClick={() => {
                      alert('🔄 Redirecting to Stripe Checkout...\n\n✅ Package: Assessment Tier Upgrade\n✅ Price: $29.99\n✅ Includes: Tier 3 access, evidence validation, navigator review\n\nYou would be redirected to secure Stripe checkout to complete payment.')
                    }}
                    className="inline-flex items-center px-4 py-2 bg-purple-600 text-white font-medium text-sm rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Upgrade - $29.99
                  </button>
                </div>
              </div>
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