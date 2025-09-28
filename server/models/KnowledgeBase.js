const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const knowledgeBaseAreaSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  area_id: {
    type: String,
    required: true,
    unique: true
  },
  area_name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: String,
  color: String,
  order: {
    type: Number,
    required: true
  },
  is_active: {
    type: Boolean,
    default: true
  },
  access_level: {
    type: String,
    enum: ['free', 'basic', 'premium', 'enterprise'],
    default: 'free'
  },
  content_summary: String,
  tags: [String],
  metadata: {
    last_updated: Date,
    content_version: String,
    review_status: {
      type: String,
      enum: ['draft', 'review', 'approved', 'archived'],
      default: 'approved'
    }
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const knowledgeBaseArticleSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  area_id: {
    type: String,
    required: true,
    ref: 'KnowledgeBaseArea'
  },
  title: {
    type: String,
    required: true,
    maxlength: 200
  },
  slug: {
    type: String,
    required: true,
    unique: true
  },
  content: {
    type: String,
    required: true
  },
  summary: {
    type: String,
    maxlength: 500
  },
  article_type: {
    type: String,
    enum: ['guide', 'template', 'checklist', 'faq', 'best_practice', 'case_study'],
    required: true
  },
  difficulty_level: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    default: 'beginner'
  },
  estimated_read_time: {
    type: Number, // in minutes
    default: 5
  },
  is_published: {
    type: Boolean,
    default: true
  },
  access_level: {
    type: String,
    enum: ['free', 'basic', 'premium', 'enterprise'],
    default: 'free'
  },
  author: {
    name: String,
    email: String,
    role: String
  },
  tags: [String],
  categories: [String],
  related_articles: [{
    article_id: String,
    title: String,
    relevance_score: Number
  }],
  external_links: [{
    title: String,
    url: String,
    description: String,
    link_type: {
      type: String,
      enum: ['resource', 'tool', 'reference', 'download']
    }
  }],
  attachments: [{
    file_name: String,
    file_path: String,
    file_type: String,
    file_size: Number,
    description: String
  }],
  seo: {
    meta_title: String,
    meta_description: String,
    keywords: [String]
  },
  analytics: {
    view_count: { type: Number, default: 0 },
    download_count: { type: Number, default: 0 },
    share_count: { type: Number, default: 0 },
    rating_average: { type: Number, min: 0, max: 5 },
    rating_count: { type: Number, default: 0 }
  },
  last_reviewed: Date,
  next_review_due: Date
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const knowledgeBaseAccessSchema = new mongoose.Schema({
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
  area_id: {
    type: String,
    required: true
  },
  article_id: String,
  access_type: {
    type: String,
    enum: ['view', 'download', 'share', 'search'],
    required: true
  },
  resource_type: {
    type: String,
    enum: ['article', 'template', 'guide', 'checklist'],
    required: true
  },
  session_id: String,
  ip_address: String,
  user_agent: String,
  referrer: String,
  duration_seconds: Number,
  metadata: {
    search_query: String,
    filter_applied: Object,
    download_format: String
  }
}, {
  timestamps: {
    createdAt: 'accessed_at',
    updatedAt: false
  }
});

