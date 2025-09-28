const express = require('express');
const User = require('../models/User');
const { AgencyLicense, AgencyTierConfiguration } = require('../models/Agency');
const { KnowledgeBaseAccess } = require('../models/KnowledgeBase');
const { Analytics } = require('../models/System');
const { authenticateToken, requireRole } = require('../middleware/auth');
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
 * GET /api/navigator/dashboard
 * Get navigator dashboard data
 */
router.get('/dashboard', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    // Get system statistics
    const stats = {
      total_users: await User.countDocuments(),
      pending_agencies: await User.countDocuments({ role: 'agency', status: 'pending' }),
      active_agencies: await User.countDocuments({ role: 'agency', status: 'approved' }),
      total_clients: await User.countDocuments({ role: 'client' }),
      total_providers: await User.countDocuments({ role: 'provider' }),
      licenses_generated: await AgencyLicense.countDocuments(),
      licenses_used: await AgencyLicense.countDocuments({ status: 'used' })
    };
    
    // Get recent activity
    const recentUsers = await User.find({})
      .sort({ created_at: -1 })
      .limit(10)
      .select('name email role status created_at');
    
    // Get pending approvals
    const pendingApprovals = await User.find({ 
      role: { $in: ['agency', 'provider'] }, 
      status: 'pending' 
    })
      .sort({ created_at: -1 })
      .limit(20)
      .select('id name email role company_name created_at');
    
    const dashboardData = {
      navigator: req.user.toSafeObject(),
      system_stats: stats,
      recent_users: recentUsers,
      pending_approvals: pendingApprovals.map(user => ({
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        company_name: user.company_name,
        created_at: user.created_at
      }))
    };
    
    res.json({
      success: true,
      data: dashboardData
    });
    
  } catch (error) {
    logger.error('Get navigator dashboard error:', error);
    next(error);
  }
});

/**
 * GET /api/navigator/agencies/pending
 * Get pending agency approvals
 */
router.get('/agencies/pending', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    
    const query = { role: 'agency', status: 'pending' };
    const total = await User.countDocuments(query);
    
    const pendingAgencies = await User.find(query)
      .sort({ created_at: 1 }) // Oldest first for FIFO processing
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .select('id name email company_name business_description location created_at');
    
    res.json({
      success: true,
      data: {
        agencies: pendingAgencies.map(agency => ({
          id: agency.id,
          name: agency.name,
          email: agency.email,
          company_name: agency.company_name,
          business_description: agency.business_description,
          location: agency.location,
          created_at: agency.created_at
        })),
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get pending agencies error:', error);
    next(error);
  }
});

/**
 * POST /api/navigator/agencies/approve
 * Approve an agency
 */
router.post('/agencies/approve', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { agency_id, notes } = req.body;
    
    if (!agency_id) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Agency ID is required',
          'Please provide the agency ID to approve'
        )
      );
    }
    
    const agency = await User.findOne({ id: agency_id, role: 'agency' });
    
    if (!agency) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Agency not found',
          'The specified agency does not exist'
        )
      );
    }
    
    if (agency.status === 'approved') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4002',
          'Agency already approved',
          'This agency has already been approved'
        )
      );
    }
    
    // Approve the agency
    agency.status = 'approved';
    await agency.save();
    
    // Create default tier configuration for the agency
    const defaultTierAccess = {};
    for (let i = 1; i <= 10; i++) {
      defaultTierAccess[`area${i}`] = 3; // Grant tier 3 access by default
    }
    
    const tierConfig = new AgencyTierConfiguration({
      agency_id: agency_id,
      tier_access_levels: defaultTierAccess,
      pricing_per_tier: {
        tier1: 25.0,
        tier2: 50.0,
        tier3: 100.0
      },
      monthly_limits: {
        license_generation: 50, // Higher limit for approved agencies
        assessments: 500,
        users: 100
      }
    });
    
    await tierConfig.save();
    
    // TODO: Send approval notification email
    
    logger.info(`Agency approved: ${agency.email} by navigator ${req.user.email}`);
    
    res.json({
      success: true,
      message: 'Agency approved successfully',
      data: {
        agency_id,
        status: 'approved',
        approved_at: new Date(),
        approved_by: req.user.id
      }
    });
    
  } catch (error) {
    logger.error('Approve agency error:', error);
    next(error);
  }
});

/**
 * POST /api/navigator/agencies/reject
 * Reject an agency application
 */
router.post('/agencies/reject', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { agency_id, reason, notes } = req.body;
    
    if (!agency_id || !reason) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Agency ID and reason are required',
          'Please provide the agency ID and rejection reason'
        )
      );
    }
    
    const agency = await User.findOne({ id: agency_id, role: 'agency' });
    
    if (!agency) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Agency not found',
          'The specified agency does not exist'
        )
      );
    }
    
    // Reject the agency
    agency.status = 'rejected';
    agency.rejection_reason = reason;
    agency.rejection_notes = notes;
    agency.rejected_at = new Date();
    agency.rejected_by = req.user.id;
    await agency.save();
    
    // TODO: Send rejection notification email
    
    logger.info(`Agency rejected: ${agency.email} by navigator ${req.user.email}, reason: ${reason}`);
    
    res.json({
      success: true,
      message: 'Agency application rejected',
      data: {
        agency_id,
        status: 'rejected',
        reason,
        rejected_at: new Date(),
        rejected_by: req.user.id
      }
    });
    
  } catch (error) {
    logger.error('Reject agency error:', error);
    next(error);
  }
});

