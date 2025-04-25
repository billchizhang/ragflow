#!/usr/bin/env node

/**
 * Quick CLI Script to Generate an Authorization Code
 * 
 * This script generates an authorization code using the debug endpoint
 * and outputs it to the console. Useful for quick testing.
 * 
 * Usage:
 *   node generate-auth-code.js [baseUrl]
 * 
 * Example:
 *   node generate-auth-code.js http://localhost:5001
 */

import fetch from 'node-fetch';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Parse command line arguments
const args = process.argv.slice(2);
const baseUrl = args[0] || process.env.API_BASE_URL || 'http://localhost:5001';
const API_URL = `${baseUrl}/api/debug/generate-auth-code`;

console.log(`Using API endpoint: ${API_URL}`);

/**
 * Generate an authorization code using the debug endpoint
 */
async function generateAuthCode() {
  console.log('Generating authorization code...');
  
  try {
    const response = await fetch(API_URL);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(`API error: ${data.message}`);
    }
    
    console.log('\n=======================================');
    console.log('AUTHORIZATION CODE GENERATED');
    console.log('=======================================');
    console.log(`Code: ${data.auth_code}`);
    console.log(`Tier: ${data.tier_name}`);
    console.log(`Expires: ${new Date(data.expires_at).toLocaleString()}`);
    console.log('=======================================');
    console.log('\nUse this code to register a new user at:');
    console.log(`${baseUrl}/register`);
    
    return data.auth_code;
  } catch (error) {
    console.error('Failed to generate authorization code:', error);
    
    if (error.code === 'ECONNREFUSED') {
      console.error('\n=============================================');
      console.error('ERROR: Could not connect to the server!');
      console.error('=============================================');
      console.error('Please ensure:');
      console.error('1. The web3 server is running');
      console.error(`2. It's accessible at ${baseUrl}`);
      console.error('3. The development mode is enabled (DEV_MODE=true)');
      console.error('\nTo start the server:');
      console.error('$ cd /Users/billzhang/Documents/GitHub/ragflow/web3');
      console.error('$ export DEV_MODE=true');
      console.error('$ npm run server');
      console.error('\nIf port 5001 is already in use, try a different port:');
      console.error('$ PORT=5002 npm run server');
      console.error('$ node generate-auth-code.js http://localhost:5002');
      console.error('=============================================');
    }
    
    throw error;
  }
}

// Run the generator
generateAuthCode()
  .then(() => {
    process.exit(0);
  })
  .catch(() => {
    process.exit(1);
  }); 