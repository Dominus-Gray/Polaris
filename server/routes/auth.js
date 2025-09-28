const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const rateLimit = require('express-rate-limit');
const User = require('../models/User');
const { AgencyLicense } = require('../models/Agency');
const { authenticateToken, optionalAuth } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse, 
  generateJWTToken,
  hashPassword,
  comparePasswords,
  sanitizeUser
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

// Rate limiting for authentication endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: {
    error: true,
    error_code: 'POL-4004',
    message: {
      error_code: 'POL-4004',
      message: 'Too many authentication attempts',
      detail: 'Please try again later'
    }
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply rate limiting to login and register
router.use('/login', authLimiter);
router.use('/register', authLimiter);

/**
 * POST /api/auth/register
 * Register a new user
 */
router.post('/register', validate(schemas.userRegistration), async (req, res, next) => {
  try {
    const { email, password, name, role, phone, company_name, license_code } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Account already exists',
          'An account with this email address already exists'
        )
      );
    }

    // Validate license code for clients
    if (role === 'client') {
      if (!license_code || !/^\d{10}$/.test(license_code)) {
        return res.status(400).json(
          formatErrorResponse(
            'POL-4003',
            'Business clients require a valid 10-digit license code from a local agency',
            'Invalid license code format'
          )
        );
      }

      // Check if license code exists and is available
      const license = await AgencyLicense.findOne({ 
        license_code,
        status: 'active',
        expires_at: { $gt: new Date() }
      });

      if (!license) {
        return res.status(400).json(
          formatErrorResponse(
            'POL-4001',
            'Invalid or expired license code',
            'Please contact your local agency for a valid license code'
          )
        );
      }

      // Check if license is already used
      if (license.usage_count >= license.usage_limit) {
        return res.status(400).json(
          formatErrorResponse(
            'POL-4001',
            'License code has already been used',
            'Please contact your local agency for a new license code'
          )
        );
      }
    }

    // Create new user
    const userData = {
      id: uuidv4(),
      email: email.toLowerCase(),
      password, // Will be hashed by pre-save middleware
      name,
      role,
      phone,
      company_name,
      license_code: role === 'client' ? license_code : undefined,
      status: 'approved' // Auto-approve for now
    };

    const user = new User(userData);
    await user.save();

    // Mark license as used if it's a client registration
    if (role === 'client' && license_code) {
      const license = await AgencyLicense.findOne({ license_code });
      if (license) {
        await license.markAsUsed(user.id);
      }
    }

    // Generate JWT token
    const token = user.generateJWT();

    // Log successful registration
    logger.info(`User registered successfully: ${email} (${role})`);

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        user: user.toSafeObject(),
        token
      }
    });

  } catch (error) {
    logger.error('Registration error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/login
 * Authenticate user and return JWT token
 */
router.post('/login', validate(schemas.userLogin), async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Find user by email
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) {
      return res.status(401).json({
        error: true,
        error_code: 'POL-6000',
        message: {
          error_code: 'POL-1001',
          message: 'Invalid authentication credentials provided: User not found',
          detail: 'User not found'
        }
      });
    }

    // Check password
    const isValidPassword = await user.comparePassword(password);
    if (!isValidPassword) {
      return res.status(401).json({
        error: true,
        error_code: 'POL-6000',
        message: {
          error_code: 'POL-1001',
          message: 'Invalid authentication credentials provided: Incorrect password',
          detail: 'Incorrect password'
        }
      });
    }

    // Check if account is approved
    if (user.status !== 'approved') {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1002',
          'Account not approved',
          `Account status: ${user.status}`
        )
      );
    }

    // Update last login
    user.last_login = new Date();
    user.failed_login_attempts = 0;
    await user.save();

    // Generate JWT token
    const token = user.generateJWT();

    // Log successful login
    logger.info(`User logged in successfully: ${email}`);

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: user.toSafeObject(),
        token,
        expires_in: process.env.JWT_EXPIRE || '7d'
      }
    });

  } catch (error) {
    logger.error('Login error:', error);
    next(error);
  }
});

/**
 * GET /api/auth/me
 * Get current user information
 */
