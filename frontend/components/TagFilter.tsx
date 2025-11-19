'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { CUSTOM_TAGS, CUSTOM_TAG_LABELS, type CustomTag } from '@/lib/constants'

export function TagFilter() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const selectedTags = searchParams.getAll('custom_tag') as CustomTag[]

  const toggleTag = (tag: CustomTag) => {
    const params = new URLSearchParams(searchParams.toString())
    const currentTags = params.getAll('custom_tag') as CustomTag[]
    
    if (currentTags.includes(tag)) {
      // Remove tag
      const newTags = currentTags.filter((t) => t !== tag)
      params.delete('custom_tag')
      newTags.forEach((t) => params.append('custom_tag', t))
    } else {
      // Add tag
      params.append('custom_tag', tag)
    }
    
    // Reset to page 1 when filter changes
    params.set('page', '1')
    router.push(`?${params.toString()}`)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Filter by Tags</h3>
      <div className="flex flex-wrap gap-2">
        {CUSTOM_TAGS.map((tag) => {
          const isSelected = selectedTags.includes(tag)
          return (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-3 py-1 text-sm font-medium rounded-full transition-colors ${
                isSelected
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {CUSTOM_TAG_LABELS[tag]}
            </button>
          )
        })}
      </div>
      {selectedTags.length > 0 && (
        <button
          onClick={() => {
            const params = new URLSearchParams(searchParams.toString())
            params.delete('custom_tag')
            params.set('page', '1')
            router.push(`?${params.toString()}`)
          }}
          className="mt-3 text-sm text-blue-600 hover:text-blue-800"
        >
          Clear filters
        </button>
      )}
    </div>
  )
}

