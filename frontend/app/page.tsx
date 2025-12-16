import { ArrowRight, Brain, Building2, Settings, TrendingUp, Users } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      {/* Header */}
      <header className="border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <span className="font-semibold text-lg text-gray-900">Disruptive Ventures</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl w-full space-y-12 py-16">
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-semibold text-gray-900 tracking-tight">
              Command Center
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Strategic intelligence system powering venture operations. 
              Most work happens in Google and Linear—this is your oversight layer.
            </p>
          </div>

          {/* Four Wheels Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              href="/people"
              className="group p-6 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">People</h2>
                  <p className="text-sm text-gray-600">
                    Relationships, contacts, and meeting intelligence
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/dealflow"
              className="group p-6 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center flex-shrink-0 group-hover:bg-green-100 transition-colors">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">Dealflow</h2>
                  <p className="text-sm text-gray-600">
                    Investment pipeline and opportunity tracking
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/portfolio"
              className="group p-6 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center flex-shrink-0 group-hover:bg-purple-100 transition-colors">
                  <Building2 className="h-5 w-5 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">Portfolio Companies</h2>
                  <p className="text-sm text-gray-600">
                    Performance monitoring and portfolio support
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>

            <Link
              href="/admin"
              className="group p-6 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 group-hover:bg-gray-200 transition-colors">
                  <Settings className="h-5 w-5 text-gray-700" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">Admin</h2>
                  <p className="text-sm text-gray-600">
                    System configuration and integrations
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          </div>

          {/* Info Note */}
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Limited access system. Daily operations happen in Google Workspace and Linear.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-6">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          © 2025 Disruptive Ventures. Command Center v1.0
        </div>
      </footer>
    </div>
  )
}



