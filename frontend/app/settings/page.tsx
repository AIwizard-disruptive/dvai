'use client'

import { AppLayout } from '@/components/app-layout'
import { useTheme } from '@/components/theme-provider'
import {
    AlertCircle,
    Check,
    Copy,
    Eye,
    EyeOff,
    Key,
    LogOut,
    Moon,
    Settings as SettingsIcon,
    Sun
} from 'lucide-react'
import { useState } from 'react'

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme()
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiSettings, setApiSettings] = useState({
    linearApiKey: '••••••••••••••••••••',
    googleClientId: '••••••••••••••••••••',
    openaiApiKey: '••••••••••••••••••••',
    supabaseUrl: 'https://your-project.supabase.co',
    supabaseKey: '••••••••••••••••••••'
  })
  const [copied, setCopied] = useState<string | null>(null)

  const handleCopy = (field: string, value: string) => {
    navigator.clipboard.writeText(value)
    setCopied(field)
    setTimeout(() => setCopied(null), 2000)
  }

  const handleLogout = () => {
    // Implement logout logic here
    console.log('Logging out...')
    // Clear tokens, redirect to login, etc.
  }

  const handleSaveApiSettings = () => {
    // Implement API settings save logic
    console.log('Saving API settings...', apiSettings)
    alert('API settings saved successfully!')
  }

  return (
    <AppLayout>
      <div className="space-y-8 max-w-4xl">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-6">
            <div className="w-10 h-10 flex items-center justify-center">
              <SettingsIcon className="h-6 w-6 text-gray-700 dark:text-gray-300" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Settings</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            Manage your account preferences and application settings
          </p>
        </div>

        {/* User Profile Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Profile</h2>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="p-6 flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <span className="text-xl font-semibold text-white">ML</span>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Marcus Löwegren
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  marcus.lowegren@disruptiveventures.se
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Owner • Joined Dec 2024
                </p>
              </div>
              <button className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors">
                Edit Profile
              </button>
            </div>
          </div>
        </div>

        {/* Appearance Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Appearance</h2>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {theme === 'dark' ? (
                      <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                    ) : (
                      <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                    )}
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Theme
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Currently using <span className="font-medium">{theme === 'dark' ? 'Dark' : 'Light'}</span> mode
                  </p>
                </div>
                <button
                  onClick={toggleTheme}
                  className="relative inline-flex h-10 w-20 items-center rounded-full bg-gray-200 dark:bg-gray-700 transition-colors"
                >
                  <span
                    className={`inline-block h-8 w-8 transform rounded-full bg-white dark:bg-gray-900 transition-transform shadow-lg flex items-center justify-center ${
                      theme === 'dark' ? 'translate-x-11' : 'translate-x-1'
                    }`}
                  >
                    {theme === 'dark' ? (
                      <Moon className="h-4 w-4 text-gray-100" />
                    ) : (
                      <Sun className="h-4 w-4 text-gray-900" />
                    )}
                  </span>
                </button>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Toggle between light and dark mode. Your preference is saved automatically.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* API Settings Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">API Configuration</h2>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="p-6 space-y-6">
              {/* Warning Banner */}
              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="flex gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="text-sm font-medium text-amber-900 dark:text-amber-100 mb-1">
                      Sensitive Information
                    </div>
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                      API keys grant access to your external services. Never share these keys publicly.
                    </p>
                  </div>
                </div>
              </div>

              {/* Linear API */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  Linear API Key
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      value={apiSettings.linearApiKey}
                      onChange={(e) => setApiSettings({ ...apiSettings, linearApiKey: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent outline-none"
                      placeholder="lin_api_..."
                    />
                  </div>
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
                  >
                    {showApiKey ? (
                      <EyeOff className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                  <button
                    onClick={() => handleCopy('linear', apiSettings.linearApiKey)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
                  >
                    {copied === 'linear' ? (
                      <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Used for syncing tasks and issues with Linear
                </p>
              </div>

              {/* Google OAuth */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  Google OAuth Client ID
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={apiSettings.googleClientId}
                    onChange={(e) => setApiSettings({ ...apiSettings, googleClientId: e.target.value })}
                    className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent outline-none"
                    placeholder="xxxxx.apps.googleusercontent.com"
                  />
                  <button
                    onClick={() => handleCopy('google', apiSettings.googleClientId)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
                  >
                    {copied === 'google' ? (
                      <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  For Google Calendar, Gmail, and Drive integration
                </p>
              </div>

              {/* OpenAI API */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  OpenAI API Key
                </label>
                <div className="flex gap-2">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    value={apiSettings.openaiApiKey}
                    onChange={(e) => setApiSettings({ ...apiSettings, openaiApiKey: e.target.value })}
                    className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent outline-none"
                    placeholder="sk-..."
                  />
                  <button
                    onClick={() => handleCopy('openai', apiSettings.openaiApiKey)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
                  >
                    {copied === 'openai' ? (
                      <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  For AI-powered document analysis and task extraction
                </p>
              </div>

              {/* Supabase URL */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  Supabase Project URL
                </label>
                <input
                  type="text"
                  value={apiSettings.supabaseUrl}
                  onChange={(e) => setApiSettings({ ...apiSettings, supabaseUrl: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent outline-none"
                  placeholder="https://xxxxx.supabase.co"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Your Supabase project URL
                </p>
              </div>

              {/* Supabase Anon Key */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  Supabase Anon Key
                </label>
                <div className="flex gap-2">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    value={apiSettings.supabaseKey}
                    onChange={(e) => setApiSettings({ ...apiSettings, supabaseKey: e.target.value })}
                    className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent outline-none"
                    placeholder="eyJ..."
                  />
                  <button
                    onClick={() => handleCopy('supabase', apiSettings.supabaseKey)}
                    className="px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
                  >
                    {copied === 'supabase' ? (
                      <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Public anonymous key for client-side authentication
                </p>
              </div>

              {/* Save Button */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-800 flex gap-3">
                <button
                  onClick={handleSaveApiSettings}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Save API Settings
                </button>
                <button
                  onClick={() => {
                    setApiSettings({
                      linearApiKey: '••••••••••••••••••••',
                      googleClientId: '••••••••••••••••••••',
                      openaiApiKey: '••••••••••••••••••••',
                      supabaseUrl: 'https://your-project.supabase.co',
                      supabaseKey: '••••••••••••••••••••'
                    })
                  }}
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Account Actions Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Account</h2>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <LogOut className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Sign Out
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Sign out of your account on this device
                  </p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Integration Status */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Integration Status</h2>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900">
            <div className="p-6 space-y-3">
              {[
                { name: 'Linear', status: 'connected', lastSync: '5 minutes ago' },
                { name: 'Google Workspace', status: 'connected', lastSync: '12 minutes ago' },
                { name: 'Whisperflow', status: 'connected', lastSync: '1 hour ago' }
              ].map((integration) => (
                <div
                  key={integration.name}
                  className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 dark:bg-green-400" />
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {integration.name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Last synced {integration.lastSync}
                      </div>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
                    {integration.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}


