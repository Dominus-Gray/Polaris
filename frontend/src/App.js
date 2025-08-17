import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { Toaster, toast } from "sonner";
import ProfileSettings from "./components/ProfileSettings";
import AdminDashboard from "./components/AdminDashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PolarisLogo({ size = 22, variant = 'default' }) {
  const logoColor = variant === 'white' ? '#ffffff' : '#1B365D';
  const starColor = variant === 'white' ? '#ffffff' : '#4A90C2';
  
  return (
    <div className={`polaris-logo-container ${variant === 'large' ? 'logo-large' : ''}`} style={{ minWidth: size, minHeight: size }}>
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className="drop-shadow-sm">
        {/* North Star - Polaris */}
        <path d="M12 2L13.09 8.26L19 7L14.91 11.09L21 12L14.74 13.09L16 19L11.91 14.91L12 21L10.91 14.74L5 16L9.09 11.91L3 12L9.26 10.91L8 5L12.09 9.09L12 2Z" fill={starColor} />
        {/* Central glow */}
        <circle cx="12" cy="12" r="2" fill={logoColor} opacity="0.8" />
        {/* Outer ring for visibility */}
        <circle cx="12" cy="12" r="10" fill="none" stroke={logoColor} strokeWidth="0.5" opacity="0.3" />
      </svg>
      {variant === 'large' && (
        <div className="logo-text">
          <span className="logo-brand">POLARIS</span>
          <span className="logo-tagline">Procurement Readiness</span>
        </div>
      )}
      {size >= 24 && variant !== 'large' && variant !== 'white' && (
        <span className="text-sm font-semibold text-slate-700 ml-1">POLARIS</span>
      )}
    </div>
  );
}

function useAuthHeader(){
  useEffect(()=>{
    const t = localStorage.getItem('polaris_token');
    if (t) axios.defaults.headers.common['Authorization'] = `Bearer ${t}`; else delete axios.defaults.headers.common['Authorization'];
  },[]);
}

