<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import Shared3DModelViewer from '../components/Shared3DModelViewer.vue'

interface CardItem {
  type: 'card'
  id: string
  content: string
}
interface HeadingItem {
  type: 'heading'
  text: string
}
type ListItem = CardItem | HeadingItem

interface Props {
  sectionId: string
  items?: ListItem[]
  modelPath?: string
  showModel?: boolean
  viewerOptions?: object
  activeCardId?: string
}

const props = withDefaults(defineProps<Props>(), {
  items: () => [],
  modelPath: "/models/horseshoe_crab_basic.glb",
  showModel: false,
  viewerOptions: () => ({}),
  activeCardId: ''
})

const emit = defineEmits<{
  cardActivated: [cardId: string, cardIndex: number]
}>()

const activateCard = (card: CardItem, index: number) => {
  emit('cardActivated', card.id, index)
}

const cardRefs = ref<HTMLElement[]>([])
const usingItemsProp = computed(() => props.items && props.items.length > 0)

const setupCardObserver = () => {
  if (!usingItemsProp.value || cardRefs.value.length === 0) return
  
  const observerOptions = {
    root: null,
    rootMargin: '-10% 0px -10% 0px',
    threshold: 0.4
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const cardElement = entry.target as HTMLElement
        // Find the original item index based on the element's ref
        const itemIndex = cardRefs.value.findIndex(ref => ref === cardElement)
        if (itemIndex === -1) return

        const item = props.items![itemIndex]
        
        // Only proceed if the item is a card and not already active
        if (item.type === 'card' && item.id !== props.activeCardId) {
          emit('cardActivated', item.id, itemIndex)
        }
      }
    })
  }, observerOptions)
  
  // Observe all card elements (refs for headings will be null)
  cardRefs.value.forEach(cardRef => {
    if (cardRef) observer.observe(cardRef)
  })
  
  return observer
}

onMounted(async () => {
  let cardObserver: IntersectionObserver | null = null
  if (usingItemsProp.value) {
    await nextTick()
    cardObserver = setupCardObserver()
  }
  
  onBeforeUnmount(() => {
    if (cardObserver) {
      cardObserver.disconnect()
    }
  })
})
</script>

<template>
  <div class="two-pane-section">
    <div class="layout-container" :class="{ 'two-column-layout': showModel, 'single-column-layout': !showModel }">
      <div class="content-column">
        <div v-if="usingItemsProp" class="cards-container">
          <template v-for="(item, index) in items" :key="item.type === 'card' ? item.id : index">
            
            <div
              v-if="item.type === 'card'"
              :ref="el => { if (el) cardRefs[index] = el as HTMLElement }"
              class="reading-card"
              :class="{ 
                'active': activeCardId === item.id, 
                'inactive': activeCardId !== item.id 
              }"
              @click="activateCard(item, index)"
            >
              <div v-html="item.content"></div>
            </div>

            <h2 v-else-if="item.type === 'heading'" class="text-3xl mt-12 mb-6">
              {{ item.text }}
            </h2>

          </template>
        </div>
        
        <div v-else>
          <slot name="content"></slot>
        </div>
      </div>
      
      <div v-if="showModel" class="visualization-column">
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

.reading-card {
  padding: 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.reading-card.active {
  background-color: #f8f9fa;
  border-left: 3px solid #3b82f6;
  color: #1f2937;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateX(4px);
}

.reading-card.inactive {
  background-color: transparent;
  border-left: 3px solid transparent;
  color: #6b7280;
  box-shadow: none;
  transform: translateX(0);
  cursor: pointer;
}

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

@media (max-width: 768px) {
  .two-column-layout {
    flex-direction: column;
    gap: 1.5rem;
  }
  .visualization-column {
    align-self: center;
  }
}
</style>