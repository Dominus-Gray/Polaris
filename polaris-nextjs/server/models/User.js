const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const userSchema = new mongoose.Schema({
  id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: true,
    minlength: 8
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  role: {
    type: String,
    enum: ['client', 'provider', 'agency', 'navigator', 'admin'],
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected', 'suspended'],
    default: 'approved'
  },
  phone: {
    type: String,
    trim: true
  },
  company_name: {
    type: String,
    trim: true
  },
  license_code: {
    type: String,
    validate: {
      validator: function(v) {
        if (this.role === 'client') {
          return v && /^\d{10}$/.test(v);
        }
        return true;
      },
      message: 'Business clients require a valid 10-digit license code'
    }
  },
  business_description: {
    type: String,
    maxlength: 1000
  },
  location: {
    city: String,
    state: String,
    country: String,
    zip_code: String
  },
  specializations: [String],
  certifications: [String],
  website: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^https?:\/\/.+/.test(v);
      },
      message: 'Website must be a valid URL'
    }
  },
  linkedin: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^https?:\/\/.+/.test(v);
      },
      message: 'LinkedIn must be a valid URL'
    }
  },
  profile_image: {
    type: String
  },
  email_verified: {
    type: Boolean,
    default: false
  },
  email_verification_token: String,
  password_reset_token: String,
  password_reset_expires: Date,
  last_login: Date,
  failed_login_attempts: {
    type: Number,
    default: 0
  },
  account_locked_until: Date,
  two_factor_enabled: {
    type: Boolean,
    default: false
  },
  two_factor_secret: String,
  preferences: {
    notifications: {
      email: { type: Boolean, default: true },
      sms: { type: Boolean, default: false },
      push: { type: Boolean, default: true }
    },
    theme: {
      type: String,
      enum: ['light', 'dark', 'auto'],
      default: 'light'
    },
    language: {
      type: String,
      default: 'en'
    }
  },
  subscription: {
    plan: {
      type: String,
      enum: ['free', 'basic', 'premium', 'enterprise'],
      default: 'free'
    },
    status: {
      type: String,
      enum: ['active', 'inactive', 'cancelled', 'expired'],
      default: 'active'
    },
    expires_at: Date
  },
  metadata: {
    signup_source: String,
    referral_code: String,
    marketing_consent: { type: Boolean, default: false }
  }
}, {
  timestamps: {
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  },
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ id: 1 });
userSchema.index({ role: 1 });
userSchema.index({ status: 1 });
userSchema.index({ license_code: 1 });

// Virtual for full name
userSchema.virtual('display_name').get(function() {
  return this.name || this.email;
});

// Pre-save middleware to hash password
userSchema.pre('save', async function(next) {
  // Only hash the password if it has been modified (or is new)
  if (!this.isModified('password')) return next();
  
  try {
    // Hash password with cost of 12
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Instance method to check password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Instance method to generate JWT
userSchema.methods.generateJWT = function() {
  const jwt = require('jsonwebtoken');
  return jwt.sign(
    { 
      id: this.id, 
      email: this.email, 
      role: this.role 
    },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRE || '7d' }
  );
};

// Instance method to sanitize user data
userSchema.methods.toSafeObject = function() {
  const userObject = this.toObject();
  delete userObject.password;
  delete userObject.__v;
  delete userObject._id;
  delete userObject.email_verification_token;
  delete userObject.password_reset_token;
  delete userObject.two_factor_secret;
  return userObject;
};

// Static method to find by credentials
userSchema.statics.findByCredentials = async function(email, password) {
  const user = await this.findOne({ email });
  
  if (!user) {
    throw new Error('Invalid credentials');
  }
  
  const isMatch = await user.comparePassword(password);
  if (!isMatch) {
    throw new Error('Invalid credentials');
  }
  
  return user;
};

// Static method to find by ID
userSchema.statics.findByUUID = function(id) {
  return this.findOne({ id });
};

module.exports = mongoose.model('User', userSchema);