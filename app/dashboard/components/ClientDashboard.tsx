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
        setDashboardData(dashboardResponse.data)

        // Fetch assessment progress using correct endpoint
        const progressResponse = await apiClient.request('/client/assessment-progress')
        setAssessmentProgress(progressResponse.data.area_progress || [])
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
  const areasCompleted = dashboardData?.procurement_readiness?.areas_completed || assessmentProgress.filter(p => p.status === 'completed').length
  const totalAreas = dashboardData?.procurement_readiness?.total_areas || 10
  const completionPercentage = Math.round((areasCompleted / totalAreas) * 100)

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user.name}!
        </h1>
        <p className="text-lg text-gray-600">
          {user.company_name ? `Manage ${user.company_name}'s` : 'Manage your'} business assessment and compliance journey.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Overall Readiness Score"
          value={`${overallScore}%`}
          change={overallScore >= 75 ? '+5%' : overallScore >= 50 ? '+2%' : 'Needs improvement'}
          changeType={overallScore >= 75 ? 'increase' : overallScore >= 50 ? 'increase' : 'neutral'}
          icon={Target}
          color={overallScore >= 75 ? 'green' : overallScore >= 50 ? 'yellow' : 'red'}
        />
        
        <StatCard
          title="Areas Completed"
          value={`${areasCompleted}/${totalAreas}`}
          change={`${completionPercentage}% complete`}
          changeType={areasCompleted > 5 ? 'increase' : 'neutral'}
          icon={CheckCircle}
          color="blue"
        />
        
        <StatCard
          title="Active Assessments"
          value={assessmentProgress.filter(p => p.status === 'active').length}
          icon={ClipboardList}
          color="purple"
        />
        
        <StatCard
          title="Service Requests"
          value="0"
          change="View all"
          icon={Briefcase}
          color="green"
        />
      </div>

      {/* Quick Actions */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link 
            href="/dashboard/assessments" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <ClipboardList className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Start Assessment</h3>
              <p className="text-sm text-gray-500">Begin or continue assessments</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>

          <Link 
            href="/dashboard/services" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <Briefcase className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Request Services</h3>
              <p className="text-sm text-gray-500">Get professional help</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>

          <Link 
            href="/dashboard/knowledge-base" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Knowledge Base</h3>
              <p className="text-sm text-gray-500">Access resources & guides</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>
        </div>
      </div>

      {/* Assessment Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Progress Overview */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Assessment Progress</h2>
            <Link 
              href="/dashboard/assessments" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All
            </Link>
          </div>

          <div className="space-y-4">
            {assessmentProgress.slice(0, 5).map((area) => (
              <div key={area.area_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-sm font-medium text-gray-900">{area.area_name}</h3>
                    <span className={`polaris-badge ${
                      area.status === 'completed' ? 'polaris-badge-success' :
                      area.status === 'active' ? 'polaris-badge-info' :
                      'polaris-badge-warning'
                    }`}>
                      {area.status === 'completed' ? 'Complete' :
                       area.status === 'active' ? 'In Progress' :
                       'Not Started'}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className="bg-polaris-blue h-2 rounded-full" 
                        style={{ width: `${area.latest_score}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-500">{area.latest_score}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Next Steps */}
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Recommended Next Steps</h2>
          <div className="space-y-4">
            {(dashboardData?.procurement_readiness?.next_steps || [
              'Complete your first business assessment',
              'Review knowledge base resources',
              'Consider requesting professional services'
            ]).map((step, index) => (
              <div key={index} className="flex items-start">
                <div className="h-6 w-6 bg-polaris-blue rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-white font-medium text-xs">{index + 1}</span>
                </div>
                <p className="text-gray-700">{step}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <Link 
              href="/dashboard/assessments" 
              className="polaris-button-primary inline-flex items-center"
            >
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activity</h2>
        
        {dashboardData?.recent_activity && dashboardData.recent_activity.length > 0 ? (
          <div className="space-y-4">
            {dashboardData.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <Clock className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.description}</p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="h-6 w-6 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Recent Activity</h3>
            <p className="text-gray-500 mb-4">Start your first assessment to see activity here</p>
            <Link 
              href="/dashboard/assessments" 
              className="polaris-button-primary inline-flex items-center"
            >
              Start Assessment
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default ClientDashboard