#!/usr/bin/env node

/**
 * Search Index Generator
 *
 * This script automatically extracts pageMetadata from all Vue page components
 * and generates the search index for searchUtils.ts
 *
 * Usage:
 *   node scripts/generate-search-index.js
 *   yarn generate-search-index
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Configuration
const PAGES_DIR = path.join(__dirname, '../src/pages')
const OUTPUT_FILE = path.join(__dirname, '../src/utilities/searchUtils.ts')

/**
 * Extract pageMetadata from a Vue file's script setup section
 */
function extractPageMetadata(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')

  // Check if file contains pageMetadata
  if (!content.includes('pageMetadata')) {
    return null
  }

  try {
    // Extract the pageMetadata object
    const metadataMatch = content.match(/const pageMetadata\s*=\s*({[\s\S]*?^})/m)
    if (!metadataMatch) {
      return null
    }

    const metadataString = metadataMatch[1]

    // Parse individual fields with regex
    const metadata = {
      id: extractField(metadataString, 'id'),
      title: extractField(metadataString, 'title'),
      content: extractField(metadataString, 'content'),
      excerpt: extractField(metadataString, 'excerpt'),
      path: extractField(metadataString, 'path'),
      tags: extractArrayField(metadataString, 'tags'),
      category: extractField(metadataString, 'category'),
      type: extractField(metadataString, 'type').replace(/\s*as const$/, '').trim(),
    }

    // Extract nested metadata object
    const nestedMetadataMatch = metadataString.match(/metadata:\s*{([^}]*)}/s)
    if (nestedMetadataMatch) {
      const nestedContent = nestedMetadataMatch[1]
      metadata.metadata = {
        chapter: extractField(nestedContent, 'chapter'),
        difficulty: extractField(nestedContent, 'difficulty').replace(/\s*as const$/, '').trim(),
        estimatedReadTime: parseInt(extractField(nestedContent, 'estimatedReadTime')) || undefined
      }
    }

    // Validate required fields
    if (!metadata.id || !metadata.title || !metadata.path) {
      console.warn(`⚠️  Skipping ${filePath}: Missing required fields (id, title, or path)`)
      return null
    }

    return metadata
  } catch (error) {
    console.error(`❌ Error parsing ${filePath}:`, error.message)
    return null
  }
}

/**
 * Extract a string field value from metadata string
 * Handles escaped quotes properly
 */
function extractField(str, fieldName) {
  // Try to find the field with single quotes
  const singleQuoteRegex = new RegExp(`${fieldName}:\\s*'`, 's')
  const singleMatch = str.match(singleQuoteRegex)

  if (singleMatch) {
    const startIndex = singleMatch.index + singleMatch[0].length
    let endIndex = startIndex
    let escaped = false

    // Find the matching closing quote, handling escapes
    while (endIndex < str.length) {
      if (str[endIndex] === '\\' && !escaped) {
        escaped = true
      } else if (str[endIndex] === '\'' && !escaped) {
        return str.substring(startIndex, endIndex)
      } else {
        escaped = false
      }
      endIndex++
    }
  }

  // Try with double quotes
  const doubleQuoteRegex = new RegExp(`${fieldName}:\\s*"`, 's')
  const doubleMatch = str.match(doubleQuoteRegex)

  if (doubleMatch) {
    const startIndex = doubleMatch.index + doubleMatch[0].length
    let endIndex = startIndex
    let escaped = false

    while (endIndex < str.length) {
      if (str[endIndex] === '\\' && !escaped) {
        escaped = true
      } else if (str[endIndex] === '"' && !escaped) {
        return str.substring(startIndex, endIndex)
      } else {
        escaped = false
      }
      endIndex++
    }
  }

  return ''
}

/**
 * Extract an array field value from metadata string
 */
