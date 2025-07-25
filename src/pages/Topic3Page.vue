<script setup lang="ts">
// Page metadata for search indexing
const pageMetadata = {
  id: 'topic3',
  title: 'Advanced Neural Networks',
  content: 'Deep dive into neural network behavior, synaptic transmission, and advanced neuroscience topics. This section explores complex neural dynamics, network topology, and computational neuroscience principles.',
  excerpt: 'Deep dive into neural network behavior and synaptic mechanisms.',
  path: '/topic3',
  tags: ['neuroscience', 'neural-networks', 'synapses', 'transmission', 'computational', 'dynamics'],
  category: 'Neuroscience',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 3',
    difficulty: 'advanced' as const,
    estimatedReadTime: 15
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
      <div class="content">
        <h1 class="text-4xl font-bold mb-6">Topic 3</h1>
        <p class="text-lg leading-relaxed">
          This is a section without an image. The content starts at the top of the section.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: calc(100vh - 4rem);
}
</style> 