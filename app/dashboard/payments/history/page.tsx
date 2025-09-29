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
import { useAuth } from '../../providers'
import { apiClient } from '../../providers'
import LoadingSpinner from '../components/LoadingSpinner'

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
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment History</h1>
        <p className="text-lg text-gray-600">
          View and manage your payment transactions and purchase history.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        {transactions.length > 0 ? (
          <div className="space-y-4">
            {transactions.map((transaction) => (
              <div key={transaction.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{transaction.package_name}</h3>
                    <p className="text-sm text-gray-500">ID: {transaction.session_id}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">${transaction.amount}</p>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {transaction.payment_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Receipt className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Payment History</h3>
            <p className="text-gray-600">You haven't made any payments yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default PaymentHistoryPage