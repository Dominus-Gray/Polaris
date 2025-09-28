const express = require('express');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { formatResponse, formatErrorResponse, sanitizeUser } = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

/**
 * GET /api/users/me
 * Get current user profile
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
    logger.error('Get user profile error:', error);
    next(error);
  }
});

/**
 * PUT /api/users/me
 * Update current user profile
 */
router.put('/me', authenticateToken, validate(schemas.profileUpdate), async (req, res, next) => {
  try {
    const userId = req.user.id;
    const updates = req.body;
    
    // Remove fields that shouldn't be updated via this endpoint
    const allowedUpdates = [
      'name', 'phone', 'company_name', 'business_description',
      'location', 'specializations', 'certifications', 'website', 'linkedin'
    ];
    
    const filteredUpdates = {};
    allowedUpdates.forEach(field => {
      if (updates[field] !== undefined) {
        filteredUpdates[field] = updates[field];
      }
    });
    
    const user = await User.findOneAndUpdate(
      { id: userId },
      { $set: filteredUpdates },
      { new: true, runValidators: true }
    );
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User account not found'
        )
      );
    }
    
    logger.info(`User profile updated: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Profile updated successfully',
      data: {
        user: user.toSafeObject()
      }
    });

  } catch (error) {
    logger.error('Update user profile error:', error);
    next(error);
  }
});

/**
 * GET /api/users/dashboard
 * Get user dashboard data
 */
router.get('/dashboard', authenticateToken, async (req, res, next) => {
  try {
    const user = req.user;
    const role = user.role;
    
    // Base dashboard data
    let dashboardData = {
      user: user.toSafeObject(),
      welcome_message: `Welcome back, ${user.name}!`,
      notifications_count: 0,
      quick_actions: []
    };
    
    // Role-specific dashboard data
    switch (role) {
      case 'client':
        dashboardData = {
          ...dashboardData,
          welcome_message: 'Welcome back, Valued Client!',
          quick_actions: [
            { title: 'Start Assessment', url: '/assessment', icon: 'clipboard' },
            { title: 'View Services', url: '/services', icon: 'briefcase' },
            { title: 'Knowledge Base', url: '/knowledge-base', icon: 'book' }
          ],
          procurement_readiness: {
            overall_score: 0,
            areas_completed: 0,
            total_areas: 10,
            next_steps: ['Complete your first business assessment']
          }
        };
        break;
        
      case 'provider':
        dashboardData = {
          ...dashboardData,
          welcome_message: 'Welcome back, Service Provider!',
          quick_actions: [
            { title: 'View Opportunities', url: '/opportunities', icon: 'search' },
            { title: 'My Services', url: '/my-services', icon: 'briefcase' },
            { title: 'Profile', url: '/profile', icon: 'user' }
          ],
          provider_stats: {
            active_engagements: 0,
            pending_responses: 0,
            total_earnings: 0,
            rating: 0
          }
        };
        break;
        
      case 'agency':
        dashboardData = {
          ...dashboardData,
          welcome_message: 'Welcome back, Agency Partner!',
          quick_actions: [
            { title: 'Generate Licenses', url: '/licenses', icon: 'key' },
            { title: 'View Clients', url: '/clients', icon: 'users' },
            { title: 'Analytics', url: '/analytics', icon: 'chart' }
          ],
          agency_stats: {
            active_licenses: 0,
            total_clients: 0,
            monthly_usage: 0,
            revenue: 0
          }
        };
        break;
        
      case 'navigator':
        dashboardData = {
          ...dashboardData,
          welcome_message: 'Welcome back, Navigator!',
          quick_actions: [
            { title: 'Approve Agencies', url: '/approve-agencies', icon: 'check' },
            { title: 'System Analytics', url: '/system-analytics', icon: 'chart' },
            { title: 'User Management', url: '/users', icon: 'users' }
          ],
          navigator_stats: {
            pending_approvals: 0,
            total_agencies: 0,
            system_health: 100,
            monthly_activities: 0
          }
        };
        break;
    }
    
    res.json({
      success: true,
      data: dashboardData
    });

  } catch (error) {
    logger.error('Get user dashboard error:', error);
    next(error);
  }
});

/**
 * GET /api/users/notifications
 * Get user notifications
 */
router.get('/notifications', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { page = 1, limit = 20, status = 'all' } = req.query;
    
    // TODO: Implement notifications system
    // For now, return empty array
    const notifications = [];
    
    res.json({
      success: true,
      data: {
        notifications,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: 0,
          totalPages: 0
        }
      }
    });

  } catch (error) {
    logger.error('Get user notifications error:', error);
    next(error);
  }
});

/**
 * PUT /api/users/notifications/:notificationId/read
 * Mark notification as read
 */
router.put('/notifications/:notificationId/read', authenticateToken, async (req, res, next) => {
  try {
    const { notificationId } = req.params;
    const userId = req.user.id;
    
    // TODO: Implement notification marking
    
    res.json({
      success: true,
      message: 'Notification marked as read'
    });

  } catch (error) {
    logger.error('Mark notification as read error:', error);
    next(error);
  }
});

/**
 * GET /api/users/preferences
 * Get user preferences
 */
router.get('/preferences', authenticateToken, async (req, res, next) => {
  try {
    const user = req.user;
    
    res.json({
      success: true,
      data: {
        preferences: user.preferences || {
          notifications: {
            email: true,
            sms: false,
            push: true
          },
          theme: 'light',
          language: 'en'
        }
      }
    });

  } catch (error) {
    logger.error('Get user preferences error:', error);
    next(error);
  }
});

/**
 * PUT /api/users/preferences
 * Update user preferences
 */
router.put('/preferences', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { preferences } = req.body;
    
    const user = await User.findOneAndUpdate(
      { id: userId },
      { $set: { preferences } },
      { new: true, runValidators: true }
    );
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User account not found'
        )
      );
    }
    
    logger.info(`User preferences updated: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Preferences updated successfully',
      data: {
        preferences: user.preferences
      }
    });

  } catch (error) {
    logger.error('Update user preferences error:', error);
    next(error);
  }
});

/**
 * DELETE /api/users/me
 * Delete user account
 */
router.delete('/me', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { confirmation } = req.body;
    
    if (confirmation !== 'DELETE_MY_ACCOUNT') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Account deletion confirmation required',
          'Please provide confirmation text: DELETE_MY_ACCOUNT'
        )
      );
    }
    
    // Soft delete - mark as deleted instead of actually removing
    const user = await User.findOneAndUpdate(
      { id: userId },
      { 
        $set: { 
          status: 'deleted',
          email: `deleted_${Date.now()}_${user.email}`,
          deleted_at: new Date()
        }
      },
      { new: true }
    );
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User account not found'
        )
      );
    }
    
    logger.info(`User account deleted: ${userId}`);
    
    res.json({
      success: true,
      message: 'Account deleted successfully'
    });

  } catch (error) {
    logger.error('Delete user account error:', error);
    next(error);
  }
});

module.exports = router;