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
        // Try to fetch real tier-based assessment schema from backend
        const response = await apiClient.request('/assessment/schema/tier-based')
        console.log('Assessment schema response:', response)
        
        if (response.data && response.data.areas) {
          setAssessmentData(response.data)
        } else if (response.areas) {
          setAssessmentData(response)
        } else {
          throw new Error('Invalid schema format')
        }
      } catch (error) {
        console.error('Error fetching assessment data, using operational fallback:', error)
        
        // Comprehensive operational assessment data for all 10 areas
        setAssessmentData({
          client_tier_access: 3, // Full tier access for QA users
          areas: [
            {
              area_id: 'area1',
              area_name: 'Business Formation & Registration',
              description: 'Legal structure, registration, licenses, and permits',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area2',
              area_name: 'Financial Operations & Management',
              description: 'Financial planning, accounting, and cash flow management',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area3',
              area_name: 'Legal & Contracting Compliance',
              description: 'Legal requirements, contracts, and compliance standards',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area4',
              area_name: 'Quality Management & Standards',
              description: 'Quality systems, certifications, and process standards',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area5',
              area_name: 'Technology & Security Infrastructure',
              description: 'IT systems, cybersecurity, and data management',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area6',
              area_name: 'Human Resources & Capacity',
              description: 'Staffing, training, and organizational capacity',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area7',
              area_name: 'Performance Tracking & Reporting',
              description: 'Metrics, reporting systems, and performance management',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area8',
              area_name: 'Risk Management & Business Continuity',
              description: 'Risk assessment, mitigation, and business continuity planning',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area9',
              area_name: 'Supply Chain Management & Vendor Relations',
              description: 'Supplier relationships, procurement, and supply chain optimization',
              tier_available: 3,
              sessions_completed: 0,
              latest_score: 0,
              status: 'not_started',
              last_assessment: null
            },
            {
              area_id: 'area10',
              area_name: 'Competitive Advantage & Market Position',
              description: 'Competitive advantages, market capture processes, strategic partnerships',
              tier_available: 3,
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
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-600">
              Tier Access Level: <span className="font-medium text-polaris-blue">Tier {assessmentData?.client_tier_access || 1}</span>
            </div>
            <div className="h-4 w-px bg-gray-300"></div>
            <div className="text-sm text-gray-600">
              {areas.length} Areas Available
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {areas.map((area, index) => (
            <div 
              key={area.area_id} 
              className="group polaris-card hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer relative overflow-hidden"
            >
              {/* Progress indicator bar */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gray-100">
                <div 
                  className="h-full bg-polaris-blue transition-all duration-500" 
                  style={{ width: `${area.latest_score}%` }}
                ></div>
              </div>

              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <div className="h-12 w-12 bg-gradient-to-br from-polaris-blue to-polaris-navy text-white rounded-xl flex items-center justify-center mr-4 text-lg font-bold shadow-md">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-polaris-blue transition-colors">
                          {area.area_name}
                        </h3>
                        <p className="text-gray-600 text-sm leading-relaxed">{area.description}</p>
                      </div>
                    </div>
                    
                    {/* Enhanced Progress Section */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-600 font-medium">Progress</span>
                        <span className="text-gray-900 font-semibold">{area.latest_score}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 shadow-inner">
                        <div 
                          className="bg-gradient-to-r from-polaris-blue to-blue-500 h-3 rounded-full transition-all duration-700 shadow-sm" 
                          style={{ width: `${area.latest_score}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Enhanced Status & Meta Info */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          area.status === 'completed' ? 'bg-green-100 text-green-800 border border-green-200' :
                          area.status === 'active' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                          'bg-gray-100 text-gray-800 border border-gray-200'
                        }`}>
                          {area.status === 'completed' ? (
                            <>
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Complete
                            </>
                          ) : area.status === 'active' ? (
                            <>
                              <Clock className="w-3 h-3 mr-1" />
                              In Progress
                            </>
                          ) : (
                            <>
                              <Target className="w-3 h-3 mr-1" />
                              Not Started
                            </>
                          )}
                        </span>
                        
                        <div className="text-xs text-gray-500 flex items-center">
                          <span className="w-2 h-2 bg-polaris-blue rounded-full mr-1"></span>
                          Tier {area.tier_available}
                        </div>
                      </div>
                      
                      {area.sessions_completed > 0 && (
                        <div className="text-xs text-gray-500 flex items-center">
                          <span className="font-medium">{area.sessions_completed}</span>
                          <span className="ml-1">sessions</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Enhanced Action Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="text-xs text-gray-500">
                    {area.last_assessment ? (
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        Last: {new Date(area.last_assessment).toLocaleDateString()}
                      </span>
                    ) : (
                      <span className="flex items-center">
                        <Target className="w-3 h-3 mr-1" />
                        Ready to start
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3">
                    {area.status === 'completed' && (
                      <Link
                        href={`/dashboard/assessments/${area.area_id}/results`}
                        className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center transition-colors"
                      >
                        <TrendingUp className="h-4 w-4 mr-1" />
                        Results
                      </Link>
                    )}
                    
                    <Link
                      href={`/dashboard/assessments/${area.area_id}`}
                      className="inline-flex items-center px-4 py-2 bg-polaris-blue text-white rounded-lg font-medium text-sm hover:bg-polaris-navy transition-colors shadow-sm hover:shadow-md group"
                    >
                      {area.status === 'not_started' ? (
                        <>
                          <span>Start Assessment</span>
                          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
                        </>
                      ) : area.status === 'active' ? (
                        <>
                          <span>Continue</span>
                          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
                        </>
                      ) : (
                        <>
                          <span>Retake</span>
                          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
                        </>
                      )}
                    </Link>
                  </div>
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