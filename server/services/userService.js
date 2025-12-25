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
  getDashboard,
  getNotifications,
  updatePreferences,
};

async function getDashboard(user) {
  const role = user.role;
  let dashboardData = {
    user: user.toSafeObject(),
    welcome_message: `Welcome back, ${user.name}!`,
    notifications_count: 0,
    quick_actions: []
  };

  switch (role) {
    case 'client':
      dashboardData.quick_actions = [
        { title: 'Start Assessment', url: '/assessment', icon: 'clipboard' },
        { title: 'View Services', url: '/services', icon: 'briefcase' },
        { title: 'Knowledge Base', url: '/knowledge-base', icon: 'book' }
      ];
      break;
    case 'provider':
      dashboardData.quick_actions = [
        { title: 'View Opportunities', url: '/opportunities', icon: 'search' },
        { title: 'My Services', url: '/my-services', icon: 'briefcase' },
        { title: 'Profile', url: '/profile', icon: 'user' }
      ];
      break;
    case 'agency':
      dashboardData.quick_actions = [
        { title: 'Generate Licenses', url: '/licenses', icon: 'key' },
        { title: 'View Clients', url: '/clients', icon: 'users' },
        { title: 'Analytics', url: '/analytics', icon: 'chart' }
      ];
      break;
    case 'navigator':
      dashboardData.quick_actions = [
        { title: 'Approve Agencies', url: '/approve-agencies', icon: 'check' },
        { title: 'System Analytics', url: '/system-analytics', icon: 'chart' },
        { title: 'User Management', url: '/users', icon: 'users' }
      ];
      break;
  }

  return dashboardData;
}

async function getNotifications(userId, page, limit) {
  // TODO: Implement notifications system
  return {
    notifications: [],
    total: 0
  };
}

async function updatePreferences(userId, preferences) {
  const user = await User.findOneAndUpdate(
    { id: userId },
    { $set: { preferences } },
    { new: true, runValidators: true }
  );

  if (!user) {
    throw new Error('User not found');
  }

  return user.preferences;
}

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
