const express = require('express')
const multer = require('multer')
const path = require('path')
const fs = require('fs').promises
const { v4: uuidv4 } = require('uuid')
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger

const router = express.Router()

// Configure comprehensive file upload system
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadType = req.body.upload_type || 'evidence'
    const uploadDir = path.join(__dirname, `../uploads/${uploadType}`)
    try {
      await fs.mkdir(uploadDir, { recursive: true })
      cb(null, uploadDir)
    } catch (error) {
      cb(error, null)
    }
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now()
    const uniqueId = uuidv4().substring(0, 8)
    const sanitizedName = file.originalname.replace(/[^a-zA-Z0-9.-]/g, '_')
    const uniqueName = `${timestamp}-${uniqueId}-${sanitizedName}`
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
    const allowedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.csv']
    const fileExt = path.extname(file.originalname).toLowerCase()
    
    if (allowedTypes.includes(fileExt)) {
      cb(null, true)
    } else {
      cb(new Error(`Invalid file type: ${fileExt}. Allowed types: ${allowedTypes.join(', ')}`), false)
    }
  }
})

/**
 * POST /api/files/upload
 * Universal file upload endpoint
 */
router.post('/upload', authenticateToken, upload.array('files', 10), async (req, res, next) => {
  try {
    const { 
      upload_type = 'evidence',
      statement_id, 
      session_id, 
      area_id, 
      tier,
      description 
    } = req.body
    const userId = req.user.id
    
    if (!req.files || req.files.length === 0) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'No files uploaded', 'Please select files to upload')
      )
    }

    const uploadedFiles = req.files.map(file => ({
      id: uuidv4(),
      filename: file.filename,
      original_name: file.originalname,
      file_path: file.path,
      file_size: file.size,
      mime_type: file.mimetype,
      upload_type,
      uploaded_by: userId,
      uploaded_at: new Date(),
      metadata: {
        statement_id,
        session_id,
        area_id,
        tier,
        description
      }
    }))

    // Save file records to database
    // For now, just log successful upload
    uploadedFiles.forEach(file => {
      logger.info(`File uploaded: ${file.original_name} by user ${userId}`)
    })

    res.json({
      success: true,
      data: {
        files_uploaded: uploadedFiles.length,
        files: uploadedFiles.map(f => ({
          id: f.id,
          filename: f.filename,
          original_name: f.original_name,
          size: f.file_size,
          type: f.mime_type,
          uploaded_at: f.uploaded_at
        }))
      }
    })

  } catch (error) {
    logger.error('File upload error:', error)
    next(error)
  }
})

/**
 * GET /api/files/download/:fileId
 * Download uploaded file
 */
router.get('/download/:fileId', authenticateToken, async (req, res, next) => {
  try {
    const { fileId } = req.params
    
    // For demo, create a sample file download
    const sampleContent = `# Evidence File Download
    
File ID: ${fileId}
Downloaded by: ${req.user.email}
Download time: ${new Date().toISOString()}

This is a sample evidence file download from the Polaris platform.
In a production system, this would retrieve the actual uploaded file.
`
    
    const filename = `evidence_${fileId}.txt`
    
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`)
    res.setHeader('Content-Type', 'text/plain')
    res.send(sampleContent)

  } catch (error) {
    logger.error('File download error:', error)
    next(error)
  }
})

/**
 * DELETE /api/files/:fileId
 * Delete uploaded file
 */
router.delete('/:fileId', authenticateToken, async (req, res, next) => {
  try {
    const { fileId } = req.params
    const userId = req.user.id

    // For demo, just log deletion
    logger.info(`File deletion requested: ${fileId} by user ${userId}`)

    res.json({
      success: true,
      data: {
        file_id: fileId,
        deleted_at: new Date(),
        message: 'File deleted successfully'
      }
    })

  } catch (error) {
    logger.error('File deletion error:', error)
    next(error)
  }
})

module.exports = router