/**
 * Application constants synchronized with backend.
 * 
 * Option A (Recommended): Load from Constants API at runtime
 * Option B: Static constants (manual synchronization required)
 * 
 * Currently using Option B for initial setup.
 * TODO: Consider migrating to Option A for runtime synchronization.
 */

// Field categories (분야)
export const FIELDS = [
  'research',
  'industry',
  'infra',
  'policy',
  'funding',
] as const

export type Field = typeof FIELDS[number]

// Custom AI tags
export const CUSTOM_TAGS = [
  'agents',
  'world_models',
  'non_transformer',
  'neuro_symbolic',
  'foundational_models',
  'inference_infra',
] as const

export type CustomTag = typeof CUSTOM_TAGS[number]

// Field labels (한글 레이블)
export const FIELD_LABELS: Record<Field, string> = {
  research: 'Research',
  industry: 'Industry',
  infra: 'Infrastructure',
  policy: 'Policy & Regulation',
  funding: 'Funding & Deals',
}

// Custom tag labels (한글 레이블)
export const CUSTOM_TAG_LABELS: Record<CustomTag, string> = {
  agents: 'Agents',
  world_models: 'World Models',
  non_transformer: 'Non-Transformer',
  neuro_symbolic: 'Neuro-Symbolic',
  foundational_models: 'Foundational Models',
  inference_infra: 'Inference Infrastructure',
}

