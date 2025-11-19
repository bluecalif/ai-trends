'use client'

import { useState, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ItemResponse } from '@/lib/types'

interface BookmarkModalProps {
  item: ItemResponse | null
  isOpen: boolean
  onClose: () => void
}

export function BookmarkModal({ item, isOpen, onClose }: BookmarkModalProps) {
  const [title, setTitle] = useState('')
  const [note, setNote] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [showTagSuggestions, setShowTagSuggestions] = useState(false)
  const queryClient = useQueryClient()

  // Get all bookmarks to extract existing tags
  const { data: allBookmarks } = useQuery({
    queryKey: ['bookmarks'],
    queryFn: () => api.getBookmarks(),
  })

  // Extract unique tags from all bookmarks
  const existingTags = useMemo(() => {
    if (!allBookmarks) return []
    const tagSet = new Set<string>()
    allBookmarks.forEach((bookmark) => {
      bookmark.tags.forEach((tag) => tagSet.add(tag))
    })
    return Array.from(tagSet).sort()
  }, [allBookmarks])

  // Filter tags based on input
  const filteredSuggestions = useMemo(() => {
    if (!tagInput.trim()) return existingTags
    const query = tagInput.toLowerCase()
    return existingTags.filter(
      (tag) =>
        tag.toLowerCase().includes(query) && !tags.includes(tag)
    )
  }, [tagInput, existingTags, tags])

  const createMutation = useMutation({
    mutationFn: (bookmarkData: {
      item_id: number
      title: string
      tags: string[]
      note?: string | null
    }) => api.createBookmark(bookmarkData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
      handleClose()
    },
  })

  const handleClose = () => {
    setTitle('')
    setNote('')
    setTags([])
    setTagInput('')
    onClose()
  }

  const handleAddTag = () => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!item) return

    createMutation.mutate({
      item_id: item.id,
      title: title || item.title,
      tags,
      note: note || null,
    })
  }

  if (!isOpen || !item) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          setShowTagSuggestions(false)
        }
      }}
    >
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Save Bookmark</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={item.title}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Note (optional)
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Add a note..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags
            </label>
            <div className="relative">
              <div className="flex gap-2 mb-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => {
                      setTagInput(e.target.value)
                      setShowTagSuggestions(true)
                    }}
                    onFocus={() => setShowTagSuggestions(true)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleAddTag()
                        setShowTagSuggestions(false)
                      }
                    }}
                    onBlur={() => {
                      // Delay to allow click on suggestion
                      setTimeout(() => setShowTagSuggestions(false), 200)
                    }}
                    placeholder="Add a tag..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {showTagSuggestions && filteredSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-y-auto">
                      {filteredSuggestions.map((tag) => (
                        <button
                          key={tag}
                          type="button"
                          onClick={() => {
                            setTagInput(tag)
                            handleAddTag()
                            setShowTagSuggestions(false)
                          }}
                          className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm text-gray-700"
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                        aria-label={`Remove ${tag}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
            {existingTags.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-1">Existing tags:</p>
                <div className="flex flex-wrap gap-1">
                  {existingTags.slice(0, 10).map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => {
                        if (!tags.includes(tag)) {
                          setTags([...tags, tag])
                        }
                      }}
                      disabled={tags.includes(tag)}
                      className={`px-2 py-1 text-xs rounded transition-colors ${
                        tags.includes(tag)
                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                  {existingTags.length > 10 && (
                    <span className="px-2 py-1 text-xs text-gray-400">
                      +{existingTags.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {createMutation.error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">
                {createMutation.error instanceof Error
                  ? createMutation.error.message
                  : 'Failed to create bookmark'}
              </p>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

