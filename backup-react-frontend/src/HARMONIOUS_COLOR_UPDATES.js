// Comprehensive color replacement script for Polaris harmonious blue system
// This file contains all the search/replace patterns needed to fix color clashes

const colorReplacements = [
  // Dashboard Headers - Replace blue-purple with harmonious blue gradients
  {
    find: /bg-gradient-to-r from-blue-600 to-purple-600/g,
    replace: "bg-gradient-to-r from-polaris-blue-500 to-polaris-blue-600"
  },
  
  // Reverse gradients
  {
    find: /bg-gradient-to-r from-purple-600 to-blue-600/g,
    replace: "bg-gradient-to-r from-polaris-blue-600 to-polaris-blue-500"
  },
  
  // Complex gradients with purple
  {
    find: /bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600/g,
    replace: "bg-gradient-to-r from-polaris-blue-600 via-polaris-blue-500 to-polaris-blue-400"
  },
  
  {
    find: /bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600/g,
    replace: "bg-gradient-to-r from-polaris-blue-600 via-polaris-blue-500 to-polaris-blue-400"
  },
  
  // Progress bars
  {
    find: /bg-gradient-to-r from-blue-500 to-purple-500/g,
    replace: "bg-gradient-to-r from-polaris-blue-400 to-polaris-blue-500"
  },
  
  // Light backgrounds
  {
    find: /bg-gradient-to-r from-blue-50 to-purple-50/g,
    replace: "bg-polaris-blue-50"
  },
  
  // Hover states
  {
    find: /hover:from-blue-700 hover:to-purple-700/g,
    replace: "hover:from-polaris-blue-600 hover:to-polaris-blue-700"
  },
  
  // Avatar and icon gradients
  {
    find: /bg-gradient-to-r from-blue-500 to-purple-500/g,
    replace: "bg-polaris-blue-500"
  }
];

// Export for use in systematic replacement
module.exports = { colorReplacements };