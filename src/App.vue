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
        title: 'Sub-topic 1.1',
        path: '/topic1/page1'
      },
      {
        id: 'section-1-2',
        title: 'Sub-topic 1.2',
        path: '/topic1/page2'
      }
    ]
  },
  {
    id: 'topic2',
    title: 'Topic 2',
    path: '/topic2/page1',
    children: [
      {
        id: 'section-2-1',
        title: 'Sub-topic 2.1',
        path: '/topic2/page1'
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
