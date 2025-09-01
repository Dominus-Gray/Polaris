import React, { useState } from 'react';

const ClientRemediationFilters = () => {
  const [selectedArea, setSelectedArea] = useState('');
  const [minRating, setMinRating] = useState('');
  const [maxBudget, setMaxBudget] = useState('');
  const [certifications, setCertifications] = useState([]);

  const businessAreas = [
    { id: 'area1', name: '1. Business Formation & Registration' },
    { id: 'area2', name: '2. Financial Operations & Management' },
    { id: 'area3', name: '3. Legal & Contracting Compliance' },
    { id: 'area4', name: '4. Quality Management & Standards' },
    { id: 'area5', name: '5. Technology & Security Infrastructure' },
    { id: 'area6', name: '6. Human Resources & Capacity' },
    { id: 'area7', name: '7. Performance Tracking & Reporting' },
    { id: 'area8', name: '8. Risk Management & Business Continuity' },
    { id: 'area9', name: '9. Supply Chain Management & Vendor Relations' },
    { id: 'area10', name: '10. Competitive Advantage & Market Position' }
  ];

  const businessCertifications = [
    { id: 'hub', name: 'HUB Certified' },
    { id: 'sbe', name: 'SBE (Small Business Enterprise)' },
    { id: 'wosb', name: 'WOSB (Women-Owned Small Business)' },
    { id: 'mbe', name: 'MBE (Minority Business Enterprise)' },
    { id: 'sdvob', name: 'SDVOB (Service-Disabled Veteran-Owned)' },
    { id: 'vob', name: 'VOB (Veteran-Owned Business)' },
    { id: 'wob', name: 'WOB (Women-Owned Business)' }
  ];

  const handleCertificationToggle = (certId) => {
    setCertifications(prev => 
      prev.includes(certId) 
        ? prev.filter(id => id !== certId)
        : [...prev, certId]
    );
  };

  const handleSearch = () => {
    const filters = {
      area: selectedArea,
      minRating,
      maxBudget,
      certifications
    };
    console.log('Searching with filters:', filters);
    // TODO: Implement search logic with backend call
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 mb-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-4 text-center">
        🔍 Find Local Service Providers
      </h4>
      <p className="text-gray-600 text-sm mb-6 text-center max-w-2xl mx-auto">
        Search for certified service providers based on your business needs, certifications, and budget.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Business Area Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Area
          </label>
          <select
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Business Areas</option>
            {businessAreas.map(area => (
              <option key={area.id} value={area.id}>{area.name}</option>
            ))}
          </select>
        </div>

        {/* Rating Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Minimum Rating
          </label>
          <select
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any Rating</option>
            <option value="4">⭐⭐⭐⭐+ (4.0+)</option>
            <option value="4.5">⭐⭐⭐⭐⭐ (4.5+)</option>
            <option value="5">⭐⭐⭐⭐⭐ (5.0 only)</option>
          </select>
        </div>

        {/* Budget Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Max Budget
          </label>
          <select
            value={maxBudget}
            onChange={(e) => setMaxBudget(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any Budget</option>
            <option value="1000">Under $1,000</option>
            <option value="5000">Under $5,000</option>
            <option value="10000">Under $10,000</option>
            <option value="25000">Under $25,000</option>
            <option value="50000">$50,000+</option>
          </select>
        </div>

        {/* Business Certifications Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Certifications
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-2 bg-white">
            {businessCertifications.map(cert => (
              <label key={cert.id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                <input
                  type="checkbox"
                  checked={certifications.includes(cert.id)}
                  onChange={() => handleCertificationToggle(cert.id)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 flex-1">{cert.name}</span>
              </label>
            ))}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Select multiple certifications to filter providers
          </div>
        </div>

        {/* Search Button */}
        <div className="flex items-end">
          <button
            onClick={handleSearch}
            className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Search Providers
          </button>
        </div>
      </div>

      {/* Active Filters Display */}
      {(selectedArea || minRating || maxBudget || certifications.length > 0) && (
        <div className="border-t pt-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-gray-700">Active Filters:</span>
            <button
              onClick={() => {
                setSelectedArea('');
                setMinRating('');
                setMaxBudget('');
                setCertifications([]);
              }}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedArea && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {businessAreas.find(a => a.id === selectedArea)?.name}
              </span>
            )}
            {minRating && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                {minRating}+ Rating
              </span>
            )}
            {maxBudget && (
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                Under ${parseInt(maxBudget).toLocaleString()}
              </span>
            )}
            {certifications.map(certId => (
              <span key={certId} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                {businessCertifications.find(c => c.id === certId)?.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientRemediationFilters;