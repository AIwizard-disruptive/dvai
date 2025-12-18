'use client'

import { AppLayout } from '@/components/app-layout'
import { BookOpen, Building2, FileText, Users } from 'lucide-react'
import Link from 'next/link'

export default function KnowledgeBankPage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-6">
            <div className="w-10 h-10 flex items-center justify-center">
              <BookOpen className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Knowledge Bank</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            AI-generated intelligence documents and insights
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Documents</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">100+</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Generated insights</div>
          </div>
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">People Profiles</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">45+</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Contact intelligence</div>
          </div>
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">Company Reports</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">30+</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Business intelligence</div>
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/knowledge/activities"
            className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/10 transition-all group bg-white dark:bg-gray-900"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30 transition-colors">
                <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Activities</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Generated activity insights, meeting summaries, and event analysis
                </p>
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Browse all activity documents →
                </div>
              </div>
            </div>
          </Link>

          <Link
            href="/knowledge/people"
            className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/10 transition-all group bg-white dark:bg-gray-900"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30 transition-colors">
                <Users className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">People</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  AI-generated people profiles, relationship maps, and contact intelligence
                </p>
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Browse all people documents →
                </div>
              </div>
            </div>
          </Link>

          <Link
            href="/knowledge/companies"
            className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/10 transition-all group bg-white dark:bg-gray-900"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 group-hover:bg-green-100 dark:group-hover:bg-green-900/30 transition-colors">
                <Building2 className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Companies</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Company research, market analysis, and business intelligence reports
                </p>
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Browse all company documents →
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Information Note */}
        <div className="mt-8 p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800 rounded-lg">
          <div className="flex gap-3">
            <BookOpen className="h-5 w-5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-indigo-900 dark:text-indigo-100 mb-1">
                AI-Generated Intelligence
              </div>
              <p className="text-sm text-indigo-700 dark:text-indigo-300">
                All documents in the Knowledge Bank are automatically generated and updated by our AI system, 
                providing you with up-to-date insights and analysis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
