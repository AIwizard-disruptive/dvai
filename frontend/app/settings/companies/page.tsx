'use client'

import { AdminRouteGuard } from '@/components/admin-route-guard'
import { AppLayout } from '@/components/app-layout'
import { Building2, ExternalLink, Users } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Company {
  domain: string
  name: string
  logo_url: string
  website: string
  employee_count: number
  employees: Array<{
    name: string
    email: string
  }>
}

export default function CompaniesAdminPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      // TODO: Replace with actual API call to backend
      // const response = await fetch('http://localhost:8000/api/companies')
      // const data = await response.json()
      // setCompanies(data)
      
      // Mock data for development
      const mockCompanies: Company[] = [
        {
          domain: 'stripe.com',
          name: 'Stripe',
          logo_url: 'https://logo.clearbit.com/stripe.com',
          website: 'https://stripe.com',
          employee_count: 3,
          employees: [
            { name: 'John Smith', email: 'john@stripe.com' },
            { name: 'Jane Doe', email: 'jane@stripe.com' },
            { name: 'Bob Johnson', email: 'bob@stripe.com' }
          ]
        },
        {
          domain: 'notion.so',
          name: 'Notion',
          logo_url: 'https://logo.clearbit.com/notion.so',
          website: 'https://notion.so',
          employee_count: 2,
          employees: [
            { name: 'Alice Cooper', email: 'alice@notion.so' },
            { name: 'Charlie Brown', email: 'charlie@notion.so' }
          ]
        }
      ]
      
      setCompanies(mockCompanies)
    } catch (error) {
      console.error('Error loading companies:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AdminRouteGuard requiredRole="admin">
      <AppLayout>
        <div className="space-y-8">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-6">
              <div className="w-10 h-10 flex items-center justify-center">
                <Building2 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">
                Companies (Admin)
              </h1>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
              Automatically extracted from email domains • Admin Access Only
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
              <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {companies.length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Companies Found</div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
              <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {companies.reduce((sum, c) => sum + c.employee_count, 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Total Contacts</div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
              <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {companies.filter(c => c.employee_count > 1).length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Multi-Contact</div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
              <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {companies.filter(c => c.employee_count === 1).length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Single Contact</div>
            </div>
          </div>

          {/* Companies Grid */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-gray-200 dark:border-gray-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
              <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">Loading companies...</p>
            </div>
          ) : companies.length === 0 ? (
            <div className="text-center py-12 border border-gray-200 dark:border-gray-800 rounded-lg">
              <Building2 className="h-12 w-12 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                No Companies Found
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Add people with business email addresses to see companies here.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {companies.map((company) => (
                <div
                  key={company.domain}
                  className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900 hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
                >
                  {/* Logo */}
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-12 h-12 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center overflow-hidden flex-shrink-0">
                      <img
                        src={company.logo_url}
                        alt={company.name}
                        className="w-full h-full object-contain p-2"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                          e.currentTarget.nextElementSibling!.classList.remove('hidden')
                        }}
                      />
                      <div className="hidden w-full h-full flex items-center justify-center text-lg font-bold text-gray-500 dark:text-gray-400">
                        {company.name[0]}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                        {company.name}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {company.domain}
                      </p>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                      <Users className="h-4 w-4" />
                      <span>{company.employee_count} contact{company.employee_count !== 1 ? 's' : ''}</span>
                    </div>
                  </div>

                  {/* Employees */}
                  <div className="space-y-1 mb-4">
                    {company.employees.slice(0, 3).map((emp, idx) => (
                      <div key={idx} className="text-xs text-gray-600 dark:text-gray-400 truncate">
                        • {emp.name}
                      </div>
                    ))}
                    {company.employee_count > 3 && (
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        +{company.employee_count - 3} more
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <a
                    href={company.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Visit Website
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              ))}
            </div>
          )}

          {/* Info Note */}
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
            <div className="flex gap-3">
              <Building2 className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-purple-900 dark:text-purple-100 mb-1">
                  Company Data Source
                </div>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  Companies are automatically extracted from email domains. Logos are fetched from Clearbit API.
                  Connect to backend API at <code className="px-1 py-0.5 bg-purple-100 dark:bg-purple-900/40 rounded">localhost:8000/api/companies</code>
                </p>
              </div>
            </div>
          </div>
        </div>
      </AppLayout>
    </AdminRouteGuard>
  )
}


