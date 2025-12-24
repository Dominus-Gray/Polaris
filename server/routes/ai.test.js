const request = require('supertest');
const express = require('express');
const aiRoutes = require('./ai');
const aiService = require('../services/aiService');

// Mock the auth middleware
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com' };
    next();
  },
}));

// Mock the aiService
jest.mock('../services/aiService', () => ({
  getAIChatInstance: jest.fn().mockResolvedValue({
    sendMessage: jest.fn().mockResolvedValue('This is a test response from the AI.'),
  }),
}));

const app = express();
app.use(express.json());
app.use('/api/ai', aiRoutes);

describe('AI Routes', () => {
  describe('POST /api/ai/coach/conversation', () => {
    it('should return a response from the AI coach', async () => {
      const response = await request(app)
        .post('/api/ai/coach/conversation')
        .send({ question: 'What is procurement?' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.response).toBe('This is a test response from the AI.');
    });

    it('should handle errors from the aiService', async () => {
      aiService.getAIChatInstance.mockImplementation(() => {
        throw new Error('Service error');
      });

      const response = await request(app)
        .post('/api/ai/coach/conversation')
        .send({ question: 'What is procurement?' });
      expect(response.status).toBe(503);
    });
  });
});
