const express = require('express')
const router = express.Router()
const { authenticateToken, requireRole } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger
const { v4: uuidv4 } = require('uuid')

// Import models
const { ServiceRequest, ProviderResponse } = require('../models/ServiceRequest')
const User = require('../models/User')

/**
 * POST /api/service-requests/professional-help
 * Create service request with automatic provider matching
 */
router.post('/professional-help', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const {
      area_id,
      title,
      description,
      budget_range,
      timeline,
      priority = 'medium',
      location,
      requirements
    } = req.body

    const clientId = req.user.id

    // Create service request
    const serviceRequestData = {
      id: uuidv4(),
      client_id: clientId,
      area_id,
      title,
      description: description + (requirements ? `\n\nSpecific Requirements:\n${requirements}` : ''),
      budget_range,
      timeline,
      priority,
      location: location || '',
      status: 'open',
      created_at: new Date(),
      updated_at: new Date(),
      providers_notified: 0,
      response_limit_reached: false
    }

    const serviceRequest = new ServiceRequest(serviceRequestData)
    await serviceRequest.save()

    // Find and notify first 5 qualified providers
    const qualifiedProviders = await User.find({
      role: 'provider',
      status: 'approved',
      specializations: { $in: [area_id] }
    }).limit(5)

    // Create provider notifications
    const notificationPromises = qualifiedProviders.map(async (provider) => {
      try {
        // Create notification record
        const notification = {
          id: uuidv4(),
          provider_id: provider.id,
          service_request_id: serviceRequest.id,
          type: 'new_opportunity',
          title: `New Service Opportunity: ${title}`,
          message: `A new ${area_id} service opportunity is available in your area.`,
          status: 'sent',
          created_at: new Date()
        }
        
        logger.info(`Notified provider ${provider.email} about service request ${serviceRequest.id}`)
        return notification
      } catch (error) {
        logger.error(`Error notifying provider ${provider.id}:`, error)
        return null
      }
    })

    const notifications = await Promise.all(notificationPromises)
    const successfulNotifications = notifications.filter(n => n !== null)

    // Update service request with notification count
    serviceRequest.providers_notified = successfulNotifications.length
    await serviceRequest.save()

    logger.info(`Service request created: ${serviceRequest.id}, notified ${successfulNotifications.length} providers`)

    res.json({
      success: true,
      data: {
        service_request_id: serviceRequest.id,
        title: serviceRequest.title,
        area_id: serviceRequest.area_id,
        budget_range: serviceRequest.budget_range,
        timeline: serviceRequest.timeline,
        status: serviceRequest.status,
        providers_notified: successfulNotifications.length,
        created_at: serviceRequest.created_at
      }
    })

  } catch (error) {
    logger.error('Create service request error:', error)
    next(error)
  }
})

/**
 * POST /api/provider/respond-to-request
 * Provider responds to service opportunity
 */
router.post('/respond-to-request', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const {
      request_id,
      proposed_fee,
      estimated_timeline,
      proposal_note,
      attachments = []
    } = req.body

    const providerId = req.user.id

    // Verify service request exists and is open
    const serviceRequest = await ServiceRequest.findOne({ id: request_id, status: 'open' })
    if (!serviceRequest) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Service request not found or no longer accepting responses')
      )
    }

    // Check if provider already responded
    const existingResponse = await ProviderResponse.findOne({ 
      request_id, 
      provider_id: providerId 
    })
    
    if (existingResponse) {
      return res.status(400).json(
        formatErrorResponse('POL-4002', 'You have already responded to this service request')
      )
    }

    // Create provider response
    const responseData = {
      id: uuidv4(),
      request_id,
      provider_id: providerId,
      proposed_fee: parseFloat(proposed_fee),
      estimated_timeline,
      proposal_note,
      attachments,
      status: 'submitted',
      submitted_at: new Date(),
      updated_at: new Date()
    }

    const providerResponse = new ProviderResponse(responseData)
    await providerResponse.save()

    // Update service request response count
    const responseCount = await ProviderResponse.countDocuments({ request_id })
    serviceRequest.response_limit_reached = responseCount >= 5
    await serviceRequest.save()

    logger.info(`Provider response created: ${providerResponse.id} for request ${request_id}`)

    res.json({
      success: true,
      data: {
        response_id: providerResponse.id,
        request_id,
        proposed_fee: providerResponse.proposed_fee,
        estimated_timeline: providerResponse.estimated_timeline,
        status: providerResponse.status,
        submitted_at: providerResponse.submitted_at
      }
    })

  } catch (error) {
    logger.error('Provider response error:', error)
    next(error)
  }
})

/**
 * GET /api/service-requests/my-requests
 * Get client's service requests
 */
router.get('/my-requests', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const clientId = req.user.id

    const serviceRequests = await ServiceRequest.find({ client_id: clientId })
      .sort({ created_at: -1 })
      .limit(20)

    // Get response counts for each request
    const requestsWithCounts = await Promise.all(
      serviceRequests.map(async (request) => {
        const responseCount = await ProviderResponse.countDocuments({ request_id: request.id })
        return {
          ...request.toObject(),
          provider_responses_count: responseCount
        }
      })
    )

    res.json({
      success: true,
      data: requestsWithCounts
    })

  } catch (error) {
    logger.error('Get client service requests error:', error)
    next(error)
  }
})

/**
 * GET /api/service-requests/opportunities
 * Get available opportunities for providers
 */
router.get('/opportunities', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerId = req.user.id

    // Get open service requests that haven't reached response limit
    const opportunities = await ServiceRequest.find({
      status: 'open',
      response_limit_reached: false
    }).sort({ created_at: -1 })

    // Filter out requests the provider has already responded to
    const filteredOpportunities = []
    for (const opportunity of opportunities) {
      const hasResponded = await ProviderResponse.findOne({
        request_id: opportunity.id,
        provider_id: providerId
      })
      
      if (!hasResponded) {
        // Get client info
        const client = await User.findOne({ id: opportunity.client_id })
        filteredOpportunities.push({
          ...opportunity.toObject(),
          client_info: {
            name: client?.name || 'Business Client',
            company: client?.company_name || 'Business',
            location: opportunity.location || 'Local Area'
          }
        })
      }
    }

    res.json({
      success: true,
      data: filteredOpportunities
    })

  } catch (error) {
    logger.error('Get provider opportunities error:', error)
    next(error)
  }
})

module.exports = router