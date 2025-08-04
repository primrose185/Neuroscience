<script setup lang="ts">
import { ref, watch, computed, onMounted, defineEmits } from 'vue'
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

const emit = defineEmits(['update-menu']);
const pageMenuItems = computed(() => {
  // Find all headings within both story block groups
  const headings = [
    ...storyBlocksGroup1.value.flatMap(block =>
      (block.items || []).filter(item => item?.type === 'heading')
    )
  ];

  // The base menu item for the current page
  const mainMenuItem = {
    id: pageMetadata.id,
    title: pageMetadata.title,
    path: pageMetadata.path,
    // Map the found headings to the format the sidebar expects
    children: headings.map(heading => ({
      id: heading.id,
      title: heading.text,
      // Create the path with a hash for scrolling: /topic1/page1#heading-id
      path: `${pageMetadata.path}#${heading.id}`
    }))
  };
  
  return [mainMenuItem];
});

// When the component mounts, emit the generated menu data
onMounted(() => {
  emit('update-menu', pageMenuItems.value);
});

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
const experimentsCard2 = {
  id: 'experiments-card-2',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">After removing the excess connective tissue and the sheath around the nerve, a single nerve fiber is isolated. This fiber is then cut, and the newly cut loose end of the fiber is connected to an electrode. The electrode can detect when an action potential passes through this fiber, which is then recorded on the oscillograph.</p>`
}
const experimentsCard3 = {
  id: 'experiments-card-3',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">This setup was used for many of Hartline's experiments, especially those that required the isolation of specific neurons. Conveniently, the visual field of a single neuron can be isolated by targeting the corresponding ommatidium and stimulating it with a precise fiber-optic light.<br/><br/>In the simplest configuration, a single ommatidium is illuminated. Using light to stimulate the ommatidium produces action potentials in the corresponding optic nerve fiber, which are recorded by the oscillograph.</p>`
}
const experimentsCard4 = {
  id: 'experiments-card-4',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">The above model illustrates the simulated activity of a bipolar neuron in the optic nerve, and the corresponding graph displays the results from the oscilloscope. Every spike in the graph represents an action potential, and smaller spaces between each spike indicate a higher rate of activity. To explore how stimulus strength affected the activity in the neuron, Hartline also varied the intensity of the light.</p>`
}
const experimentsCard5 = {
  id: 'experiments-card-5',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Two major observations were made through this experimental configuration. The first observation confirmed that the frequency of action potentials increases as the intensity of the light increases. Although this concept was already theorized before Hartline's experiments, the quantitative evidence gathered from single neurons was limited, and Hartline was the first to do so with the optic nerve.</p>`
}
const experimentsCard6 = {
  id: 'experiments-card-6',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">The second major observation is that the neuron fires at different frequencies depending on when the stimulus is introduced, firing more rapidly when the light is first turned on. The activity of the neuron decreases once the light is held steady.<br/><br/>This behavior reaffirms the concept of sensory adaptation, which describes the tendency of sensory systems to react and adjust to changes in the environment. The initial frequency is faster in response to the onset of light stimulation, indicating a sudden increase in intensity, which then stabilizes into a more regular rate of firing.</p>`
}
const experimentsCard7 = {
  id: 'experiments-card-7',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Hartline notes that “the basic mechanism of the receptor is one that emphasizes change.” These experiments on single fibers in the optic nerve are early demonstrations of a recurring theme in research on sensory systems.</p>`
}
const interactionsCard1 = {
  id: 'interactions-card-1',
  content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Working with multiple ommatidia is more complicated, as the interactions between the receptors must be factored in. Hartline's key discovery was the concept of lateral inhibition, which describes how cells in the retina communicate with each other.</p>`
}

const activeCardId = ref<string>(limulusCard1.id) // Set an initial active card
const currentModelPath = ref('/models/horseshoe_crab_basic.glb') // Reactive model path for dynamic switching

interface StoryBlock {
  type: 'sticky-model-group' | 'full-width-sticky-model' | 'text-only-section'
  modelPath?: string
  cards?: Array<{id: string, content: string}>
  title?: string
  useSlotContent?: boolean
  modelWidth?: number
  modelHeight?: number
  items?: Array<{type: 'card' | 'heading', id?: string, text?: string, content?: string}>
}

