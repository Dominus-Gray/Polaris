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
  getPaginationMeta
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

const BUSINESS_AREAS = getBusinessAreas();

/**
 * POST /api/provider/respond-to-request
 * Submit response to service request
 */
router.post('/respond-to-request', authenticateToken, requireRole('provider'), validate(schemas.providerResponse), async (req, res, next) => {
  try {
    const { 
      request_id, 
      proposed_fee, 
      estimated_timeline, 
      proposal_note,
      availability,
      deliverables = [],
      terms_conditions = {},
      portfolio_samples = []
    } = req.body;
    
    const providerId = req.user.id;
    
    // Check if service request exists
    const serviceRequest = await ServiceRequest.findOne({ id: request_id });
    
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Service request not found',
          'The specified service request does not exist'
        )
      );
    }
    
    if (serviceRequest.status !== 'open') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Service request is not open',
          'This service request is no longer accepting responses'
        )
      );
    }
    
    // Check if provider already responded
    const existingResponse = await ProviderResponse.findOne({
      request_id,
      provider_id: providerId
    });
    
    if (existingResponse) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Response already submitted',
          'You have already responded to this service request'
        )
      );
    }
    
    // Check response limit
    const responseCount = await ProviderResponse.countDocuments({ request_id });
    if (responseCount >= 5) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Response limit reached',
          'This service request has reached the maximum number of responses'
        )
      );
    }
    
    // Create provider response
    const response = new ProviderResponse({
      id: uuidv4(),
      request_id,
      provider_id: providerId,
      proposed_fee,
      estimated_timeline,
      proposal_note,
      availability,
      deliverables: deliverables.map(d => ({
        item: d.item || d,
        description: d.description || '',
        timeline: d.timeline || ''
      })),
      terms_conditions,
      portfolio_samples,
      status: 'pending'
    });
    
    await response.save();
    
    // Update service request response count
    serviceRequest.providers_notified = Math.max(serviceRequest.providers_notified, responseCount + 1);
    await serviceRequest.save();
    
    logger.info(`Provider response submitted: ${response.id} for request ${request_id}`);
    
    res.status(201).json({
      success: true,
      message: 'Response submitted successfully',
      data: {
        response_id: response.id,
        status: 'pending',
        submitted_at: response.created_at
      }
    });
    
  } catch (error) {
    logger.error('Submit provider response error:', error);
    next(error);
  }
});

/**
 * GET /api/provider/my-responses
 * Get provider's submitted responses
 */
