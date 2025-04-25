#!/bin/bash

# Start and Test Script for Web3 Authorization Code
# This script starts the web3 server in development mode and then runs the tests

# Set working directory to the location of this script
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Starting Web3 Server in Development Mode ===${NC}"
echo -e "${YELLOW}=== This will start the server in the background ===${NC}"

# Set development mode
export DEV_MODE=true

# Change to web3 directory
cd ../

# Start the server in the background
echo -e "${YELLOW}Starting server...${NC}"
npm run server > server.log 2>&1 &
SERVER_PID=$!

# Wait for the server to start
echo -e "${YELLOW}Waiting for server to start (5 seconds)...${NC}"
sleep 5

# Check if the server is running
if kill -0 $SERVER_PID 2>/dev/null; then
  echo -e "${GREEN}Server is running with PID $SERVER_PID${NC}"
else
  echo -e "${RED}Failed to start the server. Check server.log for details.${NC}"
  exit 1
fi

# Change back to tests directory
cd tests/

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing test dependencies...${NC}"
  npm install
fi

# Run the test
echo -e "${YELLOW}=== Running Authorization Code Test ===${NC}"
node test-auth-code-registration.js

# Store the test result
TEST_RESULT=$?

# Kill the server
echo -e "${YELLOW}Stopping server (PID $SERVER_PID)...${NC}"
kill $SERVER_PID

# Wait for server to stop
sleep 2

# Check test result
if [ $TEST_RESULT -eq 0 ]; then
  echo -e "${GREEN}=== Test completed successfully! ===${NC}"
else
  echo -e "${RED}=== Test failed! ===${NC}"
fi

# Exit with the test result
exit $TEST_RESULT 