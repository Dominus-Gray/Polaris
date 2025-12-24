const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../middleware/auth');
const { formatResponse, formatErrorResponse } = require('../utils/helpers');
const paymentService = require('../services/paymentService');

/**
 * Get Available Packages
 * GET /api/payments/packages
 */
router.get('/packages', async (req, res, next) => {
  try {
    const packages = paymentService.getPackages();
    res.json(formatResponse(true, { packages }));
  } catch (error) {
    next(error);
  }
});

/**
 * Create Checkout Session
 * POST /api/payments/checkout/session
 */
router.post('/checkout/session', authenticateToken, async (req, res, next) => {
  try {
    const { package_id, metadata = {} } = req.body;
    const originUrl = req.headers.origin || req.headers.referer?.split('?')[0] || 'http://localhost:3000';
    const session = await paymentService.createCheckoutSession(package_id, req.user.id, req.user.email, metadata, originUrl);
    res.json(formatResponse(true, session));
  } catch (error) {
    next(error);
  }
});

/**
 * Get Checkout Status
 * GET /api/payments/checkout/status/:session_id
 */
router.get('/checkout/status/:session_id', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params;
    const status = await paymentService.getCheckoutStatus(session_id, req.user.id);
    res.json(formatResponse(true, status));
  } catch (error) {
    if (error.message === 'Payment transaction not found') {
      return res.status(404).json(formatErrorResponse('POL-4001', error.message));
    }
    if (error.message === 'Access denied') {
      return res.status(403).json(formatErrorResponse('POL-1003', error.message));
    }
    next(error);
  }
});

/**
 * Stripe Webhook Handler
 * POST /api/payments/webhook/stripe
 */
router.post('/webhook/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const sig = req.headers['stripe-signature'];
    await paymentService.processWebhook(req.body, sig);
    res.json({ received: true });
  } catch (error) {
    res.status(400).send(`Webhook Error: ${error.message}`);
  }
});

/**
 * Get User Payment History
 * GET /api/payments/history
 */
router.get('/history', authenticateToken, async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const { transactions, total } = await paymentService.getPaymentHistory(req.user.id, parseInt(page), parseInt(limit));
    res.json(formatResponse(true, {
      transactions,
      pagination: {
        current_page: parseInt(page),
        per_page: parseInt(limit),
        total_items: total,
        total_pages: Math.ceil(total / limit)
      }
    }));
  } catch (error) {
    next(error);
  }
});

module.exports = router;
