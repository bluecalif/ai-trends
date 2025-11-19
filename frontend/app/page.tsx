'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export default function HomePage() {
  // Test API connection - Constants API
  const { data: constantsData, isLoading: constantsLoading, error: constantsError } = useQuery({
    queryKey: ['constants'],
    queryFn: async () => {
      const result = await api.getConstants()
      return result
    },
    retry: 1, // Only retry once for testing
  })

  // Test items API
  const { data: itemsData, isLoading: itemsLoading, error: itemsError } = useQuery({
    queryKey: ['items', 'test'],
    queryFn: () => api.getItems({ page: 1, page_size: 5 }),
    enabled: !!constantsData, // Only fetch after constants are loaded
    retry: 1,
  })

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">AI Trend Monitor - UX Test Page</h1>
        
        {/* API Configuration Info */}
        <section className="mb-8 p-4 border rounded-lg bg-white">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          <p className="text-sm text-gray-600">
            Base URL: <code className="bg-gray-100 px-2 py-1 rounded">{process.env.NEXT_PUBLIC_API_URL || 'Not set (default: http://localhost:8000)'}</code>
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Make sure the backend server is running on port 8000
          </p>
        </section>

        {/* Constants API Test */}
        <section className="mb-8 p-4 border rounded-lg bg-white">
          <h2 className="text-xl font-semibold mb-4">Constants API Test</h2>
          {constantsLoading && (
            <div className="flex items-center gap-2 text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
              <span>Loading constants...</span>
            </div>
          )}
          {constantsError && (
            <div className="text-red-600 bg-red-50 p-4 rounded">
              <p className="font-medium mb-2">Error loading constants:</p>
              <pre className="text-sm whitespace-pre-wrap">
                {constantsError instanceof Error ? constantsError.message : String(constantsError)}
              </pre>
              <p className="text-xs mt-2 text-red-500">
                Make sure the backend server is running: <code>cd backend && poetry run uvicorn backend.app.main:app --reload</code>
              </p>
            </div>
          )}
          {constantsData && !constantsLoading && (
            <div className="space-y-4">
              <div>
                <p className="font-medium mb-2">Fields ({constantsData.fields.fields.length}):</p>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {constantsData.fields.fields.map((field) => (
                    <li key={field} className="font-mono">{field}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-medium mb-2">Custom Tags ({constantsData.customTags.tags.length}):</p>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {constantsData.customTags.tags.map((tag) => (
                    <li key={tag} className="font-mono">{tag}</li>
                  ))}
                </ul>
              </div>
              <div className="mt-4 p-3 bg-green-50 text-green-800 rounded text-sm">
                ✓ Constants API connection successful!
              </div>
            </div>
          )}
        </section>

        {/* Items API Test */}
        <section className="mb-8 p-4 border rounded-lg bg-white">
          <h2 className="text-xl font-semibold mb-4">Items API Test</h2>
          {itemsLoading && (
            <div className="flex items-center gap-2 text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
              <span>Loading items...</span>
            </div>
          )}
          {itemsError && (
            <div className="text-red-600 bg-red-50 p-4 rounded">
              <p className="font-medium mb-2">Error loading items:</p>
              <pre className="text-sm whitespace-pre-wrap">
                {itemsError instanceof Error ? itemsError.message : String(itemsError)}
              </pre>
            </div>
          )}
          {itemsData && !itemsLoading && (
            <div className="space-y-4">
              <div className="text-sm text-gray-600 p-3 bg-blue-50 rounded">
                Total: <strong>{itemsData.total}</strong> items | 
                Page: <strong>{itemsData.page}</strong> / <strong>{Math.ceil(itemsData.total / itemsData.page_size)}</strong> | 
                Page Size: <strong>{itemsData.page_size}</strong>
              </div>
              {itemsData.items.length === 0 ? (
                <p className="text-gray-500 text-sm">No items found in the database.</p>
              ) : (
                <div className="space-y-4">
                  {itemsData.items.map((item) => (
                    <div key={item.id} className="p-4 bg-gray-50 rounded border border-gray-200 hover:border-gray-300 transition-colors">
                      <h3 className="font-medium text-lg mb-2">{item.title}</h3>
                      {item.summary_short && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.summary_short}</p>
                      )}
                      <div className="flex gap-2 flex-wrap mb-2">
                        {item.custom_tags.length > 0 ? (
                          item.custom_tags.map((tag) => (
                            <span key={tag} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {tag}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-gray-400">No tags</span>
                        )}
                      </div>
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>ID: {item.id}</span>
                        <span>{new Date(item.published_at).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-4 p-3 bg-green-50 text-green-800 rounded text-sm">
                ✓ Items API connection successful!
              </div>
            </div>
          )}
        </section>

        {/* Responsive Design Test */}
        <section className="p-4 border rounded-lg bg-white">
          <h2 className="text-lg font-semibold mb-2">Responsive Design</h2>
          <p className="text-sm text-gray-600">
            This page should be responsive. Try resizing your browser window or viewing on mobile.
          </p>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-3 bg-blue-100 rounded text-center text-sm">Mobile (1 col)</div>
            <div className="p-3 bg-green-100 rounded text-center text-sm hidden md:block">Tablet (2 cols)</div>
            <div className="p-3 bg-purple-100 rounded text-center text-sm hidden lg:block">Desktop (3 cols)</div>
          </div>
        </section>
      </div>
    </div>
  )
}
