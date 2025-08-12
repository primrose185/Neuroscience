<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, provide, inject, computed, watch } from 'vue'
import Generic3DModelViewer from '../utilities/Generic3DModelViewer.js'
import * as THREE from 'three'

interface ViewerOptions {
  fitCamera?: boolean
  camera?: {
    position?: { x: number, y: number, z: number }
    fov?: number
    near?: number
    far?: number
  }
  [key: string]: any // Allow other properties
}

interface Props {
  containerId: string
  modelPath: string
  viewerOptions?: ViewerOptions
  width?: number | string
  height?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  viewerOptions: () => ({}),
  width: 400,
  height: 700
})

// Shared model data - using provide/inject pattern for model sharing, not viewer sharing
// Use a Map to cache multiple models by path
const sharedModelCache = inject('sharedModelCache', ref<Map<string, any>>(new Map()))
const setSharedModelCache = inject('setSharedModelCache', (path: string, data: any) => {})

// Local viewer instance for this container (each container gets its own viewer)
let localViewer: Generic3DModelViewer | null = null
let modalModelViewer: Generic3DModelViewer | null = null

// Modal state
const isModalOpen = ref(false)

// Function to load model with caching
const loadModelWithCache = async (modelPath: string) => {
  if (!localViewer) return
  
  // Check if we already have cached model data for this path
  const cachedModel = sharedModelCache.value.get(modelPath)
  
  if (!cachedModel) {
    // Load the model for the first time and store the GLTF data for sharing
    console.log('Loading model for sharing:', modelPath)
    
    // Load fresh GLTF data for sharing
    const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js')
    const { DRACOLoader } = await import('three/examples/jsm/loaders/DRACOLoader.js')
    
    const loader = new GLTFLoader()
    const dracoLoader = new DRACOLoader()
    dracoLoader.setDecoderPath('/draco/')
    loader.setDRACOLoader(dracoLoader)
    
    const gltfData = await new Promise((resolve, reject) => {
      loader.load(modelPath, resolve, undefined, reject)
    })
    
    // Cache the GLTF data
    sharedModelCache.value.set(modelPath, gltfData)
    setSharedModelCache(modelPath, gltfData)
    
    // Load the model into the viewer
    const result = await localViewer.loadFromGLTFData(gltfData, {
      scale: 1.0,
      position: { x: 0, y: 0, z: 0 },
      autoPlay: false, // We'll manually control animations
      fitCamera: props.viewerOptions.fitCamera ?? true
    })
    
    // For models with animations, play animation once
    const hasAnimations = result.animations && result.animations.length > 0
    const isAnimatedModel = modelPath.includes('animated') || 
                           modelPath.includes('recordingChamber_hscrab') || 
                           modelPath.includes('electrode_hscrab')
    
    if (hasAnimations && isAnimatedModel) {
      // Log detailed animation info for debugging
      console.log('Detected animated model:', modelPath)
      localViewer.getAnimationInfo()
      
      // Play the first animation (typically the main one)
      localViewer.playAnimation(0, {
        loop: THREE.LoopOnce,
        clampWhenFinished: true
      })
    } else if (hasAnimations) {
      // Log available animations for non-animated models
      console.log('Model has animations but not configured for auto-play:', localViewer.getAnimationNames())
    }
    
    console.log('Created and stored shared model data for:', props.containerId)
  } else {
    // Use the cached GLTF data to load the model
    const result = await localViewer.loadFromGLTFData(cachedModel, {
      scale: 1.0,
      position: { x: 0, y: 0, z: 0 },
      autoPlay: false, // We'll manually control animations
      fitCamera: props.viewerOptions.fitCamera ?? true
    })
    
    // For models with animations, play animation once
    const hasAnimations = localViewer.getAnimationNames().length > 0
    const isAnimatedModel = modelPath.includes('animated') || 
                           modelPath.includes('recordingChamber_hscrab') || 
                           modelPath.includes('electrode_hscrab')
    
    if (hasAnimations && isAnimatedModel) {
      // Log detailed animation info for debugging
      console.log('Detected animated model (cached):', modelPath)
      localViewer.getAnimationInfo()
      
      // Play the first animation (typically the main one)
      localViewer.playAnimation(0, {
        loop: THREE.LoopOnce,
        clampWhenFinished: true
      })
    } else if (hasAnimations) {
      // Log available animations for non-animated models
      console.log('Cached model has animations but not configured for auto-play:', localViewer.getAnimationNames())
    }
    
    console.log('Loaded model from cached GLTF data for:', props.containerId)
  }
}

// Computed styles for dynamic dimensions
const containerStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

// Create depth-enhancing gradient texture for scene background
function createDepthGradientTexture(color1: string, color2: string, width: number = 1024, height: number = 1024): THREE.Texture {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!
  
  canvas.width = width
  canvas.height = height
  
  const gradient = ctx.createRadialGradient(
    canvas.width * 0.5, canvas.height * 0.5, 0,
    canvas.width * 0.5, canvas.height * 0.5, Math.max(canvas.width, canvas.height) * 0.7
  )
  
  gradient.addColorStop(0, color1)
  gradient.addColorStop(1, color2)
  
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  const texture = new THREE.CanvasTexture(canvas)
  texture.wrapS = THREE.ClampToEdgeWrapping
  texture.wrapT = THREE.ClampToEdgeWrapping
  texture.minFilter = THREE.LinearFilter
  texture.magFilter = THREE.LinearFilter
  
  return texture
}

// Modal functions
const closeModal = () => {
  isModalOpen.value = false
  if (modalModelViewer) {
    modalModelViewer.dispose()
    modalModelViewer = null
  }
}

const openModal = () => {
  isModalOpen.value = true
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isModalOpen.value) {
    closeModal()
  }
}

