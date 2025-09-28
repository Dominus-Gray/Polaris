const express = require('express');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const { 
  KnowledgeBaseArea, 
  KnowledgeBaseArticle, 
  KnowledgeBaseAccess, 
  AIGeneratedContent 
} = require('../models/KnowledgeBase');
const User = require('../models/User');
const { authenticateToken, checkKnowledgeBaseAccess } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse, 
  getBusinessAreas
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

const BUSINESS_AREAS = getBusinessAreas();

// Initialize knowledge base areas if they don't exist
const initializeKnowledgeBase = async () => {
  try {
    const count = await KnowledgeBaseArea.countDocuments();
    if (count === 0) {
      const areas = Object.entries(BUSINESS_AREAS).map(([id, name], index) => ({
        id: uuidv4(),
        area_id: id,
        area_name: name,
        description: getAreaDescription(id),
        order: index + 1,
        is_active: true
      }));
      
      await KnowledgeBaseArea.insertMany(areas);
      logger.info('Knowledge base areas initialized');
    }
  } catch (error) {
    logger.error('Error initializing knowledge base:', error);
  }
};

// Initialize on startup
initializeKnowledgeBase();

function getAreaDescription(areaId) {
  const descriptions = {
    area1: 'Resources for business formation, registration, and legal structure setup',
    area2: 'Financial management, accounting, and budgeting guidance',
    area3: 'Legal compliance, contracts, and regulatory requirements',
    area4: 'Quality management systems and continuous improvement',
    area5: 'Technology infrastructure and cybersecurity best practices',
    area6: 'Human resources management and organizational development',
    area7: 'Performance tracking, reporting, and business analytics',
    area8: 'Risk management and business continuity planning',
    area9: 'Supply chain optimization and vendor management',
    area10: 'Competitive strategy and market positioning'
  };
  return descriptions[areaId] || 'Business knowledge and resources';
}

/**
 * GET /api/knowledge-base/areas
 * Get all knowledge base areas
 */
router.get('/areas', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const areas = await KnowledgeBaseArea.findActiveAreas();
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: req.user.id,
      area_id: 'all',
      access_type: 'view',
      resource_type: 'area'
    });
    
    res.json({
      success: true,
      data: {
        areas: areas.map(area => ({
          area_id: area.area_id,
          area_name: area.area_name,
          description: area.description,
          order: area.order,
          icon: area.icon,
          color: area.color,
          article_count: 0 // TODO: Get actual count
        }))
      }
    });
    
  } catch (error) {
    logger.error('Get knowledge base areas error:', error);
    next(error);
  }
});

/**
 * GET /api/knowledge-base/area/:areaId
 * Get knowledge base area content
 */
router.get('/area/:areaId', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { areaId } = req.params;
    
    if (!BUSINESS_AREAS[areaId]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Knowledge base area not found',
          'The specified knowledge base area does not exist'
        )
      );
    }
    
    const area = await KnowledgeBaseArea.findOne({ area_id: areaId, is_active: true });
    if (!area) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Knowledge base area not found',
          'The specified knowledge base area is not available'
        )
      );
    }
    
    // Get articles for this area
    const articles = await KnowledgeBaseArticle.findPublishedByArea(areaId).limit(20);
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: req.user.id,
      area_id: areaId,
      access_type: 'view',
      resource_type: 'area'
    });
    
    res.json({
      success: true,
      data: {
        area: {
          area_id: area.area_id,
          area_name: area.area_name,
          description: area.description,
          icon: area.icon,
          color: area.color
        },
        articles: articles.map(article => ({
          id: article.id,
          title: article.title,
          summary: article.summary,
          article_type: article.article_type,
          difficulty_level: article.difficulty_level,
          estimated_read_time: article.estimated_read_time,
          view_count: article.analytics.view_count,
          rating: article.analytics.rating_average
        }))
      }
    });
    
  } catch (error) {
    logger.error('Get knowledge base area error:', error);
    next(error);
  }
});

/**
 * GET /api/knowledge-base/article/:articleId
 * Get specific knowledge base article
 */
