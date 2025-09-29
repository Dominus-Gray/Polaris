const express = require('express')
const multer = require('multer')
const path = require('path')
const fs = require('fs').promises
const { v4: uuidv4 } = require('uuid')
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger

const router = express.Router()

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads/evidence')
    try {
      await fs.mkdir(uploadDir, { recursive: true })
      cb(null, uploadDir)
    } catch (error) {
      cb(error, null)
    }
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${uuidv4()}-${file.originalname}`
    cb(null, uniqueName)
  }
})

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
    files: 10 // Max 10 files per upload
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    const fileExt = path.extname(file.originalname).toLowerCase()
    
    if (allowedTypes.includes(fileExt)) {
      cb(null, true)
    } else {
      cb(new Error('Invalid file type. Only PDF, Word documents, and images are allowed.'), false)
    }
  }
})

// Evidence Package Model
const EvidencePackage = require('../models/EvidencePackage')

/**
 * POST /api/evidence/upload
 * Upload evidence files for assessment statements
 */
router.post('/upload', authenticateToken, upload.array('evidence_files', 10), async (req, res, next) => {
  try {
    const { statement_id, session_id, area_id, tier, notes } = req.body
    const userId = req.user.id
    
    if (!statement_id || !session_id || !area_id) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Missing required fields', 'statement_id, session_id, and area_id are required')
      )
    }

    const uploadedFiles = req.files?.map(file => ({
      filename: file.filename,
      original_name: file.originalname,
      file_path: file.path,
      file_size: file.size,
      mime_type: file.mimetype,
      uploaded_at: new Date()
    })) || []

    // Create evidence record
    const evidenceRecord = {
      id: uuidv4(),
      user_id: userId,
      session_id,
      area_id,
      statement_id,
      tier: parseInt(tier) || 1,
      files: uploadedFiles,
      notes: notes || '',
      status: 'uploaded',
      uploaded_at: new Date(),
      updated_at: new Date()
    }

    // Save to database (using EvidencePackage model)
    const savedEvidence = new EvidencePackage(evidenceRecord)
    await savedEvidence.save()

    logger.info(`Evidence uploaded: ${uploadedFiles.length} files for statement ${statement_id}`)

    res.json({
      success: true,
      data: {
        evidence_id: evidenceRecord.id,
        files_uploaded: uploadedFiles.length,
        files: uploadedFiles.map(f => ({
          filename: f.filename,
          original_name: f.original_name,
          size: f.file_size
        }))
      }
    })

  } catch (error) {
    logger.error('Evidence upload error:', error)
    next(error)
  }
})

/**
 * POST /api/evidence/submit-package
 * Submit complete evidence package for navigator review
 */
router.post('/submit-package', authenticateToken, async (req, res, next) => {
  try {
    const { session_id, area_id, evidence_items } = req.body
    const userId = req.user.id

    // Create evidence package for navigator review
    const packageData = {
      package_id: uuidv4(),
      user_id: userId,
      session_id,
      area_id,
      evidence_items,
      status: 'pending_review',
      submitted_at: new Date(),
      navigator_assigned: null,
      review_notes: null
    }

    // Save package (simplified for demo)
    logger.info(`Evidence package submitted for review: ${packageData.package_id}`)

    res.json({
      success: true,
      data: {
        package_id: packageData.package_id,
        status: 'submitted',
        message: 'Evidence package submitted for navigator review successfully'
      }
    })

  } catch (error) {
    logger.error('Evidence package submission error:', error)
    next(error)
  }
})

/**
 * GET /api/evidence/download/:filename
 * Download evidence file
 */
router.get('/download/:filename', authenticateToken, async (req, res, next) => {
  try {
    const { filename } = req.params
    const filePath = path.join(__dirname, '../uploads/evidence', filename)
    
    // Check if file exists
    try {
      await fs.access(filePath)
    } catch (error) {
      return res.status(404).json(
        formatErrorResponse('POL-4001', 'File not found', 'The requested file does not exist')
      )
    }

    // Send file
    res.download(filePath, (error) => {
      if (error) {
        logger.error('File download error:', error)
        res.status(500).json(
          formatErrorResponse('POL-5001', 'Download failed', 'Unable to download file')
        )
      }
    })

  } catch (error) {
    logger.error('Evidence download error:', error)
    next(error)
  }
})

module.exports = router