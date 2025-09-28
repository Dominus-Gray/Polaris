'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { 
  CheckCircle, 
  ArrowRight,
  Download,
  Home,
  RefreshCw,
  AlertCircle,
  CreditCard,
  Calendar,
  Receipt
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

interface PaymentDetails {
  status: string
  payment_status: string
  amount_total: number
  currency: string
  package: {
    id: string
    name: string
  }
  processed: boolean
  metadata: any
}

const PaymentSuccessPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const searchParams = useSearchParams()
  const sessionId = searchParams?.get('session_id')
  
  const [paymentDetails, setPaymentDetails] = useState<PaymentDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [pollAttempts, setPollAttempts] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) {
      setError('No payment session found')
      setIsLoading(false)
      return
    }

    // Start polling for payment status
    pollPaymentStatus()
  }, [sessionId])

  const pollPaymentStatus = async (attempts = 0) => {
    const maxAttempts = 10
    const pollInterval = 2000 // 2 seconds

    if (attempts >= maxAttempts) {
      setError('Payment status check timed out. Please check your email for confirmation.')
      setIsLoading(false)
      return
    }

    try {
      const response = await apiClient.request(`/payments/checkout/status/${sessionId}`)
      
      if (response.data.payment_status === 'paid') {
        setPaymentDetails(response.data)
        setIsLoading(false)
        return
      } else if (response.data.status === 'expired') {
        setError('Payment session expired. Please try again.')
        setIsLoading(false)
        return
      }

      // Continue polling if payment is still pending
      setPollAttempts(attempts + 1)
      setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval)
      
    } catch (error) {
      console.error('Error checking payment status:', error)
      setError('Error checking payment status. Please try again.')
      setIsLoading(false)
    }
  }

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase()
    }).format(amount / 100) // Convert from cents
  }

  const getNextSteps = () => {
    if (!paymentDetails) return []
    
    const { package: pkg } = paymentDetails
    
    if (pkg.id.includes('knowledge_base')) {
      return [
        {
          title: 'Access Your Premium Resources',
          description: 'Browse the enhanced knowledge base with your new access level',
          action: 'Go to Knowledge Base',
          href: '/dashboard/knowledge-base'
        }
      ]
    }
    
    if (pkg.id.includes('assessment')) {
      return [
        {
          title: 'Take Advanced Assessments',
          description: 'Access higher tier assessments with detailed analytics',
          action: 'Start Assessment',
          href: '/dashboard/assessments'
        }
      ]
    }
    
    if (pkg.id.includes('service_request')) {
      return [
        {
          title: 'Create Service Requests',
          description: 'Submit professional service requests with your new credits',
          action: 'Request Services',
          href: '/dashboard/services'
        }
      ]
    }
    
    return [
      {
        title: 'Explore Your Dashboard',
        description: 'Discover all the new features available to you',
        action: 'Go to Dashboard',
        href: '/dashboard'
      }
    ]
  }

  if (isLoading) {
    return (
      <div className="polaris-container py-16">
        <div className="max-w-md mx-auto text-center">
          <div className="polaris-card">
            <div className="mb-6">
              <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <RefreshCw className="h-8 w-8 text-blue-600 animate-spin" />
              </div>
              <h1 className="polaris-heading-lg mb-2">Processing Payment</h1>
              <p className="polaris-body-sm text-gray-600">
                Please wait while we confirm your payment...
              </p>
              <div className="mt-4">
                <p className="text-sm text-gray-500">Attempt {pollAttempts + 1} of 10</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${((pollAttempts + 1) / 10) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="polaris-container py-16">
        <div className="max-w-md mx-auto text-center">
          <div className="polaris-card border-red-200">
            <div className="h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <h1 className="polaris-heading-lg mb-2 text-red-900">Payment Issue</h1>
            <p className="polaris-body-sm text-red-700 mb-6">{error}</p>
            
            <div className="flex flex-col space-y-3">
              <button
                onClick={() => {
                  setError(null)
                  setIsLoading(true)
                  setPollAttempts(0)
                  pollPaymentStatus()
                }}
                className="polaris-button-primary"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Check Again
              </button>
              
              <Link href="/dashboard" className="polaris-button-secondary">
                Return to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!paymentDetails) {
    return (
      <div className="polaris-container py-16">
        <div className="max-w-md mx-auto text-center">
          <div className="polaris-card">
            <AlertCircle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h1 className="polaris-heading-lg mb-2">Invalid Payment Session</h1>
            <p className="polaris-body-sm text-gray-600 mb-6">
              We couldn't find the payment session details.
            </p>
            <Link href="/dashboard" className="polaris-button-primary">
              Return to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const nextSteps = getNextSteps()

  return (
    <div className="polaris-container py-16">
      <div className="max-w-2xl mx-auto">
        {/* Success Message */}
        <div className="text-center mb-8">
          <div className="h-20 w-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 polaris-bounce-in">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="polaris-heading-xl mb-3 text-green-900">Payment Successful!</h1>
          <p className="polaris-body-lg text-gray-600">
            Thank you for your purchase. Your payment has been processed successfully.
          </p>
        </div>

        {/* Payment Details */}
        <div className="polaris-card mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="polaris-heading-md">Payment Details</h2>
            <span className="polaris-badge polaris-badge-success">
              {paymentDetails.processed ? 'Processed' : 'Confirmed'}
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <CreditCard className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Package</p>
                  <p className="font-medium text-gray-900">{paymentDetails.package.name}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Receipt className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Amount Paid</p>
                  <p className="font-medium text-gray-900">
                    {formatAmount(paymentDetails.amount_total, paymentDetails.currency)}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Transaction Date</p>
                  <p className="font-medium text-gray-900">{new Date().toLocaleDateString()}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Payment Status</p>
                  <p className="font-medium text-green-600 capitalize">{paymentDetails.payment_status}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        {nextSteps.length > 0 && (
          <div className="polaris-card mb-8">
            <h2 className="polaris-heading-md mb-6">What's Next?</h2>
            <div className="space-y-4">
              {nextSteps.map((step, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <h3 className="font-semibold text-gray-900 mb-2">{step.title}</h3>
                  <p className="text-gray-600 text-sm mb-3">{step.description}</p>
                  <Link 
                    href={step.href}
                    className="polaris-button-primary text-sm inline-flex items-center"
                  >
                    {step.action}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/dashboard" className="polaris-button-primary">
            <Home className="mr-2 h-4 w-4" />
            Return to Dashboard
          </Link>
          
          <Link href="/dashboard/payments/history" className="polaris-button-secondary">
            <Receipt className="mr-2 h-4 w-4" />
            View Payment History
          </Link>
          
          <button className="polaris-button-ghost">
            <Download className="mr-2 h-4 w-4" />
            Download Receipt
          </button>
        </div>
      </div>
    </div>
  )
}

export default PaymentSuccessPage