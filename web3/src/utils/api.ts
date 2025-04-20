/**
 * API Utilities
 * 
 * This module provides helper functions for making API requests,
 * handling common authentication and error handling patterns.
 */

import { API_BASE_URL, JWT_LOCAL_STORAGE_KEY } from '../config';

/**
 * Make an authenticated API request
 * 
 * @param {string} endpoint - API endpoint path (without base URL)
 * @param {Object} options - Fetch options (method, body, etc.)
 * @returns {Promise<any>} - Parsed JSON response
 * @throws {Error} - If the request fails or returns an error status
 */
export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  // Get the authentication token from localStorage
  const token = localStorage.getItem(JWT_LOCAL_STORAGE_KEY);
  
  // Create headers with authentication if token exists
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  
  // Make the API request
  try {
    console.log(`API request to: ${API_BASE_URL}${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });
    
    // Parse response as JSON
    const data = await response.json();
    
    // If response is not ok, throw an error with the message from the API
    if (!response.ok) {
      throw new Error(data.message || `API error: ${response.status}`);
    }
    
    // Return the successful response data
    return data;
  } catch (error) {
    // Log the error for debugging
    console.error('API request failed:', error);
    
    // Re-throw the error to be handled by the caller
    throw error;
  }
};

/**
 * Make an unauthenticated API request (for login, register, etc.)
 * 
 * @param {string} endpoint - API endpoint path (without base URL)
 * @param {Object} options - Fetch options (method, body, etc.)
 * @returns {Promise<any>} - Parsed JSON response
 * @throws {Error} - If the request fails or returns an error status
 */
export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  // Set default headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  // Make the API request
  try {
    console.log(`API request to: ${API_BASE_URL}${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });
    
    // Parse response as JSON
    const data = await response.json();
    
    // If response is not ok, throw an error with the message from the API
    if (!response.ok) {
      throw new Error(data.message || `API error: ${response.status}`);
    }
    
    // Return the successful response data
    return data;
  } catch (error) {
    // Log the error for debugging
    console.error('API request failed:', error);
    
    // Re-throw the error to be handled by the caller
    throw error;
  }
}; 