'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  ClipboardList, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Clock,
  Target,
  TrendingUp,
  BookOpen
} from 'lucide-react'
import { useAuth } from '../../providers'
import { apiClient } from '../../providers'
import LoadingSpinner from '../components/LoadingSpinner'

interface BusinessArea {
  area_id: string
  area_name: string
  description: string
  tier_available: number
  sessions_completed: number
  latest_score: number
  status: 'not_started' | 'active' | 'completed'
  last_assessment: string | null
}

interface AssessmentSchema {
  areas: BusinessArea[]
  client_tier_access: number
}

const AssessmentsPage = () => {
  const { state } = useAuth()
  const [assessmentData, setAssessmentData] = useState<AssessmentSchema | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAssessmentData = async () => {
      try {
        // Fetch tier-based assessment schema
        const response = await apiClient.request('/assessment/schema/tier-based')
        setAssessmentData(response.data)
      } catch (error) {
        console.error('Error fetching assessment data:', error)
        // Fallback data for development/demo
        setAssessmentData({
          client_tier_access: 1,
          areas: [
            {
              area_id: 'area1',
              area_name: 'Business Formation & Registration',
              description: 'Legal structure, registration, licenses, and permits',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area2', 
              area_name: 'Financial Operations & Management',
              description: 'Financial planning, accounting, and cash flow management',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area3',
              area_name: 'Legal & Contracting Compliance', 
              description: 'Legal requirements, contracts, and compliance standards',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area4',
              area_name: 'Quality Management & Standards',
              description: 'Quality systems, certifications, and process standards',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started', 
              last_assessment: null
            },
            {
              area_id: 'area5',
              area_name: 'Technology & Security Infrastructure',
              description: 'IT systems, cybersecurity, and data management',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area6',
              area_name: 'Human Resources & Capacity',
              description: 'Staffing, training, and organizational capacity',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area7',
              area_name: 'Performance Tracking & Reporting',
              description: 'Metrics, reporting systems, and performance management',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area8',
              area_name: 'Risk Management & Business Continuity',
              description: 'Risk assessment, mitigation, and business continuity planning',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area9',
              area_name: 'Supply Chain Management & Vendor Relations',
              description: 'Supplier relationships, procurement, and supply chain optimization',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area10',
              area_name: 'Competitive Advantage & Market Position',
              description: 'Competitive advantages, market capture processes, strategic partnerships',
              tier_available: 1,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            }
          ]
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchAssessmentData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const areas = assessmentData?.areas || []
  const completedAreas = areas.filter(area => area.status === 'completed').length
  const activeAreas = areas.filter(area => area.status === 'active').length
  const overallProgress = areas.length > 0 ? Math.round((completedAreas / areas.length) * 100) : 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Business Maturity Assessment</h1>
            <p className="text-lg text-gray-600">
              Evaluate your business readiness across 10 key areas to identify improvement opportunities.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-polaris-blue">{overallProgress}%</div>
              <div className="text-sm text-gray-600">Complete</div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="polaris-card">
          <div className="flex items-center">
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{completedAreas}</div>
              <div className="text-sm text-gray-600">Completed Areas</div>
            </div>
          </div>
        </div>

        <div className="polaris-card">
          <div className="flex items-center">
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{activeAreas}</div>
              <div className="text-sm text-gray-600">In Progress</div>
            </div>
          </div>
        </div>

        <div className="polaris-card">
          <div className="flex items-center">
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{areas.length - completedAreas - activeAreas}</div>
              <div className="text-sm text-gray-600">Not Started</div>
            </div>
          </div>
        </div>
      </div>

      {/* Assessment Areas Grid */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Assessment Areas</h2>
          <div className="text-sm text-gray-600">
            Tier Access Level: <span className="font-medium text-polaris-blue">Tier {assessmentData?.client_tier_access || 1}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {areas.map((area, index) => (
            <div key={area.area_id} className="polaris-card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <div className="h-8 w-8 bg-polaris-blue text-white rounded-full flex items-center justify-center mr-3 text-sm font-medium">
                      {index + 1}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900">{area.area_name}</h3>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{area.description}</p>
                  
                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-500">Progress</span>
                      <span className="text-gray-700 font-medium">{area.latest_score}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-polaris-blue h-2 rounded-full transition-all" 
                        style={{ width: `${area.latest_score}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Status & Tier Info */}
                  <div className="flex items-center justify-between">
                    <span className={`polaris-badge ${
                      area.status === 'completed' ? 'polaris-badge-success' :
                      area.status === 'active' ? 'polaris-badge-info' :
                      'polaris-badge-warning'
                    }`}>
                      {area.status === 'completed' ? 'Complete' :
                       area.status === 'active' ? 'In Progress' :
                       'Not Started'}
                    </span>
                    
                    <div className="text-xs text-gray-500">
                      {area.sessions_completed > 0 && (
                        <span>{area.sessions_completed} sessions completed</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  Available: Tier {area.tier_available}
                  {area.last_assessment && (
                    <span className="ml-2">Last: {new Date(area.last_assessment).toLocaleDateString()}</span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  {area.status === 'completed' && (
                    <Link
                      href={`/dashboard/assessments/${area.area_id}/results`}
                      className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
                    >
                      <TrendingUp className="h-4 w-4 mr-1" />
                      View Results
                    </Link>
                  )}
                  
                  <Link
                    href={`/dashboard/assessments/${area.area_id}`}
                    className="polaris-button-primary text-sm inline-flex items-center"
                  >
                    {area.status === 'not_started' ? 'Start Assessment' :
                     area.status === 'active' ? 'Continue' :
                     'Retake'}
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Help Section */}
      <div className="polaris-card bg-blue-50 border-blue-200">
        <div className="flex items-start">
          <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <BookOpen className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Need Help Getting Started?</h3>
            <p className="text-gray-600 mb-4">
              Our assessment system is designed to help you identify gaps and opportunities in your business. 
              Each area contains tailored questions based on your tier access level.
            </p>
            <div className="flex items-center space-x-4">
              <Link 
                href="/dashboard/knowledge-base" 
                className="polaris-button-secondary inline-flex items-center"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Access Knowledge Base
              </Link>
              <Link 
                href="/dashboard/services" 
                className="text-polaris-blue hover:text-polaris-navy font-medium"
              >
                Get Professional Help →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AssessmentsPage