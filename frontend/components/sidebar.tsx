'use client'

import { useAuth } from '@/contexts/auth-context'
import { cn } from '@/lib/utils'
import {
    Building2,
    CheckSquare,
    ChevronDown,
    ChevronLeft,
    FileText,
    Menu,
    Moon,
    Settings,
    Shield,
    Sun,
    TrendingUp,
    Upload,
    Users,
    X
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { DVLogo } from './dv-logo'
import { useTheme } from './theme-provider'

interface NavigationItem {
  name: string
  href: string
  icon: any
  description: string
  subItems?: Array<{
    name: string
    href: string
    description: string
  }>
}

const navigation: NavigationItem[] = [
  {
    name: 'People',
    href: '/people',
    icon: Users,
    description: 'Manage relationships and contacts',
    subItems: [
      { name: 'All Contacts', href: '/people/contacts', description: 'View all people' },
      { name: 'Organizations', href: '/people/orgs', description: 'Company relationships' },
    ]
  },
  {
    name: 'Dealflow',
    href: '/dealflow',
    icon: TrendingUp,
    description: 'Track investment opportunities',
    subItems: [
      { name: 'Active Deals', href: '/dealflow/active', description: 'Current pipeline' },
      { name: 'Archive', href: '/dealflow/archive', description: 'Past opportunities' },
    ]
  },
  {
    name: 'Portfolio Companies',
    href: '/portfolio',
    icon: Building2,
    description: 'Monitor portfolio performance',
    subItems: [
      { name: 'Dashboard', href: '/portfolio/dashboard', description: 'Overview & metrics' },
      { name: 'Companies', href: '/portfolio/companies', description: 'All portfolio companies' },
    ]
  },
  {
    name: 'Knowledge Bank',
    href: '/knowledge',
    icon: FileText,
    description: 'AI-generated intelligence documents',
    subItems: [
      { name: 'Activities', href: '/knowledge/activities', description: 'Generated activity insights & reports' },
      { name: 'People', href: '/knowledge/people', description: 'Generated people profiles & analysis' },
      { name: 'Companies', href: '/knowledge/companies', description: 'Generated company intelligence & research' },
    ]
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: CheckSquare,
    description: 'Kanban board and task management',
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: FileText,
    description: 'Meeting notes and files',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'Account and API configuration',
  },
]

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const [expandedItems, setExpandedItems] = useState<string[]>([])
  const [showAllSubmenus, setShowAllSubmenus] = useState(false)
  const pathname = usePathname()
  const { theme, toggleTheme } = useTheme()
  const { user, isAdmin, logout } = useAuth()

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => {
      const newExpanded = prev.includes(itemName)
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
      
      // Check if all items with submenus are now expanded
      const itemsWithSubmenus = navigation
        .filter(item => item.subItems && item.subItems.length > 0)
        .map(item => item.name)
      
      const allExpanded = itemsWithSubmenus.every(name => newExpanded.includes(name))
      setShowAllSubmenus(allExpanded)
      
      return newExpanded
    })
  }

  const toggleAllSubmenus = () => {
    if (showAllSubmenus) {
      // Collapse all
      setExpandedItems([])
      setShowAllSubmenus(false)
    } else {
      // Expand all items that have submenus
      const itemsWithSubmenus = navigation
        .filter(item => item.subItems && item.subItems.length > 0)
        .map(item => item.name)
      setExpandedItems(itemsWithSubmenus)
      setShowAllSubmenus(true)
    }
  }

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors md:hidden"
        aria-label="Toggle menu"
      >
        {isOpen ? (
          <X className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        ) : (
          <Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        )}
      </button>

      {/* Desktop Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="hidden md:block fixed top-4 left-4 z-50 p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        aria-label="Toggle sidebar"
      >
        {isOpen ? (
          <ChevronLeft className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        ) : (
          <Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        )}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/60 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-40 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-transform duration-300 ease-in-out',
          'w-[280px]',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-100 dark:border-gray-800">
            <div className="flex flex-col gap-2">
              <DVLogo variant="symbol" size="md" />
              <p className="text-xs text-gray-500 dark:text-gray-400">Command Center</p>
            </div>
          </div>

          {/* Dark Mode Toggle */}
          <div className="p-4 border-b border-gray-100 dark:border-gray-800 space-y-2">
            <button
              onClick={toggleTheme}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Light Mode</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Dark Mode</span>
                </>
              )}
            </button>

            {/* Submenu Toggle */}
            <button
              onClick={toggleAllSubmenus}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle all submenus"
            >
              <ChevronDown 
                className={cn(
                  "h-4 w-4 text-gray-600 dark:text-gray-300 transition-transform",
                  showAllSubmenus && "rotate-180"
                )}
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {showAllSubmenus ? 'Collapse All' : 'Expand All'}
              </span>
            </button>
          </div>

          {/* Upload Files Button */}
          <div className="p-4 border-b border-gray-100 dark:border-gray-800">
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 transition-colors">
              <Upload className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm font-medium text-indigo-700 dark:text-indigo-300">Upload Files</span>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname?.startsWith(item.href)
              const isExpanded = expandedItems.includes(item.name)
              const hasSubItems = item.subItems && item.subItems.length > 0

              return (
                <div key={item.name}>
                  <div className="flex items-center gap-1">
                    <Link
                      href={item.href}
                      onClick={() => !hasSubItems && setIsOpen(false)}
                      className={cn(
                        'flex-1 flex items-start gap-3 px-3 py-3 rounded-lg transition-colors group',
                        isActive
                          ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                      )}
                    >
                      <item.icon
                        className={cn(
                          'h-5 w-5 flex-shrink-0 mt-0.5',
                          isActive 
                            ? 'text-gray-900 dark:text-gray-100' 
                            : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300'
                        )}
                      />
                      <div className="flex-1 min-w-0">
                        <div className={cn(
                          'text-sm font-medium',
                          isActive ? 'text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300'
                        )}>
                          {item.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {item.description}
                        </div>
                      </div>
                    </Link>
                    {hasSubItems && (
                      <button
                        onClick={() => toggleExpanded(item.name)}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        <ChevronDown
                          className={cn(
                            'h-4 w-4 text-gray-400 dark:text-gray-500 transition-transform',
                            isExpanded && 'rotate-180'
                          )}
                        />
                      </button>
                    )}
                  </div>

                  {/* Sub Items */}
                  {hasSubItems && isExpanded && (
                    <div className="ml-8 mt-1 space-y-1">
                      {item.subItems!.map((subItem) => {
                        const isSubActive = pathname === subItem.href
                        return (
                          <Link
                            key={subItem.href}
                            href={subItem.href}
                            onClick={() => setIsOpen(false)}
                            className={cn(
                              'block px-3 py-2 rounded-lg transition-colors text-sm',
                              isSubActive
                                ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium'
                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                            )}
                          >
                            <div className="font-medium">{subItem.name}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                              {subItem.description}
                            </div>
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}
          </nav>

          {/* Admin Menu (Only for Admin/Owner) */}
          {isAdmin && (
            <div className="px-4 pb-3">
              <div className="px-3 py-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                  <span className="text-xs font-semibold text-amber-900 dark:text-amber-100 uppercase tracking-wider">
                    Admin Access
                  </span>
                </div>
                <div className="space-y-1">
                  <Link
                    href="/settings/companies"
                    className="block text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 py-1"
                  >
                    → Companies Admin
                  </Link>
                  <Link
                    href="/settings/system"
                    className="block text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 py-1"
                  >
                    → System Admin
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* Footer - User Info */}
          <div className="p-4 border-t border-gray-100 dark:border-gray-800">
            <div className="px-3 py-2">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <span className="text-xs font-semibold text-white">
                    {user?.name?.split(' ').map(n => n[0]).join('') || 'ML'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {user?.name || 'Marcus Löwegren'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email || 'marcus.lowegren@disruptiveventures.se'}
                  </div>
                  {isAdmin && (
                    <div className="text-xs text-amber-600 dark:text-amber-400 font-medium mt-0.5">
                      {user?.role?.toUpperCase()}
                    </div>
                  )}
                </div>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">System Status</p>
                <p>Most team members use:</p>
                <ul className="mt-1 space-y-0.5 list-disc list-inside">
                  <li>Google Workspace</li>
                  <li>Linear</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}


