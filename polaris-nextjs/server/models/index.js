// Central export for all models
const User = require('./User');
const { 
  AssessmentSession, 
  TierAssessmentSession, 
  AssessmentEvidence, 
  AssessmentResult 
} = require('./Assessment');
const { 
  ServiceRequest, 
  ProviderResponse, 
  Engagement 
} = require('./ServiceRequest');
const { 
  AgencyLicense, 
  AgencyTierConfiguration, 
  AgencySubscription, 
  AgencyUsage 
} = require('./Agency');
const { 
  KnowledgeBaseArea, 
  KnowledgeBaseArticle, 
  KnowledgeBaseAccess, 
  KnowledgeBaseRating, 
  AIGeneratedContent 
} = require('./KnowledgeBase');
const {
  ChatSession,
  ChatMessage,
  Notification,
  Analytics,
  Integration
} = require('./System');

module.exports = {
  // User Management
  User,
  
  // Assessment System
  AssessmentSession,
  TierAssessmentSession,
  AssessmentEvidence,
  AssessmentResult,
  
  // Service Request System
  ServiceRequest,
  ProviderResponse,
  Engagement,
  
  // Agency Management
  AgencyLicense,
  AgencyTierConfiguration,
  AgencySubscription,
  AgencyUsage,
  
  // Knowledge Base
  KnowledgeBaseArea,
  KnowledgeBaseArticle,
  KnowledgeBaseAccess,
  KnowledgeBaseRating,
  AIGeneratedContent,
  
  // System Models
  ChatSession,
  ChatMessage,
  Notification,
  Analytics,
  Integration
};