'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FIELDS, FIELD_LABELS, type Field } from '@/lib/constants'
import { validateField } from '@/lib/validators'

export function FieldTabs() {
  const pathname = usePathname()
  
  // Extract field from pathname
  const pathSegments = pathname.split('/').filter(Boolean)
  const currentField = pathSegments.length > 0 && validateField(pathSegments[0])
    ? pathSegments[0]
    : pathSegments.length === 0 ? 'all' : 'research' // Default to 'all' for home, 'research' for invalid

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          <Link
            href="/"
            className={`px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
              currentField === 'all'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            }`}
          >
            All
          </Link>
          {FIELDS.map((field) => {
            const isActive = currentField === field
            return (
              <Link
                key={field}
                href={`/${field}`}
                className={`px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                {FIELD_LABELS[field]}
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}

