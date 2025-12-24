const request = require('supertest');
const express = require('express');
const paymentRoutes = require('./payments');
const paymentService = require('../services/paymentService');

// Mock the auth middleware
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com' };
    next();
  },
  requireRole: () => (req, res, next) => next(),
}));

// Mock the paymentService
jest.mock('../services/paymentService', () => ({
  getPackages: jest.fn().mockReturnValue([
    { id: 'knowledge_base_basic', name: 'Knowledge Base Basic Access', amount: 19.99 },
    { id: 'knowledge_base_premium', name: 'Knowledge Base Premium Access', amount: 49.99 },
  ]),
}));

const app = express();
app.use(express.json());
app.use('/api/payments', paymentRoutes);

describe('Payment Routes', () => {
  describe('GET /api/payments/packages', () => {
    it('should return a list of available service packages', async () => {
      const response = await request(app).get('/api/payments/packages');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.packages).toBeInstanceOf(Array);
      expect(response.body.data.packages.length).toBeGreaterThan(0);

      // Check for a specific package
      const kbPremium = response.body.data.packages.find(p => p.id === 'knowledge_base_premium');
      expect(kbPremium).toBeDefined();
      expect(kbPremium.name).toBe('Knowledge Base Premium Access');
      expect(kbPremium.amount).toBe(49.99);
    });

    it('should handle errors from the paymentService', async () => {
      paymentService.getPackages.mockImplementation(() => {
        throw new Error('Service error');
      });

      const response = await request(app).get('/api/payments/packages');
      expect(response.status).toBe(500);
    });
  });
});
