'use client'

import { KanbanBoard, type Task } from '@/components/kanban-board'
import { TaskDetailPanel } from '@/components/task-detail-panel'
import { Filter, Plus, RefreshCw } from 'lucide-react'
import { useState } from 'react'

// Sample data - replace with API calls
const initialTasks: Task[] = [
  {
    id: '1',
    title: 'Implement authentication system',
    description: 'Set up OAuth 2.0 with Google and Linear integration for user authentication',
    status: 'in_progress',
    priority: 'high',
    assignee: {
      name: 'Marcus Löwegren',
      initials: 'ML'
    },
    dueDate: '2025-12-20',
    tags: ['backend', 'auth'],
    linearId: 'DIS-91',
    commentCount: 3
  },
  {
    id: '2',
    title: 'Design portfolio dashboard',
    description: 'Create comprehensive dashboard showing portfolio metrics and company performance',
    status: 'todo',
    priority: 'medium',
    assignee: {
      name: 'Niklas Ivarsson',
      initials: 'NI'
    },
    dueDate: '2025-12-22',
    tags: ['frontend', 'design'],
    linearId: 'DIS-92'
  },
  {
    id: '3',
    title: 'Legacy Learning platform integration',
    description: 'Integrate with existing learning management system',
    status: 'backlog',
    priority: 'low',
    linearId: 'DIS-5'
  },
  {
    id: '4',
    title: 'Fix dark mode styling issues',
    description: 'Address reported dark mode contrast and visibility problems',
    status: 'done',
    priority: 'medium',
    assignee: {
      name: 'Marcus Löwegren',
      initials: 'ML'
    },
    tags: ['frontend', 'ui'],
    linearId: 'DIS-89'
  }
]

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'my' | 'high'>('all')

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task)
    setIsPanelOpen(true)
  }

  const handleTaskUpdate = (taskId: string, updates: Partial<Task>) => {
    setTasks(prev => prev.map(task =>
      task.id === taskId ? { ...task, ...updates } : task
    ))
    
    // Update selected task if it's the one being updated
    if (selectedTask?.id === taskId) {
      setSelectedTask(prev => prev ? { ...prev, ...updates } : null)
    }

    // Here you would also call your API to persist the changes
    console.log('Task updated:', taskId, updates)
  }

  const handleClosePanel = () => {
    setIsPanelOpen(false)
    // Delay clearing selectedTask to allow animation to complete
    setTimeout(() => setSelectedTask(null), 300)
  }

  const filteredTasks = tasks.filter(task => {
    if (filter === 'my') {
      return task.assignee?.name === 'Marcus Löwegren'
    }
    if (filter === 'high') {
      return task.priority === 'high' || task.priority === 'urgent'
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
                Tasks
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Manage and track your team's work
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
                <RefreshCw className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
                <Plus className="h-4 w-4" />
                New Task
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
                All Tasks ({tasks.length})
              </button>
              <button
                onClick={() => setFilter('my')}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === 'my'
                    ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                My Tasks
              </button>
              <button
                onClick={() => setFilter('high')}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  filter === 'high'
                    ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                High Priority
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban Board - Uses full viewport width, automatically expands when sidebar is hidden */}
      <div className="max-w-[2000px] mx-auto h-[calc(100vh-180px)] px-4 sm:px-6 lg:px-8 py-6">
        <KanbanBoard
          initialTasks={filteredTasks}
          onTaskClick={handleTaskClick}
          onTaskUpdate={handleTaskUpdate}
          onTaskCreate={(status) => {
            console.log('Create new task in column:', status)
            // Implement task creation
          }}
        />
      </div>

      {/* Task Detail Panel */}
      <TaskDetailPanel
        task={selectedTask}
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
        onUpdate={handleTaskUpdate}
      />
    </div>
  )
}


