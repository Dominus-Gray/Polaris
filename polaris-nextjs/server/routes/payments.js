const express = require('express')
const router = express.Router()
const { authenticateToken, requireRole } = require('../middleware/auth')
const { formatResponse, formatErrorResponse, getBusinessAreas } = require('../utils/helpers')
const logger = require('../utils/logger').logger

// Import payment transaction model
const PaymentTransaction = require('../models/PaymentTransaction')
const { ServiceRequest } = require('../models/ServiceRequest')
const User = require('../models/User')

// Initialize Stripe with emergent key
const stripe = require('stripe')(process.env.STRIPE_API_KEY)

const BUSINESS_AREAS = getBusinessAreas()

// Define fixed service packages (security requirement - prevent price manipulation)
const SERVICE_PACKAGES = {
  'knowledge_base_basic': {
    name: 'Knowledge Base Basic Access',
    amount: 19.99,
    currency: 'usd',
    description: 'Access to basic business templates and resources'
  },
  'knowledge_base_premium': {
    name: 'Knowledge Base Premium Access', 
    amount: 49.99,
    currency: 'usd',
    description: 'Full access to premium business templates and resources'
  },
  'assessment_tier_upgrade': {
    name: 'Assessment Tier Upgrade',
    amount: 29.99,
    currency: 'usd',
    description: 'Upgrade to advanced tier assessment with detailed analytics'
  },
  'service_request_small': {
    name: 'Small Service Request',
    amount: 99.99,
    currency: 'usd',
    description: 'Professional consultation for small projects'
  },
  'service_request_medium': {
    name: 'Medium Service Request',
    amount: 299.99,
    currency: 'usd',
    description: 'Comprehensive professional service with detailed deliverables'
  },
  'service_request_large': {
    name: 'Large Service Request',
    amount: 599.99,
    currency: 'usd',
    description: 'Enterprise-level professional service and consultation'
  }
}

/**
 * Create Checkout Session (Emergent Integration)
 * POST /api/payments/checkout/session
 */
router.post('/checkout/session', authenticateToken, async (req, res, next) => {
  try {
    const { package_id, metadata = {} } = req.body
    const originUrl = req.headers.origin || req.headers.referer?.split('?')[0] || 'http://localhost:3000'
    
    // Validate package exists (security requirement)
    if (!package_id || !SERVICE_PACKAGES[package_id]) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid package selection',
          'The specified package does not exist'
        )
      )
    }

    const packageInfo = SERVICE_PACKAGES[package_id]
    
    // Build URLs using frontend origin (security requirement)
    const successUrl = `${originUrl}/dashboard/payments/success?session_id={CHECKOUT_SESSION_ID}`
    const cancelUrl = `${originUrl}/dashboard/payments/cancel`
    
    // Create checkout session with standard Stripe
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price_data: {
          currency: packageInfo.currency,
          product_data: {
            name: packageInfo.name,
            description: packageInfo.description,
          },
          unit_amount: Math.round(packageInfo.amount * 100), // Convert to cents
        },
        quantity: 1,
      }],
      mode: 'payment',
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata: {
        package_id,
        package_name: packageInfo.name,
        user_id: req.user.id.toString(),
        user_email: req.user.email,
        ...metadata
      }
    })
    
    // Create payment transaction record (MANDATORY per playbook)
    const paymentTransaction = new PaymentTransaction({
      session_id: session.id,
      user_id: req.user.id,
      user_email: req.user.email,
      package_id,
      package_name: packageInfo.name,
      amount: packageInfo.amount,
      currency: packageInfo.currency,
      payment_status: 'initiated',
      status: 'pending',
      metadata: session.metadata
    })
    
    await paymentTransaction.save()
    
    logger.info(`Payment session created: ${session.id} for package ${package_id} by user ${req.user.email}`)
    
    res.json({
      success: true,
      data: {
        checkout_session_id: session.id,
        checkout_url: session.url,
        package: {
          id: package_id,
          name: packageInfo.name,
          amount: packageInfo.amount,
          currency: packageInfo.currency,
          description: packageInfo.description
        }
      }
    })
    
  } catch (error) {
    logger.error('Stripe checkout session creation error:', error)
    next(error)
  }
})

