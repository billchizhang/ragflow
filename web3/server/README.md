# Web3 Server

This is the backend server for the Web3 application, providing authentication, user management, and API services.

## Database Configuration

The server connects to Azure SQL Database (MSSQL) for all data storage. MySQL is no longer supported.

## Setup Instructions

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file in the server directory with the following variables:
   ```
   # Server Configuration
   PORT=5001
   NODE_ENV=development

   # JWT Configuration
   JWT_SECRET=your_jwt_secret_key_here

   # Azure SQL Database Configuration
   AZURE_SQL_SERVER=your-server.database.windows.net
   AZURE_SQL_DATABASE=your_database_name
   AZURE_SQL_USER=your_database_username
   AZURE_SQL_PASSWORD=your_database_password
   AZURE_SQL_PORT=1433

   # Email Configuration for Password Reset
   EMAIL_SERVICE=gmail
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-specific-password
   EMAIL_FROM=Your App <your-email@gmail.com>
   ```

3. Start the server:
   ```
   npm run server
   ```

   Or for development with auto-restart:
   ```
   npm run dev:server
   ```

4. Run both frontend and backend concurrently (for development):
   ```
   npm run dev:full
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user with an authorization code
- `POST /api/auth/login` - Authenticate a user and get a JWT token
- `POST /api/auth/forgot-password` - Request a password reset
- `POST /api/auth/reset-password` - Reset a password with a PIN
- `POST /api/auth/validate-code` - Validate an authorization code

### User Management

- `GET /api/user/profile` - Get the authenticated user's profile

## Database Schema

The server requires the following tables in Azure SQL Database:

1. `Users` - Stores user account information
2. `PasswordResetTokens` - Stores tokens for password reset
3. `SubscriptionTiers` - Stores subscription tier information
4. `AuthCodes` - Stores authorization codes for registration

These tables will be created automatically when the server starts if they don't exist. 