import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polar-docs-ai.preview.emergentagent.com';

function NavigatorEvidenceReview() {
  const [pendingEvidence, setPendingEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [reviewData, setReviewData] = useState({
    review_status: '',
    review_comments: '',
    follow_up_required: false
  });
  const [submitLoading, setSubmitLoading] = useState(false);

  // Authentication header
  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('polaris_token')}`
    }
  };

  useEffect(() => {
    loadPendingEvidence();
  }, []);

  const loadPendingEvidence = async () => {
    try {
      const response = await axios.get(`${API}/api/navigator/evidence/pending`, authHeaders);
      setPendingEvidence(response.data.pending_evidence || []);
    } catch (error) {
      console.error('Error loading pending evidence:', error);
      alert('Failed to load pending evidence');
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSubmit = async (evidenceId) => {
    if (!reviewData.review_status) {
      alert('Please select a review status');
      return;
    }

    setSubmitLoading(true);
    try {
      await axios.post(
        `${API}/api/navigator/evidence/${evidenceId}/review`,
        reviewData,
        authHeaders
      );
      
      alert('Review submitted successfully');
      setSelectedEvidence(null);
      setReviewData({
        review_status: '',
        review_comments: '',
        follow_up_required: false
      });
      
      // Reload the list
      loadPendingEvidence();
      
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review');
    } finally {
      setSubmitLoading(false);
    }
  };

  const downloadFile = (evidenceId, fileName) => {
    const downloadUrl = `${API}/api/navigator/evidence/${evidenceId}/files/${fileName}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_blank';
    link.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading evidence submissions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Evidence Review Dashboard</h1>
          <p className="text-gray-600">Review assessment evidence submissions from clients</p>
        </div>

        {pendingEvidence.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-gray-500 mb-4">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Evidence</h3>
            <p className="text-gray-600">All evidence submissions have been reviewed.</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {pendingEvidence.map((evidence) => (
              <div key={evidence.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {evidence.user_email}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>Business Area: {evidence.business_area}</span>
                        <span>Tier Level: {evidence.tier_level}</span>
                        <span>Question: {evidence.question_id}</span>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <div>Uploaded: {new Date(evidence.uploaded_at).toLocaleDateString()}</div>
                      <div>{evidence.files?.length || 0} files</div>
                    </div>
                  </div>

                  {evidence.evidence_description && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-1">Evidence Description:</h4>
                      <p className="text-gray-700 text-sm">{evidence.evidence_description}</p>
                    </div>
                  )}

                  {evidence.files && evidence.files.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Uploaded Files:</h4>
                      <div className="space-y-2">
                        {evidence.files.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="flex items-center gap-2">
                              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              <span className="text-sm font-medium">{file.original_name}</span>
                              <span className="text-xs text-gray-500">
                                ({Math.round(file.file_size / 1024)} KB)
                              </span>
                            </div>
                            <button
                              onClick={() => downloadFile(evidence.id, file.stored_name)}
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                              Download
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        setSelectedEvidence(evidence);
                        setReviewData({
                          review_status: '',
                          review_comments: '',
                          follow_up_required: false
                        });
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Review Evidence
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Review Modal */}
        {selectedEvidence && (
          <div className="fixed inset-0 bg-primary bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Review Evidence - {selectedEvidence.user_email}
                  </h3>
                  <button
                    onClick={() => setSelectedEvidence(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Review Decision
                    </label>
                    <select
                      value={reviewData.review_status}
                      onChange={(e) => setReviewData(prev => ({ ...prev, review_status: e.target.value }))}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select review decision</option>
                      <option value="approved">Approved - Evidence is sufficient</option>
                      <option value="rejected">Rejected - Evidence is insufficient</option>
                      <option value="needs_clarification">Needs Clarification - Request more information</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Review Comments
                    </label>
                    <textarea
                      rows={4}
                      value={reviewData.review_comments}
                      onChange={(e) => setReviewData(prev => ({ ...prev, review_comments: e.target.value }))}
                      placeholder="Provide feedback on the evidence submission..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="follow_up_required"
                      checked={reviewData.follow_up_required}
                      onChange={(e) => setReviewData(prev => ({ ...prev, follow_up_required: e.target.checked }))}
                      className="mr-2"
                    />
                    <label htmlFor="follow_up_required" className="text-sm text-gray-700">
                      Follow-up meeting required
                    </label>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={() => handleReviewSubmit(selectedEvidence.id)}
                      disabled={submitLoading || !reviewData.review_status}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {submitLoading ? 'Submitting...' : 'Submit Review'}
                    </button>
                    <button
                      onClick={() => setSelectedEvidence(null)}
                      className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default NavigatorEvidenceReview;