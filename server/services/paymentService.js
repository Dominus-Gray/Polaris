const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const PaymentTransaction = require('../models/PaymentTransaction');
const { logger } = require('../utils/logger');

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
};

const getPackages = () => {
  return Object.keys(SERVICE_PACKAGES).map(key => ({
    id: key,
    ...SERVICE_PACKAGES[key]
  }));
};

const createCheckoutSession = async (packageId, userId, userEmail, metadata, originUrl) => {
  const packageInfo = SERVICE_PACKAGES[packageId];
  if (!packageInfo) {
    throw new Error('Invalid package selection');
  }

  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: packageInfo.currency,
        product_data: {
          name: packageInfo.name,
          description: packageInfo.description,
        },
        unit_amount: Math.round(packageInfo.amount * 100),
      },
      quantity: 1,
    }],
    mode: 'payment',
    success_url: `${originUrl}/dashboard/payments/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${originUrl}/dashboard/payments/cancel`,
    metadata: {
      package_id: packageId,
      package_name: packageInfo.name,
      user_id: userId.toString(),
      user_email: userEmail,
      ...metadata
    }
  });

  const paymentTransaction = new PaymentTransaction({
    session_id: session.id,
    user_id: userId,
    user_email: userEmail,
    package_id: packageId,
    package_name: packageInfo.name,
    amount: packageInfo.amount,
    currency: packageInfo.currency,
    payment_status: 'initiated',
    status: 'pending',
    metadata: session.metadata
  });

  await paymentTransaction.save();

  return {
    checkout_session_id: session.id,
    checkout_url: session.url,
    package: {
      id: packageId,
      name: packageInfo.name,
      amount: packageInfo.amount,
      currency: packageInfo.currency,
      description: packageInfo.description
    }
  };
};

const getCheckoutStatus = async (sessionId, userId) => {
  const transaction = await PaymentTransaction.findOne({ session_id: sessionId });
  if (!transaction) {
    throw new Error('Payment transaction not found');
  }

  if (transaction.user_id !== userId) {
    throw new Error('Access denied');
  }

  if (transaction.payment_status === 'paid' && transaction.processed) {
    return {
      status: transaction.status,
      payment_status: transaction.payment_status,
      amount_total: Math.round(transaction.amount * 100),
      currency: transaction.currency,
      metadata: transaction.metadata,
      package: {
        id: transaction.package_id,
        name: transaction.package_name
      },
      processed: transaction.processed
    };
  }

  const session = await stripe.checkout.sessions.retrieve(sessionId);
  transaction.payment_status = session.payment_status;
  transaction.status = session.status;

  if (session.payment_status === 'paid' && !transaction.processed) {
    await processSuccessfulPayment(transaction, session);
  }

  await transaction.save();

  return {
    status: session.status,
    payment_status: session.payment_status,
    amount_total: session.amount_total,
    currency: session.currency,
    metadata: session.metadata,
    package: {
      id: transaction.package_id,
      name: transaction.package_name
    },
    processed: transaction.processed
  };
};

const processWebhook = async (payload, signature) => {
  const event = stripe.webhooks.constructEvent(payload, signature, process.env.STRIPE_WEBHOOK_SECRET);

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const transaction = await PaymentTransaction.findOne({ session_id: session.id });

    if (transaction && !transaction.processed) {
      await processSuccessfulPayment(transaction, session);
      await transaction.save();
    }
  }
};

const processSuccessfulPayment = async (transaction, session) => {
  transaction.processed = true;
  transaction.status = 'complete';
  transaction.payment_intent_id = session.payment_intent;
  transaction.customer_id = session.customer;

  try {
    const charge = await stripe.charges.retrieve(
      (await stripe.paymentIntents.retrieve(session.payment_intent)).latest_charge
    );
    transaction.receipt_url = charge.receipt_url;
  } catch (chargeError) {
    logger.error(`Could not retrieve charge for session ${session.id}:`, chargeError);
  }

  // TODO: Grant access based on package type
};

const getPaymentHistory = async (userId, page, limit) => {
  const skip = (page - 1) * limit;
  const transactions = await PaymentTransaction.find({ user_id: userId })
    .sort({ created_at: -1 })
    .skip(skip)
    .limit(limit);
  const total = await PaymentTransaction.countDocuments({ user_id: userId });

  return {
    transactions,
    total
  };
};

module.exports = {
  getPackages,
  createCheckoutSession,
  getCheckoutStatus,
  processWebhook,
  getPaymentHistory
};
