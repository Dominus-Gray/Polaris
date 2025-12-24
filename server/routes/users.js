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
