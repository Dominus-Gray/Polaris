// Complete Knowledge Base Component for Polaris Platform
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
      setAreas(data.areas);
    } catch (e) {
      console.error('Failed to load knowledge base areas:', e);
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
      const { data } = await axios.get(`${API}/knowledge-base/${areaId}/content`);
      setResources(data.content || {});
      setSelectedArea(areaId);
    } catch (e) {
      console.error('Failed to load area resources:', e);
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
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {areas.map((area) => (
          <div 
            key={area.id} 
            className={`bg-white rounded-lg shadow-sm border transition-all hover:shadow-md ${
              area.locked ? 'opacity-75' : 'cursor-pointer hover:border-blue-300'
            }`}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{area.title}</h3>
                  <p className="text-sm text-slate-600 mb-3">{area.description}</p>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      {area.resources_count} Resources
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {area.locked ? (
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">Locked</span>
                  ) : (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Unlocked</span>
                  )}
                  {area.locked && (
                    <span className="text-sm font-medium text-slate-600">$20</span>
                  )}
                </div>
              </div>

              {area.locked ? (
                <div className="text-center py-4 border-t border-slate-100">
                  <p className="text-sm text-slate-600 mb-3">
                    Unlock AI-powered templates, guides, and compliance resources
                  </p>
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => unlockArea(area.id)}
                    disabled={paymentLoading}
                  >
                    {paymentLoading ? 'Processing...' : `Unlock for $20`}
                  </button>
                </div>
              ) : (
                <div className="border-t border-slate-100 pt-4">
                  <button 
                    className="btn btn-primary w-full"
                    onClick={() => loadAreaResources(area.id)}
                  >
                    View Resources
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
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
                      <button className="text-blue-600 hover:text-blue-700 text-sm">Download</button>
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
                      <button className="text-green-600 hover:text-green-700 text-sm">Download</button>
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
                      <button className="text-purple-600 hover:text-purple-700 text-sm">Download</button>
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

// Free Resources Page Component
function FreeResourcesPage(){
  const [resources, setResources] = useState([]);
  const [selectedArea, setSelectedArea] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadFreeResources();
  }, [selectedArea]);

  const loadFreeResources = async () => {
    try {
      const gap_areas = selectedArea === 'all' ? '' : selectedArea;
      const { data } = await axios.get(`${API}/free-resources/recommendations?gaps=${gap_areas}`);
      setResources(data.resources || []);
    } catch (e) {
      console.error('Failed to load free resources:', e);
    }
  };

  const logResourceAccess = async (resourceId, gapArea) => {
    try {
      await axios.post(`${API}/analytics/resource-access`, { 
        resource_id: resourceId, 
        gap_area: gapArea 
      });
    } catch (e) {
      console.error('Failed to log resource access:', e);
    }
  };

  const filteredResources = resources.filter(resource => 
    resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resource.area_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mt-6 max-w-6xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg p-8 mb-8">
        <h1 className="text-3xl font-bold mb-2">Free Resources</h1>
        <p className="text-green-100">Complimentary tools, guides, and templates to support your business growth</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search resources..."
              className="input w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select 
            className="input"
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
          >
            <option value="all">All Areas</option>
            <option value="area1">Business Formation</option>
            <option value="area2">Financial Operations</option>
            <option value="area3">Legal Compliance</option>
            <option value="area4">Quality Management</option>
            <option value="area5">Technology & Security</option>
            <option value="area6">Human Resources</option>
            <option value="area7">Performance Tracking</option>
            <option value="area8">Risk Management</option>
          </select>
        </div>
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredResources.map((resource, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  {resource.area_name}
                </span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">FREE</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">{resource.title}</h3>
              <p className="text-sm text-slate-600 mb-4">
                Essential resource for {resource.area_name.toLowerCase()} requirements and best practices.
              </p>
              <button 
                className="btn btn-primary w-full"
                onClick={() => {
                  logResourceAccess(resource.id, resource.area);
                  // Simulate download
                  toast.success(`Downloaded: ${resource.title}`);
                }}
              >
                Download Resource
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredResources.length === 0 && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-slate-900 mb-2">No Resources Found</h3>
          <p className="text-slate-600">Try adjusting your search criteria or selecting a different area.</p>
        </div>
      )}
    </div>
  );
}