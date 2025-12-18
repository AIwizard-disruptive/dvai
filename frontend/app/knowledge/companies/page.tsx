'use client'

import { AppLayout } from '@/components/app-layout'
import { cn } from '@/lib/utils'
import { Building2, Calendar, Globe, Grid3x3, List, Search } from 'lucide-react'
import { useState } from 'react'

// Mock data - will be replaced with real API data
const mockDocuments = [
  {
    id: 1,
    title: 'TechFlow AI - Company Intelligence Report',
    description: 'Market analysis, competitive landscape, and growth trajectory assessment',
    date: '2025-12-15',
    category: 'Intelligence',
    tags: ['AI', 'SaaS', 'B2B'],
    website: 'techflow.ai',
  },
  {
    id: 2,
    title: 'GreenEnergy Solutions - Due Diligence Summary',
    description: 'Financial analysis, team evaluation, and market opportunity assessment',
    date: '2025-12-14',
    category: 'Due Diligence',
    tags: ['CleanTech', 'Energy', 'Series A'],
    website: 'greenenergy.com',
  },
  {
    id: 3,
    title: 'HealthTech Innovations - Market Research',
    description: 'Healthcare market trends, regulatory landscape, and competitive analysis',
    date: '2025-12-12',
    category: 'Research',
    tags: ['HealthTech', 'B2C', 'Digital Health'],
    website: 'healthtech.io',
  },
  {
    id: 4,
    title: 'FinanceCore - Competitive Analysis',
    description: 'Competitor mapping, market positioning, and differentiation strategy',
    date: '2025-12-10',
    category: 'Analysis',
    tags: ['FinTech', 'B2B', 'Enterprise'],
    website: 'financecore.com',
  },
  // Add more mock documents as needed
]

export default function KnowledgeCompaniesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'list' | 'card'>('list')

  const filteredDocuments = mockDocuments.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
    doc.website?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-6">
            <div className="w-10 h-10 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Company Documents</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            AI-generated company research, market analysis, and business intelligence
          </p>
        </div>

        {/* Search and View Toggle */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          {/* Search Bar */}
          <div className="relative flex-1 w-full sm:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search companies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400"
            />
          </div>

          {/* View Toggle */}
          <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-md transition-colors',
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              )}
              aria-label="List view"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('card')}
              className={cn(
                'p-2 rounded-md transition-colors',
                viewMode === 'card'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              )}
              aria-label="Card view"
            >
              <Grid3x3 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Results Count */}
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {filteredDocuments.length} {filteredDocuments.length === 1 ? 'document' : 'documents'} found
        </div>

        {/* Documents - List View */}
        {viewMode === 'list' && (
          <div className="space-y-2">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-all cursor-pointer group bg-white dark:bg-gray-900 hover:shadow-sm"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {doc.description}
                    </p>
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(doc.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </div>
                      {doc.website && (
                        <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                          <Globe className="h-3.5 w-3.5" />
                          {doc.website}
                        </div>
                      )}
                      <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded">
                        {doc.category}
                      </span>
                      {doc.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-0.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <Building2 className="h-5 w-5 text-gray-400 dark:text-gray-500 flex-shrink-0 group-hover:text-green-500 dark:group-hover:text-green-400 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Documents - Card View */}
        {viewMode === 'card' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="p-5 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-all cursor-pointer group bg-white dark:bg-gray-900 hover:shadow-md"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/20 group-hover:bg-green-100 dark:group-hover:bg-green-900/30 transition-colors">
                    <Building2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-2">
                      {doc.title}
                    </h3>
                  </div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {doc.description}
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                    <Calendar className="h-3.5 w-3.5" />
                    {new Date(doc.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </div>
                  {doc.website && (
                    <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 truncate">
                      <Globe className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="truncate">{doc.website}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded">
                      {doc.category}
                    </span>
                    {doc.tags.slice(0, 2).map((tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2 py-0.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {doc.tags.length > 2 && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        +{doc.tags.length - 2}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {filteredDocuments.length === 0 && (
          <div className="text-center py-12">
            <Building2 className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No documents found</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Try adjusting your search query or check back later for new company intelligence.
            </p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
