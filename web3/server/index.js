/**
 * Main Server Entry Point
 * This file initializes and configures the Express server, establishes routes,
 * connects to the database, and starts the server listening on the configured port.
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { initializeDb } from './config/db.js';
import { testDatabaseConnection, createDatabaseConnection } from './config/database.js';
import authRoutes from './routes/auth.js';
import userRoutes from './routes/user.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// Load environment variables from .env file
dotenv.config();

// Force production mode - dev mode is now disabled regardless of environment
const DEV_MODE = false;
process.env.DEV_MODE = 'false';
console.log(`Server starting in PRODUCTION mode`);

// Initialize Express application
const app = express();
const PORT = process.env.PORT || 5001;

// Define mock user for development testing - kept for reference but won't be used
const MOCK_USER = {
  id: 1,
  email: 'test@example.com',
  password: '$2a$10$9qLw5YU.70QVmt/watgmG.EUkcx3sAz.1Ti9ovSQ6CzzG9e1vxLBm', // bcrypt hash for 'password'
  firstName: 'Test',
  lastName: 'User',
  tierName: 'Free',
  isExpired: false
};

// Middleware Configuration
// Enable Cross-Origin Resource Sharing (CORS) for all routes
app.use(cors());
// Parse incoming JSON request bodies
app.use(express.json());
// Serve static files from the public directory
app.use(express.static('server/public'));

// Add middleware to handle dev mode - always set to false
app.use((req, res, next) => {
  req.devMode = false;
  next();
});

// Initialize Database Connection and Schema
(async () => {
  try {
    // Test connection to Azure SQL Database
    const connected = await testDatabaseConnection();
    
    if (connected) {
      console.log('Successfully connected to Azure SQL Database');
      
      // Initialize database schema
      await initializeDb();
    } else {
      console.error('Failed to connect to Azure SQL Database. Application requires a database connection to function properly.');
    }
  } catch (error) {
    console.error('Database connection error:', error);
  }
})();

// Test Route - Simple health check endpoint
app.get('/', (req, res) => {
  res.json({ msg: 'API Running' });
});

// Debug endpoint for status - adapted for production
app.get('/api/debug/status', (req, res) => {
  res.json({
    serverMode: 'Production',
    mockEndpoints: {
      loginEnabled: false,
      changePasswordEnabled: false,
      profileEnabled: false
    },
    mockUser: null
  });
});

// Set up the auth routes
app.use('/api/auth', authRoutes);

// Set up the user routes
app.use('/api/user', userRoutes);

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 