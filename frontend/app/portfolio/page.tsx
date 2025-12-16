import { AppLayout } from '@/components/app-layout'
import { AlertTriangle, Building2, ExternalLink, TrendingUp, Users } from 'lucide-react'

export default function PortfolioPage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
              <Building2 className="h-5 w-5 text-purple-600" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900">Portfolio Companies</h1>
          </div>
          <p className="text-sm text-gray-600 ml-13">
            Monitor performance, track metrics, and support portfolio growth
          </p>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Active Companies</div>
            <div className="text-2xl font-semibold text-gray-900">18</div>
            <div className="text-xs text-gray-500 mt-1">Across all stages</div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Total Invested</div>
            <div className="text-2xl font-semibold text-gray-900">$8.4M</div>
            <div className="text-xs text-gray-500 mt-1">Current AUM</div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Avg. Growth</div>
            <div className="text-2xl font-semibold text-green-600 flex items-center gap-1">
              +42%
              <TrendingUp className="h-4 w-4" />
            </div>
            <div className="text-xs text-gray-500 mt-1">YoY revenue</div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Follow-on Ready</div>
            <div className="text-2xl font-semibold text-gray-900">5</div>
            <div className="text-xs text-gray-500 mt-1">Next 6 months</div>
          </div>
        </div>

        {/* Companies by Stage */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Companies by Stage</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { stage: 'Early Stage', count: 7, trend: 'growing' },
              { stage: 'Growth Stage', count: 8, trend: 'stable' },
              { stage: 'Late Stage', count: 3, trend: 'growing' },
            ].map((category) => (
              <div
                key={category.stage}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="text-sm font-medium text-gray-900">{category.stage}</div>
                <div className="text-2xl font-semibold text-gray-900 mt-1">{category.count}</div>
                <div className="text-xs text-gray-500 mt-1 capitalize">{category.trend}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Companies Requiring Attention */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Companies Requiring Attention</h2>
          <div className="space-y-2">
            {[
              {
                name: 'DataSync Pro',
                status: 'At Risk',
                issue: 'Burn rate increasing, 4 months runway',
                metric: 'Revenue: $120K MRR',
                statusColor: 'red',
              },
              {
                name: 'CloudBase Systems',
                status: 'Watch',
                issue: 'Key hire delayed by 2 months',
                metric: 'Revenue: $340K MRR',
                statusColor: 'yellow',
              },
              {
                name: 'AI Analytics Co',
                status: 'Follow-up',
                issue: 'Series A discussions ongoing',
                metric: 'Revenue: $580K MRR',
                statusColor: 'blue',
              },
            ].map((company, i) => (
              <div
                key={i}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="font-medium text-sm text-gray-900">{company.name}</div>
                      {company.statusColor === 'red' && (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          company.statusColor === 'red'
                            ? 'bg-red-100 text-red-700'
                            : company.statusColor === 'yellow'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {company.status}
                      </span>
                      <span className="text-xs text-gray-500">{company.metric}</span>
                    </div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                </div>
                <div className="text-sm text-gray-600 mt-2">{company.issue}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performers */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Top Performers This Quarter</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              {
                name: 'TechStack Solutions',
                growth: '+85%',
                metric: 'Revenue growth',
                team: '12 employees',
              },
              {
                name: 'MarketPlace Inc',
                growth: '+120%',
                metric: 'User acquisition',
                team: '8 employees',
              },
              {
                name: 'FinTech Innovations',
                growth: '+65%',
                metric: 'Transaction volume',
                team: '15 employees',
              },
              {
                name: 'DevTools Corp',
                growth: '+92%',
                metric: 'ARR growth',
                team: '10 employees',
              },
            ].map((company) => (
              <div
                key={company.name}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-sm text-gray-900">{company.name}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm font-semibold text-green-600">{company.growth}</span>
                      <span className="text-xs text-gray-500">{company.metric}</span>
                    </div>
                    <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
                      <Users className="h-3 w-3" />
                      {company.team}
                    </div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Note */}
        <div className="mt-8 p-4 bg-purple-50 border border-purple-100 rounded-lg">
          <div className="flex gap-3">
            <ExternalLink className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-purple-900 mb-1">
                Portfolio Data from Multiple Sources
              </div>
              <p className="text-sm text-purple-700">
                Detailed metrics and reports are managed in Linear and Google Sheets. 
                This view aggregates key insights and flags items requiring partner attention.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}


