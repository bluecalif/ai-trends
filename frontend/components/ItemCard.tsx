'use client'

import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import type { ItemResponse } from '@/lib/types'

interface ItemCardProps {
  item: ItemResponse
  eventCount?: number
}

export function ItemCard({ item, eventCount }: ItemCardProps) {
  const timeAgo = formatDistanceToNow(new Date(item.published_at), {
    addSuffix: true,
  })

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
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
        <p className="text-gray-600 mb-3 line-clamp-2 text-sm">
          {item.summary_short}
        </p>
      )}

      <div className="flex flex-wrap gap-2 mb-3">
        {item.custom_tags.length > 0 ? (
          item.custom_tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded font-medium"
            >
              {tag}
            </span>
          ))
        ) : (
          <span className="text-xs text-gray-400">No tags</span>
        )}
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{timeAgo}</span>
        {item.dup_group_id && (
          <Link
            href={`/story/${item.dup_group_id}`}
            className="text-blue-600 hover:underline font-medium"
          >
            View story →
          </Link>
        )}
      </div>
    </div>
  )
}

