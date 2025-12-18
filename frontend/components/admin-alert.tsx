'use client'

import { cn } from '@/lib/utils'
import { AlertCircle, X } from 'lucide-react'
import { useEffect, useState } from 'react'

export function AdminAlert() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Check if user just logged in (you can adjust this logic)
    const hasSeenAlert = sessionStorage.getItem('admin-alert-seen')
    
    if (!hasSeenAlert) {
      // Show alert after a short delay
      setTimeout(() => setIsVisible(true), 500)
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        setIsVisible(false)
        sessionStorage.setItem('admin-alert-seen', 'true')
      }, 3500)
    }
  }, [])

  if (!isVisible) return null

  return (
    <div
      className={cn(
        'fixed top-4 left-1/2 -translate-x-1/2 z-[100] w-full max-w-md px-4',
        'animate-in fade-in slide-in-from-top-2 duration-300'
      )}
    >
      <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg shadow-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-1">
              Admin Only
            </h3>
            <p className="text-sm text-amber-700 dark:text-amber-300">
              Partners & administrators only. Team uses Google & Linear.
            </p>
          </div>
          <button
            onClick={() => {
              setIsVisible(false)
              sessionStorage.setItem('admin-alert-seen', 'true')
            }}
            className="p-1 hover:bg-amber-100 dark:hover:bg-amber-900/40 rounded transition-colors"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4 text-amber-600 dark:text-amber-400" />
          </button>
        </div>
      </div>
    </div>
  )
}


