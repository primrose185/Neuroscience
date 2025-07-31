<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, inject } from 'vue'
import Shared3DModelViewer from './Shared3DModelViewer.vue'

interface Props {
  sectionId: string
  modelPath: string
  enableSticky?: boolean
  viewerOptions?: object
}

const props = withDefaults(defineProps<Props>(), {
  enableSticky: true,
  viewerOptions: () => ({})
})

// Refs for sticky positioning
const visualizationColumnRef = ref<HTMLElement | null>(null)
const isViewerSticky = ref(false)

// Throttle function for scroll events
const throttle = (func: Function, delay: number) => {
  let timeoutId: number | null = null
  let lastExecTime = 0
  return function (this: any, ...args: any[]) {
    const currentTime = Date.now()
    
    if (currentTime - lastExecTime > delay) {
      func.apply(this, args)
      lastExecTime = currentTime
    } else {
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        func.apply(this, args)
        lastExecTime = Date.now()
      }, delay - (currentTime - lastExecTime))
    }
  }
}

// Handle sticky positioning for 3D viewer
const handleViewerSticky = () => {
  if (!visualizationColumnRef.value || !props.enableSticky) return
  
  // Disable sticky behavior on mobile/tablet
  if (window.innerWidth <= 768) {
    isViewerSticky.value = false
    return
  }
  
  const columnRect = visualizationColumnRef.value.getBoundingClientRect()
  const stickyThreshold = 20 // Distance from top to trigger sticky
  
  // Get the section container to determine boundaries
  const sectionElement = visualizationColumnRef.value.closest('section')
  if (!sectionElement) return
  
  const sectionRect = sectionElement.getBoundingClientRect()
  const viewerHeight = 600 // Height of the 3D container
  const viewerBottom = columnRect.top + viewerHeight
  const shouldExitSticky = viewerBottom >= sectionRect.bottom - 20
  
  // Enter sticky mode when column top is near viewport top and we haven't reached section bottom
  if (columnRect.top <= stickyThreshold && !shouldExitSticky) {
    if (!isViewerSticky.value) {
      updateStickyPosition()
    }
    isViewerSticky.value = true
  }
  // Exit sticky mode when viewer bottom aligns with section bottom or scrolling back up
  else if (shouldExitSticky || columnRect.top > stickyThreshold) {
    if (isViewerSticky.value) {
      // Reset inline positioning when exiting sticky mode
      const column = visualizationColumnRef.value
      if (column) {
        column.style.left = ''
        column.style.right = ''
        column.style.top = ''
        column.style.transform = ''
      }
    }
    isViewerSticky.value = false
  }
}

// Calculate and set viewport-centered sticky positioning
const updateStickyPosition = () => {
  if (!visualizationColumnRef.value) return
  
  // Get the main content container (max-width: 1200px, centered)
  const pageContainer = document.querySelector('.page-container')
  if (!pageContainer) return
  
  const pageRect = pageContainer.getBoundingClientRect()
  
  // Calculate the column's position relative to the content area
  const contentMaxWidth = 1200
  const availableWidth = Math.min(pageRect.width - 64, contentMaxWidth)
  const contentStartX = pageRect.left + Math.max(32, (pageRect.width - contentMaxWidth) / 2)
  
  // Position the column in the right half of the content area
  const rightColumnStart = contentStartX + (availableWidth / 2)
  const columnWidth = 400 // Width of the visualization column
  const viewerCenterOffset = (availableWidth / 2 - columnWidth) / 2
  const leftPosition = rightColumnStart + viewerCenterOffset
  
  // Center vertically in viewport
  const viewerHeight = 600
  const topPosition = (window.innerHeight - viewerHeight) / 2
  
  // Apply the calculated position to the visualization column
  const column = visualizationColumnRef.value
  column.style.left = `${leftPosition}px`
  column.style.top = `${topPosition}px`
  column.style.right = 'auto'
}

// Throttled scroll handler
const throttledScrollHandler = throttle(handleViewerSticky, 16) // ~60fps

onMounted(() => {
  if (props.enableSticky) {
    // Add scroll event listener for sticky viewer
    window.addEventListener('scroll', throttledScrollHandler, { passive: true })
    
    // Add resize event listener to recalculate sticky position
    const handleResize = () => {
      if (isViewerSticky.value) {
        updateStickyPosition()
      }
    }
    window.addEventListener('resize', handleResize)
    
    // Store handlers for cleanup
    onBeforeUnmount(() => {
      window.removeEventListener('scroll', throttledScrollHandler)
      window.removeEventListener('resize', handleResize)
    })
  }
})
</script>

<template>
  <div class="two-pane-section">
    <!-- Two-column layout: text left, 3D container right -->
    <div class="two-column-layout">
      <!-- Left Column: Content Slot -->
      <div class="content-column">
        <slot name="content"></slot>
      </div>
      
      <!-- Right Column: 3D Visualization -->
      <div 
        ref="visualizationColumnRef"
        class="visualization-column"
        :class="{ 'sticky': isViewerSticky }"
      >
        <Shared3DModelViewer
          :container-id="`${sectionId}-model-container`"
          :model-path="modelPath"
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

.two-column-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.content-column {
  flex: 1;
  min-width: 0;
}

.visualization-column {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* Sticky positioning for visualization column */
.visualization-column.sticky {
  position: fixed;
  /* left and top positions will be set dynamically by JavaScript */
  z-index: 100;
  width: 400px; /* Fixed width when sticky */
}

/* Responsive Design */
@media (max-width: 768px) {
  /* Stack columns on tablet */
  .two-column-layout {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .visualization-column {
    align-self: center;
  }
  
  /* Disable sticky behavior on mobile/tablet */
  .visualization-column.sticky {
    position: relative !important;
    top: auto !important;
    left: auto !important;
    width: auto !important;
    z-index: auto !important;
  }
}
</style>