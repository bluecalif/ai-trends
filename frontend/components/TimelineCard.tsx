'use client'

import { formatDistanceToNow, format } from 'date-fns'
import type { ItemResponse } from '@/lib/types'

interface TimelineCardProps {
  item: ItemResponse
  isFirst: boolean
}

export function TimelineCard({ item, isFirst }: TimelineCardProps) {
  const timeAgo = formatDistanceToNow(new Date(item.published_at), {
    addSuffix: true,
  })
  const formattedDate = format(new Date(item.published_at), 'MMM d, yyyy HH:mm')

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      {isFirst && (
        <div className="mb-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Initial Report
          </span>
        </div>
      )}

      <h3 className="text-lg font-semibold mb-2">
        <a
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-900 hover:text-blue-600 hover:underline"
        >
          {item.title}
        </a>
      </h3>

      {item.summary_short && (
        <p className="text-gray-600 mb-3 text-sm line-clamp-3">
          {item.summary_short}
        </p>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div>
          <span className="font-medium">{formattedDate}</span>
          <span className="ml-2">({timeAgo})</span>
        </div>
        <a
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          Read more →
        </a>
      </div>
    </div>
  )
}

