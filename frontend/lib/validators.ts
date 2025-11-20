/**
 * Runtime validation functions for API contract synchronization.
 * 
 * These functions validate user input and URL parameters to ensure
 * they match backend expectations.
 */

import { FIELDS, CUSTOM_TAGS, type Field, type CustomTag } from './constants'

/**
 * Validate if a string is a valid field.
 */
export function validateField(field: string): field is Field {
  return FIELDS.includes(field as Field)
}

/**
 * Validate if a string is a valid custom tag.
 */
export function validateCustomTag(tag: string): tag is CustomTag {
  return CUSTOM_TAGS.includes(tag as CustomTag)
}

/**
 * Get field from URL path.
 * Returns null if invalid.
 */
export function getFieldFromPath(path: string): Field | null {
  const field = path.split('/')[1]
  return validateField(field) ? field : null
}

/**
 * Validate ISO date string format (YYYY-MM-DD).
 */
export function validateDateString(dateString: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/
  if (!regex.test(dateString)) {
    return false
  }
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date.getTime())
}

