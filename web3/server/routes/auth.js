/**
 * Authentication Routes
 * 
 * This module handles all authentication-related API endpoints, including:
 * - User registration
 * - Login
 * - Password reset request
 * - Password reset verification and update
 * 
 * Each route includes input validation, error handling, and appropriate responses.
 */

import express from 'express';
import { body, validationResult } from 'express-validator';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { createDatabaseConnection } from '../config/database.js';
import { sendPasswordResetEmail } from '../utils/email.js';
import { registerUser, loginUser, validateAuthCode } from '../services/authService.js';

// Test connection to database on module load
(async () => {
  try {
    const pool = await createDatabaseConnection();
    console.log('Authentication routes connected to database');
    await pool.close();
  } catch (error) {
    console.error('Failed to connect to database:', error.message);
  }
})();

const router = express.Router();

/**
 * @route   POST /api/auth/register
 * @desc    Register a new user with an authorization code
 * @access  Public
 * 
 * Creates a new user account with the provided email, password, and personal details.
 * Returns a JWT token upon successful registration.
 * 
 * Request body:
 * - email: User's email address (must be valid format)
 * - password: User's password (minimum 6 characters)
 * - firstName: User's first name
 * - lastName: User's last name
 * - authCode: User's authorization code
 * 
 * Response:
 * - token: JWT token for authentication
 * - user: User details (id, email, firstName, lastName)
 * - msg: Success message
 */
router.post('/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName, authCode } = req.body;
    
    // Validate request data
    if (!email || !password || !firstName || !lastName || !authCode) {
      return res.status(400).json({ 
        success: false, 
        message: 'All fields are required' 
      });
    }
    
    // Register the user
    const user = await registerUser({
      email,
      password,
      firstName,
      lastName,
      authCode
    });
    
    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      user
    });
  } catch (err) {
    console.error('Registration error:', err);
    res.status(400).json({
      success: false,
      message: err.message || 'Registration failed'
    });
  }
});

/**
 * @route   POST /api/auth/login
 * @desc    Authenticate user & get token
 * @access  Public
 * 
 * Authenticates a user with email and password.
 * Returns a JWT token upon successful authentication.
 * 
 * Request body:
 * - email: User's email address
 * - password: User's password
 * 
 * Response:
 * - token: JWT token for authentication
 * - user: User details (id, email, firstName, lastName)
 */
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Validate request data
    if (!email || !password) {
      console.log('Login attempt failed: Missing email or password');
      return res.status(400).json({ 
        success: false, 
        message: 'Email and password are required' 
      });
    }
    
    console.log(`Login attempt for email: ${email}`);
    
    // Authenticate user against database
    try {
      const authData = await loginUser({ email, password });
      
      console.log(`Login successful for user: ${authData.user.email} (ID: ${authData.user.id})`);
      
      // Return success with token and user data
      return res.json({
        success: true,
        message: 'Login successful',
        token: authData.token,
        user: authData.user
      });
    } catch (authError) {
      console.error(`Authentication failed for email: ${email}`, authError.message);
      
      // Return authentication error
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }
  } catch (err) {
    console.error('Login error:', err);
    
    // Return general server error
    return res.status(500).json({
      success: false,
      message: 'Server error during login attempt'
    });
  }
});

/**
 * @route   POST /api/auth/forgot-password
 * @desc    Request password reset
 * @access  Public
 * 
 * Initiates the password reset process by:
 * 1. Verifying the user exists
 * 2. Generating a 6-digit PIN
 * 3. Storing the PIN with an expiration time
 * 4. Sending the PIN to the user's email
 * 
 * Request body:
 * - email: User's email address
 * 
 * Response:
 * - msg: Success message
 */
