const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { 
  AgencyLicense, 
  AgencyTierConfiguration, 
  AgencySubscription, 
  AgencyUsage 
} = require('../models/Agency');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse, 
  generateLicenseCode,
  getPaginationMeta
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

/**
 * GET /api/agency/dashboard
 * Get agency dashboard data
 */
router.get('/dashboard', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    
    // Get license statistics
    const licenseStats = {
      total_generated: await AgencyLicense.countDocuments({ agency_user_id: agencyId }),
      available: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'active',
        expires_at: { $gt: new Date() }
      }),
      used: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'used'
      }),
      expired: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'active',
        expires_at: { $lte: new Date() }
      })
    };
    
    // Get client count (users who used this agency's licenses)
    const clientCount = await AgencyLicense.distinct('used_by_client_id', {
      agency_user_id: agencyId,
      status: 'used'
    }).length;
    
    // Get subscription info
    const subscription = await AgencySubscription.findActiveByAgency(agencyId);
    
    // Get recent usage
    const recentUsage = await AgencyUsage.find({ agency_id: agencyId })
      .sort({ created_at: -1 })
      .limit(10);
    
    const dashboardData = {
      agency: req.user.toSafeObject(),
      license_stats: licenseStats,
      client_count: clientCount,
      subscription: subscription ? {
        plan: subscription.plan,
        status: subscription.status,
        current_period_end: subscription.current_period_end,
        usage_current_period: subscription.usage_current_period
      } : null,
      recent_activity: recentUsage.map(usage => ({
        type: usage.usage_type,
        quantity: usage.quantity,
        created_at: usage.created_at,
        billable_amount: usage.billable_amount
      }))
    };
    
    res.json({
      success: true,
      data: dashboardData
    });
    
  } catch (error) {
    logger.error('Get agency dashboard error:', error);
    next(error);
  }
});

/**
 * GET /api/agency/licenses/stats
 * Get license statistics
 */
router.get('/licenses/stats', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    
    const stats = {
      total_generated: await AgencyLicense.countDocuments({ agency_user_id: agencyId }),
      available: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'active',
        expires_at: { $gt: new Date() }
      }),
      used: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'used'
      }),
      expired: await AgencyLicense.countDocuments({ 
        agency_user_id: agencyId, 
        status: 'active',
        expires_at: { $lte: new Date() }
      })
    };
    
    res.json({
      success: true,
      data: stats
    });
    
  } catch (error) {
    logger.error('Get license stats error:', error);
    next(error);
  }
});

/**
 * GET /api/agency/licenses
 * Get agency licenses
 */
router.get('/licenses', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    const { page = 1, limit = 20, status = 'all' } = req.query;
    
    const query = { agency_user_id: agencyId };
    if (status !== 'all') {
      query.status = status;
    }
    
    const total = await AgencyLicense.countDocuments(query);
    const licenses = await AgencyLicense.find(query)
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    res.json({
      success: true,
      data: {
        licenses: licenses.map(license => ({
          id: license.id,
          license_code: license.license_code,
          status: license.status,
          created_at: license.created_at,
          expires_at: license.expires_at,
          used_at: license.used_at,
          used_by_client_id: license.used_by_client_id
        })),
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get agency licenses error:', error);
    next(error);
  }
});

/**
 * POST /api/agency/licenses/generate
 * Generate new licenses
 */
router.post('/licenses/generate', authenticateToken, requireRole('agency'), validate(schemas.licenseGeneration), async (req, res, next) => {
  try {
    const { quantity, expires_days = 365 } = req.body;
    const agencyId = req.user.id;
    
    if (quantity <= 0 || quantity > 100) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid quantity',
          'Quantity must be between 1 and 100'
        )
      );
    }
    
    // Check subscription limits
    const subscription = await AgencySubscription.findActiveByAgency(agencyId);
    if (subscription && subscription.hasExceededLimit('licenses_generated')) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'License generation limit reached',
          'You have reached your monthly license generation limit'
        )
      );
    }
    
    // Generate licenses
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + expires_days);
    
    const licenses = [];
    for (let i = 0; i < quantity; i++) {
      const licenseCode = generateLicenseCode();
      
      // Ensure unique license code
      const existingLicense = await AgencyLicense.findOne({ license_code: licenseCode });
      if (existingLicense) {
        i--; // Retry with new code
        continue;
      }
      
      const license = new AgencyLicense({
        license_code: licenseCode,
        agency_user_id: agencyId,
        agency_id: agencyId,
        expires_at: expiresAt,
        metadata: {
          batch_id: uuidv4(),
          generation_source: 'agency_dashboard'
        }
      });
      
      await license.save();
      licenses.push({
        license_code: licenseCode,
        expires_at: expiresAt
      });
    }
    
    // Update subscription usage
    if (subscription) {
      await subscription.incrementUsage('licenses_generated', quantity);
    }
    
    // Log usage
    await AgencyUsage.create({
      agency_id: agencyId,
      period_start: new Date(),
      period_end: new Date(),
      usage_type: 'license_generation',
      quantity,
      billable_amount: quantity * 5.0 // $5 per license
    });
    
    logger.info(`Generated ${quantity} licenses for agency ${agencyId}`);
    
    res.status(201).json({
      success: true,
      message: `Successfully generated ${quantity} license codes`,
      data: {
        licenses,
        usage_update: {
          monthly_limit: subscription?.usage_limits?.licenses_per_month || 10,
          used_this_month: (subscription?.usage_current_period?.licenses_generated || 0) + quantity,
          remaining: Math.max(0, (subscription?.usage_limits?.licenses_per_month || 10) - ((subscription?.usage_current_period?.licenses_generated || 0) + quantity))
        }
      }
    });
    
  } catch (error) {
    logger.error('Generate licenses error:', error);
    next(error);
  }
});

