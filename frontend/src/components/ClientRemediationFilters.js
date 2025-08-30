import React, { useState } from 'react';

const ClientRemediationFilters = () => {
  const [selectedArea, setSelectedArea] = useState('');
  const [minRating, setMinRating] = useState('');
  const [maxBudget, setMaxBudget] = useState('');
  const [certifications, setCertifications] = useState([]);
  const [selectedCertification, setSelectedCertification] = useState('');

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
    { id: '8a', name: 'SBA 8(a) Business Development' },
    { id: 'hubzone', name: 'HUBZone Certified' },
    { id: 'wosb', name: 'Women-Owned Small Business (WOSB)' },
    { id: 'vosb', name: 'Veteran-Owned Small Business (VOSB)' },
    { id: 'sdvosb', name: 'Service-Disabled Veteran-Owned (SDVOSB)' },
    { id: 'mbe', name: 'Minority Business Enterprise (MBE)' },
    { id: 'wbe', name: 'Women Business Enterprise (WBE)' },
    { id: 'dbe', name: 'Disadvantaged Business Enterprise (DBE)' },
    { id: 'sbe', name: 'Small Business Enterprise (SBE)' },
    { id: 'iso9001', name: 'ISO 9001 Quality Management' },
    { id: 'iso27001', name: 'ISO 27001 Information Security' },
    { id: 'cmmi', name: 'CMMI Process Certification' },
    { id: 'nist', name: 'NIST Cybersecurity Framework' },
    { id: 'soc2', name: 'SOC 2 Compliance' }
  ];

  const handleSearch = () => {
    const filters = {
      area: selectedArea,
      minRating,
      maxBudget,
      certification: selectedCertification
    };
    console.log('Searching with filters:', filters);
    // TODO: Implement search logic with backend call
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 mb-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-4">
        🔍 Find Local Service Providers
      </h4>
      <p className="text-gray-600 text-sm mb-4">
        Search for certified service providers based on your business needs and budget.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
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

        {/* Business Certification Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Certification
          </label>
          <select
            value={selectedCertification}
            onChange={(e) => setSelectedCertification(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any Certification</option>
            {businessCertifications.map(cert => (
              <option key={cert.id} value={cert.id}>{cert.name}</option>
            ))}
          </select>
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

      {/* Certifications Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Business Certifications
        </label>
        <div className="flex flex-wrap gap-2">
          {availableCertifications.map(cert => (
            <button
              key={cert.id}
              onClick={() => handleCertificationToggle(cert.id)}
              className={`px-3 py-1 text-xs font-medium rounded-full border transition-colors ${
                certifications.includes(cert.id)
                  ? 'bg-blue-100 text-blue-800 border-blue-200'
                  : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200'
              }`}
            >
              {cert.name}
            </button>
          ))}
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
                {availableCertifications.find(c => c.id === certId)?.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientRemediationFilters;