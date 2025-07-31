<script setup lang="ts">
import { ref, provide } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import type Generic3DModelViewer from './utilities/Generic3DModelViewer.js'

interface MenuItem {
  id: string
  title: string
  path?: string
  children?: MenuItem[]
}

const router = useRouter()
const sidebarOpen = ref(false)

// Shared 3D model viewer instance
const sharedModelViewer = ref<Generic3DModelViewer | null>(null)
const setSharedModelViewer = (viewer: Generic3DModelViewer | null) => {
  sharedModelViewer.value = viewer
}

// Provide shared model viewer to all child components
provide('sharedModelViewer', sharedModelViewer)
provide('setSharedModelViewer', setSharedModelViewer)

const menuItems: MenuItem[] = [
  {
    id: 'topic1',
    title: 'Hartline—Nobel Lecture, 1967',
    path: '/topic1',
    children: [
      {
        id: 'section-1-1',
        title: 'Introducing Limulus polyphemus',
        path: '/topic1#introducing-limulus-polyphemus'
      },
      {
        id: 'section-1-2',
        title: 'Experiments with single ommatidia',
        path: '/topic1#experiments-with-single-ommatidia'
      },
      {
        id: 'section-1-3',
        title: 'Inhibitory interactions in the retina',
        path: '/topic1#inhibitory-interactions-in-the-retina'
      },
      {
        id: 'section-1-4',
        title: 'Mathematical models of inhibition',
        path: '/topic1#mathematical-models-of-mutual-inhibition'
      }
    ]
  },
  {
    id: 'topic2',
    title: 'Topic 2',
    path: '/topic2',
    children: [
      {
        id: 'section-2-1',
        title: 'Neuroscience Fundamentals',
        path: '/topic2#neuroscience-fundamentals'
      },
      {
        id: 'section-2-2',
        title: 'Neural Circuits and Connectivity',
        path: '/topic2#neural-circuits'
      },
      {
        id: 'section-2-3',
        title: 'Brain Imaging and Analysis',
        path: '/topic2#brain-imaging'
      },
      {
        id: 'section-2-4',
        title: 'Computational Neuroscience',
        path: '/topic2#computational-neuroscience'
      }
    ]
  },
  {
    id: 'topic3',
    title: 'Topic 3',
    path: '/topic3'
  }
]

const handleSidebarToggle = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const handleMenuClick = (item: MenuItem) => {
  if (item.path) {
    router.push(item.path)
    sidebarOpen.value = false
  }
}
</script>

<template>
  <div class="app-layout bg-white text-gray-800 min-h-screen flex">
    <Sidebar 
      :menu-items="menuItems"
      :is-open="sidebarOpen"
      @toggle-sidebar="handleSidebarToggle"
      @menu-click="handleMenuClick"
    />
    <!-- Main Content -->
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  margin-left: 20vw;
  width: 80vw;
  transition: margin-left 0.3s;
}
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100%;
  }
}
</style>
