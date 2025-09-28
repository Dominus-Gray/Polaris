'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  ArrowLeft,
  Briefcase,
  DollarSign,
  Clock,
  AlertCircle,
  CheckCircle,
  FileText
} from 'lucide-react'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

interface ServiceRequestForm {
  area_id: string
  title: string
  description: string
  budget_range: string
  timeline: string
  priority: 'low' | 'medium' | 'high'
  requirements: string
  location: string
}

const CreateServiceRequestPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  
  const [formData, setFormData] = useState<ServiceRequestForm>({
    area_id: '',
    title: '',
    description: '',
    budget_range: '',
    timeline: '',
    priority: 'medium',
    requirements: '',
    location: ''
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Partial<ServiceRequestForm>>({})

  const businessAreas = [
    { id: 'area1', name: 'Business Formation & Registration' },
    { id: 'area2', name: 'Financial Operations & Management' },
    { id: 'area3', name: 'Legal & Contracting Compliance' },
    { id: 'area4', name: 'Quality Management & Standards' },
    { id: 'area5', name: 'Technology & Security Infrastructure' },
    { id: 'area6', name: 'Human Resources & Capacity' },
    { id: 'area7', name: 'Performance Tracking & Reporting' },
    { id: 'area8', name: 'Risk Management & Business Continuity' },
    { id: 'area9', name: 'Supply Chain Management & Vendor Relations' },
    { id: 'area10', name: 'Competitive Advantage & Market Position' }
  ]

  const budgetRanges = [
    '$500 - $1,000',
    '$1,000 - $2,500',
    '$2,500 - $5,000',
    '$5,000 - $10,000',
    '$10,000 - $25,000',
    '$25,000+'
  ]

  const timelineOptions = [
    '1-2 weeks',
    '3-4 weeks',
    '1-2 months',
    '3-6 months',
    '6+ months'
  ]

  const handleInputChange = (field: keyof ServiceRequestForm, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<ServiceRequestForm> = {}

    if (!formData.area_id) newErrors.area_id = 'Business area is required'
    if (!formData.title.trim()) newErrors.title = 'Title is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    if (!formData.budget_range) newErrors.budget_range = 'Budget range is required'
    if (!formData.timeline) newErrors.timeline = 'Timeline is required'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsSubmitting(true)

    try {
      const response = await apiClient.request('/service-requests/professional-help', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          description: formData.description + (formData.requirements ? `\n\nSpecific Requirements:\n${formData.requirements}` : '')
        })
      })

      if (response.success) {
        router.push('/dashboard/services?tab=requests&created=true')
      } else {
        throw new Error('Failed to create service request')
      }
    } catch (error) {
      console.error('Error creating service request:', error)
      alert('Failed to create service request. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.back()}
          className="mb-4 flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Services
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Request Professional Services</h1>
        <p className="text-lg text-gray-600">
          Get expert help to improve your business processes and compliance.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Business Area */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Business Area <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.area_id}
                onChange={(e) => handleInputChange('area_id', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-polaris-blue focus:border-polaris-blue ${
                  errors.area_id ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Select a business area...</option>
                {businessAreas.map((area) => (
                  <option key={area.id} value={area.id}>{area.name}</option>
                ))}
              </select>
              {errors.area_id && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.area_id}
                </p>
              )}
            </div>

            {/* Title */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Brief description of what you need help with"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-polaris-blue focus:border-polaris-blue ${
                  errors.title ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.title}
                </p>
              )}
            </div>

            {/* Budget Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Budget Range <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.budget_range}
                onChange={(e) => handleInputChange('budget_range', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-polaris-blue focus:border-polaris-blue ${
                  errors.budget_range ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Select budget range...</option>
                {budgetRanges.map((range) => (
                  <option key={range} value={range}>{range}</option>
                ))}
              </select>
              {errors.budget_range && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.budget_range}
                </p>
              )}
            </div>

            {/* Timeline */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeline <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.timeline}
                onChange={(e) => handleInputChange('timeline', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-polaris-blue focus:border-polaris-blue ${
                  errors.timeline ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Select timeline...</option>
                {timelineOptions.map((timeline) => (
                  <option key={timeline} value={timeline}>{timeline}</option>
                ))}
              </select>
              {errors.timeline && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.timeline}
                </p>
              )}
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority Level
              </label>
              <select
                value={formData.priority}
                onChange={(e) => handleInputChange('priority', e.target.value as 'low' | 'medium' | 'high')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
              >
                <option value="low">Low - Not urgent</option>
                <option value="medium">Medium - Moderate urgency</option>
                <option value="high">High - Urgent</option>
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location/City
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                placeholder="City, State (optional)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
              />
            </div>
          </div>
        </div>

        {/* Detailed Description */}
        <div className="polaris-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Project Details</h2>
          
          <div className="space-y-6">
            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Detailed Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={5}
                placeholder="Provide a detailed description of what you need help with. Include background information, current challenges, and what you hope to achieve."
                className={`w-full px-3 py-2 border rounded-lg focus:ring-polaris-blue focus:border-polaris-blue ${
                  errors.description ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.description}
                </p>
              )}
            </div>

            {/* Requirements */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Specific Requirements (Optional)
              </label>
              <textarea
                value={formData.requirements}
                onChange={(e) => handleInputChange('requirements', e.target.value)}
                rows={4}
                placeholder="List any specific requirements, qualifications, certifications, or deliverables you need from the service provider."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
              />
            </div>
          </div>
        </div>

        {/* How it Works */}
        <div className="polaris-card bg-blue-50 border-blue-200">
          <div className="flex items-start">
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Briefcase className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">How Our Service Matching Works</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <div className="flex items-start">
                  <div className="h-5 w-5 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3 text-xs font-bold mt-0.5">1</div>
                  <p>We'll notify qualified service providers in your area about your request</p>
                </div>
                <div className="flex items-start">
                  <div className="h-5 w-5 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3 text-xs font-bold mt-0.5">2</div>
                  <p>Up to 5 providers will respond with their proposals and quotes</p>
                </div>
                <div className="flex items-start">
                  <div className="h-5 w-5 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3 text-xs font-bold mt-0.5">3</div>
                  <p>You'll review all responses and choose the best provider for your needs</p>
                </div>
                <div className="flex items-start">
                  <div className="h-5 w-5 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3 text-xs font-bold mt-0.5">4</div>
                  <p>Work directly with your chosen provider to complete the project</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={() => router.back()}
            className="polaris-button-secondary"
          >
            Cancel
          </button>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="polaris-button-primary inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ml-2">Creating Request...</span>
              </>
            ) : (
              <>
                <CheckCircle className="mr-2 h-5 w-5" />
                Create Service Request
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateServiceRequestPage