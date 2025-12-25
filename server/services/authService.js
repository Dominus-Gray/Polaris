const User = require('../models/User');
const { generateJWTToken, comparePasswords } = require('../utils/helpers');

const loginUser = async (email, password) => {
  // Find user by email
  const user = await User.findOne({ email: email.toLowerCase() });
  if (!user) {
    throw new Error('User not found');
  }

  // Check password
  const isValidPassword = await user.comparePassword(password);
  if (!isValidPassword) {
    throw new Error('Incorrect password');
  }

  // Check if account is approved
  if (user.status !== 'approved') {
    throw new Error(`Account not approved. Status: ${user.status}`);
  }

  // Update last login
  user.last_login = new Date();
  user.failed_login_attempts = 0;
  await user.save();

  // Generate JWT token
  const token = user.generateJWT();

  return { user, token };
};

const refreshAuthToken = (user) => {
  return user.generateJWT();
};

module.exports = {
  loginUser,
  refreshAuthToken,
  forgotPassword,
  resetPassword,
  changePassword,
};

async function forgotPassword(email) {
  const user = await User.findOne({ email: email.toLowerCase() });
  if (!user) {
    return;
  }

  const resetToken = require('crypto').randomBytes(32).toString('hex');
  user.password_reset_token = resetToken;
  user.password_reset_expires = new Date(Date.now() + 3600000); // 1 hour
  await user.save();

  // TODO: Send email with reset link
}

async function resetPassword(token, password) {
  const user = await User.findOne({
    password_reset_token: token,
    password_reset_expires: { $gt: new Date() }
  });

  if (!user) {
    throw new Error('Invalid or expired reset token');
  }

  user.password = password; // Will be hashed by pre-save middleware
  user.password_reset_token = undefined;
  user.password_reset_expires = undefined;
  user.failed_login_attempts = 0;
  await user.save();
}

async function changePassword(user, currentPassword, newPassword) {
  const isValidPassword = await user.comparePassword(currentPassword);
  if (!isValidPassword) {
    throw new Error('Current password is incorrect');
  }

  user.password = newPassword; // Will be hashed by pre-save middleware
  await user.save();
}
