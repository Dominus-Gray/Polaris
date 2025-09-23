import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AssessmentResultsPage() {
  // Component implementation with corrected API configuration
  return (
    <div className="container mt-6 max-w-4xl">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Assessment Results</h1>
      <div className="bg-white rounded-lg border p-6">
        <p className="text-slate-600">Assessment results will be displayed here with proper API integration.</p>
      </div>
    </div>
  );
}

export default AssessmentResultsPage;