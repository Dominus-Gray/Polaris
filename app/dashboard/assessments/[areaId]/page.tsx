'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle,
  ArrowRight,
  Upload,
  FileText,
  AlertCircle,
  Target,
  HelpCircle,
  Camera,
  Paperclip,
  Award
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

// Complete business maturity statements for all 10 areas across 3 tiers
const BUSINESS_MATURITY_STATEMENTS = {
  area1: {
    area_name: 'Business Formation & Registration',
    tier1: [
      { id: 'area1_t1_1', statement: 'Your business has a legally recognized business structure (LLC, Corporation, Partnership, etc.)', category: 'Legal Structure' },
      { id: 'area1_t1_2', statement: 'Your business is properly registered with state and local authorities', category: 'Registration' },
      { id: 'area1_t1_3', statement: 'Your business has obtained all required basic licenses and permits for operations', category: 'Licensing' }
    ],
    tier2: [
      { id: 'area1_t2_1', statement: 'Your business maintains up-to-date registered agent and business address information', category: 'Compliance Management' },
      { id: 'area1_t2_2', statement: 'Your business has established proper corporate governance structures (bylaws, operating agreements)', category: 'Governance' },
      { id: 'area1_t2_3', statement: 'Your business regularly reviews and renews all licenses and permits before expiration', category: 'License Management' }
    ],
    tier3: [
      { id: 'area1_t3_1', statement: 'Your business has documented succession planning and ownership transfer procedures', category: 'Strategic Planning' },
      { id: 'area1_t3_2', statement: 'Your business maintains comprehensive compliance tracking systems for all regulatory requirements', category: 'Compliance Systems' },
      { id: 'area1_t3_3', statement: 'Your business has established relationships with legal counsel for ongoing compliance support', category: 'Professional Support' }
    ]
  },
  area2: {
    area_name: 'Financial Operations & Management',
    tier1: [
      { id: 'area2_t1_1', statement: 'Your business maintains separate business banking accounts', category: 'Banking' },
      { id: 'area2_t1_2', statement: 'Your business tracks income and expenses regularly', category: 'Record Keeping' },
      { id: 'area2_t1_3', statement: 'Your business files required tax returns on time', category: 'Tax Compliance' }
    ],
    tier2: [
      { id: 'area2_t2_1', statement: 'Your business uses professional accounting software for financial management', category: 'Financial Systems' },
      { id: 'area2_t2_2', statement: 'Your business maintains detailed cash flow projections and budgets', category: 'Financial Planning' },
      { id: 'area2_t2_3', statement: 'Your business has established credit relationships with banks or financial institutions', category: 'Financial Relationships' }
    ],
    tier3: [
      { id: 'area2_t3_1', statement: 'Your business undergoes regular financial audits by certified public accountants', category: 'Financial Oversight' },
      { id: 'area2_t3_2', statement: 'Your business has implemented comprehensive financial controls and approval processes', category: 'Financial Controls' },
      { id: 'area2_t3_3', statement: 'Your business maintains detailed financial forecasting and scenario planning capabilities', category: 'Strategic Finance' }
    ]
  },
  area3: {
    area_name: 'Legal & Contracting Compliance',
    tier1: [
      { id: 'area3_t1_1', statement: 'Your business has basic contract templates for standard transactions', category: 'Contract Management' },
      { id: 'area3_t1_2', statement: 'Your business maintains general liability insurance coverage', category: 'Insurance' },
      { id: 'area3_t1_3', statement: 'Your business complies with basic employment law requirements', category: 'Employment Compliance' }
    ],
    tier2: [
      { id: 'area3_t2_1', statement: 'Your business has documented contract review and approval processes', category: 'Contract Processes' },
      { id: 'area3_t2_2', statement: 'Your business maintains comprehensive insurance coverage including professional liability', category: 'Risk Management' },
      { id: 'area3_t2_3', statement: 'Your business has established intellectual property protection strategies', category: 'IP Protection' }
    ],
    tier3: [
      { id: 'area3_t3_1', statement: 'Your business has legal counsel on retainer for complex contracting matters', category: 'Legal Support' },
      { id: 'area3_t3_2', statement: 'Your business maintains comprehensive compliance monitoring for industry-specific regulations', category: 'Regulatory Compliance' },
      { id: 'area3_t3_3', statement: 'Your business has implemented advanced contract management systems with automated tracking', category: 'Advanced Systems' }
    ]
  },
  area4: {
    area_name: 'Quality Management & Standards',
    tier1: [
      { id: 'area4_t1_1', statement: 'Your business has basic quality control procedures for products or services', category: 'Quality Control' },
      { id: 'area4_t1_2', statement: 'Your business documents standard operating procedures for key processes', category: 'Process Documentation' },
      { id: 'area4_t1_3', statement: 'Your business addresses customer complaints and feedback systematically', category: 'Customer Feedback' }
    ],
    tier2: [
      { id: 'area4_t2_1', statement: 'Your business has implemented formal quality management systems (ISO 9001 or similar)', category: 'QMS Implementation' },
      { id: 'area4_t2_2', statement: 'Your business conducts regular internal audits and quality reviews', category: 'Quality Auditing' },
      { id: 'area4_t2_3', statement: 'Your business maintains detailed quality metrics and improvement tracking', category: 'Quality Metrics' }
    ],
    tier3: [
      { id: 'area4_t3_1', statement: 'Your business has achieved third-party quality certifications relevant to your industry', category: 'Certifications' },
      { id: 'area4_t3_2', statement: 'Your business has established continuous improvement programs with employee involvement', category: 'Continuous Improvement' },
      { id: 'area4_t3_3', statement: 'Your business maintains advanced quality management software with real-time monitoring', category: 'Advanced QM Systems' }
    ]
  },
  area5: {
    area_name: 'Technology & Security Infrastructure',
    tier1: [
      { id: 'area5_t1_1', statement: 'Your business has basic cybersecurity measures (antivirus, firewalls, secure passwords)', category: 'Basic Security' },
      { id: 'area5_t1_2', statement: 'Your business regularly backs up critical data and systems', category: 'Data Backup' },
      { id: 'area5_t1_3', statement: 'Your business has updated hardware and software systems', category: 'Technology Infrastructure' }
    ],
    tier2: [
      { id: 'area5_t2_1', statement: 'Your business has implemented comprehensive cybersecurity policies and training', category: 'Security Policies' },
      { id: 'area5_t2_2', statement: 'Your business maintains secure data management and access control systems', category: 'Data Security' },
      { id: 'area5_t2_3', statement: 'Your business has established IT disaster recovery and business continuity plans', category: 'Disaster Recovery' }
    ],
    tier3: [
      { id: 'area5_t3_1', statement: 'Your business has achieved cybersecurity certifications (SOC 2, ISO 27001, or similar)', category: 'Security Certifications' },
      { id: 'area5_t3_2', statement: 'Your business conducts regular penetration testing and security assessments', category: 'Security Testing' },
      { id: 'area5_t3_3', statement: 'Your business has implemented advanced threat monitoring and incident response capabilities', category: 'Advanced Security' }
    ]
  },
  area6: {
    area_name: 'Human Resources & Capacity',
    tier1: [
      { id: 'area6_t1_1', statement: 'Your business has basic employee handbook and policies', category: 'HR Policies' },
      { id: 'area6_t1_2', statement: 'Your business maintains required employment records and documentation', category: 'Documentation' },
      { id: 'area6_t1_3', statement: 'Your business provides basic safety training and workplace safety measures', category: 'Workplace Safety' }
    ],
    tier2: [
      { id: 'area6_t2_1', statement: 'Your business has implemented formal performance management and review processes', category: 'Performance Management' },
      { id: 'area6_t2_2', statement: 'Your business provides comprehensive employee training and development programs', category: 'Training Programs' },
      { id: 'area6_t2_3', statement: 'Your business has established workforce planning and capacity management systems', category: 'Capacity Planning' }
    ],
    tier3: [
      { id: 'area6_t3_1', statement: 'Your business has implemented advanced HR management systems with automated workflows', category: 'HR Technology' },
      { id: 'area6_t3_2', statement: 'Your business maintains comprehensive succession planning and knowledge transfer programs', category: 'Succession Planning' },
      { id: 'area6_t3_3', statement: 'Your business has established strategic workforce development partnerships and apprenticeship programs', category: 'Strategic Development' }
    ]
  },
  area7: {
    area_name: 'Performance Tracking & Reporting',
    tier1: [
      { id: 'area7_t1_1', statement: 'Your business tracks basic performance metrics (revenue, expenses, customer satisfaction)', category: 'Basic Metrics' },
      { id: 'area7_t1_2', statement: 'Your business generates regular financial and operational reports', category: 'Reporting' },
      { id: 'area7_t1_3', statement: 'Your business reviews performance data to make business decisions', category: 'Data-Driven Decisions' }
    ],
    tier2: [
      { id: 'area7_t2_1', statement: 'Your business has implemented comprehensive key performance indicator (KPI) systems', category: 'KPI Systems' },
      { id: 'area7_t2_2', statement: 'Your business uses business intelligence tools for advanced reporting and analytics', category: 'Business Intelligence' },
      { id: 'area7_t2_3', statement: 'Your business conducts regular performance benchmarking against industry standards', category: 'Benchmarking' }
    ],
    tier3: [
      { id: 'area7_t3_1', statement: 'Your business has implemented real-time performance monitoring and dashboard systems', category: 'Real-time Monitoring' },
      { id: 'area7_t3_2', statement: 'Your business maintains predictive analytics and forecasting capabilities', category: 'Predictive Analytics' },
      { id: 'area7_t3_3', statement: 'Your business has established automated performance reporting and alert systems', category: 'Automated Systems' }
    ]
  },
  area8: {
    area_name: 'Risk Management & Business Continuity',
    tier1: [
      { id: 'area8_t1_1', statement: 'Your business has identified major business risks and potential disruptions', category: 'Risk Identification' },
      { id: 'area8_t1_2', statement: 'Your business maintains basic emergency procedures and contacts', category: 'Emergency Procedures' },
      { id: 'area8_t1_3', statement: 'Your business has adequate insurance coverage for identified risks', category: 'Risk Insurance' }
    ],
    tier2: [
      { id: 'area8_t2_1', statement: 'Your business has documented comprehensive risk assessment and mitigation strategies', category: 'Risk Assessment' },
      { id: 'area8_t2_2', statement: 'Your business maintains detailed business continuity and disaster recovery plans', category: 'Continuity Planning' },
      { id: 'area8_t2_3', statement: 'Your business conducts regular risk management reviews and plan updates', category: 'Risk Reviews' }
    ],
    tier3: [
      { id: 'area8_t3_1', statement: 'Your business has implemented enterprise risk management frameworks and systems', category: 'Enterprise Risk Management' },
      { id: 'area8_t3_2', statement: 'Your business conducts regular business continuity testing and scenario planning', category: 'Continuity Testing' },
      { id: 'area8_t3_3', statement: 'Your business maintains advanced crisis management and communication systems', category: 'Crisis Management' }
    ]
  },
  area9: {
    area_name: 'Supply Chain Management & Vendor Relations',
    tier1: [
      { id: 'area9_t1_1', statement: 'Your business has established relationships with reliable suppliers and vendors', category: 'Vendor Relations' },
      { id: 'area9_t1_2', statement: 'Your business maintains basic procurement procedures and purchase controls', category: 'Procurement' },
      { id: 'area9_t1_3', statement: 'Your business tracks supplier performance and delivery metrics', category: 'Supplier Performance' }
    ],
    tier2: [
      { id: 'area9_t2_1', statement: 'Your business has implemented formal vendor qualification and evaluation processes', category: 'Vendor Qualification' },
      { id: 'area9_t2_2', statement: 'Your business maintains comprehensive supply chain mapping and risk assessment', category: 'Supply Chain Management' },
      { id: 'area9_t2_3', statement: 'Your business has established strategic partnerships and long-term supplier agreements', category: 'Strategic Partnerships' }
    ],
    tier3: [
      { id: 'area9_t3_1', statement: 'Your business has implemented advanced supply chain management systems with real-time tracking', category: 'Advanced SCM' },
      { id: 'area9_t3_2', statement: 'Your business maintains comprehensive supplier diversity and sustainability programs', category: 'Supplier Diversity' },
      { id: 'area9_t3_3', statement: 'Your business has established supply chain innovation and continuous improvement initiatives', category: 'Supply Chain Innovation' }
    ]
  },
  area10: {
    area_name: 'Competitive Advantage & Market Position',
    tier1: [
      { id: 'area10_t1_1', statement: 'Your business has identified its primary competitive advantages', category: 'Market Analysis' },
      { id: 'area10_t1_2', statement: 'Your business has basic marketing materials and online presence', category: 'Marketing' },
      { id: 'area10_t1_3', statement: 'Your business tracks basic market trends and competitor activities', category: 'Market Intelligence' }
    ],
    tier2: [
      { id: 'area10_t2_1', statement: 'Your business has documented strategic partnerships and alliance agreements', category: 'Strategic Partnerships' },
      { id: 'area10_t2_2', statement: 'Your business maintains detailed competitive analysis and positioning strategies', category: 'Competitive Analysis' },
      { id: 'area10_t2_3', statement: 'Your business has developed proprietary processes or intellectual property', category: 'Innovation' }
    ],
    tier3: [
      { id: 'area10_t3_1', statement: 'Your business has implemented advanced market intelligence and competitive monitoring systems', category: 'Intelligence Systems' },
      { id: 'area10_t3_2', statement: 'Your business has established thought leadership and industry recognition', category: 'Market Leadership' },
      { id: 'area10_t3_3', statement: 'Your business has developed and executed comprehensive market capture and expansion strategies', category: 'Market Expansion' }
    ]
  }
}

const AssessmentAreaPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const params = useParams()
  const areaId = params?.areaId as string

  const [assessmentArea, setAssessmentArea] = useState<AssessmentArea | null>(null)
  const [currentSession, setCurrentSession] = useState<AssessmentSession | null>(null)
  const [currentStatementIndex, setCurrentStatementIndex] = useState(0)
  const [responses, setResponses] = useState<Record<string, boolean>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!areaId) return

    const initializeAssessment = async () => {
      try {
        // Create or resume assessment session
        const sessionResponse = await apiClient.request('/assessment/tier-session', {
          method: 'POST',
          body: JSON.stringify({
            area_id: areaId,
            tier: 1 // Start with tier 1, can be upgraded based on client access
          })
        })

        const session = sessionResponse.data
        setCurrentSession(session)

        // Fetch assessment area details  
        const areaResponse = await apiClient.request(`/assessment/schema/area/${areaId}`)
        setAssessmentArea(areaResponse.data)

        // If session has existing progress, load it
        if (session.progress && session.progress.completed > 0) {
          const progressResponse = await apiClient.request(`/assessment/tier-session/${session.session_id}/progress`)
          if (progressResponse.data.responses) {
            setResponses(progressResponse.data.responses)
            setCurrentStatementIndex(session.progress.current_statement || 0)
          }
        }
      } catch (error) {
        console.error('Error initializing assessment:', error)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAssessment()
  }, [areaId])

  const handleResponse = (statementId: string, isCompliant: boolean) => {
    setResponses(prev => ({
      ...prev,
      [statementId]: isCompliant
    }))
  }

  const handleNext = async () => {
    if (!currentSession || !assessmentArea) return

    const currentStatement = assessmentArea.statements[currentStatementIndex]
    const response = responses[currentStatement.statement_id]
    
    if (response === undefined) {
      alert('Please select a response before continuing.')
      return
    }

    setIsSubmitting(true)

    try {
      // Submit current response
      await apiClient.request(`/assessment/tier-session/${currentSession.session_id}/response`, {
        method: 'POST',
        body: JSON.stringify({
          statement_id: currentStatement.statement_id,
          is_compliant: response,
          notes: ''
        })
      })

      // Move to next statement or complete
      if (currentStatementIndex < assessmentArea.statements.length - 1) {
        setCurrentStatementIndex(prev => prev + 1)
      } else {
        // Assessment completed
        router.push(`/dashboard/assessments/${areaId}/results`)
      }
    } catch (error) {
      console.error('Error submitting response:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePrevious = () => {
    if (currentStatementIndex > 0) {
      setCurrentStatementIndex(prev => prev - 1)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!assessmentArea || !currentSession) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Assessment Not Found</h1>
        <p className="text-gray-600 mb-6">The requested assessment area could not be loaded.</p>
        <Link href="/dashboard/assessments" className="polaris-button-primary">
          Back to Assessments
        </Link>
      </div>
    )
  }

  const currentStatement = assessmentArea.statements[currentStatementIndex]
  const totalStatements = assessmentArea.statements.length
  const progressPercentage = Math.round(((currentStatementIndex + 1) / totalStatements) * 100)
  const currentResponse = responses[currentStatement?.statement_id]

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <button
            onClick={() => router.back()}
            className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{assessmentArea.area_name}</h1>
            <p className="text-gray-600 mt-1">{assessmentArea.description}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">
              Question {currentStatementIndex + 1} of {totalStatements}
            </span>
            <span className="text-polaris-blue font-medium">
              {progressPercentage}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-polaris-blue h-2 rounded-full transition-all duration-300" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Assessment Statement */}
      <div className="polaris-card mb-8">
        <div className="mb-6">
          <div className="flex items-start mb-4">
            <div className="h-12 w-12 bg-polaris-blue text-white rounded-lg flex items-center justify-center mr-4 text-lg font-bold">
              {currentStatementIndex + 1}
            </div>
            <div className="flex-1">
              <div className="flex items-center mb-2">
                <h2 className="text-lg font-semibold text-gray-900">Business Maturity Statement</h2>
                <span className="ml-2 polaris-badge polaris-badge-info text-xs">
                  Tier {currentStatement?.tier || 1}
                </span>
              </div>
              <p className="text-gray-600 text-sm">
                Category: {currentStatement?.category}
              </p>
            </div>
          </div>

          <div className="bg-gray-50 p-6 rounded-lg">
            <p className="text-lg text-gray-900 leading-relaxed">
              {currentStatement?.statement}
            </p>
          </div>
        </div>

        {/* Response Options */}
        <div className="space-y-4 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            How well does this statement describe your business?
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => handleResponse(currentStatement.statement_id, true)}
              className={`p-6 text-left border-2 rounded-lg transition-all ${
                currentResponse === true
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-green-300 hover:bg-green-25'
              }`}
            >
              <div className="flex items-center mb-3">
                <CheckCircle className={`h-6 w-6 mr-3 ${
                  currentResponse === true ? 'text-green-600' : 'text-gray-400'
                }`} />
                <span className={`font-semibold ${
                  currentResponse === true ? 'text-green-900' : 'text-gray-700'
                }`}>
                  ✅ Compliant
                </span>
              </div>
              <p className={`text-sm ${
                currentResponse === true ? 'text-green-800' : 'text-gray-600'
              }`}>
                This statement accurately describes our business. We have the processes, 
                documentation, or systems in place to meet this requirement.
              </p>
            </button>

            <button
              onClick={() => handleResponse(currentStatement.statement_id, false)}
              className={`p-6 text-left border-2 rounded-lg transition-all ${
                currentResponse === false
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-red-300 hover:bg-red-25'
              }`}
            >
              <div className="flex items-center mb-3">
                <XCircle className={`h-6 w-6 mr-3 ${
                  currentResponse === false ? 'text-red-600' : 'text-gray-400'
                }`} />
                <span className={`font-semibold ${
                  currentResponse === false ? 'text-red-900' : 'text-gray-700'
                }`}>
                  ❌ Not Compliant
                </span>
              </div>
              <p className={`text-sm ${
                currentResponse === false ? 'text-red-800' : 'text-gray-600'
              }`}>
                We need help with this area. We don't currently have the processes, 
                documentation, or systems to fully meet this requirement.
              </p>
            </button>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-200">
          <button
            onClick={handlePrevious}
            disabled={currentStatementIndex === 0}
            className="polaris-button-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Previous
          </button>

          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard/knowledge-base"
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
            >
              <HelpCircle className="h-4 w-4 mr-1" />
              Get Help
            </Link>

            <button
              onClick={handleNext}
              disabled={currentResponse === undefined || isSubmitting}
              className="polaris-button-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
            >
              {isSubmitting ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  {currentStatementIndex === totalStatements - 1 ? 'Complete Assessment' : 'Next'}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Help Section */}
      {currentResponse === false && (
        <div className="polaris-card bg-yellow-50 border-yellow-200">
          <div className="flex items-start">
            <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
              <Target className="h-5 w-5 text-yellow-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Need Help with This Area?</h3>
              <p className="text-gray-600 mb-4">
                Don't worry! Identifying gaps is the first step toward improvement. We can help you address this area.
              </p>
              <div className="flex items-center space-x-4">
                <Link 
                  href="/dashboard/services" 
                  className="polaris-button-primary inline-flex items-center"
                >
                  <BookOpen className="mr-2 h-4 w-4" />
                  Request Professional Help
                </Link>
                <Link 
                  href={`/dashboard/knowledge-base?area=${areaId}`}
                  className="text-polaris-blue hover:text-polaris-navy font-medium"
                >
                  Access Resources →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AssessmentAreaPage