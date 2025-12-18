'use client'

import { createContext, useContext, useEffect, useState } from 'react'

export type UserRole = 'owner' | 'admin' | 'editor' | 'viewer'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  avatar?: string
  organization?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  isAdmin: boolean
  isOwner: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkPermission: (requiredRole: UserRole) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initialize auth state
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      // TODO: Replace with actual auth API call
      // For now, mock user based on localStorage or default to admin
      const storedUser = localStorage.getItem('dv-user')
      
      if (storedUser) {
        setUser(JSON.parse(storedUser))
      } else {
        // Default mock user for development
        const mockUser: User = {
          id: '1',
          name: 'Marcus Löwegren',
          email: 'marcus.lowegren@disruptiveventures.se',
          role: 'owner',
          organization: 'Disruptive Ventures'
        }
        setUser(mockUser)
        localStorage.setItem('dv-user', JSON.stringify(mockUser))
      }
    } catch (error) {
      console.error('Error loading user:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      // TODO: Implement actual login API call
      // const response = await fetch('/api/auth/login', {
      //   method: 'POST',
      //   body: JSON.stringify({ email, password })
      // })
      // const userData = await response.json()
      
      // Mock login for development
      const mockUser: User = {
        id: '1',
        name: 'Marcus Löwegren',
        email: email,
        role: email.includes('admin') ? 'admin' : 'owner',
        organization: 'Disruptive Ventures'
      }
      
      setUser(mockUser)
      localStorage.setItem('dv-user', JSON.stringify(mockUser))
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      // TODO: Implement actual logout API call
      // await fetch('/api/auth/logout', { method: 'POST' })
      
      setUser(null)
      localStorage.removeItem('dv-user')
      localStorage.removeItem('dv-theme')
      window.location.href = '/'
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    }
  }

  const checkPermission = (requiredRole: UserRole): boolean => {
    if (!user) return false
    
    const roleHierarchy: Record<UserRole, number> = {
      viewer: 1,
      editor: 2,
      admin: 3,
      owner: 4
    }
    
    return roleHierarchy[user.role] >= roleHierarchy[requiredRole]
  }

  const isAdmin = user?.role === 'admin' || user?.role === 'owner'
  const isOwner = user?.role === 'owner'

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAdmin,
        isOwner,
        login,
        logout,
        checkPermission
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}


