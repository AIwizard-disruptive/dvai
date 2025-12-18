import { AppLayout } from '@/components/app-layout'
import { Building2 } from 'lucide-react'

export default function PortfolioPage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-6">
            <div className="w-10 h-10 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Portfolio Dashboard</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            VC KPIs and portfolio performance metrics
          </p>
        </div>

        {/* Portfolio Overview */}
        <div>
          <h2 className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mb-4">PORTFOLIO OVERVIEW</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">18</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Active Companies</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">$8.4M</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Invested</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">$24.2M</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Current Valuation</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">2.9x</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Portfolio Multiple</div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div>
          <h2 className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mb-4">PERFORMANCE METRICS</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">42%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Avg Revenue Growth</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">85%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Survival Rate</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">12</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Exits (All Time)</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">3.2x</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Avg Exit Multiple</div>
            </div>
          </div>
        </div>

        {/* Fund Metrics */}
        <div>
          <h2 className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mb-4">FUND METRICS</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">$45M</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Fund Size</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">72%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Deployed Capital</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">$12.8M</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Dry Powder</div>
            </div>
            <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">24</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Investments</div>
            </div>
          </div>
        </div>

        {/* Note */}
        <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-gray-100">Note:</span> These are template KPIs for layout purposes. Connect to your data sources to display real portfolio metrics. Detailed analytics and reporting happen in Linear and Google Sheets.
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
