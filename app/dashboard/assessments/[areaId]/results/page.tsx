'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  Target,
  BookOpen,
  Briefcase,
  AlertTriangle,
  BarChart3,
  Download,
  Share2
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../../components/LoadingSpinner'

interface AssessmentResult {
  session_id: string
  area_id: string
  area_name: string
  tier: number
  score: number
  total_statements: number
  compliant_statements: number
  non_compliant_statements: number
  completion_date: string
  gap_analysis: {
    critical_gaps: string[]
    improvement_areas: string[]
    strengths: string[]
  }
  recommendations: Array<{
    type: 'service_request' | 'knowledge_base' | 'resource'
    title: string
    description: string
    priority: 'high' | 'medium' | 'low'
    action_url: string
  }>
  statements_breakdown: Array<{
    statement_id: string
    statement: string
    tier: number
    is_compliant: boolean
    category: string
  }>
}

const AssessmentResultsPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const params = useParams()
  const areaId = params?.areaId as string

  const [results, setResults] = useState<AssessmentResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!areaId) return

    const fetchResults = async () => {
      try {
        // Fetch latest assessment results for this area
        const response = await apiClient.request(`/assessment/client/results/${areaId}`)
        setResults(response.data)
      } catch (error) {
        console.error('Error fetching assessment results:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchResults()
  }, [areaId])

  const handleServiceRequest = async (recommendationType: string) => {
    try {
      // Create service request based on assessment gaps
      const response = await apiClient.request('/service-requests/professional-help', {
        method: 'POST',
        body: JSON.stringify({
          area_id: areaId,
          description: `Professional help needed for ${results?.area_name} based on assessment gaps`,
          budget_range: '1000-5000',
          timeline: '2-4 weeks',
          priority: 'high'
        })
      })

      if (response.success) {
        router.push('/dashboard/services')
      }
    } catch (error) {
      console.error('Error creating service request:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!results) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-2">No Results Found</h1>
        <p className="text-gray-600 mb-6">Complete an assessment to see your results here.</p>
        <Link href={`/dashboard/assessments/${areaId}`} className="polaris-button-primary">
          Start Assessment
        </Link>
      </div>
    )
  }

  const scorePercentage = Math.round(results.score)
  const scoreColor = scorePercentage >= 80 ? 'text-green-600' : scorePercentage >= 60 ? 'text-yellow-600' : 'text-red-600'
  const scoreBgColor = scorePercentage >= 80 ? 'bg-green-100' : scorePercentage >= 60 ? 'bg-yellow-100' : 'bg-red-100'

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            <h1 className="text-3xl font-bold text-gray-900">{results.area_name} Results</h1>
            <p className="text-gray-600 mt-1">
              Assessment completed on {new Date(results.completion_date).toLocaleDateString()}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button className="polaris-button-secondary inline-flex items-center">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </button>
            <button className="polaris-button-secondary inline-flex items-center">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Score Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-1">
          <div className="polaris-card text-center">
            <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center ${scoreBgColor} mb-4`}>
              <div className="text-center">
                <div className={`text-3xl font-bold ${scoreColor}`}>{scorePercentage}%</div>
                <div className="text-sm text-gray-600">Overall Score</div>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {scorePercentage >= 80 ? 'Excellent' : 
               scorePercentage >= 60 ? 'Good Progress' : 
               'Needs Improvement'}
            </h3>
            <p className="text-gray-600 text-sm">
              Tier {results.tier} Assessment Complete
            </p>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
            <div className="polaris-card">
              <div className="flex items-center">
                <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{results.compliant_statements}</div>
                  <div className="text-sm text-gray-600">Compliant Areas</div>
                </div>
              </div>
            </div>

            <div className="polaris-card">
              <div className="flex items-center">
                <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
                  <XCircle className="h-5 w-5 text-red-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{results.non_compliant_statements}</div>
                  <div className="text-sm text-gray-600">Gaps Identified</div>
                </div>
              </div>
            </div>

            <div className="polaris-card">
              <div className="flex items-center">
                <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{results.total_statements}</div>
                  <div className="text-sm text-gray-600">Total Evaluated</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gap Analysis & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Gap Analysis */}
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Gap Analysis</h2>
          
          {/* Critical Gaps */}
          {results.gap_analysis.critical_gaps.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-red-700 mb-3 flex items-center">
                <XCircle className="h-5 w-5 mr-2" />
                Critical Gaps ({results.gap_analysis.critical_gaps.length})
              </h3>
              <div className="space-y-2">
                {results.gap_analysis.critical_gaps.map((gap, index) => (
                  <div key={index} className="bg-red-50 border border-red-200 p-3 rounded-lg">
                    <p className="text-sm text-red-800">{gap}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Improvement Areas */}
          {results.gap_analysis.improvement_areas.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-yellow-700 mb-3 flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Improvement Areas ({results.gap_analysis.improvement_areas.length})
              </h3>
              <div className="space-y-2">
                {results.gap_analysis.improvement_areas.map((area, index) => (
                  <div key={index} className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
                    <p className="text-sm text-yellow-800">{area}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strengths */}
          {results.gap_analysis.strengths.length > 0 && (
            <div>
              <h3 className="font-semibold text-green-700 mb-3 flex items-center">
                <CheckCircle className="h-5 w-5 mr-2" />
                Strengths ({results.gap_analysis.strengths.length})
              </h3>
              <div className="space-y-2">
                {results.gap_analysis.strengths.map((strength, index) => (
                  <div key={index} className="bg-green-50 border border-green-200 p-3 rounded-lg">
                    <p className="text-sm text-green-800">{strength}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Recommendations */}
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Recommended Actions</h2>
          
          <div className="space-y-4">
            {results.recommendations.map((rec, index) => (
              <div key={index} className={`border-l-4 pl-4 py-3 ${
                rec.priority === 'high' ? 'border-red-400 bg-red-50' :
                rec.priority === 'medium' ? 'border-yellow-400 bg-yellow-50' :
                'border-blue-400 bg-blue-50'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                  <span className={`polaris-badge text-xs ${
                    rec.priority === 'high' ? 'polaris-badge-danger' :
                    rec.priority === 'medium' ? 'polaris-badge-warning' :
                    'polaris-badge-info'
                  }`}>
                    {rec.priority} priority
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                
                {rec.type === 'service_request' && (
                  <button
                    onClick={() => handleServiceRequest(rec.type)}
                    className="polaris-button-primary text-sm inline-flex items-center"
                  >
                    <Briefcase className="mr-1 h-4 w-4" />
                    Request Professional Help
                  </button>
                )}
                
                {rec.type === 'knowledge_base' && (
                  <Link
                    href={rec.action_url}
                    className="polaris-button-secondary text-sm inline-flex items-center"
                  >
                    <BookOpen className="mr-1 h-4 w-4" />
                    Access Resources
                  </Link>
                )}

                {rec.type === 'resource' && (
                  <Link
                    href={rec.action_url}
                    className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
                  >
                    Learn More →
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Detailed Assessment Breakdown</h2>
        
        <div className="space-y-4">
          {results.statements_breakdown.map((statement, index) => (
            <div key={statement.statement_id} className={`border rounded-lg p-4 ${
              statement.is_compliant ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
            }`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center mr-3 text-sm font-medium border">
                    {index + 1}
                  </div>
                  <div>
                    <span className="polaris-badge polaris-badge-info text-xs mr-2">
                      Tier {statement.tier}
                    </span>
                    <span className="text-sm text-gray-600">{statement.category}</span>
                  </div>
                </div>
                <div className="flex items-center">
                  {statement.is_compliant ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
              </div>
              <p className="text-gray-800 mb-2">{statement.statement}</p>
              <div className={`text-sm font-medium ${
                statement.is_compliant ? 'text-green-700' : 'text-red-700'
              }`}>
                Status: {statement.is_compliant ? 'Compliant ✅' : 'Gap Identified ❌'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-8 border-t border-gray-200">
        <Link
          href="/dashboard/assessments"
          className="polaris-button-secondary"
        >
          Back to Assessments
        </Link>
        
        <div className="flex items-center space-x-4">
          <Link
            href={`/dashboard/assessments/${areaId}`}
            className="polaris-button-secondary"
          >
            Retake Assessment
          </Link>
          
          {results.non_compliant_statements > 0 && (
            <button
              onClick={() => handleServiceRequest('professional_help')}
              className="polaris-button-primary inline-flex items-center"
            >
              <Briefcase className="mr-2 h-4 w-4" />
              Get Professional Help
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default AssessmentResultsPage