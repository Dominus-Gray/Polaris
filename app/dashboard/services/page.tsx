'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Search,
  Filter,
  Briefcase,
  Clock,
  DollarSign,
  MapPin,
  Star,
  ArrowRight,
  Plus,
  CheckCircle,
  AlertCircle,
  Eye,
  MessageSquare
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../providers'
import { apiClient } from '../../providers'
import LoadingSpinner from '../components/LoadingSpinner'

interface ServiceRequest {
  id: string
  title: string
  description: string
  area_id: string
  area_name: string
  budget_range: string
  timeline: string
  status: 'open' | 'matched' | 'in_progress' | 'completed'
  created_at: string
  provider_responses_count: number
  client_info?: {
    name: string
    company: string
  }
}

interface ActiveEngagement {
  id: string
  service_info: {
    title: string
    area_name: string
  }
  provider_info?: {
    name: string
    company: string
    rating: number
  }
  client_info?: {
    name: string
    company: string
  }
  status: 'pending' | 'in_progress' | 'delivered' | 'completed'
  agreed_fee: number
  timeline: string
  updated_at: string
}

const ServicesPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([])
  const [activeEngagements, setActiveEngagements] = useState<ActiveEngagement[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'requests' | 'engagements'>('requests')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterArea, setFilterArea] = useState('')

  useEffect(() => {
    fetchServicesData()
  }, [])

  const fetchServicesData = async () => {
    try {
      if (state.user?.role === 'client') {
        // Fetch client's service requests and engagements
        const [requestsResponse, engagementsResponse] = await Promise.all([
          apiClient.request('/service-requests/my-requests'),
          apiClient.request('/engagements/my-services')
        ])
        setServiceRequests(requestsResponse.data || [])
        setActiveEngagements(engagementsResponse.data || [])
      } else if (state.user?.role === 'provider') {
        // Fetch available opportunities and provider's engagements
        const [opportunitiesResponse, engagementsResponse] = await Promise.all([
          apiClient.request('/service-requests/opportunities'),
          apiClient.request('/provider/my-services')
        ])
        setServiceRequests(opportunitiesResponse.data || [])
        setActiveEngagements(engagementsResponse.data || [])
      }
    } catch (error) {
      console.error('Error fetching services data:', error)
      // Mock data for development
      if (state.user?.role === 'client') {
        setServiceRequests([
          {
            id: '1',
            title: 'Financial Operations Assessment Help',
            description: 'Need professional help to improve our financial management processes and compliance',
            area_id: 'area2',
            area_name: 'Financial Operations & Management',
            budget_range: '$1,000 - $2,500',
            timeline: '2-3 weeks',
            status: 'open',
            created_at: '2024-01-15T10:00:00Z',
            provider_responses_count: 3
          }
        ])
      } else if (state.user?.role === 'provider') {
        setServiceRequests([
          {
            id: '2',
            title: 'Technology Infrastructure Review',
            description: 'Small tech company needs cybersecurity assessment and infrastructure recommendations',
            area_id: 'area5',
            area_name: 'Technology & Security Infrastructure', 
            budget_range: '$2,500 - $5,000',
            timeline: '1 month',
            status: 'open',
            created_at: '2024-01-14T14:30:00Z',
            provider_responses_count: 1,
            client_info: {
              name: 'Tech Solutions Inc',
              company: 'Tech Solutions Inc'
            }
          }
        ])
      }
      setActiveEngagements([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateRequest = () => {
    // Navigate to create service request page
    router.push('/dashboard/services/create')
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'open': { color: 'polaris-badge-info', text: 'Open' },
      'matched': { color: 'polaris-badge-warning', text: 'Matched' },
      'in_progress': { color: 'polaris-badge-info', text: 'In Progress' },
      'delivered': { color: 'polaris-badge-warning', text: 'Delivered' },
      'completed': { color: 'polaris-badge-success', text: 'Completed' },
      'pending': { color: 'polaris-badge-warning', text: 'Pending' }
    }
    
    const config = statusConfig[status] || statusConfig['open']
    return <span className={`polaris-badge ${config.color} text-xs`}>{config.text}</span>
  }

  const filteredRequests = serviceRequests.filter(request => 
    request.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (filterArea === '' || request.area_id === filterArea)
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {state.user?.role === 'client' ? 'Professional Services' : 'Service Opportunities'}
            </h1>
            <p className="text-lg text-gray-600">
              {state.user?.role === 'client' 
                ? 'Request professional help and manage your service engagements'
                : 'Find service opportunities and manage your client engagements'
              }
            </p>
          </div>
          
          {state.user?.role === 'client' && (
            <button
              onClick={handleCreateRequest}
              className="polaris-button-primary inline-flex items-center"
            >
              <Plus className="mr-2 h-5 w-5" />
              Request Service
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('requests')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'requests'
                  ? 'border-polaris-blue text-polaris-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {state.user?.role === 'client' ? 'My Requests' : 'Available Opportunities'}
              <span className="ml-2 bg-gray-100 text-gray-900 rounded-full px-2 py-1 text-xs">
                {filteredRequests.length}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('engagements')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'engagements'
                  ? 'border-polaris-blue text-polaris-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Active Engagements
              <span className="ml-2 bg-gray-100 text-gray-900 rounded-full px-2 py-1 text-xs">
                {activeEngagements.length}
              </span>
            </button>
          </nav>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search services..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
            />
          </div>
          
          <select
            value={filterArea}
            onChange={(e) => setFilterArea(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
          >
            <option value="">All Areas</option>
            <option value="area1">Business Formation</option>
            <option value="area2">Financial Operations</option>
            <option value="area3">Legal & Contracting</option>
            <option value="area4">Quality Management</option>
            <option value="area5">Technology & Security</option>
            <option value="area6">Human Resources</option>
            <option value="area7">Performance Tracking</option>
            <option value="area8">Risk Management</option>
            <option value="area9">Supply Chain</option>
            <option value="area10">Competitive Advantage</option>
          </select>
        </div>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'requests' ? (
        /* Service Requests */
        <div className="space-y-6">
          {filteredRequests.length > 0 ? (
            filteredRequests.map((request) => (
              <div key={request.id} className="polaris-card hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{request.title}</h3>
                      {getStatusBadge(request.status)}
                    </div>
                    <p className="text-gray-600 mb-3">{request.description}</p>
                    
                    <div className="flex items-center flex-wrap gap-4 text-sm text-gray-500 mb-4">
                      <span className="flex items-center">
                        <Briefcase className="h-4 w-4 mr-1" />
                        {request.area_name}
                      </span>
                      <span className="flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        {request.budget_range}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {request.timeline}
                      </span>
                      {request.client_info && (
                        <span className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {request.client_info.company}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-500">
                    Posted {new Date(request.created_at).toLocaleDateString()}
                    {request.provider_responses_count > 0 && (
                      <span className="ml-2">• {request.provider_responses_count} responses</span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3">
                    {state.user?.role === 'provider' && request.status === 'open' && (
                      <Link
                        href={`/dashboard/services/opportunities/${request.id}`}
                        className="polaris-button-primary text-sm inline-flex items-center"
                      >
                        <Eye className="mr-1 h-4 w-4" />
                        View & Respond
                      </Link>
                    )}
                    
                    {state.user?.role === 'client' && (
                      <>
                        <Link
                          href={`/dashboard/services/requests/${request.id}`}
                          className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
                        >
                          <Eye className="mr-1 h-4 w-4" />
                          View Details
                        </Link>
                        
                        {request.provider_responses_count > 0 && (
                          <Link
                            href={`/dashboard/services/requests/${request.id}/responses`}
                            className="polaris-button-primary text-sm inline-flex items-center"
                          >
                            <MessageSquare className="mr-1 h-4 w-4" />
                            View Responses ({request.provider_responses_count})
                          </Link>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <div className="h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Briefcase className="h-12 w-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {state.user?.role === 'client' ? 'No Service Requests Yet' : 'No Opportunities Available'}
              </h3>
              <p className="text-gray-600 mb-6">
                {state.user?.role === 'client' 
                  ? 'Create your first service request to get professional help with your business needs.'
                  : 'Check back later for new service opportunities that match your expertise.'
                }
              </p>
              {state.user?.role === 'client' && (
                <button
                  onClick={handleCreateRequest}
                  className="polaris-button-primary inline-flex items-center"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Service Request
                </button>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Active Engagements */
        <div className="space-y-6">
          {activeEngagements.length > 0 ? (
            activeEngagements.map((engagement) => (
              <div key={engagement.id} className="polaris-card hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{engagement.service_info.title}</h3>
                      {getStatusBadge(engagement.status)}
                    </div>
                    
                    <div className="flex items-center flex-wrap gap-4 text-sm text-gray-500 mb-4">
                      <span className="flex items-center">
                        <Briefcase className="h-4 w-4 mr-1" />
                        {engagement.service_info.area_name}
                      </span>
                      
                      {state.user?.role === 'client' && engagement.provider_info && (
                        <>
                          <span className="flex items-center">
                            <MapPin className="h-4 w-4 mr-1" />
                            {engagement.provider_info.company}
                          </span>
                          <span className="flex items-center">
                            <Star className="h-4 w-4 mr-1 text-yellow-500" />
                            {engagement.provider_info.rating}/5
                          </span>
                        </>
                      )}
                      
                      {state.user?.role === 'provider' && engagement.client_info && (
                        <span className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {engagement.client_info.company}
                        </span>
                      )}
                      
                      <span className="flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        ${engagement.agreed_fee.toLocaleString()}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {engagement.timeline}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-500">
                    Last updated {new Date(engagement.updated_at).toLocaleDateString()}
                  </div>

                  <div className="flex items-center space-x-3">
                    <Link
                      href={`/dashboard/services/engagements/${engagement.id}`}
                      className="text-polaris-blue hover:text-polaris-navy font-medium text-sm flex items-center"
                    >
                      <Eye className="mr-1 h-4 w-4" />
                      View Details
                    </Link>
                    
                    <Link
                      href={`/dashboard/services/engagements/${engagement.id}/chat`}
                      className="polaris-button-primary text-sm inline-flex items-center"
                    >
                      <MessageSquare className="mr-1 h-4 w-4" />
                      Chat
                    </Link>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <div className="h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-12 w-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Active Engagements</h3>
              <p className="text-gray-600 mb-6">
                {state.user?.role === 'client' 
                  ? 'Once you hire a provider, your active engagements will appear here.'
                  : 'When you win service opportunities, your active client engagements will appear here.'
                }
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ServicesPage