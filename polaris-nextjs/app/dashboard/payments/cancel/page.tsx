'use client'

import React from 'react'
import { 
  XCircle, 
  ArrowLeft,
  Home,
  CreditCard,
  HelpCircle
} from 'lucide-react'
import Link from 'next/link'

const PaymentCancelPage = () => {
  return (
    <div className="polaris-container py-16">
      <div className="max-w-2xl mx-auto text-center">
        {/* Cancel Message */}
        <div className="h-20 w-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="h-12 w-12 text-yellow-600" />
        </div>
        
        <h1 className="polaris-heading-xl mb-3 text-gray-900">Payment Cancelled</h1>
        <p className="polaris-body-lg text-gray-600 mb-8">
          Your payment was cancelled and no charges were made to your account.
        </p>

        {/* Information Card */}
        <div className="polaris-card text-left mb-8">
          <div className="flex items-start">
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <HelpCircle className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">Need Help?</h3>
              <p className="text-gray-600 text-sm mb-4">
                If you experienced any issues during checkout or have questions about our services, 
                we're here to help. You can contact our support team or try the payment process again.
              </p>
              <div className="flex items-center space-x-4">
                <Link 
                  href="/dashboard/support" 
                  className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
                >
                  Contact Support →
                </Link>
                <Link 
                  href="/dashboard/services" 
                  className="text-polaris-blue hover:text-polaris-navy font-medium text-sm"
                >
                  Browse Services →
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => window.history.back()}
            className="polaris-button-primary"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Try Payment Again
          </button>
          
          <Link href="/dashboard" className="polaris-button-secondary">
            <Home className="mr-2 h-4 w-4" />
            Return to Dashboard
          </Link>
          
          <Link href="/dashboard/services" className="polaris-button-ghost">
            <CreditCard className="mr-2 h-4 w-4" />
            Browse Other Services
          </Link>
        </div>

        {/* Alternative Options */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alternative Options</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link 
              href="/dashboard/knowledge-base"
              className="polaris-card hover:shadow-md transition-shadow text-left"
            >
              <div className="flex items-center mb-3">
                <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                  <HelpCircle className="h-4 w-4 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900">Free Resources</h4>
              </div>
              <p className="text-sm text-gray-600">
                Access our free knowledge base articles and basic templates.
              </p>
            </Link>
            
            <Link 
              href="/dashboard/assessments"
              className="polaris-card hover:shadow-md transition-shadow text-left"
            >
              <div className="flex items-center mb-3">
                <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  <CreditCard className="h-4 w-4 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900">Free Assessments</h4>
              </div>
              <p className="text-sm text-gray-600">
                Take our basic tier assessments to identify improvement areas.
              </p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaymentCancelPage