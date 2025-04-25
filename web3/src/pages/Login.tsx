/**
 * Login Page Component
 * 
 * This component provides a user interface for authentication, including:
 * - Email and password input form
 * - Form validation
 * - Error handling and display
 * - API integration with the authentication backend
 * - Navigation after successful login
 * 
 * The component uses the AuthContext to store authentication state
 * after a successful login attempt.
 */

import React, { useState, useContext, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import AuthContext from '../contexts/AuthContext'
import { API_BASE_URL } from '../config'
// Import logo directly with a require statement
// @ts-ignore
import logoImage from '../assets/logo_transparent.png'

const Login = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useContext(AuthContext)
  
  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')

  // Add state for debugging information
  const [debugInfo, setDebugInfo] = useState({
    loginAttempts: 0,
    lastServerResponse: null as any,
    showDebugPanel: false
  });

  // Check for status message in location state (e.g., from registration)
  useEffect(() => {
    if (location.state?.message) {
      setStatusMessage(location.state.message)
    }
  }, [location.state])

  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  // Add toggleDebugPanel function
  const toggleDebugPanel = () => {
    setDebugInfo(prev => ({
      ...prev,
      showDebugPanel: !prev.showDebugPanel
    }));
  };

  /**
   * Form submission handler
   * 
   * Validates form input, makes API request to authenticate user,
   * and handles the response appropriately.
   * 
   * On success: Updates auth context and navigates to home page
   * On failure: Displays appropriate error message
   * 
   * @param {React.FormEvent} e - Form submission event
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Update debug info
    setDebugInfo(prev => ({
      ...prev,
      loginAttempts: prev.loginAttempts + 1
    }));
    
    // Validate form
    if (!formData.email || !formData.password) {
      setError('Please enter both email and password')
      return
    }
    
    try {
      setLoading(true)
      setError('')
      
      // Display logging information directly on screen for debugging
      console.log('Attempting to log in with:', {
        email: formData.email,
        password: formData.password.replace(/./g, '*')
      })
      
      // For debugging only - log the API URL
      console.log(`Attempting to connect to: ${API_BASE_URL}/api/auth/login`)
      
      // Always enable dev mode for easier testing in this demo
      const devMode = true
      console.log(`Dev mode: ${devMode ? 'enabled' : 'disabled'}`)
      
      try {
        // Send login request to server
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Dev-Mode': 'true', // Always use dev mode header
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
          // Add these options to avoid caching issues
          cache: 'no-cache',
          credentials: 'same-origin',
        })
        
        // For debugging only - log the response status
        console.log('Response status:', response.status)
        
        // Get the response data
        let data;
        try {
          data = await response.json();
          
          // Update debug info with server response
          setDebugInfo(prev => ({
            ...prev,
            lastServerResponse: data
          }));
          
          // For debugging only - log the response data
          console.log('Response data:', data);
        } catch (jsonError) {
          console.error('Failed to parse response JSON:', jsonError);
          throw new Error('Invalid response from server');
        }
        
        // If response is not OK, show error message
        if (!response.ok || !data.token || !data.user) {
          console.error('Authentication failed');
          throw new Error(data.message || 'Authentication failed');
        }
        
        // If we got a good response, proceed with normal login
        console.log('Token exists:', !!data.token);
        console.log('User exists:', !!data.user);
        
        // Validate user data format to match what our app expects
        if (!data.user.id || !data.user.email) {
          console.error('User data format is invalid:', data.user)
          throw new Error('Authentication failed: Invalid user data format')
        }
        
        // Log user in using the context
        login(data.token, data.user)
        
        // Redirect to dashboard
        navigate('/')
      } catch (fetchError: any) {
        console.error('Fetch error during login:', fetchError)
        throw new Error(`Fetch error: ${fetchError.message}`)
      }
    } catch (err: any) {
      console.error('Login error:', err)
      
      // Provide more helpful error messages for specific issues
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        setError('Network error: Please check your connection and try again. Server might not be running.')
      } else if (err.message === 'Invalid email or password') {
        setError('Invalid email or password. Please try again or contact support.')
      } else {
        setError(`Login failed: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    // Main container with full height and centered content
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header section with logo/title */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex flex-col items-center">
          <img 
            src={logoImage} 
            alt="Asireon AI Logo" 
            className="h-24 w-auto"
          />
          <h1 className="mt-2 text-center text-xl font-bold text-gray-900">
            Asireon AI
          </h1>
        </div>
        <h2 className="mt-3 text-center text-3xl font-extrabold text-gray-900">
          Sign in to your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your credentials to access your dashboard
        </p>
      </div>

      {/* Login form card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Status message (e.g., from successful registration) */}
          {statusMessage && (
            <div className="mb-4 bg-green-50 border-l-4 border-green-500 p-4 text-green-700">
              <p>{statusMessage}</p>
            </div>
          )}
          
          {/* Error message */}
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 text-red-700">
              <p>{error}</p>
            </div>
          )}
          
          {/* Login form */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Email field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            
            {/* Password field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            
            {/* Remember me & forgot password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                  Remember me
                </label>
              </div>
              
              <div className="text-sm">
                <a href="/forgot-password" className="font-medium text-blue-600 hover:text-blue-500">
                  Forgot your password?
                </a>
              </div>
            </div>
            
            {/* Submit button */}
            <div>
              <button
                type="submit"
                disabled={loading}
                className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                  loading ? 'opacity-75 cursor-not-allowed' : ''
                }`}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>
          
          {/* Register link */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  Or
                </span>
              </div>
            </div>
            
            <div className="mt-6 text-center">
              <a href="/auth-code" className="font-medium text-blue-600 hover:text-blue-500">
                Sign up for a new account
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Debug panel toggle button */}
      <div className="fixed bottom-4 right-4">
        <button
          type="button"
          onClick={toggleDebugPanel}
          className="px-4 py-2 bg-gray-800 text-white rounded-md text-sm"
        >
          {debugInfo.showDebugPanel ? 'Hide Debug' : 'Show Debug'}
        </button>
      </div>

      {/* Debug information panel */}
      {debugInfo.showDebugPanel && (
        <div className="fixed bottom-16 right-4 w-96 bg-black bg-opacity-80 text-white p-4 rounded-md text-xs overflow-auto max-h-96">
          <h3 className="text-lg font-bold mb-2">Debug Information</h3>
          <div className="mb-2">
            <p>Login Attempts: {debugInfo.loginAttempts}</p>
            <p>API URL: {API_BASE_URL}/api/auth/login</p>
          </div>
          
          {debugInfo.lastServerResponse && (
            <div className="mb-2">
              <h4 className="font-bold">Last Server Response:</h4>
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(debugInfo.lastServerResponse, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Login 