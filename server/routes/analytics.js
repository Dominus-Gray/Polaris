const express = require('express');
const { Analytics } = require('../models/System');
const { KnowledgeBaseAccess } = require('../models/KnowledgeBase');
const { AssessmentSession, TierAssessmentSession } = require('../models/Assessment');
const { ServiceRequest } = require('../models/ServiceRequest');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { 
  formatResponse, 
  formatErrorResponse,
  getBusinessAreas
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

const BUSINESS_AREAS = getBusinessAreas();

/**
 * POST /api/analytics/resource-access
 * Log resource access event
 */
router.post('/resource-access', authenticateToken, async (req, res, next) => {
  try {
    const { 
      area_id, 
      resource_type, 
      access_type = 'view',
      session_id,
      metadata = {}
    } = req.body;
    
    const userId = req.user.id;
    
    if (!area_id || !resource_type) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Area ID and resource type are required',
          'Please provide area_id and resource_type'
        )
      );
    }
    
    // Create analytics event
    const analyticsEvent = new Analytics({
      event_type: 'knowledge_base_access',
      user_id: userId,
      session_id,
      area_id,
      event_data: {
        resource_type,
        access_type,
        metadata
      },
      ip_address: req.ip,
      user_agent: req.get('User-Agent')
    });
    
    await analyticsEvent.save();
    
    // Also log in knowledge base access for compatibility
    try {
      await KnowledgeBaseAccess.logAccess({
        user_id: userId,
        area_id,
        access_type,
        resource_type,
        session_id,
        ip_address: req.ip,
        user_agent: req.get('User-Agent'),
        metadata
      });
    } catch (kbError) {
      logger.warn('Failed to log KB access:', kbError);
    }
    
    res.json({
      success: true,
      message: 'Resource access logged successfully',
      data: {
        event_id: analyticsEvent.id,
        timestamp: analyticsEvent.timestamp
      }
    });
    
  } catch (error) {
    logger.error('Log resource access error:', error);
    next(error);
  }
});

/**
 * GET /api/analytics/dashboard
 * Get analytics dashboard data
 */
router.get('/dashboard', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const userRole = req.user.role;
    const { period = '30d' } = req.query;
    
    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    
    switch (period) {
      case '7d':
        startDate.setDate(startDate.getDate() - 7);
        break;
      case '30d':
        startDate.setDate(startDate.getDate() - 30);
        break;
      case '90d':
        startDate.setDate(startDate.getDate() - 90);
        break;
      default:
        startDate.setDate(startDate.getDate() - 30);
    }
    
    let dashboardData = {};
    
    if (userRole === 'client') {
      // Client analytics
      dashboardData = await getClientAnalytics(userId, startDate, endDate);
    } else if (userRole === 'provider') {
      // Provider analytics
      dashboardData = await getProviderAnalytics(userId, startDate, endDate);
    } else if (userRole === 'agency') {
      // Agency analytics
      dashboardData = await getAgencyAnalytics(userId, startDate, endDate);
    } else if (userRole === 'navigator') {
      // Navigator/system analytics
      dashboardData = await getSystemAnalytics(startDate, endDate);
    }
    
    res.json({
      success: true,
      data: {
        period: { start: startDate, end: endDate },
        ...dashboardData
      }
    });
    
  } catch (error) {
    logger.error('Get analytics dashboard error:', error);
    next(error);
  }
});

/**
 * GET /api/analytics/events
 * Get analytics events with filtering
 */
router.get('/events', authenticateToken, async (req, res, next) => {
  try {
    const { 
      event_type,
      area_id,
      start_date,
      end_date,
      page = 1,
      limit = 50
    } = req.query;
    
    const userId = req.user.id;
    const userRole = req.user.role;
    
    // Build query
    const query = {};
    
    // Non-navigators can only see their own events
    if (userRole !== 'navigator') {
      query.user_id = userId;
    }
    
    if (event_type) {
      query.event_type = event_type;
    }
    
    if (area_id) {
      query.area_id = area_id;
    }
    
    if (start_date || end_date) {
      query.timestamp = {};
      if (start_date) query.timestamp.$gte = new Date(start_date);
      if (end_date) query.timestamp.$lte = new Date(end_date);
    }
    
    const total = await Analytics.countDocuments(query);
    const events = await Analytics.find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .select('-user_agent -ip_address'); // Exclude sensitive data
    
    res.json({
      success: true,
      data: {
        events,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          totalPages: Math.ceil(total / limit)
        }
      }
    });
    
  } catch (error) {
    logger.error('Get analytics events error:', error);
    next(error);
  }
});

