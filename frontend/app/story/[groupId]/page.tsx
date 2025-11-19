'use client'

import { use, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { TimelineCard } from '@/components/TimelineCard'
import Link from 'next/link'

interface StoryPageProps {
  params: Promise<{ groupId: string }>
}

function StoryPageContent({ groupId }: { groupId: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['itemGroup', groupId],
    queryFn: () => api.getItemGroup(groupId),
  })

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading timeline...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Error loading timeline</p>
          <p className="text-red-600 text-sm mt-1">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500 text-lg">No items found in this story</p>
          <Link
            href="/"
            className="mt-4 inline-block text-blue-600 hover:text-blue-800"
          >
            ← Back to home
          </Link>
        </div>
      </div>
    )
  }

  // Find the first item (earliest published_at) as the initial report
  const firstItem = data[0]
  const otherItems = data.slice(1)

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link
          href="/"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          ← Back to home
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 mt-4">
          Story Timeline
        </h1>
        <p className="text-gray-600 text-sm mt-2">
          {data.length} {data.length === 1 ? 'item' : 'items'} in this story
        </p>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>

        <div className="space-y-6">
          {/* First item (initial report) */}
          <div className="relative pl-20">
            <div className="absolute left-6 w-4 h-4 bg-blue-600 rounded-full border-4 border-white shadow-md"></div>
            <TimelineCard item={firstItem} isFirst={true} />
          </div>

          {/* Other items (follow-up reports) */}
          {otherItems.map((item, index) => (
            <div key={item.id} className="relative pl-20">
              <div className="absolute left-6 w-4 h-4 bg-gray-400 rounded-full border-4 border-white shadow-md"></div>
              <TimelineCard item={item} isFirst={false} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function StoryPage({ params }: StoryPageProps) {
  const resolvedParams = use(params)
  const groupId = parseInt(resolvedParams.groupId, 10)

  if (isNaN(groupId)) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Invalid story ID</p>
          <Link href="/" className="mt-2 inline-block text-blue-600 hover:text-blue-800">
            ← Back to home
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
      <StoryPageContent groupId={groupId} />
    </Suspense>
  )
}

