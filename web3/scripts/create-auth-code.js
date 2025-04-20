/**
 * Authorization Code Generation Script
 * 
 * This script creates a new authorization code in the Azure SQL database
 * for testing or for providing to new users.
 */

import sql from 'mssql';
import dotenv from 'dotenv';
import { createDatabaseConnection } from '../server/config/database.js';

// Load environment variables
dotenv.config();

// Configuration
const TIER_ID = process.argv[2] || 3; // Default to Premium tier (tier_id=3)
const EMAIL = process.argv[3] || ''; // Optional email to associate with the code
const VALID_DAYS = process.argv[4] || 30; // Default expiration in 30 days

/**
 * Generates a random authorization code
 * 
 * @param {number} length - Length of the code
 * @returns {string} Random alphanumeric code
 */
function generateAuthCode(length = 12) {
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
 */
async function createAuthCode() {
  let pool;
  
  try {
    console.log('Connecting to Azure SQL database...');
    pool = await createDatabaseConnection();
    console.log('Connected to Azure SQL database');
    
    // Check if the specified tier exists
    const tierResult = await pool.request()
      .input('tierId', sql.Int, TIER_ID)
      .query('SELECT * FROM SubscriptionTiers WHERE tier_id = @tierId');
    
    if (tierResult.recordset.length === 0) {
      throw new Error(`Tier ID ${TIER_ID} not found. Available tiers are:`);
    }
    
    const tier = tierResult.recordset[0];
    
    // Generate a new authorization code
    const code = generateAuthCode();
    const expires_at = new Date();
    expires_at.setDate(expires_at.getDate() + parseInt(VALID_DAYS));
    
    // Insert the code into the database
    const result = await pool.request()
      .input('code', sql.NVarChar, code)
      .input('tierId', sql.Int, TIER_ID)
      .input('issuedEmail', sql.NVarChar, EMAIL)
      .input('expiresAt', sql.DateTime2, expires_at)
      .query(`
        INSERT INTO AuthCodes (code, tier_id, issued_email, expires_at)
        OUTPUT INSERTED.*
        VALUES (@code, @tierId, @issuedEmail, @expiresAt)
      `);
    
    const authCode = result.recordset[0];
    
    // Get the tier name separately
    const tierNameResult = await pool.request()
      .input('tierId', sql.Int, TIER_ID)
      .query('SELECT tier_name FROM SubscriptionTiers WHERE tier_id = @tierId');
    
    const tierName = tierNameResult.recordset[0].tier_name;
    
    console.log('\n=== Authorization Code Created ===');
    console.log(`Code: ${authCode.code}`);
    console.log(`Tier: ${tierName} (ID: ${authCode.tier_id})`);
    console.log(`Expires: ${new Date(authCode.expires_at).toLocaleDateString()}`);
    
    if (authCode.issued_email) {
      console.log(`Issued to: ${authCode.issued_email}`);
    }
    
    console.log('\nUse this code in the registration process');
    
  } catch (err) {
    console.error('Error creating authorization code:', err);
    
    // If tier not found, list available tiers
    if (err.message.includes('not found')) {
      try {
        const tiersResult = await pool.request()
          .query('SELECT tier_id, tier_name, description FROM SubscriptionTiers');
        
        console.log('\nAvailable tiers:');
        tiersResult.recordset.forEach(tier => {
          console.log(`${tier.tier_id}: ${tier.tier_name} - ${tier.description}`);
        });
        
        console.log('\nUsage: node create-auth-code.js [tier_id] [email] [valid_days]');
      } catch (listErr) {
        console.error('Could not list tiers:', listErr);
      }
    }
    
    process.exit(1);
  } finally {
    if (pool) {
      console.log('Closing database connection');
      await pool.close();
    }
  }
}

// Run the script
createAuthCode()
  .then(() => {
    process.exit(0);
  })
  .catch(() => {
    process.exit(1);
  }); 