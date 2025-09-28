const express = require('express');
const User = require('../models/User');
const { Analytics } = require('../models/System');
const { AssessmentSession } = require('../models/Assessment');
const { AgencyLicense } = require('../models/Agency');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { 
  formatResponse, 
  formatErrorResponse,
  getPaginationMeta
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

/**
 * GET /api/admin/system/stats
 * Get system statistics (navigators only)
 */
router.get('/system/stats', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    // Get user statistics
    const userStats = await User.aggregate([
      {
        $group: {
          _id: '$role',
          count: { $sum: 1 },
          approved: {
            $sum: { $cond: [{ $eq: ['$status', 'approved'] }, 1, 0] }
          },
          pending: {
            $sum: { $cond: [{ $eq: ['$status', 'pending'] }, 1, 0] }
          }
        }
      }
    ]);
    
    // Get activity statistics for last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const activityStats = {
      new_users_30d: await User.countDocuments({ 
        created_at: { $gte: thirtyDaysAgo } 
      }),
      assessments_completed_30d: await AssessmentSession.countDocuments({ 
        status: 'completed',
        completed_at: { $gte: thirtyDaysAgo } 
      }),
      licenses_generated_30d: await AgencyLicense.countDocuments({ 
        created_at: { $gte: thirtyDaysAgo } 
      }),
      total_events_30d: await Analytics.countDocuments({ 
        timestamp: { $gte: thirtyDaysAgo } 
      })
    };
    
    // System health metrics
    const systemHealth = {
      uptime_seconds: Math.floor(process.uptime()),
      memory_usage: process.memoryUsage(),
      cpu_usage: process.cpuUsage(),
      node_version: process.version,
      platform: process.platform
    };
    
    // Database statistics
    const dbStats = {
      total_users: await User.countDocuments(),
      total_assessments: await AssessmentSession.countDocuments(),
      total_licenses: await AgencyLicense.countDocuments(),
      total_events: await Analytics.countDocuments()
    };
    
    const stats = {
      user_statistics: userStats,
      activity_statistics: activityStats,
      system_health: systemHealth,
      database_statistics: dbStats,
      generated_at: new Date()
    };
    
    res.json({
      success: true,
      data: stats
    });
    
  } catch (error) {
    logger.error('Get system stats error:', error);
    next(error);
  }
});

/**
 * GET /api/admin/users
 * Get all users with advanced filtering
 */
router.get('/users', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      role, 
      status, 
      search,
      sort_by = 'created_at',
      sort_order = 'desc',
      created_after,
      created_before
    } = req.query;
    
    // Build query
    const query = {};
    
    if (role && role !== 'all') {
      query.role = role;
    }
    
    if (status && status !== 'all') {
      query.status = status;
    }
    
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } },
        { company_name: { $regex: search, $options: 'i' } }
      ];
    }
    
    if (created_after || created_before) {
      query.created_at = {};
      if (created_after) query.created_at.$gte = new Date(created_after);
      if (created_before) query.created_at.$lte = new Date(created_before);
    }
    
    // Build sort
    const sortObj = {};
    sortObj[sort_by] = sort_order === 'desc' ? -1 : 1;
    
    const total = await User.countDocuments(query);
    const users = await User.find(query)
      .sort(sortObj)
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .select('-password -__v -password_reset_token -two_factor_secret');
    
    res.json({
      success: true,
      data: {
        users: users.map(user => ({
          ...user.toSafeObject(),
          last_login: user.last_login,
          failed_login_attempts: user.failed_login_attempts
        })),
        pagination: getPaginationMeta(total, page, limit),
        filters: {
          role,
          status,
          search,
          sort_by,
          sort_order
        }
      }
    });
    
  } catch (error) {
    logger.error('Get admin users error:', error);
    next(error);
  }
});

/**
 * POST /api/admin/users/bulk-action
 * Perform bulk actions on users
 */
