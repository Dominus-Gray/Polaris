const request = require('supertest');
const express = require('express');
const userRoutes = require('./users');
const userService = require('../services/userService');

jest.mock('../services/userService');
jest.mock('../middleware/auth', () => ({
  authenticateToken: (req, res, next) => {
    req.user = { id: 'mockUserId', email: 'test@example.com', toSafeObject: () => ({ id: 'mockUserId', email: 'test@example.com' }) };
    next();
  },
}));

const app = express();
app.use(express.json());
app.use('/api/users', userRoutes);

describe('User Routes', () => {
  describe('GET /api/users/me', () => {
    it('should return the current user', async () => {
      const response = await request(app).get('/api/users/me');
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.user.id).toBe('mockUserId');
    });
  });

  describe('PUT /api/users/me', () => {
    it('should update a user profile', async () => {
      userService.updateUserProfile.mockResolvedValue({ toSafeObject: () => ({ id: 'mockUserId', name: 'New Name' }) });
      const response = await request(app).put('/api/users/me').send({ name: 'New Name' });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.user.name).toBe('New Name');
    });
  });

  describe('DELETE /api/users/me', () => {
    it('should delete a user', async () => {
      userService.deleteUser.mockResolvedValue(true);
      const response = await request(app).delete('/api/users/me').send({ confirmation: 'DELETE_MY_ACCOUNT' });
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Account deleted successfully');
    });
  });
});
