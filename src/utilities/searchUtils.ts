import Fuse from 'fuse.js'
import type { SearchableContent, SearchResult, SearchOptions, SearchFilters } from '../types/search'

// Mock data for existing content - this will be replaced with actual content later
const mockContent: SearchableContent[] = [
  {
    id: 'topic1-page1',
    title: 'Basic Probability',
    content: 'Randomness is all around us. Probability theory is the mathematical framework that allows us to analyze chance events in a logically sound manner. The probability of an event is a number indicating how likely that event will occur.',
    excerpt: 'Introduction to the basic concepts of probability theory and chance events.',
    path: '/topic1/page1',
    tags: ['probability', 'mathematics', 'statistics', 'theory'],
    category: 'Mathematics',
    type: 'page',
    metadata: {
      chapter: 'Chapter 1',
      difficulty: 'beginner',
      estimatedReadTime: 5
    }
  },
  {
    id: 'topic1-page2',
    title: 'Sub-topic 1.2',
    content: 'Advanced concepts in probability theory including conditional probability and Bayes theorem.',
    excerpt: 'Advanced probability concepts for deeper understanding.',
    path: '/topic1/page2',
    tags: ['probability', 'conditional', 'bayes', 'advanced'],
    category: 'Mathematics',
    type: 'page',
    metadata: {
      chapter: 'Chapter 1',
      difficulty: 'intermediate',
      estimatedReadTime: 8
    }
  },
  {
    id: 'topic2-page1',
    title: 'Topic 2',
    content: 'Neuroscience fundamentals and brain structure analysis.',
    excerpt: 'Understanding the basic structure and function of the brain.',
    path: '/topic2/page1',
    tags: ['neuroscience', 'brain', 'anatomy', 'structure'],
    category: 'Neuroscience',
    type: 'page',
    metadata: {
      chapter: 'Chapter 2',
      difficulty: 'beginner',
      estimatedReadTime: 10
    }
  },
  {
    id: 'topic3',
    title: 'Topic 3',
    content: 'Advanced neuroscience topics including neural networks and synaptic transmission.',
    excerpt: 'Deep dive into neural network behavior and synaptic mechanisms.',
    path: '/topic3',
    tags: ['neuroscience', 'neural-networks', 'synapses', 'transmission'],
    category: 'Neuroscience',
    type: 'page',
    metadata: {
      chapter: 'Chapter 3',
      difficulty: 'advanced',
      estimatedReadTime: 15
    }
  }
]

// Fuse.js configuration
const fuseOptions = {
  keys: [
    { name: 'title', weight: 0.4 },
    { name: 'content', weight: 0.3 },
    { name: 'tags', weight: 0.2 },
    { name: 'category', weight: 0.1 }
  ],
  threshold: 0.4,
  includeScore: true,
  includeMatches: true,
  minMatchCharLength: 2,
  ignoreLocation: true
}

// Initialize Fuse instance
let fuseInstance: Fuse<SearchableContent> | null = null

// Initialize search engine
export const initializeSearch = (content: SearchableContent[] = mockContent): void => {
  fuseInstance = new Fuse(content, fuseOptions)
}

// Perform search
export const performSearch = (options: SearchOptions): SearchResult[] => {
  if (!fuseInstance) {
    initializeSearch()
  }

  if (!options.query.trim()) {
    return []
  }

  const results = fuseInstance!.search(options.query)
  
  // Filter results based on additional criteria
  let filteredResults = results.map(result => ({
    item: result.item,
    score: result.score || 0,
    matches: result.matches
  }))

  // Apply tag filter
  if (options.tags && options.tags.length > 0) {
    filteredResults = filteredResults.filter(result => 
      options.tags!.some(tag => result.item.tags.includes(tag))
    )
  }

  // Apply category filter
  if (options.category) {
    filteredResults = filteredResults.filter(result => 
      result.item.category === options.category
    )
  }

  // Apply type filter
  if (options.type) {
    filteredResults = filteredResults.filter(result => 
      result.item.type === options.type
    )
  }

  // Limit results
  const maxResults = options.maxResults || 10
  return filteredResults.slice(0, maxResults)
}

// Get all available filters
export const getAvailableFilters = (): SearchFilters => {
  const content = mockContent // In real implementation, this would come from a content store
  
  const tags = Array.from(new Set(content.flatMap(item => item.tags))).sort()
  const categories = Array.from(new Set(content.map(item => item.category))).sort()
  const types = Array.from(new Set(content.map(item => item.type))) as ('page' | 'section')[]

  return {
    tags,
    categories,
    types
  }
}

// Get content by ID
export const getContentById = (id: string): SearchableContent | undefined => {
  return mockContent.find(item => item.id === id)
}

// Get related content based on tags
export const getRelatedContent = (contentId: string, limit: number = 3): SearchableContent[] => {
  const content = getContentById(contentId)
  if (!content) return []

  const relatedContent = mockContent
    .filter(item => item.id !== contentId)
    .map(item => {
      const commonTags = item.tags.filter(tag => content.tags.includes(tag))
      return {
        ...item,
        relevanceScore: commonTags.length / Math.max(item.tags.length, content.tags.length)
      }
    })
    .filter(item => item.relevanceScore > 0)
    .sort((a, b) => b.relevanceScore - a.relevanceScore)
    .slice(0, limit)

  return relatedContent.map(({ relevanceScore, ...item }) => item)
}

// Highlight search terms in text
export const highlightSearchTerms = (text: string, query: string): string => {
  if (!query.trim()) return text

  const words = query.toLowerCase().split(/\s+/)
  let highlightedText = text

  words.forEach(word => {
    const regex = new RegExp(`(${word})`, 'gi')
    highlightedText = highlightedText.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>')
  })

  return highlightedText
}

// Debounce function for search input
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

// Get search suggestions based on partial query
export const getSearchSuggestions = (query: string, limit: number = 5): string[] => {
  if (!query.trim()) return []

  const suggestions = new Set<string>()
  const lowercaseQuery = query.toLowerCase()

  // Add title suggestions
  mockContent.forEach(item => {
    if (item.title.toLowerCase().includes(lowercaseQuery)) {
      suggestions.add(item.title)
    }
  })

  // Add tag suggestions
  mockContent.forEach(item => {
    item.tags.forEach(tag => {
      if (tag.toLowerCase().includes(lowercaseQuery)) {
        suggestions.add(tag)
      }
    })
  })

  return Array.from(suggestions).slice(0, limit)
}

// Initialize search on module load
initializeSearch()