router.get('/my-responses', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id;
    const { page = 1, limit = 10, status = 'all' } = req.query;
    
    const query = { provider_id: providerId };
    if (status !== 'all') {
      query.status = status;
    }
    
    const total = await ProviderResponse.countDocuments(query);
    const responses = await ProviderResponse.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    const enhancedResponses = await Promise.all(
      responses.map(async (response) => {
        const serviceRequest = await ServiceRequest.findOne({ id: response.request_id });
        
        return {
          ...response.toObject(),
          service_request: serviceRequest ? {
            id: serviceRequest.id,
            title: serviceRequest.title,
            area_id: serviceRequest.area_id,
            area_name: BUSINESS_AREAS[serviceRequest.area_id],
            description: serviceRequest.description,
            budget_range: serviceRequest.budget_range,
            timeline: serviceRequest.timeline,
            status: serviceRequest.status,
            created_at: serviceRequest.created_at
          } : null
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        responses: enhancedResponses,
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get provider responses error:', error);
    next(error);
  }
});

/**
 * GET /api/provider/my-services
 * Get provider's active services/engagements
 */
router.get('/my-services', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id;
    const { page = 1, limit = 10, status = 'all' } = req.query;
    
    const query = { provider_id: providerId };
    if (status !== 'all') {
      query.status = status;
    }
    
    const total = await Engagement.countDocuments(query);
    const engagements = await Engagement.find(query)
      .sort({ updated_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    const enhancedEngagements = await Promise.all(
      engagements.map(async (engagement) => {
        const client = await User.findOne({ id: engagement.client_id }).select('name email company_name');
        const serviceRequest = await ServiceRequest.findOne({ id: engagement.service_request_id });
        
        return {
          ...engagement.toObject(),
          client_info: client ? {
            name: client.name,
            email: client.email,
            company: client.company_name
          } : null,
          service_info: serviceRequest ? {
            title: serviceRequest.title,
            area_name: BUSINESS_AREAS[serviceRequest.area_id],
            description: serviceRequest.description
          } : null
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        engagements: enhancedEngagements,
        pagination: getPaginationMeta(total, page, limit),
        summary: {
          total_engagements: total,
          active_engagements: await Engagement.countDocuments({ 
            provider_id: providerId, 
            status: { $in: ['accepted', 'in_progress'] } 
          }),
          completed_engagements: await Engagement.countDocuments({ 
            provider_id: providerId, 
            status: 'released' 
          })
        }
      }
    });
    
  } catch (error) {
    logger.error('Get provider services error:', error);
    next(error);
  }
});

/**
 * PUT /api/provider/profile/business
 * Update provider business profile
 */
router.put('/profile/business', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id;
    const { 
      business_description,
      specializations = [],
      certifications = [],
      experience_years,
      hourly_rate,
      availability_status,
      service_areas = [],
      portfolio_items = []
    } = req.body;
    
    const updateData = {
      business_description,
      specializations,
      certifications,
      'profile_data.experience_years': experience_years,
      'profile_data.hourly_rate': hourly_rate,
      'profile_data.availability_status': availability_status,
      'profile_data.service_areas': service_areas,
      'profile_data.portfolio_items': portfolio_items
    };
    
    // Remove undefined fields
    Object.keys(updateData).forEach(key => {
      if (updateData[key] === undefined) {
        delete updateData[key];
      }
    });
    
    const user = await User.findOneAndUpdate(
      { id: providerId },
      { $set: updateData },
      { new: true, runValidators: true }
    );
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Provider not found',
          'Provider account not found'
        )
      );
    }
    
    logger.info(`Provider business profile updated: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Business profile updated successfully',
      data: {
        provider: user.toSafeObject()
      }
    });
    
  } catch (error) {
    logger.error('Update provider business profile error:', error);
    next(error);
  }
});

/**
 * GET /api/provider/dashboard
 * Get provider dashboard data
 */
router.get('/dashboard', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id;
    
    // Get dashboard statistics
    const stats = {
      active_engagements: await Engagement.countDocuments({ 
        provider_id: providerId, 
        status: { $in: ['accepted', 'in_progress'] } 
      }),
      pending_responses: await ProviderResponse.countDocuments({ 
        provider_id: providerId, 
        status: 'pending' 
      }),
      completed_services: await Engagement.countDocuments({ 
        provider_id: providerId, 
        status: 'released' 
      }),
      total_earnings: 0, // TODO: Calculate from completed engagements
      avg_rating: 4.5, // TODO: Calculate actual rating
      response_rate: 85 // TODO: Calculate actual response rate
    };
    
    // Get recent opportunities
    const recentOpportunities = await ServiceRequest.find({
      status: 'open',
      providers_notified: { $lt: 5 },
      created_at: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } // Last 7 days
    })
      .sort({ created_at: -1 })
      .limit(5);
    
    // Get active engagements
    const activeEngagements = await Engagement.find({
      provider_id: providerId,
      status: { $in: ['accepted', 'in_progress', 'delivered'] }
    })
      .sort({ updated_at: -1 })
      .limit(5);
    
    const dashboardData = {
      provider: req.user.toSafeObject(),
      stats,
      recent_opportunities: recentOpportunities.map(opp => ({
        ...opp.toObject(),
        area_name: BUSINESS_AREAS[opp.area_id]
      })),
      active_engagements: activeEngagements
    };
    
    res.json({
      success: true,
      data: dashboardData
    });
    
  } catch (error) {
    logger.error('Get provider dashboard error:', error);
    next(error);
  }
});

/**
 * POST /api/provider/engagements/:engagementId/status
 * Update engagement status
 */
router.post('/engagements/:engagementId/status', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const { engagementId } = req.params;
    const { status, notes } = req.body;
    const providerId = req.user.id;
    
    const validStatuses = ['accepted', 'in_progress', 'delivered', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid status',
          `Status must be one of: ${validStatuses.join(', ')}`
        )
      );
    }
    
    const engagement = await Engagement.findOne({ 
      id: engagementId, 
      provider_id: providerId 
    });
    
    if (!engagement) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Engagement not found',
          'The specified engagement does not exist'
        )
      );
    }
    
    // Check if status transition is valid
    if (!engagement.canTransitionTo(status)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Invalid status transition',
          `Cannot transition from ${engagement.status} to ${status}`
        )
      );
    }
    
    // Update engagement status
    engagement.status = status;
    if (status === 'in_progress' && !engagement.started_at) {
      engagement.started_at = new Date();
    }
    if (status === 'delivered') {
      engagement.completed_at = new Date();
    }
    if (status === 'cancelled') {
      engagement.cancelled_at = new Date();
      engagement.cancellation_reason = notes;
    }
    
    // Add communication entry
    engagement.communications.push({
      from_user_id: providerId,
      message: notes || `Status updated to ${status}`,
      message_type: 'status_update'
    });
    
    await engagement.save();
    
    logger.info(`Engagement status updated: ${engagementId} -> ${status}`);
    
    res.json({
      success: true,
      message: 'Engagement status updated successfully',
      data: {
        engagement_id: engagementId,
        new_status: status,
        updated_at: engagement.updated_at
      }
    });
    
  } catch (error) {
    logger.error('Update engagement status error:', error);
    next(error);
  }
});

module.exports = router;