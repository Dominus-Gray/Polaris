const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../middleware/auth');
const { formatResponse, formatErrorResponse } = require('../utils/helpers');
const serviceRequestService = require('../services/serviceRequestService');

router.post('/professional-help', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const serviceRequest = await serviceRequestService.createServiceRequest(req.user.id, req.body);
    res.json(formatResponse(true, serviceRequest));
  } catch (error) {
    next(error);
  }
});

router.post('/respond-to-request', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const providerResponse = await serviceRequestService.respondToRequest(req.user.id, req.body);
    res.json(formatResponse(true, providerResponse));
  } catch (error) {
    if (error.message === 'Service request not found or no longer accepting responses') {
      return res.status(404).json(formatErrorResponse('POL-4001', error.message));
    }
    if (error.message === 'You have already responded to this service request') {
      return res.status(400).json(formatErrorResponse('POL-4002', error.message));
    }
    next(error);
  }
});

router.get('/my-requests', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const serviceRequests = await serviceRequestService.getClientRequests(req.user.id);
    res.json(formatResponse(true, serviceRequests));
  } catch (error) {
    next(error);
  }
});

router.get('/opportunities', authenticateToken, requireRole('provider'), async (req, res, next) => {
  try {
    const opportunities = await serviceRequestService.getProviderOpportunities(req.user.id);
    res.json(formatResponse(true, opportunities));
  } catch (error) {
    next(error);
  }
});

module.exports = router;
