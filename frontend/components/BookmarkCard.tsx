'use client'

import { formatDistanceToNow } from 'date-fns'
import type { BookmarkResponse } from '@/lib/types'

interface BookmarkCardProps {
  bookmark: BookmarkResponse
  onDelete: (id: number) => void
}

export function BookmarkCard({ bookmark, onDelete }: BookmarkCardProps) {
  const timeAgo = formatDistanceToNow(new Date(bookmark.created_at), {
    addSuffix: true,
  })

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900 flex-1">
          {bookmark.item_link ? (
            <a
              href={bookmark.item_link}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              {bookmark.title}
            </a>
          ) : (
            <span>{bookmark.title}</span>
          )}
        </h3>
        <button
          onClick={() => onDelete(bookmark.id)}
          className="ml-2 text-red-600 hover:text-red-800 text-sm font-medium"
          aria-label="Delete bookmark"
        >
          Delete
        </button>
      </div>

      {bookmark.note && (
        <p className="text-gray-600 text-sm mb-3 line-clamp-3">
          {bookmark.note}
        </p>
      )}

      {bookmark.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {bookmark.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded font-medium"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{timeAgo}</span>
        {bookmark.item_link && (
          <a
            href={bookmark.item_link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Read more →
          </a>
        )}
      </div>
    </div>
  )
}

