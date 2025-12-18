'use client'

import { AppLayout } from '@/components/app-layout'
import { ExternalLink, Grid3x3, Linkedin, List, Mail, Users } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Person {
  initials: string
  name: string
  title?: string
  email: string
  linkedin?: string
  avatar?: string
}

// Generate avatar URL from name
const getAvatarUrl = (name: string) => {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&size=128&background=random&color=fff&bold=true`
}

export default function PeoplePage() {
  const [viewMode, setViewMode] = useState<'card' | 'list'>('card')
  const [people, setPeople] = useState<Person[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPeople()
  }, [])

  const loadPeople = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('http://localhost:8000/api/people')
      // const data = await response.json()
      
      // Mock data matching the screenshot structure
      const mockPeople: Person[] = [
        { initials: 'AH', name: 'Alexander Hoglund', email: 'alexander.hoglund@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'AN', name: 'Anton Nygren', email: 'anton.nygren@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'CS', name: 'Charlotta Stickler', email: 'charlotta.stickler@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'EC', name: 'Emrik Cygnaeus', email: 'emrik.cygnaeus@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'FL', name: 'Fanny Lundin', email: 'fanny.lundin@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'GN', name: 'Guelnoji Njetein', email: 'guelnoji.njetein@disruptiveventures.se' },
        { initials: 'HW', name: 'H W Melius', email: 'hw.melius@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'H', name: 'Henrik', email: 'henrik@disruptiveventures.se' },
        { initials: 'HL', name: 'Henrik Lundgren', email: 'henrik.lundgren@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'HW', name: 'Henrik Wenckert', email: 'henrik.wenckert@disruptiveventures.se' },
        { initials: 'HC', name: 'Hugo Carlsten', email: 'hugo.carlsten@disruptiveventures.se' },
        { initials: 'JC', name: 'Jakob Cedermark', email: 'jakob.cedermark@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'JN', name: 'Jakob Nylund', email: 'jakob.nylund@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'JE', name: 'Joel Ek', email: 'joel.ek@disruptiveventures.se', linkedin: 'EmailLinkedIn' },
        { initials: 'JD', name: 'Johan de Boer', email: 'johan.deboer@disruptiveventures.se' },
        { initials: 'JE', name: 'Johnny Engman', email: 'johnny.engman@disruptiveventures.se' },
        { initials: 'JP', name: 'Jonna Persson', email: 'jonna.persson@disruptiveventures.se' },
      ].map(person => ({
        ...person,
        avatar: getAvatarUrl(person.name)
      }))
      
      setPeople(mockPeople)
    } catch (error) {
      console.error('Error loading people:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="w-10 h-10 flex items-center justify-center">
                <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">People</h1>
            </div>
            
            {/* View Toggle */}
            <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('card')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'card'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                <Grid3x3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-13">
            Manage relationships, track interactions, and maintain your network
          </p>
        </div>

        {/* People List/Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 dark:border-gray-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">Loading people...</p>
          </div>
        ) : viewMode === 'card' ? (
          /* Card View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {people.map((person, idx) => (
              <div
                key={idx}
                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-900 hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-12 h-12 rounded-full overflow-hidden flex-shrink-0 bg-gray-100 dark:bg-gray-800 ring-2 ring-gray-200 dark:ring-gray-700">
                    <img
                      src={person.avatar}
                      alt={person.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                      {person.name}
                    </h3>
                    {person.title ? (
                      <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                        {person.title}
                      </p>
                    ) : (
                      <p className="text-xs text-gray-400 dark:text-gray-500 italic truncate">
                        No title
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <a
                    href={`mailto:${person.email}`}
                    className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 truncate"
                  >
                    <Mail className="h-3 w-3 flex-shrink-0" />
                    <span className="truncate">{person.email}</span>
                  </a>
                  {person.linkedin && (
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                      <Linkedin className="h-3 w-3 flex-shrink-0" />
                      <span>LinkedIn</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* List View */
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-900">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      Avatar
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      LinkedIn
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                  {people.map((person, idx) => (
                    <tr
                      key={idx}
                      className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 ring-2 ring-gray-200 dark:ring-gray-700">
                          <img
                            src={person.avatar}
                            alt={person.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-sm text-gray-900 dark:text-gray-100">
                          {person.name}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {person.title ? (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {person.title}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-400 dark:text-gray-500 italic">
                            —
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <a
                          href={`mailto:${person.email}`}
                          className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                        >
                          {person.email}
                        </a>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {person.linkedin && (
                          <Linkedin className="h-4 w-4 text-blue-600 dark:text-blue-400 inline-block" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Integration Note */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg">
          <div className="flex gap-3">
            <ExternalLink className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                Sync with Google Contacts
              </div>
              <p className="text-sm text-blue-700 dark:text-blue-300">
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
