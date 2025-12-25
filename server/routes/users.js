const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { formatResponse, formatErrorResponse } = require('../utils/helpers');
const userService = require('../services/userService');
const logger = require('../utils/logger').logger;

router.get('/me', authenticateToken, async (req, res, next) => {
  try {
    res.json(formatResponse(true, { user: req.user.toSafeObject() }));
  } catch (error) {
    logger.error('Get user profile error:', error);
    next(error);
  }
});

router.put('/me', authenticateToken, validate(schemas.profileUpdate), async (req, res, next) => {
  try {
    const user = await userService.updateUserProfile(req.user.id, req.body);
    res.json(formatResponse(true, { user: user.toSafeObject() }, 'Profile updated successfully'));
  } catch (error) {
    logger.error('Update user profile error:', error);
    if (error.message === 'User not found') {
      return res.status(404).json(formatErrorResponse('POL-4001', error.message));
    }
    next(error);
  }
});

router.delete('/me', authenticateToken, async (req, res, next) => {
  try {
    await userService.deleteUser(req.user.id, req.body.confirmation);
    res.json(formatResponse(true, null, 'Account deleted successfully'));
  } catch (error) {
    logger.error('Delete user account error:', error);
    if (error.message === 'Account deletion confirmation required') {
      return res.status(400).json(formatErrorResponse('POL-4003', error.message));
    }
    if (error.message === 'User not found') {
      return res.status(404).json(formatErrorResponse('POL-4001', error.message));
    }
    next(error);
  }
});

module.exports = router;

router.get('/dashboard', authenticateToken, async (req, res, next) => {
  try {
    const dashboardData = await userService.getDashboard(req.user);
    res.json(formatResponse(true, dashboardData));
  } catch (error) {
    logger.error('Get user dashboard error:', error);
    next(error);
  }
});

router.get('/notifications', authenticateToken, async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const { notifications, total } = await userService.getNotifications(req.user.id, parseInt(page), parseInt(limit));
    res.json(formatResponse(true, {
      notifications,
      pagination: {
        current_page: parseInt(page),
        per_page: parseInt(limit),
        total_items: total,
        total_pages: Math.ceil(total / limit)
      }
    }));
  } catch (error) {
    logger.error('Get user notifications error:', error);
    next(error);
  }
});

router.put('/preferences', authenticateToken, async (req, res, next) => {
  try {
    const preferences = await userService.updatePreferences(req.user.id, req.body.preferences);
    res.json(formatResponse(true, { preferences }, 'Preferences updated successfully'));
  } catch (error) {
    logger.error('Update user preferences error:', error);
    if (error.message === 'User not found') {
      return res.status(404).json(formatErrorResponse('POL-4001', error.message));
    }
    next(error);
  }
});