router.post(
  '/forgot-password',
  [
    // Validate email format
    body('email', 'Please include a valid email').isEmail()
  ],
  async (req, res) => {
    // Validate request data
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email } = req.body;
    let pool;

    try {
      pool = await createDatabaseConnection();
      
      // Check if user exists in database
      const userResult = await pool.request()
        .input('email', email)
        .query('SELECT user_id FROM Users WHERE email = @email');

      if (userResult.recordset.length === 0) {
        return res.status(400).json({ msg: 'User not found' });
      }

      const user = userResult.recordset[0];

      // Generate random 6-digit PIN between 100000 and 999999
      const pin = Math.floor(100000 + Math.random() * 900000).toString();
      
      // Set token expiration time (15 minutes from now)
      const expiresAt = new Date();
      expiresAt.setMinutes(expiresAt.getMinutes() + 15);

      // Remove any existing reset tokens for this user
      await pool.request()
        .input('userId', user.user_id)
        .query('DELETE FROM PasswordResetTokens WHERE user_id = @userId');

      // Store new token in the database with expiration time
      await pool.request()
        .input('userId', user.user_id)
        .input('token', pin)
        .input('expiresAt', expiresAt)
        .query(`
          INSERT INTO PasswordResetTokens (user_id, token, expires_at) 
          VALUES (@userId, @token, @expiresAt)
        `);

      // Send email with PIN using email utility function
      await sendPasswordResetEmail(email, pin);

      // Return success message
      res.json({ msg: 'Password reset PIN sent to your email' });
    } catch (err) {
      // Log error and send generic server error response
      console.error(err.message);
      res.status(500).send('Server error');
    } finally {
      if (pool) {
        await pool.close();
      }
    }
  }
);

/**
 * @route   POST /api/auth/reset-password
 * @desc    Reset password with PIN verification
 * @access  Public
 * 
 * Completes the password reset process by:
 * 1. Verifying the user exists
 * 2. Validating the reset PIN
 * 3. Updating the password with a new hash
 * 4. Removing the used PIN
 * 
 * Request body:
 * - email: User's email address
 * - pin: 6-digit verification PIN
 * - password: New password (minimum 6 characters)
 * 
 * Response:
 * - msg: Success message
 */
router.post(
  '/reset-password',
  [
    // Validation middleware
    body('email', 'Please include a valid email').isEmail(),
    body('pin', 'PIN is required').isLength({ min: 6, max: 6 }),
    body('password', 'Password must be at least 6 characters').isLength({ min: 6 })
  ],
  async (req, res) => {
    // Validate request data against defined rules
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, pin, password } = req.body;
    let pool;

    try {
      pool = await createDatabaseConnection();
      
      // Verify user exists in database
      const userResult = await pool.request()
        .input('email', email)
        .query('SELECT user_id FROM Users WHERE email = @email');

      if (userResult.recordset.length === 0) {
        return res.status(400).json({ msg: 'User not found' });
      }

      const user = userResult.recordset[0];

      // Verify PIN is valid and not expired
      const tokenResult = await pool.request()
        .input('userId', user.user_id)
        .input('token', pin)
        .query(`
          SELECT token_id FROM PasswordResetTokens 
          WHERE user_id = @userId 
          AND token = @token 
          AND expires_at > GETDATE()
        `);

      if (tokenResult.recordset.length === 0) {
        return res.status(400).json({ msg: 'Invalid or expired PIN' });
      }

      // Generate salt and hash for new password
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(password, salt);

      // Update user's password in the database
      await pool.request()
        .input('password', hashedPassword)
        .input('userId', user.user_id)
        .query('UPDATE Users SET password = @password WHERE user_id = @userId');

      // Remove the used reset token from database
      await pool.request()
        .input('userId', user.user_id)
        .query('DELETE FROM PasswordResetTokens WHERE user_id = @userId');

      // Return success message
      res.json({ msg: 'Password updated successfully' });
    } catch (err) {
      // Log error and send generic server error response
      console.error(err.message);
      res.status(500).send('Server error');
    } finally {
      if (pool) {
        await pool.close();
      }
    }
  }
);

/**
 * @route POST /api/auth/validate-code
 * @desc Validate an authorization code
 * @access Public
 */
router.post('/validate-code', async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code) {
      return res.status(400).json({
        success: false,
        message: 'Authorization code is required'
      });
    }
    
    // Validate the auth code
    const codeData = await validateAuthCode(code);
    
    res.json({
      success: true,
      message: 'Valid authorization code',
      code: codeData
    });
  } catch (err) {
    console.error('Code validation error:', err);
    res.status(400).json({
      success: false,
      message: err.message || 'Invalid authorization code'
    });
  }
});

export default router; 