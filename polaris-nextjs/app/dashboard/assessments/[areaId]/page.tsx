'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle,
  ArrowRight,
  BookOpen,
  AlertCircle,
  Target,
  HelpCircle
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

interface AssessmentStatement {
  statement_id: string
  tier: number
  statement: string
  category: string
}

interface AssessmentArea {
  area_id: string
  area_name: string
  description: string
  statements: AssessmentStatement[]
}

interface AssessmentSession {
  session_id: string
  area_id: string
  tier: number
  progress: {
    current_statement: number
    total_statements: number
    completed: number
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