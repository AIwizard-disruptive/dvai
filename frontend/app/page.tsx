import { ArrowRight, Building2, Settings, TrendingUp, Users } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <img 
              src="/dv-wordmark.png" 
              alt="Disruptive Ventures" 
              className="h-8 w-auto object-contain"
              data-theme="preserve"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl w-full space-y-12 py-16">
          {/* Hero Section */}
          <div className="text-center space-y-6">
            <div className="flex justify-center mb-4">
              <img 
                src="/dv-wordmark.png" 
                alt="Disruptive Ventures" 
                className="h-16 w-auto object-contain"
                data-theme="preserve"
              />
            </div>
            <h1 className="text-4xl font-semibold text-gray-900 dark:text-gray-100 tracking-tight">
              Command Center
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Strategic intelligence system powering venture operations. 
              Most work happens in Google and Linear—this is your oversight layer.
            </p>
          </div>

          {/* Four Wheels Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              href="/people"
              className="group p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-sm dark:hover:bg-gray-900/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30 transition-colors">
                  <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">People</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Relationships, contacts, and meeting intelligence
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/dealflow"
              className="group p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-sm dark:hover:bg-gray-900/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center flex-shrink-0 group-hover:bg-green-100 dark:group-hover:bg-green-900/30 transition-colors">
                  <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">Dealflow</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Investment pipeline and opportunity tracking
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/portfolio"
              className="group p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-sm dark:hover:bg-gray-900/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center flex-shrink-0 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30 transition-colors">
                  <Building2 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">Portfolio Companies</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Performance monitoring and portfolio support
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/admin"
              className="group p-6 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-sm dark:hover:bg-gray-900/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 dark:group-hover:bg-gray-700 transition-colors">
                  <Settings className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">Admin</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    System configuration and integrations
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-300 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          </div>

          {/* Info Note */}
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Limited access system. Daily operations happen in Google Workspace and Linear.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-6">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500 dark:text-gray-400">
          © 2025 Disruptive Ventures. Command Center v1.0
        </div>
      </footer>
    </div>
  )
}
