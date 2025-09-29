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
  Download,
  ArrowRight
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '../../providers'

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
    <div className="max-w-7xl mx-auto px-6 py-16">
      <div className="max-w-2xl mx-auto">
        {/* Success Message */}
        <div className="text-center mb-8">
          <div className="h-20 w-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-green-900 mb-3">Payment Successful!</h1>
          <p className="text-lg text-gray-600">
            Thank you for your purchase. Your payment has been processed successfully.
          </p>
        </div>

        {/* Payment Details */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Payment Details</h2>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
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
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">What's Next?</h2>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <h3 className="font-semibold text-gray-900 mb-2">Access Your Premium Features</h3>
              <p className="text-gray-600 text-sm mb-3">
                Your payment unlocks access to premium features and resources.
              </p>
              <Link 
                href="/dashboard/knowledge-base"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                Explore Knowledge Base
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/dashboard" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
            <Home className="mr-2 h-4 w-4" />
            Return to Dashboard
          </Link>
          
          <Link href="/dashboard/payments/history" className="inline-flex items-center px-6 py-3 bg-white text-gray-700 border border-gray-300 font-medium rounded-lg hover:bg-gray-50 transition-colors">
            <Receipt className="mr-2 h-4 w-4" />
            View Payment History
          </Link>
          
          <button className="inline-flex items-center px-6 py-3 text-gray-600 font-medium rounded-lg hover:bg-gray-100 transition-colors">
            <Download className="mr-2 h-4 w-4" />
            Download Receipt
          </button>
        </div>
      </div>
    </div>
  )
}

export default PaymentSuccessPage