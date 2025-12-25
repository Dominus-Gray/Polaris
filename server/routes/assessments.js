const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { formatResponse, formatErrorResponse } = require('../utils/helpers');
const assessmentService = require('../services/assessmentService');

router.post('/tier-session', authenticateToken, async (req, res, next) => {
  try {
    const { area_id, tier = 1 } = req.body;
    const sessionData = assessmentService.createTierSession(area_id, tier, req.user.id);
    res.json(formatResponse(true, sessionData));
  } catch (error) {
    res.status(400).json(formatErrorResponse('POL-4001', error.message));
  }
});

router.post('/tier-session/:session_id/response', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params;
    const { statement_id, is_compliant, evidence_files = [], notes = '' } = req.body;
    const responseData = assessmentService.submitResponse(session_id, req.user.id, statement_id, is_compliant, evidence_files, notes);
    res.json(formatResponse(true, responseData));
  } catch (error) {
    res.status(400).json(formatErrorResponse('POL-4001', error.message));
  }
});

router.get('/tier-session/:session_id/progress', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params;
    const progressData = assessmentService.getSessionProgress(session_id, req.user.id);
    res.json(formatResponse(true, progressData));
  } catch (error) {
    next(error);
  }
});

router.get('/schema/tier-based', authenticateToken, async (req, res, next) => {
  try {
    const assessmentSchema = await assessmentService.getTierBasedSchema(req.user.id);
    res.json(formatResponse(true, assessmentSchema));
  } catch (error) {
    next(error);
  }
});

module.exports = router;
