'use client'

import { cn } from '@/lib/utils'
import {
    AlertCircle,
    Calendar,
    CheckCircle2,
    ChevronDown,
    Circle,
    CircleDot,
    CircleX,
    Link as LinkIcon,
    MessageSquare,
    Tag,
    User,
    X
} from 'lucide-react'
import { useState } from 'react'
import type { Task } from './kanban-board'

const statusOptions = [
  { value: 'backlog', label: 'Backlog', icon: Circle, color: 'text-gray-500 dark:text-gray-400' },
  { value: 'todo', label: 'Todo', icon: Circle, color: 'text-gray-500 dark:text-gray-400' },
  { value: 'in_progress', label: 'In Progress', icon: CircleDot, color: 'text-yellow-500 dark:text-yellow-400' },
  { value: 'done', label: 'Done', icon: CheckCircle2, color: 'text-green-500 dark:text-green-400' },
  { value: 'canceled', label: 'Canceled', icon: CircleX, color: 'text-gray-400 dark:text-gray-500' }
] as const

interface TaskDetailPanelProps {
  task: Task | null
  isOpen: boolean
  onClose: () => void
  onUpdate: (taskId: string, updates: Partial<Task>) => void
}

export function TaskDetailPanel({ task, isOpen, onClose, onUpdate }: TaskDetailPanelProps) {
  const [showStatusDropdown, setShowStatusDropdown] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState(task?.title || '')
  const [editedDescription, setEditedDescription] = useState(task?.description || '')

  if (!task) return null

  const currentStatus = statusOptions.find(s => s.value === task.status)
  const StatusIcon = currentStatus?.icon || Circle

  const handleStatusChange = (newStatus: Task['status']) => {
    onUpdate(task.id, { status: newStatus })
    setShowStatusDropdown(false)
  }

  const handleSave = () => {
    onUpdate(task.id, {
      title: editedTitle,
      description: editedDescription
    })
    setIsEditing(false)
  }

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={cn(
          'fixed top-0 right-0 h-screen w-[480px] bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out overflow-y-auto',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-2">
            {task.linearId && (
              <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
                {task.linearId}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status Dropdown */}
          <div>
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 block">
              Status
            </label>
            <div className="relative">
              <button
                onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-2">
                  <StatusIcon className={cn('h-4 w-4', currentStatus?.color)} />
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {currentStatus?.label}
                  </span>
                </div>
                <ChevronDown className={cn(
                  'h-4 w-4 text-gray-500 dark:text-gray-400 transition-transform',
                  showStatusDropdown && 'rotate-180'
                )} />
              </button>

              {/* Dropdown Menu */}
              {showStatusDropdown && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 z-20">
                  {statusOptions.map((status, index) => {
                    const Icon = status.icon
                    const isSelected = status.value === task.status
                    return (
                      <button
                        key={status.value}
                        onClick={() => handleStatusChange(status.value)}
                        className={cn(
                          'w-full flex items-center gap-3 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors',
                          isSelected && 'bg-gray-50 dark:bg-gray-750'
                        )}
                      >
                        <Icon className={cn('h-4 w-4', status.color)} />
                        <span className="flex-1 text-left text-gray-900 dark:text-gray-100">
                          {status.label}
                        </span>
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          {index + 1}
                        </span>
                        {isSelected && (
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                        )}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Title */}
          <div>
            {isEditing ? (
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="w-full text-xl font-semibold text-gray-900 dark:text-gray-100 bg-transparent border-b border-gray-300 dark:border-gray-700 focus:border-blue-500 dark:focus:border-blue-400 outline-none pb-2"
                placeholder="Task title"
              />
            ) : (
              <h2
                onClick={() => setIsEditing(true)}
                className="text-xl font-semibold text-gray-900 dark:text-gray-100 cursor-text hover:text-gray-700 dark:hover:text-gray-300"
              >
                {task.title}
              </h2>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 block">
              Description
            </label>
            {isEditing ? (
              <textarea
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
                rows={6}
                className="w-full text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 outline-none resize-none"
                placeholder="Add a description..."
              />
            ) : (
              <p
                onClick={() => setIsEditing(true)}
                className="text-sm text-gray-700 dark:text-gray-300 cursor-text hover:text-gray-900 dark:hover:text-gray-100 min-h-[60px]"
              >
                {task.description || 'No description'}
              </p>
            )}
          </div>

          {/* Save/Cancel Buttons */}
          {isEditing && (
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setIsEditing(false)
                  setEditedTitle(task.title)
                  setEditedDescription(task.description || '')
                }}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          )}

          {/* Meta Information */}
          <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-800">
            {/* Assignee */}
            {task.assignee && (
              <div className="flex items-center gap-3">
                <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div className="flex items-center gap-2">
                  {task.assignee.avatar ? (
                    <img
                      src={task.assignee.avatar}
                      alt={task.assignee.name}
                      className="h-6 w-6 rounded-full"
                    />
                  ) : (
                    <div className="h-6 w-6 rounded-full bg-purple-500 dark:bg-purple-600 flex items-center justify-center">
                      <span className="text-xs font-semibold text-white">
                        {task.assignee.initials || task.assignee.name.charAt(0)}
                      </span>
                    </div>
                  )}
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {task.assignee.name}
                  </span>
                </div>
              </div>
            )}

            {/* Priority */}
            {task.priority && (
              <div className="flex items-center gap-3">
                <AlertCircle className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span className={cn(
                  'text-sm font-medium',
                  task.priority === 'urgent' && 'text-red-600 dark:text-red-400',
                  task.priority === 'high' && 'text-orange-600 dark:text-orange-400',
                  task.priority === 'medium' && 'text-blue-600 dark:text-blue-400',
                  task.priority === 'low' && 'text-gray-600 dark:text-gray-400'
                )}>
                  {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                </span>
              </div>
            )}

            {/* Due Date */}
            {task.dueDate && (
              <div className="flex items-center gap-3">
                <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Due {task.dueDate}
                </span>
              </div>
            )}

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <div className="flex items-start gap-3">
                <Tag className="h-4 w-4 text-gray-500 dark:text-gray-400 mt-0.5" />
                <div className="flex flex-wrap gap-1.5">
                  {task.tags.map(tag => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Linear Link */}
            {task.linearId && (
              <div className="flex items-center gap-3">
                <LinkIcon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <a
                  href={`https://linear.app/issue/${task.linearId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Open in Linear
                </a>
              </div>
            )}

            {/* Comments Count */}
            {task.commentCount && task.commentCount > 0 && (
              <div className="flex items-center gap-3">
                <MessageSquare className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {task.commentCount} {task.commentCount === 1 ? 'comment' : 'comments'}
                </span>
              </div>
            )}
          </div>

          {/* Activity/Comments Section Placeholder */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-800">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Comments
              </h3>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No comments yet
            </div>
          </div>
        </div>
      </div>
    </>
  )
}


