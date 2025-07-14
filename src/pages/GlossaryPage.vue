<script setup lang="ts">
// Page metadata for search indexing
const pageMetadata = {
  id: 'glossary',
  title: 'Glossary',
  content: 'Comprehensive glossary of neuroscience and mathematical terms used throughout the platform. Find definitions, explanations, and related concepts for key terminology.',
  excerpt: 'Definitions and explanations of key neuroscience and mathematical terms.',
  path: '/glossary',
  tags: ['glossary', 'definitions', 'terminology', 'reference'],
  category: 'Reference',
  type: 'page' as const,
  metadata: {
    chapter: 'Reference',
    difficulty: 'beginner' as const,
    estimatedReadTime: 2
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}
</script>

<template>
  <div class="page-container">
    <div class="max-w-4xl mx-auto px-8 py-12">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Glossary</h1>
        <p class="text-xl text-gray-600">
          Key terms and definitions for neuroscience and mathematical concepts
        </p>
      </div>
      
      <div class="prose prose-lg max-w-none">
        <div class="bg-blue-50 border-l-4 border-blue-400 p-6 mb-8">
          <h2 class="text-lg font-semibold text-blue-900 mb-2">Coming Soon</h2>
          <p class="text-blue-800">
            This comprehensive glossary is currently being developed. It will include:
          </p>
          <ul class="mt-4 text-blue-800">
            <li>Neuroscience terminology and definitions</li>
            <li>Mathematical concepts and formulas</li>
            <li>Interactive cross-references</li>
            <li>Visual examples and illustrations</li>
          </ul>
        </div>
        
        <div class="grid md:grid-cols-2 gap-8 mt-12">
          <div class="bg-white p-6 rounded-lg border border-gray-200">
            <h3 class="text-xl font-semibold mb-4 text-gray-900">Browse by Category</h3>
            <div class="space-y-2">
              <button class="block w-full text-left px-4 py-2 rounded hover:bg-gray-50 text-gray-700">
                Neuroscience Terms
              </button>
              <button class="block w-full text-left px-4 py-2 rounded hover:bg-gray-50 text-gray-700">
                Mathematical Concepts
              </button>
              <button class="block w-full text-left px-4 py-2 rounded hover:bg-gray-50 text-gray-700">
                Statistical Methods
              </button>
              <button class="block w-full text-left px-4 py-2 rounded hover:bg-gray-50 text-gray-700">
                Research Techniques
              </button>
            </div>
          </div>
          
          <div class="bg-white p-6 rounded-lg border border-gray-200">
            <h3 class="text-xl font-semibold mb-4 text-gray-900">Quick Search</h3>
            <p class="text-gray-600 mb-4">
              Use the search bar in the sidebar or homepage to quickly find specific terms and their definitions.
            </p>
            <a href="/" class="text-blue-600 hover:text-blue-800 font-medium">
              Search Now →
            </a>
          </div>
        </div>
        
        <div class="mt-12 p-6 bg-gray-50 rounded-lg">
          <h3 class="text-lg font-semibold mb-3">Suggest a Term</h3>
          <p class="text-gray-600">
            Can't find a term you're looking for? The glossary will include a feature to suggest new terms and definitions to be added to our comprehensive database.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #ffffff;
}
</style>