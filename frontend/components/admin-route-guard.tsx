'use client'

import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

interface AdminRouteGuardProps {
  children: React.ReactNode
  requiredRole?: 'admin' | 'owner'
}

export function AdminRouteGuard({ children, requiredRole = 'admin' }: AdminRouteGuardProps) {
  const { user, loading, checkPermission } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!user) {
        // Not logged in - redirect to home
        router.push('/')
      } else if (!checkPermission(requiredRole)) {
        // Logged in but not authorized - redirect to dashboard
        router.push('/dashboard')
      }
    }
  }, [user, loading, checkPermission, requiredRole, router])

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-950">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 dark:border-gray-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // Not authorized
  if (!user || !checkPermission(requiredRole)) {
    return null
  }

  // Authorized - show content
  return <>{children}</>
}


