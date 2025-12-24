const express = require('express')
const { v4: uuidv4 } = require('uuid')
const axios = require('axios')
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse, getBusinessAreas } = require('../utils/helpers')
const logger = require('../utils/logger').logger

// Models
const { AIGeneratedContent } = require('../models/KnowledgeBase')
const { AssessmentSession, TierAssessmentSession } = require('../models/Assessment')
const { ServiceRequest } = require('../models/ServiceRequest')
const User = require('../models/User')

const router = express.Router()
const BUSINESS_AREAS = getBusinessAreas()

/**
 * Get AI Chat Instance
 * Manages chat history for conversational context using the database
 */
async function getAIChatInstance(sessionId, systemMessage, model, userId) {
  const history = await AIGeneratedContent.find({
    user_id: userId,
    session_id: sessionId,
    content_type: 'response'
  }).sort({ created_at: 1 });

  const chatHistory = history.map(item => [
    { role: 'user', content: item.prompt },
    { role: 'assistant', content: item.generated_content }
  ]).flat();

  return {
    model: model,
    history: [{ role: 'system', content: systemMessage }, ...chatHistory],
    send_message: async function(userMessage) {
      this.history.push({ role: 'user', content: userMessage });

      const aiResponse = await callOpenAI(this.history, this.model);
      this.history.push({ role: 'assistant', content: aiResponse });

      // Save to database
      const aiContent = new AIGeneratedContent({
        user_id: userId,
        content_type: 'response',
        area_id: 'general',
        prompt: userMessage,
        generated_content: aiResponse,
        generation_model: model,
        session_id: sessionId
      });
      await aiContent.save();

      return aiResponse;
    }
  };
}

/**
 * Call OpenAI API directly with emergent key
 */
