/**
 * Authentication Service
 * 
 * Provides functions for user authentication, registration, and subscription management
 * including auth code validation and redemption.
 */

import sql from 'mssql';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { createDatabaseConnection } from '../config/database.js';

const SALT_ROUNDS = 10;

/**
 * Register a new user with an authorization code
 * 
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User's email
 * @param {string} userData.password - User's password (will be hashed)
 * @param {string} userData.firstName - User's first name
 * @param {string} userData.lastName - User's last name
 * @param {string} userData.authCode - Authorization code for subscription
 * @returns {Promise<Object>} Newly created user (without password)
 * @throws {Error} If registration fails or auth code is invalid
 */
export async function registerUser(userData) {
  const { email, password, firstName, lastName, authCode } = userData;
  let pool;
  
  try {
    pool = await createDatabaseConnection();
    
    // Start transaction
    const transaction = new sql.Transaction(pool);
    await transaction.begin();
    
    try {
      // 1. Validate the auth code and check if it's valid and not redeemed
      const codeResult = await new sql.Request(transaction)
        .input('code', sql.NVarChar, authCode)
        .query(`
          SELECT c.*, t.tier_name, t.duration_days
          FROM AuthCodes c
          JOIN SubscriptionTiers t ON c.tier_id = t.tier_id
          WHERE c.code = @code
            AND c.is_redeemed = 0
            AND c.expires_at > GETDATE()
        `);
      
      if (codeResult.recordset.length === 0) {
        throw new Error('Invalid or expired authorization code');
      }
      
      const authCodeData = codeResult.recordset[0];
      
      // 2. Check if email is already registered
      const existingUser = await new sql.Request(transaction)
        .input('email', sql.NVarChar, email)
        .query('SELECT * FROM Users WHERE email = @email');
      
      if (existingUser.recordset.length > 0) {
        throw new Error('Email is already registered');
      }
      
      // 3. Hash the password
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
      
      // 4. Calculate subscription dates based on tier duration
      const subscriptionStart = new Date();
      const subscriptionEnd = new Date();
      subscriptionEnd.setDate(subscriptionEnd.getDate() + authCodeData.duration_days);
      
      // 5. Create the user
      const userResult = await new sql.Request(transaction)
        .input('email', sql.NVarChar, email)
        .input('password', sql.NVarChar, hashedPassword)
        .input('firstName', sql.NVarChar, firstName)
        .input('lastName', sql.NVarChar, lastName)
        .input('tierId', sql.Int, authCodeData.tier_id)
        .input('subscriptionStart', sql.DateTime2, subscriptionStart)
        .input('subscriptionEnd', sql.DateTime2, subscriptionEnd)
        .input('authCodeId', sql.Int, authCodeData.code_id)
        .query(`
          INSERT INTO Users (
            email, password, first_name, last_name, 
            tier_id, subscription_start, subscription_end, auth_code_id
          )
          OUTPUT INSERTED.*
          VALUES (
            @email, @password, @firstName, @lastName,
            @tierId, @subscriptionStart, @subscriptionEnd, @authCodeId
          )
        `);
      
      const newUser = userResult.recordset[0];
      
      // 6. Update the auth code as redeemed
      await new sql.Request(transaction)
        .input('codeId', sql.Int, authCodeData.code_id)
        .input('userId', sql.Int, newUser.user_id)
        .input('redeemedAt', sql.DateTime2, new Date())
        .query(`
          UPDATE AuthCodes
          SET is_redeemed = 1,
              redeemed_by = @userId,
              redeemed_at = @redeemedAt
          WHERE code_id = @codeId
        `);
      
      // Commit the transaction
      await transaction.commit();
      
      // Return user without password
      delete newUser.password;
      return {
        ...newUser,
        tier_name: authCodeData.tier_name
      };
    } catch (err) {
      // Rollback transaction on error
      await transaction.rollback();
      throw err;
    }
  } catch (err) {
    console.error('Registration failed:', err);
    throw err;
  } finally {
    if (pool) {
      await pool.close();
    }
  }
}

/**
 * Authenticate a user and generate JWT token
 * 
 * @param {Object} credentials - Login credentials
 * @param {string} credentials.email - User's email
 * @param {string} credentials.password - User's password
 * @returns {Promise<Object>} User data and token
 * @throws {Error} If authentication fails
 */
