#!/bin/bash

# Change to the web3 directory
cd /Users/billzhang/Documents/GitHub/ragflow/web3

# Initialize the Azure SQL database
echo "Initializing Azure SQL database..."
node server/config/init-db.js

# Start the Node.js server
echo "Starting the Node.js server..."
node server/index.js 