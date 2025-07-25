<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { performSearch, getSearchSuggestions, debounce } from '../utilities/searchUtils'
import type { SearchResult, SearchOptions } from '../types/search'

interface Props {
  placeholder?: string
  showResults?: boolean
  maxResults?: number
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search topics, concepts, or keywords...',
  showResults: true,
  maxResults: 8,
  compact: false
})

const emit = defineEmits<{
  search: [query: string, results: SearchResult[]]
  select: [result: SearchResult]
  clear: []
}>()

const router = useRouter()
const searchInput = ref<HTMLInputElement | null>(null)
const searchContainer = ref<HTMLElement | null>(null)

// Search state
const query = ref('')
const results = ref<SearchResult[]>([])
const suggestions = ref<string[]>([])
const isLoading = ref(false)
const showDropdown = ref(false)
const selectedIndex = ref(-1)

// Computed properties
const hasResults = computed(() => results.value.length > 0)
const hasSuggestions = computed(() => suggestions.value.length > 0)
const showSuggestions = computed(() => query.value.length > 0 && query.value.length < 3 && hasSuggestions.value)
const showSearchResults = computed(() => query.value.length >= 3 && hasResults.value)

// Perform search with debouncing
const debouncedSearch = debounce(async (searchQuery: string) => {
  if (searchQuery.length < 3) {
    results.value = []
    suggestions.value = getSearchSuggestions(searchQuery, 5)
    isLoading.value = false
    return
  }

  isLoading.value = true
  
  try {
    const searchOptions: SearchOptions = {
      query: searchQuery,
      maxResults: props.maxResults
    }
    
    const searchResults = performSearch(searchOptions)
    results.value = searchResults
    suggestions.value = []
    
    emit('search', searchQuery, searchResults)
  } catch (error) {
    console.error('Search error:', error)
    results.value = []
  } finally {
    isLoading.value = false
  }
}, 300)

// Handle input changes
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  query.value = target.value
  selectedIndex.value = -1
  
  if (query.value.trim()) {
    showDropdown.value = true
    debouncedSearch(query.value.trim())
  } else {
    showDropdown.value = false
    results.value = []
    suggestions.value = []
    emit('clear')
  }
}

// Handle suggestion click
const handleSuggestionClick = (suggestion: string) => {
  query.value = suggestion
  searchInput.value?.focus()
  debouncedSearch(suggestion)
}

// Handle result click
const handleResultClick = (result: SearchResult) => {
  showDropdown.value = false
  query.value = result.item.title
  emit('select', result)
  router.push(result.item.path)
}

// Handle keyboard navigation
const handleKeyDown = (event: KeyboardEvent) => {
  if (!showDropdown.value) return

  const totalItems = showSuggestions.value ? suggestions.value.length : results.value.length

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = selectedIndex.value < totalItems - 1 ? selectedIndex.value + 1 : 0
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = selectedIndex.value > 0 ? selectedIndex.value - 1 : totalItems - 1
      break
    case 'Enter':
      event.preventDefault()
      if (selectedIndex.value >= 0) {
        if (showSuggestions.value) {
          handleSuggestionClick(suggestions.value[selectedIndex.value])
        } else if (showSearchResults.value) {
          handleResultClick(results.value[selectedIndex.value])
        }
      }
      break
    case 'Escape':
      event.preventDefault()
      showDropdown.value = false
      searchInput.value?.blur()
      break
  }
}

// Handle clicks outside the search component
const handleClickOutside = (event: Event) => {
  if (searchContainer.value && !searchContainer.value.contains(event.target as Node)) {
    showDropdown.value = false
  }
}

// Focus search input
const focusSearch = () => {
  searchInput.value?.focus()
}

// Clear search
const clearSearch = () => {
  query.value = ''
  results.value = []
  suggestions.value = []
  showDropdown.value = false
  emit('clear')
}

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Expose methods for parent components
defineExpose({
  focusSearch,
  clearSearch
})
</script>

