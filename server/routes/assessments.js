const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { 
  AssessmentSession, 
  TierAssessmentSession, 
  AssessmentEvidence, 
  AssessmentResult 
} = require('../models/Assessment');
const User = require('../models/User');
const { AgencyTierConfiguration } = require('../models/Agency');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse, 
  getBusinessAreas,
  calculateAssessmentScore
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

// Business areas configuration
const BUSINESS_AREAS = getBusinessAreas();

// Assessment schema with tier-based questions
const ASSESSMENT_SCHEMA = {
  areas: Object.entries(BUSINESS_AREAS).map(([id, name], index) => ({
    id,
    name,
    description: getAreaDescription(id),
    order: index + 1,
    tiers: {
      tier1: generateTierQuestions(id, 1),
      tier2: generateTierQuestions(id, 2),
      tier3: generateTierQuestions(id, 3)
    }
  }))
};

/**
 * POST /api/assessment/tier-session
 * Create tier-based assessment session
 */
router.post('/tier-session', authenticateToken, async (req, res, next) => {
  try {
    const { area_id, tier = 1 } = req.body
    const userId = req.user.id

    if (!area_id || !BUSINESS_AREAS[area_id]) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Invalid area_id', 'Please provide a valid business area ID')
      )
    }

    if (tier < 1 || tier > 3) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Invalid tier', 'Tier must be between 1 and 3')
      )
    }

    // Create assessment session
    const sessionData = {
      session_id: uuidv4(),
      user_id: userId,
      area_id,
      tier,
      status: 'active',
      current_question: 0,
      total_questions: tier * 3, // Tier 1: 3, Tier 2: 6, Tier 3: 9
      responses: {},
      evidence_submitted: {},
      created_at: new Date(),
      updated_at: new Date()
    }

    // Save session (simplified for demo)
    logger.info(`Assessment session created: ${sessionData.session_id} for area ${area_id}, tier ${tier}`)

    res.json({
      success: true,
      data: sessionData
    })

  } catch (error) {
    logger.error('Create tier session error:', error)
    next(error)
  }
})

/**
 * POST /api/assessment/tier-session/:session_id/response
 * Submit response to assessment question
 */
router.post('/tier-session/:session_id/response', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params
    const { 
      statement_id, 
      is_compliant, 
      evidence_files = [],
      notes = ''
    } = req.body
    const userId = req.user.id

    if (!statement_id || is_compliant === undefined) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Missing required fields', 'statement_id and is_compliant are required')
      )
    }

    // Create response record
    const responseData = {
      response_id: uuidv4(),
      session_id,
      user_id: userId,
      statement_id,
      is_compliant: Boolean(is_compliant),
      evidence_files,
      notes,
      submitted_at: new Date()
    }

    logger.info(`Assessment response submitted: ${responseData.response_id} for session ${session_id}`)

    // If evidence files provided and compliant, prepare for navigator review
    if (is_compliant && evidence_files.length > 0) {
      logger.info(`Evidence files submitted for navigator review: ${evidence_files.length} files`)
    }

    res.json({
      success: true,
      data: {
        response_id: responseData.response_id,
        statement_id,
        is_compliant: responseData.is_compliant,
        evidence_files_count: evidence_files.length,
        submitted_at: responseData.submitted_at,
        navigator_review_required: is_compliant && evidence_files.length > 0
      }
    })

  } catch (error) {
    logger.error('Submit assessment response error:', error)
    next(error)
  }
})

/**
 * GET /api/assessment/tier-session/:session_id/progress
 * Get assessment session progress
 */
router.get('/tier-session/:session_id/progress', authenticateToken, async (req, res, next) => {
  try {
    const { session_id } = req.params
    const userId = req.user.id

    // Mock progress data
    const progressData = {
      session_id,
      user_id: userId,
      current_question: 0,
      total_questions: 3,
      completed_questions: 0,
      responses: {},
      evidence_required: [],
      completion_percentage: 0,
      last_updated: new Date()
    }

    res.json({
      success: true,
      data: progressData
    })

  } catch (error) {
    logger.error('Get session progress error:', error)
    next(error)
  }
})

