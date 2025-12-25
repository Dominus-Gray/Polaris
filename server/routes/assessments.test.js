const request = require('supertest');
const express = require('express');
const assessmentRoutes = require('./assessments');
const assessmentService = require('../services/assessmentService');

jest.mock('../services/assessmentService');
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com' };
    next();
  },
}));

const app = express();
app.use(express.json());
app.use('/api/assessment', assessmentRoutes);

describe('Assessment Routes', () => {
  describe('POST /api/assessment/tier-session', () => {
    it('should create a new tier session', async () => {
      assessmentService.createTierSession.mockReturnValue({ session_id: 'mockSessionId' });
      const response = await request(app).post('/api/assessment/tier-session').send({ area_id: 'area1', tier: 1 });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.session_id).toBe('mockSessionId');
    });
  });

  describe('POST /api/assessment/tier-session/:session_id/response', () => {
    it('should submit a response', async () => {
      assessmentService.submitResponse.mockReturnValue({ response_id: 'mockResponseId' });
      const response = await request(app).post('/api/assessment/tier-session/mockSessionId/response').send({ statement_id: 'mockStatementId', is_compliant: true });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.response_id).toBe('mockResponseId');
    });
  });

  describe('GET /api/assessment/tier-session/:session_id/progress', () => {
    it('should get session progress', async () => {
      assessmentService.getSessionProgress.mockReturnValue({ session_id: 'mockSessionId' });
      const response = await request(app).get('/api/assessment/tier-session/mockSessionId/progress');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.session_id).toBe('mockSessionId');
    });
  });

  describe('GET /api/assessment/schema/tier-based', () => {
    it('should get the tier-based schema', async () => {
      assessmentService.getTierBasedSchema.mockResolvedValue({ client_tier_access: 3 });
      const response = await request(app).get('/api/assessment/schema/tier-based');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.client_tier_access).toBe(3);
    });
  });
});
