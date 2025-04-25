/**
 * Test Change Password Script
 * 
 * This script tests the change password functionality of the API
 */

import fetch from 'node-fetch';

async function main() {
  try {
    // 1. Get current server status
    console.log('Checking server status...');
    const statusResponse = await fetch('http://localhost:5001/api/debug/status');
    const statusData = await statusResponse.json();
    console.log('Server Mode:', statusData.serverMode);
    console.log('Mock User:', statusData.mockUser ? 'Configured' : 'Not configured');
    
    // 2. Reset password to default
    console.log('\nResetting password to default...');
    const resetResponse = await fetch('http://localhost:5001/api/debug/reset-password');
    const resetData = await resetResponse.json();
    console.log('Reset Response:', resetData);
    
    // 3. Attempt password change with default password
    console.log('\nChanging password...');
    const changeResponse = await fetch('http://localhost:5001/api/user/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-jwt-token'
      },
      body: JSON.stringify({
        currentPassword: 'password',
        newPassword: 'newpassword123'
      })
    });
    
    const changeData = await changeResponse.json();
    console.log('Change Password Response:', changeData);
    
    // 4. Verify the change by attempting to use old password
    console.log('\nVerifying change by attempting with old password...');
    const verifyResponse = await fetch('http://localhost:5001/api/user/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-jwt-token'
      },
      body: JSON.stringify({
        currentPassword: 'password',
        newPassword: 'testpassword'
      })
    });
    
    const verifyData = await verifyResponse.json();
    console.log('Verification Response:', verifyData);
    
    // 5. Verify the change by attempting with new password
    console.log('\nVerifying change by attempting with new password...');
    const verify2Response = await fetch('http://localhost:5001/api/user/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-jwt-token'
      },
      body: JSON.stringify({
        currentPassword: 'newpassword123',
        newPassword: 'password'
      })
    });
    
    const verify2Data = await verify2Response.json();
    console.log('Verification with new password Response:', verify2Data);
    
    console.log('\nTest completed.');
  } catch (error) {
    console.error('Error during test:', error);
  }
}

main(); 