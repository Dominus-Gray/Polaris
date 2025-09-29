const express = require('express')
const router = express.Router()
const { authenticateToken, requireRole } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger
const { v4: uuidv4 } = require('uuid')

// Import models
const Agency = require('../models/Agency')
const User = require('../models/User')

/**
 * POST /api/agency/licenses/generate
 * Generate license codes for client onboarding
 */
router.post('/licenses/generate', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const { quantity = 5, expires_days = 60 } = req.body
    const agencyId = req.user.id

    if (quantity < 1 || quantity > 25) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Invalid quantity', 'Quantity must be between 1 and 25')
      )
    }

    // Generate license codes
    const licenseCodes = []
    for (let i = 0; i < quantity; i++) {
      const code = Math.random().toString().slice(2, 12) // 10-digit code
      licenseCodes.push({
        code,
        agency_id: agencyId,
        generated_at: new Date(),
        expires_at: new Date(Date.now() + expires_days * 24 * 60 * 60 * 1000),
        used_by: null,
        used_at: null,
        status: 'available'
      })
    }

    // Save license codes (simplified for demo)
    logger.info(`Generated ${quantity} license codes for agency ${agencyId}`)

    res.json({
      success: true,
      data: {
        licenses: licenseCodes.map(l => l.code),
        quantity,
        expires_days,
        message: `Successfully generated ${quantity} license codes`,
        usage_update: {
          monthly_usage: quantity,
          monthly_limit: 50
        }
      }
    })

  } catch (error) {
    logger.error('License generation error:', error)
    next(error)
  }
})

/**
 * GET /api/agency/licenses/stats
 * Get license usage statistics
 */
router.get('/licenses/stats', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id

    // Mock license statistics
    const stats = {
      total_generated: 47,
      available: 23,
      used: 18,
      expired: 6,
      monthly_limit: 50,
      current_month_usage: 12
    }

    res.json({
      success: true,
      data: stats
    })

  } catch (error) {
    logger.error('License stats error:', error)
    next(error)
  }
})

/**
 * GET /api/agency/licenses
 * Get all license codes for agency
 */
router.get('/licenses', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const agencyId = req.user.id

    // Mock license codes data
    const licenses = [
      {
        code: '1234567890',
        generated_at: '2025-01-20T10:00:00Z',
        expires_at: '2025-03-21T10:00:00Z',
        used_by: null,
        used_at: null,
        status: 'available'
      },
      {
        code: '9876543210',
        generated_at: '2025-01-19T14:30:00Z',
        expires_at: '2025-03-20T14:30:00Z',
        used_by: 'client.qa@polaris.example.com',
        used_at: '2025-01-25T09:15:00Z',
        status: 'used'
      }
    ]

    res.json({
      success: true,
      data: {
        licenses,
        total: licenses.length
      }
    })

  } catch (error) {
    logger.error('Get licenses error:', error)
    next(error)
  }
})

/**
 * POST /api/agency/tier-configuration
 * Configure tier access for clients
 */
router.post('/tier-configuration', authenticateToken, requireRole('agency'), async (req, res, next) => {
  try {
    const { client_id, tier_levels } = req.body
    const agencyId = req.user.id

    // Update client tier access
    const client = await User.findOne({ id: client_id })
    if (!client) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Client not found')
      )
    }

    // Update tier configuration (simplified)
    logger.info(`Tier configuration updated for client ${client_id} by agency ${agencyId}`)

    res.json({
      success: true,
      data: {
        client_id,
        tier_levels,
        updated_at: new Date()
      }
    })

  } catch (error) {
    logger.error('Tier configuration error:', error)
    next(error)
  }
})

module.exports = router