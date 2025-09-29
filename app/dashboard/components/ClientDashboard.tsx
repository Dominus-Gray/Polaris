'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  ClipboardList, 
  TrendingUp, 
  Briefcase, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  Star,
  Clock,
  Target
} from 'lucide-react'
import StatCard from './StatCard'
import LoadingSpinner from './LoadingSpinner'
import { apiClient } from '../../providers'

interface User {
  id: string
  name: string
  email: string
  role: string
  company_name?: string
}

interface ClientDashboardProps {
  user: User
}

interface AssessmentProgress {
  area_id: string
  area_name: string
  sessions_completed: number
  latest_score: number
  last_assessment: string | null
  status: string
}

interface DashboardData {
  procurement_readiness: {
    overall_score: number
    areas_completed: number
    total_areas: number
    next_steps: string[]
  }
  recent_activity: any[]
  quick_actions: Array<{
    title: string
    url: string
    icon: string
  }>
}

const ClientDashboard: React.FC<ClientDashboardProps> = ({ user }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [assessmentProgress, setAssessmentProgress] = useState<AssessmentProgress[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch dashboard data using correct endpoint
        const dashboardResponse = await apiClient.request('/home/client')
        if (dashboardResponse && dashboardResponse.data) {
          setDashboardData(dashboardResponse.data)
        } else {
          setDashboardData(dashboardResponse)
        }

        // Fetch assessment progress using correct endpoint  
        const progressResponse = await apiClient.request('/client/assessment-progress')
        if (progressResponse && progressResponse.data) {
          setAssessmentProgress(progressResponse.data.area_progress || progressResponse.data.areas || [])
        } else {
          setAssessmentProgress(progressResponse.area_progress || progressResponse.areas || [])
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        // Provide fallback data to prevent crashes
        setDashboardData({
          procurement_readiness: {
            overall_score: 0,
            areas_completed: 0,
            total_areas: 10,
            next_steps: ['Connect with your local agency partner', 'Complete business maturity assessment', 'Access professional service providers']
          },
          recent_activity: [],
          quick_actions: []
        })
        setAssessmentProgress([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const overallScore = dashboardData?.procurement_readiness?.overall_score || 0
  const areasCompleted = dashboardData?.procurement_readiness?.areas_completed || (Array.isArray(assessmentProgress) ? assessmentProgress.filter(p => p.status === 'completed').length : 0)
  const totalAreas = dashboardData?.procurement_readiness?.total_areas || 10
  const completionPercentage = Math.round((areasCompleted / totalAreas) * 100)

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Clean Welcome Section */}
      <div className="mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">
          Welcome back, {user.name || 'User'}!
        </h1>
        <p className="text-lg text-gray-600 leading-relaxed">
          {user.company_name ? `Manage ${user.company_name}'s` : 'Manage your'} procurement readiness journey.
        </p>
      </div>

      {/* Clean Key Metrics */}
      <div className="mb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl border border-gray-100 p-6 text-center hover:shadow-md transition-shadow">
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{overallScore}%</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Overall Readiness</div>
            <div className="text-xs text-green-600 font-medium mt-2">
              {overallScore >= 75 ? '+5% this month' : overallScore >= 50 ? '+2% this month' : 'Needs improvement'}
            </div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-100 p-6 text-center hover:shadow-md transition-shadow">
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{areasCompleted}/{totalAreas}</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Areas Completed</div>
            <div className="text-xs text-blue-600 font-medium mt-2">{completionPercentage}% complete</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-100 p-6 text-center hover:shadow-md transition-shadow">
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <ClipboardList className="h-6 w-6 text-purple-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {Array.isArray(assessmentProgress) ? assessmentProgress.filter(p => p.status === 'active').length : 0}
            </div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Active Assessments</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-100 p-6 text-center hover:shadow-md transition-shadow">
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Briefcase className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">0</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Service Requests</div>
          </div>
        </div>
      </div>

      {/* Clean Quick Actions */}
      <div className="mb-12">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link 
              href="/dashboard/assessments" 
              className="flex items-center p-6 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-200 transition-all group"
            >
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <ClipboardList className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Start Assessment</h3>
                <p className="text-sm text-gray-600">Begin or continue assessments</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
            </Link>

            <Link 
              href="/dashboard/services" 
              className="flex items-center p-6 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-green-200 transition-all group"
            >
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <Briefcase className="h-6 w-6 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Request Services</h3>
                <p className="text-sm text-gray-600">Get professional help</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
            </Link>

            <Link 
              href="/dashboard/knowledge-base" 
              className="flex items-center p-6 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-purple-200 transition-all group"
            >
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <BookOpen className="h-6 w-6 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Knowledge Base</h3>
                <p className="text-sm text-gray-600">Access resources & guides</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" />
            </Link>
          </div>
        </div>
      </div>

      {/* Clean Assessment Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Assessment Progress</h2>
            <Link 
              href="/dashboard/assessments" 
              className="text-blue-600 hover:text-blue-700 font-medium text-sm transition-colors"
            >
              View All →
            </Link>
          </div>

          <div className="space-y-6">
            {Array.isArray(assessmentProgress) && assessmentProgress.length > 0 ? assessmentProgress.slice(0, 5).map((area) => (
              <div key={area.area_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">{area.area_name}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    area.status === 'completed' ? 'bg-green-100 text-green-800' :
                    area.status === 'active' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {area.status === 'completed' ? 'Complete' :
                     area.status === 'active' ? 'In Progress' :
                     'Not Started'}
                  </span>
                </div>
                
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{area.latest_score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-500" 
                      style={{ width: `${area.latest_score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )) : (
              // Show default areas when no progress data
              ['Business Formation', 'Financial Operations', 'Legal Compliance', 'Quality Management', 'Technology Security'].map((areaName, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">{areaName}</h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Not Started
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Clean Next Steps */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Recommended Next Steps</h2>
          <div className="space-y-4">
            {(dashboardData?.procurement_readiness?.next_steps || [
              'Connect with your local agency partner',
              'Complete your first business assessment',
              'Review knowledge base resources',
              'Consider requesting professional services'
            ]).map((step, index) => (
              <div key={index} className="flex items-start">
                <div className="h-6 w-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <span className="text-white font-medium text-xs">{index + 1}</span>
                </div>
                <p className="text-gray-700 leading-relaxed">{step}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <Link 
              href="/dashboard/assessments" 
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClientDashboard