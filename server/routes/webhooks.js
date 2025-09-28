const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const { ServiceRequest, Engagement } = require('../models/ServiceRequest');
const { KnowledgeBaseAccess } = require('../models/KnowledgeBase');
const User = require('../models/User');
const { Analytics } = require('../models/System');
const logger = require('../utils/logger').logger;

const router = express.Router();

// Raw body parser for Stripe webhooks
router.use('/stripe', express.raw({ type: 'application/json' }));

/**
 * POST /api/webhook/stripe
 * Handle Stripe webhook events
 */
router.post('/stripe', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    // Verify webhook signature
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    logger.error('Stripe webhook signature verification failed:', err.message);
    return res.status(400).json({
      error: true,
      message: 'Webhook signature verification failed'
    });
  }

  try {
    // Handle the event
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutSessionCompleted(event.data.object);
        break;
      
      case 'payment_intent.succeeded':
        await handlePaymentIntentSucceeded(event.data.object);
        break;
      
      case 'payment_intent.payment_failed':
        await handlePaymentIntentFailed(event.data.object);
        break;
      
      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(event.data.object);
        break;
      
      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object);
        break;
      
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;
      
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;
      
      default:
        logger.info(`Unhandled Stripe event type: ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    logger.error('Error processing Stripe webhook:', error);
    res.status(500).json({
      error: true,
      message: 'Error processing webhook'
    });
  }
});

/**
 * Handle successful checkout session
 */
async function handleCheckoutSessionCompleted(session) {
  logger.info(`Checkout session completed: ${session.id}`);
  
  const metadata = session.metadata;
  
  if (metadata.type === 'service_request_payment') {
    await handleServiceRequestPayment(session, metadata);
  } else if (metadata.type === 'knowledge_base_payment') {
    await handleKnowledgeBasePayment(session, metadata);
  }
  
  // Log analytics event
  await logAnalyticsEvent('payment_completed', metadata.user_id || metadata.client_id, {
    session_id: session.id,
    amount: session.amount_total / 100,
    payment_type: metadata.type
  });
}

/**
 * Handle service request payment
 */
async function handleServiceRequestPayment(session, metadata) {
  try {
    const { service_request_id, provider_response_id, client_id, provider_id } = metadata;
    
    // Create engagement
    const engagement = new Engagement({
      service_request_id,
      provider_response_id,
      client_id,
      provider_id,
      agreed_fee: session.amount_total / 100,
      agreed_timeline: 'As specified in proposal', // TODO: Get from provider response
      status: 'initiated',
      payment_status: 'escrowed',
      payment_details: {
        stripe_payment_intent_id: session.payment_intent,
        amount_escrowed: session.amount_total / 100
      }
    });
    
    await engagement.save();
    
    // Update service request status
    await ServiceRequest.findOneAndUpdate(
      { id: service_request_id },
      { status: 'in_progress' }
    );
    
    logger.info(`Engagement created: ${engagement.id} for service request ${service_request_id}`);
    
    // TODO: Send notifications to client and provider
    
  } catch (error) {
    logger.error('Error handling service request payment:', error);
  }
}

/**
 * Handle knowledge base payment
 */
async function handleKnowledgeBasePayment(session, metadata) {
  try {
    const { area_id, access_type, user_id } = metadata;
    
    // Grant knowledge base access
    // In a real implementation, you'd update user's access permissions
    // For now, just log the access grant
    
    await logAnalyticsEvent('knowledge_base_access_granted', user_id, {
      area_id,
      access_type,
      payment_session_id: session.id,
      amount_paid: session.amount_total / 100
    });
    
    logger.info(`Knowledge base access granted: ${access_type} for area ${area_id} to user ${user_id}`);
    
    // TODO: Update user permissions and send confirmation email
    
  } catch (error) {
    logger.error('Error handling knowledge base payment:', error);
  }
}

/**
 * Handle successful payment intent
 */
async function handlePaymentIntentSucceeded(paymentIntent) {
  logger.info(`Payment succeeded: ${paymentIntent.id}, amount: ${paymentIntent.amount / 100}`);
  
  // Additional processing for successful payments
  await logAnalyticsEvent('payment_intent_succeeded', null, {
    payment_intent_id: paymentIntent.id,
    amount: paymentIntent.amount / 100,
    currency: paymentIntent.currency
  });
}

/**
 * Handle failed payment intent
 */
async function handlePaymentIntentFailed(paymentIntent) {
  logger.error(`Payment failed: ${paymentIntent.id}, error: ${paymentIntent.last_payment_error?.message}`);
  
  await logAnalyticsEvent('payment_intent_failed', null, {
    payment_intent_id: paymentIntent.id,
    amount: paymentIntent.amount / 100,
    error: paymentIntent.last_payment_error?.message
  });
  
  // TODO: Handle failed payment (notify user, retry logic, etc.)
}

/**
 * Handle successful invoice payment
 */
async function handleInvoicePaymentSucceeded(invoice) {
  logger.info(`Invoice payment succeeded: ${invoice.id}`);
  
  await logAnalyticsEvent('invoice_payment_succeeded', invoice.customer, {
    invoice_id: invoice.id,
    amount: invoice.amount_paid / 100,
    subscription_id: invoice.subscription
  });
  
  // TODO: Update subscription status, send receipt, etc.
}

/**
 * Handle subscription creation
 */
async function handleSubscriptionCreated(subscription) {
  logger.info(`Subscription created: ${subscription.id}`);
  
  await logAnalyticsEvent('subscription_created', subscription.customer, {
    subscription_id: subscription.id,
    plan: subscription.items.data[0]?.price?.id,
    status: subscription.status
  });
  
  // TODO: Update user subscription status in database
}

/**
 * Handle subscription update
 */
async function handleSubscriptionUpdated(subscription) {
  logger.info(`Subscription updated: ${subscription.id}`);
  
  await logAnalyticsEvent('subscription_updated', subscription.customer, {
    subscription_id: subscription.id,
    status: subscription.status,
    current_period_end: new Date(subscription.current_period_end * 1000)
  });
  
  // TODO: Update user subscription in database
}

/**
 * Handle subscription deletion
 */
async function handleSubscriptionDeleted(subscription) {
  logger.info(`Subscription deleted: ${subscription.id}`);
  
  await logAnalyticsEvent('subscription_deleted', subscription.customer, {
    subscription_id: subscription.id,
    canceled_at: new Date(subscription.canceled_at * 1000)
  });
  
  // TODO: Update user subscription status, handle access revocation
}

/**
 * Log analytics event
 */
async function logAnalyticsEvent(eventType, userId, eventData) {
  try {
    const analyticsEvent = new Analytics({
      event_type: eventType,
      user_id: userId,
      event_data: eventData,
      timestamp: new Date()
    });
    
    await analyticsEvent.save();
  } catch (error) {
    logger.error('Error logging analytics event:', error);
  }
}

/**
 * POST /api/webhook/test
 * Test webhook endpoint for development
 */
router.post('/test', express.json(), async (req, res) => {
  if (process.env.NODE_ENV === 'production') {
    return res.status(404).json({
      error: true,
      message: 'Test endpoint not available in production'
    });
  }
  
  try {
    const { event_type, data } = req.body;
    
    logger.info(`Test webhook received: ${event_type}`);
    
    // Log test event
    await logAnalyticsEvent(`test_${event_type}`, null, data);
    
    res.json({
      success: true,
      message: 'Test webhook processed successfully',
      received_data: { event_type, data }
    });
    
  } catch (error) {
    logger.error('Error processing test webhook:', error);
    res.status(500).json({
      error: true,
      message: 'Error processing test webhook'
    });
  }
});

/**
 * GET /api/webhook/health
 * Webhook service health check
 */
router.get('/health', (req, res) => {
  res.json({
    success: true,
    service: 'webhooks',
    status: 'healthy',
    timestamp: new Date(),
    endpoints: {
      stripe: '/api/webhook/stripe',
      test: process.env.NODE_ENV !== 'production' ? '/api/webhook/test' : 'not_available'
    }
  });
});

module.exports = router;