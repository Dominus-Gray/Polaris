const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const User = require('../models/User');
const { authenticateToken } = require('../middleware/auth');
const { validate, schemas } = require('../utils/validation');
const { 
  formatResponse, 
  formatErrorResponse,
  sanitizeFilename,
  generateUploadPath
} = require('../utils/helpers');
const logger = require('../utils/logger').logger;

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads', req.user.id);
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      cb(null, uploadDir);
    } catch (error) {
      cb(error);
    }
  },
  filename: (req, file, cb) => {
    const sanitized = sanitizeFilename(file.originalname);
    const timestamp = Date.now();
    cb(null, `${timestamp}_${sanitized}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: parseInt(process.env.UPLOAD_MAX_SIZE) || 5 * 1024 * 1024, // 5MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`File type ${ext} not allowed`), false);
    }
  }
});

/**
 * GET /api/profiles/me
 * Get current user profile
 */
router.get('/me', authenticateToken, async (req, res, next) => {
  try {
    const user = req.user;
    
    res.json({
      success: true,
      data: {
        profile: user.toSafeObject()
      }
    });
    
  } catch (error) {
    logger.error('Get user profile error:', error);
    next(error);
  }
});

/**
 * PATCH /api/profiles/me
 * Update current user profile
 */
router.patch('/me', authenticateToken, validate(schemas.profileUpdate), async (req, res, next) => {
  try {
    const userId = req.user.id;
    const updates = req.body;
    
    // Remove fields that shouldn't be updated via this endpoint
    const restrictedFields = ['id', 'email', 'password', 'role', 'status', 'created_at', 'updated_at'];
    restrictedFields.forEach(field => delete updates[field]);
    
    const user = await User.findOneAndUpdate(
      { id: userId },
      { $set: updates },
      { new: true, runValidators: true }
    );
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User profile not found'
        )
      );
    }
    
    logger.info(`Profile updated for user: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Profile updated successfully',
      data: {
        profile: user.toSafeObject()
      }
    });
    
  } catch (error) {
    logger.error('Update user profile error:', error);
    next(error);
  }
});

/**
 * POST /api/profiles/me/avatar
 * Upload user avatar
 */
