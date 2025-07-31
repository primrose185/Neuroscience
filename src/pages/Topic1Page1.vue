<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import TwoPaneVisualizationSection from '../components/TwoPaneVisualizationSection.vue'

// Page metadata for search indexing
const pageMetadata = {
  id: 'topic1-page1',
  title: 'Visual receptors and retinal interaction',
  content: 'Abstract text',
  excerpt: 'Complete guide to probability theory from basic concepts to advanced applications.',
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
// 0: Limulus card 1, 1: Limulus card 2, 2: Experiments card 1, 3: Experiments card 2
const activeGlobalCard = ref<number>(0)

// Card refs for intersection observer - Limulus section
const card1Ref = ref<HTMLElement | null>(null)
const card2Ref = ref<HTMLElement | null>(null)

// Card refs for intersection observer - Experiments section
const expCard1Ref = ref<HTMLElement | null>(null)
const expCard2Ref = ref<HTMLElement | null>(null)


// Function to center the active card in viewport
const scrollToCenter = (cardRef: HTMLElement) => {
  if (cardRef) {
    cardRef.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    })
  }
}


onMounted(async () => {
  
  // Setup Intersection Observer for card activation
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -20% 0px',
    threshold: 0.6
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const target = entry.target as HTMLElement
        // Unified global card system - only one active card across all sections
        if (target === card1Ref.value) {
          activeGlobalCard.value = 0 // Limulus card 1
        } else if (target === card2Ref.value) {
          activeGlobalCard.value = 1 // Limulus card 2
        } else if (target === expCard1Ref.value) {
          activeGlobalCard.value = 2 // Experiments card 1
        } else if (target === expCard2Ref.value) {
          activeGlobalCard.value = 3 // Experiments card 2
        }
      }
    })
  }, observerOptions)
  
  // Start observing cards when they're available
  if (card1Ref.value) observer.observe(card1Ref.value)
  if (card2Ref.value) observer.observe(card2Ref.value)
  if (expCard1Ref.value) observer.observe(expCard1Ref.value)
  if (expCard2Ref.value) observer.observe(expCard2Ref.value)
  
  // Store observer for cleanup
  onBeforeUnmount(() => {
    observer.disconnect()
  })
})


// Helper function to get card reference by global index
const getCardRefByIndex = (index: number): HTMLElement | null => {
  switch (index) {
    case 0: return card1Ref.value       // Limulus card 1
    case 1: return card2Ref.value       // Limulus card 2
    case 2: return expCard1Ref.value    // Experiments card 1
    case 3: return expCard2Ref.value    // Experiments card 2
    default: return null
  }
}