function AuthWidget(){
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [role, setRole] = useState('client');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [paymentInfo, setPaymentInfo] = useState({
    card_number: '',
    expiry_month: '',
    expiry_year: '',
    cvv: '',
    cardholder_name: ''
  });
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showOAuthModal, setShowOAuthModal] = useState(false);
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  
  const submit = async()=>{
    if (mode === 'register' && !termsAccepted) {
      toast.error('Please accept the Terms of Service and Privacy Policy to continue');
      return;
    }
    
    // Validate invitation code for clients
    if (mode === 'register' && role === 'client' && !inviteCode.trim()) {
      toast.error('Invitation code is required for small business client registration');
      return;
    }
    
    // Validate payment information for non-navigator registrations
    if (mode === 'register' && role !== 'navigator') {
      if (!paymentInfo.card_number || !paymentInfo.expiry_month || !paymentInfo.expiry_year || 
          !paymentInfo.cvv || !paymentInfo.cardholder_name) {
        toast.error('Payment information is required for registration');
        return;
      }
    }
    
    setIsSubmitting(true);
    
    try{
      if(mode==='register'){
        const registrationData = { 
          email, 
          password, 
          role, 
          terms_accepted: termsAccepted,
          ...(role === 'client' && { invite_code: inviteCode }),
          ...(role !== 'navigator' && { payment_info: paymentInfo })
        };
        
        await axios.post(`${API}/auth/register`, registrationData);
        toast.success('Registration successful', { 
          description: role === 'client' 
            ? 'Welcome! Please sign in to begin your assessment'
            : 'Please sign in with your credentials'
        });
        setMode('login');
      } else {
        const { data } = await axios.post(`${API}/auth/login`, { email, password });
        localStorage.setItem('polaris_token', data.access_token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
        const me = await axios.get(`${API}/auth/me`);
        localStorage.setItem('polaris_me', JSON.stringify(me.data));
        toast.success('Welcome', { description: me.data.email });
        navigate('/home');
      }
    }catch(e){ 
      let errorMessage = 'Authentication failed';
      let errorDescription = 'Please try again';
      
      if (e.response?.data?.detail) {
        if (typeof e.response.data.detail === 'string') {
          errorDescription = e.response.data.detail;
        } else if (Array.isArray(e.response.data.detail)) {
          errorDescription = e.response.data.detail.map(err => {
            if (typeof err === 'string') return err;
            if (err.msg) return err.msg;
            return 'Validation error';
          }).join(', ');
        }
      }
      
      toast.error(errorMessage, { description: errorDescription });
    }
    
    setIsSubmitting(false);
  };

  const handleGoogleAuth = () => {
    setShowOAuthModal(true);
  };

  const proceedWithGoogleAuth = () => {
    const currentUrl = window.location.origin;
    const redirectUrl = `${currentUrl}/profile`;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="auth-widget" id="auth">
      <div className="bg-white rounded-lg p-6 shadow-lg border">
        <h3 className="font-semibold text-slate-900 mb-4 text-center">Get Started Today</h3>
        
        {/* Google OAuth Button */}
        <button 
          className="w-full flex items-center justify-center gap-3 px-4 py-2 border border-slate-300 rounded-md bg-white hover:bg-slate-50 transition-colors mb-4"
          onClick={handleGoogleAuth}
          disabled={isSubmitting}
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          <span className="font-medium text-slate-700">Continue with Google</span>
        </button>

        <div className="relative mb-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-slate-500">or</span>
          </div>
        </div>

        {/* Traditional Auth Form */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <select className="input flex-1" value={mode} onChange={e=>setMode(e.target.value)} disabled={isSubmitting}>
              <option value="login">Login</option>
              <option value="register">Register</option>
            </select>
            {mode==='register' && (
              <select className="input flex-1" value={role} onChange={e=>setRole(e.target.value)} disabled={isSubmitting}>
                <option value="client">Client</option>
                <option value="provider">Provider</option>
                <option value="navigator">Navigator</option>
                <option value="agency">Agency</option>
              </select>
            )}
          </div>
          <input 
            className="input w-full" 
            placeholder="Email address" 
            type="email" 
            value={email} 
            onChange={e=>setEmail(e.target.value)}
            disabled={isSubmitting}
          />
          <input 
            className="input w-full" 
            placeholder="Password" 
            type="password" 
            value={password} 
            onChange={e=>setPassword(e.target.value)}
            disabled={isSubmitting}
          />
          
          {/* Invitation Code for Clients */}
          {mode === 'register' && role === 'client' && (
            <input 
              className="input w-full" 
              placeholder="Agency Invitation Code *" 
              value={inviteCode} 
              onChange={e=>setInviteCode(e.target.value)}
              disabled={isSubmitting}
            />
          )}
          
          {/* Payment Information for Non-Navigators */}
          {mode === 'register' && role !== 'navigator' && (
            <div className="space-y-3 p-4 bg-slate-50 rounded border">
              <div className="text-sm font-medium text-slate-900">Payment Information</div>
              <input 
                className="input w-full" 
                placeholder="Cardholder Name *" 
                value={paymentInfo.cardholder_name} 
                onChange={e=>setPaymentInfo({...paymentInfo, cardholder_name: e.target.value})}
                disabled={isSubmitting}
              />
              <input 
                className="input w-full" 
                placeholder="Card Number *" 
                value={paymentInfo.card_number} 
                onChange={e=>setPaymentInfo({...paymentInfo, card_number: e.target.value})}
                disabled={isSubmitting}
              />
              <div className="grid grid-cols-3 gap-2">
                <select 
                  className="input"
                  value={paymentInfo.expiry_month}
                  onChange={e=>setPaymentInfo({...paymentInfo, expiry_month: e.target.value})}
                  disabled={isSubmitting}
                >
                  <option value="">Month *</option>
                  {Array.from({length: 12}, (_, i) => i + 1).map(month => (
                    <option key={month} value={month.toString().padStart(2, '0')}>
                      {month.toString().padStart(2, '0')}
                    </option>
                  ))}
                </select>
                <select 
                  className="input"
                  value={paymentInfo.expiry_year}
                  onChange={e=>setPaymentInfo({...paymentInfo, expiry_year: e.target.value})}
                  disabled={isSubmitting}
                >
                  <option value="">Year *</option>
                  {Array.from({length: 10}, (_, i) => new Date().getFullYear() + i).map(year => (
                    <option key={year} value={year.toString()}>{year}</option>
                  ))}
                </select>
                <input 
                  className="input" 
                  placeholder="CVV *" 
                  value={paymentInfo.cvv} 
                  onChange={e=>setPaymentInfo({...paymentInfo, cvv: e.target.value})}
                  disabled={isSubmitting}
                  maxLength={4}
                />
              </div>
              <div className="text-xs text-slate-500">
                {role === 'client' ? 'Payment will be processed only when you select service providers' :
                 role === 'provider' ? 'Card will be charged only when you receive service requests' :
                 'Platform registration fee applies'}
              </div>
            </div>
          )}
          
          {mode === 'register' && (
            <div className="flex items-start gap-3 p-3 bg-slate-50 rounded border">
              <input 
                type="checkbox" 
                id="terms" 
                checked={termsAccepted} 
                onChange={e=>setTermsAccepted(e.target.checked)}
                className="mt-1"
                disabled={isSubmitting}
              />
              <label htmlFor="terms" className="text-xs text-slate-600 leading-relaxed">
                I agree to the <strong>Terms of Service</strong> and <strong>Privacy Policy</strong>. I understand that service providers must be approved by Digital Navigators before joining the marketplace, and that my data will be protected according to NIST cybersecurity standards.
              </label>
            </div>
          )}
          
          <button 
            className="btn btn-primary w-full" 
            onClick={submit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Processing...' : (mode==='login' ? 'Sign In' : 'Create Account')}
          </button>
        </div>

        <p className="text-xs text-slate-500 text-center mt-4">
          Secure platform with enterprise-grade data protection and compliance standards.
        </p>
      </div>

      {/* Branded OAuth Modal */}
      {showOAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="polaris-oauth-modal">
            <div className="modal-content">
              {/* Custom Polaris Branding Header */}
              <div className="oauth-header">
                <div className="polaris-brand-showcase">
                  <PolarisLogo size={48} />
                  <div className="brand-elements">
                    <div className="constellation-bg">
                      <div className="star star-1"></div>
                      <div className="star star-2"></div>
                      <div className="star star-3"></div>
                      <div className="star star-4"></div>
                      <div className="star star-5"></div>
                    </div>
                  </div>
                </div>
                <h2 className="oauth-title">Welcome to Polaris</h2>
                <p className="oauth-subtitle">Your North Star for Procurement Readiness</p>
              </div>

              {/* Professional Graphic Elements */}
              <div className="oauth-visual-elements">
                <div className="procurement-icons">
                  <div className="icon-group">
                    <div className="proc-icon proc-icon-1">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                      </svg>
                    </div>
                    <div className="proc-icon proc-icon-2">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <div className="proc-icon proc-icon-3">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2 2z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              {/* OAuth Action Section */}
              <div className="oauth-actions">
                <p className="oauth-description">
                  Continue with Google to access your secure, government-grade procurement readiness platform
                </p>
                <div className="oauth-security-badges">
                  <span className="security-badge">🔒 NIST Compliant</span>
                  <span className="security-badge">🛡️ Enterprise Security</span>
                  <span className="security-badge">⚡ Fast & Secure</span>
                </div>
                <div className="oauth-buttons">
                  <button 
                    className="btn-oauth-primary" 
                    onClick={proceedWithGoogleAuth}
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Continue with Google
                  </button>
                  <button 
                    className="btn-oauth-secondary" 
                    onClick={() => setShowOAuthModal(false)}
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
  );
}

function VerifyCert(){
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(()=>{ const load=async()=>{ try{ const {data} = await axios.get(`${API}/certificates/${id}/public`); setData(data); }catch(e){ setError(e?.response?.data?.detail || 'Unavailable'); } }; load(); },[id]);
  return (
    <div className="container mt-10 max-w-2xl">
      <h1 className="text-xl font-semibold mb-3">Certificate Verification</h1>
      {error && <div className="alert">{error}</div>}
      {!error && !data && <div className="skel h-24 w-full" />}
      {data && (
        <div className="p-4 border rounded bg-white shadow-sm">
          <div className="text-lg font-medium">{data.title || 'Small Business Maturity Assurance'}</div>
          <div className="text-sm text-slate-600">Certificate ID: {data.id}</div>
          <div className="mt-2 text-sm">Readiness: <span className="font-semibold">{data.readiness_percent}%</span></div>
          <div className="text-sm">Issued at: {new Date(data.issued_at).toLocaleString()}</div>
          <div className="text-xs text-slate-500 mt-2">Sponsoring Agency ID: {data.agency_user_id}</div>
          <div className="mt-3 text-xs text-slate-500">This verification page confirms the certificate details recorded in Polaris.</div>
        </div>
      )}
    </div>
  );
}

function ProfilePage(){
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [role, setRole] = useState('client');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      // Check for session ID in URL fragment
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);
      const sessionId = params.get('session_id');

      if (sessionId && !isProcessing) {
        setIsProcessing(true);
        try {
          // Call backend to exchange session ID for user data
          const response = await axios.post(`${API}/auth/oauth/callback`, { 
            session_id: sessionId,
            role: role 
          });
          
          if (response.data.access_token) {
            localStorage.setItem('polaris_token', response.data.access_token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
            localStorage.setItem('polaris_me', JSON.stringify({
              id: response.data.user_id,
              email: response.data.email,
              name: response.data.name,
              role: response.data.role
            }));
            
            toast.success('Welcome to Polaris!', { description: response.data.email });
            navigate('/home');
          }
        } catch (error) {
          console.error('OAuth callback error:', error);
          toast.error('Authentication failed', { description: 'Please try again' });
          navigate('/');
        }
      }
    };

    handleOAuthCallback();
  }, [navigate, isProcessing, role]);

  if (isProcessing) {
    return (
      <div className="oauth-processing-page">
        <div className="processing-container">
          {/* Enhanced Polaris Branding */}
          <div className="processing-header">
            <div className="polaris-brand-large">
              <PolarisLogo size={64} />
              <div className="brand-constellation">
                <div className="constellation-large">
                  <div className="star-large star-1"></div>
                  <div className="star-large star-2"></div>
                  <div className="star-large star-3"></div>
                  <div className="star-large star-4"></div>
                  <div className="star-large star-5"></div>
                  <div className="star-large star-6"></div>
                  <div className="star-large star-7"></div>
                  <div className="star-large star-8"></div>
                </div>
              </div>
            </div>
            <h1 className="processing-title">Welcome to Polaris</h1>
            <p className="processing-subtitle">Your North Star for Procurement Readiness</p>
          </div>

          {/* Professional Loading Animation */}
          <div className="processing-animation">
            <div className="polaris-loader">
              <div className="loader-ring"></div>
              <div className="loader-ring"></div>
              <div className="loader-ring"></div>
            </div>
          </div>

          {/* Processing Steps Visualization */}
          <div className="processing-steps">
            <div className="step-item active">
              <div className="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span>Authenticating</span>
            </div>
            <div className="step-item active">
              <div className="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span>Securing Account</span>
            </div>
            <div className="step-item">
              <div className="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span>Preparing Dashboard</span>
            </div>
          </div>

          <div className="processing-message">
            <p>Setting up your secure, government-grade procurement readiness platform...</p>
            <div className="security-indicators">
              <span className="security-indicator">🔒 NIST Compliant</span>
              <span className="security-indicator">🛡️ Enterprise Security</span>
              <span className="security-indicator">⚡ Fast & Reliable</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-selection-page">
      <div className="selection-container">
        {/* Enhanced Header with Polaris Branding */}
        <div className="selection-header">
          <div className="polaris-brand-showcase-large">
            <PolarisLogo size={56} />
            <div className="brand-elements-large">
              <div className="procurement-visual">
                <div className="proc-element proc-1"></div>
                <div className="proc-element proc-2"></div>
                <div className="proc-element proc-3"></div>
              </div>
            </div>
          </div>
          <h2 className="selection-title">Complete Your Polaris Profile</h2>
          <p className="selection-subtitle">Choose your role to personalize your procurement readiness experience</p>
        </div>
        
        {/* Enhanced Role Selection Cards */}
        <div className="role-selection-grid">
          <label className={`role-card ${role === 'client' ? 'selected' : ''}`}>
            <input 
              type="radio" 
              name="role" 
              value="client" 
              checked={role === 'client'} 
              onChange={(e) => setRole(e.target.value)}
            />
            <div className="role-icon client-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div className="role-content">
              <h3>Small Business</h3>
              <p>Assess readiness and get certified for government contracting opportunities</p>
              <ul>
                <li>Maturity assessment</li>
                <li>Readiness certification</li>
                <li>Provider matching</li>
              </ul>
            </div>
          </label>
          
          <label className={`role-card ${role === 'provider' ? 'selected' : ''}`}>
            <input 
              type="radio" 
              name="role" 
              value="provider" 
              checked={role === 'provider'} 
              onChange={(e) => setRole(e.target.value)}
            />
            <div className="role-icon provider-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="role-content">
              <h3>Service Provider</h3>
              <p>Connect with businesses needing your expertise and grow your client base</p>
              <ul>
                <li>Client matching</li>
                <li>Proposal management</li>
                <li>Engagement tracking</li>
              </ul>
            </div>
          </label>
          
          <label className={`role-card ${role === 'navigator' ? 'selected' : ''}`}>
            <input 
              type="radio" 
              name="role" 
              value="navigator" 
              checked={role === 'navigator'} 
              onChange={(e) => setRole(e.target.value)}
            />
            <div className="role-icon navigator-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <div className="role-content">
              <h3>Digital Navigator</h3>
              <p>Review assessments, validate evidence, and guide businesses to readiness</p>
              <ul>
                <li>Evidence review</li>
                <li>Provider approval</li>
                <li>Quality assurance</li>
              </ul>
            </div>
          </label>
          
          <label className={`role-card ${role === 'agency' ? 'selected' : ''}`}>
            <input 
              type="radio" 
              name="role" 
              value="agency" 
              checked={role === 'agency'} 
              onChange={(e) => setRole(e.target.value)}
            />
            <div className="role-icon agency-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div className="role-content">
              <h3>Local Agency</h3>
              <p>Invite businesses, manage assessments, and track community impact</p>
              <ul>
                <li>Business invitations</li>
                <li>Impact dashboards</li>
                <li>Opportunity management</li>
              </ul>
            </div>
          </label>
        </div>

        <button 
          className="continue-button"
          onClick={() => window.location.reload()}
        >
          Continue with {role}
          <svg className="continue-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>
      </div>
    </div>
  );
}

function AssessmentPage(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [currentArea, setCurrentArea] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResources, setShowResources] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [showAreaNavigation, setShowAreaNavigation] = useState(false);
  
  // Redirect non-clients to home
  if (!me || me.role !== 'client') {
    return <Navigate to="/home" replace />;
  }

  // Assessment areas and questions - Updated to match backend schema
  const assessmentAreas = [
    {
      id: 'area1',
      title: 'Business Formation & Registration',
      questions: [
        { id: 'q1_1', text: 'Do you have a valid business license in your jurisdiction?', deliverable: 'Valid business license certificate', alternatives: 'City/county business registration, professional licenses' },
        { id: 'q1_2', text: 'Is your business registered with the appropriate state and local authorities?', deliverable: 'Articles of incorporation or LLC formation documents', alternatives: 'Certificate of formation, partnership agreement' },
        { id: 'q1_3', text: 'Do you have proper business insurance coverage?', deliverable: 'General liability insurance certificate', alternatives: 'Professional liability, errors & omissions insurance' }
      ]
    },
    {
      id: 'area2', 
      title: 'Financial Operations & Management',
      questions: [
        { id: 'q2_1', text: 'Do you have a professional accounting system in place?', deliverable: 'Organized bookkeeping records, accounting software setup', alternatives: 'QuickBooks, spreadsheet tracking, CPA-maintained records' },
        { id: 'q2_2', text: 'Are your financial records current and audit-ready?', deliverable: 'Balance sheet, income statement, cash flow statement', alternatives: 'Tax returns, profit/loss statements, financial summaries' },
        { id: 'q2_3', text: 'Do you have established credit and banking relationships?', deliverable: 'Business bank account statements, credit references', alternatives: 'Business credit report, banking history documentation' }
      ]
    },
    {
      id: 'area3',
      title: 'Legal & Contracting Compliance', 
      questions: [
        { id: 'q3_1', text: 'Do you have standard service agreements and contracts?', deliverable: 'Attorney-reviewed contract templates', alternatives: 'Service agreements, terms of service, work order templates' },
        { id: 'q3_2', text: 'Are you compliant with relevant industry regulations?', deliverable: 'Compliance certificates and documentation', alternatives: 'Industry certifications, regulatory filings, audit reports' },
        { id: 'q3_3', text: 'Do you have proper intellectual property protections?', deliverable: 'IP documentation and protections', alternatives: 'Trademark registrations, copyright notices, trade secrets policy' }
      ]
    },
    {
      id: 'area4',
      title: 'Quality Management & Standards', 
      questions: [
        { id: 'q4_1', text: 'Do you have documented quality control processes?', deliverable: 'Quality control procedures and checklists', alternatives: 'Process documentation, quality standards, testing protocols' },
        { id: 'q4_2', text: 'Are your services certified or accredited where applicable?', deliverable: 'Professional certifications and accreditations', alternatives: 'Industry certifications, training certificates, quality awards' },
        { id: 'q4_3', text: 'Do you have customer feedback and improvement systems?', deliverable: 'Customer satisfaction tracking system', alternatives: 'Review processes, feedback forms, improvement documentation' }
      ]
    },
    {
      id: 'area5',
      title: 'Technology & Security Infrastructure', 
      questions: [
        { id: 'q5_1', text: 'Do you have adequate cybersecurity measures in place?', deliverable: 'Cybersecurity policies and implementation proof', alternatives: 'Security software, data protection measures, incident response plan' },
        { id: 'q5_2', text: 'Are your technology systems scalable for larger contracts?', deliverable: 'Technology capacity and scalability documentation', alternatives: 'System specifications, cloud infrastructure, upgrade plans' },
        { id: 'q5_3', text: 'Do you have data backup and recovery procedures?', deliverable: 'Data backup and disaster recovery plan', alternatives: 'Backup schedules, recovery testing, cloud storage proof' }
      ]
    },
    {
      id: 'area6',
      title: 'Human Resources & Capacity', 
      questions: [
        { id: 'q6_1', text: 'Do you have sufficient staffing for project delivery?', deliverable: 'Staffing plan and capacity documentation', alternatives: 'Org chart, staff qualifications, capacity analysis' },
        { id: 'q6_2', text: 'Are your team members properly trained and certified?', deliverable: 'Staff training records and certifications', alternatives: 'Professional licenses, training certificates, skills documentation' },
        { id: 'q6_3', text: 'Do you have employee onboarding and development programs?', deliverable: 'HR policies and training programs', alternatives: 'Employee handbook, training schedules, development plans' }
      ]
    },
    {
      id: 'area7',
      title: 'Performance Tracking & Reporting', 
      questions: [
        { id: 'q7_1', text: 'Do you have KPI tracking and reporting systems?', deliverable: 'Performance metrics and reporting tools', alternatives: 'KPI dashboards, performance reports, tracking systems' },
        { id: 'q7_2', text: 'Can you provide regular progress reports to clients?', deliverable: 'Client reporting templates and schedules', alternatives: 'Project status reports, communication plans, update protocols' },
        { id: 'q7_3', text: 'Do you maintain project documentation and deliverables?', deliverable: 'Project management system and documentation', alternatives: 'File organization system, deliverable tracking, archive procedures' }
      ]
    },
    {
      id: 'area8',
      title: 'Risk Management & Business Continuity', 
      questions: [
        { id: 'q8_1', text: 'Do you have a business continuity plan?', deliverable: 'Business continuity and disaster recovery plan', alternatives: 'Emergency procedures, contingency plans, recovery strategies' },
        { id: 'q8_2', text: 'Are you prepared for emergency situations and disruptions?', deliverable: 'Emergency response procedures', alternatives: 'Crisis management plan, emergency contacts, backup procedures' },
        { id: 'q8_3', text: 'Do you have appropriate liability and professional insurance?', deliverable: 'Professional liability insurance certificates', alternatives: 'Comprehensive business insurance, bonding capacity, risk coverage' }
      ]
    }
  ];

  const currentAreaData = assessmentAreas[currentArea];
  const isLastArea = currentArea === assessmentAreas.length - 1;

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));

    if (answer === 'no') {
      setSelectedQuestion(questionId);
      setShowResources(true);
    }
  };

  const getQuestion = (questionId) => {
    for (const area of assessmentAreas) {
      const question = area.questions.find(q => q.id === questionId);
      if (question) return question;
    }
    return null;
  };

  const nextArea = () => {
    if (isLastArea) {
      // Calculate completion and redirect to home
      navigate('/home');
    } else {
      setCurrentArea(currentArea + 1);
    }
  };

  const previousArea = () => {
    if (currentArea > 0) {
      setCurrentArea(currentArea - 1);
    }
  };

  const handleGetHelp = (questionId, area_id) => {
    const question = getQuestion(questionId);
    navigate(`/matching?area_id=${area_id}&desc=${encodeURIComponent(question.text)}`);
  };

  if (showResources && selectedQuestion) {
    const question = getQuestion(selectedQuestion);
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-4">Resources for: {question.text}</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Free Resources */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h3 className="font-semibold text-green-800">Free Resources</h3>
              </div>
              <div className="space-y-3">
                <div className="text-sm text-green-700">
                  <strong>Required Deliverable:</strong> {question.deliverable}
                </div>
                <div className="text-sm text-green-700">
                  <strong>Acceptable Alternatives:</strong> {question.alternatives}
                </div>
                <div className="bg-white rounded p-3 text-sm text-slate-600">
                  <div className="space-y-2">
                    <div className="font-medium">Free Resources Available:</div>
                    <ul className="list-disc list-inside space-y-1 text-xs">
                      <li>SBA.gov procurement resources and guides</li>
                      <li>SCORE business mentoring and templates</li>
                      <li>Local PTAC (Procurement Technical Assistance Center)</li>
                      <li>Industry association guidance and checklists</li>
                    </ul>
                  </div>
                </div>
              </div>
              <button 
                className="btn w-full mt-4 bg-green-600 hover:bg-green-700 text-white"
                onClick={() => {
                  // Mark as using free resources and continue
                  setAnswers(prev => ({
                    ...prev,
                    [selectedQuestion]: 'free_resources'
                  }));
                  setShowResources(false);
                }}
              >
                Use Free Resources
              </button>
            </div>

            {/* Provider Help */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <h3 className="font-semibold text-blue-800">Professional Help</h3>
              </div>
              <div className="space-y-3">
                <div className="text-sm text-blue-700">
                  Get matched with qualified service providers who can help you complete this requirement professionally.
                </div>
                <div className="bg-white rounded p-3">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Your Budget Range
                  </label>
                  <select className="input w-full">
                    <option value="">Select budget range</option>
                    <option value="under-500">Under $500</option>
                    <option value="500-1000">$500 - $1,000</option>
                    <option value="1000-2500">$1,000 - $2,500</option>
                    <option value="2500-5000">$2,500 - $5,000</option>
                    <option value="over-5000">Over $5,000</option>
                  </select>
                </div>
              </div>
              <button 
                className="btn btn-primary w-full mt-4"
                onClick={() => handleGetHelp(selectedQuestion, currentAreaData.id)}
              >
                Get Provider Help
              </button>
            </div>
          </div>

          <div className="mt-6 flex justify-center">
            <button 
              className="btn" 
              onClick={() => setShowResources(false)}
            >
              Continue Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm border">
        {/* Progress Header */}
        <div className="border-b p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Small Business Maturity Assessment</h2>
            <div className="flex items-center gap-4">
              <button
                className="btn btn-sm"
                onClick={() => setShowAreaNavigation(!showAreaNavigation)}
              >
                Jump to Area
              </button>
              <div className="text-sm text-slate-600">
                Area {currentArea + 1} of {assessmentAreas.length}
              </div>
            </div>
          </div>
          
          {/* Area Navigation Dropdown */}
          {showAreaNavigation && (
            <div className="mb-4 bg-slate-50 rounded-lg p-4">
              <h3 className="font-medium text-slate-900 mb-3">Jump to Business Area:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {assessmentAreas.map((area, index) => (
                  <button
                    key={area.id}
                    className={`p-3 rounded-lg text-left transition-colors ${
                      currentArea === index 
                        ? 'bg-blue-100 text-blue-900 border border-blue-300' 
                        : 'bg-white hover:bg-slate-100 border border-slate-200'
                    }`}
                    onClick={() => {
                      setCurrentArea(index);
                      setShowAreaNavigation(false);
                    }}
                  >
                    <div className="font-medium text-sm">Area {index + 1}</div>
                    <div className="text-xs text-slate-600">{area.title}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-[#1B365D] to-[#4A90C2] h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentArea + 1) / assessmentAreas.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Current Area */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">{currentAreaData.title}</h3>
          
          <div className="space-y-4">
            {currentAreaData.questions.map((question, index) => (
              <div key={question.id} className="bg-slate-50 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 mb-2">
                      {index + 1}. {question.text}
                    </p>
                    <div className="text-xs text-slate-600 mb-3">
                      <strong>Deliverable:</strong> {question.deliverable}
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-3 mb-3">
                  <button 
                    className={`btn btn-sm ${answers[question.id] === 'yes' ? 'btn-primary' : 'border'}`}
                    onClick={() => handleAnswer(question.id, 'yes')}
                  >
                    Yes, I have this
                  </button>
                  <button 
                    className={`btn btn-sm ${answers[question.id] === 'no' ? 'bg-orange-600 text-white' : 'border'}`}
                    onClick={() => handleAnswer(question.id, 'no')}
                  >
                    No, I need help
                  </button>
                </div>

                {/* Evidence Upload Section */}
                {answers[question.id] === 'yes' && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        Upload Evidence (Optional)
                      </label>
                      <p className="text-xs text-green-700 mb-3">
                        Provide documentation to support your claim and strengthen your assessment score.
                      </p>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="border-2 border-dashed border-green-300 rounded-lg p-4 text-center hover:border-green-400 transition-colors">
                        <input
                          type="file"
                          multiple
                          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                          className="hidden"
                          id={`evidence-${question.id}`}
                        />
                        <label htmlFor={`evidence-${question.id}`} className="cursor-pointer">
                          <svg className="w-8 h-8 text-green-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                          <div className="text-sm text-green-700 font-medium">Upload Documents</div>
                          <div className="text-xs text-green-600">PDF, DOC, JPG, PNG (Max 10MB each)</div>
                        </label>
                      </div>
                      
                      <div className="flex gap-2">
                        <button className="btn btn-sm text-green-700 border-green-300 hover:bg-green-100 flex-1">
                          📷 Take Photo
                        </button>
                        <button className="btn btn-sm text-green-700 border-green-300 hover:bg-green-100 flex-1">
                          📝 Add Note
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="border-t p-6 flex justify-between">
          <button 
            className="btn"
            onClick={previousArea}
            disabled={currentArea === 0}
          >
            Previous
          </button>
          <button 
            className="btn btn-primary"
            onClick={nextArea}
          >
            {isLastArea ? 'Complete Assessment' : 'Next Area'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------- Business Profile Form ----------------
function BusinessProfileForm(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  
  // Standardized dropdown options for data quality
  const dropdownOptions = {
    legal_entity_type: [
      'LLC', 'Corporation', 'Partnership', 'Sole Proprietorship', 'S-Corporation', 'Non-Profit', 'Other'
    ],
    industry: [
      'Technology', 'Healthcare', 'Manufacturing', 'Construction', 'Professional Services', 
      'Retail', 'Transportation', 'Finance', 'Education', 'Government', 'Non-Profit', 'Other'
    ],
    revenue_range: [
      'Under $100K', '$100K - $500K', '$500K - $1M', '$1M - $5M', '$5M - $10M', 'Over $10M'
    ],
    employees_count: [
      '1-5', '6-10', '11-25', '26-50', '51-100', '101-250', '251-500', '500+'
    ],
    ownership_structure: [
      'Private', 'Public', 'Family-Owned', 'Employee-Owned', 'Government', 'Non-Profit'
    ],
    contact_title: [
      'CEO', 'President', 'Owner', 'General Manager', 'Operations Manager', 'CFO', 'CTO', 'Other'
    ]
  };

  const [form, setForm] = useState({ 
    company_name:'', 
    legal_entity_type:'LLC', 
    tax_id:'', 
    registered_address:'', 
    website_url:'', 
    industry:'', 
    business_type: 'service', // Changed from primary_products_services to toggle
    business_description: '', // Detailed description of products/services
    revenue_range:'', 
    revenue_currency:'USD', 
    employees_count:'', 
    year_founded:'', 
    ownership_structure:'Private', 
    contact_name:'', 
    contact_title:'', 
    contact_email:'', 
    contact_phone:''
  });
  const [logo, setLogo] = useState(null);
  const [missing, setMissing] = useState([]);
  const [errors, setErrors] = useState({});
  const [isValidating, setIsValidating] = useState(false);

  // Validation patterns
  const validationPatterns = {
    email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    phone: /^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$/,
    ein: /^\d{2}-?\d{7}$/,
    website: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
    year: /^\d{4}$/
  };

  // Validation rules
  const validateField = (name, value) => {
    const errors = [];
    
    switch(name) {
      case 'company_name':
        if (!value.trim()) errors.push('Company name is required');
        else if (value.trim().length < 2) errors.push('Company name must be at least 2 characters');
        else if (value.trim().length > 100) errors.push('Company name must be less than 100 characters');
        break;
      
      case 'tax_id':
        if (!value.trim()) errors.push('Tax ID/EIN is required');
        else if (!validationPatterns.ein.test(value.replace(/-/g, ''))) errors.push('Invalid Tax ID/EIN format (e.g., 12-3456789)');
        break;
      
      case 'registered_address':
        if (!value.trim()) errors.push('Registered address is required');
        else if (value.trim().length < 10) errors.push('Address must be at least 10 characters');
        break;
      
      case 'website_url':
        if (value && !validationPatterns.website.test(value)) errors.push('Invalid website URL format');
        break;
      
      case 'industry':
        if (!value.trim()) errors.push('Industry is required');
        else if (value.trim().length < 2) errors.push('Industry must be at least 2 characters');
        break;
      
      case 'business_type':
        if (!value) errors.push('Business type is required');
        else if (!['product', 'service'].includes(value)) errors.push('Business type must be either product or service');
        break;
      
      case 'business_description':
        if (!value.trim()) errors.push('Business description is required');
        else if (value.trim().length < 10) errors.push('Business description must be at least 10 characters');
        else if (value.trim().length > 500) errors.push('Business description must be less than 500 characters');
        break;
      
      case 'revenue_range':
        if (!value.trim()) errors.push('Revenue range is required');
        break;
      
      case 'employees_count':
        if (!value.trim()) errors.push('Employee count is required');
        break;
      
      case 'year_founded':
        if (value && !validationPatterns.year.test(value)) errors.push('Invalid year format');
        else if (value && (parseInt(value) < 1800 || parseInt(value) > new Date().getFullYear())) {
          errors.push('Year founded must be between 1800 and current year');
        }
        break;
      
      case 'contact_name':
        if (!value.trim()) errors.push('Contact name is required');
        else if (value.trim().length < 2) errors.push('Contact name must be at least 2 characters');
        break;
      
      case 'contact_email':
        if (!value.trim()) errors.push('Contact email is required');
        else if (!validationPatterns.email.test(value)) errors.push('Invalid email format');
        break;
      
      case 'contact_phone':
        if (!value.trim()) errors.push('Contact phone is required');
        else if (!validationPatterns.phone.test(value)) errors.push('Invalid phone format (e.g., (123) 456-7890)');
        break;
      
      case 'billing_contact_email':
        if (value && !validationPatterns.email.test(value)) errors.push('Invalid billing email format');
        break;
      
      case 'billing_contact_phone':
        if (value && !validationPatterns.phone.test(value)) errors.push('Invalid billing phone format (e.g., (123) 456-7890)');
        break;
    }
    
    return errors;
  };

  // Real-time validation
  const handleFieldChange = (name, value) => {
    // Format specific fields
    if (name === 'tax_id') {
      value = value.replace(/[^\d-]/g, '').replace(/^(\d{2})(\d{7})$/, '$1-$2');
    }
    if (name === 'contact_phone' || name === 'billing_contact_phone') {
      value = value.replace(/[^\d()-.\s]/g, '');
    }
    if (name === 'contact_email' || name === 'billing_contact_email') {
      value = value.toLowerCase().trim();
    }
    
    setForm({...form, [name]: value});
    
    // Validate field
    const fieldErrors = validateField(name, value);
    setErrors(prev => ({
      ...prev,
      [name]: fieldErrors.length > 0 ? fieldErrors[0] : null
    }));
  };

  // Validate all fields
  const validateForm = () => {
    const newErrors = {};
    let hasErrors = false;
    
    Object.keys(form).forEach(key => {
      const fieldErrors = validateField(key, form[key]);
      if (fieldErrors.length > 0) {
        newErrors[key] = fieldErrors[0];
        hasErrors = true;
      }
    });
    
    setErrors(newErrors);
    return !hasErrors;
  };

  useEffect(()=>{ 
    const load=async()=>{ 
      try{ 
        const {data} = await axios.get(`${API}/business/profile/me`); 
        if(data){ 
          setForm({ ...form, ...data, payment_methods: (data.payment_methods||[]).join(', ')});
        } 
        const c = await axios.get(`${API}/business/profile/me/completion`); 
        setMissing(c.data.missing||[]);
      }catch{} 
    }; 
    load(); 
  },[]);

  const save = async()=>{
    setIsValidating(true);
    
    if (!validateForm()) {
      toast.error('Please fix validation errors before saving');
      setIsValidating(false);
      return;
    }

    try{
      // Prepare payload with proper data types
      const payload = { 
        ...form, 
        website_url: form.website_url ? (form.website_url.startsWith('http') ? form.website_url : `https://${form.website_url}`) : null,
        year_founded: form.year_founded ? parseInt(form.year_founded) : null
      };
      
      const { data } = await axios.post(`${API}/business/profile`, payload); 
      toast.success('Profile saved', { description: data.company_name });
      
      if (logo){
        const init = await axios.post(`${API}/business/logo/initiate`, new URLSearchParams({ file_name: logo.name, total_size: String(logo.size), mime_type: logo.type }));
        const uploadId = init.data.upload_id; const chunkSize = init.data.chunk_size; const totalChunks = Math.ceil(logo.size / chunkSize);
        for(let i=0;i<totalChunks;i++){
          const start=i*chunkSize; const end=Math.min(start+chunkSize, logo.size); const blob=logo.slice(start,end); const fd=new FormData(); fd.append('upload_id', uploadId); fd.append('chunk_index', String(i)); fd.append('file', blob, `${logo.name}.part`); await fetch(`${API}/business/logo/chunk`, { method:'POST', body: fd }); }
        await axios.post(`${API}/business/logo/complete`, new URLSearchParams({ upload_id: uploadId, total_chunks: String(totalChunks) }));
      }
      
      // Navigate based on user role
      const currentUser = JSON.parse(localStorage.getItem('polaris_me')||'{}');
      if (currentUser && currentUser.role === 'client') {
        navigate('/assessment');
      } else {
        navigate('/home');
      }
    }catch(e){ 
      console.error('Business profile save error:', e);
      let errorMessage = 'Save failed';
      let errorDetails = e.message;
      
      if (e.response?.data) {
        if (typeof e.response.data === 'string') {
          errorDetails = e.response.data;
        } else if (e.response.data.detail) {
          if (Array.isArray(e.response.data.detail)) {
            errorDetails = e.response.data.detail.map(err => `${err.loc?.join('.')||'field'}: ${err.msg}`).join(', ');
          } else {
            errorDetails = e.response.data.detail;
          }
        }
      }
      
      toast.error(errorMessage, { description: errorDetails }); 
    }
    setIsValidating(false);
  };

  return (
    <div className="container max-w-4xl mt-6">
      <h2 className="text-xl font-semibold mb-1">Business Profile</h2>
      <p className="text-sm text-slate-600 mb-4">Complete these details to unlock your personalized dashboard.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Company Name */}
        <div>
          <input 
            className={`input ${errors.company_name ? 'border-red-500' : ''}`} 
            placeholder="Company Name *" 
            value={form.company_name} 
            onChange={e=>handleFieldChange('company_name', e.target.value)} 
          />
          {errors.company_name && <div className="error-message">{errors.company_name}</div>}
        </div>

        {/* Legal Entity Type */}
        <div>
          <select 
            className={`input ${errors.legal_entity_type ? 'border-red-500' : ''}`} 
            value={form.legal_entity_type} 
            onChange={e=>handleFieldChange('legal_entity_type', e.target.value)}
          >
            <option value="">Select Legal Entity Type *</option>
            {dropdownOptions.legal_entity_type.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.legal_entity_type && <div className="error-message">{errors.legal_entity_type}</div>}
        </div>

        {/* Tax ID */}
        <div>
          <input 
            className={`input ${errors.tax_id ? 'border-red-500' : ''}`} 
            placeholder="Federal Tax ID (EIN) *" 
            value={form.tax_id} 
            onChange={e=>handleFieldChange('tax_id', e.target.value)} 
          />
          {errors.tax_id && <div className="error-message">{errors.tax_id}</div>}
        </div>

        {/* Industry */}
        <div>
          <select 
            className={`input ${errors.industry ? 'border-red-500' : ''}`} 
            value={form.industry} 
            onChange={e=>handleFieldChange('industry', e.target.value)}
          >
            <option value="">Select Industry *</option>
            {dropdownOptions.industry.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.industry && <div className="error-message">{errors.industry}</div>}
        </div>

        {/* Registered Address */}
        <div className="md:col-span-2">
          <input 
            className={`input ${errors.registered_address ? 'border-red-500' : ''}`} 
            placeholder="Registered Business Address *" 
            value={form.registered_address} 
            onChange={e=>handleFieldChange('registered_address', e.target.value)} 
          />
          {errors.registered_address && <div className="error-message">{errors.registered_address}</div>}
        </div>

        {/* Website URL */}
        <div>
          <input 
            className={`input ${errors.website_url ? 'border-red-500' : ''}`} 
            placeholder="Website URL (optional)" 
            value={form.website_url} 
            onChange={e=>handleFieldChange('website_url', e.target.value)} 
          />
          {errors.website_url && <div className="error-message">{errors.website_url}</div>}
        </div>

        {/* Business Type Toggle */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Business Type *</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="business_type"
                value="product"
                checked={form.business_type === 'product'}
                onChange={e=>handleFieldChange('business_type', e.target.value)}
                className="mr-2"
              />
              Product-Based Business
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="business_type"
                value="service"
                checked={form.business_type === 'service'}
                onChange={e=>handleFieldChange('business_type', e.target.value)}
                className="mr-2"
              />
              Service-Based Business
            </label>
          </div>
          {errors.business_type && <div className="error-message">{errors.business_type}</div>}
        </div>

        {/* Business Description */}
        <div className="md:col-span-2">
          <textarea 
            className={`input ${errors.business_description ? 'border-red-500' : ''}`} 
            placeholder={`Describe your ${form.business_type === 'product' ? 'products' : 'services'} in detail *`}
            value={form.business_description} 
            onChange={e=>handleFieldChange('business_description', e.target.value)}
            rows="3"
          />
          {errors.business_description && <div className="error-message">{errors.business_description}</div>}
          <div className="text-xs text-slate-500 mt-1">
            Provide a detailed description of what your business offers (10-500 characters)
          </div>
        </div>

        {/* Revenue Range */}
        <div>
          <select 
            className={`input ${errors.revenue_range ? 'border-red-500' : ''}`} 
            value={form.revenue_range} 
            onChange={e=>handleFieldChange('revenue_range', e.target.value)}
          >
            <option value="">Select Annual Revenue *</option>
            {dropdownOptions.revenue_range.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.revenue_range && <div className="error-message">{errors.revenue_range}</div>}
        </div>

        {/* Employee Count */}
        <div>
          <select 
            className={`input ${errors.employees_count ? 'border-red-500' : ''}`} 
            value={form.employees_count} 
            onChange={e=>handleFieldChange('employees_count', e.target.value)}
          >
            <option value="">Select Employee Count *</option>
            {dropdownOptions.employees_count.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.employees_count && <div className="error-message">{errors.employees_count}</div>}
        </div>

        {/* Year Founded */}
        <div>
          <input 
            className={`input ${errors.year_founded ? 'border-red-500' : ''}`} 
            placeholder="Year Founded (optional)" 
            value={form.year_founded} 
            onChange={e=>handleFieldChange('year_founded', e.target.value)} 
          />
          {errors.year_founded && <div className="error-message">{errors.year_founded}</div>}
        </div>

        {/* Ownership Structure */}
        <div>
          <select 
            className={`input ${errors.ownership_structure ? 'border-red-500' : ''}`} 
            value={form.ownership_structure} 
            onChange={e=>handleFieldChange('ownership_structure', e.target.value)}
          >
            <option value="">Select Ownership Structure *</option>
            {dropdownOptions.ownership_structure.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.ownership_structure && <div className="error-message">{errors.ownership_structure}</div>}
        </div>

        {/* Contact Information Section */}
        <div className="md:col-span-2 mt-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Primary Contact Information</h3>
        </div>

        {/* Contact Name */}
        <div>
          <input 
            className={`input ${errors.contact_name ? 'border-red-500' : ''}`} 
            placeholder="Contact Name *" 
            value={form.contact_name} 
            onChange={e=>handleFieldChange('contact_name', e.target.value)} 
          />
          {errors.contact_name && <div className="error-message">{errors.contact_name}</div>}
        </div>

        {/* Contact Title */}
        <div>
          <select 
            className={`input ${errors.contact_title ? 'border-red-500' : ''}`} 
            value={form.contact_title} 
            onChange={e=>handleFieldChange('contact_title', e.target.value)}
          >
            <option value="">Select Title *</option>
            {dropdownOptions.contact_title.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          {errors.contact_title && <div className="error-message">{errors.contact_title}</div>}
        </div>

        {/* Contact Email */}
        <div>
          <input 
            className={`input ${errors.contact_email ? 'border-red-500' : ''}`} 
            placeholder="Contact Email *" 
            type="email"
            value={form.contact_email} 
            onChange={e=>handleFieldChange('contact_email', e.target.value)} 
          />
          {errors.contact_email && <div className="error-message">{errors.contact_email}</div>}
        </div>

        {/* Contact Phone */}
        <div>
          <input 
            className={`input ${errors.contact_phone ? 'border-red-500' : ''}`} 
            placeholder="Contact Phone *" 
            value={form.contact_phone} 
            onChange={e=>handleFieldChange('contact_phone', e.target.value)} 
          />
          {errors.contact_phone && <div className="error-message">{errors.contact_phone}</div>}
        </div>

        {/* Logo Upload Section */}
        <div className="md:col-span-2 mt-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Company Logo (Optional)</h3>
          <input 
            type="file" 
            accept="image/*" 
            onChange={e=>setLogo(e.target.files?.[0]||null)} 
            className="input"
          />
          <p className="text-xs text-slate-500 mt-1">Upload your company logo for a professional profile appearance.</p>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 flex justify-end">
        <button 
          className="btn btn-primary px-8"
          onClick={save}
          disabled={isValidating}
        >
          {isValidating ? 'Saving...' : 'Save Profile'}
        </button>
      </div>
    </div>
  );

}

// ---------------- Home Pages ----------------
function ClientHome(){
  const [data, setData] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [matchedServices, setMatchedServices] = useState([]);
  const navigate = useNavigate();
  useEffect(()=>{ 
    const load=async()=>{ 
      const {data} = await axios.get(`${API}/home/client`); 
      setData(data); 
      try{
        const certs = await axios.get(`${API}/client/certificates`);
        setCertificates(certs.data.certificates || []);
        
        // Load matched services for the client
        const services = await axios.get(`${API}/client/matched-services`);
        setMatchedServices(services.data.services || []);
      }catch{}
    }; 
    load(); 
  },[]);

  const downloadCertificate = async(certId) => {
    try{
      const response = await fetch(`${API}/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
      });
      if(!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Polaris_Certificate_${certId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Certificate downloaded');
    }catch(e){ toast.error('Download failed', { description: e.message }); }
  };

  const copyVerificationLink = async(certId) => {
    try{
      const link = `${window.location.origin}/verify/cert/${certId}`;
      await navigator.clipboard.writeText(link);
      toast.success('Verification link copied to clipboard');
    }catch(e){ toast.error('Failed to copy link', { description: e.message }); }
  };

  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  
  return (
    <div className="container mt-6">
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="border-b">
          <nav className="flex">
            <button
              className={`px-6 py-3 font-medium ${activeTab === 'overview' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`px-6 py-3 font-medium ${activeTab === 'services' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('services')}
            >
              Services
            </button>
            <button
              className={`px-6 py-3 font-medium ${activeTab === 'assessment' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('assessment')}
            >
              Assessment
            </button>
            <button
              className={`px-6 py-3 font-medium ${activeTab === 'certificates' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('certificates')}
            >
              Certificates
            </button>
            <button
              className={`px-6 py-3 font-medium ${activeTab === 'knowledge' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('knowledge')}
            >
              Knowledge Base
              <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">Premium</span>
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div>
              <div className="dashboard-grid">
                <div className="tile">
                  <div className="tile-title">
                    <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 714.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 713.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 710 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 710-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 713.138-3.138z" />
                    </svg>
                    Readiness Score
                  </div>
                  <div className="tile-num">{String(data.readiness || 0)}%</div>
                  <div className="tile-sub">Evidence-approved</div>
                </div>
                <div className="tile">
                  <div className="tile-title">
                    <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 811-1h2a1 1 0 811 1v5m-4 0h4" />
                    </svg>
                    Opportunities
                  </div>
                  <div className="tile-num">{String(data.opportunities || 0)}</div>
                  <div className="tile-sub">Available to you</div>
                </div>
                <div className="tile">
                  <div className="tile-title">
                    <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 714.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 713.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 710 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 710-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 713.138-3.138z" />
                    </svg>
                    Certificate
                  </div>
                  <div className="tile-num">{data.has_certificate? 'Yes' : 'No'}</div>
                  <div className="tile-sub">Download once issued</div>
                </div>
                <div className="tile cursor-pointer hover:bg-gray-50 transition-colors" onClick={()=>navigate('/assessment')}>
                  <div className="tile-title">
                    <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 812-2h2a2 2 0 812 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                    Assessment
                  </div>
                  <div className="tile-num">→</div>
                  <div className="tile-sub">Continue</div>
                </div>
              </div>
              
              <div className="mt-6 flex gap-3">
                  <button className="btn btn-primary" onClick={()=>navigate('/service-request')}>Request Service Provider</button>
                <button className="btn" onClick={()=>navigate('/assessment')}>Continue Assessment</button>
              </div>
            </div>
          )}

          {activeTab === 'services' && (
            <div>
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Matched Services</h3>
                <p className="text-slate-600">Service providers matched to help you complete procurement requirements</p>
              </div>
              
              {matchedServices.length > 0 ? (
                <div className="space-y-4">
                  {matchedServices.map((service, index) => (
                    <div key={index} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="font-semibold text-lg">{service.provider_name || `Service Provider ${index + 1}`}</h4>
                          <p className="text-slate-600">{service.service_type || 'Professional Services'}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-slate-500">Budget Range</div>
                          <div className="font-medium">{service.budget_range || '$500 - $2,500'}</div>
                        </div>
                      </div>
                      <div className="mb-4">
                        <div className="text-sm font-medium text-slate-700 mb-2">Service Areas:</div>
                        <div className="flex flex-wrap gap-2">
                          {(service.areas || ['Business Formation', 'Financial Operations', 'Legal Compliance']).map((area, i) => (
                            <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {area}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="mb-4">
                        <p className="text-sm text-slate-600">
                          {service.description || 'Professional services to help complete procurement readiness requirements with expert guidance and documentation support.'}
                        </p>
                      </div>
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <div className="flex items-center">
                            <svg className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                            </svg>
                            <span className="text-sm text-slate-600 ml-1">{service.rating || '4.8'} ({service.reviews || '12'} reviews)</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button className="btn btn-sm">View Details</button>
                          <button className="btn btn-sm btn-primary">Contact Provider</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg className="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 815.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 819.288 0M15 7a3 3 0 11-6 0 3 3 0 816 0zm6 3a2 2 0 11-4 0 2 2 0 814 0zM7 10a2 2 0 11-4 0 2 2 0 814 0z" />
                  </svg>
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No Services Matched Yet</h3>
                  <p className="text-slate-600 mb-4">We'll match you with qualified service providers based on your assessment needs.</p>
                  <button className="btn btn-primary" onClick={()=>navigate('/service-request')}>Find Service Providers</button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'assessment' && (
            <div>
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Assessment Progress</h3>
                <p className="text-slate-600">Complete your procurement readiness assessment across 8 key business areas</p>
              </div>
              
              {/* Assessment Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-sm text-blue-600 font-medium">Completed Areas</div>
                      <div className="text-xl font-bold text-blue-900">3 of 8</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-sm text-green-600 font-medium">Readiness Score</div>
                      <div className="text-xl font-bold text-green-900">{data?.readiness || 0}%</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-sm text-orange-600 font-medium">Areas Needing Attention</div>
                      <div className="text-xl font-bold text-orange-900">5</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Business Areas Progress */}
              <div className="space-y-4 mb-6">
                <h4 className="font-medium text-slate-900">Business Areas Progress</h4>
                {[
                  { id: 1, title: 'Business Formation & Registration', completion: 100, status: 'complete' },
                  { id: 2, title: 'Financial Operations & Management', completion: 85, status: 'in-progress' },
                  { id: 3, title: 'Legal & Contracting Compliance', completion: 100, status: 'complete' },
                  { id: 4, title: 'Quality Management & Standards', completion: 30, status: 'in-progress' },
                  { id: 5, title: 'Technology & Security Infrastructure', completion: 0, status: 'not-started' },
                  { id: 6, title: 'Human Resources & Capacity', completion: 0, status: 'not-started' },
                  { id: 7, title: 'Performance Tracking & Reporting', completion: 0, status: 'not-started' },
                  { id: 8, title: 'Risk Management & Business Continuity', completion: 100, status: 'complete' }
                ].map((area) => (
                  <div key={area.id} className="border rounded-lg p-4 hover:bg-slate-50 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                          area.status === 'complete' ? 'bg-green-100 text-green-800' :
                          area.status === 'in-progress' ? 'bg-orange-100 text-orange-800' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {area.id}
                        </div>
                        <div>
                          <div className="font-medium text-slate-900">{area.title}</div>
                          <div className="text-sm text-slate-600">
                            {area.status === 'complete' ? 'Complete' :
                             area.status === 'in-progress' ? 'In Progress' : 'Not Started'}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-900">{area.completion}%</div>
                        <div className="w-20 bg-slate-200 rounded-full h-2 mt-1">
                          <div 
                            className={`h-2 rounded-full transition-all ${
                              area.completion === 100 ? 'bg-green-500' :
                              area.completion > 0 ? 'bg-orange-500' : 'bg-slate-300'
                            }`}
                            style={{ width: `${area.completion}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* AI Insights for Compliance */}
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6 mb-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-purple-900 mb-2">AI Compliance Insights</h4>
                    <div className="space-y-3 text-sm text-purple-800">
                      <div className="bg-white/60 rounded p-3">
                        <div className="font-medium mb-1">🎯 Priority Recommendation</div>
                        <p>Focus on completing "Technology & Security Infrastructure" - this area is critical for government contracting and currently at 0% completion.</p>
                      </div>
                      <div className="bg-white/60 rounded p-3">
                        <div className="font-medium mb-1">📊 Gap Analysis</div>
                        <p>Your strongest areas are Business Formation (100%) and Legal Compliance (100%). Consider leveraging these strengths while addressing technology gaps.</p>
                      </div>
                      <div className="bg-white/60 rounded p-3">
                        <div className="font-medium mb-1">🚀 Quick Wins</div>
                        <p>Complete "Financial Operations" (currently 85%) to boost your overall readiness score significantly with minimal effort.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button 
                  className="btn btn-primary flex-1"
                  onClick={() => navigate('/assessment')}
                >
                  Continue Assessment
                </button>
                <button 
                  className="btn"
                  onClick={() => navigate('/service-request')}
                >
                  Get Provider Help
                </button>
              </div>
            </div>
          )}

          {activeTab === 'certificates' && (
            <div>
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Your Certificates</h3>
                <p className="text-slate-600">Download and share your procurement readiness certificates</p>
              </div>

              {certificates.length > 0 ? (
                <div className="space-y-4">
                  {certificates.map(cert => (
                    <div key={cert.id} className="certificate-card">
                      <div>
                        <div className="font-medium">{cert.title}</div>
                        <div className="text-sm text-slate-600">Readiness: {cert.readiness_percent}% • Issued: {cert.issued_at ? new Date(cert.issued_at).toLocaleDateString() : 'Unknown'}</div>
                      </div>
                      <div className="flex gap-2">
                        <button className="btn btn-sm" onClick={()=>downloadCertificate(cert.id)}>Download PDF</button>
                        <button className="btn btn-sm" onClick={()=>copyVerificationLink(cert.id)}>Copy verification link</button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg className="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 714.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 713.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 710 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 710-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 713.138-3.138z" />
                  </svg>
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No Certificates Yet</h3>
                  <p className="text-slate-600 mb-4">Complete your assessment to earn procurement readiness certificates.</p>
                  <button className="btn btn-primary" onClick={()=>navigate('/assessment')}>Start Assessment</button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'knowledge' && (
            <div>
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Knowledge Base</h3>
                    <p className="text-slate-600">AI-powered templates and guidance for procurement readiness compliance</p>
                  </div>
                  <div className="bg-purple-100 border border-purple-300 rounded-lg px-4 py-2">
                    <div className="text-sm font-medium text-purple-900">Premium Feature</div>
                    <div className="text-xs text-purple-700">$20/area or $100 all areas</div>
                  </div>
                </div>
              </div>

              {/* Knowledge Base Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { 
                    id: 1, 
                    title: 'Business Formation & Registration', 
                    price: 20, 
                    unlocked: true, // Don't lock for test users
                    templates: ['Business License Application Template', 'Articles of Incorporation Guide', 'EIN Registration Walkthrough'],
                    guidance: 'Complete step-by-step guidance for legal business formation'
                  },
                  { 
                    id: 2, 
                    title: 'Financial Operations & Management', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Chart of Accounts Template', 'Financial Statement Template', 'Cash Flow Projection'],
                    guidance: 'Professional accounting setup and financial management systems'
                  },
                  { 
                    id: 3, 
                    title: 'Legal & Contracting Compliance', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Service Agreement Template', 'Terms & Conditions Template', 'Compliance Checklist'],
                    guidance: 'Legal templates and compliance frameworks for contractors'
                  },
                  { 
                    id: 4, 
                    title: 'Quality Management & Standards', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Quality Control Procedures', 'ISO 9001 Checklist', 'Quality Assurance Plan'],
                    guidance: 'Quality management systems and certification processes'
                  },
                  { 
                    id: 5, 
                    title: 'Technology & Security Infrastructure', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Cybersecurity Policy Template', 'Data Backup Plan', 'IT Security Checklist'],
                    guidance: 'Complete cybersecurity and technology infrastructure guide'
                  },
                  { 
                    id: 6, 
                    title: 'Human Resources & Capacity', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Employee Handbook Template', 'Training Program Guide', 'Capacity Planning Tool'],
                    guidance: 'HR policies and workforce capacity management'
                  },
                  { 
                    id: 7, 
                    title: 'Performance Tracking & Reporting', 
                    price: 20, 
                    unlocked: true,
                    templates: ['KPI Dashboard Template', 'Progress Report Template', 'Performance Metrics Guide'],
                    guidance: 'Performance measurement and reporting systems'
                  },
                  { 
                    id: 8, 
                    title: 'Risk Management & Business Continuity', 
                    price: 20, 
                    unlocked: true,
                    templates: ['Risk Assessment Template', 'Business Continuity Plan', 'Emergency Response Guide'],
                    guidance: 'Comprehensive risk management and continuity planning'
                  }
                ].map((area) => (
                  <div key={area.id} className={`border rounded-lg p-6 ${area.unlocked ? 'bg-white' : 'bg-slate-50 opacity-75'}`}>
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-slate-900">{area.title}</h4>
                      {area.unlocked ? (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Unlocked</span>
                      ) : (
                        <span className="text-xs bg-slate-200 text-slate-600 px-2 py-1 rounded-full">${area.price}</span>
                      )}
                    </div>
                    
                    <p className="text-sm text-slate-600 mb-4">{area.guidance}</p>
                    
                    {area.unlocked ? (
                      <div className="space-y-3">
                        <div>
                          <div className="text-xs font-medium text-slate-700 mb-2">Available Templates:</div>
                          <ul className="space-y-1">
                            {area.templates.map((template, idx) => (
                              <li key={idx} className="flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                <span className="text-slate-700">{template}</span>
                                <button className="ml-auto text-blue-600 hover:text-blue-700 text-xs">Download</button>
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="flex gap-2 pt-2">
                          <button className="btn btn-sm btn-primary flex-1">
                            AI Guidance
                          </button>
                          <button className="btn btn-sm flex-1">
                            View Templates
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <div className="text-sm text-slate-600 mb-3">Unlock AI-powered templates and guidance</div>
                        <button className="btn btn-primary btn-sm">
                          Unlock for ${area.price}
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              {/* Bulk Purchase Option */}
              <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                <div className="text-center">
                  <h4 className="font-semibold text-purple-900 mb-2">Unlock All Areas</h4>
                  <p className="text-purple-700 mb-4">Get complete access to all 8 business areas with AI guidance and templates</p>
                  <div className="flex items-center justify-center gap-4 mb-4">
                    <span className="text-sm text-slate-500 line-through">$160 individual</span>
                    <span className="text-2xl font-bold text-purple-900">$100</span>
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium">38% OFF</span>
                  </div>
                  <button className="btn btn-primary px-8">
                    Unlock All Areas - $100
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ProviderHome(){
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/provider`); setData(data); }; load(); },[]);
  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="tile"><div className="tile-title">Eligible Requests</div><div className="tile-num">{String(data.eligible_requests || 0)}</div><div className="tile-sub">by expertise</div></div>
        <div className="tile"><div className="tile-title">Responses</div><div className="tile-num">{String(data.responses || 0)}</div><div className="tile-sub">submitted</div></div>
        <div className="tile"><div className="tile-title">Profile</div><div className="tile-num">✓</div><div className="tile-sub">Complete</div></div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/provider/proposals')}>Open Proposal Composer</button>
      </div>
    </div>
  );
}

function NavigatorHome(){
  const [data, setData] = useState(null);
  const [pendingProviders, setPendingProviders] = useState([]);
  const navigate = useNavigate();
  
  useEffect(()=>{ 
    const load=async()=>{ 
      try{
        const {data} = await axios.get(`${API}/home/navigator`); 
        setData(data);
        
        // Load pending providers for approval
        const providersRes = await axios.get(`${API}/navigator/providers/pending`);
        setPendingProviders(providersRes.data.providers || []);
      }catch(e){
        console.error('Navigator home load error:', e);
      }
    }; 
    load(); 
  },[]);

  const approveProvider = async(providerId, status, notes = '') => {
    try{
      await axios.post(`${API}/navigator/providers/approve`, {
        provider_user_id: providerId,
        approval_status: status,
        notes: notes
      });
      
      toast.success(`Provider ${status === 'approved' ? 'approved' : 'rejected'} successfully`);
      
      // Refresh pending providers
      const providersRes = await axios.get(`${API}/navigator/providers/pending`);
      setPendingProviders(providersRes.data.providers || []);
    }catch(e){
      toast.error('Approval action failed', { description: e.message });
    }
  };

  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  
  return (
    <div className="container mt-6">
      <div className="dashboard-grid">
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Pending Reviews
          </div>
          <div className="tile-num">{String(data.pending_reviews || 0)}</div>
          <div className="tile-sub">awaiting review</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Provider Approvals
          </div>
          <div className="tile-num">{pendingProviders.length}</div>
          <div className="tile-sub">pending approval</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Active Engagements
          </div>
          <div className="tile-num">{String(data.active_engagements || 0)}</div>
          <div className="tile-sub">in progress</div>
        </div>
        <div className="tile cursor-pointer hover:bg-gray-50 transition-colors" onClick={()=>navigate('/navigator')}>
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Queue Management
          </div>
          <div className="tile-num">→</div>
          <div className="tile-sub">Open</div>
        </div>
      </div>

      {/* Provider Approval Section */}
      {pendingProviders.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Provider Approval Queue</h3>
          <div className="space-y-3">
            {pendingProviders.map(provider => (
              <div key={provider.id} className="certificate-card">
                <div className="flex-1">
                  <div className="font-medium">{provider.email}</div>
                  <div className="text-sm text-slate-600">
                    Role: Service Provider • 
                    Registered: {new Date(provider.created_at).toLocaleDateString()}
                  </div>
                  {provider.business_profile && (
                    <div className="text-sm text-slate-600 mt-1">
                      Company: {provider.business_profile.company_name} • 
                      Industry: {provider.business_profile.industry}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <button 
                    className="btn btn-sm bg-green-600 hover:bg-green-700 text-white"
                    onClick={()=>approveProvider(provider.id, 'approved')}
                  >
                    Approve
                  </button>
                  <button 
                    className="btn btn-sm bg-red-600 hover:bg-red-700 text-white"
                    onClick={()=>approveProvider(provider.id, 'rejected')}
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 flex gap-2">
        <Link className="btn btn-primary" to="/navigator">Open Review Queue</Link>
      </div>
    </div>
  );
}

function AgencyHome(){
  const [impact, setImpact] = useState(null);
  const [certificates, setCertificates] = useState([]);
  useEffect(()=>{ 
    const load=async()=>{ 
      const {data} = await axios.get(`${API}/home/agency`); 
      setImpact(data); 
      try{
        const certs = await axios.get(`${API}/agency/certificates`);
        setCertificates(certs.data.certificates || []);
      }catch{}
    }; 
    load(); 
  },[]);

  const downloadCertificate = async(certId) => {
    try{
      const response = await fetch(`${API}/certificates/${certId}/download`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
      });
      if(!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Polaris_Certificate_${certId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Certificate downloaded');
    }catch(e){ toast.error('Download failed', { description: e.message }); }
  };

  const copyVerificationLink = async(certId) => {
    try{
      const link = `${window.location.origin}/verify/cert/${certId}`;
      await navigator.clipboard.writeText(link);
      toast.success('Verification link copied to clipboard');
    }catch(e){ toast.error('Failed to copy link', { description: e.message }); }
  };

  // Calculate current tier based on invites
  const getTierInfo = () => {
    if (!impact) return { tier: 'Basic', price: 100, next: 'Volume' };
    const total = impact.invites.total || 0;
    if (total >= 100) return { tier: 'Enterprise', price: 60, next: null };
    if (total >= 25) return { tier: 'Growth', price: 75, next: 'Enterprise (100+ invites = $60 each)' };
    if (total >= 5) return { tier: 'Volume', price: 85, next: 'Growth (25+ invites = $75 each)' };
    return { tier: 'Basic', price: 100, next: 'Volume (5+ invites = $85 each)' };
  };

  if(!impact) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  
  const tierInfo = getTierInfo();
  
  return (
    <div className="container mt-6">
      {/* Enhanced Tier Banner */}
      <div className="tier-banner">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-semibold text-lg">{tierInfo.tier} Plan</div>
            <div className="text-blue-100">Current price: ${tierInfo.price} per invitation</div>
            {tierInfo.next && <div className="text-blue-200 text-sm mt-1">Next tier: {tierInfo.next}</div>}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{String(impact.invites?.total || 0)}</div>
            <div className="text-blue-100 text-sm">Total invitations</div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Total Invites
          </div>
          <div className="tile-num">{String(impact.invites?.total || 0)}</div>
          <div className="tile-sub">businesses engaged</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Paid Assessments
          </div>
          <div className="tile-num">{String(impact.invites?.paid || 0)}</div>
          <div className="tile-sub">completed assessments</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Revenue Generated
          </div>
          <div className="tile-num">${String(impact.revenue?.assessment_fees || 0)}</div>
          <div className="tile-sub">assessment fees</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            Opportunities
          </div>
          <div className="tile-num">{String(impact.opportunities?.count || 0)}</div>
          <div className="tile-sub">available contracts</div>
        </div>
      </div>

      {certificates.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Issued Certificates</h3>
          <div className="space-y-2">
            {certificates.map(cert => (
              <div key={cert.id} className="certificate-card">
                <div>
                  <div className="font-medium">{cert.title}</div>
                  <div className="text-sm text-slate-600">Client: {cert.client_user_id} • Readiness: {cert.readiness_percent}% • Issued: {cert.issued_at ? new Date(cert.issued_at).toLocaleDateString() : 'Unknown'}</div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-sm" onClick={()=>downloadCertificate(cert.id)}>Download PDF</button>
                  <button className="btn btn-sm" onClick={()=>copyVerificationLink(cert.id)}>Copy verification link</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex gap-2">
        <Link className="btn btn-primary" to="/agency">Open Agency Dashboard</Link>
      </div>
    </div>
  );
}

function HomeRouter(){
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  if(!me) return <Navigate to="/" replace />;
  if(me.role==='client') return <ClientHome/>;
  if(me.role==='provider') return <ProviderHome/>;
  if(me.role==='navigator') return <NavigatorHome/>;
  if(me.role==='agency') return <AgencyHome/>;
  return <Navigate to="/" replace />;
}

// ---------------- Matching with Accept → Engagement ----------------
function MatchingPage(){
  const location = useLocation();
  const [req, setReq] = useState({ budget: '', payment_pref: '', timeline: '', area_id: 'area6', description: '' });
  const [requestId, setRequestId] = useState('');
  const [matches, setMatches] = useState([]);
  const [responses, setResponses] = useState([]);
  const [agreedFee, setAgreedFee] = useState('');
  useEffect(()=>{
    const params = new URLSearchParams(location.search);
    const area = params.get('area_id'); const desc = params.get('desc');
    if (area || desc) setReq(prev=>({ ...prev, area_id: area || prev.area_id, description: desc || prev.description }));
  }, [location.search]);
  const createReq = async()=>{
    try{
      const payload = { ...req, budget: Number(req.budget) };
      const {data} = await axios.post(`${API}/match/request`, payload);
      setRequestId(data.request_id);
      toast.success('Request created');
      const r2 = await axios.get(`${API}/match/${data.request_id}/matches`); setMatches(r2.data.matches||[]);
      const r3 = await axios.get(`${API}/match/${data.request_id}/responses`); setResponses(r3.data.responses||[]);
    }catch(e){ toast.error('Create request failed'); }
  };
  const refresh = async()=>{
    if(!requestId) return;
    const r2 = await axios.get(`${API}/match/${requestId}/matches`); setMatches(r2.data.matches||[]);
    const r3 = await axios.get(`${API}/match/${requestId}/responses`); setResponses(r3.data.responses||[]);
  };
  const inviteTop5 = async()=>{ try{ await axios.post(`${API}/match/${requestId}/invite-top5`); toast.success('Invited top 5'); }catch{ toast.error('Invite failed'); } };
  const acceptResponse = async(resp)=>{
    try{
      const { data } = await axios.post(`${API}/engagements/create`, { request_id: requestId, response_id: resp.id || resp._id, agreed_fee: Number(agreedFee||0) });
      toast.success('Engagement created', { description: data.engagement_id });
      await refresh();
    }catch(e){ toast.error('Accept failed', { description: e?.response?.data?.detail || e.message }); }
  };
  return (
    <div className="container mt-6">
      <h2 className="text-lg font-semibold mb-3">Provider Matching</h2>
      {!requestId && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input className="input" placeholder="Budget" value={req.budget} onChange={e=>setReq({...req, budget:e.target.value})} />
          <input className="input" placeholder="Payment preference (optional)" value={req.payment_pref} onChange={e=>setReq({...req, payment_pref:e.target.value})} />
          <input className="input" placeholder="Timeline" value={req.timeline} onChange={e=>setReq({...req, timeline:e.target.value})} />
          <select className="input" value={req.area_id} onChange={e=>setReq({...req, area_id:e.target.value})}>
            <option value="area1">Business Formation & Registration</option>
            <option value="area2">Financial Operations</option>
            <option value="area3">Legal & Contracting</option>
            <option value="area4">Technology & Cybersecurity</option>
            <option value="area5">People & HR</option>
            <option value="area6">Marketing & Sales</option>
            <option value="area7">Procurement & Supply Chain</option>
            <option value="area8">Quality & Continuous Improvement</option>
          </select>
          <input className="input" placeholder="Short description" value={req.description} onChange={e=>setReq({...req, description:e.target.value})} />
        </div>
      )}
      {!requestId ? (<div className="mt-3"><button className="btn btn-primary" onClick={createReq}>Create request</button></div>) : (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2"><div className="text-sm text-slate-600">Top matches</div><div className="flex gap-2"><button className="btn" onClick={inviteTop5}>Invite top-5</button><button className="btn" onClick={refresh}>Refresh</button></div></div>
          <table className="table">
            <thead><tr><th>Company</th><th>Areas</th><th>Location</th><th>Price range</th><th>Score</th></tr></thead>
            <tbody>
              {matches.map(m => (
                <tr key={m.provider_id}><td>{m.company_name}</td><td>{(m.service_areas||[]).join(', ')}</td><td>{m.location||'-'}</td><td>{m.price_min||'-'} - {m.price_max||'-'}</td><td>{m.score}</td></tr>
              ))}
            </tbody>
          </table>
          <div className="mt-6">
            <div className="text-sm font-medium mb-2">Responses</div>
            <table className="table">
              <thead><tr><th>Response</th><th>Provider</th><th>Created</th><th>Agree fee</th><th>Action</th></tr></thead>
              <tbody>
                {responses.map(r => (
                  <tr key={r.id || r._id}><td className="max-w-md truncate" title={r.proposal_note}>{r.proposal_note||'-'}</td><td>{r.provider_user_id}</td><td>{r.created_at}</td><td><input className="input" style={{width:120}} placeholder="$" onChange={e=>setAgreedFee(e.target.value)} /></td><td><button className="btn btn-primary" onClick={()=>acceptResponse(r)}>Accept</button></td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------- Provider Proposal Composer ----------------
function ProviderProposalsPage(){
  const [eligible, setEligible] = useState([]);
  const [notes, setNotes] = useState({});
  const [attachments, setAttachments] = useState({}); // responseId -> files[] local
  const load = async()=>{ try{ const {data} = await axios.get(`${API}/match/eligible`); setEligible(data.requests||[]);}catch{} };
  useEffect(()=>{ load(); },[]);
  const respond = async(reqId)=>{
    try{
      const fd = new FormData(); fd.append('request_id', reqId); fd.append('proposal_note', notes[reqId] || '');
      const res = await fetch(`${API}/match/respond`, { method:'POST', body: fd });
      const data = await res.json();
      if(!data.ok){ toast.error(data.reason || 'Respond failed'); return; }
      toast.success('Response sent');
      if (data.response_id && attachments[reqId]?.length){
        for (const file of attachments[reqId]){
          const init = await fetch(`${API}/provider/proposals/upload/initiate`, { method:'POST', body: new URLSearchParams({ response_id: data.response_id, file_name: file.name, total_size: String(file.size), mime_type: file.type })});
          const initJson = await init.json(); const uploadId = initJson.upload_id; const chunkSize = initJson.chunk_size; const totalChunks = Math.ceil(file.size / chunkSize);
          for(let i=0;i<totalChunks;i++){
            const start=i*chunkSize; const end=Math.min(start+chunkSize, file.size); const blob=file.slice(start,end); const fd2=new FormData(); fd2.append('upload_id', uploadId); fd2.append('chunk_index', String(i)); fd2.append('file', blob, `${file.name}.part`); await fetch(`${API}/provider/proposals/upload/chunk`, { method:'POST', body: fd2 });
          }
          await fetch(`${API}/provider/proposals/upload/complete`, { method:'POST', body: new URLSearchParams({ upload_id: uploadId, total_chunks: String(totalChunks) })});
        }
      }
      setNotes(prev=>({ ...prev, [reqId]: '' })); setAttachments(prev=>({ ...prev, [reqId]: [] }));
      await load();
    }catch(e){ toast.error('Respond failed'); }
  };
  return (
    <div className="container mt-6">
      <h2 className="text-lg font-semibold mb-3">Proposal Composer</h2>
      <table className="table">
        <thead><tr><th>Area</th><th>Budget</th><th>Timeline</th><th>Invited</th><th>Proposal</th><th>Attachments</th><th>Action</th></tr></thead>
        <tbody>
          {eligible.map(r => (
            <tr key={r.id}>
              <td>{r.area_id}</td><td>{r.budget}</td><td>{r.timeline||'-'}</td><td>{r.invited ? 'Yes' : 'No'}</td>
              <td><input className="input" placeholder="Short proposal note" value={notes[r.id]||''} onChange={e=>setNotes(prev=>({ ...prev, [r.id]: e.target.value }))} /></td>
              <td><input type="file" multiple onChange={e=>{ const files = Array.from(e.target.files||[]); setAttachments(prev=>({ ...prev, [r.id]: files })); }} /></td>
              <td><button className="btn btn-primary" onClick={()=>respond(r.id)}>Send</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Header(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const logout = () => {
    localStorage.removeItem('polaris_token');
    localStorage.removeItem('polaris_me');
    delete axios.defaults.headers.common['Authorization'];
    toast.success('Logged out successfully');
    navigate('/');
  };

  return (
    <header className="professional-header">
      <div className="header-container">
        {/* Logo */}
        <div className="header-logo">
          <Link to={me ? '/home' : '/'}>
            <PolarisLogo size={24} />
          </Link>
        </div>

        {/* Professional Navigation */}
        {me && (
          <nav className="main-navigation">
            <Link className="nav-item" to="/home">
              <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z" />
              </svg>
              <span>Dashboard</span>
            </Link>
            
            {me.role === 'client' && (
              <Link className="nav-item" to="/matching">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span>Services</span>
              </Link>
            )}
            
            {me.role === 'client' && (
              <Link className="nav-item" to="/assessment">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                <span>Assessment</span>
              </Link>
            )}
            
            {me.role === 'provider' && (
              <Link className="nav-item" to="/provider/proposals">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Proposals</span>
              </Link>
            )}
            
            {me.role === 'navigator' && (
              <Link className="nav-item" to="/navigator">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                <span>Review Queue</span>
              </Link>
            )}
            
            {me.role === 'agency' && (
              <Link className="nav-item" to="/agency">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>Agency Portal</span>
              </Link>
            )}
          </nav>
        )}

        {/* User Menu */}
        <div className="header-actions">
          {!me ? (
            <a className="btn btn-primary" href="#auth">Sign In</a>
          ) : (
            <div className="user-menu-container">
              <button 
                className="user-menu-trigger"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <div className="user-avatar">
                  <span>{me.email?.charAt(0).toUpperCase()}</span>
                </div>
                <div className="user-info">
                  <div className="user-email">{me.email}</div>
                  <div className="user-role">{me.role}</div>
                </div>
                <svg className="chevron-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showUserMenu && (
                <div className="user-menu-dropdown">
                  <Link className="menu-item" to="/business/profile">
                    <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    Business Profile
                  </Link>
                  <Link className="menu-item" to="/settings">
                    <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Profile Settings
                  </Link>
                  {me.role === 'admin' && (
                    <Link className="menu-item" to="/admin">
                      <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Administration
                    </Link>
                  )}
                  <button className="menu-item logout-button" onClick={logout}>
                    <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function Landing(){
  return (
    <div>
      {/* Enhanced Hero Section */}
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-inner">
          <div className="flex-1 text-white">
            <PolarisLogo size={32} />
            <h1 className="hero-title mt-4">Your North Star for Procurement Readiness</h1>
            <p className="hero-sub">Transform your business into a government contracting powerhouse with our comprehensive readiness platform.</p>
            <div className="hero-ctas">
              <a className="btn btn-primary" href="#auth">Start Your Journey</a>
              <a className="btn bg-white/10 backdrop-blur border-white/20 text-white hover:bg-white/20" href="#auth">Sign In</a>
            </div>
          </div>
          <div className="w-[420px] max-w-full"><AuthWidget /></div>
        </div>
      </section>

      {/* Value Proposition for Each User Type */}
      <section className="container section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Built for Every Step of Your Procurement Journey</h2>
          <p className="text-slate-600 max-w-2xl mx-auto">Whether you're a small business, service provider, navigator, or local agency, Polaris provides tailored solutions for procurement readiness.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="user-segment">
            <div className="segment-icon bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="segment-title">Small Businesses</h3>
            <p className="segment-desc">Assess your readiness, get certified, and unlock government contracting opportunities.</p>
            <ul className="segment-features">
              <li>Comprehensive maturity assessment</li>
              <li>Public verification certificates</li>
              <li>Free resources and guidance</li>
            </ul>
          </div>

          <div className="user-segment">
            <div className="segment-icon bg-emerald-50">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="segment-title">Service Providers</h3>
            <p className="segment-desc">Connect with businesses needing your expertise and grow your client base.</p>
            <ul className="segment-features">
              <li>Automated client matching</li>
              <li>Proposal management system</li>
              <li>Engagement tracking</li>
            </ul>
          </div>

          <div className="user-segment">
            <div className="segment-icon bg-purple-50">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <h3 className="segment-title">Navigators</h3>
            <p className="segment-desc">Review assessments, validate evidence, and guide businesses to success.</p>
            <ul className="segment-features">
              <li>Evidence review queue</li>
              <li>Assessment validation tools</li>
              <li>Progress tracking</li>
            </ul>
          </div>

          <div className="user-segment">
            <div className="segment-icon bg-orange-50">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="segment-title">Local Agencies</h3>
            <p className="segment-desc">Invite businesses, manage assessments, and track community impact.</p>
            <ul className="segment-features">
              <li>Volume-based pricing tiers</li>
              <li>Impact dashboards</li>
              <li>Opportunity management</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Enhanced Features Section with High-Quality Images */}
      <section className="bg-slate-50 py-12">
        <div className="container">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-slate-900 mb-2">Comprehensive Procurement Readiness Platform</h2>
            <p className="text-slate-600">Everything you need to succeed in government contracting</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="feature-card">
              <div className="feature-image">
                <img src="https://images.unsplash.com/photo-1659035259667-b7ff7efe29dd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMGNoZWNrbGlzdHxlbnwwfHx8Ymx1ZXwxNzU1Mzg0OTU1fDA&ixlib=rb-4.1.0&q=85&w=600" alt="Assessment Checklist" className="w-full h-48 object-cover" />
              </div>
              <div className="p-6">
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Smart Assessment System</h3>
                <p className="text-slate-600 text-sm">Comprehensive evaluation across 8 key business areas with AI-powered guidance and concrete deliverables.</p>
                <ul className="mt-3 text-xs text-slate-500 space-y-1">
                  <li>• Evidence-based evaluation</li>
                  <li>• AI-generated free resources</li>
                  <li>• Real-time progress tracking</li>
                </ul>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-image">
                <img src="https://images.unsplash.com/photo-1660020619062-70b16c44bf0f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMGFuYWx5dGljc3xlbnwwfHx8Ymx1ZXwxNzU1Mjk0NjcyfDA&ixlib=rb-4.1.0&q=85&w=600" alt="Analytics Dashboard" className="w-full h-48 object-cover" />
              </div>
              <div className="p-6">
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Readiness Analytics</h3>
                <p className="text-slate-600 text-sm">Advanced analytics and reporting to track your procurement readiness journey and identify improvement areas.</p>
                <ul className="mt-3 text-xs text-slate-500 space-y-1">
                  <li>• Performance analytics</li>
                  <li>• Progress visualization</li>
                  <li>• Benchmark comparisons</li>
                </ul>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-image">
                <img src="https://images.unsplash.com/photo-1586281381264-de3d24d4fbd3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxidXNpbmVzcyUyMGNoZWNrbGlzdHxlbnwwfHx8Ymx1ZXwxNzU1Mzg0OTU1fDA&ixlib=rb-4.1.0&q=85&w=600" alt="Compliance Verification" className="w-full h-48 object-cover" />
              </div>
              <div className="p-6">
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Strategic Certification</h3>
                <p className="text-slate-600 text-sm">Earn publicly verifiable certificates that demonstrate your procurement readiness to government agencies.</p>
                <ul className="mt-3 text-xs text-slate-500 space-y-1">
                  <li>• Public verification system</li>
                  <li>• Government-recognized standards</li>
                  <li>• QR code authentication</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics and Impact */}
      <section className="container section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Driving Procurement Readiness</h2>
          <p className="text-slate-600">Built in partnership with the City of San Antonio's Small Business Assurance Program</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="stat-card">
            <div className="stat-number">8</div>
            <div className="stat-label">Assessment Areas</div>
            <div className="stat-desc">Comprehensive business evaluation</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">75%</div>
            <div className="stat-label">Readiness Threshold</div>
            <div className="stat-desc">For certificate eligibility</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">4</div>
            <div className="stat-label">User Types</div>
            <div className="stat-desc">Tailored experiences</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Platform Access</div>
            <div className="stat-desc">Always available</div>
          </div>
        </div>
      </section>

      {/* Terms and Privacy Policy Footer */}
      <section className="bg-slate-100 py-8">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Terms of Service</h3>
              <div className="text-sm text-slate-600 space-y-2 max-h-48 overflow-y-auto bg-white p-4 rounded border">
                <p><strong>1. Acceptance of Terms</strong></p>
                <p>By accessing and using the Polaris Small Business Procurement Readiness Platform, you accept and agree to be bound by the terms and provision of this agreement.</p>
                
                <p><strong>2. Platform Purpose</strong></p>
                <p>Polaris is designed to assess small business procurement readiness and connect businesses with qualified service providers and government contracting opportunities.</p>
                
                <p><strong>3. User Responsibilities</strong></p>
                <p>Users agree to provide accurate information, maintain the confidentiality of their account credentials, and use the platform in compliance with all applicable laws and regulations.</p>
                
                <p><strong>4. Service Provider Approval</strong></p>
                <p>All service providers must be approved by certified Digital Navigators before being added to the marketplace. Polaris reserves the right to remove any provider who fails to meet our quality standards.</p>
                
                <p><strong>5. Data Security</strong></p>
                <p>We implement industry-standard security measures including data encryption, access controls, and regular security audits to protect your information.</p>
                
                <p><strong>6. Limitation of Liability</strong></p>
                <p>Polaris provides the platform "as is" and makes no warranties regarding the accuracy of assessments or success in government contracting.</p>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Privacy Policy</h3>
              <div className="text-sm text-slate-600 space-y-2 max-h-48 overflow-y-auto bg-white p-4 rounded border">
                <p><strong>1. Information Collection</strong></p>
                <p>We collect business profile information, assessment responses, and usage analytics to provide personalized procurement readiness services.</p>
                
                <p><strong>2. Data Usage</strong></p>
                <p>Your data is used to: assess procurement readiness, match you with appropriate service providers, generate certificates, and improve our platform services.</p>
                
                <p><strong>3. Data Protection</strong></p>
                <p>All sensitive data is encrypted at rest and in transit using AES-256 encryption. We implement role-based access controls and conduct quarterly security audits.</p>
                
                <p><strong>4. Data Sharing</strong></p>
                <p>We do not sell your personal information. Data may be shared with approved service providers for engagement purposes and with government agencies for certification verification.</p>
                
                <p><strong>5. Compliance</strong></p>
                <p>Our platform complies with NIST cybersecurity frameworks, FISMA requirements, and applicable data protection regulations including CCPA and GDPR principles.</p>
                
                <p><strong>6. Data Retention</strong></p>
                <p>Business profiles and assessment data are retained for 7 years to support ongoing certification verification and compliance auditing.</p>
                
                <p><strong>7. Your Rights</strong></p>
                <p>You have the right to access, update, or delete your personal information. Contact support for data requests or privacy concerns.</p>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-slate-300 text-center text-xs text-slate-500">
            <p>© 2025 Polaris Small Business Procurement Readiness Platform • Built in partnership with the City of San Antonio</p>
            <p className="mt-1">By using this platform, you agree to our Terms of Service and Privacy Policy</p>
          </div>
        </div>
      </section>
    </div>
  );
}

function AppShell(){
  useAuthHeader();
  const location = useLocation();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const showLanding = location.pathname === '/' && !me;
  return (
    <div className="app-shell">
      <Header />
      {showLanding ? (
        <Landing />
      ) : (
        <Routes>
          <Route path="/verify/cert/:id" element={<VerifyCert />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<ProfileSettings />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/home" element={<HomeRouter />} />
          <Route path="/business/profile" element={<BusinessProfileForm />} />
          <Route path="/matching" element={<MatchingPage />} />
          <Route path="/provider/proposals" element={<ProviderProposalsPage />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/" element={<Navigate to={me?'/home':'/'} replace />} />
        </Routes>
      )}
      <Toaster richColors position="top-center" />
    </div>
  );
}

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }