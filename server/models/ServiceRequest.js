const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const serviceRequestSchema = new mongoose.Schema({
  id: {
    type: String,
    default: () => `req_${uuidv4()}`,
    unique: true,
    required: true
  },
  client_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  area_id: {
    type: String,
    required: true
  },
  service_type: {
    type: String,
    enum: ['assessment_help', 'compliance_support', 'professional_help', 'consultation'],
    required: true
  },
  title: {
    type: String,
    required: true,
    maxlength: 200
  },
  description: {
    type: String,
    required: true,
    maxlength: 2000
  },
  budget_range: {
    type: String,
    enum: [
      'under-1000',
      '1000-2500', 
      '2500-5000',
      '5000-10000',
      '10000-25000',
      'over-25000',
      'negotiable'
    ]
  },
  timeline: {
    type: String,
    enum: [
      'asap',
      '1-2 weeks',
      '1 month',
      '1-2 months',
      '2-3 months',
      '3-6 months',
      'flexible'
    ]
  },
  urgency: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent'],
    default: 'medium'
  },
  status: {
    type: String,
    enum: ['open', 'in_progress', 'completed', 'cancelled'],
    default: 'open'
  },
  providers_notified: {
    type: Number,
    default: 0
  },
  max_providers: {
    type: Number,
    default: 5
  },
  location: {
    city: String,
    state: String,
    country: String,
    remote_ok: { type: Boolean, default: true }
  },
  requirements: [{
    requirement: String,
    priority: {
      type: String,
      enum: ['required', 'preferred', 'optional'],
      default: 'required'
    }
  }],
  attachments: [{
    file_name: String,
    file_path: String,
    file_size: Number,
    uploaded_at: { type: Date, default: Date.now }
  }],
  tags: [String],
  metadata: {
    source: String,
    referral_code: String,
    assessment_session_id: String
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const providerResponseSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  request_id: {
    type: String,
    required: true,
    ref: 'ServiceRequest'
  },
  provider_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  proposed_fee: {
    type: Number,
    required: true,
    min: 0
  },
  estimated_timeline: {
    type: String,
    required: true
  },
  proposal_note: {
    type: String,
    required: true,
    maxlength: 2000
  },
  availability: {
    type: String,
    enum: ['immediate', 'within-week', 'within-month', 'flexible']
  },
  status: {
    type: String,
    enum: ['pending', 'accepted', 'rejected', 'withdrawn'],
    default: 'pending'
  },
  deliverables: [{
    item: String,
    description: String,
    timeline: String
  }],
  terms_conditions: {
    payment_terms: String,
    revision_policy: String,
    cancellation_policy: String
  },
  portfolio_samples: [{
    title: String,
    description: String,
    url: String,
    file_path: String
  }],
  client_viewed: {
    type: Boolean,
    default: false
  },
  client_viewed_at: Date,
  response_ranking: {
    type: Number,
    min: 1,
    max: 5
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const engagementSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  service_request_id: {
    type: String,
    required: true,
    ref: 'ServiceRequest'
  },
  provider_response_id: {
    type: String,
    required: true,
    ref: 'ProviderResponse'
  },
  client_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  provider_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  status: {
    type: String,
    enum: [
      'initiated',
      'accepted',
      'in_progress',
      'delivered',
      'under_review',
      'approved',
      'released',
      'disputed',
      'cancelled'
    ],
    default: 'initiated'
  },
  agreed_fee: {
    type: Number,
    required: true
  },
  agreed_timeline: {
    type: String,
    required: true
  },
  milestones: [{
    id: { type: String, default: uuidv4 },
    title: String,
    description: String,
    due_date: Date,
    amount: Number,
    status: {
      type: String,
      enum: ['pending', 'in_progress', 'completed', 'approved'],
      default: 'pending'
    },
    deliverables: [String],
    completed_at: Date,
    approved_at: Date
  }],
  communications: [{
    id: { type: String, default: uuidv4 },
    from_user_id: String,
    message: String,
    message_type: {
      type: String,
      enum: ['message', 'status_update', 'milestone_update', 'file_share'],
      default: 'message'
    },
    attachments: [{
      file_name: String,
      file_path: String,
      file_size: Number
    }],
    timestamp: { type: Date, default: Date.now },
    read_by: [{
      user_id: String,
      read_at: Date
    }]
  }],
  payment_status: {
    type: String,
    enum: ['pending', 'escrowed', 'released', 'refunded', 'disputed'],
    default: 'pending'
  },
  payment_details: {
    stripe_payment_intent_id: String,
    amount_escrowed: Number,
    amount_released: Number,
    release_date: Date,
    refund_amount: Number,
    refund_date: Date
  },
  deliverables: [{
    id: { type: String, default: uuidv4 },
    title: String,
    description: String,
    file_path: String,
    file_name: String,
    submitted_at: Date,
    approved_at: Date,
    feedback: String
  }],
  reviews: {
    client_review: {
      rating: { type: Number, min: 1, max: 5 },
      comment: String,
      submitted_at: Date
    },
    provider_review: {
      rating: { type: Number, min: 1, max: 5 },
      comment: String,
      submitted_at: Date
    }
  },
  started_at: Date,
  completed_at: Date,
  cancelled_at: Date,
  cancellation_reason: String
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Indexes
serviceRequestSchema.index({ client_id: 1 });
serviceRequestSchema.index({ area_id: 1 });
serviceRequestSchema.index({ status: 1 });
serviceRequestSchema.index({ created_at: -1 });
serviceRequestSchema.index({ service_type: 1 });

providerResponseSchema.index({ request_id: 1 });
providerResponseSchema.index({ provider_id: 1 });
providerResponseSchema.index({ status: 1 });
providerResponseSchema.index({ created_at: -1 });

engagementSchema.index({ client_id: 1 });
engagementSchema.index({ provider_id: 1 });
engagementSchema.index({ status: 1 });
engagementSchema.index({ service_request_id: 1 });

// Virtual fields
serviceRequestSchema.virtual('response_count', {
  ref: 'ProviderResponse',
  localField: 'id',
  foreignField: 'request_id',
  count: true
});

// Static methods
serviceRequestSchema.statics.findOpenRequests = function() {
  return this.find({ status: 'open' }).sort({ created_at: -1 });
};

serviceRequestSchema.statics.findByArea = function(areaId) {
  return this.find({ area_id: areaId }).sort({ created_at: -1 });
};

providerResponseSchema.statics.findByRequest = function(requestId) {
  return this.find({ request_id: requestId }).sort({ created_at: 1 });
};

engagementSchema.statics.findActiveByUser = function(userId) {
  return this.find({
    $or: [{ client_id: userId }, { provider_id: userId }],
    status: { $in: ['accepted', 'in_progress', 'delivered', 'under_review'] }
  }).sort({ updated_at: -1 });
};

// Instance methods
serviceRequestSchema.methods.canReceiveResponses = function() {
  return this.status === 'open' && this.providers_notified < this.max_providers;
};

engagementSchema.methods.canTransitionTo = function(newStatus) {
  const validTransitions = {
    'initiated': ['accepted', 'cancelled'],
    'accepted': ['in_progress', 'cancelled'],
    'in_progress': ['delivered', 'cancelled'],
    'delivered': ['under_review', 'approved'],
    'under_review': ['approved', 'in_progress'],
    'approved': ['released'],
    'released': [],
    'cancelled': [],
    'disputed': ['in_progress', 'cancelled', 'released']
  };
  
  return validTransitions[this.status]?.includes(newStatus) || false;
};

const ServiceRequest = mongoose.model('ServiceRequest', serviceRequestSchema);
const ProviderResponse = mongoose.model('ProviderResponse', providerResponseSchema);
const Engagement = mongoose.model('Engagement', engagementSchema);

module.exports = {
  ServiceRequest,
  ProviderResponse,
  Engagement
};