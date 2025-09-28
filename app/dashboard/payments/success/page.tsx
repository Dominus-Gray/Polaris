'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  CheckCircle, 
  Home,
  RefreshCw,
  AlertCircle,
  CreditCard,
  Calendar,
  Receipt,
  Download
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../../providers'

const PaymentSuccessPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  useEffect(() => {
    // Get session ID from URL on client side
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      setSessionId(urlParams.get('session_id'))
    }
  }, [])

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
              Confirmed
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <CreditCard className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Transaction</p>
                  <p className="font-medium text-gray-900">{sessionId ? `Session: ${sessionId.substring(0, 20)}...` : 'Processing...'}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Transaction Date</p>
                  <p className="font-medium text-gray-900">{new Date().toLocaleDateString()}</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Payment Status</p>
                  <p className="font-medium text-green-600">Successful</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Receipt className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Receipt</p>
                  <p className="font-medium text-gray-900">Available for download</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="polaris-card mb-8">
          <h2 className="polaris-heading-md mb-6">What's Next?</h2>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <h3 className="font-semibold text-gray-900 mb-2">Access Your Premium Features</h3>
              <p className="text-gray-600 text-sm mb-3">
                Your payment unlocks access to premium features and resources.
              </p>
              <Link 
                href="/dashboard/knowledge-base"
                className="polaris-button-primary text-sm inline-flex items-center"
              >
                Explore Knowledge Base
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>

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