const { v4: uuidv4 } = require('uuid');
const {
  AssessmentSession,
  TierAssessmentSession,
  AssessmentEvidence,
  AssessmentResult
} = require('../models/Assessment');
const User = require('../models/User');
const { AgencyTierConfiguration } = require('../models/Agency');
const { getBusinessAreas, calculateAssessmentScore } = require('../utils/helpers');

const BUSINESS_AREAS = getBusinessAreas();

const createTierSession = (areaId, tier, userId) => {
  if (!BUSINESS_AREAS[areaId]) {
    throw new Error('Invalid area_id');
  }
  if (tier < 1 || tier > 3) {
    throw new Error('Invalid tier');
  }

  return {
    session_id: uuidv4(),
    user_id: userId,
    area_id: areaId,
    tier,
    status: 'active',
    current_question: 0,
    total_questions: tier * 3,
    responses: {},
    evidence_submitted: {},
  };
};

const submitResponse = (sessionId, userId, statementId, isCompliant, evidenceFiles, notes) => {
  if (!statementId || isCompliant === undefined) {
    throw new Error('Missing required fields');
  }

  return {
    response_id: uuidv4(),
    session_id: sessionId,
    user_id: userId,
    statement_id: statementId,
    is_compliant: Boolean(isCompliant),
    evidence_files: evidenceFiles,
    notes,
    submitted_at: new Date(),
    navigator_review_required: Boolean(isCompliant) && evidenceFiles.length > 0,
  };
};

const getSessionProgress = (sessionId, userId) => {
  return {
    session_id: sessionId,
    user_id: userId,
    current_question: 0,
    total_questions: 3,
    completed_questions: 0,
    responses: {},
    evidence_required: [],
    completion_percentage: 0,
  };
};

const getTierBasedSchema = async (userId) => {
  const user = await User.findById(userId);
  let clientTierAccess = 1;
  if (user.role === 'client') {
    if (user.email?.includes('@polaris.example.com')) {
      clientTierAccess = 3;
    } else {
      const agencyConfig = await AgencyTierConfiguration.findOne({ client_id: userId });
      clientTierAccess = agencyConfig?.max_tier_access || 1;
    }
  } else {
    clientTierAccess = 3;
  }

  const assessmentSchema = {
    client_tier_access: clientTierAccess,
    areas: Object.keys(BUSINESS_AREAS).map(areaId => ({
      area_id: areaId,
      area_name: BUSINESS_AREAS[areaId],
      description: '...',
      tier_available: clientTierAccess,
      sessions_completed: 0,
      latest_score: 0,
      status: 'not_started',
      last_assessment: null
    })),
  };

  return assessmentSchema;
};

module.exports = {
  createTierSession,
  submitResponse,
  getSessionProgress,
  getTierBasedSchema,
};
