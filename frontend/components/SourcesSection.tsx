'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { SourceResponse, SourceCreate, SourceUpdate } from '@/lib/types'

export function SourcesSection() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingSource, setEditingSource] = useState<SourceResponse | null>(null)
  const queryClient = useQueryClient()

  const { data: sources, isLoading, error } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.getSources(),
  })

  const createMutation = useMutation({
    mutationFn: (sourceData: SourceCreate) => api.createSource(sourceData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      setIsAddModalOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: SourceUpdate }) =>
      api.updateSource(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      setEditingSource(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteSource(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const toggleActive = (source: SourceResponse) => {
    updateMutation.mutate({
      id: source.id,
      data: { is_active: !source.is_active },
    })
  }

  // Type guard to check if data is SourceCreate
  const isSourceCreate = (
    data: SourceCreate | SourceUpdate
  ): data is SourceCreate => {
    // SourceCreate requires title and feed_url to be non-null strings
    const isCreate =
      typeof data.title === 'string' &&
      data.title.length > 0 &&
      typeof data.feed_url === 'string' &&
      data.feed_url.length > 0

    if (!isCreate) {
      console.warn('[SourcesSection] Type guard failed: data is not SourceCreate', {
        data,
        titleType: typeof data.title,
        titleValue: data.title,
        feedUrlType: typeof data.feed_url,
        feedUrlValue: data.feed_url,
      })
    } else {
      console.log('[SourcesSection] Type guard passed: data is SourceCreate', {
        title: data.title,
        feed_url: data.feed_url,
      })
    }

    return isCreate
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading sources...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-medium">Error loading sources</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : 'Unknown error occurred'}
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">RSS Sources</h2>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add Source
        </button>
      </div>

      {sources && sources.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500 text-lg">No sources found</p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Add your first source
          </button>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feed URL
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sources?.map((source) => (
                <tr key={source.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {source.title}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500 max-w-xs truncate">
                      {source.feed_url}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{source.category || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => toggleActive(source)}
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        source.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {source.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => setEditingSource(source)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Are you sure you want to delete "${source.title}"?`)) {
                          deleteMutation.mutate(source.id)
                        }
                      }}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isAddModalOpen && (
        <SourceModal
          onClose={() => setIsAddModalOpen(false)}
          onSave={(data) => {
            console.log('[SourcesSection] onSave called (add mode)', {
              data,
              dataKeys: Object.keys(data),
            })

            if (isSourceCreate(data)) {
              console.log('[SourcesSection] Type guard passed, calling createMutation')
              createMutation.mutate(data)
            } else {
              console.error(
                '[SourcesSection] Type guard failed: Expected SourceCreate but got SourceUpdate',
                { data }
              )
              // Fallback: try to convert SourceUpdate to SourceCreate
              if (data.title && data.feed_url) {
                console.warn(
                  '[SourcesSection] Attempting to convert SourceUpdate to SourceCreate',
                  { data }
                )
                createMutation.mutate({
                  title: data.title,
                  feed_url: data.feed_url,
                  site_url: data.site_url ?? null,
                  category: data.category ?? null,
                  lang: data.lang ?? 'en',
                  is_active: data.is_active ?? true,
                })
              } else {
                console.error(
                  '[SourcesSection] Cannot convert: missing required fields',
                  { data }
                )
              }
            }
          }}
          isLoading={createMutation.isPending}
          error={createMutation.error}
        />
      )}

      {editingSource && (
        <SourceModal
          source={editingSource}
          onClose={() => setEditingSource(null)}
          onSave={(data) =>
            updateMutation.mutate({ id: editingSource.id, data })
          }
          isLoading={updateMutation.isPending}
          error={updateMutation.error}
        />
      )}
    </div>
  )
}

interface SourceModalProps {
  source?: SourceResponse
  onClose: () => void
  onSave: (data: SourceCreate | SourceUpdate) => void
  isLoading: boolean
  error: unknown
}

function SourceModal({
  source,
  onClose,
  onSave,
  isLoading,
  error,
}: SourceModalProps) {
  const [title, setTitle] = useState(source?.title || '')
  const [feedUrl, setFeedUrl] = useState(source?.feed_url || '')
  const [siteUrl, setSiteUrl] = useState(source?.site_url || '')
  const [category, setCategory] = useState(source?.category || '')
  const [lang, setLang] = useState(source?.lang || 'en')
  const [isActive, setIsActive] = useState(source?.is_active ?? true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (source) {
      onSave({
        title: title || null,
        feed_url: feedUrl || null,
        site_url: siteUrl || null,
        category: category || null,
        lang: lang || null,
        is_active: isActive,
      })
    } else {
      onSave({
        title,
        feed_url: feedUrl,
        site_url: siteUrl || null,
        category: category || null,
        lang,
        is_active: isActive,
      })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {source ? 'Edit Source' : 'Add Source'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Feed URL *
            </label>
            <input
              type="url"
              value={feedUrl}
              onChange={(e) => setFeedUrl(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Site URL
            </label>
            <input
              type="url"
              value={siteUrl}
              onChange={(e) => setSiteUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <input
              type="text"
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Active</span>
            </label>
          </div>

          {error != null && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">
                {error instanceof Error ? error.message : 'Failed to save source'}
              </p>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

