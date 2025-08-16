import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PolarisLogo({ size = 22 }) {
  return (
    <div className="flex items-center gap-2" aria-label="Polaris">
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 1 L13.8 8.2 L21 10 L13.8 11.8 L12 19 L10.2 11.8 L3 10 L10.2 8.2 Z" fill="#1B365D"/>
        <path d="M12 5 L12.9 7.8 L15.5 8.6 L12.9 9.4 L12 12.2 L11.1 9.4 L8.5 8.6 L11.1 7.8 Z" fill="#4A90C2"/>
      </svg>
      <span className="font-semibold tracking-tight" style={{color:'#1B365D'}}>POLARIS</span>
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
  
  const submit = async()=>{
    try{
      if(mode==='register'){
        await axios.post(`${API}/auth/register`, { email, password, role });
      }
      const { data } = await axios.post(`${API}/auth/login`, { email, password });
      localStorage.setItem('polaris_token', data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      const me = await axios.get(`${API}/auth/me`);
      localStorage.setItem('polaris_me', JSON.stringify(me.data));
      toast.success('Welcome', { description: me.data.email });
      navigate('/home');
    }catch(e){ toast.error('Auth failed', { description: e?.response?.data?.detail || e.message }); }
  };

  const handleGoogleAuth = () => {
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
            <select className="input flex-1" value={mode} onChange={e=>setMode(e.target.value)}>
              <option value="login">Login</option>
              <option value="register">Register</option>
            </select>
            {mode==='register' && (
              <select className="input flex-1" value={role} onChange={e=>setRole(e.target.value)}>
                <option value="client">Client</option>
                <option value="provider">Provider</option>
                <option value="navigator">Navigator</option>
                <option value="agency">Agency</option>
              </select>
            )}
          </div>
          <input className="input w-full" placeholder="Email address" type="email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input className="input w-full" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
          <button className="btn btn-primary w-full" onClick={submit}>
            {mode==='login' ? 'Sign In' : 'Create Account'}
          </button>
        </div>

        <p className="text-xs text-slate-500 text-center mt-4">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
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
      <div className="container mt-10 max-w-md mx-auto text-center">
        <div className="bg-white rounded-lg p-8 shadow-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-lg font-semibold mb-2">Setting up your account...</h2>
          <p className="text-slate-600 text-sm">Please wait while we complete your registration.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-10 max-w-md mx-auto">
      <div className="bg-white rounded-lg p-8 shadow-lg">
        <h2 className="text-xl font-semibold mb-4 text-center">Complete Your Profile</h2>
        <p className="text-slate-600 text-sm mb-6 text-center">
          Please select your role to personalize your Polaris experience.
        </p>
        
        <div className="space-y-3 mb-6">
          <label className="flex items-center p-3 border rounded-lg hover:bg-slate-50 cursor-pointer">
            <input 
              type="radio" 
              name="role" 
              value="client" 
              checked={role === 'client'} 
              onChange={(e) => setRole(e.target.value)}
              className="mr-3" 
            />
            <div>
              <div className="font-medium">Small Business</div>
              <div className="text-sm text-slate-600">Assess readiness and get certified</div>
            </div>
          </label>
          
          <label className="flex items-center p-3 border rounded-lg hover:bg-slate-50 cursor-pointer">
            <input 
              type="radio" 
              name="role" 
              value="provider" 
              checked={role === 'provider'} 
              onChange={(e) => setRole(e.target.value)}
              className="mr-3" 
            />
            <div>
              <div className="font-medium">Service Provider</div>
              <div className="text-sm text-slate-600">Connect with businesses needing help</div>
            </div>
          </label>
          
          <label className="flex items-center p-3 border rounded-lg hover:bg-slate-50 cursor-pointer">
            <input 
              type="radio" 
              name="role" 
              value="navigator" 
              checked={role === 'navigator'} 
              onChange={(e) => setRole(e.target.value)}
              className="mr-3" 
            />
            <div>
              <div className="font-medium">Navigator</div>
              <div className="text-sm text-slate-600">Review and guide businesses</div>
            </div>
          </label>
          
          <label className="flex items-center p-3 border rounded-lg hover:bg-slate-50 cursor-pointer">
            <input 
              type="radio" 
              name="role" 
              value="agency" 
              checked={role === 'agency'} 
              onChange={(e) => setRole(e.target.value)}
              className="mr-3" 
            />
            <div>
              <div className="font-medium">Local Agency</div>
              <div className="text-sm text-slate-600">Manage community programs</div>
            </div>
          </label>
        </div>

        <button 
          className="btn btn-primary w-full"
          onClick={() => window.location.reload()}
        >
          Continue with {role}
        </button>
      </div>
    </div>
  );
}

function AssessmentPage(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  
  // Redirect non-clients to home
  if (!me || me.role !== 'client') {
    return <Navigate to="/home" replace />;
  }

  return (
    <div className="container mt-6">
      <h2 className="text-xl font-semibold mb-3">Small Business Maturity Assessment</h2>
      <p className="text-slate-600 mb-6">Complete your assessment to determine your business maturity and procurement readiness.</p>
      
      <div className="assessment-overview">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center">
            <span className="text-sm font-semibold">1</span>
          </div>
          <h3 className="text-lg font-semibold">Assessment Overview</h3>
        </div>
        <p className="text-sm text-slate-600 mb-4">
          This assessment covers 8 key business areas to evaluate your procurement readiness. 
          Each area focuses on concrete deliverables and evidence-based requirements.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Business Formation & Registration</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Financial Operations</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Legal & Contracting</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Technology & Cybersecurity</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Human Resources</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Marketing & Sales</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Supply Chain Management</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span>Quality Assurance</span>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 text-amber-800">
          <span className="text-lg">⚠️</span>
          <div>
            <div className="font-medium">Assessment Coming Soon</div>
            <div className="text-sm">The full interactive assessment is currently under development. Please check back soon or contact support for assistance.</div>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="btn btn-primary" onClick={()=>navigate('/home')}>Return to Dashboard</button>
        <button className="btn" onClick={()=>navigate('/matching')}>Request Provider Assistance</button>
      </div>
    </div>
  );
}

// ---------------- Business Profile Form ----------------
function BusinessProfileForm(){
  const navigate = useNavigate();
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const [form, setForm] = useState({ 
    company_name:'', legal_entity_type:'LLC', tax_id:'', registered_address:'', mailing_address:'', 
    website_url:'', industry:'', primary_products_services:'', revenue_range:'', revenue_currency:'USD', 
    employees_count:'', year_founded:'', ownership_structure:'private', contact_name:'', contact_title:'', 
    contact_email:'', contact_phone:'', billing_contact_name:'', billing_contact_email:'', 
    billing_contact_phone:'', payment_methods:'Card, ACH', subscription_plan:'Basic', 
    subscription_features:'', billing_frequency:'monthly' 
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
      case 'mailing_address':
        if (!value.trim()) errors.push(`${name.replace('_', ' ')} is required`);
        else if (value.trim().length < 10) errors.push('Address must be at least 10 characters');
        break;
      
      case 'website_url':
        if (value && !validationPatterns.website.test(value)) errors.push('Invalid website URL format');
        break;
      
      case 'industry':
        if (!value.trim()) errors.push('Industry is required');
        else if (value.trim().length < 2) errors.push('Industry must be at least 2 characters');
        break;
      
      case 'primary_products_services':
        if (!value.trim()) errors.push('Primary products/services is required');
        else if (value.trim().length < 5) errors.push('Products/services description must be at least 5 characters');
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
        payment_methods: form.payment_methods.split(',').map(s=>s.trim()).filter(Boolean),
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <input 
            className={`input ${errors.company_name ? 'border-red-500' : ''}`} 
            placeholder="Company name *" 
            value={form.company_name} 
            onChange={e=>handleFieldChange('company_name', e.target.value)} 
          />
          {errors.company_name && <div className="text-red-500 text-xs mt-1">{errors.company_name}</div>}
        </div>
        <select className="input" value={form.legal_entity_type} onChange={e=>handleFieldChange('legal_entity_type', e.target.value)}>
          <option>LLC</option><option>C-Corp</option><option>S-Corp</option><option>Partnership</option><option>Sole Proprietorship</option>
        </select>
        <div>
          <input 
            className={`input ${errors.tax_id ? 'border-red-500' : ''}`} 
            placeholder="EIN / Tax ID *" 
            value={form.tax_id} 
            onChange={e=>handleFieldChange('tax_id', e.target.value)} 
          />
          {errors.tax_id && <div className="text-red-500 text-xs mt-1">{errors.tax_id}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.registered_address ? 'border-red-500' : ''}`} 
            placeholder="Registered business address *" 
            value={form.registered_address} 
            onChange={e=>handleFieldChange('registered_address', e.target.value)} 
          />
          {errors.registered_address && <div className="text-red-500 text-xs mt-1">{errors.registered_address}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.mailing_address ? 'border-red-500' : ''}`} 
            placeholder="Mailing address *" 
            value={form.mailing_address} 
            onChange={e=>handleFieldChange('mailing_address', e.target.value)} 
          />
          {errors.mailing_address && <div className="text-red-500 text-xs mt-1">{errors.mailing_address}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.website_url ? 'border-red-500' : ''}`} 
            placeholder="Website URL" 
            value={form.website_url} 
            onChange={e=>handleFieldChange('website_url', e.target.value)} 
          />
          {errors.website_url && <div className="text-red-500 text-xs mt-1">{errors.website_url}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.industry ? 'border-red-500' : ''}`} 
            placeholder="Industry / Sector *" 
            value={form.industry} 
            onChange={e=>handleFieldChange('industry', e.target.value)} 
          />
          {errors.industry && <div className="text-red-500 text-xs mt-1">{errors.industry}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.primary_products_services ? 'border-red-500' : ''}`} 
            placeholder="Primary products / services *" 
            value={form.primary_products_services} 
            onChange={e=>handleFieldChange('primary_products_services', e.target.value)} 
          />
          {errors.primary_products_services && <div className="text-red-500 text-xs mt-1">{errors.primary_products_services}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.revenue_range ? 'border-red-500' : ''}`} 
            placeholder="Revenue range (e.g., $0-$100k) *" 
            value={form.revenue_range} 
            onChange={e=>handleFieldChange('revenue_range', e.target.value)} 
          />
          {errors.revenue_range && <div className="text-red-500 text-xs mt-1">{errors.revenue_range}</div>}
        </div>
        <select className="input" value={form.revenue_currency} onChange={e=>handleFieldChange('revenue_currency', e.target.value)}>
          <option>USD</option><option>MXN</option><option>EUR</option>
        </select>
        <div>
          <input 
            className={`input ${errors.employees_count ? 'border-red-500' : ''}`} 
            placeholder="Employees (range or exact) *" 
            value={form.employees_count} 
            onChange={e=>handleFieldChange('employees_count', e.target.value)} 
          />
          {errors.employees_count && <div className="text-red-500 text-xs mt-1">{errors.employees_count}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.year_founded ? 'border-red-500' : ''}`} 
            placeholder="Year founded" 
            value={form.year_founded} 
            onChange={e=>handleFieldChange('year_founded', e.target.value)} 
          />
          {errors.year_founded && <div className="text-red-500 text-xs mt-1">{errors.year_founded}</div>}
        </div>
        <input className="input" placeholder="Ownership structure (private/public)" value={form.ownership_structure} onChange={e=>handleFieldChange('ownership_structure', e.target.value)} />
        <div>
          <input 
            className={`input ${errors.contact_name ? 'border-red-500' : ''}`} 
            placeholder="Contact name *" 
            value={form.contact_name} 
            onChange={e=>handleFieldChange('contact_name', e.target.value)} 
          />
          {errors.contact_name && <div className="text-red-500 text-xs mt-1">{errors.contact_name}</div>}
        </div>
        <input className="input" placeholder="Contact title" value={form.contact_title} onChange={e=>handleFieldChange('contact_title', e.target.value)} />
        <div>
          <input 
            className={`input ${errors.contact_email ? 'border-red-500' : ''}`} 
            placeholder="Contact email *" 
            value={form.contact_email} 
            onChange={e=>handleFieldChange('contact_email', e.target.value)} 
          />
          {errors.contact_email && <div className="text-red-500 text-xs mt-1">{errors.contact_email}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.contact_phone ? 'border-red-500' : ''}`} 
            placeholder="Contact phone *" 
            value={form.contact_phone} 
            onChange={e=>handleFieldChange('contact_phone', e.target.value)} 
          />
          {errors.contact_phone && <div className="text-red-500 text-xs mt-1">{errors.contact_phone}</div>}
        </div>
        <input className="input" placeholder="Billing contact name" value={form.billing_contact_name} onChange={e=>handleFieldChange('billing_contact_name', e.target.value)} />
        <div>
          <input 
            className={`input ${errors.billing_contact_email ? 'border-red-500' : ''}`} 
            placeholder="Billing contact email" 
            value={form.billing_contact_email} 
            onChange={e=>handleFieldChange('billing_contact_email', e.target.value)} 
          />
          {errors.billing_contact_email && <div className="text-red-500 text-xs mt-1">{errors.billing_contact_email}</div>}
        </div>
        <div>
          <input 
            className={`input ${errors.billing_contact_phone ? 'border-red-500' : ''}`} 
            placeholder="Billing contact phone" 
            value={form.billing_contact_phone} 
            onChange={e=>handleFieldChange('billing_contact_phone', e.target.value)} 
          />
          {errors.billing_contact_phone && <div className="text-red-500 text-xs mt-1">{errors.billing_contact_phone}</div>}
        </div>
        <input className="input" placeholder="Payment methods accepted" value={form.payment_methods} onChange={e=>handleFieldChange('payment_methods', e.target.value)} />
        <input className="input" placeholder="Subscription plan (tier)" value={form.subscription_plan} onChange={e=>handleFieldChange('subscription_plan', e.target.value)} />
        <input className="input" placeholder="Subscription features (optional)" value={form.subscription_features} onChange={e=>handleFieldChange('subscription_features', e.target.value)} />
        <select className="input" value={form.billing_frequency} onChange={e=>handleFieldChange('billing_frequency', e.target.value)}>
          <option>monthly</option><option>annual</option>
        </select>
        <div className="col-span-1 md:col-span-2">
          <label className="text-sm font-medium">Business logo</label>
          <input type="file" className="input mt-1" onChange={e=>setLogo(e.target.files?.[0]||null)} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        {missing?.length>0 && <div className="text-xs text-amber-600">Missing: {missing.join(', ')}</div>}
        {Object.keys(errors).some(key => errors[key]) && (
          <div className="text-xs text-red-600">Please fix validation errors before saving</div>
        )}
        <button 
          className={`btn btn-primary ${isValidating ? 'opacity-50 cursor-not-allowed' : ''}`} 
          onClick={save}
          disabled={isValidating}
        >
          {isValidating ? 'Validating...' : 'Save & Continue'}
        </button>
      </div>
    </div>
  );
}

