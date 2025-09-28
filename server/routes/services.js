const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { ServiceRequest, ProviderResponse, Engagement } = require('../models/ServiceRequest');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse, 
  getBusinessAreas,
  getPaginationMeta,
  paginate
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

const BUSINESS_AREAS = getBusinessAreas();

/**
 * POST /api/service-requests/professional-help
 * Create a new service request
 */
router.post('/professional-help', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const { 
      area_id, 
      service_type = 'professional_help',
      description, 
      budget_range, 
      timeline, 
      urgency = 'medium',
      location,
      requirements = [],
      tags = []
    } = req.body;
    
    const clientId = req.user.id;
    
    // Validate area_id
    if (!BUSINESS_AREAS[area_id]) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }
    
    // Generate title based on area and type
    const areaName = BUSINESS_AREAS[area_id];
    const title = `${service_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} - ${areaName}`;
    
    // Create service request
    const serviceRequest = new ServiceRequest({
      id: `req_${uuidv4()}`,
      client_id: clientId,
      area_id,
      service_type,
      title,
      description,
      budget_range,
      timeline,
      urgency,
      location,
      requirements: requirements.map(req => ({
        requirement: req.requirement || req,
        priority: req.priority || 'required'
      })),
      tags,
      status: 'open'
    });
    
    await serviceRequest.save();
    
    // Find and notify relevant providers (limit to 5)
    const providers = await User.find({
      role: 'provider',
      status: 'approved',
      specializations: { $in: [area_id, areaName] }
    }).limit(5);
    
    const providersNotified = Math.min(providers.length, 5);
    serviceRequest.providers_notified = providersNotified;
    await serviceRequest.save();
    
    // TODO: Send notifications to providers
    logger.info(`Service request created: ${serviceRequest.id}, providers notified: ${providersNotified}`);
    
    res.status(201).json({
      success: true,
      message: 'Service request created successfully',
      data: {
        request_id: serviceRequest.id,
        providers_notified: providersNotified,
        status: 'open'
      }
    });
    
  } catch (error) {
    logger.error('Create service request error:', error);
    next(error);
  }
});

/**
 * GET /api/service-requests/:requestId
 * Get service request details
 */
router.get('/:requestId', authenticateToken, async (req, res, next) => {
  try {
    const { requestId } = req.params;
    const userId = req.user.id;
    const userRole = req.user.role;
    
    const serviceRequest = await ServiceRequest.findOne({ id: requestId });
    
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Service request not found',
          'The specified service request does not exist'
        )
      );
    }
    
    // Check access permissions
    if (userRole === 'client' && serviceRequest.client_id !== userId) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only view your own service requests'
        )
      );
    }
    
    // Get responses count
    const responsesCount = await ProviderResponse.countDocuments({ request_id: requestId });
    
    const response = {
      ...serviceRequest.toObject(),
      area_name: BUSINESS_AREAS[serviceRequest.area_id],
      provider_responses: [],
      responses_count: responsesCount,
      response_limit_reached: responsesCount >= 5
    };
    
    res.json({
      success: true,
      data: response
    });
    
  } catch (error) {
    logger.error('Get service request error:', error);
    next(error);
  }
});

/**
 * GET /api/service-requests/:requestId/responses
 * Get responses for a service request
 */
router.get('/:requestId/responses', authenticateToken, async (req, res, next) => {
  try {
    const { requestId } = req.params;
    const userId = req.user.id;
    const userRole = req.user.role;
    
    const serviceRequest = await ServiceRequest.findOne({ id: requestId });
    
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Service request not found',
          'The specified service request does not exist'
        )
      );
    }
    
    // Check access permissions
    if (userRole === 'client' && serviceRequest.client_id !== userId) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only view responses to your own service requests'
        )
      );
    }
    
    // Get responses with provider details
    const responses = await ProviderResponse.find({ request_id: requestId })
      .sort({ created_at: 1 });
    
    const enrichedResponses = await Promise.all(
      responses.map(async (response) => {
        const provider = await User.findOne({ id: response.provider_id }).select('-password -__v');
        return {
          ...response.toObject(),
          provider: provider ? provider.toSafeObject() : null
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        responses: enrichedResponses,
        total_responses: enrichedResponses.length,
        response_limit_reached: enrichedResponses.length >= 5
      }
    });
    
  } catch (error) {
    logger.error('Get service request responses error:', error);
    next(error);
  }
});