/**
 * GET /api/analytics/reports/:reportType
 * Generate analytics reports
 */
router.get('/reports/:reportType', authenticateToken, async (req, res, next) => {
  try {
    const { reportType } = req.params;
    const { period = '30d', format = 'json' } = req.query;
    const userId = req.user.id;
    const userRole = req.user.role;
    
    // Only navigators can access system-wide reports
    if (['system', 'platform', 'usage'].includes(reportType) && userRole !== 'navigator') {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'System reports are only available to navigators'
        )
      );
    }
    
    let reportData = {};
    
    switch (reportType) {
      case 'user-activity':
        reportData = await generateUserActivityReport(userId, period);
        break;
      case 'knowledge-base':
        reportData = await generateKnowledgeBaseReport(userId, period, userRole);
        break;
      case 'assessments':
        reportData = await generateAssessmentReport(userId, period, userRole);
        break;
      case 'system':
        reportData = await generateSystemReport(period);
        break;
      default:
        return res.status(400).json(
          formatErrorResponse(
            'POL-4001',
            'Invalid report type',
            'The specified report type is not supported'
          )
        );
    }
    
    if (format === 'csv') {
      // TODO: Implement CSV export
      return res.status(501).json(
        formatErrorResponse(
          'POL-5001',
          'CSV format not implemented',
          'CSV export is not yet available'
        )
      );
    }
    
    res.json({
      success: true,
      data: {
        report_type: reportType,
        period,
        generated_at: new Date(),
        ...reportData
      }
    });
    
  } catch (error) {
    logger.error('Generate analytics report error:', error);
    next(error);
  }
});

