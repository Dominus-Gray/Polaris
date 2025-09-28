const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const { ServiceRequest, Engagement } = require('../models/ServiceRequest');
const { KnowledgeBaseAccess } = require('../models/KnowledgeBase');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { 
  formatResponse, 
  formatErrorResponse,
  getBusinessAreas
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

const BUSINESS_AREAS = getBusinessAreas();

/**
 * POST /api/payments/service-request
 * Create payment for service request
 */
router.post('/service-request', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const { 
      service_request_id, 
      provider_response_id, 
      success_url,
      cancel_url 
    } = req.body;
    
    const clientId = req.user.id;
    
    // Validate service request
    const serviceRequest = await ServiceRequest.findOne({ 
      id: service_request_id,
      client_id: clientId
    });
    
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Service request not found',
          'The specified service request does not exist or you do not have access to it'
        )
      );
    }
    
    // Get provider response
    const { ProviderResponse } = require('../models/ServiceRequest');
    const providerResponse = await ProviderResponse.findOne({ 
      id: provider_response_id,
      request_id: service_request_id
    });
    
    if (!providerResponse) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Provider response not found',
          'The specified provider response does not exist'
        )
      );
    }
    
    // Get provider details
    const provider = await User.findOne({ id: providerResponse.provider_id });
    if (!provider) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Provider not found',
          'The specified provider does not exist'
        )
      );
    }
    
    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'payment',
      success_url: success_url || `${process.env.APP_URL}/payments/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancel_url || `${process.env.APP_URL}/payments/cancel`,
      customer_email: req.user.email,
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `${serviceRequest.title} - Professional Services`,
              description: `Service provided by ${provider.name || provider.email}`,
              metadata: {
                service_request_id,
                provider_response_id,
                area_id: serviceRequest.area_id
              }
            },
            unit_amount: Math.round(providerResponse.proposed_fee * 100) // Convert to cents
          },
          quantity: 1
        }
      ],
      metadata: {
        type: 'service_request_payment',
        service_request_id,
        provider_response_id,
        client_id: clientId,
        provider_id: providerResponse.provider_id
      }
    });
    
    logger.info(`Payment session created: ${session.id} for service request ${service_request_id}`);
    
    res.json({
      success: true,
      data: {
        checkout_session_id: session.id,
        checkout_url: session.url,
        amount: providerResponse.proposed_fee,
        currency: 'USD',
        provider_name: provider.name || provider.email,
        service_title: serviceRequest.title
      }
    });
    
  } catch (error) {
    logger.error('Create service payment error:', error);
    next(error);
  }
});

/**
 * POST /api/payments/knowledge-base
 * Create payment for knowledge base access
 */
router.post('/knowledge-base', authenticateToken, async (req, res, next) => {
  try {
    const { 
      area_id, 
      access_type = 'full', 
      success_url,
      cancel_url 
    } = req.body;
    
    const userId = req.user.id;
    
    // Check if user has access (paywall protection)
    if (req.user.email?.endsWith('@polaris.example.com')) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Payment not required',
          'Test accounts have full access to knowledge base resources'
        )
      );
    }
    
    if (!BUSINESS_AREAS[area_id]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    const areaName = BUSINESS_AREAS[area_id];
    
    // Determine pricing based on access type
    const pricing = {
      'basic': 19.99,
      'premium': 49.99,
      'full': 99.99
    };
    
    const amount = pricing[access_type] || pricing.basic;
    
    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'payment',
      success_url: success_url || `${process.env.APP_URL}/knowledge-base/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancel_url || `${process.env.APP_URL}/knowledge-base/cancel`,
      customer_email: req.user.email,
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: `Knowledge Base Access - ${areaName}`,
              description: `${access_type.charAt(0).toUpperCase() + access_type.slice(1)} access to ${areaName} resources`,
              metadata: {
                area_id,
                access_type
              }
            },
            unit_amount: Math.round(amount * 100) // Convert to cents
          },
          quantity: 1
        }
      ],
      metadata: {
        type: 'knowledge_base_payment',
        area_id,
        access_type,
        user_id: userId
      }
    });
    
    logger.info(`Knowledge base payment session created: ${session.id} for area ${area_id}`);
    
    res.json({
      success: true,
      data: {
        checkout_session_id: session.id,
        checkout_url: session.url,
        amount,
        currency: 'USD',
        area_name: areaName,
        access_type
      }
    });
    
  } catch (error) {
    logger.error('Create knowledge base payment error:', error);
    next(error);
  }
});

