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

export default router; 