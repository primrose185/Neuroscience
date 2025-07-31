<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, provide, inject } from 'vue'
import Generic3DModelViewer from '../utilities/Generic3DModelViewer.js'
import * as THREE from 'three'

interface Props {
  containerId: string
  modelPath: string
  viewerOptions?: object
}

const props = withDefaults(defineProps<Props>(), {
  viewerOptions: () => ({})
})

// Shared model data - using provide/inject pattern for model sharing, not viewer sharing
const sharedModelData = inject('sharedModelData', ref<any>(null))
const setSharedModelData = inject('setSharedModelData', (data: any) => {})

// Local viewer instance for this container (each container gets its own viewer)
let localViewer: Generic3DModelViewer | null = null
let modalModelViewer: Generic3DModelViewer | null = null

// Modal state
const isModalOpen = ref(false)

// Create depth-enhancing gradient texture for scene background
function createDepthGradientTexture(color1: string, color2: string): THREE.Texture {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!
  
  canvas.width = 1024
  canvas.height = 1024
  
  const gradient = ctx.createRadialGradient(
    canvas.width * 0.5, canvas.height * 0.5, 0,
    canvas.width * 0.5, canvas.height * 0.5, canvas.width * 0.7
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
    
    // Apply gradient background
    const gradientTexture = createDepthGradientTexture('#ecebf5', '#6c6596')
    localViewer.scene.background = gradientTexture

    // Check if we already have shared model data
    if (!sharedModelData.value) {
      // Load the model for the first time and store the GLTF data for sharing
      const result = await localViewer.loadModel(props.modelPath, {
        scale: 1.0,
        position: { x: 0, y: 0, z: 0 },
        autoPlay: false,
        fitCamera: true
      })
      
      // Store the GLTF data for sharing (not the Three.js objects)
      // We need to access the original GLTF data from the loader
      console.log('Loading model for sharing:', props.modelPath)
      
      // Load fresh GLTF data for sharing
      const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js')
      const { DRACOLoader } = await import('three/examples/jsm/loaders/DRACOLoader.js')
      
      const loader = new GLTFLoader()
      const dracoLoader = new DRACOLoader()
      dracoLoader.setDecoderPath('/draco/')
      loader.setDRACOLoader(dracoLoader)
      
      const gltfData = await new Promise((resolve, reject) => {
        loader.load(props.modelPath, resolve, undefined, reject)
      })
      
      setSharedModelData(gltfData)
      console.log('Created and stored shared model data for:', props.containerId)
    } else {
      // Use the shared GLTF data to load the model
      await localViewer.loadFromGLTFData(sharedModelData.value, {
        scale: 1.0,
        position: { x: 0, y: 0, z: 0 },
        autoPlay: false,
        fitCamera: true
      })
      
      console.log('Loaded model from shared GLTF data for:', props.containerId)
    }
  } catch (error) {
    console.error('Failed to load 3D model:', error)
  }
  
  // Add keyboard event listener for modal
  window.addEventListener('keydown', handleKeydown)
})

// Watch for modal state changes to initialize/cleanup modal 3D viewer
const initializeModalViewer = async () => {
  if (isModalOpen.value) {
    await nextTick()
    
    console.log('Initializing modal 3D model viewer...')
    modalModelViewer = new Generic3DModelViewer(`modal-${props.containerId}`, {
      static: false,
      enableControls: true,
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
    
    // Apply gradient background
    const modalGradientTexture = createDepthGradientTexture('#e4e1f2', '#7b6add')
    modalModelViewer.scene.background = modalGradientTexture
    
    // Load model in modal using shared data if available
    try {
      if (sharedModelData.value) {
        await modalModelViewer.loadFromGLTFData(sharedModelData.value, {
          scale: 1.0,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: false,
          fitCamera: true
        })
      } else {
        await modalModelViewer.loadModel(props.modelPath, {
          scale: 1.0,
          position: { x: 0, y: 0, z: 0 },
          autoPlay: false,
          fitCamera: true
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

// Provide the modal functions to parent components if needed
defineExpose({
  openModal,
  closeModal
})
</script>

<template>
  <div class="shared-3d-viewer">
    <!-- 3D Container -->
    <div 
      :id="containerId"
      class="model-3d-container"
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
        <div :id="`modal-${containerId}`" class="modal-3d-container"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shared-3d-viewer {
  width: 100%;
  height: 100%;
}

/* 3D Container Styling */
.model-3d-container {
  width: 400px;
  height: 600px;
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
  .model-3d-container {
    width: 100%;
    max-width: 350px;
    height: 500px;
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
  /* Mobile optimizations */
  .model-3d-container {
    height: 400px;
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