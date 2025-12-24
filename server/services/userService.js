const User = require('../models/User');
const { AgencyLicense } = require('../models/Agency');
const { v4: uuidv4 } = require('uuid');

const registerUser = async (userData) => {
  const { email, password, name, role, phone, company_name, license_code } = userData;

  // Check if user already exists
  const existingUser = await User.findOne({ email });
  if (existingUser) {
    throw new Error('An account with this email address already exists');
  }

  // Validate license code for clients
  if (role === 'client') {
    if (!license_code || !/^\d{10}$/.test(license_code)) {
      throw new Error('Business clients require a valid 10-digit license code from a local agency');
    }

    const license = await AgencyLicense.findOne({
      license_code,
      status: 'active',
      expires_at: { $gt: new Date() }
    });

    if (!license) {
      throw new Error('Invalid or expired license code');
    }

    if (license.usage_count >= license.usage_limit) {
      throw new Error('License code has already been used');
    }
  }

  // Create new user
  const newUser = new User({
    id: uuidv4(),
    email: email.toLowerCase(),
    password, // Will be hashed by pre-save middleware
    name,
    role,
    phone,
    company_name,
    license_code: role === 'client' ? license_code : undefined,
    status: 'approved' // Auto-approve for now
  });

  await newUser.save();

  // Mark license as used if it's a client registration
  if (role === 'client' && license_code) {
    const license = await AgencyLicense.findOne({ license_code });
    if (license) {
      await license.markAsUsed(newUser.id);
    }
  }

  return newUser;
};

module.exports = {
  registerUser,
  updateUserProfile,
  deleteUser,
};

async function updateUserProfile(userId, updates) {
  const allowedUpdates = [
    'name', 'phone', 'company_name', 'business_description',
    'location', 'specializations', 'certifications', 'website', 'linkedin'
  ];

  const filteredUpdates = {};
  allowedUpdates.forEach(field => {
    if (updates[field] !== undefined) {
      filteredUpdates[field] = updates[field];
    }
  });

  const user = await User.findOneAndUpdate(
    { id: userId },
    { $set: filteredUpdates },
    { new: true, runValidators: true }
  );

  if (!user) {
    throw new Error('User not found');
  }

  return user;
}

async function deleteUser(userId, confirmation) {
  if (confirmation !== 'DELETE_MY_ACCOUNT') {
    throw new Error('Account deletion confirmation required');
  }

  const user = await User.findOne({ id: userId });
  if (!user) {
    throw new Error('User not found');
  }

  // Soft delete
  user.status = 'deleted';
  user.email = `deleted_${Date.now()}_${user.email}`;
  user.deleted_at = new Date();

  await user.save();
}
