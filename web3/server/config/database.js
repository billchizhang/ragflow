import sql from 'mssql';

export class Database {
  constructor(config) {
    this.config = config;
  }

  async connect() {
    try {
      this.pool = await sql.connect(this.config);
      console.log('Connected to Azure SQL Database');
    } catch (err) {
      console.error('Database connection failed:', err);
      throw err;
    }
  }

  async disconnect() {
    try {
      await this.pool.close();
      console.log('Disconnected from Azure SQL Database');
    } catch (err) {
      console.error('Error disconnecting from database:', err);
      throw err;
    }
  }

  async executeQuery(query, params = {}) {
    try {
      const request = this.pool.request();
      
      // Add parameters to the request
      Object.entries(params).forEach(([key, value]) => {
        request.input(key, value);
      });

      const result = await request.query(query);
      return result.recordset;
    } catch (err) {
      console.error('Error executing query:', err);
      throw err;
    }
  }

  async executeNonQuery(query, params = {}) {
    try {
      const request = this.pool.request();
      
      // Add parameters to the request
      Object.entries(params).forEach(([key, value]) => {
        request.input(key, value);
      });

      const result = await request.query(query);
      return result.rowsAffected;
    } catch (err) {
      console.error('Error executing non-query:', err);
      throw err;
    }
  }
}

export async function createDatabaseConnection(config) {
  const db = new Database(config);
  await db.connect();
  return db;
} 