/**
 * Get Checkout Status (Emergent Integration with polling support)
 * GET /api/payments/checkout/status/:session_id
 */
router.get('/checkout/status/:session_id', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params
    
    // Find existing transaction
    const transaction = await PaymentTransaction.findOne({ session_id })
    if (!transaction) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Payment transaction not found',
          'The specified payment session does not exist'
        )
      )
    }

    // Verify transaction belongs to current user
    if (transaction.user_id !== req.user.id) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only view your own payment transactions'
        )
      )
    }

    // If already processed as successful, return cached status
    if (transaction.payment_status === 'paid' && transaction.processed) {
      return res.json({
        success: true,
        data: {
          status: transaction.status,
          payment_status: transaction.payment_status,
          amount_total: Math.round(transaction.amount * 100), // Convert to cents for frontend
          currency: transaction.currency,
          metadata: transaction.metadata,
          package: {
            id: transaction.package_id,
            name: transaction.package_name
          },
          processed: transaction.processed
        }
      })
    }

    // Check status with Stripe using emergent integration
    const stripe = getStripeCheckout(req.headers.origin || 'http://localhost:3000')
    if (!stripe) {
      return res.status(500).json(
        formatErrorResponse(
          'POL-5001',
          'Payment service unavailable',
          'Cannot check payment status at this time'
        )
      )
    }

    const checkoutStatus = await stripe.get_checkout_status(session_id)
    
    // Update transaction status
    const oldPaymentStatus = transaction.payment_status
    transaction.payment_status = checkoutStatus.payment_status
    transaction.status = checkoutStatus.status

    // Process successful payment only once
    if (checkoutStatus.payment_status === 'paid' && !transaction.processed) {
      transaction.processed = true
      transaction.status = 'complete'
      
      // Grant access based on package type
      await processSuccessfulPayment(transaction)
      
      logger.info(`Payment processed successfully: ${session_id} for user ${transaction.user_email}`)
    }
    
    await transaction.save()
    
    res.json({
      success: true,
      data: {
        status: checkoutStatus.status,
        payment_status: checkoutStatus.payment_status,
        amount_total: checkoutStatus.amount_total,
        currency: checkoutStatus.currency,
        metadata: checkoutStatus.metadata,
        package: {
          id: transaction.package_id,
          name: transaction.package_name
        },
        processed: transaction.processed
      }
    })
    
  } catch (error) {
    logger.error('Stripe checkout status error:', error)
    next(error)
  }
})

/**
 * Process successful payment (grant access, update permissions, etc.)
 */
async function processSuccessfulPayment(transaction) {
  try {
    const { package_id, user_id, user_email } = transaction
    
    // Grant access based on package type
    if (package_id.includes('knowledge_base')) {
      // Grant knowledge base access
      logger.info(`Granting knowledge base access to user ${user_email} for package ${package_id}`)
      // TODO: Implement knowledge base access logic
    } 
    else if (package_id.includes('assessment_tier')) {
      // Upgrade assessment tier
      logger.info(`Upgrading assessment tier for user ${user_email}`)
      // TODO: Implement tier upgrade logic
    }
    else if (package_id.includes('service_request')) {
      // Grant service request credits or access
      logger.info(`Granting service request access to user ${user_email} for package ${package_id}`)
      // TODO: Implement service request access logic
    }
    
  } catch (error) {
    logger.error('Error processing successful payment:', error)
  }
}

/**
 * Stripe Webhook Handler (Emergent Integration)
 * POST /api/payments/webhook/stripe
 */
router.post('/webhook/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const stripe = getStripeCheckout('http://localhost:3000')
    if (!stripe) {
      return res.status(500).json({ error: 'Payment service unavailable' })
    }
    
    const sig = req.headers['stripe-signature']
    
    // Handle webhook using emergent integration
    const webhookResponse = await stripe.handle_webhook(req.body, sig)
    
    if (webhookResponse.session_id && webhookResponse.payment_status === 'paid') {
      // Find and update transaction
      const transaction = await PaymentTransaction.findOne({ 
        session_id: webhookResponse.session_id 
      })
      
      if (transaction && !transaction.processed) {
        transaction.payment_status = webhookResponse.payment_status
        transaction.status = 'complete'
        transaction.processed = true
        
        // Process successful payment
        await processSuccessfulPayment(transaction)
        await transaction.save()
        
        logger.info(`Webhook: Payment processed for ${transaction.user_email}, package: ${transaction.package_id}`)
      }
    }
    
    res.json({ received: true })
    
  } catch (error) {
    logger.error('Stripe webhook error:', error)
    res.status(400).json({ error: 'Webhook processing failed' })
  }
})

