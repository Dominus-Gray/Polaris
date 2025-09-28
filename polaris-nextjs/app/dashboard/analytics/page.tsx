'use client'

import React, { useState, useEffect } from 'react'
import { 
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  Target,
  CheckCircle,
  Clock,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Star,
  FileText,
  Building
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../providers'
import { apiClient } from '../../providers'
import LoadingSpinner from '../components/LoadingSpinner'

interface AnalyticsData {
  overview: {
    total_assessments: number
    completed_assessments: number
    active_services: number
    total_spending: number
    readiness_score: number
    improvement_trend: 'up' | 'down' | 'stable'
  }
  assessment_progress: {
    area_id: string
    area_name: string
    completion_percentage: number
    score: number
    last_updated: string
    status: 'not_started' | 'in_progress' | 'completed'
  }[]
  service_metrics: {
    total_requests: number
    completed_services: number
    average_satisfaction: number
    total_spent: number
    active_engagements: number
    provider_rating: number
  }
  time_series: {
    date: string
    assessments: number
    services: number
    spending: number
    readiness_score: number
  }[]
  recent_activity: {
    id: string
    type: 'assessment' | 'service' | 'engagement' | 'system'
    title: string
    description: string
    timestamp: string
    status: 'completed' | 'in_progress' | 'pending'
  }[]
}

const AnalyticsPage = () => {
  const { state } = useAuth()
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    fetchAnalyticsData()
  }, [timeRange])

  const fetchAnalyticsData = async () => {
    try {
      const response = await apiClient.request(`/analytics/dashboard?range=${timeRange}`)
      setAnalyticsData(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
      // Mock data for demonstration
      setAnalyticsData({
        overview: {
          total_assessments: 10,
          completed_assessments: 3,
          active_services: 2,
          total_spending: 4500,
          readiness_score: 72,
          improvement_trend: 'up'
        },
        assessment_progress: [
          {
            area_id: 'area1',
            area_name: 'Business Formation & Registration',
            completion_percentage: 100,
            score: 85,
            last_updated: '2024-01-15T10:00:00Z',
            status: 'completed'
          },
          {
            area_id: 'area2',
            area_name: 'Financial Operations & Management',
            completion_percentage: 100,
            score: 78,
            last_updated: '2024-01-14T15:30:00Z',
            status: 'completed'
          },
          {
            area_id: 'area3',
            area_name: 'Legal & Contracting Compliance',
            completion_percentage: 60,
            score: 45,
            last_updated: '2024-01-12T11:20:00Z',
            status: 'in_progress'
          },
          {
            area_id: 'area5',
            area_name: 'Technology & Security Infrastructure',
            completion_percentage: 30,
            score: 25,
            last_updated: '2024-01-10T14:15:00Z',
            status: 'in_progress'
          },
          {
            area_id: 'area4',
            area_name: 'Quality Management & Standards',
            completion_percentage: 0,
            score: 0,
            last_updated: null,
            status: 'not_started'
          }
        ],
        service_metrics: {
          total_requests: 5,
          completed_services: 2,
          average_satisfaction: 4.8,
          total_spent: 4500,
          active_engagements: 2,
          provider_rating: 4.7
        },
        time_series: [
          { date: '2024-01-01', assessments: 0, services: 0, spending: 0, readiness_score: 15 },
          { date: '2024-01-08', assessments: 2, services: 1, spending: 1500, readiness_score: 35 },
          { date: '2024-01-15', assessments: 4, services: 2, spending: 3000, readiness_score: 55 },
          { date: '2024-01-22', assessments: 6, services: 3, spending: 4500, readiness_score: 72 }
        ],
        recent_activity: [
          {
            id: '1',
            type: 'assessment',
            title: 'Completed Financial Operations Assessment',
            description: 'Achieved 78% score with 5 improvement areas identified',
            timestamp: '2024-01-15T10:00:00Z',
            status: 'completed'
          },
          {
            id: '2',
            type: 'service',
            title: 'Hired Financial Consultant',
            description: 'Started engagement with Sarah Johnson for cash flow optimization',
            timestamp: '2024-01-14T15:30:00Z',
            status: 'in_progress'
          },
          {
            id: '3',
            type: 'engagement',
            title: 'Legal Compliance Review Delivered',
            description: 'Received comprehensive compliance checklist and recommendations',
            timestamp: '2024-01-12T09:15:00Z',
            status: 'completed'
          },
          {
            id: '4',
            type: 'system',
            title: 'New Knowledge Base Resources Available',
            description: 'Technology security templates and guides added to your library',
            timestamp: '2024-01-10T16:45:00Z',
            status: 'completed'
          }
        ]
      })
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchAnalyticsData()
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'assessment':
        return <Target className="h-5 w-5 text-blue-600" />
      case 'service':
        return <Users className="h-5 w-5 text-green-600" />
      case 'engagement':
        return <Building className="h-5 w-5 text-purple-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!analyticsData) {
    return (
      <div className="polaris-container py-8 text-center">
        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Analytics Unavailable</h1>
        <p className="text-gray-600">Unable to load your analytics data. Please try again later.</p>
      </div>
    )
  }

  return (
    <div className="polaris-container py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="polaris-heading-xl mb-2">Analytics & Insights</h1>
            <p className="polaris-body text-gray-600">
              Track your business readiness progress and service engagement metrics.
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="polaris-input py-2 px-3 text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="polaris-button-secondary"
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            
            <button className="polaris-button-primary">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="polaris-stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Overall Readiness</p>
              <p className="text-3xl font-bold text-gray-900">{analyticsData.overview.readiness_score}%</p>
              <div className="flex items-center mt-1">
                {getTrendIcon(analyticsData.overview.improvement_trend)}
                <span className="text-sm text-gray-600 ml-1">vs last month</span>
              </div>
            </div>
            <div className="h-12 w-12 bg-polaris-100 rounded-full flex items-center justify-center">
              <Target className="h-6 w-6 text-polaris-600" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Completed Assessments</p>
              <p className="text-3xl font-bold text-gray-900">
                {analyticsData.overview.completed_assessments}
                <span className="text-lg text-gray-500">/{analyticsData.overview.total_assessments}</span>
              </p>
              <p className="text-sm text-green-600 mt-1">
                {Math.round((analyticsData.overview.completed_assessments / analyticsData.overview.total_assessments) * 100)}% complete
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Services</p>
              <p className="text-3xl font-bold text-gray-900">{analyticsData.overview.active_services}</p>
              <p className="text-sm text-blue-600 mt-1">
                {analyticsData.service_metrics.active_engagements} engagements
              </p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Investment</p>
              <p className="text-3xl font-bold text-gray-900">${analyticsData.overview.total_spending.toLocaleString()}</p>
              <div className="flex items-center mt-1">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <span className="text-sm text-gray-600">{analyticsData.service_metrics.average_satisfaction}/5 satisfaction</span>
              </div>
            </div>
            <div className="h-12 w-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <DollarSign className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Assessment Progress & Service Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Assessment Progress */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="polaris-heading-md">Assessment Progress</h2>
            <Link 
              href="/dashboard/assessments" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All →
            </Link>
          </div>
          
          <div className="space-y-4">
            {analyticsData.assessment_progress.slice(0, 5).map((area) => (
              <div key={area.area_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900 text-sm">{area.area_name}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-bold ${getScoreColor(area.score)}`}>
                      {area.score}%
                    </span>
                    <span className={`polaris-badge text-xs ${
                      area.status === 'completed' ? 'polaris-badge-success' :
                      area.status === 'in_progress' ? 'polaris-badge-info' :
                      'polaris-badge-neutral'
                    }`}>
                      {area.status === 'completed' ? 'Complete' :
                       area.status === 'in_progress' ? 'In Progress' :
                       'Not Started'}
                    </span>
                  </div>
                </div>
                
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{area.completion_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="polaris-progress-fill" 
                      style={{ width: `${area.completion_percentage}%` }}
                    ></div>
                  </div>
                </div>
                
                {area.last_updated && (
                  <p className="text-xs text-gray-500">
                    Updated {new Date(area.last_updated).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Service Metrics */}
        <div className="polaris-card">
          <h2 className="polaris-heading-md mb-6">Service Engagement</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{analyticsData.service_metrics.total_requests}</p>
              <p className="text-sm text-gray-600">Total Requests</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{analyticsData.service_metrics.completed_services}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-center justify-center mb-1">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <p className="text-2xl font-bold text-yellow-600">{analyticsData.service_metrics.average_satisfaction}</p>
              </div>
              <p className="text-sm text-gray-600">Avg. Rating</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">${analyticsData.service_metrics.total_spent.toLocaleString()}</p>
              <p className="text-sm text-gray-600">Total Spent</p>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between">
              <p className="font-medium text-gray-900">Provider Performance</p>
              <div className="flex items-center">
                <div className="flex items-center mr-2">
                  {[1,2,3,4,5].map((star) => (
                    <Star 
                      key={star} 
                      className={`h-4 w-4 ${
                        star <= Math.round(analyticsData.service_metrics.provider_rating) 
                          ? 'text-yellow-400 fill-current' 
                          : 'text-gray-300'
                      }`} 
                    />
                  ))}
                </div>
                <span className="text-sm font-medium text-gray-700">{analyticsData.service_metrics.provider_rating}/5</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="polaris-card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="polaris-heading-md">Recent Activity</h2>
          <button className="polaris-button-ghost text-sm">
            <Filter className="mr-2 h-4 w-4" />
            Filter
          </button>
        </div>
        
        <div className="space-y-4">
          {analyticsData.recent_activity.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                {getActivityIcon(activity.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-medium text-gray-900">{activity.title}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`polaris-badge text-xs ${
                      activity.status === 'completed' ? 'polaris-badge-success' :
                      activity.status === 'in_progress' ? 'polaris-badge-info' :
                      'polaris-badge-warning'
                    }`}>
                      {activity.status === 'completed' ? 'Completed' :
                       activity.status === 'in_progress' ? 'Active' :
                       'Pending'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{activity.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center pt-6 border-t border-gray-200 mt-6">
          <button className="polaris-button-secondary">
            View All Activity
          </button>
        </div>
      </div>
    </div>
  )
}

export default AnalyticsPage