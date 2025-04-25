/**
 * User Routes
 * 
 * This module handles all user-related API endpoints, including:
 * - Fetching user profile data
 * - Updating user profile
 * - Password changes
 * - Account deletion
 * 
 * All routes in this module require authentication.
 */

import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { createDatabaseConnection } from '../config/database.js';

const router = express.Router();

// Authentication middleware
const authenticateToken = (req, res, next) => {
  // Get the token from the Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'Access denied. No token provided.' 
    });
  }
  
  try {
    // Verify the token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default_jwt_secret');
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ 
      success: false, 
      message: 'Invalid token.' 
    });
  }
};

/**
 * @route   GET /api/user/profile
 * @desc    Get user profile data
 * @access  Private
 * 
 * Fetches the user's profile information from the database
 * based on the user ID from the JWT token.
 * 
 * Response:
 * - user: User profile data (id, email, firstName, lastName, etc.)
 */
router.get('/profile', authenticateToken, async (req, res) => {
  let pool;
  
  try {
    // Connect to the SQL Server database
    pool = await createDatabaseConnection();
    
    // Query user data from SQL Server
    const result = await pool.request()
      .input('userId', req.user.id)
      .query(`
        SELECT u.user_id as id, u.email, u.first_name as firstName, u.last_name as lastName,
               t.tier_name as tierName, 
               CASE WHEN u.subscription_end < GETDATE() THEN 1 ELSE 0 END as isExpired
        FROM Users u
        JOIN SubscriptionTiers t ON u.tier_id = t.tier_id
        WHERE u.user_id = @userId
      `);
    
    if (result.recordset.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    return res.json({
      success: true,
      user: result.recordset[0]
    });
  } catch (err) {
    console.error('Error fetching user profile:', err);
    res.status(500).json({
      success: false,
      message: 'Server error while fetching profile data'
    });
  } finally {
    if (pool) {
      await pool.close();
    }
  }
});

/**
 * @route   POST /api/user/change-password
 * @desc    Change user password
 * @access  Private
 * 
 * Updates the user's password after verifying their current password.
 * 
 * Request body:
 * - currentPassword: User's current password
 * - newPassword: User's new password (minimum 6 characters)
 * 
 * Response:
 * - success: Boolean indicating success
 * - message: Success or error message
 */
router.post('/change-password', authenticateToken, async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  let pool;
  
  // Basic validation
  if (!currentPassword || !newPassword) {
    return res.status(400).json({
      success: false,
      message: 'Both current password and new password are required'
    });
  }
  
  if (newPassword.length < 6) {
    return res.status(400).json({
      success: false,
      message: 'New password must be at least 6 characters'
    });
  }
  
  try {
    // Connect to the database
    pool = await createDatabaseConnection();
    
    // Get user record with password for verification
    const userResult = await pool.request()
      .input('userId', req.user.id)
      .query('SELECT password FROM Users WHERE user_id = @userId');
    
    if (userResult.recordset.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    const user = userResult.recordset[0];
    
    // Verify current password
    const isMatch = await bcrypt.compare(currentPassword, user.password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Current password is incorrect'
      });
    }
    
    // Hash the new password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(newPassword, salt);
    
    // Update the password in the database
    await pool.request()
      .input('password', hashedPassword)
      .input('userId', req.user.id)
      .query('UPDATE Users SET password = @password WHERE user_id = @userId');
    
    // Return success response
    return res.json({
      success: true,
      message: 'Password updated successfully'
    });
  } catch (err) {
    console.error('Error changing password:', err);
    return res.status(500).json({
      success: false,
      message: 'Server error while updating password'
    });
  } finally {
    if (pool) {
      await pool.close();
    }
  }
});

export default router; 