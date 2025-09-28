const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { ChatSession, ChatMessage } = require('../models/System');
const { Engagement } = require('../models/ServiceRequest');
const User = require('../models/User');
const { authenticateToken } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse,
  getPaginationMeta
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

/**
 * POST /api/chat/sessions
 * Create a new chat session
 */
router.post('/sessions', authenticateToken, async (req, res, next) => {
  try {
    const { 
      participants, 
      chat_type = 'direct', 
      engagement_id,
      title 
    } = req.body;
    
    const currentUserId = req.user.id;
    
    // Validate participants
    if (!participants || !Array.isArray(participants) || participants.length === 0) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Participants are required',
          'At least one participant must be specified'
        )
      );
    }
    
    // Ensure current user is included in participants
    const participantIds = participants.map(p => typeof p === 'string' ? p : p.user_id);
    if (!participantIds.includes(currentUserId)) {
      participantIds.push(currentUserId);
    }
    
    // Validate all participants exist
    const users = await User.find({ id: { $in: participantIds } });
    if (users.length !== participantIds.length) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4001',
          'Invalid participants',
          'One or more participants do not exist'
        )
      );
    }
    
    // If engagement-based chat, validate engagement
    if (engagement_id) {
      const engagement = await Engagement.findOne({ id: engagement_id });
      if (!engagement) {
        return res.status(404).json(
          formatErrorResponse(
            'POL-4001',
            'Engagement not found',
            'The specified engagement does not exist'
          )
        );
      }
      
      // Verify user is part of the engagement
      if (engagement.client_id !== currentUserId && engagement.provider_id !== currentUserId) {
        return res.status(403).json(
          formatErrorResponse(
            'POL-1003',
            'Access denied',
            'You are not authorized to create chat for this engagement'
          )
        );
      }
    }
    
    // Create chat session
    const session = new ChatSession({
      participants: users.map(user => ({
        user_id: user.id,
        role: user.role,
        joined_at: new Date()
      })),
      chat_type,
      engagement_id,
      title: title || generateChatTitle(users, chat_type),
      status: 'active'
    });
    
    await session.save();
    
    logger.info(`Chat session created: ${session.id} with ${users.length} participants`);
    
    res.status(201).json({
      success: true,
      message: 'Chat session created successfully',
      data: {
        session: {
          id: session.id,
          title: session.title,
          chat_type: session.chat_type,
          participants: session.participants,
          created_at: session.created_at
        }
      }
    });
    
  } catch (error) {
    logger.error('Create chat session error:', error);
    next(error);
  }
});

/**
 * GET /api/chat/sessions
 * Get user's chat sessions
 */
router.get('/sessions', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { page = 1, limit = 20, status = 'active' } = req.query;
    
    const query = {
      'participants.user_id': userId,
      'participants.is_active': true
    };
    
    if (status !== 'all') {
      query.status = status;
    }
    
    const total = await ChatSession.countDocuments(query);
    const sessions = await ChatSession.find(query)
      .sort({ last_message_at: -1, created_at: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    // Enhance sessions with participant details and last message
    const enhancedSessions = await Promise.all(
      sessions.map(async (session) => {
        // Get participant details
        const participantIds = session.participants.map(p => p.user_id);
        const users = await User.find({ id: { $in: participantIds } })
          .select('id name email role');
        
        // Get last message
        const lastMessage = await ChatMessage.findOne({ chat_id: session.id })
          .sort({ sent_at: -1 })
          .select('message sender_id sent_at message_type');
        
        return {
          id: session.id,
          title: session.title,
          chat_type: session.chat_type,
          status: session.status,
          message_count: session.message_count,
          participants: users.map(user => ({
            user_id: user.id,
            name: user.name,
            email: user.email,
            role: user.role
          })),
          last_message: lastMessage ? {
            message: lastMessage.message,
            sender_id: lastMessage.sender_id,
            sent_at: lastMessage.sent_at,
            type: lastMessage.message_type
          } : null,
          created_at: session.created_at,
          last_message_at: session.last_message_at
        };
      })
    );
    
    res.json({
      success: true,
      data: {
        sessions: enhancedSessions,
        pagination: getPaginationMeta(total, page, limit)
      }
    });
    
  } catch (error) {
    logger.error('Get chat sessions error:', error);
    next(error);
  }
});

/**
 * POST /api/chat/send
 * Send a message in a chat
 */
router.post('/send', authenticateToken, validate(schemas.chatMessage), async (req, res, next) => {
  try {
    const { chat_id, message, message_type = 'text', reply_to } = req.body;
    const senderId = req.user.id;
    
    // Validate chat session exists and user is participant
    const session = await ChatSession.findOne({
      id: chat_id,
      'participants.user_id': senderId,
      'participants.is_active': true,
      status: 'active'
    });
    
    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Chat session not found',
          'The specified chat session does not exist or you are not a participant'
        )
      );
    }
    
    // Create message
    const chatMessage = new ChatMessage({
      chat_id,
      sender_id: senderId,
      message,
      message_type,
      reply_to
    });
    
    await chatMessage.save();
    
    // Update session last activity
    await session.updateLastActivity();
    
    // Emit socket event to other participants
    const io = req.app.get('io');
    if (io) {
      io.to(`chat-${chat_id}`).emit('new-message', {
        id: chatMessage.id,
        chat_id,
        sender_id: senderId,
        sender_name: req.user.name,
        message,
        message_type,
        sent_at: chatMessage.sent_at
      });
    }
    
    logger.info(`Message sent in chat ${chat_id} by user ${senderId}`);
    
    res.status(201).json({
      success: true,
      message: 'Message sent successfully',
      data: {
        message: {
          id: chatMessage.id,
          chat_id,
          sender_id: senderId,
          message,
          message_type,
          sent_at: chatMessage.sent_at
        }
      }
    });
    
  } catch (error) {
    logger.error('Send chat message error:', error);
    next(error);
  }
});

