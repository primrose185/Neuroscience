<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Reference to the split container
const splitContainer = ref<HTMLElement | null>(null)
const isResizing = ref(false)
const leftPanel = ref<HTMLElement | null>(null)

// Initial width of the left panel (in percentage)
const leftPanelWidth = ref(50)

// Handle mouse events for resizing
const startResize = (e: MouseEvent) => {
  isResizing.value = true
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
}

const resize = (e: MouseEvent) => {
  if (!isResizing.value || !splitContainer.value) return
  
  const containerRect = splitContainer.value.getBoundingClientRect()
  const containerWidth = containerRect.width
  const mouseX = e.clientX - containerRect.left
  
  // Calculate percentage (constrain between 30% and 70%)
  let newWidth = (mouseX / containerWidth) * 100
  newWidth = Math.min(Math.max(newWidth, 30), 70)
  
  leftPanelWidth.value = newWidth
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
}
</script>

<template>
  <div class="page-container">
    <!-- Chapter Header Section -->
    <header class="bg-gray-100 py-16 mb-12">
      <div class="max-w-7xl mx-auto px-8">
        <div class="text-sm text-gray-600 mb-2">Chapter 1</div>
        <h1 class="text-5xl font-bold mb-4">Basic Probability</h1>
        <p class="text-xl text-gray-700">
          This chapter is an introduction to the basic concepts of probability theory.
        </p>
      </div>
    </header>

    <!-- Split Panel Container -->
    <div 
      ref="splitContainer"
      class="split-container max-w-7xl mx-auto px-8"
    >
      <!-- Left Panel - Content -->
      <div 
        ref="leftPanel"
        class="left-panel"
        :style="{ width: `${leftPanelWidth}%` }"
      >
        <section class="pr-8">
          <h2 class="text-3xl font-bold mb-6">Chance Events</h2>
          <p class="text-lg leading-relaxed mb-6">
            Randomness is all around us. Probability theory is the mathematical framework that allows us 
            to analyze chance events in a logically sound manner. The probability of an event is a number 
            indicating how likely that event will occur. This number is always between 0 and 1, where 0 
            indicates impossibility and 1 indicates certainty.
          </p>

          <!-- Mathematical Expression -->
          <div class="bg-gray-50 rounded-lg p-6 mb-8">
            <p class="text-lg mb-4">The mathematical expression for probability can be written as:</p>
            <div class="flex justify-center">
              <div class="bg-white px-8 py-4 rounded shadow-sm">
                P(E) = n(E) / n(S)
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Resizer -->
      <div 
        class="resizer"
        @mousedown="startResize"
      ></div>

      <!-- Right Panel - Visualization -->
      <div 
        class="right-panel"
        :style="{ width: `${100 - leftPanelWidth}%` }"
      >
        <div class="visualization-container">
          <div class="bg-white rounded-lg shadow-lg p-8 h-full">
            <h3 class="text-2xl font-semibold mb-4">Interactive Visualization</h3>
            <div class="bg-gray-100 rounded-lg p-6 flex items-center justify-center" style="min-height: 500px">
              <span class="text-gray-500">Visualization Placeholder</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #ffffff;
}

.split-container {
  display: flex;
  align-items: stretch;
  min-height: 600px;
  position: relative;
}

.left-panel {
  overflow-y: auto;
  transition: width 0.1s ease;
}

.right-panel {
  overflow-y: auto;
  transition: width 0.1s ease;
}

.resizer {
  width: 8px;
  background-color: #e5e7eb;
  cursor: col-resize;
  transition: background-color 0.2s ease;
  margin: 0 -4px;
  z-index: 10;
  position: relative;
}

.resizer:hover, .resizer:active {
  background-color: #93c5fd;
}

.visualization-container {
  height: 100%;
  padding-left: 8px;
}

/* Prevent text selection while resizing */
.split-container.resizing {
  user-select: none;
  cursor: col-resize;
}

/* Add smooth transitions */
.transition-colors {
  transition: all 0.3s ease;
}
</style> 