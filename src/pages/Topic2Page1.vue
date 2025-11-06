<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import BlenderModelViewer from '../utilities/BlenderModelViewer.js'
import * as THREE from 'three'

/**
 * Create a radial gradient texture for depth enhancement
 * Lighter in center, darker at edges
 */
function createDepthGradientTexture(color1: string, color2: string, width: number = 1024, height: number = 1024): THREE.Texture {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!

  canvas.width = width
  canvas.height = height

  // Create radial gradient from center to edges
  const gradient = ctx.createRadialGradient(
    canvas.width * 0.5, canvas.height * 0.5, 0,  // Inner circle at center, radius 0
    canvas.width * 0.5, canvas.height * 0.5, Math.max(canvas.width, canvas.height) * 0.7  // Outer circle
  )

  gradient.addColorStop(0, color1)  // Center color (lighter)
  gradient.addColorStop(1, color2)  // Edge color (darker)

  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const texture = new THREE.CanvasTexture(canvas)
  texture.wrapS = THREE.ClampToEdgeWrapping
  texture.wrapT = THREE.ClampToEdgeWrapping
  texture.minFilter = THREE.LinearFilter
  texture.magFilter = THREE.LinearFilter

  return texture
}

// Page metadata for search indexing
const pageMetadata = {
  id: 'topic2-page1',
  title: 'Two Ommatidia Lateral Inhibition Simulation',
  content: 'Interactive 3D visualization of two neighboring ommatidia (eccentric cells) from the horseshoe crab compound eye, demonstrating lateral inhibition with NEURON simulation data.',
  excerpt: 'Visualizing lateral inhibition in horseshoe crab ommatidia with live voltage data.',
  path: '/topic2/page1',
  tags: ['neuroscience', 'lateral-inhibition', 'ommatidia', 'horseshoe-crab', 'NEURON', 'simulation', 'voltage'],
  category: 'Neuroscience',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 2',
    difficulty: 'intermediate' as const,
    estimatedReadTime: 15
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}

// Viewer and animation state
let viewer: any = null
const isPlaying = ref(false)
const animationSpeed = ref(0.5)
const currentTime = ref(0)
const totalTime = ref(200) // 200ms simulation duration

