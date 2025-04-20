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

// Load environment variables from .env file
dotenv.config();

// Read development mode flag
const DEV_MODE = process.env.DEV_MODE === 'true';

// Initialize Express application
const app = express();
const PORT = process.env.PORT || 5001;

// Middleware Configuration
// Enable Cross-Origin Resource Sharing (CORS) for all routes
app.use(cors());
// Parse incoming JSON request bodies
app.use(express.json());

// Initialize Database Connection and Schema
(async () => {
  try {
    if (!DEV_MODE) {
      // Test connection to Azure SQL Database
      const connected = await testDatabaseConnection();
      
      if (connected) {
        console.log('Successfully connected to Azure SQL Database');
        
        // Initialize database schema
        await initializeDb();
      } else {
        console.error('Failed to connect to Azure SQL Database. Application requires a database connection to function properly.');
        console.log('Starting in limited mode with mock data. For testing only.');
      }
    } else {
      console.log('Starting in development mode with mock data.');
    }
  } catch (error) {
    console.error('Database connection error:', error);
    console.log('Starting in limited mode with mock data. For testing only.');
  }
})();

// Test Route - Simple health check endpoint
app.get('/', (req, res) => {
  res.json({ msg: 'API Running' });
});

// Mock login endpoint for testing
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  // Basic validation
  if (!email || !password) {
    return res.status(400).json({ message: 'Please provide email and password' });
  }
  
  // For testing purposes, accept any login
  return res.status(200).json({
    token: 'test-jwt-token',
    user: {
      id: 1,
      email: email,
      firstName: 'Test',
      lastName: 'User',
      tierName: 'Free',
      isExpired: false
    }
  });
});

// Get real user profile data from the database
app.get('/api/user/profile', async (req, res) => {
  try {
    // Get the user ID from the request headers or query
    // In a real app, this would come from the JWT token
    const userId = req.query.id || 1; // Default to ID 1 for testing
    
    // Connect to the database
    const pool = await createDatabaseConnection();
    
    // Query the database for the user
    const result = await pool.request()
      .input('userId', userId)
      .query(`
        SELECT 
          u.user_id,
          u.email,
          u.first_name,
          u.last_name,
          u.tier_id,
          u.subscription_start,
          u.subscription_end,
          t.tier_name
        FROM Users u
        LEFT JOIN SubscriptionTiers t ON u.tier_id = t.tier_id
        WHERE u.user_id = @userId
      `);
    
    // Close the database connection
    await pool.close();
    
    // Check if user exists
    if (result.recordset.length === 0) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Get the user data
    const user = result.recordset[0];
    
    // Format the user data for response
    const formattedUser = {
      id: user.user_id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      tierName: user.tier_name || 'Basic',
      subscriptionStart: user.subscription_start,
      subscriptionEnd: user.subscription_end,
      isExpired: user.subscription_end ? new Date(user.subscription_end) < new Date() : false
    };
    
    // Return the user data
    return res.json(formattedUser);
  } catch (error) {
    console.error('Error fetching user profile:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

// Mount full routes if not in dev mode
if (!DEV_MODE) {
  // Mount authentication routes under /api/auth prefix
  app.use('/api/auth', authRoutes);
  // Mount user routes under /api/user prefix
  app.use('/api/user', userRoutes);
}

// Start Server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Server mode: ${DEV_MODE ? 'Development (Mock Data)' : 'Production'}`);
});

export default app; // Export for testing 