router.get('/article/:articleId', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { articleId } = req.params;
    
    const article = await KnowledgeBaseArticle.findOne({ 
      id: articleId, 
      is_published: true 
    });
    
    if (!article) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Article not found',
          'The specified knowledge base article does not exist'
        )
      );
    }
    
    // Increment view count
    await article.incrementViewCount();
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: req.user.id,
      area_id: article.area_id,
      article_id: articleId,
      access_type: 'view',
      resource_type: 'article'
    });
    
    res.json({
      success: true,
      data: {
        article: {
          id: article.id,
          title: article.title,
          content: article.content,
          summary: article.summary,
          article_type: article.article_type,
          difficulty_level: article.difficulty_level,
          estimated_read_time: article.estimated_read_time,
          tags: article.tags,
          categories: article.categories,
          related_articles: article.related_articles,
          external_links: article.external_links,
          attachments: article.attachments,
          analytics: {
            view_count: article.analytics.view_count,
            rating_average: article.analytics.rating_average,
            rating_count: article.analytics.rating_count
          },
          created_at: article.created_at,
          updated_at: article.updated_at
        }
      }
    });
    
  } catch (error) {
    logger.error('Get knowledge base article error:', error);
    next(error);
  }
});

/**
 * POST /api/knowledge-base/generate-template/:areaId/:templateType
 * Generate AI-powered template
 */
router.post('/generate-template/:areaId/:templateType', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { areaId, templateType } = req.params;
    const userId = req.user.id;
    
    if (!BUSINESS_AREAS[areaId]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    const validTemplateTypes = ['template', 'guide', 'checklist', 'practices'];
    if (!validTemplateTypes.includes(templateType)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid template type',
          `Template type must be one of: ${validTemplateTypes.join(', ')}`
        )
      );
    }
    
    // Generate content based on area and template type
    const areaName = BUSINESS_AREAS[areaId];
    const content = generateTemplateContent(areaId, templateType, areaName);
    
    // Create AI generated content record
    const aiContent = new AIGeneratedContent({
      user_id: userId,
      content_type: 'template',
      area_id: areaId,
      template_type: templateType,
      prompt: `Generate ${templateType} for ${areaName}`,
      generated_content: content,
      content_format: 'markdown',
      generation_model: 'polaris-template-engine',
      quality_score: 0.95
    });
    
    await aiContent.save();
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: userId,
      area_id: areaId,
      access_type: 'download',
      resource_type: 'template',
      metadata: { template_type: templateType }
    });
    
    // Determine file extension based on template type
    const fileExtensions = {
      template: '.docx',
      guide: '.docx', 
      checklist: '.docx',
      practices: '.pptx'
    };
    
    const filename = `polaris_${areaId}_${templateType}${fileExtensions[templateType] || '.md'}`;
    
    res.json({
      success: true,
      data: {
        content,
        filename,
        content_type: fileExtensions[templateType] ? 'application/octet-stream' : 'text/markdown',
        generated_at: aiContent.created_at,
        template_type: templateType,
        area_name: areaName
      }
    });
    
  } catch (error) {
    logger.error('Generate template error:', error);
    next(error);
  }
});

/**
 * GET /api/knowledge-base/generate-template/:areaId/:templateType
 * Get/Generate AI-powered template (GET version for compatibility)
 */
router.get('/generate-template/:areaId/:templateType', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { areaId, templateType } = req.params;
    const userId = req.user.id;
    
    if (!BUSINESS_AREAS[areaId]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    const validTemplateTypes = ['template', 'guide', 'checklist', 'practices'];
    if (!validTemplateTypes.includes(templateType)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid template type',
          `Template type must be one of: ${validTemplateTypes.join(', ')}`
        )
      );
    }
    
    const areaName = BUSINESS_AREAS[areaId];
    const content = generateTemplateContent(areaId, templateType, areaName);
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: userId,
      area_id: areaId,
      access_type: 'download',
      resource_type: 'template',
      metadata: { template_type: templateType }
    });
    
    const fileExtensions = {
      template: '.docx',
      guide: '.docx', 
      checklist: '.docx',
      practices: '.pptx'
    };
    
    const filename = `polaris_${areaId}_${templateType}${fileExtensions[templateType] || '.md'}`;
    
    res.json({
      success: true,
      data: {
        content,
        filename,
        content_type: fileExtensions[templateType] ? 'application/octet-stream' : 'text/markdown',
        generated_at: new Date().toISOString(),
        template_type: templateType,
        area_name: areaName
      }
    });
    
  } catch (error) {
    logger.error('Get template error:', error);
    next(error);
  }
});

