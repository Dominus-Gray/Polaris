import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'https://polar-docs-ai.preview.emergentagent.com/api';

export default function Login(){
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try{
      const { data } = await axios.post(`${API_BASE}/auth/login`, { email, password });
      const token = data?.access_token || data?.token;
      if (!token) throw new Error('No token returned');
      localStorage.setItem('polaris_token', token);
      // load profile
      try{
        const meRes = await axios.get(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        localStorage.setItem('polaris_me', JSON.stringify(meRes.data));
      }catch(_){ /* ignore */ }
      navigate('/home');
    }catch(e){
      setError(e.response?.data?.detail || e.message);
    }finally{
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="bg-white rounded-xl shadow-sm border w-full max-w-md p-6">
        <h1 className="text-xl font-semibold mb-4">Sign in</h1>
        {error && (
          <div className="state-error mb-3"><div className="title">Login failed</div><div className="sub">{error}</div></div>
        )}
        <form onSubmit={submit} className="space-y-3">
          <div>
            <label className="form-label">Email</label>
            <input className="input w-full" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>
          <div>
            <label className="form-label">Password</label>
            <input className="input w-full" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button className="btn btn-primary w-full" type="submit" disabled={loading}>{loading? 'Signing in...' : 'Sign in'}</button>
        </form>
      </div>
    </div>
  );
}