router.post('/users/bulk-action', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    const { user_ids, action, reason } = req.body;
    
    if (!user_ids || !Array.isArray(user_ids) || user_ids.length === 0) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'User IDs required',
          'Please provide an array of user IDs'
        )
      );
    }
    
    const validActions = ['approve', 'reject', 'suspend', 'activate', 'delete'];
    if (!validActions.includes(action)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid action',
          `Action must be one of: ${validActions.join(', ')}`
        )
      );
    }
    
    let updateData = {};
    let statusMessage = '';
    
    switch (action) {
      case 'approve':
        updateData = { status: 'approved' };
        statusMessage = 'approved';
        break;
      case 'reject':
        updateData = { status: 'rejected', rejection_reason: reason };
        statusMessage = 'rejected';
        break;
      case 'suspend':
        updateData = { status: 'suspended', suspension_reason: reason };
        statusMessage = 'suspended';
        break;
      case 'activate':
        updateData = { status: 'approved' };
        statusMessage = 'activated';
        break;
      case 'delete':
        updateData = { status: 'deleted', deleted_at: new Date() };
        statusMessage = 'deleted';
        break;
    }
    
    // Perform bulk update
    const result = await User.updateMany(
      { id: { $in: user_ids } },
      { 
        $set: {
          ...updateData,
          bulk_action_by: req.user.id,
          bulk_action_at: new Date()
        }
      }
    );
    
    logger.info(`Bulk action '${action}' performed on ${result.modifiedCount} users by ${req.user.email}`);
    
    res.json({
      success: true,
      message: `Successfully ${statusMessage} ${result.modifiedCount} user(s)`,
      data: {
        action,
        affected_count: result.modifiedCount,
        total_requested: user_ids.length,
        performed_by: req.user.id,
        performed_at: new Date()
      }
    });
    
  } catch (error) {
    logger.error('Bulk user action error:', error);
    next(error);
  }
});

/**
 * POST /api/admin/users/:userId/action
 * Perform action on specific user
 */
router.post('/users/:userId/action', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { action, reason, notes } = req.body;
    
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
    
    const validActions = ['approve', 'reject', 'suspend', 'activate', 'reset_password', 'unlock'];
    if (!validActions.includes(action)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid action',
          `Action must be one of: ${validActions.join(', ')}`
        )
      );
    }
    
    const previousStatus = user.status;
    
    switch (action) {
      case 'approve':
        user.status = 'approved';
        break;
      case 'reject':
        user.status = 'rejected';
        user.rejection_reason = reason;
        break;
      case 'suspend':
        user.status = 'suspended';
        user.suspension_reason = reason;
        break;
      case 'activate':
        user.status = 'approved';
        break;
      case 'reset_password':
        user.password_reset_token = require('crypto').randomBytes(32).toString('hex');
        user.password_reset_expires = new Date(Date.now() + 3600000); // 1 hour
        break;
      case 'unlock':
        user.failed_login_attempts = 0;
        user.account_locked_until = null;
        break;
    }
    
    user.admin_action_by = req.user.id;
    user.admin_action_at = new Date();
    user.admin_notes = notes;
    
    await user.save();
    
    logger.info(`Admin action '${action}' performed on user ${user.email} by ${req.user.email}`);
    
    res.json({
      success: true,
      message: `Action '${action}' performed successfully`,
      data: {
        user_id: userId,
        action,
        previous_status: previousStatus,
        new_status: user.status,
        performed_by: req.user.id,
        performed_at: new Date()
      }
    });
    
  } catch (error) {
    logger.error('Admin user action error:', error);
    next(error);
  }
});

/**
 * GET /api/admin/audit-logs
 * Get system audit logs
 */
