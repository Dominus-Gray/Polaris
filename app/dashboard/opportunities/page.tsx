'use client'

import React, { useState, useEffect } from 'react'
import { 
  Search,
  Filter,
  MapPin,
  Star,
  Clock,
  DollarSign,
  Send,
  Eye,
  Building,
  Award
} from 'lucide-react'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

interface ServiceOpportunity {
  id: string
  title: string
  description: string
  area_name: string
  budget_range: string
  timeline: string
  client_company: string
  location: string
  posted_date: string
  responses_count: number
  max_responses: number
}

const OperationalProviderOpportunitiesPage = () => {
  const { state } = useAuth()
  const [opportunities, setOpportunities] = useState<ServiceOpportunity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchOpportunities()
  }, [])

  const fetchOpportunities = async () => {
    try {
      const response = await apiClient.request('/service-requests/opportunities')
      setOpportunities(response.data || [])
    } catch (error) {
      console.error('Error fetching opportunities:', error)
      // Operational fallback data
      setOpportunities([
        {
          id: 'opp_001',
          title: 'Financial Operations Assessment',
          description: 'Small tech company needs financial operations review and cash flow management improvements.',
          area_name: 'Financial Operations & Management',
          budget_range: '$2,500 - $5,000',
          timeline: '4-6 weeks',
          client_company: 'Tech Solutions Inc',
          location: 'Austin, TX',
          posted_date: '2025-01-28T09:00:00Z',
          responses_count: 2,
          max_responses: 5
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <div className="flex items-center justify-center py-12"><LoadingSpinner size="lg" /></div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Service Opportunities</h1>
        <p className="text-lg text-gray-600">
          Find procurement readiness service opportunities from local businesses.
        </p>
      </div>

      <div className="space-y-6">
        {opportunities.map((opportunity) => (
          <div key={opportunity.id} className="polaris-card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{opportunity.title}</h3>
                <p className="text-gray-700 mb-4">{opportunity.description}</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Building className="h-4 w-4 mr-2" />
                    {opportunity.client_company}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    {opportunity.location}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <DollarSign className="h-4 w-4 mr-2" />
                    {opportunity.budget_range}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    {opportunity.timeline}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-500">
                Posted {new Date(opportunity.posted_date).toLocaleDateString()} • 
                {opportunity.responses_count}/{opportunity.max_responses} responses
              </div>
              
              <button className="polaris-button-primary text-sm inline-flex items-center">
                <Send className="mr-1 h-4 w-4" />
                Submit Proposal
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default OperationalProviderOpportunitiesPage