// Initialize viewer
onMounted(async () => {
  try {
    console.log('Initializing BlenderModelViewer...')

    // Create viewer instance
    viewer = new BlenderModelViewer('model-viewer-container', {
      enableControls: true,
      background: 0x000000, // Initial black background (will be replaced with gradient)
      camera: {
        position: { x: 0, y: 0, z: 50 },
        fov: 60
      }
    })

    // Enable standard scroll wheel zoom (override BlenderModelViewer's Shift+scroll requirement)
    if (viewer.controls) {
      viewer.controls.enableZoom = true
      viewer.controls.zoomSpeed = 1.0
      // Set zoom limits for better framing
      viewer.controls.minDistance = 0   // Prevent zooming too close
      viewer.controls.maxDistance = 200  // Prevent zooming too far
    }

    console.log('Loading two_ommatidia.glb model...')
    // Load the 3D model
    await viewer.loadModel('/models/two_ommatidia.glb', {
      scale: 1.0,
      position: { x: 0, y: 0, z: 0 },
      fitCamera: true
    })

    console.log('Applying gradient background...')
    // Create and apply radial gradient background (lighter center, darker edges)
    const gradientTexture = createDepthGradientTexture(
      '#ecebf5',  // Center: light lavender
      '#6c6596',  // Edges: darker purple
      window.innerWidth,
      window.innerHeight
    )
    viewer.scene.background = gradientTexture

    console.log('Loading voltage data...')
    // Load voltage simulation data
    await viewer.loadVoltageData('/data/voltages_formatted.json')

    console.log('Starting voltage animation...')
    // Start animation
    viewer.playVoltageAnimation(animationSpeed.value)
    isPlaying.value = true

    // Update current time display (if available in viewer)
    if (viewer.getCurrentTime) {
      const updateTimeDisplay = () => {
        if (viewer) {
          currentTime.value = viewer.getCurrentTime()
        }
      }
      setInterval(updateTimeDisplay, 50) // Update 20 times per second
    }

  } catch (error) {
    console.error('Error initializing voltage visualization:', error)
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (viewer) {
    viewer.stopVoltageAnimation()
    viewer.dispose()
    viewer = null
  }
})

// Playback controls
const togglePlayPause = () => {
  if (!viewer) return

  if (isPlaying.value) {
    viewer.pauseVoltageAnimation()
    isPlaying.value = false
  } else {
    viewer.playVoltageAnimation(animationSpeed.value)
    isPlaying.value = true
  }
}

const changeSpeed = (speed: number) => {
  animationSpeed.value = speed
  if (viewer && isPlaying.value) {
    viewer.stopVoltageAnimation()
    viewer.playVoltageAnimation(speed)
  }
}

const restart = () => {
  if (!viewer) return
  viewer.stopVoltageAnimation()
  viewer.playVoltageAnimation(animationSpeed.value)
  isPlaying.value = true
}
</script>

<template>
  <div class="immersive-page">
    <!-- Model Viewer Container -->
    <div id="model-viewer-container" class="model-container"></div>

    <!-- Playback Controls Overlay -->
    <div class="controls-overlay">
      <div class="controls-panel">
        <!-- Play/Pause Button -->
        <button @click="togglePlayPause" class="control-button" aria-label="Play/Pause">
          <span v-if="isPlaying">⏸</span>
          <span v-else>▶</span>
        </button>

        <!-- Restart Button -->
        <button @click="restart" class="control-button" aria-label="Restart">
          ⟲
        </button>

        <!-- Speed Controls -->
        <div class="speed-controls">
          <span class="control-label">Speed:</span>
          <button
            @click="changeSpeed(0.25)"
            :class="['speed-button', { active: animationSpeed === 0.25 }]"
          >
            0.25×
          </button>
          <button
            @click="changeSpeed(0.5)"
            :class="['speed-button', { active: animationSpeed === 0.5 }]"
          >
            0.5×
          </button>
          <button
            @click="changeSpeed(1.0)"
            :class="['speed-button', { active: animationSpeed === 1.0 }]"
          >
            1×
          </button>
          <button
            @click="changeSpeed(2.0)"
            :class="['speed-button', { active: animationSpeed === 2.0 }]"
          >
            2×
          </button>
        </div>

        <!-- Time Display -->
        <div class="time-display">
          <span class="control-label">Time:</span>
          <span class="time-value">{{ currentTime.toFixed(1) }}ms / {{ totalTime }}ms</span>
        </div>
      </div>
    </div>

    <!-- Info Overlay (top) -->
    <div class="info-overlay">
      <h1 class="title">Two Ommatidia: Lateral Inhibition</h1>
      <p class="subtitle">NEURON simulation of coupled eccentric cells with light stimulation</p>
    </div>
  </div>
</template>

<style scoped>
.immersive-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #000;
}

.model-container {
  position: absolute;
  top: 2rem;
  left: calc(280px + 2rem);  /* Account for sidebar width + margin */
  right: 2rem;
  bottom: 2rem;
  width: calc(100vw - 280px - 4rem);  /* Adjust width for sidebar */
  height: calc(100vh - 4rem);
  border-radius: 8px;
  overflow: hidden;
}

/* Info Overlay (Top) */
.info-overlay {
  position: absolute;
  top: 3rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  padding: 1.5rem 2rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 600px;
  text-align: center;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* Controls Overlay (Bottom) */
.controls-overlay {
  position: absolute;
  bottom: 3rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.controls-panel {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.control-button {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.05);
}

.control-button:active {
  transform: scale(0.95);
}

.speed-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-left: 1rem;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.control-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
  margin-right: 0.25rem;
}

.speed-button {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.speed-button:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.speed-button.active {
  background: rgba(147, 51, 234, 0.5);
  border-color: rgba(168, 85, 247, 0.8);
  color: #fff;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-left: 1rem;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.time-value {
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .model-container {
    top: 1rem;
    left: 1rem;
    right: 1rem;
    bottom: 1rem;
    width: calc(100vw - 2rem);
    height: calc(100vh - 2rem);
  }

  .info-overlay {
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    padding: 1rem 1.5rem;
    max-width: calc(100vw - 3rem);
  }

  .title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.875rem;
  }

  .controls-overlay {
    bottom: 1.5rem;
  }

  .controls-panel {
    flex-wrap: wrap;
    justify-content: center;
    padding: 0.75rem 1rem;
    gap: 0.5rem;
  }

  .speed-controls,
  .time-display {
    border-left: none;
    padding-left: 0;
  }
}
</style>