/**
 * GET /api/assessment/schema/tier-based
 * Get tier-based assessment schema with client access levels
 */
router.get('/schema/tier-based', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id
    const userRole = req.user.role

    // Get client tier access (agencies set this, default to tier 1)
    let clientTierAccess = 1
    if (userRole === 'client') {
      // For QA users, provide full tier 3 access
      if (req.user.email?.includes('@polaris.example.com')) {
        clientTierAccess = 3
      } else {
        // Get from agency configuration
        const agencyConfig = await AgencyTierConfiguration.findOne({ client_id: userId })
        clientTierAccess = agencyConfig?.max_tier_access || 1
      }
    } else {
      // Providers, agencies, navigators get full access
      clientTierAccess = 3
    }

    // Build comprehensive schema for all 10 areas
    const assessmentSchema = {
      client_tier_access: clientTierAccess,
      areas: [
        {
          area_id: 'area1',
          area_name: 'Business Formation & Registration',
          description: 'Legal structure, registration, licenses, and permits',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area2',
          area_name: 'Financial Operations & Management',
          description: 'Financial planning, accounting, and cash flow management',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area3',
          area_name: 'Legal & Contracting Compliance',
          description: 'Legal requirements, contracts, and compliance standards',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area4',
          area_name: 'Quality Management & Standards',
          description: 'Quality systems, certifications, and process standards',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area5',
          area_name: 'Technology & Security Infrastructure',
          description: 'IT systems, cybersecurity, and data management',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area6',
          area_name: 'Human Resources & Capacity',
          description: 'Staffing, training, and organizational capacity',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area7',
          area_name: 'Performance Tracking & Reporting',
          description: 'Metrics, reporting systems, and performance management',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area8',
          area_name: 'Risk Management & Business Continuity',
          description: 'Risk assessment, mitigation, and business continuity planning',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area9',
          area_name: 'Supply Chain Management & Vendor Relations',
          description: 'Supplier relationships, procurement, and supply chain optimization',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        },
        {
          area_id: 'area10',
          area_name: 'Competitive Advantage & Market Position',
          description: 'Competitive advantages, market capture processes, strategic partnerships',
          tier_available: clientTierAccess,
          sessions_completed: 0,
          latest_score: 0,
          status: 'not_started',
          last_assessment: null
        }
      ]
    }

    res.json({
      success: true,
      data: assessmentSchema
    })

  } catch (error) {
    logger.error('Get tier-based schema error:', error)
    next(error)
  }
})
    area8: 'Manage risks and ensure business continuity planning',
    area9: 'Optimize supply chain and vendor relationship management',
    area10: 'Develop competitive advantages and market capture processes'
  };
  return descriptions[areaId] || 'Business assessment area';
}

// Helper function to generate tier questions
function generateTierQuestions(areaId, tier) {
  const baseQuestions = {
    area1: {
      tier1: [
        'Your business has valid licenses and is properly registered with all required authorities',
        'You have a clear business structure (LLC, Corporation, etc.) appropriate for your operations',
        'Your business name is legally protected and properly trademarked if applicable'
      ],
      tier2: [
        'You maintain comprehensive records of all business registrations and renewals',
        'Your business structure optimizes tax efficiency and liability protection',
        'You have established clear operating agreements and governance documents'
      ],
      tier3: [
        'You regularly review and update business structure for optimal performance',
        'Your intellectual property strategy aligns with business objectives',
        'You have contingency plans for regulatory changes affecting your business structure'
      ]
    },
    area2: {
      tier1: [
        'You maintain accurate financial records and regular bookkeeping practices',
        'You have established business banking accounts separate from personal finances',
        'You can produce basic financial statements (P&L, Balance Sheet) when needed'
      ],
      tier2: [
        'You use professional accounting software and maintain detailed financial controls',
        'You have established budgeting and forecasting processes for business planning',
        'You regularly monitor cash flow and have established credit facilities'
      ],
      tier3: [
        'You have implemented advanced financial analytics and KPI tracking systems',
        'Your financial planning includes scenario analysis and risk assessment',
        'You maintain investor-ready financial reports and audit trails'
      ]
    },
    area3: {
      tier1: [
        'You understand and comply with basic employment and business laws',
        'You have standard contracts and agreements for common business relationships',
        'You maintain required business insurance and understand your coverage'
      ],
      tier2: [
        'You have established comprehensive compliance monitoring and documentation systems',
        'Your contracts include appropriate risk allocation and dispute resolution mechanisms',
        'You regularly review and update legal compliance based on changing regulations'
      ],
      tier3: [
        'You have implemented proactive legal risk management and mitigation strategies',
        'Your contract management system includes automated compliance tracking',
        'You maintain relationships with specialized legal counsel for complex matters'
      ]
    },
    area4: {
      tier1: [
        'You have defined quality standards and basic procedures for your products/services',
        'You collect and respond to customer feedback regularly',
        'You have processes to identify and correct quality issues when they occur'
      ],
      tier2: [
        'You have implemented formal quality management systems with documented procedures',
        'You conduct regular quality audits and maintain continuous improvement processes',
        'You track quality metrics and have established performance benchmarks'
      ],
      tier3: [
        'Your quality management system meets industry standards (ISO, etc.) where applicable',
        'You have integrated quality management with strategic planning and risk management',
        'You maintain supplier quality programs and end-to-end quality assurance'
      ]
    },
    area5: {
      tier1: [
        'You have reliable technology infrastructure that supports your business operations',
        'You maintain basic cybersecurity measures including secure passwords and antivirus',
        'You regularly backup important business data and test recovery procedures'
      ],
      tier2: [
        'You have implemented comprehensive cybersecurity policies and employee training',
        'Your technology infrastructure includes redundancy and disaster recovery capabilities',
        'You maintain documented IT policies and procedures for security and operations'
      ],
      tier3: [
        'You have implemented enterprise-level security frameworks and compliance monitoring',
        'Your technology strategy aligns with business objectives and includes emerging technologies',
        'You maintain 24/7 monitoring and incident response capabilities'
      ]
    },
    area6: {
      tier1: [
        'You have clear job descriptions and basic HR policies for your workforce',
        'You maintain required employment records and understand basic labor law compliance',
        'You have established basic processes for hiring, onboarding, and performance management'
      ],
      tier2: [
        'You have implemented comprehensive HR policies including employee handbook and procedures',
        'You conduct regular performance reviews and have established career development programs',
        'You maintain competitive compensation and benefits programs appropriate for your industry'
      ],
      tier3: [
        'You have implemented strategic workforce planning and talent management systems',
        'Your HR systems include advanced analytics for workforce optimization and retention',
        'You maintain comprehensive employee engagement and organizational development programs'
      ]
    },
    area7: {
      tier1: [
        'You track basic business metrics and can produce simple performance reports',
        'You have established key performance indicators (KPIs) for your business',
        'You regularly review business performance and make data-driven decisions'
      ],
      tier2: [
        'You have implemented comprehensive reporting systems with automated data collection',
        'You maintain dashboards and analytics tools for real-time performance monitoring',
        'You conduct regular business reviews with stakeholders based on performance data'
      ],
      tier3: [
        'You have implemented advanced analytics and predictive modeling for business optimization',
        'Your reporting systems provide actionable insights for strategic decision-making',
        'You maintain benchmarking programs and competitive analysis capabilities'
      ]
    },
    area8: {
      tier1: [
        'You have identified key business risks and have basic mitigation strategies',
        'You maintain appropriate business insurance coverage for your operations',
        'You have basic emergency procedures and business continuity plans'
      ],
      tier2: [
        'You have implemented formal risk management processes with regular risk assessments',
        'You maintain comprehensive business continuity and disaster recovery plans',
        'You conduct regular testing and updates of your risk management and continuity procedures'
      ],
      tier3: [
        'You have implemented enterprise risk management with integrated risk and opportunity assessment',
        'Your business continuity planning includes advanced scenario planning and crisis management',
        'You maintain risk management systems that integrate with strategic planning and operations'
      ]
    },
    area9: {
      tier1: [
        'You have established reliable suppliers and basic vendor management processes',
        'You maintain appropriate contracts and agreements with key suppliers',
        'You have processes to evaluate and select vendors based on your business needs'
      ],
      tier2: [
        'You have implemented comprehensive supplier management with performance monitoring',
        'You maintain strategic supplier relationships and conduct regular supplier evaluations',
        'You have established supply chain risk management and contingency planning'
      ],
      tier3: [
        'You have implemented strategic supply chain optimization with advanced analytics',
        'Your supplier management includes sustainability and social responsibility criteria',
        'You maintain integrated supply chain systems with real-time monitoring and optimization'
      ]
    },
    area10: {
      tier1: [
        'You have identified your key competitive advantages and unique value propositions',
        'You understand your target market and have basic marketing and sales processes',
        'You regularly monitor competitors and market trends that affect your business'
      ],
      tier2: [
        'You have developed comprehensive competitive intelligence and market analysis capabilities',
        'You maintain strategic partnerships and alliances that enhance your competitive position',
        'You have implemented systematic processes for innovation and market capture'
      ],
      tier3: [
        'You have implemented advanced competitive strategy with dynamic market positioning',
        'Your competitive advantage strategy includes intellectual property and innovation management',
        'You maintain strategic market intelligence systems with predictive analytics for market opportunities'
      ]
    }
  };

  return (baseQuestions[areaId]?.[`tier${tier}`] || []).map((text, index) => ({
    id: `${areaId}_tier${tier}_q${index + 1}`,
    text,
    tier_level: tier,
    area_id: areaId,
    order: index + 1
  }));
}

// Helper function to get client tier access
async function getClientTierAccess(userId) {
  try {
    const user = await User.findOne({ id: userId });
    if (!user || user.role !== 'client') {
      return {};
    }

    // QA override: grant Tier 3 for all areas to test accounts
    if (process.env.QA_TIER_OVERRIDE === 'true' && user.email?.endsWith('@polaris.example.com')) {
      const tierAccess = {};
      for (let i = 1; i <= 10; i++) {
        tierAccess[`area${i}`] = 3;
      }
      return tierAccess;
    }

    const licenseCode = user.license_code;
    if (!licenseCode) {
      // Default to tier 1 for all areas
      const tierAccess = {};
      for (let i = 1; i <= 10; i++) {
        tierAccess[`area${i}`] = 1;
      }
      return tierAccess;
    }

    // Get agency from license
    const { AgencyLicense } = require('../models/Agency');
    const license = await AgencyLicense.findOne({ license_code: licenseCode });
    if (!license) {
      const tierAccess = {};
      for (let i = 1; i <= 10; i++) {
        tierAccess[`area${i}`] = 1;
      }
      return tierAccess;
    }

    const agencyUserId = license.agency_user_id || license.agency_id;
    if (!agencyUserId) {
      const tierAccess = {};
      for (let i = 1; i <= 10; i++) {
        tierAccess[`area${i}`] = 1;
      }
      return tierAccess;
    }

    // Get agency tier configuration
    const agencyConfig = await AgencyTierConfiguration.findOne({ agency_id: agencyUserId });
    if (!agencyConfig) {
      // Check for default tier 3 configuration
      const defaultConfig = await AgencyTierConfiguration.findOne({ agency_id: 'default' });
      if (defaultConfig) {
        return defaultConfig.tier_access_levels;
      }

      // Fallback: create tier 1 configuration
      const fallbackConfig = {};
      for (let i = 1; i <= 10; i++) {
        fallbackConfig[`area${i}`] = 1;
      }
      
      await AgencyTierConfiguration.create({
        _id: uuidv4(),
        agency_id: agencyUserId,
        tier_access_levels: fallbackConfig,
        pricing_per_tier: { tier1: 25.0, tier2: 50.0, tier3: 100.0 }
      });
      
      return fallbackConfig;
    }

    return agencyConfig.tier_access_levels || {};
  } catch (error) {
    logger.error('Error getting client tier access:', error);
    // Return default tier 1 access as fallback
    const tierAccess = {};
    for (let i = 1; i <= 10; i++) {
      tierAccess[`area${i}`] = 1;
    }
    return tierAccess;
  }
}

/**
 * GET /api/assessment/schema
 * Get assessment schema
 */
router.get('/schema', async (req, res, next) => {
  try {
    res.json({
      success: true,
      data: ASSESSMENT_SCHEMA
    });
  } catch (error) {
    logger.error('Get assessment schema error:', error);
    next(error);
  }
});

/**
 * GET /api/assessment/schema/tier-based
 * Get tier-based assessment schema with client access levels
 */
router.get('/schema/tier-based', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const clientTierAccess = await getClientTierAccess(userId);

    const tierBasedSchema = {
      areas: ASSESSMENT_SCHEMA.areas.map(area => {
        const maxTier = clientTierAccess[area.id] || 1;
        const availableTiers = {};
        
        for (let tier = 1; tier <= maxTier; tier++) {
          availableTiers[`tier${tier}`] = area.tiers[`tier${tier}`];
        }
        
        return {
          ...area,
          tiers: availableTiers,
          max_tier_access: maxTier
        };
      }),
      client_tier_access: clientTierAccess
    };

    res.json({
      success: true,
      data: tierBasedSchema
    });
  } catch (error) {
    logger.error('Get tier-based schema error:', error);
    next(error);
  }
});

/**
 * POST /api/assessment/session
 * Create new assessment session
 */
router.post('/session', authenticateToken, async (req, res, next) => {
  try {
    const { area_id } = req.body;
    const userId = req.user.id;

    if (!BUSINESS_AREAS[area_id]) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }

    // Check for existing active session
    const existingSession = await AssessmentSession.findOne({
      user_id: userId,
      area_id,
      status: 'active'
    });

    if (existingSession) {
      return res.json({
        success: true,
        message: 'Active session found',
        data: {
          session: existingSession
        }
      });
    }

    // Create new session with tier 1 questions
    const questions = generateTierQuestions(area_id, 1);
    
    const session = new AssessmentSession({
      id: uuidv4(),
      user_id: userId,
      area_id,
      session_type: 'standard',
      tier_level: 1,
      questions,
      status: 'active'
    });

    await session.save();

    logger.info(`Assessment session created: ${session.id} for user ${userId} in area ${area_id}`);

    res.status(201).json({
      success: true,
      message: 'Assessment session created',
      data: {
        session
      }
    });
  } catch (error) {
    logger.error('Create assessment session error:', error);
    next(error);
  }
});

/**
 * POST /api/assessment/tier-session
 * Create new tier-based assessment session
 */
router.post('/tier-session', authenticateToken, async (req, res, next) => {
  try {
    const { area_id, tier_level } = req.body;
    const userId = req.user.id;

    if (!BUSINESS_AREAS[area_id]) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid business area',
          'The specified business area does not exist'
        )
      );
    }

    if (!tier_level || tier_level < 1 || tier_level > 3) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid tier level',
          'Tier level must be between 1 and 3'
        )
      );
    }

    // Check client tier access
    const clientTierAccess = await getClientTierAccess(userId);
    const maxTier = clientTierAccess[area_id] || 1;
    
    if (tier_level > maxTier) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Insufficient tier access',
          `Your maximum tier access for this area is ${maxTier}`
        )
      );
    }

    // Check for existing active session
    const existingSession = await TierAssessmentSession.findOne({
      user_id: userId,
      area_id,
      tier_level,
      status: 'active'
    });

    if (existingSession) {
      return res.json({
        success: true,
        message: 'Active tier session found',
        data: {
          session: existingSession
        }
      });
    }

    // Generate questions for all tiers up to the requested level
    const questions = [];
    for (let tier = 1; tier <= tier_level; tier++) {
      const tierQuestions = generateTierQuestions(area_id, tier);
      questions.push(...tierQuestions);
    }

    const session = new TierAssessmentSession({
      _id: uuidv4(),
      user_id: userId,
      area_id,
      tier_level,
      questions,
      status: 'active'
    });

    await session.save();

    logger.info(`Tier assessment session created: ${session._id} for user ${userId} in area ${area_id} tier ${tier_level}`);

    res.status(201).json({
      success: true,
      message: 'Tier assessment session created',
      data: {
        session
      }
    });
  } catch (error) {
    logger.error('Create tier assessment session error:', error);
    next(error);
  }
});

/**
 * POST /api/assessment/session/:sessionId/response
 * Submit response to assessment question
 */
router.post('/session/:sessionId/response', authenticateToken, validate(schemas.assessmentResponse), async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const { question_id, response, evidence_provided = 'false', evidence_url, notes } = req.body;
    const userId = req.user.id;

    const session = await AssessmentSession.findOne({
      id: sessionId,
      user_id: userId
    });

    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Assessment session not found',
          'The specified assessment session does not exist'
        )
      );
    }

    if (session.status !== 'active') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Assessment session is not active',
          'Cannot submit responses to inactive sessions'
        )
      );
    }

    // Find the question
    const question = session.questions.find(q => q.id === question_id);
    if (!question) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Question not found',
          'The specified question does not exist in this session'
        )
      );
    }

    // Update or add response
    const responseData = {
      question_id,
      response,
      tier_level: question.tier_level,
      evidence_required: question.tier_level >= 2 && response === 'compliant',
      evidence_provided: evidence_provided === 'true',
      evidence_url,
      notes,
      submitted_at: new Date(),
      verification_status: question.tier_level >= 2 ? 'pending' : undefined
    };

    const existingResponseIndex = session.responses.findIndex(r => r.question_id === question_id);
    if (existingResponseIndex !== -1) {
      session.responses[existingResponseIndex] = responseData;
    } else {
      session.responses.push(responseData);
    }

    // Check if assessment is complete
    const totalQuestions = session.questions.length;
    const completedQuestions = session.responses.length;

    if (completedQuestions >= totalQuestions) {
      session.status = 'completed';
      session.completed_at = new Date();
      session.completion_score = calculateAssessmentScore(session.responses);
    }

    await session.save();

    res.json({
      success: true,
      message: 'Response submitted successfully',
      data: {
        session,
        progress: {
          completed_questions: completedQuestions,
          total_questions: totalQuestions,
          percentage: Math.round((completedQuestions / totalQuestions) * 100)
        }
      }
    });
  } catch (error) {
    logger.error('Submit assessment response error:', error);
    next(error);
  }
});

/**
 * POST /api/assessment/tier-session/:sessionId/response
 * Submit response to tier assessment question
 */
router.post('/tier-session/:sessionId/response', authenticateToken, async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const { question_id, response, evidence_provided = 'false', evidence_url, notes } = req.body;
    const userId = req.user.id;

    const session = await TierAssessmentSession.findOne({
      _id: sessionId,
      user_id: userId
    });

    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Assessment session not found',
          'The specified tier assessment session does not exist'
        )
      );
    }

    if (session.status !== 'active') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Assessment session is not active',
          'Cannot submit responses to inactive sessions'
        )
      );
    }

    // Find the question
    const question = session.questions.find(q => q.id === question_id);
    if (!question) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Question not found',
          'The specified question does not exist in this session'
        )
      );
    }

    // Evidence requirement check for Tier 2 & 3
    const tierLevel = question.tier_level || session.tier_level || 1;
    if (response === 'compliant' && tierLevel >= 2) {
      const evidenceProvidedBool = evidence_provided === 'true';
      
      if (!evidenceProvidedBool && !evidence_url) {
        // Check if evidence exists in database
        const evidenceRecord = await AssessmentEvidence.findOne({
          session_id: sessionId,
          question_id: question_id,
          user_id: userId
        });
        
        if (!evidenceRecord) {
          return res.status(422).json(
            formatErrorResponse(
              'POL-4003',
              `Evidence upload is required for Tier ${tierLevel} compliant responses. Please upload supporting documentation before submitting your response.`,
              'Evidence required'
            )
          );
        }
      }
    }

    // Update or add response
    const responseData = {
      question_id,
      response,
      tier_level: tierLevel,
      evidence_required: tierLevel >= 2 && response === 'compliant',
      evidence_provided: evidence_provided === 'true',
      evidence_url,
      notes,
      submitted_at: new Date(),
      verification_status: tierLevel >= 2 ? 'pending' : undefined
    };

    const existingResponseIndex = session.responses.findIndex(r => r.question_id === question_id);
    if (existingResponseIndex !== -1) {
      session.responses[existingResponseIndex] = responseData;
    } else {
      session.responses.push(responseData);
    }

    // Check if assessment is complete
    const totalQuestions = session.questions.length;
    const completedQuestions = session.responses.length;

    if (completedQuestions >= totalQuestions) {
      session.status = 'completed';
      session.completed_at = new Date();
      session.tier_completion_score = calculateAssessmentScore(session.responses);
    }

    session.updated_at = new Date();
    await session.save();

    res.json({
      success: true,
      message: 'Response submitted successfully',
      data: {
        completed_questions: completedQuestions,
        total_questions: totalQuestions,
        progress_percentage: Math.round((completedQuestions / totalQuestions) * 100),
        is_complete: completedQuestions >= totalQuestions
      }
    });
  } catch (error) {
    logger.error('Submit tier assessment response error:', error);
    next(error);
  }
});

/**
 * GET /api/assessment/tier-session/:sessionId/progress
 * Get tier assessment session progress
 */
router.get('/tier-session/:sessionId/progress', authenticateToken, async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;

    const session = await TierAssessmentSession.findOne({
      _id: sessionId,
      user_id: userId
    });

    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Assessment session not found',
          'The specified tier assessment session does not exist'
        )
      );
    }

    const totalQuestions = session.questions.length;
    const completedQuestions = session.responses.length;
    const progressPercentage = totalQuestions > 0 ? Math.round((completedQuestions / totalQuestions) * 100) : 0;

    res.json({
      success: true,
      data: {
        session_id: sessionId,
        area_id: session.area_id,
        tier_level: session.tier_level,
        status: session.status,
        progress: {
          completed_questions: completedQuestions,
          total_questions: totalQuestions,
          percentage: progressPercentage
        },
        responses: session.responses,
        created_at: session.created_at,
        updated_at: session.updated_at
      }
    });
  } catch (error) {
    logger.error('Get tier assessment progress error:', error);
    next(error);
  }
});

/**
 * GET /api/assessment/results/:sessionId
 * Get assessment results
 */
