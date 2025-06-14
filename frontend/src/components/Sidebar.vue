<script setup lang="ts">
import { useRouter } from 'vue-router'

interface MenuItem {
  id: string
  title: string
  path?: string
  children?: MenuItem[]
}

interface Props {
  menuItems: MenuItem[]
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['toggleSidebar', 'menuClick'])
const router = useRouter()

const handleMenuClick = (item: MenuItem) => {
  if (item.path) {
    router.push(item.path)
    emit('menuClick', item)
  }
}

const handleToggle = () => {
  emit('toggleSidebar')
}

const handleHomeClick = () => {
  router.push('/')
}
</script>

<template>
  <nav :class="['sidebar p-6 fixed top-0 left-0 h-full z-20 bg-gray-50 border-r border-gray-200 overflow-y-auto transition-transform', isOpen ? 'open' : '']">
    <div class="flex items-center justify-between mb-8">
      <button @click="handleHomeClick" class="text-xl font-bold text-gray-900 hover:text-gray-600">Home</button>
    </div>
    <ul class="sidebar-menu space-y-2">
      <li v-for="item in menuItems" :key="item.id">
        <div 
          class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-200 toc-item cursor-pointer"
          @click="handleMenuClick(item)"
        >
          <span>{{ item.title }}</span>
          <span 
            v-if="item.children?.length" 
            class="text-xs transform transition-transform"
          >▼</span>
        </div>
        <ul v-if="item.children?.length" class="ml-4 mt-2 space-y-2">
          <li v-for="child in item.children" :key="child.id">
            <div 
              class="block p-2 rounded-lg hover:bg-gray-200 cursor-pointer"
              @click="handleMenuClick(child)"
            >
              {{ child.title }}
            </div>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
  <!-- Mobile Menu Toggle Button -->
  <button 
    class="menu-toggle fixed top-4 left-4 z-30 bg-white p-2 rounded-md shadow-md md:hidden" 
    @click="handleToggle"
  >
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
    </svg>
  </button>
</template>

<style scoped>
.sidebar {
  width: 20%;
  min-width: 220px;
  max-width: 300px;
  transition: transform 0.3s ease-in-out;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: 250px;
    position: fixed;
    z-index: 20;
  }
  .sidebar.open {
    transform: translateX(0);
  }
}

.sidebar-menu ul {
  display: block;
}

.cursor-pointer {
  cursor: pointer;
}
</style> 