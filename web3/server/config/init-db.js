/**
 * Database Initialization Script
 * 
 * This script initializes the Azure SQL database with required tables and data.
 */

import { createDatabaseConnection } from './database.js';
import { passwordConfig } from './config.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Initialize Database
 * 
 * Creates necessary tables and initializes the database schema.
 */
export async function initializeDatabase() {
  let db;
  try {
    // Create database connection
    db = await createDatabaseConnection(passwordConfig);
    
    // Read SQL initialization script
    const initScript = fs.readFileSync(
      path.join(__dirname, 'init.sql'),
      'utf8'
    );

    // Split the script into individual statements
    const statements = initScript
      .split(';')
      .map(statement => statement.trim())
      .filter(statement => statement.length > 0);

    // Execute each statement
    for (const statement of statements) {
      await db.executeNonQuery(statement);
      console.log('Executed SQL statement successfully');
    }

    console.log('Database initialization completed successfully');
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  } finally {
    if (db) {
      await db.disconnect();
    }
  }
}

// Run initialization
initializeDatabase(); 