onMounted(async () => {
  try {
    // Default viewer options
    const defaultOptions = {
      static: false,
      enableControls: true,
      background: 0x000000,
      fog: false,
      lights: {
        ambient: { color: 0x404040, intensity: 0.4 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: 5, y: 5, z: 5 },
        fov: 60,
        near: 0.1,
        far: 1000
      }
    }

    const mergedOptions = { ...defaultOptions, ...props.viewerOptions }

    // Create a new viewer instance for this container
    localViewer = new Generic3DModelViewer(props.containerId, mergedOptions)
    
    // Apply gradient background with container dimensions
    const containerWidth = typeof props.width === 'number' ? props.width : 400
    const containerHeight = typeof props.height === 'number' ? props.height : 700
    const gradientTexture = createDepthGradientTexture('#ecebf5', '#6c6596', containerWidth, containerHeight)
    localViewer.scene.background = gradientTexture

    // Load model with caching by path
    await loadModelWithCache(props.modelPath)
  } catch (error) {
    console.error('Failed to load 3D model:', error)
  }
  
  // Add keyboard event listener for modal
  window.addEventListener('keydown', handleKeydown)
})

// Watch for modelPath changes and reload model
watch(() => props.modelPath, async (newPath, oldPath) => {
  if (newPath !== oldPath && localViewer) {
    console.log('Model path changed from', oldPath, 'to', newPath)
    await loadModelWithCache(newPath)
  }
})

// Watch for modal state changes to initialize/cleanup modal 3D viewer
const initializeModalViewer = async () => {
  if (isModalOpen.value) {
    await nextTick()
    
    console.log('Initializing modal 3D model viewer...')
    modalModelViewer = new Generic3DModelViewer(`modal-${props.containerId}`, {
      static: false,
      enableControls: true,
      modalMode: true,
      background: 0x000000,
      fog: false,
      lights: {
        ambient: { color: 0xffffff, intensity: 0.6 },
        directional: { color: 0xffffff, intensity: 0.8 }
      },
      camera: {
        position: { x: 5, y: 5, z: 5 },
        fov: 60,
        near: 0.1,
        far: 1000
      }
    })
    
    // Apply gradient background for modal (fixed dimensions)
    const modalGradientTexture = createDepthGradientTexture('#e4e1f2', '#7b6add', 900, 700)
    modalModelViewer.scene.background = modalGradientTexture
    
    // Load model in modal using cached data
    try {
      const cachedModel = sharedModelCache.value.get(props.modelPath)
      if (cachedModel) {
        await modalModelViewer.loadFromGLTFData(cachedModel, {
          scale: 1.0,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: false, // We'll manually control animations
          fitCamera: props.viewerOptions.fitCamera ?? true
        })
      } else {
        await modalModelViewer.loadModel(props.modelPath, {
          scale: 1.0,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: false, // We'll manually control animations
          fitCamera: props.viewerOptions.fitCamera ?? true
        })
      }
      
      // For models with animations, play animation once
      const hasAnimations = modalModelViewer.getAnimationNames().length > 0
      const isAnimatedModel = props.modelPath.includes('animated') || 
                             props.modelPath.includes('recordingChamber_hscrab') || 
                             props.modelPath.includes('electrode_hscrab')
      
      if (hasAnimations && isAnimatedModel) {
        console.log('Playing animation in modal for:', props.modelPath)
        modalModelViewer.playAnimation(0, {
          loop: THREE.LoopOnce,
          clampWhenFinished: true
        })
      }
      
      console.log('Modal 3D model loaded successfully')
    } catch (error) {
      console.error('Failed to load modal 3D model:', error)
    }
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  
  if (localViewer) {
    localViewer.dispose()
  }
  
  if (modalModelViewer) {
    modalModelViewer.dispose()
  }
})

// Provide the modal functions and viewer access to parent components
defineExpose({
  openModal,
  closeModal,
  resetCamera: () => {
    if (localViewer) {
      localViewer.resetCamera()
    }
  },
  getViewer: () => localViewer
})
</script>

<template>
  <div class="shared-3d-viewer">
    <!-- 3D Container -->
    <div 
      :id="containerId"
      class="model-3d-container"
      :style="containerStyle"
    >
      <!-- Expand Icon -->
      <button 
        @click="openModal(); initializeModalViewer()"
        class="expand-icon"
        title="Expand 3D model"
      >
        「 ｣
      </button>
    </div>

    <!-- Modal Popup for Expanded 3D View - Teleported to body -->
    <Teleport to="body">
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
          <div :id="`modal-${containerId}`" class="modal-3d-container"></div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* Component styles remain scoped */
.shared-3d-viewer {
  width: 100%;
  height: 100%;
}

/* 3D Container Styling */
.model-3d-container {
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background-color: #f9fafb;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}


.model-3d-container canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 6px;
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

/* Responsive Design */
@media (max-width: 768px) {
  .model-3d-container {
    width: 100%;
    max-width: 350px;
    height: 500px;
  }
  
  .expand-icon {
    font-size: 14px;
    padding: 3px 6px;
  }
}

@media (max-width: 480px) {
  /* Mobile optimizations */
  .model-3d-container {
    height: 400px;
  }
}
</style>

<!-- Global styles for teleported modal -->
<style>
/* Modal Styles - Global because teleported to body */
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
  z-index: 9999;
  backdrop-filter: blur(2px);
  /* Create new stacking context to ensure modal appears above everything */
  isolation: isolate;
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

/* Responsive Design for Modal */
@media (max-width: 768px) {
  .modal-content {
    width: 95vw;
    height: 80vh;
    padding: 15px;
  }
}

@media (max-width: 480px) {
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