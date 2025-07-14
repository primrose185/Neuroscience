<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { highlightSearchTerms, getRelatedContent } from '../utilities/searchUtils'
import type { SearchResult } from '../types/search'

interface Props {
  results: SearchResult[]
  query: string
  isLoading?: boolean
  showRelated?: boolean
  maxResults?: number
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  showRelated: true,
  maxResults: 20
})

const emit = defineEmits<{
  resultClick: [result: SearchResult]
  loadMore: []
}>()

const router = useRouter()

// Computed properties
const displayedResults = computed(() => props.results.slice(0, props.maxResults))
const hasMoreResults = computed(() => props.results.length > props.maxResults)
const totalResults = computed(() => props.results.length)

// Handle result click
const handleResultClick = (result: SearchResult) => {
  emit('resultClick', result)
  router.push(result.item.path)
}

// Get highlighted content
const getHighlightedContent = (text: string) => {
  return highlightSearchTerms(text, props.query)
}

// Get difficulty color
const getDifficultyColor = (difficulty?: string) => {
  switch (difficulty) {
    case 'beginner':
      return 'text-green-600 bg-green-50'
    case 'intermediate':
      return 'text-yellow-600 bg-yellow-50'
    case 'advanced':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

// Get category color
const getCategoryColor = (category: string) => {
  switch (category.toLowerCase()) {
    case 'mathematics':
      return 'text-blue-600 bg-blue-50'
    case 'neuroscience':
      return 'text-purple-600 bg-purple-50'
    case 'biology':
      return 'text-green-600 bg-green-50'
    case 'physics':
      return 'text-orange-600 bg-orange-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

// Format reading time
const formatReadingTime = (minutes?: number) => {
  if (!minutes) return ''
  return `${minutes} min read`
}

// Handle load more
const handleLoadMore = () => {
  emit('loadMore')
}
</script>

<template>
  <div class="search-results">
    <!-- Loading State -->
    <div v-if="isLoading" class="search-results-loading">
      <div class="flex items-center justify-center py-12">
        <div class="search-spinner"></div>
        <span class="ml-3 text-gray-500">Searching...</span>
      </div>
    </div>

    <!-- Results Header -->
    <div v-else-if="results.length > 0" class="search-results-header">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        Search Results
      </h2>
      <p class="text-gray-600">
        Found {{ totalResults }} result{{ totalResults === 1 ? '' : 's' }} 
        <span v-if="query" class="font-medium">for "{{ query }}"</span>
      </p>
    </div>

    <!-- Results List -->
    <div v-if="displayedResults.length > 0" class="search-results-list">
      <article
        v-for="result in displayedResults"
        :key="result.item.id"
        class="search-result-card"
        @click="handleResultClick(result)"
      >
        <!-- Result Header -->
        <div class="search-result-header">
          <div class="search-result-meta-top">
            <span 
              :class="[
                'search-result-category',
                getCategoryColor(result.item.category)
              ]"
            >
              {{ result.item.category }}
            </span>
            <span 
              v-if="result.item.metadata?.difficulty"
              :class="[
                'search-result-difficulty',
                getDifficultyColor(result.item.metadata.difficulty)
              ]"
            >
              {{ result.item.metadata.difficulty }}
            </span>
          </div>
          
          <h3 
            class="search-result-title"
            v-html="getHighlightedContent(result.item.title)"
          ></h3>
          
          <div class="search-result-meta-bottom">
            <span class="search-result-path">{{ result.item.path }}</span>
            <span 
              v-if="result.item.metadata?.estimatedReadTime"
              class="search-result-read-time"
            >
              {{ formatReadingTime(result.item.metadata.estimatedReadTime) }}
            </span>
          </div>
        </div>

        <!-- Result Content -->
        <div class="search-result-content">
          <p 
            class="search-result-excerpt"
            v-html="getHighlightedContent(result.item.excerpt)"
          ></p>
          
          <!-- Tags -->
          <div class="search-result-tags">
            <span
              v-for="tag in result.item.tags"
              :key="tag"
              class="search-result-tag"
            >
              #{{ tag }}
            </span>
          </div>
        </div>

        <!-- Result Footer -->
        <div class="search-result-footer">
          <div class="search-result-score">
            <span class="text-xs text-gray-400">
              Relevance: {{ Math.round((1 - result.score) * 100) }}%
            </span>
          </div>
          
          <div class="search-result-actions">
            <button 
              class="search-result-action-btn"
              @click.stop="handleResultClick(result)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <span>View</span>
            </button>
          </div>
        </div>
      </article>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMoreResults" class="search-results-load-more">
      <button
        @click="handleLoadMore"
        class="load-more-btn"
      >
        Load More Results
        <span class="ml-2 text-sm text-gray-500">
          ({{ results.length - maxResults }} more)
        </span>
      </button>
    </div>

    <!-- No Results -->
    <div v-else-if="query && !isLoading" class="search-no-results">
      <div class="text-center py-16">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
        <p class="text-gray-600 mb-4">
          We couldn't find anything matching "{{ query }}"
        </p>
        <div class="text-sm text-gray-500">
          <p>Try:</p>
          <ul class="list-disc list-inside mt-2 space-y-1">
            <li>Different keywords or synonyms</li>
            <li>Broader search terms</li>
            <li>Checking spelling</li>
            <li>Browsing topics directly</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!query && !isLoading" class="search-empty-state">
      <div class="text-center py-16">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Start searching</h3>
        <p class="text-gray-600">
          Enter keywords to find relevant topics and content
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-results {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.search-results-loading {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #93c5fd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-results-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.search-results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-result-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-result-card:hover {
  border-color: #93c5fd;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.search-result-header {
  margin-bottom: 12px;
}

.search-result-meta-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.search-result-category,
.search-result-difficulty {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.search-result-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
  line-height: 1.4;
}

.search-result-meta-bottom {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.search-result-path {
  font-family: monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.search-result-read-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-result-excerpt {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 12px;
}

.search-result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.search-result-tag {
  padding: 2px 8px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.search-result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.search-result-actions {
  display: flex;
  gap: 8px;
}

.search-result-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-result-action-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #374151;
}

.search-results-load-more {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.load-more-btn {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  border-color: #93c5fd;
  background: #f8fafc;
}

.search-no-results,
.search-empty-state {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 40px;
}

/* Highlight styles */
:deep(mark) {
  background-color: #fef3c7;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 500;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .search-result-card {
    padding: 16px;
  }
  
  .search-result-title {
    font-size: 16px;
  }
  
  .search-result-meta-top {
    flex-wrap: wrap;
  }
  
  .search-result-meta-bottom {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .search-result-footer {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .search-result-actions {
    justify-content: center;
  }
}
</style>