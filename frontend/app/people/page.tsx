import { AppLayout } from '@/components/app-layout'
import { ExternalLink, Users } from 'lucide-react'

export default function PeoplePage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900">People</h1>
          </div>
          <p className="text-sm text-gray-600 ml-13">
            Manage relationships, track interactions, and maintain your network
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Total Contacts</div>
            <div className="text-2xl font-semibold text-gray-900">247</div>
            <div className="text-xs text-gray-500 mt-1">Across all categories</div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Recent Meetings</div>
            <div className="text-2xl font-semibold text-gray-900">12</div>
            <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
            <div className="text-sm text-gray-600 mb-1">Follow-ups Due</div>
            <div className="text-2xl font-semibold text-gray-900">8</div>
            <div className="text-xs text-gray-500 mt-1">This week</div>
          </div>
        </div>

        {/* Categories */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { name: 'Founders', count: 89, color: 'blue' },
              { name: 'Investors', count: 45, color: 'green' },
              { name: 'Advisors', count: 32, color: 'purple' },
              { name: 'Service Providers', count: 28, color: 'orange' },
              { name: 'Portfolio Executives', count: 53, color: 'pink' },
            ].map((category) => (
              <button
                key={category.name}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-all text-left group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{category.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{category.count} contacts</div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Recent Activity</h2>
          <div className="space-y-2">
            {[
              {
                name: 'Sarah Chen',
                action: 'Meeting scheduled',
                time: '2 hours ago',
                type: 'Founder',
              },
              {
                name: 'Michael Rodriguez',
                action: 'Email sent',
                time: '5 hours ago',
                type: 'Investor',
              },
              {
                name: 'Emily Thompson',
                action: 'Note added',
                time: 'Yesterday',
                type: 'Advisor',
              },
            ].map((activity, i) => (
              <div
                key={i}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="font-medium text-sm text-gray-900">{activity.name}</div>
                      <span className="text-xs text-gray-500">·</span>
                      <div className="text-xs text-gray-500">{activity.type}</div>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{activity.action}</div>
                  </div>
                  <div className="text-xs text-gray-500">{activity.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Note */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-lg">
          <div className="flex gap-3">
            <ExternalLink className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-blue-900 mb-1">
                Sync with Google Contacts
              </div>
              <p className="text-sm text-blue-700">
                Most relationship management happens in Google Contacts and Gmail. 
                This view provides a strategic overview and meeting intelligence.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}


