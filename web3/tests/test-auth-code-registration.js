/**
 * Test Authorization Code Generation and User Registration
 * 
 * This script tests the following workflow:
 * 1. Generate a new authorization code via the debug endpoint
 * 2. Validate the code
 * 3. Register a new user with the code
 * 4. Login with the new user credentials
 * 
 * Usage:
 *   node test-auth-code-registration.js [baseUrl]
 * 
 * Example:
 *   node test-auth-code-registration.js http://localhost:5001
 */

import fetch from 'node-fetch';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Parse command line arguments
const args = process.argv.slice(2);
const baseUrl = args[0] || process.env.API_BASE_URL || 'http://localhost:5001';
const API_BASE_URL = `${baseUrl}/api`;

console.log(`Using API base URL: ${API_BASE_URL}`);

// Configuration
const TEST_USER = {
  email: `test-user-${Date.now()}@example.com`,
  password: 'Password123!',
  firstName: 'Test',
  lastName: 'User'
};

/**
 * Check if the server is running and in development mode
 */
async function checkServer() {
  try {
    console.log('Checking server status...');
    const response = await fetch(`${baseUrl}/api/debug/status`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`Server mode: ${data.serverMode}`);
    
    if (data.serverMode !== 'Development') {
      console.warn('⚠️ Warning: Server is not in development mode. Some features may not work.');
    }
    
    return true;
  } catch (error) {
    console.error('❌ Server check failed:', error);
    
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
      console.error('$ node test-auth-code-registration.js http://localhost:5002');
      console.error('=============================================');
    }
    
    return false;
  }
}

/**
 * Generate an authorization code using the debug endpoint
 */
async function generateAuthCode() {
  console.log('Generating authorization code...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/debug/generate-auth-code`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(`API error: ${data.message}`);
    }
    
    console.log('Authorization code generated successfully!');
    console.log(`Code: ${data.auth_code}`);
    console.log(`Tier: ${data.tier_name}`);
    console.log(`Expires: ${new Date(data.expires_at).toLocaleString()}`);
    
    return data.auth_code;
  } catch (error) {
    console.error('Failed to generate authorization code:', error);
    throw error;
  }
}

/**
 * Validate an authorization code
 */
async function validateAuthCode(code) {
  console.log(`Validating authorization code: ${code}`);
  
  try {
    // The server endpoint expects the code in the request body
    const response = await fetch(`${API_BASE_URL}/auth/validate-code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code })
    });
    
    // For debugging purposes
    const responseText = await response.text();
    console.log('Response from validate-code:', responseText);
    
    let data;
    try {
      // Convert the response text back to JSON
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Invalid JSON response: ${responseText}`);
    }
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}, Message: ${data.message || 'Unknown error'}`);
    }
    
    if (!data.success) {
      throw new Error(`API error: ${data.message}`);
    }
    
    console.log('Authorization code is valid!');
    console.log(`Tier: ${data.code.tier_name}`);
    console.log(`Features: ${data.code.features || 'None'}`);
    
    return data.code;
  } catch (error) {
    console.error('Failed to validate authorization code:', error);
    throw error;
  }
}

/**
 * Register a new user with an authorization code
 */
async function registerUser(authCode) {
  console.log(`Registering new user with email: ${TEST_USER.email}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...TEST_USER,
        authCode
      })
    });
    
    // For debugging purposes
    const responseText = await response.text();
    console.log('Response from register:', responseText);
    
    let data;
    try {
      // Convert the response text back to JSON
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Invalid JSON response: ${responseText}`);
    }
    
    if (!response.ok) {
      throw new Error(`Registration failed: Status ${response.status}, Message: ${data.message || 'Unknown error'}`);
    }
    
    if (!data.success) {
      throw new Error(`API error: ${data.message}`);
    }
    
    console.log('User registered successfully!');
    console.log(`User ID: ${data.user.id}`);
    console.log(`Tier: ${data.user.tierName || data.user.tier_name || 'Unknown'}`);
    
    return data.user;
  } catch (error) {
    console.error('Failed to register user:', error);
    throw error;
  }
}

/**
 * Login with user credentials
 */
async function loginUser() {
  console.log(`Logging in with email: ${TEST_USER.email}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: TEST_USER.email,
        password: TEST_USER.password
      })
    });
    
    // For debugging purposes
    const responseText = await response.text();
    console.log('Response from login:', responseText);
    
    let data;
    try {
      // Convert the response text back to JSON
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Invalid JSON response: ${responseText}`);
    }
    
    if (!response.ok) {
      throw new Error(`Login failed: Status ${response.status}, Message: ${data.message || 'Unknown error'}`);
    }
    
    if (!data.success) {
      throw new Error(`API error: ${data.message}`);
    }
    
    console.log('Login successful!');
    if (data.token) {
      console.log(`Token: ${data.token.substring(0, 15)}...`);
    } else {
      console.log('Note: No token returned in response');
    }
    console.log(`User: ${data.user.firstName} ${data.user.lastName}`);
    console.log(`Tier: ${data.user.tierName || data.user.tier_name || 'Unknown'}`);
    
    return {
      token: data.token,
      user: data.user
    };
  } catch (error) {
    console.error('Failed to login:', error);
    throw error;
  }
}

/**
 * Run the full test
 */
async function runTest() {
  try {
    // Step 0: Check if server is running
    const serverRunning = await checkServer();
    if (!serverRunning) {
      process.exit(1);
    }
    
    // Step 1: Generate an authorization code
    const authCode = await generateAuthCode();
    
    // Step 2: Validate the authorization code
    await validateAuthCode(authCode);
    
    // Step 3: Register a new user with the code
    await registerUser(authCode);
    
    // Step 4: Login with the new user
    await loginUser();
    
    console.log('\n✅ Test completed successfully!');
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    process.exit(1);
  }
}

// Run the test
runTest(); 