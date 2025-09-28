const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const chatSessionSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  participants: [{
    user_id: { type: String, required: true, ref: 'User' },
    role: { type: String, enum: ['client', 'provider', 'moderator'] },
    joined_at: { type: Date, default: Date.now },
    last_seen: Date,
    is_active: { type: Boolean, default: true }
  }],
  chat_type: {
    type: String,
    enum: ['direct', 'group', 'support', 'engagement'],
    required: true
  },
  engagement_id: {
    type: String,
    ref: 'Engagement'
  },
  title: String,
  status: {
    type: String,
    enum: ['active', 'archived', 'closed'],
    default: 'active'
  },
  last_message_at: Date,
  message_count: {
    type: Number,
    default: 0
  },
  metadata: {
    auto_archive_days: { type: Number, default: 30 },
    priority: { type: String, enum: ['low', 'medium', 'high'], default: 'medium' },
    tags: [String]
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const chatMessageSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  chat_id: {
    type: String,
    required: true,
    ref: 'ChatSession'
  },
  sender_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  message: {
    type: String,
    required: true,
    maxlength: 2000
  },
  message_type: {
    type: String,
    enum: ['text', 'file', 'image', 'system', 'notification'],
    default: 'text'
  },
  attachments: [{
    file_name: String,
    file_path: String,
    file_type: String,
    file_size: Number,
    thumbnail_path: String
  }],
  reply_to: {
    type: String,
    ref: 'ChatMessage'
  },
  edited: {
    is_edited: { type: Boolean, default: false },
    edited_at: Date,
    original_message: String
  },
  read_by: [{
    user_id: String,
    read_at: { type: Date, default: Date.now }
  }],
  reactions: [{
    user_id: String,
    emoji: String,
    added_at: { type: Date, default: Date.now }
  }],
  is_deleted: {
    type: Boolean,
    default: false
  },
  deleted_at: Date
}, {
  timestamps: {
    createdAt: 'sent_at',
    updatedAt: 'updated_at'
  }
});

const notificationSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  title: {
    type: String,
    required: true,
    maxlength: 200
  },
  message: {
    type: String,
    required: true,
    maxlength: 1000
  },
  type: {
    type: String,
    enum: [
      'assessment_completed',
      'service_request_received',
      'provider_response',
      'engagement_update',
      'payment_received',
      'system_alert',
      'knowledge_base_update',
      'license_expiring',
      'account_update'
    ],
    required: true
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent'],
    default: 'medium'
  },
  status: {
    type: String,
    enum: ['unread', 'read', 'dismissed', 'archived'],
    default: 'unread'
  },
  action_url: String,
  action_data: Object,
  delivery_methods: {
    in_app: { type: Boolean, default: true },
    email: { type: Boolean, default: false },
    sms: { type: Boolean, default: false },
    push: { type: Boolean, default: false }
  },
  delivery_status: {
    in_app: { sent: Boolean, sent_at: Date },
    email: { sent: Boolean, sent_at: Date, message_id: String },
    sms: { sent: Boolean, sent_at: Date, message_id: String },
    push: { sent: Boolean, sent_at: Date, message_id: String }
  },
  read_at: Date,
  expires_at: Date,
  metadata: {
    source_id: String,
    source_type: String,
    related_user_id: String
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const analyticsSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  event_type: {
    type: String,
    required: true,
    enum: [
      'page_view',
      'user_registration',
      'assessment_started',
      'assessment_completed',
      'service_request_created',
      'knowledge_base_access',
      'template_download',
      'provider_response',
      'engagement_created',
      'payment_completed',
      'error_occurred'
    ]
  },
  user_id: {
    type: String,
    ref: 'User'
  },
  session_id: String,
  area_id: String,
  page_url: String,
  referrer: String,
  user_agent: String,
  ip_address: String,
  country: String,
  city: String,
  device_type: {
    type: String,
    enum: ['desktop', 'tablet', 'mobile']
  },
  browser: String,
  os: String,
  event_data: Object,
  performance_metrics: {
    page_load_time: Number,
    time_on_page: Number,
    bounce_rate: Boolean
  },
  conversion_data: {
    funnel_step: String,
    conversion_value: Number,
    goal_completed: String
  }
}, {
  timestamps: {
    createdAt: 'timestamp',
    updatedAt: false
  }
});

const integrationSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  integration_type: {
    type: String,
    enum: ['quickbooks', 'stripe', 'google_oauth', 'microsoft_365', 'salesforce'],
    required: true
  },
  status: {
    type: String,
    enum: ['connected', 'disconnected', 'error', 'pending'],
    default: 'pending'
  },
  connection_data: {
    access_token: String,
    refresh_token: String,
    token_expires_at: Date,
    scope: [String],
    company_id: String,
    base_uri: String
  },
  settings: {
    auto_sync: { type: Boolean, default: false },
    sync_frequency: {
      type: String,
      enum: ['hourly', 'daily', 'weekly', 'manual'],
      default: 'daily'
    },
    data_types: [String],
    notifications: { type: Boolean, default: true }
  },
  last_sync: {
    timestamp: Date,
    status: {
      type: String,
      enum: ['success', 'partial', 'failed']
    },
    records_synced: Number,
    errors: [String]
  },
  health_status: {
    score: { type: Number, min: 0, max: 100 },
    last_check: Date,
    issues: [{
      type: String,
      severity: { type: String, enum: ['low', 'medium', 'high'] },
      message: String,
      detected_at: Date,
      resolved_at: Date
    }]
  },
  usage_stats: {
    api_calls_this_month: { type: Number, default: 0 },
    data_transferred_mb: { type: Number, default: 0 },
    last_activity: Date
  },
  error_log: [{
    timestamp: { type: Date, default: Date.now },
    error_type: String,
    error_message: String,
    request_details: Object,
    resolved: { type: Boolean, default: false }
  }]
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Indexes
chatSessionSchema.index({ 'participants.user_id': 1 });
chatSessionSchema.index({ chat_type: 1 });
chatSessionSchema.index({ status: 1 });
chatSessionSchema.index({ last_message_at: -1 });

chatMessageSchema.index({ chat_id: 1, sent_at: -1 });
chatMessageSchema.index({ sender_id: 1 });
chatMessageSchema.index({ is_deleted: 1 });

notificationSchema.index({ user_id: 1, created_at: -1 });
notificationSchema.index({ status: 1 });
notificationSchema.index({ type: 1 });
notificationSchema.index({ priority: 1 });
notificationSchema.index({ expires_at: 1 });

analyticsSchema.index({ event_type: 1 });
analyticsSchema.index({ user_id: 1 });
analyticsSchema.index({ timestamp: -1 });
analyticsSchema.index({ area_id: 1 });

integrationSchema.index({ user_id: 1 });
integrationSchema.index({ integration_type: 1 });
integrationSchema.index({ status: 1 });

// Static methods
chatSessionSchema.statics.findByUser = function(userId) {
  return this.find({
    'participants.user_id': userId,
    'participants.is_active': true
  }).sort({ last_message_at: -1 });
};

notificationSchema.statics.findUnreadByUser = function(userId) {
  return this.find({
    user_id: userId,
    status: 'unread',
    $or: [
      { expires_at: { $exists: false } },
      { expires_at: { $gt: new Date() } }
    ]
  }).sort({ created_at: -1 });
};

analyticsSchema.statics.findByEventType = function(eventType, startDate, endDate) {
  const query = { event_type: eventType };
  if (startDate || endDate) {
    query.timestamp = {};
    if (startDate) query.timestamp.$gte = startDate;
    if (endDate) query.timestamp.$lte = endDate;
  }
  return this.find(query);
};

integrationSchema.statics.findActiveByUser = function(userId) {
  return this.find({
    user_id: userId,
    status: 'connected'
  });
};

// Instance methods
chatSessionSchema.methods.addParticipant = function(userId, role = 'client') {
  const existingParticipant = this.participants.find(p => p.user_id === userId);
  if (!existingParticipant) {
    this.participants.push({ user_id: userId, role });
  }
  return this.save();
};

chatSessionSchema.methods.updateLastActivity = function() {
  this.last_message_at = new Date();
  this.message_count += 1;
  return this.save();
};

notificationSchema.methods.markAsRead = function() {
  this.status = 'read';
  this.read_at = new Date();
  return this.save();
};

integrationSchema.methods.updateHealthScore = function() {
  const issues = this.health_status.issues.filter(issue => !issue.resolved_at);
  const highSeverityCount = issues.filter(issue => issue.severity === 'high').length;
  const mediumSeverityCount = issues.filter(issue => issue.severity === 'medium').length;
  
  let score = 100;
  score -= (highSeverityCount * 30);
  score -= (mediumSeverityCount * 15);
  score -= (issues.length * 5);
  
  this.health_status.score = Math.max(0, score);
  this.health_status.last_check = new Date();
  
  return this.save();
};

const ChatSession = mongoose.model('ChatSession', chatSessionSchema);
const ChatMessage = mongoose.model('ChatMessage', chatMessageSchema);
const Notification = mongoose.model('Notification', notificationSchema);
const Analytics = mongoose.model('Analytics', analyticsSchema);
const Integration = mongoose.model('Integration', integrationSchema);

module.exports = {
  ChatSession,
  ChatMessage,
  Notification,
  Analytics,
  Integration
};