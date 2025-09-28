'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../providers'
import ClientDashboard from './components/ClientDashboard'
import ProviderDashboard from './components/ProviderDashboard'
import AgencyDashboard from './components/AgencyDashboard'
import NavigatorDashboard from './components/NavigatorDashboard'
import DashboardLayout from './components/DashboardLayout'
import LoadingSpinner from './components/LoadingSpinner'

const DashboardPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!state.isLoading) {
      if (!state.isAuthenticated) {
        router.push('/auth/login')
      } else {
        setIsLoading(false)
      }
    }
  }, [state.isLoading, state.isAuthenticated, router])

  if (isLoading || state.isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (!state.user) {
    return null
  }

  const renderDashboard = () => {
    switch (state.user.role) {
      case 'client':
        return <ClientDashboard user={state.user} />
      case 'provider':
        return <ProviderDashboard user={state.user} />
      case 'agency':
        return <AgencyDashboard user={state.user} />
      case 'navigator':
      case 'admin':
        return <NavigatorDashboard user={state.user} />
      default:
        return (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Unknown Role</h2>
            <p className="text-gray-600">Your account role is not recognized. Please contact support.</p>
          </div>
        )
    }
  }

  return (
    <DashboardLayout user={state.user}>
      {renderDashboard()}
    </DashboardLayout>
  )
}

export default DashboardPage