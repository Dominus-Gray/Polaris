'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Target, 
  TrendingUp,
  Briefcase, 
  BookOpen, 
  CheckCircle, 
  Clock,
  ArrowRight,
  Star,
  Zap,
  BarChart3,
  MessageSquare,
  Award,
  Sparkles,
  Activity,
  Calendar,
  Users
} from 'lucide-react'
import { useAuth } from '../../providers'

interface User {
  id: string
  name: string
  email: string
  role: string
  company_name?: string
}

interface EnhancedClientDashboardProps {
  user: User
}

const EnhancedClientDashboard: React.FC<EnhancedClientDashboardProps> = ({ user }) => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Mock data for enhanced dashboard
  const dashboardData = {
    readiness_score: 72,
    areas_completed: 3,
    total_areas: 10,
    active_services: 2,
    recent_activity: [
      {
        id: '1',
        title: 'Financial Assessment Completed',
        description: 'Scored 85% with 3 improvement areas identified',
        timestamp: '2 hours ago',
        type: 'assessment',
        status: 'completed'
      },
      {
        id: '2',
        title: 'Service Provider Matched',
        description: 'Sarah Johnson accepted your technology infrastructure request',
        timestamp: '5 hours ago',
        type: 'service',
        status: 'active'
      },
      {
        id: '3',
        title: 'Knowledge Base Access',
        description: 'Downloaded 3 compliance templates',
        timestamp: '1 day ago',
        type: 'resource',
        status: 'completed'
      }
    ],
    upcoming_deadlines: [
      {
        title: 'Quality Management Assessment',
        due_date: '2025-01-05',
        priority: 'high'
      },
      {
        title: 'Provider Meeting - Tech Review',
        due_date: '2025-01-03',
        priority: 'medium'
      }
    ]
  }

  const getGreeting = () => {
    const hour = currentTime.getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'assessment': return <Target className="h-5 w-5 text-blue-600" />
      case 'service': return <Users className="h-5 w-5 text-green-600" />
      case 'resource': return <BookOpen className="h-5 w-5 text-purple-600" />
      default: return <Activity className="h-5 w-5 text-gray-600" />
    }
  }

  return (
    <div className="space-y-8 p-6">
      {/* ===== ENHANCED WELCOME SECTION ===== */}
      <div className="polaris-card-premium polaris-fade-in-up">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {getGreeting()}, {user.name}! 
              </h1>
              <Sparkles className="ml-3 h-6 w-6 text-yellow-500 polaris-pulse-premium" />
            </div>
            <p className="text-lg text-gray-600">
              {user.company_name && `Managing ${user.company_name}'s`} business assessment and compliance journey
            </p>
            <div className="flex items-center mt-3 text-sm text-gray-500">
              <Calendar className="h-4 w-4 mr-2" />
              {currentTime.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>
          
          <div className="hidden md:block">
            <div className="polaris-score-circle polaris-pulse-premium">
              {dashboardData.readiness_score}%
            </div>
            <p className="text-center text-sm text-gray-600 mt-2">Readiness</p>
          </div>
        </div>
      </div>

      {/* ===== ENHANCED KEY METRICS ===== */}
      <div className="polaris-dashboard-grid">
        <div className="polaris-stat-card-premium polaris-hover-lift-premium group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2 font-semibold tracking-wide">OVERALL READINESS</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">{dashboardData.readiness_score}%</p>
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600 font-medium">+12% this month</span>
              </div>
            </div>
            <div className="h-14 w-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Target className="h-7 w-7 text-white" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card-premium polaris-hover-lift-premium group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2 font-semibold tracking-wide">AREAS COMPLETED</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">
                {dashboardData.areas_completed}
                <span className="text-lg text-gray-500">/{dashboardData.total_areas}</span>
              </p>
              <div className="flex items-center">
                <span className="text-sm text-blue-600 font-medium">
                  {Math.round((dashboardData.areas_completed / dashboardData.total_areas) * 100)}% complete
                </span>
              </div>
            </div>
            <div className="h-14 w-14 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <CheckCircle className="h-7 w-7 text-white" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card-premium polaris-hover-lift-premium group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2 font-semibold tracking-wide">ACTIVE SERVICES</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">{dashboardData.active_services}</p>
              <div className="flex items-center">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <span className="text-sm text-gray-600 font-medium">4.8 avg rating</span>
              </div>
            </div>
            <div className="h-14 w-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Briefcase className="h-7 w-7 text-white" />
            </div>
          </div>
        </div>

        <div className="polaris-stat-card-premium polaris-hover-lift-premium group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2 font-semibold tracking-wide">AI INSIGHTS</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">24</p>
              <div className="flex items-center">
                <Zap className="h-4 w-4 text-blue-500 mr-1" />
                <span className="text-sm text-blue-600 font-medium">Available now</span>
              </div>
            </div>
            <div className="h-14 w-14 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Sparkles className="h-7 w-7 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* ===== ENHANCED QUICK ACTIONS ===== */}
      <div className="polaris-card-premium">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
          <div className="polaris-badge-premium">
            Priority Tasks
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link 
            href="/dashboard/assessments" 
            className="polaris-assessment-card polaris-hover-glow polaris-click-feedback"
          >
            <div className="flex items-center mb-4">
              <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <Target className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900">Start Assessment</h3>
                <p className="text-sm text-gray-600">Begin or continue assessments</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="polaris-tier-badge">Tier 1 Ready</span>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
            </div>
          </Link>

          <Link 
            href="/dashboard/services" 
            className="polaris-service-card polaris-hover-glow polaris-click-feedback"
          >
            <div className="flex items-center mb-4">
              <div className="h-12 w-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-xl flex items-center justify-center mr-4">
                <Users className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900">Request Services</h3>
                <p className="text-sm text-gray-600">Get professional help</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="polaris-badge polaris-badge-success text-xs">5 Providers Available</span>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
            </div>
          </Link>

          <Link 
            href="/dashboard/knowledge-base" 
            className="polaris-card-interactive polaris-hover-glow polaris-click-feedback"
          >
            <div className="flex items-center mb-4">
              <div className="h-12 w-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mr-4">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900">Knowledge Base</h3>
                <p className="text-sm text-gray-600">Access resources & AI guidance</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="polaris-badge polaris-badge-glow bg-gradient-to-r from-purple-500 to-pink-600 text-white">AI Powered</span>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" />
            </div>
          </Link>
        </div>
      </div>

      {/* ===== ENHANCED PROGRESS & ACTIVITY ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Enhanced Progress Overview */}
        <div className="polaris-dashboard-section polaris-slide-in-right">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Assessment Progress</h2>
            <Link 
              href="/dashboard/assessments" 
              className="text-blue-600 hover:text-purple-600 font-semibold text-sm transition-colors"
            >
              View All →
            </Link>
          </div>

          <div className="space-y-4">
            {/* Enhanced Progress Bars */}
            <div className="polaris-assessment-card">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">Business Formation</h3>
                <div className="polaris-score-circle bg-gradient-to-br from-green-500 to-blue-600 w-12 h-12 text-sm">
                  85%
                </div>
              </div>
              <div className="polaris-progress-premium">
                <div className="polaris-progress-fill-animated" style={{ width: '85%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">Completed • Last updated 2 days ago</p>
            </div>

            <div className="polaris-assessment-card">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">Financial Operations</h3>
                <div className="polaris-score-circle bg-gradient-to-br from-yellow-500 to-orange-600 w-12 h-12 text-sm">
                  60%
                </div>
              </div>
              <div className="polaris-progress-premium">
                <div className="polaris-progress-fill-animated" style={{ width: '60%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">In Progress • 2 items remaining</p>
            </div>

            <div className="polaris-assessment-card">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">Technology & Security</h3>
                <div className="polaris-score-circle bg-gradient-to-br from-red-500 to-pink-600 w-12 h-12 text-sm">
                  25%
                </div>
              </div>
              <div className="polaris-progress-premium">
                <div className="polaris-progress-fill-animated" style={{ width: '25%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">Needs Attention • Professional help recommended</p>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <Link 
              href="/dashboard/assessments" 
              className="polaris-button-premium w-full justify-center group"
            >
              <Target className="mr-2 h-5 w-5" />
              Continue Assessment Journey
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>

        {/* Enhanced Recent Activity */}
        <div className="polaris-dashboard-section polaris-slide-in-right" style={{animationDelay: '0.2s'}}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
            <span className="polaris-badge-glow bg-gradient-to-r from-blue-500 to-purple-600 text-white">
              Live Updates
            </span>
          </div>
          
          <div className="space-y-4">
            {dashboardData.recent_activity.map((activity, index) => (
              <div 
                key={activity.id} 
                className="polaris-card-interactive polaris-hover-glow"
                style={{animationDelay: `${index * 0.1}s`}}
              >
                <div className="flex items-start space-x-4">
                  <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                    {getActivityIcon(activity.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 mb-1">{activity.title}</h3>
                    <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{activity.timestamp}</span>
                      <span className={`polaris-badge text-xs ${
                        activity.status === 'completed' ? 'polaris-badge-success' : 'polaris-badge-info'
                      }`}>
                        {activity.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 text-center">
            <Link 
              href="/dashboard/analytics" 
              className="text-blue-600 hover:text-purple-600 font-semibold text-sm transition-colors"
            >
              View Full Activity Timeline →
            </Link>
          </div>
        </div>
      </div>

      {/* ===== ENHANCED UPCOMING DEADLINES ===== */}
      <div className="polaris-card-premium polaris-scale-in">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Upcoming Deadlines</h2>
          <Award className="h-6 w-6 text-yellow-500 polaris-pulse-premium" />
        </div>
        
        <div className="space-y-4">
          {dashboardData.upcoming_deadlines.map((deadline, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
              <div className="flex items-center">
                <div className={`h-3 w-3 rounded-full mr-3 ${
                  deadline.priority === 'high' ? 'bg-red-500 polaris-pulse-premium' : 'bg-yellow-500'
                }`}></div>
                <div>
                  <h3 className="font-semibold text-gray-900">{deadline.title}</h3>
                  <p className="text-sm text-gray-600">Due: {new Date(deadline.due_date).toLocaleDateString()}</p>
                </div>
              </div>
              <span className={`polaris-badge text-xs ${
                deadline.priority === 'high' ? 'polaris-badge-danger' : 'polaris-badge-warning'
              }`}>
                {deadline.priority} priority
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ===== ENHANCED AI ASSISTANT PREVIEW ===== */}
      <div className="polaris-card-premium bg-gradient-to-br from-blue-600 via-purple-600 to-blue-700 text-white">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div className="h-12 w-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mr-4">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold">AI Assistant Ready</h2>
              <p className="text-blue-200">Get instant answers to your business questions</p>
            </div>
          </div>
          <Sparkles className="h-8 w-8 text-yellow-300 polaris-pulse-premium" />
        </div>
        
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-6">
          <p className="text-blue-100 text-sm italic">
            "How can I improve my technology security compliance score?"
          </p>
        </div>
        
        <Link 
          href="/dashboard/knowledge-base" 
          className="polaris-button-glass w-full justify-center group"
        >
          <MessageSquare className="mr-2 h-5 w-5" />
          Ask AI Assistant
          <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>
    </div>
  )
}

export default EnhancedClientDashboard