/**
 * POST /api/knowledge-base/ai-assistance
 * Get AI-powered assistance
 */
router.post('/ai-assistance', authenticateToken, checkKnowledgeBaseAccess, validate(schemas.aiQuery), async (req, res, next) => {
  try {
    const { question, context } = req.body;
    const userId = req.user.id;
    
    // Check if user has access (paywall protection)
    const user = await User.findOne({ id: userId });
    if (!user.email?.endsWith('@polaris.example.com')) {
      return res.json({
        success: true,
        data: {
          response: "Thank you for your question. To access AI-powered assistance and get personalized guidance, please upgrade your account or contact your local agency partner. Our Knowledge Base articles and templates are available for your reference.",
          is_premium_feature: true,
          upgrade_required: true
        }
      });
    }
    
    // Generate AI response using emergent LLM integration
    const aiResponse = await generateAIResponse(question, context);
    
    // Log access
    await KnowledgeBaseAccess.logAccess({
      user_id: userId,
      area_id: context?.area_id || 'general',
      access_type: 'search',
      resource_type: 'article',
      metadata: { search_query: question }
    });
    
    res.json({
      success: true,
      data: {
        response: aiResponse,
        context_used: context || {},
        generated_at: new Date().toISOString(),
        model: 'polaris-ai-assistant'
      }
    });
    
  } catch (error) {
    logger.error('AI assistance error:', error);
    next(error);
  }
});

/**
 * GET /api/knowledge-base/contextual-cards/:areaId
 * Get contextual guidance cards
 */
router.get('/contextual-cards/:areaId', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { areaId } = req.params;
    
    if (!BUSINESS_AREAS[areaId]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    const cards = generateContextualCards(areaId);
    
    res.json({
      success: true,
      data: {
        area_id: areaId,
        area_name: BUSINESS_AREAS[areaId],
        cards
      }
    });
    
  } catch (error) {
    logger.error('Get contextual cards error:', error);
    next(error);
  }
});

/**
 * GET /api/knowledge-base/next-best-actions/:areaId
 * Get next best actions for an area
 */
router.get('/next-best-actions/:areaId', authenticateToken, checkKnowledgeBaseAccess, async (req, res, next) => {
  try {
    const { areaId } = req.params;
    
    if (!BUSINESS_AREAS[areaId]) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    const actions = generateNextBestActions(areaId);
    
    res.json({
      success: true,
      data: {
        area_id: areaId,
        area_name: BUSINESS_AREAS[areaId],
        actions
      }
    });
    
  } catch (error) {
    logger.error('Get next best actions error:', error);
    next(error);
  }
});

// Helper functions
function generateTemplateContent(areaId, templateType, areaName) {
  const templates = {
    area1: {
      template: `# ${areaName} Business Template\n\n## Business Registration Checklist\n\n- [ ] Choose business structure (LLC, Corporation, etc.)\n- [ ] Register business name\n- [ ] Obtain EIN from IRS\n- [ ] Register with state and local authorities\n- [ ] Obtain necessary licenses and permits\n\n## Required Documents\n\n1. Articles of Incorporation/Organization\n2. Operating Agreement/Bylaws\n3. Business License Application\n4. Tax Registration Forms\n\n## Next Steps\n\n1. Open business bank account\n2. Set up accounting system\n3. Obtain business insurance\n4. Create operating procedures\n\nThis template provides a comprehensive framework for ${areaName} compliance and best practices.`,
      guide: `# Complete Guide to ${areaName}\n\n## Overview\n\nThis comprehensive guide covers all aspects of ${areaName} for small and medium businesses.\n\n## Getting Started\n\n### Step 1: Assessment\n- Evaluate current state\n- Identify gaps\n- Set priorities\n\n### Step 2: Planning\n- Develop action plan\n- Allocate resources\n- Set timeline\n\n### Step 3: Implementation\n- Execute planned activities\n- Monitor progress\n- Make adjustments\n\n## Best Practices\n\n1. Regular reviews and updates\n2. Document all processes\n3. Train staff properly\n4. Maintain compliance records\n\n## Common Pitfalls to Avoid\n\n- Incomplete documentation\n- Lack of regular updates\n- Insufficient staff training\n- Poor record keeping\n\n## Resources and Tools\n\n- Template documents\n- Checklists\n- Software recommendations\n- Professional services directory\n\nThis guide serves as your complete resource for ${areaName} excellence.`
    }
  };
  
  const areaTemplates = templates[areaId] || templates.area1;
  return areaTemplates[templateType] || areaTemplates.template;
}

