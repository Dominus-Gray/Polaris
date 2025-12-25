const request = require('supertest');
const express = require('express');
const serviceRequestRoutes = require('./serviceRequests');
const serviceRequestService = require('../services/serviceRequestService');

jest.mock('../services/serviceRequestService');
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com' };
    next();
  },
  requireRole: () => (req, res, next) => next(),
}));

const app = express();
app.use(express.json());
app.use('/api/service-requests', serviceRequestRoutes);

describe('Service Request Routes', () => {
  describe('POST /api/service-requests/professional-help', () => {
    it('should create a new service request', async () => {
      serviceRequestService.createServiceRequest.mockResolvedValue({ id: 'mockRequestId' });
      const response = await request(app).post('/api/service-requests/professional-help').send({ title: 'Test Request' });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe('mockRequestId');
    });
  });

  describe('POST /api/service-requests/respond-to-request', () => {
    it('should allow a provider to respond to a request', async () => {
      serviceRequestService.respondToRequest.mockResolvedValue({ id: 'mockResponseId' });
      const response = await request(app).post('/api/service-requests/respond-to-request').send({ request_id: 'mockRequestId' });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe('mockResponseId');
    });
  });

  describe('GET /api/service-requests/my-requests', () => {
    it('should get a client\'s service requests', async () => {
      serviceRequestService.getClientRequests.mockResolvedValue([]);
      const response = await request(app).get('/api/service-requests/my-requests');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeInstanceOf(Array);
    });
  });

  describe('GET /api/service-requests/opportunities', () => {
    it('should get a provider\'s opportunities', async () => {
      serviceRequestService.getProviderOpportunities.mockResolvedValue([]);
      const response = await request(app).get('/api/service-requests/opportunities');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeInstanceOf(Array);
    });
  });
});
