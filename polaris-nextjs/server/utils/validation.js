const Joi = require('joi');

// Common validation schemas
const schemas = {
  // User registration
  userRegistration: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().min(8).pattern(new RegExp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]')).required(),
    name: Joi.string().min(2).max(100).required(),
    role: Joi.string().valid('client', 'provider', 'agency', 'navigator').required(),
    phone: Joi.string().pattern(new RegExp('^[+]?[1-9]\\d{1,14}$')).optional(),
    company_name: Joi.string().max(200).optional(),
    license_code: Joi.when('role', {
      is: 'client',
      then: Joi.string().length(10).pattern(/^\d{10}$/).required(),
      otherwise: Joi.forbidden()
    })
  }),

  // User login
  userLogin: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required()
  }),

  // Assessment response
  assessmentResponse: Joi.object({
    question_id: Joi.string().required(),
    response: Joi.string().valid('compliant', 'not_compliant', 'partially_compliant').required(),
    evidence_provided: Joi.string().valid('true', 'false').optional(),
    evidence_url: Joi.string().uri().optional(),
    notes: Joi.string().max(1000).optional()
  }),

  // Service request
  serviceRequest: Joi.object({
    area_id: Joi.string().required(),
    service_type: Joi.string().valid('assessment_help', 'compliance_support', 'professional_help').required(),
    description: Joi.string().min(10).max(2000).required(),
    budget_range: Joi.string().optional(),
    timeline: Joi.string().optional(),
    urgency: Joi.string().valid('low', 'medium', 'high', 'urgent').optional()
  }),

  // Provider response
  providerResponse: Joi.object({
    request_id: Joi.string().required(),
    proposed_fee: Joi.number().min(0).max(100000).required(),
    estimated_timeline: Joi.string().required(),
    proposal_note: Joi.string().min(10).max(2000).required(),
    availability: Joi.string().optional()
  }),

  // Profile update
  profileUpdate: Joi.object({
    name: Joi.string().min(2).max(100).optional(),
    phone: Joi.string().pattern(new RegExp('^[+]?[1-9]\\d{1,14}$')).optional(),
    company_name: Joi.string().max(200).optional(),
    business_description: Joi.string().max(1000).optional(),
    location: Joi.object({
      city: Joi.string().max(100).optional(),
      state: Joi.string().max(100).optional(),
      country: Joi.string().max(100).optional(),
      zip_code: Joi.string().max(20).optional()
    }).optional(),
    specializations: Joi.array().items(Joi.string()).max(10).optional(),
    certifications: Joi.array().items(Joi.string()).max(20).optional(),
    website: Joi.string().uri().optional(),
    linkedin: Joi.string().uri().optional()
  }),

  // License generation
  licenseGeneration: Joi.object({
    quantity: Joi.number().integer().min(1).max(100).required(),
    expires_days: Joi.number().integer().min(1).max(365).optional()
  }),

  // Chat message
  chatMessage: Joi.object({
    chat_id: Joi.string().required(),
    message: Joi.string().min(1).max(2000).required(),
    message_type: Joi.string().valid('text', 'file', 'image').optional()
  }),

  // AI query
  aiQuery: Joi.object({
    question: Joi.string().min(5).max(1000).required(),
    context: Joi.object().optional(),
    session_id: Joi.string().optional()
  }),

  // Pagination
  pagination: Joi.object({
    page: Joi.number().integer().min(1).optional(),
    limit: Joi.number().integer().min(1).max(100).optional(),
    sort: Joi.string().optional(),
    order: Joi.string().valid('asc', 'desc').optional()
  })
};

// Validation middleware generator
const validate = (schema, property = 'body') => {
  return (req, res, next) => {
    const { error } = schema.validate(req[property], { 
      abortEarly: false,
      stripUnknown: true 
    });
    
    if (error) {
      const details = error.details.map(detail => detail.message).join(', ');
      return res.status(400).json({
        error: true,
        error_code: 'POL-4003',
        message: {
          error_code: 'POL-4003',
          message: 'Validation Error',
          detail: details
        }
      });
    }
    
    next();
  };
};

// Custom validators
const customValidators = {
  isValidObjectId: (value) => {
    return /^[0-9a-fA-F]{24}$/.test(value);
  },
  
  isValidUUID: (value) => {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
  },
  
  isValidEmail: (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },
  
  isStrongPassword: (password) => {
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
  }
};

module.exports = {
  schemas,
  validate,
  customValidators
};