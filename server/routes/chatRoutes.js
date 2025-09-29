const express = require('express')
const router = express.Router()
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger
const { v4: uuidv4 } = require('uuid')

// Import models
const User = require('../models/User')

/**
 * GET /api/chat/rooms
 * Get user's chat rooms
 */
router.get('/rooms', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id

    // Mock chat rooms data for operational testing
    const chatRooms = [
      {
        chat_id: 'chat1',
        name: 'Financial Assessment Support',
        type: 'service',
        participants: [
          {
            user_id: 'provider1',
            name: 'Sarah Johnson',
            role: 'provider',
            online: true
          }
        ],
        last_message: {
          id: 'msg1',
          content: 'I\'ve completed the initial financial assessment review. Let me know if you have any questions!',
          sender_id: 'provider1',
          sender_name: 'Sarah Johnson',
          sender_role: 'provider',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          type: 'text',
          read_status: false
        },
        unread_count: 1,
        service_request_id: 'req1',
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
      },
      {
        chat_id: 'chat2',
        name: 'Technology Infrastructure Review',
        type: 'service',
        participants: [
          {
            user_id: 'provider2',
            name: 'Michael Chen',
            role: 'provider',
            online: false,
            last_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
          }
        ],
        last_message: {
          id: 'msg2',
          content: 'Thanks for the documentation. I\'ll start the security audit tomorrow.',
          sender_id: userId,
          sender_name: 'You',
          sender_role: 'client',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          type: 'text',
          read_status: true
        },
        unread_count: 0,
        service_request_id: 'req2',
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
      }
    ]

    res.json({
      success: true,
      data: chatRooms
    })

  } catch (error) {
    logger.error('Get chat rooms error:', error)
    next(error)
  }
})

/**
 * GET /api/chat/messages/:chat_id
 * Get messages for a chat room
 */
router.get('/messages/:chat_id', authenticateToken, async (req, res, next) => {
  try {
    const { chat_id } = req.params
    const userId = req.user.id

    // Mock messages data for operational testing
    const messages = [
      {
        id: 'msg1',
        content: 'Hi! I\'ve reviewed your service request for financial operations assessment. I have 8+ years of experience helping small businesses improve their financial processes.',
        sender_id: 'provider1',
        sender_name: 'Sarah Johnson',
        sender_role: 'provider',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        type: 'text',
        read_status: true
      },
      {
        id: 'msg2',
        content: 'That sounds great! I\'m particularly concerned about our cash flow management and budget planning. What would be your approach?',
        sender_id: userId,
        sender_name: 'You',
        sender_role: 'client',
        timestamp: new Date(Date.now() - 23 * 60 * 60 * 1000).toISOString(),
        type: 'text',
        read_status: true
      },
      {
        id: 'msg3',
        content: 'I typically start with a comprehensive analysis of your current financial statements, then develop customized dashboards for cash flow tracking. I\'ll also help you set up automated budget alerts.',
        sender_id: 'provider1',
        sender_name: 'Sarah Johnson',
        sender_role: 'provider',
        timestamp: new Date(Date.now() - 22 * 60 * 60 * 1000).toISOString(),
        type: 'text',
        read_status: true
      },
      {
        id: 'msg4',
        content: 'I\'ve completed the initial financial assessment review. Let me know if you have any questions!',
        sender_id: 'provider1',
        sender_name: 'Sarah Johnson',
        sender_role: 'provider',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        type: 'text',
        read_status: false
      }
    ]

    res.json({
      success: true,
      data: {
        messages,
        chat_id,
        total_messages: messages.length
      }
    })

  } catch (error) {
    logger.error('Get chat messages error:', error)
    next(error)
  }
})

/**
 * POST /api/chat/send
 * Send message in chat room
 */
router.post('/send', authenticateToken, async (req, res, next) => {
  try {
    const { chat_id, content, type = 'text' } = req.body
    const userId = req.user.id

    const messageData = {
      id: uuidv4(),
      chat_id,
      content,
      sender_id: userId,
      sender_name: req.user.name || 'User',
      sender_role: req.user.role,
      timestamp: new Date().toISOString(),
      type,
      read_status: false
    }

    logger.info(`Message sent in chat ${chat_id} by user ${userId}`)

    res.json({
      success: true,
      data: {
        message: messageData
      }
    })

  } catch (error) {
    logger.error('Send message error:', error)
    next(error)
  }
})

module.exports = router