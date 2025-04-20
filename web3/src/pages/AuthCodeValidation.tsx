/**
 * Authorization Code Validation Page
 * 
 * This page is the first step in the signup process where users enter their
 * authorization code before proceeding to registration. It:
 * - Validates the authorization code with the backend
 * - Shows information about the subscription tier associated with the code
 * - Allows proceeding to the registration form upon successful validation
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoImg from '../assets/logo_transparent.png';
import { API_BASE_URL } from '../config';

const AuthCodeValidation = () => {
  // Form state
  const [authCode, setAuthCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [validatedCode, setValidatedCode] = useState<any>(null);
  
  // Navigation
  const navigate = useNavigate();

  /**
   * Validates the authorization code with the backend
   * 
   * @param {React.FormEvent} e - Form submission event
   */
  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form input
    if (!authCode.trim()) {
      setError('Please enter your authorization code');
      return;
    }
    
    try {
      // Set loading state and clear previous errors
      setLoading(true);
      setError('');
      
      // Make API request to validate code endpoint
      const response = await fetch(`${API_BASE_URL}/api/auth/validate-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: authCode })
      });
      
      // Parse response data
      const data = await response.json();
      
      // Handle unsuccessful validation
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'Invalid authorization code');
      }
      
      // Store validated code information and show subscription details
      setValidatedCode(data.code);
      
    } catch (err: any) {
      // Display appropriate error message
      setError(err.message || 'Failed to validate authorization code');
      setValidatedCode(null);
    } finally {
      // Reset loading state regardless of outcome
      setLoading(false);
    }
  };

  /**
   * Proceeds to registration with the validated code
   */
  const handleProceed = () => {
    // Navigate to registration page with the validated code
    navigate('/register', { state: { authCode, codeData: validatedCode } });
  };

  return (
    // Main container with full height and centered content
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header section with logo/title */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <img src={logoImg} alt="Asireon AI Logo" className="h-24 w-auto" />
        </div>
        <h2 className="mt-3 text-center text-3xl font-extrabold text-gray-900">
          Asireon AI
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your authorization code to begin
        </p>
      </div>

      {/* Authorization code form card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Error message display */}
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 text-red-700">
              <p>{error}</p>
            </div>
          )}
          
          {/* Validated code information display */}
          {validatedCode && (
            <div className="mb-6 bg-green-50 border-l-4 border-green-500 p-4">
              <h3 className="text-lg font-medium text-green-800">Valid Authorization Code!</h3>
              <div className="mt-2 text-sm text-green-700">
                <p>Subscription Tier: <span className="font-semibold">{validatedCode.tier_name}</span></p>
                <p className="mt-1">{validatedCode.description}</p>
                <p className="mt-1">Expires: {new Date(validatedCode.expires_at).toLocaleDateString()}</p>
              </div>
            </div>
          )}
          
          {!validatedCode ? (
            // Authorization code form
            <form className="space-y-6" onSubmit={handleValidate}>
              {/* Authorization code input field */}
              <div>
                <label htmlFor="authCode" className="block text-sm font-medium text-gray-700">
                  Authorization Code
                </label>
                <div className="mt-1">
                  <input
                    id="authCode"
                    name="authCode"
                    type="text"
                    required
                    value={authCode}
                    onChange={(e) => setAuthCode(e.target.value)}
                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Enter your authorization code"
                  />
                </div>
              </div>

              {/* Validate button with loading state */}
              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                    loading ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? 'Validating...' : 'Validate Code'}
                </button>
              </div>
            </form>
          ) : (
            // Proceed button after successful validation
            <div className="space-y-4">
              <button
                onClick={handleProceed}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Proceed to Registration
              </button>
              <button
                onClick={() => setValidatedCode(null)}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Try a Different Code
              </button>
            </div>
          )}
          
          {/* Login link */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  Already have an account?
                </span>
              </div>
            </div>
            <div className="mt-6 text-center">
              <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Sign in to your account
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthCodeValidation; 