import React, { useState, useEffect } from 'react';

// Smart Validation System with Real-time Feedback
export class SmartValidator {
  static validateBusinessName(name) {
    if (!name || name.length < 2) {
      return {
        valid: false,
        message: "Business name must be at least 2 characters",
        suggestion: "Try including your business type (e.g., 'ABC Consulting LLC')",
        severity: 'error'
      };
    }
    
    if (!/^[a-zA-Z0-9\s\-&.,'"()]+$/.test(name)) {
      return {
        valid: false,
        message: "Business name contains invalid characters",
        suggestion: "Use only letters, numbers, spaces, and basic punctuation",
        severity: 'error'
      };
    }
    
    if (name.length > 100) {
      return {
        valid: false,
        message: "Business name is too long",
        suggestion: "Try abbreviating or using a shorter version",
        severity: 'warning'
      };
    }
    
    return {
      valid: true,
      message: "Valid business name",
      suggestion: "Great! This name looks professional and compliant",
      severity: 'success'
    };
  }

  static validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email) {
      return {
        valid: false,
        message: "Email address is required",
        suggestion: "Enter your business email address",
        severity: 'error'
      };
    }
    
    if (!emailRegex.test(email)) {
      return {
        valid: false,
        message: "Invalid email format",
        suggestion: "Use format: name@company.com",
        severity: 'error'
      };
    }
    
    // Check for common domains that might not be professional
    const personalDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'];
    const domain = email.split('@')[1]?.toLowerCase();
    
    if (personalDomains.includes(domain)) {
      return {
        valid: true,
        message: "Valid email address",
        suggestion: "Consider using your business email for professional credibility",
        severity: 'info'
      };
    }
    
    return {
      valid: true,
      message: "Professional email address",
      suggestion: "Perfect! Business emails build trust with partners",
      severity: 'success'
    };
  }

  static validatePassword(password) {
    const checks = {
      length: password?.length >= 12,
      uppercase: /[A-Z]/.test(password || ''),
      lowercase: /[a-z]/.test(password || ''),
      number: /\d/.test(password || ''),
      special: /[!@#$%^&*]/.test(password || '')
    };

    const passedChecks = Object.values(checks).filter(Boolean).length;
    
    if (passedChecks < 3) {
      return {
        valid: false,
        message: "Password doesn't meet security requirements",
        suggestion: "Use at least 12 characters with uppercase, lowercase, numbers, and symbols",
        severity: 'error',
        checks
      };
    }
    
    if (passedChecks < 5) {
      return {
        valid: true,
        message: "Password meets minimum requirements",
        suggestion: "Consider adding more character types for stronger security",
        severity: 'warning',
        checks
      };
    }
    
    return {
      valid: true,
      message: "Strong password",
      suggestion: "Excellent! This password provides strong protection",
      severity: 'success',
      checks
    };
  }

  static validatePhoneNumber(phone) {
    if (!phone) {
      return {
        valid: false,
        message: "Phone number is required",
        suggestion: "Enter your business phone number",
        severity: 'error'
      };
    }

    // Remove formatting to check digits
    const digitsOnly = phone.replace(/\D/g, '');
    
    if (digitsOnly.length !== 10) {
      return {
        valid: false,
        message: "Phone number must be 10 digits",
        suggestion: "Use format: (555) 123-4567 or 555-123-4567",
        severity: 'error'
      };
    }

    return {
      valid: true,
      message: "Valid phone number",
      suggestion: "We'll use this for important account notifications",
      severity: 'success'
    };
  }
}

