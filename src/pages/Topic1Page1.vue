<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import TwoPaneVisualizationSection from '../components/TwoPaneVisualizationSection.vue'

// Page metadata for search indexing
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

// Unified card system state - single active card across all sections
// 0-1: Limulus cards (2 cards), 2-4: Experiments cards (3 cards), 5-8: Inhibitory cards (4 cards)
const activeGlobalCard = ref<number>(0)

// Card data for Limulus section
const limulusCards = [
  {
    id: 'limulus-card-1',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">In the early 1930s, Hartline et al. chose <i>Limulus polyphemus</i>, a species of horseshoe crab, as a model organism for studying the optic nerve. Due to their ancient evolutionary lineage, the nervous system of <i>Limulus polyphemus</i> is relatively simple. Vision is a prominent component of this nervous system, making it ideal for Hartline's studies on the optic nerve.</p>`
  },
  {
    id: 'limulus-card-2', 
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;"><i>Limulus polyphemus</i> has multiple sets of eyes, but Hartline et al. focused on studying the lateral compound eyes. Although <i>Limulus polyphemus</i> is more closely related to arachnids, the lateral compound eye resembles the compound eyes of insects, as they are composed of repeating distinct units called ommatidia. Each ommatidium is connected to a nerve fiber, and these fibers combine to form the optic nerve.</p>`
  }
]

// Card data for Experiments section
const experimentsCards = [
  {
    id: 'experiments-card-1',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Hartline's experiments began with the isolation of a single neuron, since understanding the behavior of a single neuron creates a baseline for researching the overall behavior in the retina. The response of a neuron to different sensory inputs corresponds to the rate of action potentials, which can be measured using an oscillograph.<br/><br/>The experimental setup is very invasive, since the electrodes of the oscillograph must be directly connected to the nerve fiber. The location of the optic nerve can be estimated based on the locations of the lateral and median eyes. According to this position, a hole is drilled into the carapace of the horseshoe crab, and the recording chamber is lowered into the hole to isolate the optic nerve.</p>`
  },
  {
    id: 'experiments-card-2',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">After removing the excess connective tissue and the sheath around the nerve, a single nerve fiber is isolated. This fiber is then cut, and the newly cut loose end of the fiber is connected to an electrode. The electrode can detect when an action potential passes through this fiber, which is then recorded on the oscillograph.</p>`
  },
  {
    id: 'experiments-card-3',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">This type of setup was used for the majority of the experiments that Hartline did at this point. Conveniently, the visual field of a single neuron can be isolated by isolating an ommatidium.</p><p class="text-lg leading-relaxed" style="font-size: 18px;">We can learn a lot about visual processing from the behavior of a single neuron. The simplest situation is when a single light is repeatedly shone on a single ommatidium. To shine a light on a single ommatidium, a fiber optic light pipe is used to focus the light on a precise place. By doing so, when the light is shone on the ommatidium, the corresponding fiber in the optic nerve starts sending action potentials, which is what is measured by the oscillograph.</p>`
  }
]
const inhibitoryCards = [
  {
    id: 'inhibitory-card-1',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">Things get a little bit more complicated when working with multiple ommatidia at once. Hartline's key discovery was the concept of lateral inhibition, which describes how cells in the retina communicate with each other.</p>`
  },
  {
    id: 'inhibitory-card-2',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">An arbitrary ommatidium was chosen and a light was shone on this ommatidium. Then, light was shone on neighboring ommatidia, which caused some interesting results—the rate of action potentials decreased in the initially selected neuron. This means that having light on neighboring ommatidia inhibits the activity in the initial ommatidium's neuron, which is the general principle of lateral inhibition.</p>`
  },
  {
    id: 'inhibitory-card-3',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">This behavior comes with a host of different characteristics when tested with different intensities and different amounts of neighbors simulated. Brighter light on neighbors = more inhibition to the test receptor. In general: stronger light = stronger inhibition More neighbors illuminated = stronger combined inhibition (spatial summation) Closer neighbors = stronger inhibition.</p>`
  },
  {
    id: 'inhibitory-card-4',
    content: `<p class="text-lg leading-relaxed" style="font-size: 18px;">There were also some other events that occurred with the inhibition (but in general, and not corresponding to different dependent variables). They observed a period of post-inhibitory rebound, during which there is a brief increase in activity (usually even more than baseline with interaction at all) after the lights on neighboring receptors are turned off, which is a common response after an end to inhibition in neurons. Inhibition happens during hyperpolarization (being more negative makes it harder to reach threshold for action potential)—this behavior has already been seen in other parts of the brain, and was observed to work the same way in the limulus eye Although these observations are all important and play a large role in our understanding of lateral inhibition in sensory systems, the major observation is that inhibition is mutual: each ommatidium both inhibits and is inhibited by nearby ommatidia, as they are connected through the retina. Since all interactions are inhibitory, this tells us a lot about how visual processing works.</p>`
  }
]




// Handle card activation from TwoPaneVisualizationSection components
const handleLimulusCardActivated = (cardId: string, cardIndex: number) => {
  activeGlobalCard.value = cardIndex // 0 or 1
}

const handleExperimentsCardActivated = (cardId: string, cardIndex: number) => {
  activeGlobalCard.value = cardIndex + 2 // 2-4 (offset by 2 for experiments section)
}

const handleInhibitoryCardActivated = (cardId: string, cardIndex: number) => {
  activeGlobalCard.value = cardIndex + 5 // 5-8 (offset by 5 for inhibitory section)
}



