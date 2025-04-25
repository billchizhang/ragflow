#!/bin/bash

# Change to the web3 directory
cd /Users/billzhang/Documents/GitHub/ragflow/web3

# Set environment variables
echo "Setting up environment variables for Azure SQL Database connection..."
export NODE_ENV=production

# Create .env file if it doesn't exist
if [ ! -f "./server/.env" ]; then
    echo "Creating .env file with default Azure SQL Database settings..."
    cat > ./server/.env << EOL
# Server Configuration
PORT=5001
NODE_ENV=production

# JWT Configuration
JWT_SECRET=ragflow_jwt_secret_key

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
EOL
    echo "Please update the Azure SQL Database credentials in ./server/.env"
    echo "Then run this script again."
    exit 1
fi

# Start the Node.js server
echo "Starting the Node.js server with Azure SQL Database..."
npm run server 