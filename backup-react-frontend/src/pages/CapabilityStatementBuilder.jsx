import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://polaris-migrate.preview.emergentagent.com/api';

function CapabilityStatementBuilder() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [assessmentData, setAssessmentData] = useState(null);
  const [capabilityData, setCapabilityData] = useState({
    company_overview: '',
    core_competencies: [],
    past_performance: [],
    differentiators: [],
    certifications: [],
    contract_vehicles: '',
    naics_codes: [],
    socioeconomic_status: [],
    contact_information: {
      company_name: '',
      address: '',
      phone: '',
      email: '',
      website: '',
      duns_number: '',
      cage_code: ''
    }
  });
  const [activeTab, setActiveTab] = useState('overview');
  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      // Load assessment data to auto-populate capability statement
      const [assessmentRes, profileRes] = await Promise.all([
        axios.get(`${API}/assessment/latest`),
        axios.get(`${API}/auth/me`)
      ]);

      setAssessmentData(assessmentRes.data);
      
      // Pre-populate with existing data
      if (profileRes.data.business_profile) {
        setCapabilityData(prev => ({
          ...prev,
          contact_information: {
            ...prev.contact_information,
            company_name: profileRes.data.business_profile.company_name || '',
            address: profileRes.data.business_profile.registered_address || '',
            phone: profileRes.data.business_profile.contact_phone || '',
            email: profileRes.data.business_profile.contact_email || '',
            website: profileRes.data.business_profile.website_url || ''
          }
        }));
      }
      
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAIContent = async (section) => {
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/tools/capability-statement/generate`, {
        section,
        assessment_data: assessmentData,
        company_info: capabilityData.contact_information
      });
      
      if (section === 'company_overview') {
        setCapabilityData(prev => ({
          ...prev,
          company_overview: response.data.content
        }));
      } else if (section === 'core_competencies') {
        setCapabilityData(prev => ({
          ...prev,
          core_competencies: response.data.competencies || []
        }));
      } else if (section === 'differentiators') {
        setCapabilityData(prev => ({
          ...prev,
          differentiators: response.data.differentiators || []
        }));
      }
      
    } catch (error) {
      console.error('Error generating AI content:', error);
    } finally {
      setGenerating(false);
    }
  };

  const addItem = (section, item) => {
    if (item.trim()) {
      setCapabilityData(prev => ({
        ...prev,
        [section]: [...prev[section], item.trim()]
      }));
    }
  };

  const removeItem = (section, index) => {
    setCapabilityData(prev => ({
      ...prev,
      [section]: prev[section].filter((_, i) => i !== index)
    }));
  };

  const updateContactInfo = (field, value) => {
    setCapabilityData(prev => ({
      ...prev,
      contact_information: {
        ...prev.contact_information,
        [field]: value
      }
    }));
  };

  const saveCapabilityStatement = async () => {
    try {
      await axios.post(`${API}/tools/capability-statement/save`, capabilityData);
      // Show success message or redirect
      alert('Capability statement saved successfully!');
    } catch (error) {
      console.error('Error saving capability statement:', error);
      alert('Error saving capability statement. Please try again.');
    }
  };

  const exportToPDF = async () => {
    try {
      const response = await axios.post(`${API}/tools/capability-statement/export`, capabilityData, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `${capabilityData.contact_information.company_name || 'capability-statement'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting to PDF:', error);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-6xl">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/2 mb-6"></div>
          <div className="h-96 bg-slate-200 rounded-lg"></div>
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
            <h1 className="text-3xl font-bold mb-2">Capability Statement Builder</h1>
            <p className="text-blue-100">Create a professional capability statement powered by your assessment results</p>
          </div>
          <div className="flex gap-3">
            <button 
              className={`btn ${previewMode ? 'btn-secondary' : 'btn-primary'}`}
              onClick={() => setPreviewMode(!previewMode)}
            >
              {previewMode ? 'Edit Mode' : 'Preview'}
            </button>
            {!previewMode && (
              <button 
                className="btn btn-success"
                onClick={exportToPDF}
                disabled={!capabilityData.company_overview}
              >
                Export PDF
              </button>
            )}
          </div>
        </div>
      </div>

      {previewMode ? (
        /* Preview Mode */
        <div className="bg-white rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
          <div className="text-center border-b pb-6 mb-6">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              {capabilityData.contact_information.company_name || 'Company Name'}
            </h1>
            <div className="text-slate-600 space-y-1">
              <div>{capabilityData.contact_information.address}</div>
              <div>{capabilityData.contact_information.phone} • {capabilityData.contact_information.email}</div>
              <div>{capabilityData.contact_information.website}</div>
              {capabilityData.contact_information.duns_number && (
                <div>DUNS: {capabilityData.contact_information.duns_number} • CAGE: {capabilityData.contact_information.cage_code}</div>
              )}
            </div>
          </div>

          {capabilityData.company_overview && (
            <div className="mb-6">
              <h2 className="text-xl font-bold text-slate-900 mb-3 text-center">Company Overview</h2>
              <p className="text-slate-700 leading-relaxed text-justify">
                {capabilityData.company_overview}
              </p>
            </div>
          )}

          {capabilityData.core_competencies.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-bold text-slate-900 mb-3 text-center">Core Competencies</h2>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {capabilityData.core_competencies.map((competency, index) => (
                  <li key={index} className="flex items-center gap-2 text-slate-700">
                    <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                    {competency}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {capabilityData.past_performance.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-bold text-slate-900 mb-3 text-center">Past Performance</h2>
              <ul className="space-y-2">
                {capabilityData.past_performance.map((performance, index) => (
                  <li key={index} className="text-slate-700">• {performance}</li>
                ))}
              </ul>
            </div>
          )}

          {capabilityData.differentiators.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-bold text-slate-900 mb-3 text-center">Differentiators</h2>
              <ul className="space-y-2">
                {capabilityData.differentiators.map((diff, index) => (
                  <li key={index} className="text-slate-700">• {diff}</li>
                ))}
              </ul>
            </div>
          )}

          {(capabilityData.certifications.length > 0 || capabilityData.socioeconomic_status.length > 0) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {capabilityData.certifications.length > 0 && (
                <div>
                  <h3 className="font-bold text-slate-900 mb-2">Certifications</h3>
                  <ul className="space-y-1">
                    {capabilityData.certifications.map((cert, index) => (
                      <li key={index} className="text-sm text-slate-700">• {cert}</li>
                    ))}
                  </ul>
                </div>
              )}

              {capabilityData.socioeconomic_status.length > 0 && (
                <div>
                  <h3 className="font-bold text-slate-900 mb-2">Socioeconomic Status</h3>
                  <ul className="space-y-1">
                    {capabilityData.socioeconomic_status.map((status, index) => (
                      <li key={index} className="text-sm text-slate-700">• {status}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {capabilityData.naics_codes.length > 0 && (
            <div className="text-center">
              <h3 className="font-bold text-slate-900 mb-2">NAICS Codes</h3>
              <p className="text-sm text-slate-700">{capabilityData.naics_codes.join(', ')}</p>
            </div>
          )}
        </div>
      ) : (
        /* Edit Mode */
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4 sticky top-6">
              <h3 className="font-semibold text-slate-900 mb-4">Sections</h3>
              <nav className="space-y-1">
                {[
                  { id: 'overview', label: 'Company Overview', icon: '🏢' },
                  { id: 'competencies', label: 'Core Competencies', icon: '🎯' },
                  { id: 'performance', label: 'Past Performance', icon: '📈' },
                  { id: 'differentiators', label: 'Differentiators', icon: '⭐' },
                  { id: 'certifications', label: 'Certifications', icon: '🏆' },
                  { id: 'contact', label: 'Contact Info', icon: '📞' }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      activeTab === tab.id 
                        ? 'bg-blue-100 text-blue-700 font-medium' 
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </nav>

              <div className="mt-6 pt-4 border-t">
                <button 
                  className="w-full btn btn-primary btn-sm"
                  onClick={saveCapabilityStatement}
                >
                  Save Progress
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm p-6">
              {/* Company Overview Tab */}
              {activeTab === 'overview' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">Company Overview</h2>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => generateAIContent('company_overview')}
                      disabled={generating}
                    >
                      {generating ? 'Generating...' : '🤖 AI Generate'}
                    </button>
                  </div>
                  
                  <textarea
                    className="w-full h-40 p-4 border rounded-lg resize-none"
                    placeholder="Describe your company's mission, history, and overall capabilities. This should be a compelling summary that showcases your organization's strengths and experience."
                    value={capabilityData.company_overview}
                    onChange={(e) => setCapabilityData(prev => ({ ...prev, company_overview: e.target.value }))}
                  />
                  
                  <div className="mt-4 text-sm text-slate-600">
                    <p className="mb-2"><strong>Tips for a strong company overview:</strong></p>
                    <ul className="space-y-1 text-xs">
                      <li>• Keep it concise (150-250 words)</li>
                      <li>• Highlight your company's unique value proposition</li>
                      <li>• Include years of experience and key accomplishments</li>
                      <li>• Mention your target markets or customer base</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Core Competencies Tab */}
              {activeTab === 'competencies' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">Core Competencies</h2>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => generateAIContent('core_competencies')}
                      disabled={generating}
                    >
                      {generating ? 'Generating...' : '🤖 AI Generate'}
                    </button>
                  </div>

                  <AddItemInput 
                    placeholder="Add a core competency (e.g., Project Management, Financial Analysis)"
                    onAdd={(item) => addItem('core_competencies', item)}
                  />

                  <div className="mt-4 space-y-2">
                    {capabilityData.core_competencies.map((competency, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-slate-900">{competency}</span>
                        <button 
                          className="text-red-500 hover:text-red-700"
                          onClick={() => removeItem('core_competencies', index)}
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 text-sm text-slate-600">
                    <p className="mb-2"><strong>Based on your assessment results:</strong></p>
                    <div className="text-xs space-y-1">
                      {assessmentData?.strengths?.slice(0, 3).map((strength, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <button 
                            className="text-blue-600 hover:underline"
                            onClick={() => addItem('core_competencies', strength)}
                          >
                            + Add "{strength}"
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Past Performance Tab */}
              {activeTab === 'performance' && (
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 mb-6">Past Performance</h2>

                  <AddItemInput 
                    placeholder="Add a past performance example (e.g., Managed $2M project for Fortune 500 client)"
                    onAdd={(item) => addItem('past_performance', item)}
                  />

                  <div className="mt-4 space-y-2">
                    {capabilityData.past_performance.map((performance, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-slate-900">{performance}</span>
                        <button 
                          className="text-red-500 hover:text-red-700"
                          onClick={() => removeItem('past_performance', index)}
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 text-sm text-slate-600">
                    <p className="mb-2"><strong>Include specific examples with:</strong></p>
                    <ul className="space-y-1 text-xs">
                      <li>• Project scope and dollar value</li>
                      <li>• Client name (if permissible)</li>
                      <li>• Timeline and deliverables</li>
                      <li>• Quantifiable results achieved</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Differentiators Tab */}
              {activeTab === 'differentiators' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">Differentiators</h2>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => generateAIContent('differentiators')}
                      disabled={generating}
                    >
                      {generating ? 'Generating...' : '🤖 AI Generate'}
                    </button>
                  </div>

                  <AddItemInput 
                    placeholder="What sets you apart from competitors?"
                    onAdd={(item) => addItem('differentiators', item)}
                  />

                  <div className="mt-4 space-y-2">
                    {capabilityData.differentiators.map((diff, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-slate-900">{diff}</span>
                        <button 
                          className="text-red-500 hover:text-red-700"
                          onClick={() => removeItem('differentiators', index)}
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications Tab */}
              {activeTab === 'certifications' && (
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 mb-6">Certifications & Status</h2>

                  <div className="space-y-6">
                    <div>
                      <h3 className="font-medium text-slate-900 mb-3">Certifications</h3>
                      <AddItemInput 
                        placeholder="Add certification (e.g., ISO 9001:2015, PMP)"
                        onAdd={(item) => addItem('certifications', item)}
                      />
                      <div className="mt-3 space-y-2">
                        {capabilityData.certifications.map((cert, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <span className="text-slate-900">{cert}</span>
                            <button 
                              className="text-red-500 hover:text-red-700"
                              onClick={() => removeItem('certifications', index)}
                            >
                              Remove
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium text-slate-900 mb-3">Socioeconomic Status</h3>
                      <AddItemInput 
                        placeholder="Add status (e.g., Small Business, Woman-Owned, Veteran-Owned)"
                        onAdd={(item) => addItem('socioeconomic_status', item)}
                      />
                      <div className="mt-3 space-y-2">
                        {capabilityData.socioeconomic_status.map((status, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <span className="text-slate-900">{status}</span>
                            <button 
                              className="text-red-500 hover:text-red-700"
                              onClick={() => removeItem('socioeconomic_status', index)}
                            >
                              Remove
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium text-slate-900 mb-3">NAICS Codes</h3>
                      <AddItemInput 
                        placeholder="Add NAICS code (e.g., 541611, 541330)"
                        onAdd={(item) => addItem('naics_codes', item)}
                      />
                      <div className="mt-3 space-y-2">
                        {capabilityData.naics_codes.map((code, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <span className="text-slate-900">{code}</span>
                            <button 
                              className="text-red-500 hover:text-red-700"
                              onClick={() => removeItem('naics_codes', index)}
                            >
                              Remove
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Contact Information Tab */}
              {activeTab === 'contact' && (
                <div>
                  <h2 className="text-xl font-semibold text-slate-900 mb-6">Contact Information</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
                      <input
                        type="text"
                        className="w-full input"
                        value={capabilityData.contact_information.company_name}
                        onChange={(e) => updateContactInfo('company_name', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                      <input
                        type="tel"
                        className="w-full input"
                        value={capabilityData.contact_information.phone}
                        onChange={(e) => updateContactInfo('phone', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                      <input
                        type="email"
                        className="w-full input"
                        value={capabilityData.contact_information.email}
                        onChange={(e) => updateContactInfo('email', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Website</label>
                      <input
                        type="url"
                        className="w-full input"
                        value={capabilityData.contact_information.website}
                        onChange={(e) => updateContactInfo('website', e.target.value)}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-slate-700 mb-1">Address</label>
                      <textarea
                        className="w-full input h-20 resize-none"
                        value={capabilityData.contact_information.address}
                        onChange={(e) => updateContactInfo('address', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">DUNS Number</label>
                      <input
                        type="text"
                        className="w-full input"
                        value={capabilityData.contact_information.duns_number}
                        onChange={(e) => updateContactInfo('duns_number', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">CAGE Code</label>
                      <input
                        type="text"
                        className="w-full input"
                        value={capabilityData.contact_information.cage_code}
                        onChange={(e) => updateContactInfo('cage_code', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper component for adding items
function AddItemInput({ placeholder, onAdd }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onAdd(value);
      setValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        className="flex-1 input"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button type="submit" className="btn btn-primary">Add</button>
    </form>
  );
}

export default CapabilityStatementBuilder;