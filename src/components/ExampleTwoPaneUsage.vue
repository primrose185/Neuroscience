<template>
  <div>
    <!-- Example using the new cards prop system -->
    <TwoPaneVisualizationSection
      section-id="example-cards"
      :cards="exampleCards"
      model-path="/models/horseshoe_crab_basic.glb"
      :show-model="true"
      @card-activated="handleCardActivated"
    />
    
    <!-- Example using the old slot system (backward compatibility) -->
    <TwoPaneVisualizationSection
      section-id="example-slot"
      model-path="/models/horseshoe_crab_basic.glb"
      :show-model="true"
    >
      <template #content>
        <div class="reading-card mb-6 active">
          <p>This is using the old slot-based system for backward compatibility.</p>
        </div>
      </template>
    </TwoPaneVisualizationSection>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TwoPaneVisualizationSection from './TwoPaneVisualizationSection.vue'

// Example cards data
const exampleCards = ref([
  {
    id: 'card-1',
    content: '<p class="text-lg leading-relaxed" style="font-size: 18px;">This is the first card with <strong>HTML content</strong>. It demonstrates the new cards prop system.</p>'
  },
  {
    id: 'card-2', 
    content: '<p class="text-lg leading-relaxed" style="font-size: 18px;">This is the second card. The right pane will use <em>advanced sticky behavior</em> that responds to scroll direction.</p>'
  },
  {
    id: 'card-3',
    content: '<p class="text-lg leading-relaxed" style="font-size: 18px;">This is the third card. When scrolling down, the right pane sticks until the bottom of this content aligns with the bottom of the 3D viewer.</p>'
  }
])

// Handle card activation events
const handleCardActivated = (cardId: string, cardIndex: number) => {
  console.log(`Card activated: ${cardId} (index: ${cardIndex})`)
  // You can perform additional actions here, such as updating global state
}
</script>