const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const { authenticateToken } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { formatResponse, formatErrorResponse } = require('../utils/helpers');
const userService = require('../services/userService');
const authService = require('../services/authService');

// Rate limiting for authentication endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  message: formatErrorResponse('POL-4004', 'Too many authentication attempts'),
  standardHeaders: true,
  legacyHeaders: false,
});

router.use('/login', authLimiter);
router.use('/register', authLimiter);

router.post('/register', validate(schemas.userRegistration), async (req, res, next) => {
  try {
    const user = await userService.registerUser(req.body);
    const token = authService.refreshAuthToken(user);
    res.status(201).json(formatResponse(true, { user: user.toSafeObject(), token }));
  } catch (error) {
    res.status(400).json(formatErrorResponse('POL-4002', error.message));
  }
});

router.post('/login', validate(schemas.userLogin), async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const { user, token } = await authService.loginUser(email, password);
    res.json(formatResponse(true, { user: user.toSafeObject(), token }));
  } catch (error) {
    res.status(401).json(formatErrorResponse('POL-1001', error.message));
  }
});

router.get('/me', authenticateToken, (req, res) => {
  res.json(formatResponse(true, { user: req.user.toSafeObject() }));
});

router.post('/refresh', authenticateToken, (req, res) => {
  const token = authService.refreshAuthToken(req.user);
  res.json(formatResponse(true, { token }));
});

router.post('/logout', authenticateToken, (req, res) => {
  res.json(formatResponse(true, null, 'Logged out successfully'));
});

router.post('/forgot-password', validate({ email: schemas.userLogin.extract('email') }), async (req, res, next) => {
  try {
    await authService.forgotPassword(req.body.email);
    res.json(formatResponse(true, null, 'If an account with that email exists, a password reset link has been sent'));
  } catch (error) {
    next(error);
  }
});

router.post('/reset-password', validate({ token: require('joi').string().required(), password: schemas.userRegistration.extract('password') }), async (req, res, next) => {
  try {
    await authService.resetPassword(req.body.token, req.body.password);
    res.json(formatResponse(true, null, 'Password reset successfully'));
  } catch (error) {
    res.status(400).json(formatErrorResponse('POL-4001', error.message));
  }
});

router.post('/change-password', authenticateToken, validate({ current_password: require('joi').string().required(), new_password: schemas.userRegistration.extract('password') }), async (req, res, next) => {
  try {
    await authService.changePassword(req.user, req.body.current_password, req.body.new_password);
    res.json(formatResponse(true, null, 'Password changed successfully'));
  } catch (error) {
    res.status(400).json(formatErrorResponse('POL-4003', error.message));
  }
});

module.exports = router;
