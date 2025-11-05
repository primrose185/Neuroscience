<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import TwoPaneVisualizationSection from './TwoPaneVisualizationSection.vue'
import Shared3DModelViewer from './Shared3DModelViewer.vue'
import type {
  StoryBlockGroup,
  ViewerOptions,
  ModelDimensions,
  CardActivationEvent
} from '../types/stickyStoryBlocks'

interface Props {
  groups: StoryBlockGroup[]
  cardToModelMap?: Record<string, string>
  modelConfigurations?: Record<string, ViewerOptions>
  initialActiveCardId?: string
  sideModelDimensions?: ModelDimensions
  fullWidthModelDimensions?: ModelDimensions
}

const props = withDefaults(defineProps<Props>(), {
  cardToModelMap: () => ({}),
  modelConfigurations: () => ({}),
  initialActiveCardId: '',
  sideModelDimensions: () => ({ width: 400, height: 700 }),
  fullWidthModelDimensions: () => ({ width: 1000, height: 200 })
})

const emit = defineEmits<{
  cardActivated: [event: CardActivationEvent]
  modelSwitched: [event: { oldPath: string, newPath: string }]
}>()

// State management
const activeCardId = ref<string>(props.initialActiveCardId)
const modelViewerRefs = ref<Map<number, any>>(new Map())

// Get initial model path from first sticky-model-group
const getInitialModelPath = (): string => {
  const firstStickyGroup = props.groups.find(g => g.type === 'sticky-model-group')
  return firstStickyGroup?.modelPath || ''
}

const currentModelPath = ref<string>(getInitialModelPath())

// Default viewer options
const defaultViewerOptions: ViewerOptions = {
  camera: {
    position: { x: 5, y: 5, z: 5 },
    fov: 60,
    near: 0.1,
    far: 1000
  },
  fitCamera: false
}

// Get viewer options for a specific model path
const getViewerOptions = (modelPath: string): ViewerOptions => {
  return props.modelConfigurations[modelPath] || defaultViewerOptions
}

// Computed property for current viewer options based on active model
const currentViewerOptions = computed(() => {
  return getViewerOptions(currentModelPath.value)
})

// Calculate custom rootMargin for full-width sticky layout
// This shifts the detection zone down to account for the sticky model at the top
const fullWidthObserverRootMargin = computed(() => {
  // Calculate total height occupied by sticky model
  const topOffset = 16  // top: 1rem in pixels
  const padding = 32    // padding: 1rem top + 1rem bottom
  const modelHeight = props.fullWidthModelDimensions.height
  const marginBottom = 16  // margin-bottom: 1rem
  const cardsPaddingTop = 16  // padding-top: 1rem from .full-width-cards-column

  const totalHeight = topOffset + padding + modelHeight + marginBottom + cardsPaddingTop

  // Add buffer for smooth activation transitions
  const buffer = 60
  const adjustedTopMargin = totalHeight + buffer

  // Return rootMargin with pixel-based top offset to shift detection zone below sticky model
  // Bottom margin remains percentage-based (20%) for consistent bottom detection
  return `-${adjustedTopMargin}px 0px -20% 0px`
})

// Get current model path for a group (handles dynamic switching for sticky-model-group)
const getCurrentModelPath = (groupIndex: number, group: StoryBlockGroup): string => {
  if (group.type === 'sticky-model-group') {
    // For sticky-model-group, use the reactive currentModelPath
    return currentModelPath.value
  } else {
    // For full-width-sticky-model, use the static modelPath from group
    return group.modelPath
  }
}

// Set model viewer ref for a specific group
const setModelViewerRef = (groupIndex: number, el: any) => {
  if (el) {
    modelViewerRefs.value.set(groupIndex, el)
  }
}

// Handle card activation from child components
const handleCardActivation = (cardId: string, cardIndex?: number) => {
  // Prevent re-activation of already active card
  if (activeCardId.value === cardId) {
    return
  }

  activeCardId.value = cardId

  // Find which group this card belongs to
  let groupIndex = 0
  let modelPath = currentModelPath.value

  for (let i = 0; i < props.groups.length; i++) {
    const group = props.groups[i]
    const cardExists = group.items?.some(item => item.id === cardId)
    if (cardExists) {
      groupIndex = i
      modelPath = group.modelPath
      break
    }
  }

  emit('cardActivated', {
    cardId,
    cardIndex: cardIndex || 0,
    groupIndex,
    modelPath
  })
}

