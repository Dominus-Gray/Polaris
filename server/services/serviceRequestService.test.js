const serviceRequestService = require('./serviceRequestService');
const { ServiceRequest, ProviderResponse } = require('../models/ServiceRequest');
const User = require('../models/User');

jest.mock('../models/ServiceRequest', () => ({
  ServiceRequest: jest.fn(),
  ProviderResponse: jest.fn(),
}));
jest.mock('../models/User');

describe('Service Request Service', () => {
  beforeEach(() => {
    ServiceRequest.findOne = jest.fn();
    ServiceRequest.find = jest.fn();
    ProviderResponse.findOne = jest.fn();
    ProviderResponse.countDocuments = jest.fn();
  });
  describe('createServiceRequest', () => {
    it('should create a new service request', async () => {
      User.find.mockReturnValue({
        limit: jest.fn().mockResolvedValue([]),
      });
      const mockSave = jest.fn().mockResolvedValue(true);
      ServiceRequest.mockImplementation(() => ({
        save: mockSave,
      }));

      const requestData = {
        area_id: 'area1',
        title: 'Test Request',
        description: 'Test Description',
      };
      await serviceRequestService.createServiceRequest('mockClientId', requestData);
      expect(mockSave).toHaveBeenCalled();
    });
  });

  describe('respondToRequest', () => {
    it('should allow a provider to respond to a request', async () => {
      ServiceRequest.findOne.mockResolvedValue({ id: 'mockRequestId', status: 'open', save: jest.fn().mockResolvedValue(true) });
      ProviderResponse.findOne.mockResolvedValue(null);
      ProviderResponse.countDocuments.mockResolvedValue(0);
      const mockSave = jest.fn().mockResolvedValue(true);
      ProviderResponse.mockImplementation(() => ({
        save: mockSave,
      }));

      const responseData = { request_id: 'mockRequestId' };
      await serviceRequestService.respondToRequest('mockProviderId', responseData);
      expect(mockSave).toHaveBeenCalled();
    });

    it('should throw an error if the request is not found', async () => {
      ServiceRequest.findOne.mockResolvedValue(null);
      await expect(serviceRequestService.respondToRequest('mockProviderId', {})).rejects.toThrow('Service request not found or no longer accepting responses');
    });

    it('should throw an error if the provider has already responded', async () => {
      ServiceRequest.findOne.mockResolvedValue({ id: 'mockRequestId', status: 'open' });
      ProviderResponse.findOne.mockResolvedValue({ id: 'mockResponseId' });
      await expect(serviceRequestService.respondToRequest('mockProviderId', { request_id: 'mockRequestId' })).rejects.toThrow('You have already responded to this service request');
    });
  });

  describe('getClientRequests', () => {
    it('should get a client\'s service requests', async () => {
      ServiceRequest.find.mockReturnValue({
        sort: jest.fn().mockReturnThis(),
        limit: jest.fn().mockResolvedValue([]),
      });
      const requests = await serviceRequestService.getClientRequests('mockClientId');
      expect(requests).toBeInstanceOf(Array);
    });
  });

  describe('getProviderOpportunities', () => {
    it('should get a provider\'s opportunities', async () => {
      ServiceRequest.find.mockReturnValue({
        sort: jest.fn().mockResolvedValue([]),
      });
      const opportunities = await serviceRequestService.getProviderOpportunities('mockProviderId');
      expect(opportunities).toBeInstanceOf(Array);
    });
  });
});