/**
 * GET /api/navigator/analytics/resources
 * Get resource usage analytics
 */
router.get('/analytics/resources', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { since_days = 30 } = req.query;
    
    const sinceDate = new Date();
    sinceDate.setDate(sinceDate.getDate() - parseInt(since_days));
    
    // Get knowledge base access analytics
    const resourceAccess = await KnowledgeBaseAccess.find({
      accessed_at: { $gte: sinceDate }
    });
    
    // Group by area
    const byArea = resourceAccess.reduce((acc, access) => {
      const areaId = access.area_id;
      if (!acc[areaId]) {
        acc[areaId] = {
          area_id: areaId,
          area_name: BUSINESS_AREAS[areaId] || 'Unknown Area',
          count: 0
        };
      }
      acc[areaId].count++;
      return acc;
    }, {});
    
    // Get last 7 days trend
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      
      const dayAccess = await KnowledgeBaseAccess.countDocuments({
        accessed_at: {
          $gte: date,
          $lt: nextDate
        }
      });
      
      last7Days.push({
        date: date.toISOString().split('T')[0],
        count: dayAccess
      });
    }
    
    res.json({
      success: true,
      data: {
        since: sinceDate.toISOString(),
        total: resourceAccess.length,
        by_area: Object.values(byArea),
        last7: last7Days
      }
    });
    
  } catch (error) {
    logger.error('Get resource analytics error:', error);
    next(error);
  }
});

/**
 * GET /api/navigator/analytics/system
 * Get system-wide analytics
 */
router.get('/analytics/system', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
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
    
    // Get user registrations over time
    const userRegistrations = await User.aggregate([
      {
        $match: {
          created_at: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: {
            date: { $dateToString: { format: '%Y-%m-%d', date: '$created_at' } },
            role: '$role'
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.date': 1 } }
    ]);
    
    // Get license usage statistics
    const licenseStats = {
      total_generated: await AgencyLicense.countDocuments({ 
        created_at: { $gte: startDate, $lte: endDate } 
      }),
      total_used: await AgencyLicense.countDocuments({ 
        used_at: { $gte: startDate, $lte: endDate } 
      }),
      usage_rate: 0
    };
    
    if (licenseStats.total_generated > 0) {
      licenseStats.usage_rate = (licenseStats.total_used / licenseStats.total_generated) * 100;
    }
    
    // Get top performing areas
    const topAreas = await KnowledgeBaseAccess.aggregate([
      {
        $match: {
          accessed_at: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: '$area_id',
          access_count: { $sum: 1 }
        }
      },
      { $sort: { access_count: -1 } },
      { $limit: 5 }
    ]);
    
    const topAreasWithNames = topAreas.map(area => ({
      area_id: area._id,
      area_name: BUSINESS_AREAS[area._id] || 'Unknown Area',
      access_count: area.access_count
    }));
    
    // System health metrics
    const systemHealth = {
      total_users: await User.countDocuments(),
      active_agencies: await User.countDocuments({ role: 'agency', status: 'approved' }),
      pending_approvals: await User.countDocuments({ 
        role: { $in: ['agency', 'provider'] }, 
        status: 'pending' 
      }),
      system_uptime: process.uptime(),
      last_updated: new Date()
    };
    
    res.json({
      success: true,
      data: {
        period: {
          start: startDate,
          end: endDate,
          duration: period
        },
        user_registrations: userRegistrations,
        license_stats: licenseStats,
        top_areas: topAreasWithNames,
        system_health: systemHealth
      }
    });
    
  } catch (error) {
    logger.error('Get system analytics error:', error);
    next(error);
  }
});

/**
 * GET /api/navigator/users
 * Get all users with filtering
 */
router.get('/users', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      role = 'all', 
      status = 'all', 
      search = '' 
    } = req.query;
    
    const query = {};
    
    if (role !== 'all') {
      query.role = role;
    }
    
    if (status !== 'all') {
      query.status = status;
    }
    
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
        { company_name: { $regex: search, $options: 'i' } }
      ];
    }
    
    const total = await User.countDocuments(query);
    const users = await User.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .select('-password -__v');
    
    res.json({
      success: true,
      data: {
        users: users.map(user => user.toSafeObject()),
        pagination: getPaginationMeta(total, page, limit),
        filters: {
          role,
          status,
          search
        }
      }
    });
    
  } catch (error) {
    logger.error('Get users error:', error);
    next(error);
  }
});

/**
 * PUT /api/navigator/users/:userId/status
 * Update user status
 */
router.put('/users/:userId/status', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { status, reason } = req.body;
    
    const validStatuses = ['pending', 'approved', 'rejected', 'suspended'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid status',
          `Status must be one of: ${validStatuses.join(', ')}`
        )
      );
    }
    
    const user = await User.findOne({ id: userId });
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'The specified user does not exist'
        )
      );
    }
    
    const previousStatus = user.status;
    user.status = status;
    
    if (status === 'rejected' || status === 'suspended') {
      user.status_reason = reason;
      user.status_updated_by = req.user.id;
      user.status_updated_at = new Date();
    }
    
    await user.save();
    
    logger.info(`User status updated: ${user.email} from ${previousStatus} to ${status} by navigator ${req.user.email}`);
    
    res.json({
      success: true,
      message: 'User status updated successfully',
      data: {
        user_id: userId,
        previous_status: previousStatus,
        new_status: status,
        updated_at: new Date(),
        updated_by: req.user.id
      }
    });
    
  } catch (error) {
    logger.error('Update user status error:', error);
    next(error);
  }
});

module.exports = router;