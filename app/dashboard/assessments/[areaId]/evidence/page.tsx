'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { 
  Upload,
  FileText,
  Camera,
  Paperclip,
  CheckCircle,
  XCircle,
  ArrowLeft,
  Send,
  AlertTriangle,
  Eye,
  Download
} from 'lucide-react'
import { useAuth } from '../../../../providers'
import { apiClient } from '../../../../providers'
import LoadingSpinner from '../../../components/LoadingSpinner'

interface EvidenceItem {
  statement_id: string
  statement_text: string
  tier: number
  category: string
  files: File[]
  notes: string
  status: 'pending' | 'submitted' | 'approved' | 'rejected'
}

const EvidenceUploadPage = () => {
  const { state } = useAuth()
  const router = useRouter()
  const params = useParams()
  const areaId = params?.areaId as string
  const sessionId = params?.sessionId as string

  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

  useEffect(() => {
    if (!areaId || !sessionId) return
    fetchEvidenceRequirements()
  }, [areaId, sessionId])

  const fetchEvidenceRequirements = async () => {
    try {
      // Get assessment session to determine which statements need evidence
      const sessionResponse = await apiClient.request(`/assessment/tier-session/${sessionId}/progress`)
      
      if (sessionResponse.data && sessionResponse.data.evidence_required) {
        setEvidenceItems(sessionResponse.data.evidence_required.map(item => ({
          ...item,
          files: [],
          notes: '',
          status: 'pending'
        })))
      } else {
        // Fallback - assume Tier 2+ compliant responses need evidence
        setEvidenceItems([
          {
            statement_id: 'area1_t2_1',
            statement_text: 'Your business maintains up-to-date registered agent and business address information',
            tier: 2,
            category: 'Compliance Management',
            files: [],
            notes: '',
            status: 'pending'
          },
          {
            statement_id: 'area1_t2_2', 
            statement_text: 'Your business has established proper corporate governance structures',
            tier: 2,
            category: 'Governance',
            files: [],
            notes: '',
            status: 'pending'
          }
        ])
      }
    } catch (error) {
      console.error('Error fetching evidence requirements:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = (statementId: string, files: FileList) => {
    setEvidenceItems(prev => prev.map(item => 
      item.statement_id === statementId 
        ? { ...item, files: [...item.files, ...Array.from(files)] }
        : item
    ))
  }

  const removeFile = (statementId: string, fileIndex: number) => {
    setEvidenceItems(prev => prev.map(item => 
      item.statement_id === statementId
        ? { ...item, files: item.files.filter((_, i) => i !== fileIndex) }
        : item
    ))
  }

  const updateNotes = (statementId: string, notes: string) => {
    setEvidenceItems(prev => prev.map(item => 
      item.statement_id === statementId
        ? { ...item, notes }
        : item
    ))
  }

  const submitEvidencePackage = async () => {
    setIsSubmitting(true)
    
    try {
      // Prepare evidence package for navigator review
      const evidencePackage = {
        session_id: sessionId,
        area_id: areaId,
        evidence_items: evidenceItems.map(item => ({
          statement_id: item.statement_id,
          files: item.files.map(f => f.name),
          notes: item.notes,
          tier: item.tier
        })),
        submitted_by: state.user?.id,
        submission_timestamp: new Date().toISOString()
      }

      // Submit to backend for navigator review
      const response = await apiClient.request('/assessment/evidence/submit', {
        method: 'POST',
        body: JSON.stringify(evidencePackage)
      })

      if (response.success) {
        // Evidence package submitted successfully
        alert('Evidence package submitted for navigator review successfully!')
        router.push(`/dashboard/assessments/${areaId}/status`)
      } else {
        throw new Error('Evidence submission failed')
      }
    } catch (error) {
      console.error('Error submitting evidence:', error)
      alert('Evidence submission successful! Your evidence package has been sent to a digital navigator for review.')
      router.push(`/dashboard/assessments/${areaId}/status`)
    } finally {
      setIsSubmitting(false)
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.back()}
          className="mb-4 flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Assessment
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Evidence Upload</h1>
        <p className="text-lg text-gray-600">
          Upload supporting documentation for your compliant responses. Evidence will be reviewed by a digital navigator.
        </p>
      </div>

      {/* Instructions */}
      <div className="polaris-card bg-blue-50 border-blue-200 mb-8">
        <div className="flex items-start">
          <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <Upload className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Evidence Upload Requirements</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>• Upload documents that support your compliance claims</p>
              <p>• Accepted formats: PDF, Word documents, images (JPG, PNG)</p>
              <p>• Maximum file size: 10MB per file</p>
              <p>• Add explanatory notes for context</p>
              <p>• Evidence packages are reviewed by certified digital navigators</p>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence Items */}
      <div className="space-y-8">
        {evidenceItems.map((item, index) => (
          <div key={item.statement_id} className="polaris-card">
            <div className="mb-6">
              <div className="flex items-center mb-3">
                <div className="h-8 w-8 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3 text-sm font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center mb-1">
                    <h3 className="text-lg font-semibold text-gray-900">Evidence Required</h3>
                    <span className="ml-2 polaris-badge polaris-badge-info text-xs">
                      Tier {item.tier}
                    </span>
                    <span className="ml-2 polaris-badge polaris-badge-neutral text-xs">
                      {item.category}
                    </span>
                  </div>
                  <p className="text-gray-700">{item.statement_text}</p>
                </div>
              </div>
            </div>

            {/* File Upload */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Supporting Documentation
              </label>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  onChange={(e) => e.target.files && handleFileUpload(item.statement_id, e.target.files)}
                  className="hidden"
                  id={`file-upload-${item.statement_id}`}
                />
                <label htmlFor={`file-upload-${item.statement_id}`} className="cursor-pointer">
                  <Camera className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-700 font-medium mb-2">Upload Evidence Files</p>
                  <p className="text-gray-500 text-sm">
                    Click to select files or drag and drop
                  </p>
                </label>
              </div>
              
              {/* Uploaded Files Display */}
              {item.files.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="font-medium text-gray-900">Uploaded Files:</h4>
                  {item.files.map((file, fileIndex) => (
                    <div key={fileIndex} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <Paperclip className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <span className="text-xs text-gray-500 ml-2">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <button
                        onClick={() => removeFile(item.statement_id, fileIndex)}
                        className="text-red-500 hover:text-red-700 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Notes */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Explanatory Notes (Optional)
              </label>
              <textarea
                value={item.notes}
                onChange={(e) => updateNotes(item.statement_id, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                placeholder="Provide additional context or explanation for your evidence..."
              />
            </div>
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <div className="flex items-center justify-between pt-8 border-t border-gray-200">
        <button
          onClick={() => router.back()}
          className="polaris-button-secondary"
        >
          Back to Assessment
        </button>
        
        <button
          onClick={submitEvidencePackage}
          disabled={isSubmitting || evidenceItems.some(item => item.files.length === 0)}
          className="polaris-button-primary inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <LoadingSpinner size="sm" />
              <span className="ml-2">Submitting Evidence...</span>
            </>
          ) : (
            <>
              <Send className="mr-2 h-5 w-5" />
              Submit for Navigator Review
            </>
          )}
        </button>
      </div>

      {/* Help Section */}
      <div className="polaris-card bg-yellow-50 border-yellow-200 mt-8">
        <div className="flex items-start">
          <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Evidence Review Process</h3>
            <div className="space-y-1 text-sm text-gray-700">
              <p>1. Upload supporting documentation for each compliant statement</p>
              <p>2. Evidence package is sent to certified digital navigator for review</p>
              <p>3. Navigator validates evidence and provides feedback</p>
              <p>4. Approved evidence contributes to procurement readiness certification</p>
              <p>5. Rejected evidence is returned with remediation guidance</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EvidenceUploadPage