router.get('/audit-logs', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    const { 
      page = 1, 
      limit = 50, 
      event_type,
      user_id,
      start_date,
      end_date
    } = req.query;
    
    // Build query for analytics events (our audit log)
    const query = {};
    
    if (event_type) {
      query.event_type = event_type;
    }
    
    if (user_id) {
      query.user_id = user_id;
    }
    
    if (start_date || end_date) {
      query.timestamp = {};
      if (start_date) query.timestamp.$gte = new Date(start_date);
      if (end_date) query.timestamp.$lte = new Date(end_date);
    }
    
    const total = await Analytics.countDocuments(query);
    const logs = await Analytics.find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    // Enhance logs with user information
    const userIds = [...new Set(logs.map(log => log.user_id).filter(Boolean))];
    const users = await User.find({ id: { $in: userIds } })
      .select('id name email role');
    const userMap = users.reduce((map, user) => {
      map[user.id] = user;
      return map;
    }, {});
    
    const enhancedLogs = logs.map(log => ({
      id: log.id,
      event_type: log.event_type,
      timestamp: log.timestamp,
      user: log.user_id ? {
        id: log.user_id,
        name: userMap[log.user_id]?.name || 'Unknown User',
        email: userMap[log.user_id]?.email || 'Unknown Email',
        role: userMap[log.user_id]?.role || 'unknown'
      } : null,
      event_data: log.event_data,
      ip_address: log.ip_address,
      user_agent: log.user_agent,
      session_id: log.session_id
    }));
    
    res.json({
      success: true,
      data: {
        logs: enhancedLogs,
        pagination: getPaginationMeta(total, page, limit),
        summary: {
          total_events: total,
          date_range: {
            start: start_date || null,
            end: end_date || null
          },
          filtered_by: {
            event_type: event_type || null,
            user_id: user_id || null
          }
        }
      }
    });
    
  } catch (error) {
    logger.error('Get audit logs error:', error);
    next(error);
  }
});

/**
 * GET /api/admin/system/health
 * Get detailed system health information
 */
router.get('/system/health', authenticateToken, requireRole('navigator', 'admin'), async (req, res, next) => {
  try {
    // Database connectivity check
    const dbHealth = {
      status: 'healthy',
      connection: 'active',
      response_time_ms: null
    };
    
    try {
      const start = Date.now();
      await User.findOne().limit(1);
      dbHealth.response_time_ms = Date.now() - start;
    } catch (dbError) {
      dbHealth.status = 'unhealthy';
      dbHealth.connection = 'failed';
      dbHealth.error = dbError.message;
    }
    
    // Memory and CPU metrics
    const memoryUsage = process.memoryUsage();
    const systemMetrics = {
      uptime_seconds: Math.floor(process.uptime()),
      memory: {
        rss_mb: Math.round(memoryUsage.rss / 1024 / 1024),
        heap_used_mb: Math.round(memoryUsage.heapUsed / 1024 / 1024),
        heap_total_mb: Math.round(memoryUsage.heapTotal / 1024 / 1024),
        external_mb: Math.round(memoryUsage.external / 1024 / 1024)
      },
      cpu_usage: process.cpuUsage(),
      node_version: process.version,
      platform: process.platform,
      arch: process.arch
    };
    
    // Service status checks
    const services = {
      database: dbHealth,
      redis: {
        status: 'not_configured', // Would check Redis if configured
        connection: 'n/a'
      },
      email: {
        status: 'not_configured', // Would check SMTP if configured
        connection: 'n/a'
      },
      stripe: {
        status: process.env.STRIPE_API_KEY ? 'configured' : 'not_configured',
        connection: 'n/a'
      }
    };
    
    // Overall health score
    const healthyServices = Object.values(services).filter(s => 
      s.status === 'healthy' || s.status === 'configured'
    ).length;
    const totalServices = Object.keys(services).length;
    const healthScore = Math.round((healthyServices / totalServices) * 100);
    
    const healthStatus = {
      overall_status: healthScore >= 75 ? 'healthy' : healthScore >= 50 ? 'warning' : 'critical',
      health_score: healthScore,
      system_metrics: systemMetrics,
      services,
      checks_performed_at: new Date(),
      environment: process.env.NODE_ENV || 'development'
    };
    
    res.json({
      success: true,
      data: healthStatus
    });
    
  } catch (error) {
    logger.error('Get system health error:', error);
    
    res.status(500).json({
      success: false,
      data: {
        overall_status: 'critical',
        health_score: 0,
        error: error.message,
        checks_performed_at: new Date()
      }
    });
  }
});

module.exports = router;