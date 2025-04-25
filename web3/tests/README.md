# Web3 Authentication Tests

This directory contains test scripts for the Web3 authentication system.

## Prerequisites

Before running any tests, make sure:

1. The web3 server is running in development mode:
   ```bash
   # From the web3 directory
   cd ../
   export DEV_MODE=true
   npm run server
   ```

2. The server is accessible at http://localhost:5001 (default) or your custom URL

## Test Authorization Code Registration

The `test-auth-code-registration.js` script tests the complete authentication flow:

1. Generating a new authorization code via the debug endpoint
2. Validating the code
3. Registering a new user with the code
4. Logging in with the new user credentials

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in this directory with the following content (optional):
   ```
   # API Configuration (optional - can also be specified on command line)
   API_BASE_URL=http://localhost:5001
   
   # Test User Configuration (optional - defaults are in the script)
   # TEST_USER_EMAIL=test@example.com
   # TEST_USER_PASSWORD=Password123!
   # TEST_USER_FIRST_NAME=Test
   # TEST_USER_LAST_NAME=User
   ```

### Running the Test

Run with the default URL (http://localhost:5001):
```bash
npm test
```

Or specify a custom server URL:
```bash
node test-auth-code-registration.js http://your-server-url
```

### Troubleshooting Connection Issues

If you see `ECONNREFUSED` errors:

1. Make sure the web3 server is running:
   ```bash
   # From the web3 directory
   cd ../
   npm run server
   ```

2. Check that the server is running in development mode by setting the environment variable:
   ```bash
   # On macOS/Linux
   export DEV_MODE=true
   npm run server
   
   # On Windows
   set DEV_MODE=true
   npm run server
   ```

3. If using a non-default server URL, make sure to specify it:
   ```bash
   node test-auth-code-registration.js http://your-server-url
   ```

4. If port 5001 is already in use, you can specify a different port:
   ```bash
   # Start the server on a different port
   PORT=5002 npm run server
   
   # Then run the test with the new port
   node test-auth-code-registration.js http://localhost:5002
   ```

### Expected Output

The test will output progress messages for each step of the authentication flow:

```
Using API base URL: http://localhost:5001/api
Checking server status...
Server mode: Development
Generating authorization code...
Authorization code generated successfully!
Code: XXXXX-XXXXX-XXXXX
Tier: Premium
Expires: MM/DD/YYYY, HH:MM:SS AM/PM

Validating authorization code: XXXXX-XXXXX-XXXXX
Authorization code is valid!
Tier: Premium
Features: [features list]

Registering new user with email: test-user-1234567890@example.com
User registered successfully!
User ID: 123
Tier: Premium

Logging in with email: test-user-1234567890@example.com
Login successful!
Token: eyJhbGciOiJIUz...
User: Test User
Tier: Premium

✅ Test completed successfully!
```

## Quick Authorization Code Generation

For quickly generating an authorization code without running the full test:

```bash
node generate-auth-code.js
```

Or with a custom server URL:

```bash
node generate-auth-code.js http://your-server-url
```

## Alternative: Manual Testing

You can also test the authorization code generation and registration process manually:

1. Visit `http://localhost:5001/test-auth-code.html` in your browser
2. Click "Generate Authorization Code" to create a new code
3. Use this code in the registration form at `http://localhost:5001/register` 