'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Search, 
  Briefcase, 
  DollarSign, 
  Star, 
  TrendingUp,
  Clock,
  CheckCircle,
  ArrowRight,
  MessageSquare,
  Eye
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

interface ProviderDashboardProps {
  user: User
}

interface DashboardData {
  provider_stats: {
    active_engagements: number
    pending_responses: number
    total_earnings: number
    rating: number
  }
  recent_opportunities: any[]
  active_engagements: any[]
}

const ProviderDashboard: React.FC<ProviderDashboardProps> = ({ user }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch provider dashboard data
        const response = await apiClient.request('/provider/dashboard')
        setDashboardData(response.data)
      } catch (error) {
        console.error('Error fetching provider dashboard:', error)
        // Set mock data for development
        setDashboardData({
          provider_stats: {
            active_engagements: 3,
            pending_responses: 2,
            total_earnings: 5420,
            rating: 4.8
          },
          recent_opportunities: [
            {
              id: '1',
              title: 'Financial Operations Assessment Help',
              area_name: 'Financial Operations & Management',
              budget_range: '1000-2500',
              timeline: '2-3 weeks',
              created_at: '2024-01-15T10:00:00Z'
            },
            {
              id: '2', 
              title: 'Technology Infrastructure Review',
              area_name: 'Technology & Security Infrastructure',
              budget_range: '2500-5000',
              timeline: '1 month',
              created_at: '2024-01-14T14:30:00Z'
            }
          ],
          active_engagements: [
            {
              id: '1',
              service_info: {
                title: 'Quality Management System Implementation',
                area_name: 'Quality Management & Standards'
              },
              client_info: {
                name: 'Tech Solutions Inc',
                company: 'Tech Solutions Inc'
              },
              status: 'in_progress',
              agreed_fee: 2500,
              updated_at: '2024-01-16T09:00:00Z'
            }
          ]
        })
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

  const stats = dashboardData?.provider_stats

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user.name}!
        </h1>
        <p className="text-lg text-gray-600">
          Manage your service offerings and client engagements.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Engagements"
          value={stats?.active_engagements || 0}
          icon={Briefcase}
          color="blue"
        />
        
        <StatCard
          title="Pending Responses"
          value={stats?.pending_responses || 0}
          icon={Clock}
          color="yellow"
        />
        
        <StatCard
          title="Total Earnings"
          value={`$${stats?.total_earnings?.toLocaleString() || '0'}`}
          change="+12% this month"
          changeType="increase"
          icon={DollarSign}
          color="green"
        />
        
        <StatCard
          title="Rating"
          value={`${stats?.rating || '0'}/5`}
          icon={Star}
          color="purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link 
            href="/dashboard/opportunities" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Search className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Browse Opportunities</h3>
              <p className="text-sm text-gray-500">Find new service requests</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>

          <Link 
            href="/dashboard/my-services" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <Briefcase className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">My Services</h3>
              <p className="text-sm text-gray-500">Manage active engagements</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>

          <Link 
            href="/dashboard/profile" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
              <Star className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Update Profile</h3>
              <p className="text-sm text-gray-500">Enhance your profile</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 ml-auto" />
          </Link>
        </div>
      </div>

      {/* Recent Opportunities & Active Engagements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Opportunities */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Opportunities</h2>
            <Link 
              href="/dashboard/opportunities" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All
            </Link>
          </div>

          {dashboardData?.recent_opportunities && dashboardData.recent_opportunities.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.recent_opportunities.map((opportunity) => (
                <div key={opportunity.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{opportunity.title}</h3>
                    <span className="polaris-badge polaris-badge-info text-xs">
                      {opportunity.budget_range}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{opportunity.area_name}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {opportunity.timeline}
                    </span>
                    <span>{new Date(opportunity.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center justify-between mt-3">
                    <Link
                      href={`/dashboard/opportunities/${opportunity.id}`}
                      className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Opportunities Available</h3>
              <p className="text-gray-500">Check back later for new service requests</p>
            </div>
          )}
        </div>

        {/* Active Engagements */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Active Engagements</h2>
            <Link 
              href="/dashboard/my-services" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All
            </Link>
          </div>

          {dashboardData?.active_engagements && dashboardData.active_engagements.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.active_engagements.map((engagement) => (
                <div key={engagement.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{engagement.service_info?.title}</h3>
                    <span className={`polaris-badge ${
                      engagement.status === 'in_progress' ? 'polaris-badge-info' :
                      engagement.status === 'completed' ? 'polaris-badge-success' :
                      'polaris-badge-warning'
                    } text-xs`}>
                      {engagement.status.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{engagement.service_info?.area_name}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                    <span>Client: {engagement.client_info?.name}</span>
                    <span>${engagement.agreed_fee?.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      Updated: {new Date(engagement.updated_at).toLocaleDateString()}
                    </span>
                    <Link
                      href={`/dashboard/my-services/${engagement.id}`}
                      className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
                    >
                      <MessageSquare className="h-4 w-4 mr-1" />
                      Manage
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Engagements</h3>
              <p className="text-gray-500 mb-4">Start bidding on opportunities to build your portfolio</p>
              <Link 
                href="/dashboard/opportunities" 
                className="polaris-button-primary inline-flex items-center"
              >
                Browse Opportunities
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProviderDashboard