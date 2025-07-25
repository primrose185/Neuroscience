export interface SearchableContent {
  id: string
  title: string
  content: string
  excerpt: string
  path: string
  tags: string[]
  category: string
  type: 'page' | 'section'
  metadata?: {
    chapter?: string
    difficulty?: 'beginner' | 'intermediate' | 'advanced'
    estimatedReadTime?: number
  }
}

export interface SearchResult {
  item: SearchableContent
  score: number
  matches?: SearchMatch[]
}

export interface SearchMatch {
  key: string
  value: string
  indices: number[][]
}

export interface SearchOptions {
  query: string
  tags?: string[]
  category?: string
  type?: 'page' | 'section'
  maxResults?: number
}

export interface SearchState {
  query: string
  results: SearchResult[]
  isLoading: boolean
  selectedTags: string[]
  selectedCategory: string
  totalResults: number
}

export interface SearchFilters {
  tags: string[]
  categories: string[]
  types: ('page' | 'section')[]
}