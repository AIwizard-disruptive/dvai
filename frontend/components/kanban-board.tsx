'use client'

import { cn } from '@/lib/utils'
import {
    Calendar,
    CheckCircle2,
    Circle,
    CircleDot,
    CircleX,
    MessageSquare,
    MoreHorizontal,
    Plus,
    Tag
} from 'lucide-react'
import { useState } from 'react'

export interface Task {
  id: string
  title: string
  description?: string
  status: 'backlog' | 'todo' | 'in_progress' | 'done' | 'canceled'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  assignee?: {
    name: string
    avatar?: string
    initials?: string
  }
  dueDate?: string
  tags?: string[]
  commentCount?: number
  linearId?: string
}

const statusConfig = {
  backlog: {
    label: 'Backlog',
    icon: Circle,
    color: 'text-gray-500 dark:text-gray-400',
    bgColor: 'bg-gray-100 dark:bg-gray-800'
  },
  todo: {
    label: 'Todo',
    icon: Circle,
    color: 'text-gray-500 dark:text-gray-400',
    bgColor: 'bg-gray-100 dark:bg-gray-800'
  },
  in_progress: {
    label: 'In Progress',
    icon: CircleDot,
    color: 'text-yellow-500 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/20'
  },
  done: {
    label: 'Done',
    icon: CheckCircle2,
    color: 'text-green-500 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/20'
  },
  canceled: {
    label: 'Canceled',
    icon: CircleX,
    color: 'text-gray-400 dark:text-gray-500',
    bgColor: 'bg-gray-100 dark:bg-gray-800'
  }
}

interface KanbanBoardProps {
  initialTasks?: Task[]
  onTaskClick?: (task: Task) => void
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void
  onTaskCreate?: (columnStatus: Task['status']) => void
}

export function KanbanBoard({ 
  initialTasks = [],
  onTaskClick,
  onTaskUpdate,
  onTaskCreate 
}: KanbanBoardProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [draggedTask, setDraggedTask] = useState<Task | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const columns: Task['status'][] = ['backlog', 'todo', 'in_progress', 'done', 'canceled']

  const getTasksByStatus = (status: Task['status']) => {
    return tasks.filter(task => task.status === status)
  }

  const handleDragStart = (task: Task) => {
    setDraggedTask(task)
    setIsDragging(true)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (status: Task['status']) => {
    if (draggedTask && draggedTask.status !== status) {
      const updatedTasks = tasks.map(task =>
        task.id === draggedTask.id ? { ...task, status } : task
      )
      setTasks(updatedTasks)
      onTaskUpdate?.(draggedTask.id, { status })
    }
    setDraggedTask(null)
    // Small delay to prevent click firing after drag
    setTimeout(() => setIsDragging(false), 100)
  }

  const handleDragEnd = () => {
    setDraggedTask(null)
    setTimeout(() => setIsDragging(false), 100)
  }

  return (
    <div className="flex gap-4 h-full overflow-x-auto pb-4">
      {columns.map(status => {
        const config = statusConfig[status]
        const StatusIcon = config.icon
        const columnTasks = getTasksByStatus(status)

        return (
          <div
            key={status}
            className="flex-shrink-0 w-80 flex flex-col"
            onDragOver={handleDragOver}
            onDrop={() => handleDrop(status)}
          >
            {/* Column Header */}
            <div className="flex items-center justify-between mb-3 px-3">
              <div className="flex items-center gap-2">
                <StatusIcon className={cn('h-4 w-4', config.color)} />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {config.label}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">
                  {columnTasks.length}
                </span>
              </div>
              <button
                onClick={() => onTaskCreate?.(status)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-opacity"
              >
                <Plus className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Column Content */}
            <div className="flex-1 space-y-2 px-2 min-h-[200px]">
              {columnTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onClick={() => !isDragging && onTaskClick?.(task)}
                  onDragStart={() => handleDragStart(task)}
                  onDragEnd={handleDragEnd}
                  isDragging={draggedTask?.id === task.id}
                  isAnyDragging={isDragging}
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

interface TaskCardProps {
  task: Task
  onClick: () => void
  onDragStart: () => void
  onDragEnd: () => void
  isDragging: boolean
  isAnyDragging: boolean
}

function TaskCard({ task, onClick, onDragStart, onDragEnd, isDragging, isAnyDragging }: TaskCardProps) {
  const priorityColors = {
    low: 'text-gray-500 dark:text-gray-400',
    medium: 'text-blue-500 dark:text-blue-400',
    high: 'text-orange-500 dark:text-orange-400',
    urgent: 'text-red-500 dark:text-red-400'
  }

  const handleClick = (e: React.MouseEvent) => {
    // Prevent click if currently dragging
    if (isAnyDragging) {
      e.preventDefault()
      e.stopPropagation()
      return
    }
    onClick()
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onClick={handleClick}
      className={cn(
        'group p-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg cursor-pointer hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-sm transition-all select-none',
        isDragging && 'opacity-50 cursor-grabbing',
        !isDragging && 'cursor-pointer'
      )}
    >
      {/* Task Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 flex-1">
          {task.title}
        </h4>
        <button
          onClick={(e) => {
            e.stopPropagation()
            // Handle task menu
          }}
          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-opacity"
        >
          <MoreHorizontal className="h-3 w-3 text-gray-500 dark:text-gray-400" />
        </button>
      </div>

      {/* Task Description */}
      {task.description && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Task Meta */}
      <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
        {/* Linear ID */}
        {task.linearId && (
          <span className="font-mono text-gray-400 dark:text-gray-500">
            {task.linearId}
          </span>
        )}

        {/* Priority */}
        {task.priority && (
          <span className={cn('flex items-center gap-1', priorityColors[task.priority])}>
            <Tag className="h-3 w-3" />
            {task.priority}
          </span>
        )}

        {/* Due Date */}
        {task.dueDate && (
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {task.dueDate}
          </span>
        )}

        {/* Comments */}
        {task.commentCount && task.commentCount > 0 && (
          <span className="flex items-center gap-1">
            <MessageSquare className="h-3 w-3" />
            {task.commentCount}
          </span>
        )}

        {/* Assignee */}
        {task.assignee && (
          <div className="ml-auto flex items-center gap-1.5">
            {task.assignee.avatar ? (
              <img
                src={task.assignee.avatar}
                alt={task.assignee.name}
                className="h-5 w-5 rounded-full"
              />
            ) : (
              <div className="h-5 w-5 rounded-full bg-purple-500 dark:bg-purple-600 flex items-center justify-center">
                <span className="text-[10px] font-semibold text-white">
                  {task.assignee.initials || task.assignee.name.charAt(0)}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Tags */}
      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {task.tags.map(tag => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}


