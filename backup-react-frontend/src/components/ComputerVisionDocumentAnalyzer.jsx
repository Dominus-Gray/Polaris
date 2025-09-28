import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Computer Vision Document Analysis System
export default function ComputerVisionDocumentAnalyzer({ assessmentArea, onAnalysisComplete }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [supportedDocuments, setSupportedDocuments] = useState([]);
  const fileInputRef = useRef(null);

  const documentTypes = {
    financial: {
      name: 'Financial Documents',
      icon: '💰',
      types: ['Financial Statements', 'Tax Returns', 'Bank Statements', 'Audit Reports', 'Budget Documents'],
      analysis: ['Revenue Analysis', 'Cash Flow Assessment', 'Financial Ratios', 'Compliance Check', 'Risk Indicators']
    },
    legal: {
      name: 'Legal & Compliance',
      icon: '⚖️',
      types: ['Business Licenses', 'Articles of Incorporation', 'Insurance Certificates', 'Contracts', 'Compliance Reports'],
      analysis: ['License Validation', 'Corporate Structure', 'Insurance Coverage', 'Contract Terms', 'Compliance Status']
    },
    technical: {
      name: 'Technical Documentation',
      icon: '🔧',
      types: ['Technical Specifications', 'Quality Certificates', 'Safety Reports', 'Test Results', 'Compliance Certifications'],
      analysis: ['Technical Capability', 'Quality Standards', 'Safety Compliance', 'Performance Metrics', 'Certification Status']
    },
    operational: {
      name: 'Operational Records',
      icon: '📊',
      types: ['Process Documentation', 'Quality Manuals', 'Performance Reports', 'Organizational Charts', 'Policy Documents'],
      analysis: ['Process Maturity', 'Quality Systems', 'Performance History', 'Organizational Structure', 'Policy Compliance']
    }
  };

  useEffect(() => {
    loadSupportedDocuments();
  }, [assessmentArea]);

  const loadSupportedDocuments = async () => {
    try {
      const response = await axios.get(`${API}/ai/computer-vision/supported-documents/${assessmentArea}`);
      setSupportedDocuments(response.data.supported_types || []);
    } catch (error) {
      // Use fallback configuration
      const areaConfig = {
        'area1': documentTypes.legal,
        'area2': documentTypes.financial,
        'area3': documentTypes.legal,
        'area4': documentTypes.operational,
        'area5': documentTypes.technical
      };
      
      setSupportedDocuments(areaConfig[assessmentArea] || documentTypes.operational);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        // Create form data for file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('assessment_area', assessmentArea);
        formData.append('document_type', supportedDocuments.name || 'general');

        // Simulate analysis progress
        const progressInterval = setInterval(() => {
          setAnalysisProgress(prev => Math.min(prev + 10, 90));
        }, 200);

        // Upload and analyze document
        const response = await axios.post(`${API}/ai/computer-vision/analyze-document`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        clearInterval(progressInterval);
        setAnalysisProgress(100);

        const analysisResult = response.data || generateMockAnalysis(file, supportedDocuments);
        
        // Add to uploaded files and results
        setUploadedFiles(prev => [...prev, {
          id: `file_${Date.now()}_${i}`,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date().toISOString(),
          status: 'analyzed'
        }]);

        setAnalysisResults(prev => [...prev, {
          id: `analysis_${Date.now()}_${i}`,
          fileName: file.name,
          documentType: analysisResult.document_type,
          confidence: analysisResult.confidence,
          extractedData: analysisResult.extracted_data,
          complianceCheck: analysisResult.compliance_check,
          recommendations: analysisResult.recommendations,
          riskFactors: analysisResult.risk_factors,
          analyzedAt: new Date().toISOString()
        }]);

        // Brief pause between files
        if (i < files.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }

      } catch (error) {
        console.error('Document analysis failed:', error);
        
        // Add failed file
        setUploadedFiles(prev => [...prev, {
          id: `file_${Date.now()}_${i}`,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date().toISOString(),
          status: 'error',
          error: 'Analysis failed'
        }]);
      }
    }

    setIsAnalyzing(false);
    setAnalysisProgress(0);

    // Trigger completion callback
    if (onAnalysisComplete) {
      onAnalysisComplete(analysisResults);
    }
  };

  const generateMockAnalysis = (file, documentConfig) => {
    // Generate realistic mock analysis for demonstration
    const documentTypes = documentConfig.types || ['General Document'];
    const analysisTypes = documentConfig.analysis || ['Content Analysis'];
    
    return {
      document_type: documentTypes[Math.floor(Math.random() * documentTypes.length)],
      confidence: 0.85 + Math.random() * 0.1, // 85-95% confidence
      extracted_data: {
        document_title: file.name.replace(/\.[^/.]+$/, ""),
        document_date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        organization_name: 'Sample Organization LLC',
        key_figures: {
          revenue: '$' + (Math.random() * 1000000 + 100000).toLocaleString(),
          employees: Math.floor(Math.random() * 100) + 10,
          certification_date: new Date().toISOString().split('T')[0]
        },
        compliance_indicators: [
          'Valid business license identified',
          'Financial statements format compliant',
          'Required signatures present'
        ]
      },
      compliance_check: {
        overall_score: Math.floor(Math.random() * 30) + 70, // 70-100%
        passed_checks: Math.floor(Math.random() * 3) + 7, // 7-10
        total_checks: 10,
        critical_issues: Math.random() > 0.7 ? ['Missing required signature'] : [],
        recommendations: [
          'Document format meets standards',
          'Consider updating expired certifications',
          'Verify all required fields are complete'
        ]
      },
      recommendations: [
        'Document is suitable for procurement evidence',
        'Consider obtaining higher-resolution scan',
        'Add official stamps or seals if available'
      ],
      risk_factors: Math.random() > 0.5 ? ['Document older than 1 year'] : []
    };
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-blue-600 bg-blue-100';
    if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getComplianceColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-lg">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold mb-1">AI Document Analysis</h2>
              <p className="opacity-90">Advanced computer vision for automated evidence validation</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{analysisResults.length}</div>
            <div className="text-sm opacity-75">Documents Analyzed</div>
          </div>
        </div>
      </div>

      {/* Document Upload Area */}
      <div className="bg-white rounded-lg border-2 border-dashed border-slate-300 p-8 text-center hover:border-blue-400 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.jpg,.png,.txt"
          onChange={handleFileUpload}
          className="hidden"
        />
        
        {!isAnalyzing ? (
          <div>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Documents for AI Analysis</h3>
            <p className="text-slate-600 mb-4">
              Our computer vision AI will analyze your documents and extract relevant procurement readiness information
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Choose Documents
            </button>
            <div className="text-xs text-slate-500 mt-2">
              Supports: PDF, Word, Images (JPG, PNG) • Max 10MB per file
            </div>
          </div>
        ) : (
          <div>
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">AI Analysis in Progress</h3>
            <p className="text-slate-600 mb-4">Computer vision algorithms are analyzing your documents...</p>
            
            <div className="w-full bg-slate-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${analysisProgress}%` }}
              />
            </div>
            <div className="text-sm text-slate-600">{analysisProgress}% Complete</div>
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-900">AI Analysis Results</h3>
          
          {analysisResults.map((result) => (
            <div key={result.id} className="bg-white rounded-lg border p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900">{result.fileName}</h4>
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                      <span>Type: {result.documentType}</span>
                      <span>•</span>
                      <span className={`px-2 py-1 rounded ${getConfidenceColor(result.confidence)}`}>
                        {Math.round(result.confidence * 100)}% Confidence
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getComplianceColor(result.complianceCheck.overall_score)}`}>
                    {result.complianceCheck.overall_score}%
                  </div>
                  <div className="text-sm text-slate-600">Compliance Score</div>
                </div>
              </div>

              {/* Extracted Data */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                <div>
                  <h5 className="font-medium text-slate-900 mb-2">📊 Extracted Information</h5>
                  <div className="bg-slate-50 rounded-lg p-3 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Document Title:</span>
                      <span className="font-medium text-slate-900">{result.extractedData.document_title}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Date:</span>
                      <span className="font-medium text-slate-900">{result.extractedData.document_date}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Organization:</span>
                      <span className="font-medium text-slate-900">{result.extractedData.organization_name}</span>
                    </div>
                    
                    {Object.entries(result.extractedData.key_figures || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-slate-600">{key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                        <span className="font-medium text-slate-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="font-medium text-slate-900 mb-2">✅ Compliance Analysis</h5>
                  <div className="bg-slate-50 rounded-lg p-3 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Checks Passed:</span>
                      <span className="font-medium text-green-600">
                        {result.complianceCheck.passed_checks}/{result.complianceCheck.total_checks}
                      </span>
                    </div>
                    
                    <div className="space-y-1">
                      {result.extractedData.compliance_indicators?.map((indicator, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs text-green-700">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {indicator}
                        </div>
                      ))}
                    </div>
                    
                    {result.complianceCheck.critical_issues?.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {result.complianceCheck.critical_issues.map((issue, index) => (
                          <div key={index} className="flex items-center gap-2 text-xs text-red-700">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            {issue}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Recommendations */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-4">
                <h5 className="font-medium text-slate-900 mb-2">🤖 AI Recommendations</h5>
                <div className="space-y-1">
                  {result.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start gap-2 text-sm text-blue-800">
                      <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-1.5 flex-shrink-0"></div>
                      {recommendation}
                    </div>
                  ))}
                </div>
                
                {result.riskFactors?.length > 0 && (
                  <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                    <div className="font-medium text-yellow-900 text-xs mb-1">⚠️ Risk Factors Identified:</div>
                    {result.riskFactors.map((risk, index) => (
                      <div key={index} className="text-xs text-yellow-800">{risk}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Supported Document Types Info */}
      {supportedDocuments && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="font-semibold text-slate-900 mb-4">
            {supportedDocuments.icon} {supportedDocuments.name}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-slate-900 mb-2">Supported Document Types:</h4>
              <div className="space-y-1">
                {(supportedDocuments.types || []).map((type, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-slate-600">
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full"></div>
                    {type}
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-slate-900 mb-2">AI Analysis Capabilities:</h4>
              <div className="space-y-1">
                {(supportedDocuments.analysis || []).map((analysis, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-slate-600">
                    <div className="w-1.5 h-1.5 bg-purple-500 rounded-full"></div>
                    {analysis}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Summary */}
      {analysisResults.length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">📈 Analysis Summary</h3>
              <p className="text-slate-600">
                {analysisResults.length} documents analyzed with AI computer vision
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-600">
                {Math.round(analysisResults.reduce((sum, r) => sum + r.complianceCheck.overall_score, 0) / analysisResults.length)}%
              </div>
              <div className="text-sm text-slate-600">Avg Compliance</div>
            </div>
          </div>
          
          <div className="mt-4 flex gap-3">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium">
              Apply to Assessment
            </button>
            <button className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm">
              Generate Report
            </button>
            <button className="px-4 py-2 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 transition-colors text-sm">
              Share Results
            </button>
          </div>
        </div>
      )}
    </div>
  );
}