export async function loginUser(credentials) {
  const { email, password } = credentials;
  let pool;
  
  try {
    pool = await createDatabaseConnection();
    
    // Find user by email with detailed information
    const result = await pool.request()
      .input('email', sql.NVarChar, email)
      .query(`
        SELECT 
          u.user_id,
          u.email,
          u.password,
          u.first_name,
          u.last_name,
          u.tier_id,
          u.subscription_start,
          u.subscription_end,
          u.created_at,
          u.last_login,
          t.tier_name,
          t.description as tier_description
        FROM Users u
        JOIN SubscriptionTiers t ON u.tier_id = t.tier_id
        WHERE u.email = @email
      `);
    
    if (result.recordset.length === 0) {
      console.log(`User not found: ${email}`);
      throw new Error('Invalid email or password');
    }
    
    const user = result.recordset[0];
    console.log(`User found: ${user.email} (ID: ${user.user_id})`);
    
    // Check if subscription is expired
    const now = new Date();
    const isExpired = user.subscription_end < now;
    
    // Validate password using bcrypt
    const isValidPassword = await bcrypt.compare(password, user.password);
    
    if (!isValidPassword) {
      console.log(`Invalid password for user: ${email}`);
      throw new Error('Invalid email or password');
    }
    
    console.log(`Password validated for user: ${email}`);
    
    // Update last login timestamp
    await pool.request()
      .input('userId', sql.Int, user.user_id)
      .input('lastLogin', sql.DateTime2, now)
      .query(`
        UPDATE Users
        SET last_login = @lastLogin
        WHERE user_id = @userId
      `);
    
    // Create formatted user object with proper field naming
    const formattedUser = {
      id: user.user_id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      tierId: user.tier_id,
      tierName: user.tier_name,
      subscriptionStart: user.subscription_start,
      subscriptionEnd: user.subscription_end,
      isExpired: isExpired,
      createdAt: user.created_at,
      lastLogin: now
    };
    
    console.log(`Generating token for user: ${email}`);
    
    // Generate JWT token with essential user information
    const token = jwt.sign(
      { 
        id: formattedUser.id,
        email: formattedUser.email,
        tier: formattedUser.tierId,
        tierName: formattedUser.tierName,
        isExpired: formattedUser.isExpired
      },
      process.env.JWT_SECRET || 'default_jwt_secret',
      { expiresIn: '24h' }
    );
    
    console.log(`Login successful for user: ${email}`);
    
    return {
      user: formattedUser,
      token
    };
  } catch (err) {
    console.error('Login failed:', err);
    throw err;
  } finally {
    if (pool) {
      await pool.close();
    }
  }
}

/**
 * Validate an authorization code
 * 
 * @param {string} code - Authorization code to validate
 * @returns {Promise<Object>} Auth code details including tier info
 * @throws {Error} If code is invalid, expired, or already redeemed
 */
export async function validateAuthCode(code) {
  let pool;
  
  try {
    pool = await createDatabaseConnection();
    
    const result = await pool.request()
      .input('code', sql.NVarChar, code)
      .query(`
        SELECT c.*, t.tier_name, t.description, t.features, t.duration_days
        FROM AuthCodes c
        JOIN SubscriptionTiers t ON c.tier_id = t.tier_id
        WHERE c.code = @code
      `);
    
    if (result.recordset.length === 0) {
      throw new Error('Invalid authorization code');
    }
    
    const codeData = result.recordset[0];
    
    // Check if code is already redeemed
    if (codeData.is_redeemed) {
      throw new Error('This authorization code has already been used');
    }
    
    // Check if code is expired
    const now = new Date();
    if (new Date(codeData.expires_at) < now) {
      throw new Error('This authorization code has expired');
    }
    
    return codeData;
  } catch (err) {
    console.error('Authorization code validation failed:', err);
    throw err;
  } finally {
    if (pool) {
      await pool.close();
    }
  }
}

/**
 * Generate a debug JWT token for testing purposes
 * @param {Object} data Debug user data
 * @param {string} data.email Email for the debug token
 * @param {number} data.tierId Optional tier ID 
 * @param {string} data.tierName Optional tier name
 * @param {boolean} data.isExpired Whether to generate an expired token
 * @returns {Object} Debug token information
 */
export const generateDebugToken = async (data) => {
  try {
    const { email, tierId = 1, tierName = 'Basic', isExpired = false } = data;
    
    // Create user payload for JWT
    const payload = {
      user: {
        id: 'debug-user-id',
        email,
        tier: {
          id: tierId,
          name: tierName
        }
      }
    };

    // If generating expired token, set expiration to past date
    const expiresIn = isExpired ? '-1h' : process.env.JWT_EXPIRATION || '24h';
    
    // Generate token
    const token = jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn }
    );
    
    return {
      token,
      user: {
        id: 'debug-user-id',
        email,
        tier: {
          id: tierId,
          name: tierName
        }
      },
      isExpired,
      expiresIn
    };
  } catch (error) {
    console.error('Error generating debug token:', error);
    throw new Error('Failed to generate debug token');
  }
};

/**
 * Verify a JWT token
 * @param {string} token - The JWT token to verify
 * @returns {Object} The decoded token payload
 * @throws {Error} If token is invalid or expired
 */
export const verifyToken = (token) => {
  try {
    if (!token) {
      throw new Error('No token provided');
    }
    
    // Verify and decode the token
    const decoded = jwt.verify(
      token, 
      process.env.JWT_SECRET || 'default_jwt_secret'
    );
    
    return decoded;
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      throw new Error('Token has expired');
    }
    if (error.name === 'JsonWebTokenError') {
      throw new Error('Invalid token');
    }
    throw error;
  }
}; 