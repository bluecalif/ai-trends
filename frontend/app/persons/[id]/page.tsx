'use client'

import { use, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { formatDistanceToNow, format } from 'date-fns'
import Link from 'next/link'
import type { PersonTimelineEventResponse } from '@/lib/types'

interface PersonDetailPageProps {
  params: Promise<{ id: string }>
}

function PersonDetailContent({ personId }: { personId: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['person', personId],
    queryFn: () => api.getPerson(personId, true, true),
  })

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading person details...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Error loading person</p>
          <p className="text-red-600 text-sm mt-1">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
          <Link
            href="/persons"
            className="mt-4 inline-block text-blue-600 hover:text-blue-800"
          >
            ← Back to persons
          </Link>
        </div>
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link
          href="/persons"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          ← Back to persons
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-4">{data.name}</h1>
        {data.bio && (
          <p className="text-gray-600 mt-2">{data.bio}</p>
        )}
      </div>

      {/* Timeline Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline</h2>
        {data.timeline.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">No timeline events yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {data.timeline.map((event) => (
              <TimelineEventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>

      {/* Relationship Graph Section (placeholder) */}
      {data.relationship_graph && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Relationship Graph
          </h2>
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">
              Relationship graph visualization (coming soon)
            </p>
            <p className="text-gray-400 text-sm mt-2">
              This feature will be implemented in Phase 3
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

function TimelineEventCard({ event }: { event: PersonTimelineEventResponse }) {
  const timeAgo = formatDistanceToNow(new Date(event.created_at), {
    addSuffix: true,
  })
  const formattedDate = format(new Date(event.created_at), 'MMM d, yyyy HH:mm')

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {event.event_type}
          </span>
        </div>
        <div className="text-sm text-gray-500">
          <span className="font-medium">{formattedDate}</span>
          <span className="ml-2">({timeAgo})</span>
        </div>
      </div>

      {event.description && (
        <p className="text-gray-600 mb-3 text-sm">{event.description}</p>
      )}

      {event.item_title && (
        <div className="mt-3">
          <a
            href={event.item_link || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            {event.item_title} →
          </a>
        </div>
      )}
    </div>
  )
}

export default function PersonDetailPage({ params }: PersonDetailPageProps) {
  const resolvedParams = use(params)
  const personId = parseInt(resolvedParams.id, 10)

  if (isNaN(personId)) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Invalid person ID</p>
          <Link href="/persons" className="mt-2 inline-block text-blue-600 hover:text-blue-800">
            ← Back to persons
          </Link>
        </div>
      </div>
    )
  }

  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading...</span>
          </div>
        </div>
      }
    >
      <PersonDetailContent personId={personId} />
    </Suspense>
  )
}