/**
 * GET /api/payments/session/:sessionId
 * Get payment session details
 */
router.get('/session/:sessionId', authenticateToken, async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    
    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Payment session not found',
          'The specified payment session does not exist'
        )
      );
    }
    
    // Verify session belongs to current user
    if (session.customer_email !== req.user.email) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only view your own payment sessions'
        )
      );
    }
    
    res.json({
      success: true,
      data: {
        session_id: session.id,
        payment_status: session.payment_status,
        amount_total: session.amount_total / 100, // Convert from cents
        currency: session.currency,
        metadata: session.metadata,
        created: new Date(session.created * 1000),
        expires_at: new Date(session.expires_at * 1000)
      }
    });
    
  } catch (error) {
    logger.error('Get payment session error:', error);
    next(error);
  }
});

/**
 * GET /api/payments/history
 * Get user payment history
 */
router.get('/history', authenticateToken, async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const userEmail = req.user.email;
    
    // Get payment sessions from Stripe
    const sessions = await stripe.checkout.sessions.list({
      customer_email: userEmail,
      limit: parseInt(limit),
      expand: ['data.line_items']
    });
    
    const payments = sessions.data.map(session => ({
      session_id: session.id,
      payment_status: session.payment_status,
      amount_total: session.amount_total / 100,
      currency: session.currency,
      metadata: session.metadata,
      created: new Date(session.created * 1000),
      description: session.line_items?.data[0]?.price?.product?.name || 'Payment'
    }));
    
    res.json({
      success: true,
      data: {
        payments,
        has_more: sessions.has_more,
        total_count: sessions.data.length
      }
    });
    
  } catch (error) {
    logger.error('Get payment history error:', error);
    next(error);
  }
});

/**
 * POST /api/payments/refund
 * Request refund for a payment
 */
router.post('/refund', authenticateToken, async (req, res, next) => {
  try {
    const { session_id, reason } = req.body;
    
    if (!session_id || !reason) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Session ID and reason are required',
          'Please provide the payment session ID and refund reason'
        )
      );
    }
    
    const session = await stripe.checkout.sessions.retrieve(session_id);
    
    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Payment session not found',
          'The specified payment session does not exist'
        )
      );
    }
    
    // Verify session belongs to current user
    if (session.customer_email !== req.user.email) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only request refunds for your own payments'
        )
      );
    }
    
    if (session.payment_status !== 'paid') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Payment not eligible for refund',
          'Only successful payments can be refunded'
        )
      );
    }
    
    // Get payment intent
    const paymentIntent = await stripe.paymentIntents.retrieve(session.payment_intent);
    
    // Create refund
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntent.id,
      reason: 'requested_by_customer',
      metadata: {
        requested_by: req.user.id,
        reason: reason,
        original_session_id: session_id
      }
    });
    
    logger.info(`Refund requested: ${refund.id} for session ${session_id} by user ${req.user.email}`);
    
    res.json({
      success: true,
      message: 'Refund request submitted successfully',
      data: {
        refund_id: refund.id,
        amount: refund.amount / 100,
        currency: refund.currency,
        status: refund.status,
        reason: refund.reason
      }
    });
    
  } catch (error) {
    logger.error('Request refund error:', error);
    next(error);
  }
});

/**
 * GET /api/payments/methods
 * Get user's saved payment methods
 */
router.get('/methods', authenticateToken, async (req, res, next) => {
  try {
    // For now, return empty array as we're using checkout sessions
    // In a full implementation, you'd create and manage Stripe customers
    res.json({
      success: true,
      data: {
        payment_methods: [],
        default_payment_method: null
      }
    });
    
  } catch (error) {
    logger.error('Get payment methods error:', error);
    next(error);
  }
});

module.exports = router;