router.get('/results/:sessionId', authenticateToken, async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;

    // Try both session types
    let session = await AssessmentSession.findOne({
      id: sessionId,
      user_id: userId
    });

    if (!session) {
      session = await TierAssessmentSession.findOne({
        _id: sessionId,
        user_id: userId
      });
    }

    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Assessment session not found',
          'The specified assessment session does not exist'
        )
      );
    }

    if (session.status !== 'completed') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Assessment not completed',
          'Results are only available for completed assessments'
        )
      );
    }

    // Generate results
    const overallScore = session.completion_score || session.tier_completion_score || 0;
    const areaName = BUSINESS_AREAS[session.area_id];
    
    // Analyze responses for gaps and recommendations
    const gaps = session.responses
      .filter(r => r.response === 'not_compliant' || r.response === 'partially_compliant')
      .map(r => {
        const question = session.questions.find(q => q.id === r.question_id);
        return {
          question_id: r.question_id,
          question_text: question?.text,
          response: r.response,
          tier_level: r.tier_level,
          priority: r.response === 'not_compliant' ? 'high' : 'medium'
        };
      });

    const recommendations = generateRecommendations(session.area_id, gaps);

    const results = {
      session_id: sessionId,
      area_id: session.area_id,
      area_name: areaName,
      overall_score: overallScore,
      tier_level: session.tier_level,
      completed_at: session.completed_at,
      total_questions: session.questions.length,
      responses: session.responses,
      gaps,
      recommendations,
      next_steps: generateNextSteps(session.area_id, gaps)
    };

    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    logger.error('Get assessment results error:', error);
    next(error);
  }
});

// Helper function to generate recommendations
function generateRecommendations(areaId, gaps) {
  const baseRecommendations = {
    area1: [
      'Review and update business registration documents',
      'Consult with legal counsel about business structure optimization',
      'Implement document management system for compliance tracking'
    ],
    area2: [
      'Implement professional accounting software',
      'Establish regular financial review meetings',
      'Consider hiring a financial advisor or accountant'
    ],
    // Add more recommendations for other areas...
  };

  const recommendations = baseRecommendations[areaId] || ['Consult with relevant professionals for improvement'];
  
  return gaps.slice(0, 3).map((gap, index) => ({
    priority: gap.priority,
    category: BUSINESS_AREAS[areaId],
    description: recommendations[index] || 'Address identified compliance gap',
    resources: [`Knowledge Base: ${BUSINESS_AREAS[areaId]}`, 'Professional Services Directory']
  }));
}

// Helper function to generate next steps
function generateNextSteps(areaId, gaps) {
  if (gaps.length === 0) {
    return [
      'Maintain current compliance standards',
      'Consider advancing to higher tier assessments',
      'Regular periodic reviews recommended'
    ];
  }

  return [
    'Address high-priority compliance gaps first',
    'Consult Knowledge Base resources for guidance',
    'Consider engaging professional service providers',
    'Schedule follow-up assessment in 30-60 days'
  ];
}

/**
 * GET /api/client/assessment-progress
 * Get client assessment progress across all areas
 */
router.get('/client/assessment-progress', authenticateToken, requireRole('client'), async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    // Get all sessions for the user
    const sessions = await AssessmentSession.find({ user_id: userId });
    const tierSessions = await TierAssessmentSession.find({ user_id: userId });
    
    const allSessions = [...sessions, ...tierSessions];
    
    const progress = Object.entries(BUSINESS_AREAS).map(([areaId, areaName]) => {
      const areaSessions = allSessions.filter(s => s.area_id === areaId);
      const completedSessions = areaSessions.filter(s => s.status === 'completed');
      const latestSession = areaSessions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
      
      return {
        area_id: areaId,
        area_name: areaName,
        sessions_completed: completedSessions.length,
        latest_score: latestSession?.completion_score || latestSession?.tier_completion_score || 0,
        last_assessment: latestSession?.completed_at,
        status: latestSession?.status || 'not_started'
      };
    });
    
    const overallProgress = {
      total_areas: Object.keys(BUSINESS_AREAS).length,
      areas_started: progress.filter(p => p.status !== 'not_started').length,
      areas_completed: progress.filter(p => p.status === 'completed').length,
      average_score: progress.reduce((sum, p) => sum + p.latest_score, 0) / progress.length
    };
    
    res.json({
      success: true,
      data: {
        overall_progress: overallProgress,
        area_progress: progress
      }
    });
  } catch (error) {
    logger.error('Get client assessment progress error:', error);
    next(error);
  }
});

module.exports = router;