import { AppLayout } from '@/components/app-layout'
import {
    Activity,
    AlertCircle,
    Bell,
    Database,
    ExternalLink,
    FileText,
    Link as LinkIcon,
    Settings,
    Shield,
    Users
} from 'lucide-react'

export default function AdminPage() {
  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
              <Settings className="h-5 w-5 text-gray-700" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900">Admin</h1>
          </div>
          <p className="text-sm text-gray-600 ml-13">
            System configuration, integrations, and administrative controls
          </p>
        </div>

        {/* Warning Banner */}
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-amber-900 mb-1">
                Restricted Access Area
              </div>
              <p className="text-sm text-amber-700">
                This is the brain of the system. Most users should work primarily in Google and Linear. 
                Only partners and system administrators should access these settings regularly.
              </p>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <Database className="h-5 w-5 text-gray-600" />
                <div className="font-medium text-sm text-gray-900">Database</div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Status</span>
                  <span className="text-green-600 font-medium">Healthy</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Tables</span>
                  <span className="text-gray-900">24 active</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Storage</span>
                  <span className="text-gray-900">2.4 GB</span>
                </div>
              </div>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <Activity className="h-5 w-5 text-gray-600" />
                <div className="font-medium text-sm text-gray-900">API Usage</div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Requests Today</span>
                  <span className="text-gray-900">1,247</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Avg Response</span>
                  <span className="text-gray-900">142ms</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Error Rate</span>
                  <span className="text-green-600 font-medium">0.2%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Integrations */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Integrations</h2>
          <div className="space-y-2">
            {[
              {
                name: 'Google Workspace',
                status: 'Connected',
                services: ['Gmail', 'Calendar', 'Contacts', 'Drive'],
                lastSync: '5 minutes ago',
              },
              {
                name: 'Linear',
                status: 'Connected',
                services: ['Issues', 'Projects', 'Teams'],
                lastSync: '12 minutes ago',
              },
              {
                name: 'Whisperflow (Transcription)',
                status: 'Connected',
                services: ['Audio Processing', 'AI Extraction'],
                lastSync: '1 hour ago',
              },
            ].map((integration, i) => (
              <div
                key={i}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <LinkIcon className="h-4 w-4 text-gray-400" />
                      <div className="font-medium text-sm text-gray-900">{integration.name}</div>
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">
                        {integration.status}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {integration.services.map((service) => (
                        <span
                          key={service}
                          className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                    <div className="text-xs text-gray-500">Last sync: {integration.lastSync}</div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Configuration Sections */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              {
                icon: Users,
                title: 'User Management',
                description: 'Manage team members and permissions',
                color: 'blue',
              },
              {
                icon: Shield,
                title: 'Security & Access',
                description: 'Configure authentication and roles',
                color: 'red',
              },
              {
                icon: Bell,
                title: 'Notifications',
                description: 'Set up alerts and notification rules',
                color: 'yellow',
              },
              {
                icon: FileText,
                title: 'Templates',
                description: 'Manage meeting and email templates',
                color: 'purple',
              },
              {
                icon: Database,
                title: 'Data Management',
                description: 'Backup, export, and data controls',
                color: 'green',
              },
              {
                icon: Activity,
                title: 'System Logs',
                description: 'View activity and audit logs',
                color: 'gray',
              },
            ].map((section) => (
              <button
                key={section.title}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-all text-left group"
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-${section.color}-50 flex items-center justify-center flex-shrink-0`}>
                    <section.icon className={`h-4 w-4 text-${section.color}-600`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-gray-900 mb-1">{section.title}</div>
                    <div className="text-xs text-gray-500">{section.description}</div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600 flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Four Wheels System Info */}
        <div className="space-y-4">
          <h2 className="text-sm font-medium text-gray-700">System Architecture</h2>
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Users className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-gray-900 mb-1">People Wheel</div>
                  <div className="text-xs text-gray-600">
                    Relationship management, contact tracking, meeting intelligence
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Database className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-gray-900 mb-1">Dealflow Wheel</div>
                  <div className="text-xs text-gray-600">
                    Investment pipeline, due diligence, deal tracking
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Building2 className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-gray-900 mb-1">Portfolio Wheel</div>
                  <div className="text-xs text-gray-600">
                    Company monitoring, metrics tracking, portfolio support
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Settings className="h-5 w-5 text-gray-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-gray-900 mb-1">Admin Wheel</div>
                  <div className="text-xs text-gray-600">
                    System configuration, integrations, user management
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Best Practices */}
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="flex gap-3">
            <Shield className="h-5 w-5 text-gray-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-gray-900 mb-2">
                Best Practices for System Usage
              </div>
              <ul className="text-sm text-gray-700 space-y-1.5">
                <li className="flex gap-2">
                  <span className="text-gray-400">•</span>
                  <span>Daily work should happen in Google Workspace and Linear</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-gray-400">•</span>
                  <span>Use this system for strategic oversight and intelligence</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-gray-400">•</span>
                  <span>Partners access for decisions and high-level monitoring</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-gray-400">•</span>
                  <span>System admins for configuration and integration management</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}


