<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// Refs
const modelContainer = ref<HTMLDivElement>()
const isLoading = ref(true)
const loadingError = ref<string | null>(null)

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let animationId: number

// Initialize Three.js scene
const initScene = () => {
  if (!modelContainer.value) return

  // Scene setup
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f0f0) // Light gray background

  // Camera setup
  const aspect = modelContainer.value.clientWidth / modelContainer.value.clientHeight
  camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
  camera.position.set(0, 5, 10)

  // Renderer setup
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(modelContainer.value.clientWidth, modelContainer.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.outputColorSpace = THREE.SRGBColorSpace

  modelContainer.value.appendChild(renderer.domElement)

  // Controls setup
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.autoRotate = true
  controls.autoRotateSpeed = 1.0

  // Lighting setup
  setupLights()

  // Handle window resize
  window.addEventListener('resize', onWindowResize)
}

// Setup lighting
const setupLights = () => {
  // Ambient light
  const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
  scene.add(ambientLight)

  // Main directional light
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 5)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  scene.add(directionalLight)

  // Fill light
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3)
  fillLight.position.set(-10, 0, -10)
  scene.add(fillLight)
}

// Load 3D model
const loadModel = async () => {
  const loader = new GLTFLoader()
  
  // Setup DRACO decoder for compressed models
  const dracoLoader = new DRACOLoader()
  dracoLoader.setDecoderPath('/draco/')
  loader.setDRACOLoader(dracoLoader)

  try {
    // Replace '/models/your-model.glb' with your actual model path
    const gltf = await new Promise<any>((resolve, reject) => {
      loader.load(
        '/models/donut_trial.glb', // Put your model file in public/models/
        resolve,
        (progress) => {
          console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%')
        },
        reject
      )
    })

    const model = gltf.scene

    // Enable shadows
    model.traverse((child: any) => {
      if (child.isMesh) {
        child.castShadow = true
        child.receiveShadow = true
      }
    })

    // Auto-fit camera to model
    fitCameraToModel(model)

    // Add to scene
    scene.add(model)
    
    isLoading.value = false
    console.log('Model loaded successfully')

  } catch (error) {
    console.error('Error loading model:', error)
    loadingError.value = 'Failed to load 3D model. Please check the model path.'
    isLoading.value = false
  }
}

// Fit camera to model bounds
const fitCameraToModel = (model: THREE.Object3D) => {
  const box = new THREE.Box3().setFromObject(model)
  const size = box.getSize(new THREE.Vector3()).length()
  const center = box.getCenter(new THREE.Vector3())

  // Adjust camera position
  const distance = size * 1.5
  camera.position.copy(center)
  camera.position.x += distance
  camera.position.y += distance * 0.5
  camera.position.z += distance

  // Update controls target
  controls.target.copy(center)
  controls.update()
}

// Handle window resize
const onWindowResize = () => {
  if (!modelContainer.value) return

  const width = modelContainer.value.clientWidth
  const height = modelContainer.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// Animation loop
const animate = () => {
  animationId = requestAnimationFrame(animate)

  // Update controls
  controls.update()

  // Render
  renderer.render(scene, camera)
}

// Cleanup
const cleanup = () => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  if (controls) {
    controls.dispose()
  }

  if (renderer) {
    renderer.dispose()
  }

  window.removeEventListener('resize', onWindowResize)
}

// Lifecycle hooks
onMounted(() => {
  initScene()
  loadModel()
  animate()
})

onUnmounted(() => {
  cleanup()
})
</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl mx-auto">
      <div 
        ref="modelContainer" 
        class="model-container bg-gray-100 rounded-lg h-64 w-full mb-8 shadow-lg relative overflow-hidden"
      >
        <!-- Loading state -->
        <div 
          v-if="isLoading" 
          class="absolute inset-0 flex items-center justify-center bg-gray-200 rounded-lg"
        >
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <span class="text-gray-600">Loading 3D Model...</span>
          </div>
        </div>

        <!-- Error state -->
        <div 
          v-else-if="loadingError" 
          class="absolute inset-0 flex items-center justify-center bg-red-50 rounded-lg"
        >
          <div class="text-center text-red-600">
            <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm">{{ loadingError }}</p>
          </div>
        </div>

        <!-- Instructions overlay (shows when loaded) -->
        <div 
          v-if="!isLoading && !loadingError"
          class="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm"
        >
          Click and drag to rotate • Scroll to zoom
        </div>
      </div>
      
      <div class="content">
        <h1 class="text-4xl font-bold mb-6">Sub-topic 1.2</h1>
        <p class="text-lg leading-relaxed">
          Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: calc(100vh - 4rem);
}

.model-container {
  position: relative;
}

.model-container canvas {
  border-radius: 0.5rem;
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>