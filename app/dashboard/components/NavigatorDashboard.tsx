'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Shield, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Settings,
  ArrowRight,
  Server,
  Database,
  Activity
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

interface NavigatorDashboardProps {
  user: User
}

interface SystemStats {
  total_users: number
  pending_agencies: number
  active_agencies: number
  total_clients: number
  total_providers: number
  licenses_generated: number
  licenses_used: number
}

interface DashboardData {
  system_stats: SystemStats
  recent_users: any[]
  pending_approvals: any[]
}

const NavigatorDashboard: React.FC<NavigatorDashboardProps> = ({ user }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [systemHealth, setSystemHealth] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch navigator dashboard data
        const response = await apiClient.request('/navigator/dashboard')
        setDashboardData(response.data)

        // Fetch system health
        const healthResponse = await apiClient.request('/admin/system/health')
        setSystemHealth(healthResponse.data)
      } catch (error) {
        console.error('Error fetching navigator dashboard:', error)
        // Set mock data for development
        setDashboardData({
          system_stats: {
            total_users: 1247,
            pending_agencies: 8,
            active_agencies: 34,
            total_clients: 892,
            total_providers: 156,
            licenses_generated: 2156,
            licenses_used: 1834
          },
          recent_users: [
            {
              name: 'John Smith',
              email: 'john@techcorp.com',
              role: 'client',
              status: 'approved',
              created_at: '2024-01-16T10:00:00Z'
            },
            {
              name: 'Sarah Johnson',
              email: 'sarah@consulting.com',
              role: 'provider',
              status: 'approved',
              created_at: '2024-01-15T14:30:00Z'
            }
          ],
          pending_approvals: [
            {
              id: '1',
              name: 'Metro Business Solutions',
              email: 'admin@metrobiz.com',
              role: 'agency',
              company_name: 'Metro Business Solutions',
              created_at: '2024-01-14T09:00:00Z'
            },
            {
              id: '2',
              name: 'TechConsult Pro',
              email: 'info@techconsult.com',
              role: 'provider',
              company_name: 'TechConsult Pro',
              created_at: '2024-01-13T16:45:00Z'
            }
          ]
        })

        setSystemHealth({
          overall_status: 'healthy',
          health_score: 98,
          system_metrics: {
            uptime_seconds: 2856420,
            memory: {
              rss_mb: 245,
              heap_used_mb: 156,
              heap_total_mb: 201
            }
          },
          services: {
            database: { status: 'healthy', response_time_ms: 23 },
            redis: { status: 'not_configured' },
            email: { status: 'not_configured' },
            stripe: { status: 'configured' }
          }
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

  const stats = dashboardData?.system_stats
  const licenseUtilization = stats ? Math.round((stats.licenses_used / stats.licenses_generated) * 100) : 0

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome, Navigator {user.name}!
        </h1>
        <p className="text-lg text-gray-600">
          Monitor system health, manage user approvals, and oversee platform operations.
        </p>
      </div>

      {/* System Health Alert */}
      {systemHealth && systemHealth.overall_status !== 'healthy' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <h3 className="text-sm font-medium text-red-800">System Health Alert</h3>
          </div>
          <p className="text-sm text-red-700 mt-1">
            System health score: {systemHealth.health_score}%. Please review system status.
          </p>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={stats?.total_users?.toLocaleString() || '0'}
          change="+12 this week"
          changeType="increase"
          icon={Users}
          color="blue"
        />
        
        <StatCard
          title="Pending Approvals"
          value={stats?.pending_agencies || 0}
          icon={Clock}
          color={stats?.pending_agencies && stats.pending_agencies > 0 ? 'yellow' : 'green'}
        />
        
        <StatCard
          title="Active Agencies"
          value={stats?.active_agencies || 0}
          icon={Shield}
          color="green"
        />
        
        <StatCard
          title="License Utilization"
          value={`${licenseUtilization}%`}
          change={`${stats?.licenses_used || 0}/${stats?.licenses_generated || 0}`}
          changeType={licenseUtilization > 80 ? 'increase' : 'neutral'}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link 
            href="/dashboard/approvals" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
              <Shield className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Review Approvals</h3>
              <p className="text-sm text-gray-500">{stats?.pending_agencies || 0} pending</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/users" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">User Management</h3>
              <p className="text-sm text-gray-500">Manage all users</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/analytics" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <BarChart3 className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">System Analytics</h3>
              <p className="text-sm text-gray-500">View metrics</p>
            </div>
          </Link>

          <Link 
            href="/dashboard/audit" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
              <Settings className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Audit Logs</h3>
              <p className="text-sm text-gray-500">Review activity</p>
            </div>
          </Link>
        </div>
      </div>

      {/* System Health & Pending Approvals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* System Health */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">System Health</h2>
            <span className={`polaris-badge ${
              systemHealth?.overall_status === 'healthy' ? 'polaris-badge-success' :
              systemHealth?.overall_status === 'warning' ? 'polaris-badge-warning' :
              'polaris-badge-error'
            }`}>
              {systemHealth?.overall_status || 'Unknown'}
            </span>
          </div>

          {systemHealth && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Server className="h-5 w-5 text-gray-500 mr-3" />
                  <span className="text-sm font-medium text-gray-900">Server Uptime</span>
                </div>
                <span className="text-sm text-gray-600">
                  {Math.round(systemHealth.system_metrics.uptime_seconds / 86400)} days
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Database className="h-5 w-5 text-gray-500 mr-3" />
                  <span className="text-sm font-medium text-gray-900">Database</span>
                </div>
                <span className={`polaris-badge ${
                  systemHealth.services.database.status === 'healthy' ? 'polaris-badge-success' : 'polaris-badge-error'
                }`}>
                  {systemHealth.services.database.status}
                  {systemHealth.services.database.response_time_ms && (
                    <span className="ml-1">({systemHealth.services.database.response_time_ms}ms)</span>
                  )}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Activity className="h-5 w-5 text-gray-500 mr-3" />
                  <span className="text-sm font-medium text-gray-900">Memory Usage</span>
                </div>
                <span className="text-sm text-gray-600">
                  {systemHealth.system_metrics.memory.heap_used_mb}MB / {systemHealth.system_metrics.memory.heap_total_mb}MB
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <TrendingUp className="h-5 w-5 text-gray-500 mr-3" />
                  <span className="text-sm font-medium text-gray-900">Health Score</span>
                </div>
                <span className={`text-lg font-bold ${
                  systemHealth.health_score >= 95 ? 'text-green-600' :
                  systemHealth.health_score >= 80 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {systemHealth.health_score}%
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Pending Approvals */}
        <div className="polaris-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Pending Approvals</h2>
            <Link 
              href="/dashboard/approvals" 
              className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
            >
              View All
            </Link>
          </div>

          {dashboardData?.pending_approvals && dashboardData.pending_approvals.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.pending_approvals.slice(0, 4).map((approval) => (
                <div key={approval.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className={`h-10 w-10 rounded-lg flex items-center justify-center mr-3 ${
                      approval.role === 'agency' ? 'bg-yellow-100' :
                      approval.role === 'provider' ? 'bg-blue-100' :
                      'bg-gray-100'
                    }`}>
                      {approval.role === 'agency' ? (
                        <Shield className="h-5 w-5 text-yellow-600" />
                      ) : approval.role === 'provider' ? (
                        <Users className="h-5 w-5 text-blue-600" />
                      ) : (
                        <Users className="h-5 w-5 text-gray-600" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{approval.name}</h3>
                      <p className="text-sm text-gray-500">{approval.email}</p>
                      <p className="text-xs text-gray-400 capitalize">{approval.role}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">
                      {new Date(approval.created_at).toLocaleDateString()}
                    </p>
                    <Link
                      href={`/dashboard/approvals/${approval.id}`}
                      className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
                    >
                      Review
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">All Caught Up!</h3>
              <p className="text-gray-500">No pending approvals at this time</p>
            </div>
          )}
        </div>
      </div>

      {/* Platform Statistics */}
      <div className="polaris-card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Platform Statistics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="h-12 w-12 bg-blue-500 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Users className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-blue-600">{stats?.total_clients?.toLocaleString() || '0'}</h3>
            <p className="text-sm text-gray-600">Total Clients</p>
          </div>

          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="h-12 w-12 bg-green-500 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Users className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-green-600">{stats?.total_providers?.toLocaleString() || '0'}</h3>
            <p className="text-sm text-gray-600">Service Providers</p>
          </div>

          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="h-12 w-12 bg-purple-500 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-purple-600">{stats?.active_agencies?.toLocaleString() || '0'}</h3>
            <p className="text-sm text-gray-600">Active Agencies</p>
          </div>

          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="h-12 w-12 bg-yellow-500 rounded-lg flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-yellow-600">{licenseUtilization}%</h3>
            <p className="text-sm text-gray-600">License Utilization</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NavigatorDashboard