router.post('/me/avatar', authenticateToken, upload.single('avatar'), async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    if (!req.file) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'No file uploaded',
          'Please select an avatar image to upload'
        )
      );
    }
    
    // Validate file type for avatar
    const allowedImageTypes = ['.jpg', '.jpeg', '.png', '.gif'];
    const ext = path.extname(req.file.originalname).toLowerCase();
    
    if (!allowedImageTypes.includes(ext)) {
      // Remove uploaded file
      await fs.unlink(req.file.path).catch(() => {});
      
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid file type',
          'Avatar must be an image file (jpg, jpeg, png, gif)'
        )
      );
    }
    
    // Generate avatar URL
    const avatarUrl = `/uploads/${userId}/${req.file.filename}`;
    
    // Update user profile
    const user = await User.findOneAndUpdate(
      { id: userId },
      { $set: { profile_image: avatarUrl } },
      { new: true }
    );
    
    if (!user) {
      // Remove uploaded file if user not found
      await fs.unlink(req.file.path).catch(() => {});
      
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User profile not found'
        )
      );
    }
    
    logger.info(`Avatar uploaded for user: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Avatar uploaded successfully',
      data: {
        avatar_url: avatarUrl,
        file_info: {
          filename: req.file.filename,
          size: req.file.size,
          mimetype: req.file.mimetype
        }
      }
    });
    
  } catch (error) {
    // Clean up uploaded file on error
    if (req.file) {
      await fs.unlink(req.file.path).catch(() => {});
    }
    
    logger.error('Upload avatar error:', error);
    next(error);
  }
});

/**
 * POST /api/profiles/me/documents
 * Upload profile documents
 */
router.post('/me/documents', authenticateToken, upload.array('documents', 5), async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { document_type, description } = req.body;
    
    if (!req.files || req.files.length === 0) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'No files uploaded',
          'Please select documents to upload'
        )
      );
    }
    
    const uploadedDocuments = req.files.map(file => ({
      filename: file.filename,
      original_name: file.originalname,
      path: `/uploads/${userId}/${file.filename}`,
      size: file.size,
      mimetype: file.mimetype,
      upload_date: new Date(),
      document_type: document_type || 'general',
      description: description || ''
    }));
    
    // Update user profile with documents
    const user = await User.findOneAndUpdate(
      { id: userId },
      { 
        $push: { 
          'profile_data.documents': { $each: uploadedDocuments } 
        }
      },
      { new: true }
    );
    
    if (!user) {
      // Clean up uploaded files if user not found
      for (const file of req.files) {
        await fs.unlink(file.path).catch(() => {});
      }
      
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User profile not found'
        )
      );
    }
    
    logger.info(`${req.files.length} documents uploaded for user: ${user.email}`);
    
    res.json({
      success: true,
      message: `${req.files.length} document(s) uploaded successfully`,
      data: {
        documents: uploadedDocuments,
        total_uploaded: req.files.length
      }
    });
    
  } catch (error) {
    // Clean up uploaded files on error
    if (req.files) {
      for (const file of req.files) {
        await fs.unlink(file.path).catch(() => {});
      }
    }
    
    logger.error('Upload documents error:', error);
    next(error);
  }
});

/**
 * GET /api/profiles/me/documents
 * Get user documents
 */
router.get('/me/documents', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { document_type } = req.query;
    
    const user = await User.findOne({ id: userId });
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User profile not found'
        )
      );
    }
    
    let documents = user.profile_data?.documents || [];
    
    if (document_type) {
      documents = documents.filter(doc => doc.document_type === document_type);
    }
    
    res.json({
      success: true,
      data: {
        documents,
        total_count: documents.length,
        document_types: [...new Set(documents.map(doc => doc.document_type))]
      }
    });
    
  } catch (error) {
    logger.error('Get user documents error:', error);
    next(error);
  }
});

/**
 * DELETE /api/profiles/me/documents/:filename
 * Delete a user document
 */
router.delete('/me/documents/:filename', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { filename } = req.params;
    
    const user = await User.findOne({ id: userId });
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'User profile not found'
        )
      );
    }
    
    const documents = user.profile_data?.documents || [];
    const documentIndex = documents.findIndex(doc => doc.filename === filename);
    
    if (documentIndex === -1) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'Document not found',
          'The specified document does not exist'
        )
      );
    }
    
    const document = documents[documentIndex];
    
    // Remove from database
    await User.findOneAndUpdate(
      { id: userId },
      { 
        $pull: { 
          'profile_data.documents': { filename: filename } 
        }
      }
    );
    
    // Delete physical file
    const filePath = path.join(__dirname, '../uploads', userId, filename);
    try {
      await fs.unlink(filePath);
    } catch (fileError) {
      logger.warn(`Failed to delete physical file: ${filePath}`, fileError);
    }
    
    logger.info(`Document deleted: ${filename} for user: ${user.email}`);
    
    res.json({
      success: true,
      message: 'Document deleted successfully',
      data: {
        deleted_document: {
          filename: document.filename,
          original_name: document.original_name
        }
      }
    });
    
  } catch (error) {
    logger.error('Delete user document error:', error);
    next(error);
  }
});

/**
 * POST /api/profiles/me/data-export
 * Request data export
 */
router.post('/me/data-export', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { format = 'json', include_documents = false } = req.body;
    
    if (!['json', 'csv'].includes(format)) {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid format',
          'Format must be either json or csv'
        )
      );
    }
    
    // Generate export request ID
    const exportId = require('uuid').v4();
    
    // In a real implementation, you'd queue this for background processing
    // For now, return immediate response
    
    logger.info(`Data export requested by user: ${req.user.email}, format: ${format}`);
    
    res.json({
      success: true,
      message: 'Data export request submitted successfully',
      data: {
        export_id: exportId,
        format,
        include_documents,
        status: 'processing',
        estimated_completion: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes
        download_url: null // Will be populated when ready
      }
    });
    
  } catch (error) {
    logger.error('Request data export error:', error);
    next(error);
  }
});

/**
 * POST /api/profiles/me/data-deletion
 * Request account data deletion
 */
router.post('/me/data-deletion', authenticateToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { confirmation_text, reason } = req.body;
    
    if (confirmation_text !== 'DELETE_MY_DATA') {
      return res.status(400).json(
        formatErrorResponse(
          'POL-4003',
          'Invalid confirmation',
          'Please provide the exact confirmation text: DELETE_MY_DATA'
        )
      );
    }
    
    // Generate deletion request ID
    const deletionId = require('uuid').v4();
    
    // In a real implementation, you'd:
    // 1. Mark account for deletion
    // 2. Queue background job to remove data after grace period
    // 3. Send confirmation email
    // 4. Comply with GDPR requirements
    
    logger.info(`Data deletion requested by user: ${req.user.email}, reason: ${reason}`);
    
    res.json({
      success: true,
      message: 'Data deletion request submitted successfully',
      data: {
        deletion_id: deletionId,
        status: 'pending',
        grace_period_days: 30,
        scheduled_deletion: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
        cancellation_deadline: new Date(Date.now() + 29 * 24 * 60 * 60 * 1000) // 29 days
      }
    });
    
  } catch (error) {
    logger.error('Request data deletion error:', error);
    next(error);
  }
});

/**
 * GET /api/profiles/:userId/public
 * Get public profile (for other users to view)
 */
router.get('/:userId/public', async (req, res, next) => {
  try {
    const { userId } = req.params;
    
    const user = await User.findOne({ id: userId })
      .select('id name role company_name business_description location specializations certifications profile_image created_at');
    
    if (!user) {
      return res.status(404).json(
        formatErrorResponse(
          'POL-4001',
          'User not found',
          'The specified user profile does not exist'
        )
      );
    }
    
    // Only show public information
    const publicProfile = {
      id: user.id,
      name: user.name,
      role: user.role,
      company_name: user.company_name,
      business_description: user.business_description,
      location: user.location,
      specializations: user.specializations,
      certifications: user.certifications,
      profile_image: user.profile_image,
      member_since: user.created_at
    };
    
    res.json({
      success: true,
      data: {
        profile: publicProfile
      }
    });
    
  } catch (error) {
    logger.error('Get public profile error:', error);
    next(error);
  }
});

module.exports = router;