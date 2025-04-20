import React, { useState, useEffect, useContext } from 'react'
import AuthContext from '../contexts/AuthContext'
import { API_BASE_URL, JWT_LOCAL_STORAGE_KEY } from '../config'

const Greeting = () => {
  const [greeting, setGreeting] = useState('')
  const [firstName, setFirstName] = useState('User')
  const { user, isAuthenticated } = useContext(AuthContext)

  // Fetch the real user's first name from the database
  useEffect(() => {
    const fetchUserData = async () => {
      if (!isAuthenticated) return

      try {
        // First try to use the name from context
        if (user?.firstName) {
          setFirstName(user.firstName)
        }

        // Then fetch from API to ensure most recent data
        const token = localStorage.getItem(JWT_LOCAL_STORAGE_KEY)
        if (!token) return

        const response = await fetch(`${API_BASE_URL}/api/user/profile?id=${user?.id || 1}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.firstName) {
            setFirstName(data.firstName)
          }
        }
      } catch (error) {
        console.error('Error fetching user data for greeting:', error)
        // Fall back to user from context if available
        if (user?.firstName) {
          setFirstName(user.firstName)
        }
      }
    }

    fetchUserData()
  }, [user, isAuthenticated])

  // Set the appropriate greeting based on the time of day
  useEffect(() => {
    const updateGreeting = () => {
      const hour = new Date().getHours()
      if (hour >= 5 && hour < 12) {
        setGreeting('Good Morning')
      } else if (hour >= 12 && hour < 18) {
        setGreeting('Good Afternoon')
      } else {
        setGreeting('Good Evening')
      }
    }

    updateGreeting()
    const interval = setInterval(updateGreeting, 60000)
    return () => clearInterval(interval)
  }, [])

  return (
    <h2 className="text-2xl font-semibold text-gray-800">
      {greeting}, {firstName}
    </h2>
  )
}

export default Greeting 