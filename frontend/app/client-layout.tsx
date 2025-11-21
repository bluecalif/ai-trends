'use client'

import { useEffect } from "react";
import { Providers } from "@/lib/providers";
import { Navigation } from "@/components/Navigation";
import { ErrorBoundary } from "@/lib/error-boundary";
import { DebugLogger } from "@/lib/debug";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    DebugLogger.step(1, 'RootLayout Body Rendered')
  }, [])

  return (
    <ErrorBoundary>
      <Providers>
        <Navigation />
        <main className="min-h-screen">{children}</main>
      </Providers>
    </ErrorBoundary>
  );
}

