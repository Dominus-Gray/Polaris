import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = BACKEND_URL;

function TierBasedAssessmentPage() {
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [availableAreas, setAvailableAreas] = useState([]);
  const [currentArea, setCurrentArea] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [responses, setResponses] = useState({});
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showGapOptions, setShowGapOptions] = useState(false);

  const loadAssessmentData = async () => {
    try {
      const token = localStorage.getItem('polaris_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const { data } = await axios.get(`${API}/assessment/schema/tier-based`, { headers });
      
      // Map backend structure to frontend format
      const areas = (data.areas || []).map(area => ({
        id: area.area_id,
        name: area.area_name || area.name,
        description: area.description || 'Assessment area for procurement readiness',
        tiers: area.tiers || {}
      }));
      
      setAvailableAreas(areas);
    } catch (error) {
      console.error('Error loading assessment data:', error);
      // Fallback data - Complete 10 areas matching backend schema
      setAvailableAreas([
        { id: 'area1', name: 'Business Formation & Registration', description: 'Business formation, licenses, legal requirements, insurance coverage' },
        { id: 'area2', name: 'Financial Operations & Management', description: 'Accounting systems, financial records, credit and banking relationships' },
        { id: 'area3', name: 'Legal & Contracting Compliance', description: 'Service agreements, regulatory compliance, intellectual property protections' },
        { id: 'area4', name: 'Quality Management & Standards', description: 'Quality control processes, certifications, customer feedback systems' },
        { id: 'area5', name: 'Technology & Security Infrastructure', description: 'Cybersecurity measures, scalable technology, data backup and recovery' },
        { id: 'area6', name: 'Human Resources & Capacity', description: 'Staffing capacity, training and certifications, employee development programs' },
        { id: 'area7', name: 'Performance Tracking & Reporting', description: 'KPI tracking systems, client reporting, project documentation' },
        { id: 'area8', name: 'Risk Management & Business Continuity', description: 'Business continuity planning, emergency preparedness, professional insurance' },
        { id: 'area9', name: 'Supply Chain Management & Vendor Relations', description: 'Vendor qualification processes, supply chain resilience, vendor performance monitoring' },
        { id: 'area10', name: 'Competitive Advantage & Market Position', description: 'Competitive advantages, market capture processes, strategic partnerships' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssessmentData();
  }, []);

  const handleMaturityResponse = async (response) => {
    if (response === 'not-compliant') {
      // Show gap options: service request, external resources, knowledge base
      setShowGapOptions(true);
    } else {
      // Move to next question or area
      const area = availableAreas[currentArea];
      if (currentQuestion < 2) { // 3 questions per area (0, 1, 2)
        setCurrentQuestion(currentQuestion + 1);
      } else {
        // Move to next area
        if (currentArea < availableAreas.length - 1) {
          setCurrentArea(currentArea + 1);
          setCurrentQuestion(0);
        } else {
          // Assessment complete
          navigate('/assessment/results');
        }
      }
    }
  };

  const handleGapOption = (option) => {
    switch(option) {
      case 'service-request':
        navigate('/service-request');
        break;
      case 'external-resources':
        navigate(`/external-resources/${availableAreas[currentArea]?.id}`);
        break;
      case 'knowledge-base':
        navigate('/knowledge-base');
        break;
    }
  };

  if (loading) {
    return (
      <div className="container mt-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="h-32 bg-slate-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Area selection view
  if (currentArea === null) {
    return (
      <div className="container mt-6 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Business Maturity Assessment</h1>
          <p className="text-xl text-slate-600">Select a business area to begin your assessment</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableAreas.map((area, index) => (
            <div key={area.id} className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
                 onClick={() => setCurrentArea(index)}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{area.name}</h3>
                  <p className="text-sm text-slate-600">{area.description}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-bold">{index + 1}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-500">
                  3 Maturity Statements
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                  Begin Assessment
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const area = availableAreas[currentArea];
  const progress = ((currentArea * 3) + currentQuestion + 1) / (availableAreas.length * 3) * 100;

  // Single statement assessment view
  return (
    <div className="container mt-6 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <button 
          className="btn mb-4"
          onClick={() => {
            if (currentQuestion > 0) {
              setCurrentQuestion(currentQuestion - 1);
            } else if (currentArea > 0) {
              setCurrentArea(currentArea - 1);
              setCurrentQuestion(2);
            } else {
              setCurrentArea(null);
            }
            setShowGapOptions(false);
          }}
        >
          ← Back
        </button>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-700">{area?.name}</h1>
              <p className="text-gray-600">Question {currentQuestion + 1} of 3</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Overall Progress</div>
              <div className="text-2xl font-bold text-blue-600">{Math.round(progress)}%</div>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 rounded-full h-2 transition-all duration-300" style={{width: `${progress}%`}}></div>
          </div>
        </div>
      </div>

      {!showGapOptions ? (
        // Single maturity statement presentation
        <div className="bg-white rounded-lg border p-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Business Maturity Statement</h2>
          
          {/* Single statement based on area and question */}
          <div className="text-lg text-gray-700 mb-8 leading-relaxed">
            {area?.id === 'area1' && currentQuestion === 0 && "Your business has valid licenses and is properly registered with all required authorities."}
            {area?.id === 'area1' && currentQuestion === 1 && "Your business maintains comprehensive insurance coverage appropriate for your services."}
            {area?.id === 'area1' && currentQuestion === 2 && "Your business formation documents are current and accessible for review."}
            {/* Add more statements for other areas as needed */}
            {!area && "Loading assessment statement..."}
          </div>
          
          <div className="space-y-4">
            <button 
              className="w-full p-4 bg-green-50 border-2 border-green-200 rounded-lg text-green-800 font-medium hover:bg-green-100 transition-colors"
              onClick={() => handleMaturityResponse('compliant')}
            >
              ✅ Compliant - This statement accurately describes our business
            </button>
            
            <button 
              className="w-full p-4 bg-red-50 border-2 border-red-200 rounded-lg text-red-800 font-medium hover:bg-red-100 transition-colors"
              onClick={() => handleMaturityResponse('not-compliant')}
            >
              ❌ Not Compliant - We need help with this area
            </button>
          </div>
        </div>
      ) : (
        // Gap options when not compliant selected
        <div className="bg-white rounded-lg border p-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Gap Identified</h2>
          <p className="text-gray-600 mb-6">You've identified a gap in {area?.name}. How would you like to address this?</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <button 
              className="p-6 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors text-center"
              onClick={() => handleGapOption('service-request')}
            >
              <div className="text-3xl mb-3">🔧</div>
              <h3 className="font-semibold text-blue-800 mb-2">Request Service Provider</h3>
              <p className="text-sm text-blue-700">Get professional help from our marketplace</p>
            </button>
            
            <button 
              className="p-6 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors text-center"
              onClick={() => handleGapOption('external-resources')}
            >
              <div className="text-3xl mb-3">📋</div>
              <h3 className="font-semibold text-green-800 mb-2">Access External Resources</h3>
              <p className="text-sm text-green-700">View free resources and templates</p>
            </button>
            
            <button 
              className="p-6 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors text-center"
              onClick={() => handleGapOption('knowledge-base')}
            >
              <div className="text-3xl mb-3">📚</div>
              <h3 className="font-semibold text-purple-800 mb-2">Knowledge Base</h3>
              <p className="text-sm text-purple-700">Explore our comprehensive guides</p>
            </button>
          </div>
          
          <div className="mt-6 text-center">
            <button 
              className="btn"
              onClick={() => setShowGapOptions(false)}
            >
              Continue Assessment
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TierBasedAssessmentPage;