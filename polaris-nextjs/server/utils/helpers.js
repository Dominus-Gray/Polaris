const crypto = require('crypto');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

/**
 * Generate unique ID
 */
const generateId = () => {
  return uuidv4();
};

/**
 * Generate secure random string
 */
const generateSecureToken = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * Generate license code (10 digits)
 */
const generateLicenseCode = () => {
  return Math.floor(1000000000 + Math.random() * 9000000000).toString();
};

/**
 * Hash password
 */
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(12);
  return bcrypt.hash(password, salt);
};

/**
 * Compare password
 */
const comparePasswords = async (plainPassword, hashedPassword) => {
  return bcrypt.compare(plainPassword, hashedPassword);
};

/**
 * Generate JWT token
 */
const generateJWTToken = (payload, expiresIn = process.env.JWT_EXPIRE || '7d') => {
  return jwt.sign(payload, process.env.JWT_SECRET, { expiresIn });
};

/**
 * Verify JWT token
 */
const verifyJWTToken = (token) => {
  return jwt.verify(token, process.env.JWT_SECRET);
};

/**
 * Format response with consistent structure
 */
const formatResponse = (success = true, data = null, message = null, error_code = null) => {
  const response = {
    success,
    ...(data && { data }),
    ...(message && { message }),
    ...(error_code && { error_code }),
    timestamp: new Date().toISOString()
  };
  
  if (!success) {
    response.error = true;
  }
  
  return response;
};

/**
 * Format error response with Polaris error codes
 */
const formatErrorResponse = (error_code, message, detail = null, statusCode = 400) => {
  return {
    error: true,
    error_code,
    message: {
      error_code,
      message,
      detail: detail || message
    },
    statusCode
  };
};

/**
 * Sanitize filename for uploads
 */
const sanitizeFilename = (filename) => {
  return filename.replace(/[^a-zA-Z0-9.-]/g, '_').toLowerCase();
};

/**
 * Get file extension
 */
const getFileExtension = (filename) => {
  return path.extname(filename).toLowerCase();
};

/**
 * Check if file type is allowed
 */
const isAllowedFileType = (filename, allowedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']) => {
  const ext = getFileExtension(filename);
  return allowedTypes.includes(ext);
};

/**
 * Generate upload path
 */
const generateUploadPath = (userId, filename) => {
  const sanitized = sanitizeFilename(filename);
  const timestamp = Date.now();
  return `${userId}/${timestamp}_${sanitized}`;
};

/**
 * Paginate results
 */
const paginate = (query, page = 1, limit = 10) => {
  const skip = (page - 1) * limit;
  return query.skip(skip).limit(limit);
};

/**
 * Calculate pagination metadata
 */
const getPaginationMeta = (total, page = 1, limit = 10) => {
  const totalPages = Math.ceil(total / limit);
  const hasNext = page < totalPages;
  const hasPrev = page > 1;
  
  return {
    total,
    page: parseInt(page),
    limit: parseInt(limit),
    totalPages,
    hasNext,
    hasPrev
  };
};

/**
 * Sleep utility for testing
 */
const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Deep clone object
 */
const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Remove sensitive data from user object
 */
const sanitizeUser = (user) => {
  const userObj = user.toObject ? user.toObject() : user;
  const { password, __v, _id, ...sanitized } = userObj;
  return sanitized;
};

/**
 * Calculate assessment completion score
 */
const calculateAssessmentScore = (responses) => {
  if (!responses || responses.length === 0) return 0;
  
  const compliantCount = responses.filter(r => r.response === 'compliant').length;
  const partialCount = responses.filter(r => r.response === 'partially_compliant').length;
  
  const score = ((compliantCount * 1.0) + (partialCount * 0.5)) / responses.length;
  return Math.round(score * 100);
};

/**
 * Generate business area names
 */
const getBusinessAreas = () => {
  return {
    area1: 'Business Formation & Registration',
    area2: 'Financial Operations & Management',
    area3: 'Legal & Contracting Compliance',
    area4: 'Quality Management & Standards',
    area5: 'Technology & Security Infrastructure',
    area6: 'Human Resources & Capacity',
    area7: 'Performance Tracking & Reporting',
    area8: 'Risk Management & Business Continuity',
    area9: 'Supply Chain Management & Vendor Relations',
    area10: 'Competitive Advantage & Market Position'
  };
};

/**
 * Format currency
 */
const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

/**
 * Format date
 */
const formatDate = (date, options = {}) => {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };
  
  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
};

/**
 * Validate environment variables
 */
const validateEnvVars = () => {
  const required = ['MONGO_URL', 'JWT_SECRET'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
};

module.exports = {
  generateId,
  generateSecureToken,
  generateLicenseCode,
  hashPassword,
  comparePasswords,
  generateJWTToken,
  verifyJWTToken,
  formatResponse,
  formatErrorResponse,
  sanitizeFilename,
  getFileExtension,
  isAllowedFileType,
  generateUploadPath,
  paginate,
  getPaginationMeta,
  sleep,
  deepClone,
  sanitizeUser,
  calculateAssessmentScore,
  getBusinessAreas,
  formatCurrency,
  formatDate,
  validateEnvVars
};