function extractArrayField(str, fieldName) {
  const regex = new RegExp(`${fieldName}:\\s*\\[([^\\]]*?)\\]`, 's')
  const match = str.match(regex)
  if (!match) return []

  // Extract string values from the array
  const arrayContent = match[1]
  const stringMatches = arrayContent.match(/['"]([^'"]+)['"]/g)
  if (!stringMatches) return []

  return stringMatches.map(s => s.replace(/['"]/g, ''))
}

/**
 * Scan pages directory and extract all metadata
 */
function extractAllMetadata() {
  const files = fs.readdirSync(PAGES_DIR)
  const allMetadata = []

  console.log('🔍 Scanning pages directory...\n')

  for (const file of files) {
    if (!file.endsWith('.vue')) continue

    const filePath = path.join(PAGES_DIR, file)
    const metadata = extractPageMetadata(filePath)

    if (metadata) {
      allMetadata.push(metadata)
      console.log(`✅ Extracted metadata from ${file}`)
      console.log(`   → ${metadata.title} (${metadata.path})`)
    } else {
      console.log(`⏭️  Skipped ${file} (no pageMetadata found)`)
    }
  }

  console.log(`\n📊 Found ${allMetadata.length} pages with metadata\n`)
  return allMetadata
}

/**
 * Generate the TypeScript content for searchUtils.ts
 */
function generateSearchUtilsContent(metadataArray) {
  // Sort by path for consistent ordering
  metadataArray.sort((a, b) => a.path.localeCompare(b.path))

  const metadataStrings = metadataArray.map(meta => {
    // Helper function to properly escape strings for JavaScript
    const escapeString = (str) => {
      if (!str) return ''
      return str
        .replace(/\\/g, '\\\\')  // Escape backslashes first
        .replace(/'/g, "\\'")     // Escape single quotes
        .replace(/\n/g, '\\n')    // Escape newlines
        .replace(/\r/g, '\\r')    // Escape carriage returns
    }

    const metadataObj = meta.metadata ? `{
    chapter: '${escapeString(meta.metadata.chapter || '')}',
    difficulty: '${escapeString(meta.metadata.difficulty || 'beginner')}',
    estimatedReadTime: ${meta.metadata.estimatedReadTime || 5}
  }` : '{}'

    const tags = meta.tags.map(tag => `'${escapeString(tag)}'`).join(', ')

    return `  {
    id: '${escapeString(meta.id)}',
    title: '${escapeString(meta.title)}',
    content: '${escapeString(meta.content)}',
    excerpt: '${escapeString(meta.excerpt)}',
    path: '${escapeString(meta.path)}',
    tags: [${tags}],
    category: '${escapeString(meta.category)}',
    type: '${escapeString(meta.type)}',
    metadata: ${metadataObj}
  }`
  })

  return `// Auto-generated file - DO NOT EDIT MANUALLY
// Generated by scripts/generate-search-index.js
// Last updated: ${new Date().toISOString()}

import Fuse from 'fuse.js'
import type { SearchableContent, SearchResult, SearchOptions } from '../types/search'

/**
 * Search content index - automatically generated from page metadata
 * To update: run \`yarn generate-search-index\` or \`node scripts/generate-search-index.js\`
 */
const searchContent: SearchableContent[] = [
${metadataStrings.join(',\n')}
]

// Fuse.js configuration for fuzzy search
const fuseOptions = {
  keys: [
    { name: 'title', weight: 0.4 },
    { name: 'content', weight: 0.3 },
    { name: 'tags', weight: 0.2 },
    { name: 'category', weight: 0.1 }
  ],
  threshold: 0.4,
  includeScore: true,
  minMatchCharLength: 3,
  ignoreLocation: true
}

// Create Fuse instance
const fuse = new Fuse(searchContent, fuseOptions)

/**
 * Perform a search query with options
 * @param options - Search options including query, filters, and limits
 */
export function performSearch(options: SearchOptions): SearchResult[] {
  const { query, tags, category, type, maxResults = 10 } = options

  if (!query || query.length < 3) {
    return []
  }

  // Perform fuzzy search
  let results = fuse.search(query, { limit: maxResults * 2 })

  // Apply additional filters
  if (tags && tags.length > 0) {
    results = results.filter(result =>
      tags.some(tag => result.item.tags.includes(tag))
    )
  }

  if (category) {
    results = results.filter(result => result.item.category === category)
  }

  if (type) {
    results = results.filter(result => result.item.type === type)
  }

  // Transform to SearchResult format and limit
  return results.slice(0, maxResults).map(result => ({
    item: result.item,
    score: result.score || 0,
    matches: result.matches as any
  }))
}

/**
 * Get search suggestions based on partial query
 * @param partialQuery - Partial search string
 * @param limit - Maximum number of suggestions (default: 5)
 */
export function getSearchSuggestions(partialQuery: string, limit: number = 5): string[] {
  if (!partialQuery || partialQuery.length < 1) {
    return []
  }

  const query = partialQuery.toLowerCase()
  const suggestions = new Set<string>()

  // Suggest from titles
  searchContent.forEach(item => {
    if (item.title.toLowerCase().includes(query)) {
      suggestions.add(item.title)
    }
  })

  // Suggest from tags
  searchContent.forEach(item => {
    item.tags.forEach(tag => {
      if (tag.toLowerCase().includes(query)) {
        suggestions.add(tag)
      }
    })
  })

  return Array.from(suggestions).slice(0, limit)
}

/**
 * Debounce utility function
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Get all searchable content
 */
export function getAllContent(): SearchableContent[] {
  return searchContent
}

/**
 * Get content by category
 */
export function getContentByCategory(category: string): SearchableContent[] {
  return searchContent.filter(item => item.category === category)
}

/**
 * Get content by tag
 */
export function getContentByTag(tag: string): SearchableContent[] {
  return searchContent.filter(item => item.tags.includes(tag))
}

/**
 * Get all unique categories
 */
export function getAllCategories(): string[] {
  return Array.from(new Set(searchContent.map(item => item.category)))
}

/**
 * Get all unique tags
 */
export function getAllTags(): string[] {
  const tags = new Set<string>()
  searchContent.forEach(item => {
    item.tags.forEach(tag => tags.add(tag))
  })
  return Array.from(tags).sort()
}
`
}

/**
 * Main execution
 */
function main() {
  console.log('🚀 Search Index Generator\n')
  console.log('=' .repeat(50) + '\n')

  try {
    // Extract metadata from all pages
    const allMetadata = extractAllMetadata()

    if (allMetadata.length === 0) {
      console.error('❌ No pages with metadata found!')
      process.exit(1)
    }

    // Generate TypeScript content
    const content = generateSearchUtilsContent(allMetadata)

    // Write to file
    fs.writeFileSync(OUTPUT_FILE, content, 'utf-8')

    console.log('=' .repeat(50))
    console.log(`\n✨ Successfully generated search index!`)
    console.log(`📝 Output: ${path.relative(process.cwd(), OUTPUT_FILE)}`)
    console.log(`📊 Total entries: ${allMetadata.length}\n`)

    // Display summary by category
    const categories = {}
    allMetadata.forEach(meta => {
      categories[meta.category] = (categories[meta.category] || 0) + 1
    })

    console.log('📋 Breakdown by category:')
    Object.entries(categories).forEach(([category, count]) => {
      console.log(`   • ${category}: ${count} page${count > 1 ? 's' : ''}`)
    })
    console.log('')

  } catch (error) {
    console.error('❌ Error generating search index:', error)
    process.exit(1)
  }
}

// Run if executed directly
main()