// First group: Introduction and basic experiments
const storyBlocksGroup1 = ref([
  {
    type: 'sticky-model-group',
    modelPath: '/models/horseshoe_crab_basic.glb',
    items: [
      { 
        type: 'heading' as const, 
        id: 'introducing-limulus-polyphemus',
        text: 'Introducing Limulus polyphemus' 
      },
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
        id: 'experiments-with-single-ommatidia',
        text: 'Experiments with single ommatidia' 
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-1', 
        content: experimentsCard1.content
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-2', 
        content: experimentsCard2.content
      },
    ]
  },
]);

// Second group: Advanced experiments with full-width model
const storyBlocksGroup2 = ref([
  {
    type: 'full-width-sticky-model',
    modelPath: '/models/blenderSpike_test.glb',
    items: [
      { 
        type: 'card' as const, 
        id: 'experiments-card-4', 
        content: experimentsCard4.content
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-5', 
        content: experimentsCard5.content
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-6', 
        content: experimentsCard6.content
      },
      { 
        type: 'card' as const, 
        id: 'experiments-card-7', 
        content: experimentsCard7.content
      },
    ]
  },
]);

// Change: A single, simplified event handler.
const handleCardActivation = (cardId: string) => {
  activeCardId.value = cardId
}

// Watcher for card changes and model switching
watch(activeCardId, (newId) => {
  console.log(`Active card changed to: ${newId}`)
  
  // Switching models
  if (newId === 'experiments-card-1') {
    currentModelPath.value = '/models/recordingChamber_hscrab.glb'
  } else if (newId === 'experiments-card-2') {
    currentModelPath.value = '/models/electrode_hscrab.glb'
  } else if (newId === 'limulus-card-1') {
    // Switch back to basic model if going back to card 1
    currentModelPath.value = '/models/horseshoe_crab_basic.glb'
  }
  
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
      
      <!-- First story block group: Introduction and basic experiments -->
      <div v-for="(block, index) in storyBlocksGroup1" :key="`group1-${index}`">
        <section v-if="block.type === 'sticky-model-group'" class="sticky-group-container">
          <div class="cards-column">
            <TwoPaneVisualizationSection
              :section-id="`group1-${index}`"
              :show-model="false"
              :items="block.items"
              :active-card-id="activeCardId"
              @card-activated="handleCardActivation"
            />
          </div>
          <div class="model-column-sticky">
            <Shared3DModelViewer
              :container-id="`sticky-model-group1-${index}`"
              :model-path="currentModelPath"
              :width="400"
              :height="700"
            />
          </div>
        </section>
      </div>

      <!-- Transition section: experimentsCard3 -->
      <TwoPaneVisualizationSection
        section-id="experiments-part-3"
        :show-model="false"
        :items="[{ 
          type: 'card', 
          id: experimentsCard3.id, 
          content: experimentsCard3.content 
        }]"
        :active-card-id="activeCardId"
        @card-activated="handleCardActivation"
      />

      <!-- Second story block group: Advanced experiments with full-width model -->
      <div v-for="(block, index) in storyBlocksGroup2" :key="`group2-${index}`">
        <section v-if="block.type === 'full-width-sticky-model'" class="full-width-sticky-container">
          <div class="full-width-model-sticky">
            <Shared3DModelViewer
              :container-id="`full-width-model-group2-${index}`"
              :model-path="block.modelPath!"
              :width=1000
              :height=200
            />
          </div>
          <div class="full-width-cards-column">
            <TwoPaneVisualizationSection
              :section-id="`full-width-group2-${index}`"
              :show-model="false"
              :items="block.items"
              :active-card-id="activeCardId"
              @card-activated="handleCardActivation"
            />
          </div>
        </section>
      </div>

      <TwoPaneVisualizationSection
        section-id="inhibitory-interactions-in-the-retina"
        :show-model="false"
        :items="[
          { 
            type: 'heading' as const, 
            id: 'inhibitory-interactions-in-the-retina',
            text: 'Inhibitory interactions in the retina' 
          },
          {
            type: 'card' as const, 
            id: 'interactions-card-1', 
            content: interactionsCard1.content
          }
        ]"
        :active-card-id="activeCardId"
        @card-activated="handleCardActivation"
      />
      
      <p class="text-xl text-gray-700 mb-6"style="font-size: 18px">
        <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
      </p>
      
    </div>
  </div>
</template>

<style scoped>
/* Change: Added new styles for the sticky layout */
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

.tag-chip {
  display: inline-block;
  padding: 6px 12px;
  background-color: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  font-size: 14px;
  margin-right: 6px
}
</style>