// Helper functions for analytics
async function getClientAnalytics(userId, startDate, endDate) {
  const assessmentCount = await AssessmentSession.countDocuments({
    user_id: userId,
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  const kbAccess = await KnowledgeBaseAccess.countDocuments({
    user_id: userId,
    accessed_at: { $gte: startDate, $lte: endDate }
  });
  
  const serviceRequests = await ServiceRequest.countDocuments({
    client_id: userId,
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  return {
    user_type: 'client',
    assessments_completed: assessmentCount,
    knowledge_base_access: kbAccess,
    service_requests_created: serviceRequests,
    engagement_score: Math.min(100, (assessmentCount * 20) + (kbAccess * 5) + (serviceRequests * 15))
  };
}

async function getProviderAnalytics(userId, startDate, endDate) {
  const { ProviderResponse, Engagement } = require('../models/ServiceRequest');
  
  const responses = await ProviderResponse.countDocuments({
    provider_id: userId,
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  const engagements = await Engagement.countDocuments({
    provider_id: userId,
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  return {
    user_type: 'provider',
    responses_submitted: responses,
    engagements_created: engagements,
    success_rate: responses > 0 ? Math.round((engagements / responses) * 100) : 0
  };
}

async function getAgencyAnalytics(userId, startDate, endDate) {
  const { AgencyLicense } = require('../models/Agency');
  
  const licensesGenerated = await AgencyLicense.countDocuments({
    agency_user_id: userId,
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  const licensesUsed = await AgencyLicense.countDocuments({
    agency_user_id: userId,
    status: 'used',
    used_at: { $gte: startDate, $lte: endDate }
  });
  
  return {
    user_type: 'agency',
    licenses_generated: licensesGenerated,
    licenses_used: licensesUsed,
    usage_rate: licensesGenerated > 0 ? Math.round((licensesUsed / licensesGenerated) * 100) : 0
  };
}

async function getSystemAnalytics(startDate, endDate) {
  const totalUsers = await User.countDocuments({
    created_at: { $gte: startDate, $lte: endDate }
  });
  
  const totalEvents = await Analytics.countDocuments({
    timestamp: { $gte: startDate, $lte: endDate }
  });
  
  const topEvents = await Analytics.aggregate([
    {
      $match: {
        timestamp: { $gte: startDate, $lte: endDate }
      }
    },
    {
      $group: {
        _id: '$event_type',
        count: { $sum: 1 }
      }
    },
    { $sort: { count: -1 } },
    { $limit: 10 }
  ]);
  
  return {
    user_type: 'navigator',
    new_users: totalUsers,
    total_events: totalEvents,
    top_events: topEvents,
    system_health: {
      uptime: process.uptime(),
      memory_usage: process.memoryUsage(),
      cpu_usage: process.cpuUsage()
    }
  };
}

async function generateUserActivityReport(userId, period) {
  const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  const events = await Analytics.find({
    user_id: userId,
    timestamp: { $gte: startDate }
  }).sort({ timestamp: -1 });
  
  const eventsByDay = events.reduce((acc, event) => {
    const day = event.timestamp.toISOString().split('T')[0];
    if (!acc[day]) acc[day] = 0;
    acc[day]++;
    return acc;
  }, {});
  
  return {
    total_events: events.length,
    events_by_day: eventsByDay,
    most_active_day: Object.keys(eventsByDay).reduce((a, b) => 
      eventsByDay[a] > eventsByDay[b] ? a : b, Object.keys(eventsByDay)[0]
    )
  };
}

async function generateKnowledgeBaseReport(userId, period, userRole) {
  const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  const query = {
    accessed_at: { $gte: startDate }
  };
  
  if (userRole !== 'navigator') {
    query.user_id = userId;
  }
  
  const accesses = await KnowledgeBaseAccess.find(query);
  
  const byArea = accesses.reduce((acc, access) => {
    const areaName = BUSINESS_AREAS[access.area_id] || access.area_id;
    if (!acc[areaName]) acc[areaName] = 0;
    acc[areaName]++;
    return acc;
  }, {});
  
  return {
    total_accesses: accesses.length,
    accesses_by_area: byArea,
    most_popular_area: Object.keys(byArea).reduce((a, b) => 
      byArea[a] > byArea[b] ? a : b, Object.keys(byArea)[0]
    )
  };
}

async function generateAssessmentReport(userId, period, userRole) {
  const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  const query = {
    created_at: { $gte: startDate }
  };
  
  if (userRole !== 'navigator') {
    query.user_id = userId;
  }
  
  const sessions = await AssessmentSession.find(query);
  const tierSessions = await TierAssessmentSession.find(query);
  
  const completedSessions = sessions.filter(s => s.status === 'completed').length;
  const completedTierSessions = tierSessions.filter(s => s.status === 'completed').length;
  
  return {
    total_sessions: sessions.length + tierSessions.length,
    completed_sessions: completedSessions + completedTierSessions,
    completion_rate: sessions.length > 0 
      ? Math.round(((completedSessions + completedTierSessions) / (sessions.length + tierSessions.length)) * 100)
      : 0
  };
}

async function generateSystemReport(period) {
  const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  const userStats = await User.aggregate([
    {
      $match: {
        created_at: { $gte: startDate }
      }
    },
    {
      $group: {
        _id: '$role',
        count: { $sum: 1 }
      }
    }
  ]);
  
  const eventStats = await Analytics.aggregate([
    {
      $match: {
        timestamp: { $gte: startDate }
      }
    },
    {
      $group: {
        _id: '$event_type',
        count: { $sum: 1 }
      }
    },
    { $sort: { count: -1 } }
  ]);
  
  return {
    period_days: days,
    user_registrations: userStats,
    event_distribution: eventStats,
    system_metrics: {
      total_users: await User.countDocuments(),
      total_events: await Analytics.countDocuments(),
      uptime_hours: Math.round(process.uptime() / 3600)
    }
  };
}

module.exports = router;