const jwt = require('jsonwebtoken');
const { promisify } = require('util');
const User = require('../models/User');
const logger = require('winston');

// JWT verification
const verifyToken = promisify(jwt.verify);

/**
 * Authentication middleware
 */
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        error: true,
        error_code: 'POL-1001',
        message: {
          error_code: 'POL-1001',
          message: 'Access token is required',
          detail: 'No authorization token provided'
        }
      });
    }

    try {
      const decoded = await verifyToken(token, process.env.JWT_SECRET);
      
      // Get user from database
      const user = await User.findOne({ id: decoded.id }).select('-password');
      
      if (!user) {
        return res.status(401).json({
          error: true,
          error_code: 'POL-1001',
          message: {
            error_code: 'POL-1001',
            message: 'Invalid authentication credentials provided: User not found',
            detail: 'User not found'
          }
        });
      }

      if (user.status !== 'approved') {
        return res.status(403).json({
          error: true,
          error_code: 'POL-1002',
          message: {
            error_code: 'POL-1002',
            message: 'Account not approved',
            detail: 'User account is not approved'
          }
        });
      }

      req.user = user;
      next();
    } catch (jwtError) {
      logger.error('JWT verification error:', jwtError);
      return res.status(401).json({
        error: true,
        error_code: 'POL-1001',
        message: {
          error_code: 'POL-1001',
          message: 'Invalid authentication credentials provided: Invalid token',
          detail: 'Token verification failed'
        }
      });
    }
  } catch (error) {
    logger.error('Authentication middleware error:', error);
    return res.status(500).json({
      error: true,
      error_code: 'POL-5000',
      message: {
        error_code: 'POL-5000',
        message: 'Internal server error during authentication',
        detail: 'Authentication process failed'
      }
    });
  }
};

/**
 * Role-based authorization middleware
 */
const requireRole = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: true,
        error_code: 'POL-1001',
        message: {
          error_code: 'POL-1001',
          message: 'Authentication required',
          detail: 'User not authenticated'
        }
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        error: true,
        error_code: 'POL-1003',
        message: {
          error_code: 'POL-1003',
          message: 'Insufficient permissions',
          detail: `Required roles: ${roles.join(', ')}, user role: ${req.user.role}`
        }
      });
    }

    next();
  };
};

/**
 * Optional authentication - doesn't fail if no token
 */
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      req.user = null;
      return next();
    }

    try {
      const decoded = await verifyToken(token, process.env.JWT_SECRET);
      const user = await User.findOne({ id: decoded.id }).select('-password');
      
      req.user = user || null;
    } catch (jwtError) {
      req.user = null;
    }
    
    next();
  } catch (error) {
    logger.error('Optional auth middleware error:', error);
    req.user = null;
    next();
  }
};

/**
 * Check if user has access to specific knowledge base areas
 */
const checkKnowledgeBaseAccess = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: true,
        error_code: 'POL-1001',
        message: 'Authentication required for knowledge base access'
      });
    }

    // QA users with @polaris.example.com have full access
    if (req.user.email && req.user.email.endsWith('@polaris.example.com')) {
      req.hasKnowledgeBaseAccess = true;
      return next();
    }

    // Check if user has knowledge base access based on their subscription/license
    // For now, allow basic access for all authenticated users
    req.hasKnowledgeBaseAccess = true;
    next();
  } catch (error) {
    logger.error('Knowledge base access check error:', error);
    return res.status(500).json({
      error: true,
      error_code: 'POL-5000',
      message: 'Error checking knowledge base access'
    });
  }
};

module.exports = {
  authenticateToken,
  requireRole,
  optionalAuth,
  checkKnowledgeBaseAccess
};