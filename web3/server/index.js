/**
 * Main Server Entry Point
 * This file initializes and configures the Express server, establishes routes,
 * connects to the database, and starts the server listening on the configured port.
 */

import express from 'express';
import cors from 'cors';
import { createDatabaseConnection } from './config/database.js';
import { passwordConfig } from './config/config.js';
import { initializeDatabase } from './config/init-db.js';
import authRoutes from './routes/auth.js';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Initialize Express application
const app = express();
const port = process.env.PORT || 5001;

// Middleware Configuration
// Enable Cross-Origin Resource Sharing (CORS) for all routes
app.use(cors());
// Parse incoming JSON request bodies
app.use(express.json());

// Database connection
let db;

// Initialize database and start server
async function startServer() {
  try {
    // Initialize database schema
    await initializeDatabase();
    
    // Create database connection
    db = await createDatabaseConnection(passwordConfig);
    
    // Route Registration
    // Mount authentication routes under /api/auth prefix
    app.use('/api/auth', authRoutes);

    // Basic health check endpoint
    app.get('/api/health', (req, res) => {
      res.json({ status: 'ok', message: 'Server is running' });
    });

    // Start server
    app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  if (db) {
    await db.disconnect();
  }
  process.exit(0);
});

// Start the server
startServer();

// Export for testing
export default app; 