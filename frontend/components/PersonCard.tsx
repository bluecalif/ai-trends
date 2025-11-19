'use client'

import Link from 'next/link'
import type { PersonResponse } from '@/lib/types'

interface PersonCardProps {
  person: PersonResponse
}

export function PersonCard({ person }: PersonCardProps) {
  return (
    <Link href={`/persons/${person.id}`}>
      <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {person.name}
        </h3>

        {person.bio && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {person.bio}
          </p>
        )}

        <div className="flex items-center justify-end text-sm text-gray-500">
          <span className="text-blue-600 hover:text-blue-800 font-medium">
            View details →
          </span>
        </div>
      </div>
    </Link>
  )
}