// Smart Form Field Component with Real-time Validation
export function SmartFormField({ 
  type, 
  value, 
  onChange, 
  label, 
  placeholder, 
  required = false,
  suggestions = [],
  validator = null
}) {
  const [validation, setValidation] = useState({ valid: true, message: '', suggestion: '', severity: 'success' });
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (value && validator) {
      const result = validator(value);
      setValidation(result);
    }
  }, [value, validator]);

  const getSeverityStyles = (severity) => {
    switch (severity) {
      case 'error':
        return {
          input: 'border-red-300 focus:border-red-500 focus:ring-red-500',
          message: 'text-red-600',
          suggestion: 'text-red-700 bg-red-50'
        };
      case 'warning':
        return {
          input: 'border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500',
          message: 'text-yellow-600',
          suggestion: 'text-yellow-700 bg-yellow-50'
        };
      case 'info':
        return {
          input: 'border-blue-300 focus:border-blue-500 focus:ring-blue-500',
          message: 'text-blue-600',
          suggestion: 'text-blue-700 bg-blue-50'
        };
      case 'success':
        return {
          input: 'border-green-300 focus:border-green-500 focus:ring-green-500',
          message: 'text-green-600',
          suggestion: 'text-green-700 bg-green-50'
        };
      default:
        return {
          input: 'border-slate-300 focus:border-blue-500 focus:ring-blue-500',
          message: 'text-slate-600',
          suggestion: 'text-slate-700 bg-slate-50'
        };
    }
  };

  const styles = getSeverityStyles(validation.severity);

  return (
    <div className="space-y-2">
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input with suggestions */}
      <div className="relative">
        <input
          type={type}
          value={value}
          onChange={onChange}
          onFocus={() => {
            setIsFocused(true);
            setShowSuggestions(suggestions.length > 0);
          }}
          onBlur={() => {
            setIsFocused(false);
            setTimeout(() => setShowSuggestions(false), 150);
          }}
          placeholder={placeholder}
          className={`w-full px-3 py-2 border rounded-lg transition-colors duration-200 ${styles.input}`}
        />

        {/* Validation Status Icon */}
        {value && (
          <div className="absolute right-3 top-2.5">
            {validation.severity === 'success' && (
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            {validation.severity === 'error' && (
              <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            {validation.severity === 'warning' && (
              <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            )}
          </div>
        )}

        {/* Suggestions Dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-lg shadow-lg z-10 mt-1">
            {suggestions.filter(s => 
              !value || s.toLowerCase().includes(value.toLowerCase())
            ).slice(0, 5).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  onChange({ target: { value: suggestion } });
                  setShowSuggestions(false);
                }}
                className="w-full text-left px-3 py-2 hover:bg-slate-50 text-sm border-b last:border-b-0"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Validation Messages */}
      {value && validation.message && (
        <div className={`text-sm ${styles.message}`}>
          {validation.message}
        </div>
      )}

      {/* Helpful Suggestion */}
      {value && validation.suggestion && isFocused && (
        <div className={`text-xs p-2 rounded border ${styles.suggestion}`}>
          💡 {validation.suggestion}
        </div>
      )}

      {/* Password Strength Indicator */}
      {type === 'password' && value && validation.checks && (
        <div className="space-y-1">
          <div className="text-xs text-slate-600">Password strength:</div>
          <div className="grid grid-cols-5 gap-1">
            {Object.entries(validation.checks).map(([check, passed]) => (
              <div
                key={check}
                className={`h-2 rounded ${passed ? 'bg-green-500' : 'bg-slate-200'}`}
                title={check}
              />
            ))}
          </div>
          <div className="grid grid-cols-5 gap-2 text-xs">
            <span className={validation.checks.length ? 'text-green-600' : 'text-slate-400'}>12+ chars</span>
            <span className={validation.checks.uppercase ? 'text-green-600' : 'text-slate-400'}>Upper</span>
            <span className={validation.checks.lowercase ? 'text-green-600' : 'text-slate-400'}>Lower</span>
            <span className={validation.checks.number ? 'text-green-600' : 'text-slate-400'}>Number</span>
            <span className={validation.checks.special ? 'text-green-600' : 'text-slate-400'}>Symbol</span>
          </div>
        </div>
      )}
    </div>
  );
}

// Auto-complete suggestions based on common values
export const FORM_SUGGESTIONS = {
  business_type: [
    'Limited Liability Company (LLC)',
    'Corporation (Corp)', 
    'Partnership',
    'Sole Proprietorship',
    'S-Corporation',
    'Non-Profit Organization',
    'Professional Corporation (PC)',
    'Limited Partnership (LP)'
  ],
  industry: [
    'Technology & Software',
    'Construction & Engineering', 
    'Healthcare & Medical',
    'Manufacturing & Production',
    'Professional Services',
    'Retail & E-commerce',
    'Transportation & Logistics',
    'Finance & Banking',
    'Education & Training',
    'Government Contracting',
    'Non-Profit Services'
  ],
  employee_count: [
    '1-10 employees',
    '11-50 employees',
    '51-200 employees', 
    '201-500 employees',
    '500+ employees'
  ],
  annual_revenue: [
    'Under $100,000',
    '$100,000 - $500,000',
    '$500,000 - $1,000,000',
    '$1,000,000 - $5,000,000',
    '$5,000,000 - $10,000,000',
    'Over $10,000,000'
  ],
  business_location: [
    'Home-based',
    'Shared office space',
    'Leased commercial space',
    'Owned commercial property',
    'Multiple locations',
    'Virtual/Remote business'
  ]
};