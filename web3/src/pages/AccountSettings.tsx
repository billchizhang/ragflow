import React, { useState, useContext, useEffect } from 'react'
import AuthContext from '../contexts/AuthContext'
import { API_BASE_URL, JWT_LOCAL_STORAGE_KEY } from '../config'

const AccountSettings = () => {
  // State for form inputs
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingProfile, setLoadingProfile] = useState(true)
  const [profileData, setProfileData] = useState<{
    firstName: string;
    lastName: string;
    email: string;
    id: number;
    tierName?: string;
    isExpired?: boolean;
  } | null>(null)
  
  // Get user data from auth context
  const { user, isAuthenticated } = useContext(AuthContext)
  
  // Fetch profile data directly from database
  useEffect(() => {
    const fetchProfileData = async () => {
      if (!isAuthenticated) return
      
      try {
        setLoadingProfile(true)
        
        // Fetch user profile data from Users table
        const token = localStorage.getItem(JWT_LOCAL_STORAGE_KEY)
        
        // If we don't have a token, use the data from context
        if (!token) {
          setProfileData(user)
          setLoadingProfile(false)
          return
        }
        
        // Real API call to fetch latest data from the database
        try {
          const response = await fetch(`${API_BASE_URL}/api/user/profile?id=${user?.id || 1}`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (!response.ok) {
            throw new Error('Failed to fetch profile data')
          }
          
          const data = await response.json()
          console.log('Profile data fetched from database:', data)
          
          // Update profile data with response data directly
          setProfileData(data)
          
        } catch (apiError) {
          console.error('API error:', apiError)
          // Fall back to context data if API call fails
          setProfileData(user)
        }
        
        setLoadingProfile(false)
        
      } catch (err: any) {
        console.error('Error fetching profile:', err.message)
        // If fetch fails, fall back to context data
        setProfileData(user)
        setLoadingProfile(false)
      }
    }
    
    fetchProfileData()
  }, [user, isAuthenticated])
  
  // Display name combining first and last name
  const displayName = loadingProfile
    ? 'Loading...'
    : profileData
      ? `${profileData.firstName} ${profileData.lastName}`
      : 'Not available'
  
  // Handle password update
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Reset messages
    setError('')
    setSuccessMessage('')
    
    // Validate passwords
    if (!currentPassword) {
      setError('Please enter your current password')
      return
    }
    
    if (!newPassword) {
      setError('Please enter a new password')
      return
    }
    
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match')
      return
    }
    
    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters')
      return
    }
    
    // Update password logic would go here
    setLoading(true)
    
    try {
      // Example API call (commented out until backend endpoint is ready)
      /*
      const response = await fetch('http://localhost:5001/api/user/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          currentPassword, 
          newPassword 
        })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to update password')
      }
      */
      
      // Mock successful response for now
      setTimeout(() => {
        setSuccessMessage('Password updated successfully')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        setLoading(false)
      }, 1000)
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while updating your password')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Account Settings</h1>
      
      {/* Profile Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Profile</h2>
        
        {loadingProfile ? (
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <input
                type="text"
                value={profileData?.firstName || 'Not available'}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                type="text"
                value={profileData?.lastName || 'Not available'}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={profileData?.email || 'Not available'}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">User ID</label>
              <input
                type="text"
                value={profileData?.id || 'Not available'}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
          </div>
        )}
      </div>

      {/* Password Change Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Change Password</h2>
        
        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 text-red-700">
            {error}
          </div>
        )}
        
        {successMessage && (
          <div className="mb-4 bg-green-50 border-l-4 border-green-500 p-4 text-green-700">
            {successMessage}
          </div>
        )}
        
        <form onSubmit={handlePasswordUpdate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Current Password</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <button 
            type="submit"
            disabled={loading}
            className={`w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 ${
              loading ? 'opacity-75 cursor-not-allowed' : ''
            }`}
          >
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>

      {/* Subscription Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Subscription</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium text-gray-900">Current Plan: {profileData?.tierName || 'Premium'}</p>
              <p className="text-sm text-gray-500">
                {profileData?.isExpired ? 'Subscription expired' : 'Subscription active'}
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Manage Subscription
            </button>
          </div>
        </div>
      </div>

      {/* Account Cancellation */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-red-600 mb-4">Cancel Account</h2>
        <p className="text-gray-600 mb-4">
          Once you cancel your account, all of your data will be permanently deleted.
          This action cannot be undone.
        </p>
        <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">
          Cancel Account
        </button>
      </div>
    </div>
  )
}

export default AccountSettings 