/**
 * GET /api/agency/tier-configuration
 * Get agency tier configuration
 */
router.get('/tier-configuration', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    
    let config = await AgencyTierConfiguration.findOne({ agency_id: agencyId });
    
    if (!config) {
      // Create default configuration
      const defaultTierAccess = {};
      for (let i = 1; i <= 10; i++) {
        defaultTierAccess[`area${i}`] = 1;
      }
      
      config = new AgencyTierConfiguration({
        agency_id: agencyId,
        tier_access_levels: defaultTierAccess
      });
      
      await config.save();
    }
    
    res.json({
      success: true,
      data: {
        tier_configuration: {
          agency_id: config.agency_id,
          tier_access_levels: config.tier_access_levels,
          pricing_per_tier: config.pricing_per_tier,
          subscription_model: config.subscription_model,
          monthly_limits: config.monthly_limits,
          features_enabled: config.features_enabled,
          branding: config.branding
        }
      }
    });
    
  } catch (error) {
    logger.error('Get tier configuration error:', error);
    next(error);
  }
});

/**
 * PUT /api/agency/tier-configuration
 * Update agency tier configuration
 */
router.put('/tier-configuration', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    const { 
      tier_access_levels,
      pricing_per_tier,
      subscription_model,
      monthly_limits,
      features_enabled,
      branding
    } = req.body;
    
    const updateData = {};
    if (tier_access_levels) updateData.tier_access_levels = tier_access_levels;
    if (pricing_per_tier) updateData.pricing_per_tier = pricing_per_tier;
    if (subscription_model) updateData.subscription_model = subscription_model;
    if (monthly_limits) updateData.monthly_limits = monthly_limits;
    if (features_enabled) updateData.features_enabled = features_enabled;
    if (branding) updateData.branding = branding;
    
    updateData.updated_at = new Date();
    
    const config = await AgencyTierConfiguration.findOneAndUpdate(
      { agency_id: agencyId },
      { $set: updateData },
      { new: true, upsert: true }
    );
    
    logger.info(`Tier configuration updated for agency ${agencyId}`);
    
    res.json({
      success: true,
      message: 'Tier configuration updated successfully',
      data: {
        tier_configuration: config
      }
    });
    
  } catch (error) {
    logger.error('Update tier configuration error:', error);
    next(error);
  }
});

/**
 * POST /api/agency/tier-configuration/upgrade
 * Upgrade client tier access
 */
