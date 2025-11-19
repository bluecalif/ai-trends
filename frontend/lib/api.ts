/**
 * API client for backend API.
 * 
 * Uses axios for HTTP requests with snake_case query parameters
 * to match backend API expectations.
 */

import axios, { AxiosInstance } from 'axios'
import type {
  ItemListResponse,
  ItemResponse,
  PersonResponse,
  PersonDetailResponse,
  BookmarkResponse,
  BookmarkCreate,
  BookmarkUpdate,
  SourceResponse,
  SourceCreate,
  SourceUpdate,
  WatchRuleResponse,
  WatchRuleCreate,
  WatchRuleUpdate,
  GroupsListResponse,
  GroupItem,
  ConstantsResponse,
  CustomTagsResponse,
} from './types'
import type { Field, CustomTag } from './constants'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API methods
export const api = {
  // Items
  getItems: async (filters?: {
    field?: Field
    custom_tag?: CustomTag
    date_from?: string // YYYY-MM-DD
    date_to?: string // YYYY-MM-DD
    source_id?: number
    page?: number
    page_size?: number
    order_by?: 'published_at' | 'created_at'
    order_desc?: boolean
  }): Promise<ItemListResponse> => {
    const { data } = await apiClient.get<ItemListResponse>('/api/items', {
      params: filters, // axios automatically converts to snake_case
    })
    return data
  },

  getItem: async (itemId: number): Promise<ItemResponse> => {
    const { data } = await apiClient.get<ItemResponse>(`/api/items/${itemId}`)
    return data
  },

  // Groups
  getGroups: async (params: {
    since: string // YYYY-MM-DD
    kind?: 'new' | 'incremental'
    page?: number
    page_size?: number
  }): Promise<GroupsListResponse> => {
    const { data } = await apiClient.get<GroupsListResponse>('/api/groups', {
      params,
    })
    return data
  },

  getItemGroup: async (dupGroupId: number): Promise<ItemResponse[]> => {
    const { data } = await apiClient.get<ItemResponse[]>(
      `/api/items/group/${dupGroupId}`
    )
    return data
  },

  // Persons
  getPersons: async (): Promise<PersonResponse[]> => {
    const { data } = await apiClient.get<PersonResponse[]>('/api/persons')
    return data
  },

  getPerson: async (
    personId: number,
    includeTimeline: boolean = true,
    includeGraph: boolean = true
  ): Promise<PersonDetailResponse> => {
    const { data } = await apiClient.get<PersonDetailResponse>(
      `/api/persons/${personId}`,
      {
        params: {
          include_timeline: includeTimeline,
          include_graph: includeGraph,
        },
      }
    )
    return data
  },

  createPerson: async (personData: {
    name: string
    bio?: string | null
  }): Promise<PersonResponse> => {
    const { data } = await apiClient.post<PersonResponse>(
      '/api/persons',
      personData
    )
    return data
  },

  // Bookmarks
  getBookmarks: async (tag?: string): Promise<BookmarkResponse[]> => {
    const { data } = await apiClient.get<BookmarkResponse[]>('/api/bookmarks', {
      params: tag ? { tag } : undefined,
    })
    return data
  },

  createBookmark: async (
    bookmarkData: BookmarkCreate
  ): Promise<BookmarkResponse> => {
    const { data } = await apiClient.post<BookmarkResponse>(
      '/api/bookmarks',
      bookmarkData
    )
    return data
  },

  updateBookmark: async (
    bookmarkId: number,
    bookmarkData: BookmarkUpdate
  ): Promise<BookmarkResponse> => {
    const { data } = await apiClient.put<BookmarkResponse>(
      `/api/bookmarks/${bookmarkId}`,
      bookmarkData
    )
    return data
  },

  deleteBookmark: async (bookmarkId: number): Promise<void> => {
    await apiClient.delete(`/api/bookmarks/${bookmarkId}`)
  },

  // Sources
  getSources: async (isActive?: boolean): Promise<SourceResponse[]> => {
    const { data } = await apiClient.get<SourceResponse[]>('/api/sources', {
      params: isActive !== undefined ? { is_active: isActive } : undefined,
    })
    return data
  },

  createSource: async (sourceData: SourceCreate): Promise<SourceResponse> => {
    const { data } = await apiClient.post<SourceResponse>(
      '/api/sources',
      sourceData
    )
    return data
  },

  updateSource: async (
    sourceId: number,
    sourceData: SourceUpdate
  ): Promise<SourceResponse> => {
    const { data } = await apiClient.put<SourceResponse>(
      `/api/sources/${sourceId}`,
      sourceData
    )
    return data
  },

  deleteSource: async (sourceId: number): Promise<void> => {
    await apiClient.delete(`/api/sources/${sourceId}`)
  },

  // Watch Rules
  getWatchRules: async (personId?: number): Promise<WatchRuleResponse[]> => {
    const { data } = await apiClient.get<WatchRuleResponse[]>(
      '/api/watch-rules',
      {
        params: personId !== undefined ? { person_id: personId } : undefined,
      }
    )
    return data
  },

  createWatchRule: async (
    ruleData: WatchRuleCreate
  ): Promise<WatchRuleResponse> => {
    const { data } = await apiClient.post<WatchRuleResponse>(
      '/api/watch-rules',
      ruleData
    )
    return data
  },

  updateWatchRule: async (
    ruleId: number,
    ruleData: WatchRuleUpdate
  ): Promise<WatchRuleResponse> => {
    const { data } = await apiClient.patch<WatchRuleResponse>(
      `/api/watch-rules/${ruleId}`,
      ruleData
    )
    return data
  },

  deleteWatchRule: async (ruleId: number): Promise<void> => {
    await apiClient.delete(`/api/watch-rules/${ruleId}`)
  },

  // Constants
  getConstants: async (): Promise<{
    fields: ConstantsResponse
    customTags: CustomTagsResponse
  }> => {
    const [fieldsRes, tagsRes] = await Promise.all([
      apiClient.get<ConstantsResponse>('/api/constants/fields'),
      apiClient.get<CustomTagsResponse>('/api/constants/custom-tags'),
    ])
    return {
      fields: fieldsRes.data,
      customTags: tagsRes.data,
    }
  },
}

export default api