async function callOpenAI(messages, model = 'gpt-4o-mini') {
  try {
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: model,
      messages: messages,
      max_tokens: 500,
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.EMERGENT_LLM_KEY}`,
        'Content-Type': 'application/json'
      }
    })
    
    return response.data.choices[0].message.content
  } catch (error) {
    logger.error('OpenAI API error:', error.response?.data || error.message)
    throw error
  }
}
    
    const responses = {
      coaching: {
        'how do i start': 'To start your procurement readiness assessment, I recommend beginning with Area 1: Business Formation & Registration. This foundational area ensures your business structure is properly established. Follow these steps: 1) Review your current business registration status, 2) Complete the tier-based assessment for this area, 3) Address any gaps identified, 4) Move to the next area systematically.',
/**
 * POST /api/ai/coach/conversation
 * AI Conversational Coaching with Emergent LLM
 */
router.post('/coach/conversation', authenticateToken, async (req, res, next) => {
  try {
    const { question, context = {}, session_id } = req.body
    const userId = req.user.id
    
    if (!question || question.trim().length === 0) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Question is required',
          'Please provide a question for AI assistance'
        )
      )
    }

    // Create session ID if not provided
    const chatSessionId = session_id || `coach-${userId}-${Date.now()}`
    
    // System message for business coaching
    const systemMessage = `You are a professional business coach and compliance expert for the Polaris platform specializing in procurement readiness and business development.

EXPERTISE: You help small and medium businesses improve their:
- Business formation and registration
- Financial operations and compliance
- Legal and contracting requirements
- Quality management systems
- Technology and security infrastructure
- Human resources and capacity building
- Performance tracking and reporting
- Risk management and business continuity
- Supply chain and vendor relations
- Competitive advantage and market positioning

RESPONSE STYLE:
- Provide actionable, specific advice (under 250 words)
- Use numbered steps for complex processes
- Reference relevant business areas when applicable
- Suggest next steps and resources
- Maintain an encouraging, professional tone
- Focus on practical implementation

CONTEXT: ${context.area_id ? `User is asking about ${BUSINESS_AREAS[context.area_id] || 'business development'}` : 'General business coaching'}`

    try {
      // Get AI chat instance
      const chat = await getAIChatInstance(chatSessionId, systemMessage, 'gpt-4o', userId)
      
      // Get AI response
      const aiResponse = await chat.send_message(question)
      
      // Log the interaction for analytics
      logger.info(`AI coaching conversation: User ${userId}, Session: ${chatSessionId}`)
      
      res.json({
        success: true,
        data: {
          response: aiResponse,
          session_id: chatSessionId,
          context_used: context,
          generated_at: new Date().toISOString(),
          model: 'gpt-4o',
          provider: 'openai'
        }
      })
      
    } catch (llmError) {
      logger.error('LLM integration error:', llmError)
      
      // Fallback response with proper error status
      res.status(503).json({
        success: false,
        error: {
          code: 'POL-5003',
          message: 'AI service is currently unavailable. Please try again later.',
          details: `LLM integration error for session ${chatSessionId}`
        },
        data: {
          response: "I'm here to help with your business questions. Due to high demand, I'm currently operating in limited mode. Please try rephrasing your question or contact our support team for direct assistance.",
          session_id: chatSessionId,
          fallback: true,
          generated_at: new Date().toISOString()
        }
      })
    }
    
  } catch (error) {
    logger.error('AI coaching conversation error:', error)
    next(error)
  }
})

/**
 * GET /api/ai/coach/history/:session_id
 * Get AI coaching conversation history
 */
router.get('/coach/history/:session_id', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params;
    const userId = req.user.id;

    const conversations = await AIGeneratedContent.find({
      user_id: userId,
      session_id: session_id,
      content_type: 'response'
    }).sort({ created_at: 1 });

    const history = conversations.map(conv => ({
      id: conv.id,
      question: conv.prompt,
      response: conv.generated_content,
      timestamp: conv.created_at,
      area_id: conv.area_id
    }));

    res.json({
      success: true,
      data: {
        session_id: session_id,
        conversation_history: history,
        total_interactions: history.length
      }
    });

  } catch (error) {
    logger.error('Get AI coach history error:', error);
    next(error);
  }
});
        provider: [
          {
            title: 'Update Your Profile',
            description: 'Complete your provider profile to attract more clients',
            priority: 'high',
            estimated_time: '20 minutes',
            action_items: ['Add specializations', 'Upload portfolio', 'Set availability status']
          }
        ],
        agency: [
          {
            title: 'Generate License Codes',
            description: 'Create license codes for your client onboarding',
            priority: 'high',
            estimated_time: '5 minutes',
            action_items: ['Access license management', 'Generate codes', 'Distribute to clients']
          },
          {
            title: 'Configure Tier Access',
            description: 'Set up tier-based assessment access for your clients',
            priority: 'medium',
            estimated_time: '15 minutes',
            action_items: ['Review tier settings', 'Adjust access levels', 'Update pricing']
          }
        ],
        navigator: [
          {
            title: 'Review Pending Agencies',
            description: 'Process agency approval requests in your queue',
            priority: 'high',
            estimated_time: '10 minutes',
            action_items: ['Check applications', 'Verify documentation', 'Approve or request updates']
          },
          {
            title: 'Analyze System Metrics',
            description: 'Review platform usage and performance metrics',
            priority: 'medium',
            estimated_time: '20 minutes',
            action_items: ['Check analytics dashboard', 'Review user activity', 'Identify trends']
          }
        ]
      },
      predictive: {
        success_probability: Math.random() * 10, // 0-10 scale
        risk_level: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
        metrics: {
          assessment_completion_rate: Math.random() * 100,
          knowledge_base_engagement: Math.random() * 100,
          service_request_success_rate: Math.random() * 100
        },
        predictions: [
          'Based on your assessment patterns, you have a strong foundation in business formation',
          'Your engagement with financial management resources suggests good compliance awareness',
          'Technology infrastructure appears to be an area for potential improvement'
        ],
        recommendations: [
          'Focus on completing assessments in your weaker areas first',
          'Consider engaging professional services for complex compliance requirements',
          'Regular review and updates of your business processes are recommended'
        ]
      }
    };
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    return responses;
  }
}

/**
 * POST /api/ai/predictive-analytics
 * AI-powered predictive analytics
 */
router.post('/predictive-analytics', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { analysis_type = 'success_prediction', data_points = {} } = req.body;
    
    // Get user's historical data for analysis
    const userAssessments = await AssessmentSession.find({ user_id: userId });
    const userTierAssessments = await TierAssessmentSession.find({ user_id: userId });
    const userServiceRequests = await ServiceRequest.find({ client_id: userId });
    
    // Generate predictive analysis
    const aiResponses = await AIService.generateResponse('predictive_analysis', {
      user_id: userId,
      assessments: userAssessments.length,
      tier_assessments: userTierAssessments.length,
      service_requests: userServiceRequests.length,
      analysis_type
    });
    
    const analysis = {
      analysis_type,
      user_id: userId,
      generated_at: new Date(),
      ...aiResponses.predictive,
      data_sources: {
        assessments_analyzed: userAssessments.length,
        tier_assessments_analyzed: userTierAssessments.length,
        service_requests_analyzed: userServiceRequests.length
      }
    };
    
    // Save analysis
    const aiContent = new AIGeneratedContent({
      user_id: userId,
      content_type: 'recommendation',
      area_id: 'analytics',
      prompt: `Predictive analysis: ${analysis_type}`,
      generated_content: JSON.stringify(analysis),
      generation_model: 'polaris-predictive-ai'
    });
    
    await aiContent.save();
    
    logger.info(`Predictive analysis generated for user ${userId}`);
    
    res.json({
      success: true,
      data: analysis
    });
    
  } catch (error) {
    logger.error('AI predictive analytics error:', error);
    next(error);
  }
});

/**
 * GET /api/ai/recommendations/:role
 * Get AI-powered recommendations based on user role
 */
router.get('/recommendations/:role', authenticateToken, async (req, res, next) => {
  try {
    const { role } = req.params;
    const userId = req.user.id;
    
    const validRoles = ['client', 'provider', 'agency', 'navigator'];
    if (!validRoles.includes(role)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid role',
          `Role must be one of: ${validRoles.join(', ')}`
        )
      );
    }
    
    // Generate role-specific recommendations
    const aiResponses = await AIService.generateResponse('recommendations', { role, user_id: userId });
    const recommendations = aiResponses.recommendations[role] || [];
    
    // Save recommendations
    const aiContent = new AIGeneratedContent({
      user_id: userId,
      content_type: 'recommendation',
      area_id: 'general',
      prompt: `Role-based recommendations for ${role}`,
      generated_content: JSON.stringify(recommendations),
      generation_model: 'polaris-recommendation-ai'
    });
    
    await aiContent.save();
    
    res.json({
      success: true,
      data: {
        role,
        recommendations,
        generated_at: new Date(),
        total_recommendations: recommendations.length
      }
    });
    
  } catch (error) {
    logger.error('AI recommendations error:', error);
    next(error);
  }
});

/**
 * POST /api/ai/content/generate
 * Generate AI content for specific purposes
 */
router.post('/content/generate', authenticateToken, async (req, res, next) => {
  try {
    const { 
      content_type, 
      area_id, 
      template_type, 
      custom_prompt,
      parameters = {}
    } = req.body;
    
    const userId = req.user.id;
    
    if (!content_type || !area_id) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Content type and area ID are required',
          'Please specify content_type and area_id'
        )
      );
    }
    
    const validContentTypes = ['template', 'guide', 'checklist', 'recommendation', 'summary'];
    if (!validContentTypes.includes(content_type)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid content type',
          `Content type must be one of: ${validContentTypes.join(', ')}`
        )
      );
    }
    
    if (!BUSINESS_AREAS[area_id]) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    // Generate content based on type and area
    const areaName = BUSINESS_AREAS[area_id];
    const prompt = custom_prompt || `Generate ${content_type} for ${areaName}`;
    
    // Mock content generation (replace with actual AI service)
    let generatedContent = '';
    
    switch (content_type) {
      case 'template':
        generatedContent = `# ${areaName} ${template_type || 'Template'}\n\nThis template provides a comprehensive framework for ${areaName.toLowerCase()} compliance and best practices.\n\n## Key Components\n\n1. Assessment checklist\n2. Implementation guide\n3. Compliance tracking\n4. Review procedures\n\n## Instructions\n\n1. Complete each section thoroughly\n2. Gather required documentation\n3. Review with stakeholders\n4. Implement recommendations\n\nGenerated on: ${new Date().toLocaleDateString()}`;
        break;
      case 'guide':
        generatedContent = `# Complete Guide to ${areaName}\n\nThis comprehensive guide covers all essential aspects of ${areaName.toLowerCase()} for your business.\n\n## Getting Started\n\n### Step 1: Assessment\n- Evaluate your current state\n- Identify gaps and opportunities\n- Set realistic goals\n\n### Step 2: Planning\n- Develop action plan\n- Allocate resources\n- Set timeline\n\n### Step 3: Implementation\n- Execute planned activities\n- Monitor progress\n- Make adjustments as needed\n\n## Best Practices\n\n- Regular reviews and updates\n- Document all processes\n- Train staff appropriately\n- Maintain compliance records`;
        break;
      case 'checklist':
        generatedContent = `# ${areaName} Checklist\n\n## Essential Requirements\n\n- [ ] Initial assessment completed\n- [ ] Documentation gathered\n- [ ] Compliance review conducted\n- [ ] Stakeholder approval obtained\n\n## Implementation Steps\n\n- [ ] Action plan developed\n- [ ] Resources allocated\n- [ ] Timeline established\n- [ ] Progress tracking system set up\n\n## Ongoing Maintenance\n\n- [ ] Regular reviews scheduled\n- [ ] Update procedures established\n- [ ] Staff training completed\n- [ ] Record keeping system active`;
        break;
      default:
        generatedContent = `AI-generated content for ${areaName} - ${content_type}. This content has been customized based on your business needs and current assessment status.`;
    }
    
    // Save generated content
    const aiContent = new AIGeneratedContent({
      user_id: userId,
      content_type,
      area_id,
      template_type,
      prompt,
      generated_content: generatedContent,
      generation_model: 'polaris-content-ai',
      generation_parameters: parameters
    });
    
    await aiContent.save();
    
    logger.info(`AI content generated: ${content_type} for area ${area_id} by user ${userId}`);
    
    res.json({
      success: true,
      data: {
        content_id: aiContent.id,
        content_type,
        area_id,
        area_name: areaName,
        generated_content: generatedContent,
        generated_at: aiContent.created_at,
        model: aiContent.generation_model
      }
    });
    
  } catch (error) {
    logger.error('AI content generation error:', error);
    next(error);
  }
});

