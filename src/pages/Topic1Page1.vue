<script setup lang="ts">
import { ref, watch } from 'vue'
import TwoPaneVisualizationSection from '../components/TwoPaneVisualizationSection.vue'
import Shared3DModelViewer from '../components/Shared3DModelViewer.vue'

const pageMetadata = {
  id: 'topic1-page1',
  title: 'Visual receptors and retinal interaction',
  content: 'The Nobel Prize in Physiology or Medicine in 1967 was awarded jointly to Haldan Keffer Hartline, Ragnar Granit, and George Wald for their discoveries concerning visual processes. In his Nobel Lecture, Hartline explains his work on the concept of lateral inhibition, a defining characteristic of retinal interactions that demonstrates the importance of contrast in visual processing.',
  excerpt: 'the basic mechanism of the receptor is one that emphasizes change.',
  path: '/topic1/page1',
  tags: ['model organisms', 'vision', 'retina', 'lateral-inhibition'],
  category: 'Senses',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 1',
    difficulty: 'beginner' as const,
    estimatedReadTime: 12
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}

// --- Card Content Definitions ---
const limulusCard1 = {
  id: 'limulus-card-1',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">In the early 1930s, Hartline et al. chose <i>Limulus polyphemus</i>, a species of horseshoe crab, as a model organism for studying the optic nerve. Due to their ancient evolutionary lineage, the nervous system of <i>Limulus polyphemus</i> is relatively simple. Vision is a prominent component of this nervous system, making it ideal for Hartline's studies on the optic nerve.</p>`
}
const limulusCard2 = { 
  id: 'limulus-card-2', 
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;"><i>Limulus polyphemus</i> has multiple sets of eyes, but Hartline et al. focused on studying the lateral compound eyes. Although <i>Limulus polyphemus</i> is more closely related to arachnids, the lateral compound eye resembles the compound eyes of insects, as they are composed of repeating distinct units called ommatidia. Each ommatidium is connected to a nerve fiber, and these fibers combine to form the optic nerve.</p>`
}
const experimentsCard1 = {
  id: 'experiments-card-1',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Hartline's experiments began with the isolation of a single neuron, since understanding the behavior of a single neuron creates a baseline for researching the overall behavior in the retina. The response of a neuron to different sensory inputs corresponds to the rate of action potentials, which can be measured using an oscillograph.<br/><br/>The experimental setup is very invasive, since the electrodes of the oscillograph must be directly connected to the nerve fiber. The location of the optic nerve can be estimated based on the locations of the lateral and median eyes. According to this position, a hole is drilled into the carapace of the horseshoe crab, and the recording chamber is lowered into the hole to isolate the optic nerve.</p>`
}


// Change: A single, unified state tracking the active card's ID. Much simpler than offsets.
const activeCardId = ref<string>(limulusCard1.id) // Set an initial active card

interface StoryBlock {
  type: 'sticky-model-group' | 'text-only-section'
  modelPath?: string
  cards?: Array<{id: string, content: string}>
  title?: string
  useSlotContent?: boolean
}

// Change: A new data structure that defines the layout of the entire page.
const storyBlocks = ref([
  {
    type: 'sticky-model-group',
    modelPath: '/models/horseshoe_crab_basic.glb',
    // Change: 'cards' array is now an 'items' array with typed objects.
    items: [
      { 
        type: 'card' as const, 
        id: 'limulus-card-1', 
        content: limulusCard1.content
      },
      { 
        type: 'card' as const, 
        id: 'limulus-card-2', 
        content: limulusCard2.content
      },
      { 
        type: 'heading' as const, 
        text: 'Experiments with single ommatidia' 
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-1', 
        content: experimentsCard1.content
      },
    ]
  },
]);

// Change: A single, simplified event handler.
const handleCardActivation = (cardId: string) => {
  activeCardId.value = cardId
}

// Watcher remains useful for triggering future 3D animations or analytics.
watch(activeCardId, (newId) => {
  console.log(`Active card changed to: ${newId}`)
  // Future logic:
  // - Tell the 3D model to change its state/animation.
  // - Send an analytics event.
})

</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl mx-auto">
      <div class="text-sm text-gray-600 mb-2"><br></div>
      <h1 class="text-4xl mb-6"style="font-size: 40px;">Visual receptors and retinal interaction</h1>
      <p class="text-xl text-gray-700 mb-6"style="font-size: 18px">
        H. K. Hartline, Nobel Lecture, 1967
      </p>
      <div class="tags-section mb-8">
        <div class="flex flex-wrap items-center gap-3">
          <span class="text-xl text-gray-700" style="font-size: 18px">Tags: </span>
          <span v-for="tag in pageMetadata.tags" :key="tag" class="tag-chip">#{{ tag }}</span>
        </div>
      </div>
      <p class="text-xl text-gray-700 mb-6"style="font-size: 18px">
        The Nobel Prize in Physiology or Medicine in 1967 was awarded jointly to Haldan Keffer Hartline, Ragnar Granit, and George Wald for their discoveries concerning visual processes. In his Nobel Lecture, Hartline explains his work on the concept of lateral inhibition, a defining characteristic of retinal interactions that demonstrates the importance of contrast in visual processing.
      </p>
      
      <div v-for="(block, index) in storyBlocks" :key="index">
        
        <section v-if="block.type === 'sticky-model-group'" class="sticky-group-container">
          <div class="cards-column">
            <TwoPaneVisualizationSection
              :section-id="`group-${index}`"
              :show-model="false"
              :items="block.items"
              :active-card-id="activeCardId"
              @card-activated="handleCardActivation"
            />
          </div>
          <div class="model-column-sticky">
            <Shared3DModelViewer
              :container-id="`sticky-model-${index}`"
              :model-path="block.modelPath!"
            />
          </div>
        </section>
        
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Change: Added new styles for the sticky layout */
.sticky-group-container {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  margin-bottom: 4rem;
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

.tag-chip {
  display: inline-block;
  padding: 6px 12px;
  background-color: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  font-size: 14px;
}
</style>