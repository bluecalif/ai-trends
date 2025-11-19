'use client'

import { useState } from 'react'
import { SourcesSection } from '@/components/SourcesSection'
import { WatchRulesSection } from '@/components/WatchRulesSection'

type TabType = 'sources' | 'watch-rules'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('sources')

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('sources')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'sources'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            RSS Sources
          </button>
          <button
            onClick={() => setActiveTab('watch-rules')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'watch-rules'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Watch Rules
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'sources' && <SourcesSection />}
      {activeTab === 'watch-rules' && <WatchRulesSection />}
    </div>
  )
}