// Unified watcher for active card changes - placeholder for future functionality
watch(activeGlobalCard, async (newCardIndex) => {
  await nextTick() // Wait for DOM updates
  
  // Future functionality can be added here based on active card changes
  // For example: updating 3D model states, analytics tracking, etc.
})
</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl">
      <div class="text-sm text-gray-600 mb-2"><br></div>
      <h1 class="text-4xl mb-6"style="font-size: 40px;">Visual receptors and retinal interaction</h1>
      <p class="text-xl text-gray-700 mb-6"style="font-size: 18px">
        H. K. Hartline, Nobel Lecture, 1967
      </p>
      
      <!-- Tags Section -->
      <div class="tags-section mb-8">
        <div class="flex flex-wrap items-center gap-3">
          <span class="text-xl text-gray-700" style="font-size: 18px">Tags: </span>
          <span
            v-for="tag in pageMetadata.tags"
            :key="tag"
            class="tag-chip"
          >
            #{{ tag }}
          </span>
        </div>
      </div>

      <p class="text-xl text-gray-700 mb-6"style="font-size: 18px">
        The Nobel Prize in Physiology or Medicine in 1967 was awarded jointly to Haldan Keffer Hartline, Ragnar Granit, and George Wald for their discoveries concerning visual processes. In his Nobel Lecture, Hartline explains his work on the concept of lateral inhibition, a defining characteristic of retinal interactions that demonstrates the importance of contrast in visual processing.
      </p>
      
      <!-- Section: Introducing Limulus polyphemus ---->
      <section id="introducing-limulus-polyphemus" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Introducing <i>Limulus polyphemus</i></h2>
          
          <TwoPaneVisualizationSection
            section-id="limulus-intro"
            model-path="/models/horseshoe_crab_basic.glb"
            :show-model="true"
            :cards="limulusCards"
            :global-active-card-index="activeGlobalCard < 2 ? activeGlobalCard : -1"
            @card-activated="handleLimulusCardActivated"
          />
        </div>
      </section>

      <!-- Section: Experiments with a single ommatidium ---->
      <section id="experiments-with-single-ommatidia" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Experiments with single ommatidia</h2>
          
          <TwoPaneVisualizationSection
            section-id="experiments"
            model-path="/models/horseshoe_crab_basic.glb"
            :show-model="true"
            :cards="experimentsCards"
            :global-active-card-index="activeGlobalCard >= 2 && activeGlobalCard <= 4 ? activeGlobalCard - 2 : -1"
            @card-activated="handleExperimentsCardActivated"
          />
        </div>
      </section>

      <!-- Section: Inhibitory interactions in the retina ---->
      <section id="inhibitory-interactions-in-the-retina" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Inhibitory interactions in the retina</h2>
          
          <TwoPaneVisualizationSection
            section-id="inhibitory-interactions"
            :show-model="false"
            :cards="inhibitoryCards"
            :global-active-card-index="activeGlobalCard >= 5 && activeGlobalCard <= 8 ? activeGlobalCard - 5 : -1"
            @card-activated="handleInhibitoryCardActivated"
          />
        </div>
      </section>

      <!-- Section: Mathematical models of mutual inhibition ---->
      <section id="mathematical-models-of-mutual-inhibition" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Mathematical models of mutual inhibition</h2>
          
          <TwoPaneVisualizationSection
            section-id="mathematical-models"
            model-path="/models/horseshoe_crab_basic.glb"
            :show-model="false"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6" style="font-size: 18px;">
                Statistical inference uses probability theory to draw conclusions about populations based on sample data.
                It provides methods for hypothesis testing, parameter estimation, and quantifying uncertainty in our conclusions.
              </p>
              
              <div class="bg-orange-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl mb-4">Inference Methods</h3>
                <ul class="list-disc list-inside space-y-2 text-lg" style="font-size: 18px;">
                  <li>Point estimation: Finding single best estimates of parameters</li>
                  <li>Interval estimation: Constructing confidence intervals</li>
                  <li>Hypothesis testing: Making decisions based on sample evidence</li>
                  <li>Bayesian inference: Incorporating prior knowledge</li>
                </ul>
              </div>
              
              <p class="text-lg leading-relaxed">
                These advanced concepts build upon basic probability theory to provide powerful tools for 
                data analysis, scientific research, and decision making under uncertainty.
              </p>
            </template>
          </TwoPaneVisualizationSection>
        </div>
      </section>

      <section id="research-with-dynamic-vision" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Research with dynamic vision</h2>
          
          <TwoPaneVisualizationSection
            section-id="mathematical-models"
            model-path="/models/horseshoe_crab_basic.glb"
            :show-model="false"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6" style="font-size: 18px;">
                Statistical inference uses probability theory to draw conclusions about populations based on sample data.
                It provides methods for hypothesis testing, parameter estimation, and quantifying uncertainty in our conclusions.
              </p>
              
              <div class="bg-orange-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl mb-4">Inference Methods</h3>
                <ul class="list-disc list-inside space-y-2 text-lg" style="font-size: 18px;">
                  <li>Point estimation: Finding single best estimates of parameters</li>
                  <li>Interval estimation: Constructing confidence intervals</li>
                  <li>Hypothesis testing: Making decisions based on sample evidence</li>
                  <li>Bayesian inference: Incorporating prior knowledge</li>
                </ul>
              </div>
              
              <p class="text-lg leading-relaxed">
                These advanced concepts build upon basic probability theory to provide powerful tools for 
                data analysis, scientific research, and decision making under uncertainty.
              </p>
            </template>
          </TwoPaneVisualizationSection>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: calc(100vh - 4rem);
}

/* Reading Card Styles */
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

.reading-card p {
  margin: 0;
  color: inherit;
}

/* Tags Section Styles */
.tags-section {
  padding: 0;
}

.tag-chip {
  display: inline-block;
  padding: 6px 12px;
  background-color: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  margin-right: 8px;
  transition: all 0.2s ease;
}

.tag-chip:hover {
  background-color: #e5e7eb;
  color: #374151;
}
</style>