'use client'

import { KanbanBoard, type Task } from '@/components/kanban-board'
import { TaskDetailPanel } from '@/components/task-detail-panel'
import { Filter, Plus, RefreshCw } from 'lucide-react'
import { useState } from 'react'

// Sample activities data for Disruptive Ventures - replace with API calls
const initialActivities: Task[] = [
  {
    id: 'a1',
    title: 'Q4 2025 Board Meeting',
    description: 'Quarterly board meeting to review portfolio performance, discuss strategy, and make key decisions',
    status: 'in_progress',
    priority: 'high',
    assignee: {
      name: 'Marcus Löwegren',
      initials: 'ML'
    },
    dueDate: '2025-12-20',
    tags: ['board', 'quarterly', 'strategy'],
    commentCount: 5
  },
  {
    id: 'a2',
    title: 'LP Update Report - December',
    description: 'Monthly limited partner update covering portfolio performance and new investments',
    status: 'todo',
    priority: 'high',
    assignee: {
      name: 'Niklas Ivarsson',
      initials: 'NI'
    },
    dueDate: '2025-12-28',
    tags: ['lp', 'reporting', 'monthly']
  },
  {
    id: 'a3',
    title: 'Portfolio Company Check-ins',
    description: 'Quarterly check-in calls with all 18 portfolio companies',
    status: 'in_progress',
    priority: 'medium',
    assignee: {
      name: 'Marcus Löwegren',
      initials: 'ML'
    },
    dueDate: '2025-12-31',
    tags: ['portfolio', 'check-in', 'quarterly']
  },
  {
    id: 'a4',
    title: 'Annual Investment Committee Meeting',
    description: 'Review investment performance, approve new fund allocations, and set 2026 strategy',
    status: 'backlog',
    priority: 'medium',
    dueDate: '2026-01-15',
    tags: ['investment', 'annual', 'strategy']
  },
  {
    id: 'a5',
    title: 'Partner Offsite Planning',
    description: 'Organize Q1 2026 partner offsite, including location, agenda, and guest speakers',
    status: 'backlog',
    priority: 'low',
    dueDate: '2026-01-20',
    tags: ['team', 'planning', 'offsite']
  },
  {
    id: 'a6',
    title: 'TechFlow AI Due Diligence',
    description: 'Complete technical and financial due diligence for potential Series A investment',
    status: 'in_progress',
    priority: 'urgent',
    assignee: {
      name: 'Kassi Rantanen',
      initials: 'KR'
    },
    dueDate: '2025-12-22',
    tags: ['dealflow', 'due-diligence', 'series-a']
  },
  {
    id: 'a7',
    title: 'Q3 2025 Financial Close',
    description: 'Finalize Q3 financial statements and submit to auditors',
    status: 'done',
    priority: 'high',
    tags: ['finance', 'quarterly', 'compliance']
  },
  {
    id: 'a8',
    title: 'Fund II Fundraising Preparation',
    description: 'Prepare materials, pitch deck, and data room for Fund II fundraising',
    status: 'backlog',
    priority: 'medium',
    dueDate: '2026-02-01',
    tags: ['fundraising', 'fund-ii', 'strategy']
  },
  {
    id: 'a9',
    title: 'Advisory Board Meeting',
    description: 'Quarterly advisory board meeting with external advisors',
    status: 'todo',
    priority: 'medium',
    assignee: {
      name: 'Marcus Löwegren',
      initials: 'ML'
    },
    dueDate: '2026-01-10',
    tags: ['advisory', 'quarterly', 'governance']
  }
]

export default function KnowledgeActivitiesPage() {
  const [activities, setActivities] = useState<Task[]>(initialActivities)
  const [selectedActivity, setSelectedActivity] = useState<Task | null>(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'my' | 'urgent'>('all')

  const handleActivityClick = (activity: Task) => {
    setSelectedActivity(activity)
    setIsPanelOpen(true)
  }

  const handleActivityUpdate = (activityId: string, updates: Partial<Task>) => {
    setActivities(prev => prev.map(activity =>
      activity.id === activityId ? { ...activity, ...updates } : activity
    ))
    
    // Update selected activity if it's the one being updated
    if (selectedActivity?.id === activityId) {
      setSelectedActivity(prev => prev ? { ...prev, ...updates } : null)
    }

    // Here you would also call your API to persist the changes
    console.log('Activity updated:', activityId, updates)
  }

  const handleClosePanel = () => {
    setIsPanelOpen(false)
    // Delay clearing selectedActivity to allow animation to complete
    setTimeout(() => setSelectedActivity(null), 300)
  }

  const filteredActivities = activities.filter(activity => {
    if (filter === 'my') {
      return activity.assignee?.name === 'Marcus Löwegren'
    }
    if (filter === 'urgent') {
      return activity.priority === 'high' || activity.priority === 'urgent'
    }
    return true
  })

  return (
    <div className="relative min-h-screen bg-white dark:bg-gray-950">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 sticky top-0 z-30">
        <div className="max-w-[2000px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                Activities
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Track and manage Disruptive Ventures activities, meetings, and events
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
                <RefreshCw className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
                <Plus className="h-4 w-4" />
                New Activity
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === 'all'
                    ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                All Activities ({activities.length})
              </button>
              <button
                onClick={() => setFilter('my')}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === 'my'
                    ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                My Activities
              </button>
              <button
                onClick={() => setFilter('urgent')}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === 'urgent'
                    ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Urgent
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban Board - Uses full viewport width */}
      <div className="max-w-[2000px] mx-auto h-[calc(100vh-180px)] px-4 sm:px-6 lg:px-8 py-6">
        <KanbanBoard
          initialTasks={filteredActivities}
          onTaskClick={handleActivityClick}
          onTaskUpdate={handleActivityUpdate}
          onTaskCreate={(status) => {
            console.log('Create new activity in column:', status)
            // Implement activity creation
          }}
        />
      </div>

      {/* Activity Detail Panel */}
      <TaskDetailPanel
        task={selectedActivity}
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
        onUpdate={handleActivityUpdate}
      />
    </div>
  )
}
