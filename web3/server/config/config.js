/**
 * Application Configuration Module
 * 
 * This module centralizes configuration parameters for the application,
 * pulling values from environment variables and providing defaults
 * when environment variables are not set.
 */

import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// SQL Server connection configuration
export const passwordConfig = {
  server: process.env.AZURE_SQL_SERVER,
  database: process.env.AZURE_SQL_DATABASE, 
  user: process.env.AZURE_SQL_USER,
  password: process.env.AZURE_SQL_PASSWORD,
  port: parseInt(process.env.AZURE_SQL_PORT || '1433'),
  options: {
    encrypt: true, // Required for Azure SQL
    trustServerCertificate: false, 
    connectTimeout: 30000, // 30 seconds
    requestTimeout: 30000, // 30 seconds
    pool: {
      max: 10,
      min: 0,
      idleTimeoutMillis: 30000
    }
  }
};

// JWT configuration
export const jwtConfig = {
  secret: process.env.JWT_SECRET || 'your_jwt_secret_key_here',
  expiresIn: '24h'
};

// Email configuration
export const emailConfig = {
  service: process.env.EMAIL_SERVICE,
  user: process.env.EMAIL_USER,
  password: process.env.EMAIL_PASSWORD,
  from: process.env.EMAIL_FROM
};

// Server configuration
export const serverConfig = {
  port: process.env.PORT || 5001,
  environment: process.env.NODE_ENV || 'development'
}; 