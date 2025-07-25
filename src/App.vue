<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

interface MenuItem {
  id: string
  title: string
  path?: string
  children?: MenuItem[]
}

const router = useRouter()
const sidebarOpen = ref(false)

const menuItems: MenuItem[] = [
  {
    id: 'topic1',
    title: 'Hartline et al.—Title, 19somethign',
    path: '/topic1/page1',
    children: [
      {
        id: 'section-1-1',
        title: 'Basic Probability',
        path: '/topic1#basic-probability'
      },
      {
        id: 'section-1-2',
        title: 'Conditional Probability',
        path: '/topic1#conditional-probability'
      },
      {
        id: 'section-1-3',
        title: 'Bayes\' Theorem',
        path: '/topic1#bayes-theorem'
      },
      {
        id: 'section-1-4',
        title: 'Statistical Inference',
        path: '/topic1#statistical-inference'
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
