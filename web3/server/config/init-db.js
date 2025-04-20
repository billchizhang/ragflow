/**
 * Database Initialization Module
 * 
 * This module handles the creation and initialization of database tables
 * for the user subscription system. It creates the following tables:
 * - SubscriptionTiers: Defines available subscription tiers
 * - AuthCodes: Stores authorization codes for subscriptions
 * - Users: Stores user account information with subscription details
 */

import sql from 'mssql';
import { createDatabaseConnection } from './database.js';

/**
 * Creates necessary database tables if they don't exist
 */
export async function initializeDatabase() {
  let pool;
  
  try {
    // Create database connection
    pool = await createDatabaseConnection();
    
    // Create SubscriptionTiers table
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SubscriptionTiers')
      BEGIN
        CREATE TABLE SubscriptionTiers (
          tier_id INT PRIMARY KEY IDENTITY(1,1),
          tier_name NVARCHAR(50) NOT NULL,
          description NVARCHAR(255),
          price DECIMAL(10, 2) NOT NULL,
          duration_days INT NOT NULL,
          features NVARCHAR(MAX),
          created_at DATETIME2 DEFAULT GETDATE(),
          updated_at DATETIME2 DEFAULT GETDATE()
        );
        
        -- Insert default subscription tiers
        INSERT INTO SubscriptionTiers (tier_name, description, price, duration_days, features)
        VALUES 
          ('Free', 'Basic access with limited features', 0.00, 365, 'Basic search, Limited queries'),
          ('Standard', 'Standard access with enhanced features', 9.99, 30, 'Advanced search, Unlimited queries, Basic analytics'),
          ('Premium', 'Premium access with all features', 19.99, 30, 'All features, Priority support, Advanced analytics, Custom integrations');
      END
    `);
    
    // Create AuthCodes table
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuthCodes')
      BEGIN
        CREATE TABLE AuthCodes (
          code_id INT PRIMARY KEY IDENTITY(1,1),
          code NVARCHAR(16) NOT NULL UNIQUE,
          tier_id INT NOT NULL,
          issued_email NVARCHAR(255),
          issued_at DATETIME2 DEFAULT GETDATE(),
          expires_at DATETIME2 NOT NULL,
          is_redeemed BIT DEFAULT 0,
          redeemed_by INT,
          redeemed_at DATETIME2,
          CONSTRAINT FK_AuthCodes_SubscriptionTiers FOREIGN KEY (tier_id) 
            REFERENCES SubscriptionTiers(tier_id)
        );
        
        -- Create index on code for faster lookups
        CREATE INDEX IX_AuthCodes_Code ON AuthCodes(code);
      END
    `);
    
    // Create Users table
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
      BEGIN
        CREATE TABLE Users (
          user_id INT PRIMARY KEY IDENTITY(1,1),
          email NVARCHAR(255) NOT NULL UNIQUE,
          password NVARCHAR(255) NOT NULL,
          first_name NVARCHAR(100),
          last_name NVARCHAR(100),
          tier_id INT NOT NULL,
          subscription_start DATETIME2,
          subscription_end DATETIME2,
          auth_code_id INT,
          last_login DATETIME2,
          created_at DATETIME2 DEFAULT GETDATE(),
          updated_at DATETIME2 DEFAULT GETDATE(),
          CONSTRAINT FK_Users_SubscriptionTiers FOREIGN KEY (tier_id)
            REFERENCES SubscriptionTiers(tier_id),
          CONSTRAINT FK_Users_AuthCodes FOREIGN KEY (auth_code_id)
            REFERENCES AuthCodes(code_id)
        );
        
        -- Create index on email for faster lookups
        CREATE INDEX IX_Users_Email ON Users(email);
      END
    `);
    
    // Create UserPayments table
    await pool.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserPayments')
      BEGIN
        CREATE TABLE UserPayments (
          payment_id INT PRIMARY KEY IDENTITY(1,1),
          user_id INT NOT NULL,
          amount DECIMAL(10, 2) NOT NULL,
          payment_date DATETIME2 DEFAULT GETDATE(),
          payment_method NVARCHAR(50),
          transaction_id NVARCHAR(100),
          status NVARCHAR(20),
          tier_id INT NOT NULL,
          CONSTRAINT FK_UserPayments_Users FOREIGN KEY (user_id)
            REFERENCES Users(user_id),
          CONSTRAINT FK_UserPayments_SubscriptionTiers FOREIGN KEY (tier_id)
            REFERENCES SubscriptionTiers(tier_id)
        );
      END
    `);
    
    console.log('Database initialization completed successfully');
  } catch (err) {
    console.error('Database initialization failed:', err);
    throw err;
  } finally {
    if (pool) {
      await pool.close();
    }
  }
}

/**
 * Generates a random authorization code
 * 
 * @param {number} length - Length of the code (default: 12)
 * @returns {string} Random alphanumeric code
 */
export function generateAuthCode(length = 12) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * chars.length);
    code += chars.charAt(randomIndex);
  }
  
  return code;
}

/**
 * Creates an authorization code in the database
 * 
 * @param {Object} codeData - Authorization code data
 * @param {number} codeData.tier_id - Subscription tier ID
 * @param {string} codeData.issued_email - Email the code is issued to
 * @param {number} codeData.valid_days - Days until expiration
 * @returns {Promise<Object>} Created auth code record
 */
export async function createAuthCode(codeData) {
  const { tier_id, issued_email, valid_days = 30 } = codeData;
  const code = generateAuthCode();
  const expires_at = new Date();
  expires_at.setDate(expires_at.getDate() + valid_days);
  
  let pool;
  
  try {
    pool = await createDatabaseConnection();
    
    const result = await pool.request()
      .input('code', sql.NVarChar, code)
      .input('tier_id', sql.Int, tier_id)
      .input('issued_email', sql.NVarChar, issued_email)
      .input('expires_at', sql.DateTime2, expires_at)
      .query(`
        INSERT INTO AuthCodes (code, tier_id, issued_email, expires_at)
        OUTPUT INSERTED.*
        VALUES (@code, @tier_id, @issued_email, @expires_at)
      `);
    
    return result.recordset[0];
  } catch (err) {
    console.error('Failed to create auth code:', err);
    throw err;
  } finally {
    if (pool) {
      await pool.close();
    }
  }
} 