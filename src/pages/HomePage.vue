<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'
import SearchResults from '../components/SearchResults.vue'
import { getAvailableFilters, getRelatedContent } from '../utilities/searchUtils'
import type { SearchResult, SearchFilters } from '../types/search'

const router = useRouter()

// State
const searchResults = ref<SearchResult[]>([])
const searchQuery = ref('')
const isSearching = ref(false)
const showResults = ref(false)
const showRecentlyAdded = ref(false)
const availableFilters = ref<SearchFilters>({
  tags: [],
  categories: [],
  types: []
})

// Recently added articles data
const recentlyAdded = [
  {
    id: 'topic1',
    title: 'Basic Probability',
    description: 'Introduction to probability theory and mathematical concepts',
    category: 'Mathematics',
    path: '/topic1/page1',
    tags: ['probability', 'mathematics', 'theory'],
    estimatedTime: '5 min',
    icon: '📊'
  },
  {
    id: 'topic2',
    title: 'Neuroscience Fundamentals',
    description: 'Understanding brain structure and neural mechanisms',
    category: 'Neuroscience',
    path: '/topic2/page1',
    tags: ['neuroscience', 'brain', 'anatomy'],
    estimatedTime: '10 min',
    icon: '🧠'
  },
  {
    id: 'topic3',
    title: 'Advanced Neural Networks',
    description: 'Deep dive into neural network behavior and synaptic transmission',
    category: 'Neuroscience',
    path: '/topic3',
    tags: ['neural-networks', 'synapses'],
    estimatedTime: '15 min',
    icon: '🔬'
  },
  {
    id: 'topic4',
    title: 'Statistical Analysis',
    description: 'Comprehensive guide to statistical methods in research',
    category: 'Mathematics',
    path: '/topic4',
    tags: ['statistics', 'analysis', 'research'],
    estimatedTime: '12 min',
    icon: '📈'
  }
]

// How to use links
const howToUseLinks = [
  { title: 'Getting Started', path: '/how-to-use/getting-started', icon: '🚀' },
  { title: 'Navigation Guide', path: '/how-to-use/navigation', icon: '🧭' },
  { title: 'Search Tips', path: '/how-to-use/search', icon: '🔍' },
  { title: 'Features Overview', path: '/how-to-use/features', icon: '✨' }
]

// Popular tags
const popularTags = [
  'probability',
  'neuroscience',
  'mathematics',
  'brain',
  'neural-networks',
  'statistics',
  'theory',
  'visualization',
  'synapses',
  'anatomy'
]

// Handle search results
const handleSearch = (query: string, results: SearchResult[]) => {
  searchQuery.value = query
  searchResults.value = results
  showResults.value = true
  isSearching.value = false
}

// Handle search result selection
const handleResultSelect = (result: SearchResult) => {
  // This will be handled by the SearchResults component
  console.log('Selected result:', result)
}

// Handle topic click
const handleTopicClick = (topic: any) => {
  router.push(topic.path)
}

// Handle tag click
const handleTagClick = (tag: string) => {
  // Focus search and add tag to query
  searchQuery.value = tag
  // The SearchBar component will handle the actual search
}

// Clear search
const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
}

