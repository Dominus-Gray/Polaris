const express = require('express');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const { Integration } = require('../models/System');
const User = require('../models/User');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { 
  formatResponse, 
  formatErrorResponse
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

/**
 * GET /api/integrations/status
 * Get integration status overview
 */
router.get('/status', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const integrations = await Integration.findActiveByUser(userId);
    
    const statusOverview = {
      total_integrations: integrations.length,
      active_integrations: integrations.filter(i => i.status === 'connected').length,
      health_score: integrations.length > 0 
        ? Math.round(integrations.reduce((sum, i) => sum + (i.health_status?.score || 0), 0) / integrations.length)
        : 100,
      integrations: integrations.map(integration => ({
        id: integration.id,
        type: integration.integration_type,
        status: integration.status,
        health_score: integration.health_status?.score || 0,
        last_sync: integration.last_sync?.timestamp,
        created_at: integration.created_at
      }))
    };
    
    res.json({
      success: true,
      data: statusOverview
    });
    
  } catch (error) {
    logger.error('Get integration status error:', error);
    next(error);
  }
});

/**
 * GET /api/integrations/quickbooks/auth-url
 * Get QuickBooks OAuth authorization URL
 */
router.get('/quickbooks/auth-url', authenticateToken, async (req, res, next) => {
  try {
    const state = uuidv4();
    const redirectUri = `${process.env.APP_URL}/integrations/quickbooks/callback`;
    const scope = 'com.intuit.quickbooks.accounting';
    
    // In a real implementation, you'd use the QuickBooks OAuth2 client
    const authUrl = `https://appcenter.intuit.com/connect/oauth2?` +
      `client_id=YOUR_QUICKBOOKS_CLIENT_ID&` +
      `scope=${scope}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `access_type=offline&` +
      `state=${state}`;
    
    res.json({
      success: true,
      data: {
        auth_url: authUrl,
        state: state,
        expires_in: 3600 // 1 hour
      }
    });
    
  } catch (error) {
    logger.error('Get QuickBooks auth URL error:', error);
    next(error);
  }
});

/**
 * POST /api/integrations/quickbooks/connect
 * Connect QuickBooks integration
 */
router.post('/quickbooks/connect', authenticateToken, async (req, res, next) => {
  try {
    const { code, state, realmId } = req.body;
    const userId = req.user.id;
    
    if (!code || !realmId) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Missing required parameters',
          'Authorization code and realm ID are required'
        )
      );
    }
    
    // In a real implementation, you'd exchange the code for tokens
    // For now, create a mock integration
    const integration = new Integration({
      user_id: userId,
      integration_type: 'quickbooks',
      status: 'connected',
      connection_data: {
        company_id: realmId,
        base_uri: 'https://sandbox-quickbooks.api.intuit.com',
        scope: ['com.intuit.quickbooks.accounting']
      },
      settings: {
        auto_sync: false,
        sync_frequency: 'daily',
        data_types: ['customers', 'invoices', 'expenses', 'items'],
        notifications: true
      },
      health_status: {
        score: 100,
        last_check: new Date(),
        issues: []
      }
    });
    
    await integration.save();
    
    logger.info(`QuickBooks integration connected for user ${userId}`);
    
    res.json({
      success: true,
      message: 'QuickBooks integration connected successfully',
      data: {
        integration_id: integration.id,
        status: 'connected',
        company_id: realmId,
        connected_at: integration.created_at
      }
    });
    
  } catch (error) {
    logger.error('Connect QuickBooks integration error:', error);
    next(error);
  }
});

/**
 * GET /api/integrations/quickbooks/financial-health
 * Get financial health analysis from QuickBooks
 */
router.get('/quickbooks/financial-health', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const integration = await Integration.findOne({
      user_id: userId,
      integration_type: 'quickbooks',
      status: 'connected'
    });
    
    if (!integration) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'QuickBooks integration not found',
          'Please connect your QuickBooks account first'
        )
      );
    }
    
    // In a real implementation, you'd fetch actual financial data
    // For now, return mock financial health analysis
    const financialHealth = {
      overall_score: 8.7,
      scores: {
        cash_flow: 9.2,
        profitability: 8.5,
        liquidity: 8.8,
        debt_ratio: 7.9,
        growth_trend: 8.4
      },
      metrics: {
        current_ratio: 2.3,
        quick_ratio: 1.8,
        debt_to_equity: 0.35,
        gross_profit_margin: 0.42,
        net_profit_margin: 0.15,
        revenue_growth: 0.23
      },
      recommendations: [
        {
          category: 'Cash Flow',
          priority: 'medium',
          description: 'Consider implementing automated invoicing to improve cash flow timing',
          potential_impact: 'Reduce average collection time by 5-7 days'
        },
        {
          category: 'Profitability',
          priority: 'high',
          description: 'Review high-cost expense categories for optimization opportunities',
          potential_impact: 'Potential 3-5% increase in net margin'
        },
        {
          category: 'Growth',
          priority: 'low',
          description: 'Strong growth trajectory - maintain current customer acquisition strategy',
          potential_impact: 'Sustained 20%+ annual growth'
        }
      ],
      insights: [
        'Your business shows strong financial health with above-average performance in most areas',
        'Cash flow management is excellent with consistent positive trends',
        'Debt levels are well-managed and within industry standards',
        'Consider increasing investment in growth initiatives given strong foundation'
      ],
      last_updated: new Date(),
      data_period: {
        start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // 90 days ago
        end: new Date()
      }
    };
    
    res.json({
      success: true,
      data: financialHealth
    });
    
  } catch (error) {
    logger.error('Get QuickBooks financial health error:', error);
    next(error);
  }
});

/**
 * POST /api/integrations/quickbooks/sync
 * Sync data from QuickBooks
 */
router.post('/quickbooks/sync', authenticateToken, async (req, res, next) => {
  try {
    const { sync_type = 'all' } = req.body;
    const userId = req.user.id;
    
    const integration = await Integration.findOne({
      user_id: userId,
      integration_type: 'quickbooks',
      status: 'connected'
    });
    
    if (!integration) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'QuickBooks integration not found',
          'Please connect your QuickBooks account first'
        )
      );
    }
    
    // Mock sync results
    const syncResults = {
      all: { customers: 25, invoices: 48, expenses: 67, items: 15, total: 155 },
      customers: { customers: 25, total: 25 },
      invoices: { invoices: 48, total: 48 },
      expenses: { expenses: 67, total: 67 },
      items: { items: 15, total: 15 }
    };
    
    const result = syncResults[sync_type] || syncResults.all;
    
    // Update integration sync status
    integration.last_sync = {
      timestamp: new Date(),
      status: 'success',
      records_synced: result.total,
      errors: []
    };
    
    integration.usage_stats.api_calls_this_month += 1;
    integration.usage_stats.last_activity = new Date();
    
    await integration.save();
    
    logger.info(`QuickBooks sync completed for user ${userId}: ${result.total} records`);
    
    res.json({
      success: true,
      message: 'Data sync completed successfully',
      data: {
        sync_type,
        records_synced: result.total,
        breakdown: result,
        sync_timestamp: integration.last_sync.timestamp,
        next_auto_sync: integration.settings.auto_sync 
          ? new Date(Date.now() + 24 * 60 * 60 * 1000) // Next day
          : null
      }
    });
    
  } catch (error) {
    logger.error('QuickBooks sync error:', error);
    next(error);
  }
});

/**
 * GET /api/integrations/quickbooks/cash-flow-analysis
 * Get cash flow analysis from QuickBooks data
 */
router.get('/quickbooks/cash-flow-analysis', authenticateToken, async (req, res, next) => {
  try {
    const { days = 30 } = req.query;
    const userId = req.user.id;
    
    const integration = await Integration.findOne({
      user_id: userId,
      integration_type: 'quickbooks',
      status: 'connected'
    });
    
    if (!integration) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'QuickBooks integration not found',
          'Please connect your QuickBooks account first'
        )
      );
    }
    
    // Mock cash flow analysis
    const cashFlowAnalysis = {
      period_days: parseInt(days),
      analysis_date: new Date(),
      current_position: {
        cash_on_hand: 45000,
        accounts_receivable: 22000,
        accounts_payable: 12000,
        total_liquid_assets: 75000
      },
      period_summary: {
        total_inflows: 85000,
        total_outflows: 52000,
        net_cash_flow: 33000,
        average_daily_flow: Math.round(33000 / parseInt(days))
      },
      trends: {
        inflow_trend: 'increasing',
        outflow_trend: 'stable',
        net_trend: 'positive',
        trend_percentage: 15.2
      },
      weekly_projections: [
        { week: 1, projected_inflow: 18000, projected_outflow: 12000, net_flow: 6000 },
        { week: 2, projected_inflow: 22000, projected_outflow: 14000, net_flow: 8000 },
        { week: 3, projected_inflow: 19000, projected_outflow: 13000, net_flow: 6000 },
        { week: 4, projected_inflow: 21000, projected_outflow: 15000, net_flow: 6000 }
      ],
      recommendations: [
        {
          type: 'opportunity',
          priority: 'medium',
          description: 'Strong cash position allows for strategic investments or debt reduction',
          action: 'Consider investing excess cash in growth initiatives'
        },
        {
          type: 'risk',
          priority: 'low',
          description: 'Accounts receivable turnover could be improved',
          action: 'Implement automated follow-up for overdue invoices'
        }
      ],
      key_metrics: {
        cash_conversion_cycle: 35, // days
        days_sales_outstanding: 28,
        days_payable_outstanding: 15,
        cash_ratio: 3.75
      }
    };
    
    res.json({
      success: true,
      data: cashFlowAnalysis
    });
    
  } catch (error) {
    logger.error('Get QuickBooks cash flow analysis error:', error);
    next(error);
  }
});

/**
 * DELETE /api/integrations/:integrationId
 * Disconnect an integration
 */
router.delete('/:integrationId', authenticateToken, async (req, res, next) => {
  try {
    const { integrationId } = req.params;
    const userId = req.user.id;
    
    const integration = await Integration.findOne({
      id: integrationId,
      user_id: userId
    });
    
    if (!integration) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Integration not found',
          'The specified integration does not exist'
        )
      );
    }
    
    // Update status instead of deleting for audit trail
    integration.status = 'disconnected';
    integration.connection_data = {}; // Clear sensitive data
    integration.updated_at = new Date();
    
    await integration.save();
    
    logger.info(`Integration ${integrationId} disconnected by user ${userId}`);
    
    res.json({
      success: true,
      message: 'Integration disconnected successfully',
      data: {
        integration_id: integrationId,
        status: 'disconnected',
        disconnected_at: new Date()
      }
    });
    
  } catch (error) {
    logger.error('Disconnect integration error:', error);
    next(error);
  }
});

/**
 * PUT /api/integrations/:integrationId/settings
 * Update integration settings
 */
router.put('/:integrationId/settings', authenticateToken, async (req, res, next) => {
  try {
    const { integrationId } = req.params;
    const { settings } = req.body;
    const userId = req.user.id;
    
    const integration = await Integration.findOne({
      id: integrationId,
      user_id: userId
    });
    
    if (!integration) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Integration not found',
          'The specified integration does not exist'
        )
      );
    }
    
    // Update settings
    integration.settings = { ...integration.settings, ...settings };
    integration.updated_at = new Date();
    
    await integration.save();
    
    logger.info(`Integration settings updated for ${integrationId}`);
    
    res.json({
      success: true,
      message: 'Integration settings updated successfully',
      data: {
        integration_id: integrationId,
        settings: integration.settings,
        updated_at: integration.updated_at
      }
    });
    
  } catch (error) {
    logger.error('Update integration settings error:', error);
    next(error);
  }
});

module.exports = router;