<template>
  <div 
    ref="searchContainer"
    :class="[
      'search-container',
      { 'search-container--compact': compact }
    ]"
  >
    <!-- Search Input -->
    <div class="search-input-wrapper">
      <div class="search-input-icon">
        <svg 
          class="w-5 h-5 text-gray-400" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
      
      <input
        ref="searchInput"
        v-model="query"
        type="text"
        :placeholder="placeholder"
        class="search-input"
        autocomplete="off"
        @input="handleInput"
        @keydown="handleKeyDown"
        @focus="showDropdown = true"
      />
      
      <button
        v-if="query"
        @click="clearSearch"
        class="search-clear-btn"
        aria-label="Clear search"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Search Dropdown -->
    <div 
      v-if="showDropdown && props.showResults"
      class="search-dropdown"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="search-loading">
        <div class="search-spinner"></div>
        <span class="text-sm text-gray-500">Searching...</span>
      </div>

      <!-- Suggestions -->
      <div v-else-if="showSuggestions" class="search-suggestions">
        <div class="search-section-title">Suggestions</div>
        <button
          v-for="(suggestion, index) in suggestions"
          :key="suggestion"
          :class="[
            'search-suggestion-item',
            { 'search-suggestion-item--selected': selectedIndex === index }
          ]"
          @click="handleSuggestionClick(suggestion)"
        >
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>{{ suggestion }}</span>
        </button>
      </div>

      <!-- Search Results -->
      <div v-else-if="showSearchResults" class="search-results">
        <div class="search-section-title">
          {{ results.length }} result{{ results.length === 1 ? '' : 's' }}
        </div>
        <button
          v-for="(result, index) in results"
          :key="result.item.id"
          :class="[
            'search-result-item',
            { 'search-result-item--selected': selectedIndex === index }
          ]"
          @click="handleResultClick(result)"
        >
          <div class="search-result-content">
            <h4 class="search-result-title">{{ result.item.title }}</h4>
            <p class="search-result-excerpt">{{ result.item.excerpt }}</p>
            <div class="search-result-meta">
              <span class="search-result-category">{{ result.item.category }}</span>
              <span class="search-result-separator">•</span>
              <span class="search-result-path">{{ result.item.path }}</span>
            </div>
          </div>
          <div class="search-result-tags">
            <span
              v-for="tag in result.item.tags.slice(0, 3)"
              :key="tag"
              class="search-result-tag"
            >
              {{ tag }}
            </span>
          </div>
        </button>
      </div>

      <!-- No Results -->
      <div v-else-if="query.length >= 3" class="search-no-results">
        <div class="text-center py-8">
          <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p class="text-gray-500 text-sm">No results found for "{{ query }}"</p>
          <p class="text-gray-400 text-xs mt-1">Try different keywords or browse topics</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 600px;
}

.search-container--compact {
  max-width: 400px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-icon {
  position: absolute;
  left: 12px;
  z-index: 1;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  background-color: white;
  transition: all 0.2s ease;
  outline: none;
}

.search-input:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.1);
}

.search-clear-btn {
  position: absolute;
  right: 12px;
  padding: 4px;
  color: #6b7280;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.search-clear-btn:hover {
  color: #374151;
  background-color: #f3f4f6;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  margin-top: 4px;
  max-height: 400px;
  overflow-y: auto;
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.search-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #93c5fd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-section-title {
  padding: 12px 16px 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f3f4f6;
}

.search-suggestions {
  padding-bottom: 8px;
}

.search-suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 16px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-suggestion-item:hover,
.search-suggestion-item--selected {
  background-color: #f9fafb;
}

.search-results {
  padding-bottom: 8px;
}

.search-result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-result-item:hover,
.search-result-item--selected {
  background-color: #f9fafb;
}

.search-result-content {
  flex: 1;
  min-width: 0;
}

.search-result-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.search-result-excerpt {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
  margin-bottom: 6px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.search-result-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #9ca3af;
}

.search-result-category {
  font-weight: 500;
}

.search-result-separator {
  opacity: 0.5;
}

.search-result-path {
  font-family: monospace;
}

.search-result-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.search-result-tag {
  padding: 2px 6px;
  background-color: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
}

.search-no-results {
  padding: 8px;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .search-input {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  .search-dropdown {
    max-height: 300px;
  }
  
  .search-result-tags {
    display: none;
  }
}
</style>