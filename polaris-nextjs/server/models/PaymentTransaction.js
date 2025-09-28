const mongoose = require('mongoose')

const PaymentTransactionSchema = new mongoose.Schema({
  // Stripe session ID
  session_id: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  
  // User information
  user_id: {
    type: String,
    index: true
  },
  user_email: {
    type: String,
    index: true
  },
  
  // Package information
  package_id: {
    type: String,
    required: true
  },
  package_name: {
    type: String,
    required: true
  },
  
  // Payment details
  amount: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    required: true,
    default: 'usd'
  },
  
  // Payment status from Stripe
  payment_status: {
    type: String,
    required: true,
    enum: ['initiated', 'pending', 'paid', 'failed', 'expired', 'canceled'],
    default: 'initiated'
  },
  
  // Overall transaction status
  status: {
    type: String,
    required: true,
    enum: ['pending', 'complete', 'failed', 'expired'],
    default: 'pending'
  },
  
  // Flag to prevent duplicate processing
  processed: {
    type: Boolean,
    default: false
  },
  
  // Additional metadata
  metadata: {
    type: Object,
    default: {}
  },
  
  // Service request related fields (if applicable)
  service_request_id: String,
  provider_response_id: String,
  provider_id: String,
  
  // Knowledge base access fields (if applicable)
  area_id: String,
  access_type: String,
  
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  collection: 'payment_transactions'
})

// Update the updated_at field before saving
PaymentTransactionSchema.pre('save', function(next) {
  this.updated_at = new Date()
  next()
})

// Indexes for better query performance
PaymentTransactionSchema.index({ session_id: 1 })
PaymentTransactionSchema.index({ user_id: 1, created_at: -1 })
PaymentTransactionSchema.index({ user_email: 1, created_at: -1 })
PaymentTransactionSchema.index({ payment_status: 1 })
PaymentTransactionSchema.index({ status: 1 })
PaymentTransactionSchema.index({ processed: 1 })

const PaymentTransaction = mongoose.model('PaymentTransaction', PaymentTransactionSchema)

module.exports = PaymentTransaction