router.post('/tier-configuration/upgrade', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const { client_id, area_id, new_tier_level } = req.body;
    const agencyId = req.user.id;
    
    if (!client_id || !area_id || !new_tier_level) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Missing required fields',
          'client_id, area_id, and new_tier_level are required'
        )
      );
    }
    
    if (new_tier_level < 1 || new_tier_level > 3) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid tier level',
          'Tier level must be between 1 and 3'
        )
      );
    }
    
    // Verify the client is associated with this agency
    const client = await User.findOne({ id: client_id, role: 'client' });
    if (!client) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Client not found',
          'The specified client does not exist'
        )
      );
    }
    
    // Verify client's license is from this agency
    const license = await AgencyLicense.findOne({ 
      license_code: client.license_code,
      agency_user_id: agencyId
    });
    
    if (!license) {
      return res.status(403).json(
        formatErrorResponse(
          'POL-1003',
          'Access denied',
          'This client is not associated with your agency'
        )
      );
    }
    
    // Update tier configuration for this client
    let config = await AgencyTierConfiguration.findOne({ agency_id: agencyId });
    if (!config) {
      // Create default configuration
      const defaultTierAccess = {};
      for (let i = 1; i <= 10; i++) {
        defaultTierAccess[`area${i}`] = 1;
      }
      
      config = new AgencyTierConfiguration({
        agency_id: agencyId,
        tier_access_levels: defaultTierAccess
      });
    }
    
    // Update the specific area tier level
    config.tier_access_levels.set(area_id, new_tier_level);
    config.updated_at = new Date();
    await config.save();
    
    // Log the upgrade
    await AgencyUsage.create({
      agency_id: agencyId,
      period_start: new Date(),
      period_end: new Date(),
      usage_type: 'tier_upgrade',
      quantity: 1,
      client_id: client_id,
      metadata: {
        area_id,
        new_tier_level,
        previous_tier_level: config.tier_access_levels.get(area_id) || 1
      },
      billable_amount: (new_tier_level - 1) * 25.0 // $25 per tier upgrade
    });
    
    logger.info(`Tier upgrade: Client ${client_id} upgraded to tier ${new_tier_level} in ${area_id} by agency ${agencyId}`);
    
    res.json({
      success: true,
      message: 'Client tier access upgraded successfully',
      data: {
        client_id,
        area_id,
        new_tier_level,
        upgraded_at: new Date()
      }
    });
    
  } catch (error) {
    logger.error('Upgrade client tier error:', error);
    next(error);
  }
});

/**
 * GET /api/agency/billing/usage
 * Get billing and usage information
 */
router.get('/billing/usage', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id;
    const { period = 'current' } = req.query;
    
    // Get current period usage
    const currentMonth = new Date();
    currentMonth.setDate(1);
    currentMonth.setHours(0, 0, 0, 0);
    
    const nextMonth = new Date(currentMonth);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    
    const usage = await AgencyUsage.find({
      agency_id: agencyId,
      created_at: {
        $gte: currentMonth,
        $lt: nextMonth
      }
    });
    
    // Calculate usage by type
    const usageByType = usage.reduce((acc, item) => {
      if (!acc[item.usage_type]) {
        acc[item.usage_type] = {
          quantity: 0,
          billable_amount: 0
        };
      }
      acc[item.usage_type].quantity += item.quantity;
      acc[item.usage_type].billable_amount += item.billable_amount;
      return acc;
    }, {});
    
    const totalBillableAmount = usage.reduce((sum, item) => sum + item.billable_amount, 0);
    
    // Get subscription info
    const subscription = await AgencySubscription.findActiveByAgency(agencyId);
    
    res.json({
      success: true,
      data: {
        period: {
          start: currentMonth,
          end: nextMonth
        },
        usage_by_type: usageByType,
        total_billable_amount: totalBillableAmount,
        subscription: subscription ? {
          plan: subscription.plan,
          status: subscription.status,
          current_period_end: subscription.current_period_end,
          usage_limits: subscription.usage_limits,
          usage_current_period: subscription.usage_current_period
        } : null,
        usage_details: usage.map(item => ({
          type: item.usage_type,
          quantity: item.quantity,
          billable_amount: item.billable_amount,
          created_at: item.created_at,
          metadata: item.metadata
        }))
      }
    });
    
  } catch (error) {
    logger.error('Get billing usage error:', error);
    next(error);
  }
});

module.exports = router;