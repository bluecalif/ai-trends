'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { FieldTabs } from '@/components/FieldTabs'
import { ItemCard } from '@/components/ItemCard'
import { TagFilter } from '@/components/TagFilter'
import { Pagination } from '@/components/Pagination'
import type { CustomTag } from '@/lib/constants'

function HomePageContent() {
  const searchParams = useSearchParams()

  // Get query parameters
  const page = parseInt(searchParams.get('page') || '1', 10)
  const pageSize = parseInt(searchParams.get('page_size') || '20', 10)
  const customTag = searchParams.get('custom_tag') as CustomTag | null
  const dateFrom = searchParams.get('date_from') || undefined
  const dateTo = searchParams.get('date_to') || undefined

  // Fetch items (no field filter for "All")
  const { data, isLoading, error } = useQuery({
    queryKey: ['items', 'all', page, pageSize, customTag, dateFrom, dateTo],
    queryFn: () => {
      console.log('[HomePage] Fetching items...')
      return api.getItems({
        custom_tag: customTag || undefined,
        date_from: dateFrom,
        date_to: dateTo,
        page,
        page_size: pageSize,
        order_by: 'published_at',
        order_desc: true,
      })
    },
    onError: (err) => {
      console.error('[HomePage] Query error:', err)
    },
  })

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <FieldTabs />
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading items...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <FieldTabs />
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">Error loading items</p>
          <p className="text-red-600 text-sm mt-1">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
        </div>
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <FieldTabs />
      
      <div className="mt-6">
        <TagFilter />
      </div>

      {data.items.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500 text-lg">No items found</p>
          <p className="text-gray-400 text-sm mt-2">
            Try adjusting your filters or check back later.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
          <Pagination
            total={data.total}
            page={data.page}
            pageSize={data.page_size}
          />
        </>
      )}
    </div>
  )
}

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <FieldTabs />
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading...</span>
          </div>
        </div>
      }
    >
      <HomePageContent />
    </Suspense>
  )
}
