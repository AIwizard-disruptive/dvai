import { AppLayout } from '@/components/app-layout'
import { AlertCircle, Clock, DollarSign, ExternalLink, Target, TrendingUp } from 'lucide-react'

export default function DealflowPage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-6">
            <div className="w-10 h-10 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Dealflow</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            Track investment opportunities from sourcing through diligence
          </p>
        </div>

        {/* Pipeline Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { stage: 'Sourcing', count: 24, color: 'blue' },
            { stage: 'Review', count: 12, color: 'yellow' },
            { stage: 'Due Diligence', count: 5, color: 'orange' },
            { stage: 'Decision', count: 3, color: 'green' },
          ].map((stage) => (
            <div
              key={stage.stage}
              className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">{stage.stage}</div>
              <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{stage.count}</div>
            </div>
          ))}
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">Target Investment</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">$2.4M</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Active pipeline</div>
          </div>
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">Conversion Rate</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">8.2%</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Last 12 months</div>
          </div>
          <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <div className="text-sm text-gray-600 dark:text-gray-400">Avg. Cycle Time</div>
            </div>
            <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">42 days</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Source to decision</div>
          </div>
        </div>

        {/* Active Deals */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">Active Deals Requiring Attention</h2>
          <div className="space-y-2">
            {[
              {
                company: 'TechFlow AI',
                stage: 'Due Diligence',
                amount: '$500K',
                status: 'On track',
                nextAction: 'Founder call scheduled for Thursday',
                priority: 'high',
              },
              {
                company: 'GreenEnergy Solutions',
                stage: 'Review',
                amount: '$300K',
                status: 'Waiting',
                nextAction: 'Awaiting financial documents',
                priority: 'medium',
              },
              {
                company: 'HealthTech Innovations',
                stage: 'Decision',
                amount: '$750K',
                status: 'Critical',
                nextAction: 'Partner meeting tomorrow',
                priority: 'high',
              },
            ].map((deal, i) => (
              <div
                key={i}
                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors cursor-pointer group bg-white dark:bg-gray-900"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="font-medium text-sm text-gray-900 dark:text-gray-100">{deal.company}</div>
                      {deal.priority === 'high' && (
                        <AlertCircle className="h-4 w-4 text-red-500 dark:text-red-400" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded">
                        {deal.stage}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{deal.amount}</span>
                    </div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">{deal.nextAction}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Sources */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">Recent Deal Sources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { source: 'Inbound Referral', count: 8 },
              { source: 'Partner Network', count: 5 },
              { source: 'Events & Conferences', count: 4 },
              { source: 'Cold Outreach', count: 3 },
            ].map((source) => (
              <div
                key={source.source}
                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors bg-white dark:bg-gray-900"
              >
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{source.source}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{source.count} deals this quarter</div>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Note */}
        <div className="mt-8 p-4 bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 rounded-lg">
          <div className="flex gap-3">
            <ExternalLink className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-green-900 dark:text-green-100 mb-1">
                Sync with Linear for Deal Tracking
              </div>
              <p className="text-sm text-green-700 dark:text-green-300">
                Daily operations and deal tracking happen in Linear. 
                This dashboard provides strategic oversight and key metrics.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
