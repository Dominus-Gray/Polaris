const authService = require('./authService');
const User = require('../models/User');
const { generateJWTToken, comparePasswords } = require('../utils/helpers');

jest.mock('../models/User');
jest.mock('../utils/helpers', () => ({
  generateJWTToken: jest.fn(),
  comparePasswords: jest.fn(),
}));

describe('Auth Service', () => {
  describe('loginUser', () => {
    it('should login a user and return a token', async () => {
      const mockUser = {
        email: 'test@example.com',
        password: 'hashedpassword',
        status: 'approved',
        comparePassword: jest.fn().mockResolvedValue(true),
        generateJWT: jest.fn().mockReturnValue('testtoken'),
        save: jest.fn().mockResolvedValue(true),
      };
      User.findOne.mockResolvedValue(mockUser);

      const { user, token } = await authService.loginUser('test@example.com', 'password');

      expect(user).toBe(mockUser);
      expect(token).toBe('testtoken');
      expect(user.last_login).toBeInstanceOf(Date);
    });

    it('should throw an error for a non-existent user', async () => {
      User.findOne.mockResolvedValue(null);
      await expect(authService.loginUser('test@example.com', 'password')).rejects.toThrow('User not found');
    });

    it('should throw an error for an incorrect password', async () => {
      const mockUser = {
        comparePassword: jest.fn().mockResolvedValue(false),
      };
      User.findOne.mockResolvedValue(mockUser);
      await expect(authService.loginUser('test@example.com', 'password')).rejects.toThrow('Incorrect password');
    });

    it('should throw an error for a non-approved user', async () => {
      const mockUser = {
        status: 'pending',
        comparePassword: jest.fn().mockResolvedValue(true),
      };
      User.findOne.mockResolvedValue(mockUser);
      await expect(authService.loginUser('test@example.com', 'password')).rejects.toThrow('Account not approved. Status: pending');
    });
  });

  describe('refreshAuthToken', () => {
    it('should refresh a user token', () => {
      const mockUser = {
        generateJWT: jest.fn().mockReturnValue('refreshedtoken'),
      };
      const token = authService.refreshAuthToken(mockUser);
      expect(token).toBe('refreshedtoken');
    });
  });
});
