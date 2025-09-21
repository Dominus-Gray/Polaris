import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";

// Import new page components
import RevenueOptimization from './pages/RevenueOptimization';
import NavigatorApprovals from './pages/NavigatorApprovals';
import NavigatorEvidenceReview from './components/NavigatorEvidenceReview';
import AgencyBusinessIntelligence from './components/AgencyBusinessIntelligence';
import AgencyBusinessIntelligenceDashboard from './components/AgencyBusinessIntelligenceDashboard';
import AgencyLicenseDistribution from './components/AgencyLicenseDistribution';
import AgencyAIContractMatching from './components/AgencyAIContractMatching';
import AgencyAccountSettings from './components/AgencyAccountSettings';
import AgencyIssueCertificate from './pages/AgencyIssueCertificate';
import AgencyLicenses from './pages/AgencyLicenses';
import AssessmentResultsPage from './pages/AssessmentResultsPage';
import ReadinessDashboard from './pages/ReadinessDashboard';
import CapabilityStatementBuilder from './pages/CapabilityStatementBuilder';
import ProviderVerification from './pages/ProviderVerification';
import ActionPlanPage from './pages/ActionPlanPage';
import CertificationCenter from './pages/CertificationCenter';

// Enhanced error boundary for production stability
import ClientRemediationFilters from './components/ClientRemediationFilters';
import AssessmentTierSelector from './components/AssessmentTierSelector';
import TierBasedAssessmentPage from './components/TierBasedAssessmentPage';
import AssessmentResults from './components/AssessmentResults';

import AgencyContractMatching from './pages/AgencyContractMatching';


import ClientLocalDirectory from './pages/ClientLocalDirectory';

import ProviderRequestsCenter from './components/ProviderRequestsCenter';
import AgencySponsoredClients from './pages/AgencySponsoredClients';
import AgencySponsorKPIs from './components/AgencySponsorKPIs';


import EngagementDetails from './pages/EngagementDetails';

class PolarisErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Polaris Error:', error, errorInfo);
    // Log to monitoring service in production
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: false
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
          <div className="text-center p-8 max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">
              Something went wrong
            </h2>
            <p className="text-slate-600 mb-6">
              We're sorry, but something unexpected happened. Please refresh the page or contact support if the issue persists.
            </p>
            <div className="space-x-4">
              <button 
                className="btn btn-primary"
                onClick={() => window.location.reload()}
              >
                Refresh Page
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => window.location.href = '/'}
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
import { Toaster, toast } from "sonner";
import ProfileSettings from "./components/ProfileSettings";
import AdminDashboard from "./components/AdminDashboard";
import 'uplot/dist/uPlot.min.css';