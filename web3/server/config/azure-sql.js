/**
 * Azure SQL Database Configuration Module
 * 
 * This module handles the Azure SQL Database connection configuration
 * and provides functions for database operations.
 */

const { Connection, Request } = require('tedious');
const { config } = require('dotenv');
config();

/**
 * Azure SQL Database Configuration
 * 
 * Creates a connection configuration for Azure SQL Database using environment variables.
 * 
 * Configuration:
 * - server: Azure SQL server name (from AZURE_SQL_SERVER env)
 * - authentication: SQL authentication with username and password
 * - options: Database configuration options
 *   - database: Database name (from AZURE_SQL_DATABASE env)
 *   - encrypt: Enable encryption
 *   - trustServerCertificate: Trust server certificate
 *   - rowCollectionOnDone: Return rows as collections
 *   - useColumnNames: Use column names in results
 */
const dbConfig = {
  server: process.env.AZURE_SQL_SERVER,
  authentication: {
    type: 'default',
    options: {
      userName: process.env.AZURE_SQL_USER,
      password: process.env.AZURE_SQL_PASSWORD
    }
  },
  options: {
    database: process.env.AZURE_SQL_DATABASE,
    encrypt: true,
    trustServerCertificate: true,
    rowCollectionOnDone: true,
    useColumnNames: true,
    connectTimeout: 30000, // 30 seconds
    requestTimeout: 30000, // 30 seconds
    connectionRetryInterval: 1000, // 1 second
    maxRetriesOnTransientErrors: 3
  }
};

/**
 * Create Database Connection
 * 
 * Creates a connection to Azure SQL Database
 * 
 * @returns {Promise<Connection>} - Resolves with the database connection
 */
async function createConnection() {
  return new Promise((resolve, reject) => {
    const connection = new Connection(dbConfig);
    
    connection.on('connect', (err) => {
      if (err) {
        console.error('Connection error:', err);
        reject(err);
      } else {
        console.log('Successfully connected to Azure SQL Database');
        resolve(connection);
      }
    });

    connection.on('error', (err) => {
      console.error('Connection error:', err);
      reject(err);
    });

    connection.connect();
  });
}

/**
 * Execute SQL Query
 * 
 * Executes a SQL query and returns the results
 * 
 * @param {string} query - SQL query to execute
 * @param {Array} params - Query parameters
 * @returns {Promise<Array>} - Resolves with query results
 */
async function executeQuery(query, params = []) {
  const connection = await createConnection();
  
  return new Promise((resolve, reject) => {
    const request = new Request(query, (err, rowCount, rows) => {
      connection.close();
      if (err) {
        console.error('Query execution error:', err);
        reject(err);
      } else {
        console.log(`Query executed successfully. Rows affected: ${rowCount}`);
        resolve(rows);
      }
    });

    // Add parameters if provided
    params.forEach(param => {
      request.addParameter(param.name, param.type, param.value);
    });

    connection.execSql(request);
  });
}

/**
 * Test Database Connection
 * 
 * Tests the database connection and logs the connection status.
 * 
 * @returns {Promise<boolean>} - Resolves with true if connection is successful
 */
async function testConnection() {
  try {
    const connection = await createConnection();
    console.log('Database connection successful');
    connection.close();
    return true;
  } catch (error) {
    console.error('Database connection failed:', error.message);
    console.error('Please check your database configuration and ensure the Azure SQL server is accessible.');
    return false;
  }
}

module.exports = {
  createConnection,
  executeQuery,
  testConnection,
  dbConfig
}; 