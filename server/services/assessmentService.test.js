const assessmentService = require('./assessmentService');
const User = require('../models/User');
const { AgencyTierConfiguration } = require('../models/Agency');

jest.mock('../models/User');
jest.mock('../models/Agency', () => ({
  AgencyTierConfiguration: {
    findOne: jest.fn(),
  },
}));

describe('Assessment Service', () => {
  describe('createTierSession', () => {
    it('should create a new tier session', () => {
      const session = assessmentService.createTierSession('area1', 1, 'mockUserId');
      expect(session.area_id).toBe('area1');
      expect(session.tier).toBe(1);
      expect(session.user_id).toBe('mockUserId');
    });

    it('should throw an error for an invalid area_id', () => {
      expect(() => assessmentService.createTierSession('invalid', 1, 'mockUserId')).toThrow('Invalid area_id');
    });

    it('should throw an error for an invalid tier', () => {
      expect(() => assessmentService.createTierSession('area1', 4, 'mockUserId')).toThrow('Invalid tier');
    });
  });

  describe('submitResponse', () => {
    it('should submit a response', () => {
      const response = assessmentService.submitResponse('mockSessionId', 'mockUserId', 'mockStatementId', true, [], '');
      expect(response.session_id).toBe('mockSessionId');
      expect(response.user_id).toBe('mockUserId');
      expect(response.statement_id).toBe('mockStatementId');
      expect(response.is_compliant).toBe(true);
    });

    it('should throw an error if required fields are missing', () => {
      expect(() => assessmentService.submitResponse('mockSessionId', 'mockUserId')).toThrow('Missing required fields');
    });
  });

  describe('getSessionProgress', () => {
    it('should get session progress', () => {
      const progress = assessmentService.getSessionProgress('mockSessionId', 'mockUserId');
      expect(progress.session_id).toBe('mockSessionId');
      expect(progress.user_id).toBe('mockUserId');
    });
  });

  describe('getTierBasedSchema', () => {
    it('should get the tier-based schema for a client', async () => {
      User.findById.mockResolvedValue({ role: 'client', email: 'test@example.com' });
      AgencyTierConfiguration.findOne.mockResolvedValue({ max_tier_access: 2 });
      const schema = await assessmentService.getTierBasedSchema('mockUserId');
      expect(schema.client_tier_access).toBe(2);
    });

    it('should get the tier-based schema for a provider', async () => {
      User.findById.mockResolvedValue({ role: 'provider' });
      const schema = await assessmentService.getTierBasedSchema('mockUserId');
      expect(schema.client_tier_access).toBe(3);
    });
  });
});
