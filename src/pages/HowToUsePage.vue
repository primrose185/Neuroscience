<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import BlenderModelViewer from '../utilities/BlenderModelViewer.js'
import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'

// Page metadata for search indexing
const pageMetadata = {
  id: 'platform-guide',
  title: 'Platform Guide',
  content: 'Learn how to navigate and make the most of this neuroscience learning platform. This guide covers getting started, navigation, search features, and platform overview.',
  excerpt: 'Complete guide to using the neuroscience learning platform effectively.',
  path: '/platform-guide',
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

// 3D Model Viewers
let modelViewer: BlenderModelViewer | null = null // Banner background viewer
let contentModelViewer: BlenderModelViewer | null = null // Content container viewer
let modalModelViewer: BlenderModelViewer | null = null // Modal popup viewer
let composer: EffectComposer | null = null

// Modal state
const isModalOpen = ref(false)

// Modal functions
const closeModal = () => {
  isModalOpen.value = false
  if (modalModelViewer) {
    modalModelViewer.dispose()
    modalModelViewer = null
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isModalOpen.value) {
    closeModal()
  }
}

// BlenderSpike color space conversion functions (from materials.py)
function srgb2lin(s: number): number {
  if (s <= 0.0404482362771082) {
    return s / 12.92
  } else {
    return Math.pow((s + 0.055) / 1.055, 2.4)
  }
}

function lin2srgb(lin: number): number {
  if (lin > 0.0031308) {
    return 1.055 * Math.pow(lin, 1.0 / 2.4) - 0.055
  } else {
    return 12.92 * lin
  }
}

function toBlenderColor(rgb: [number, number, number]): [number, number, number] {
  return [
    srgb2lin(rgb[0]),
    srgb2lin(rgb[1]),
    srgb2lin(rgb[2])
  ]
}

// Create depth-enhancing gradient texture for scene background
function createDepthGradientTexture(color1, color2): THREE.Texture {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!
  
  // High resolution for smooth gradient
  canvas.width = 1024
  canvas.height = 1024
  
  // Create radial gradient for depth perception
  const gradient = ctx.createRadialGradient(
    canvas.width * 0.5, canvas.height * 0.5, 0, // Center point (slightly higher for better composition)
    canvas.width * 0.5, canvas.height * 0.5, canvas.width * 0.7 // Outer radius
  )
  
  gradient.addColorStop(0, color1)
  gradient.addColorStop(1, color2)
  
  // Fill canvas with gradient
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // Create Three.js texture
  const texture = new THREE.CanvasTexture(canvas)
  texture.wrapS = THREE.ClampToEdgeWrapping
  texture.wrapT = THREE.ClampToEdgeWrapping
  texture.minFilter = THREE.LinearFilter
  texture.magFilter = THREE.LinearFilter
  
  return texture
}

// Custom emission material application for BlenderSpike compatibility
function applyBlenderSpikeEmissionMaterial(mesh: THREE.Mesh, voltage: number, minVoltage: number, maxVoltage: number, materialConfig: any) {
  // Get the plasma color from the existing colormap
  const tempColor = modelViewer!.voltageToColor(voltage, minVoltage, maxVoltage)
  
  // Convert to linear color space (matching BlenderSpike)
  const linearColor = toBlenderColor([tempColor.r, tempColor.g, tempColor.b])
  
  // Create pure emission material (matching Blender's emission shader)
  if (!mesh.material.isBlenderSpikeEmission) {
    mesh.material = new THREE.MeshBasicMaterial({
      color: new THREE.Color(linearColor[0], linearColor[1], linearColor[2]),
      transparent: false,
      side: THREE.DoubleSide
    })
    mesh.material.isBlenderSpikeEmission = true
    mesh.receiveShadow = false // Emission materials don't receive shadows
    mesh.castShadow = false // Emission materials don't cast shadows
  } else {
    // Update existing emission material
    mesh.material.color.setRGB(linearColor[0], linearColor[1], linearColor[2])
  }
  
  // Apply emission strength from material configuration
  const emissionStrength = materialConfig?.emission_strength || 2.0
  
  // Scale the color by emission strength (simulating Blender's emission strength)
  mesh.material.color.multiplyScalar(emissionStrength)
  
  mesh.material.needsUpdate = true
}

onMounted(async () => {
  try {
    // Initialize the 3D model viewer with BlenderSpike settings
    modelViewer = new BlenderModelViewer('model-container', {
      static: false, // Enable rotation capabilities
      enableControls: false, // Disable user controls but allow programmatic rotation
      background: 0x000000, // Will be replaced with gradient texture
      fog: false,
      lights: {
        ambient: { color: 0xffffff, intensity: 0.6 }, // Reduced ambient for emission materials
        directional: { color: 0xffffff, intensity: 0.8 } // Reduced directional for emission materials
      },
      camera: {
        position: { x: -1, y: 14, z: 0}, // Top-down view
        fov: 60,
        near: 0.1,
        far: 1000
      }
    })
    
    // Apply depth-enhancing gradient background
    const gradientTexture = createDepthGradientTexture('#d3ceed', '#5b5773')
    modelViewer.scene.background = gradientTexture
    
    // Store gradient texture for potential animation
    let gradientRotation = 0
    
    // Override the renderer settings for emission materials
    modelViewer.renderer.outputColorSpace = THREE.LinearSRGBColorSpace // Linear color space like Blender
    modelViewer.renderer.toneMapping = THREE.NoToneMapping // Disable tone mapping for pure emission
    modelViewer.renderer.toneMappingExposure = 1.0

    // Load the BlenderSpike test model
    await modelViewer.loadModel('/models/blenderSpike_test.glb', {
      scale: 1.5,
      position: { x: 6, y: 0, z: 7},
      autoPlay: false,
      fitCamera: false // Disable automatic camera positioning
    })

    // Setup bloom post-processing (matching Blender's bloom)
    composer = new EffectComposer(modelViewer.renderer)
    const renderPass = new RenderPass(modelViewer.scene, modelViewer.camera)
    composer.addPass(renderPass)
    
    // Configure bloom to match Blender's settings
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.5, // strength
      0.4, // radius  
      0.85 // threshold
    )
    composer.addPass(bloomPass)
    
    // Override the render loop to use post-processing
    const originalAnimate = modelViewer.animate.bind(modelViewer)
    modelViewer.animate = function() {
      requestAnimationFrame(() => modelViewer!.animate())
      
      const delta = modelViewer!.clock.getDelta()
      
      // Update animations
      if (modelViewer!.mixer) {
        modelViewer!.mixer.update(delta)
      }
      
      // Update voltage animation with custom emission materials
      if (modelViewer!.voltageAnimation.isPlaying && modelViewer!.voltageData) {
        const framesPerSecond = modelViewer!.voltageAnimation.totalFrames / (modelViewer!.voltageData.metadata.duration_ms / 1000)
        const frameIncrement = delta * framesPerSecond * modelViewer!.voltageAnimation.speed
        
        modelViewer!.voltageAnimation.currentFrame += frameIncrement
        
        if (modelViewer!.voltageAnimation.currentFrame >= modelViewer!.voltageAnimation.totalFrames) {
          modelViewer!.voltageAnimation.currentFrame = 0
        }
        
        // Apply custom BlenderSpike emission materials
        const voltageRange = modelViewer!.materialConfig?.voltage_range || modelViewer!.voltageData.metadata.global_voltage_range
        const { min: minVoltage, max: maxVoltage } = voltageRange
        
        const frameFloat = modelViewer!.voltageAnimation.currentFrame
        const frameIndex = Math.floor(frameFloat)
        const nextFrameIndex = Math.min(frameIndex + 1, modelViewer!.voltageAnimation.totalFrames - 1)
        const frameFraction = frameFloat - frameIndex
        
        modelViewer!.voltageAnimation.meshMap.forEach((sectionData, mesh) => {
          if (frameIndex < sectionData.voltage_frames.length) {
            const currentVoltage = sectionData.voltage_frames[frameIndex] || 0
            const nextVoltage = sectionData.voltage_frames[nextFrameIndex] || currentVoltage
            const interpolatedVoltage = currentVoltage + (nextVoltage - currentVoltage) * frameFraction
            
            applyBlenderSpikeEmissionMaterial(mesh, interpolatedVoltage, minVoltage, maxVoltage, modelViewer!.materialConfig)
          }
        })
      }
      
      // Add Y-axis rotation to the neuron model
      if (modelViewer!.currentModel) {
        // Slow, elegant rotation - approximately 1 full rotation per 60 seconds
        modelViewer!.currentModel.rotation.z += delta * 0.1 // Adjust speed as needed
      }
      
      // Add subtle gradient animation for enhanced depth
      gradientRotation += delta * 0.02 // Very slow rotation
      if (gradientTexture) {
        gradientTexture.offset.x = Math.sin(gradientRotation) * 0.005
        gradientTexture.offset.y = Math.cos(gradientRotation) * 0.003
        gradientTexture.needsUpdate = true
      }
      
      // Animate content gradient as well for consistency
      contentGradientRotation += delta * 0.015 // Slightly different speed for variation
      if (contentGradientTexture) {
        contentGradientTexture.offset.x = Math.sin(contentGradientRotation) * 0.004
        contentGradientTexture.offset.y = Math.cos(contentGradientRotation) * 0.002
        contentGradientTexture.needsUpdate = true
      }
      
      // Update controls
      if (modelViewer!.controls) {
        modelViewer!.controls.update()
      }
      
      // Render with bloom post-processing
      composer!.render()
    }

    // Load voltage animation data for the model
    try {
      const voltageData = await modelViewer.loadVoltageData('/models/material_test.json')
      
      // Validate data before starting animation
      if (!voltageData.sections || voltageData.sections.length === 0) {
        console.warn('No voltage sections found in data')
        throw new Error('Invalid voltage data: no sections found')
      }
      
      // Log useful information about loaded data
      console.log(`Loaded voltage data: ${voltageData.sections.length} sections, ${voltageData.metadata.frames} frames`)
      console.log(`Animation duration: ${voltageData.metadata.duration_ms}ms`)
      console.log(`Voltage range: ${voltageData.metadata.global_voltage_range.min} to ${voltageData.metadata.global_voltage_range.max} mV`)
      console.log('BlenderSpike material configuration:', voltageData.material_config)
      
      // Adjust animation speed based on data duration (slower for longer simulations)
      const speed = voltageData.metadata.duration_ms > 100 ? 0.5 : 1.0
      
      // Start voltage animation with BlenderSpike emission materials
      modelViewer.playVoltageAnimation(speed)
      console.log(`BlenderSpike voltage animation started at ${speed}x speed with emission materials and bloom`)
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
    
    // Initialize content 3D model viewer in the bordered container
    console.log('Initializing content 3D model viewer...')
    contentModelViewer = new BlenderModelViewer('content-model-container', {
      static: false,
      enableControls: true, // Allow user interaction with content model
      background: 0x000000, // Will be replaced with gradient texture
      fog: false,
      lights: {
        ambient: { color: 0x404040, intensity: 0.4 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: -1, y: 14, z: 0 }, // Similar to banner but allow interaction
        fov: 60,
        near: 0.1,
        far: 1000
      }
    })
    
    // Apply the same gradient background as the banner
    const contentGradientTexture = createDepthGradientTexture('#ecebf5', '#6c6596')
    contentModelViewer.scene.background = contentGradientTexture
    
    // Store content gradient texture for animation
    let contentGradientRotation = 0
    
    // Load the same model in the content container
    try {
      await contentModelViewer.loadModel('/models/blenderSpike_test.glb', {
        scale: 1.5,
        position: { x: 6, y: 0, z: 7 },
        autoPlay: false,
        fitCamera: true // Auto-fit for better initial view
      })
      
      // Load voltage data for content model as well
      try {
        const voltageData = await contentModelViewer.loadVoltageData('/models/material_test.json')
        console.log('Content model voltage data loaded successfully')
        
        // Start voltage animation for content model
        contentModelViewer.playVoltageAnimation(0.5) // Slower speed for study
        console.log('Content model voltage animation started')
      } catch (error) {
        console.warn('Could not load voltage animation data for content model:', error.message)
        
        // Fallback to GLB animations if voltage data unavailable
        if (contentModelViewer.getAnimationNames().length > 0) {
          contentModelViewer.playAnimation(0, {
            loop: THREE.LoopRepeat,
            clampWhenFinished: false
          })
        }
      }
      
      console.log('Content 3D model loaded successfully')
    } catch (error) {
      console.error('Failed to load content 3D model:', error)
    }
    
    // Handle window resize for post-processing
    const handleResize = () => {
      if (modelViewer && composer) {
        const width = modelViewer.container.clientWidth
        const height = modelViewer.container.clientHeight
        
        modelViewer.camera.aspect = width / height
        modelViewer.camera.updateProjectionMatrix()
        modelViewer.renderer.setSize(width, height)
        composer.setSize(width, height)
      }
    }
    
    window.addEventListener('resize', handleResize)
    
    // Add keyboard event listener for modal
    window.addEventListener('keydown', handleKeydown)

    console.log('3D model loaded successfully with BlenderSpike emission materials and bloom')
  } catch (error) {
    console.error('Failed to load 3D model:', error)
  }
})

// Watch for modal state changes to initialize/cleanup modal 3D viewer
watch(isModalOpen, async (newValue) => {
  if (newValue) {
    // Initialize modal 3D viewer when modal opens
    await nextTick() // Wait for DOM to update
    
    console.log('Initializing modal 3D model viewer...')
    modalModelViewer = new BlenderModelViewer('modal-model-container', {
      static: false,
      enableControls: true, // Full interaction in modal
      background: 0x000000, // Will be replaced with gradient
      fog: false,
      lights: {
        ambient: { color: 0xffffff, intensity: 0.6 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: -1, y: 14, z: 0 },
        fov: 60,
        near: 0.1,
        far: 1000
      }
    })
    
    // Apply gradient background
    const modalGradientTexture = createDepthGradientTexture('#e4e1f2', '#7b6add')
    modalModelViewer.scene.background = modalGradientTexture
    
    // Load model in modal
    try {
      await modalModelViewer.loadModel('/models/blenderSpike_test.glb', {
        scale: 1.5,
        position: { x: 6, y: 0, z: 7 },
        autoPlay: false,
        fitCamera: true
      })
      
      // Load voltage data
      try {
        await modalModelViewer.loadVoltageData('/models/material_test.json')
        modalModelViewer.playVoltageAnimation(0.5)
        console.log('Modal 3D model loaded successfully with voltage animation')
      } catch (error) {
        console.warn('Could not load voltage data for modal:', error.message)
        if (modalModelViewer.getAnimationNames().length > 0) {
          modalModelViewer.playAnimation(0, {
            loop: THREE.LoopRepeat,
            clampWhenFinished: false
          })
        }
      }
    } catch (error) {
      console.error('Failed to load modal 3D model:', error)
    }
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => {})
  window.removeEventListener('keydown', handleKeydown)
  
  if (composer) {
    composer.dispose()
  }
  
  if (modelViewer) {
    modelViewer.dispose()
  }
  
  if (contentModelViewer) {
    contentModelViewer.dispose()
  }
  
  if (modalModelViewer) {
    modalModelViewer.dispose()
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
        <h1 class="banner-title">Platform Guide</h1>
      </div>
    </div>

    <!-- Content Section -->
    <div class="content-section">
      <div class="content-container">
        <!-- Two-column layout: text left, 3D container right -->
        <p class="paragraph-text">
          Welcome to nREM, where complex neuroscience is simplified! Neuroscience includes
          fascinating but sometimes challenging ideas that may be easier to understand through
          observation. nREM aims to transform the experience of learning neuroscience through
          immersive 3D visualizations that show exactly how neural processes work.
        </p>
        <div class="content-layout">
          <!-- Left Column: Text Content -->
          <div class="text-column">
            <p class="paragraph-text">
              <br>
              As you read through our articles, you'll notice interactive 3D visualizations are embedded in the content. These 3D models correspond to and change with the text content being displayed. Scroll down to reveal and zoom in on the neuron model in this 3D visualization.
              <br><br>
              While you are reading the article, you will not be able to interact with the model, since the motions are timed to the text. However, you can explore the 3D model in closer detail by clicking on the<br>「｣ icon.
              <br><br>
              With certain models, you can see the graph over time. Click here to see the animation restart the processes that generate the graph.
              <br><br>
              There are also some functions on this site which do not involve 3D models. Sometimes, we provide footnotes that contain more about the research process, but are not necessary to understand the concepts in the articles. Hover over these symbols [wiki style ^[] symbols] to view the footnotes.
              <br><br>
              You can also open the footnotes sidebar to view as you read the article.
              <br><br>
              Additionally, we may make mistakes in writing the articles! In the contact us page, we have an option where you can contact us about any inaccuracies in our material. 
              <br><br>
              With that, you're ready to make use of the basic functions of this website! Here are some articles to start you off:[give articles]
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
              <br>↓
            </p>
          </div>
          
          <!-- Right Column: 3D Container -->
          <div class="visualization-column">
            <div id="content-model-container" class="content-3d-container">
              <!-- Expand Icon -->
              <button 
                @click="isModalOpen = true"
                class="expand-icon"
                title="Expand 3D model"
              >
                「 ｣
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal Popup for Expanded 3D View -->
    <div v-if="isModalOpen" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <!-- Close Button -->
        <button 
          @click="closeModal"
          class="modal-close"
          title="Close expanded view"
        >
          ×
        </button>
        
        <!-- Modal 3D Container -->
        <div id="modal-model-container" class="modal-3d-container"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #ffffff;
  position: relative; /* Allow normal document flow for scrolling */
  width: 100%; /* Use available width from app layout */
  overflow-x: hidden; /* Prevent horizontal scrolling */
}

.banner-section {
  position: relative;
  width: 100%; /* Use full available width from app layout */
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
  padding: 4rem 2rem; /* Proper padding for readability */
  max-width: 1200px; /* Match content container width */
  margin: 0 auto; /* Center the content */
  width: 100%;
}

.banner-title {
  font-size: 6rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  margin: 0;
  line-height: 1.2;
}

.content-section {
  background-color: #ffffff;
  position: relative;
  z-index: 3;
  width: 100%; /* Use full available width from app layout */
}

.content-container {
  max-width: 1200px; /* Constrain width for readability */
  margin: 0 auto; /* Center the content */
  padding: 3rem 2rem; /* Proper padding for readability */
}

.paragraph-text {
  font-size: 18px;
  line-height: 1.5;
  color: #374151;
  text-align: left;
  margin: 0;
  max-width: 100%; /* Use full available width within container */
}

/* Two-column layout for content */
.content-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.text-column {
  flex: 1;
  min-width: 0; /* Prevents flex item from overflowing */
}

.visualization-column {
  flex: 0 0 400px; /* Fixed width for 3D container */
  display: flex;
  justify-content: center;
  padding-top: 2rem;
}

.content-3d-container {
  width: 400px;
  height: 600px;
  border: 2px solid #d1d5db; /* Light gray border */
  border-radius: 8px;
  background-color: #f9fafb;
  position: relative;
  overflow: hidden;
}

.content-3d-container canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 6px; /* Slightly less than container to account for border */
}

/* Expand Icon */
.expand-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  outline: none;
}

.expand-icon:hover {
  transform: scale(1.1);
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 20px;
  max-width: 90vw;
  max-height: 90vh;
  width: 900px;
  height: 700px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  color: #666;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
}

.modal-close:hover {
  color: #333;
  transform: scale(1.1);
}

.modal-3d-container {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.modal-3d-container canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 8px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .banner-section {
    height: 50vh;
    min-height: 300px;
  }
  
  .banner-title {
    font-size: 2.5rem;
  }
  
  .banner-content {
    padding: 2rem 1.5rem; /* Proper padding for tablets */
  }
  
  .content-container {
    padding: 2rem 1.5rem; /* Proper padding for tablets */
  }
  
  /* Stack columns on mobile */
  .content-layout {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .visualization-column {
    flex: none;
    align-self: center;
  }
  
  .content-3d-container {
    width: 100%;
    max-width: 350px;
  }
  
  /* Modal responsive design */
  .modal-content {
    width: 95vw;
    height: 80vh;
    padding: 15px;
  }
  
  .expand-icon {
    font-size: 14px;
    padding: 3px 6px;
  }
}

@media (max-width: 480px) {
  .banner-title {
    font-size: 2rem;
  }
  
  .banner-content {
    padding: 1.5rem 1rem; /* Proper padding for mobile */
    text-align: center; /* Center text on mobile for better appearance */
  }
  
  .content-container {
    padding: 1.5rem 1rem; /* Proper padding for mobile */
  }
  
  /* Modal mobile design */
  .modal-content {
    width: 100vw;
    height: 100vh;
    padding: 10px;
    border-radius: 0;
  }
  
  .modal-close {
    width: 28px;
    height: 28px;
    font-size: 18px;
  }
}
</style>