'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { DebugLogger } from './debug'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () => {
      DebugLogger.step(2, 'Creating QueryClient')
      return       new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
            retry: 1, // Reduce retries for faster error detection
          },
        },
      })
    }
  )

  useEffect(() => {
    DebugLogger.step(2, 'Providers Mounted')
    DebugLogger.env()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

