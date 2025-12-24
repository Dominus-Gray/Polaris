const { formatErrorResponse } = require('../utils/helpers')

const requireJsonContent = (req, res, next) => {
  if (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH') {
    if (!req.is('application/json')) {
      return res.status(415).json(
        formatErrorResponse(
          'POL-4004',
          'Unsupported Media Type',
          'This endpoint requires Content-Type: application/json'
        )
      )
    }
  }
  next()
}

module.exports = { requireJsonContent }
