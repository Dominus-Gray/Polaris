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
};
