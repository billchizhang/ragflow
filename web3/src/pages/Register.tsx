/**
 * User Registration Page
 * 
 * This page is the second step in the signup process where users enter their personal
 * information and create an account. It includes:
 * - Form with email, name, and password fields
 * - Strong password validation with specific requirements
 * - Account creation using the validated authorization code from the previous step
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

// Password validation helper functions
const hasMinLength = (password: string) => password.length >= 8;
const hasUpperCase = (password: string) => /[A-Z]/.test(password);
const hasDigit = (password: string) => /\d/.test(password);
const hasSpecialChar = (password: string) => /[!@#$%^&*(),.?":{}|<>]/.test(password);

const Register = () => {
  // Get location state from router (contains auth code validation data)
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract auth code data from location state
  const { authCode, codeData } = location.state || {};
  
  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    company: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Password validation state
  const [passwordValidation, setPasswordValidation] = useState({
    minLength: false,
    hasUpperCase: false,
    hasDigit: false,
    hasSpecialChar: false,
    passwordsMatch: false
  });
  
  // Update password validation state whenever password or confirmPassword changes
  useEffect(() => {
    setPasswordValidation({
      minLength: hasMinLength(formData.password),
      hasUpperCase: hasUpperCase(formData.password),
      hasDigit: hasDigit(formData.password),
      hasSpecialChar: hasSpecialChar(formData.password),
      passwordsMatch: formData.password === formData.confirmPassword && formData.password !== ''
    });
  }, [formData.password, formData.confirmPassword]);
  
  // Redirect to auth code validation if no code provided
  useEffect(() => {
    if (!authCode || !codeData) {
      navigate('/auth-code');
    }
  }, [authCode, codeData, navigate]);
  
  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    // Validate password strength
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$/;
    if (!passwordRegex.test(formData.password)) {
      setError('Password must be at least 8 characters long and include at least 1 uppercase letter, 1 digit, and 1 special character');
      return;
    }
    
    // Validate that both first and last name are provided
    if (!formData.firstName || !formData.lastName) {
      setError('First name and last name are required');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // Send registration request to server
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          firstName: formData.firstName,
          lastName: formData.lastName,
          company: formData.company,
          authCode: authCode,
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }
      
      // If successful, navigate to login page
      navigate('/login', { 
        state: { 
          message: 'Registration successful! Please login with your new account.' 
        } 
      });
      
    } catch (err: any) {
      setError(err.message || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };
  
  // If no auth code data, show loading
  if (!authCode || !codeData) {
    return <div className="min-h-screen flex justify-center items-center">Redirecting...</div>;
  }
  
  // Helper function to render validation requirements
  const renderRequirement = (isValid: boolean, text: string) => (
    <li className="flex items-center mt-1">
      <span className={`mr-2 text-lg ${isValid ? 'text-green-500' : 'text-gray-400'}`}>
        {isValid ? '✓' : '○'}
      </span>
      <span className={`text-xs ${isValid ? 'text-green-600' : 'text-gray-500'}`}>{text}</span>
    </li>
  );
  
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header section with logo and title */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="h-24 w-auto bg-blue-600 text-white px-6 py-4 rounded-lg flex items-center justify-center">
            <span className="text-3xl font-bold">Asireon AI</span>
          </div>
        </div>
        <h2 className="mt-3 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Your authorization code has been validated
        </p>
      </div>

      {/* Registration form card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Subscription information */}
          <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4">
            <h3 className="text-lg font-medium text-blue-800">Subscription Details</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>Tier: <span className="font-semibold">{codeData.tier_name}</span></p>
              <p className="mt-1">{codeData.description}</p>
              <p className="mt-1">Valid until: {new Date(codeData.expires_at).toLocaleDateString()}</p>
            </div>
          </div>
          
          {/* Error message */}
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 text-red-700">
              <p>{error}</p>
            </div>
          )}
          
          {/* Registration form */}
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
            
            {/* First Name field */}
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <div className="mt-1">
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  autoComplete="given-name"
                  required
                  value={formData.firstName}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            
            {/* Last Name field */}
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <div className="mt-1">
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  autoComplete="family-name"
                  required
                  value={formData.lastName}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            
            {/* Company field */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                Company (Optional)
              </label>
              <div className="mt-1">
                <input
                  id="company"
                  name="company"
                  type="text"
                  autoComplete="organization"
                  value={formData.company}
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
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <div className="mt-2">
                <p className="text-xs font-medium text-gray-700 mb-1">Password requirements:</p>
                <ul className="ml-2">
                  {renderRequirement(passwordValidation.minLength, "At least 8 characters")}
                  {renderRequirement(passwordValidation.hasUpperCase, "At least 1 uppercase letter")}
                  {renderRequirement(passwordValidation.hasDigit, "At least 1 number")}
                  {renderRequirement(passwordValidation.hasSpecialChar, "At least 1 special character")}
                </ul>
              </div>
            </div>
            
            {/* Confirm Password field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <div className="mt-1">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              {formData.confirmPassword && (
                <div className="mt-2">
                  {renderRequirement(passwordValidation.passwordsMatch, "Passwords match")}
                </div>
              )}
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
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </div>
          </form>
          
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

export default Register; 