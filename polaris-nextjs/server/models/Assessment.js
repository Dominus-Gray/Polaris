const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const assessmentSessionSchema = new mongoose.Schema({
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
  session_type: {
    type: String,
    enum: ['standard', 'tier_based'],
    default: 'standard'
  },
  area_id: {
    type: String,
    required: true
  },
  tier_level: {
    type: Number,
    min: 1,
    max: 3,
    default: 1
  },
  status: {
    type: String,
    enum: ['active', 'completed', 'abandoned'],
    default: 'active'
  },
  questions: [{
    id: { type: String, required: true },
    text: { type: String, required: true },
    tier_level: { type: Number, required: true },
    area_id: { type: String, required: true },
    order: { type: Number, required: true }
  }],
  responses: [{
    question_id: { type: String, required: true },
    response: { 
      type: String, 
      enum: ['compliant', 'not_compliant', 'partially_compliant'],
      required: true 
    },
    tier_level: { type: Number, required: true },
    evidence_required: { type: Boolean, default: false },
    evidence_provided: { type: Boolean, default: false },
    evidence_url: String,
    notes: String,
    submitted_at: { type: Date, default: Date.now },
    verification_status: {
      type: String,
      enum: ['pending', 'verified', 'rejected'],
      default: 'pending'
    }
  }],
  completion_score: {
    type: Number,
    min: 0,
    max: 100
  },
  tier_completion_score: {
    type: Number,
    min: 0,
    max: 100
  },
  completed_at: Date,
  metadata: {
    client_tier_access: Object,
    started_from: String,
    completion_time_seconds: Number
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Tier-based assessment session schema
const tierAssessmentSessionSchema = new mongoose.Schema({
  _id: {
    type: String,
    default: uuidv4
  },
  user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  area_id: {
    type: String,
    required: true
  },
  tier_level: {
    type: Number,
    min: 1,
    max: 3,
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'completed', 'abandoned'],
    default: 'active'
  },
  questions: [{
    id: { type: String, required: true },
    text: { type: String, required: true },
    tier_level: { type: Number, required: true },
    area_id: { type: String, required: true },
    order: { type: Number, required: true }
  }],
  responses: [{
    question_id: { type: String, required: true },
    response: { 
      type: String, 
      enum: ['compliant', 'not_compliant', 'partially_compliant'],
      required: true 
    },
    tier_level: { type: Number, required: true },
    evidence_required: { type: Boolean, default: false },
    evidence_provided: { type: Boolean, default: false },
    evidence_url: String,
    notes: String,
    submitted_at: { type: Date, default: Date.now },
    verification_status: {
      type: String,
      enum: ['pending', 'verified', 'rejected']
    }
  }],
  tier_completion_score: {
    type: Number,
    min: 0,
    max: 100
  },
  completed_at: Date,
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
}, {
  collection: 'tier_assessment_sessions'
});

// Evidence upload schema
const assessmentEvidenceSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  session_id: {
    type: String,
    required: true
  },
  question_id: {
    type: String,
    required: true
  },
  user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  file_name: {
    type: String,
    required: true
  },
  file_path: {
    type: String,
    required: true
  },
  file_size: {
    type: Number,
    required: true
  },
  file_type: {
    type: String,
    required: true
  },
  upload_status: {
    type: String,
    enum: ['pending', 'completed', 'failed'],
    default: 'completed'
  },
  verification_status: {
    type: String,
    enum: ['pending', 'verified', 'rejected'],
    default: 'pending'
  },
  verification_notes: String
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Assessment results schema
const assessmentResultSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  session_id: {
    type: String,
    required: true,
    ref: 'AssessmentSession'
  },
  user_id: {
    type: String,
    required: true,
    ref: 'User'
  },
  area_id: {
    type: String,
    required: true
  },
  overall_score: {
    type: Number,
    min: 0,
    max: 100,
    required: true
  },
  tier_scores: {
    tier1: Number,
    tier2: Number,
    tier3: Number
  },
  gap_analysis: [{
    question_id: String,
    area_id: String,
    tier_level: Number,
    response: String,
    recommendation: String,
    priority: {
      type: String,
      enum: ['low', 'medium', 'high', 'critical']
    }
  }],
  recommendations: [{
    type: String,
    priority: {
      type: String,
      enum: ['low', 'medium', 'high', 'critical']
    },
    category: String,
    description: String,
    resources: [String]
  }],
  next_steps: [String],
  certificate_generated: {
    type: Boolean,
    default: false
  },
  certificate_url: String,
  shared_with: [{
    email: String,
    shared_at: { type: Date, default: Date.now },
    access_level: {
      type: String,
      enum: ['view', 'download'],
      default: 'view'
    }
  }]
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Indexes
assessmentSessionSchema.index({ user_id: 1 });
assessmentSessionSchema.index({ area_id: 1 });
assessmentSessionSchema.index({ status: 1 });
assessmentSessionSchema.index({ created_at: -1 });

tierAssessmentSessionSchema.index({ user_id: 1 });
tierAssessmentSessionSchema.index({ area_id: 1 });
tierAssessmentSessionSchema.index({ status: 1 });

assessmentEvidenceSchema.index({ session_id: 1 });
assessmentEvidenceSchema.index({ user_id: 1 });

assessmentResultSchema.index({ user_id: 1 });
assessmentResultSchema.index({ session_id: 1 });
assessmentResultSchema.index({ area_id: 1 });

// Static methods
assessmentSessionSchema.statics.findActiveByUser = function(userId) {
  return this.find({ user_id: userId, status: 'active' });
};

assessmentSessionSchema.statics.findByUserAndArea = function(userId, areaId) {
  return this.find({ user_id: userId, area_id: areaId });
};

// Instance methods
assessmentSessionSchema.methods.calculateProgress = function() {
  const totalQuestions = this.questions.length;
  const answeredQuestions = this.responses.length;
  return totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
};

assessmentSessionSchema.methods.isComplete = function() {
  return this.questions.length > 0 && this.responses.length >= this.questions.length;
};

const AssessmentSession = mongoose.model('AssessmentSession', assessmentSessionSchema);
const TierAssessmentSession = mongoose.model('TierAssessmentSession', tierAssessmentSessionSchema);
const AssessmentEvidence = mongoose.model('AssessmentEvidence', assessmentEvidenceSchema);
const AssessmentResult = mongoose.model('AssessmentResult', assessmentResultSchema);

module.exports = {
  AssessmentSession,
  TierAssessmentSession,
  AssessmentEvidence,
  AssessmentResult
};