// Simple script to test the Azure SQL database connection
import dotenv from 'dotenv';
import sql from 'mssql';

// Load environment variables from .env file
dotenv.config();

const config = {
  server: process.env.AZURE_SQL_SERVER,
  database: process.env.AZURE_SQL_DATABASE,
  user: process.env.AZURE_SQL_USER,
  password: process.env.AZURE_SQL_PASSWORD,
  port: parseInt(process.env.AZURE_SQL_PORT || '1433'),
  options: {
    encrypt: true, // Required for Azure SQL
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
    // Attempt to connect to the database
    await sql.connect(config);
    console.log('Connection successful!');
    
    // Execute a simple query to verify the connection
    const result = await sql.query`SELECT 1 as test`;
    console.log('Query result:', result.recordset);
    
    // Close the connection
    await sql.close();
  } catch (error) {
    console.error('Connection failed:', error);
  }
}

testConnection(); 