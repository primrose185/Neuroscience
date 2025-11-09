<script setup lang="ts">
import { onMounted, ref } from 'vue'

const searchContainerRef = ref<HTMLDivElement | null>(null)
const isLoaded = ref(false)

// Get the Search Engine ID from environment variables
const searchEngineId = import.meta.env.VITE_GOOGLE_SEARCH_ENGINE_ID

onMounted(() => {
  // Only load if we have a valid search engine ID
  if (!searchEngineId) {
    console.warn('Google Search Engine ID not found. Please add VITE_GOOGLE_SEARCH_ENGINE_ID to your .env.local file')
    return
  }

  // Load Google Custom Search script
  const script = document.createElement('script')
  script.src = 'https://cse.google.com/cse.js?cx=' + searchEngineId
  script.async = true

  script.onload = () => {
    isLoaded.value = true
  }

  script.onerror = () => {
    console.error('Failed to load Google Custom Search')
  }

  document.head.appendChild(script)
})
</script>

<template>
  <div class="google-search-container">
    <!-- Google Custom Search Element -->
    <div v-if="searchEngineId" class="gcse-search"></div>

    <!-- Warning message if no search engine ID -->
    <div v-else class="search-warning">
      <p class="warning-text">
        ⚠️ Google Search not configured
      </p>
      <p class="warning-subtext">
        Add your Google Search Engine ID to <code>.env.local</code>
      </p>
      <p class="warning-help">
        See <a href="/GOOGLE_SEARCH_SETUP.md" target="_blank">setup guide</a> for instructions
      </p>
    </div>
  </div>
</template>

<style scoped>
.google-search-container {
  width: 100%;
  padding: 0.5rem 0;
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

/* Override Google Search default styles to match your design */
:deep(.gsc-control-cse) {
  padding: 0;
  border: none;
  background-color: transparent;
}

:deep(.gsc-search-box) {
  margin-bottom: 0;
}

:deep(.gsc-input-box) {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #ffffff;
}

:deep(.gsc-input) {
  padding: 0.5rem !important;
  font-size: 0.875rem !important;
}

:deep(.gsc-search-button) {
  margin-left: 0.5rem;
}

/* Results styling */
:deep(.gsc-results-wrapper-overlay) {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.gsc-result) {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

:deep(.gsc-result:hover) {
  background-color: #f9fafb;
}

:deep(.gs-title) {
  color: #1d4ed8 !important;
  font-weight: 600;
}

:deep(.gs-snippet) {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .google-search-container {
    padding: 0.25rem 0;
  }

  :deep(.gsc-input) {
    font-size: 0.8rem !important;
  }
}
</style>