router.get('/me', authenticateToken, async (req, res, next) => {
  try {
    const user = req.user;
    
    res.json({
      success: true,
      data: {
        user: user.toSafeObject()
      }
    });

  } catch (error) {
    logger.error('Get user info error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/refresh
 * Refresh JWT token
 */
router.post('/refresh', authenticateToken, async (req, res, next) => {
  try {
    const user = req.user;
    
    // Generate new token
    const token = user.generateJWT();
    
    res.json({
      success: true,
      message: 'Token refreshed successfully',
      data: {
        token,
        expires_in: process.env.JWT_EXPIRE || '7d'
      }
    });

  } catch (error) {
    logger.error('Token refresh error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/logout
 * Logout user (client-side token removal)
 */
router.post('/logout', authenticateToken, async (req, res, next) => {
  try {
    // In a stateless JWT system, logout is handled client-side
    // But we can log the event for analytics
    logger.info(`User logged out: ${req.user.email}`);
    
    res.json({
      success: true,
      message: 'Logged out successfully'
    });

  } catch (error) {
    logger.error('Logout error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/forgot-password
 * Send password reset email
 */
router.post('/forgot-password', validate({
  email: schemas.userLogin.extract('email')
}), async (req, res, next) => {
  try {
    const { email } = req.body;
    
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) {
      // Don't reveal if email exists or not
      return res.json({
        success: true,
        message: 'If an account with that email exists, a password reset link has been sent'
      });
    }
    
    // Generate reset token
    const resetToken = require('crypto').randomBytes(32).toString('hex');
    user.password_reset_token = resetToken;
    user.password_reset_expires = new Date(Date.now() + 3600000); // 1 hour
    await user.save();
    
    // TODO: Send email with reset link
    // await sendPasswordResetEmail(user.email, resetToken);
    
    logger.info(`Password reset requested for: ${email}`);
    
    res.json({
      success: true,
      message: 'If an account with that email exists, a password reset link has been sent'
    });

  } catch (error) {
    logger.error('Forgot password error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/reset-password
 * Reset password using token
 */
router.post('/reset-password', validate({
  token: require('joi').string().required(),
  password: schemas.userRegistration.extract('password')
}), async (req, res, next) => {
  try {
    const { token, password } = req.body;
    
    const user = await User.findOne({
      password_reset_token: token,
      password_reset_expires: { $gt: new Date() }
    });
    
    if (!user) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid or expired reset token',
          'Password reset token is invalid or has expired'
        )
      );
    }
    
    // Update password
    user.password = password; // Will be hashed by pre-save middleware
    user.password_reset_token = undefined;
    user.password_reset_expires = undefined;
    user.failed_login_attempts = 0;
    await user.save();
    
    logger.info(`Password reset successfully for: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Password reset successfully'
    });

  } catch (error) {
    logger.error('Reset password error:', error);
    next(error);
  }
});

/**
 * GET /api/auth/password-requirements
 * Get password requirements
 */
router.get('/password-requirements', (req, res) => {
  res.json({
    success: true,
    data: {
      requirements: {
        min_length: 8,
        require_uppercase: true,
        require_lowercase: true,
        require_numbers: true,
        require_special_characters: true,
        allowed_special_characters: '@$!%*?&'
      },
      pattern: '^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$'
    }
  });
});

/**
 * POST /api/auth/change-password
 * Change password for authenticated user
 */
router.post('/change-password', authenticateToken, validate({
  current_password: require('joi').string().required(),
  new_password: schemas.userRegistration.extract('password')
}), async (req, res, next) => {
  try {
    const { current_password, new_password } = req.body;
    const user = req.user;
    
    // Verify current password
    const isValidPassword = await user.comparePassword(current_password);
    if (!isValidPassword) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Current password is incorrect',
          'Please enter your current password correctly'
        )
      );
    }
    
    // Update password
    user.password = new_password; // Will be hashed by pre-save middleware
    await user.save();
    
    logger.info(`Password changed for user: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Password changed successfully'
    });

  } catch (error) {
    logger.error('Change password error:', error);
    next(error);
  }
});

/**
 * POST /api/auth/oauth/callback
 * Handle OAuth callback (Google, etc.)
 */
router.post('/oauth/callback', async (req, res, next) => {
  try {
    const { provider, code, state } = req.body;
    
    // TODO: Implement OAuth flow
    // This would typically involve:
    // 1. Verify state parameter
    // 2. Exchange code for access token
    // 3. Get user info from OAuth provider
    // 4. Create or update user in database
    // 5. Generate JWT token
    
    res.status(501).json(
      formatErrorResponse(
        'POL-5001',
        'OAuth authentication not implemented',
        'OAuth functionality is not yet implemented'
      )
    );

  } catch (error) {
    logger.error('OAuth callback error:', error);
    next(error);
  }
});

module.exports = router;