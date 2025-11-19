'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { BookmarkCard } from '@/components/BookmarkCard'
import { TagFilter } from '@/components/TagFilter'

export default function SavedPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: bookmarks, isLoading, error } = useQuery({
    queryKey: ['bookmarks', selectedTag],
    queryFn: () => api.getBookmarks(selectedTag || undefined),
  })

  const deleteMutation = useMutation({
    mutationFn: (bookmarkId: number) => api.deleteBookmark(bookmarkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    },
  })

  // Filter bookmarks by search query
  const filteredBookmarks = useMemo(() => {
    if (!bookmarks) return []

    if (!searchQuery.trim()) return bookmarks

    const query = searchQuery.toLowerCase()
    return bookmarks.filter((bookmark) =>
      bookmark.title.toLowerCase().includes(query) ||
      (bookmark.note && bookmark.note.toLowerCase().includes(query))
    )
  }, [bookmarks, searchQuery])

  // Extract unique tags from all bookmarks
  const allTags = useMemo(() => {
    if (!bookmarks) return []
    const tagSet = new Set<string>()
    bookmarks.forEach((bookmark) => {
      bookmark.tags.forEach((tag) => tagSet.add(tag))
    })
    return Array.from(tagSet).sort()
  }, [bookmarks])

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading bookmarks...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Error loading bookmarks</p>
          <p className="text-red-600 text-sm mt-1">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Saved</h1>

        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search by title or note..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedTag(null)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedTag === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              {allTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setSelectedTag(tag)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedTag === tag
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {filteredBookmarks.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500 text-lg">
            {searchQuery || selectedTag
              ? 'No bookmarks found matching your filters'
              : 'No bookmarks yet'}
          </p>
          {(searchQuery || selectedTag) && (
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedTag(null)
              }}
              className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBookmarks.map((bookmark) => (
            <BookmarkCard
              key={bookmark.id}
              bookmark={bookmark}
              onDelete={(id) => {
                if (confirm('Are you sure you want to delete this bookmark?')) {
                  deleteMutation.mutate(id)
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}

