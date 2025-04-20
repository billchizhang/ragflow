/**
 * Azure SQL Database Connection Module
 * 
 * This module provides functionality to connect to Azure SQL database.
 * It uses the mssql package to establish and manage connections.
 */

import sql from 'mssql';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Database configuration for Azure SQL
 * 
 * Uses environment variables for sensitive information:
 * - AZURE_SQL_SERVER: Azure SQL server address
 * - AZURE_SQL_DATABASE: Database name
 * - AZURE_SQL_USER: SQL server username
 * - AZURE_SQL_PASSWORD: SQL server password
 * - AZURE_SQL_PORT: SQL server port (default: 1433)
 */
export const sqlConfig = {
  server: process.env.AZURE_SQL_SERVER,
  database: process.env.AZURE_SQL_DATABASE,
  user: process.env.AZURE_SQL_USER,
  password: process.env.AZURE_SQL_PASSWORD,
  port: parseInt(process.env.AZURE_SQL_PORT || '1433'),
  options: {
    encrypt: true, // Use encryption (required for Azure SQL)
    trustServerCertificate: false, // Change to true for local dev / self-signed certs
    enableArithAbort: true
  }
};

/**
 * Creates a connection to the Azure SQL database
 * 
 * @param {Object} config - Database configuration object (optional, uses default if not provided)
 * @returns {Promise<Object>} SQL connection pool
 * @throws {Error} If connection fails
 */
export async function createDatabaseConnection(config = sqlConfig) {
  try {
    console.log('Connecting to Azure SQL database...');
    const pool = await sql.connect(config);
    console.log('Database connection established successfully');
    return pool;
  } catch (err) {
    console.error('Database connection failed:', err);
    throw new Error(`Failed to connect to database: ${err.message}`);
  }
}

/**
 * Test database connection
 * 
 * @returns {Promise<boolean>} True if connection successful, false otherwise
 */
export async function testDatabaseConnection() {
  try {
    const pool = await createDatabaseConnection();
    const result = await pool.request().query('SELECT 1 as testConnection');
    await pool.close();
    return result.recordset[0].testConnection === 1;
  } catch (err) {
    console.error('Test connection failed:', err);
    return false;
  }
} 