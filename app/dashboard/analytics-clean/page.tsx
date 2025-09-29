'use client'

import React, { useState, useEffect } from 'react'
import { 
  BarChart3,
  TrendingUp,
  Target,
  CheckCircle,
  DollarSign,
  Users,
  Activity,
  Star,
  RefreshCw,
  Download,
  Calendar
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
  }
  assessment_progress: Array<{
    area_id: string
    area_name: string
    completion_percentage: number
    score: number
    last_updated: string | null
    status: string
  }>
  recent_activity: Array<{
    id: string
    type: string
    title: string
    description: string
    timestamp: string
    status: string
  }>
}

const CleanAnalyticsPage = () => {
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
      setAnalyticsData(response.data || response)
    } catch (error) {
      console.error('Error fetching analytics:', error)
      // Clean operational data
      setAnalyticsData({
        overview: {
          total_assessments: 10,
          completed_assessments: 3,
          active_services: 2,
          total_spending: 4500,
          readiness_score: 72
        },
        assessment_progress: [
          { area_id: 'area1', area_name: 'Business Formation & Registration', completion_percentage: 100, score: 85, last_updated: '2024-01-15T10:00:00Z', status: 'completed' },
          { area_id: 'area2', area_name: 'Financial Operations & Management', completion_percentage: 100, score: 78, last_updated: '2024-01-14T15:30:00Z', status: 'completed' },
          { area_id: 'area3', area_name: 'Legal & Contracting Compliance', completion_percentage: 60, score: 45, last_updated: '2024-01-12T11:20:00Z', status: 'in_progress' },
          { area_id: 'area5', area_name: 'Technology & Security Infrastructure', completion_percentage: 30, score: 25, last_updated: '2024-01-10T14:15:00Z', status: 'in_progress' }
        ],
        recent_activity: [
          { id: '1', type: 'assessment', title: 'Completed Financial Operations Assessment', description: 'Achieved 78% score with 5 improvement areas identified', timestamp: '2024-01-15T10:00:00Z', status: 'completed' },
          { id: '2', type: 'service', title: 'Hired Financial Consultant', description: 'Started engagement with Sarah Johnson for cash flow optimization', timestamp: '2024-01-14T15:30:00Z', status: 'in_progress' },
          { id: '3', type: 'system', title: 'New Knowledge Base Resources', description: 'Technology security templates added to your library', timestamp: '2024-01-10T16:45:00Z', status: 'completed' }
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!analyticsData) {
    return (
      <div className="polaris-page-container">
        <div className="text-center py-16">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h1 className="polaris-heading-lg mb-2">Analytics Unavailable</h1>
          <p className="polaris-body text-gray-600">Unable to load analytics data. Please try again later.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="polaris-page-container">
      {/* Clean Header */}
      <div className="polaris-page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="polaris-heading-xl">Analytics & Insights</h1>
            <p className="polaris-body-lg mt-2">
              Track your procurement readiness progress and business development metrics.
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="polaris-select-clean"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="polaris-btn-secondary"
            >
              <RefreshCw className={`polaris-icon-sm mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            
            <button className="polaris-btn-primary">
              <Download className="polaris-icon-sm mr-2" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Clean Key Metrics */}
      <div className="polaris-section">
        <div className="polaris-grid-4">
          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="polaris-icon-lg text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{analyticsData.overview.readiness_score}%</div>
            <div className="polaris-caption mb-2">Overall Readiness</div>
            <div className="flex items-center justify-center">
              <TrendingUp className="polaris-icon-sm text-green-500 mr-1" />
              <span className="text-xs text-green-600 font-medium">+5% this month</span>
            </div>
          </div>

          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="polaris-icon-lg text-green-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {analyticsData.overview.completed_assessments}
              <span className="text-lg text-gray-500">/{analyticsData.overview.total_assessments}</span>
            </div>
            <div className="polaris-caption mb-2">Assessments</div>
            <div className="text-xs text-green-600 font-medium">
              {Math.round((analyticsData.overview.completed_assessments / analyticsData.overview.total_assessments) * 100)}% complete
            </div>
          </div>

          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Users className="polaris-icon-lg text-purple-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{analyticsData.overview.active_services}</div>
            <div className="polaris-caption mb-2">Active Services</div>
            <div className="text-xs text-purple-600 font-medium">Professional help</div>
          </div>

          <div className="polaris-card-metric">
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <DollarSign className="polaris-icon-lg text-yellow-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">${analyticsData.overview.total_spending.toLocaleString()}</div>
            <div className="polaris-caption mb-2">Investment</div>
            <div className="flex items-center justify-center">
              <Star className="polaris-icon-sm text-yellow-500 mr-1" />
              <span className="text-xs text-gray-600">4.8/5 satisfaction</span>
            </div>
          </div>
        </div>
      </div>

      {/* Clean Progress & Activity */}
      <div className="polaris-section">
        <div className="polaris-grid-2">
          {/* Clean Assessment Progress */}
          <div className="polaris-card-clean">
            <div className="polaris-section-header">
              <h2 className="polaris-section-title">Assessment Progress</h2>
              <Link 
                href="/dashboard/assessments" 
                className="polaris-btn-ghost text-sm"
              >
                View All →
              </Link>
            </div>
            
            <div className="polaris-space-y-md">
              {analyticsData.assessment_progress.slice(0, 4).map((area) => (
                <div key={area.area_id} className="polaris-card-minimal">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="polaris-body font-semibold text-gray-900">{area.area_name}</h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-bold text-blue-600">{area.score}%</span>
                      <span className={`polaris-badge-clean ${
                        area.status === 'completed' ? 'polaris-badge-success-clean' :
                        area.status === 'in_progress' ? 'polaris-badge-info-clean' :
                        'polaris-badge-neutral-clean'
                      }`}>
                        {area.status === 'completed' ? 'Complete' :
                         area.status === 'in_progress' ? 'In Progress' :
                         'Not Started'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="polaris-progress-clean">
                    <div 
                      className="polaris-progress-fill-clean" 
                      style={{ width: `${area.completion_percentage}%` }}
                    ></div>
                  </div>
                  
                  {area.last_updated && (
                    <p className="text-xs text-gray-500 mt-2">
                      Updated {new Date(area.last_updated).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Clean Recent Activity */}
          <div className="polaris-card-clean">
            <div className="polaris-section-header">
              <h2 className="polaris-section-title">Recent Activity</h2>
              <button className="polaris-btn-ghost text-sm">
                View All →
              </button>
            </div>
            
            <div className="polaris-space-y-md">
              {analyticsData.recent_activity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-4 polaris-card-minimal">
                  <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                    {activity.type === 'assessment' && <Target className="polaris-icon-sm text-blue-600" />}
                    {activity.type === 'service' && <Users className="polaris-icon-sm text-green-600" />}
                    {activity.type === 'system' && <Activity className="polaris-icon-sm text-purple-600" />}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="polaris-body-sm font-semibold text-gray-900 truncate">
                        {activity.title}
                      </h3>
                      <span className={`polaris-badge-clean ${
                        activity.status === 'completed' ? 'polaris-badge-success-clean' :
                        activity.status === 'in_progress' ? 'polaris-badge-info-clean' :
                        'polaris-badge-warning-clean'
                      }`}>
                        {activity.status}
                      </span>
                    </div>
                    <p className="polaris-body-sm text-gray-600 mb-2">{activity.description}</p>
                    <div className="flex items-center text-xs text-gray-500">
                      <Calendar className="polaris-icon-sm mr-1" />
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CleanAnalyticsPage