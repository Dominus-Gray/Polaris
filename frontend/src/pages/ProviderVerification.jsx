import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://agencydash.preview.emergentagent.com/api';

function ProviderVerification() {
  const navigate = useNavigate();
  const [verificationData, setVerificationData] = useState({
    business_license: null,
    insurance_certificate: null,
    tax_documents: null,
    professional_certifications: [],
    references: [
      { name: '', company: '', email: '', phone: '', project_description: '' },
      { name: '', company: '', email: '', phone: '', project_description: '' },
      { name: '', company: '', email: '', phone: '', project_description: '' }
    ],
    portfolio_items: [],
    specialty_areas: [],
    years_experience: '',
    annual_revenue: '',
    team_size: '',
    government_contracting_experience: false,
    security_clearance: '',
    bonding_capacity: ''
  });
  
  const [currentStep, setCurrentStep] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);

  const totalSteps = 5;

  useEffect(() => {
    loadExistingData();
  }, []);

  const loadExistingData = async () => {
    try {
      const response = await axios.get(`${API}/provider/verification/status`);
      if (response.data.verification_data) {
        setVerificationData(response.data.verification_data);
        setVerificationStatus(response.data.status);
      }
    } catch (error) {
      console.error('Error loading verification data:', error);
    }
  };

  const uploadDocument = async (file, documentType) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    try {
      const response = await axios.post(`${API}/provider/verification/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setVerificationData(prev => ({
        ...prev,
        [documentType]: response.data.file_url
      }));
      
      return response.data.file_url;
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error uploading document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const updateReference = (index, field, value) => {
    setVerificationData(prev => ({
      ...prev,
      references: prev.references.map((ref, i) => 
        i === index ? { ...ref, [field]: value } : ref
      )
    }));
  };

  const addPortfolioItem = (item) => {
    setVerificationData(prev => ({
      ...prev,
      portfolio_items: [...prev.portfolio_items, item]
    }));
  };

  const removePortfolioItem = (index) => {
    setVerificationData(prev => ({
      ...prev,
      portfolio_items: prev.portfolio_items.filter((_, i) => i !== index)
    }));
  };

  const submitVerification = async () => {
    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/provider/verification/submit`, verificationData);
      setVerificationStatus('pending');
      alert('Verification submitted successfully! We will review your application within 2-3 business days.');
      navigate('/provider/profile');
    } catch (error) {
      console.error('Error submitting verification:', error);
      alert('Error submitting verification. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getStepStatus = (step) => {
    if (step < currentStep) return 'completed';
    if (step === currentStep) return 'active';
    return 'pending';
  };

  const canProceedToNextStep = () => {
    switch (currentStep) {
      case 1:
        return verificationData.business_license && verificationData.insurance_certificate;
      case 2:
        return verificationData.references.every(ref => ref.name && ref.company && ref.email);
      case 3:
        return verificationData.portfolio_items.length >= 2;
      case 4:
        return verificationData.specialty_areas.length > 0 && verificationData.years_experience;
      case 5:
        return true;
      default:
        return false;
    }
  };

  if (verificationStatus === 'verified') {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✅</span>
          </div>
          <h2 className="text-2xl font-bold text-green-800 mb-2">Verification Complete!</h2>
          <p className="text-green-700 mb-6">
            Congratulations! Your provider account has been verified. You now have access to premium features 
            and enhanced visibility in the marketplace.
          </p>
          <div className="flex gap-4 justify-center">
            <button 
              className="btn btn-success"
              onClick={() => navigate('/provider/services')}
            >
              Manage Services
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/provider/profile')}
            >
              View Profile
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (verificationStatus === 'pending') {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">⏳</span>
          </div>
          <h2 className="text-2xl font-bold text-yellow-800 mb-2">Verification Under Review</h2>
          <p className="text-yellow-700 mb-6">
            Thank you for submitting your verification documents. Our team is currently reviewing your application. 
            You should hear back from us within 2-3 business days.
          </p>
          <button 
            className="btn btn-secondary"
            onClick={() => navigate('/provider/profile')}
          >
            Back to Profile
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-sm p-8 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Provider Verification</h1>
            <p className="text-blue-100">Build trust with clients through our comprehensive verification process</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold mb-2">Step {currentStep}</div>
            <div className="text-blue-200 text-sm">of {totalSteps}</div>
            <div className="w-32 bg-blue-800 rounded-full h-2 mt-2">
              <div 
                className="bg-white h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Progress Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Verification Steps</h3>
            <div className="space-y-4">
              {[
                { id: 1, title: 'Business Documents', icon: '📄' },
                { id: 2, title: 'Professional References', icon: '👥' },
                { id: 3, title: 'Portfolio & Experience', icon: '💼' },
                { id: 4, title: 'Expertise & Specialization', icon: '🎯' },
                { id: 5, title: 'Review & Submit', icon: '✅' }
              ].map(step => {
                const status = getStepStatus(step.id);
                return (
                  <div
                    key={step.id}
                    className={`p-3 rounded-lg transition-colors cursor-pointer ${
                      status === 'completed' ? 'bg-green-100 text-green-800' :
                      status === 'active' ? 'bg-blue-100 text-blue-800' :
                      'bg-slate-100 text-slate-600'
                    }`}
                    onClick={() => setCurrentStep(step.id)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{step.icon}</span>
                      <div>
                        <div className="font-medium text-sm">{step.title}</div>
                        <div className="text-xs capitalize">{status}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm p-8">
            {/* Step 1: Business Documents */}
            {currentStep === 1 && (
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Business Documents</h2>
                <p className="text-slate-600 mb-8">
                  Upload your business documents to verify your legitimacy and professional standing.
                </p>

                <div className="space-y-6">
                  {/* Business License */}
                  <div className="border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Business License *</h3>
                    <p className="text-sm text-slate-600 mb-4">
                      Upload your current business license or certificate of incorporation.
                    </p>
                    
                    {verificationData.business_license ? (
                      <div className="flex items-center gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <span className="text-green-600">✅</span>
                        <div>
                          <div className="font-medium text-green-800">Document Uploaded</div>
                          <div className="text-sm text-green-600">Business license verified</div>
                        </div>
                        <button 
                          className="btn btn-sm btn-secondary ml-auto"
                          onClick={() => setVerificationData(prev => ({ ...prev, business_license: null }))}
                        >
                          Replace
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
                        <div className="text-4xl mb-4">📄</div>
                        <p className="text-slate-600 mb-4">Drag and drop your business license here, or click to browse</p>
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={(e) => {
                            if (e.target.files[0]) {
                              uploadDocument(e.target.files[0], 'business_license');
                            }
                          }}
                          className="hidden"
                          id="business-license"
                        />
                        <label htmlFor="business-license" className="btn btn-primary">
                          {uploading ? 'Uploading...' : 'Upload Document'}
                        </label>
                      </div>
                    )}
                  </div>

                  {/* Insurance Certificate */}
                  <div className="border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Professional Liability Insurance *</h3>
                    <p className="text-sm text-slate-600 mb-4">
                      Upload your current professional liability insurance certificate.
                    </p>
                    
                    {verificationData.insurance_certificate ? (
                      <div className="flex items-center gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <span className="text-green-600">✅</span>
                        <div>
                          <div className="font-medium text-green-800">Document Uploaded</div>
                          <div className="text-sm text-green-600">Insurance certificate verified</div>
                        </div>
                        <button 
                          className="btn btn-sm btn-secondary ml-auto"
                          onClick={() => setVerificationData(prev => ({ ...prev, insurance_certificate: null }))}
                        >
                          Replace
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
                        <div className="text-4xl mb-4">🛡️</div>
                        <p className="text-slate-600 mb-4">Upload your insurance certificate</p>
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={(e) => {
                            if (e.target.files[0]) {
                              uploadDocument(e.target.files[0], 'insurance_certificate');
                            }
                          }}
                          className="hidden"
                          id="insurance-cert"
                        />
                        <label htmlFor="insurance-cert" className="btn btn-primary">
                          {uploading ? 'Uploading...' : 'Upload Certificate'}
                        </label>
                      </div>
                    )}
                  </div>

                  {/* Tax Documents (Optional) */}
                  <div className="border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Tax Documentation (Optional)</h3>
                    <p className="text-sm text-slate-600 mb-4">
                      Upload recent tax returns or financial statements to demonstrate business stability.
                    </p>
                    
                    {verificationData.tax_documents ? (
                      <div className="flex items-center gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <span className="text-green-600">✅</span>
                        <div>
                          <div className="font-medium text-green-800">Document Uploaded</div>
                          <div className="text-sm text-green-600">Tax documents verified</div>
                        </div>
                        <button 
                          className="btn btn-sm btn-secondary ml-auto"
                          onClick={() => setVerificationData(prev => ({ ...prev, tax_documents: null }))}
                        >
                          Replace
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
                        <div className="text-4xl mb-4">📊</div>
                        <p className="text-slate-600 mb-4">Upload tax returns or financial statements</p>
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={(e) => {
                            if (e.target.files[0]) {
                              uploadDocument(e.target.files[0], 'tax_documents');
                            }
                          }}
                          className="hidden"
                          id="tax-docs"
                        />
                        <label htmlFor="tax-docs" className="btn btn-secondary">
                          {uploading ? 'Uploading...' : 'Upload Documents'}
                        </label>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Professional References */}
            {currentStep === 2 && (
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Professional References</h2>
                <p className="text-slate-600 mb-8">
                  Provide three professional references who can vouch for your work quality and reliability.
                </p>

                <div className="space-y-6">
                  {verificationData.references.map((reference, index) => (
                    <div key={index} className="border rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-slate-900 mb-4">
                        Reference #{index + 1}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">
                            Contact Name *
                          </label>
                          <input
                            type="text"
                            className="w-full input"
                            placeholder="John Smith"
                            value={reference.name}
                            onChange={(e) => updateReference(index, 'name', e.target.value)}
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">
                            Company *
                          </label>
                          <input
                            type="text"
                            className="w-full input"
                            placeholder="ABC Corporation"
                            value={reference.company}
                            onChange={(e) => updateReference(index, 'company', e.target.value)}
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">
                            Email *
                          </label>
                          <input
                            type="email"
                            className="w-full input"
                            placeholder="john@company.com"
                            value={reference.email}
                            onChange={(e) => updateReference(index, 'email', e.target.value)}
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">
                            Phone
                          </label>
                          <input
                            type="tel"
                            className="w-full input"
                            placeholder="(555) 123-4567"
                            value={reference.phone}
                            onChange={(e) => updateReference(index, 'phone', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="mt-4">
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Project Description
                        </label>
                        <textarea
                          className="w-full input h-24 resize-none"
                          placeholder="Briefly describe the project you worked on with this client..."
                          value={reference.project_description}
                          onChange={(e) => updateReference(index, 'project_description', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Step 3: Portfolio & Experience */}
            {currentStep === 3 && (
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Portfolio & Experience</h2>
                <p className="text-slate-600 mb-8">
                  Showcase your best work and demonstrate your expertise to potential clients.
                </p>

                <PortfolioManager
                  portfolioItems={verificationData.portfolio_items}
                  onAdd={addPortfolioItem}
                  onRemove={removePortfolioItem}
                />
              </div>
            )}

            {/* Step 4: Expertise & Specialization */}
            {currentStep === 4 && (
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Expertise & Specialization</h2>
                <p className="text-slate-600 mb-8">
                  Tell us about your areas of expertise and professional background.
                </p>

                <ExpertiseForm
                  verificationData={verificationData}
                  setVerificationData={setVerificationData}
                />
              </div>
            )}

            {/* Step 5: Review & Submit */}
            {currentStep === 5 && (
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-6">Review & Submit</h2>
                <p className="text-slate-600 mb-8">
                  Review your verification information before submitting.
                </p>

                <VerificationSummary verificationData={verificationData} />
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between pt-8 mt-8 border-t">
              <button
                className="btn btn-secondary"
                onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                disabled={currentStep === 1}
              >
                Previous
              </button>

              <div className="flex gap-4">
                {currentStep < totalSteps ? (
                  <button
                    className="btn btn-primary"
                    onClick={() => setCurrentStep(currentStep + 1)}
                    disabled={!canProceedToNextStep()}
                  >
                    Next Step
                  </button>
                ) : (
                  <button
                    className="btn btn-success px-8"
                    onClick={submitVerification}
                    disabled={submitting || !canProceedToNextStep()}
                  >
                    {submitting ? 'Submitting...' : 'Submit for Review'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Portfolio Manager Component
function PortfolioManager({ portfolioItems, onAdd, onRemove }) {
  const [newItem, setNewItem] = useState({
    title: '',
    description: '',
    client: '',
    project_value: '',
    completion_date: '',
    outcomes: '',
    image_url: ''
  });

  const handleAdd = () => {
    if (newItem.title && newItem.description) {
      onAdd({ ...newItem, id: Date.now() });
      setNewItem({
        title: '',
        description: '',
        client: '',
        project_value: '',
        completion_date: '',
        outcomes: '',
        image_url: ''
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Add New Portfolio Item */}
      <div className="border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Add Portfolio Item</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Project Title *</label>
            <input
              type="text"
              className="w-full input"
              placeholder="Website Redesign Project"
              value={newItem.title}
              onChange={(e) => setNewItem(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Client Name</label>
            <input
              type="text"
              className="w-full input"
              placeholder="ABC Company (optional)"
              value={newItem.client}
              onChange={(e) => setNewItem(prev => ({ ...prev, client: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Project Value</label>
            <input
              type="text"
              className="w-full input"
              placeholder="$50,000"
              value={newItem.project_value}
              onChange={(e) => setNewItem(prev => ({ ...prev, project_value: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Completion Date</label>
            <input
              type="date"
              className="w-full input"
              value={newItem.completion_date}
              onChange={(e) => setNewItem(prev => ({ ...prev, completion_date: e.target.value }))}
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">Project Description *</label>
          <textarea
            className="w-full input h-24 resize-none"
            placeholder="Describe the project scope, your role, and key deliverables..."
            value={newItem.description}
            onChange={(e) => setNewItem(prev => ({ ...prev, description: e.target.value }))}
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">Outcomes & Results</label>
          <textarea
            className="w-full input h-20 resize-none"
            placeholder="What were the measurable outcomes and client benefits?"
            value={newItem.outcomes}
            onChange={(e) => setNewItem(prev => ({ ...prev, outcomes: e.target.value }))}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleAdd}
          disabled={!newItem.title || !newItem.description}
        >
          Add to Portfolio
        </button>
      </div>

      {/* Existing Portfolio Items */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">
          Portfolio Items ({portfolioItems.length})
        </h3>
        
        {portfolioItems.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-4">📁</div>
            <p>No portfolio items added yet. Add at least 2 items to proceed.</p>
          </div>
        )}

        {portfolioItems.map((item, index) => (
          <div key={item.id} className="border rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-semibold text-slate-900 mb-2">{item.title}</h4>
                <p className="text-sm text-slate-600 mb-2">{item.description}</p>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  {item.client && <span>Client: {item.client}</span>}
                  {item.project_value && <span>Value: {item.project_value}</span>}
                  {item.completion_date && <span>Completed: {new Date(item.completion_date).toLocaleDateString()}</span>}
                </div>
              </div>
              <button
                className="text-red-500 hover:text-red-700 ml-4"
                onClick={() => onRemove(index)}
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Expertise Form Component
function ExpertiseForm({ verificationData, setVerificationData }) {
  const [newSpecialty, setNewSpecialty] = useState('');

  const addSpecialty = () => {
    if (newSpecialty.trim() && !verificationData.specialty_areas.includes(newSpecialty.trim())) {
      setVerificationData(prev => ({
        ...prev,
        specialty_areas: [...prev.specialty_areas, newSpecialty.trim()]
      }));
      setNewSpecialty('');
    }
  };

  const removeSpecialty = (specialty) => {
    setVerificationData(prev => ({
      ...prev,
      specialty_areas: prev.specialty_areas.filter(s => s !== specialty)
    }));
  };

  return (
    <div className="space-y-6">
      {/* Specialty Areas */}
      <div className="border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Specialty Areas *</h3>
        
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            className="flex-1 input"
            placeholder="e.g., Business Formation, Financial Planning, Marketing Strategy"
            value={newSpecialty}
            onChange={(e) => setNewSpecialty(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addSpecialty()}
          />
          <button className="btn btn-primary" onClick={addSpecialty}>Add</button>
        </div>

        <div className="flex flex-wrap gap-2">
          {verificationData.specialty_areas.map((specialty, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {specialty}
              <button
                className="text-blue-600 hover:text-blue-800"
                onClick={() => removeSpecialty(specialty)}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Experience Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Years of Experience *</h3>
          <select
            className="w-full input"
            value={verificationData.years_experience}
            onChange={(e) => setVerificationData(prev => ({ ...prev, years_experience: e.target.value }))}
            required
          >
            <option value="">Select experience level</option>
            <option value="1-2">1-2 years</option>
            <option value="3-5">3-5 years</option>
            <option value="6-10">6-10 years</option>
            <option value="11-15">11-15 years</option>
            <option value="16+">16+ years</option>
          </select>
        </div>

        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Team Size</h3>
          <select
            className="w-full input"
            value={verificationData.team_size}
            onChange={(e) => setVerificationData(prev => ({ ...prev, team_size: e.target.value }))}
          >
            <option value="">Select team size</option>
            <option value="solo">Solo practitioner</option>
            <option value="2-5">2-5 employees</option>
            <option value="6-15">6-15 employees</option>
            <option value="16-50">16-50 employees</option>
            <option value="50+">50+ employees</option>
          </select>
        </div>
      </div>

      {/* Government Contracting Experience */}
      <div className="border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Government Contracting</h3>
        
        <div className="mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={verificationData.government_contracting_experience}
              onChange={(e) => setVerificationData(prev => ({ 
                ...prev, 
                government_contracting_experience: e.target.checked 
              }))}
            />
            <span className="text-slate-700">I have experience with government contracting</span>
          </label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Security Clearance</label>
            <select
              className="w-full input"
              value={verificationData.security_clearance}
              onChange={(e) => setVerificationData(prev => ({ ...prev, security_clearance: e.target.value }))}
            >
              <option value="">None</option>
              <option value="public_trust">Public Trust</option>
              <option value="secret">Secret</option>
              <option value="top_secret">Top Secret</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Bonding Capacity</label>
            <input
              type="text"
              className="w-full input"
              placeholder="e.g., $1M, $5M"
              value={verificationData.bonding_capacity}
              onChange={(e) => setVerificationData(prev => ({ ...prev, bonding_capacity: e.target.value }))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Verification Summary Component
function VerificationSummary({ verificationData }) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">✅ What happens next?</h3>
        <ul className="space-y-2 text-blue-800">
          <li>• Our verification team will review your documents within 2-3 business days</li>
          <li>• We may contact your references to verify your professional experience</li>
          <li>• You'll receive an email notification once verification is complete</li>
          <li>• Verified providers get enhanced visibility and premium features</li>
        </ul>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold text-slate-900 mb-3">Documents Submitted</h4>
          <ul className="space-y-2 text-sm">
            <li className={verificationData.business_license ? 'text-green-600' : 'text-slate-500'}>
              {verificationData.business_license ? '✅' : '❌'} Business License
            </li>
            <li className={verificationData.insurance_certificate ? 'text-green-600' : 'text-slate-500'}>
              {verificationData.insurance_certificate ? '✅' : '❌'} Insurance Certificate
            </li>
            <li className={verificationData.tax_documents ? 'text-green-600' : 'text-slate-500'}>
              {verificationData.tax_documents ? '✅' : '⚪'} Tax Documents (Optional)
            </li>
          </ul>
        </div>

        <div className="border rounded-lg p-4">
          <h4 className="font-semibold text-slate-900 mb-3">Professional Info</h4>
          <ul className="space-y-1 text-sm text-slate-600">
            <li>References: {verificationData.references.filter(r => r.name && r.email).length}/3</li>
            <li>Portfolio Items: {verificationData.portfolio_items.length}</li>
            <li>Specialties: {verificationData.specialty_areas.length}</li>
            <li>Experience: {verificationData.years_experience || 'Not specified'}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ProviderVerification;