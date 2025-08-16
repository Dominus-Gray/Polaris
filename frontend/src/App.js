import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, Navigate, useParams } from "react-router-dom";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ... existing components above ...

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

function AppShell(){ /* existing content preserved */ }

export default function App(){ return (<BrowserRouter>
  <Routes>
    <Route path="/verify/cert/:id" element={<VerifyCert />} />
    <Route path="*" element={<AppShell />} />
  </Routes>
</BrowserRouter>); }