// Unified watcher for active card changes - centers active card in viewport
watch(activeGlobalCard, async (newCardIndex) => {
  await nextTick() // Wait for DOM updates
  
  // Add small delay to let card activation animation complete
  setTimeout(() => {
    const cardRef = getCardRefByIndex(newCardIndex)
    if (cardRef) {
      scrollToCenter(cardRef)
    }
  }, 100) // 100ms delay for smooth experience
})
</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl">
      <div class="text-sm text-gray-600 mb-2"><br></div>
      <h1 class="text-4xl mb-6"style="font-size: 40px;">Visual receptors and retinal interaction</h1>
      <p class="text-xl text-gray-700 mb-8"style="font-size: 18px">
        H. K. Hartline, Nobel Lecture, 1967
      </p>
      
      <!-- Section: Introducing Limulus polyphemus ---->
      <section id="introducing-limulus-polyphemus" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Introducing <i>Limulus polyphemus</i></h2>
          
          <TwoPaneVisualizationSection
            section-id="limulus-intro"
            model-path="/models/horseshoe_crab_basic.glb"
            :show-model="true"
          >
            <template #content>
              <!-- Card 1: Model organism selection -->
              <div 
                ref="card1Ref"
                class="reading-card mb-6"
                :class="{ 'active': activeGlobalCard === 0, 'inactive': activeGlobalCard !== 0 }"
              >
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  In the early 1930s, Hartline et al. chose <i>Limulus polyphemus</i>, a species of horseshoe crab, as a model organism for studying the optic nerve. Due to their ancient evolutionary lineage, the nervous system of <i>Limulus polyphemus</i> is relatively simple. Vision is a prominent component of this nervous system, making it ideal for Hartline's studies on the optic nerve.
                </p>
              </div>
              
              <!-- Card 2: Compound eye structure -->
              <div 
                ref="card2Ref"
                class="reading-card mb-6"
                :class="{ 'active': activeGlobalCard === 1, 'inactive': activeGlobalCard !== 1 }"
              >
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  <i>Limulus polyphemus</i> has multiple sets of eyes, but Hartline et al. focused on studying the lateral compound eyes. Although <i>Limulus polyphemus</i> is more closely related to arachnids, the lateral compound eye resembles the compound eyes of insects, as they are composed of repeating distinct units called ommatidia. Each ommatidium is connected to a nerve fiber, and these fibers combine to form the optic nerve.
                </p>
              </div>
            </template>
          </TwoPaneVisualizationSection>
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
          >
            <template #content>
              <!-- Experiments Card 1: Setup and recording procedure -->
              <div 
                ref="expCard1Ref"
                class="reading-card mb-6"
                :class="{ 'active': activeGlobalCard === 2, 'inactive': activeGlobalCard !== 2 }"
              >
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  To collect information about vision, Hartline measured the rate of activity in a singular neuron. The optic nerve in Limulus polyphemus is long, and Harline isolated a single axon. He then put electrodes into the axon to measure the rate of action potentials. The goal was to measure the level of activity in the axon in an oscillograph of action potentials.
                </p>
                <br>
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  The oscillograph for one nerve fiber is set up by drilling a hole into the carapace of the horseshoe crab and placing a recording chamber inside that hole. The location of the optic nerve can be estimated through the locations of the lateral and median eyes, as the optic nerve runs in between them.
                </p>
                <br>
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  After the hole is drilled approximately where the optic nerve will be, the optic nerve is drawing into the recording chamber. Excess connective tissue is removed around the nerve, and the sheath around the nerve is also removed. A single fiber is then isolated and cut. The electrode of the oscillograph is then connected to the cut end of the fiber, which allows it to record the electrical signals that are running through the fiber.
                </p>
              </div>
              
              <!-- Experiments Card 2: Experimental application -->
              <div 
                ref="expCard2Ref"
                class="reading-card mb-6"
                :class="{ 'active': activeGlobalCard === 3, 'inactive': activeGlobalCard !== 3 }"
              >
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  This type of setup was used for the majority of the experiments that Hartline did at this point. Conveniently, the visual field of a single neuron can be isolated by isolating an ommatidium.
                </p>
                <br>
                <p class="text-lg leading-relaxed" style="font-size: 18px;">
                  We can learn a lot about visual processing from the behavior of a single neuron. The simplest situation is when a single light is repeatedly shone on a single ommatidium. To shine a light on a single ommatidium, a fiber optic light pipe is used to focus the light on a precise place. By doing so, when the light is shone on the ommatidium, the corresponding fiber in the optic nerve starts sending action potentials, which is what is measured by the oscillograph.
                </p>
              </div>
            </template>
          </TwoPaneVisualizationSection>
        </div>
      </section>

      <!-- Section: Inhibitory interactions in the retina ---->
      <section id="inhibitory-interactions-in-the-retina" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl mb-6">Inhibitory interactions in the retina</h2>
          
          <TwoPaneVisualizationSection
            section-id="inhibitory-interactions"
            :show-model="false"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6" style="font-size: 18px;">
                Bayes' theorem describes the probability of an event based on prior knowledge of conditions 
                that might be related to the event. It provides a mathematical framework for updating beliefs 
                or hypotheses based on new evidence.
              </p>
              
              <div class="bg-purple-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl mb-4">Applications</h3>
                <ul class="list-disc list-inside space-y-2 text-lg" style="font-size: 18px;">
                  <li>Medical diagnosis and screening tests</li>
                  <li>Machine learning and pattern recognition</li>
                  <li>Quality control and reliability analysis</li>
                  <li>Information theory and signal processing</li>
                </ul>
              </div>

              <div class="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl mb-4">Bayes' Theorem Formula</h3>
                <p class="text-lg leading-relaxed mb-4" style="font-size: 18px;">
                  The posterior probability of hypothesis A given evidence B:
                </p>
                <div class="bg-white px-6 py-3 rounded shadow-sm">
                  P(A|B) = P(B|A) × P(A) / P(B)
                </div>
              </div>
            </template>
          </TwoPaneVisualizationSection>
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

/* Ensure smooth transitions for all card properties */
.reading-card p {
  margin: 0;
  transition: color 0.3s ease;
}

</style>