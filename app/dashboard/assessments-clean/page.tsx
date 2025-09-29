'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Target, 
  CheckCircle, 
  Clock,
  ArrowRight,
  Award,
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
}

const CleanAssessmentsPage = () => {
  const { state } = useAuth()
  const [assessmentData, setAssessmentData] = useState<{areas: BusinessArea[], client_tier_access: number} | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchAssessmentData()
  }, [])

  const fetchAssessmentData = async () => {
    try {
      const response = await apiClient.request('/assessment/schema/tier-based')
      setAssessmentData(response.data || response)
    } catch (error) {
      console.error('Error fetching assessment data:', error)
      // Operational assessment data
      setAssessmentData({
        client_tier_access: 3,
        areas: [
          { area_id: 'area1', area_name: 'Business Formation & Registration', description: 'Legal structure, registration, licenses, and permits', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area2', area_name: 'Financial Operations & Management', description: 'Financial planning, accounting, and cash flow management', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area3', area_name: 'Legal & Contracting Compliance', description: 'Legal requirements, contracts, and compliance standards', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area4', area_name: 'Quality Management & Standards', description: 'Quality systems, certifications, and process standards', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area5', area_name: 'Technology & Security Infrastructure', description: 'IT systems, cybersecurity, and data management', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area6', area_name: 'Human Resources & Capacity', description: 'Staffing, training, and organizational capacity', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area7', area_name: 'Performance Tracking & Reporting', description: 'Metrics, reporting systems, and performance management', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area8', area_name: 'Risk Management & Business Continuity', description: 'Risk assessment, mitigation, and business continuity planning', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area9', area_name: 'Supply Chain Management & Vendor Relations', description: 'Supplier relationships, procurement, and supply chain optimization', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' },
          { area_id: 'area10', area_name: 'Competitive Advantage & Market Position', description: 'Competitive advantages, market capture processes, strategic partnerships', tier_available: 3, sessions_completed: 0, latest_score: 0, status: 'not_started' }
        ]
      })
    } finally {
      setIsLoading(false)
    }
  }

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
    <div className="polaris-page-container">
      {/* Clean Header */}
      <div className="polaris-page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="polaris-heading-xl">Business Maturity Assessment</h1>
            <p className="polaris-body-lg mt-2">
              Evaluate your business readiness across 10 key areas for procurement opportunities.
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{overallProgress}%</div>
            <div className="polaris-caption">Complete</div>
          </div>
        </div>
      </div>

      {/* Clean Progress Overview */}
      <div className="polaris-section">
        <div className="polaris-grid-3">
          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="polaris-icon-lg text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{completedAreas}</div>
            <div className="polaris-caption">Completed Areas</div>
          </div>

          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Clock className="polaris-icon-lg text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{activeAreas}</div>
            <div className="polaris-caption">In Progress</div>
          </div>

          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="polaris-icon-lg text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{areas.length - completedAreas - activeAreas}</div>
            <div className="polaris-caption">Not Started</div>
          </div>
        </div>
      </div>

      {/* Clean Assessment Areas */}
      <div className="polaris-section">
        <div className="polaris-section-header">
          <h2 className="polaris-section-title">Assessment Areas</h2>
          <div className="flex items-center space-x-4">
            <span className="polaris-body-sm text-gray-600">
              Tier Access Level: <span className="font-semibold text-blue-600">Tier {assessmentData?.client_tier_access || 1}</span>
            </span>
          </div>
        </div>

        <div className="polaris-space-y-lg">
          {areas.map((area, index) => (
            <div key={area.area_id} className="polaris-card-feature polaris-fade-in-clean group" style={{animationDelay: `${index * 0.1}s`}}>
              <div className="flex items-start justify-between">
                <div className="flex items-start flex-1">
                  <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl flex items-center justify-center mr-4 text-lg font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="polaris-heading-md mb-2 group-hover:text-blue-600 transition-colors">
                      {area.area_name}
                    </h3>
                    <p className="polaris-body-sm text-gray-600 mb-4 leading-relaxed">
                      {area.description}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className={`polaris-badge-clean ${
                    area.status === 'completed' ? 'polaris-badge-success-clean' :
                    area.status === 'active' ? 'polaris-badge-info-clean' :
                    'polaris-badge-neutral-clean'
                  }`}>
                    {area.status === 'completed' ? 'Complete' :
                     area.status === 'active' ? 'In Progress' :
                     'Not Started'}
                  </span>
                  
                  <span className="polaris-body-sm text-gray-500">
                    Tier {area.tier_available} Available
                  </span>
                </div>

                <Link
                  href={`/dashboard/assessments/${area.area_id}?tier=${area.tier_available}`}
                  className="polaris-btn-primary group"
                >
                  <span>{area.status === 'not_started' ? 'Start Assessment' : area.status === 'active' ? 'Continue' : 'Retake'}</span>
                  <ArrowRight className="polaris-icon-sm ml-2 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Clean Help Section */}
      <div className="polaris-card-clean bg-blue-50 border-blue-100">
        <div className="flex items-start">
          <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <BookOpen className="polaris-icon-md text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="polaris-heading-sm mb-2">Need Help Getting Started?</h3>
            <p className="polaris-body-sm text-gray-700 mb-4">
              Our assessment system helps identify opportunities in your business. Each area contains questions based on your tier access level.
            </p>
            <div className="flex items-center space-x-4">
              <Link 
                href="/dashboard/knowledge-base" 
                className="polaris-btn-secondary"
              >
                <BookOpen className="polaris-icon-sm mr-2" />
                Access Knowledge Base
              </Link>
              <Link 
                href="/dashboard/services" 
                className="polaris-btn-ghost"
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

export default CleanAssessmentsPage