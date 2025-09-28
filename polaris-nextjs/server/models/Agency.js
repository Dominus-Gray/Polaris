const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const agencyLicenseSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  license_code: {
    type: String,
    required: true,
    unique: true,
    validate: {
      validator: function(v) {
        return /^\d{10}$/.test(v);
      },
      message: 'License code must be exactly 10 digits'
    }
  },
  agency_user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  agency_id: {
    type: String,
    ref: 'User'
  },
  status: {
    type: String,
    enum: ['active', 'used', 'expired', 'revoked'],
    default: 'active'
  },
  used_by_client_id: {
    type: String,
    ref: 'User'
  },
  used_at: Date,
  expires_at: {
    type: Date,
    required: true
  },
  usage_limit: {
    type: Number,
    default: 1
  },
  usage_count: {
    type: Number,
    default: 0
  },
  metadata: {
    batch_id: String,
    generation_source: String,
    notes: String
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const agencyTierConfigurationSchema = new mongoose.Schema({
  _id: {
    type: String,
    default: uuidv4
  },
  agency_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  tier_access_levels: {
    type: Map,
    of: Number,
    default: () => {
      const levels = {};
      for (let i = 1; i <= 10; i++) {
        levels[`area${i}`] = 1;
      }
      return levels;
    }
  },
  pricing_per_tier: {
    tier1: { type: Number, default: 25.0 },
    tier2: { type: Number, default: 50.0 },
    tier3: { type: Number, default: 100.0 }
  },
  subscription_model: {
    type: String,
    enum: ['pay_per_assessment', 'monthly_subscription', 'annual_subscription'],
    default: 'pay_per_assessment'
  },
  monthly_limits: {
    license_generation: { type: Number, default: 10 },
    assessments: { type: Number, default: 100 },
    users: { type: Number, default: 50 }
  },
  features_enabled: {
    white_label: { type: Boolean, default: false },
    custom_branding: { type: Boolean, default: false },
    api_access: { type: Boolean, default: false },
    advanced_analytics: { type: Boolean, default: false },
    priority_support: { type: Boolean, default: false }
  },
  branding: {
    logo_url: String,
    primary_color: String,
    secondary_color: String,
    company_name: String,
    website: String,
    custom_domain: String
  },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
}, {
  collection: 'agency_tier_configurations'
});

const agencySubscriptionSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  agency_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  plan: {
    type: String,
    enum: ['trial', 'basic', 'professional', 'enterprise'],
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'cancelled', 'expired', 'suspended'],
    default: 'active'
  },
  billing_cycle: {
    type: String,
    enum: ['monthly', 'annual'],
    default: 'monthly'
  },
  current_period_start: {
    type: Date,
    required: true
  },
  current_period_end: {
    type: Date,
    required: true
  },
  stripe_subscription_id: String,
  stripe_customer_id: String,
  usage_current_period: {
    licenses_generated: { type: Number, default: 0 },
    assessments_conducted: { type: Number, default: 0 },
    users_created: { type: Number, default: 0 },
    api_calls: { type: Number, default: 0 }
  },
  usage_limits: {
    licenses_per_month: Number,
    assessments_per_month: Number,
    users_max: Number,
    api_calls_per_month: Number
  },
  pricing: {
    base_price: Number,
    per_assessment_price: Number,
    per_user_price: Number,
    setup_fee: Number
  },
  trial_ends_at: Date,
  cancelled_at: Date,
  cancellation_reason: String
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const agencyUsageSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  agency_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  period_start: {
    type: Date,
    required: true
  },
  period_end: {
    type: Date,
    required: true
  },
  usage_type: {
    type: String,
    enum: ['license_generation', 'assessment_completion', 'user_creation', 'api_call'],
    required: true
  },
  quantity: {
    type: Number,
    required: true,
    default: 1
  },
  tier_level: Number,
  area_id: String,
  client_id: {
    type: String,
    ref: 'User'
  },
  billable_amount: {
    type: Number,
    default: 0
  },
  billed: {
    type: Boolean,
    default: false
  },
  invoice_id: String,
  metadata: {
    session_id: String,
    request_id: String,
    notes: String
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Indexes
agencyLicenseSchema.index({ license_code: 1 });
agencyLicenseSchema.index({ agency_user_id: 1 });
agencyLicenseSchema.index({ status: 1 });
agencyLicenseSchema.index({ expires_at: 1 });

agencyTierConfigurationSchema.index({ agency_id: 1 });

agencySubscriptionSchema.index({ agency_id: 1 });
agencySubscriptionSchema.index({ status: 1 });
agencySubscriptionSchema.index({ current_period_end: 1 });

agencyUsageSchema.index({ agency_id: 1 });
agencyUsageSchema.index({ period_start: 1, period_end: 1 });
agencyUsageSchema.index({ usage_type: 1 });
agencyUsageSchema.index({ billed: 1 });

// Static methods
agencyLicenseSchema.statics.findAvailableByAgency = function(agencyId) {
  return this.find({
    agency_user_id: agencyId,
    status: 'active',
    expires_at: { $gt: new Date() }
  });
};

agencyLicenseSchema.statics.findExpiredLicenses = function() {
  return this.find({
    status: 'active',
    expires_at: { $lte: new Date() }
  });
};

agencySubscriptionSchema.statics.findActiveByAgency = function(agencyId) {
  return this.findOne({
    agency_id: agencyId,
    status: 'active',
    current_period_end: { $gt: new Date() }
  });
};

agencyUsageSchema.statics.findBillableUsage = function(agencyId, periodStart, periodEnd) {
  return this.find({
    agency_id: agencyId,
    period_start: { $gte: periodStart },
    period_end: { $lte: periodEnd },
    billed: false
  });
};

// Instance methods
agencyLicenseSchema.methods.markAsUsed = function(clientId) {
  this.status = 'used';
  this.used_by_client_id = clientId;
  this.used_at = new Date();
  this.usage_count += 1;
  return this.save();
};

agencyLicenseSchema.methods.isExpired = function() {
  return this.expires_at <= new Date();
};

agencyLicenseSchema.methods.isAvailable = function() {
  return this.status === 'active' && !this.isExpired() && this.usage_count < this.usage_limit;
};

agencySubscriptionSchema.methods.isActive = function() {
  return this.status === 'active' && this.current_period_end > new Date();
};

agencySubscriptionSchema.methods.hasExceededLimit = function(usageType) {
  const currentUsage = this.usage_current_period[usageType] || 0;
  const limit = this.usage_limits[usageType];
  return limit && currentUsage >= limit;
};

agencySubscriptionSchema.methods.incrementUsage = function(usageType, quantity = 1) {
  if (!this.usage_current_period[usageType]) {
    this.usage_current_period[usageType] = 0;
  }
  this.usage_current_period[usageType] += quantity;
  return this.save();
};

// Pre-save middleware
agencyTierConfigurationSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

const AgencyLicense = mongoose.model('AgencyLicense', agencyLicenseSchema);
const AgencyTierConfiguration = mongoose.model('AgencyTierConfiguration', agencyTierConfigurationSchema);
const AgencySubscription = mongoose.model('AgencySubscription', agencySubscriptionSchema);
const AgencyUsage = mongoose.model('AgencyUsage', agencyUsageSchema);

module.exports = {
  AgencyLicense,
  AgencyTierConfiguration,
  AgencySubscription,
  AgencyUsage
};