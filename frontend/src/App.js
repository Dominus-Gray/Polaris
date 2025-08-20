import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { Toaster, toast } from "sonner";
import ProfileSettings from "./components/ProfileSettings";
import AdminDashboard from "./components/AdminDashboard";
import 'uplot/dist/uPlot.min.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PolarisLogo({ size = 22, variant = 'default' }) {
  const logoColor = variant === 'white' ? '#ffffff' : '#0F172A';
  const starColor = variant === 'white' ? '#ffffff' : '#2563EB';
  return (
    <div className={`polaris-logo-container ${variant === 'large' ? 'logo-large' : ''}`} style={{ minWidth: size, minHeight: size }}>
      <svg width={size} height={size} viewBox="0 0 48 48" fill="none" className="drop-shadow-sm">
        {/* Crisp North Star */}
        <g filter="url(#glow)">
          <path d="M24 4l2.18 12.52L39 13l-11.3 8.3L44 24l-16.3 2.7L35 35l-8.48-11.3L24 44l-2.7-16.3L13 35l8.3-11.3L4 24l16.7-2.7L13 13l12.52 3.7L24 4z" fill={starColor} />
        </g>
        <defs>
          <filter id="glow" x="0" y="0" width="48" height="48" filterUnits="userSpaceOnUse">
            <feGaussianBlur stdDeviation="0.5" />
          </filter>
        </defs>
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

function EnhancedPolarisBrand() {
  const [fallback, setFallback] = useState(false);
  return (
    <div className="enhanced-brand flex items-center justify-center gap-3">
      {!fallback ? (
        <img
          src="/polaris-logo-lockup-hero.svg"
          alt="Polaris – Procurement Readiness"
          className="h-12 md:h-14 w-auto drop-shadow-lg"
          onError={() => setFallback(true)}
        />
      ) : (
        <PolarisLogo size={40} variant="white" />
      )}
      <div className="brand-wordmark">
        <div className="brand-name">POLARIS</div>
        <div className="brand-sub">Procurement Readiness</div>
      </div>
    </div>
  );
}

function useAuthHeader(){
  useEffect(()=>{
    const t = localStorage.getItem('polaris_token');
    if (t) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${t}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  },[]);
  
  // Also set up a listener for localStorage changes to update auth header
  useEffect(() => {
    const handleStorageChange = () => {
      const t = localStorage.getItem('polaris_token');
      if (t) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${t}`;
      } else {
        delete axios.defaults.headers.common['Authorization'];
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);
}

function AuthWidget({ selectedRole = null, onBackToRoleSelection = null }){
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [licenseCode, setLicenseCode] = useState(''); // 10-digit license code for business clients
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

  const roleOptions = [
    {
      id: 'client',
      title: 'Small Business Client',
      description: 'Get assessed for procurement readiness and access service providers',
      requirements: 'Requires 10-digit license code from your local agency',
      features: ['Maturity assessment', 'Readiness certification', 'Service requests', 'Knowledge base access'],
      icon: '🏢'
    },
    {
      id: 'agency', 
      title: 'Local Agency',
      description: 'Invite businesses and distribute assessment licenses',
      requirements: 'Subject to verification and approval by Digital Navigators',
      features: ['License distribution', 'Opportunity forecasting', 'Business dashboards', 'Volume pricing'],
      icon: '🏛️'
    },
    {
      id: 'provider',
      title: 'Service Provider', 
      description: 'Offer services to help businesses achieve procurement readiness',
      requirements: 'Subject to vetting and approval by Digital Navigators',
      features: ['Service marketplace', 'Client matching', 'Payment processing', 'Performance tracking'],
      icon: '🔧'
    },
    {
      id: 'navigator',
      title: 'Digital Navigator',
      description: 'Platform administrators - review, approve, and guide businesses',
      requirements: 'Polaris team members only',
      features: ['Evidence review', 'Provider approval', 'Quality assurance', 'Platform management'],
      icon: '👥'
    }
  ];
  
  const submit = async()=>{
    if (mode === 'register' && !termsAccepted) {
      toast.error('Please accept the Terms of Service and Privacy Policy to continue');
      return;
    }
    
    // Validate license code for business clients
    if (mode === 'register' && selectedRole === 'client' && !licenseCode.trim()) {
      toast.error('10-digit license code is required for business client registration');
      return;
    }
    
    if (mode === 'register' && selectedRole === 'client' && licenseCode.length !== 10) {
      toast.error('License code must be exactly 10 digits');
      return;
    }
    
    // Validate payment information for clients and providers (not agencies or navigators)
    if (mode === 'register' && ['client', 'provider'].includes(selectedRole)) {
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
          role: selectedRole, 
          terms_accepted: termsAccepted,
          ...(selectedRole === 'client' && { license_code: licenseCode }),
          ...((['client', 'provider'].includes(selectedRole)) && { payment_info: paymentInfo })
        };
        
        await axios.post(`${API}/auth/register`, registrationData);
        
        // Show appropriate success message based on role
        let successMessage = 'Registration successful';
        let description = 'Please sign in with your credentials';
        
        if (selectedRole === 'client') {
          description = 'Welcome! Please sign in to begin your assessment';
        } else if (selectedRole === 'agency') {
          description = 'Your application has been submitted for review by Digital Navigators. You will be notified once approved.';
        } else if (selectedRole === 'provider') {
          description = 'Your application has been submitted for vetting by Digital Navigators. You will be notified once approved.';
        } else if (selectedRole === 'navigator') {
          description = 'Navigator registration complete. Please sign in to access platform administration.';
        }
        
        toast.success(successMessage, { description });
        setMode('login');
      } else {
        const { data } = await axios.post(`${API}/auth/login`, { email, password });
        localStorage.setItem('polaris_token', data.access_token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
        const me = await axios.get(`${API}/auth/me`);
        localStorage.setItem('polaris_me', JSON.stringify(me.data));
        
        // Handle pending approval states
        if (me.data.approval_status === 'pending') {
          toast.info('Account Pending Approval', { 
            description: `Your ${me.data.role} application is under review by Digital Navigators. You will be notified once approved.` 
          });
          // Don't navigate, show pending state
          return;
        } else if (me.data.approval_status === 'rejected') {
          toast.error('Application Rejected', { 
            description: 'Your application was not approved. Please contact support for more information.' 
          });
          return;
        }
        
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

  // Login/Register Form
  return (
    <div className="auth-widget" id="auth">
      <div className="bg-white rounded-lg p-6 shadow-lg border">
        {selectedRole && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-lg">{roleOptions.find(r => r.id === selectedRole)?.icon}</span>
              <span className="font-medium text-blue-900">
                {roleOptions.find(r => r.id === selectedRole)?.title}
              </span>
              {onBackToRoleSelection && (
                <button 
                  className="ml-auto text-blue-600 hover:text-blue-700 text-sm"
                  onClick={onBackToRoleSelection}
                >
                  Change
                </button>
              )}
            </div>
          </div>
        )}
        
        <h3 className="font-semibold text-slate-900 mb-4 text-center">
          {mode === 'register' ? 'Create Account' : 'Sign In'}
        </h3>
        
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
              <option value="login">Sign In</option>
              {selectedRole && <option value="register">Register</option>}
            </select>
            {!selectedRole && mode === 'login' && onBackToRoleSelection && (
              <button 
                className="btn"
                onClick={onBackToRoleSelection}
                disabled={isSubmitting}
              >
                Register
              </button>
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
          
          {/* License Code for Business Clients */}
          {mode === 'register' && selectedRole === 'client' && (
            <div>
              <input 
                className="input w-full" 
                placeholder="10-Digit License Code from Local Agency *" 
                value={licenseCode} 
                onChange={e=>setLicenseCode(e.target.value.replace(/\D/g, '').slice(0, 10))}
                disabled={isSubmitting}
                maxLength={10}
              />
              <div className="text-xs text-slate-500 mt-1">
                Contact your local agency to obtain a license code for business client registration
              </div>
            </div>
          )}
          
          {/* Payment Information for Clients and Providers */}
          {mode === 'register' && ['client', 'provider'].includes(selectedRole) && (
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
                {selectedRole === 'client' ? 'Payment will be processed only when you select service providers' :
                 'Card will be charged only when you receive approved service requests'}
              </div>
            </div>
          )}
          
          {/* Special Notice for Agencies and Providers */}
          {mode === 'register' && ['agency', 'provider'].includes(selectedRole) && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded">
              <div className="text-sm font-medium text-amber-800 mb-1">
                {selectedRole === 'agency' ? 'Agency Verification Required' : 'Provider Vetting Required'}
              </div>
              <div className="text-xs text-amber-700">
                {selectedRole === 'agency' 
                  ? 'Your registration will be reviewed by Digital Navigators. You will be notified once your agency is verified and approved.'
                  : 'Your application will be vetted by Digital Navigators to ensure service quality. You will be notified once approved to join the marketplace.'
                }
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
                I agree to the <strong>Terms of Service</strong> and <strong>Privacy Policy</strong>. I understand that {
                  selectedRole === 'agency' ? 'agencies must be verified by Digital Navigators before distribution of licenses' :
                  selectedRole === 'provider' ? 'service providers must be approved by Digital Navigators before joining the marketplace' :
                  selectedRole === 'client' ? 'business clients require valid license codes from local agencies' :
                  'digital navigators are platform administrators'
                }.
              </label>
            </div>
          )}
          
          <button 
            className="btn btn-primary w-full" 
            onClick={submit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Processing...' : (mode === 'register' ? 'Create Account' : 'Sign In')}
          </button>
          
          {!selectedRole && mode === 'login' && onBackToRoleSelection && (
            <div className="text-center mt-3">
              <button 
                className="text-blue-600 hover:text-blue-700 text-sm"
                onClick={onBackToRoleSelection}
              >
                New user? Select your role to register
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Google OAuth Modal */}
      {showOAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h4 className="font-semibold text-slate-900 mb-3">Continue with Google</h4>
            <p className="text-sm text-slate-600 mb-4">
              You will be redirected to Google to sign in securely. After authentication, you'll return to complete your profile setup.
            </p>
            <div className="flex gap-3">
              <button
                className="btn flex-1"
                onClick={() => setShowOAuthModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary flex-1"
                onClick={proceedWithGoogleAuth}
              >
                Proceed
              </button>
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
            <p className="processing-subtitle">Your North Star for Small Business Procurement Readiness</p>
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
            <img src="/polaris-lockup-premium-light.svg" alt="Polaris" className="h-10 w-auto"/>
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
                <li>Service requests</li>
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

  const handleAnswer = async (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));

    // Save answer to backend immediately
    try {
      await axios.post(`${API}/assessment/answer`, {
        question_id: questionId,
        answer: answer
      });
    } catch (e) {
      console.error('Failed to save answer:', e);
    }

    if (answer === 'no_help') {
      setSelectedQuestion(questionId);
      setShowResources(true);
    }
  };

  const handleEvidenceUpload = async (questionId, files) => {
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('question_id', questionId);
    
    for (let file of files) {
      formData.append('files', file);
    }

    try {
      const response = await axios.post(`${API}/assessment/evidence`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      toast.success(`Successfully uploaded ${response.data.files.length} evidence files`);
    } catch (e) {
      toast.error('Failed to upload evidence', { description: e.response?.data?.detail || e.message });
    }
  };

  const handleProfessionalHelp = async (questionId, areaId, budgetRange) => {
    try {
      const response = await axios.post(`${API}/service-requests/professional-help`, {
        area_id: areaId,
        budget_range: budgetRange,
        description: `Professional help needed for: ${getQuestion(questionId)?.text}`
      });
      
      toast.success('Service request created!', { 
        description: `Notified ${response.data.notified_providers} matching providers` 
      });
      
      // Navigate to services page
      navigate('/service-request');
    } catch (e) {
      toast.error('Failed to create service request', { description: e.response?.data?.detail || e.message });
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
    // Navigate to the new Service Request flow with context params
    navigate(`/service-request?area_id=${area_id}&from=assessment&question=${encodeURIComponent(question.text)}`);
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
                onClick={async () => {
                  // Keep answer as 'no_help' (gap remains) and log analytics
                  try {
                    await axios.post(`${API}/analytics/resource-access`, {
                      resource_id: `free_resources_${selectedQuestion}`,
                      gap_area: currentAreaData.id
                    });
                    toast.success('Free resources logged');
                    navigate('/free-resources');
                  } catch (e) {
                    console.warn('Analytics logging failed', e);
                    toast.error('Could not log to analytics');
                  }
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
          
          <div className="space-y-6">
            {currentAreaData.questions.map((question, index) => (
              <div key={question.id} className="card-enhanced p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold">
                        {index + 1}
                      </span>
                      <h4 className="text-base font-semibold text-slate-900 leading-relaxed">
                        {question.text}
                      </h4>
                    </div>
                    
                    <div className="ml-11">
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                        <div className="text-xs font-medium text-blue-800 mb-1">Required Deliverable:</div>
                        <div className="text-sm text-blue-700">{question.deliverable}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="ml-11">
                  <div className="flex gap-3 mb-4">
                    <button 
                      className={`btn btn-sm transition-all duration-200 ${
                        answers[question.id] === 'yes' 
                          ? 'btn-primary shadow-lg' 
                          : 'border border-green-300 hover:bg-green-50 text-green-700'
                      }`}
                      onClick={() => handleAnswer(question.id, 'yes')}
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Yes, I have this
                    </button>
                    <button 
                      className={`btn btn-sm transition-all duration-200 ${
                        answers[question.id] === 'no_help' 
                          ? 'bg-red-600 text-white border-red-600 shadow-lg' 
                          : 'border border-red-300 hover:bg-red-50 hover:border-red-400 text-red-700'
                      }`}
                      onClick={() => handleAnswer(question.id, 'no_help')}
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      No, I need help
                    </button>
                  </div>
                </div>


                
                {/* Professional Help Option */}
                {answers[question.id] === 'no_help' && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="text-sm font-medium text-red-900 mb-2">Get Professional Help</div>
                    <p className="text-sm text-red-700 mb-3">
                      Need expert assistance with {question.text.toLowerCase()}? Get matched with qualified service providers.
                    </p>
                    <div className="flex gap-2">
                      <select 
                        className="text-sm border border-red-300 rounded px-2 py-1"
                        onChange={(e) => {
                          if (e.target.value) {
                            handleProfessionalHelp(question.id, currentAreaData.id, e.target.value);
                          }
                        }}
                        defaultValue=""
                      >
                        <option value="">Select Budget Range</option>
                        <option value="$500-$1,000">$500 - $1,000</option>
                        <option value="$1,000-$2,500">$1,000 - $2,500</option>
                        <option value="$2,500-$5,000">$2,500 - $5,000</option>
                        <option value="$5,000+">$5,000+</option>
                      </select>
                    </div>
                  </div>
                )}
                
                {/* Evidence Upload (single, canonical) */}
                {answers[question.id] === 'yes' && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="text-sm font-medium text-green-900 mb-2">Upload Evidence (Optional)</div>
                    <p className="text-sm text-green-700 mb-3">
                      Upload documentation to support your attestation for this requirement.
                    </p>
                    <input 
                      type="file" 
                      className="text-sm"
                      multiple
                      accept=".pdf,.doc,.docx,.jpg,.png"
                      onChange={(e) => handleEvidenceUpload(question.id, e.target.files)}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Contextual Knowledge Base Cards */}
        <KBContextualCards 
          areaId={currentAreaData.id} 
          context="assessment"
          title={`Resources for ${currentAreaData.title}`}
        />

        {/* AI Assistant Section */}
        <AIAssistantCard 
          areaId={currentAreaData.id}
          context="assessment"
        />

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

// ---------------- Knowledge Base System ----------------
function KnowledgeBasePage(){
  const [areas, setAreas] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [resources, setResources] = useState([]);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [userAccess, setUserAccess] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadKnowledgeBaseAreas();
    loadUserAccess();
  }, []);

  const loadKnowledgeBaseAreas = async () => {
    try {
      const { data } = await axios.get(`${API}/knowledge-base/areas`);
      setAreas(data.areas || []);
    } catch (e) {
      console.error('Failed to load knowledge base areas:', e);
      // Fallback to static areas if API fails
      setAreas([
        { id: 'area1', title: 'Business Formation & Registration', description: 'Essential business setup, licensing, and legal registration requirements', resources: 12 },
        { id: 'area2', title: 'Financial Operations & Management', description: 'Accounting systems, financial controls, and budget management', resources: 15 },
        { id: 'area3', title: 'Legal & Contracting Compliance', description: 'Contract management, legal compliance, and regulatory requirements', resources: 18 },
        { id: 'area4', title: 'Quality Management & Standards', description: 'Quality assurance processes, standards compliance, and certifications', resources: 10 },
        { id: 'area5', title: 'Technology & Security Infrastructure', description: 'IT systems, cybersecurity protocols, and technology management', resources: 20 },
        { id: 'area6', title: 'Human Resources & Capacity', description: 'HR policies, workforce management, and organizational capacity', resources: 14 },
        { id: 'area7', title: 'Performance Tracking & Reporting', description: 'Metrics, KPIs, performance monitoring, and reporting systems', resources: 16 },
        { id: 'area8', title: 'Risk Management & Business Continuity', description: 'Risk assessment, mitigation strategies, and business continuity planning', resources: 13 }
      ]);
    }
  };

  const loadUserAccess = async () => {
    try {
      const { data } = await axios.get(`${API}/knowledge-base/access`);
      setUserAccess(data);
    } catch (e) {
      console.error('Failed to load user access:', e);
    }
  };

  const loadAreaResources = async (areaId) => {
    try {
      const token = localStorage.getItem('polaris_token');
      const authHeaders = {
        headers: { Authorization: `Bearer ${token}` }
      };
      
      const { data } = await axios.get(`${API}/knowledge-base/${areaId}/content`, authHeaders);
      setResources(data.content || {});
      setSelectedArea(areaId);
    } catch (e) {
      console.error('Failed to load area resources:', e);
      toast.error('Failed to load resources', {
        description: e.response?.data?.detail || 'Unable to load area resources'
      });
    }
  };

  const unlockArea = async (areaId) => {
    setPaymentLoading(true);
    try {
      const { data } = await axios.post(`${API}/payments/knowledge-base`, {
        package_id: 'knowledge_base_single',
        origin_url: window.location.origin,
        metadata: { area_id: areaId }
      });
      window.location.href = data.url;
    } catch (e) {
      toast.error('Failed to process payment', { description: e.response?.data?.detail || e.message });
      setPaymentLoading(false);
    }
  };

  const unlockAllAreas = async () => {
    setPaymentLoading(true);
    try {
      const { data } = await axios.post(`${API}/payments/knowledge-base`, {
        package_id: 'knowledge_base_all',
        origin_url: window.location.origin
      });
      window.location.href = data.url;
    } catch (e) {
      toast.error('Failed to process payment', { description: e.response?.data?.detail || e.message });
      setPaymentLoading(false);
    }
  };

  const downloadTemplate = async (template, resourceType = 'template') => {
    try {
      const response = await axios.get(
        `${API}/knowledge-base/generate-template/${selectedArea}/${resourceType}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
        }
      );
      
      // Create and download file with proper content type
      const content = response.data.content;
      const filename = response.data.filename || `polaris_${selectedArea}_${resourceType}.docx`;
      const contentType = response.data.content_type || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      
      // For Office documents, we need to handle base64 encoding
      let blob;
      if (contentType.includes('officedocument')) {
        // Assume base64 encoded content for Office documents
        const binaryString = window.atob(content);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        blob = new Blob([bytes], { type: contentType });
      } else {
        // Plain text content
        blob = new Blob([content], { type: contentType });
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${template.name || resourceType}`);
    } catch (e) {
      console.error('Download failed:', e);
      toast.error('Download failed', { 
        description: e.response?.data?.detail || 'Unable to download template' 
      });
    }
  };

  const downloadAreaTemplate = async (areaId, resourceType) => {
    try {
      const response = await axios.get(
        `${API}/knowledge-base/generate-template/${areaId}/${resourceType}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
        }
      );
      
      // Create and download file with proper content type
      const content = response.data.content;
      const filename = response.data.filename || `polaris_${areaId}_${resourceType}.docx`;
      const contentType = response.data.content_type || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      
      // For Office documents, we need to handle base64 encoding
      let blob;
      if (contentType.includes('officedocument')) {
        // Assume base64 encoded content for Office documents
        const binaryString = window.atob(content);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        blob = new Blob([bytes], { type: contentType });
      } else {
        // Plain text content
        blob = new Blob([content], { type: contentType });
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${resourceType} for ${areaId}`);
    } catch (e) {
      console.error('Download failed:', e);
      toast.error('Download failed', { 
        description: e.response?.data?.detail || 'Unable to download template' 
      });
    }
  };

  return (
    <div className="container mt-6 max-w-7xl">
      {/* Knowledge Base Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-8 mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white/20 rounded-lg">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold">Knowledge Base</h1>
            <p className="text-purple-100 mt-2">AI-powered resources, templates, and guidance for procurement readiness</p>
          </div>
        </div>

        {userAccess && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-2xl font-bold">{userAccess.unlocked_areas.length}/8</div>
              <div className="text-sm opacity-80">Areas Unlocked</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-2xl font-bold">{userAccess.has_all_access ? 'Unlimited' : '102'}</div>
              <div className="text-sm opacity-80">Resources Available</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-2xl font-bold">$20</div>
              <div className="text-sm opacity-80">Per Area or $100 All</div>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Purchase Option */}
      {userAccess && !userAccess.has_all_access && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-amber-900 mb-2">🎯 Complete Access Package</h3>
              <p className="text-amber-700 mb-4">
                Unlock all 8 business areas with comprehensive templates, guides, and AI-powered assistance
              </p>
              <div className="flex items-center gap-4 mb-4">
                <span className="text-lg text-slate-500 line-through">$160 individual</span>
                <span className="text-3xl font-bold text-amber-900">$100</span>
                <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium">38% SAVINGS</span>
              </div>
            </div>
            <button 
              className="btn btn-primary bg-amber-600 hover:bg-amber-700 px-8 py-3 text-lg"
              onClick={unlockAllAreas}
              disabled={paymentLoading}
            >
              {paymentLoading ? 'Processing...' : 'Unlock All Areas - $100'}
            </button>
          </div>
        </div>
      )}

      {/* Knowledge Base Areas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {areas.map((area) => {
          const isUnlocked = userAccess?.has_all_access || userAccess?.unlocked_areas?.includes(area.id);
          
          return (
            <div 
              key={area.id} 
              className={`bg-white rounded-xl shadow-sm border hover:shadow-lg transition-all duration-200 ${
                !isUnlocked ? 'hover:border-blue-200' : 'hover:border-green-200'
              }`}
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-slate-900 mb-2 leading-tight">{area.title}</h3>
                    <p className="text-sm text-slate-600 leading-relaxed">{area.description}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    {isUnlocked ? (
                      <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
                        Unlocked
                      </span>
                    ) : (
                      <span className="text-xs bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-medium">
                        $20
                      </span>
                    )}
                  </div>
                </div>

                {/* Resource Count */}
                <div className="flex items-center gap-4 mb-4 text-xs text-slate-500">
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="font-medium">{area.resources || area.resources_count || 12} Resources</span>
                  </span>
                </div>

                {/* Action Area */}
                {!isUnlocked ? (
                  <div className="text-center py-4 border-t border-slate-100">
                    <p className="text-sm text-slate-600 mb-4">
                      🎯 AI-powered templates, guides, and compliance resources
                    </p>
                    <button 
                      className="btn btn-primary bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 px-6 py-2 text-sm font-medium"
                      onClick={() => unlockArea(area.id)}
                      disabled={paymentLoading}
                    >
                      {paymentLoading ? (
                        <span className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Processing...
                        </span>
                      ) : (
                        `Unlock for $20`
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="border-t border-slate-100 pt-4">
                    <div className="space-y-3 mb-4">
                      <div className="text-xs font-medium text-slate-700 mb-2">Available Resources:</div>
                      <ul className="space-y-2">
                        <li className="flex items-center gap-2 text-sm">
                          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-slate-700">Templates & Checklists</span>
                          <button 
                            className="ml-auto text-blue-600 hover:text-blue-700 text-xs font-medium"
                            onClick={() => downloadAreaTemplate(area.id, 'template')}
                          >
                            Download
                          </button>
                        </li>
                        <li className="flex items-center gap-2 text-sm">
                          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-slate-700">Compliance Guides</span>
                          <button 
                            className="ml-auto text-blue-600 hover:text-blue-700 text-xs font-medium"
                            onClick={() => downloadAreaTemplate(area.id, 'guide')}
                          >
                            Download
                          </button>
                        </li>
                        <li className="flex items-center gap-2 text-sm">
                          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-slate-700">Best Practices</span>
                          <button 
                            className="ml-auto text-blue-600 hover:text-blue-700 text-xs font-medium"
                            onClick={() => downloadAreaTemplate(area.id, 'practices')}
                          >
                            Download
                          </button>
                        </li>
                      </ul>
                    </div>
                    
                    <button 
                      className="btn btn-primary w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
                      onClick={() => loadAreaResources(area.id)}
                    >
                      View All Resources
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Resource Viewer */}
      {selectedArea && resources && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">
              {areas.find(a => a.id === selectedArea)?.title} Resources
            </h3>
            <button 
              className="text-slate-500 hover:text-slate-700"
              onClick={() => setSelectedArea(null)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Templates */}
            {resources.templates && (
              <div>
                <h4 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Templates & Checklists
                </h4>
                <div className="space-y-3">
                  {resources.templates.map((template, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium text-blue-900">{template.name}</span>
                      <button 
                        className="text-blue-600 hover:text-blue-700 text-sm"
                        onClick={() => downloadTemplate(template, 'template')}
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Guides */}
            {resources.guides && (
              <div>
                <h4 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Compliance Guides
                </h4>
                <div className="space-y-3">
                  {resources.guides.map((guide, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium text-green-900">{guide.name}</span>
                      <button 
                        className="text-green-600 hover:text-green-700 text-sm"
                        onClick={() => downloadTemplate(guide, 'guide')}
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Resources */}
            {resources.resources && (
              <div>
                <h4 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Additional Resources
                </h4>
                <div className="space-y-3">
                  {resources.resources.map((resource, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-sm font-medium text-purple-900">{resource.name}</span>
                      <button 
                        className="text-purple-600 hover:text-purple-700 text-sm"
                        onClick={() => downloadTemplate(resource, 'resource')}
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* AI Guidance Section */}
          <div className="mt-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
            <h4 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI-Powered Guidance
            </h4>
            <p className="text-indigo-700 text-sm mb-4">
              Get personalized recommendations and step-by-step guidance for implementing {areas.find(a => a.id === selectedArea)?.title.toLowerCase()} best practices.
            </p>
            <button className="btn bg-indigo-600 text-white hover:bg-indigo-700">
              Get AI Guidance
            </button>
          </div>
        </div>
      )}

      {/* Features Overview */}
      {!selectedArea && (
        <div className="bg-slate-50 rounded-lg p-8">
          <h3 className="text-xl font-semibold text-slate-900 mb-6 text-center">What's Included in Each Area</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h4 className="font-medium text-slate-900 mb-2">Templates</h4>
              <p className="text-sm text-slate-600">Ready-to-use documents and checklists</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h4 className="font-medium text-slate-900 mb-2">Guides</h4>
              <p className="text-sm text-slate-600">Step-by-step compliance guides</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h4 className="font-medium text-slate-900 mb-2">AI Guidance</h4>
              <p className="text-sm text-slate-600">Personalized AI-powered assistance</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-medium text-slate-900 mb-2">Best Practices</h4>
              <p className="text-sm text-slate-600">Industry standards and recommendations</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function FreeResourcesPage() {
  const [resources, setResources] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFreeResources();
  }, []);

  const loadFreeResources = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/free-resources`);
      setResources(data);
    } catch (e) {
      console.error('Failed to load free resources:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-2 justify-center">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Loading free resources...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!resources) {
    return (
      <div className="container mt-6 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
          <p className="text-slate-600">Unable to load resources. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Free Community Resources</h2>
          <p className="text-slate-600">
            {resources.registration_instructions}
          </p>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {resources.community_resources?.map((resource, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-slate-900">{resource.name}</h3>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {resource.type}
                  </span>
                </div>
                
                <p className="text-sm text-slate-600 mb-4">{resource.description}</p>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-slate-900 mb-2">Focus Areas:</h4>
                  <div className="flex flex-wrap gap-2">
                    {resource.focus_areas?.map((area, areaIndex) => (
                      <span key={areaIndex} className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded">
                        {area}
                      </span>
                    ))}
                  </div>
                </div>
                
                <a
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary w-full"
                >
                  Visit Website & Register
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Ready for Premium Features?</h3>
            <p className="text-slate-600 mb-4">
              {resources.additional_support}
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '/knowledge-base'}
            >
              Explore Knowledge Base
            </button>
          </div>
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
  const [knowledgeBaseAccess, setKnowledgeBaseAccess] = useState(null);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [assessmentData, setAssessmentData] = useState(null);
  const [serviceRequests, setServiceRequests] = useState([]);
  const [sponsoringAgency, setSponsoringAgency] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [freeServices, setFreeServices] = useState([]);
  const navigate = useNavigate();
  
  useEffect(()=>{ 
    const load=async()=>{ 
      try {
        const token = localStorage.getItem('polaris_token');
        if (!token) {
          console.error('No authentication token found');
          return;
        }
        
        const authHeaders = {
          headers: { Authorization: `Bearer ${token}` }
        };
        
        const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
        const {data} = await axios.get(`${API}/home/client`, authHeaders); 
        setData(data); 
        const meLocal = JSON.parse(localStorage.getItem('polaris_me')||'null');
        
        // Load certificates
        const certs = await axios.get(`${API}/client/certificates`, authHeaders);
        setCertificates(certs.data.certificates || []);
        
        // Load matched services for the client
        const services = await axios.get(`${API}/client/matched-services`, authHeaders);
        setMatchedServices(services.data.services || []);

        // Load knowledge base access status
        const access = await axios.get(`${API}/knowledge-base/access`, authHeaders);
        setKnowledgeBaseAccess(access.data);

        // Load assessment data and gaps
        const userId = meLocal?.id;
        let assessmentRes = null;
        if (userId) {
          assessmentRes = await axios.get(`${API}/assessment/progress/${userId}`, authHeaders);
          setAssessmentData(assessmentRes.data);
        }

        // Load active service requests
        const requests = await axios.get(`${API}/engagements/my-services`, authHeaders);
        setServiceRequests(requests.data.engagements || []);

        // Load sponsoring agency info (from license code)
        if (data.sponsoring_agency_id) {
          const agency = await axios.get(`${API}/agency/info/${data.sponsoring_agency_id}`, authHeaders);
          setSponsoringAgency(agency.data);
        }

        // Calculate gaps from assessment
        if (assessmentRes && assessmentRes.data && assessmentRes.data.answers) {
          const calculatedGaps = calculateGaps(assessmentRes.data.answers);
          setGaps(calculatedGaps);
          
          // Load dynamic free services based on gaps
          const freeServicesRes = await axios.get(`${API}/free-resources/recommendations`, {
            ...authHeaders,
            params: { gaps: calculatedGaps.map(g => g.area_id).join(',') }
          });
          setFreeServices(freeServicesRes.data.resources || []);
        }
      } catch(e) {
        console.error('Error loading client home data:', e);
        // Show user-friendly error message
        if (e.response?.status === 401) {
          console.error('Authentication failed - redirecting to login');
          localStorage.removeItem('polaris_token');
          localStorage.removeItem('polaris_me');
          navigate('/');
        }
      }
    }; 
    load(); 
  },[]);

  // Calculate gaps from assessment answers
  const calculateGaps = (answers) => {
    const gaps = [];
    const areaNames = {
      'area1': 'Business Formation & Registration',
      'area2': 'Financial Operations & Management', 
      'area3': 'Legal & Contracting Compliance',
      'area4': 'Quality Management & Standards',
      'area5': 'Technology & Security Infrastructure',
      'area6': 'Human Resources & Capacity',
      'area7': 'Performance Tracking & Reporting',
      'area8': 'Risk Management & Business Continuity'
    };

    Object.entries(answers).forEach(([questionId, answer]) => {
      const areaId = questionId.split('_')[0]; // Extract area from q1_1 format
      
      // Gap if no answer OR "No, I need help"
      if (!answer || answer === 'no_help') {
        const existingGap = gaps.find(g => g.area_id === areaId);
        if (!existingGap) {
          gaps.push({
            area_id: areaId,
            area_name: areaNames[areaId],
            question_ids: [questionId],
            severity: answer === 'no_help' ? 'high' : 'medium'
          });
        } else {
          existingGap.question_ids.push(questionId);
          if (answer === 'no_help' && existingGap.severity === 'medium') {
            existingGap.severity = 'high';
          }
        }
      }
    });

    return gaps;
  };

  // Check for payment completion from URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, []);

  const checkPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      toast.error('Payment status check timed out. Please refresh the page.');
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/v1/checkout/status/${sessionId}`);
      const data = response.data;
      
      if (data.payment_status === 'paid') {
        toast.success('Payment successful! Knowledge base unlocked.');
        // Reload access status
        const access = await axios.get(`${API}/knowledge-base/access`);
        setKnowledgeBaseAccess(access.data);
        setActiveTab('knowledge');
        return;
      } else if (data.status === 'expired') {
        toast.error('Payment session expired. Please try again.');
        return;
      }

      // Continue polling if still pending
      setTimeout(() => checkPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      if (attempts === 0) {
        toast.error('Error checking payment status. Please refresh the page.');
      }
    }
  };

  const unlockKnowledgeBase = async (packageId, areaId = null) => {
    setPaymentLoading(true);
    try {
      const metadata = areaId ? { area_id: areaId } : {};
      const { data } = await axios.post(`${API}/payments/knowledge-base`, {
        package_id: packageId,
        origin_url: window.location.origin,
        metadata
      });

      // Redirect to Stripe Checkout
      window.location.href = data.url;
    } catch (e) {
      toast.error('Failed to process payment', { description: e.response?.data?.detail || e.message });
      setPaymentLoading(false);
    }
  };

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

  const downloadAreaTemplate = async (areaId, resourceType) => {
    try {
      const response = await axios.get(
        `${API}/knowledge-base/generate-template/${areaId}/${resourceType}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('polaris_token')}` }
        }
      );
      
      // Create and download file
      const content = response.data.content;
      const filename = response.data.filename || `polaris_${areaId}_${resourceType}.md`;
      
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${resourceType} for ${areaId}`);
    } catch (e) {
      console.error('Download failed:', e);
      toast.error('Download failed', { 
        description: e.response?.data?.detail || 'Unable to download template' 
      });
    }
  };

  if(!data) {
    return (
      <div className="container mt-6">
        <div className="text-center py-12">
          <div className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 hover:bg-indigo-400 transition ease-in-out duration-150 cursor-not-allowed" disabled="">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading your dashboard...
          </div>
          <p className="text-slate-600 mt-4">Please wait while we fetch your procurement readiness data.</p>
        </div>
      </div>
    );
  }
  // Note: Removed profile_complete check - clients should see dashboard even without complete profile
  
  return (
    <div className="container mt-6">
      {/* Enhanced Dashboard Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold mb-2">Welcome to Your Procurement Readiness Dashboard</h1>
        <p className="opacity-90">Track your assessment progress, manage gaps, and access professional services</p>
        
        {/* Quick Status Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold">{assessmentData?.completion_percentage || 0}%</div>
                <div className="text-sm opacity-90">Assessment Complete</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500/30 rounded-lg">
                <svg className="w-5 h-5 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-200">{gaps.length}</div>
                <div className="text-sm opacity-90">Critical Gaps</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/30 rounded-lg">
                <svg className="w-5 h-5 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-200">{serviceRequests.filter(r => r.status === 'active').length}</div>
                <div className="text-sm opacity-90">Active Services</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-500/30 rounded-lg">
                <svg className="w-5 h-5 text-yellow-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-200">{data.readiness || 0}%</div>
                <div className="text-sm opacity-90">Readiness Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sponsoring Agency Info */}
      {sponsoringAgency && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">Your Sponsoring Agency</h3>
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h4 className="font-medium text-slate-800">{sponsoringAgency.agency_name}</h4>
              <p className="text-slate-600 text-sm mb-2">{sponsoringAgency.description}</p>
              <div className="text-sm text-slate-500">
                <p><strong>Contact:</strong> {sponsoringAgency.contact_name}</p>
                <p><strong>Email:</strong> {sponsoringAgency.contact_email}</p>
                <p><strong>Phone:</strong> {sponsoringAgency.contact_phone}</p>
              </div>
            </div>
            <div className="text-sm bg-blue-50 px-3 py-2 rounded-lg">
              <div className="font-medium text-blue-900">License Status</div>
              <div className="text-blue-700">Active & Verified</div>
            </div>
          </div>
        </div>
      )}

      {/* Critical Gaps Alert */}
      {gaps.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <h4 className="font-medium text-amber-900">Action Required: {gaps.length} Critical Gap{gaps.length > 1 ? 's' : ''} Identified</h4>
              <p className="text-amber-700 text-sm mt-1">
                Complete your assessment and address these gaps to improve your procurement readiness score.
              </p>
              <div className="flex gap-2 mt-3">
                <button 
                  className="btn btn-sm bg-amber-600 text-white hover:bg-amber-700"
                  onClick={() => navigate('/assessment')}
                >
                  Continue Assessment
                </button>
                <button 
                  className="btn btn-sm"
                  onClick={() => setActiveTab('gaps')}
                >
                  View Gap Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Free Services Recommendations */}
      {freeServices.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <h4 className="font-medium text-green-900 mb-2">🎯 Free Resources Available for Your Gaps</h4>
          <p className="text-green-700 text-sm mb-3">Based on your assessment, we recommend these free resources:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {freeServices.slice(0, 6).map((service, idx) => (
              <button
                key={idx}
                className="text-left bg-white border border-green-200 rounded-lg p-3 hover:bg-green-50 transition-colors"
                onClick={() => {
                  // Log resource access for navigator analytics
                  axios.post(`${API}/analytics/resource-access`, { resource_id: service.id, gap_area: service.area });
                  navigate('/free-resources');
                }}
              >
                <div className="font-medium text-green-800 text-sm">{service.title}</div>
                <div className="text-green-600 text-xs">{service.area_name}</div>
              </button>
            ))}
          </div>
          {freeServices.length > 6 && (
            <button 
              className="mt-3 text-green-700 text-sm hover:text-green-800"
              onClick={() => navigate('/free-resources')}
            >
              View all {freeServices.length} recommended resources →
            </button>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="border-b border-slate-200 px-6 pt-4">
          <nav className="flex gap-8">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'gaps', label: 'Gap Analysis', icon: '🎯' },
              { id: 'services', label: 'Services', icon: '🔧' },
              { id: 'assessment', label: 'Assessment', icon: '📝' },
              { id: 'knowledge', label: 'Knowledge Base', icon: '📚' },
              { id: 'certificates', label: 'Certificates', icon: '🏆' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-4 px-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
                {tab.id === 'gaps' && gaps.length > 0 && (
                  <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">{gaps.length}</span>
                )}
                {tab.id === 'services' && serviceRequests.filter(r => r.status === 'active').length > 0 && (
                  <span className="ml-2 bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    {serviceRequests.filter(r => r.status === 'active').length}
                  </span>
                )}
              </button>
            ))}
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

              {/* AI Insights & Gap Analysis */}
              <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-blue-900">AI Compliance Insights</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="bg-white rounded-lg p-4 border border-blue-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Priority Actions</div>
                      <p className="text-sm text-slate-600">
                        Complete Financial Operations assessment to improve readiness score by ~15%
                      </p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-blue-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Compliance Status</div>
                      <p className="text-sm text-slate-600">
                        {data.readiness >= 75 
                          ? '✅ Meeting Small Business Maturity Attestation requirements' 
                          : '⚠️ Additional documentation needed for Small Business Maturity Attestation'
                        }
                      </p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-blue-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Knowledge Base</div>
                      <p className="text-sm text-slate-600">
                        {knowledgeBaseAccess?.has_all_access 
                          ? '✅ Full access to all business area resources'
                          : `${knowledgeBaseAccess?.unlocked_areas.length || 0}/8 areas unlocked - consider upgrading for complete guidance`
                        }
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-amber-100 rounded-lg">
                      <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-amber-900">Gap Analysis</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="bg-white rounded-lg p-4 border border-amber-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Critical Gaps</div>
                      <p className="text-sm text-slate-600">
                        {data.readiness < 50 
                          ? 'Business formation and financial documentation need immediate attention'
                          : data.readiness < 75 
                          ? 'Technology infrastructure and quality management require improvement'
                          : 'Minor documentation gaps - nearly procurement ready'
                        }
                      </p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-amber-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Recommendations</div>
                      <p className="text-sm text-slate-600">
                        {data.readiness < 75 
                          ? 'Consider working with service providers to accelerate compliance'
                          : 'Continue assessment completion for certification eligibility'
                        }
                      </p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-amber-100">
                      <div className="text-sm font-medium text-slate-800 mb-1">Estimated Timeline</div>
                      <p className="text-sm text-slate-600">
                        {data.readiness < 50 
                          ? '3-6 months to achieve procurement readiness'
                          : data.readiness < 75 
                          ? '1-3 months with focused effort'
                          : '2-4 weeks for final documentation'
                        }
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Contextual Knowledge Base Cards */}
              <KBContextualCards 
                areaId={gaps.length > 0 ? gaps[0].area_id : 'area1'} 
                context="client_home"
                title="📚 Recommended Resources for You"
                limit={4}
              />
              
              <div className="mt-6 flex gap-3">
                <button className="btn btn-primary" onClick={()=>navigate('/service-request')}>Request Service Provider</button>
                <button className="btn" onClick={()=>navigate('/assessment')}>Continue Assessment</button>
                {knowledgeBaseAccess && !knowledgeBaseAccess.has_all_access && (
                  <button className="btn" onClick={() => setActiveTab('knowledge')}>View Knowledge Base</button>
                )}
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

              {knowledgeBaseAccess && (
                <div className="mb-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-2">
                      <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="font-medium text-blue-900">
                        {knowledgeBaseAccess.has_all_access 
                          ? 'All Areas Unlocked' 
                          : `${knowledgeBaseAccess.unlocked_areas.length}/8 Areas Unlocked`}
                      </span>
                    </div>
                    {!knowledgeBaseAccess.has_all_access && (
                      <p className="text-sm text-blue-700">
                        You have access to {knowledgeBaseAccess.unlocked_areas.length} business areas. 
                        Unlock more areas to access additional templates and AI guidance.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Knowledge Base Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { id: 'area1', title: 'Business Formation & Registration' },
                  { id: 'area2', title: 'Financial Operations & Management' },
                  { id: 'area3', title: 'Legal & Contracting Compliance' },
                  { id: 'area4', title: 'Quality Management & Standards' },
                  { id: 'area5', title: 'Technology & Security Infrastructure' },
                  { id: 'area6', title: 'Human Resources & Capacity' },
                  { id: 'area7', title: 'Performance Tracking & Reporting' },
                  { id: 'area8', title: 'Risk Management & Business Continuity' }
                ].map((area) => {
                  const isUnlocked = knowledgeBaseAccess?.has_all_access || 
                                   knowledgeBaseAccess?.unlocked_areas.includes(area.id);
                  
                  return (
                    <div key={area.id} className={`border rounded-lg p-6 ${isUnlocked ? 'bg-white' : 'bg-slate-50 opacity-75'}`}>
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold text-slate-900">{area.title}</h4>
                        {isUnlocked ? (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Unlocked</span>
                        ) : (
                          <span className="text-xs bg-slate-200 text-slate-600 px-2 py-1 rounded-full">$20</span>
                        )}
                      </div>
                      
                      <p className="text-sm text-slate-600 mb-4">
                        AI-powered templates, guides, and compliance resources for {area.title.toLowerCase()}
                      </p>
                      
                      {isUnlocked ? (
                        <div className="space-y-3">
                          <div>
                            <div className="text-xs font-medium text-slate-700 mb-2">Available Resources:</div>
                            <ul className="space-y-1">
                              <li className="flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                <span className="text-slate-700">Templates & Checklists</span>
                                <button 
                                  className="ml-auto text-blue-600 hover:text-blue-700 text-xs"
                                  onClick={() => downloadAreaTemplate(area.id, 'template')}
                                >
                                  Download
                                </button>
                              </li>
                              <li className="flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                <span className="text-slate-700">Compliance Guides</span>
                                <button 
                                  className="ml-auto text-blue-600 hover:text-blue-700 text-xs"
                                  onClick={() => downloadAreaTemplate(area.id, 'guide')}
                                >
                                  Download
                                </button>
                              </li>
                              <li className="flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                <span className="text-slate-700">Best Practices</span>
                                <button 
                                  className="ml-auto text-blue-600 hover:text-blue-700 text-xs"
                                  onClick={() => downloadAreaTemplate(area.id, 'practices')}
                                >
                                  Download
                                </button>
                              </li>
                            </ul>
                          </div>
                          
                          <div className="flex gap-2 pt-2">
                            <button className="btn btn-sm btn-primary flex-1">
                              AI Guidance
                            </button>
                            <button className="btn btn-sm flex-1">
                              View All Resources
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-4">
                          <div className="text-sm text-slate-600 mb-3">Unlock AI-powered templates and guidance</div>
                          <button 
                            className="btn btn-primary btn-sm"
                            onClick={() => unlockKnowledgeBase('knowledge_base_single', area.id)}
                            disabled={paymentLoading}
                          >
                            {paymentLoading ? 'Processing...' : 'Unlock for $20'}
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Bulk Purchase Option */}
              {knowledgeBaseAccess && !knowledgeBaseAccess.has_all_access && (
                <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                  <div className="text-center">
                    <h4 className="font-semibold text-purple-900 mb-2">Unlock All Areas</h4>
                    <p className="text-purple-700 mb-4">Get complete access to all 8 business areas with AI guidance and templates</p>
                    <div className="flex items-center justify-center gap-4 mb-4">
                      <span className="text-sm text-slate-500 line-through">$160 individual</span>
                      <span className="text-2xl font-bold text-purple-900">$100</span>
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium">38% OFF</span>
                    </div>
                    <button 
                      className="btn btn-primary px-8"
                      onClick={() => unlockKnowledgeBase('knowledge_base_all')}
                      disabled={paymentLoading}
                    >
                      {paymentLoading ? 'Processing...' : 'Unlock All Areas - $100'}
                    </button>
                  </div>
                </div>
              )}
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
  const [resourceStats, setResourceStats] = useState(null);
  const [sinceDays, setSinceDays] = useState(30);
  const navigate = useNavigate();
  
  useEffect(()=>{ 
    const load=async()=>{ 
      try{
        const {data} = await axios.get(`${API}/home/navigator`); 
        setData(data);
        
        // Load pending providers for approval
        const providersRes = await axios.get(`${API}/navigator/providers/pending`);
        setPendingProviders(providersRes.data.providers || []);
        
        // Load resource analytics
        const statsRes = await axios.get(`${API}/navigator/analytics/resources`, { params: { since_days: sinceDays }});
        setResourceStats(statsRes.data);
      }catch(e){
        console.error('Navigator home load error:', e);
      }
    }; 
    load(); 
  },[sinceDays]);

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
      {/* Free Resources Analytics */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Free Resources Usage</h3>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600">Since</span>
            <select className="input" value={sinceDays} onChange={e=>setSinceDays(Number(e.target.value))}>
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
        </div>
        {!resourceStats ? (
          <div className="skel h-24 w-full" />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="tile">
              <div className="tile-title">Total Selections</div>
              <div className="tile-num">{String(resourceStats.total || 0)}</div>
              <div className="tile-sub">in last {sinceDays} days</div>
            </div>
            <div className="tile md:col-span-2">
              <div className="tile-title">By Area (Top)</div>
              {resourceStats.by_area?.length ? (
                <ul className="mt-2 space-y-1">
                  {resourceStats.by_area.slice(0,6).map((item)=> (
                    <li key={item.area_id} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">{item.area_name}</span>
                      <span className="font-semibold">{item.count}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-slate-500 mt-2">No selections yet</div>
              )}
            </div>
          </div>
        )}
        {resourceStats?.last7?.length ? (
          <div className="mt-4 bg-white border rounded-lg p-4">
            <div className="tile-title mb-2">Last 7 Days</div>
            <div className="grid grid-cols-7 gap-2 text-center text-xs">
              {resourceStats.last7.map(d => (
                <div key={d.date} className="p-2 bg-slate-50 rounded">
                  <div className="font-semibold">{d.count}</div>
                  <div className="text-slate-500">{d.date.slice(5)}</div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

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

function NavigatorAnalyticsPage(){
  const [resourceStats, setResourceStats] = useState(null);
  const [sinceDays, setSinceDays] = useState(7);
  const [loading, setLoading] = useState(true);
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  
  // Redirect non-navigators to home
  if (!me || me.role !== 'navigator') {
    return <Navigate to="/home" replace />;
  }

  useEffect(() => {
    loadAnalytics();
  }, [sinceDays]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/navigator/analytics/resources`, { 
        params: { since_days: sinceDays }
      });
      setResourceStats(response.data);
    } catch (e) {
      console.error('Failed to load analytics:', e);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeframeChange = (newSinceDays) => {
    setSinceDays(newSinceDays);
  };

  if (loading && !resourceStats) {
    return (
      <div className="container mt-6 max-w-6xl">
        <h1 className="text-2xl font-bold mb-6">Navigator Analytics</h1>
        <div className="skel h-32 w-full mb-4" />
        <div className="skel h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Navigator Analytics</h1>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Timeframe:</span>
          <select 
            className="input"
            value={sinceDays} 
            onChange={e => handleTimeframeChange(Number(e.target.value))}
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Total Selections Tile */}
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Total Selections
          </div>
          <div className="tile-num">{String(resourceStats?.total || 0)}</div>
          <div className="tile-sub">in last {sinceDays} days</div>
        </div>

        {/* By Area Summary */}
        <div className="tile lg:col-span-2">
          <div className="tile-title">By Area</div>
          {resourceStats?.by_area?.length ? (
            <div className="mt-3 space-y-2">
              {resourceStats.by_area.slice(0, 6).map((item) => (
                <div key={item.area_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-slate-700">{item.area_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full transition-all"
                        style={{ 
                          width: `${Math.max(10, (item.count / (resourceStats.total || 1)) * 100)}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold w-8 text-right">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-slate-500 mt-3">No resource selections yet</div>
          )}
        </div>
      </div>

      {/* Last 7 Days Chart */}
      {resourceStats?.last7?.length ? (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Last 7 Days Trend</h3>
          <div className="uplot-container">
            <div className="grid grid-cols-7 gap-2 text-center">
              {resourceStats.last7.map((d, index) => (
                <div key={d.date} className="flex flex-col items-center">
                  <div className="w-full flex items-end justify-center h-32 mb-2">
                    <div 
                      className="bg-blue-500 rounded-t w-8 transition-all hover:bg-blue-600"
                      style={{ 
                        height: `${Math.max(8, (d.count / Math.max(...resourceStats.last7.map(x => x.count), 1)) * 120)}px` 
                      }}
                    ></div>
                  </div>
                  <div className="text-xs font-semibold">{d.count}</div>
                  <div className="text-xs text-slate-500">{d.date.slice(5)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Last 7 Days Trend</h3>
          <div className="skel h-32 w-full"></div>
        </div>
      )}

      {/* Detailed By Area List */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Resource Usage by Business Area</h3>
        {resourceStats?.by_area?.length ? (
          <div className="space-y-3">
            {resourceStats.by_area.map((item, index) => (
              <div key={item.area_id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-sm font-semibold text-blue-700">{index + 1}</span>
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">{item.area_name}</div>
                    <div className="text-sm text-slate-600">Area ID: {item.area_id}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-slate-900">{item.count}</div>
                  <div className="text-sm text-slate-600">selections</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p>No resource usage data available for the selected timeframe</p>
          </div>
        )}
      </div>
    </div>
  );
}

function AgencyHome(){
  const [impact, setImpact] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  
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

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="border-b p-4">
          <nav className="flex gap-6">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'branding', label: 'Branding & Theme', icon: '🎨' },
              { id: 'system', label: 'System Health', icon: '⚡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 px-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id 
                    ? 'border-indigo-500 text-indigo-600' 
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div>
              <div className="dashboard-grid mb-6">
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Total Invites
          </div>
          <div className="tile-num">{String(impact?.invites?.total || 0)}</div>
          <div className="tile-sub">businesses engaged</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Paid Assessments
          </div>
          <div className="tile-num">{String(impact?.invites?.paid || 0)}</div>
          <div className="tile-sub">completed assessments</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Revenue Generated
          </div>
          <div className="tile-num">${String(impact?.revenue?.assessment_fees || 0)}</div>
          <div className="tile-sub">assessment fees</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            Opportunities
          </div>
          <div className="tile-num">{String(impact?.opportunities?.count || 0)}</div>
          <div className="tile-sub">available contracts</div>
        </div>
      </div>

              {/* Certificates Section */}
              {certificates.length > 0 && (
                <div>
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
            </div>
          )}

          {activeTab === 'branding' && <AgencyThemeManager />}
          
          {activeTab === 'system' && <SystemHealthDashboard />}
        </div>
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

// ---------------- Enhanced Service Request with Payment Integration ----------------
function ServiceRequestPage(){
  const location = useLocation();
  const [req, setReq] = useState({ budget: '', timeline: '', area_id: 'area1', description: '', urgency: 'standard', deliverables: '' });
  const [requestId, setRequestId] = useState('');
  const [matches, setMatches] = useState([]);
  const [responses, setResponses] = useState([]);
  const [myServices, setMyServices] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [agreedFee, setAgreedFee] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('create'); // 'create', 'tracking', 'history'

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const sessionId = urlParams.get('session_id');
    const reqId = urlParams.get('request_id');
    
    if (sessionId) {
      checkPaymentStatus(sessionId, reqId);
    }
    
    loadMyServices();
  }, [location]);

  const loadMyServices = async () => {
    try {
      const { data } = await axios.get(`${API}/engagements/my-services`);
      setMyServices(data.engagements || []);
    } catch (e) {
      console.error('Failed to load services:', e);
    }
  };

  const checkPaymentStatus = async (sessionId, requestId = null, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      toast.error('Payment status check timed out. Please check your email for confirmation.');
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/v1/checkout/status/${sessionId}`);
      const data = response.data;
      
      if (data.payment_status === 'paid') {
        toast.success('Payment successful! Your service request is now active.');
        if (requestId) {
          setRequestId(requestId);
          await loadRequestData(requestId);
        }
        await loadMyServices();
        setActiveTab('tracking');
        return;
      } else if (data.status === 'expired') {
        toast.error('Payment session expired. Please try again.');
        return;
      }

      // If payment is still pending, continue polling
      toast.info('Payment is being processed...');
      setTimeout(() => checkPaymentStatus(sessionId, requestId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      toast.error('Error checking payment status. Please try again.');
    }
  };

  const loadRequestData = async (reqId) => {
    try {
      // Load provider responses for this service request
      const responsesRes = await axios.get(`${API}/service-requests/${reqId}/responses`);
      setResponses(responsesRes.data.responses || []);
      // Optionally, load more detailed request info
      const reqRes = await axios.get(`${API}/service-requests/${reqId}`);
      // If your backend returns any suggested matches, you can set them here
      setMatches(reqRes.data.suggested_matches || []);
    } catch (e) {
      console.error('Failed to load request data:', e);
    }
  };

  const createRequest = async () => {
    if (!req.budget || !req.timeline || !req.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const payload = { 
        budget: parseFloat(req.budget.replace(/[^0-9.-]+/g, '')) || 0,
        payment_pref: 'card',
        timeline: req.timeline,
        area_id: req.area_id,
        description: req.description
      };
      
      const { data } = await axios.post(`${API}/match/request`, payload);
      setRequestId(data.request_id);
      toast.success('Service request created successfully');
      await loadRequestData(data.request_id);
    } catch (e) { 
      toast.error('Failed to create service request', { description: e.response?.data?.detail || e.message }); 
    }
  };

  const refresh = async () => {
    if (!requestId) return;
    await loadRequestData(requestId);
  };

  const inviteProviders = async () => { 
    try { 
      await axios.post(`${API}/match/${requestId}/invite-top5`); 
      toast.success('Invitations sent to qualified providers'); 
    } catch { 
      toast.error('Failed to send invitations'); 
    } 
  };

  const selectProvider = (provider, response) => {
    setSelectedProvider({ ...provider, response });
    setAgreedFee(response.proposed_fee || '');
    setShowPaymentModal(true);
  };

  const processPayment = async () => {
    if (!selectedProvider || !agreedFee) {
      toast.error('Please enter the agreed fee amount');
      return;
    }

    setPaymentLoading(true);
    try {
      const { data } = await axios.post(`${API}/payments/service-request`, {
        request_id: requestId,
        provider_id: selectedProvider.provider_id || selectedProvider.id,
        agreed_fee: parseFloat(agreedFee),
        origin_url: window.location.origin
      });

      // Redirect to Stripe Checkout
      window.location.href = data.url;
    } catch (e) {
      toast.error('Failed to process payment', { description: e.response?.data?.detail || e.message });
      setPaymentLoading(false);
    }
  };

  const updateServiceStatus = async (engagementId, status, notes = '') => {
    try {
      await axios.post(`${API}/engagements/${engagementId}/update`, {
        status,
        notes,
        progress_percentage: status === 'completed' ? 100 : status === 'in_progress' ? 50 : 25
      });
      toast.success('Service status updated');
      await loadMyServices();
    } catch (e) {
      toast.error('Failed to update status', { description: e.response?.data?.detail || e.message });
    }
  };

  const rateService = async (engagementId, rating, feedback = '') => {
    try {
      await axios.post(`${API}/engagements/${engagementId}/rating`, {
        engagement_id: engagementId,
        rating,
        feedback,
        quality_score: rating,
        communication_score: rating,
        timeliness_score: rating
      });
      toast.success('Rating submitted successfully');
      await loadMyServices();
    } catch (e) {
      toast.error('Failed to submit rating', { description: e.response?.data?.detail || e.message });
    }
  };

  const budgetRanges = ['500', '1000', '2500', '5000', '10000'];
  const timelineOptions = ['ASAP (1-3 days)', 'Within 1 week', 'Within 2 weeks', 'Within 1 month', 'Within 3 months', 'Flexible timeline'];

  return (
    <div className="container mt-6 max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Service Requests</h2>
        <div className="flex gap-2">
          <button 
            className={`btn ${activeTab === 'create' ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            Create Request
          </button>
          <button 
            className={`btn ${activeTab === 'tracking' ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab('tracking')}
          >
            Active Services
          </button>
          <button 
            className={`btn ${activeTab === 'history' ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Service History
          </button>
        </div>
      </div>

      {/* Create Request Tab */}
      {activeTab === 'create' && (
        <>
          {!requestId && (
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4">Create New Service Request</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">Business Area *</label>
                  <select className="input w-full" value={req.area_id} onChange={e=>setReq({...req, area_id:e.target.value})}>
                    <option value="area1">Business Formation & Registration</option>
                    <option value="area2">Financial Operations & Management</option>
                    <option value="area3">Legal & Contracting Compliance</option>
                    <option value="area4">Quality Management & Standards</option>
                    <option value="area5">Technology & Security Infrastructure</option>
                    <option value="area6">Human Resources & Capacity</option>
                    <option value="area7">Performance Tracking & Reporting</option>
                    <option value="area8">Risk Management & Business Continuity</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Budget (USD) *</label>
                  <select className="input w-full" value={req.budget} onChange={e=>setReq({...req, budget:e.target.value})}>
                    <option value="">Select budget range</option>
                    {budgetRanges.map(amount => (
                      <option key={amount} value={amount}>${amount}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Timeline *</label>
                  <select className="input w-full" value={req.timeline} onChange={e=>setReq({...req, timeline:e.target.value})}>
                    <option value="">Select timeline</option>
                    {timelineOptions.map(timeline => (
                      <option key={timeline} value={timeline}>{timeline}</option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">Project Description *</label>
                  <textarea 
                    className="input w-full h-32" 
                    placeholder="Describe your project requirements, goals, and any specific deliverables you need..." 
                    value={req.description} 
                    onChange={e=>setReq({...req, description:e.target.value})}
                  />
                </div>

                <div className="md:col-span-2">
                  <button className="btn btn-primary" onClick={createRequest}>
                    Create Service Request
                  </button>
                </div>
              </div>
            </div>
          )}

          {requestId && (
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Service Request Tracking</h3>
                <div className="flex gap-2">
                  <button className="btn" onClick={inviteProviders}>Invite Providers</button>
                  <button className="btn" onClick={refresh}>Refresh</button>
                </div>
              </div>
              
              <div className="mb-6">
                <div className="text-sm text-slate-600 mb-2">Qualified Service Providers</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {matches.map(m => (
                    <div key={m.provider_id} className="p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-900">{m.company_name}</div>
                          <div className="text-xs text-slate-600">{(m.service_areas||[]).join(', ')}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-slate-500">Typical Range</div>
                          <div className="font-semibold">{m.price_min ? `$${m.price_min} - $${m.price_max}` : (req.budget?`$${req.budget}`:'—')}</div>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center gap-1 text-sm text-slate-600">
                          <span className="text-yellow-500">★</span>
                          <span>{m.score || '4.8'}</span>
                          <span className="ml-2">{m.location||'San Antonio, TX'}</span>
                        </div>
                        <div>
                          <button className="btn btn-sm">View Profile</button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {matches.length === 0 && (
                    <div className="text-sm text-slate-500">No suggested matches yet. Invite providers or wait for responses.</div>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold mb-4">Proposals Received</h3>
                <div className="space-y-4">
                  {responses.map(r => (
                    <div key={r.id || r._id} className="border rounded-lg p-4 hover:bg-slate-50">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                              {(r.provider_company||'SP').slice(0,2).toUpperCase()}
                            </div>
                            <div>
                              <h4 className="font-semibold text-slate-900">{r.provider_company || 'Service Provider'}</h4>
                              <div className="text-xs text-slate-500">{r.provider_email}</div>
                            </div>
                          </div>
                          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div className="p-3 rounded-md bg-slate-50 border">
                              <div className="text-xs text-slate-500">Proposed Fee</div>
                              <div className="text-lg font-semibold">${r.proposed_fee || '—'}</div>
                            </div>
                            <div className="p-3 rounded-md bg-slate-50 border">
                              <div className="text-xs text-slate-500">ETA</div>
                              <div className="text-lg font-semibold">{r.estimated_timeline || '—'}</div>
                            </div>
                            <div className="p-3 rounded-md bg-slate-50 border md:col-span-1">
                              <div className="text-xs text-slate-500">Status</div>
                              <div className="text-sm font-medium capitalize">{r.status || 'submitted'}</div>
                            </div>
                          </div>
                          <div className="mt-3">
                            <div className="text-xs text-slate-500 mb-1">Proposal Note</div>
                            <p className="text-sm text-slate-700 leading-relaxed">{r.proposal_note || 'No proposal note provided'}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button 
                            className="btn btn-primary"
                            onClick={() => selectProvider(r, r)}
                          >
                            Accept & Pay
                          </button>
                        </div>
                      </div>
                      {/* Status timeline bar */}
                      <div className="mt-3">
                        <div className="w-full bg-slate-200 rounded h-2 overflow-hidden">
                          <div className="h-2 bg-blue-500" style={{ width: (r.status === 'submitted' ? 25 : r.status === 'shortlisted' ? 50 : r.status === 'accepted' ? 75 : r.status === 'paid' ? 100 : 10) + '%' }} />
                        </div>
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                          <span>Submitted</span>
                          <span>Shortlisted</span>
                          <span>Accepted</span>
                          <span>Paid</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  {responses.length === 0 && (
                    <div className="text-sm text-slate-500">No proposals yet. Providers will respond soon.</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Active Services Tab */}
      {activeTab === 'tracking' && (
        <div className="space-y-6">
          {myServices.filter(s => ['payment_completed', 'active', 'in_progress'].includes(s.status)).map(service => (
            <div key={service._id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">Service Request #{service.request_id?.slice(-8)}</h3>
                  <p className="text-slate-600">Provider: {service.provider_company || 'Service Provider'}</p>
                  <p className="text-sm text-slate-500">Fee: ${service.agreed_fee} | Status: {service.status}</p>
                </div>
                <div className="flex gap-2">
                  <button 
                    className="btn btn-sm"
                    onClick={() => updateServiceStatus(service._id, 'in_progress', 'Client confirmed start')}
                  >
                    Mark In Progress
                  </button>
                  <button 
                    className="btn btn-sm"
                    onClick={() => updateServiceStatus(service._id, 'completed', 'Service completed')}
                  >
                    Mark Complete
                  </button>
                </div>
              </div>
              
              {service.latest_tracking && (
                <div className="bg-slate-50 rounded p-3 mb-3">
                  <p className="text-sm"><strong>Latest Update:</strong> {service.latest_tracking.status}</p>
                  {service.latest_tracking.notes && (
                    <p className="text-sm text-slate-600 mt-1">{service.latest_tracking.notes}</p>
                  )}
                  <p className="text-xs text-slate-500 mt-1">
                    {new Date(service.latest_tracking.updated_at).toLocaleDateString()}
                  </p>
                </div>
              )}
              
              {service.status === 'completed' && !service.rating && (
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Rate this service:</h4>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map(rating => (
                      <button
                        key={rating}
                        className="text-2xl text-slate-300 hover:text-yellow-500"
                        onClick={() => rateService(service._id, rating)}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {myServices.filter(s => ['payment_completed', 'active', 'in_progress'].includes(s.status)).length === 0 && (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-slate-900 mb-2">No Active Services</h3>
              <p className="text-slate-600">You don't have any active services at the moment.</p>
            </div>
          )}
        </div>
      )}

      {/* Service History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {myServices.filter(s => ['completed', 'cancelled'].includes(s.status)).map(service => (
            <div key={service._id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold">Service Request #{service.request_id?.slice(-8)}</h3>
                  <p className="text-slate-600">Provider: {service.provider_company || 'Service Provider'}</p>
                  <p className="text-sm text-slate-500">Fee: ${service.agreed_fee} | Status: {service.status}</p>
                  <p className="text-xs text-slate-400">
                    Completed: {new Date(service.updated_at || service.created_at).toLocaleDateString()}
                  </p>
                </div>
                {service.rating && (
                  <div className="text-sm">
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span>{service.rating.rating}/5</span>
                    </div>
                    {service.rating.feedback && (
                      <p className="text-slate-600 mt-1 max-w-xs">{service.rating.feedback}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {myServices.filter(s => ['completed', 'cancelled'].includes(s.status)).length === 0 && (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-slate-900 mb-2">No Service History</h3>
              <p className="text-slate-600">You haven't completed any services yet.</p>
            </div>
          )}
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Confirm Service Payment</h3>
            
            <div className="space-y-4 mb-6">
              <div>
                <p className="text-sm text-slate-600">Provider</p>
                <p className="font-medium">{selectedProvider?.provider_company || 'Service Provider'}</p>
              </div>
              
              <div>
                <p className="text-sm text-slate-600">Service Description</p>
                <p className="text-sm">{selectedProvider?.response?.proposal_note || 'Service request'}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Agreed Fee (USD)</label>
                <input
                  type="number"
                  className="input w-full"
                  value={agreedFee}
                  onChange={e => setAgreedFee(e.target.value)}
                  placeholder="Enter agreed fee amount"
                />
              </div>
              
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-sm text-blue-800">
                  <strong>Payment will be processed securely through Stripe.</strong><br/>
                  A 5% platform fee will be added to cover payment processing and platform services.
                </p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                className="btn flex-1"
                onClick={() => setShowPaymentModal(false)}
                disabled={paymentLoading}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary flex-1"
                onClick={processPayment}
                disabled={paymentLoading || !agreedFee}
              >
                {paymentLoading ? 'Processing...' : 'Pay & Start Service'}
              </button>
            </div>
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
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Load notification count for user icon highlight
  useEffect(() => {
    if (me) {
      loadNotificationCount();
      // Poll for new notifications every 30 seconds
      const interval = setInterval(loadNotificationCount, 30000);
      return () => clearInterval(interval);
    }
  }, [me]);

  const loadNotificationCount = async () => {
    try {
      const { data } = await axios.get(`${API}/notifications/my`, {
        params: { unread_only: true }
      });
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      console.error('Failed to load notification count:', e);
    }
  };
  
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
            <img src="/polaris_lockup_horizontal_light.svg" alt="POLARIS" className="h-8 w-auto"/>
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
              <Link className="nav-item" to="/service-request">
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
            
            {(me.role === 'client' || me.role === 'provider') && (
              <>
                <Link className="nav-item" to="/knowledge-base">
                  <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  <span>Knowledge Base</span>
                </Link>
                <Link className="nav-item" to="/engagements">
                  <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6M7 8h10M5 5h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2z" />
                  </svg>
                  <span>Engagements</span>
                </Link>
              </>
            )}

            {me.role === 'agency' && (
              <Link className="nav-item" to="/opportunities">
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7h18M3 12h12M3 17h18"/></svg>
                <span>Opportunities</span>
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
              <>
                <Link className="nav-item" to="/navigator">
                  <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                  <span>Review Queue</span>
                </Link>
                <Link className="nav-item" to="/navigator/analytics">
                  <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3a1 1 0 00-1 1v14a1 1 0 102 0V4a1 1 0 00-1-1zm-6 8a1 1 0 00-1 1v6a1 1 0 102 0v-6a1 1 0 00-1-1zm12-6a1 1 0 00-1 1v12a1 1 0 102 0V6a1 1 0 00-1-1z" />
                  </svg>
                  <span>Analytics</span>
                </Link>
              </>
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
            <div className="flex items-center gap-3">
              <div className="user-menu-container">
                <button 
                  className="user-menu-trigger"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  <div className="user-avatar relative">
                    <span>{me.email?.charAt(0).toUpperCase()}</span>
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-medium">
                        {unreadCount > 9 ? '9+' : unreadCount}
                      </span>
                    )}
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
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Profile Settings
                    </Link>
                    <Link className="menu-item" to="/notifications">
                      <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5V3h0z" />
                      </svg>
                      Notifications
                      {unreadCount > 0 && (
                        <span className="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                          {unreadCount}
                        </span>
                      )}
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
                    <button className="menu-item" onClick={logout}>
                      <svg className="menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function Landing(){
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [step, setStep] = useState('role-selection'); // 'role-selection', 'register', 'login'
  const [selectedRole, setSelectedRole] = useState(null);
  const [kpis, setKpis] = useState(null);
  useEffect(()=>{
    (async()=>{
      try{
        const { data } = await axios.get(`${API}/metrics/landing`);
        setKpis(data);
      }catch(e){ setKpis({ total_clients:0, engagements:0, certificates:0, opportunities_open:0, gaps_addressed_30d:0, avg_yes_answers:0, clients_started_assessment:0, median_provider_response_hrs:null }); }
    })();
  },[]);

  const roleOptions = [
    {
      id: 'client',
      title: 'Small Business Client',
      description: 'Get assessed for procurement readiness and access service providers',
      requirements: 'Requires 10-digit license code from your local agency',
      features: ['Maturity assessment', 'Readiness certification', 'Service requests', 'Knowledge base access'],
      icon: '🏢'
    },
    {
      id: 'agency', 
      title: 'Local Agency',
      description: 'Invite businesses and distribute assessment licenses',
      requirements: 'Subject to verification and approval by Digital Navigators',
      features: ['License distribution', 'Opportunity forecasting', 'Business dashboards', 'Volume pricing'],
      icon: '🏛️'
    },
    {
      id: 'provider',
      title: 'Service Provider', 
      description: 'Offer services to help businesses achieve procurement readiness',
      requirements: 'Subject to vetting and approval by Digital Navigators',
      features: ['Service marketplace', 'Client matching', 'Payment processing', 'Performance tracking'],
      icon: '🔧'
    },
    {
      id: 'navigator',
      title: 'Digital Navigator',
      description: 'Platform administrators - review, approve, and guide businesses',
      requirements: 'Polaris team members only',
      features: ['Evidence review', 'Provider approval', 'Quality assurance', 'Platform management'],
      icon: '👥'
    }
  ];

  const selectRole = (roleId) => {
    setSelectedRole(roleId);
    setStep('register');
  };

  return (
    <div>
      {/* Enhanced Hero Section */}
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-inner justify-center items-center">
          <div className="text-white text-center max-w-3xl mx-auto">
            <div className="mt-2 flex flex-col items-center justify-center gap-2">
              <img src="/polaris_mark_corporate_white.svg" alt="Polaris mark" className="h-10 md:h-12 w-auto"/>
              <div className="text-white font-extrabold text-3xl lg:text-5xl" style={{ letterSpacing: '0.35em' }}>POLARIS</div>
            </div>

            <h1 className="text-white text-3xl lg:text-5xl font-semibold leading-tight mt-4">Your North Star for Small Business Procurement Readiness</h1>
            <p className="hero-sub">Prove Readiness. Unlock Opportunity.</p>
            <div className="hero-ctas justify-center">
              <a className="btn btn-primary" href="#role-selection">Start Your Journey</a>
            </div>
          </div>
        </div>
      </section>

      {/* Auth Section - Only show when needed */}
      {step !== 'role-selection' && (
        <section className="container section" id="auth">
          <div className="max-w-md mx-auto">
            <AuthWidget selectedRole={selectedRole} onBackToRoleSelection={() => setStep('role-selection')} />
          </div>
        </section>
      )}

      {/* Role Selection Section */}
      {step === 'role-selection' && (
        <section className="container section" id="role-selection">
          <div className="bg-white rounded-lg p-8 shadow-lg border max-w-6xl mx-auto">
            <h3 className="font-semibold text-slate-900 mb-2 text-center text-2xl">Choose Your User Type</h3>
            <p className="text-slate-600 text-center mb-8">Select the option that best describes your role</p>
            
            <div className="flex flex-col lg:flex-row gap-4 mb-6">
              {roleOptions.map((role) => (
                <div 
                  key={role.id}
                  className="border rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-all flex-1"
                  onClick={() => selectRole(role.id)}
                >
                  <div className="text-center">
                    <div className="text-3xl mb-3">{role.icon}</div>
                    <h4 className="font-semibold text-slate-900 mb-2">{role.title}</h4>
                    <p className="text-sm text-slate-600 mb-3">{role.description}</p>
                    <div className="text-xs text-amber-600 bg-amber-50 px-3 py-2 rounded mb-4">
                      {role.requirements}
                    </div>
                    <ul className="text-xs text-slate-500 space-y-1">
                      {role.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center justify-center gap-2">
                          <span className="text-green-500">•</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="text-center">
              <a 
                className="text-blue-600 hover:text-blue-700 text-sm"
                href="#auth"
                onClick={() => setStep('login')}
              >
                Already have an account? Sign in here
              </a>
            </div>
          </div>
        </section>
      )}

      {/* Value Proposition section removed per request */}

      {/* Features section removed per request */}


      {/* Statistics and Impact */}
      <section className="container section">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Driving Procurement Readiness</h2>
          <p className="text-slate-600">Establishing local level service to support small business pathway towards opportunity</p>
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
            <p>© 2025 Polaris Small Business Procurement Readiness Platform • Establishing local level service to support small business pathway towards opportunity</p>
            <p className="mt-1">By using this platform, you agree to our Terms of Service and Privacy Policy</p>
          </div>
        </div>
      </section>
    </div>
  );
}


function OpportunitiesPage(){
  const [items, setItems] = useState([]);
  const [mine, setMine] = useState([]);
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  useEffect(()=>{
    (async()=>{
      try{
        const list = await axios.get(`${API}/opportunities`);
        setItems(list.data.opportunities||[]);
        if(me?.role==='agency'){
          const own = await axios.get(`${API}/opportunities/mine`);
          setMine(own.data.opportunities||[]);
        }
      }catch(e){ console.error(e); }
    })();
  },[]);
  return (
    <div className="container mt-6 max-w-6xl">
      <h2 className="text-xl font-semibold mb-4">Opportunities</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border rounded p-4">
          <div className="text-sm font-semibold mb-2">Open Opportunities</div>
          <ul className="space-y-2">
            {items.map(it => (
              <li key={it.id} className="border rounded p-3">
                <div className="font-semibold text-slate-900">{it.title}</div>
                <div className="text-xs text-slate-500">Areas: {(it.area_ids||[]).join(', ')}</div>
              </li>
            ))}
            {!items.length && <div className="text-sm text-slate-500">No opportunities yet.</div>}
          </ul>
        </div>
        {me?.role==='agency' && (
          <div className="bg-white border rounded p-4">
            <div className="text-sm font-semibold mb-2">My Opportunities</div>
            <ul className="space-y-2">
              {mine.map(it => (
                <li key={it.id} className="border rounded p-3">
                  <div className="font-semibold text-slate-900">{it.title}</div>
                  <div className="text-xs text-slate-500">Status: {it.status}</div>
                </li>
              ))}
              {!mine.length && <div className="text-sm text-slate-500">None yet.</div>}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function EngagementsPage(){
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [tracking, setTracking] = useState([]);
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(()=>{ (async()=>{
    try{
      const { data } = await axios.get(`${API}/engagements/my-services`);
      // Normalize to array of engagements
      const arr = Array.isArray(data) ? data : (data.engagements || data.my_services || []);
      setItems(arr);
    }catch(e){ console.error(e); toast.error('Failed to load engagements'); }
  })(); },[]);

  const loadTracking = async(id)=>{
    try{
      const { data } = await axios.get(`${API}/engagements/${id}/tracking`);
      setTracking(data.tracking_history||[]);
    }catch(e){ setTracking([]); }
  };

  const currentStatus = (eng)=>{
    if(!eng) return 'active';
    if(tracking && tracking.length) return tracking[0].status || 'active';
    return eng.status || 'active';
  };

  const stepIndex = (status)=>{
    const order = ['active','in_progress','under_review','completed'];
    const idx = order.indexOf((status||'active'));
    return idx >= 0 ? idx : 0;
  };

  return (
    <div className="container mt-6 max-w-6xl">
      <h2 className="text-xl font-semibold mb-4">Engagements</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 bg-white border rounded p-3">
          {!items.length && <div className="text-sm text-slate-500">No engagements yet.</div>}
          <ul className="space-y-2">
            {items.map(it => (
              <li key={it.id || it._id} className={`p-2 rounded border cursor-pointer ${selected?.id===it.id?'bg-blue-50 border-blue-300':''}`} onClick={()=>{ setSelected(it); loadTracking(it.id||it._id); }}>
                <div className="font-semibold text-slate-900">{it.description || it.area_id || 'Engagement'}</div>
                <div className="text-xs text-slate-500">Status: {it.status || 'active'}</div>
              </li>
            ))}
          </ul>
        </div>
        <div className="md:col-span-2 bg-white border rounded p-4">
          {!selected ? (
            <div className="text-sm text-slate-500">Select an engagement to view details.</div>
          ) : (
            <div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-lg font-semibold">{selected.description || 'Engagement'}</div>
                  <div className="text-xs text-slate-500">Client: {selected.client_user_id?.slice(0,6)} • Provider: {selected.provider_user_id?.slice(0,6)}</div>
                </div>
              </div>

              {/* Timeline */}
              <div className="mt-4">
                <div className="text-sm font-semibold mb-2">Timeline</div>
                {(() => { const idx = stepIndex(currentStatus(selected)); const steps=['Active','In Progress','Under Review','Completed']; return (
                  <div>
                    <div className="flex items-center gap-2">
                      {steps.map((label,i)=> (
                        <div key={label} className="flex-1 flex items-center gap-2">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${i<=idx?'bg-blue-600 text-white':'bg-slate-200 text-slate-500'}`}>{i+1}</div>
                          {i<steps.length-1 && <div className={`h-1 flex-1 rounded ${i<idx?'bg-blue-600':'bg-slate-200'}`}></div>}
                        </div>
                      ))}
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs text-slate-600">
                      {steps.map(label=> (<span key={label}>{label}</span>))}
                    </div>
                  </div>
                ); })()}
              </div>

              {/* Tracking history */}
              <div className="mt-4">
                <div className="text-sm font-semibold mb-2">Activity</div>
                <ul className="space-y-2 max-h-48 overflow-y-auto">
                  {tracking.map(ev => (
                    <li key={ev._id} className="p-2 border rounded flex items-center justify-between">
                      <div>
                        <div className="font-medium capitalize">{(ev.status||'').replace('_',' ')}</div>
                        <div className="text-xs text-slate-500">{new Date(ev.updated_at).toLocaleString()}</div>
                      </div>
                      {ev.progress_percentage!=null && <div className="text-xs text-slate-500">{ev.progress_percentage}%</div>}
                    </li>
                  ))}
                  {!tracking.length && <div className="text-sm text-slate-500">No activity yet.</div>}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
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
      {!showLanding && <Header />}
      {showLanding ? (
        <Landing />
      ) : (
        <Routes>
          <Route path="/verify/cert/:id" element={<VerifyCert />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<ProfileSettings />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="/free-resources" element={<FreeResourcesPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/engagements" element={<EngagementsPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/home" element={<HomeRouter />} />
          <Route path="/business/profile" element={<BusinessProfileForm />} />
          <Route path="/service-request" element={<ServiceRequestPage />} />
          <Route path="/provider/proposals" element={<ProviderProposalsPage />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/agency" element={<AgencyHome />} />
          <Route path="/navigator/analytics" element={<NavigatorAnalyticsPage />} />
          {/* <Route path="/brand-preview" element={<BrandPreview />} /> */}
          <Route path="/opportunities" element={<OpportunitiesPage />} />
          <Route path="/" element={<Navigate to={me?'/home':'/'} replace />} />
        </Routes>
      )}
      <Toaster richColors position="top-center" />
    </div>
  );
}

// ---------------- Phase 3: Contextual KB Cards Component ----------------
function KBContextualCards({ areaId, context, title, limit = 3 }) {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (areaId) {
      loadContextualCards();
    }
  }, [areaId, context]);

  const loadContextualCards = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/knowledge-base/contextual-cards`, {
        params: { area_id: areaId, user_context: context, limit }
      });
      setCards(data.cards || []);
    } catch (e) {
      console.error('Failed to load contextual cards:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-slate-600">Loading resources...</span>
        </div>
      </div>
    );
  }

  if (!cards.length) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C20.832 18.477 19.246 18 17.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <h4 className="text-lg font-semibold text-slate-900">{title || 'Recommended Resources'}</h4>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((card) => (
          <div key={card.id} className="bg-white rounded-lg p-4 border border-blue-200 hover:border-blue-300 transition-colors">
            <div className="flex items-start justify-between mb-2">
              <h5 className="text-sm font-semibold text-slate-900 line-clamp-2">{card.title}</h5>
              <div className="flex items-center gap-1 text-xs text-slate-500">
                {card.content_type === 'template' && (
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                )}
                {card.content_type === 'checklist' && (
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                )}
              </div>
            </div>
            
            <p className="text-xs text-slate-600 mb-3 line-clamp-3">{card.description}</p>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                {card.difficulty_level && (
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    card.difficulty_level === 'beginner' ? 'bg-green-100 text-green-700' :
                    card.difficulty_level === 'intermediate' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {card.difficulty_level}
                  </span>
                )}
                {card.estimated_time && (
                  <span className="text-xs text-slate-500">{card.estimated_time}</span>
                )}
              </div>
              
              <button 
                className="btn btn-sm btn-primary text-xs px-3 py-1"
                onClick={() => {
                  // Navigate to knowledge base with specific article
                  window.open(`/knowledge-base#article-${card.id}`, '_blank');
                }}
              >
                View
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <button 
          className="btn btn-sm border text-blue-700 hover:bg-blue-50"
          onClick={() => window.open(`/knowledge-base?area=${areaId}`, '_blank')}
        >
          View All Resources for This Area
        </button>
      </div>
    </div>
  );
}

// ---------------- Phase 3: AI Assistant Component ----------------
function AIAssistantCard({ areaId, context }) {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [nextActions, setNextActions] = useState([]);

  useEffect(() => {
    if (isOpen && !nextActions.length) {
      loadNextBestActions();
    }
  }, [isOpen]);

  const loadNextBestActions = async () => {
    try {
      const me = JSON.parse(localStorage.getItem('polaris_me') || 'null');
      if (!me) return;

      const { data } = await axios.post(`${API}/knowledge-base/next-best-actions`, {
        user_id: me.id,
        current_gaps: [areaId], // Current area as gap for context
        completed_areas: [],
        business_profile: {}
      });

      // Parse AI response to extract actions (simplified)
      if (data.recommendations) {
        setNextActions([
          {
            title: "Complete Current Assessment Area",
            description: "Focus on completing this business area assessment first.",
            priority: "high",
            estimated_time: "30 minutes"
          },
          {
            title: "Review Knowledge Base Resources",
            description: "Explore templates and guides specific to this area.",
            priority: "medium", 
            estimated_time: "15 minutes"
          },
          {
            title: "Consider Professional Help",
            description: "Get expert assistance for complex requirements.",
            priority: "low",
            estimated_time: "Varies"
          }
        ]);
      }
    } catch (e) {
      console.error('Failed to load next best actions:', e);
    }
  };

  const askAI = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    try {
      const me = JSON.parse(localStorage.getItem('polaris_me') || 'null');
      const { data } = await axios.post(`${API}/knowledge-base/ai-assistance`, {
        question: question,
        area_id: areaId,
        context: { page: context, area: areaId },
        user_assessment_data: { gaps: [areaId] }
      });

      setResponse(data.response || 'Sorry, I couldn\'t provide an answer right now.');
    } catch (e) {
      setResponse('I\'m having trouble right now. Please try again or contact support.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-sm border p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900">AI Business Assistant</h4>
              <p className="text-xs text-slate-600">Get personalized guidance and next steps</p>
            </div>
          </div>
          <button 
            className="btn btn-sm btn-primary"
            onClick={() => setIsOpen(true)}
          >
            Get AI Help
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <h4 className="text-lg font-semibold text-slate-900">AI Business Assistant</h4>
        </div>
        <button 
          className="text-slate-500 hover:text-slate-700"
          onClick={() => setIsOpen(false)}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Next Best Actions */}
      {nextActions.length > 0 && (
        <div className="mb-6">
          <h5 className="text-sm font-semibold text-slate-900 mb-3">💡 Next Best Actions</h5>
          <div className="space-y-2">
            {nextActions.map((action, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  action.priority === 'high' ? 'bg-red-500' :
                  action.priority === 'medium' ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}></div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h6 className="text-sm font-medium text-slate-900">{action.title}</h6>
                    <span className="text-xs text-slate-500">({action.estimated_time})</span>
                  </div>
                  <p className="text-xs text-slate-600">{action.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Chat Interface */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Ask me anything about this business area:
          </label>
          <div className="flex gap-2">
            <input 
              type="text"
              className="input flex-1"
              placeholder="e.g., How do I get started with business licensing?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && askAI()}
            />
            <button 
              className="btn btn-primary"
              onClick={askAI}
              disabled={loading || !question.trim()}
            >
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </div>
        </div>

        {response && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-sm text-blue-900">
                <strong>AI Assistant:</strong>
                <div className="mt-1 whitespace-pre-wrap">{response}</div>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-center pt-2">
          <p className="text-xs text-slate-500">
            Powered by AI • For complex issues, consider getting professional help
          </p>
        </div>
      </div>
    </div>
  );
}

// ---------------- Phase 4: Multi-tenant/White-label Components ----------------
function AgencyThemeManager() {
  const [theme, setTheme] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const me = JSON.parse(localStorage.getItem('polaris_me') || 'null');

  useEffect(() => {
    if (me?.role === 'agency') {
      loadAgencyTheme();
    }
  }, []);

  const loadAgencyTheme = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/agency/theme/${me.id}`);
      setTheme(data);
    } catch (e) {
      console.log('No existing theme found, creating default:', e.response?.status);
      // No theme exists yet, create default
      setTheme({
        agency_id: me.id,
        branding_name: '',
        theme_config: {
          primary_color: '#1B365D',
          secondary_color: '#4A90C2',
          logo_url: ''
        },
        contact_info: {
          support_email: '',
          website: ''
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const saveTheme = async () => {
    if (!theme) return;
    
    setSaving(true);
    try {
      await axios.post(`${API}/agency/theme`, theme);
      toast.success('Agency theme updated successfully');
    } catch (e) {
      console.error('Theme save error:', e.response?.data);
      toast.error('Failed to update theme', { 
        description: e.response?.data?.detail || 'Unknown error occurred' 
      });
    } finally {
      setSaving(false);
    }
  };

  if (!me || me.role !== 'agency') {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="text-center text-slate-500">
          <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <h3 className="text-lg font-medium text-slate-900 mb-2">Access Restricted</h3>
          <p className="text-slate-600">Theme management is only available to agency users.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center gap-2 justify-center">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading theme settings...</span>
        </div>
      </div>
    );
  }

  if (!theme) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="text-center text-slate-500">
          <p>Unable to load theme settings. Please try again.</p>
          <button className="btn btn-primary mt-3" onClick={loadAgencyTheme}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="border-b p-6">
        <h3 className="text-xl font-semibold">Agency Theme & Branding</h3>
        <p className="text-slate-600 mt-1">Customize the platform appearance for your agency</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Branding Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Agency Branding Name
          </label>
          <input
            type="text"
            className="input w-full"
            value={theme.branding_name || ''}
            onChange={(e) => setTheme({...theme, branding_name: e.target.value})}
            placeholder="Your Agency Name"
          />
        </div>

        {/* Colors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Primary Color
            </label>
            <div className="flex gap-2">
              <input
                type="color"
                className="w-12 h-10 border border-slate-300 rounded"
                value={theme.theme_config?.primary_color || '#1B365D'}
                onChange={(e) => setTheme({
                  ...theme,
                  theme_config: { ...theme.theme_config, primary_color: e.target.value }
                })}
              />
              <input
                type="text"
                className="input flex-1"
                value={theme.theme_config?.primary_color || '#1B365D'}
                onChange={(e) => setTheme({
                  ...theme,
                  theme_config: { ...theme.theme_config, primary_color: e.target.value }
                })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Secondary Color
            </label>
            <div className="flex gap-2">
              <input
                type="color"
                className="w-12 h-10 border border-slate-300 rounded"
                value={theme.theme_config?.secondary_color || '#4A90C2'}
                onChange={(e) => setTheme({
                  ...theme,
                  theme_config: { ...theme.theme_config, secondary_color: e.target.value }
                })}
              />
              <input
                type="text"
                className="input flex-1"
                value={theme.theme_config?.secondary_color || '#4A90C2'}
                onChange={(e) => setTheme({
                  ...theme,
                  theme_config: { ...theme.theme_config, secondary_color: e.target.value }
                })}
              />
            </div>
          </div>
        </div>

        {/* Logo URL */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Logo URL
          </label>
          <input
            type="url"
            className="input w-full"
            value={theme.theme_config?.logo_url || ''}
            onChange={(e) => setTheme({
              ...theme,
              theme_config: { ...theme.theme_config, logo_url: e.target.value }
            })}
            placeholder="https://example.com/logo.png"
          />
        </div>

        {/* Contact Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Support Email
            </label>
            <input
              type="email"
              className="input w-full"
              value={theme.contact_info?.support_email || ''}
              onChange={(e) => setTheme({
                ...theme,
                contact_info: { ...theme.contact_info, support_email: e.target.value }
              })}
              placeholder="support@youragency.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Website
            </label>
            <input
              type="url"
              className="input w-full"
              value={theme.contact_info?.website || ''}
              onChange={(e) => setTheme({
                ...theme,
                contact_info: { ...theme.contact_info, website: e.target.value }
              })}
              placeholder="https://youragency.com"
            />
          </div>
        </div>

        {/* Preview */}
        <div className="bg-slate-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-slate-900 mb-3">Preview</h4>
          <div 
            className="rounded-lg p-4 text-white"
            style={{ backgroundColor: theme.theme_config?.primary_color || '#1B365D' }}
          >
            <h3 className="text-lg font-semibold">
              {theme.branding_name || 'Your Agency Name'} - Procurement Platform
            </h3>
            <p className="opacity-90 text-sm">Small Business Readiness Assessment</p>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-3">
          <button className="btn" onClick={loadAgencyTheme} disabled={loading}>
            Reset
          </button>
          <button 
            className="btn btn-primary"
            onClick={saveTheme}
            disabled={saving || !theme}
          >
            {saving ? 'Saving...' : 'Save Theme'}
          </button>
        </div>
      </div>
    </div>
  );
}

function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, [showAll]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/notifications/my`, {
        params: { unread_only: !showAll }
      });
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      console.error('Failed to load notifications:', e);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await axios.put(`${API}/notifications/${notificationId}/read`);
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      ));
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (e) {
      console.error('Failed to mark as read:', e);
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      info: '📋',
      success: '✅',
      warning: '⚠️',
      error: '❌',
      opportunity: '🎯',
      assessment: '📝',
      service: '🔧'
    };
    return icons[type] || '📋';
  };

  return (
    <div className="container mt-6 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">Notifications</h2>
              <p className="text-slate-600 mt-1">Stay updated with your latest activities and updates</p>
            </div>
            <div className="flex gap-2">
              <button
                className={`btn btn-sm ${!showAll ? 'btn-primary' : ''}`}
                onClick={() => setShowAll(false)}
              >
                Unread ({unreadCount})
              </button>
              <button
                className={`btn btn-sm ${showAll ? 'btn-primary' : ''}`}
                onClick={() => setShowAll(true)}
              >
                All
              </button>
            </div>
          </div>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-6 text-center">
              <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <span className="text-sm text-slate-600">Loading notifications...</span>
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-6 text-center text-slate-500">
              <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5V3h0z" />
              </svg>
              <h3 className="text-lg font-medium text-slate-900 mb-2">No notifications</h3>
              <p>{showAll ? 'No notifications yet' : 'No unread notifications'}</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <div 
                  key={notification.id} 
                  className={`p-4 hover:bg-slate-50 transition-colors ${!notification.read ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notification.notification_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <h4 className="text-sm font-medium text-slate-900">
                          {notification.title}
                        </h4>
                        <div className="flex items-center gap-2 ml-2 flex-shrink-0">
                          <span className="text-xs text-slate-500">
                            {new Date(notification.created_at).toLocaleDateString()}
                          </span>
                          {!notification.read && (
                            <button
                              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                              onClick={() => markAsRead(notification.id)}
                            >
                              Mark read
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 mt-1">
                        {notification.message}
                      </p>
                      {notification.action_url && (
                        <button
                          className="text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium"
                          onClick={() => {
                            markAsRead(notification.id);
                            window.location.href = notification.action_url;
                          }}
                        >
                          Take Action →
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------- Quick Wins: System Health Component ----------------
function SystemHealthDashboard() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get(`${API}/system/health`);
      setHealth(data);
    } catch (e) {
      console.error('System health check failed:', e);
      setError(e.response?.data?.detail || e.message || 'Failed to check system health');
      setHealth({
        status: 'unhealthy',
        error: 'Failed to check system health',
        components: {
          database: 'unknown',
          ai_integration: 'unknown',
          payment_integration: 'unknown'
        },
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      healthy: 'text-green-600 bg-green-100',
      unhealthy: 'text-red-600 bg-red-100',
      unavailable: 'text-yellow-600 bg-yellow-100',
      unknown: 'text-slate-600 bg-slate-100'
    };
    return colors[status] || 'text-slate-600 bg-slate-100';
  };

  const getStatusIcon = (status) => {
    if (status === 'healthy') return '✅';
    if (status === 'unhealthy') return '❌';
    if (status === 'unavailable') return '⚠️';
    return '❓';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">System Health Monitor</h3>
          <p className="text-slate-600 text-sm">Real-time system status and component health</p>
        </div>
        <div className="flex items-center gap-3">
          {health && (
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${health.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm font-medium capitalize">{health.status}</span>
            </div>
          )}
          {loading && (
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          )}
          <button 
            className="btn btn-sm"
            onClick={checkSystemHealth}
            disabled={loading}
          >
            {loading ? 'Checking...' : 'Check Now'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-red-900">System Health Check Failed</h4>
              <p className="text-sm text-red-800 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {health ? (
        <div>
          {/* Overall Status */}
          <div className="mb-6 p-4 rounded-lg bg-slate-50">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-slate-900">Overall System Status</h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-2xl">{getStatusIcon(health.status)}</span>
                  <span className="text-lg font-semibold capitalize">{health.status}</span>
                </div>
              </div>
              <div className="text-right text-sm text-slate-500">
                <div>Version: {health.version || '1.0.0'}</div>
                <div>Last Check: {health.timestamp ? new Date(health.timestamp).toLocaleString() : 'Just now'}</div>
              </div>
            </div>
          </div>

          {/* Component Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {health.components && Object.entries(health.components).map(([component, status]) => (
              <div key={component} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium capitalize">
                    {component.replace(/_/g, ' ')}
                  </h4>
                  <span className="text-lg">{getStatusIcon(status)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)}`}>
                    {status}
                  </span>
                  {component === 'database' && status === 'healthy' && (
                    <span className="text-xs text-slate-500">Connected</span>
                  )}
                  {component === 'ai_integration' && status === 'healthy' && (
                    <span className="text-xs text-slate-500">API Ready</span>
                  )}
                  {component === 'payment_integration' && status === 'healthy' && (
                    <span className="text-xs text-slate-500">Stripe OK</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* System Metrics */}
          <div className="bg-slate-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-slate-900 mb-3">System Information</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-slate-500">Environment</div>
                <div className="font-medium">Production</div>
              </div>
              <div>
                <div className="text-slate-500">Uptime</div>
                <div className="font-medium text-green-600">Operational</div>
              </div>
              <div>
                <div className="text-slate-500">Last Deploy</div>
                <div className="font-medium">Recently</div>
              </div>
              <div>
                <div className="text-slate-500">Monitoring</div>
                <div className="font-medium text-blue-600">Active</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="w-12 h-12 border-2 border-slate-300 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500">Initializing system health check...</p>
        </div>
      )}
    </div>
  );
}

// ---------------- Phase 4: White-label Landing & Certificate Verification ----------------
function WhiteLabelLanding({ agencyId }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWhiteLabelConfig();
  }, [agencyId]);

  const loadWhiteLabelConfig = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/public/white-label/${agencyId}`);
      setConfig(data);
    } catch (e) {
      console.error('Failed to load white-label config:', e);
      // Fallback to default Polaris branding
      setConfig({
        branding_name: "Polaris",
        theme_config: {
          primary_color: "#1B365D",
          secondary_color: "#4A90C2",
          logo_url: "/polaris-logo.svg"
        },
        custom_messaging: {
          hero_title: "Small Business Procurement Readiness",
          hero_subtitle: "Assess readiness, get certified, and win government contracts",
          cta_text: "Start Assessment"
        }
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Loading platform...</p>
        </div>
      </div>
    );
  }

  if (!config) return null;

  const primaryColor = config.theme_config?.primary_color || '#1B365D';
  const secondaryColor = config.theme_config?.secondary_color || '#4A90C2';

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section with Agency Branding */}
      <div 
        className="relative text-white py-24"
        style={{ 
          background: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)` 
        }}
      >
        <div className="container mx-auto px-6 text-center">
          {config.theme_config?.logo_url && (
            <img 
              src={config.theme_config.logo_url} 
              alt={config.branding_name}
              className="h-16 mx-auto mb-6"
            />
          )}
          
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            {config.custom_messaging?.hero_title || `${config.branding_name} Platform`}
          </h1>
          
          <p className="text-xl md:text-2xl opacity-90 mb-8 max-w-3xl mx-auto">
            {config.custom_messaging?.hero_subtitle || "Powered by Polaris - Small Business Assessment & Certification"}
          </p>
          
          <button 
            className="px-8 py-4 bg-white text-slate-900 rounded-lg font-semibold hover:bg-slate-100 transition-colors text-lg"
            onClick={() => window.location.href = '#auth'}
          >
            {config.custom_messaging?.cta_text || "Begin Assessment"}
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Comprehensive Procurement Readiness
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Complete assessment, get certified, and unlock government contracting opportunities
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div 
                className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: `${primaryColor}20` }}
              >
                <svg className="w-8 h-8" style={{ color: primaryColor }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">8-Area Assessment</h3>
              <p className="text-slate-600">Comprehensive evaluation across all key business areas for procurement readiness</p>
            </div>

            <div className="text-center p-6">
              <div 
                className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: `${primaryColor}20` }}
              >
                <svg className="w-8 h-8" style={{ color: primaryColor }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 714.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 713.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 710 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 710-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 713.138-3.138z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Official Certification</h3>
              <p className="text-slate-600">Receive verified certification recognized by government agencies</p>
            </div>

            <div className="text-center p-6">
              <div 
                className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: `${primaryColor}20` }}
              >
                <svg className="w-8 h-8" style={{ color: primaryColor }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 515.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 919.288 0M15 7a3 3 0 11-6 0 3 3 0 616 0zm6 3a2 2 0 11-4 0 2 2 0 414 0zM7 10a2 2 0 11-4 0 2 2 0 414 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Expert Support</h3>
              <p className="text-slate-600">Connect with qualified service providers for professional assistance</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer with Agency Branding */}
      <footer className="bg-slate-900 text-white py-8">
        <div className="container mx-auto px-6 text-center">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">{config.branding_name}</h3>
            {config.contact_info?.website && (
              <a 
                href={config.contact_info.website}
                className="text-slate-400 hover:text-white transition-colors"
              >
                {config.contact_info.website}
              </a>
            )}
          </div>
          <p className="text-slate-400 text-sm">
            Powered by Polaris • Small Business Procurement Readiness Platform
          </p>
        </div>
      </footer>
    </div>
  );
}

function CertificateVerification({ certificateId }) {
  const [certificate, setCertificate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (certificateId) {
      verifyCertificate();
    }
  }, [certificateId]);

  const verifyCertificate = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get(`${API}/verify/certificate/${certificateId}`);
      setCertificate(data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Certificate verification failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Verifying certificate...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center p-6">
          <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Certificate Verification Failed</h1>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            className="btn btn-primary"
            onClick={verifyCertificate}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!certificate) return null;

  const primaryColor = certificate.agency_branding?.primary_color || '#1B365D';

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-4xl mx-auto px-6">
        {/* Verification Success Header */}
        <div className="text-center mb-8">
          <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 714.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 713.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 710 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 710-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 713.138-3.138z" />
          </svg>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Certificate Verified ✅</h1>
          <p className="text-lg text-slate-600">This certificate is valid and officially recognized</p>
        </div>

        {/* Certificate Details */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Certificate Header */}
          <div 
            className="text-white p-8"
            style={{ backgroundColor: primaryColor }}
          >
            <div className="flex items-center justify-between">
              <div>
                {certificate.agency_branding?.logo_url && (
                  <img 
                    src={certificate.agency_branding.logo_url} 
                    alt={certificate.agency_branding.name}
                    className="h-12 mb-4"
                  />
                )}
                <h2 className="text-2xl font-bold">{certificate.certificate_type}</h2>
                <p className="opacity-90">Issued by {certificate.agency_branding?.name || 'Polaris'}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">{certificate.certification_level}</div>
                <div className="opacity-90">Certification Level</div>
              </div>
            </div>
          </div>

          {/* Certificate Body */}
          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Certificate Holder</h3>
                <div className="space-y-2">
                  <div>
                    <span className="text-slate-600">Business Name:</span>
                    <span className="ml-2 font-medium">{certificate.business_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Certificate Holder:</span>
                    <span className="ml-2 font-medium">{certificate.client_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Certificate ID:</span>
                    <span className="ml-2 font-mono text-sm">{certificate.certificate_id}</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Verification Code:</span>
                    <span className="ml-2 font-mono text-sm font-bold">{certificate.verification_code}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Certificate Details</h3>
                <div className="space-y-2">
                  <div>
                    <span className="text-slate-600">Issued Date:</span>
                    <span className="ml-2 font-medium">{new Date(certificate.issued_at).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Expires Date:</span>
                    <span className="ml-2 font-medium">{new Date(certificate.expires_at).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Status:</span>
                    <span className="ml-2 font-medium text-green-600">Valid & Active</span>
                  </div>
                  <div>
                    <span className="text-slate-600">Compliance Standards:</span>
                    <div className="ml-2 flex gap-2 mt-1">
                      {certificate.compliance_standards?.map((standard, index) => (
                        <span key={index} className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded">
                          {standard}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Verification Footer */}
            <div className="mt-8 pt-6 border-t border-slate-200 text-center">
              <p className="text-sm text-slate-600">
                This certificate has been verified as authentic and is recognized for government contracting purposes.
                For questions about this certificate, please contact {certificate.agency_branding?.name || 'the issuing agency'}.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App(){ return (<BrowserRouter><AppShell /></BrowserRouter>); }