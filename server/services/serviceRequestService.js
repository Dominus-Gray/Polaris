const { v4: uuidv4 } = require('uuid');
const { ServiceRequest, ProviderResponse } = require('../models/ServiceRequest');
const User = require('../models/User');
const { logger } = require('../utils/logger');

const createServiceRequest = async (clientId, requestData) => {
  const { area_id, title, description, budget_range, timeline, priority, location, requirements } = requestData;

  const serviceRequest = new ServiceRequest({
    id: uuidv4(),
    client_id: clientId,
    area_id,
    title,
    description: description + (requirements ? `\n\nSpecific Requirements:\n${requirements}` : ''),
    budget_range,
    timeline,
    priority: priority || 'medium',
    location: location || '',
    status: 'open',
  });

  await serviceRequest.save();

  const qualifiedProviders = await User.find({
    role: 'provider',
    status: 'approved',
    specializations: { $in: [area_id] }
  }).limit(5);

  const notificationPromises = qualifiedProviders.map(async (provider) => {
    logger.info(`Notified provider ${provider.email} about service request ${serviceRequest.id}`);
    // In a real application, this would create a notification record and send an email/push notification
    return provider.id;
  });

  const notifiedProviders = await Promise.all(notificationPromises);
  serviceRequest.providers_notified = notifiedProviders.length;
  await serviceRequest.save();

  return serviceRequest;
};

const respondToRequest = async (providerId, responseData) => {
  const { request_id, proposed_fee, estimated_timeline, proposal_note, attachments } = responseData;

  const serviceRequest = await ServiceRequest.findOne({ id: request_id, status: 'open' });
  if (!serviceRequest) {
    throw new Error('Service request not found or no longer accepting responses');
  }

  const existingResponse = await ProviderResponse.findOne({ request_id, provider_id: providerId });
  if (existingResponse) {
    throw new Error('You have already responded to this service request');
  }

  const providerResponse = new ProviderResponse({
    id: uuidv4(),
    request_id,
    provider_id: providerId,
    proposed_fee: parseFloat(proposed_fee),
    estimated_timeline,
    proposal_note,
    attachments: attachments || [],
    status: 'submitted',
  });

  await providerResponse.save();

  const responseCount = await ProviderResponse.countDocuments({ request_id });
  serviceRequest.response_limit_reached = responseCount >= 5;
  await serviceRequest.save();

  return providerResponse;
};

const getClientRequests = async (clientId) => {
  const serviceRequests = await ServiceRequest.find({ client_id: clientId })
    .sort({ created_at: -1 })
    .limit(20);

  return Promise.all(
    serviceRequests.map(async (request) => {
      const responseCount = await ProviderResponse.countDocuments({ request_id: request.id });
      return {
        ...request.toObject(),
        provider_responses_count: responseCount,
      };
    })
  );
};

const getProviderOpportunities = async (providerId) => {
  const opportunities = await ServiceRequest.find({
    status: 'open',
    response_limit_reached: false,
  }).sort({ created_at: -1 });

  const filteredOpportunities = [];
  for (const opportunity of opportunities) {
    const hasResponded = await ProviderResponse.findOne({
      request_id: opportunity.id,
      provider_id: providerId,
    });

    if (!hasResponded) {
      const client = await User.findOne({ id: opportunity.client_id });
      filteredOpportunities.push({
        ...opportunity.toObject(),
        client_info: {
          name: client?.name || 'Business Client',
          company: client?.company_name || 'Business',
          location: opportunity.location || 'Local Area',
        },
      });
    }
  }

  return filteredOpportunities;
};

module.exports = {
  createServiceRequest,
  respondToRequest,
  getClientRequests,
  getProviderOpportunities,
};
