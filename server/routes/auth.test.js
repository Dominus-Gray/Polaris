const request = require('supertest');
const express = require('express');
const authRoutes = require('./auth');
const authService = require('../services/authService');
const userService = require('../services/userService');

jest.mock('../services/authService');
jest.mock('../services/userService');
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com', toSafeObject: () => ({ id: 'mockUserId', email: 'test@example.com' }) };
    next();
  },
}));

const app = express();
app.use(express.json());
app.use('/api/auth', authRoutes);

describe('Auth Routes', () => {
  describe('POST /api/auth/register', () => {
    it('should register a new user and return a token', async () => {
      userService.registerUser.mockResolvedValue({ toSafeObject: () => ({ id: 'mockUserId' }) });
      authService.refreshAuthToken.mockReturnValue('testtoken');
      const response = await request(app).post('/api/auth/register').send({
        email: 'test@example.com',
        password: 'Password123!',
        name: 'Test User',
        role: 'provider',
      });
      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.token).toBe('testtoken');
    });

    it('should return a 400 error if validation fails', async () => {
      const response = await request(app).post('/api/auth/register').send({ email: 'test@example.com' });
      expect(response.status).toBe(400);
    });
  });

  describe('POST /api/auth/login', () => {
    it('should login a user and return a token', async () => {
      authService.loginUser.mockResolvedValue({ user: { toSafeObject: () => ({ id: 'mockUserId' }) }, token: 'testtoken' });
      const response = await request(app).post('/api/auth/login').send({ email: 'test@example.com', password: 'Password123!' });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.token).toBe('testtoken');
    });
  });

  describe('GET /api/auth/me', () => {
    it('should return the current user', async () => {
      const response = await request(app).get('/api/auth/me');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.user.id).toBe('mockUserId');
    });
  });

  describe('POST /api/auth/refresh', () => {
    it('should refresh a user token', async () => {
      authService.refreshAuthToken.mockReturnValue('refreshedtoken');
      const response = await request(app).post('/api/auth/refresh');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.token).toBe('refreshedtoken');
    });
  });

  describe('POST /api/auth/logout', () => {
    it('should logout a user', async () => {
      const response = await request(app).post('/api/auth/logout');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Logged out successfully');
    });
  });
});
