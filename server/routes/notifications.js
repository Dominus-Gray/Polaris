const express = require('express')
const router = express.Router()
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger
const { v4: uuidv4 } = require('uuid')

// In-memory notification storage (in production, use database)
let notifications = []

/**
 * POST /api/notifications/send
 * Send notification to user
 */
router.post('/send', authenticateToken, async (req, res, next) => {
  try {
    const { 
      recipient_id, 
      title, 
      message, 
      type = 'info',
      action_url,
      priority = 'normal'
    } = req.body
    const senderId = req.user.id

    const notification = {
      id: uuidv4(),
      recipient_id,
      sender_id: senderId,
      title,
      message,
      type,
      action_url,
      priority,
      status: 'unread',
      created_at: new Date(),
      read_at: null
    }

    notifications.push(notification)

    logger.info(`Notification sent to user ${recipient_id}: ${title}`)

    res.json({
      success: true,
      data: {
        notification_id: notification.id,
        status: 'sent',
        created_at: notification.created_at
      }
    })

  } catch (error) {
    logger.error('Send notification error:', error)
    next(error)
  }
})

/**
 * GET /api/notifications/my
 * Get user's notifications
 */
router.get('/my', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id
    const { status, limit = 20 } = req.query

    let userNotifications = notifications.filter(n => n.recipient_id === userId)
    
    if (status) {
      userNotifications = userNotifications.filter(n => n.status === status)
    }

    userNotifications = userNotifications
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, parseInt(limit))

    // Add some sample notifications for demonstration
    if (userNotifications.length === 0) {
      userNotifications = [
        {
          id: 'notif_1',
          title: 'Assessment Evidence Reviewed',
          message: 'Your Business Formation evidence package has been approved by the navigator. You can now proceed to the next tier.',
          type: 'success',
          action_url: '/dashboard/assessments/area1/results',
          priority: 'high',
          status: 'unread',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000),
          read_at: null
        },
        {
          id: 'notif_2',
          title: 'New Service Provider Response',
          message: 'Sarah Johnson has responded to your Financial Operations service request with a proposal of $1,800.',
          type: 'info',
          action_url: '/dashboard/services',
          priority: 'normal',
          status: 'unread',
          created_at: new Date(Date.now() - 4 * 60 * 60 * 1000),
          read_at: null
        },
        {
          id: 'notif_3',
          title: 'Knowledge Base Updated',
          message: 'New technology security templates have been added to your knowledge base.',
          type: 'info',
          action_url: '/dashboard/knowledge-base',
          priority: 'low',
          status: 'read',
          created_at: new Date(Date.now() - 24 * 60 * 60 * 1000),
          read_at: new Date(Date.now() - 12 * 60 * 60 * 1000)
        }
      ]
    }

    res.json({
      success: true,
      data: {
        notifications: userNotifications,
        total: userNotifications.length,
        unread_count: userNotifications.filter(n => n.status === 'unread').length
      }
    })

  } catch (error) {
    logger.error('Get notifications error:', error)
    next(error)
  }
})

/**
 * POST /api/notifications/:notification_id/read
 * Mark notification as read
 */
router.post('/:notification_id/read', authenticateToken, async (req, res, next) => {
  try {
    const { notification_id } = req.params
    const userId = req.user.id

    const notification = notifications.find(n => n.id === notification_id && n.recipient_id === userId)
    
    if (!notification) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'Notification not found')
      )
    }

    notification.status = 'read'
    notification.read_at = new Date()

    res.json({
      success: true,
      data: {
        notification_id,
        status: 'read',
        read_at: notification.read_at
      }
    })

  } catch (error) {
    logger.error('Mark notification read error:', error)
    next(error)
  }
})

/**
 * POST /api/notifications/provider-match
 * Send notification when client creates service request (internal use)
 */
router.post('/provider-match', authenticateToken, async (req, res, next) => {
  try {
    const { service_request_id, provider_ids, area_name, budget_range } = req.body

    // Send notifications to first 5 providers
    const notificationPromises = provider_ids.slice(0, 5).map(async (providerId) => {
      const notification = {
        id: uuidv4(),
        recipient_id: providerId,
        sender_id: 'system',
        title: 'New Service Opportunity Available',
        message: `A new ${area_name} service opportunity is available with budget ${budget_range}. Click to view details and submit your proposal.`,
        type: 'opportunity',
        action_url: `/dashboard/opportunities/${service_request_id}`,
        priority: 'high',
        status: 'unread',
        created_at: new Date(),
        read_at: null
      }

      notifications.push(notification)
      logger.info(`Provider notification sent to ${providerId} for service ${service_request_id}`)
      return notification
    })

    await Promise.all(notificationPromises)

    res.json({
      success: true,
      data: {
        providers_notified: Math.min(provider_ids.length, 5),
        service_request_id,
        notifications_sent: notificationPromises.length
      }
    })

  } catch (error) {
    logger.error('Provider match notification error:', error)
    next(error)
  }
})

module.exports = router