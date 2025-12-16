'use client'

import { cn } from '@/lib/utils'
import {
    Brain,
    Building2,
    ChevronLeft,
    Menu,
    Settings,
    TrendingUp,
    Users,
    X
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

const navigation = [
  {
    name: 'People',
    href: '/people',
    icon: Users,
    description: 'Manage relationships and contacts'
  },
  {
    name: 'Dealflow',
    href: '/dealflow',
    icon: TrendingUp,
    description: 'Track investment opportunities'
  },
  {
    name: 'Portfolio Companies',
    href: '/portfolio',
    icon: Building2,
    description: 'Monitor portfolio performance'
  },
  {
    name: 'Admin',
    href: '/admin',
    icon: Settings,
    description: 'System configuration'
  },
]

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 p-2 rounded-lg bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors md:hidden"
        aria-label="Toggle menu"
      >
        {isOpen ? (
          <X className="h-5 w-5 text-gray-600" />
        ) : (
          <Menu className="h-5 w-5 text-gray-600" />
        )}
      </button>

      {/* Desktop Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="hidden md:block fixed top-4 left-4 z-50 p-2 rounded-lg bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors"
        aria-label="Toggle sidebar"
      >
        {isOpen ? (
          <ChevronLeft className="h-5 w-5 text-gray-600" />
        ) : (
          <Menu className="h-5 w-5 text-gray-600" />
        )}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-40 h-screen bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out',
          'w-[280px]',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">Disruptive Ventures</h2>
                <p className="text-xs text-gray-500">Command Center</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname?.startsWith(item.href)
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'flex items-start gap-3 px-3 py-3 rounded-lg transition-colors group',
                    isActive
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5 flex-shrink-0 mt-0.5',
                      isActive ? 'text-gray-900' : 'text-gray-400 group-hover:text-gray-600'
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    <div className={cn(
                      'text-sm font-medium',
                      isActive ? 'text-gray-900' : 'text-gray-700'
                    )}>
                      {item.name}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-100">
            <div className="px-3 py-2 text-xs text-gray-500">
              <p className="font-medium text-gray-700 mb-1">Limited Access System</p>
              <p>Most work should happen in Google and Linear</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
