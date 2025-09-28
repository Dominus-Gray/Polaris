'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Receipt,
  Download,
  RefreshCw,
  Filter,
  Search,
  Calendar,
  DollarSign,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle
} from 'lucide-react'
import { useAuth } from '../../../providers'
import { apiClient } from '../../../providers'
import LoadingSpinner from '../../components/LoadingSpinner'

interface PaymentTransaction {
  id: string
  session_id: string
  package_id: string
  package_name: string
  amount: number
  currency: string
  payment_status: string
  status: string
  processed: boolean
  created_at: string
  updated_at: string
}

interface PaginationInfo {
  current_page: number
  per_page: number
  total_items: number
  total_pages: number
}

const PaymentHistoryPage = () => {
  const { state } = useAuth()
  const [transactions, setTransactions] = useState<PaymentTransaction[]>([])
  const [pagination, setPagination] = useState<PaginationInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    fetchPaymentHistory()
  }, [currentPage])

  const fetchPaymentHistory = async () => {
    try {
      const response = await apiClient.request(`/payments/history?page=${currentPage}&limit=10`)
      setTransactions(response.data.transactions || [])
      setPagination(response.data.pagination)
    } catch (error) {
      console.error('Error fetching payment history:', error)
      // Mock data for development
      setTransactions([
        {
          id: '1',
          session_id: 'cs_test_123456',
          package_id: 'knowledge_base_premium',
          package_name: 'Knowledge Base Premium Access',
          amount: 49.99,
          currency: 'usd',
          payment_status: 'paid',
          status: 'complete',
          processed: true,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:05:00Z'
        },
        {
          id: '2',
          session_id: 'cs_test_789012',
          package_id: 'service_request_medium',
          package_name: 'Medium Service Request',
          amount: 299.99,
          currency: 'usd',
          payment_status: 'paid',
          status: 'complete',
          processed: true,
          created_at: '2024-01-12T14:30:00Z',
          updated_at: '2024-01-12T14:35:00Z'
        },
        {
          id: '3',
          session_id: 'cs_test_345678',
          package_id: 'assessment_tier_upgrade',
          package_name: 'Assessment Tier Upgrade',
          amount: 29.99,
          currency: 'usd',
          payment_status: 'processing',
          status: 'pending',
          processed: false,
          created_at: '2024-01-10T09:15:00Z',
          updated_at: '2024-01-10T09:15:00Z'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string, paymentStatus: string) => {
    if (paymentStatus === 'paid' && status === 'complete') {
      return <CheckCircle className="h-5 w-5 text-green-600" />
    }
    if (paymentStatus === 'processing' || status === 'pending') {
      return <Clock className="h-5 w-5 text-yellow-600" />
    }
    if (paymentStatus === 'failed' || status === 'failed') {
      return <XCircle className="h-5 w-5 text-red-600" />
    }
    return <AlertTriangle className="h-5 w-5 text-gray-600" />
  }

  const getStatusText = (status: string, paymentStatus: string) => {
    if (paymentStatus === 'paid' && status === 'complete') return 'Completed'
    if (paymentStatus === 'processing' || status === 'pending') return 'Processing'
    if (paymentStatus === 'failed' || status === 'failed') return 'Failed'
    return 'Unknown'
  }

  const getStatusBadgeClass = (status: string, paymentStatus: string) => {
    if (paymentStatus === 'paid' && status === 'complete') return 'polaris-badge-success'
    if (paymentStatus === 'processing' || status === 'pending') return 'polaris-badge-warning'
    if (paymentStatus === 'failed' || status === 'failed') return 'polaris-badge-danger'
    return 'polaris-badge-neutral'
  }

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase()
    }).format(amount)
  }

  const filteredTransactions = transactions.filter(transaction =>
    transaction.package_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (statusFilter === '' || transaction.payment_status === statusFilter)
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="polaris-container py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="polaris-heading-xl mb-2">Payment History</h1>
            <p className="polaris-body text-gray-600">
              View and manage your payment transactions and purchase history.
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button 
              onClick={fetchPaymentHistory}
              className="polaris-button-secondary"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </button>
            
            <button className="polaris-button-primary">
              <Download className="mr-2 h-4 w-4" />
              Export All
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="polaris-card mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
              />
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-polaris-blue focus:border-polaris-blue"
            >
              <option value="">All Status</option>
              <option value="paid">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          
          <div className="text-sm text-gray-600">
            {filteredTransactions.length} of {transactions.length} transactions
          </div>
        </div>
      </div>

      {/* Payment History Table */}
      <div className="polaris-card">
        {filteredTransactions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Service/Package</th>
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Amount</th>
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Status</th>
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Date</th>
                  <th className="text-right py-4 px-4 font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div>
                        <p className="font-medium text-gray-900">{transaction.package_name}</p>
                        <p className="text-sm text-gray-500">ID: {transaction.session_id.substring(0, 20)}...</p>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="font-medium text-gray-900">
                        {formatAmount(transaction.amount, transaction.currency)}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        {getStatusIcon(transaction.status, transaction.payment_status)}
                        <span className={`ml-2 polaris-badge ${getStatusBadgeClass(transaction.status, transaction.payment_status)} text-xs`}>
                          {getStatusText(transaction.status, transaction.payment_status)}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div>
                        <p className="text-gray-900">{new Date(transaction.created_at).toLocaleDateString()}</p>
                        <p className="text-sm text-gray-500">{new Date(transaction.created_at).toLocaleTimeString()}</p>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button className="text-polaris-blue hover:text-polaris-navy font-medium text-sm">
                          <Receipt className="h-4 w-4 mr-1 inline" />
                          Receipt
                        </button>
                        
                        {transaction.payment_status === 'paid' && (
                          <button className="text-gray-600 hover:text-gray-900 font-medium text-sm">
                            <Download className="h-4 w-4 mr-1 inline" />
                            Download
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Receipt className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Payment History</h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || statusFilter 
                ? 'No transactions match your current search criteria.'
                : 'You haven\'t made any payments yet. Explore our services to get started.'
              }
            </p>
            <div className="flex items-center justify-center space-x-4">
              {(searchTerm || statusFilter) ? (
                <button
                  onClick={() => {
                    setSearchTerm('')
                    setStatusFilter('')
                  }}
                  className="polaris-button-secondary"
                >
                  Clear Filters
                </button>
              ) : (
                <>
                  <Link href="/dashboard/services" className="polaris-button-primary">
                    Browse Services
                  </Link>
                  <Link href="/dashboard/knowledge-base" className="polaris-button-secondary">
                    Explore Knowledge Base
                  </Link>
                </>
              )}
            </div>
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-between pt-6 border-t border-gray-200 mt-6">
            <div className="text-sm text-gray-600">
              Showing {((pagination.current_page - 1) * pagination.per_page) + 1} to {Math.min(pagination.current_page * pagination.per_page, pagination.total_items)} of {pagination.total_items} transactions
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={pagination.current_page === 1}
                className="polaris-button-ghost disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              <span className="px-3 py-1 bg-polaris-blue text-white rounded-lg text-sm font-medium">
                {pagination.current_page}
              </span>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, pagination.total_pages))}
                disabled={pagination.current_page === pagination.total_pages}
                className="polaris-button-ghost disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PaymentHistoryPage