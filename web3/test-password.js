import bcrypt from 'bcryptjs';

const oldHashedPassword = '$2a$10$mLK.rrdlvx9DCFb6Eck1t.TlltnGulepXnov3bBp5T5v7O3p3imai'; // The existing hash that's not working

async function testPassword() {
  try {
    // Test with the old hash
    const isValid1 = await bcrypt.compare('password', oldHashedPassword);
    console.log('Comparing "password" with old stored hash:', isValid1);
    
    // Generate a new hash
    const newHashedPassword = await bcrypt.hash('password', 10);
    console.log('New hash generated:', newHashedPassword);
    
    // Test with the new hash
    const isValid2 = await bcrypt.compare('password', newHashedPassword);
    console.log('Comparing "password" with new hash:', isValid2);
    
    // Test with wrong password
    const isValid3 = await bcrypt.compare('wrongpassword', newHashedPassword);
    console.log('Comparing "wrongpassword" with new hash:', isValid3);
  } catch (error) {
    console.error('Error during password verification:', error);
  }
}

testPassword(); 