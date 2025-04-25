/**
 * API Test File
 * 
 * Run this file with: node server/testapi.js
 * Shows the current configuration of the server
 */

import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Read development mode flag
const DEV_MODE = process.env.DEV_MODE === 'true';

console.log('Server configuration:');
console.log('--------------------');
console.log(`DEV_MODE: ${DEV_MODE}`);
console.log(`PORT: ${process.env.PORT || 5001}`);
console.log(`JWT_SECRET: ${process.env.JWT_SECRET ? '[Set]' : '[Not Set]'}`);
console.log(`NODE_ENV: ${process.env.NODE_ENV}`);
console.log('--------------------');
console.log('APIs that should be available:');
console.log('- POST /api/auth/login');

if (DEV_MODE) {
  console.log('- POST /api/user/change-password (mock)');
  console.log('- GET /api/user/profile (mock)');
} 

console.log('- All other auth routes from authRoutes.js');
console.log('- All user routes from userRoutes.js'); 