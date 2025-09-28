'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Menu, 
  X, 
  Home, 
  ClipboardList, 
  Users, 
  BookOpen, 
  MessageSquare, 
  BarChart3, 
  Settings, 
  LogOut,
  Bell,
  Search,
  ChevronDown,
  Briefcase,
  CreditCard,
  Shield,
  Key
} from 'lucide-react'
import { useAuth } from '../../providers'

interface User {
  id: string
  email: string
  name: string
  role: string
  profile_image?: string
  company_name?: string
}

interface DashboardLayoutProps {
  children: React.ReactNode
  user: User
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, user }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false)
  const pathname = usePathname()
  const { logout } = useAuth()

  // Navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [
      { name: 'Dashboard', href: '/dashboard', icon: Home },
      { name: 'Profile', href: '/dashboard/profile', icon: Settings },
    ]

    switch (user.role) {
      case 'client':
        return [
          ...baseItems.slice(0, 1), // Dashboard
          { name: 'Assessments', href: '/dashboard/assessments', icon: ClipboardList },
          { name: 'Service Requests', href: '/dashboard/services', icon: Briefcase },
          { name: 'Knowledge Base', href: '/dashboard/knowledge-base', icon: BookOpen },
          { name: 'Messages', href: '/dashboard/messages', icon: MessageSquare },
          { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
          ...baseItems.slice(1), // Profile
        ]
      
      case 'provider':
        return [
          ...baseItems.slice(0, 1), // Dashboard
          { name: 'Opportunities', href: '/dashboard/opportunities', icon: Search },
          { name: 'My Services', href: '/dashboard/my-services', icon: Briefcase },
          { name: 'Messages', href: '/dashboard/messages', icon: MessageSquare },
          { name: 'Earnings', href: '/dashboard/earnings', icon: CreditCard },
          ...baseItems.slice(1), // Profile
        ]
      
      case 'agency':
        return [
          ...baseItems.slice(0, 1), // Dashboard
          { name: 'License Management', href: '/dashboard/licenses', icon: Key },
          { name: 'Clients', href: '/dashboard/clients', icon: Users },
          { name: 'Tier Configuration', href: '/dashboard/tiers', icon: Settings },
          { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
          { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
          ...baseItems.slice(1), // Profile
        ]
      
      case 'navigator':
      case 'admin':
        return [
          ...baseItems.slice(0, 1), // Dashboard
          { name: 'Agency Approvals', href: '/dashboard/approvals', icon: Shield },
          { name: 'User Management', href: '/dashboard/users', icon: Users },
          { name: 'System Analytics', href: '/dashboard/analytics', icon: BarChart3 },
          { name: 'Audit Logs', href: '/dashboard/audit', icon: ClipboardList },
          ...baseItems.slice(1), // Profile
        ]
      
      default:
        return baseItems
    }
  }

  const navigationItems = getNavigationItems()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="h-8 w-8 polaris-gradient rounded-lg flex items-center justify-center mr-3">
              <span className="text-white font-bold text-sm">P</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Polaris</h1>
              <p className="text-xs text-gray-500 capitalize">{user.role} Portal</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-polaris-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-white' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* User info at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-polaris-blue rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">
                {(user.name || user.email || 'U').charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user.name || user.email?.split('@')[0] || 'User'}
              </p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top navigation */}
        <div className="sticky top-0 z-40 bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-400 hover:text-gray-600"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div className="ml-4 lg:ml-0">
                <h1 className="text-2xl font-semibold text-gray-900">
                  {user.role === 'client' && 'Business Dashboard'}
                  {user.role === 'provider' && 'Provider Dashboard'}
                  {user.role === 'agency' && 'Agency Dashboard'}
                  {(user.role === 'navigator' || user.role === 'admin') && 'Navigator Dashboard'}
                </h1>
                <p className="text-sm text-gray-500">
                  Welcome back, {user.name}
                  {user.company_name && ` - ${user.company_name}`}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="text-gray-400 hover:text-gray-600 relative">
                <Bell className="h-6 w-6" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400"></span>
              </button>

              {/* Profile dropdown */}
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="flex items-center text-sm text-gray-700 hover:text-gray-900"
                >
                  <div className="h-8 w-8 bg-polaris-blue rounded-full flex items-center justify-center mr-2">
                    <span className="text-white font-medium text-sm">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <ChevronDown className="h-4 w-4" />
                </button>

                {profileDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                    <Link
                      href="/dashboard/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setProfileDropdownOpen(false)}
                    >
                      <Settings className="inline h-4 w-4 mr-2" />
                      Profile Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut className="inline h-4 w-4 mr-2" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-8 px-4 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default DashboardLayout