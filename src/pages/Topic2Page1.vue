<script setup lang="ts">
import TwoPaneVisualizationSection from '../components/TwoPaneVisualizationSection.vue'

// Page metadata for search indexing
const pageMetadata = {
  id: 'topic2-page1',
  title: 'Neuroscience Fundamentals',
  content: 'Understanding the basic structure and function of the brain, neural mechanisms, and fundamental principles of neuroscience. This section covers brain anatomy, neural circuits, and the cellular basis of neural function.',
  excerpt: 'Understanding the basic structure and function of the brain and neural mechanisms.',
  path: '/topic2/page1',
  tags: ['neuroscience', 'brain', 'anatomy', 'structure', 'neural-circuits', 'neurons'],
  category: 'Neuroscience',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 2',
    difficulty: 'beginner' as const,
    estimatedReadTime: 10
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}
</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl mx-auto">
      <div class="text-sm text-gray-600 mb-2">Chapter 2</div>
      <h1 class="text-4xl font-bold mb-6">Topic 2</h1>
      <p class="text-xl text-gray-700 mb-8">
        Exploring the fundamentals of neuroscience and brain structure analysis.
      </p>
      
      <!-- Section: Neuroscience Fundamentals -->
      <section id="neuroscience-fundamentals" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl font-bold mb-6">Neuroscience Fundamentals</h2>
          
          <TwoPaneVisualizationSection
            section-id="neuroscience-fundamentals"
            model-path="/models/horseshoe_crab_basic.glb"
            :enable-sticky="true"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6">
                Understanding the basic structure and function of the brain is essential for neuroscience research. 
                This section covers fundamental concepts including neural anatomy, brain regions, and cellular mechanisms 
                that underlie neural function and behavior.
              </p>
              
              <div class="bg-blue-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl font-semibold mb-4">Key Concepts</h3>
                <ul class="list-disc list-inside space-y-2 text-base">
                  <li>Neural anatomy and brain structure</li>
                  <li>Cellular basis of neural function</li>
                  <li>Neural circuits and connectivity</li>
                  <li>Brain regions and their functions</li>
                </ul>
              </div>
              
              <p class="text-lg leading-relaxed">
                These fundamental principles form the foundation for understanding more complex neuroscientific phenomena 
                and provide the basis for advanced research in computational neuroscience and neural modeling.
              </p>
            </template>
          </TwoPaneVisualizationSection>
        </div>
      </section>

      <!-- Section: Neural Circuits and Connectivity -->
      <section id="neural-circuits" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl font-bold mb-6">Neural Circuits and Connectivity</h2>
          
          <TwoPaneVisualizationSection
            section-id="neural-circuits"
            model-path="/models/horseshoe_crab_basic.glb"
            :enable-sticky="true"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6">
                Neural circuits represent the fundamental computational units of the brain, consisting of interconnected 
                neurons that process and transmit information. Understanding circuit organization and connectivity patterns 
                is crucial for comprehending how the brain performs complex cognitive functions.
              </p>
              
              <div class="bg-green-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl font-semibold mb-4">Circuit Types</h3>
                <ul class="list-disc list-inside space-y-2 text-base">
                  <li>Feed-forward circuits for information processing</li>
                  <li>Recurrent circuits for memory and decision-making</li>
                  <li>Inhibitory circuits for signal regulation</li>
                  <li>Modular circuits for specialized functions</li>
                </ul>
              </div>
              
              <p class="text-lg leading-relaxed mb-6">
                Modern techniques in connectomics allow researchers to map neural connections at unprecedented resolution, 
                revealing the intricate wiring patterns that underlie brain function and dysfunction.
              </p>
            </template>
          </TwoPaneVisualizationSection>
        </div>
      </section>

      <!-- Section: Brain Imaging and Analysis -->
      <section id="brain-imaging" class="mb-16">
        <div class="image-container bg-gray-300 rounded-lg h-64 w-full mb-8 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Brain Imaging Data</span>
        </div>
        <div class="content text-left">
          <h2 class="text-3xl font-bold mb-6">Brain Imaging and Analysis</h2>
          <p class="text-lg leading-relaxed mb-6">
            Advanced brain imaging techniques provide non-invasive windows into brain structure and function. 
            These methods enable researchers to study brain activity, connectivity, and changes over time in 
            both healthy and diseased states.
          </p>
          
          <div class="bg-purple-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Imaging Modalities</h3>
            <ul class="list-disc list-inside space-y-2 text-base">
              <li>Functional MRI (fMRI) for activity mapping</li>
              <li>Diffusion MRI for white matter structure</li>
              <li>PET imaging for metabolic processes</li>
              <li>EEG/MEG for electrical activity</li>
            </ul>
          </div>
          
          <p class="text-lg leading-relaxed">
            The integration of multiple imaging modalities with computational analysis techniques provides 
            comprehensive insights into brain organization and function across different spatial and temporal scales.
          </p>
        </div>
      </section>

      <!-- Section: Computational Neuroscience -->
      <section id="computational-neuroscience" class="mb-16">
        <div class="content text-left">
          <h2 class="text-3xl font-bold mb-6">Computational Neuroscience</h2>
          
          <TwoPaneVisualizationSection
            section-id="computational-neuroscience"
            model-path="/models/horseshoe_crab_basic.glb"
            :enable-sticky="true"
          >
            <template #content>
              <p class="text-lg leading-relaxed mb-6">
                Computational neuroscience uses mathematical models and theoretical analysis to understand brain function. 
                This interdisciplinary field combines neuroscience, mathematics, physics, and computer science to 
                create quantitative descriptions of neural processes.
              </p>
              
              <div class="bg-orange-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl font-semibold mb-4">Modeling Approaches</h3>
                <ul class="list-disc list-inside space-y-2 text-base">
                  <li>Single neuron models (Hodgkin-Huxley, integrate-and-fire)</li>
                  <li>Network models for population dynamics</li>
                  <li>Machine learning approaches for pattern recognition</li>
                  <li>Dynamical systems theory for brain states</li>
                </ul>
              </div>
              
              <div class="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 class="text-xl font-semibold mb-4">Key Equations</h3>
                <p class="text-base mb-4">The membrane potential dynamics can be described by:</p>
                <div class="bg-white px-6 py-3 rounded shadow-sm w-fit">
                  C(dV/dt) = -g(V - E) + I(t)
                </div>
              </div>
              
              <p class="text-lg leading-relaxed">
                These computational approaches enable researchers to test hypotheses about brain function, 
                predict neural responses, and develop new treatments for neurological disorders.
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
</style> 