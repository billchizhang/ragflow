/**
 * Azure SQL Database Tables Creation Script
 * 
 * This script creates the following tables in the Azure SQL database if they don't exist:
 * - SubscriptionTiers: Defines available subscription tiers
 * - AuthCodes: Stores authorization codes for subscriptions
 * - Users: Stores user account information with subscription details
 * - UserPayments: Tracks payment information
 */

import sql from 'mssql';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createDatabaseConnection } from '../server/config/database.js';

// Load environment variables
dotenv.config();

// Get the current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const showSuccessMessages = true;

/**
 * Creates tables in the database if they don't exist
 */
async function createTables() {
  let pool;
  
  try {
    console.log('Connecting to Azure SQL database...');
    pool = await createDatabaseConnection();
    console.log('Connected to Azure SQL database');
    
    // Execute all table creation queries in sequence
    console.log('Creating tables...');
    
    // Create SubscriptionTiers table
    await createSubscriptionTiersTable(pool);
    
    // Create AuthCodes table
    await createAuthCodesTable(pool);
    
    // Create Users table
    await createUsersTable(pool);
    
    // Create UserPayments table
    await createUserPaymentsTable(pool);
    
    console.log('All tables created successfully');
  } catch (err) {
    console.error('Error creating tables:', err);
    throw err;
  } finally {
    if (pool) {
      console.log('Closing database connection');
      await pool.close();
    }
  }
}

/**
 * Creates the SubscriptionTiers table
 */
async function createSubscriptionTiersTable(pool) {
  try {
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
    
    if (showSuccessMessages) {
      console.log('SubscriptionTiers table created or already exists');
    }
  } catch (err) {
    console.error('Error creating SubscriptionTiers table:', err);
    throw err;
  }
}

/**
 * Creates the AuthCodes table
 */
async function createAuthCodesTable(pool) {
  try {
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
    
    if (showSuccessMessages) {
      console.log('AuthCodes table created or already exists');
    }
  } catch (err) {
    console.error('Error creating AuthCodes table:', err);
    throw err;
  }
}

/**
 * Creates the Users table
 */
async function createUsersTable(pool) {
  try {
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
    
    if (showSuccessMessages) {
      console.log('Users table created or already exists');
    }
  } catch (err) {
    console.error('Error creating Users table:', err);
    throw err;
  }
}

/**
 * Creates the UserPayments table
 */
async function createUserPaymentsTable(pool) {
  try {
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
    
    if (showSuccessMessages) {
      console.log('UserPayments table created or already exists');
    }
  } catch (err) {
    console.error('Error creating UserPayments table:', err);
    throw err;
  }
}

// Run the script
createTables()
  .then(() => {
    console.log('Database initialization completed successfully');
    process.exit(0);
  })
  .catch((err) => {
    console.error('Database initialization failed:', err);
    process.exit(1);
  }); 