'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  WatchRuleResponse,
  WatchRuleCreate,
  WatchRuleUpdate,
} from '@/lib/types'
import type { PersonResponse } from '@/lib/types'

export function WatchRulesSection() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<WatchRuleResponse | null>(null)
  const queryClient = useQueryClient()

  const { data: rules, isLoading, error } = useQuery({
    queryKey: ['watch-rules'],
    queryFn: () => api.getWatchRules(),
  })

  const { data: persons } = useQuery({
    queryKey: ['persons'],
    queryFn: () => api.getPersons(),
  })

  const createMutation = useMutation({
    mutationFn: (ruleData: WatchRuleCreate) => api.createWatchRule(ruleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watch-rules'] })
      setIsAddModalOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: WatchRuleUpdate }) =>
      api.updateWatchRule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watch-rules'] })
      setEditingRule(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteWatchRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watch-rules'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading watch rules...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-medium">Error loading watch rules</p>
        <p className="text-red-600 text-sm mt-1">
          {error instanceof Error ? error.message : 'Unknown error occurred'}
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Watch Rules</h2>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add Rule
        </button>
      </div>

      {rules && rules.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500 text-lg">No watch rules found</p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Add your first rule
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {rules?.map((rule) => (
            <div
              key={rule.id}
              className="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {rule.label}
                  </h3>
                  {rule.person_id && (
                    <p className="text-sm text-gray-500 mt-1">
                      Person ID: {rule.person_id}
                    </p>
                  )}
                  <p className="text-sm text-gray-500">Priority: {rule.priority}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingRule(rule)}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`Are you sure you want to delete "${rule.label}"?`)) {
                        deleteMutation.mutate(rule.id)
                      }
                    }}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-gray-700 mb-1">Required Keywords:</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.required_keywords.length > 0 ? (
                      rule.required_keywords.map((keyword) => (
                        <span
                          key={keyword}
                          className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs"
                        >
                          {keyword}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400">None</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="font-medium text-gray-700 mb-1">Optional Keywords:</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.optional_keywords.length > 0 ? (
                      rule.optional_keywords.map((keyword) => (
                        <span
                          key={keyword}
                          className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                        >
                          {keyword}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400">None</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="font-medium text-gray-700 mb-1">Include Rules:</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.include_rules.length > 0 ? (
                      rule.include_rules.map((rule) => (
                        <span
                          key={rule}
                          className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs"
                        >
                          {rule}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400">None</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="font-medium text-gray-700 mb-1">Exclude Rules:</p>
                  <div className="flex flex-wrap gap-1">
                    {rule.exclude_rules.length > 0 ? (
                      rule.exclude_rules.map((rule) => (
                        <span
                          key={rule}
                          className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs"
                        >
                          {rule}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400">None</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isAddModalOpen && (
        <WatchRuleModal
          persons={persons || []}
          onClose={() => setIsAddModalOpen(false)}
          onSave={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
          error={createMutation.error}
        />
      )}

      {editingRule && (
        <WatchRuleModal
          rule={editingRule}
          persons={persons || []}
          onClose={() => setEditingRule(null)}
          onSave={(data) =>
            updateMutation.mutate({ id: editingRule.id, data })
          }
          isLoading={updateMutation.isPending}
          error={updateMutation.error}
        />
      )}
    </div>
  )
}

interface WatchRuleModalProps {
  rule?: WatchRuleResponse
  persons: PersonResponse[]
  onClose: () => void
  onSave: (data: WatchRuleCreate | WatchRuleUpdate) => void
  isLoading: boolean
  error: unknown
}

function WatchRuleModal({
  rule,
  persons,
  onClose,
  onSave,
  isLoading,
  error,
}: WatchRuleModalProps) {
  // Find person name from person_id
  const getPersonName = (id: number | null) => {
    if (!id) return ''
    const person = persons.find((p) => p.id === id)
    return person?.name || ''
  }

  const [personId, setPersonId] = useState<number | null>(rule?.person_id || null)
  const [label, setLabel] = useState(rule?.label || getPersonName(rule?.person_id || null))
  const [priority, setPriority] = useState(rule?.priority || 0)
  const [requiredKeywords, setRequiredKeywords] = useState<string[]>(
    rule?.required_keywords || []
  )
  const [optionalKeywords, setOptionalKeywords] = useState<string[]>(
    rule?.optional_keywords || []
  )
  const [includeRules, setIncludeRules] = useState<string[]>(
    rule?.include_rules || []
  )
  const [excludeRules, setExcludeRules] = useState<string[]>(
    rule?.exclude_rules || []
  )
  const [jsonMode, setJsonMode] = useState(false)
  const [jsonText, setJsonText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (jsonMode) {
      try {
        const parsed = JSON.parse(jsonText)
        // If person_id is set, use person name as label
        let finalLabel = parsed.label
        if (parsed.person_id) {
          const selectedPerson = persons.find((p) => p.id === parsed.person_id)
          if (selectedPerson) {
            finalLabel = selectedPerson.name
          }
        }
        
        if (rule) {
          onSave({
            label: finalLabel || null,
            required_keywords: parsed.required_keywords || null,
            optional_keywords: parsed.optional_keywords || null,
            include_rules: parsed.include_rules || null,
            exclude_rules: parsed.exclude_rules || null,
            priority: parsed.priority || null,
            person_id: parsed.person_id || null,
          })
        } else {
          onSave({
            label: finalLabel,
            required_keywords: parsed.required_keywords || [],
            optional_keywords: parsed.optional_keywords || [],
            include_rules: parsed.include_rules || [],
            exclude_rules: parsed.exclude_rules || [],
            priority: parsed.priority || 0,
            person_id: parsed.person_id || null,
          })
        }
      } catch (err) {
        alert('Invalid JSON format')
        return
      }
    } else {
      // Ensure label is set from person name if person is selected
      const finalLabel = personId ? getPersonName(personId) : label
      
      if (rule) {
        onSave({
          label: finalLabel || null,
          required_keywords: requiredKeywords.length > 0 ? requiredKeywords : null,
          optional_keywords: optionalKeywords.length > 0 ? optionalKeywords : null,
          include_rules: includeRules.length > 0 ? includeRules : null,
          exclude_rules: excludeRules.length > 0 ? excludeRules : null,
          priority: priority || null,
          person_id: personId || null,
        })
      } else {
        onSave({
          label: finalLabel,
          required_keywords: requiredKeywords,
          optional_keywords: optionalKeywords,
          include_rules: includeRules,
          exclude_rules: excludeRules,
          priority,
          person_id: personId || null,
        })
      }
    }
  }

  const addKeyword = (
    keyword: string,
    setter: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    const trimmed = keyword.trim()
    if (trimmed && !requiredKeywords.includes(trimmed) && !optionalKeywords.includes(trimmed)) {
      setter((prev) => [...prev, trimmed])
    }
  }

  const removeKeyword = (
    keyword: string,
    setter: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    setter((prev) => prev.filter((k) => k !== keyword))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 overflow-y-auto">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 my-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {rule ? 'Edit Watch Rule' : 'Add Watch Rule'}
        </h2>

        <div className="mb-4">
          <button
            type="button"
            onClick={() => setJsonMode(!jsonMode)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {jsonMode ? 'Switch to Form Mode' : 'Switch to JSON Mode'}
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {jsonMode ? (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                JSON
              </label>
              <textarea
                value={jsonText || JSON.stringify({
                  label: rule?.label || '',
                  required_keywords: rule?.required_keywords || [],
                  optional_keywords: rule?.optional_keywords || [],
                  include_rules: rule?.include_rules || [],
                  exclude_rules: rule?.exclude_rules || [],
                  priority: rule?.priority || 0,
                  person_id: rule?.person_id || null,
                }, null, 2)}
                onChange={(e) => setJsonText(e.target.value)}
                rows={15}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
          ) : (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Person (Label) *
                </label>
                <select
                  value={personId || ''}
                  onChange={(e) => {
                    const selectedPersonId = e.target.value ? parseInt(e.target.value) : null
                    setPersonId(selectedPersonId)
                    // Auto-set label to person name
                    if (selectedPersonId) {
                      const selectedPerson = persons.find((p) => p.id === selectedPersonId)
                      setLabel(selectedPerson?.name || '')
                    } else {
                      setLabel('')
                    }
                  }}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a person...</option>
                  {persons.map((person) => (
                    <option key={person.id} value={person.id}>
                      {person.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  The person's name will be used as the label
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <input
                  type="number"
                  value={priority}
                  onChange={(e) => setPriority(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <KeywordArrayInput
                label="Required Keywords"
                keywords={requiredKeywords}
                onAdd={(keyword) => addKeyword(keyword, setRequiredKeywords)}
                onRemove={(keyword) => removeKeyword(keyword, setRequiredKeywords)}
              />

              <KeywordArrayInput
                label="Optional Keywords"
                keywords={optionalKeywords}
                onAdd={(keyword) => addKeyword(keyword, setOptionalKeywords)}
                onRemove={(keyword) => removeKeyword(keyword, setOptionalKeywords)}
              />

              <KeywordArrayInput
                label="Include Rules"
                keywords={includeRules}
                onAdd={(keyword) => addKeyword(keyword, setIncludeRules)}
                onRemove={(keyword) => removeKeyword(keyword, setIncludeRules)}
              />

              <KeywordArrayInput
                label="Exclude Rules"
                keywords={excludeRules}
                onAdd={(keyword) => addKeyword(keyword, setExcludeRules)}
                onRemove={(keyword) => removeKeyword(keyword, setExcludeRules)}
              />
            </>
          )}

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">
                {error instanceof Error ? error.message : 'Failed to save rule'}
              </p>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface KeywordArrayInputProps {
  label: string
  keywords: string[]
  onAdd: (keyword: string) => void
  onRemove: (keyword: string) => void
}

function KeywordArrayInput({
  label,
  keywords,
  onAdd,
  onRemove,
}: KeywordArrayInputProps) {
  const [input, setInput] = useState('')

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              onAdd(input)
              setInput('')
            }
          }}
          placeholder="Add keyword..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="button"
          onClick={() => {
            onAdd(input)
            setInput('')
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {keywords.map((keyword) => (
          <span
            key={keyword}
            className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
          >
            {keyword}
            <button
              type="button"
              onClick={() => onRemove(keyword)}
              className="ml-2 text-blue-600 hover:text-blue-800"
            >
              ×
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}