/**
 * GET /api/chat/messages/:chatId
 * Get messages for a chat session
 */
router.get('/messages/:chatId', authenticateToken, async (req, res, next) => {
  try {
    const { chatId } = req.params;
    const { page = 1, limit = 50, before } = req.query;
    const userId = req.user.id;
    
    // Validate user is participant in chat
    const session = await ChatSession.findOne({
      id: chatId,
      'participants.user_id': userId,
      'participants.is_active': true
    });
    
    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Chat session not found',
          'The specified chat session does not exist or you are not a participant'
        )
      );
    }
    
    // Build query
    const query = { 
      chat_id: chatId,
      is_deleted: false
    };
    
    if (before) {
      query.sent_at = { $lt: new Date(before) };
    }
    
    const total = await ChatMessage.countDocuments(query);
    const messages = await ChatMessage.find(query)
      .sort({ sent_at: -1 }) // Most recent first
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    // Get sender details
    const senderIds = [...new Set(messages.map(m => m.sender_id))];
    const senders = await User.find({ id: { $in: senderIds } })
      .select('id name email role');
    const senderMap = senders.reduce((map, user) => {
      map[user.id] = user;
      return map;
    }, {});
    
    const enhancedMessages = messages.map(message => ({
      id: message.id,
      chat_id: message.chat_id,
      sender: {
        id: message.sender_id,
        name: senderMap[message.sender_id]?.name || 'Unknown User',
        role: senderMap[message.sender_id]?.role
      },
      message: message.message,
      message_type: message.message_type,
      attachments: message.attachments,
      reply_to: message.reply_to,
      reactions: message.reactions,
      edited: message.edited,
      sent_at: message.sent_at,
      read_by: message.read_by
    }));
    
    // Mark messages as read by current user
    await ChatMessage.updateMany(
      { 
        chat_id: chatId,
        sender_id: { $ne: userId },
        'read_by.user_id': { $ne: userId }
      },
      {
        $push: {
          read_by: {
            user_id: userId,
            read_at: new Date()
          }
        }
      }
    );
    
    res.json({
      success: true,
      data: {
        messages: enhancedMessages.reverse(), // Return in chronological order
        pagination: getPaginationMeta(total, page, limit),
        chat_info: {
          id: session.id,
          title: session.title,
          participants: session.participants
        }
      }
    });
    
  } catch (error) {
    logger.error('Get chat messages error:', error);
    next(error);
  }
});

/**
 * GET /api/chat/online/:chatId
 * Get online users in a chat
 */
router.get('/online/:chatId', authenticateToken, async (req, res, next) => {
  try {
    const { chatId } = req.params;
    const userId = req.user.id;
    
    // Validate user is participant in chat
    const session = await ChatSession.findOne({
      id: chatId,
      'participants.user_id': userId,
      'participants.is_active': true
    });
    
    if (!session) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Chat session not found',
          'The specified chat session does not exist or you are not a participant'
        )
      );
    }
    
    // For simplicity, return all active participants
    // In a real implementation, you'd track online status via socket connections
    const onlineUsers = session.participants
      .filter(p => p.is_active)
      .map(p => ({
        user_id: p.user_id,
        last_seen: p.last_seen || new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
        is_online: true // Mock online status
      }));
    
    res.json({
      success: true,
      data: {
        chat_id: chatId,
        online_users: onlineUsers,
        total_online: onlineUsers.length
      }
    });
    
  } catch (error) {
    logger.error('Get online chat users error:', error);
    next(error);
  }
});

/**
 * PUT /api/chat/messages/:messageId/read
 * Mark message as read
 */
router.put('/messages/:messageId/read', authenticateToken, async (req, res, next) => {
  try {
    const { messageId } = req.params;
    const userId = req.user.id;
    
    const message = await ChatMessage.findOne({ id: messageId });
    
    if (!message) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Message not found',
          'The specified message does not exist'
        )
      );
    }
    
    // Check if user already marked as read
    const alreadyRead = message.read_by.some(r => r.user_id === userId);
    if (!alreadyRead) {
      message.read_by.push({
        user_id: userId,
        read_at: new Date()
      });
      await message.save();
    }
    
    res.json({
      success: true,
      message: 'Message marked as read'
    });
    
  } catch (error) {
    logger.error('Mark message as read error:', error);
    next(error);
  }
});

// Helper function to generate chat title
function generateChatTitle(users, chatType) {
  if (chatType === 'support') {
    return 'Support Chat';
  }
  
  if (users.length === 2) {
    return `Chat between ${users.map(u => u.name).join(' and ')}`;
  }
  
  return `Group Chat (${users.length} participants)`;
}

module.exports = router;