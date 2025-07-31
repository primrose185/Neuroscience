<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, inject, nextTick, computed } from 'vue'
import Shared3DModelViewer from './Shared3DModelViewer.vue'

interface CardData {
  id: string
  content: string
  active?: boolean
}

interface Props {
  sectionId: string
  cards?: CardData[]
  modelPath?: string
  showModel?: boolean
  viewerOptions?: object
}

const props = withDefaults(defineProps<Props>(), {
  cards: () => [],
  modelPath: "/models/horseshoe_crab_basic.glb",
  showModel: false,
  viewerOptions: () => ({})
})

const emit = defineEmits<{
  cardActivated: [cardId: string, cardIndex: number]
}>()

// Refs for cards
const cardRefs = ref<HTMLElement[]>([])
const activeCardIndex = ref<number>(-1)

// Track if we're using cards prop or slot content
const usingCardsProp = computed(() => props.cards && props.cards.length > 0)


// Setup card intersection observer
const setupCardObserver = () => {
  if (!usingCardsProp.value || cardRefs.value.length === 0) return
  
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -20% 0px',
    threshold: 0.6
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const cardElement = entry.target as HTMLElement
        const cardIndex = cardRefs.value.findIndex(ref => ref === cardElement)
        
        if (cardIndex !== -1 && cardIndex !== activeCardIndex.value) {
          activeCardIndex.value = cardIndex
          const card = props.cards![cardIndex]
          emit('cardActivated', card.id, cardIndex)
        }
      }
    })
  }, observerOptions)
  
  // Observe all card elements
  cardRefs.value.forEach(cardRef => {
    if (cardRef) observer.observe(cardRef)
  })
  
  return observer
}

onMounted(async () => {
  let cardObserver: IntersectionObserver | null = null
  
  // Setup card observer if using cards prop
  if (usingCardsProp.value) {
    await nextTick() // Wait for DOM to be ready
    cardObserver = setupCardObserver()
  }
  
  // Store observer for cleanup
  onBeforeUnmount(() => {
    if (cardObserver) {
      cardObserver.disconnect()
    }
  })
})
</script>

<template>
  <div class="two-pane-section">
    <!-- Conditional layout: single column or two-column based on showModel -->
    <div class="layout-container" :class="{ 'two-column-layout': showModel, 'single-column-layout': !showModel }">
      <!-- Left Column: Cards or Slot Content (full width when showModel=false) -->
      <div ref="contentColumnRef" class="content-column">
        <!-- Cards from props (new system) -->
        <div v-if="usingCardsProp" class="cards-container">
          <div
            v-for="(card, index) in cards"
            :key="card.id"
            :ref="el => { if (el) cardRefs[index] = el as HTMLElement }"
            class="reading-card mb-6"
            :class="{ 
              'active': activeCardIndex === index || card.active, 
              'inactive': activeCardIndex !== index && !card.active 
            }"
          >
            <div v-html="card.content"></div>
          </div>
        </div>
        
        <!-- Slot content (backward compatibility) -->
        <div v-else>
          <slot name="content"></slot>
        </div>
      </div>
      
      <!-- Right Column: 3D Visualization (only shown when showModel=true) -->
      <div 
        v-if="showModel"
        ref="visualizationColumnRef"
        class="visualization-column"
      >
        <Shared3DModelViewer
          :container-id="`${sectionId}-model-container`"
          :model-path="modelPath!"
          :viewer-options="viewerOptions"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.two-pane-section {
  width: 100%;
}

.layout-container {
  width: 100%;
}

.two-column-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.single-column-layout {
  display: flex;
  flex-direction: column;
}

.content-column {
  flex: 1;
  min-width: 0;
}

.cards-container {
  width: 100%;
}

/* Card Styles */
.reading-card {
  padding: 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

/* Active Card - Currently Reading */
.reading-card.active {
  background-color: #f8f9fa;
  border-left: 3px solid #3b82f6;
  color: #1f2937;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateX(4px);
}

/* Inactive Card - Not Currently Reading */
.reading-card.inactive {
  background-color: transparent;
  border-left: 3px solid transparent;
  color: #6b7280;
  box-shadow: none;
  transform: translateX(0);
}

/* Ensure smooth transitions for all card properties */
.reading-card :deep(p) {
  margin: 0;
  transition: color 0.3s ease;
}

.visualization-column {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* Responsive Design */
@media (max-width: 768px) {
  /* Stack columns on tablet when showing model */
  .two-column-layout {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .visualization-column {
    align-self: center;
  }
}
</style>