// Get difficulty color
const getDifficultyColor = (difficulty: string) => {
  switch (difficulty) {
    case 'beginner':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'intermediate':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'advanced':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

// Initialize filters
onMounted(() => {
  availableFilters.value = getAvailableFilters()
})
</script>

<template>
  <div class="homepage">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            nREM
          </h1>
          <p class="hero-description">
            Explore interactive content, visualizations, and comprehensive resources 
            for understanding neuroscience concepts and mathematical foundations.
          </p>
        </div>
        
        <!-- Search Section -->
        <div class="hero-search">
          <SearchBar 
            :placeholder="'Search topics, concepts, or keywords...'"
            :show-results="true"
            @search="handleSearch"
            @select="handleResultSelect"
            @clear="clearSearch"
          />
        </div>
      </div>
    </section>

    <!-- Search Results Section -->
    <section v-if="showResults" class="search-results-section">
      <div class="container">
        <SearchResults 
          :results="searchResults"
          :query="searchQuery"
          :is-loading="isSearching"
          @result-click="handleResultSelect"
        />
      </div>
    </section>

    <!-- Recently Added Section -->
    <section v-if="!showResults && showRecentlyAdded" class="recently-added-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Recently Added</h2>
          <p class="section-description">
            Our latest articles and resources
          </p>
        </div>
        
        <div class="topics-grid">
          <article
            v-for="topic in recentlyAdded"
            :key="topic.id"
            class="topic-card"
            @click="handleTopicClick(topic)"
          >
            <div class="topic-icon">{{ topic.icon }}</div>
            <div class="topic-content">
              <h3 class="topic-title">{{ topic.title }}</h3>
              <p class="topic-description">{{ topic.description }}</p>
              
              <div class="topic-meta">
                <span class="topic-category">{{ topic.category }}</span>
                <span class="topic-time">{{ topic.estimatedTime }}</span>
              </div>
              
              <div class="topic-tags">
                <span
                  v-for="tag in topic.tags"
                  :key="tag"
                  class="topic-tag"
                  @click.stop="handleTagClick(tag)"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- How to Use Section -->
    <section v-if="!showResults" class="how-to-use-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">How to Use</h2>
          <p class="section-description">
            Learn how to navigate and make the most of this platform
          </p>
        </div>
        
        <div class="how-to-use-grid">
          <a
            v-for="link in howToUseLinks"
            :key="link.title"
            :href="link.path"
            class="how-to-use-card"
            @click.prevent="router.push(link.path)"
          >
            <div class="how-to-use-icon">{{ link.icon }}</div>
            <span class="how-to-use-title">{{ link.title }}</span>
          </a>
        </div>
      </div>
    </section>

    <!-- Popular Tags Section -->
    <section v-if="!showResults" class="popular-tags-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Popular Tags</h2>
          <p class="section-description">
            Discover content by popular topics and keywords
          </p>
        </div>
        
        <div class="tags-container">
          <button
            v-for="tag in popularTags"
            :key="tag"
            class="popular-tag"
            @click="handleTagClick(tag)"
          >
            #{{ tag }}
          </button>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.homepage {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Reduced margin sections */
.recently-added-section,
.how-to-use-section,
.popular-tags-section {
  margin: 0 -12px;
}

@media (min-width: 768px) {
  .recently-added-section,
  .how-to-use-section,
  .popular-tags-section {
    margin: 0 -24px;
  }
}

/* Hero Section */
.hero-section {
  padding: 80px 0 120px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1a202c;
  margin-bottom: 24px;
  line-height: 1.1;
}

.hero-description {
  font-size: 1.25rem;
  color: #4a5568;
  margin-bottom: 48px;
  line-height: 1.6;
}

.hero-search {
  max-width: 600px;
  margin: 0 auto;
}

/* Search Results Section */
.search-results-section {
  padding: 40px 0;
}

/* Recently Added Section */
.recently-added-section {
  padding: 80px 0;
  background: white;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 16px;
}

.section-description {
  font-size: 1.1rem;
  color: #4a5568;
  max-width: 600px;
  margin: 0 auto;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-top: 48px;
}

@media (max-width: 768px) {
  .topics-grid {
    grid-template-columns: 1fr;
  }
}

.topic-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.topic-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border-color: #93c5fd;
}

.topic-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.topic-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 12px;
}

.topic-description {
  color: #4a5568;
  margin-bottom: 16px;
  line-height: 1.5;
}

.topic-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.topic-category {
  padding: 4px 12px;
  background: #edf2f7;
  color: #4a5568;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
}


.topic-time {
  padding: 4px 12px;
  background: #f7fafc;
  color: #2d3748;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.topic-tag {
  padding: 4px 8px;
  background: #f8fafc;
  color: #4a5568;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.topic-tag:hover {
  background: #e2e8f0;
  color: #2d3748;
}

/* How to Use Section */
.how-to-use-section {
  padding: 80px 0;
  background: #f8fafc;
}

.how-to-use-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 48px;
}

.how-to-use-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  text-decoration: none;
  color: #2d3748;
  transition: all 0.3s ease;
}

.how-to-use-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #93c5fd;
}

.how-to-use-icon {
  font-size: 1.5rem;
}

.how-to-use-title {
  font-weight: 500;
}

/* Popular Tags Section */
.popular-tags-section {
  padding: 80px 0;
  background: white;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 48px;
}

.popular-tag {
  padding: 8px 16px;
  background: #f8fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.popular-tag:hover {
  background: #e2e8f0;
  color: #2d3748;
  border-color: #cbd5e0;
}


/* Mobile Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-description {
    font-size: 1.1rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .topic-card {
    padding: 24px;
  }
  
  .how-to-use-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 0 80px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .container {
    padding: 0 16px;
  }
  
  .hero-content {
    padding: 0 16px;
  }
}
</style>