/**
 * Generate AI response using OpenAI API with Emergent LLM key
 */
async function generateAIResponse(question, context = {}) {
  try {
    const apiKey = process.env.EMERGENT_LLM_KEY
    
    if (!apiKey) {
      throw new Error('EMERGENT_LLM_KEY not configured')
    }

    // Create context-aware system message
    const systemMessage = `You are a professional business compliance and assessment AI assistant for the Polaris platform. 

CONTEXT: You're helping business owners with procurement readiness, compliance requirements, and business improvement strategies.

KNOWLEDGE AREAS: You have expertise in all 10 business areas:
1. Business Formation & Registration
2. Financial Operations & Management  
3. Legal & Contracting Compliance
4. Quality Management & Standards
5. Technology & Security Infrastructure
6. Human Resources & Capacity
7. Performance Tracking & Reporting
8. Risk Management & Business Continuity
9. Supply Chain Management & Vendor Relations
10. Competitive Advantage & Market Position

RESPONSE STYLE: 
- Provide concise, actionable advice (under 200 words)
- Use numbered steps when appropriate
- Focus on practical, implementable solutions
- Reference specific business areas when relevant
- Maintain a professional, supportive tone

ADDITIONAL CONTEXT: ${context.area_id ? `User is asking about ${BUSINESS_AREAS[context.area_id]}` : 'General business question'}`

    const messages = [
      { role: 'system', content: systemMessage },
      { role: 'user', content: question }
    ]

    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-4o-mini',
      messages: messages,
      max_tokens: 300,
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    
    return response.data.choices[0].message.content || "I apologize, but I'm unable to provide a response at the moment. Please try again or contact support."
    
  } catch (error) {
    logger.error('AI response generation error:', error.response?.data || error.message)
    // Return fallback response
    return "I'm experiencing technical difficulties. Please try rephrasing your question or contact our support team for assistance."
  }
}

function generateContextualCards(areaId) {
  const cardTemplates = {
    area1: [
      {
        title: 'Business Structure Setup',
        description: 'Choose the right legal structure for your business',
        action_type: 'template',
        priority: 'high',
        estimated_effort: '2-4 hours'
      },
      {
        title: 'License & Permit Checklist',
        description: 'Ensure all required licenses are obtained',
        action_type: 'checklist',
        priority: 'high',
        estimated_effort: '1-2 hours'
      },
      {
        title: 'Registration Documentation',
        description: 'Complete all necessary registration paperwork',
        action_type: 'guide',
        priority: 'medium',
        estimated_effort: '3-5 hours'
      }
    ]
  };
  
  return cardTemplates[areaId] || cardTemplates.area1;
}

function generateNextBestActions(areaId) {
  const actionTemplates = {
    area1: [
      {
        action: 'Complete Business Structure Assessment',
        description: 'Evaluate your current business structure and identify optimization opportunities',
        priority: 'high',
        estimated_time: '30 minutes',
        resources: ['Business Structure Guide', 'Legal Consultation']
      },
      {
        action: 'Update Registration Documents',
        description: 'Ensure all business registrations are current and compliant',
        priority: 'medium',
        estimated_time: '1-2 hours',
        resources: ['Registration Checklist', 'Government Websites']
      },
      {
        action: 'Review License Requirements',
        description: 'Verify all required licenses are obtained and up to date',
        priority: 'high',
        estimated_time: '45 minutes',
        resources: ['License Database', 'Professional Services']
      }
    ]
  };
  
  return actionTemplates[areaId] || actionTemplates.area1;
}

module.exports = router;