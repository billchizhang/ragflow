// Test database connection script
import dotenv from 'dotenv';
import sql from 'mssql';

// Load environment variables
dotenv.config();

const config = {
  server: process.env.AZURE_SQL_SERVER,
  database: process.env.AZURE_SQL_DATABASE,
  user: process.env.AZURE_SQL_USER,
  password: process.env.AZURE_SQL_PASSWORD,
  port: parseInt(process.env.AZURE_SQL_PORT || '1433'),
  options: {
    encrypt: true,
    trustServerCertificate: false
  }
};

async function testConnection() {
  console.log('Testing connection to Azure SQL database...');
  console.log('Connection config:', {
    server: config.server,
    database: config.database,
    user: config.user,
    port: config.port
  });

  try {
    // Attempt to connect
    await sql.connect(config);
    console.log('Connection successful!');
    
    // Test a simple query
    const result = await sql.query`SELECT 1 as test`;
    console.log('Query result:', result.recordset);
    
    // Close the connection
    await sql.close();
  } catch (error) {
    console.error('Connection failed:', error);
  }
}

// Run the test
testConnection(); 