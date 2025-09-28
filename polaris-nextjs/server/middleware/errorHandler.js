const winston = require('winston');
const { ValidationError } = require('joi');
const { MongooseError } = require('mongoose');

const logger = winston.createLogger({
  level: 'error',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

/**
 * Global error handler middleware
 */
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // Log error
  logger.error(err);

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = {
      statusCode: 404,
      error_code: 'POL-4001',
      message: {
        error_code: 'POL-4001',
        message,
        detail: 'Invalid ID format'
      }
    };
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const message = 'Duplicate field value entered';
    const field = Object.keys(err.keyValue)[0];
    error = {
      statusCode: 400,
      error_code: 'POL-4002',
      message: {
        error_code: 'POL-4002',
        message,
        detail: `${field} already exists`
      }
    };
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = {
      statusCode: 400,
      error_code: 'POL-4003',
      message: {
        error_code: 'POL-4003',
        message: 'Validation Error',
        detail: message
      }
    };
  }

  // Joi validation error
  if (error instanceof ValidationError) {
    const message = error.details.map(detail => detail.message).join(', ');
    error = {
      statusCode: 400,
      error_code: 'POL-4003',
      message: {
        error_code: 'POL-4003',
        message: 'Validation Error',
        detail: message
      }
    };
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    error = {
      statusCode: 401,
      error_code: 'POL-1001',
      message: {
        error_code: 'POL-1001',
        message: 'Invalid authentication credentials provided',
        detail: 'Invalid token'
      }
    };
  }

  if (err.name === 'TokenExpiredError') {
    error = {
      statusCode: 401,
      error_code: 'POL-1001',
      message: {
        error_code: 'POL-1001',
        message: 'Authentication token has expired',
        detail: 'Token expired'
      }
    };
  }

  // Rate limiting error
  if (err.status === 429) {
    error = {
      statusCode: 429,
      error_code: 'POL-4004',
      message: {
        error_code: 'POL-4004',
        message: 'Too many requests',
        detail: 'Rate limit exceeded'
      }
    };
  }

  // Default to 500 server error
  const statusCode = error.statusCode || 500;
  const errorCode = error.error_code || 'POL-5000';
  
  res.status(statusCode).json({
    error: true,
    error_code: errorCode,
    message: error.message || {
      error_code: errorCode,
      message: 'Internal Server Error',
      detail: 'Something went wrong'
    },
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

module.exports = errorHandler;