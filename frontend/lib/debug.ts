/**
 * Centralized debugging utility
 * Provides step-by-step logging for troubleshooting
 */

const DEBUG_PREFIX = '[DEBUG]'

export const DebugLogger = {
  step: (stepNumber: number, stepName: string, data?: any) => {
    const message = `[STEP ${stepNumber}] ${stepName}`
    console.log(message, data || '')
    if (typeof window !== 'undefined') {
      // Also log to window for easy access
      ;(window as any).__debugLogs = (window as any).__debugLogs || []
      ;(window as any).__debugLogs.push({
        step: stepNumber,
        name: stepName,
        data,
        timestamp: new Date().toISOString(),
      })
    }
  },

  env: () => {
    if (typeof window === 'undefined') return
    
    console.group(`${DEBUG_PREFIX} Environment Variables`)
    console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
    console.log('NODE_ENV:', process.env.NODE_ENV)
    console.log('All NEXT_PUBLIC_* vars:', Object.keys(process.env).filter(k => k.startsWith('NEXT_PUBLIC_')))
    console.groupEnd()
  },

  api: (action: string, data?: any) => {
    console.log(`${DEBUG_PREFIX} [API] ${action}`, data || '')
  },

  query: (action: string, data?: any) => {
    console.log(`${DEBUG_PREFIX} [Query] ${action}`, data || '')
  },

  error: (context: string, error: any) => {
    console.error(`${DEBUG_PREFIX} [ERROR] ${context}:`, error)
    if (error?.stack) {
      console.error('Stack trace:', error.stack)
    }
  },
}

// Global error handlers
if (typeof window !== 'undefined') {
  // Unhandled errors
  window.addEventListener('error', (event) => {
    DebugLogger.error('Global Error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error,
    })
  })

  // Unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    DebugLogger.error('Unhandled Promise Rejection', {
      reason: event.reason,
      promise: event.promise,
    })
  })

  // Log initial load
  DebugLogger.step(0, 'Page Load', {
    url: window.location.href,
    userAgent: navigator.userAgent,
  })
}

