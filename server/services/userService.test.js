const userService = require('./userService');
const User = require('../models/User');
const { AgencyLicense } = require('../models/Agency');

jest.mock('../models/User');
jest.mock('../models/Agency', () => ({
  AgencyLicense: {
    findOne: jest.fn(),
  },
}));

describe('User Service', () => {
  describe('registerUser', () => {
    it('should register a new user', async () => {
      User.findOne.mockResolvedValue(null);
      const mockSave = jest.fn().mockResolvedValue(true);
      User.mockImplementation(() => ({
        save: mockSave,
      }));

      const userData = {
        email: 'test@example.com',
        password: 'password',
        name: 'Test User',
        role: 'provider',
      };
      await userService.registerUser(userData);
      expect(mockSave).toHaveBeenCalled();
    });

    it('should throw an error if the user already exists', async () => {
      User.findOne.mockResolvedValue({ email: 'test@example.com' });
      const userData = { email: 'test@example.com' };
      await expect(userService.registerUser(userData)).rejects.toThrow('An account with this email address already exists');
    });

    it('should successfully register a client with a valid license code', async () => {
      User.findOne.mockResolvedValue(null);
      AgencyLicense.findOne.mockResolvedValue({
        license_code: '1234567890',
        status: 'active',
        expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24),
        usage_count: 0,
        usage_limit: 1,
        markAsUsed: jest.fn().mockResolvedValue(true),
      });
      const mockSave = jest.fn().mockResolvedValue(true);
      User.mockImplementation(() => ({
        id: 'mockUserId',
        save: mockSave,
      }));

      const userData = {
        email: 'client@example.com',
        password: 'password',
        name: 'Client User',
        role: 'client',
        license_code: '1234567890',
      };
      await userService.registerUser(userData);
      expect(mockSave).toHaveBeenCalled();
    });

    it('should throw an error for a client with an invalid license code', async () => {
      User.findOne.mockResolvedValue(null);
      AgencyLicense.findOne.mockResolvedValue(null);
      const userData = { role: 'client', license_code: '1234567890' };
      await expect(userService.registerUser(userData)).rejects.toThrow('Invalid or expired license code');
    });
  });

  describe('updateUserProfile', () => {
    it('should update a user profile', async () => {
      const mockUser = {
        name: 'Old Name',
        save: jest.fn().mockResolvedValue(true),
      };
      User.findOneAndUpdate.mockResolvedValue(mockUser);

      const updates = { name: 'New Name' };
      const user = await userService.updateUserProfile('mockUserId', updates);

      expect(user).toBe(mockUser);
    });

    it('should throw an error if the user is not found', async () => {
      User.findOneAndUpdate.mockResolvedValue(null);
      await expect(userService.updateUserProfile('mockUserId', {})).rejects.toThrow('User not found');
    });
  });

  describe('deleteUser', () => {
    it('should delete a user', async () => {
      const mockUser = {
        email: 'test@example.com',
        save: jest.fn().mockResolvedValue(true),
      };
      User.findOne.mockResolvedValue(mockUser);

      await userService.deleteUser('mockUserId', 'DELETE_MY_ACCOUNT');
      expect(mockUser.status).toBe('deleted');
      expect(mockUser.deleted_at).toBeInstanceOf(Date);
      expect(mockUser.save).toHaveBeenCalled();
    });

    it('should throw an error if the confirmation is incorrect', async () => {
      await expect(userService.deleteUser('mockUserId', 'wrong')).rejects.toThrow('Account deletion confirmation required');
    });

    it('should throw an error if the user is not found', async () => {
      User.findOne.mockResolvedValue(null);
      await expect(userService.deleteUser('mockUserId', 'DELETE_MY_ACCOUNT')).rejects.toThrow('User not found');
    });
  });
});