// Watch for card changes and handle model switching
watch(activeCardId, (newId, oldId) => {
  console.log(`Active card changed to: ${newId}`)

  // Check if there's a mapping for this card to a specific model
  if (props.cardToModelMap[newId]) {
    const newPath = props.cardToModelMap[newId]
    const oldPath = currentModelPath.value

    currentModelPath.value = newPath

    emit('modelSwitched', {
      oldPath,
      newPath
    })

    // Reset camera position after model change with a small delay
    setTimeout(() => {
      // Find the first sticky-model-group and reset its camera
      const stickyGroupIndex = props.groups.findIndex(g => g.type === 'sticky-model-group')
      if (stickyGroupIndex !== -1) {
        const viewer = modelViewerRefs.value.get(stickyGroupIndex)
        if (viewer && typeof viewer.resetCamera === 'function') {
          viewer.resetCamera()
        }
      }
    }, 500)
  }
})

// Exposed methods for parent components
const setActiveCard = (cardId: string) => {
  activeCardId.value = cardId
}

const resetCamera = (groupIndex?: number) => {
  if (groupIndex !== undefined) {
    const viewer = modelViewerRefs.value.get(groupIndex)
    if (viewer && typeof viewer.resetCamera === 'function') {
      viewer.resetCamera()
    }
  } else {
    // Reset all cameras
    modelViewerRefs.value.forEach(viewer => {
      if (viewer && typeof viewer.resetCamera === 'function') {
        viewer.resetCamera()
      }
    })
  }
}

const getCurrentModel = (groupIndex: number): string => {
  const group = props.groups[groupIndex]
  if (!group) return ''
  return getCurrentModelPath(groupIndex, group)
}

defineExpose({
  setActiveCard,
  resetCamera,
  getCurrentModel
})
</script>

<template>
  <div class="sticky-story-blocks">
    <div v-for="(group, groupIndex) in groups" :key="`group-${groupIndex}`">
      <!-- Side-by-side sticky layout -->
      <section v-if="group.type === 'sticky-model-group'" class="sticky-group-container">
        <div class="cards-column">
          <TwoPaneVisualizationSection
            :section-id="`sticky-group-${groupIndex}`"
            :show-model="false"
            :items="group.items"
            :active-card-id="activeCardId"
            @card-activated="handleCardActivation"
          />
        </div>
        <div class="model-column-sticky">
          <Shared3DModelViewer
            :ref="(el: any) => setModelViewerRef(groupIndex, el)"
            :container-id="`sticky-model-${groupIndex}`"
            :model-path="getCurrentModelPath(groupIndex, group)"
            :viewer-options="currentViewerOptions"
            :width="sideModelDimensions.width"
            :height="sideModelDimensions.height"
          />
        </div>
      </section>

      <!-- Full-width sticky layout -->
      <section v-else-if="group.type === 'full-width-sticky-model'" class="full-width-sticky-container">
        <div class="full-width-model-sticky">
          <Shared3DModelViewer
            :ref="(el: any) => setModelViewerRef(groupIndex, el)"
            :container-id="`full-width-model-${groupIndex}`"
            :model-path="group.modelPath"
            :viewer-options="getViewerOptions(group.modelPath)"
            :width="fullWidthModelDimensions.width"
            :height="fullWidthModelDimensions.height"
          />
        </div>
        <div class="full-width-cards-column">
          <TwoPaneVisualizationSection
            :section-id="`full-width-group-${groupIndex}`"
            :show-model="false"
            :items="group.items"
            :active-card-id="activeCardId"
            :observer-root-margin="fullWidthObserverRootMargin"
            @card-activated="handleCardActivation"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* Side-by-side sticky layout */
.sticky-group-container {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.cards-column {
  flex: 1;
  min-width: 0;
}

.model-column-sticky {
  flex: 1;
  position: sticky;
  top: 2rem;
  height: calc(100vh - 4rem);
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .sticky-group-container {
    flex-direction: column;
  }
  .model-column-sticky {
    width: 100%;
    height: 50vh;
    position: sticky;
    top: 1rem;
  }
}

/* Full-width sticky model layout */
.full-width-sticky-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 0rem 0;
}

.full-width-model-sticky {
  width: 100%;
  top: 1rem;
  position: sticky;
  background: white;
  margin-bottom: 1rem;
  z-index: 10;
  padding: 1rem;
}

.full-width-cards-column {
  width: 100%;
  padding-top: 1rem;
}
</style>
