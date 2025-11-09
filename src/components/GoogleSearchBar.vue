<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

// Get the Search Engine ID from environment variables
const searchEngineId = import.meta.env.VITE_GOOGLE_SEARCH_ENGINE_ID

const searchInput = ref<HTMLInputElement | null>(null)
const searchResultsContainer = ref<HTMLElement | null>(null)
const query = ref('')
const showResults = ref(false)
const isGoogleLoaded = ref(false)

// Load Google Custom Search script
onMounted(() => {
  console.log('Google Search Engine ID:', searchEngineId)
  if (!searchEngineId) return

  // Load Google Custom Search script if not already loaded
  if (!document.querySelector('script[src*="cse.google.com"]')) {
    const script = document.createElement('script')
    script.src = 'https://cse.google.com/cse.js?cx=' + searchEngineId
    script.async = true
    script.onload = () => {
      isGoogleLoaded.value = true
    }
    document.head.appendChild(script)
  } else {
    isGoogleLoaded.value = true
  }
})

const handleSearch = () => {
  if (!query.value.trim() || !searchEngineId || !isGoogleLoaded.value) return

  showResults.value = true

  nextTick(() => {
    // Trigger Google search by programmatically setting up the search element
    if (searchResultsContainer.value) {
      // Clear previous results
      searchResultsContainer.value.innerHTML = '<div class="gcse-search" data-gname="styledSearch"></div>'

      // Initialize Google Custom Search on the new element
      if ((window as any).google && (window as any).google.search) {
        (window as any).google.search.cse.element.render({
          div: searchResultsContainer.value.querySelector('.gcse-search'),
          tag: 'search',
          gname: 'styledSearch'
        })

        // Execute search with the query
        const searchElement = (window as any).google.search.cse.element.getElement('styledSearch')
        if (searchElement) {
          searchElement.execute(query.value)
        }
      }
    }
  })
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    handleSearch()
  } else if (event.key === 'Escape') {
    closeResults()
  }
}

const clearSearch = () => {
  query.value = ''
  searchInput.value?.focus()
}

const closeResults = () => {
  showResults.value = false
}

// Focus search input when component is mounted
const focusSearch = () => {
  searchInput.value?.focus()
}

// Expose for parent component
defineExpose({
  focusSearch,
  clearSearch
})
</script>

<template>
  <div class="google-search-container">
    <!-- Custom Search Input matching local search style -->
    <div v-if="searchEngineId" class="search-input-wrapper">
      <input
        ref="searchInput"
        v-model="query"
        type="text"
        placeholder="Search with Google..."
        class="search-input"
        autocomplete="off"
        @keydown="handleKeyDown"
      />

      <button
        @click="handleSearch"
        class="search-button"
        type="button"
        title="Search"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
        >
          <path
            d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667ZM14 14l-2.9-2.9"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

      <!-- Search Results Overlay -->
      <div v-if="showResults" class="search-overlay" @click.self="closeResults">
        <div class="search-results-modal">
          <button class="close-button" @click="closeResults" title="Close">✕</button>
          <div ref="searchResultsContainer" class="results-container"></div>
        </div>
      </div>
    </div>

    <!-- Warning message if no search engine ID -->
    <div v-else class="search-warning">
      <p class="warning-text">
        ⚠️ Google Search not configured
      </p>
      <p class="warning-subtext">
        Add your Google Search Engine ID to <code>.env.local</code>
      </p>
      <p class="warning-help">
        See <a href="docs/GOOGLE_SEARCH_SETUP.md" target="_blank">setup guide</a> for instructions
      </p>
    </div>
  </div>
</template>

<style scoped>
.google-search-container {
  width: 100%;
}

/* Match local search styling exactly */
.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #ffffff;
  color: #374151;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-button {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #3b82f6;
  border: none;
  border-radius: 6px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-button:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-button:active {
  transform: translateY(0);
}

.search-button svg {
  flex-shrink: 0;
}

/* Search Results Overlay */
.search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.search-results-modal {
  background-color: white;
  border-radius: 12px;
  max-width: 90%;
  max-height: 90%;
  width: 1200px;
  height: 800px;
  overflow: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
  padding: 20px;
}

.close-button {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  background-color: #f3f4f6;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: #e5e7eb;
}

.results-container {
  width: 100%;
  height: 100%;
  padding-top: 40px;
}

/* Warning styles */
.search-warning {
  padding: 1rem;
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  font-size: 0.875rem;
}

.warning-text {
  font-weight: 600;
  color: #92400e;
  margin: 0 0 0.5rem 0;
}

.warning-subtext {
  color: #78350f;
  margin: 0 0 0.5rem 0;
  font-family: monospace;
  font-size: 0.8rem;
}

.warning-subtext code {
  background-color: #fde68a;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.warning-help {
  margin: 0;
  font-size: 0.8rem;
}

.warning-help a {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .search-input {
    font-size: 0.8rem;
    padding: 0.45rem 0.6rem;
  }

  .search-button {
    width: 32px;
    height: 32px;
  }

  .search-button svg {
    width: 14px;
    height: 14px;
  }

  .search-results-modal {
    width: 95%;
    height: 85%;
    padding: 15px;
  }
}
</style>
