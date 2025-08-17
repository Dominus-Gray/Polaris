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
              className={`px-6 py-3 font-medium ${activeTab === 'certificates' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-slate-600 hover:text-slate-900'}`}
              onClick={() => setActiveTab('certificates')}
            >
              Certificates
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
                <button className="btn btn-primary" onClick={()=>navigate('/matching')}>Request Service Provider</button>
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
                  <button className="btn btn-primary" onClick={()=>navigate('/matching')}>Find Service Providers</button>
                </div>
              )}
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
        </div>
      </div>
    </div>
  );
}