// ---------------- Home Pages ----------------
function ClientHome(){
  const [data, setData] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const navigate = useNavigate();
  useEffect(()=>{ 
    const load=async()=>{ 
      const {data} = await axios.get(`${API}/home/client`); 
      setData(data); 
      try{
        const certs = await axios.get(`${API}/client/certificates`);
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

  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  if(!data.profile_complete) return <BusinessProfileForm/>;
  return (
    <div className="container mt-6">
      <div className="dashboard-grid">
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Readiness Score
          </div>
          <div className="tile-num">{String(data.readiness || 0)}%</div>
          <div className="tile-sub">Evidence-approved</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            Opportunities
          </div>
          <div className="tile-num">{String(data.opportunities || 0)}</div>
          <div className="tile-sub">Available to you</div>
        </div>
        <div className="tile">
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Certificate
          </div>
          <div className="tile-num">{data.has_certificate? 'Yes' : 'No'}</div>
          <div className="tile-sub">Download once issued</div>
        </div>
        <div className="tile cursor-pointer hover:bg-gray-50 transition-colors" onClick={()=>navigate('/assessment')}>
          <div className="tile-title">
            <svg className="tile-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Assessment
          </div>
          <div className="tile-num">→</div>
          <div className="tile-sub">Continue</div>
        </div>
      </div>
      
      {certificates.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Your Certificates</h3>
          <div className="space-y-2">
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
        </div>
      )}

      <div className="mt-4 flex gap-2">
        <button className="btn btn-primary" onClick={()=>navigate('/matching')}>Request a provider</button>
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
  const navigate = useNavigate();
  useEffect(()=>{ const load=async()=>{ const {data} = await axios.get(`${API}/home/navigator`); setData(data); }; load(); },[]);
  if(!data) return <div className="container mt-6"><div className="skel h-10 w-40"/><div className="skel h-32 w-full mt-2"/></div>;
  return (
    <div className="container mt-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="tile"><div className="tile-title">Pending Reviews</div><div className="tile-num">{String(data.pending_reviews || 0)}</div><div className="tile-sub">awaiting review</div></div>
        <div className="tile"><div className="tile-title">Active Engagements</div><div className="tile-num">{String(data.active_engagements || 0)}</div></div>
        <div className="tile"><div className="tile-title">Queue</div><div className="tile-num">→</div><div className="tile-sub">Open</div></div>
      </div>
      <div className="mt-4"><Link className="btn btn-primary" to="/navigator">Open review queue</Link></div>
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
        <div className="tile"><div className="tile-title">Invites</div><div className="tile-num">{String(impact.invites?.total || 0)}</div><div className="tile-sub">total</div></div>
        <div className="tile"><div className="tile-title">Paid</div><div className="tile-num">{String(impact.invites?.paid || 0)}</div><div className="tile-sub">assessments</div></div>
        <div className="tile"><div className="tile-title">Revenue</div><div className="tile-num">${String(impact.revenue?.assessment_fees || 0)}</div><div className="tile-sub">assessment fees</div></div>
        <div className="tile"><div className="tile-title">Opportunities</div><div className="tile-num">{String(impact.opportunities?.count || 0)}</div></div>
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
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  return (
    <header className="header">
      <div className="header-inner">
        <PolarisLogo />
        <nav className="nav">
          {me && <Link className="link" to="/home">Home</Link>}
          {me && me.role==='client' && <Link className="link" to="/matching">Matching</Link>}
          {me && me.role==='provider' && <Link className="link" to="/provider/proposals">Proposals</Link>}
          {me && me.role==='navigator' && <Link className="link" to="/navigator">Navigator</Link>}
          {me && me.role==='agency' && <Link className="link" to="/agency">Agency</Link>}
        </nav>
        <div className="flex-1" />
        {!me ? <a className="btn" href="#auth">Sign in</a> : <Link className="btn" to="/home">Dashboard</Link>}
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
            <h1 className="hero-title mt-4">Your North Star for Procurement Success</h1>
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
                <img src="https://images.unsplash.com/photo-1545063328-c8e3faffa16f?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=600" alt="Assessment Dashboard" className="w-full h-48 object-cover" />
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
                <img src="https://images.unsplash.com/photo-1477013743164-ffc3a5e556da?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=600" alt="Analytics Dashboard" className="w-full h-48 object-cover" />
              </div>
              <div className="p-6">
                <h3 className="font-semibold text-lg text-slate-900 mb-2">Data-Driven Insights</h3>
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
                <img src="https://images.unsplash.com/photo-1532102235608-dc8fc689c9ab?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85&w=600" alt="Strategic Planning" className="w-full h-48 object-cover" />
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
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Driving Procurement Success</h2>
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