/**
 * Get Available Packages
 * GET /api/payments/packages
 */
router.get('/packages', async (req, res, next) => {
  try {
    const packages = Object.keys(SERVICE_PACKAGES).map(key => ({
      id: key,
      ...SERVICE_PACKAGES[key]
    }))
    
    res.json({
      success: true,
      data: { packages }
    })
  } catch (error) {
    logger.error('Get packages error:', error)
    next(error)
  }
})

/**
 * Get User Payment History  
 * GET /api/payments/history
 */
router.get('/history', authenticateToken, async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query
    const skip = (page - 1) * limit

    const transactions = await PaymentTransaction.find({ 
      user_id: req.user.id 
    })
    .sort({ created_at: -1 })
    .skip(skip)
    .limit(parseInt(limit))
    
    const total = await PaymentTransaction.countDocuments({ user_id: req.user.id })
    
    res.json({
      success: true,
      data: {
        transactions: transactions.map(t => ({
          id: t._id,
          session_id: t.session_id,
          package_id: t.package_id,
          package_name: t.package_name,
          amount: t.amount,
          currency: t.currency,
          payment_status: t.payment_status,
          status: t.status,
          processed: t.processed,
          created_at: t.created_at,
          updated_at: t.updated_at
        })),
        pagination: {
          current_page: parseInt(page),
          per_page: parseInt(limit),
          total_items: total,
          total_pages: Math.ceil(total / limit)
        }
      }
    })
    
  } catch (error) {
    logger.error('Payment history error:', error)
    next(error)
  }
})

// Keep existing service-request and knowledge-base payment methods for backward compatibility
// but update them to use the new package system

/**
 * POST /api/payments/service-request (Legacy support)
 * Create payment for service request - now uses package system
 */
router.post('/service-request', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const { service_request_id, provider_response_id } = req.body
    const originUrl = req.headers.origin || 'http://localhost:3000'
    
    // Get provider response to determine package size based on fee
    const { ProviderResponse } = require('../models/ServiceRequest')
    const providerResponse = await ProviderResponse.findOne({ 
      id: provider_response_id,
      request_id: service_request_id
    })
    
    if (!providerResponse) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Provider response not found')
      )
    }

    // Determine package based on proposed fee
    let package_id = 'service_request_small'
    if (providerResponse.proposed_fee > 200) package_id = 'service_request_medium'
    if (providerResponse.proposed_fee > 500) package_id = 'service_request_large'

    // Use the new checkout session endpoint
    req.body = {
      package_id,
      metadata: {
        service_request_id,
        provider_response_id,
        provider_id: providerResponse.provider_id,
        legacy_fee: providerResponse.proposed_fee
      }
    }
    
    // Forward to new checkout endpoint
    return router.handle(req, res, next)
    
  } catch (error) {
    logger.error('Legacy service request payment error:', error)
    next(error)
  }
})

/**
 * POST /api/payments/knowledge-base (Legacy support)  
 * Create payment for knowledge base access
 */
router.post('/knowledge-base', authenticateToken, async (req, res, next) => {
  try {
    const { area_id, access_type = 'premium' } = req.body
    
    // Check if user has access (paywall protection for test accounts)
    if (req.user.email?.endsWith('@polaris.example.com')) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Payment not required',
          'Test accounts have full access to knowledge base resources'
        )
      )
    }
    
    // Determine package based on access type
    const package_id = access_type === 'basic' ? 'knowledge_base_basic' : 'knowledge_base_premium'
    
    // Forward to new checkout endpoint
    req.body = {
      package_id,
      metadata: { area_id, access_type }
    }
    
    return router.handle(req, res, next)
    
  } catch (error) {
    logger.error('Legacy knowledge base payment error:', error)
    next(error)
  }
})

module.exports = router