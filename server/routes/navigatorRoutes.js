const express = require('express')
const router = express.Router()
const { authenticateToken, requireRole } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger
const { v4: uuidv4 } = require('uuid')

// Import models
const EvidencePackage = require('../models/EvidencePackage')
const User = require('../models/User')
const Agency = require('../models/Agency')

/**
 * GET /api/navigator/evidence/pending
 * Get evidence packages pending review
 */
router.get('/evidence/pending', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const packages = await EvidencePackage.find({
      status: 'pending_review'
    }).sort({ submitted_at: -1 })

    // Enrich with client information
    const enrichedPackages = await Promise.all(
      packages.map(async (pkg) => {
        const client = await User.findOne({ id: pkg.user_id })
        return {
          ...pkg.toObject(),
          client_info: {
            id: client?.id || pkg.user_id,
            name: client?.name || 'Business Client',
            email: client?.email || 'unknown@example.com',
            company_name: client?.company_name || 'Business Company'
          }
        }
      })
    )

    res.json({
      success: true,
      data: {
        packages: enrichedPackages,
        total_pending: enrichedPackages.length
      }
    })

  } catch (error) {
    logger.error('Get pending evidence error:', error)
    next(error)
  }
})

/**
 * POST /api/navigator/evidence/{evidence_id}/review
 * Review evidence package
 */
router.post('/evidence/:evidence_id/review', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { evidence_id } = req.params
    const { decision, navigator_notes } = req.body
    const navigatorId = req.user.id

    if (!['approved', 'rejected'].includes(decision)) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Invalid decision', 'Decision must be approved or rejected')
      )
    }

    // Find evidence package
    const evidencePackage = await EvidencePackage.findOne({ package_id: evidence_id })
    if (!evidencePackage) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Evidence package not found')
      )
    }

    // Update evidence package
    evidencePackage.status = decision
    evidencePackage.navigator_assigned = navigatorId
    evidencePackage.review_notes = navigator_notes
    evidencePackage.reviewed_at = new Date()
    await evidencePackage.save()

    // If approved, update client's assessment progress
    if (decision === 'approved') {
      // Logic to update client's tier completion status
      logger.info(`Evidence approved for client ${evidencePackage.user_id}, area ${evidencePackage.area_id}`)
    } else {
      // Send remediation notice to client
      logger.info(`Evidence requires remediation for client ${evidencePackage.user_id}`)
    }

    res.json({
      success: true,
      data: {
        package_id: evidence_id,
        decision,
        navigator_notes,
        reviewed_at: evidencePackage.reviewed_at
      }
    })

  } catch (error) {
    logger.error('Evidence review error:', error)
    next(error)
  }
})

/**
 * GET /api/navigator/agencies/pending
 * Get agencies pending approval
 */
router.get('/agencies/pending', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const pendingAgencies = await Agency.find({
      status: 'pending'
    }).sort({ created_at: -1 })

    res.json({
      success: true,
      data: {
        agencies: pendingAgencies,
        total_pending: pendingAgencies.length
      }
    })

  } catch (error) {
    logger.error('Get pending agencies error:', error)
    next(error)
  }
})

/**
 * POST /api/navigator/agencies/approve
 * Approve agency
 */
router.post('/agencies/approve', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { agency_id, approval_notes } = req.body
    const navigatorId = req.user.id

    const agency = await Agency.findOne({ id: agency_id })
    if (!agency) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Agency not found')
      )
    }

    // Approve agency
    agency.status = 'approved'
    agency.approved_by = navigatorId
    agency.approval_notes = approval_notes
    agency.approved_at = new Date()
    await agency.save()

    logger.info(`Agency approved: ${agency_id} by navigator ${navigatorId}`)

    res.json({
      success: true,
      data: {
        agency_id,
        status: 'approved',
        approved_at: agency.approved_at
      }
    })

  } catch (error) {
    logger.error('Agency approval error:', error)
    next(error)
  }
})

/**
 * GET /api/navigator/analytics/resources
 * Get navigator analytics for resource usage
 */
router.get('/analytics/resources', authenticateToken, requireRole('navigator'), async (req, res, next) => {
  try {
    const { since_days = 30 } = req.query
    const sinceDate = new Date(Date.now() - parseInt(since_days) * 24 * 60 * 60 * 1000)

    // Mock analytics data for navigator dashboard
    const analyticsData = {
      since: sinceDate.toISOString(),
      total: 156,
      by_area: [
        { area_id: 'area1', area_name: 'Business Formation & Registration', count: 24 },
        { area_id: 'area2', area_name: 'Financial Operations & Management', count: 31 },
        { area_id: 'area5', area_name: 'Technology & Security Infrastructure', count: 18 },
        { area_id: 'area4', area_name: 'Quality Management & Standards', count: 15 }
      ],
      last7: [12, 18, 25, 19, 22, 16, 14]
    }

    res.json({
      success: true,
      data: analyticsData
    })

  } catch (error) {
    logger.error('Navigator analytics error:', error)
    next(error)
  }
})

module.exports = router