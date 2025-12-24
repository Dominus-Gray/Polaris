const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const { formatResponse, formatErrorResponse, getBusinessAreas } = require('../utils/helpers');
const aiService = require('../services/aiService');

const BUSINESS_AREAS = getBusinessAreas();

/**
 * POST /api/ai/coach/conversation
 * AI Conversational Coaching with Emergent LLM
 */
router.post('/coach/conversation', authenticateToken, async (req, res, next) => {
  try {
    const { question, context = {}, session_id } = req.body;
    const userId = req.user.id;
    
    if (!question || question.trim().length === 0) {
      return res.status(400).json(
        formatErrorResponse('POL-4003', 'Question is required')
      );
    }

    const chatSessionId = session_id || `coach-${userId}-${Date.now()}`;
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

CONTEXT: ${context.area_id ? `User is asking about ${BUSINESS_AREAS[context.area_id] || 'business development'}` : 'General business coaching'}`;

    try {
      const chat = await aiService.getAIChatInstance(chatSessionId, systemMessage, 'gpt-4o', userId);
      const aiResponse = await chat.sendMessage(question);
      
      res.json(formatResponse(true, {
        response: aiResponse,
        session_id: chatSessionId,
        context_used: context,
        generated_at: new Date().toISOString(),
        model: 'gpt-4o',
        provider: 'openai'
      }));
      
    } catch (llmError) {
      res.status(503).json(formatErrorResponse('POL-5003', 'AI service is currently unavailable. Please try again later.'));
    }
    
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/ai/coach/history/:session_id
 * Get AI coaching conversation history
 */
router.get('/coach/history/:session_id', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params;
    const userId = req.user.id;
    const history = await aiService.getChatHistory(session_id, userId);
    res.json(formatResponse(true, {
      session_id: session_id,
      conversation_history: history,
      total_interactions: history.length
    }));
  } catch (error) {
    next(error);
  }
});

module.exports = router;
