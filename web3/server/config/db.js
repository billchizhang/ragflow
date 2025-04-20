/**
 * Database Configuration Module
 * 
 * This module handles the Azure SQL database connection and schema initialization.
 * It provides functions to initialize and test the database connection.
 */

import sql from 'mssql';
import dotenv from 'dotenv';
import { sqlConfig, createDatabaseConnection } from './database.js';

dotenv.config();

/**
 * Test Database Connection
 * 
 * Tests the database connection and logs the connection status.
 * 
 * @returns {Promise<boolean>} - Resolves with true if connection is successful
 */
async function testConnection() {
  try {
    const pool = await createDatabaseConnection();
    console.log('Database connection successful');
    await pool.close();
    return true;
  } catch (error) {
    console.error('Database connection failed:', error.message);
    console.error('Please check your database configuration and ensure the Azure SQL server is accessible.');
    return false;
  }
}

/**
 * Initialize Database Schema
 * 
 * Creates the necessary database tables if they don't already exist.
 * This function is called when the server starts up.
 * 
 * @returns {Promise<void>}
 */
async function initializeDb() {
  let pool;
  try {
    // First test the connection
    const connected = await testConnection();
    if (!connected) {
      console.log('Skipping database initialization due to connection issues');
      return;
    }

    pool = await createDatabaseConnection();
    
    // Create users table if it doesn't exist
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
      BEGIN
        CREATE TABLE Users (
          user_id INT IDENTITY(1,1) PRIMARY KEY,
          email NVARCHAR(255) NOT NULL UNIQUE,
          password NVARCHAR(255) NOT NULL,
          first_name NVARCHAR(100),
          last_name NVARCHAR(100),
          tier_id INT,
          subscription_start DATETIME2,
          subscription_end DATETIME2,
          auth_code_id INT,
          created_at DATETIME2 DEFAULT GETDATE(),
          last_login DATETIME2,
          CONSTRAINT UQ_Users_Email UNIQUE (email)
        )
      END
    `);

    // Create password_reset_tokens table if it doesn't exist
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PasswordResetTokens')
      BEGIN
        CREATE TABLE PasswordResetTokens (
          token_id INT IDENTITY(1,1) PRIMARY KEY,
          user_id INT NOT NULL,
          token NVARCHAR(6) NOT NULL,
          expires_at DATETIME2 NOT NULL,
          created_at DATETIME2 DEFAULT GETDATE(),
          CONSTRAINT FK_PasswordResetTokens_Users FOREIGN KEY (user_id) 
          REFERENCES Users(user_id) ON DELETE CASCADE
        )
      END
    `);

    // Create subscription tiers table if it doesn't exist
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SubscriptionTiers')
      BEGIN
        CREATE TABLE SubscriptionTiers (
          tier_id INT IDENTITY(1,1) PRIMARY KEY,
          tier_name NVARCHAR(50) NOT NULL,
          description NVARCHAR(MAX),
          duration_days INT NOT NULL,
          created_at DATETIME2 DEFAULT GETDATE()
        )
      END
    `);

    // Create auth codes table if it doesn't exist
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuthCodes')
      BEGIN
        CREATE TABLE AuthCodes (
          code_id INT IDENTITY(1,1) PRIMARY KEY,
          code NVARCHAR(12) NOT NULL UNIQUE,
          tier_id INT NOT NULL,
          is_redeemed BIT DEFAULT 0,
          redeemed_by INT,
          redeemed_at DATETIME2,
          created_at DATETIME2 DEFAULT GETDATE(),
          expires_at DATETIME2 NOT NULL,
          CONSTRAINT FK_AuthCodes_Tiers FOREIGN KEY (tier_id) REFERENCES SubscriptionTiers(tier_id),
          CONSTRAINT FK_AuthCodes_Users FOREIGN KEY (redeemed_by) REFERENCES Users(user_id)
        )
      END
    `);

    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Database initialization error:', error);
    console.error('The server will continue to run, but database functionality will be limited.');
  } finally {
    if (pool) {
      await pool.close();
    }
  }
}

// Export the initialization functions
export {
  initializeDb,
  testConnection
}; 