/**
 * GET /api/service-requests/:requestId/responses/enhanced
 * Get enhanced responses for a service request
 */
router.get('/:requestId/responses/enhanced', authenticateToken, async (req, res, next) => {
  try {
    const { requestId } = req.params;
    const userId = req.user.id;
    const userRole = req.user.role;
    
    const serviceRequest = await ServiceRequest.findOne({ id: requestId });
    
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Service request not found',
          'The specified service request does not exist'
        )
      );
    }
    
    // Check access permissions
    if (userRole === 'client' && serviceRequest.client_id !== userId) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'You can only view responses to your own service requests'
        )
      );
    }
    
    // Get responses with enhanced provider details
    const responses = await ProviderResponse.find({ request_id: requestId })
      .sort({ created_at: 1 });
    
    const enhancedResponses = await Promise.all(
      responses.map(async (response) => {
        const provider = await User.findOne({ id: response.provider_id }).select('-password -__v');
        
        return {
          id: response.id,
          provider_id: response.provider_id,
          provider_name: provider?.name || 'Unknown Provider',
          provider_email: provider?.email || '',
          provider_company: provider?.company_name || '',
          provider_rating: 4.5, // TODO: Calculate actual rating
          proposed_fee: response.proposed_fee,
          estimated_timeline: response.estimated_timeline,
          proposal_note: response.proposal_note,
          availability: response.availability,
          status: response.status,
          created_at: response.created_at,
          deliverables: response.deliverables || [],
          portfolio_samples: response.portfolio_samples || []
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        request_id: requestId,
        responses: enhancedResponses,
        total_responses: enhancedResponses.length,
        response_limit_reached: enhancedResponses.length >= 5,
        request_status: serviceRequest.status
      }
    });
    
  } catch (error) {
    logger.error('Get enhanced service request responses error:', error);
    next(error);
  }
});

/**
 * GET /api/service-requests/client/my-requests
 * Get client's service requests
 */
router.get('/client/my-requests', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const clientId = req.user.id;
    const { page = 1, limit = 10, status = 'all' } = req.query;
    
    const query = { client_id: clientId };
    if (status !== 'all') {
      query.status = status;
    }
    
    const total = await ServiceRequest.countDocuments(query);
    const requests = await ServiceRequest.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    const enhancedRequests = await Promise.all(
      requests.map(async (request) => {
        const responsesCount = await ProviderResponse.countDocuments({ request_id: request.id });
        
        return {
          ...request.toObject(),
          area_name: BUSINESS_AREAS[request.area_id],
          responses_count: responsesCount,
          response_limit_reached: responsesCount >= 5
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        requests: enhancedRequests,
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get client service requests error:', error);
    next(error);
  }
});

/**
 * GET /api/service-requests/provider/opportunities
 * Get available opportunities for providers
 */
router.get('/provider/opportunities', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id;
    const { page = 1, limit = 10, area_id, budget_range } = req.query;
    
    const query = { 
      status: 'open',
      providers_notified: { $lt: 5 } // Still accepting responses
    };
    
    if (area_id) {
      query.area_id = area_id;
    }
    
    if (budget_range) {
      query.budget_range = budget_range;
    }
    
    // Exclude requests where provider already responded
    const existingResponses = await ProviderResponse.find({ provider_id: providerId }).distinct('request_id');
    query.id = { $nin: existingResponses };
    
    const total = await ServiceRequest.countDocuments(query);
    const opportunities = await ServiceRequest.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    const enhancedOpportunities = opportunities.map(opp => ({
      ...opp.toObject(),
      area_name: BUSINESS_AREAS[opp.area_id],
      time_posted: opp.created_at,
      can_respond: opp.providers_notified < 5
    }));
    
    res.json({
      success: true,
      data: {
        opportunities: enhancedOpportunities,
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get provider opportunities error:', error);
    next(error);
  }
});

module.exports = router;