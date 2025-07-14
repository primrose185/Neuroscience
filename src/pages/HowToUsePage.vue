<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import BlenderModelViewer from '../utilities/BlenderModelViewer.js'
import * as THREE from 'three'

// Page metadata for search indexing
const pageMetadata = {
  id: 'how-to-use',
  title: 'How to Use',
  content: 'Learn how to navigate and make the most of this neuroscience learning platform. This guide covers getting started, navigation, search features, and platform overview.',
  excerpt: 'Complete guide to using the neuroscience learning platform effectively.',
  path: '/how-to-use',
  tags: ['guide', 'navigation', 'help', 'tutorial'],
  category: 'Help',
  type: 'page' as const,
  metadata: {
    chapter: 'Help',
    difficulty: 'beginner' as const,
    estimatedReadTime: 3
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}

// 3D Model Viewer
let modelViewer: BlenderModelViewer | null = null

onMounted(async () => {
  try {
    // Initialize the 3D model viewer
    modelViewer = new BlenderModelViewer('model-container', {
      enableControls: true, // Enable controls for auto-rotation
      autoRotate: true, // Enable auto-rotation with voltage animation
      background: 0xE3E7FC, // Dark background
      fog: false,
      lights: {
        ambient: { color: 0x404040, intensity: 1.0 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: 2, y: 14, z: 0}, // Top-down view
        fov: 60,
        near: 0.1,
        far: 1000
      }
    })

    // Load the BlenderSpike test model
    await modelViewer.loadModel('/models/blenderSpike_test.glb', {
      scale: 1.5,
      position: { x: 6, y: 0, z: 7},
      autoPlay: false,
      fitCamera: false // Disable automatic camera positioning
    })

    // Load voltage animation data for the model
    try {
      const voltageData = await modelViewer.loadVoltageData('/models/blenderSpike_test.json')
      
      // Validate data before starting animation
      if (!voltageData.sections || voltageData.sections.length === 0) {
        console.warn('No voltage sections found in data')
        throw new Error('Invalid voltage data: no sections found')
      }
      
      // Log useful information about loaded data
      console.log(`Loaded voltage data: ${voltageData.sections.length} sections, ${voltageData.metadata.frames} frames`)
      console.log(`Animation duration: ${voltageData.metadata.duration_ms}ms`)
      console.log(`Voltage range: ${voltageData.metadata.global_voltage_range.min} to ${voltageData.metadata.global_voltage_range.max} mV`)
      
      // Adjust animation speed based on data duration (slower for longer simulations)
      const speed = voltageData.metadata.duration_ms > 100 ? 0.5 : 1.0
      
      // Start voltage animation
      modelViewer.playVoltageAnimation(speed)
      console.log(`Voltage animation started at ${speed}x speed`)
    } catch (error) {
      console.warn('Could not load voltage animation data:', error.message)
      console.log('Falling back to standard GLB animations')
      
      // Fallback to GLB animations if voltage data unavailable
      if (modelViewer.getAnimationNames().length > 0) {
        modelViewer.playAnimation(0, {
          loop: THREE.LoopRepeat,
          clampWhenFinished: false
        })
      }
    }

    // Manually ensure camera looks at center of model
    modelViewer.camera.lookAt(5, 0, 0)

    console.log('3D model loaded successfully')
  } catch (error) {
    console.error('Failed to load 3D model:', error)
  }
})

onBeforeUnmount(() => {
  if (modelViewer) {
    modelViewer.dispose()
  }
})
</script>

<template>
  <div class="page-container">
    <!-- Banner Section with 3D Background -->
    <div class="banner-section">
      <!-- 3D Model Container (Background) -->
      <div id="model-container" class="model-background"></div>
      
      <!-- Banner Content (Foreground) -->
      <div class="banner-content">
        <h1 class="banner-title">How to Use</h1>
      </div>
    </div>

    <!-- Content Section -->
    <div class="content-section">
      <div class="content-container">
        <p class="paragraph-text">
          Welcome to our comprehensive neuroscience learning platform. This interactive environment 
          is designed to help you explore complex neurological concepts through immersive 3D visualizations, 
          detailed explanations, and hands-on learning experiences. Navigate through various topics using 
          the sidebar menu, search for specific content using our intelligent search system, and engage 
          with interactive models to deepen your understanding of neuroscience principles. Whether you're 
          a student, researcher, or enthusiast, this platform provides the tools and resources you need 
          to master the fascinating world of neuroscience.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #ffffff;
  position: fixed; /* Break completely out of normal flow */
  top: 0;
  left: 0; /* Start from true left edge */
  width: 100vw; /* Full viewport width */
  z-index: 1; /* Ensure it's above normal content but below modals */
}

.banner-section {
  position: relative;
  width: 80vw; /* Exactly 4/5 of viewport width */
  margin-left: 20vw; /* Start after sidebar (20vw) */
  height: 60vh;
  min-height: 400px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.model-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  opacity: 0.7;
}

.model-background canvas {
  width: 100% !important;
  height: 100% !important;
}

.banner-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
  padding: 4rem 6rem; /* Generous padding for better spacing */
  width: 100%;
}

.banner-title {
  font-size: 4rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  margin: 0;
  line-height: 1.2;
}

.content-section {
  background-color: #ffffff;
  position: relative;
  z-index: 3;
  width: 80vw; /* Match banner width exactly */
  margin-left: 20vw; /* Align with banner */
}

.content-container {
  width: 100%; /* 100% of the 80vw container */
  padding: 3rem 6rem; /* Match banner padding style for consistency */
}

.paragraph-text {
  font-size: 16px;
  line-height: 1.6;
  color: #374151;
  text-align: left;
  margin: 0;
  max-width: 65vw; /* Limit width to center the text block */
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-container {
    margin-left: 0; /* Reset on mobile */
    width: 100vw;
  }
  
  .banner-section {
    width: 100vw; /* Full width on mobile */
    margin-left: 0; /* No sidebar on mobile */
    height: 50vh;
    min-height: 300px;
  }
  
  .content-section {
    width: 100vw; /* Full width on mobile */
    margin-left: 0; /* No sidebar on mobile */
  }
  
  .banner-title {
    font-size: 2.5rem;
  }
  
  .banner-content {
    padding: 2rem 3rem; /* Reduced padding for tablets */
  }
  
  .content-container {
    padding: 2rem 3rem; /* Match banner padding on tablets */
  }
}

@media (max-width: 480px) {
  .banner-title {
    font-size: 2rem;
  }
  
  .banner-content {
    padding: 1.5rem 2rem; /* Minimal padding for mobile */
    text-align: center; /* Center text on mobile for better appearance */
  }
  
  .content-container {
    padding: 1.5rem 2rem; /* Match banner padding on mobile */
  }
}
</style>