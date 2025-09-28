'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Key, 
  Users, 
  TrendingUp, 
  DollarSign, 
  Settings,
  Clock,
  CheckCircle,
  ArrowRight,
  Plus,
  BarChart3
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

interface AgencyDashboardProps {
  user: User
}

interface LicenseStats {
  total_generated: number
  available: number
  used: number
  expired: number
}

interface DashboardData {
  license_stats: LicenseStats
  client_count: number
  subscription: any
  recent_activity: any[]
}

const AgencyDashboard: React.FC<AgencyDashboardProps> = ({ user }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch agency dashboard data
        const response = await apiClient.request('/agency/dashboard')
        setDashboardData(response.data)
      } catch (error) {
        console.error('Error fetching agency dashboard:', error)
        // Set mock data for development
        setDashboardData({
          license_stats: {
            total_generated: 25,
            available: 18,
            used: 7,
            expired: 0
          },
          client_count: 7,
          subscription: {
            plan: 'professional',
            status: 'active',
            current_period_end: '2024-03-15T00:00:00Z',
            usage_current_period: {
              licenses_generated: 25,
              assessments: 45,
              users: 7
            }
          },
          recent_activity: [
            {
              type: 'license_generation',
              quantity: 10,
              created_at: '2024-01-16T10:00:00Z',
              billable_amount: 50.0
            },
            {
              type: 'assessment_completion',
              quantity: 3,
              created_at: '2024-01-15T14:30:00Z',
              billable_amount: 75.0
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

  const stats = dashboardData?.license_stats
  const usageRate = stats ? Math.round((stats.used / stats.total_generated) * 100) : 0

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user.name}!
        </h1>
        <p className="text-lg text-gray-600">
          {user.company_name ? `Manage ${user.company_name}'s` : 'Manage your'} client licenses and business assessments.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Licenses"
          value={stats?.total_generated || 0}
          change={`${usageRate}% utilized`}
          changeType={usageRate > 70 ? 'increase' : 'neutral'}
          icon={Key}
          color="blue"
        />
        
        <StatCard
          title="Active Clients"
          value={dashboardData?.client_count || 0}
          icon={Users}
          color="green"
        />
        
        <StatCard
          title="Available Licenses"
          value={stats?.available || 0}
          change={stats?.expired ? `${stats.expired} expired` : 'All active'}
          changeType={stats?.expired ? 'decrease' : 'increase'}
          icon={CheckCircle}
          color="purple"
        />
        
        <StatCard
          title="Monthly Revenue"
          value="$1,250"
          change="+8% this month"
          changeType="increase"
          icon={DollarSign}
          color="yellow"
        />
      </div>

      {/* Quick Actions */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link 
            href="/dashboard/licenses/generate" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Plus className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Generate Licenses</h3>
              <p className="text-sm text-gray-500">Create new client codes</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/clients" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Manage Clients</h3>
              <p className="text-sm text-gray-500">View client progress</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/tiers" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
              <Settings className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Tier Configuration</h3>
              <p className="text-sm text-gray-500">Set access levels</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/analytics" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
              <BarChart3 className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Analytics</h3>
              <p className="text-sm text-gray-500">View performance</p>
            </div>
          </Link>
        </div>
      </div>

      {/* License Overview & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* License Distribution */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">License Distribution</h2>
            <Link 
              href="/dashboard/licenses" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All
            </Link>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <div className="h-10 w-10 bg-green-500 rounded-lg flex items-center justify-center mr-4">
                  <CheckCircle className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Used Licenses</h3>
                  <p className="text-sm text-gray-500">Active client accounts</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-green-600">{stats?.used || 0}</span>
            </div>

            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="h-10 w-10 bg-blue-500 rounded-lg flex items-center justify-center mr-4">
                  <Key className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Available Licenses</h3>
                  <p className="text-sm text-gray-500">Ready for distribution</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-blue-600">{stats?.available || 0}</span>
            </div>

            {stats?.expired && stats.expired > 0 && (
              <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                <div className="flex items-center">
                  <div className="h-10 w-10 bg-red-500 rounded-lg flex items-center justify-center mr-4">
                    <Clock className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Expired Licenses</h3>
                    <p className="text-sm text-gray-500">Need renewal</p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-red-600">{stats.expired}</span>
              </div>
            )}
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <Link 
              href="/dashboard/licenses/generate" 
              className="polaris-button-primary inline-flex items-center w-full justify-center"
            >
              <Plus className="mr-2 h-4 w-4" />
              Generate New Licenses
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
            <Link 
              href="/dashboard/billing" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View Billing
            </Link>
          </div>

          {dashboardData?.recent_activity && dashboardData.recent_activity.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.recent_activity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                      {activity.type === 'license_generation' ? (
                        <Key className="h-4 w-4 text-blue-600" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {activity.type === 'license_generation' ? 
                          `Generated ${activity.quantity} licenses` :
                          `${activity.quantity} assessments completed`}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm font-medium text-green-600">
                    +${activity.billable_amount}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Recent Activity</h3>
              <p className="text-gray-500">Activity will appear here as clients use your licenses</p>
            </div>
          )}
        </div>
      </div>

      {/* Subscription Status */}
      {dashboardData?.subscription && (
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Subscription Status</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-medium text-gray-900 capitalize">
                {dashboardData.subscription.plan} Plan
              </h3>
              <p className="text-sm text-gray-500">
                Status: {dashboardData.subscription.status}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Renews: {new Date(dashboardData.subscription.current_period_end).toLocaleDateString()}
              </p>
            </div>

            <div className="text-center">
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-medium text-gray-900">Usage This Period</h3>
              <p className="text-sm text-gray-500">
                {dashboardData.subscription.usage_current_period?.licenses_generated || 0} licenses generated
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {dashboardData.subscription.usage_current_period?.assessments || 0} assessments completed
              </p>
            </div>

            <div className="text-center">
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-medium text-gray-900">Active Users</h3>
              <p className="text-sm text-gray-500">
                {dashboardData.subscription.usage_current_period?.users || 0} / 50 users
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {Math.round(((dashboardData.subscription.usage_current_period?.users || 0) / 50) * 100)}% capacity
              </p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200 text-center">
            <Link 
              href="/dashboard/billing" 
              className="polaris-button-secondary inline-flex items-center"
            >
              <Settings className="mr-2 h-4 w-4" />
              Manage Subscription
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgencyDashboard