/**
 * TypeScript type definitions synchronized with backend schemas.
 * 
 * These types must match the backend Pydantic schemas exactly:
 * - Field names: snake_case (not camelCase)
 * - Types: Date → string (ISO date string)
 * - Optional fields: match backend Optional fields
 * - Array types: List[str] → string[]
 */

// Item types
export interface ItemResponse {
  id: number
  source_id: number
  title: string
  summary_short: string | null
  link: string
  published_at: string // ISO date string
  author: string | null
  thumbnail_url: string | null
  field: string | null
  iptc_topics: string[]
  iab_categories: string[]
  custom_tags: string[]
  dup_group_id: number | null
  created_at: string // ISO date string
  updated_at: string // ISO date string
}

export interface ItemListResponse {
  items: ItemResponse[]
  total: number
  page: number
  page_size: number
}

// Person types
export interface PersonResponse {
  id: number
  name: string
  bio: string | null
  created_at: string // ISO date string
  updated_at: string // ISO date string
}

export interface PersonTimelineEventResponse {
  id: number
  person_id: number
  item_id: number
  event_type: string
  description: string | null
  created_at: string // ISO date string
  item_title: string | null
  item_link: string | null
  item_published_at: string | null // ISO date string
}

export interface PersonDetailResponse {
  id: number
  name: string
  bio: string | null
  created_at: string // ISO date string
  updated_at: string // ISO date string
  timeline: PersonTimelineEventResponse[]
  relationship_graph: Record<string, unknown> | null
}

// Bookmark types
export interface BookmarkResponse {
  id: number
  item_id: number
  title: string
  tags: string[]
  note: string | null
  created_at: string // ISO date string
  item_title: string | null
  item_link: string | null
  item_published_at: string | null // ISO date string
}

export interface BookmarkCreate {
  item_id?: number | null
  link?: string | null
  title: string
  tags: string[]
  note?: string | null
}

export interface BookmarkUpdate {
  title?: string | null
  tags?: string[] | null
  note?: string | null
}

// Source types
export interface SourceResponse {
  id: number
  title: string
  feed_url: string
  site_url: string | null
  category: string | null
  lang: string
  is_active: boolean
  created_at: string // ISO date string
  updated_at: string // ISO date string
}

export interface SourceCreate {
  title: string
  feed_url: string
  site_url?: string | null
  category?: string | null
  lang?: string
  is_active?: boolean
}

export interface SourceUpdate {
  title?: string | null
  feed_url?: string | null
  site_url?: string | null
  category?: string | null
  lang?: string | null
  is_active?: boolean | null
}

// WatchRule types
export interface WatchRuleResponse {
  id: number
  label: string
  include_rules: string[]
  exclude_rules: string[]
  required_keywords: string[]
  optional_keywords: string[]
  priority: number
  person_id: number | null
  created_at: string // ISO date string
  updated_at: string // ISO date string
}

export interface WatchRuleCreate {
  label: string
  include_rules?: string[]
  exclude_rules?: string[]
  required_keywords?: string[]
  optional_keywords?: string[]
  priority?: number
  person_id?: number | null
}

export interface WatchRuleUpdate {
  label?: string | null
  include_rules?: string[] | null
  exclude_rules?: string[] | null
  required_keywords?: string[] | null
  optional_keywords?: string[] | null
  priority?: number | null
  person_id?: number | null
}

// Group types
export interface GroupItem {
  id: number
  title: string
  link: string
  published_at: string // ISO date string
  summary_short: string | null
}

export interface GroupRepresentative {
  id: number | null
  title: string | null
  link: string | null
  published_at: string | null // ISO date string
  summary_short: string | null
}

export interface GroupResponse {
  dup_group_id: number
  first_seen_at: string // ISO date string
  last_updated_at: string // ISO date string
  member_count: number
  representative: GroupRepresentative
}

export interface GroupsListResponse {
  total: number
  page: number
  page_size: number
  groups: GroupResponse[]
}

// Constants types
export interface ConstantsResponse {
  fields: string[]
}

export interface CustomTagsResponse {
  tags: string[]
}

