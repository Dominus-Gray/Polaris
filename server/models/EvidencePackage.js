const mongoose = require('mongoose')

const EvidencePackageSchema = new mongoose.Schema({
  package_id: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  
  user_id: {
    type: String,
    required: true,
    index: true
  },
  
  session_id: {
    type: String,
    required: true
  },
  
  area_id: {
    type: String,
    required: true
  },
  
  evidence_items: [{
    statement_id: String,
    statement_text: String,
    tier: Number,
    category: String,
    files: [{
      filename: String,
      original_name: String,
      file_path: String,
      file_size: Number,
      mime_type: String,
      uploaded_at: Date
    }],
    notes: String
  }],
  
  status: {
    type: String,
    enum: ['pending_review', 'under_review', 'approved', 'rejected', 'remediation_required'],
    default: 'pending_review'
  },
  
  navigator_assigned: {
    type: String,
    default: null
  },
  
  review_notes: {
    type: String,
    default: null
  },
  
  reviewed_at: {
    type: Date,
    default: null
  },
  
  submitted_at: {
    type: Date,
    default: Date.now
  },
  
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  collection: 'evidence_packages'
})

// Update the updated_at field before saving
EvidencePackageSchema.pre('save', function(next) {
  this.updated_at = new Date()
  next()
})

const EvidencePackage = mongoose.model('EvidencePackage', EvidencePackageSchema)

module.exports = EvidencePackage