/**
 * GET /api/ai/content/history
 * Get user's AI-generated content history
 */
router.get('/content/history', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { content_type, area_id, page = 1, limit = 20 } = req.query;
    
    const query = { user_id: userId };
    if (content_type) query.content_type = content_type;
    if (area_id) query.area_id = area_id;
    
    const total = await AIGeneratedContent.countDocuments(query);
    const content = await AIGeneratedContent.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .select('-generated_content'); // Exclude full content for list view
    
    const history = content.map(item => ({
      id: item.id,
      content_type: item.content_type,
      area_id: item.area_id,
      area_name: BUSINESS_AREAS[item.area_id] || item.area_id,
      template_type: item.template_type,
      prompt: item.prompt,
      created_at: item.created_at,
      usage_count: item.usage_count,
      model: item.generation_model
    }));
    
    res.json({
      success: true,
      data: {
        content_history: history,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          totalPages: Math.ceil(total / limit)
        },
        filters: {
          content_type: content_type || 'all',
          area_id: area_id || 'all'
        }
      }
    });
    
  } catch (error) {
    logger.error('Get AI content history error:', error);
    next(error);
  }
});

/**
 * GET /api/ai/content/:contentId
 * Get specific AI-generated content
 */
router.get('/content/:contentId', authenticateToken, async (req, res, next) => {
  try {
    const { contentId } = req.params;
    const userId = req.user.id;
    
    const content = await AIGeneratedContent.findOne({
      id: contentId,
      user_id: userId
    });
    
    if (!content) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Content not found',
          'The specified AI-generated content does not exist'
        )
      );
    }
    
    // Increment usage count
    await content.incrementUsage();
    
    res.json({
      success: true,
      data: {
        id: content.id,
        content_type: content.content_type,
        area_id: content.area_id,
        area_name: BUSINESS_AREAS[content.area_id] || content.area_id,
        template_type: content.template_type,
        prompt: content.prompt,
        generated_content: content.generated_content,
        content_format: content.content_format,
        created_at: content.created_at,
        usage_count: content.usage_count,
        model: content.generation_model,
        quality_score: content.quality_score
      }
    });
    
  } catch (error) {
    logger.error('Get AI content error:', error);
    next(error);
  }
});

module.exports = router;