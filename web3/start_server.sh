#!/bin/bash

# Change to the web3 directory
cd /Users/billzhang/Documents/GitHub/ragflow/web3

# Set environment variables
echo "Setting up environment variables for Azure SQL Database connection..."
export NODE_ENV=production

# Check if Azure SQL credentials are available
if [ -z "$AZURE_SQL_SERVER" ] || [ -z "$AZURE_SQL_DATABASE" ] || [ -z "$AZURE_SQL_USER" ] || [ -z "$AZURE_SQL_PASSWORD" ]; then
    echo "ERROR: Azure SQL Database credentials are not set."
    echo "Please set the following environment variables:"
    echo "  - AZURE_SQL_SERVER"
    echo "  - AZURE_SQL_DATABASE"
    echo "  - AZURE_SQL_USER"
    echo "  - AZURE_SQL_PASSWORD"
    exit 1
fi

# Start the Node.js server
echo "Starting the Node.js server with Azure SQL Database..."
npm run server 