const knowledgeBaseRatingSchema = new mongoose.Schema({
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
  article_id: {
    type: String,
    required: true,
    ref: 'KnowledgeBaseArticle'
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  comment: {
    type: String,
    maxlength: 1000
  },
  helpful_votes: {
    type: Number,
    default: 0
  },
  is_verified_user: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

const aiGeneratedContentSchema = new mongoose.Schema({
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
  content_type: {
    type: String,
    enum: ['template', 'guide', 'checklist', 'response', 'recommendation'],
    required: true
  },
  area_id: {
    type: String,
    required: true
  },
  template_type: String,
  prompt: {
    type: String,
    required: true
  },
  generated_content: {
    type: String,
    required: true
  },
  content_format: {
    type: String,
    enum: ['markdown', 'html', 'plain_text', 'docx', 'pdf'],
    default: 'markdown'
  },
  generation_model: {
    type: String,
    default: 'emergent-llm'
  },
  generation_parameters: {
    temperature: Number,
    max_tokens: Number,
    model_version: String
  },
  quality_score: {
    type: Number,
    min: 0,
    max: 1
  },
  user_feedback: {
    rating: { type: Number, min: 1, max: 5 },
    comment: String,
    is_helpful: Boolean
  },
  usage_count: {
    type: Number,
    default: 0
  },
  shared: {
    type: Boolean,
    default: false
  },
  expires_at: Date
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// Indexes
knowledgeBaseAreaSchema.index({ area_id: 1 });
knowledgeBaseAreaSchema.index({ order: 1 });
knowledgeBaseAreaSchema.index({ is_active: 1 });

knowledgeBaseArticleSchema.index({ area_id: 1 });
knowledgeBaseArticleSchema.index({ slug: 1 });
knowledgeBaseArticleSchema.index({ is_published: 1 });
knowledgeBaseArticleSchema.index({ article_type: 1 });
knowledgeBaseArticleSchema.index({ tags: 1 });
knowledgeBaseArticleSchema.index({ 'analytics.view_count': -1 });

knowledgeBaseAccessSchema.index({ user_id: 1 });
knowledgeBaseAccessSchema.index({ area_id: 1 });
knowledgeBaseAccessSchema.index({ accessed_at: -1 });
knowledgeBaseAccessSchema.index({ access_type: 1 });

knowledgeBaseRatingSchema.index({ article_id: 1 });
knowledgeBaseRatingSchema.index({ user_id: 1, article_id: 1 }, { unique: true });

aiGeneratedContentSchema.index({ user_id: 1 });
aiGeneratedContentSchema.index({ area_id: 1 });
aiGeneratedContentSchema.index({ content_type: 1 });
aiGeneratedContentSchema.index({ created_at: -1 });
aiGeneratedContentSchema.index({ expires_at: 1 });

// Static methods
knowledgeBaseAreaSchema.statics.findActiveAreas = function() {
  return this.find({ is_active: true }).sort({ order: 1 });
};

knowledgeBaseArticleSchema.statics.findPublishedByArea = function(areaId) {
  return this.find({ 
    area_id: areaId, 
    is_published: true 
  }).sort({ created_at: -1 });
};

knowledgeBaseArticleSchema.statics.findPopularArticles = function(limit = 10) {
  return this.find({ is_published: true })
    .sort({ 'analytics.view_count': -1 })
    .limit(limit);
};

knowledgeBaseAccessSchema.statics.logAccess = function(accessData) {
  return this.create(accessData);
};

aiGeneratedContentSchema.statics.findByUserAndType = function(userId, contentType) {
  return this.find({ 
    user_id: userId, 
    content_type: contentType 
  }).sort({ created_at: -1 });
};

// Instance methods
knowledgeBaseArticleSchema.methods.incrementViewCount = function() {
  this.analytics.view_count += 1;
  return this.save();
};

knowledgeBaseArticleSchema.methods.updateRating = function(newRating) {
  const currentAvg = this.analytics.rating_average || 0;
  const currentCount = this.analytics.rating_count || 0;
  
  const newCount = currentCount + 1;
  const newAvg = ((currentAvg * currentCount) + newRating) / newCount;
  
  this.analytics.rating_average = Math.round(newAvg * 10) / 10;
  this.analytics.rating_count = newCount;
  
  return this.save();
};

aiGeneratedContentSchema.methods.incrementUsage = function() {
  this.usage_count += 1;
  return this.save();
};

// Pre-save middleware
knowledgeBaseArticleSchema.pre('save', function(next) {
  if (this.isModified('title') && !this.slug) {
    this.slug = this.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  }
  
  if (this.isModified('content')) {
    // Calculate estimated read time (assuming 200 words per minute)
    const wordCount = this.content.split(/\s+/).length;
    this.estimated_read_time = Math.ceil(wordCount / 200);
  }
  
  next();
});

const KnowledgeBaseArea = mongoose.model('KnowledgeBaseArea', knowledgeBaseAreaSchema);
const KnowledgeBaseArticle = mongoose.model('KnowledgeBaseArticle', knowledgeBaseArticleSchema);
const KnowledgeBaseAccess = mongoose.model('KnowledgeBaseAccess', knowledgeBaseAccessSchema);
const KnowledgeBaseRating = mongoose.model('KnowledgeBaseRating', knowledgeBaseRatingSchema);
const AIGeneratedContent = mongoose.model('AIGeneratedContent', aiGeneratedContentSchema);

module.exports = {
  KnowledgeBaseArea,
  KnowledgeBaseArticle,
  KnowledgeBaseAccess,
  KnowledgeBaseRating,
  AIGeneratedContent
};