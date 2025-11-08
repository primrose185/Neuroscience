<script setup lang="ts">
import { ref, provide } from 'vue'
import { useRouter } from 'vue-router'
import Shared3DModelViewer from '../components/Shared3DModelViewer.vue'

const router = useRouter()

// Model cache setup for 3D viewer
const sharedModelCache = ref<Map<string, any>>(new Map())
const setSharedModelCache = (path: string, data: any) => {
  sharedModelCache.value.set(path, data)
}
provide('sharedModelCache', sharedModelCache)
provide('setSharedModelCache', setSharedModelCache)

// Navigate to Platform Guide
const goToPlatformGuide = () => {
  router.push('/platform-guide')
}

// Viewer options for auto-rotating horseshoe crab
const viewerOptions = {
  autoRotate: true,
  enableControls: false,
  background: 0x1a202c,
  camera: {
    position: { x: 8, y: 12, z: 10 },
    fov: 55,
    near: 0.1,
    far: 1000
  },
  lights: {
    ambient: { color: 0x404040, intensity: 0.6 },
    directional: { color: 0xffffff, intensity: 0.9 }
  },
  fitCamera: true
}
</script>

<template>
  <div class="homepage">
    <!-- 3D Model Viewer - Full Viewport Background -->
    <div class="model-viewer-container">
      <Shared3DModelViewer
        container-id="homepage-model-viewer"
        model-path="/models/horseshoe_crab_basic.glb"
        :viewer-options="viewerOptions"
        width="100%"
        height="100vh"
      />
    </div>

    <!-- Hero Overlay Section -->
    <section class="hero-overlay">
      <div class="hero-content">
        <div class="hero-text">
          <div class="hero-title">
            <img src="/white.png" alt="nREM" class="hero-logo" />
          </div>
          <p class="hero-description">
            Neuroscience research explained modestly.
          </p>
        </div>

        <!-- Platform Guide Button -->
        <button class="platform-guide-button" @click="goToPlatformGuide">
          Platform Guide →
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.homepage {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 3D Model Viewer Container */
.model-viewer-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* Remove border and adjust background for full viewport model */
.model-viewer-container :deep(.model-3d-container) {
  border: none;
  border-radius: 0;
  background-color: transparent;
  width: 100%;
  height: 100%;
}

/* Hide expand icon on homepage full viewport viewer */
.model-viewer-container :deep(.expand-icon) {
  display: none;
}

/* Hero Overlay Section */
.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
  text-align: center;
  pointer-events: auto;
}

.hero-text {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  padding: 48px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  margin-bottom: 32px;
}

.hero-title {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-logo {
  height: 4rem;
  width: auto;
  display: block;
  filter: drop-shadow(0 2px 10px rgba(255, 255, 255, 0.5));
}

.hero-description {
  font-size: 1.25rem;
  color: #2d3748;
  line-height: 1.6;
  margin: 0;
}

.platform-guide-button {
  display: inline-block;
  padding: 18px 48px;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(104, 70, 219, 0.3);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  text-decoration: none;
}

.platform-guide-button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.35);
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(104, 70, 219, 0.6);
}

.platform-guide-button:active {
  transform: translateY(0) scale(0.98);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .hero-logo {
    height: 2.75rem;
  }

  .hero-description {
    font-size: 1.1rem;
  }

  .hero-text {
    padding: 32px 24px;
  }

  .platform-guide-button {
    padding: 16px 36px;
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .hero-logo {
    height: 2.25rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .hero-content {
    padding: 0 16px;
  }

  .hero-text {
    padding: 24px 20px;
    margin-bottom: 24px;
  }

  .platform-guide-button {
    padding: 14px 32px;
    font-size: 1rem;
  }
}
</style>