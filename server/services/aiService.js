const axios = require('axios');
const { AIGeneratedContent } = require('../models/KnowledgeBase');
const { logger } = require('../utils/logger');

const callOpenAI = async (messages, model = 'gpt-4o-mini') => {
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
    });
    return response.data.choices[0].message.content;
  } catch (error) {
    logger.error('OpenAI API error:', error.response?.data || error.message);
    throw error;
  }
};

const getAIChatInstance = async (sessionId, systemMessage, model, userId) => {
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
    sendMessage: async function(userMessage) {
      this.history.push({ role: 'user', content: userMessage });

      const aiResponse = await callOpenAI(this.history, this.model);
      this.history.push({ role: 'assistant', content: aiResponse });

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
};

const getChatHistory = async (sessionId, userId) => {
  const conversations = await AIGeneratedContent.find({
    user_id: userId,
    session_id: sessionId,
    content_type: 'response'
  }).sort({ created_at: 1 });

  return conversations.map(conv => ({
    id: conv.id,
    question: conv.prompt,
    response: conv.generated_content,
    timestamp: conv.created_at,
    area_id: conv.area_id
  }));
};

module.exports = {
  getAIChatInstance,
  getChatHistory
};
